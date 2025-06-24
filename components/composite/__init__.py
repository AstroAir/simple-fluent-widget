"""
Composite Fluent Design Components - Optimized for Python 3.11+

This module contains higher-level composite components that combine multiple 
basic widgets into commonly-used UI patterns with modern Python features.

Enhanced with:
- Modern type system with dataclasses and slots
- Performance optimizations and caching
- Advanced animation system
- Comprehensive error handling
- Memory-efficient state management
"""

from .panels import (
    FluentSettingsPanel,
    FluentPropertiesEditor,
    FluentFormDialog,
    FluentConfirmationDialog
)

from .navigation import (
    FluentSidebar,
    FluentHeaderNavigation,
    FluentBreadcrumbBar,
    # Modern type definitions
    NavigationItem,
    NavigationSection,
    HeaderAction,
    NavigationComponentState,
    NavigationMode
)

from .forms import (
    FluentFieldGroup,
    FluentValidationForm,
    FluentQuickForm,
    # Modern type definitions
    FieldType,
    ValidationResult,
    FieldDefinition,
    FormState,
    ValidationProtocol,
    FormFieldData
)

from .toolbars import (
    FluentActionToolbar,
    FluentSearchToolbar,
    FluentViewToolbar,
    FluentStatusToolbar
)

__all__ = [
    # Panels
    'FluentSettingsPanel',
    'FluentPropertiesEditor', 
    'FluentFormDialog',
    'FluentConfirmationDialog',
    
    # Navigation
    'FluentSidebar',
    'FluentHeaderNavigation',
    'FluentBreadcrumbBar',
    'NavigationItem',
    'NavigationSection',
    'HeaderAction',
    'NavigationComponentState',
    'NavigationMode',
    
    # Forms
    'FluentFieldGroup',
    'FluentValidationForm',
    'FluentQuickForm',
    'FieldType',
    'ValidationResult',
    'FieldDefinition',
    'FormState',
    'ValidationProtocol',
    'FormFieldData',
    
    # Toolbars
    'FluentActionToolbar',
    'FluentSearchToolbar',
    'FluentViewToolbar',
    'FluentStatusToolbar'
]
