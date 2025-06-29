"""
Fluent Design Dialog Components

This module provides comprehensive Fluent Design dialog components including:
- FluentBaseDialog: Base class for all dialogs with consistent styling and behavior
- FluentContentDialog: Modal dialog container for general content
- FluentMessageDialog: Simple message dialogs with preset types  
- FluentInputDialog: Input dialogs for collecting user data
- FluentProgressDialog: Progress dialogs for long-running operations
- FluentFormDialog: Complex form dialogs with validation
- FluentTeachingTip: Contextual help tooltips and guidance
"""

# Base dialog infrastructure
from .base_dialog import (
    FluentBaseDialog, FluentDialogBuilder,
    DialogSize, DialogType, ButtonRole
)

# Specific dialog types
from .content_dialog import FluentContentDialog, show_content_dialog
from .message_dialog import (
    FluentMessageDialog, MessageType, MessageResult,
    show_information_dialog, show_warning_dialog, show_error_dialog,
    show_question_dialog, show_success_dialog
)
from .input_dialog import (
    FluentInputDialog, InputType,
    get_text_input, get_password_input, get_number_input,
    get_choice_input, get_file_path, get_folder_path
)
from .progress_dialog import (
    FluentProgressDialog, ProgressMode, ProgressContext,
    show_progress_dialog
)
from .form_dialog import (
    FluentFormDialog, FieldType, FieldConfig,
    create_contact_form, create_settings_form
)
from .teaching_tip import FluentTeachingTip

__all__ = [
    # Base infrastructure
    'FluentBaseDialog',
    'FluentDialogBuilder', 
    'DialogSize',
    'DialogType',
    'ButtonRole',
    
    # Content dialog
    'FluentContentDialog',
    'show_content_dialog',
    
    # Message dialogs
    'FluentMessageDialog',
    'MessageType',
    'MessageResult',
    'show_information_dialog',
    'show_warning_dialog', 
    'show_error_dialog',
    'show_question_dialog',
    'show_success_dialog',
    
    # Input dialogs
    'FluentInputDialog',
    'InputType',
    'get_text_input',
    'get_password_input',
    'get_number_input',
    'get_choice_input',
    'get_file_path',
    'get_folder_path',
    
    # Progress dialogs
    'FluentProgressDialog',
    'ProgressMode', 
    'ProgressContext',
    'show_progress_dialog',
    
    # Form dialogs
    'FluentFormDialog',
    'FieldType',
    'FieldConfig',
    'create_contact_form',
    'create_settings_form',
    
    # Teaching tips
    'FluentTeachingTip'
]
