"""
FluentFormDialog - Form dialogs for complex data entry

Features:
- Multiple input fields with validation
- Field groups and sections
- Real-time validation feedback
- Required field indicators
- Custom field types
- Data binding and form submission
- Field dependencies and conditional visibility
"""

from typing import Optional, Callable, Dict, Any, List, Union
from enum import Enum
from dataclasses import dataclass

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
                               QComboBox, QCheckBox, QRadioButton, QFrame,
                               QGroupBox, QScrollArea, QButtonGroup, QDialog)
from PySide6.QtCore import Signal, Qt

from .base_dialog import FluentBaseDialog, DialogType, DialogSize, ButtonRole


class FieldType(Enum):
    """Form field type enumeration."""
    TEXT = "text"
    MULTILINE_TEXT = "multiline_text"
    PASSWORD = "password"
    EMAIL = "email"
    INTEGER = "integer"
    DOUBLE = "double"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    COMBOBOX = "combobox"
    SECTION = "section"  # Visual section separator


@dataclass
class FieldConfig:
    """Configuration for a form field."""
    name: str
    label: str
    field_type: FieldType
    default_value: Any = None
    required: bool = False
    placeholder: str = ""
    validator: Optional[Callable] = None
    items: Optional[List[str]] = None  # For combobox/radio
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    help_text: str = ""
    visible: bool = True
    enabled: bool = True
    depends_on: Optional[str] = None  # Field dependency
    depends_value: Any = None  # Value that dependency must have


class FluentFormDialog(FluentBaseDialog):
    """
    A form dialog with Fluent Design styling.

    Provides complex form functionality with validation,
    field dependencies, and organized layout.
    """

    # Signals
    field_changed = Signal(str, object)  # Field name, new value
    validation_changed = Signal(bool)    # Overall form validity
    form_submitted = Signal(dict)        # Form data submitted

    def __init__(self, parent: Optional[QWidget] = None, title: str = "Form"):
        super().__init__(parent, title, DialogType.MODAL, DialogSize.LARGE)

        # Form state
        self._fields: Dict[str, FieldConfig] = {}
        self._field_widgets: Dict[str, Any] = {}
        self._field_labels: Dict[str, QLabel] = {}
        self._field_errors: Dict[str, QLabel] = {}
        self._radio_groups: Dict[str, QButtonGroup] = {}

        # Validation
        self._is_form_valid = False
        self._validation_enabled = True

        # Layout
        self._form_layout: Optional[QVBoxLayout] = None
        self._current_section: Optional[QGroupBox] = None

        self._setup_form_content()
        self._setup_default_buttons()

    def _setup_form_content(self):
        """Setup the scrollable form content area."""
        # Create scrollable area for form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)

        # Form widget
        form_widget = QWidget()
        self._form_layout = QVBoxLayout(form_widget)
        self._form_layout.setContentsMargins(0, 0, 0, 0)
        self._form_layout.setSpacing(16)

        scroll_area.setWidget(form_widget)
        self.add_content_widget(scroll_area, 1)

    def _setup_default_buttons(self):
        """Setup default form buttons."""
        self.add_button("Cancel", ButtonRole.CANCEL, self.reject)
        self.submit_button = self.add_button(
            "Submit", ButtonRole.PRIMARY, self._submit_form)

        # Initially disable submit button
        self.set_button_enabled(ButtonRole.PRIMARY, False)

    def add_field(self, config: FieldConfig) -> QWidget:
        """Add a field to the form."""
        if config.name in self._fields:
            raise ValueError(f"Field '{config.name}' already exists")

        self._fields[config.name] = config

        if config.field_type == FieldType.SECTION:
            return self._add_section(config)
        else:
            return self._add_input_field(config)

    def _add_section(self, config: FieldConfig) -> QGroupBox:
        """Add a section separator."""
        section = QGroupBox(config.label)
        section.setObjectName("formSection")
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(16, 16, 16, 16)
        section_layout.setSpacing(12)

        if self._form_layout:
            self._form_layout.addWidget(section)
        self._current_section = section

        return section

    def _add_input_field(self, config: FieldConfig) -> QWidget:
        """Add an input field to the form."""
        # Create field container
        field_container = QFrame()
        field_layout = QVBoxLayout(field_container)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(4)

        # Create label with required indicator
        label = self._create_field_label(config)
        field_layout.addWidget(label)
        self._field_labels[config.name] = label

        # Create input widget
        input_widget = self._create_input_widget(config)
        field_layout.addWidget(input_widget)
        self._field_widgets[config.name] = input_widget

        # Help text
        if config.help_text:
            help_label = QLabel(config.help_text)
            help_label.setObjectName("fieldHelp")
            help_label.setWordWrap(True)
            field_layout.addWidget(help_label)

        # Error label (initially hidden)
        error_label = QLabel()
        error_label.setObjectName("fieldError")
        error_label.setWordWrap(True)
        error_label.hide()
        field_layout.addWidget(error_label)
        self._field_errors[config.name] = error_label

        # Add to appropriate layout
        if self._current_section:
            section_layout = self._current_section.layout()
            if section_layout:
                section_layout.addWidget(field_container)
        elif self._form_layout:
            self._form_layout.addWidget(field_container)

        # Connect validation
        self._connect_field_validation(config.name, input_widget)

        # Set initial state
        self._set_field_value(config.name, config.default_value)
        self._update_field_visibility(config.name)

        return field_container

    def _create_field_label(self, config: FieldConfig) -> QLabel:
        """Create field label with required indicator."""
        label_text = config.label
        if config.required:
            label_text += " *"

        label = QLabel(label_text)
        label.setObjectName("fieldLabel")

        if config.required:
            # Add required styling
            label.setProperty("required", True)

        return label

    def _create_input_widget(self, config: FieldConfig) -> QWidget:
        """Create the appropriate input widget for the field type."""
        if config.field_type == FieldType.TEXT:
            widget = QLineEdit()
            widget.setPlaceholderText(config.placeholder)

        elif config.field_type == FieldType.MULTILINE_TEXT:
            widget = QTextEdit()
            widget.setMaximumHeight(100)

        elif config.field_type == FieldType.PASSWORD:
            widget = QLineEdit()
            widget.setEchoMode(QLineEdit.EchoMode.Password)
            widget.setPlaceholderText(config.placeholder)

        elif config.field_type == FieldType.EMAIL:
            widget = QLineEdit()
            widget.setPlaceholderText(
                config.placeholder or "email@example.com")

        elif config.field_type == FieldType.INTEGER:
            widget = QSpinBox()
            if config.min_value is not None:
                widget.setMinimum(int(config.min_value))
            if config.max_value is not None:
                widget.setMaximum(int(config.max_value))

        elif config.field_type == FieldType.DOUBLE:
            widget = QDoubleSpinBox()
            widget.setDecimals(2)
            if config.min_value is not None:
                widget.setMinimum(float(config.min_value))
            if config.max_value is not None:
                widget.setMaximum(float(config.max_value))

        elif config.field_type == FieldType.CHECKBOX:
            widget = QCheckBox(config.label)

        elif config.field_type == FieldType.RADIO:
            widget = self._create_radio_group(config)

        elif config.field_type == FieldType.COMBOBOX:
            widget = QComboBox()
            if config.items:
                widget.addItems(config.items)

        else:
            widget = QLineEdit()
            widget.setPlaceholderText(config.placeholder)

        widget.setEnabled(config.enabled)
        return widget

    def _create_radio_group(self, config: FieldConfig) -> QWidget:
        """Create radio button group."""
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        button_group = QButtonGroup()
        self._radio_groups[config.name] = button_group

        if config.items:
            for i, item in enumerate(config.items):
                radio = QRadioButton(item)
                button_group.addButton(radio, i)
                layout.addWidget(radio)

        return container

    def _connect_field_validation(self, field_name: str, widget: Any):
        """Connect field validation signals."""
        config = self._fields[field_name]

        # Use hasattr to safely check for signal existence
        if config.field_type == FieldType.TEXT and hasattr(widget, 'textChanged'):
            widget.textChanged.connect(
                lambda: self._validate_field(field_name))
        elif config.field_type == FieldType.MULTILINE_TEXT and hasattr(widget, 'textChanged'):
            widget.textChanged.connect(
                lambda: self._validate_field(field_name))
        elif config.field_type == FieldType.PASSWORD and hasattr(widget, 'textChanged'):
            widget.textChanged.connect(
                lambda: self._validate_field(field_name))
        elif config.field_type == FieldType.EMAIL and hasattr(widget, 'textChanged'):
            widget.textChanged.connect(
                lambda: self._validate_field(field_name))
        elif config.field_type == FieldType.INTEGER and hasattr(widget, 'valueChanged'):
            widget.valueChanged.connect(
                lambda: self._validate_field(field_name))
        elif config.field_type == FieldType.DOUBLE and hasattr(widget, 'valueChanged'):
            widget.valueChanged.connect(
                lambda: self._validate_field(field_name))
        elif config.field_type == FieldType.CHECKBOX and hasattr(widget, 'toggled'):
            widget.toggled.connect(lambda: self._validate_field(field_name))
        elif config.field_type == FieldType.RADIO:
            if field_name in self._radio_groups:
                self._radio_groups[field_name].buttonToggled.connect(
                    lambda: self._validate_field(field_name))
        elif config.field_type == FieldType.COMBOBOX and hasattr(widget, 'currentTextChanged'):
            widget.currentTextChanged.connect(
                lambda: self._validate_field(field_name))

    def _validate_field(self, field_name: str):
        """Validate a specific field."""
        if not self._validation_enabled:
            return

        config = self._fields[field_name]
        value = self.get_field_value(field_name)
        error_label = self._field_errors.get(field_name)

        is_valid = True
        error_message = ""

        # Required field validation
        if config.required and self._is_empty_value(value):
            is_valid = False
            error_message = "This field is required."

        # Email validation
        elif config.field_type == FieldType.EMAIL and value:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(value)):
                is_valid = False
                error_message = "Please enter a valid email address."

        # Custom validation
        elif is_valid and config.validator:
            try:
                result = config.validator(value)
                if result is False:
                    is_valid = False
                    error_message = "Invalid input."
                elif isinstance(result, str):
                    is_valid = False
                    error_message = result
            except Exception as e:
                is_valid = False
                error_message = str(e)

        # Update error display
        if error_label:
            if error_message:
                error_label.setText(error_message)
                error_label.show()
            else:
                error_label.hide()

        # Update field dependencies
        self._update_dependent_fields(field_name)

        # Emit field change signal
        self.field_changed.emit(field_name, value)

        # Update overall form validation
        self._update_form_validation()

    def _is_empty_value(self, value: Any) -> bool:
        """Check if value is considered empty."""
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, (list, tuple)) and not value:
            return True
        return False

    def _update_dependent_fields(self, changed_field: str):
        """Update fields that depend on the changed field."""
        for field_name, config in self._fields.items():
            if config.depends_on == changed_field:
                self._update_field_visibility(field_name)

    def _update_field_visibility(self, field_name: str):
        """Update field visibility based on dependencies."""
        config = self._fields[field_name]

        visible = config.visible

        # Check dependency
        if config.depends_on:
            dep_value = self.get_field_value(config.depends_on)
            visible = visible and (dep_value == config.depends_value)

        # Update widget visibility
        widget = self._field_widgets.get(field_name)
        label = self._field_labels.get(field_name)

        if widget:
            widget.parent().setVisible(visible)

    def _update_form_validation(self):
        """Update overall form validation state."""
        old_valid = self._is_form_valid
        self._is_form_valid = True

        for field_name, config in self._fields.items():
            if config.field_type == FieldType.SECTION:
                continue

            # Skip hidden fields
            widget = self._field_widgets.get(field_name)
            if widget and not widget.parent().isVisible():
                continue

            # Check required fields
            if config.required:
                value = self.get_field_value(field_name)
                if self._is_empty_value(value):
                    self._is_form_valid = False
                    break

            # Check field-specific validation
            error_label = self._field_errors.get(field_name)
            if error_label and error_label.isVisible():
                self._is_form_valid = False
                break

        # Update submit button
        self.set_button_enabled(ButtonRole.PRIMARY, self._is_form_valid)

        # Emit validation change if state changed
        if old_valid != self._is_form_valid:
            self.validation_changed.emit(self._is_form_valid)

    def get_field_value(self, field_name: str) -> Any:
        """Get the value of a specific field."""
        widget = self._field_widgets.get(field_name)
        config = self._fields.get(field_name)

        if not widget or not config:
            return None

        if config.field_type == FieldType.TEXT:
            return widget.text()
        elif config.field_type == FieldType.MULTILINE_TEXT:
            return widget.toPlainText()
        elif config.field_type == FieldType.PASSWORD:
            return widget.text()
        elif config.field_type == FieldType.EMAIL:
            return widget.text()
        elif config.field_type == FieldType.INTEGER:
            return widget.value()
        elif config.field_type == FieldType.DOUBLE:
            return widget.value()
        elif config.field_type == FieldType.CHECKBOX:
            return widget.isChecked()
        elif config.field_type == FieldType.RADIO:
            button_group = self._radio_groups.get(field_name)
            if button_group:
                checked_button = button_group.checkedButton()
                if checked_button:
                    return button_group.id(checked_button)
            return None
        elif config.field_type == FieldType.COMBOBOX:
            return widget.currentText()

        return None

    def _set_field_value(self, field_name: str, value: Any):
        """Set the value of a specific field."""
        if value is None:
            return

        widget = self._field_widgets.get(field_name)
        config = self._fields.get(field_name)

        if not widget or not config:
            return

        if config.field_type == FieldType.TEXT:
            widget.setText(str(value))
        elif config.field_type == FieldType.MULTILINE_TEXT:
            widget.setPlainText(str(value))
        elif config.field_type == FieldType.PASSWORD:
            widget.setText(str(value))
        elif config.field_type == FieldType.EMAIL:
            widget.setText(str(value))
        elif config.field_type == FieldType.INTEGER:
            widget.setValue(int(value))
        elif config.field_type == FieldType.DOUBLE:
            widget.setValue(float(value))
        elif config.field_type == FieldType.CHECKBOX:
            widget.setChecked(bool(value))
        elif config.field_type == FieldType.RADIO:
            button_group = self._radio_groups.get(field_name)
            if button_group and isinstance(value, int):
                button = button_group.button(value)
                if button:
                    button.setChecked(True)
        elif config.field_type == FieldType.COMBOBOX:
            widget.setCurrentText(str(value))

    def get_form_data(self) -> Dict[str, Any]:
        """Get all form data as a dictionary."""
        data = {}
        for field_name in self._fields:
            if self._fields[field_name].field_type != FieldType.SECTION:
                data[field_name] = self.get_field_value(field_name)
        return data

    def set_form_data(self, data: Dict[str, Any]):
        """Set form data from a dictionary."""
        self._validation_enabled = False  # Temporarily disable validation

        for field_name, value in data.items():
            if field_name in self._fields:
                self._set_field_value(field_name, value)

        self._validation_enabled = True

        # Validate all fields
        for field_name in self._fields:
            self._validate_field(field_name)

    def _submit_form(self):
        """Handle form submission."""
        if self._is_form_valid:
            data = self.get_form_data()
            self.form_submitted.emit(data)
            self.accept()

    def accept(self):
        """Accept the dialog."""
        self.close_animated(QDialog.DialogCode.Accepted)

    def reject(self):
        """Reject the dialog."""
        self.close_animated(QDialog.DialogCode.Rejected)


# Convenience functions for common form patterns
def create_contact_form(parent: Optional[QWidget] = None) -> FluentFormDialog:
    """Create a contact information form."""
    form = FluentFormDialog(parent, "Contact Information")

    # Personal section
    form.add_field(FieldConfig(
        "personal", "Personal Information", FieldType.SECTION))
    form.add_field(FieldConfig("first_name", "First Name",
                   FieldType.TEXT, required=True))
    form.add_field(FieldConfig("last_name", "Last Name",
                   FieldType.TEXT, required=True))
    form.add_field(FieldConfig("email", "Email",
                   FieldType.EMAIL, required=True))

    # Contact section
    form.add_field(FieldConfig(
        "contact", "Contact Details", FieldType.SECTION))
    form.add_field(FieldConfig("phone", "Phone Number", FieldType.TEXT))
    form.add_field(FieldConfig("address", "Address", FieldType.MULTILINE_TEXT))

    return form


def create_settings_form(parent: Optional[QWidget] = None) -> FluentFormDialog:
    """Create a settings configuration form."""
    form = FluentFormDialog(parent, "Settings")

    # General section
    form.add_field(FieldConfig(
        "general", "General Settings", FieldType.SECTION))
    form.add_field(FieldConfig("app_name", "Application Name",
                   FieldType.TEXT, required=True))
    form.add_field(FieldConfig("auto_save", "Auto-save",
                   FieldType.CHECKBOX, default_value=True))

    # Advanced section
    form.add_field(FieldConfig(
        "advanced", "Advanced Settings", FieldType.SECTION))
    form.add_field(FieldConfig("debug_mode", "Debug Mode", FieldType.CHECKBOX))
    form.add_field(FieldConfig("log_level", "Log Level", FieldType.COMBOBOX,
                               items=["DEBUG", "INFO", "WARNING", "ERROR"], default_value="INFO"))

    return form
