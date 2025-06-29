"""
Enhanced Fluent Design Pagination Component

Implements modern pagination controls with smooth animations and optimized performance.
Based on Windows 11 Fluent Design principles with QFluentWidget patterns.
"""

from typing import Optional, List, Dict, Any, Callable
import math
import weakref
from functools import lru_cache
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel,
                               QComboBox, QSpinBox, QGraphicsOpacityEffect,
                               QGraphicsDropShadowEffect, QSizePolicy)
from PySide6.QtCore import (Qt, Signal, QPropertyAnimation, QParallelAnimationGroup,
                            QSequentialAnimationGroup, QEasingCurve, QTimer,
                            Property, QObject, QRect, QByteArray, QEvent)
from PySide6.QtGui import QPainter, QPainterPath, QColor, QBrush, QPen

from core.theme import theme_manager
from core.enhanced_animations import FluentRevealEffect, FluentMicroInteraction, FluentTransition
from core.animation import FluentAnimation


class AnimatedPaginationProperty(QObject):
    """Helper class for custom animated properties in pagination"""

    def __init__(self, parent):
        super().__init__(parent)
        self._glow_intensity = 0.0
        self._scale_factor = 1.0
        self._opacity = 1.0
        self._parent_update_fn = None

        # Cache the parent's update method for performance
        if parent and hasattr(parent, 'update') and callable(getattr(parent, 'update')):
            self._parent_update_fn = weakref.WeakMethod(parent.update)

    @property
    def glow_intensity(self) -> float:
        return self._glow_intensity

    @glow_intensity.setter
    def glow_intensity(self, value: float) -> None:
        if abs(self._glow_intensity - value) > 0.001:  # Threshold to avoid tiny updates
            self._glow_intensity = value
            self._trigger_update()

    @property
    def scale_factor(self) -> float:
        return self._scale_factor

    @scale_factor.setter
    def scale_factor(self, value: float) -> None:
        if abs(self._scale_factor - value) > 0.001:  # Threshold to avoid tiny updates
            self._scale_factor = value
            self._trigger_update()

    @property
    def opacity(self) -> float:
        return self._opacity

    @opacity.setter
    def opacity(self, value: float) -> None:
        if abs(self._opacity - value) > 0.001:  # Threshold to avoid tiny updates
            self._opacity = value
            self._trigger_update()

    def _trigger_update(self) -> None:
        """Trigger parent widget update with null-check"""
        if self._parent_update_fn:
            update_method = self._parent_update_fn()
            if update_method:
                update_method()


class EnhancedPaginationButton(QPushButton):
    """Enhanced pagination button with modern animations and effects"""

    # Class-level animation pool for better reuse
    _animation_pool = {}

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        # Animation properties
        self._animated_props = AnimatedPaginationProperty(self)
        self._is_hovered = False
        self._is_pressed = False
        self._is_current = False
        self._should_animate = True  # Flag to control animations

        # Animation groups
        self._hover_group = QParallelAnimationGroup(self)
        self._press_group = QSequentialAnimationGroup(self)

        # Performance optimization
        self._cached_colors = {}
        self._last_theme_hash = None
        self._painting_enabled = True  # Flag to control painting
        self._update_pending = False   # Flag for debounced updates

        # Create debounce timer for updates
        self._update_timer = QTimer(self)
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._perform_update)

        self._setup_animations()
        self._setup_properties()

        # Track application performance mode
        self._performance_mode = False
        self._check_system_performance()

    def _check_system_performance(self):
        """Check system capabilities and adjust animation settings"""
        # This would be implemented based on system metrics
        # For now using a simple approach
        import os
        if os.environ.get('LOW_PERFORMANCE_MODE') == '1':
            self._performance_mode = True
            self._should_animate = False

    def _setup_properties(self):
        """Setup button properties for optimal performance"""
        self.setFixedSize(36, 36)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAutoFillBackground(False)

        # Enable hover tracking without using enterEvent/leaveEvent
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.installEventFilter(self)

    def _setup_animations(self):
        """Setup comprehensive animation system"""
        # Use shorter durations for better performance
        duration_fast = FluentAnimation.DURATION_FAST if not self._performance_mode else FluentAnimation.DURATION_FAST // 2

        # Hover animations
        self._hover_glow_anim = QPropertyAnimation(
            self._animated_props, QByteArray(b"glow_intensity"))
        self._hover_glow_anim.setDuration(duration_fast)
        self._hover_glow_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)

        self._hover_scale_anim = QPropertyAnimation(
            self._animated_props, QByteArray(b"scale_factor"))
        self._hover_scale_anim.setDuration(duration_fast)
        self._hover_scale_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Use existing animations from pool if available
        key = f"hover_{id(self)}"
        if key not in EnhancedPaginationButton._animation_pool:
            EnhancedPaginationButton._animation_pool[key] = self._hover_group

        self._hover_group.addAnimation(self._hover_glow_anim)
        self._hover_group.addAnimation(self._hover_scale_anim)

        # Press animations
        self._press_scale_down = QPropertyAnimation(
            self._animated_props, QByteArray(b"scale_factor"))
        self._press_scale_down.setDuration(duration_fast // 3)
        self._press_scale_down.setEasingCurve(QEasingCurve.Type.InQuad)

        self._press_scale_up = QPropertyAnimation(
            self._animated_props, QByteArray(b"scale_factor"))
        self._press_scale_up.setDuration(duration_fast // 2)
        self._press_scale_up.setEasingCurve(QEasingCurve.Type.OutElastic)

        key = f"press_{id(self)}"
        if key not in EnhancedPaginationButton._animation_pool:
            EnhancedPaginationButton._animation_pool[key] = self._press_group

        self._press_group.addAnimation(self._press_scale_down)
        self._press_group.addAnimation(self._press_scale_up)

    def eventFilter(self, obj, event):
        """Efficient event filter for hover and other events"""
        if obj is self:
            if event.type() == QEvent.Type.HoverEnter:
                self._handle_hover_enter()
                return True
            elif event.type() == QEvent.Type.HoverLeave:
                self._handle_hover_leave()
                return True
        return super().eventFilter(obj, event)

    def _handle_hover_enter(self):
        """Optimized hover enter handler"""
        if self._is_hovered or not self.isEnabled() or not self._should_animate:
            return

        self._is_hovered = True

        # Skip animation in performance mode
        if self._performance_mode:
            target_glow = 0.8 if self._is_current else 0.4
            target_scale = 1.08 if self._is_current else 1.03
            self._animated_props.glow_intensity = target_glow
            self._animated_props.scale_factor = target_scale
            return

        # Stop any running animations
        if self._hover_group.state() == QParallelAnimationGroup.State.Running:
            self._hover_group.stop()

        # Setup hover animations
        target_glow = 0.8 if self._is_current else 0.4
        target_scale = 1.08 if self._is_current else 1.03

        self._hover_glow_anim.setStartValue(
            self._animated_props.glow_intensity)
        self._hover_glow_anim.setEndValue(target_glow)

        self._hover_scale_anim.setStartValue(self._animated_props.scale_factor)
        self._hover_scale_anim.setEndValue(target_scale)

        self._hover_group.start()

    def _handle_hover_leave(self):
        """Optimized hover leave handler"""
        if not self._is_hovered or not self._should_animate:
            return

        self._is_hovered = False

        # Skip animation in performance mode
        if self._performance_mode:
            target_glow = 0.6 if self._is_current else 0.0
            target_scale = 1.05 if self._is_current else 1.0
            self._animated_props.glow_intensity = target_glow
            self._animated_props.scale_factor = target_scale
            return

        # Stop any running animations
        if self._hover_group.state() == QParallelAnimationGroup.State.Running:
            self._hover_group.stop()

        # Return to normal or current state
        target_glow = 0.6 if self._is_current else 0.0
        target_scale = 1.05 if self._is_current else 1.0

        self._hover_glow_anim.setStartValue(
            self._animated_props.glow_intensity)
        self._hover_glow_anim.setEndValue(target_glow)

        self._hover_scale_anim.setStartValue(self._animated_props.scale_factor)
        self._hover_scale_anim.setEndValue(target_scale)

        self._hover_group.start()

    def set_current(self, is_current: bool):
        """Set current page state with smooth transition"""
        if self._is_current != is_current:
            self._is_current = is_current

            if self._should_animate:
                self._animate_current_state_change()
            else:
                # Direct property update in performance mode
                target_glow = 0.6 if self._is_current else 0.0
                target_scale = 1.05 if self._is_current else 1.0
                self._animated_props.glow_intensity = target_glow
                self._animated_props.scale_factor = target_scale
                self.update()

    def _animate_current_state_change(self):
        """Animate current state change"""
        target_glow = 0.6 if self._is_current else 0.0
        target_scale = 1.05 if self._is_current else 1.0

        # Smooth transition to current state
        current_anim = QParallelAnimationGroup(self)

        glow_anim = QPropertyAnimation(
            self._animated_props, QByteArray(b"glow_intensity"))
        glow_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
        glow_anim.setStartValue(self._animated_props.glow_intensity)
        glow_anim.setEndValue(target_glow)
        glow_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)

        scale_anim = QPropertyAnimation(
            self._animated_props, QByteArray(b"scale_factor"))
        scale_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
        scale_anim.setStartValue(self._animated_props.scale_factor)
        scale_anim.setEndValue(target_scale)
        scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        current_anim.addAnimation(glow_anim)
        current_anim.addAnimation(scale_anim)
        current_anim.start()

    def mousePressEvent(self, event):
        """Enhanced press event with tactile feedback"""
        if not self.isEnabled() or not self._should_animate:
            return super().mousePressEvent(event)

        self._is_pressed = True

        # Setup press animation
        current_scale = self._animated_props.scale_factor
        self._press_scale_down.setStartValue(current_scale)
        self._press_scale_down.setEndValue(current_scale * 0.92)

        self._press_scale_up.setStartValue(current_scale * 0.92)
        self._press_scale_up.setEndValue(current_scale)

        self._press_group.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Enhanced release event"""
        self._is_pressed = False
        super().mouseReleaseEvent(event)

    def _perform_update(self):
        """Execute the actual update"""
        self._update_pending = False
        if self._painting_enabled:
            super().update()

    def paintEvent(self, event):
        """Enhanced paint event with custom effects"""
        if not self._painting_enabled:
            return

        # Apply transform only if needed
        painter = None
        scale_value = self._animated_props.scale_factor

        if abs(scale_value - 1.0) > 0.01:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            center = self.rect().center()
            painter.translate(center)
            painter.scale(scale_value, scale_value)
            painter.translate(-center)

            # Let the base class draw the button
            super().paintEvent(event)

            # Draw glow effect if needed
            if self._animated_props.glow_intensity > 0:
                self._draw_glow_effect(painter)

            painter.end()
        else:
            # No scaling needed, call normal paint
            super().paintEvent(event)

            # Draw glow effect if needed
            if self._animated_props.glow_intensity > 0:
                self._draw_glow_effect()

    def _draw_glow_effect(self, existing_painter=None):
        """Draw custom glow effect with performance optimization"""
        if not theme_manager:
            return

        painter = existing_painter or QPainter(self)
        if not existing_painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Cache theme colors for performance
        if not self._cached_colors:
            self._cached_colors['primary'] = theme_manager.get_color('primary')

        primary_color = self._cached_colors['primary']
        glow_color = QColor(primary_color)
        glow_color.setAlphaF(self._animated_props.glow_intensity * 0.4)

        # Create glow path
        glow_rect = self.rect().adjusted(-2, -2, 2, 2)
        glow_path = QPainterPath()
        glow_path.addRoundedRect(glow_rect, 8, 8)

        # Draw glow
        painter.setBrush(QBrush(glow_color))
        painter.setPen(QPen(glow_color, 2))
        painter.drawPath(glow_path)

        # Only end painter if we created it
        if not existing_painter:
            painter.end()

    def disable_animations(self):
        """Disable animations for performance"""
        self._should_animate = False

    def enable_animations(self):
        """Enable animations"""
        self._should_animate = True

    def cleanup(self):
        """Cleanup animations and resources"""
        self._painting_enabled = False

        if self._hover_group:
            self._hover_group.stop()

        if self._press_group:
            self._press_group.stop()

        # Remove from animation pool
        key = f"hover_{id(self)}"
        if key in EnhancedPaginationButton._animation_pool:
            del EnhancedPaginationButton._animation_pool[key]

        key = f"press_{id(self)}"
        if key in EnhancedPaginationButton._animation_pool:
            del EnhancedPaginationButton._animation_pool[key]

        # Clear cached data
        self._cached_colors.clear()

        if hasattr(self, '_update_timer'):
            self._update_timer.stop()


class FluentPagination(QWidget):
    """
    Enhanced Modern Pagination Component with Smooth Animations
    """

    # Signals
    page_changed = Signal(int)
    page_size_changed = Signal(int)

    # Display modes
    MODE_SIMPLE = "simple"
    MODE_FULL = "full"
    MODE_COMPACT = "compact"

    def __init__(self,
                 total: int = 0,
                 page_size: int = 10,
                 current_page: int = 1,
                 mode: str = MODE_FULL,
                 show_page_size: bool = True,
                 show_jumper: bool = True,
                 show_total: bool = True,
                 page_size_options: Optional[List[int]] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Core properties
        self._total = total
        self._page_size = page_size
        self._current_page = current_page
        self._mode = mode
        self._show_page_size = show_page_size
        self._show_jumper = show_jumper
        self._show_total = show_total
        self._page_size_options = page_size_options or [10, 20, 50, 100]

        # Performance optimization
        self._cached_theme_colors = {}
        self._last_theme_hash = None
        self._page_buttons_cache = {}
        self._layout_cache = None
        self._page_range_cache = {}  # Cache for page ranges
        self._update_is_scheduled = False
        self._animations_enabled = True

        # Determine performance mode
        self._check_performance_mode()

        # Animation management
        self._animation_registry = {}
        self._is_animating = False

        # Debounce timer
        self._update_timer = QTimer(self)
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._perform_update)

        self._setup_ui()
        self._connect_signals()
        self._cache_theme_colors()
        self._setup_responsive_design()

        # Initial state
        self._update_state()
        self._play_entrance_animation()

    def _check_performance_mode(self):
        """Check system performance and adjust settings"""
        import os
        low_performance = os.environ.get('LOW_PERFORMANCE_MODE') == '1'
        self._animations_enabled = not low_performance

    def _setup_ui(self):
        """Setup enhanced UI with modern layout"""
        self._layout_cache = QHBoxLayout(self)
        self._layout_cache.setContentsMargins(8, 4, 8, 4)
        self._layout_cache.setSpacing(12)

        self._create_total_section()
        self._create_page_size_section()
        self._create_pagination_section()
        self._create_jumper_section()

    def _setup_responsive_design(self):
        """Setup responsive design properties"""
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(48)

    def _create_total_section(self):
        """Create total items display section"""
        if self._show_total and self._layout_cache is not None:
            self._total_label = QLabel()
            self._total_label.setObjectName("pagination_total_label")
            self._layout_cache.addWidget(self._total_label)
            self._layout_cache.addStretch()

    def _create_page_size_section(self):
        """Create page size selection section"""
        if self._show_page_size and self._layout_cache is not None:
            self._page_size_label = QLabel("Items per page")
            self._page_size_label.setObjectName("pagination_page_size_label")

            self._page_size_combo = QComboBox()
            self._page_size_combo.setObjectName("pagination_page_size_combo")
            self._page_size_combo.setFixedWidth(80)

            for size in self._page_size_options:
                self._page_size_combo.addItem(str(size), size)

            self._page_size_combo.setCurrentText(str(self._page_size))

            self._layout_cache.addWidget(self._page_size_label)
            self._layout_cache.addWidget(self._page_size_combo)

    def _create_pagination_section(self):
        """Create main pagination controls section"""
        self._pagination_container = QWidget()
        self._pagination_container.setObjectName(
            "pagination_controls_container")
        self._pagination_layout = QHBoxLayout(self._pagination_container)
        self._pagination_layout.setContentsMargins(0, 0, 0, 0)
        self._pagination_layout.setSpacing(6)

        # Enhanced navigation buttons
        self._prev_button = EnhancedPaginationButton("‹")
        self._prev_button.setObjectName("pagination_prev_button")
        self._prev_button.setToolTip("Previous page")
        self._prev_button.clicked.connect(self._go_prev_page)

        self._next_button = EnhancedPaginationButton("›")
        self._next_button.setObjectName("pagination_next_button")
        self._next_button.setToolTip("Next page")
        self._next_button.clicked.connect(self._go_next_page)

        # Disable animations if needed
        if not self._animations_enabled:
            self._prev_button.disable_animations()
            self._next_button.disable_animations()

        # Page buttons container with dynamic layout
        self._page_buttons_container = QWidget()
        self._page_buttons_container.setObjectName(
            "pagination_page_buttons_container")
        self._page_buttons_layout = QHBoxLayout(self._page_buttons_container)
        self._page_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self._page_buttons_layout.setSpacing(4)

        # Assemble pagination layout
        self._pagination_layout.addWidget(self._prev_button)
        self._pagination_layout.addWidget(self._page_buttons_container)
        self._pagination_layout.addWidget(self._next_button)

        if self._layout_cache is not None:
            self._layout_cache.addWidget(self._pagination_container)

    def _create_jumper_section(self):
        """Create page jumper section"""
        if self._show_jumper and self._layout_cache is not None:
            self._jumper_label = QLabel("Go to page")
            self._jumper_label.setObjectName("pagination_jumper_label")

            self._jumper_spinbox = QSpinBox()
            self._jumper_spinbox.setObjectName("pagination_jumper_spinbox")
            self._jumper_spinbox.setFixedWidth(70)
            self._jumper_spinbox.setMinimum(1)

            self._layout_cache.addWidget(self._jumper_label)
            self._layout_cache.addWidget(self._jumper_spinbox)

    def _connect_signals(self):
        """Connect signals with proper cleanup"""
        if hasattr(self, '_page_size_combo'):
            self._page_size_combo.currentTextChanged.connect(
                self._on_page_size_changed)

        if hasattr(self, '_jumper_spinbox'):
            self._jumper_spinbox.valueChanged.connect(self._on_jumper_changed)

        if theme_manager:
            theme_manager.theme_changed.connect(
                self._on_theme_changed_debounced)

        self._update_style()

    def _cache_theme_colors(self):
        """Cache theme colors for performance optimization"""
        if not theme_manager:
            return

        theme_hash = hash(str(theme_manager.get_current_theme()))

        if theme_hash != self._last_theme_hash:
            self._cached_theme_colors = {
                'background': theme_manager.get_color('background'),
                'surface': theme_manager.get_color('surface'),
                'primary': theme_manager.get_color('primary'),
                'on_surface': theme_manager.get_color('on_surface'),
                'on_primary': theme_manager.get_color('on_primary'),
                'border': theme_manager.get_color('border'),
                'surface_variant': theme_manager.get_color('surface_variant'),
                'on_surface_variant': theme_manager.get_color('on_surface_variant'),
                'outline': theme_manager.get_color('outline')
            }
            self._last_theme_hash = theme_hash

    @lru_cache(maxsize=8)
    def _get_button_style(self, is_current: bool, is_nav: bool = False) -> str:
        """Get cached button style"""
        if not self._cached_theme_colors:
            self._cache_theme_colors()

        colors = self._cached_theme_colors

        if is_nav:
            return f"""
                EnhancedPaginationButton {{
                    background-color: {colors['surface'].name()};
                    color: {colors['on_surface'].name()};
                    border: 1px solid {colors['border'].name()};
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: 600;
                    padding: 0px;
                }}
                EnhancedPaginationButton:hover:enabled {{
                    background-color: {colors['primary'].lighter(140).name()};
                    border-color: {colors['primary'].name()};
                    color: {colors['on_primary'].name()};
                }}
                EnhancedPaginationButton:pressed:enabled {{
                    background-color: {colors['primary'].name()};
                    border-color: {colors['primary'].darker(110).name()};
                }}
                EnhancedPaginationButton:disabled {{
                    background-color: {colors['surface_variant'].name()};
                    color: {colors['on_surface_variant'].darker(150).name()};
                    border-color: {colors['outline'].name()};
                    opacity: 0.6;
                }}
            """

        if is_current:
            return f"""
                EnhancedPaginationButton {{
                    background-color: {colors['primary'].name()};
                    color: {colors['on_primary'].name()};
                    border: 2px solid {colors['primary'].name()};
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 700;
                }}
                EnhancedPaginationButton:hover {{
                    background-color: {colors['primary'].darker(110).name()};
                    border-color: {colors['primary'].darker(110).name()};
                }}
            """
        else:
            return f"""
                EnhancedPaginationButton {{
                    background-color: {colors['surface'].name()};
                    color: {colors['on_surface'].name()};
                    border: 1px solid {colors['border'].name()};
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                EnhancedPaginationButton:hover:enabled {{
                    background-color: {colors['primary'].lighter(140).name()};
                    border-color: {colors['primary'].name()};
                    color: {colors['on_primary'].name()};
                }}
                EnhancedPaginationButton:pressed:enabled {{
                    background-color: {colors['primary'].name()};
                }}
            """

    def _update_style(self):
        """Update styles with cached colors and smooth transitions"""
        # Apply nav button styles from cache
        nav_button_style = self._get_button_style(False, True)
        self._prev_button.setStyleSheet(nav_button_style)
        self._next_button.setStyleSheet(nav_button_style)

        # Get colors
        if not self._cached_theme_colors:
            self._cache_theme_colors()

        colors = self._cached_theme_colors

        # Label styles with modern typography
        label_style = f"""
            QLabel {{
                color: {colors['on_surface'].name()};
                font-size: 14px;
                font-weight: 500;
                padding: 0 4px;
            }}
        """

        if hasattr(self, '_total_label'):
            self._total_label.setStyleSheet(label_style)
        if hasattr(self, '_page_size_label'):
            self._page_size_label.setStyleSheet(label_style)
        if hasattr(self, '_jumper_label'):
            self._jumper_label.setStyleSheet(label_style)

        # Input controls with modern styling
        input_style = f"""
            QComboBox, QSpinBox {{
                background-color: {colors['surface'].name()};
                color: {colors['on_surface'].name()};
                border: 1px solid {colors['border'].name()};
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 13px;
                font-weight: 500;
            }}
            QComboBox:hover, QSpinBox:hover {{
                border-color: {colors['primary'].name()};
                background-color: {colors['surface'].lighter(105).name()};
            }}
            QComboBox:focus, QSpinBox:focus {{
                border-color: {colors['primary'].name()};
                border-width: 2px;
                outline: none;
            }}
            QComboBox::drop-down {{
                border: none;
                border-radius: 0 6px 6px 0;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
        """

        if hasattr(self, '_page_size_combo'):
            self._page_size_combo.setStyleSheet(input_style)
        if hasattr(self, '_jumper_spinbox'):
            self._jumper_spinbox.setStyleSheet(input_style)

    def _update_page_buttons(self):
        """Update page buttons with optimized rendering and animations"""
        if self._is_animating:
            return

        # Clear existing buttons efficiently
        self._clear_page_buttons()

        if self._mode == self.MODE_SIMPLE:
            return

        total_pages = self.get_total_pages()
        if total_pages <= 1 and self._mode != self.MODE_FULL:
            self._page_buttons_container.setVisible(False)
            return

        self._page_buttons_container.setVisible(True)

        # Use cached page range if available
        cache_key = f"{self._current_page}_{total_pages}_{self._mode}"
        if cache_key in self._page_range_cache:
            page_range = self._page_range_cache[cache_key]
        else:
            page_range = self._calculate_optimized_page_range(total_pages)
            # Store in cache (limit cache size)
            if len(self._page_range_cache) > 20:
                self._page_range_cache.clear()
            self._page_range_cache[cache_key] = page_range

        # Create buttons with staggered animation
        buttons_to_animate = []

        for i, page_item in enumerate(page_range):
            if page_item == "...":
                ellipsis = self._create_ellipsis_label()
                self._page_buttons_layout.addWidget(ellipsis)
                buttons_to_animate.append(ellipsis)
            else:
                page_num = int(page_item)
                button = self._create_page_button(page_num)
                self._page_buttons_layout.addWidget(button)
                buttons_to_animate.append(button)

        # Staggered reveal animation (if enabled)
        if buttons_to_animate and self._animations_enabled:
            self._animate_buttons_reveal(buttons_to_animate)

    def _clear_page_buttons(self):
        """Efficiently clear page buttons"""
        while self._page_buttons_layout.count():
            item = self._page_buttons_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    # Cleanup enhanced buttons - only EnhancedPaginationButton has cleanup method
                    if isinstance(widget, EnhancedPaginationButton):
                        widget.cleanup()
                    widget.setParent(None)
                    widget.deleteLater()

    def _create_ellipsis_label(self) -> QLabel:
        """Create styled ellipsis label"""
        ellipsis = QLabel("...")
        ellipsis.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ellipsis.setFixedSize(36, 36)

        if self._cached_theme_colors:
            ellipsis.setStyleSheet(f"""
                QLabel {{
                    color: {self._cached_theme_colors['on_surface'].name()};
                    font-size: 16px;
                    font-weight: 500;
                }}
            """)

        return ellipsis

    def _create_page_button(self, page_num: int) -> EnhancedPaginationButton:
        """Create enhanced page button"""
        button = EnhancedPaginationButton(str(page_num))
        button.setToolTip(f"Go to page {page_num}")

        # Disable animations if needed
        if not self._animations_enabled:
            button.disable_animations()

        button.clicked.connect(lambda: self._on_page_button_clicked(page_num))

        # Set current state
        button.set_current(page_num == self._current_page)

        # Apply appropriate styling from cache
        is_current = page_num == self._current_page
        button.setStyleSheet(self._get_button_style(is_current))

        return button

    @lru_cache(maxsize=20)
    def _calculate_optimized_page_range(self, total_pages: int) -> List:
        """Calculate optimized page range for display with caching"""
        if total_pages <= 0:
            return []
        if total_pages <= 7:
            return list(range(1, total_pages + 1))

        current = self._current_page
        page_range = []

        # Always show first page
        page_range.append(1)

        # Calculate middle range
        if current <= 4:
            # Near beginning
            for i in range(2, min(6, total_pages)):
                page_range.append(i)
            if total_pages > 6:
                page_range.append("...")
        elif current >= total_pages - 3:
            # Near end
            if total_pages > 6:
                page_range.append("...")
            for i in range(max(total_pages - 4, 2), total_pages):
                page_range.append(i)
        else:
            # Middle
            page_range.append("...")
            for i in range(current - 1, current + 2):
                page_range.append(i)
            page_range.append("...")

        # Always show last page
        if total_pages > 1:
            page_range.append(total_pages)

        return page_range

    def _update_state(self):
        """Update state with debounced execution"""
        if not self._update_is_scheduled:
            self._update_is_scheduled = True
            self._update_timer.start(50)  # 50ms debounce

    def _perform_update(self):
        """Perform the actual state update"""
        self._update_is_scheduled = False

        if self._is_animating:
            # Reschedule if animations are running
            self._update_timer.start(50)
            return

        total_pages = self.get_total_pages()

        # Update navigation buttons
        self._update_navigation_buttons(total_pages)

        # Update total display
        self._update_total_display()

        # Update jumper
        self._update_jumper(total_pages)

        # Update page buttons
        self._update_page_buttons()

        # Update visibility
        self._update_visibility()

    def _update_navigation_buttons(self, total_pages: int):
        """Update navigation button states"""
        prev_enabled = self._current_page > 1
        next_enabled = self._current_page < total_pages and total_pages > 0

        if self._prev_button.isEnabled() != prev_enabled:
            self._prev_button.setEnabled(prev_enabled)
            if prev_enabled and self._animations_enabled:
                self._animate_button_enable(self._prev_button)

        if self._next_button.isEnabled() != next_enabled:
            self._next_button.setEnabled(next_enabled)
            if next_enabled and self._animations_enabled:
                self._animate_button_enable(self._next_button)

    def _animate_button_enable(self, button: QWidget):
        """Animate button enable state"""
        effect = QGraphicsOpacityEffect()
        button.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
        animation.setDuration(
            FluentAnimation.DURATION_FAST // 2)  # Faster animation
        animation.setStartValue(0.5)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(
            lambda: button.setGraphicsEffect(QGraphicsOpacityEffect()))
        animation.start()

        # Register animation for cleanup
        key = f"enable_{id(button)}_{id(animation)}"
        self._animation_registry[key] = animation
        animation.finished.connect(
            lambda: self._animation_registry.pop(key, None))

    def _update_total_display(self):
        """Update total items display with smooth transitions"""
        if not hasattr(self, '_total_label'):
            return

        if self._total == 0:
            new_text = "No items"
        else:
            start_item = (self._current_page - 1) * self._page_size + 1
            end_item = min(self._current_page * self._page_size, self._total)
            new_text = f"Showing {start_item}-{end_item} of {self._total:,} items"

        if self._total_label.text() != new_text:
            self._total_label.setText(new_text)
            if self._animations_enabled:
                self._animate_label_change(self._total_label)

    def _animate_label_change(self, label: QLabel):
        """Animate label text change"""
        effect = QGraphicsOpacityEffect()
        label.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
        animation.setDuration(
            FluentAnimation.DURATION_FAST // 2)  # Faster animation
        animation.setStartValue(0.7)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(
            lambda: label.setGraphicsEffect(QGraphicsOpacityEffect()))
        animation.start()

        # Register animation for cleanup
        key = f"label_{id(label)}_{id(animation)}"
        self._animation_registry[key] = animation
        animation.finished.connect(
            lambda: self._animation_registry.pop(key, None))

    def _update_jumper(self, total_pages: int):
        """Update jumper controls"""
        if not hasattr(self, '_jumper_spinbox'):
            return

        self._jumper_spinbox.blockSignals(True)
        self._jumper_spinbox.setMaximum(max(1, total_pages))
        self._jumper_spinbox.setValue(self._current_page)
        self._jumper_spinbox.setEnabled(total_pages > 1)
        self._jumper_spinbox.blockSignals(False)

    def _update_visibility(self):
        """Update control visibility with smooth animations"""
        is_simple_mode = self._mode == self.MODE_SIMPLE
        has_items = self._total > 0

        # Update visibility states
        if hasattr(self, '_total_label'):
            should_show = self._show_total and not is_simple_mode
            if self._animations_enabled:
                self._animate_widget_visibility(self._total_label, should_show)
            else:
                self._total_label.setVisible(should_show)

        if hasattr(self, '_page_size_label'):
            should_show = self._show_page_size and not is_simple_mode and has_items
            if self._animations_enabled:
                self._animate_widget_visibility(
                    self._page_size_label, should_show)
                self._animate_widget_visibility(
                    self._page_size_combo, should_show)
            else:
                self._page_size_label.setVisible(should_show)
                self._page_size_combo.setVisible(should_show)

        if hasattr(self, '_jumper_label'):
            should_show = self._show_jumper and not is_simple_mode and has_items
            if self._animations_enabled:
                self._animate_widget_visibility(
                    self._jumper_label, should_show)
                self._animate_widget_visibility(
                    self._jumper_spinbox, should_show)
            else:
                self._jumper_label.setVisible(should_show)
                self._jumper_spinbox.setVisible(should_show)

    def _animate_widget_visibility(self, widget: QWidget, should_show: bool):
        """Animate widget visibility changes"""
        if widget.isVisible() == should_show:
            return

        if should_show:
            widget.setVisible(True)
            effect = QGraphicsOpacityEffect()
            effect.setOpacity(0.0)
            widget.setGraphicsEffect(effect)

            animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
            animation.setDuration(FluentAnimation.DURATION_FAST)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation.finished.connect(
                lambda: widget.setGraphicsEffect(QGraphicsOpacityEffect()))
            animation.start()

            # Register animation for cleanup
            key = f"vis_show_{id(widget)}_{id(animation)}"
            self._animation_registry[key] = animation
            animation.finished.connect(
                lambda: self._animation_registry.pop(key, None))
        else:
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)

            animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
            animation.setDuration(
                FluentAnimation.DURATION_FAST // 2)  # Faster hide
            animation.setStartValue(1.0)
            animation.setEndValue(0.0)
            animation.setEasingCurve(QEasingCurve.Type.InCubic)
            animation.finished.connect(lambda: widget.setVisible(False))
            animation.start()

            # Register animation for cleanup
            key = f"vis_hide_{id(widget)}_{id(animation)}"
            self._animation_registry[key] = animation
            animation.finished.connect(
                lambda: self._animation_registry.pop(key, None))

    def _animate_buttons_reveal(self, buttons: List[QWidget]):
        """Animate buttons reveal with staggered effect"""
        # Don't animate more than a reasonable amount of buttons
        max_animated = min(10, len(buttons))
        buttons_to_animate = buttons[:max_animated] if max_animated < len(
            buttons) else buttons

        for i, button in enumerate(buttons_to_animate):
            # Start invisible
            effect = QGraphicsOpacityEffect()
            effect.setOpacity(0.0)
            button.setGraphicsEffect(effect)

            # Animate with delay (shorter delay)
            delay = min(i * 20, 200)  # Cap maximum delay
            QTimer.singleShot(delay, lambda b=button,
                              e=effect: self._animate_single_button_reveal(b, e))

        # For remaining buttons, just show them
        for button in buttons[max_animated:]:
            button.setGraphicsEffect(QGraphicsOpacityEffect())

    def _animate_single_button_reveal(self, button: QWidget, effect: QGraphicsOpacityEffect):
        """Animate single button reveal"""
        animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
        animation.setDuration(
            FluentAnimation.DURATION_FAST // 2)  # Faster animation
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(
            lambda: button.setGraphicsEffect(QGraphicsOpacityEffect()))
        animation.start()

        # Register animation for cleanup
        key = f"btn_reveal_{id(button)}_{id(animation)}"
        self._animation_registry[key] = animation
        animation.finished.connect(
            lambda: self._animation_registry.pop(key, None))

    def _play_entrance_animation(self):
        """Play entrance animation for the entire component"""
        if not self._animations_enabled:
            return

        effect = QGraphicsOpacityEffect()
        effect.setOpacity(0.0)
        self.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
        animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(
            lambda: self.setGraphicsEffect(QGraphicsOpacityEffect()))
        animation.start()

        # Register animation for cleanup
        key = f"entrance_{id(self)}_{id(animation)}"
        self._animation_registry[key] = animation
        animation.finished.connect(
            lambda: self._animation_registry.pop(key, None))

    def _on_page_button_clicked(self, page_num: int):
        """Handle page button click with smooth transition"""
        if page_num != self._current_page:
            self.set_current_page(page_num)

    def _on_page_size_changed(self, text: str):
        """Handle page size change with smart positioning"""
        try:
            new_size = int(text)
            if new_size <= 0 or new_size == self._page_size:
                return

            # Calculate new page to maintain data position
            old_first_item = (self._current_page - 1) * self._page_size + 1
            new_page = max(1, math.ceil(old_first_item / new_size))

            self._page_size = new_size
            self._current_page = new_page

            # Clear cached page ranges as they depend on page size
            self._page_range_cache.clear()

            self._update_state()
            self.page_size_changed.emit(new_size)

        except ValueError:
            # Reset to current value on invalid input
            if hasattr(self, '_page_size_combo'):
                self._page_size_combo.setCurrentText(str(self._page_size))

    def _on_jumper_changed(self, page: int):
        """Handle jumper page change"""
        if page != self._current_page and page >= 1:
            total_pages = self.get_total_pages()
            if page <= total_pages or total_pages == 0:
                self.set_current_page(page)

    def _go_prev_page(self):
        """Go to previous page with animation"""
        if self._current_page > 1:
            self.set_current_page(self._current_page - 1)

    def _go_next_page(self):
        """Go to next page with animation"""
        if self._current_page < self.get_total_pages():
            self.set_current_page(self._current_page + 1)

    def _on_theme_changed_debounced(self, theme_name: str):
        """Debounced theme change handler"""
        QTimer.singleShot(100, self._apply_theme_change)

    def _apply_theme_change(self):
        """Apply theme change with smooth transition"""
        self._cache_theme_colors()

        # Clear style caches
        self._get_button_style.cache_clear()

        if self._animations_enabled:
            # Smooth transition effect
            effect = QGraphicsOpacityEffect()
            self.setGraphicsEffect(effect)

            animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
            # Faster transition
            animation.setDuration(FluentAnimation.DURATION_FAST // 2)
            animation.setStartValue(1.0)
            animation.setKeyValueAt(0.5, 0.8)
            animation.setEndValue(1.0)
            animation.finished.connect(
                lambda: self.setGraphicsEffect(QGraphicsOpacityEffect()))

            self._update_style()
            animation.start()

            # Register animation for cleanup
            key = f"theme_{id(self)}_{id(animation)}"
            self._animation_registry[key] = animation
            animation.finished.connect(
                lambda: self._animation_registry.pop(key, None))
        else:
            self._update_style()

    # Public API methods
    def get_total_pages(self) -> int:
        """Get total number of pages"""
        if self._total == 0:
            return 0
        return max(1, math.ceil(self._total / self._page_size))

    def set_total(self, total: int):
        """Set total items with validation"""
        total = max(0, total)
        if total != self._total:
            self._total = total

            # Adjust current page if necessary
            total_pages = self.get_total_pages()
            if self._current_page > total_pages and total_pages > 0:
                self._current_page = total_pages
            elif total_pages == 0:
                self._current_page = 1

            # Clear cached page ranges as they depend on total
            self._page_range_cache.clear()

            self._update_state()

    def set_current_page(self, page: int):
        """Set current page with validation and smooth transition"""
        total_pages = self.get_total_pages()

        if total_pages == 0:
            new_page = 1
        else:
            new_page = max(1, min(page, total_pages))

        if new_page != self._current_page:
            self._current_page = new_page
            self._update_state()
            self.page_changed.emit(new_page)

    def set_page_size(self, size: int):
        """Set page size with smart positioning"""
        if size <= 0 or size == self._page_size:
            return

        # Maintain data position
        old_first_item = (self._current_page - 1) * self._page_size + 1
        self._page_size = size
        new_page = max(1, math.ceil(old_first_item / size))

        total_pages = self.get_total_pages()
        self._current_page = min(
            new_page, total_pages) if total_pages > 0 else 1

        # Update UI
        if hasattr(self, '_page_size_combo'):
            self._page_size_combo.blockSignals(True)
            self._page_size_combo.setCurrentText(str(size))
            self._page_size_combo.blockSignals(False)

        # Clear cached page ranges as they depend on page size
        self._page_range_cache.clear()

        self._update_state()
        self.page_size_changed.emit(size)

    def set_mode(self, mode: str):
        """Set display mode with smooth transition"""
        if mode in [self.MODE_SIMPLE, self.MODE_FULL, self.MODE_COMPACT] and mode != self._mode:
            self._mode = mode

            # Clear cached page ranges as they depend on mode
            self._page_range_cache.clear()

            self._update_state()

    def enable_animations(self):
        """Enable animations"""
        if not self._animations_enabled:
            self._animations_enabled = True
            self._prev_button.enable_animations()
            self._next_button.enable_animations()

            # Enable animations for all page buttons
            for i in range(self._page_buttons_layout.count()):
                widget = self._page_buttons_layout.itemAt(i).widget()
                if isinstance(widget, EnhancedPaginationButton):
                    widget.enable_animations()

    def disable_animations(self):
        """Disable animations for performance"""
        if self._animations_enabled:
            self._animations_enabled = False
            self._prev_button.disable_animations()
            self._next_button.disable_animations()

            # Disable animations for all page buttons
            for i in range(self._page_buttons_layout.count()):
                widget = self._page_buttons_layout.itemAt(i).widget()
                if isinstance(widget, EnhancedPaginationButton):
                    widget.disable_animations()

    # Getters
    def get_current_page(self) -> int:
        return self._current_page

    def get_page_size(self) -> int:
        return self._page_size

    def get_total(self) -> int:
        return self._total

    def cleanup(self):
        """Cleanup resources and animations"""
        # Stop all timers
        self._update_timer.stop()

        # Stop and clear all animations
        for anim_key, anim in list(self._animation_registry.items()):
            if anim and hasattr(anim, 'stop'):
                anim.stop()
        self._animation_registry.clear()

        # Clear page buttons
        self._clear_page_buttons()

        # Clear caches
        self._cached_theme_colors.clear()
        self._page_buttons_cache.clear()
        self._page_range_cache.clear()

        # Clear LRU caches
        self._calculate_optimized_page_range.cache_clear()
        self._get_button_style.cache_clear()

        # Cleanup navigation buttons
        if hasattr(self, '_prev_button') and hasattr(self._prev_button, 'cleanup'):
            self._prev_button.cleanup()
        if hasattr(self, '_next_button') and hasattr(self._next_button, 'cleanup'):
            self._next_button.cleanup()

    def __del__(self):
        """Destructor with cleanup"""
        self.cleanup()


class FluentSimplePagination(QWidget):
    """
    Enhanced Simple Pagination Component with Modern Animations
    """

    page_changed = Signal(int)

    def __init__(self,
                 current_page: int = 1,
                 has_prev: bool = False,
                 has_next: bool = True,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._current_page = current_page
        self._has_prev = has_prev
        self._has_next = has_next

        # Performance optimization
        self._cached_colors = {}
        self._animation_registry = {}
        self._animations_enabled = True
        self._update_pending = False

        # Check performance mode
        self._check_performance_mode()

        # Debounce timer
        self._update_timer = QTimer(self)
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._perform_update)

        self._setup_ui()
        self._connect_signals()
        self._update_state()

        # Entrance animation
        self._play_entrance_animation()

    def _check_performance_mode(self):
        """Check system performance and adjust settings"""
        import os
        low_performance = os.environ.get('LOW_PERFORMANCE_MODE') == '1'
        self._animations_enabled = not low_performance

    def _setup_ui(self):
        """Setup enhanced UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(16)

        # Enhanced previous button
        self._prev_button = EnhancedPaginationButton("‹ Previous")
        self._prev_button.setFixedHeight(40)
        self._prev_button.setMinimumWidth(100)
        self._prev_button.setToolTip("Go to previous page")
        self._prev_button.clicked.connect(self._go_prev_page)

        # Disable animations if needed
        if not self._animations_enabled:
            self._prev_button.disable_animations()

        # Page info with modern styling
        self._page_label = QLabel()
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._page_label.setMinimumWidth(120)

        # Enhanced next button
        self._next_button = EnhancedPaginationButton("Next ›")
        self._next_button.setFixedHeight(40)
        self._next_button.setMinimumWidth(100)
        self._next_button.setToolTip("Go to next page")
        self._next_button.clicked.connect(self._go_next_page)

        # Disable animations if needed
        if not self._animations_enabled:
            self._next_button.disable_animations()

        layout.addWidget(self._prev_button)
        layout.addStretch()
        layout.addWidget(self._page_label)
        layout.addStretch()
        layout.addWidget(self._next_button)

    def _connect_signals(self):
        """Connect signals and setup styling"""
        if theme_manager:
            theme_manager.theme_changed.connect(self._update_style)
        self._update_style()

    def _update_style(self):
        """Update component styling"""
        if not theme_manager:
            return

        colors = {
            'surface': theme_manager.get_color('surface'),
            'primary': theme_manager.get_color('primary'),
            'on_surface': theme_manager.get_color('on_surface'),
            'on_primary': theme_manager.get_color('on_primary'),
            'border': theme_manager.get_color('border'),
            'surface_variant': theme_manager.get_color('surface_variant'),
            'outline': theme_manager.get_color('outline')
        }

        # Cache colors
        self._cached_colors = colors

        button_style = f"""
            EnhancedPaginationButton {{
                background-color: {colors['surface'].name()};
                color: {colors['on_surface'].name()};
                border: 1px solid {colors['border'].name()};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 600;
            }}
            EnhancedPaginationButton:hover:enabled {{
                background-color: {colors['primary'].lighter(130).name()};
                border-color: {colors['primary'].name()};
                color: {colors['on_primary'].name()};
            }}
            EnhancedPaginationButton:pressed:enabled {{
                background-color: {colors['primary'].name()};
            }}
            EnhancedPaginationButton:disabled {{
                background-color: {colors['surface_variant'].name()};
                color: {colors['on_surface'].darker(150).name()};
                border-color: {colors['outline'].name()};
                opacity: 0.6;
            }}
        """

        self._prev_button.setStyleSheet(button_style)
        self._next_button.setStyleSheet(button_style)

        self._page_label.setStyleSheet(f"""
            QLabel {{
                color: {colors['on_surface'].name()};
                font-size: 16px;
                font-weight: 600;
                padding: 8px 16px;
                background-color: {colors['surface'].lighter(105).name()};
                border-radius: 8px;
                border: 1px solid {colors['border'].name()};
            }}
        """)

    def _perform_update(self):
        """Execute the actual update"""
        self._update_pending = False
        super().update()

    def _update_state(self):
        """Update state with smooth transitions"""
        # Update button states
        if self._prev_button.isEnabled() != self._has_prev:
            self._prev_button.setEnabled(self._has_prev)
            if self._has_prev and self._animations_enabled:
                self._animate_button_state_change(self._prev_button, True)

        if self._next_button.isEnabled() != self._has_next:
            self._next_button.setEnabled(self._has_next)
            if self._has_next and self._animations_enabled:
                self._animate_button_state_change(self._next_button, True)

        # Update page label
        new_text = f"Page {self._current_page}"
        if self._page_label.text() != new_text:
            self._page_label.setText(new_text)
            if self._animations_enabled:
                self._animate_label_update()

    def _animate_button_state_change(self, button: EnhancedPaginationButton, enabled: bool):
        """Animate button state change"""
        if enabled:
            effect = QGraphicsOpacityEffect()
            button.setGraphicsEffect(effect)

            animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
            animation.setDuration(
                FluentAnimation.DURATION_FAST // 2)  # Faster animation
            animation.setStartValue(0.5)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation.finished.connect(
                lambda: button.setGraphicsEffect(QGraphicsOpacityEffect()))
            animation.start()

            # Register animation for cleanup
            key = f"btn_state_{id(button)}_{id(animation)}"
            self._animation_registry[key] = animation
            animation.finished.connect(
                lambda: self._animation_registry.pop(key, None))

    def _animate_label_update(self):
        """Animate label text update"""
        effect = QGraphicsOpacityEffect()
        self._page_label.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
        animation.setDuration(
            FluentAnimation.DURATION_FAST // 2)  # Faster animation
        animation.setStartValue(0.7)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(
            lambda: self._page_label.setGraphicsEffect(QGraphicsOpacityEffect()))
        animation.start()

        # Register animation for cleanup
        key = f"label_update_{id(self._page_label)}_{id(animation)}"
        self._animation_registry[key] = animation
        animation.finished.connect(
            lambda: self._animation_registry.pop(key, None))

    def _play_entrance_animation(self):
        """Play entrance animation"""
        if not self._animations_enabled:
            return

        widgets = [self._prev_button, self._page_label, self._next_button]

        for i, widget in enumerate(widgets):
            effect = QGraphicsOpacityEffect()
            effect.setOpacity(0.0)
            widget.setGraphicsEffect(effect)

            # Use shorter delays
            delay = i * 50
            QTimer.singleShot(delay, lambda w=widget,
                              e=effect: self._animate_widget_entrance(w, e))

    def _animate_widget_entrance(self, widget: QWidget, effect: QGraphicsOpacityEffect):
        """Animate individual widget entrance"""
        animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
        animation.setDuration(
            FluentAnimation.DURATION_FAST)  # Faster animation
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(
            lambda: widget.setGraphicsEffect(QGraphicsOpacityEffect()))
        animation.start()

        # Register animation for cleanup
        key = f"widget_entrance_{id(widget)}_{id(animation)}"
        self._animation_registry[key] = animation
        animation.finished.connect(
            lambda: self._animation_registry.pop(key, None))

    def _go_prev_page(self):
        """Go to previous page with animation"""
        if self._has_prev:
            self._current_page -= 1
            self.page_changed.emit(self._current_page)
            self._update_state()

    def _go_next_page(self):
        """Go to next page with animation"""
        if self._has_next:
            self._current_page += 1
            self.page_changed.emit(self._current_page)
            self._update_state()

    def set_page_info(self, current_page: int, has_prev: bool, has_next: bool):
        """Set page information with smooth transitions"""
        changed = (self._current_page != current_page or
                   self._has_prev != has_prev or
                   self._has_next != has_next)

        if changed:
            self._current_page = current_page
            self._has_prev = has_prev
            self._has_next = has_next
            self._update_state()

    def enable_animations(self):
        """Enable animations"""
        if not self._animations_enabled:
            self._animations_enabled = True
            self._prev_button.enable_animations()
            self._next_button.enable_animations()

    def disable_animations(self):
        """Disable animations for performance"""
        if self._animations_enabled:
            self._animations_enabled = False
            self._prev_button.disable_animations()
            self._next_button.disable_animations()

    def get_current_page(self) -> int:
        """Get current page"""
        return self._current_page

    def cleanup(self):
        """Cleanup resources"""
        # Stop all timers
        if hasattr(self, '_update_timer'):
            self._update_timer.stop()

        # Stop and clear all animations
        for anim_key, anim in list(self._animation_registry.items()):
            if anim and hasattr(anim, 'stop'):
                anim.stop()
        self._animation_registry.clear()

        # Clear cached colors
        self._cached_colors.clear()

        # Cleanup enhanced buttons
        if hasattr(self, '_prev_button') and hasattr(self._prev_button, 'cleanup'):
            self._prev_button.cleanup()
        if hasattr(self, '_next_button') and hasattr(self._next_button, 'cleanup'):
            self._next_button.cleanup()

    def __del__(self):
        """Destructor with cleanup"""
        self.cleanup()
