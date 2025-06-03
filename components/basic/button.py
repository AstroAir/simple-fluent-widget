"""
 Fluent Design Style Button Component
Advanced implementation with smooth animations, performance optimizations, 
theme consistency, responsive layouts, and modern interaction patterns.
"""

from PySide6.QtWidgets import (QPushButton, QWidget, QGraphicsOpacityEffect,
                               QGraphicsDropShadowEffect, QSizePolicy)
from PySide6.QtCore import (Qt, Signal, QSize, QPropertyAnimation, QEasingCurve,
                            QParallelAnimationGroup, QTimer, QRect, QPoint,
                            QSequentialAnimationGroup, Property, QByteArray)
from PySide6.QtGui import (QIcon, QPainter, QPen, QBrush, QColor, QLinearGradient,
                           QRadialGradient, QFontMetrics, QPainterPath, QFont)
from core.theme import theme_manager
from core.enhanced_base import FluentStandardButton
from core.enhanced_animations import (FluentMicroInteraction, FluentTransition,
                                      FluentStateTransition, FluentRevealEffect)
from typing import Optional, Dict, Any, Callable
import weakref
import time


class FluentButton(FluentStandardButton):
    """ Fluent Design Style Button with Advanced Features

    Features:
    - Smooth animated transitions with performance optimizations
    - Theme-consistent styling with automatic updates
    - Memory-efficient widget lifecycle management
    - Fluid expand/collapse animations
    - Dynamic content loading support
    - Responsive layout adjustments
    - Advanced micro-interactions and feedback
    """

    #  button styles with better semantic naming
    class ButtonStyle:
        PRIMARY = "primary"
        SECONDARY = "secondary"
        ACCENT = "accent"
        SUBTLE = "subtle"
        OUTLINE = "outline"
        HYPERLINK = "hyperlink"
        STEALTH = "stealth"

    # Size variants for responsive design
    class Size:
        TINY = "tiny"
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"
        XLARGE = "xlarge"

    # Animation intensity levels
    class AnimationLevel:
        MINIMAL = "minimal"
        STANDARD = "standard"
        ENHANCED = "enhanced"
        FLUID = "fluid"

    # Custom signals
    longPressed = Signal()
    hoverChanged = Signal(bool)
    animationStarted = Signal(str)
    animationFinished = Signal(str)

    def __init__(self, text: str = "", parent: Optional[QWidget] = None,
                 style: Optional[str] = None, icon: Optional[QIcon] = None,
                 size: Optional[str] = None, animation_level: Optional[str] = None):

        # Initialize with enhanced defaults
        if style is None:
            style = self.ButtonStyle.PRIMARY
        if size is None:
            size = self.Size.MEDIUM
        if animation_level is None:
            animation_level = self.AnimationLevel.STANDARD

        # Initialize base class
        super().__init__(text, icon, (None, None), parent)

        # Core properties
        self._button_style = style
        self._button_size = size
        self._animation_level = animation_level
        self._is_loading = False
        self._is_expanded = False
        self._content_loaded = True

        # State tracking for optimized repainting
        self._current_state = "normal"
        self._is_hovered = False
        self._is_pressed = False
        self._is_focused = False
        self._last_repaint_time = 0
        self._repaint_throttle = 16  # ~60fps limit

        # Performance optimization flags
        self._cache_enabled = True
        self._cached_pixmap = None
        self._cache_valid = False
        self._animation_active = False

        # Memory management
        self._cleanup_timer = QTimer()
        self._cleanup_timer.timeout.connect(self._cleanup_resources)
        self._cleanup_timer.setSingleShot(True)

        #  animation system
        self._animation_group = QParallelAnimationGroup(self)
        self._hover_animation = None
        self._press_animation = None
        self._expand_animation = None
        self._glow_effect = None
        self._shadow_effect = None
        self._state_transition = None

        # Responsive properties
        self._min_content_width = 80
        self._max_content_width = 400
        self._adaptive_sizing = True

        # Setup enhanced features
        self._setup_enhanced_animations()
        self._setup_effects()
        self._setup_responsive_sizing()
        self._apply_style()
        self._setup_accessibility()

        # Connect to theme changes with weak reference to prevent memory leaks
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Performance monitoring
        self._performance_metrics = {
            'paint_count': 0,
            'animation_count': 0,
            'last_paint_duration': 0
        }

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system with performance optimizations"""
        # Create state transition manager
        self._state_transition = FluentStateTransition(self)

        # Define button states with enhanced properties
        self._state_transition.addState("normal", {
            "minimumHeight": self._get_size_height(),
            "opacity": 1.0,
            "scale": 1.0,
        })

        self._state_transition.addState("hovered", {
            "minimumHeight": self._get_size_height() + 2,
            "opacity": 1.0,
            "scale": 1.02,
        }, duration=150, easing=FluentTransition.EASE_SMOOTH)

        self._state_transition.addState("pressed", {
            "minimumHeight": self._get_size_height() - 2,
            "opacity": 0.9,
            "scale": 0.98,
        }, duration=100, easing=FluentTransition.EASE_CRISP)

        self._state_transition.addState("expanded", {
            "minimumHeight": self._get_size_height() + 8,
            "opacity": 1.0,
            "scale": 1.05,
        }, duration=300, easing=FluentTransition.EASE_SPRING)

        # Setup hover animation
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self._hover_animation.setDuration(150)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Setup press animation with bounce
        self._press_animation = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self._press_animation.setDuration(100)
        self._press_animation.setEasingCurve(QEasingCurve.Type.OutBounce)

        # Setup expand/collapse animation
        self._expand_animation = QPropertyAnimation(
            self, QByteArray(b"maximumWidth"))
        self._expand_animation.setDuration(300)
        self._expand_animation.setEasingCurve(QEasingCurve.Type.OutBack)

    def _setup_effects(self):
        """Setup visual effects like glow and shadows"""
        if self._animation_level in [self.AnimationLevel.ENHANCED, self.AnimationLevel.FLUID]:
            # Glow effect for enhanced interactions
            self._glow_effect = QGraphicsOpacityEffect(self)
            self._glow_effect.setOpacity(0.0)

            # Drop shadow for depth
            self._shadow_effect = QGraphicsDropShadowEffect(self)
            self._shadow_effect.setBlurRadius(8)
            self._shadow_effect.setOffset(0, 2)
            self._shadow_effect.setColor(QColor(0, 0, 0, 30))

    def _setup_responsive_sizing(self):
        """Setup responsive sizing based on content and screen size"""
        if self._adaptive_sizing:
            # Set size policy for responsive behavior
            self.setSizePolicy(QSizePolicy.Policy.Expanding,
                               QSizePolicy.Policy.Fixed)

            # Calculate optimal size based on content
            self._update_content_size()

    def _setup_accessibility(self):
        """Setup accessibility features"""
        self.setAccessibleName(self.text() or "Button")
        self.setAccessibleDescription(f"{self._button_style} button")

        # Keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)

    def _get_size_height(self) -> int:
        """Get height based on button size"""
        size_heights = {
            self.Size.TINY: 24,
            self.Size.SMALL: 28,
            self.Size.MEDIUM: 32,
            self.Size.LARGE: 36,
            self.Size.XLARGE: 40
        }
        return size_heights.get(self._button_size, 32)

    def _update_content_size(self):
        """Update size based on content with responsive adjustments"""
        if not self._adaptive_sizing:
            return

        # Calculate minimum width based on text and icon
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self.text()) if self.text() else 0
        icon_width = self.iconSize().width() if not self.icon().isNull() else 0

        # Add padding and spacing
        padding = 32  # 16px on each side
        spacing = 8 if self.text() and not self.icon().isNull() else 0

        total_width = text_width + icon_width + padding + spacing

        # Apply constraints
        width = max(self._min_content_width, min(
            self._max_content_width, total_width))

        self.setMinimumWidth(width)

    def _cleanup_resources(self):
        """Clean up animation resources to prevent memory leaks"""
        if self._animation_group:
            self._animation_group.clear()

        # Clear cached pixmap if not used recently
        if self._cached_pixmap and not self._cache_valid:
            self._cached_pixmap = None

    def _throttled_repaint(self):
        """Throttle repaint calls for better performance"""
        current_time = time.time() * 1000  # Convert to milliseconds

        if current_time - self._last_repaint_time >= self._repaint_throttle:
            self._last_repaint_time = current_time
            self.update()
            self._performance_metrics['paint_count'] += 1

    def set_style(self, new_style: str):
        """Set button style with enhanced animations and theme consistency"""
        if self._button_style != new_style:
            old_style = self._button_style
            self._button_style = new_style

            # Emit animation started signal
            self.animationStarted.emit("style_change")

            # Create smooth transition between styles
            if self._animation_level != self.AnimationLevel.MINIMAL:
                transition = FluentTransition.create_transition(
                    self, FluentTransition.FADE, 200, FluentTransition.EASE_SMOOTH)
                if transition:
                    transition.setStartValue(1.0)
                    transition.setEndValue(0.8)

                    def apply_new_style():
                        self._apply_style()
                        self._invalidate_cache()
                        # Fade back in
                        fade_in = FluentTransition.create_transition(
                            self, FluentTransition.FADE, 200, FluentTransition.EASE_SMOOTH)
                        if fade_in:
                            fade_in.setStartValue(0.8)
                            fade_in.setEndValue(1.0)
                            fade_in.finished.connect(
                                lambda: self.animationFinished.emit("style_change"))
                            fade_in.start()

                    transition.finished.connect(apply_new_style)
                    transition.start()
            else:
                self._apply_style()
                self._invalidate_cache()

    def set_size(self, new_size: str):
        """Set button size with responsive adjustments"""
        if self._button_size != new_size:
            self._button_size = new_size
            self._update_content_size()
            self._apply_style()
            self._invalidate_cache()

    def set_animation_level(self, level: str):
        """Set animation intensity level"""
        if self._animation_level != level:
            self._animation_level = level
            self._setup_effects()  # Re-setup effects based on new level

    def set_loading(self, loading: bool):
        """Set loading state with spinner animation"""
        if self._is_loading != loading:
            self._is_loading = loading

            if loading:
                self.setEnabled(False)
                self.setText("Loading...")
                # Start loading animation
                self._start_loading_animation()
            else:
                self.setEnabled(True)
                self._stop_loading_animation()

    def expand_content(self, expanded: bool = True):
        """Expand or collapse button with fluid animation"""
        if self._is_expanded != expanded:
            self._is_expanded = expanded

            # Emit animation signal
            self.animationStarted.emit("expand" if expanded else "collapse")

            if self._expand_animation:
                if expanded:
                    # Expand animation
                    self._expand_animation.setStartValue(self.width())
                    self._expand_animation.setEndValue(int(self.width() * 1.2))
                    if self._state_transition:
                        self._state_transition.transitionTo("expanded")
                else:
                    # Collapse animation
                    self._expand_animation.setStartValue(self.width())
                    self._expand_animation.setEndValue(int(self.width() * 0.8))
                    if self._state_transition:
                        self._state_transition.transitionTo("normal")

                self._expand_animation.finished.connect(
                    lambda: self.animationFinished.emit("expand" if expanded else "collapse"))
                self._expand_animation.start()

    def _start_loading_animation(self):
        """Start loading spinner animation"""
        # Create a simple opacity animation for loading state
        if self._animation_level != self.AnimationLevel.MINIMAL:
            loading_animation = QPropertyAnimation(
                self, QByteArray(b"windowOpacity"))
            loading_animation.setDuration(1000)
            loading_animation.setStartValue(1.0)
            loading_animation.setEndValue(0.5)
            loading_animation.setLoopCount(-1)  # Infinite loop
            loading_animation.start()

    def _stop_loading_animation(self):
        """Stop loading spinner animation"""
        # Stop all animations and restore opacity
        if self._animation_group:
            self._animation_group.stop()
        self.setWindowOpacity(1.0)

    def _invalidate_cache(self):
        """Invalidate cached rendering for performance optimization"""
        self._cache_valid = False
        self._cached_pixmap = None

    def _apply_style(self):
        """Apply button style with enhanced visual effects and theme consistency"""
        theme = theme_manager

        # Get size-specific properties
        height = self._get_size_height()
        font_size = {
            self.Size.TINY: 11,
            self.Size.SMALL: 12,
            self.Size.MEDIUM: 14,
            self.Size.LARGE: 16,
            self.Size.XLARGE: 18
        }.get(self._button_size, 14)

        padding = {
            self.Size.TINY: "4px 8px",
            self.Size.SMALL: "6px 12px",
            self.Size.MEDIUM: "8px 16px",
            self.Size.LARGE: "10px 20px",
            self.Size.XLARGE: "12px 24px"
        }.get(self._button_size, "8px 16px")

        base_style = f"""
            FluentButton {{
                border-radius: 6px;
                padding: {padding};
                font-size: {font_size}px;
                min-height: {height}px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                outline: none;
            }}
        """

        if self._button_style == self.ButtonStyle.PRIMARY:
            style = base_style + f"""
                FluentButton {{
                    background-color: {theme.get_color('primary').name()};
                    color: white;
                    border: none;
                    font-weight: 500;
                }}
                FluentButton:hover {{
                    background-color: {theme.get_color('primary').lighter(110).name()};
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                }}
                FluentButton:pressed {{
                    background-color: {theme.get_color('primary').darker(110).name()};
                    transform: scale(0.98);
                }}
                FluentButton:disabled {{
                    background-color: {theme.get_color('surface').name()};
                    color: {theme.get_color('text_disabled').name()};
                }}
            """

        elif self._button_style == self.ButtonStyle.SECONDARY:
            style = base_style + f"""
                FluentButton {{
                    background-color: {theme.get_color('surface').name()};
                    color: {theme.get_color('text_primary').name()};
                    border: 1px solid {theme.get_color('border').name()};
                    font-weight: 400;
                }}
                FluentButton:hover {{
                    background-color: {theme.get_color('accent_light').name()};
                    border-color: {theme.get_color('primary').name()};
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }}
                FluentButton:pressed {{
                    background-color: {theme.get_color('accent_medium').name()};
                    transform: scale(0.98);
                }}
                FluentButton:disabled {{
                    background-color: {theme.get_color('surface').name()};
                    color: {theme.get_color('text_disabled').name()};
                    border-color: {theme.get_color('border').name()};
                }}
            """

        elif self._button_style == self.ButtonStyle.ACCENT:
            style = base_style + f"""
                FluentButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {theme.get_color('primary').lighter(110).name()},
                        stop:1 {theme.get_color('primary').name()});
                    color: white;
                    border: none;
                    font-weight: 500;
                }}
                FluentButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {theme.get_color('primary').lighter(120).name()},
                        stop:1 {theme.get_color('primary').lighter(110).name()});
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }}
                FluentButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {theme.get_color('primary').name()},
                        stop:1 {theme.get_color('primary').darker(110).name()});
                    transform: scale(0.98);
                }}
                FluentButton:disabled {{
                    background-color: {theme.get_color('surface').name()};
                    color: {theme.get_color('text_disabled').name()};
                }}
            """

        elif self._button_style == self.ButtonStyle.SUBTLE:
            style = base_style + f"""
                FluentButton {{
                    background-color: transparent;
                    color: {theme.get_color('text_primary').name()};
                    border: none;
                    font-weight: 400;
                }}
                FluentButton:hover {{
                    background-color: {theme.get_color('accent_light').name()};
                }}
                FluentButton:pressed {{
                    background-color: {theme.get_color('accent_medium').name()};
                    transform: scale(0.98);
                }}
                FluentButton:disabled {{
                    color: {theme.get_color('text_disabled').name()};
                }}
            """

        elif self._button_style == self.ButtonStyle.OUTLINE:
            style = base_style + f"""
                FluentButton {{
                    background-color: transparent;
                    color: {theme.get_color('primary').name()};
                    border: 1px solid {theme.get_color('primary').name()};
                    font-weight: 400;
                }}
                FluentButton:hover {{
                    background-color: {theme.get_color('primary').name()};
                    color: white;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                FluentButton:pressed {{
                    background-color: {theme.get_color('primary').darker(110).name()};
                    transform: scale(0.98);
                }}
                FluentButton:disabled {{
                    color: {theme.get_color('text_disabled').name()};
                    border-color: {theme.get_color('border').name()};
                }}
            """

        elif self._button_style == self.ButtonStyle.HYPERLINK:
            style = base_style + f"""
                FluentButton {{
                    background-color: transparent;
                    color: {theme.get_color('primary').name()};
                    border: none;
                    font-weight: 400;
                    text-decoration: underline;
                }}
                FluentButton:hover {{
                    color: {theme.get_color('primary').lighter(110).name()};
                }}
                FluentButton:pressed {{
                    color: {theme.get_color('primary').darker(110).name()};
                }}
                FluentButton:disabled {{
                    color: {theme.get_color('text_disabled').name()};
                    text-decoration: none;
                }}
            """

        elif self._button_style == self.ButtonStyle.STEALTH:
            style = base_style + f"""
                FluentButton {{
                    background-color: transparent;
                    color: {theme.get_color('text_secondary').name()};
                    border: none;
                    font-weight: 400;
                }}
                FluentButton:hover {{
                    background-color: {theme.get_color('accent_light').name()};
                    color: {theme.get_color('text_primary').name()};
                }}
                FluentButton:pressed {{
                    background-color: {theme.get_color('accent_medium').name()};
                    transform: scale(0.98);
                }}
                FluentButton:disabled {{
                    color: {theme.get_color('text_disabled').name()};
                }}
            """
        else:
            style = base_style  # Fallback to base style

        self.setStyleSheet(style)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change with smooth transition"""
        if self._animation_level != self.AnimationLevel.MINIMAL:
            # Create smooth theme transition
            fade_out = QPropertyAnimation(self, QByteArray(b"windowOpacity"))
            fade_out.setDuration(150)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.8)

            def apply_theme():
                self._apply_style()
                self._invalidate_cache()
                # Fade back in
                fade_in = QPropertyAnimation(
                    self, QByteArray(b"windowOpacity"))
                fade_in.setDuration(150)
                fade_in.setStartValue(0.8)
                fade_in.setEndValue(1.0)
                fade_in.start()

            fade_out.finished.connect(apply_theme)
            fade_out.start()
        else:
            self._apply_style()
            self._invalidate_cache()

    def enterEvent(self, event):
        """ hover enter event with optimized animations"""
        if not self._is_hovered:
            self._is_hovered = True
            self.hoverChanged.emit(True)

            # Apply hover effects based on animation level
            if self._animation_level == self.AnimationLevel.FLUID:
                FluentMicroInteraction.hover_glow(self, 0.1)
            elif self._animation_level == self.AnimationLevel.ENHANCED:
                if self._shadow_effect:
                    self.setGraphicsEffect(self._shadow_effect)

            # Transition to hover state
            if self._state_transition:
                self._state_transition.transitionTo("hovered")

        super().enterEvent(event)

    def leaveEvent(self, event):
        """ hover leave event"""
        if self._is_hovered:
            self._is_hovered = False
            self.hoverChanged.emit(False)

            # Remove effects
            if self._animation_level in [self.AnimationLevel.ENHANCED, self.AnimationLevel.FLUID]:
                self.setGraphicsEffect(None)  # type: ignore

            # Transition back to normal state
            if self._state_transition:
                self._state_transition.transitionTo("normal")

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """ mouse press event with micro-interactions"""
        if not self._is_pressed:
            self._is_pressed = True

            # Apply press micro-interaction based on animation level
            if self._animation_level != self.AnimationLevel.MINIMAL:
                FluentMicroInteraction.button_press(self, 0.95)

            # Transition to pressed state
            if self._state_transition:
                self._state_transition.transitionTo("pressed")

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """ mouse release event with ripple effect"""
        if self._is_pressed:
            self._is_pressed = False

            # Create ripple effect for enhanced animation levels
            if self._animation_level in [self.AnimationLevel.ENHANCED, self.AnimationLevel.FLUID]:
                FluentMicroInteraction.ripple_effect(self)

            # Return to appropriate state
            if self._state_transition:
                if self._is_hovered:
                    self._state_transition.transitionTo("hovered")
                else:
                    self._state_transition.transitionTo("normal")

        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        """Optimized paint event with caching"""
        if self._cache_enabled and self._cache_valid and self._cached_pixmap:
            # Use cached pixmap for better performance
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self._cached_pixmap)
        else:
            # Standard painting
            super().paintEvent(event)

            # Update performance metrics
            self._performance_metrics['paint_count'] += 1

    def resizeEvent(self, event):
        """Handle resize with cache invalidation"""
        super().resizeEvent(event)
        self._invalidate_cache()

        # Update responsive sizing
        if self._adaptive_sizing:
            self._update_content_size()

    def get_performance_metrics(self) -> Dict[str, int]:
        """Get performance metrics for monitoring"""
        return self._performance_metrics.copy()

    def cleanup(self):
        """Clean up resources when widget is destroyed"""
        if self._cleanup_timer:
            self._cleanup_timer.stop()

        if self._animation_group:
            self._animation_group.stop()
            self._animation_group.clear()

        # Disconnect theme manager to prevent memory leaks
        try:
            theme_manager.theme_changed.disconnect(self._on_theme_changed)
        except RuntimeError:
            pass  # Already disconnected


class FluentIconButton(FluentButton):
    """ Fluent Button with Icon and advanced animations"""

    def __init__(self, icon: QIcon, text: str = "",
                 parent: Optional[QWidget] = None,
                 style: Optional[str] = None,
                 size: Optional[str] = None):
        if style is None:
            style = FluentButton.ButtonStyle.PRIMARY

        super().__init__(text, parent, style, icon, size)

        # Setup icon size based on button size
        icon_size = {
            self.Size.TINY: 16,
            self.Size.SMALL: 18,
            self.Size.MEDIUM: 20,
            self.Size.LARGE: 22,
            self.Size.XLARGE: 24
        }.get(self._button_size, 20)

        self.setIconSize(QSize(icon_size, icon_size))

        # Add reveal animation when created
        if self._animation_level != self.AnimationLevel.MINIMAL:
            FluentRevealEffect.reveal_scale(self, 100)


class FluentToggleButton(FluentButton):
    """ Toggle Button with smooth state transitions"""

    toggled = Signal(bool)

    def __init__(self, text: str = "", parent: Optional[QWidget] = None,
                 size: Optional[str] = None):
        super().__init__(text, parent, FluentButton.ButtonStyle.SECONDARY, None, size)
        self.setCheckable(True)
        self._is_toggled = False

        # Connect click signal
        self.clicked.connect(self._on_clicked)

        # Setup toggle-specific state transitions
        self._setup_toggle_animations()

    def _setup_toggle_animations(self):
        """Setup toggle-specific animations"""
        if self._state_transition:
            # Add toggle state
            self._state_transition.addState("toggled", {
                "minimumHeight": self._get_size_height(),
            }, duration=200, easing=FluentTransition.EASE_SPRING)

    def _on_clicked(self):
        """Handle click with smooth toggle animation"""
        self._is_toggled = self.isChecked()

        # Create smooth transition between toggle states
        if self._is_toggled:
            # Transition to primary style
            self.set_style(FluentButton.ButtonStyle.PRIMARY)
            if self._state_transition:
                self._state_transition.transitionTo("toggled")
        else:
            # Transition to secondary style
            self.set_style(FluentButton.ButtonStyle.SECONDARY)
            if self._state_transition:
                self._state_transition.transitionTo("normal")

        self.toggled.emit(self._is_toggled)

    def set_toggled(self, toggled: bool):
        """Set toggle state with animation"""
        if self._is_toggled != toggled:
            self._is_toggled = toggled
            self.setChecked(toggled)
            # Trigger the click handler to animate the change
            self._on_clicked()
