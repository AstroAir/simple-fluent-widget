"""
Enhanced Base Components with Theme and Animation Integration
Provides optimized base classes that work seamlessly with the enhanced theme system
"""

from typing import Optional, Dict, Any, List, Callable, Union
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QByteArray, Signal, Property, QObject
from PySide6.QtGui import QFont, QIcon, QColor, QPainter, QPaintEvent, QMouseEvent

from .base import FluentBaseWidget, FluentBaseContainer
from .theme import get_theme_manager, register_component_for_theme, ThemeTransitionType
from .enhanced_animations import FluentAnimation, FluentTransition


class ThemeAwareWidget(FluentBaseWidget):
    """Base widget with enhanced theme integration and automatic registration"""

    # Theme change signals
    theme_applied = Signal()
    transition_started = Signal()
    transition_finished = Signal()

    def __init__(self, parent: Optional[QWidget] = None,
                 auto_register: bool = True,
                 transition_type: ThemeTransitionType = ThemeTransitionType.FADE):
        super().__init__(parent)

        self._theme_manager = get_theme_manager()
        self._transition_type = transition_type
        self._theme_animation: Optional[QPropertyAnimation] = None
        self._theme_properties: Dict[str, Any] = {}
        self._cached_styles: Dict[str, str] = {}

        # Auto-register for theme updates
        if auto_register:
            self._theme_manager.register_component(self)

        # Connect theme signals
        self._connect_theme_signals()

        # Setup initial theme
        self._apply_initial_theme()

    def _connect_theme_signals(self):
        """Connect to theme manager signals"""
        self._theme_manager.theme_changed.connect(self._on_theme_changed)
        self._theme_manager.mode_changed.connect(self._on_mode_changed)
        self._theme_manager.transition_started.connect(
            self._on_transition_started)
        self._theme_manager.transition_finished.connect(
            self._on_transition_finished)

    def _apply_initial_theme(self):
        """Apply initial theme without animation"""
        self._update_theme_properties()
        self._apply_theme_styles()

    def _update_theme_properties(self):
        """Update cached theme properties"""
        self._theme_properties = {
            'primary': self._theme_manager.get_color('primary'),
            'secondary': self._theme_manager.get_color('secondary'),
            'surface': self._theme_manager.get_color('surface'),
            'background': self._theme_manager.get_color('background'),
            'text_primary': self._theme_manager.get_color('text_primary'),
            'text_secondary': self._theme_manager.get_color('text_secondary'),
            'border': self._theme_manager.get_color('border'),
            'hover': self._theme_manager.get_color('hover'),
            'pressed': self._theme_manager.get_color('pressed'),
            'focus': self._theme_manager.get_color('focus'),
        }

    def _apply_theme_styles(self):
        """Apply theme styles - to be overridden by subclasses"""
        self.update()

    def _on_theme_changed(self):
        """Handle theme change with optional animation"""
        if self._theme_manager._animation_enabled:
            self._animate_theme_transition()
        else:
            self._update_theme_properties()
            self._apply_theme_styles()
            self.theme_applied.emit()

    def _on_mode_changed(self):
        """Handle theme mode change"""
        self._on_theme_changed()

    def _on_transition_started(self, transition_type: str):
        """Handle global transition start"""
        self.transition_started.emit()

    def _on_transition_finished(self):
        """Handle global transition finish"""
        self.transition_finished.emit()

    def _animate_theme_transition(self):
        """Create and start theme transition animation"""
        if self._theme_animation and self._theme_animation.state() == QPropertyAnimation.State.Running:
            self._theme_animation.stop()

        self._theme_animation = self._theme_manager.create_component_transition(
            self, self._transition_type)

        if self._theme_animation:
            # Update theme properties before animation
            self._update_theme_properties()

            # Connect animation finished to apply new styles
            self._theme_animation.finished.connect(self._on_animation_finished)
            self._theme_animation.start()
        else:
            # Fallback to immediate update
            self._update_theme_properties()
            self._apply_theme_styles()
            self.theme_applied.emit()

    def _on_animation_finished(self):
        """Handle animation completion"""
        self._apply_theme_styles()
        self.theme_applied.emit()

    def get_theme_color(self, color_name: str) -> QColor:
        """Get theme color with caching"""
        if color_name in self._theme_properties:
            return self._theme_properties[color_name]
        return self._theme_manager.get_color(color_name)

    def get_themed_style(self, component_type: str) -> str:
        """Get themed style sheet for component type"""
        cache_key = f"{component_type}_{self._theme_manager.get_theme_mode().value}"

        if cache_key in self._cached_styles:
            return self._cached_styles[cache_key]

        style = self._theme_manager.get_style_sheet(component_type)
        self._cached_styles[cache_key] = style
        return style

    def set_transition_type(self, transition_type: ThemeTransitionType):
        """Set transition animation type"""
        self._transition_type = transition_type

    def invalidate_theme_cache(self):
        """Invalidate cached theme data"""
        self._cached_styles.clear()
        self._theme_properties.clear()
        self._update_theme_properties()

    def closeEvent(self, event):
        """Handle close event with cleanup"""
        if self._theme_animation:
            self._theme_animation.stop()

        # Unregister from theme manager
        self._theme_manager.unregister_component(self)
        super().closeEvent(event)


class ThemeAwareButton(ThemeAwareWidget, QPushButton):
    """Enhanced button with automatic theme integration"""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None,
                 button_type: str = "button"):
        QPushButton.__init__(self, text, parent)
        ThemeAwareWidget.__init__(self, parent)

        self._button_type = button_type
        self._hover_animation: Optional[QPropertyAnimation] = None
        self._press_animation: Optional[QPropertyAnimation] = None

        self._setup_animations()

    def _setup_animations(self):
        """Setup button interaction animations"""
        # Hover animation
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)

        # Press animation
        self._press_animation = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self._press_animation.setDuration(FluentAnimation.DURATION_VERY_FAST)

    def _apply_theme_styles(self):
        """Apply themed button styles"""
        style = self.get_themed_style(self._button_type)
        self.setStyleSheet(style)

    def enterEvent(self, event):
        """Handle mouse enter with animation"""
        if self._hover_animation and self._hover_animation.state() != QPropertyAnimation.State.Running:
            # Subtle scale effect
            current_rect = self.geometry()
            hover_rect = current_rect.adjusted(-1, -1, 1, 1)

            self._hover_animation.setStartValue(current_rect)
            self._hover_animation.setEndValue(hover_rect)
            self._hover_animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave with animation"""
        if self._hover_animation:
            self._hover_animation.stop()
            # Return to original size
            self.setGeometry(self.geometry().adjusted(1, 1, -1, -1))

        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press with animation"""
        if self._press_animation:
            current_rect = self.geometry()
            press_rect = current_rect.adjusted(1, 1, -1, -1)

            self._press_animation.setStartValue(current_rect)
            self._press_animation.setEndValue(press_rect)
            self._press_animation.start()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release with animation"""
        if self._press_animation:
            self._press_animation.stop()
            # Return to normal size
            self.setGeometry(self.geometry().adjusted(-1, -1, 1, 1))

        super().mouseReleaseEvent(event)


class ThemeAwarePanel(ThemeAwareWidget, QFrame):
    """Enhanced panel with theme integration and layout management"""

    def __init__(self, parent: Optional[QWidget] = None,
                 layout_type: str = "vertical",
                 padding: int = 16):
        QFrame.__init__(self, parent)
        ThemeAwareWidget.__init__(self, parent)

        self._padding = padding
        self._setup_layout(layout_type)

    def _setup_layout(self, layout_type: str):
        """Setup panel layout"""
        if layout_type == "vertical":
            self._layout = QVBoxLayout(self)
        elif layout_type == "horizontal":
            self._layout = QHBoxLayout(self)
        else:
            self._layout = QVBoxLayout(self)

        self._layout.setContentsMargins(self._padding, self._padding,
                                        self._padding, self._padding)
        self._layout.setSpacing(8)

    def _apply_theme_styles(self):
        """Apply themed panel styles"""
        style = self.get_themed_style("panel")
        self.setStyleSheet(style)

    def add_widget(self, widget: QWidget, stretch: int = 0):
        """Add widget to panel layout"""
        self._layout.addWidget(widget, stretch)

    def add_spacing(self, spacing: int):
        """Add spacing to panel layout"""
        self._layout.addSpacing(spacing)

    def set_padding(self, padding: int):
        """Set panel padding"""
        self._padding = padding
        self._layout.setContentsMargins(padding, padding, padding, padding)


class AnimatedThemeProperty(QObject):
    """Helper class for animating theme-dependent properties"""

    value_changed = Signal(object)

    def __init__(self, parent: QObject, property_name: str,
                 start_value: Any, end_value: Any):
        super().__init__(parent)
        self._property_name = property_name
        self._current_value = start_value
        self._start_value = start_value
        self._end_value = end_value
        self._animation: Optional[QPropertyAnimation] = None

    def animate_to_value(self, target_value: Any, duration: int = 200):
        """Animate property to target value"""
        if self._animation:
            self._animation.stop()

        self._animation = QPropertyAnimation(
            self, QByteArray(b"current_value"))
        self._animation.setDuration(duration)
        self._animation.setStartValue(self._current_value)
        self._animation.setEndValue(target_value)
        self._animation.setEasingCurve(FluentTransition.EASE_SMOOTH)

        self._animation.valueChanged.connect(self.value_changed.emit)
        self._animation.start()

    def get_current_value(self):
        """Get current animated value"""
        return self._current_value

    def set_current_value(self, value):
        """Set current animated value"""
        self._current_value = value
        self.value_changed.emit(value)

    current_value = Property(object, get_current_value,
                             set_current_value, None, "")


class ThemeTransitionManager:
    """Manages coordinated theme transitions across multiple components"""

    def __init__(self):
        self._managed_components: List[ThemeAwareWidget] = []
        self._transition_animations: List[QPropertyAnimation] = []
        self._transition_callbacks: List[Callable] = []

    def add_component(self, component: ThemeAwareWidget):
        """Add component to managed transitions"""
        if component not in self._managed_components:
            self._managed_components.append(component)

    def remove_component(self, component: ThemeAwareWidget):
        """Remove component from managed transitions"""
        if component in self._managed_components:
            self._managed_components.remove(component)

    def add_transition_callback(self, callback: Callable):
        """Add callback to be called during transitions"""
        if callback not in self._transition_callbacks:
            self._transition_callbacks.append(callback)

    def start_coordinated_transition(self, transition_type: ThemeTransitionType,
                                     duration: int = 250, stagger_delay: int = 50):
        """Start coordinated transition across all managed components"""
        self._stop_all_animations()

        # Call transition callbacks
        for callback in self._transition_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in transition callback: {e}")

        # Start staggered animations
        for i, component in enumerate(self._managed_components):
            delay = i * stagger_delay
            QTimer.singleShot(delay,
                              lambda comp=component: self._start_component_transition(comp, transition_type, duration))

    def _start_component_transition(self, component: ThemeAwareWidget,
                                    transition_type: ThemeTransitionType, duration: int):
        """Start transition for individual component"""
        component.set_transition_type(transition_type)
        animation = component._theme_manager.create_component_transition(
            component, transition_type)

        if animation:
            animation.setDuration(duration)
            self._transition_animations.append(animation)
            animation.start()

    def _stop_all_animations(self):
        """Stop all running transition animations"""
        for animation in self._transition_animations:
            if animation.state() == QPropertyAnimation.State.Running:
                animation.stop()
        self._transition_animations.clear()


# Global transition manager instance
_transition_manager = None


def get_transition_manager() -> ThemeTransitionManager:
    """Get global transition manager instance"""
    global _transition_manager
    if _transition_manager is None:
        _transition_manager = ThemeTransitionManager()
    return _transition_manager


# Convenience functions
def create_themed_button(text: str = "", parent: Optional[QWidget] = None,
                         button_type: str = "button") -> ThemeAwareButton:
    """Create themed button with automatic theme integration"""
    return ThemeAwareButton(text, parent, button_type)


def create_themed_panel(parent: Optional[QWidget] = None,
                        layout_type: str = "vertical",
                        padding: int = 16) -> ThemeAwarePanel:
    """Create themed panel with automatic theme integration"""
    return ThemeAwarePanel(parent, layout_type, padding)


def register_for_coordinated_transitions(component: ThemeAwareWidget):
    """Register component for coordinated theme transitions"""
    get_transition_manager().add_component(component)


def start_global_theme_transition(transition_type: ThemeTransitionType = ThemeTransitionType.FADE,
                                  duration: int = 250, stagger_delay: int = 50):
    """Start coordinated theme transition across all registered components"""
    get_transition_manager().start_coordinated_transition(
        transition_type, duration, stagger_delay)
