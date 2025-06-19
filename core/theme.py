"""
Enhanced Fluent Design Theme Management System
Supports light/dark theme switching, custom theme colors, and animation coordination
"""

from typing import Dict, Any, Optional, Set, Callable, List, Tuple
from enum import Enum
from PySide6.QtCore import QObject, Signal, QSettings, QTimer, QPropertyAnimation, QByteArray
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QWidget


class ThemeMode(Enum):
    """Theme mode enumeration"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class ThemeTransitionType(Enum):
    """Theme transition animation types"""
    INSTANT = "instant"
    FADE = "fade"
    SLIDE = "slide"
    MORPH = "morph"


class ComponentThemeState:
    """Manages theme state for individual components"""
    
    def __init__(self, component: QWidget):
        self.component = component
        self.animations: Dict[str, QPropertyAnimation] = {}
        self.cached_styles: Dict[str, str] = {}
        self.transition_in_progress = False
    
    def clear_cache(self):
        """Clear cached styles"""
        self.cached_styles.clear()
    
    def stop_animations(self):
        """Stop all running animations"""
        for animation in self.animations.values():
            if animation.state() == QPropertyAnimation.State.Running:
                animation.stop()


class FluentTheme(QObject):
    """**Enhanced Fluent Design Theme Manager**"""

    # Enhanced theme change signals
    theme_changed = Signal(str)  # theme_name
    mode_changed = Signal(ThemeMode)  # theme_mode
    transition_started = Signal(str)  # transition_type
    transition_finished = Signal()
    
    # Component registration signals
    component_registered = Signal(QWidget)
    component_unregistered = Signal(QWidget)

    def __init__(self):
        super().__init__()
        self._current_mode = ThemeMode.LIGHT
        self._current_theme = "default"
        self._custom_colors = {}
        self._registered_components: Dict[QWidget, ComponentThemeState] = {}
        self._transition_callbacks: List[Callable] = []
        self._style_cache: Dict[str, str] = {}
        self._color_cache: Dict[str, QColor] = {}
        self._animation_enabled = True
        self._transition_duration = 250
        self._transition_type = ThemeTransitionType.FADE
        
        self.settings = QSettings("FluentUI", "Theme")

        # **Enhanced Fluent Design Color Palette**
        self._light_palette = {
            "primary": QColor("#0078d4"),
            "secondary": QColor("#106ebe"),
            "surface": QColor("#ffffff"),
            "background": QColor("#f3f2f1"),
            "card": QColor("#ffffff"),
            "border": QColor("#d1d1d1"),
            "text_primary": QColor("#323130"),
            "text_secondary": QColor("#605e5c"),
            "text_disabled": QColor("#a19f9d"),
            "accent_light": QColor("#deecf9"),
            "accent_medium": QColor("#c7e0f4"),
            "accent_dark": QColor("#004578"),
            
            # Extended palette for better component support
            "success": QColor("#107c10"),
            "warning": QColor("#ff8c00"),
            "error": QColor("#d13438"),
            "info": QColor("#0078d4"),
            "overlay": QColor(0, 0, 0, 80),
            "hover": QColor("#f3f2f1"),
            "pressed": QColor("#edebe9"),
            "focus": QColor("#005a9e"),
            "selection": QColor(0, 120, 212, 40),
            
            # Material elevations
            "elevation_1": QColor("#ffffff"),
            "elevation_2": QColor("#fcfcfc"),
            "elevation_4": QColor("#f8f8f8"),
            "elevation_8": QColor("#f4f4f4"),
            "elevation_12": QColor("#f0f0f0"),
        }

        self._dark_palette = {
            "primary": QColor("#60cdff"),
            "secondary": QColor("#0078d4"),
            "surface": QColor("#2d2d30"),
            "background": QColor("#1e1e1e"),
            "card": QColor("#252526"),
            "border": QColor("#3e3e42"),
            "text_primary": QColor("#ffffff"),
            "text_secondary": QColor("#cccccc"),
            "text_disabled": QColor("#808080"),
            "accent_light": QColor("#0d2240"),
            "accent_medium": QColor("#1a3a5c"),
            "accent_dark": QColor("#60cdff"),
            
            # Extended dark palette
            "success": QColor("#6bb700"),
            "warning": QColor("#ffb900"),
            "error": QColor("#ff5349"),
            "info": QColor("#60cdff"),
            "overlay": QColor(0, 0, 0, 120),
            "hover": QColor("#323233"),
            "pressed": QColor("#404041"),
            "focus": QColor("#0099ff"),
            "selection": QColor(96, 205, 255, 60),
            
            # Dark material elevations
            "elevation_1": QColor("#252526"),
            "elevation_2": QColor("#2d2d30"),
            "elevation_4": QColor("#363637"),
            "elevation_8": QColor("#3e3e42"),
            "elevation_12": QColor("#464647"),
        }

        self.load_settings()
        self._cache_colors()

    def register_component(self, component: QWidget):
        """Register component for theme updates"""
        if component not in self._registered_components:
            state = ComponentThemeState(component)
            self._registered_components[component] = state
            self.component_registered.emit(component)
            
            # Connect to component destroyed signal for cleanup
            component.destroyed.connect(
                lambda: self._unregister_component_internal(component))

    def unregister_component(self, component: QWidget):
        """Unregister component from theme updates"""
        self._unregister_component_internal(component)

    def _unregister_component_internal(self, component: QWidget):
        """Internal method to unregister component"""
        if component in self._registered_components:
            state = self._registered_components[component]
            state.stop_animations()
            del self._registered_components[component]
            self.component_unregistered.emit(component)

    def add_transition_callback(self, callback: Callable):
        """Add callback to be called during theme transitions"""
        if callback not in self._transition_callbacks:
            self._transition_callbacks.append(callback)

    def remove_transition_callback(self, callback: Callable):
        """Remove transition callback"""
        if callback in self._transition_callbacks:
            self._transition_callbacks.remove(callback)

    def set_animation_enabled(self, enabled: bool):
        """Enable or disable theme transition animations"""
        self._animation_enabled = enabled

    def set_transition_duration(self, duration: int):
        """Set theme transition duration in milliseconds"""
        self._transition_duration = max(0, duration)

    def set_transition_type(self, transition_type: ThemeTransitionType):
        """Set theme transition animation type"""
        self._transition_type = transition_type

    def _cache_colors(self):
        """Cache colors for improved performance"""
        self._color_cache.clear()
        palette = (self._light_palette if self._current_mode == ThemeMode.LIGHT
                   else self._dark_palette)
        
        for color_name, color in palette.items():
            self._color_cache[color_name] = QColor(color)
        
        # Cache custom colors
        for color_name, color in self._custom_colors.items():
            self._color_cache[color_name] = QColor(color)

    def _invalidate_caches(self):
        """Invalidate all caches when theme changes"""
        self._style_cache.clear()
        self._color_cache.clear()
        
        # Invalidate component caches
        for state in self._registered_components.values():
            state.clear_cache()
        
        self._cache_colors()

    def _notify_registered_components(self):
        """Notify all registered components of theme change"""
        if self._animation_enabled:
            self.transition_started.emit(self._transition_type.value)
            
            # Mark all components as transitioning
            for state in self._registered_components.values():
                state.transition_in_progress = True
            
            # Call transition callbacks
            for callback in self._transition_callbacks:
                try:
                    callback()
                except Exception as e:
                    print(f"Error in theme transition callback: {e}")
            
            # Delay the actual theme change signal for smooth transitions
            QTimer.singleShot(50, self._emit_theme_changed)
        else:
            self._emit_theme_changed()

    def _emit_theme_changed(self):
        """Emit theme changed signals"""
        self.theme_changed.emit(self._current_theme)
        
        if self._animation_enabled:
            # End transition after duration
            QTimer.singleShot(self._transition_duration, self._finish_transition)
        else:
            self._finish_transition()

    def _finish_transition(self):
        """Finish theme transition"""
        # Mark all components as transition complete
        for state in self._registered_components.values():
            state.transition_in_progress = False
        
        self.transition_finished.emit()

    def get_color(self, color_name: str) -> QColor:
        """**Get current theme color with enhanced caching**"""
        # Check cache first
        if color_name in self._color_cache:
            return QColor(self._color_cache[color_name])
        
        # Check custom colors
        if color_name in self._custom_colors:
            color = QColor(self._custom_colors[color_name])
            self._color_cache[color_name] = color
            return color

        # Get from current palette
        palette = (self._light_palette if self._current_mode == ThemeMode.LIGHT
                   else self._dark_palette)
        
        if color_name in palette:
            color = QColor(palette[color_name])
            self._color_cache[color_name] = color
            return color
        
        # Return default color and cache it
        default_color = QColor("#000000")
        self._color_cache[color_name] = default_color
        return default_color

    def get_color_with_alpha(self, color_name: str, alpha: int) -> QColor:
        """Get color with specific alpha value"""
        color = self.get_color(color_name)
        color.setAlpha(alpha)
        return color

    def get_semantic_color(self, semantic_type: str) -> QColor:
        """Get semantic colors (success, warning, error, info)"""
        return self.get_color(semantic_type)

    def get_elevation_color(self, level: int) -> QColor:
        """Get color for specific elevation level"""
        elevation_key = f"elevation_{min(level, 12)}"
        return self.get_color(elevation_key)

    def get_theme_mode(self) -> ThemeMode:
        """**Get current theme mode**"""
        return self._current_mode

    def get_current_theme(self) -> str:
        """**Get current theme name**"""
        return self._current_theme

    def set_theme_mode(self, mode: ThemeMode):
        """**Set theme mode with enhanced transition**"""
        if self._current_mode != mode:
            self._current_mode = mode
            self._invalidate_caches()
            self.save_settings()
            self.mode_changed.emit(mode)
            self._notify_registered_components()

    def set_custom_color(self, color_name: str, color: QColor):
        """**Set custom color**"""
        self._custom_colors[color_name] = color
        self._color_cache[color_name] = QColor(color)
        self._notify_registered_components()

    def get_style_sheet(self, component_type: str) -> str:
        """**Get component style sheet with enhanced caching**"""
        cache_key = f"{component_type}_{self._current_mode.value}"
        
        if cache_key in self._style_cache:
            return self._style_cache[cache_key]
        
        style = self._generate_component_style(component_type)
        self._style_cache[cache_key] = style
        return style

    def _generate_component_style(self, component_type: str) -> str:
        """Generate component style with comprehensive theme support"""
        colors = {
            "primary": self.get_color("primary").name(),
            "secondary": self.get_color("secondary").name(),
            "surface": self.get_color("surface").name(),
            "background": self.get_color("background").name(),
            "card": self.get_color("card").name(),
            "border": self.get_color("border").name(),
            "text_primary": self.get_color("text_primary").name(),
            "text_secondary": self.get_color("text_secondary").name(),
            "text_disabled": self.get_color("text_disabled").name(),
            "hover": self.get_color("hover").name(),
            "pressed": self.get_color("pressed").name(),
            "focus": self.get_color("focus").name(),
            "success": self.get_color("success").name(),
            "warning": self.get_color("warning").name(),
            "error": self.get_color("error").name(),
            "info": self.get_color("info").name(),
        }

        return self._get_component_css(component_type, colors)

    def _get_component_css(self, component_type: str, colors: Dict[str, str]) -> str:
        """Get comprehensive component CSS styles"""
        styles = {
            "button": f"""
                QPushButton {{
                    background-color: {colors['primary']};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 400;
                    min-height: 32px;
                }}
                QPushButton:hover {{
                    background-color: {colors['secondary']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['pressed']};
                }}
                QPushButton:focus {{
                    border: 2px solid {colors['focus']};
                }}
                QPushButton:disabled {{
                    background-color: {colors['border']};
                    color: {colors['text_disabled']};
                }}
            """,
            
            "secondary_button": f"""
                QPushButton {{
                    background-color: {colors['surface']};
                    color: {colors['text_primary']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 400;
                    min-height: 32px;
                }}
                QPushButton:hover {{
                    background-color: {colors['hover']};
                    border-color: {colors['primary']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['pressed']};
                }}
                QPushButton:focus {{
                    border: 2px solid {colors['focus']};
                }}
                QPushButton:disabled {{
                    background-color: {colors['background']};
                    color: {colors['text_disabled']};
                    border-color: {colors['border']};
                }}
            """,
            
            "textbox": f"""
                QLineEdit {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 14px;
                    color: {colors['text_primary']};
                    min-height: 20px;
                }}
                QLineEdit:focus {{
                    border-color: {colors['focus']};
                    border-width: 2px;
                }}
                QLineEdit:hover {{
                    border-color: {colors['secondary']};
                }}
                QLineEdit:disabled {{
                    background-color: {colors['background']};
                    color: {colors['text_disabled']};
                    border-color: {colors['border']};
                }}
            """,
            
            "card": f"""
                QFrame {{
                    background-color: {colors['card']};
                    border: 1px solid {colors['border']};
                    border-radius: 8px;
                    padding: 16px;
                }}
                QFrame:hover {{
                    border-color: {colors['primary']};
                }}
            """,
            
            "panel": f"""
                QFrame {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 6px;
                }}
            """,
            
            "label": f"""
                QLabel {{
                    color: {colors['text_primary']};
                    font-size: 14px;
                    background-color: transparent;
                }}
            """,
            
            "combobox": f"""
                QComboBox {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 14px;
                    color: {colors['text_primary']};
                    min-height: 20px;
                }}
                QComboBox:focus {{
                    border-color: {colors['focus']};
                    border-width: 2px;
                }}
                QComboBox:hover {{
                    border-color: {colors['secondary']};
                }}
                QComboBox::drop-down {{
                    border: none;
                    padding-right: 8px;
                }}
                QComboBox::down-arrow {{
                    border: none;
                }}
            """,
        }
        
        return styles.get(component_type, "")

    def create_component_transition(self, component: QWidget,
                                  transition_type: Optional[ThemeTransitionType] = None) -> Optional[QPropertyAnimation]:
        """Create transition animation for component theme change"""
        if transition_type is None:
            transition_type = self._transition_type
        
        if component not in self._registered_components:
            self.register_component(component)
        
        state = self._registered_components[component]
        
        if transition_type == ThemeTransitionType.FADE:
            return self._create_fade_transition(component, state)
        elif transition_type == ThemeTransitionType.SLIDE:
            return self._create_slide_transition(component, state)
        elif transition_type == ThemeTransitionType.MORPH:
            return self._create_morph_transition(component, state)
        
        return None

    def _create_fade_transition(self, component: QWidget, 
                              state: ComponentThemeState) -> QPropertyAnimation:
        """Create fade transition animation"""
        if "fade" in state.animations:
            state.animations["fade"].stop()
        
        # Create opacity animation
        animation = QPropertyAnimation(component, QByteArray(b"windowOpacity"))
        animation.setDuration(self._transition_duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.3)
        
        def on_fade_out_finished():
            # Apply new theme styles here
            component.update()
            # Fade back in
            animation.setStartValue(0.3)
            animation.setEndValue(1.0)
            animation.start()
        
        animation.finished.connect(on_fade_out_finished)
        state.animations["fade"] = animation
        return animation

    def _create_slide_transition(self, component: QWidget,
                               state: ComponentThemeState) -> QPropertyAnimation:
        """Create slide transition animation"""
        if "slide" in state.animations:
            state.animations["slide"].stop()
        
        animation = QPropertyAnimation(component, QByteArray(b"geometry"))
        animation.setDuration(self._transition_duration)
        
        # Store original geometry and create slide effect
        original_rect = component.geometry()
        slide_rect = original_rect.translated(10, 0)
        
        animation.setStartValue(original_rect)
        animation.setEndValue(slide_rect)
        
        def on_slide_finished():
            component.update()
            # Return to original position
            animation.setStartValue(slide_rect)
            animation.setEndValue(original_rect)
            animation.start()
        
        animation.finished.connect(on_slide_finished)
        state.animations["slide"] = animation
        return animation

    def _create_morph_transition(self, component: QWidget,
                               state: ComponentThemeState) -> QPropertyAnimation:
        """Create morph transition animation"""
        # For morph transition, we'll use a combination of scaling and fading
        if "morph" in state.animations:
            state.animations["morph"].stop()
        
        animation = QPropertyAnimation(component, QByteArray(b"geometry"))
        animation.setDuration(self._transition_duration)
        
        original_rect = component.geometry()
        morph_rect = original_rect.adjusted(-5, -5, 5, 5)  # Slightly larger
        
        animation.setStartValue(original_rect)
        animation.setEndValue(morph_rect)
        
        def on_morph_finished():
            component.update()
            animation.setStartValue(morph_rect)
            animation.setEndValue(original_rect)
            animation.start()
        
        animation.finished.connect(on_morph_finished)
        state.animations["morph"] = animation
        return animation

    def save_settings(self):
        """**Save theme settings**"""
        self.settings.setValue("theme_mode", self._current_mode.value)
        self.settings.setValue("current_theme", self._current_theme)
        self.settings.setValue("animation_enabled", self._animation_enabled)
        self.settings.setValue("transition_duration", self._transition_duration)
        self.settings.setValue("transition_type", self._transition_type.value)

    def load_settings(self):
        """**Load theme settings**"""
        mode_value = self.settings.value("theme_mode", ThemeMode.LIGHT.value)
        try:
            self._current_mode = ThemeMode(mode_value)
        except ValueError:
            self._current_mode = ThemeMode.LIGHT
        
        self._current_theme = str(self.settings.value("current_theme", "default"))
        self._animation_enabled = bool(self.settings.value("animation_enabled", True))
        duration_value = self.settings.value("transition_duration", 250)
        try:
            self._transition_duration = int(str(duration_value))
        except Exception:
            self._transition_duration = 250
        
        transition_type_value = self.settings.value("transition_type", ThemeTransitionType.FADE.value)
        try:
            self._transition_type = ThemeTransitionType(transition_type_value)
        except ValueError:
            self._transition_type = ThemeTransitionType.FADE


# Enhanced global theme instance with lazy loading
_theme_manager = None

def get_theme_manager():
    """Get theme manager instance (lazy loading)"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = FluentTheme()
    return _theme_manager

# Backward compatibility proxy
class ThemeManagerProxy:
    """Theme manager proxy for lazy loading and backward compatibility"""
    def __getattr__(self, name):
        return getattr(get_theme_manager(), name)
    
    def __setattr__(self, name, value):
        setattr(get_theme_manager(), name, value)

theme_manager = ThemeManagerProxy()


# Utility functions for easier theme integration
def register_component_for_theme(component: QWidget):
    """Convenience function to register component for theme updates"""
    get_theme_manager().register_component(component)

def get_themed_style(component_type: str) -> str:
    """Convenience function to get themed style for component"""
    return get_theme_manager().get_style_sheet(component_type)

def create_theme_transition(component: QWidget,
                          transition_type: Optional[ThemeTransitionType] = None) -> Optional[QPropertyAnimation]:
    """Convenience function to create theme transition animation"""
    return get_theme_manager().create_component_transition(component, transition_type)
