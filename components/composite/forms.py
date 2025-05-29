"""
Composite Form Components

This module provides higher-level form components that combine multiple
basic widgets into common form patterns with built-in validation and
dynamic user feedback.
"""

from typing import Optional, Dict, Any, List, Callable, Union

from PySide6.QtWidgets import (QWidget, QLabel, QLineEdit, QTextEdit,
                               QComboBox, QCheckBox, QRadioButton, QButtonGroup,
                               QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit,
                               QFrame, QScrollArea, QVBoxLayout, QGraphicsOpacityEffect)
from PySide6.QtCore import (Signal, QDate, QTime, QObject, QPropertyAnimation,
                            QByteArray)
from PySide6.QtGui import QFont

from ...core.enhanced_base import (FluentStandardButton,
                                   FluentLayoutBuilder, FluentCompositeWidget,
                                   FluentFormGroup)
from ...core.animation import FluentAnimation

from ..basic.textbox import FluentLineEdit, FluentTextEdit
from ..basic.checkbox import FluentCheckBox


class FluentFieldGroup(FluentFormGroup):
    """
    Enhanced form group that provides structured field organization
    with automatic validation and error display. Includes animated error feedback.
    """

    field_changed = Signal(str, object)  # field_name, value
    validation_changed = Signal(bool)  # is_valid

    def __init__(self, title: str = "",
                 required_fields: Optional[List[str]] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(title, parent=parent)

        # Fix: Do not override _fields type, just use as inherited (Dict[str, QWidget])
        # If you must store QButtonGroup, use a separate dict or cast as needed.
        # self._fields: Dict[str, Union[QWidget, QButtonGroup]] = {}  # <-- removed

        self._validators: Dict[str, List[Callable]] = {}
        self._required_fields = required_fields or []
        self._validation_errors: Dict[str, str] = {}

        # Error display label and animation
        self._setup_error_display()

    def _setup_error_display(self):
        """Setup error message display with animation."""
        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            QLabel {
                color: red;
                font-size: 12px;
                margin-top: 4px;
            }
        """)
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        self.addWidget(self.error_label)

        # Set up opacity effect and animation
        self.error_opacity_effect = QGraphicsOpacityEffect(self.error_label)
        self.error_label.setGraphicsEffect(self.error_opacity_effect)
        self.error_label_transition = QPropertyAnimation(
            self.error_opacity_effect, QByteArray(b"opacity"))
        self.error_label_transition.setDuration(200)

    def add_text_field(self, field_name: str, label: str,
                       placeholder: str = "", required: bool = False,
                       validator: Optional[Callable] = None) -> FluentLineEdit:
        """Add a text input field."""
        field_edit = FluentLineEdit()
        field_edit.setPlaceholderText(placeholder)
        field_edit.textChanged.connect(
            lambda text: self._on_field_changed(field_name, text))

        self._add_field_to_layout(field_name, label, field_edit, required)

        if validator:
            self._validators[field_name] = [validator]

        if required and field_name not in self._required_fields:
            self._required_fields.append(field_name)

        return field_edit

    def add_multiline_field(self, field_name: str, label: str,
                            placeholder: str = "", required: bool = False,
                            max_height: int = 100,
                            validator: Optional[Callable] = None) -> FluentTextEdit:
        """Add a multiline text area field."""
        field_edit = FluentTextEdit()
        field_edit.setPlaceholderText(placeholder)
        field_edit.setMaximumHeight(max_height)
        field_edit.textChanged.connect(
            lambda: self._on_field_changed(field_name, field_edit.toPlainText()))

        self._add_field_to_layout(field_name, label, field_edit, required)

        if validator:
            self._validators[field_name] = [validator]

        if required and field_name not in self._required_fields:
            self._required_fields.append(field_name)

        return field_edit

    def add_choice_field(self, field_name: str, label: str,
                         choices: List[str], default_index: int = -1,
                         required: bool = False) -> QComboBox:
        """Add a dropdown choice field."""
        combo = QComboBox()
        combo.addItems(choices)
        if default_index >= 0 and default_index < len(choices):
            combo.setCurrentIndex(default_index)

        combo.currentTextChanged.connect(
            lambda text: self._on_field_changed(field_name, text))

        self._add_field_to_layout(field_name, label, combo, required)

        if required and field_name not in self._required_fields:
            self._required_fields.append(field_name)

        return combo

    def add_number_field(self, field_name: str, label: str,
                         min_value: int = 0, max_value: int = 100,
                         default_value: int = 0, required: bool = False,
                         validator: Optional[Callable] = None) -> QSpinBox:
        """Add a number input field."""
        spinbox = QSpinBox()
        spinbox.setRange(min_value, max_value)
        spinbox.setValue(default_value)
        spinbox.valueChanged.connect(
            lambda value: self._on_field_changed(field_name, value))

        self._add_field_to_layout(field_name, label, spinbox, required)

        if validator:
            self._validators[field_name] = [validator]

        if required and field_name not in self._required_fields:
            self._required_fields.append(field_name)

        return spinbox

    def add_decimal_field(self, field_name: str, label: str,
                          min_value: float = 0.0, max_value: float = 100.0,
                          decimals: int = 2, default_value: float = 0.0,
                          required: bool = False,
                          validator: Optional[Callable] = None) -> QDoubleSpinBox:
        """Add a decimal number input field."""
        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_value, max_value)
        spinbox.setDecimals(decimals)
        spinbox.setValue(default_value)
        spinbox.valueChanged.connect(
            lambda value: self._on_field_changed(field_name, value))

        self._add_field_to_layout(field_name, label, spinbox, required)

        if validator:
            self._validators[field_name] = [validator]

        if required and field_name not in self._required_fields:
            self._required_fields.append(field_name)

        return spinbox

    def add_boolean_field(self, field_name: str, label: str,
                          default_value: bool = False) -> FluentCheckBox:
        """Add a boolean checkbox field."""
        checkbox = FluentCheckBox(label)
        checkbox.setChecked(default_value)
        checkbox.toggled.connect(
            lambda checked: self._on_field_changed(field_name, checked))

        self.addWidget(checkbox)
        self._fields[field_name] = checkbox

        return checkbox

    def add_radio_group(self, field_name: str, label: str,
                        options: List[str], default_index: int = 0) -> QButtonGroup:
        """Add a radio button group field."""
        group_frame = QFrame()
        group_layout = FluentLayoutBuilder.create_vertical_layout(spacing=4)
        group_frame.setLayout(group_layout)

        group_label_text = label + ":"
        group_qlabel = QLabel(group_label_text)
        group_qlabel.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        group_layout.addWidget(group_qlabel)

        button_group = QButtonGroup()

        for i, option_text in enumerate(options):
            radio = QRadioButton(option_text)
            if i == default_index:
                radio.setChecked(True)

            group_layout.addWidget(radio)
            button_group.addButton(radio, i)

        button_group.idClicked.connect(
            lambda btn_id: self._on_field_changed(field_name, options[btn_id]))

        self.addWidget(group_frame)
        # Fix: Store button_group in a separate dict if needed, or cast as needed
        # Store the frame, not the group
        self._fields[field_name] = group_frame

        # Store the button group in a separate attribute if you need to access it later
        if not hasattr(self, '_button_groups'):
            self._button_groups = {}
        self._button_groups[field_name] = button_group

        return button_group

    def add_date_field(self, field_name: str, label: str,
                       default_date: Optional[QDate] = None,
                       required: bool = False) -> QDateEdit:
        """Add a date picker field."""
        date_edit = QDateEdit()
        if default_date:
            date_edit.setDate(default_date)
        else:
            date_edit.setDate(QDate.currentDate())

        date_edit.setCalendarPopup(True)
        date_edit.dateChanged.connect(
            lambda date_val: self._on_field_changed(field_name, date_val))

        self._add_field_to_layout(field_name, label, date_edit, required)

        if required and field_name not in self._required_fields:
            self._required_fields.append(field_name)

        return date_edit

    def _add_field_to_layout(self, field_name: str, label: str,
                             widget: QWidget, required: bool = False):
        """Helper to add a field with its label to the group's layout."""
        field_frame = QFrame()
        field_layout = FluentLayoutBuilder.create_vertical_layout(spacing=2)
        field_frame.setLayout(field_layout)

        label_text = label + ("*" if required else "") + ":"
        field_label = QLabel(label_text)
        field_label.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))

        if required:
            field_label.setStyleSheet("color: #D13438;")

        field_layout.addWidget(field_label)
        field_layout.addWidget(widget)

        self.addWidget(field_frame)
        self._fields[field_name] = widget

    def _on_field_changed(self, field_name: str, value: Any):
        """Handle field value change and trigger validation."""
        if field_name in self._validation_errors:
            del self._validation_errors[field_name]

        if field_name in self._validators and self._validators[field_name]:
            validator_func = self._validators[field_name][0]
            try:
                validation_result = validator_func(value)
                is_valid = False
                custom_message = None

                if isinstance(validation_result, tuple) and len(validation_result) == 2 and isinstance(validation_result[0], bool):
                    is_valid = validation_result[0]
                    if isinstance(validation_result[1], str):
                        custom_message = validation_result[1]
                elif isinstance(validation_result, bool):
                    is_valid = validation_result

                if not is_valid:
                    if custom_message:
                        self._validation_errors[field_name] = custom_message
                    else:
                        label_text = self._get_field_label_text(
                            field_name) or field_name
                        self._validation_errors[field_name] = f"Invalid value for {label_text}"
            except Exception as e:
                self._validation_errors[field_name] = str(e)

        self._update_error_display()
        self.field_changed.emit(field_name, value)
        self.validation_changed.emit(self.is_valid())

    def _get_field_label_text(self, field_name: str) -> Optional[str]:
        """Attempt to get the label text for a field for more descriptive errors."""
        return field_name

    def _update_error_display(self):
        """Update error message display with animation."""
        if self._validation_errors:
            error_text = "\n".join(self._validation_errors.values())
            self.error_label.setText(error_text)
            if not self.error_label.isVisible():
                self.error_label.setVisible(True)
                fade_in = FluentAnimation.fade_in(self.error_label)
                fade_in.start()
        else:
            if self.error_label.isVisible():
                fade_out = FluentAnimation.fade_out(self.error_label)
                fade_out.finished.connect(
                    lambda: self.error_label.setVisible(False))
                fade_out.start()
                self.error_label_transition.finished.connect(
                    lambda: self.error_label.setVisible(
                        False) if not self._validation_errors else None
                )
                self.error_label_transition.start()

    def validate(self) -> bool:
        """Validate all fields in the group."""
        self._validation_errors.clear()

        for field_name in self._required_fields:
            if field_name not in self._fields:
                continue
            value = self._get_field_value(field_name)
            if self._is_empty_value(value):
                label = self._get_field_label_text(field_name) or field_name
                self._validation_errors[field_name] = f"{label} is required."

        for field_name, validator_list in self._validators.items():
            if field_name not in self._fields:
                continue
            if field_name in self._validation_errors:
                continue

            if validator_list:
                validator_func = validator_list[0]
                value = self._get_field_value(field_name)
                try:
                    validation_result = validator_func(value)
                    is_valid = False
                    custom_message = None

                    if isinstance(validation_result, tuple) and len(validation_result) == 2 and isinstance(validation_result[0], bool):
                        is_valid = validation_result[0]
                        if isinstance(validation_result[1], str):
                            custom_message = validation_result[1]
                    elif isinstance(validation_result, bool):
                        is_valid = validation_result

                    if not is_valid:
                        label_text = self._get_field_label_text(
                            field_name) or field_name
                        if custom_message:
                            self._validation_errors[field_name] = custom_message
                        else:
                            self._validation_errors[field_name] = f"Invalid value for {label_text}."
                except Exception as e:
                    self._validation_errors[field_name] = str(e)

        self._update_error_display()
        is_group_valid = len(self._validation_errors) == 0
        self.validation_changed.emit(is_group_valid)
        return is_group_valid

    def is_valid(self) -> bool:
        """Check if all fields are currently considered valid based on last validation."""
        return len(self._validation_errors) == 0

    def get_field_value(self, field_name: str) -> Any:
        """Get current value of a specific field."""
        return self._get_field_value(field_name)

    def _get_field_value(self, field_name: str) -> Any:
        """Internal method to get field value based on widget type."""
        if field_name not in self._fields:
            return None

        widget_or_group = self._fields[field_name]

        if isinstance(widget_or_group, (FluentLineEdit, QLineEdit)):
            return widget_or_group.text()
        elif isinstance(widget_or_group, (FluentTextEdit, QTextEdit)):
            return widget_or_group.toPlainText()
        elif isinstance(widget_or_group, QComboBox):
            return widget_or_group.currentText()
        elif isinstance(widget_or_group, (QSpinBox, QDoubleSpinBox)):
            return widget_or_group.value()
        elif isinstance(widget_or_group, (FluentCheckBox, QCheckBox)):
            return widget_or_group.isChecked()
        elif hasattr(self, '_button_groups') and field_name in self._button_groups:
            checked_button = self._button_groups[field_name].checkedButton()
            return checked_button.text() if checked_button else None
        elif isinstance(widget_or_group, QDateEdit):
            return widget_or_group.date()
        elif isinstance(widget_or_group, QTimeEdit):
            return widget_or_group.time()

        return None

    def _is_empty_value(self, value: Any) -> bool:
        """Check if a value is considered empty (None, empty string/list/dict)."""
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip()
        if isinstance(value, (list, dict, set)):
            return len(value) == 0
        if isinstance(value, QDate) and value.isNull():
            return True
        return False

    def set_field_value(self, field_name: str, value: Any):
        """Set the value of a specific field."""
        if field_name not in self._fields:
            return

        widget_or_group = self._fields[field_name]

        if isinstance(widget_or_group, (FluentLineEdit, QLineEdit)):
            widget_or_group.setText(str(value))
        elif isinstance(widget_or_group, (FluentTextEdit, QTextEdit)):
            widget_or_group.setPlainText(str(value))
        elif isinstance(widget_or_group, QComboBox):
            index = widget_or_group.findText(str(value))
            if index >= 0:
                widget_or_group.setCurrentIndex(index)
        elif isinstance(widget_or_group, QSpinBox):
            widget_or_group.setValue(int(value))
        elif isinstance(widget_or_group, QDoubleSpinBox):
            widget_or_group.setValue(float(value))
        elif isinstance(widget_or_group, (FluentCheckBox, QCheckBox)):
            widget_or_group.setChecked(bool(value))
        elif isinstance(widget_or_group, QDateEdit):
            if isinstance(value, QDate):
                widget_or_group.setDate(value)
            elif isinstance(value, str):
                widget_or_group.setDate(QDate.fromString(value, "yyyy-MM-dd"))
        elif isinstance(widget_or_group, QTimeEdit):
            if isinstance(value, QTime):
                widget_or_group.setTime(value)
        elif hasattr(self, '_button_groups') and field_name in self._button_groups:
            for button in self._button_groups[field_name].buttons():
                if button.text() == str(value):
                    button.setChecked(True)
                    break

    def get_all_values(self) -> Dict[str, Any]:
        """Get all field values as a dictionary."""
        values = {}
        for field_name in self._fields.keys():
            values[field_name] = self._get_field_value(field_name)
        return values

    def clear_all_fields(self):
        """Clear all field values to their defaults or empty state."""
        for field_name in self._fields:
            widget_or_group = self._fields[field_name]

            if isinstance(widget_or_group, (FluentLineEdit, QLineEdit, FluentTextEdit, QTextEdit)):
                widget_or_group.clear()
            elif isinstance(widget_or_group, QComboBox):
                widget_or_group.setCurrentIndex(-1)
            elif isinstance(widget_or_group, QSpinBox):
                widget_or_group.setValue(widget_or_group.minimum())
            elif isinstance(widget_or_group, QDoubleSpinBox):
                widget_or_group.setValue(widget_or_group.minimum())
            elif isinstance(widget_or_group, (FluentCheckBox, QCheckBox)):
                widget_or_group.setChecked(False)
            elif hasattr(self, '_button_groups') and field_name in self._button_groups:
                # Uncheck all radio buttons
                for button in self._button_groups[field_name].buttons():
                    button.setChecked(False)
            elif isinstance(widget_or_group, QDateEdit):
                widget_or_group.setDate(QDate.currentDate())
        self._validation_errors.clear()
        self._update_error_display()
        self.validation_changed.emit(True)


class FluentValidationForm(FluentCompositeWidget):
    """
    A complete form widget that can host multiple FluentFieldGroup instances,
    manages overall validation, and provides standard form actions (Submit, Cancel, Clear).
    """

    submitted = Signal(dict)
    cancelled = Signal()
    validation_changed = Signal(bool)

    def __init__(self, title: str = "Form",
                 show_actions: bool = True,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._field_groups: Dict[str, FluentFieldGroup] = {}
        self._show_actions = show_actions

        # Changed: Store the main layout explicitly to avoid issues with self.layout()
        # QVBoxLayout or more general QLayout
        self._main_layout: Optional[QVBoxLayout] = None

        self._setup_form_ui(title)
        if self._show_actions and hasattr(self, 'submit_button'):
            self._on_group_validation_changed(self.is_valid())

    def _setup_form_ui(self, title: str):
        """Initialize the main UI structure of the form."""
        # Changed: Use self._main_layout
        self._main_layout = FluentLayoutBuilder.create_vertical_layout()
        self.setLayout(self._main_layout)

        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            self._main_layout.addWidget(title_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.form_widget = QWidget()
        self.form_layout = FluentLayoutBuilder.create_vertical_layout(
            spacing=10)
        self.form_widget.setLayout(self.form_layout)

        self.scroll_area.setWidget(self.form_widget)
        self._main_layout.addWidget(self.scroll_area, 1)

        self.form_layout.addStretch()

        if self._show_actions:
            self._setup_action_buttons()

    def _setup_action_buttons(self):
        """Create and arrange form action buttons (Clear, Cancel, Submit)."""
        button_frame = QFrame()
        button_layout = FluentLayoutBuilder.create_horizontal_layout(spacing=8)
        button_frame.setLayout(button_layout)

        button_layout.addStretch()

        self.clear_button = FluentStandardButton("Clear All", size=(100, 32))
        self.clear_button.clicked.connect(self._on_clear)
        button_layout.addWidget(self.clear_button)

        self.cancel_button = FluentStandardButton("Cancel", size=(100, 32))
        self.cancel_button.clicked.connect(self.cancelled.emit)
        button_layout.addWidget(self.cancel_button)

        self.submit_button = FluentStandardButton("Submit", size=(100, 32))
        self.submit_button.clicked.connect(self._on_submit)
        button_layout.addWidget(self.submit_button)

        # Changed: Add to self._main_layout directly
        if self._main_layout:
            self._main_layout.addWidget(button_frame)

    def add_field_group(self, group_id: str, title: Optional[str] = None,
                        required_fields: Optional[List[str]] = None) -> FluentFieldGroup:
        """Add a new field group to the form."""
        actual_title = title if title is not None else group_id.replace(
            "_", " ").title()

        group = FluentFieldGroup(
            actual_title, required_fields, parent=self.form_widget)
        # Changed: Parameter renamed to _ in lambda
        group.validation_changed.connect(
            lambda valid_status: self._on_group_validation_changed(valid_status))

        self._field_groups[group_id] = group

        layout_item_count = self.form_layout.count()
        insert_index = max(0, layout_item_count - 1)
        self.form_layout.insertWidget(insert_index, group)

        return group

    # Changed: Parameter renamed to _ to indicate it's unused
    def _on_group_validation_changed(self, _: bool):
        """Handle validation status change from any field group."""
        overall_form_valid = self.is_valid()
        self.validation_changed.emit(overall_form_valid)

        if hasattr(self, 'submit_button') and self._show_actions:
            self.submit_button.setEnabled(overall_form_valid)

    def _on_submit(self):
        """Handle form submission: validate and emit data if valid."""
        if not self.validate():
            return

        form_data = {}
        for group_id, group_instance in self._field_groups.items():
            group_data = group_instance.get_all_values()
            form_data[group_id] = group_data

        self.submitted.emit(form_data)

    def _on_clear(self):
        """Clear all fields in all groups of the form."""
        for group in self._field_groups.values():
            group.clear_all_fields()
        self._on_group_validation_changed(True)

    def validate(self) -> bool:
        """Validate the entire form by validating each field group."""
        all_groups_valid = True
        for group_id in self._field_groups:
            group = self._field_groups[group_id]
            if not group.validate():
                all_groups_valid = False

        if hasattr(self, 'submit_button') and self._show_actions:
            self.submit_button.setEnabled(all_groups_valid)
        self.validation_changed.emit(all_groups_valid)
        return all_groups_valid

    def is_valid(self) -> bool:
        """Check if the entire form is currently valid based on its groups' states."""
        if not self._field_groups:  # No groups, considered valid
            return True
        return all(group.is_valid() for group in self._field_groups.values())

    def get_form_data(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve all data from the form, structured by group ID."""
        form_data = {}
        for group_id, group_instance in self._field_groups.items():
            form_data[group_id] = group_instance.get_all_values()
        return form_data


class FluentQuickForm(FluentCompositeWidget):
    """
    A simplified form builder for creating basic forms quickly using a fluent interface.
    Does not include complex validation or grouping like FluentValidationForm.
    """

    submitted = Signal(dict)  # Emits form_data as Dict[field_name, value]

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._fields: Dict[str, QWidget] = {}
        # For consistency if self.layout() is an issue
        self._main_layout: Optional[QVBoxLayout] = None
        self._setup_quick_form_ui(title)

    def _setup_quick_form_ui(self, title: str):
        """Set up the basic UI for the quick form."""
        self._main_layout = FluentLayoutBuilder.create_vertical_layout()
        self.setLayout(self._main_layout)

        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            self._main_layout.addWidget(title_label)

        self.fields_widget = QWidget()
        self.fields_layout = FluentLayoutBuilder.create_vertical_layout(
            spacing=8)
        self.fields_widget.setLayout(self.fields_layout)
        self._main_layout.addWidget(self.fields_widget)

        self._main_layout.addStretch(1)

        self.submit_button = FluentStandardButton("Submit", size=(100, 32))
        self.submit_button.clicked.connect(self._on_submit)
        self._main_layout.addWidget(self.submit_button)

    def text(self, field_name: str, label: str, placeholder: str = "") -> 'FluentQuickForm':
        """Add a text input field using a fluent interface."""
        field_edit = FluentLineEdit()
        field_edit.setPlaceholderText(placeholder)
        self._add_labeled_field(field_name, label, field_edit)
        return self

    def choice(self, field_name: str, label: str, options: List[str], default_index: int = -1) -> 'FluentQuickForm':
        """Add a dropdown choice field using a fluent interface."""
        combo = QComboBox()
        combo.addItems(options)
        if default_index >= 0 and default_index < len(options):
            combo.setCurrentIndex(default_index)
        self._add_labeled_field(field_name, label, combo)
        return self

    def checkbox(self, field_name: str, label: str, checked: bool = False) -> 'FluentQuickForm':
        """Add a checkbox field using a fluent interface."""
        checkbox = FluentCheckBox(label)
        checkbox.setChecked(checked)
        self.fields_layout.addWidget(checkbox)
        self._fields[field_name] = checkbox
        return self

    def _add_labeled_field(self, field_name: str, label_text: str, widget: QWidget):
        """Helper to add a field with an accompanying label to the fields_layout."""
        field_label = QLabel(label_text + ":")
        field_label.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))

        self.fields_layout.addWidget(field_label)
        self.fields_layout.addWidget(widget)
        self._fields[field_name] = widget

    def _on_submit(self):
        """Handle form submission: collect data and emit the 'submitted' signal."""
        data = {}
        for field_name, widget_instance in self._fields.items():
            if isinstance(widget_instance, (FluentLineEdit, QLineEdit)):
                data[field_name] = widget_instance.text()
            elif isinstance(widget_instance, QComboBox):
                data[field_name] = widget_instance.currentText()
            elif isinstance(widget_instance, (FluentCheckBox, QCheckBox)):
                data[field_name] = widget_instance.isChecked()

        self.submitted.emit(data)

    def get_values(self) -> Dict[str, Any]:
        """Retrieve all current values from the quick form."""
        data = {}
        for field_name, widget_instance in self._fields.items():
            if isinstance(widget_instance, (FluentLineEdit, QLineEdit)):
                data[field_name] = widget_instance.text()
            elif isinstance(widget_instance, QComboBox):
                data[field_name] = widget_instance.currentText()
            elif isinstance(widget_instance, (FluentCheckBox, QCheckBox)):
                data[field_name] = widget_instance.isChecked()
        return data

    def clear(self):
        """Clear all fields in the quick form."""
        for widget_instance in self._fields.values():
            if isinstance(widget_instance, (FluentLineEdit, QLineEdit)):
                widget_instance.clear()
            elif isinstance(widget_instance, QComboBox):
                widget_instance.setCurrentIndex(-1)
            elif isinstance(widget_instance, (FluentCheckBox, QCheckBox)):
                widget_instance.setChecked(False)
