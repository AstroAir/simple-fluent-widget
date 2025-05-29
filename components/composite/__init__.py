"""
Composite Fluent Design Components

This module contains higher-level composite components that combine multiple 
basic widgets into commonly-used UI patterns, reducing code duplication and 
improving consistency across applications.
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
    FluentBreadcrumbBar
)

from .forms import (
    FluentFieldGroup,
    FluentValidationForm,
    FluentQuickForm
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
    
    # Forms
    'FluentFieldGroup',
    'FluentValidationForm',
    'FluentQuickForm',
    
    # Toolbars
    'FluentActionToolbar',
    'FluentSearchToolbar',
    'FluentViewToolbar',
    'FluentStatusToolbar'
    'FluentActionToolbar',
    'FluentSearchToolbar',
    'FluentViewToolbar'
]
