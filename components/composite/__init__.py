"""
Composite Fluent Design Components - Organized Structure

This module contains higher-level composite components organized by functionality:

- forms: Complex form systems with validation and field management
- interface: Interface management components (navigation, toolbars)
- containers: Container components (panels, dialogs, settings)

Enhanced with:
- Modern type system with dataclasses and slots
- Performance optimizations and caching
- Advanced animation system
- Comprehensive error handling
- Memory-efficient state management
"""

# Import from organized submodules
from .forms import *
from .interface import *
from .containers import *

# Legacy imports for backward compatibility
from .containers.panels import (
    FluentSettingsPanel,
    FluentPropertiesEditor,
    FluentFormDialog,
    FluentConfirmationDialog
)

from .interface.navigation import (
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

from .forms.forms import (
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

from .interface.toolbars import (
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
