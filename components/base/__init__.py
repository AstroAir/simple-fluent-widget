"""
Base classes for Fluent Design components
Provides consistent patterns for component behavior, styling, and interactions
"""

from .fluent_control_base import (
    FluentControlBase,
    FluentInputBase, 
    FluentContainerBase,
    FluentNavigationBase,
    FluentThemeAware,
    # Type aliases
    FluentWidget,
)

from .fluent_component_interface import (
    IFluentComponent,
    IFluentThemeable,
    IFluentAnimatable,
    IFluentAccessible,
    IFluentStateful,
    IFluentValidatable,
    IFluentResizable,
    IFluentSelectable,
    IFluentContainer,
    FluentComponentMixin,
    FluentComponentState,
    FluentComponentSize,
    FluentComponentVariant
)

__all__ = [
    # Main base classes
    'FluentControlBase',
    'FluentInputBase',
    'FluentContainerBase', 
    'FluentNavigationBase',
    'FluentThemeAware',
    
    # Interfaces
    'IFluentComponent',
    'IFluentThemeable',
    'IFluentAnimatable',
    'IFluentAccessible',
    'IFluentStateful',
    'IFluentValidatable',
    'IFluentResizable',
    'IFluentSelectable',
    'IFluentContainer',
    'FluentComponentMixin',
    
    # Enums
    'FluentComponentState',
    'FluentComponentSize',
    'FluentComponentVariant',
    
    # Type aliases
    'FluentWidget',
    'FluentControl',
    'FluentInput',
    'FluentContainer',
    'FluentNavigation'
]
