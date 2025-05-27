"""
Simple Fluent UI Bootstrap File
Updates the __init__.py files to include the new components
"""

import os
import sys

def update_init_files():
    """Update __init__ files to include new components"""
    print("Updating __init__ files...")
    
    # Update components/basic/__init__.py
    basic_init_path = "components/basic/__init__.py"
    new_components_basic = """# Import all basic components
from .button import FluentButton
from .checkbox import FluentCheckBox
from .combobox import FluentComboBox
from .progress import FluentProgressBar
from .spinbox import FluentSpinBox
from .textbox import FluentLineEdit, FluentTextEdit
from .badge import FluentBadge, FluentTag
from .toggle import FluentToggleSwitch

# Export all components
__all__ = [
    'FluentButton',
    'FluentCheckBox',
    'FluentComboBox',
    'FluentProgressBar',
    'FluentSpinBox',
    'FluentLineEdit',
    'FluentTextEdit',
    'FluentBadge',
    'FluentTag',
    'FluentToggleSwitch',
]
"""
    
    with open(basic_init_path, 'w') as f:
        f.write(new_components_basic)
    
    # Update components/data/__init__.py
    data_init_path = "components/data/__init__.py"
    new_components_data = """# Import all data components
from .charts import FluentProgressRing
from .entry import FluentMaskedLineEdit
from .status import FluentStatusIndicator
from .table import FluentTableWidget
from .tree import FluentTreeWidget
from .filter_sort import FluentFilterBar, FluentSortingMenu, FluentFilterSortHeader, FluentFilterProxyModel
from .formatters import FluentFormatter, FluentListFormatter, FluentDateTimeFormat, FluentNumberFormat
from .rich_text import FluentRichTextEditor, FluentMaskedInput
from .notification import FluentToast, FluentNotificationCenter, FluentStatusBadge
from .visualization import FluentTreeMap, FluentNetworkGraph

# Export all components
__all__ = [
    'FluentProgressRing',
    'FluentMaskedLineEdit',
    'FluentStatusIndicator',
    'FluentTableWidget',
    'FluentTreeWidget',
    'FluentFilterBar',
    'FluentSortingMenu',
    'FluentFilterSortHeader',
    'FluentFilterProxyModel',
    'FluentFormatter',
    'FluentListFormatter',
    'FluentDateTimeFormat',
    'FluentNumberFormat',
    'FluentRichTextEditor',
    'FluentMaskedInput',
    'FluentToast',
    'FluentNotificationCenter',
    'FluentStatusBadge',
    'FluentTreeMap',
    'FluentNetworkGraph',
]
"""
    
    with open(data_init_path, 'w') as f:
        f.write(new_components_data)
    
    print("__init__ files updated successfully.")

if __name__ == "__main__":
    update_init_files()
    print("Bootstrap completed successfully.")
