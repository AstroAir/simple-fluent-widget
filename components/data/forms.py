"""
Fluent Design Form Components
Advanced form controls with validation, multi-step forms, and form builders
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QFrame, QPushButton, QScrollArea, QComboBox, QTextEdit,
    QSpinBox, QDateEdit, QGroupBox,
    QProgressBar, QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont
from core.theme import theme_manager
from typing import Optional, List, Dict, Callable
import re


class ValidationRule:
    """Validation rule for form fields"""

    def __init__(self, validator: Callable[[str], bool], message: str, severity: str = "error"):
        self.validator = validator
        self.message = message
        self.severity = severity  # "error", "warning", "info"


class ValidationResult:
    """Result of form field validation"""

    def __init__(self, is_valid: bool = True, message: str = "", severity: str = "info"):
        self.is_valid = is_valid
        self.message = message
        self.severity = severity


class FluentFormField(QWidget):
    """Advanced form field with validation and styling"""

    # Signals
    valueChanged = Signal(str)
    validationChanged = Signal(bool)  # True if valid, False if invalid

    def __init__(self, parent: Optional[QWidget] = None, label: str = "",
                 required: bool = False, field_type: str = "text"):
        super().__init__(parent)

        self.label_text = label
        self.required = required
        self.field_type = field_type
        self.validation_rules: List[ValidationRule] = []
        self.current_validation = ValidationResult()

        self.input_widget: QWidget  # Declare type for clarity
        self.label: Optional[QLabel] = None
        self.validation_label: QLabel

        self.setup_ui()
        self.setup_style()
        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup the form field UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Label with required indicator
        if self.label_text:
            label_layout = QHBoxLayout()
            label_layout.setContentsMargins(0, 0, 0, 0)

            self.label = QLabel(self.label_text)
            self.label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
            label_layout.addWidget(self.label)

            if self.required:
                required_label = QLabel("*")
                required_label.setStyleSheet(
                    "color: #d13438; font-weight: bold;")
                label_layout.addWidget(required_label)

            label_layout.addStretch()
            layout.addLayout(label_layout)

        # Input widget based on field type
        self.input_widget = self.create_input_widget()
        layout.addWidget(self.input_widget)

        # Validation message
        self.validation_label = QLabel()
        self.validation_label.setVisible(False)
        self.validation_label.setWordWrap(True)
        self.validation_label.setFont(QFont("Segoe UI", 8))
        layout.addWidget(self.validation_label)

    def create_input_widget(self) -> QWidget:
        """Create the appropriate input widget based on field type"""
        widget: QWidget
        if self.field_type == "text":
            line_edit = QLineEdit()
            line_edit.textChanged.connect(
                lambda text: self.valueChanged.emit(text))
            line_edit.textChanged.connect(self.validate_field)
            widget = line_edit
        elif self.field_type == "email":
            email_edit = QLineEdit()
            email_edit.setPlaceholderText("example@domain.com")
            email_edit.textChanged.connect(
                lambda text: self.valueChanged.emit(text))
            email_edit.textChanged.connect(self.validate_field)
            # Add email validation
            self.add_validation_rule(
                lambda text: re.match(
                    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', text) is not None,
                "Please enter a valid email address"
            )
            widget = email_edit
        elif self.field_type == "password":
            password_edit = QLineEdit()
            password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            password_edit.textChanged.connect(
                lambda text: self.valueChanged.emit(text))
            password_edit.textChanged.connect(self.validate_field)
            widget = password_edit
        elif self.field_type == "number":
            spin_box = QSpinBox()
            spin_box.setMaximum(999999)
            spin_box.valueChanged.connect(
                lambda value: self.valueChanged.emit(str(value)))
            spin_box.valueChanged.connect(
                self.validate_field)  # Pass the int value
            widget = spin_box
        elif self.field_type == "date":
            date_edit = QDateEdit()
            date_edit.setDate(QDate.currentDate())
            date_edit.dateChanged.connect(lambda date: self.valueChanged.emit(
                date.toString(Qt.DateFormat.ISODate)))
            date_edit.dateChanged.connect(
                self.validate_field)  # Pass the QDate value
            widget = date_edit
        elif self.field_type == "textarea":
            text_area = QTextEdit()
            text_area.setMaximumHeight(100)
            text_area.textChanged.connect(
                lambda: self.valueChanged.emit(text_area.toPlainText()))
            text_area.textChanged.connect(self.validate_field)
            widget = text_area
        elif self.field_type == "dropdown":
            combo_box = QComboBox()
            combo_box.currentTextChanged.connect(self.valueChanged.emit)
            combo_box.currentTextChanged.connect(self.validate_field)
            widget = combo_box
        else:
            default_edit = QLineEdit()
            default_edit.textChanged.connect(
                lambda text: self.valueChanged.emit(text))
            default_edit.textChanged.connect(self.validate_field)
            widget = default_edit

        return widget

    def add_validation_rule(self, validator: Callable[[str], bool], message: str, severity: str = "error"):
        """Add a validation rule to this field"""
        rule = ValidationRule(validator, message, severity)
        self.validation_rules.append(rule)

    def validate_field(self, _=None):  # Add _ to accept potential arguments from signals
        """Validate the current field value"""
        value = self.get_value()

        # Check required field
        if self.required and not value.strip():
            self.set_validation_result(ValidationResult(
                False, "This field is required", "error"))
            return False

        # Check custom validation rules
        for rule in self.validation_rules:
            if not rule.validator(value):
                self.set_validation_result(ValidationResult(
                    False, rule.message, rule.severity))
                return False

        # All validations passed
        self.set_validation_result(ValidationResult(True))
        return True

    def set_validation_result(self, result: ValidationResult):
        """Set the validation result and update UI"""
        self.current_validation = result

        if result.is_valid:
            self.validation_label.setVisible(False)
            # Reset to themed style potentially
            self.input_widget.setStyleSheet("")
        else:
            self.validation_label.setText(result.message)
            self.validation_label.setVisible(True)

            error_border_style = "border: 2px solid #d13438;"
            warning_border_style = "border: 2px solid #f7630c;"

            current_style = self.input_widget.styleSheet()
            # Attempt to preserve other styles if possible, or simplify
            base_style_match = re.search(
                r'(QLineEdit|QTextEdit|QSpinBox|QDateEdit|QComboBox)\s*{[^}]*}', current_style)
            base_style = base_style_match.group(0) if base_style_match else ""

            if result.severity == "error":
                self.validation_label.setStyleSheet("color: #d13438;")
                self.input_widget.setStyleSheet(
                    base_style + error_border_style)
            elif result.severity == "warning":
                self.validation_label.setStyleSheet("color: #f7630c;")
                self.input_widget.setStyleSheet(
                    base_style + warning_border_style)

        self.validationChanged.emit(result.is_valid)

    def get_value(self) -> str:
        """Get the current field value"""
        if isinstance(self.input_widget, QLineEdit):
            return self.input_widget.text()
        elif isinstance(self.input_widget, QTextEdit):
            return self.input_widget.toPlainText()
        elif isinstance(self.input_widget, QComboBox):
            return self.input_widget.currentText()
        elif isinstance(self.input_widget, QSpinBox):
            return str(self.input_widget.value())
        elif isinstance(self.input_widget, QDateEdit):
            return self.input_widget.date().toString(Qt.DateFormat.ISODate)
        return ""

    def set_value(self, value: str):
        """Set the field value"""
        if isinstance(self.input_widget, QLineEdit):
            self.input_widget.setText(value)
        elif isinstance(self.input_widget, QTextEdit):
            self.input_widget.setPlainText(value)
        elif isinstance(self.input_widget, QComboBox):
            self.input_widget.setCurrentText(value)
        elif isinstance(self.input_widget, QSpinBox):
            try:
                self.input_widget.setValue(int(value))
            except ValueError:
                # Or some default / error handling
                self.input_widget.setValue(0)
        elif isinstance(self.input_widget, QDateEdit):
            date_obj = QDate.fromString(value, Qt.DateFormat.ISODate)
            if date_obj.isValid():
                self.input_widget.setDate(date_obj)

    def setup_style(self):
        """Setup field styling"""
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme"""
        theme = theme_manager

        # Style the input widget
        # Check if input_widget has been initialized
        if hasattr(self, 'input_widget') and self.input_widget is not None:
            self.input_widget.setStyleSheet(f"""
                QLineEdit, QTextEdit, QSpinBox, QDateEdit, QComboBox {{
                    background-color: {theme.get_color('surface').name()};
                    border: 2px solid {theme.get_color('border').name()};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 14px;
                    color: {theme.get_color('text_primary').name()};
                    min-height: 20px;
                }}
                QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDateEdit:focus, QComboBox:focus {{
                    border-color: {theme.get_color('primary').name()};
                    outline: none;
                }}
                QLineEdit:hover, QTextEdit:hover, QSpinBox:hover, QDateEdit:hover, QComboBox:hover {{
                    border-color: {theme.get_color('primary').lighter(130).name()};
                }}
            """)
        if hasattr(self, 'label') and self.label is not None:
            self.label.setStyleSheet(
                f"color: {theme.get_color('text_secondary').name()};")


class FluentForm(QScrollArea):
    """Advanced form container with validation and submission handling"""

    # Signals
    formValidated = Signal(bool)  # Emitted when form validation state changes
    # Emitted when form is submitted with field values
    formSubmitted = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None, title: str = ""):
        super().__init__(parent)

        self.title = title
        self.fields: Dict[str, FluentFormField] = {}
        self.field_groups: Dict[str, List[str]] = {}

        self.setup_ui()
        self.setup_style()
        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup the form UI"""
        # Create scrollable content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(16)

        # Form title
        if self.title:
            title_label = QLabel(self.title)
            title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            self.content_layout.addWidget(title_label)

        # Fields will be added dynamically

        # Submit button area
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_form)
        self.submit_button.setEnabled(False)  # Disabled until form is valid

        self.cancel_button = QPushButton("Cancel")

        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.submit_button)

        self.content_layout.addStretch()
        self.content_layout.addLayout(self.button_layout)

        # Setup scroll area
        self.setWidget(self.content_widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def add_field(self, field_name: str, label: str, field_type: str = "text",
                  required: bool = False, group: Optional[str] = None) -> FluentFormField:
        """Add a field to the form"""
        field = FluentFormField(
            label=label, required=required, field_type=field_type)
        field.validationChanged.connect(self.validate_form)

        self.fields[field_name] = field

        # Add to group if specified
        if group:
            if group not in self.field_groups:
                self.field_groups[group] = []
            self.field_groups[group].append(field_name)

        # Insert before button layout
        insert_index = self.content_layout.count() - 2  # Before stretch and buttons
        self.content_layout.insertWidget(insert_index, field)

        return field

    def add_field_group(self, group_name: str, title: Optional[str] = None):
        """Add a group container for organizing fields"""
        group_box = QGroupBox(title or group_name)
        group_layout = QVBoxLayout(group_box)

        insert_index = self.content_layout.count() - 2
        self.content_layout.insertWidget(insert_index, group_box)

        # Store reference for adding fields to this group
        setattr(self, f"_group_{group_name}", group_box)
        setattr(self, f"_group_layout_{group_name}", group_layout)

    def add_field_to_group(self, group_name: str, field_name: str, label: str,
                           field_type: str = "text", required: bool = False) -> FluentFormField:
        """Add a field to a specific group"""
        field = FluentFormField(
            label=label, required=required, field_type=field_type)
        field.validationChanged.connect(self.validate_form)

        self.fields[field_name] = field

        # Add to group layout
        group_layout = getattr(self, f"_group_layout_{group_name}", None)
        if group_layout:
            group_layout.addWidget(field)

        if group_name not in self.field_groups:
            self.field_groups[group_name] = []
        self.field_groups[group_name].append(field_name)

        return field

    def validate_form(self):
        """Validate all form fields"""
        all_valid = True

        for field in self.fields.values():
            if not field.validate_field():
                all_valid = False

        self.submit_button.setEnabled(all_valid)
        self.formValidated.emit(all_valid)
        return all_valid

    def submit_form(self):
        """Submit the form if valid"""
        if self.validate_form():
            form_data = {}
            for field_name, field in self.fields.items():
                form_data[field_name] = field.get_value()

            self.formSubmitted.emit(form_data)

    def get_form_data(self) -> Dict[str, str]:
        """Get all form field values"""
        return {field_name: field.get_value() for field_name, field in self.fields.items()}

    def set_form_data(self, data: Dict[str, str]):
        """Set form field values from data dictionary"""
        for field_name, value in data.items():
            if field_name in self.fields:
                self.fields[field_name].set_value(value)

    def clear_form(self):
        """Clear all form fields"""
        for field in self.fields.values():
            field.set_value("")

    def setup_style(self):
        """Setup form styling"""
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme"""
        theme = theme_manager

        self.setStyleSheet(f"""
            FluentForm {{
                background-color: {theme.get_color('background').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
            QPushButton {{
                background-color: {theme.get_color('primary').name()};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('primary').darker(110).name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('primary').darker(120).name()};
            }}
            QPushButton:disabled {{
                background-color: {theme.get_color('surface_variant').name()};
                color: {theme.get_color('text_disabled').name()};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {theme.get_color('border').name()};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_primary').name()};
            }}
        """)
        if self.title:
            title_label = self.content_widget.findChild(
                QLabel, self.title)  # Find by object name if set, or by text
            if not title_label:  # Fallback: assume first QLabel if not specifically named
                labels = self.content_widget.findChildren(QLabel)
                if labels and labels[0].text() == self.title:
                    title_label = labels[0]
            if title_label:
                title_label.setStyleSheet(
                    f"color: {theme.get_color('text_primary').name()};")


class FluentMultiStepForm(QWidget):
    """Multi-step form wizard with navigation and progress tracking"""

    # Signals
    stepChanged = Signal(int)  # Current step index
    formCompleted = Signal(dict)  # Final form data when all steps completed

    def __init__(self, parent: Optional[QWidget] = None, title: str = "Setup Wizard"):
        super().__init__(parent)

        self.title = title
        self.steps: List[Dict] = []
        self.current_step = 0
        self.step_data: Dict = {}

        self.setup_ui()
        self.setup_style()
        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup the multi-step form UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with progress
        self.header = QFrame()
        self.header.setFixedHeight(80)
        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(20, 10, 20, 10)

        # Title
        self.title_label = QLabel(self.title)  # Store as attribute for theming
        self.title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        header_layout.addWidget(self.progress_bar)

        layout.addWidget(self.header)

        # Step content area
        self.step_stack = QStackedWidget()
        layout.addWidget(self.step_stack)

        # Navigation buttons
        self.nav_frame = QFrame()
        self.nav_frame.setFixedHeight(60)
        nav_layout = QHBoxLayout(self.nav_frame)
        nav_layout.setContentsMargins(20, 10, 20, 10)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setEnabled(False)

        nav_layout.addWidget(self.back_button)
        nav_layout.addStretch()

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.go_next)

        self.finish_button = QPushButton("Finish")
        self.finish_button.clicked.connect(self.finish_wizard)
        self.finish_button.setVisible(False)

        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.finish_button)

        layout.addWidget(self.nav_frame)

    def add_step(self, title: str, description: str = "", form_widget: Optional[QWidget] = None) -> int:
        """Add a step to the wizard"""
        if form_widget is None:
            form_widget = FluentForm()  # Default to FluentForm if none provided

        step_info = {
            'title': title,
            'description': description,
            'widget': form_widget,
            'data': {}
        }

        self.steps.append(step_info)
        self.step_stack.addWidget(form_widget)

        # Update progress bar
        self.progress_bar.setMaximum(len(self.steps))
        if len(self.steps) == 1:  # First step
            self.progress_bar.setValue(1)
            self.update_step_display()  # Ensure initial display is correct

        return len(self.steps) - 1

    def go_next(self):
        """Go to next step"""
        if self.current_step < len(self.steps) - 1:
            # Validate current step if it's a form
            current_widget = self.steps[self.current_step]['widget']
            if isinstance(current_widget, FluentForm):  # Check if it's a FluentForm
                if not current_widget.validate_form():
                    return  # Don't proceed if validation fails

                # Store step data
                self.step_data.update(current_widget.get_form_data())

            self.current_step += 1
            self.update_step_display()

    def go_back(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step_display()

    def finish_wizard(self):
        """Complete the wizard"""
        # Validate final step
        current_widget = self.steps[self.current_step]['widget']
        if isinstance(current_widget, FluentForm):  # Check if it's a FluentForm
            if not current_widget.validate_form():
                return

            self.step_data.update(current_widget.get_form_data())

        self.formCompleted.emit(self.step_data)

    def update_step_display(self):
        """Update the display for current step"""
        if not self.steps:  # No steps added yet
            return

        self.step_stack.setCurrentIndex(self.current_step)
        self.progress_bar.setValue(self.current_step + 1)

        # Update button states
        self.back_button.setEnabled(self.current_step > 0)

        is_last_step = self.current_step == len(self.steps) - 1
        self.next_button.setVisible(not is_last_step)
        self.finish_button.setVisible(is_last_step)

        self.stepChanged.emit(self.current_step)

    def setup_style(self):
        """Setup styling"""
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme"""
        theme = theme_manager

        self.setStyleSheet(f"""
            FluentMultiStepForm {{
                background-color: {theme.get_color('background').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
            QFrame#header, QFrame#nav_frame {{ /* Use object names for specificity if set */
                background-color: {theme.get_color('surface').name()};
                border: none;
            }}
            QProgressBar {{
                border: none;
                background-color: {theme.get_color('surface_variant').name()};
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {theme.get_color('primary').name()};
                border-radius: 3px;
            }}
            QPushButton {{
                background-color: {theme.get_color('primary').name()};
                color: white; /* Assuming on_primary is white or light */
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('primary').darker(110).name()};
            }}
            QPushButton:disabled {{
                background-color: {theme.get_color('surface_variant').name()};
                color: {theme.get_color('text_disabled').name()};
            }}
        """)
        # Theme the title label
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(
                f"color: {theme.get_color('text_primary').name()};")


# Export all form components
__all__ = [
    'ValidationRule',
    'ValidationResult',
    'FluentFormField',
    'FluentForm',
    'FluentMultiStepForm'
]
