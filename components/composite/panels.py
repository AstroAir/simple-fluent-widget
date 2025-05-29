"""
Composite Panel Components

This module provides higher-level panel components that combine multiple basic
widgets into common patterns like settings panels, property editors, and dialogs.
"""

from typing import Optional, Dict, Any, List, Callable, Union
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QLabel, QLineEdit, QComboBox, QCheckBox, 
                               QSpinBox, QSlider, QTextEdit, QGroupBox,
                               QScrollArea, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

from ..core.enhanced_base import (FluentPanel, FluentStandardButton, 
                                   FluentLayoutBuilder, FluentCompositeWidget,
                                   FluentFormGroup)
from ..core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                         FluentStateTransition)
from ..core.theme import theme_manager
from ..basic.textbox import FluentLineEdit
from ..basic.button import FluentButton
from ..basic.checkbox import FluentCheckBox


class FluentSettingsPanel(FluentPanel):
    """
    High-level settings panel that automatically organizes settings into
    collapsible groups with consistent styling and validation.
    """
    
    setting_changed = Signal(str, object)  # setting_key, new_value
    
    def __init__(self, title: str = "Settings", parent: Optional[QWidget] = None):
        super().__init__(title, collapsible=False, parent=parent)
        self._settings_groups: Dict[str, FluentFormGroup] = {}
        self._current_values: Dict[str, Any] = {}
        
        # Setup main layout for settings groups
        self._setup_settings_layout()
        
    def _setup_settings_layout(self):
        """Setup the main settings layout"""
        # Add action buttons at the bottom
        self._setup_action_buttons()
        
    def _setup_action_buttons(self):
        """Setup action buttons (Apply, Reset, etc.)"""
        button_frame = QFrame()
        button_layout = FluentLayoutBuilder.create_horizontal_layout(spacing=8)
        button_frame.setLayout(button_layout)
        
        # Add stretch to push buttons to the right
        button_layout.addStretch()
        
        # Reset button
        self.reset_button = FluentStandardButton("Reset", size=(80, 32))
        self.reset_button.clicked.connect(self._reset_settings)
        button_layout.addWidget(self.reset_button)
        
        # Apply button  
        self.apply_button = FluentStandardButton("Apply", size=(80, 32))
        self.apply_button.clicked.connect(self._apply_settings)
        button_layout.addWidget(self.apply_button)
        
        self.addWidget(button_frame)
        
    def add_settings_group(self, group_name: str, title: str = None) -> FluentFormGroup:
        """Add a new settings group"""
        if title is None:
            title = group_name
            
        group = FluentFormGroup(title, collapsible=True)
        self._settings_groups[group_name] = group
        
        # Insert before action buttons
        layout = self.content_layout
        layout.insertWidget(layout.count() - 1, group)
        
        return group
        
    def add_text_setting(self, group_name: str, setting_key: str, 
                        label: str, default_value: str = "",
                        placeholder: str = "") -> FluentLineEdit:
        """Add a text input setting"""
        group = self._get_or_create_group(group_name)
        
        field_edit = FluentLineEdit()
        field_edit.setText(default_value)
        if placeholder:
            field_edit.setPlaceholderText(placeholder)
            
        field_edit.textChanged.connect(
            lambda text: self._on_setting_changed(setting_key, text))
        
        group.add_field(label, field_edit)
        self._current_values[setting_key] = default_value
        
        return field_edit
        
    def add_choice_setting(self, group_name: str, setting_key: str,
                          label: str, choices: List[str], 
                          default_index: int = 0) -> QComboBox:
        """Add a choice dropdown setting"""
        group = self._get_or_create_group(group_name)
        
        combo = QComboBox()
        combo.addItems(choices)
        combo.setCurrentIndex(default_index)
        
        combo.currentTextChanged.connect(
            lambda text: self._on_setting_changed(setting_key, text))
            
        group.add_field(label, combo)
        self._current_values[setting_key] = choices[default_index] if choices else ""
        
        return combo
        
    def add_boolean_setting(self, group_name: str, setting_key: str,
                           label: str, default_value: bool = False) -> FluentCheckBox:
        """Add a boolean checkbox setting"""
        group = self._get_or_create_group(group_name)
        
        checkbox = FluentCheckBox(label)
        checkbox.setChecked(default_value)
        
        checkbox.toggled.connect(
            lambda checked: self._on_setting_changed(setting_key, checked))
            
        group.addWidget(checkbox)
        self._current_values[setting_key] = default_value
        
        return checkbox
        
    def add_number_setting(self, group_name: str, setting_key: str,
                          label: str, default_value: int = 0,
                          min_value: int = 0, max_value: int = 100) -> QSpinBox:
        """Add a number input setting"""
        group = self._get_or_create_group(group_name)
        
        spinbox = QSpinBox()
        spinbox.setRange(min_value, max_value)
        spinbox.setValue(default_value)
        
        spinbox.valueChanged.connect(
            lambda value: self._on_setting_changed(setting_key, value))
            
        group.add_field(label, spinbox)
        self._current_values[setting_key] = default_value
        
        return spinbox
        
    def _get_or_create_group(self, group_name: str) -> FluentFormGroup:
        """Get existing group or create new one"""
        if group_name not in self._settings_groups:
            return self.add_settings_group(group_name)
        return self._settings_groups[group_name]
        
    def _on_setting_changed(self, setting_key: str, value: Any):
        """Handle setting value change"""
        self._current_values[setting_key] = value
        self.setting_changed.emit(setting_key, value)
        
    def _apply_settings(self):
        """Apply current settings"""
        # Validate all form groups first
        all_valid = True
        for group in self._settings_groups.values():
            if hasattr(group, 'validate') and not group.validate():
                all_valid = False
                
        if all_valid:
            # Apply settings logic here
            pass
            
    def _reset_settings(self):
        """Reset all settings to defaults"""
        # Reset logic here
        pass
        
    def get_setting_value(self, setting_key: str) -> Any:
        """Get current value of a setting"""
        return self._current_values.get(setting_key)
        
    def set_setting_value(self, setting_key: str, value: Any):
        """Set value of a setting"""
        self._current_values[setting_key] = value
        # Update UI controls here
        

class FluentPropertiesEditor(FluentCompositeWidget):
    """
    Properties editor panel for editing object properties with
    automatic type detection and validation.
    """
    
    property_changed = Signal(str, object)  # property_name, new_value
    
    def __init__(self, title: str = "Properties", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._properties: Dict[str, Any] = {}
        self._controls: Dict[str, QWidget] = {}
        
        self._setup_ui(title)
        
    def _setup_ui(self, title: str):
        """Setup the properties editor UI"""
        # Main layout
        layout = FluentLayoutBuilder.create_vertical_layout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Properties scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.properties_widget = QWidget()
        self.properties_layout = FluentLayoutBuilder.create_vertical_layout(spacing=4)
        self.properties_widget.setLayout(self.properties_layout)
        
        self.scroll_area.setWidget(self.properties_widget)
        layout.addWidget(self.scroll_area)
        
        # Add stretch at the bottom
        self.properties_layout.addStretch()
        
    def set_object_properties(self, obj: object, property_names: List[str] = None):
        """Set object to edit properties for"""
        self.clear_properties()
        
        if property_names is None:
            # Auto-detect properties
            property_names = [attr for attr in dir(obj) 
                            if not attr.startswith('_') and 
                            not callable(getattr(obj, attr))]
        
        for prop_name in property_names:
            if hasattr(obj, prop_name):
                value = getattr(obj, prop_name)
                self.add_property(prop_name, value, type(value))
                
    def add_property(self, name: str, value: Any, prop_type: type = None):
        """Add a property to edit"""
        if prop_type is None:
            prop_type = type(value)
            
        # Create appropriate control based on type
        control = self._create_control_for_type(prop_type, value)
        if control is None:
            return
            
        # Create property row
        prop_frame = QFrame()
        prop_layout = FluentLayoutBuilder.create_horizontal_layout()
        prop_frame.setLayout(prop_layout)
        
        # Property name label
        name_label = QLabel(name + ":")
        name_label.setMinimumWidth(120)
        name_label.setFont(QFont("Segoe UI", 9))
        prop_layout.addWidget(name_label)
        
        # Property control
        prop_layout.addWidget(control)
        
        # Store references
        self._properties[name] = value
        self._controls[name] = control
        
        # Insert before the stretch
        layout = self.properties_layout
        layout.insertWidget(layout.count() - 1, prop_frame)
        
    def _create_control_for_type(self, prop_type: type, value: Any) -> Optional[QWidget]:
        """Create appropriate control for property type"""
        if prop_type == str:
            control = FluentLineEdit()
            control.setText(str(value))
            control.textChanged.connect(
                lambda text, name=name: self._on_property_changed(name, text))
            return control
            
        elif prop_type == bool:
            control = FluentCheckBox()
            control.setChecked(bool(value))
            control.toggled.connect(
                lambda checked, name=name: self._on_property_changed(name, checked))
            return control
            
        elif prop_type == int:
            control = QSpinBox()
            control.setRange(-999999, 999999)
            control.setValue(int(value))
            control.valueChanged.connect(
                lambda val, name=name: self._on_property_changed(name, val))
            return control
            
        elif prop_type == float:
            control = QLineEdit()  # Could use QDoubleSpinBox
            control.setText(str(value))
            control.textChanged.connect(
                lambda text, name=name: self._on_property_changed(name, float(text) if text else 0.0))
            return control
            
        # Default for unknown types
        control = QLineEdit()
        control.setText(str(value))
        control.textChanged.connect(
            lambda text, name=name: self._on_property_changed(name, text))
        return control
        
    def _on_property_changed(self, name: str, value: Any):
        """Handle property value change"""
        self._properties[name] = value
        self.property_changed.emit(name, value)
        
    def clear_properties(self):
        """Clear all properties"""
        # Remove all property controls
        while self.properties_layout.count() > 1:  # Keep the stretch
            item = self.properties_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self._properties.clear()
        self._controls.clear()
        
    def get_property_value(self, name: str) -> Any:
        """Get current value of a property"""
        return self._properties.get(name)
        

class FluentFormDialog(FluentCompositeWidget):
    """
    High-level form dialog that automatically creates form fields
    and handles validation and submission.
    """
    
    submitted = Signal(dict)  # form_data
    cancelled = Signal()
    
    def __init__(self, title: str = "Form", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._form_fields: Dict[str, QWidget] = {}
        self._validators: Dict[str, Callable] = {}
        
        self._setup_ui(title)
        
    def _setup_ui(self, title: str):
        """Setup form dialog UI"""
        layout = FluentLayoutBuilder.create_vertical_layout()
        self.setLayout(layout)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Form area
        self.form_widget = QWidget()
        self.form_layout = FluentLayoutBuilder.create_vertical_layout()
        self.form_widget.setLayout(self.form_layout)
        layout.addWidget(self.form_widget)
        
        # Button area
        self._setup_buttons()
        
    def _setup_buttons(self):
        """Setup form buttons"""
        button_frame = QFrame()
        button_layout = FluentLayoutBuilder.create_horizontal_layout()
        button_frame.setLayout(button_layout)
        
        button_layout.addStretch()
        
        # Cancel button
        self.cancel_button = FluentStandardButton("Cancel", size=(80, 32))
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)
        
        # Submit button
        self.submit_button = FluentStandardButton("Submit", size=(80, 32))
        self.submit_button.clicked.connect(self._on_submit)
        button_layout.addWidget(self.submit_button)
        
        self.layout().addWidget(button_frame)
        
    def add_text_field(self, field_name: str, label: str, 
                      required: bool = False, validator: Callable = None) -> FluentLineEdit:
        """Add text input field"""
        field_edit = FluentLineEdit()
        field_edit.setPlaceholderText(f"Enter {label.lower()}")
        
        self._add_form_row(label, field_edit, required)
        self._form_fields[field_name] = field_edit
        
        if validator:
            self._validators[field_name] = validator
            
        return field_edit
        
    def add_choice_field(self, field_name: str, label: str, 
                        choices: List[str], required: bool = False) -> QComboBox:
        """Add choice field"""
        combo = QComboBox()
        combo.addItems(choices)
        
        self._add_form_row(label, combo, required)
        self._form_fields[field_name] = combo
        
        return combo
        
    def _add_form_row(self, label: str, widget: QWidget, required: bool = False):
        """Add a form row with label and widget"""
        row_frame = QFrame()
        row_layout = FluentLayoutBuilder.create_horizontal_layout()
        row_frame.setLayout(row_layout)
        
        # Label
        label_text = label + ("*" if required else "") + ":"
        label_widget = QLabel(label_text)
        label_widget.setMinimumWidth(100)
        if required:
            label_widget.setStyleSheet("color: red;")
            
        row_layout.addWidget(label_widget)
        row_layout.addWidget(widget, 1)
        
        self.form_layout.addWidget(row_frame)
        
    def _on_submit(self):
        """Handle form submission"""
        # Validate all fields
        if not self._validate_form():
            return
            
        # Collect form data
        form_data = {}
        for field_name, widget in self._form_fields.items():
            if isinstance(widget, FluentLineEdit):
                form_data[field_name] = widget.text()
            elif isinstance(widget, QComboBox):
                form_data[field_name] = widget.currentText()
            elif isinstance(widget, FluentCheckBox):
                form_data[field_name] = widget.isChecked()
                
        self.submitted.emit(form_data)
        
    def _on_cancel(self):
        """Handle form cancellation"""
        self.cancelled.emit()
        
    def _validate_form(self) -> bool:
        """Validate all form fields"""
        for field_name, validator in self._validators.items():
            widget = self._form_fields[field_name]
            value = widget.text() if hasattr(widget, 'text') else widget.currentText()
            
            if not validator(value):
                # Show validation error
                return False
                
        return True


class FluentConfirmationDialog(FluentCompositeWidget):
    """
    Standardized confirmation dialog with customizable actions and animations.
    """
    
    confirmed = Signal()
    rejected = Signal()
    
    def __init__(self, message: str = "Are you sure?", 
                 title: str = "Confirm", 
                 confirm_text: str = "Yes",
                 cancel_text: str = "No",
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._setup_ui(title, message, confirm_text, cancel_text)
        self._setup_animations()
        
    def _setup_ui(self, title: str, message: str, 
                  confirm_text: str, cancel_text: str):
        """Setup confirmation dialog UI"""
        layout = FluentLayoutBuilder.create_vertical_layout(spacing=16)
        self.setLayout(layout)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(message_label)
        
        # Buttons
        button_frame = QFrame()
        button_layout = FluentLayoutBuilder.create_horizontal_layout()
        button_frame.setLayout(button_layout)
        
        button_layout.addStretch()
        
        # Cancel button
        self.cancel_button = FluentStandardButton(cancel_text, size=(80, 32))
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)
        
        # Confirm button
        self.confirm_button = FluentStandardButton(confirm_text, size=(80, 32))
        self.confirm_button.clicked.connect(self._on_confirm)
        button_layout.addWidget(self.confirm_button)
        
        layout.addWidget(button_frame)
        
    def _setup_animations(self):
        """Setup entrance animations"""
        self._entrance_transition = FluentTransition.fade_in(self, duration=200)
        
    def _on_confirm(self):
        """Handle confirmation"""
        self.confirmed.emit()
        
    def _on_cancel(self):
        """Handle cancellation"""
        self.rejected.emit()
        
    def show_animated(self):
        """Show dialog with animation"""
        self.show()
        self._entrance_transition.start()
