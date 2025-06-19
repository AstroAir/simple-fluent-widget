"""
Enhanced Fluent Design style dropdown components with improved animations and performance
"""

from PySide6.QtWidgets import (QComboBox, QWidget, QVBoxLayout, QHBoxLayout,
                               QListWidget, QListWidgetItem, QPushButton,
                               QScrollArea, QLineEdit, QGraphicsDropShadowEffect,
                               QCheckBox, QGraphicsOpacityEffect)
from PySide6.QtCore import (Qt, Signal, QPropertyAnimation, QRect, QByteArray,
                            QTimer, QEasingCurve, QSignalBlocker)
from PySide6.QtGui import QIcon, QColor, QPainter
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional, List, Any, Dict, Callable
import weakref


# Performance configuration to adjust based on device capabilities
class PerformanceConfig:
    """Configuration to optimize performance based on device capabilities"""
    LOW_PERFORMANCE_MODE = False  # Set to True for low-end devices
    ANIMATION_DURATION_SCALE = 1.0  # Reduce to speed up animations
    USE_SHADOWS = True  # Disable for better performance on low-end devices
    MAX_CACHED_ANIMATIONS = 100  # Limit animation cache size

    @classmethod
    def scale_duration(cls, duration: int) -> int:
        """Scale animation duration based on performance settings"""
        return int(duration * cls.ANIMATION_DURATION_SCALE)

    @classmethod
    def should_use_shadows(cls) -> bool:
        """Check if shadows should be used based on performance settings"""
        return cls.USE_SHADOWS

    @classmethod
    def should_use_advanced_effects(cls) -> bool:
        """Check if advanced effects should be used"""
        return not cls.LOW_PERFORMANCE_MODE


# Style caching system to avoid expensive QSS parsing
class StyleCache:
    """Cache for stylesheets to avoid regenerating them"""
    _style_cache: Dict[str, str] = {}

    @classmethod
    def get_style(cls, key: str, generator: Callable[[], str]) -> str:
        """Get cached style or generate it if not cached"""
        if key not in cls._style_cache:
            cls._style_cache[key] = generator()
        return cls._style_cache[key]

    @classmethod
    def clear_cache(cls):
        """Clear style cache, usually on theme change"""
        cls._style_cache.clear()


class FluentComboBoxStyle:
    """Centralized style management for all ComboBox components"""

    _cached_base_styles: Dict[str, Dict[str, str]] = {}

    @staticmethod
    def get_base_styles() -> Dict[str, str]:
        """Get base styles for consistency across all components with caching"""
        theme_mode = theme_manager.get_theme_mode()

        if theme_mode not in FluentComboBoxStyle._cached_base_styles:
            theme = theme_manager
            FluentComboBoxStyle._cached_base_styles[theme_mode] = {
                "primary": theme.get_color('primary').name(),
                "secondary": theme.get_color('secondary').name(),
                "surface": theme.get_color('surface').name(),
                "background": theme.get_color('background').name(),
                "card": theme.get_color('card').name(),
                "border": theme.get_color('border').name(),
                "text_primary": theme.get_color('text_primary').name(),
                "text_secondary": theme.get_color('text_secondary').name(),
                "text_disabled": theme.get_color('text_disabled').name(),
                "accent_light": theme.get_color('accent_light').name(),
                "accent_medium": theme.get_color('accent_medium').name(),
                "accent_dark": theme.get_color('accent_dark').name(),
            }

        return FluentComboBoxStyle._cached_base_styles[theme_mode]

    @staticmethod
    def get_combobox_style() -> str:
        """Get unified ComboBox style with caching"""
        theme_mode = theme_manager.get_theme_mode()
        cache_key = f"combobox_style_{theme_mode}"

        return StyleCache.get_style(cache_key, lambda: FluentComboBoxStyle._generate_combobox_style())

    @staticmethod
    def _generate_combobox_style() -> str:
        """Generate ComboBox style without caching"""
        colors = FluentComboBoxStyle.get_base_styles()

        return f"""
            QComboBox {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                font-weight: 400;
                color: {colors['text_primary']};
                selection-background-color: {colors['primary']};
                min-height: 20px;
            }}
            QComboBox:hover {{
                border-color: {colors['primary']};
                background-color: {colors['accent_light']};
            }}
            QComboBox:focus {{
                border-color: {colors['primary']};
                border-width: 2px;
                padding: 9px 13px;
                background-color: {colors['surface']};
            }}
            QComboBox:disabled {{
                background-color: {colors['background']};
                border-color: {colors['border']};
                color: {colors['text_disabled']};
                opacity: 0.6;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 32px;
                background: transparent;
                border-radius: 6px;
                margin-right: 4px;
            }}
            QComboBox::drop-down:hover {{
                background-color: {colors['accent_light']};
            }}
            QComboBox::down-arrow {{
                image: none;
                border-style: solid;
                border-width: 4px 4px 0 4px;
                border-color: {colors['text_primary']} transparent transparent transparent;
                width: 0;
                height: 0;
                margin: 8px;
            }}
            QComboBox::down-arrow:hover {{
                border-top-color: {colors['primary']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
                selection-background-color: {colors['primary']};
                selection-color: white;
                padding: 8px;
                outline: none;
                margin-top: 4px;
                show-decoration-selected: 1;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 12px 16px;
                border-radius: 8px;
                margin: 2px;
                border: none;
                min-height: 20px;
                color: {colors['text_primary']};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {colors['accent_light']};
                color: {colors['text_primary']};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {colors['primary']};
                color: white;
                font-weight: 500;
            }}
            QComboBox QAbstractItemView::item:selected:hover {{
                background-color: {colors['accent_dark']};
                color: white;
            }}
        """

    @staticmethod
    def get_button_style() -> str:
        """Get unified button style with caching"""
        theme_mode = theme_manager.get_theme_mode()
        cache_key = f"button_style_{theme_mode}"

        return StyleCache.get_style(cache_key, lambda: FluentComboBoxStyle._generate_button_style())

    @staticmethod
    def _generate_button_style() -> str:
        """Generate button style without caching"""
        colors = FluentComboBoxStyle.get_base_styles()

        return f"""
            QPushButton {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: 400;
                color: {colors['text_primary']};
                text-align: left;
                min-height: 20px;
            }}
            QPushButton:hover {{
                border-color: {colors['primary']};
                background-color: {colors['accent_light']};
            }}
            QPushButton:pressed {{
                background-color: {colors['accent_medium']};
            }}
            QPushButton:disabled {{
                background-color: {colors['background']};
                border-color: {colors['border']};
                color: {colors['text_disabled']};
                opacity: 0.6;
            }}
        """

    @staticmethod
    def get_list_style() -> str:
        """Get unified list widget style with caching"""
        theme_mode = theme_manager.get_theme_mode()
        cache_key = f"list_style_{theme_mode}"

        return StyleCache.get_style(cache_key, lambda: FluentComboBoxStyle._generate_list_style())

    @staticmethod
    def _generate_list_style() -> str:
        """Generate list style without caching"""
        colors = FluentComboBoxStyle.get_base_styles()

        return f"""
            QListWidget {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
                outline: none;
                padding: 8px;
            }}
            QListWidget::item {{
                padding: 12px 16px;
                border-radius: 8px;
                margin: 2px;
                color: {colors['text_primary']};
                border: none;
                min-height: 20px;
            }}
            QListWidget::item:hover {{
                background-color: {colors['accent_light']};
            }}
            QListWidget::item:selected {{
                background-color: {colors['primary']};
                color: white;
            }}
            QScrollBar:vertical {{
                background: {colors['background']};
                width: 8px;
                border-radius: 4px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors['border']};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors['text_secondary']};
            }}
        """

    @staticmethod
    def clear_style_cache():
        """Clear all style caches when theme changes"""
        FluentComboBoxStyle._cached_base_styles.clear()
        StyleCache.clear_cache()


class FluentAnimationManager:
    """Centralized animation management for better performance"""

    # Use weakrefs to avoid reference cycles
    _animation_cache: Dict[str, QPropertyAnimation] = {}
    _effect_cache: Dict[int, Any] = {}  # Use widget ID instead of widget
    _cache_size = 0
    _MAX_CACHE_SIZE = PerformanceConfig.MAX_CACHED_ANIMATIONS

    @classmethod
    def get_or_create_animation(cls, widget: QWidget, property_name: str,
                                duration: int = FluentAnimation.DURATION_MEDIUM) -> QPropertyAnimation:
        """Get or create animation with improved caching and memory management"""
        widget_id = id(widget)
        cache_key = f"{widget_id}_{property_name}"

        # Apply performance scaling to duration
        duration = PerformanceConfig.scale_duration(duration)

        # Clean up cache if it's getting too large
        if cls._cache_size > cls._MAX_CACHE_SIZE:
            cls._cleanup_oldest_animations(cls._MAX_CACHE_SIZE // 2)

        if cache_key not in cls._animation_cache:
            animation = QPropertyAnimation(
                widget, QByteArray(property_name.encode()))
            animation.setDuration(duration)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            cls._animation_cache[cache_key] = animation
            cls._cache_size += 1

            # Clean up when widget is destroyed
            widget.destroyed.connect(
                lambda obj=None, key=cache_key: cls._cleanup_animation(key))

        return cls._animation_cache[cache_key]

    @classmethod
    def _cleanup_animation(cls, cache_key: str):
        """Clean up animation cache with proper error handling"""
        if cache_key in cls._animation_cache:
            try:
                animation = cls._animation_cache[cache_key]
                if animation and not animation.signalsBlocked():
                    animation.stop()
            except RuntimeError:
                # Animation object may have been deleted
                pass
            finally:
                if cache_key in cls._animation_cache:
                    del cls._animation_cache[cache_key]
                    cls._cache_size -= 1

    @classmethod
    def _cleanup_oldest_animations(cls, keep_count: int):
        """Clean up oldest animations when cache gets too large"""
        keys = list(cls._animation_cache.keys())
        to_remove = keys[:-keep_count] if len(keys) > keep_count else []

        for key in to_remove:
            cls._cleanup_animation(key)

    @classmethod
    def create_smooth_dropdown_animation(cls, view_widget: QWidget) -> QPropertyAnimation:
        """Create optimized dropdown animation"""
        # Use simpler animations in low performance mode
        if PerformanceConfig.LOW_PERFORMANCE_MODE:
            duration = FluentAnimation.DURATION_FAST // 2
        else:
            duration = FluentAnimation.DURATION_FAST

        animation = cls.get_or_create_animation(
            view_widget, "geometry", duration)
        # More efficient than OutBack
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        return animation

    @classmethod
    def create_fade_animation(cls, widget: QWidget, duration: int = 200) -> QPropertyAnimation:
        """Create optimized fade animation with efficient caching"""
        # Skip fade animations in low performance mode
        if PerformanceConfig.LOW_PERFORMANCE_MODE:
            # Return a dummy animation that completes immediately
            dummy = QPropertyAnimation(widget, QByteArray())
            dummy.setDuration(0)
            return dummy

        duration = PerformanceConfig.scale_duration(duration)

        # Use widget ID for cache key
        widget_id = id(widget)

        # Create effect only if needed
        if widget_id not in cls._effect_cache:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            cls._effect_cache[widget_id] = effect

            # Clean up when widget is destroyed
            widget.destroyed.connect(
                lambda obj=None, wid=widget_id: cls._effect_cache.pop(wid, None))

        effect = cls._effect_cache[widget_id]
        animation = cls.get_or_create_animation(effect, "opacity", duration)
        return animation

    @classmethod
    def clear_caches(cls):
        """Clear all caches (useful for testing or low-memory situations)"""
        # Stop all animations
        for key, animation in list(cls._animation_cache.items()):
            try:
                if animation and not animation.signalsBlocked():
                    animation.stop()
            except RuntimeError:
                pass

        # Clear caches
        cls._animation_cache.clear()
        cls._effect_cache.clear()
        cls._cache_size = 0


class FluentSearchBox(QLineEdit):
    """Enhanced search box component with improved performance"""

    text_changed = Signal(str)  # Debounced text change signal

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Use member variables for better performance
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_debounced_change)

        # Connect to Qt's text changed signal
        self.textChanged.connect(self._on_text_changed)

        # Apply style
        self._setup_style()

        # Track theme changes
        self._theme_mode = theme_manager.get_theme_mode()
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup search box style with caching"""
        self.setStyleSheet(self._get_cached_style())

    def _get_cached_style(self) -> str:
        """Get cached search box style"""
        theme_mode = theme_manager.get_theme_mode()
        cache_key = f"search_box_style_{theme_mode}"

        return StyleCache.get_style(cache_key, lambda: self._generate_style())

    def _generate_style(self) -> str:
        """Generate search box style"""
        colors = FluentComboBoxStyle.get_base_styles()

        return f"""
            QLineEdit {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: {colors['text_primary']};
                selection-background-color: {colors['primary']};
            }}
            QLineEdit:hover {{
                border-color: {colors['primary']};
                background-color: {colors['accent_light']};
            }}
            QLineEdit:focus {{
                border-color: {colors['primary']};
                border-width: 2px;
                padding: 9px 13px;
            }}
        """

    def set_text(self, text: str):
        """Set text without triggering the debounce timer"""
        # Block signals to prevent recursive calls
        self.blockSignals(True)
        self.setText(text)
        self.blockSignals(False)

        # Emit the signal directly since this is a programmatic change
        self.text_changed.emit(text)

    def _on_text_changed(self, text: str):
        """Handle text changes with efficient debouncing"""
        # Reset and restart the timer
        self._debounce_timer.stop()
        self._debounce_timer.start(150)

    def _emit_debounced_change(self):
        """Emit the debounced text changed signal"""
        self.text_changed.emit(self.text())

    def _on_theme_changed(self):
        """Handle theme changes efficiently"""
        current_theme = theme_manager.get_theme_mode()
        if current_theme != self._theme_mode:
            self._theme_mode = current_theme
            self._setup_style()


class FluentComboBox(QComboBox):
    """Enhanced Fluent Design style combo box with improved animations and performance"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._drop_animation = None
        self._is_expanded = False
        self._theme_mode = theme_manager.get_theme_mode()

        # Set minimum height for better touch targets
        self.setMinimumHeight(42)

        # Apply style
        self._setup_style()

        # Track theme changes
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup combo box style with shadow effect based on performance settings"""
        self.setStyleSheet(FluentComboBoxStyle.get_combobox_style())

        # Add shadow only if performance settings allow it
        if PerformanceConfig.should_use_shadows():
            shadow = QGraphicsDropShadowEffect()
            # Reduced blur radius for better performance
            shadow.setBlurRadius(6)
            shadow.setColor(QColor(0, 0, 0, 25))
            shadow.setOffset(0, 2)
            self.setGraphicsEffect(shadow)

    def _get_cached_drop_animation(self) -> QPropertyAnimation:
        """Get cached dropdown animation"""
        if not self._drop_animation:
            self._drop_animation = FluentAnimationManager.create_smooth_dropdown_animation(
                self)
        return self._drop_animation

    def showPopup(self):
        """Show dropdown with optimized animation"""
        self._is_expanded = True

        # Always call the base implementation first
        super().showPopup()

        # Skip animation in low performance mode
        if PerformanceConfig.LOW_PERFORMANCE_MODE:
            return

        # Queue animation for better performance
        QTimer.singleShot(5, self._animate_popup_show)

    def _animate_popup_show(self):
        """Animate popup show with efficient animation"""
        if not self.view() or not self._is_expanded:
            return

        view = self.view()

        # Get final position
        final_rect = view.geometry()

        # Create smooth reveal animation
        start_rect = QRect(
            final_rect.x(),
            final_rect.y(),
            final_rect.width(),
            max(1, final_rect.height() // 3)  # Start with 1/3 height
        )

        # Get cached animation
        animation = self._get_cached_drop_animation()
        animation.setStartValue(start_rect)
        animation.setEndValue(final_rect)
        animation.setDuration(PerformanceConfig.scale_duration(180))
        animation.start()

        # Add fade effect only if advanced effects are enabled
        if PerformanceConfig.should_use_advanced_effects():
            fade_anim = FluentAnimationManager.create_fade_animation(view, 150)
            fade_anim.setStartValue(0.6)
            fade_anim.setEndValue(1.0)
            fade_anim.start()

    def hidePopup(self):
        """Hide dropdown with optimized fade animation"""
        self._is_expanded = False

        # Skip animation in low performance mode
        if PerformanceConfig.LOW_PERFORMANCE_MODE or not self.view():
            super().hidePopup()
            return

        # Create fade out animation
        fade_anim = FluentAnimationManager.create_fade_animation(
            self.view(), 100)
        fade_anim.setStartValue(1.0)
        fade_anim.setEndValue(0.0)
        fade_anim.finished.connect(self._complete_hide_popup)
        fade_anim.start()

    def _complete_hide_popup(self):
        """Complete hiding the popup after animation"""
        if not self._is_expanded:  # Check if still not expanded
            super().hidePopup()

    def enterEvent(self, event):
        """Optimize hover effect"""
        if not self._is_expanded:
            # Use style property instead of creating a new effect
            self.setProperty("hovered", True)
            self.style().unpolish(self)
            self.style().polish(self)

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Optimize hover effect removal"""
        # Remove hover state
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)

        super().leaveEvent(event)

    def _on_theme_changed(self):
        """Handle theme changes efficiently"""
        current_theme = theme_manager.get_theme_mode()
        if current_theme != self._theme_mode:
            self._theme_mode = current_theme
            self._setup_style()

    def paintEvent(self, event):
        """Optimized paint event with conditional rendering"""
        # Always call the base implementation first
        super().paintEvent(event)

        # Skip additional drawing in low performance mode
        if PerformanceConfig.LOW_PERFORMANCE_MODE:
            return

        # Add visual indicator only when needed
        if self.currentText() and not self._is_expanded:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Draw subtle selection indicator
            rect = self.rect()
            painter.setPen(QColor(theme_manager.get_color('primary')))
            painter.drawLine(rect.left() + 2, rect.bottom() - 2,
                             rect.left() + 20, rect.bottom() - 2)

    def hideEvent(self, event):
        """Clean up animations when hidden"""
        if self._drop_animation:
            self._drop_animation.stop()
        super().hideEvent(event)


class FluentMultiSelectComboBox(QWidget):
    """Enhanced multi-select combo box with optimized animations and performance"""

    selection_changed = Signal(list)  # List of selected items

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items = []
        self._selected_items = []
        self._is_expanded = False
        self._dropdown_widget = None
        self._theme_mode = theme_manager.get_theme_mode()

        # Setup UI
        self._setup_ui()
        self._setup_style()

        # Track theme changes
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI with optimized layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main button with tooltip
        self.main_button = QPushButton("Select items...")
        self.main_button.setMinimumHeight(42)
        self.main_button.clicked.connect(self._toggle_dropdown)
        self.main_button.setToolTip("Click to select items")

        layout.addWidget(self.main_button)

    def _setup_style(self):
        """Setup style with conditional shadow"""
        self.main_button.setStyleSheet(FluentComboBoxStyle.get_button_style())

        # Add shadow only if performance settings allow it
        if PerformanceConfig.should_use_shadows():
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(4)  # Reduced blur radius
            shadow.setColor(QColor(0, 0, 0, 20))  # Less opacity
            shadow.setOffset(0, 1)
            self.main_button.setGraphicsEffect(shadow)

    def add_item(self, text: str, data: Any = None):
        """Add item with optimized handling"""
        item = {
            'text': text,
            'data': data,
            'selected': False
        }
        self._items.append(item)
        self._update_display()

    def add_items(self, items: List[str]):
        """Add multiple items in batch for better performance"""
        # Create items in batch without updating display until complete
        for item_text in items:
            self._items.append({
                'text': item_text,
                'data': None,
                'selected': False
            })

        # Update display once at the end
        self._update_display()

    def get_selected_items(self) -> List[str]:
        """Get selected items efficiently"""
        # Use list comprehension for better performance
        return [item['text'] for item in self._items if item['selected']]

    def get_selected_data(self) -> List[Any]:
        """Get selected item data efficiently"""
        # Use list comprehension for better performance
        return [item['data'] for item in self._items if item['selected']]

    def set_selected_items(self, selected_texts: List[str]):
        """Set selected items efficiently"""
        # Convert list to set for O(1) lookups
        selected_set = set(selected_texts)
        changed = False

        for item in self._items:
            new_selected = item['text'] in selected_set
            if item['selected'] != new_selected:
                item['selected'] = new_selected
                changed = True

        if changed:
            self._selected_items = self.get_selected_items()
            self._update_display()
            self.selection_changed.emit(self._selected_items)

    def clear_selection(self):
        """Clear selection efficiently"""
        # Check if any items are selected first
        changed = any(item['selected'] for item in self._items)

        if changed:
            # Clear selections
            for item in self._items:
                item['selected'] = False

            self._selected_items = []
            self._update_display()
            self.selection_changed.emit(self._selected_items)

    def _toggle_dropdown(self):
        """Toggle dropdown with optimized state management"""
        if self._is_expanded:
            self._hide_dropdown()
        else:
            self._show_dropdown()

    def _show_dropdown(self):
        """Show dropdown with optimized animation"""
        # Close existing dropdown first
        if self._dropdown_widget:
            self._dropdown_widget.close()
            self._dropdown_widget = None

        # Create new dropdown
        self._dropdown_widget = self._create_dropdown_widget()
        self._dropdown_widget.show()
        self._is_expanded = True

        # Skip animation in low performance mode
        if PerformanceConfig.LOW_PERFORMANCE_MODE:
            return

        # Setup animations
        scale_anim = FluentAnimationManager.get_or_create_animation(
            self._dropdown_widget, "geometry",
            PerformanceConfig.scale_duration(180))

        # Calculate animation parameters
        final_rect = self._dropdown_widget.geometry()
        start_rect = QRect(final_rect.x(), final_rect.y(),
                           final_rect.width(), max(1, final_rect.height() // 3))

        scale_anim.setStartValue(start_rect)
        scale_anim.setEndValue(final_rect)
        scale_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        scale_anim.start()

        # Add fade effect only if advanced effects are enabled
        if PerformanceConfig.should_use_advanced_effects():
            fade_anim = FluentAnimationManager.create_fade_animation(
                self._dropdown_widget, 150)
            fade_anim.setStartValue(0.6)
            fade_anim.setEndValue(1.0)
            fade_anim.start()

    def _hide_dropdown(self):
        """Hide dropdown with optimized animation"""
        if not self._dropdown_widget:
            return

        self._is_expanded = False

        # Skip animation in low performance mode
        if PerformanceConfig.LOW_PERFORMANCE_MODE:
            self._dropdown_widget.close()
            self._dropdown_widget = None
            return

        # Create optimized fade animation
        fade_anim = FluentAnimationManager.create_fade_animation(
            self._dropdown_widget, 100)
        fade_anim.setStartValue(1.0)
        fade_anim.setEndValue(0.0)

        # Use weak reference to avoid circular references
        dropdown_ref = weakref.ref(self._dropdown_widget)

        def complete_hide():
            dropdown = dropdown_ref()
            if dropdown:
                dropdown.close()

        fade_anim.finished.connect(complete_hide)
        fade_anim.start()

    def _create_dropdown_widget(self) -> QWidget:
        """Create optimized dropdown widget"""
        dropdown = QWidget(self, Qt.WindowType.Popup)
        dropdown.setFixedWidth(self.width())
        dropdown.setMaximumHeight(280)

        # Calculate optimal position
        global_pos = self.mapToGlobal(self.rect().bottomLeft())
        dropdown.move(global_pos)

        layout = QVBoxLayout(dropdown)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Apply style
        colors = FluentComboBoxStyle.get_base_styles()
        dropdown.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
            }}
        """)

        # Add shadow conditionally
        if PerformanceConfig.should_use_shadows():
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(12)
            shadow.setColor(QColor(0, 0, 0, 30))
            shadow.setOffset(0, 4)
            dropdown.setGraphicsEffect(shadow)

        # Create optimized scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(4, 4, 4, 4)
        content_layout.setSpacing(3)

        # Create checkboxes efficiently
        self._create_checkbox_items(content_layout)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        # Add action buttons
        self._create_action_buttons(layout)

        return dropdown

    def _create_checkbox_items(self, layout: QVBoxLayout):
        """Create optimized checkbox items"""
        colors = FluentComboBoxStyle.get_base_styles()
        checkbox_style = f"""
            QCheckBox {{
                color: {colors['text_primary']};
                font-size: 14px;
                padding: 8px;
                border-radius: 6px;
            }}
            QCheckBox:hover {{
                background-color: {colors['accent_light']};
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid {colors['border']};
                background-color: {colors['surface']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {colors['primary']};
                border-color: {colors['primary']};
            }}
        """

        # Block signals during batch creation for better performance
        with QSignalBlocker(layout.parentWidget()):
            # Create checkboxes in batch
            for i, item in enumerate(self._items):
                checkbox = QCheckBox(item['text'])
                checkbox.setChecked(item['selected'])

                # Use a closure to capture the index
                def create_handler(idx):
                    return lambda state: self._on_item_toggled(idx, state)

                checkbox.stateChanged.connect(create_handler(i))
                checkbox.setStyleSheet(checkbox_style)
                layout.addWidget(checkbox)

    def _create_action_buttons(self, layout: QVBoxLayout):
        """Create optimized action buttons"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        colors = FluentComboBoxStyle.get_base_styles()
        button_style = f"""
            QPushButton {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 13px;
                font-weight: 500;
                color: {colors['text_primary']};
                min-height: 16px;
            }}
            QPushButton:hover {{
                background-color: {colors['primary']};
                color: white;
                border-color: {colors['primary']};
            }}
            QPushButton:pressed {{
                background-color: {colors['accent_dark']};
            }}
        """

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        select_all_btn.setStyleSheet(button_style)

        clear_all_btn = QPushButton("Clear")
        clear_all_btn.clicked.connect(self.clear_selection)
        clear_all_btn.setStyleSheet(button_style)

        done_btn = QPushButton("Done")
        done_btn.clicked.connect(self._hide_dropdown)
        done_btn.setStyleSheet(button_style + f"""
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {colors['accent_dark']};
            }}
        """)

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(clear_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(done_btn)

        layout.addLayout(button_layout)

    def _on_item_toggled(self, index: int, state: int):
        """Handle item toggle efficiently"""
        if 0 <= index < len(self._items):
            # Update item state
            self._items[index]['selected'] = (
                state == Qt.CheckState.Checked.value)
            # Update cached selected items
            self._selected_items = self.get_selected_items()
            # Update display
            self._update_display()
            # Emit signal
            self.selection_changed.emit(self._selected_items)

    def _select_all(self):
        """Select all items efficiently"""
        # Check if all items are already selected
        if all(item['selected'] for item in self._items):
            return

        # Update all items
        for item in self._items:
            item['selected'] = True

        # Update state
        self._selected_items = self.get_selected_items()
        self._update_display()
        self.selection_changed.emit(self._selected_items)

        # Recreate dropdown to update checkboxes
        # Use a timer to prevent immediate recreation
        if self._dropdown_widget:
            self._dropdown_widget.close()
            self._dropdown_widget = None
            QTimer.singleShot(10, self._show_dropdown)

    def _update_display(self):
        """Update display text efficiently"""
        selected_count = len(self._selected_items)

        if selected_count == 0:
            new_text = "Select items..."
        elif selected_count == 1:
            # Truncate long text for better performance
            text = self._selected_items[0]
            new_text = text[:22] + "..." if len(text) > 25 else text
        else:
            new_text = f"{selected_count} items selected"

        # Update button text only if changed
        current_text = self.main_button.text()
        if new_text != current_text:
            self.main_button.setText(new_text)

    def _on_theme_changed(self):
        """Handle theme changes efficiently"""
        current_theme = theme_manager.get_theme_mode()
        if current_theme != self._theme_mode:
            self._theme_mode = current_theme
            self._setup_style()


class FluentSearchableComboBox(QWidget):
    """Enhanced searchable combo box with optimized search and animations"""

    item_selected = Signal(str, object)  # text, data

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items = []
        self._filtered_items = []
        self._selected_item = None
        self._is_expanded = False
        self._theme_mode = theme_manager.get_theme_mode()

        # Setup debounced search
        self._search_debounce_timer = QTimer()
        self._search_debounce_timer.setSingleShot(True)
        self._search_debounce_timer.timeout.connect(self._perform_search)

        # Setup UI
        self._setup_ui()

        # Track theme changes
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI with optimized layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Enhanced search input
        self.search_box = FluentSearchBox()
        self.search_box.setPlaceholderText("Type to search...")
        self.search_box.setMinimumHeight(42)
        self.search_box.text_changed.connect(self._on_search_text_changed)
        self.search_box.returnPressed.connect(self._select_first_item)

        # Enhanced dropdown list
        self.list_widget = QListWidget()
        self.list_widget.setMaximumHeight(240)
        self.list_widget.setVisible(False)
        self.list_widget.itemClicked.connect(self._on_item_clicked)

        layout.addWidget(self.search_box)
        layout.addWidget(self.list_widget)

        self._setup_list_style()

    def _setup_list_style(self):
        """Setup list style with conditional shadow"""
        self.list_widget.setStyleSheet(FluentComboBoxStyle.get_list_style())

        # Add shadow only if performance settings allow it
        if PerformanceConfig.should_use_shadows():
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(8)  # Reduced blur radius
            shadow.setColor(QColor(0, 0, 0, 30))  # Reduced opacity
            shadow.setOffset(0, 3)
            self.list_widget.setGraphicsEffect(shadow)

    def add_item(self, text: str, data: Any = None):
        """Add item efficiently"""
        item = {
            'text': text,
            'data': data
        }
        self._items.append(item)

        # Update filtered items if there's no filter text
        if not self.search_box.text():
            if len(self._filtered_items) < 50:  # Only update if under display limit
                self._filtered_items.append(item)

                # Add to list widget if it's visible
                if self.list_widget.isVisible():
                    list_item = QListWidgetItem(item['text'])
                    list_item.setData(Qt.ItemDataRole.UserRole, item)
                    self.list_widget.addItem(list_item)

    def add_items(self, items: List[str]):
        """Add multiple items in batch for better performance"""
        # Create all items at once
        new_items = [{'text': item_text, 'data': None} for item_text in items]

        # Add to internal list
        self._items.extend(new_items)

        # Update UI if needed
        if not self.search_box.text():
            self._update_filtered_items()

    def clear_items(self):
        """Clear items efficiently"""
        self._items.clear()
        self._filtered_items.clear()
        self.list_widget.clear()

        if self.list_widget.isVisible():
            self._hide_list_with_animation()

    def set_selected_text(self, text: str):
        """Set selected text efficiently"""
        # Try to find the item in the existing items
        self._selected_item = next(
            (item for item in self._items if item['text'] == text), None)

        self.search_box.set_text(text)

    def get_selected_item(self) -> Optional[dict]:
        """Get selected item"""
        return self._selected_item

    def _on_search_text_changed(self, text: str):
        """Handle search text change with optimized debouncing"""
        # Reset and restart the timer - use shorter delay for better responsiveness
        debounce_time = 300 if PerformanceConfig.LOW_PERFORMANCE_MODE else 150
        self._search_debounce_timer.stop()
        self._search_debounce_timer.start(debounce_time)

    def _perform_search(self):
        """Perform optimized search"""
        text = self.search_box.text()

        # Update filtered items based on search text
        self._update_filtered_items(text)

        # Show or hide the list based on search results
        if text and self._filtered_items:
            if not self.list_widget.isVisible():
                self._show_list_with_animation()
            self._is_expanded = True
        elif self.list_widget.isVisible():
            self._hide_list_with_animation()
            self._is_expanded = False

    def _show_list_with_animation(self):
        """Show list with optimized animation"""
        self.list_widget.setVisible(True)

        # Skip animation in low performance mode
        if PerformanceConfig.LOW_PERFORMANCE_MODE:
            return

        # Create optimized reveal animation
        reveal_anim = FluentAnimationManager.get_or_create_animation(
            self.list_widget, "geometry",
            PerformanceConfig.scale_duration(160))

        final_rect = self.list_widget.geometry()
        start_rect = QRect(final_rect.x(), final_rect.y(),
                           final_rect.width(), max(1, final_rect.height() // 3))

        reveal_anim.setStartValue(start_rect)
        reveal_anim.setEndValue(final_rect)
        reveal_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        reveal_anim.start()

        # Add fade effect only if advanced effects are enabled
        if PerformanceConfig.should_use_advanced_effects():
            fade_anim = FluentAnimationManager.create_fade_animation(
                self.list_widget, 120)
            fade_anim.setStartValue(0.7)
            fade_anim.setEndValue(1.0)
            fade_anim.start()

    def _hide_list_with_animation(self):
        """Hide list with optimized animation"""
        # Skip animation in low performance mode
        if PerformanceConfig.LOW_PERFORMANCE_MODE:
            self.list_widget.setVisible(False)
            return

        # Create fade animation
        fade_anim = FluentAnimationManager.create_fade_animation(
            self.list_widget, 100)
        fade_anim.setStartValue(1.0)
        fade_anim.setEndValue(0.0)

        # Use weak reference to avoid circular references
        widget_ref = weakref.ref(self.list_widget)

        def hide_list():
            widget = widget_ref()
            if widget:
                widget.setVisible(False)

        fade_anim.finished.connect(hide_list)
        fade_anim.start()

    def _update_filtered_items(self, filter_text: str = ""):
        """Update filtered items with optimized search algorithm"""
        # Block signals during batch updates
        with QSignalBlocker(self.list_widget):
            self.list_widget.clear()
            self._filtered_items.clear()

            # Apply filter
            if not filter_text:
                # Without a filter, just use the original items (up to display limit)
                self._filtered_items = self._items[:50]
            else:
                # Optimized search algorithm with prioritization
                filter_lower = filter_text.lower()
                limit_reached = False

                # First check for exact matches and startswith (higher priority)
                for item in self._items:
                    item_text_lower = item['text'].lower()

                    # Exact match or starts with
                    if item_text_lower == filter_lower or item_text_lower.startswith(filter_lower):
                        self._filtered_items.append(item)

                        # Check display limit
                        if len(self._filtered_items) >= 50:
                            limit_reached = True
                            break

                # If we have room for more, check for contains matches
                if not limit_reached:
                    for item in self._items:
                        item_text_lower = item['text'].lower()

                        # Skip items that have already been added
                        if item in self._filtered_items:
                            continue

                        # Contains match
                        if filter_lower in item_text_lower:
                            self._filtered_items.append(item)

                            # Check display limit
                            if len(self._filtered_items) >= 50:
                                break

            # Add filtered items to list widget
            for item in self._filtered_items:
                list_item = QListWidgetItem(item['text'])
                list_item.setData(Qt.ItemDataRole.UserRole, item)
                self.list_widget.addItem(list_item)

            # Add ellipsis if more items available
            if len(self._filtered_items) < len(self._items) and len(self._filtered_items) >= 50:
                ellipsis_item = QListWidgetItem(
                    f"... and {len(self._items) - 50} more")
                ellipsis_item.setData(Qt.ItemDataRole.UserRole, None)
                self.list_widget.addItem(ellipsis_item)

        # Update viewport only instead of the entire widget
        self.list_widget.viewport().update()

    def _on_item_clicked(self, list_item: QListWidgetItem):
        """Handle item click efficiently"""
        item = list_item.data(Qt.ItemDataRole.UserRole)

        # Ignore ellipsis item
        if item is None:
            return

        # Update state
        self._selected_item = item
        self.search_box.set_text(item['text'])

        # Hide list
        self._hide_list_with_animation()
        self._is_expanded = False

        # Emit signal
        self.item_selected.emit(item['text'], item['data'])

    def _select_first_item(self):
        """Select first item efficiently"""
        if not self._filtered_items:
            return

        # Select first item
        first_item = self._filtered_items[0]
        self._selected_item = first_item
        self.search_box.set_text(first_item['text'])

        # Hide list
        self._hide_list_with_animation()
        self._is_expanded = False

        # Emit signal
        self.item_selected.emit(first_item['text'], first_item['data'])

    def _on_theme_changed(self):
        """Handle theme changes efficiently"""
        current_theme = theme_manager.get_theme_mode()
        if current_theme != self._theme_mode:
            self._theme_mode = current_theme
            self._setup_list_style()


class FluentDropDownButton(QPushButton):
    """Enhanced dropdown button with optimized animations and performance"""

    item_clicked = Signal(str, object)  # text, data

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self._menu_items = []
        self._dropdown_widget = None
        self._is_expanded = False
        self._original_text = text
        self._theme_mode = theme_manager.get_theme_mode()

        # Connect signals
        self.clicked.connect(self._toggle_dropdown)

        # Set minimum height for better touch targets
        self.setMinimumHeight(42)

        # Apply style
        self._setup_style()

        # Track theme changes
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style with conditional shadow"""
        self.setStyleSheet(FluentComboBoxStyle.get_button_style())

        # Add shadow only if performance settings allow it
        if PerformanceConfig.should_use_shadows():
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(6)  # Reduced blur radius
            shadow.setColor(QColor(0, 0, 0, 20))  # Reduced opacity
            shadow.setOffset(0, 2)
            self.setGraphicsEffect(shadow)

        # Update button text
        self._update_button_text()

    def _update_button_text(self):
        """Update button text efficiently"""
        new_text = f"{self._original_text} ▼" if self._original_text else "Select ▼"

        # Only update if text actually changed
        if self.text() != new_text:
            self.setText(new_text)

    def add_menu_item(self, text: str, data: Any = None, icon: Optional[QIcon] = None):
        """Add menu item efficiently"""
        self._menu_items.append({
            'text': text,
            'data': data,
            'icon': icon
        })

    def add_menu_items(self, items: List[str]):
        """Add multiple menu items in batch for better performance"""
        # Create all items at once
        self._menu_items.extend([
            {'text': item_text, 'data': None, 'icon': None} for item_text in items
        ])

    def clear_menu_items(self):
        """Clear menu items efficiently"""
        self._menu_items.clear()

    def _toggle_dropdown(self):
        """Toggle dropdown menu efficiently"""
        if self._is_expanded:
            self._hide_dropdown()
        else:
            self._show_dropdown()

    def _show_dropdown(self):
        """Show dropdown menu with optimized animation"""
        # Skip if there are no items
        if not self._menu_items:
            return

        # Close existing dropdown first
        if self._dropdown_widget:
            self._dropdown_widget.close()
            self._dropdown_widget = None

        # Create new dropdown
        self._dropdown_widget = self._create_dropdown_menu()
        self._dropdown_widget.show()
        self._is_expanded = True

        # Skip animation in low performance mode
        if PerformanceConfig.LOW_PERFORMANCE_MODE:
            return

        # Setup animations
        scale_anim = FluentAnimationManager.get_or_create_animation(
            self._dropdown_widget, "geometry",
            PerformanceConfig.scale_duration(160))

        # Calculate animation parameters
        final_rect = self._dropdown_widget.geometry()
        start_rect = QRect(final_rect.x(), final_rect.y(),
                           final_rect.width(), max(1, final_rect.height() // 3))

        scale_anim.setStartValue(start_rect)
        scale_anim.setEndValue(final_rect)
        scale_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        scale_anim.start()

        # Add fade effect only if advanced effects are enabled
        if PerformanceConfig.should_use_advanced_effects():
            fade_anim = FluentAnimationManager.create_fade_animation(
                self._dropdown_widget, 150)
            fade_anim.setStartValue(0.7)
            fade_anim.setEndValue(1.0)
            fade_anim.start()

    def _hide_dropdown(self):
        """Hide dropdown menu with optimized animation"""
        if not self._dropdown_widget:
            return

        # Update state
        self._is_expanded = False

        # Skip animation in low performance mode
        if PerformanceConfig.LOW_PERFORMANCE_MODE:
            self._dropdown_widget.close()
            self._dropdown_widget = None
            return

        # Create optimized fade animation
        fade_anim = FluentAnimationManager.create_fade_animation(
            self._dropdown_widget, 100)
        fade_anim.setStartValue(1.0)
        fade_anim.setEndValue(0.0)

        # Use weak reference to avoid circular references
        dropdown_ref = weakref.ref(self._dropdown_widget)

        def complete_hide():
            dropdown = dropdown_ref()
            if dropdown:
                dropdown.close()

        fade_anim.finished.connect(complete_hide)
        fade_anim.start()

    def _create_dropdown_menu(self) -> QWidget:
        """Create optimized dropdown menu"""
        # Create menu widget
        menu = QWidget(None, Qt.WindowType.Popup)
        menu.setMinimumWidth(self.width())

        # Calculate optimal position
        global_pos = self.mapToGlobal(self.rect().bottomLeft())
        menu.move(global_pos)

        # Setup layout
        layout = QVBoxLayout(menu)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Apply style
        colors = FluentComboBoxStyle.get_base_styles()
        menu.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
            }}
        """)

        # Add shadow conditionally
        if PerformanceConfig.should_use_shadows():
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(12)
            shadow.setColor(QColor(0, 0, 0, 40))
            shadow.setOffset(0, 4)
            menu.setGraphicsEffect(shadow)

        # Create menu items efficiently
        self._create_menu_items(layout, colors)

        return menu

    def _create_menu_items(self, layout: QVBoxLayout, colors: Dict[str, str]):
        """Create menu items efficiently with shared styling"""
        # Cache the style string for performance
        item_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                text-align: left;
                color: {colors['text_primary']};
                font-size: 14px;
                font-weight: 400;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {colors['accent_light']};
            }}
            QPushButton:pressed {{
                background-color: {colors['accent_medium']};
            }}
        """

        # Create buttons in batch with signal blocking
        with QSignalBlocker(layout.parentWidget()):
            for item in self._menu_items:
                menu_item_btn = QPushButton(item['text'])

                if item['icon']:
                    menu_item_btn.setIcon(item['icon'])

                menu_item_btn.setStyleSheet(item_style)

                # Create a closure to capture the item data
                def create_handler(item_data):
                    return lambda: self._on_menu_item_clicked(item_data)

                menu_item_btn.clicked.connect(create_handler(item))
                layout.addWidget(menu_item_btn)

    def _on_menu_item_clicked(self, item: dict):
        """Handle menu item click efficiently"""
        # Hide dropdown with minimal delay
        QTimer.singleShot(10, self._hide_dropdown)

        # Emit signal
        self.item_clicked.emit(item['text'], item['data'])

    def _on_theme_changed(self):
        """Handle theme changes efficiently"""
        current_theme = theme_manager.get_theme_mode()
        if current_theme != self._theme_mode:
            self._theme_mode = current_theme
            self._setup_style()
