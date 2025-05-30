"""
Composite Panel Components

This module provides higher-level panel components that combine multiple basic
widgets into common patterns like settings panels, property editors, and dialogs.
"""

from typing import Optional, Dict, Any, List, Callable
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QLineEdit, QComboBox, QSpinBox,
                               QScrollArea, QFrame)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

from core.enhanced_base import (FluentPanel, FluentStandardButton,
                                FluentLayoutBuilder, FluentCompositeWidget,
                                FluentFormGroup)
from core.enhanced_animations import FluentTransition
from ..basic.textbox import FluentLineEdit
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

    def add_settings_group(self, group_name: str, title: Optional[str] = None) -> FluentFormGroup:
        """Add a new settings group"""
        if title is None:
            title = group_name

        group = FluentFormGroup(title)
        self._settings_groups[group_name] = group

        # Insert before action buttons
        layout = self.content_layout
        if layout:  # Ensure content_layout is not None
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
            lambda text, key=setting_key: self._on_setting_changed(key, text))

        # Use addField from FluentFormGroup
        group.addField(setting_key, field_edit, label_text=label)
        self._current_values[setting_key] = default_value

        return field_edit

    def add_choice_setting(self, group_name: str, setting_key: str,
                           label: str, choices: List[str],
                           default_index: int = 0) -> QComboBox:
        """Add a choice dropdown setting"""
        group = self._get_or_create_group(group_name)

        combo = QComboBox()
        combo.addItems(choices)
        if choices:  # Ensure choices is not empty before setting index
            combo.setCurrentIndex(default_index if 0 <=
                                  default_index < len(choices) else 0)

        combo.currentTextChanged.connect(
            lambda text, key=setting_key: self._on_setting_changed(key, text))

        # Use addField from FluentFormGroup
        group.addField(setting_key, combo, label_text=label)
        self._current_values[setting_key] = choices[default_index] if choices and 0 <= default_index < len(
            choices) else ""

        return combo

    def add_boolean_setting(self, group_name: str, setting_key: str,
                            label: str, default_value: bool = False) -> FluentCheckBox:
        """Add a boolean checkbox setting"""
        group = self._get_or_create_group(group_name)

        checkbox = FluentCheckBox(label)  # Pass label to checkbox constructor
        checkbox.setChecked(default_value)

        checkbox.toggled.connect(
            lambda checked, key=setting_key: self._on_setting_changed(key, checked))

        # Checkbox itself has the label
        group.addField(setting_key, checkbox, label_text="")
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
            lambda value, key=setting_key: self._on_setting_changed(key, value))

        # Use addField from FluentFormGroup
        group.addField(setting_key, spinbox, label_text=label)
        self._current_values[setting_key] = default_value

        return spinbox

    def _get_or_create_group(self, group_name: str) -> FluentFormGroup:
        """Get existing group or create new one"""
        if group_name not in self._settings_groups:
            # Pass title as well
            return self.add_settings_group(group_name, group_name)
        return self._settings_groups[group_name]

    def _on_setting_changed(self, setting_key: str, value: Any):
        """Handle setting value change"""
        self._current_values[setting_key] = value
        self.setting_changed.emit(setting_key, value)

    def _apply_settings(self):
        """Apply current settings"""
        all_valid = True
        for group_name, group in self._settings_groups.items():
            if hasattr(group, 'validateAll') and not group.validateAll():
                all_valid = False
                # Optionally, log which group failed validation
                # print(f"Validation failed for group: {group_name}")

        if all_valid:
            # Apply settings logic here
            # print(f"Applying settings: {self._current_values}")
            pass

    def _reset_settings(self):
        """Reset all settings to defaults"""
        # This needs to know the original default values for each setting
        # For now, it just clears current_values, which isn't a true reset.
        # A proper reset would involve iterating through added settings and restoring their initial defaults.
        # print("Resetting settings (placeholder)")
        # Example: Iterate through controls and set their default values
        # This is complex as default values are not stored systematically for reset here.
        pass

    def get_setting_value(self, setting_key: str) -> Any:
        """Get current value of a setting"""
        return self._current_values.get(setting_key)

    def set_setting_value(self, setting_key: str, value: Any):
        """Set value of a setting"""
        self._current_values[setting_key] = value
        # Update UI controls here - this requires finding the control associated with setting_key
        # For example:
        # for group in self._settings_groups.values():
        #     if hasattr(group, '_fields') and setting_key in group._fields: # Assuming FluentFormGroup stores fields
        #         widget = group._fields[setting_key]['widget']
        #         if isinstance(widget, FluentLineEdit): widget.setText(str(value))
        #         elif isinstance(widget, QComboBox): widget.setCurrentText(str(value))
        #         elif isinstance(widget, FluentCheckBox): widget.setChecked(bool(value))
        #         elif isinstance(widget, QSpinBox): widget.setValue(int(value))
        #         break


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
        layout = FluentLayoutBuilder.create_vertical_layout()
        self.setLayout(layout)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.properties_widget = QWidget()
        self.properties_layout = FluentLayoutBuilder.create_vertical_layout(
            spacing=4)
        self.properties_widget.setLayout(self.properties_layout)

        self.scroll_area.setWidget(self.properties_widget)
        layout.addWidget(self.scroll_area)

        self.properties_layout.addStretch()

    def set_object_properties(self, obj: object, property_names: Optional[List[str]] = None):
        """Set object to edit properties for"""
        self.clear_properties()

        if property_names is None:
            property_names = [attr for attr in dir(obj)
                              if not attr.startswith('_') and
                              not callable(getattr(obj, attr))]

        for prop_name in property_names:
            if hasattr(obj, prop_name):
                value = getattr(obj, prop_name)
                self.add_property(prop_name, value, type(value))

    def add_property(self, name: str, value: Any, prop_type: Optional[type] = None):
        """Add a property to edit"""
        if prop_type is None:
            prop_type = type(value)

        control = self._create_control_for_type(name, prop_type, value)
        if control is None:
            return

        prop_frame = QFrame()
        prop_layout = FluentLayoutBuilder.create_horizontal_layout()
        prop_frame.setLayout(prop_layout)

        name_label = QLabel(name + ":")
        name_label.setMinimumWidth(120)
        name_label.setFont(QFont("Segoe UI", 9))
        prop_layout.addWidget(name_label)

        prop_layout.addWidget(control)

        self._properties[name] = value
        self._controls[name] = control

        layout = self.properties_layout
        layout.insertWidget(layout.count() - 1, prop_frame)

    def _create_control_for_type(self, prop_name: str, prop_type: type, value: Any) -> Optional[QWidget]:
        """Create appropriate control for property type"""
        control: Optional[QWidget] = None
        if prop_type == str:
            edit_control = FluentLineEdit()
            edit_control.setText(str(value))
            edit_control.textChanged.connect(
                lambda text, current_prop_name=prop_name: self._on_property_changed(current_prop_name, text))
            control = edit_control

        elif prop_type == bool:
            # No text label needed here as it's a property value
            check_control = FluentCheckBox()
            check_control.setChecked(bool(value))
            check_control.toggled.connect(
                lambda checked, current_prop_name=prop_name: self._on_property_changed(current_prop_name, checked))
            control = check_control

        elif prop_type == int:
            spin_control = QSpinBox()
            spin_control.setRange(-2147483648, 2147483647)  # Max int range
            spin_control.setValue(int(value))
            spin_control.valueChanged.connect(
                lambda val, current_prop_name=prop_name: self._on_property_changed(current_prop_name, val))
            control = spin_control

        elif prop_type == float:
            float_edit_control = QLineEdit()  # Or QDoubleSpinBox for better float handling
            float_edit_control.setText(str(value))
            float_edit_control.textChanged.connect(
                lambda text, current_prop_name=prop_name: self._on_property_changed(current_prop_name, float(text) if text else 0.0))
            control = float_edit_control

        else:  # Default for unknown types
            default_edit_control = QLineEdit()
            default_edit_control.setText(str(value))
            # Make it read-only if type is not directly editable
            default_edit_control.setReadOnly(True)
            # Or connect if changes should be attempted:
            # default_edit_control.textChanged.connect(
            #     lambda text, current_prop_name=prop_name: self._on_property_changed(current_prop_name, text))
            control = default_edit_control
        return control

    def _on_property_changed(self, name: str, value: Any):
        """Handle property value change"""
        self._properties[name] = value
        self.property_changed.emit(name, value)

    def clear_properties(self):
        """Clear all properties"""
        while self.properties_layout.count() > 1:  # Keep the stretch
            item = self.properties_layout.takeAt(0)
            if item and item.widget():
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
        main_layout = FluentLayoutBuilder.create_vertical_layout()
        self.setLayout(main_layout)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        main_layout.addWidget(title_label)

        self.form_widget = QWidget()
        self.form_layout = FluentLayoutBuilder.create_vertical_layout()
        self.form_widget.setLayout(self.form_layout)
        main_layout.addWidget(self.form_widget)

        # Pass main_layout to add button_frame
        self._setup_buttons(main_layout)

    def _setup_buttons(self, main_layout: QVBoxLayout):  # Accept main_layout
        """Setup form buttons"""
        button_frame = QFrame()
        button_layout = FluentLayoutBuilder.create_horizontal_layout()
        button_frame.setLayout(button_layout)

        button_layout.addStretch()

        self.cancel_button = FluentStandardButton("Cancel", size=(80, 32))
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)

        self.submit_button = FluentStandardButton("Submit", size=(80, 32))
        self.submit_button.clicked.connect(self._on_submit)
        button_layout.addWidget(self.submit_button)

        main_layout.addWidget(button_frame)  # Add to the passed main_layout

    def add_text_field(self, field_name: str, label: str,
                       required: bool = False, validator: Optional[Callable] = None) -> FluentLineEdit:
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

        label_text = label + ("*" if required else "") + ":"
        label_widget = QLabel(label_text)
        label_widget.setMinimumWidth(100)
        if required:
            # Consider theme-based styling
            label_widget.setStyleSheet("color: red;")

        row_layout.addWidget(label_widget)
        row_layout.addWidget(widget, 1)  # Add stretch factor

        self.form_layout.addWidget(row_frame)

    def _on_submit(self):
        """Handle form submission"""
        if not self._validate_form():
            return

        form_data = {}
        for field_name, widget in self._form_fields.items():
            if isinstance(widget, FluentLineEdit):  # Handles QLineEdit as well
                form_data[field_name] = widget.text()
            elif isinstance(widget, QComboBox):
                form_data[field_name] = widget.currentText()
            elif isinstance(widget, FluentCheckBox):
                form_data[field_name] = widget.isChecked()
            # Add other widget types as needed

        self.submitted.emit(form_data)

    def _on_cancel(self):
        """Handle form cancellation"""
        self.cancelled.emit()

    def _validate_form(self) -> bool:
        """Validate all form fields"""
        for field_name, validator in self._validators.items():
            widget = self._form_fields[field_name]
            value_to_validate: Any

            # FluentLineEdit inherits QLineEdit
            if isinstance(widget, (QLineEdit, FluentLineEdit)):
                value_to_validate = widget.text()
            elif isinstance(widget, QComboBox):
                value_to_validate = widget.currentText()
            elif isinstance(widget, FluentCheckBox):
                value_to_validate = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                value_to_validate = widget.value()
            else:
                # print(f"Warning: Validator for {field_name} called on unhandled widget type {type(widget)}")
                continue  # Skip validation for this field

            if not validator(value_to_validate):
                # Optionally, highlight the field or show a message
                # print(f"Validation failed for field: {field_name}")
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

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(message_label)

        button_frame = QFrame()
        button_layout = FluentLayoutBuilder.create_horizontal_layout()
        button_frame.setLayout(button_layout)

        button_layout.addStretch()

        self.cancel_button = FluentStandardButton(cancel_text, size=(80, 32))
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)

        self.confirm_button = FluentStandardButton(confirm_text, size=(80, 32))
        self.confirm_button.clicked.connect(self._on_confirm)
        button_layout.addWidget(self.confirm_button)

        layout.addWidget(button_frame)

    def _setup_animations(self):
        """Setup entrance animations"""
        # Ensure self is a QWidget for FluentTransition
        if isinstance(self, QWidget):
            self._entrance_transition = FluentTransition.create_transition(
                self, FluentTransition.FADE, duration=200)
        else:
            self._entrance_transition = None

    def _on_confirm(self):
        """Handle confirmation"""
        self.confirmed.emit()

    def _on_cancel(self):
        """Handle cancellation"""
        self.rejected.emit()

    def show_animated(self):
        """Show dialog with animation"""
        self.show()
        if self._entrance_transition:
            # Assuming fade in means opacity from 0 to 1
            if hasattr(self._entrance_transition, 'setStartValue') and hasattr(self._entrance_transition, 'setEndValue'):
                # For QPropertyAnimation on opacity effect
                effect = self.graphicsEffect()
                # Check if setGraphicsEffect exists
                if not effect and hasattr(self, 'setGraphicsEffect'):
                    from PySide6.QtWidgets import QGraphicsOpacityEffect
                    effect = QGraphicsOpacityEffect(self)
                    self.setGraphicsEffect(effect)  # type: ignore

                if effect:  # Check if effect is not None
                    self._entrance_transition.setTargetObject(
                        effect)  # Ensure target is effect for opacity
                    self._entrance_transition.setPropertyName(b"opacity")
                    self._entrance_transition.setStartValue(0.0)
                    self._entrance_transition.setEndValue(1.0)
            self._entrance_transition.start()
