"""
Fluent Component Interface Definitions
Provides consistent interfaces and contracts for all Fluent components
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Callable, Union, Protocol
from enum import Enum
from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QColor, QFont


class FluentComponentState(Enum):
    """Standard component states"""
    NORMAL = "normal"
    HOVERED = "hovered"
    PRESSED = "pressed"
    FOCUSED = "focused"
    DISABLED = "disabled"
    LOADING = "loading"
    ERROR = "error"
    SUCCESS = "success"


class FluentComponentSize(Enum):
    """Standard component sizes"""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE = "xlarge"


class FluentComponentVariant(Enum):
    """Standard component variants"""
    STANDARD = "standard"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACCENT = "accent"
    SUBTLE = "subtle"
    OUTLINE = "outline"
    HYPERLINK = "hyperlink"
    STEALTH = "stealth"


class IFluentThemeable(Protocol):
    """Interface for components that support theming"""
    
    @abstractmethod
    def apply_theme(self, theme_tokens: Dict[str, Any]) -> None:
        """Apply theme tokens to the component"""
        pass
    
    @abstractmethod
    def get_theme_tokens(self) -> Dict[str, Any]:
        """Get current theme tokens"""
        pass


class IFluentAnimatable(Protocol):
    """Interface for components that support animations"""
    
    @abstractmethod
    def set_animation_enabled(self, enabled: bool) -> None:
        """Enable or disable animations"""
        pass
    
    @abstractmethod
    def get_animation_duration(self) -> int:
        """Get animation duration in milliseconds"""
        pass
    
    @abstractmethod
    def set_animation_duration(self, duration: int) -> None:
        """Set animation duration in milliseconds"""
        pass


class IFluentAccessible(Protocol):
    """Interface for components that support accessibility"""
    
    @abstractmethod
    def set_accessible_name(self, name: str) -> None:
        """Set accessible name"""
        pass
    
    @abstractmethod
    def set_accessible_description(self, description: str) -> None:
        """Set accessible description"""
        pass
    
    @abstractmethod
    def set_accessible_role(self, role: str) -> None:
        """Set accessible role"""
        pass


class IFluentStateful(Protocol):
    """Interface for components that manage state"""
    
    state_changed = Signal(str)  # state name
    
    @abstractmethod
    def get_state(self) -> FluentComponentState:
        """Get current component state"""
        pass
    
    @abstractmethod
    def set_state(self, state: FluentComponentState) -> None:
        """Set component state"""
        pass


class IFluentValidatable(Protocol):
    """Interface for components that support validation"""
    
    validation_changed = Signal(bool)  # is_valid
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate component value"""
        pass
    
    @abstractmethod
    def get_validation_errors(self) -> List[str]:
        """Get validation errors"""
        pass
    
    @abstractmethod
    def set_validator(self, validator: Callable[[Any], bool]) -> None:
        """Set validation function"""
        pass


class IFluentResizable(Protocol):
    """Interface for components that support resizing"""
    
    @abstractmethod
    def set_minimum_size(self, width: int, height: int) -> None:
        """Set minimum size"""
        pass
    
    @abstractmethod
    def set_maximum_size(self, width: int, height: int) -> None:
        """Set maximum size"""
        pass
    
    @abstractmethod
    def set_preferred_size(self, width: int, height: int) -> None:
        """Set preferred size"""
        pass


class IFluentSelectable(Protocol):
    """Interface for components that support selection"""
    
    selection_changed = Signal()
    
    @abstractmethod
    def is_selected(self) -> bool:
        """Check if component is selected"""
        pass
    
    @abstractmethod
    def set_selected(self, selected: bool) -> None:
        """Set selection state"""
        pass


class IFluentContainer(Protocol):
    """Interface for components that contain other components"""
    
    @abstractmethod
    def add_child(self, child: 'IFluentComponent') -> None:
        """Add child component"""
        pass
    
    @abstractmethod
    def remove_child(self, child: 'IFluentComponent') -> None:
        """Remove child component"""
        pass
    
    @abstractmethod
    def get_children(self) -> List['IFluentComponent']:
        """Get all child components"""
        pass


class IFluentComponent(IFluentThemeable, IFluentAnimatable, IFluentAccessible, 
                      IFluentStateful, Protocol):
    """Main interface that all Fluent components should implement"""
    
    # Standard signals
    clicked = Signal()
    focus_changed = Signal(bool)
    hover_changed = Signal(bool)
    
    @abstractmethod
    def get_component_type(self) -> str:
        """Get component type identifier"""
        pass
    
    @abstractmethod
    def get_component_version(self) -> str:
        """Get component version"""
        pass
    
    @abstractmethod
    def set_size(self, size: FluentComponentSize) -> None:
        """Set component size"""
        pass
    
    @abstractmethod
    def set_variant(self, variant: FluentComponentVariant) -> None:
        """Set component variant"""
        pass


class FluentComponentMixin:
    """Mixin class providing common functionality for Fluent components"""
    
    def __init__(self):
        self._component_id: str = ""
        self._component_type: str = ""
        self._component_version: str = "1.0.0"
        self._size: FluentComponentSize = FluentComponentSize.MEDIUM
        self._variant: FluentComponentVariant = FluentComponentVariant.PRIMARY
        self._state: FluentComponentState = FluentComponentState.NORMAL
        self._theme_tokens: Dict[str, Any] = {}
        self._animation_enabled: bool = True
        self._animation_duration: int = 200
        
    def get_component_type(self) -> str:
        return self._component_type
    
    def get_component_version(self) -> str:
        return self._component_version
    
    def set_size(self, size: FluentComponentSize) -> None:
        if self._size != size:
            self._size = size
            self._on_size_changed()
    
    def set_variant(self, variant: FluentComponentVariant) -> None:
        if self._variant != variant:
            self._variant = variant
            self._on_variant_changed()
    
    def get_state(self) -> FluentComponentState:
        return self._state
    
    def set_state(self, state: FluentComponentState) -> None:
        if self._state != state:
            old_state = self._state
            self._state = state
            self._on_state_changed(old_state, state)
    
    def set_animation_enabled(self, enabled: bool) -> None:
        self._animation_enabled = enabled
    
    def get_animation_duration(self) -> int:
        return self._animation_duration
    
    def set_animation_duration(self, duration: int) -> None:
        self._animation_duration = max(0, duration)
    
    def _on_size_changed(self) -> None:
        """Override to handle size changes"""
        pass
    
    def _on_variant_changed(self) -> None:
        """Override to handle variant changes"""
        pass
    
    def _on_state_changed(self, old_state: FluentComponentState, 
                         new_state: FluentComponentState) -> None:
        """Override to handle state changes"""
        pass
