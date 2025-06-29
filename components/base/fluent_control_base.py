"""
Enhanced Base Classes for Fluent Design Components
Provides consistent patterns for component behavior, styling, and interactions
"""

from typing import Optional, Dict, Any, List, Callable, Union
from abc import ABC, abstractmethod

from PySide6.QtWidgets import QWidget, QFrame, QPushButton, QLineEdit
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer, Property
from PySide6.QtGui import QFont, QColor, QIcon

from core.enhanced_base import FluentBaseWidget
from core.theme import theme_manager
from core.enhanced_animations import FluentAnimation, FluentTransition


class FluentControlBase(FluentBaseWidget):
    """
    Base class for all interactive Fluent controls
    
    Provides:
    - Consistent state management
    - Theme integration
    - Animation patterns
    - Accessibility support
    - Event handling patterns
    """
    
    # Common signals
    state_changed = Signal(str)  # State change notifications
    theme_applied = Signal()     # Theme change notifications
    interaction_started = Signal()  # User interaction start
    interaction_finished = Signal()  # User interaction end
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # State management
        self._control_state = "normal"  # normal, hovered, pressed, focused, disabled
        self._previous_state = "normal"
        self._state_transition_enabled = True
        
        # Theme integration
        self._theme_tokens = {}
        self._cached_styles = {}
        self._theme_version = 0
        
        # Animation system
        self._animations = {}
        self._animation_duration = 200
        self._animation_easing = QEasingCurve.Type.OutCubic
        
        # Accessibility
        self._accessible_name = ""
        self._accessible_description = ""
        self._keyboard_navigation_enabled = True
        
        # Setup
        self._setup_control_base()
        self._connect_theme_changes()
        
    def _setup_control_base(self):
        """Setup base control functionality"""
        # Apply initial theme
        self._update_theme_tokens()
        self._apply_theme()
        
        # Setup animations
        self._setup_base_animations()
        
        # Setup accessibility
        self._setup_accessibility()
        
    def _connect_theme_changes(self):
        """Connect to theme change notifications"""
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)
            
    def _setup_base_animations(self):
        """Setup common animations for state transitions"""
        # State transition animation
        self._state_animation = QPropertyAnimation(self, b"geometry")
        self._state_animation.setDuration(self._animation_duration)
        self._state_animation.setEasingCurve(self._animation_easing)
        
        # Store animation reference
        self._animations["state"] = self._state_animation
        
    def _setup_accessibility(self):
        """Setup accessibility features"""
        # Set accessible properties
        if self._accessible_name:
            self.setAccessibleName(self._accessible_name)
        if self._accessible_description:
            self.setAccessibleDescription(self._accessible_description)
            
    def _update_theme_tokens(self):
        """Update theme tokens from theme manager"""
        if not theme_manager:
            return
            
        # Get current theme tokens
        self._theme_tokens = {
            "primary": theme_manager.get_color("primary"),
            "secondary": theme_manager.get_color("secondary"),
            "surface": theme_manager.get_color("surface"),
            "background": theme_manager.get_color("background"),
            "border": theme_manager.get_color("border"),
            "text_primary": theme_manager.get_color("text_primary"),
            "text_secondary": theme_manager.get_color("text_secondary"),
            "corner_radius": theme_manager.get_radius("medium"),
            "elevation": theme_manager.get_elevation("low")
        }
        
        # Update theme version for cache invalidation
        self._theme_version = getattr(theme_manager, '_version', 0)
        
    def _apply_theme(self):
        """Apply theme to the control"""
        # Clear style cache if theme changed
        if self._should_invalidate_cache():
            self._cached_styles.clear()
            
        # Apply themed styles
        self._apply_themed_styles()
        self.theme_applied.emit()
        
    def _should_invalidate_cache(self) -> bool:
        """Check if style cache should be invalidated"""
        current_version = getattr(theme_manager, '_version', 0)
        return current_version != self._theme_version
        
    @abstractmethod
    def _apply_themed_styles(self):
        """Apply themed styles - must be implemented by subclasses"""
        pass
        
    def set_control_state(self, state: str):
        """Set the control state with optional animation"""
        if state == self._control_state:
            return
            
        self._previous_state = self._control_state
        self._control_state = state
        
        # Animate state transition if enabled
        if self._state_transition_enabled:
            self._animate_state_transition()
            
        # Apply new state styling
        self._apply_state_styles()
        self.state_changed.emit(state)
        
    def get_control_state(self) -> str:
        """Get current control state"""
        return self._control_state
        
    def _animate_state_transition(self):
        """Animate transition between states"""
        # Override in subclasses for specific animations
        pass
        
    @abstractmethod
    def _apply_state_styles(self):
        """Apply styles for current state - must be implemented by subclasses"""
        pass
        
    def set_animation_duration(self, duration: int):
        """Set animation duration in milliseconds"""
        self._animation_duration = duration
        for animation in self._animations.values():
            if hasattr(animation, 'setDuration'):
                animation.setDuration(duration)
                
    def set_animation_easing(self, easing: QEasingCurve.Type):
        """Set animation easing curve"""
        self._animation_easing = easing
        for animation in self._animations.values():
            if hasattr(animation, 'setEasingCurve'):
                animation.setEasingCurve(easing)
                
    def enable_state_transitions(self, enabled: bool):
        """Enable or disable state transition animations"""
        self._state_transition_enabled = enabled
        
    def set_accessible_name(self, name: str):
        """Set accessible name for screen readers"""
        self._accessible_name = name
        self.setAccessibleName(name)
        
    def set_accessible_description(self, description: str):
        """Set accessible description for screen readers"""
        self._accessible_description = description
        self.setAccessibleDescription(description)
        
    def _on_theme_changed(self):
        """Handle theme changes"""
        self._update_theme_tokens()
        self._apply_theme()
        
    def cleanup(self):
        """Clean up resources"""
        # Stop all animations
        for animation in self._animations.values():
            if hasattr(animation, 'stop'):
                animation.stop()
                
        # Clear caches
        self._cached_styles.clear()
        self._theme_tokens.clear()
        
        super().cleanup()


class FluentInputBase(FluentControlBase):
    """
    Base class for input controls (text boxes, number inputs, etc.)
    
    Provides:
    - Input validation
    - Placeholder text handling
    - Error state management
    - Input formatting
    - Accessibility for inputs
    """
    
    # Input-specific signals
    value_changed = Signal(object)  # Value changed
    validation_changed = Signal(bool)  # Validation state changed
    input_started = Signal()  # User started input
    input_finished = Signal()  # User finished input
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Input properties
        self._value = None
        self._placeholder_text = ""
        self._is_required = False
        self._is_readonly = False
        self._is_valid = True
        self._validation_message = ""
        
        # Validation
        self._validators = []
        self._validation_enabled = True
        
        # Formatting
        self._input_formatter = None
        self._display_formatter = None
        
        # Setup input-specific features
        self._setup_input_base()
        
    def _setup_input_base(self):
        """Setup input-specific functionality"""
        # Setup validation
        self._setup_validation()
        
        # Setup formatting
        self._setup_formatting()
        
    def _setup_validation(self):
        """Setup input validation"""
        # Connect validation to value changes
        self.value_changed.connect(self._validate_input)
        
    def _setup_formatting(self):
        """Setup input/display formatting"""
        pass  # Override in subclasses
        
    def set_value(self, value: Any):
        """Set the input value"""
        if value == self._value:
            return
            
        self._value = value
        self._update_display()
        self._validate_input()
        self.value_changed.emit(value)
        
    def get_value(self) -> Any:
        """Get the current input value"""
        return self._value
        
    def set_placeholder_text(self, text: str):
        """Set placeholder text"""
        self._placeholder_text = text
        self._update_placeholder()
        
    def get_placeholder_text(self) -> str:
        """Get placeholder text"""
        return self._placeholder_text
        
    def set_required(self, required: bool):
        """Set whether input is required"""
        self._is_required = required
        self._validate_input()
        
    def is_required(self) -> bool:
        """Check if input is required"""
        return self._is_required
        
    def set_readonly(self, readonly: bool):
        """Set read-only state"""
        self._is_readonly = readonly
        self._update_readonly_state()
        
    def is_readonly(self) -> bool:
        """Check if input is read-only"""
        return self._is_readonly
        
    def add_validator(self, validator: Callable[[Any], tuple[bool, str]]):
        """Add a validation function"""
        self._validators.append(validator)
        
    def remove_validator(self, validator: Callable):
        """Remove a validation function"""
        if validator in self._validators:
            self._validators.remove(validator)
            
    def enable_validation(self, enabled: bool):
        """Enable or disable validation"""
        self._validation_enabled = enabled
        if enabled:
            self._validate_input()
            
    def is_valid(self) -> bool:
        """Check if current input is valid"""
        return self._is_valid
        
    def get_validation_message(self) -> str:
        """Get current validation message"""
        return self._validation_message
        
    def _validate_input(self):
        """Validate current input"""
        if not self._validation_enabled:
            return
            
        # Check required validation
        if self._is_required and not self._value:
            self._set_validation_state(False, "This field is required")
            return
            
        # Run custom validators
        for validator in self._validators:
            is_valid, message = validator(self._value)
            if not is_valid:
                self._set_validation_state(False, message)
                return
                
        # All validations passed
        self._set_validation_state(True, "")
        
    def _set_validation_state(self, is_valid: bool, message: str):
        """Set validation state"""
        if self._is_valid == is_valid and self._validation_message == message:
            return
            
        self._is_valid = is_valid
        self._validation_message = message
        
        # Update visual state
        if is_valid:
            self.set_control_state("normal")
        else:
            self.set_control_state("error")
            
        self.validation_changed.emit(is_valid)
        
    @abstractmethod
    def _update_display(self):
        """Update the display of the input - must be implemented by subclasses"""
        pass
        
    @abstractmethod
    def _update_placeholder(self):
        """Update placeholder display - must be implemented by subclasses"""
        pass
        
    @abstractmethod
    def _update_readonly_state(self):
        """Update read-only state - must be implemented by subclasses"""
        pass


class FluentContainerBase(FluentControlBase):
    """
    Base class for container controls (cards, panels, dialogs, etc.)
    
    Provides:
    - Child widget management
    - Layout coordination
    - Container styling
    - Responsive behavior
    - Animation coordination
    """
    
    # Container-specific signals
    child_added = Signal(QWidget)
    child_removed = Signal(QWidget)
    layout_changed = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Container properties
        self._child_widgets = []
        self._layout_manager = None
        self._responsive_enabled = True
        self._padding = {"top": 16, "right": 16, "bottom": 16, "left": 16}
        self._spacing = 8
        
        # Animation coordination
        self._child_animations = {}
        self._layout_animation_enabled = True
        
        # Setup container-specific features
        self._setup_container_base()
        
    def _setup_container_base(self):
        """Setup container-specific functionality"""
        # Setup responsive behavior
        self._setup_responsive_behavior()
        
        # Setup layout management
        self._setup_layout_management()
        
    def _setup_responsive_behavior(self):
        """Setup responsive behavior"""
        if self._responsive_enabled:
            # Connect to resize events
            self.resizeEvent = self._on_resize_event
            
    def _setup_layout_management(self):
        """Setup layout management"""
        pass  # Override in subclasses
        
    def add_child(self, widget: QWidget, **kwargs):
        """Add a child widget with optional animation"""
        if widget in self._child_widgets:
            return
            
        self._child_widgets.append(widget)
        widget.setParent(self)
        
        # Add to layout if available
        if self._layout_manager:
            self._add_to_layout(widget, **kwargs)
            
        # Animate entrance if enabled
        if self._layout_animation_enabled:
            self._animate_child_entrance(widget)
            
        self.child_added.emit(widget)
        
    def remove_child(self, widget: QWidget):
        """Remove a child widget with optional animation"""
        if widget not in self._child_widgets:
            return
            
        # Animate exit if enabled
        if self._layout_animation_enabled:
            self._animate_child_exit(widget, self._complete_child_removal)
        else:
            self._complete_child_removal(widget)
            
    def _complete_child_removal(self, widget: QWidget):
        """Complete child widget removal"""
        if widget in self._child_widgets:
            self._child_widgets.remove(widget)
            
        # Remove from layout
        if self._layout_manager:
            self._remove_from_layout(widget)
            
        widget.setParent(None)
        self.child_removed.emit(widget)
        
    def get_children(self) -> List[QWidget]:
        """Get list of child widgets"""
        return self._child_widgets.copy()
        
    def set_padding(self, top: int = None, right: int = None, 
                   bottom: int = None, left: int = None):
        """Set container padding"""
        if top is not None:
            self._padding["top"] = top
        if right is not None:
            self._padding["right"] = right
        if bottom is not None:
            self._padding["bottom"] = bottom
        if left is not None:
            self._padding["left"] = left
            
        self._update_layout_margins()
        
    def get_padding(self) -> Dict[str, int]:
        """Get container padding"""
        return self._padding.copy()
        
    def set_spacing(self, spacing: int):
        """Set spacing between child widgets"""
        self._spacing = spacing
        self._update_layout_spacing()
        
    def get_spacing(self) -> int:
        """Get spacing between child widgets"""
        return self._spacing
        
    def enable_responsive_behavior(self, enabled: bool):
        """Enable or disable responsive behavior"""
        self._responsive_enabled = enabled
        
    def enable_layout_animations(self, enabled: bool):
        """Enable or disable layout animations"""
        self._layout_animation_enabled = enabled
        
    @abstractmethod
    def _add_to_layout(self, widget: QWidget, **kwargs):
        """Add widget to layout - must be implemented by subclasses"""
        pass
        
    @abstractmethod
    def _remove_from_layout(self, widget: QWidget):
        """Remove widget from layout - must be implemented by subclasses"""
        pass
        
    @abstractmethod
    def _update_layout_margins(self):
        """Update layout margins - must be implemented by subclasses"""
        pass
        
    @abstractmethod
    def _update_layout_spacing(self):
        """Update layout spacing - must be implemented by subclasses"""
        pass
        
    def _animate_child_entrance(self, widget: QWidget):
        """Animate child widget entrance"""
        # Override in subclasses for specific animations
        pass
        
    def _animate_child_exit(self, widget: QWidget, callback: Callable):
        """Animate child widget exit"""
        # Override in subclasses for specific animations
        if callback:
            callback(widget)
            
    def _on_resize_event(self, event):
        """Handle resize events for responsive behavior"""
        # Override in subclasses for responsive behavior
        pass


class FluentNavigationBase(FluentControlBase):
    """
    Base class for navigation controls (menus, tabs, breadcrumbs, etc.)
    
    Provides:
    - Navigation item management
    - Selection handling
    - Keyboard navigation
    - Navigation events
    """
    
    # Navigation-specific signals
    item_selected = Signal(str)  # Item ID selected
    item_activated = Signal(str)  # Item activated (double-click/enter)
    navigation_requested = Signal(str, object)  # Navigation request with data
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Navigation properties
        self._navigation_items = {}
        self._selected_item_id = None
        self._allow_multiple_selection = False
        self._selected_items = set()
        
        # Keyboard navigation
        self._keyboard_navigation_enabled = True
        self._current_focus_item = None
        
        # Setup navigation-specific features
        self._setup_navigation_base()
        
    def _setup_navigation_base(self):
        """Setup navigation-specific functionality"""
        # Setup keyboard navigation
        self._setup_keyboard_navigation()
        
        # Enable focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def _setup_keyboard_navigation(self):
        """Setup keyboard navigation"""
        if self._keyboard_navigation_enabled:
            self.keyPressEvent = self._handle_key_press
            
    def add_navigation_item(self, item_id: str, item_data: Dict[str, Any]):
        """Add a navigation item"""
        self._navigation_items[item_id] = item_data
        self._create_visual_item(item_id, item_data)
        
    def remove_navigation_item(self, item_id: str):
        """Remove a navigation item"""
        if item_id in self._navigation_items:
            del self._navigation_items[item_id]
            self._remove_visual_item(item_id)
            
        # Clear selection if removed item was selected
        if item_id == self._selected_item_id:
            self.clear_selection()
            
    def get_navigation_items(self) -> Dict[str, Dict[str, Any]]:
        """Get all navigation items"""
        return self._navigation_items.copy()
        
    def select_item(self, item_id: str):
        """Select a navigation item"""
        if item_id not in self._navigation_items:
            return
            
        # Handle multiple selection
        if self._allow_multiple_selection:
            self._selected_items.add(item_id)
        else:
            self._selected_items.clear()
            self._selected_items.add(item_id)
            self._selected_item_id = item_id
            
        self._update_item_selection(item_id, True)
        self.item_selected.emit(item_id)
        
    def deselect_item(self, item_id: str):
        """Deselect a navigation item"""
        if item_id in self._selected_items:
            self._selected_items.remove(item_id)
            
        if item_id == self._selected_item_id:
            self._selected_item_id = None
            
        self._update_item_selection(item_id, False)
        
    def clear_selection(self):
        """Clear all selections"""
        for item_id in self._selected_items.copy():
            self.deselect_item(item_id)
            
    def get_selected_item(self) -> Optional[str]:
        """Get the selected item ID"""
        return self._selected_item_id
        
    def get_selected_items(self) -> List[str]:
        """Get all selected item IDs"""
        return list(self._selected_items)
        
    def set_multiple_selection(self, enabled: bool):
        """Enable or disable multiple selection"""
        self._allow_multiple_selection = enabled
        if not enabled and len(self._selected_items) > 1:
            # Keep only the last selected item
            if self._selected_item_id:
                self.clear_selection()
                self.select_item(self._selected_item_id)
                
    def enable_keyboard_navigation(self, enabled: bool):
        """Enable or disable keyboard navigation"""
        self._keyboard_navigation_enabled = enabled
        
    @abstractmethod
    def _create_visual_item(self, item_id: str, item_data: Dict[str, Any]):
        """Create visual representation of item - must be implemented by subclasses"""
        pass
        
    @abstractmethod
    def _remove_visual_item(self, item_id: str):
        """Remove visual representation of item - must be implemented by subclasses"""
        pass
        
    @abstractmethod
    def _update_item_selection(self, item_id: str, selected: bool):
        """Update visual selection state - must be implemented by subclasses"""
        pass
        
    def _handle_key_press(self, event):
        """Handle keyboard navigation"""
        # Override in subclasses for specific navigation behavior
        super().keyPressEvent(event)


class FluentThemeAware:
    """
    Mixin class providing theme awareness for Fluent components.
    
    This class provides common theme-related functionality that can be
    mixed into any component to add theme support.
    """
    
    def __init__(self):
        self._theme_cache = {}
        self._current_theme = None
        
    def get_current_theme(self) -> Optional[Dict[str, Any]]:
        """Get the current theme dictionary."""
        try:
            from core.theme import theme_manager
            return theme_manager.get_current_theme()
        except ImportError:
            return self._current_theme
            
    def get_theme_color(self, color_key: str, default: str = "#000000") -> str:
        """
        Get a color from the current theme.
        
        Args:
            color_key: Key for the color in the theme
            default: Default color if key not found
            
        Returns:
            Color string (hex format)
        """
        theme = self.get_current_theme()
        if theme and color_key in theme:
            return theme[color_key]
        return default
        
    def apply_theme(self):
        """Apply theme to the component. Override in subclasses."""
        pass
        
    def on_theme_changed(self):
        """Called when theme changes. Override in subclasses."""
        self.apply_theme()


# Convenience type aliases
FluentWidget = Union[FluentControlBase, FluentContainerBase, FluentNavigationBase]
