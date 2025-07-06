"""
Enhanced Base Classes for Fluent Layout Components
Provides consistent patterns for layout behavior, styling, and responsive design
"""

from typing import Optional, Dict, Any, List, Callable, Union
from abc import ABC, abstractmethod
from enum import Enum

from PySide6.QtWidgets import QWidget, QFrame, QLayout, QLayoutItem, QSizePolicy
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer, QSize, QRect, QMargins, QByteArray
from PySide6.QtGui import QResizeEvent, QShowEvent, QHideEvent

from core.enhanced_base import FluentBaseWidget
from core.theme import theme_manager
from core.enhanced_animations import FluentAnimation


class FluentLayoutBase(FluentBaseWidget):
    """
    Enhanced base class for all Fluent layout components
    
    Provides:
    - Consistent responsive behavior
    - Theme integration with layout-specific tokens
    - Animation patterns for layout changes
    - Accessibility support
    - Performance optimization
    """
    
    # Layout change signals
    layout_changed = Signal()
    layout_animating = Signal(bool)  # True when starting, False when finished
    responsive_breakpoint_changed = Signal(str)  # breakpoint name
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Layout properties
        self._spacing = 8
        self._padding = QMargins(0, 0, 0, 0)
        self._responsive_enabled = True
        self._layout_animations_enabled = True
        
        # Responsive breakpoints
        self._breakpoints = {
            'xs': 0,      # Extra small (mobile)
            'sm': 576,    # Small (large mobile)
            'md': 768,    # Medium (tablet)
            'lg': 992,    # Large (desktop)
            'xl': 1200,   # Extra large (large desktop)
            'xxl': 1400   # Extra extra large (wide desktop)
        }
        self._current_breakpoint = 'xs'
        
        # Animation system
        self._layout_animations = {}
        self._animation_duration = 200
        self._animation_easing = QEasingCurve.Type.OutCubic
        
        # Performance tracking
        self._layout_update_timer = QTimer()
        self._layout_update_timer.setSingleShot(True)
        self._layout_update_timer.setInterval(16)  # ~60fps
        self._layout_update_timer.timeout.connect(self._process_layout_update)
        
        # Setup
        self._setup_layout_base()
        
    def _setup_layout_base(self):
        """Setup base layout functionality"""
        # Apply theme
        self._apply_layout_theme()
        
        # Connect theme changes
        if theme_manager:
            theme_manager.theme_changed.connect(self._apply_layout_theme)
            
        # Setup responsive behavior
        self._update_current_breakpoint()
        
    def _apply_layout_theme(self):
        """Apply theme specific to layout components"""
        if not theme_manager:
            return
            
        # Get layout-specific theme tokens
        theme_tokens = {
            'spacing_xs': 4,
            'spacing_sm': 8, 
            'spacing_md': 16,
            'spacing_lg': 24,
            'spacing_xl': 32,
            'padding_xs': 4,
            'padding_sm': 8,
            'padding_md': 16,
            'padding_lg': 24,
            'padding_xl': 32,
            'border_radius': 8,
            'elevation_1': 2,
            'elevation_2': 4,
            'elevation_3': 8,
            'animation_duration_fast': 150,
            'animation_duration_normal': 200,
            'animation_duration_slow': 300,
        }
        
        # Update animation duration from theme
        self._animation_duration = theme_tokens.get('animation_duration_normal', 200)
        
        # Allow subclasses to customize theme application
        self._apply_custom_theme_tokens(theme_tokens)
        
    def _apply_custom_theme_tokens(self, tokens: Dict[str, Any]):
        """Override in subclasses to apply custom theme tokens"""
        pass
        
    def resizeEvent(self, event: QResizeEvent):
        """Handle resize events for responsive behavior"""
        super().resizeEvent(event)
        
        if self._responsive_enabled:
            old_breakpoint = self._current_breakpoint
            self._update_current_breakpoint()
            
            if old_breakpoint != self._current_breakpoint:
                self.responsive_breakpoint_changed.emit(self._current_breakpoint)
                self._on_breakpoint_changed(old_breakpoint, self._current_breakpoint)
                
        # Throttle layout updates for performance
        if self._layout_animations_enabled:
            self._layout_update_timer.start()
        else:
            self._process_layout_update()
            
    def _update_current_breakpoint(self):
        """Update current responsive breakpoint"""
        width = self.width()
        
        for name, min_width in reversed(list(self._breakpoints.items())):
            if width >= min_width:
                self._current_breakpoint = name
                break
                
    def _on_breakpoint_changed(self, old_breakpoint: str, new_breakpoint: str):
        """Handle responsive breakpoint changes - override in subclasses"""
        pass
        
    def _process_layout_update(self):
        """Process throttled layout updates"""
        if hasattr(self, '_needs_layout_update') and self._needs_layout_update:
            self._perform_layout_update()
            self._needs_layout_update = False
            
    def _perform_layout_update(self):
        """Perform actual layout update - override in subclasses"""
        self.layout_changed.emit()
        
    def request_layout_update(self):
        """Request a throttled layout update"""
        self._needs_layout_update = True
        if self._layout_animations_enabled:
            self._layout_update_timer.start()
        else:
            self._process_layout_update()
    
    # Public API
    
    def set_spacing(self, spacing: int):
        """Set spacing between layout items"""
        if self._spacing != spacing:
            self._spacing = spacing
            self.request_layout_update()
            
    def get_spacing(self) -> int:
        """Get current spacing"""
        return self._spacing
        
    def set_padding(self, left: int, top: Optional[int] = None, right: Optional[int] = None, bottom: Optional[int] = None):
        """Set layout padding"""
        if top is None:
            top = right = bottom = left
        elif right is None:
            right = left
            bottom = top
        elif bottom is None:
            bottom = top
            
        new_padding = QMargins(left, top, right, bottom)
        if self._padding != new_padding:
            self._padding = new_padding
            self.request_layout_update()
            
    def get_padding(self) -> QMargins:
        """Get current padding"""
        return self._padding
        
    def set_responsive_enabled(self, enabled: bool):
        """Enable or disable responsive behavior"""
        self._responsive_enabled = enabled
        
    def is_responsive_enabled(self) -> bool:
        """Check if responsive behavior is enabled"""
        return self._responsive_enabled
        
    def set_breakpoints(self, breakpoints: Dict[str, int]):
        """Set custom responsive breakpoints"""
        self._breakpoints = breakpoints.copy()
        self._update_current_breakpoint()
        
    def get_breakpoints(self) -> Dict[str, int]:
        """Get current breakpoints"""
        return self._breakpoints.copy()
        
    def get_current_breakpoint(self) -> str:
        """Get current responsive breakpoint"""
        return self._current_breakpoint
        
    def set_layout_animations_enabled(self, enabled: bool):
        """Enable or disable layout animations"""
        self._layout_animations_enabled = enabled
        
    def animate_layout_change(self, animation_name: str, property_name: str, 
                             start_value: Any, end_value: Any,
                             finished_callback: Optional[Callable] = None):
        """Animate a layout property change"""
        if not self._layout_animations_enabled:
            if finished_callback:
                finished_callback()
            return
            
        # Stop existing animation
        if animation_name in self._layout_animations:
            self._layout_animations[animation_name].stop()
            
        # Create new animation
        animation = QPropertyAnimation(self, QByteArray(property_name.encode('utf-8')))
        animation.setDuration(self._animation_duration)
        animation.setEasingCurve(self._animation_easing)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        
        if finished_callback:
            animation.finished.connect(finished_callback)
            
        # Track animation
        self._layout_animations[animation_name] = animation
        
        # Emit signals
        self.layout_animating.emit(True)
        animation.finished.connect(lambda: self.layout_animating.emit(False))
        
        animation.start()


class FluentContainerBase(FluentLayoutBase):
    """
    Base class for container layout components (Card, Expander, etc.)
    
    Provides:
    - Content area management
    - Header/footer support
    - Elevation effects
    - Click interactions
    """
    
    # Container signals
    content_changed = Signal()
    clicked = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Container properties
        self._clickable = False
        self._elevated = False
        self._elevation_level = 1
        self._corner_radius = 8
        
        # Content areas
        self._header_widget = None
        self._content_widget = None
        self._footer_widget = None
        
        self._setup_container_base()
        
    def _setup_container_base(self):
        """Setup container-specific functionality"""
        # Only set frame style if this is a QFrame
        if hasattr(self, 'setFrameStyle') and isinstance(self, QFrame):
            self.setFrameStyle(QFrame.Shape.NoFrame)
        self._apply_container_styling()
        
    def _apply_container_styling(self):
        """Apply container-specific styling"""
        if not theme_manager:
            return
            
        elevation_shadow = ""
        if self._elevated:
            shadow_offset = 2 * self._elevation_level
            shadow_blur = 4 * self._elevation_level
            shadow_opacity = min(20 + (self._elevation_level * 5), 40)
            elevation_shadow = f"""
                border: 1px solid {theme_manager.get_color('border').name()};
                box-shadow: 0px {shadow_offset}px {shadow_blur}px rgba(0, 0, 0, {shadow_opacity / 100});
            """
            
        cursor_style = "cursor: pointer;" if self._clickable else ""
        
        style = f"""
            {self.__class__.__name__} {{
                background-color: {theme_manager.get_color('surface').name()};
                border-radius: {self._corner_radius}px;
                {elevation_shadow}
                {cursor_style}
            }}
        """
        
        self.setStyleSheet(style)
        
    def set_clickable(self, clickable: bool):
        """Set whether the container is clickable"""
        if self._clickable != clickable:
            self._clickable = clickable
            self._apply_container_styling()
            
    def is_clickable(self) -> bool:
        """Check if container is clickable"""
        return self._clickable
        
    def set_elevated(self, elevated: bool, level: int = 1):
        """Set elevation effect"""
        if self._elevated != elevated or self._elevation_level != level:
            self._elevated = elevated
            self._elevation_level = max(1, min(level, 5))
            self._apply_container_styling()
            
    def is_elevated(self) -> bool:
        """Check if container has elevation"""
        return self._elevated
        
    def set_corner_radius(self, radius: int):
        """Set corner radius"""
        if self._corner_radius != radius:
            self._corner_radius = max(0, radius)
            self._apply_container_styling()
            
    def get_corner_radius(self) -> int:
        """Get corner radius"""
        return self._corner_radius
        
    def mousePressEvent(self, event):
        """Handle mouse press for clickable containers"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class FluentAdaptiveLayoutBase(FluentLayoutBase):
    """
    Base class for adaptive layout components that change behavior based on screen size
    
    Provides:
    - Multiple layout strategies per breakpoint
    - Smooth transitions between layouts
    - Content overflow handling
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Adaptive properties
        self._layout_strategies = {}  # breakpoint -> layout configuration
        self._transition_animations = []
        
    def add_layout_strategy(self, breakpoint: str, strategy: Dict[str, Any]):
        """Add a layout strategy for a specific breakpoint"""
        self._layout_strategies[breakpoint] = strategy
        
    def _on_breakpoint_changed(self, old_breakpoint: str, new_breakpoint: str):
        """Handle breakpoint changes with layout strategy switching"""
        super()._on_breakpoint_changed(old_breakpoint, new_breakpoint)
        
        if new_breakpoint in self._layout_strategies:
            self._apply_layout_strategy(self._layout_strategies[new_breakpoint])
            
    def _apply_layout_strategy(self, strategy: Dict[str, Any]):
        """Apply a layout strategy - override in subclasses"""
        pass
