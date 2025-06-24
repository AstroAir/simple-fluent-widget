"""
Composite Form Components - Optimized for Python 3.11+

This module provides higher-level form components that combine multiple
basic widgets into common form patterns with built-in validation and
dynamic user feedback using modern Python features.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable, Union, Protocol, TypedDict
from weakref import WeakValueDictionary
from enum import Enum, auto
import time
import re

from PySide6.QtWidgets import (QWidget, QLabel, QLineEdit, QTextEdit,
                               QComboBox, QCheckBox, QRadioButton, QButtonGroup,
                               QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit,
                               QFrame, QScrollArea, QVBoxLayout, QGraphicsOpacityEffect,
                               QHBoxLayout, QGridLayout)
from PySide6.QtCore import (Signal, QDate, QTime, QObject, QPropertyAnimation,
                            QByteArray, QTimer, Qt)
from PySide6.QtGui import QFont, QColor

from core.enhanced_base import (FluentStandardButton,
                                FluentLayoutBuilder, FluentCompositeWidget,
                                FluentFormGroup)
from core.animation import FluentAnimation
from core.theme import theme_manager
from core.enhanced_animations import FluentMicroInteraction, FluentTransition

# Try to import enhanced components, fallback to basic ones
try:
    from components.basic.textbox import FluentLineEdit, FluentTextEdit
    # 彻底解决类名遮蔽问题：避免在 except 分支定义 FluentCheckBox，始终用 _BaseFluentCheckBox
    from components.basic.checkbox import FluentCheckBox as _BaseFluentCheckBox

    class FluentCheckBox(_BaseFluentCheckBox):
        """Composite FluentCheckBox for type compatibility."""
        pass
    from components.basic.button import FluentButton
    from components.basic.combobox import FluentComboBox
except ImportError:
    from PySide6.QtWidgets import (QLineEdit as FluentLineEdit,
                                   QTextEdit as FluentTextEdit,
                                   QCheckBox,
                                   QPushButton as FluentButton,
                                   QComboBox as FluentComboBox)
    # fallback: 定义 FluentCheckBox 占位，确保类型总是可用
    # 不再定义 FluentCheckBox，始终用上方的类


# Modern type definitions
class FieldType(Enum):
    """Field types for form components"""
    TEXT = auto()
    MULTILINE = auto()
    NUMBER = auto()
    EMAIL = auto()
    PASSWORD = auto()
    CHOICE = auto()
    BOOLEAN = auto()
    DATE = auto()
    TIME = auto()
    DATETIME = auto()


class ValidationResult(Enum):
    """Validation result states"""
    VALID = auto()
    INVALID = auto()
    PENDING = auto()
    WARNING = auto()


@dataclass(slots=True, frozen=True)
class FieldDefinition:
    """Immutable field definition with slots for memory efficiency"""
    name: str
    label: str
    field_type: FieldType
    required: bool = False
    placeholder: str = ""
    tooltip: str = ""
    validator: Optional[Callable[[Any], ValidationResult]] = None
    options: List[str] = field(default_factory=list)  # For choice fields
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    max_length: Optional[int] = None


@dataclass(slots=True)
class FormState:
    """Mutable state container for form"""
    fields: Dict[str, QWidget] = field(default_factory=dict)
    validators: Dict[str, List[Callable]] = field(default_factory=dict)
    validation_errors: Dict[str, str] = field(default_factory=dict)
    required_fields: List[str] = field(default_factory=list)
    is_valid: bool = False
    last_validation_time: float = field(default_factory=time.time)


class ValidationProtocol(Protocol):
    """Protocol for validation functions"""

    def __call__(self, value: Any) -> ValidationResult: ...


class FormFieldData(TypedDict, total=False):
    """Type-safe form field data structure"""
    value: Any
    is_valid: bool
    error_message: str
    field_type: FieldType


class FluentFieldGroup(FluentFormGroup):
    """
    Enhanced form group with modern Python features and comprehensive validation

    Features:
    - Type-safe field definitions
    - Async validation support
    - Enhanced animations
    - Memory-efficient state management
    - Comprehensive error handling
    """

    # Enhanced signals with type information
    # field_name, value, field_type
    field_changed = Signal(str, object, FieldType)
    validation_changed = Signal(bool, dict)  # is_valid, validation_errors
    field_focused = Signal(str)  # field_name
    field_blurred = Signal(str)  # field_name

    def __init__(self, title: str = "",
                 required_fields: Optional[List[str]] = None,
                 parent: Optional[QWidget] = None,
                 enable_animations: bool = True):
        super().__init__(title, parent=parent)

        # Modern state management
        self._state = FormState(required_fields=required_fields or [])

        # Performance optimization
        self._field_cache: WeakValueDictionary[str,
                                               QWidget] = WeakValueDictionary()
        self._style_cache: Dict[str, str] = {}

        # Animation system
        self._animations: Dict[str, QPropertyAnimation] = {}
        self._animation_enabled = enable_animations

        # Validation debouncing
        self._validation_timer = QTimer()
        self._validation_timer.setSingleShot(True)
        self._validation_timer.timeout.connect(self._perform_validation)
        self._validation_delay = 300  # ms

        # Error display and animation
        self._setup_error_display()
        self._setup_animations()
        self._setup_accessibility()

        # Connect theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_error_display(self):
        """Setup enhanced error message display with modern styling"""
        self.error_label = QLabel()
        self.error_label.setObjectName("formErrorLabel")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        self.addWidget(self.error_label)

        # Set up opacity effect and animation
        self.error_opacity_effect = QGraphicsOpacityEffect(self.error_label)
        self.error_label.setGraphicsEffect(self.error_opacity_effect)

        # Apply theme-aware styling
        self._apply_error_styling()

    def _setup_animations(self):
        """Setup enhanced animation system"""
        if not self._animation_enabled:
            return

        # Error label fade animation
        self._animations['error_fade'] = QPropertyAnimation(
            self.error_opacity_effect, QByteArray(b"opacity")
        )
        self._animations['error_fade'].setDuration(200)

        # Field highlight animation
        self._animations['field_highlight'] = QPropertyAnimation(
            self, QByteArray(b"windowOpacity")
        )
        self._animations['field_highlight'].setDuration(150)

    def _setup_accessibility(self):
        """Setup accessibility features"""
        self.setAccessibleName("Form Field Group")
        self.setAccessibleDescription("Group of form fields with validation")

        # Enable keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)

    def _apply_error_styling(self):
        """Apply theme-aware error styling"""
        theme = theme_manager

        error_style = f"""
            QLabel#formErrorLabel {{
                color: {theme.get_color('error', '#dc3545').name()};
                background-color: {theme.get_color('error_background', '#f8d7da').name()};
                border: 1px solid {theme.get_color('error_border', '#f5c6cb').name()};
                border-radius: 4px;
                padding: 8px 12px;
                margin-top: 4px;
                font-size: 12px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }}
        """

        self.error_label.setStyleSheet(error_style)

    def _on_theme_changed(self):
        """Handle theme change"""
        self._style_cache.clear()
        self._apply_error_styling()

    def add_field_from_definition(self, field_def: FieldDefinition) -> QWidget:
        """Add field from modern field definition"""
        match field_def.field_type:
            case FieldType.TEXT:
                return self.add_text_field(
                    field_def.name, field_def.label, field_def.placeholder,
                    field_def.required, field_def.validator
                )
            case FieldType.MULTILINE:
                return self.add_multiline_field(
                    field_def.name, field_def.label, field_def.placeholder,
                    field_def.required, validator=field_def.validator
                )
            case FieldType.EMAIL:
                return self.add_email_field(
                    field_def.name, field_def.label, field_def.placeholder,
                    field_def.required
                )
            case FieldType.PASSWORD:
                return self.add_password_field(
                    field_def.name, field_def.label, field_def.placeholder,
                    field_def.required
                )
            case FieldType.NUMBER:
                # 类型安全处理，float 用 add_decimal_field，int 用 add_number_field
                if isinstance(field_def.min_value, float) or isinstance(field_def.max_value, float):
                    return self.add_decimal_field(
                        field_def.name,
                        field_def.label,
                        float(
                            field_def.min_value) if field_def.min_value is not None else 0.0,
                        float(
                            field_def.max_value) if field_def.max_value is not None else 100.0,
                        required=field_def.required
                    )
                else:
                    return self.add_number_field(
                        field_def.name,
                        field_def.label,
                        field_def.required,
                        int(field_def.min_value) if field_def.min_value is not None else 0,
                        int(field_def.max_value) if field_def.max_value is not None else 100
                    )
            case FieldType.CHOICE:
                return self.add_choice_field(
                    field_def.name, field_def.label, field_def.options,
                    field_def.required
                )
            case FieldType.BOOLEAN:
                return self.add_boolean_field(
                    field_def.name, field_def.label, field_def.required
                )
            case _:
                # Default to text field
                return self.add_text_field(
                    field_def.name, field_def.label, field_def.placeholder,
                    field_def.required, field_def.validator
                )

    def add_text_field(self, field_name: str, label: str,
                       placeholder: str = "", required: bool = False,
                       validator: Optional[Callable] = None) -> QLineEdit:
        """Add enhanced text input field with modern features"""
        field_edit = FluentLineEdit()
        field_edit.setPlaceholderText(placeholder)
        field_edit.setObjectName(f"field_{field_name}")

        # Enhanced event connections
        field_edit.textChanged.connect(
            lambda text: self._on_field_changed(
                field_name, text
            )
        )
        # 修复 Pylance 类型报错，避免类型联合，确保类型安全
        orig_focus_in = field_edit.focusInEvent
        orig_focus_out = field_edit.focusOutEvent

        def focus_in_event(event):
            orig_focus_in(event)
            self.field_focused.emit(field_name)
            self._animate_field_focus(field_edit, True)

        def focus_out_event(event):
            orig_focus_out(event)
            self.field_blurred.emit(field_name)
            self._animate_field_focus(field_edit, False)

        field_edit.focusInEvent = focus_in_event
        field_edit.focusOutEvent = focus_out_event

        self._add_field_to_layout(field_name, label, field_edit, required)
        self._setup_field_validation(field_name, validator, required)

        # Cache field for performance
        self._field_cache[field_name] = field_edit

        return field_edit

    def add_email_field(self, field_name: str, label: str,
                        placeholder: str = "", required: bool = False) -> QLineEdit:
        """Add email field with built-in validation"""
        def email_validator(value): return (
            ValidationResult.VALID if re.match(r'^[^@]+@[^@]+\.[^@]+$', value)
            else ValidationResult.INVALID
        )

        field_edit = self.add_text_field(
            field_name, label, placeholder, required, email_validator)
        field_edit.setObjectName(f"email_field_{field_name}")

        return field_edit

    def add_password_field(self, field_name: str, label: str,
                           placeholder: str = "", required: bool = False) -> QLineEdit:
        """Add password field with enhanced security features"""
        field_edit = self.add_text_field(
            field_name, label, placeholder, required)
        field_edit.setEchoMode(QLineEdit.EchoMode.Password)
        field_edit.setObjectName(f"password_field_{field_name}")

        return field_edit

    def add_number_field(self, field_name: str, label: str, required: bool = False,
                         min_value: Optional[Union[int, float]] = None,
                         max_value: Optional[Union[int, float]] = None) -> Union[QSpinBox, QDoubleSpinBox]:
        """Add number field with range validation"""
        if isinstance(min_value, float) or isinstance(max_value, float):
            field_edit = QDoubleSpinBox()
            if min_value is not None:
                field_edit.setMinimum(float(min_value))
            if max_value is not None:
                field_edit.setMaximum(float(max_value))
        else:
            field_edit = QSpinBox()
            if min_value is not None:
                field_edit.setMinimum(int(min_value))
            if max_value is not None:
                field_edit.setMaximum(int(max_value))

        field_edit.setObjectName(f"number_field_{field_name}")
        field_edit.valueChanged.connect(
            lambda value: self._on_field_changed(
                field_name, value)
        )

        self._add_field_to_layout(field_name, label, field_edit, required)
        self._setup_field_validation(field_name, None, required)

        return field_edit

    def add_choice_field(self, field_name: str, label: str, options: List[str],
                         required: bool = False) -> QComboBox:
        """Add choice field with enhanced styling"""
        field_edit = FluentComboBox()
        field_edit.addItems(options)
        field_edit.setObjectName(f"choice_field_{field_name}")
        field_edit.currentTextChanged.connect(
            lambda text: self._on_field_changed(
                field_name, text)
        )

        self._add_field_to_layout(field_name, label, field_edit, required)
        self._setup_field_validation(field_name, None, required)

        return field_edit

    # 合并新旧 add_boolean_field，返回类型统一为 FluentCheckBox
    # 只保留新版实现，移除旧版add_boolean_field，返回类型为FluentCheckBox
    def add_boolean_field(self, field_name: str, label: str,
                          required: bool = False, default_value: bool = False) -> FluentCheckBox:
        """Add a boolean checkbox field with enhanced styling"""
        checkbox = FluentCheckBox(label)
        checkbox.setObjectName(f"boolean_field_{field_name}")
        checkbox.setChecked(default_value)
        checkbox.toggled.connect(
            lambda checked: self._on_field_changed(field_name, checked)
        )
        self._state.fields[field_name] = checkbox
        self.addWidget(checkbox)
        self._setup_field_validation(field_name, None, required)
        return checkbox

    def add_multiline_field(self, field_name: str, label: str,
                            placeholder: str = "", required: bool = False,
                            max_height: int = 100,
                            validator: Optional[Callable] = None) -> QTextEdit:
        """Add enhanced multiline text area field"""
        field_edit = FluentTextEdit()
        field_edit.setPlaceholderText(placeholder)
        field_edit.setMaximumHeight(max_height)
        field_edit.setObjectName(f"multiline_field_{field_name}")

        field_edit.textChanged.connect(
            lambda: self._on_field_changed(
                field_name, field_edit.toPlainText())
        )

        self._add_field_to_layout(field_name, label, field_edit, required)
        self._setup_field_validation(field_name, validator, required)

        return field_edit

    def _setup_field_validation(self, field_name: str, validator: Optional[Callable], required: bool):
        """Setup validation for a field"""
        if validator:
            self._state.validators[field_name] = [validator]

        if required and field_name not in self._state.required_fields:
            self._state.required_fields.append(field_name)

    def _animate_field_focus(self, field: QWidget, focused: bool):
        """Animate field focus state"""
        if not self._animation_enabled:
            return
        # 移除无效动画调用，防止属性不存在报错
        pass

    # 移除重复的 _on_field_changed，只保留主实现

    def _perform_validation(self):
        """Perform comprehensive form validation"""
        self._state.validation_errors.clear()

        for field_name, field_widget in self._state.fields.items():
            # Get field value
            value = self._get_field_value(field_widget)

            # Check required fields
            if field_name in self._state.required_fields:
                if not value or (isinstance(value, str) and not value.strip()):
                    self._state.validation_errors[field_name] = f"{field_name} is required"
                    continue

            # Run custom validators
            if field_name in self._state.validators:
                for validator in self._state.validators[field_name]:
                    try:
                        result = validator(value)
                        if result == ValidationResult.INVALID:
                            self._state.validation_errors[field_name] = f"Invalid {field_name}"
                            break
                        elif result == ValidationResult.WARNING:
                            # Could show warnings differently
                            pass
                    except Exception as e:
                        self._state.validation_errors[field_name] = f"Validation error: {e}"
                        break

        # Update validation state
        self._state.is_valid = len(self._state.validation_errors) == 0
        self._state.last_validation_time = time.time()

        # Update UI
        self._update_error_display()

        # Emit validation signal
        self.validation_changed.emit(
            self._state.is_valid, self._state.validation_errors.copy())

    def _get_field_value(self, widget: QWidget) -> Any:
        """Get value from field widget based on its type"""
        if isinstance(widget, (FluentLineEdit, QLineEdit)):
            return widget.text()
        elif isinstance(widget, (FluentTextEdit, QTextEdit)):
            return widget.toPlainText()
        elif isinstance(widget, (FluentCheckBox, QCheckBox)):
            return widget.isChecked()
        elif isinstance(widget, (FluentComboBox, QComboBox)):
            return widget.currentText()
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.value()
        elif isinstance(widget, QDateEdit):
            return widget.date()
        elif isinstance(widget, QTimeEdit):
            return widget.time()
        else:
            return None

    # 移除重复的 _update_error_display，只保留主实现

    def get_form_data(self) -> Dict[str, Any]:
        """Get all form data as a dictionary"""
        form_data = {}
        for field_name, field_widget in self._state.fields.items():
            form_data[field_name] = self._get_field_value(field_widget)
        return form_data

    def set_form_data(self, data: Dict[str, Any]):
        """Set form data from dictionary"""
        for field_name, value in data.items():
            if field_name in self._state.fields:
                self._set_field_value(self._state.fields[field_name], value)

    def _set_field_value(self, field_widget: QWidget, value: Any):
        """Set value for field widget based on its type"""
        try:
            if isinstance(field_widget, (FluentLineEdit, QLineEdit)):
                field_widget.setText(str(value) if value is not None else "")
            elif isinstance(field_widget, (FluentTextEdit, QTextEdit)):
                field_widget.setPlainText(
                    str(value) if value is not None else "")
            elif isinstance(field_widget, (FluentCheckBox, QCheckBox)):
                field_widget.setChecked(bool(value))
            elif isinstance(field_widget, (FluentComboBox, QComboBox)):
                if isinstance(value, int):
                    field_widget.setCurrentIndex(value)
                else:
                    field_widget.setCurrentText(str(value))
            elif isinstance(field_widget, (QSpinBox, QDoubleSpinBox)):
                field_widget.setValue(value)
            elif isinstance(field_widget, QDateEdit):
                if isinstance(value, QDate):
                    field_widget.setDate(value)
            elif isinstance(field_widget, QTimeEdit):
                if isinstance(value, QTime):
                    field_widget.setTime(value)
        except Exception as e:
            print(f"Error setting field value for {field_widget}: {e}")

    def validate_form(self) -> bool:
        """Manually trigger form validation"""
        self._perform_validation()
        return self._state.is_valid

    def clear_form(self):
        """Clear all form fields"""
        for field_widget in self._state.fields.values():
            self._set_field_value(field_widget, None)

        # Clear validation errors
        self._state.validation_errors.clear()
        self._update_error_display()

    def get_validation_errors(self) -> Dict[str, str]:
        """Get current validation errors"""
        return self._state.validation_errors.copy()

    def is_form_valid(self) -> bool:
        """Check if form is currently valid"""
        return self._state.is_valid

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring"""
        return {
            'field_count': len(self._state.fields),
            'required_fields': len(self._state.required_fields),
            'validation_errors': len(self._state.validation_errors),
            'cached_fields': len(self._field_cache),
            'cached_styles': len(self._style_cache),
            'last_validation': self._state.last_validation_time,
            'is_valid': self._state.is_valid,
            'animations_enabled': self._animation_enabled
        }

    def cleanup(self):
        """Clean up resources when widget is destroyed"""
        # Stop validation timer
        if self._validation_timer:
            self._validation_timer.stop()

        # Stop all animations
        for animation in self._animations.values():
            if animation:
                animation.stop()

        # Clear caches
        self._field_cache.clear()
        self._style_cache.clear()

        # Disconnect theme manager
        try:
            theme_manager.theme_changed.disconnect(self._on_theme_changed)
        except RuntimeError:
            pass  # Already disconnected

    # Legacy method - keeping for backward compatibility
    def add_choice_field_legacy(self, field_name: str, label: str,
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

    def _add_number_field_legacy(self, field_name: str, label: str,
                                 min_value: int = 0, max_value: int = 100,
                                 default_value: int = 0, required: bool = False,
                                 validator: Optional[Callable] = None) -> QSpinBox:
        """[Legacy] Add a number input field."""
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

    # 移除旧 add_boolean_field（QCheckBox 版本），避免与新版重复

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
        # 修正：使用 self._state.validation_errors
        if field_name in self._state.validation_errors:
            del self._state.validation_errors[field_name]

        if hasattr(self, "_validators") and field_name in self._validators and self._validators[field_name]:
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
                        self._state.validation_errors[field_name] = custom_message
                    else:
                        label_text = self._get_field_label_text(
                            field_name) or field_name
                        self._state.validation_errors[
                            field_name] = f"Invalid value for {label_text}"
            except Exception as e:
                self._state.validation_errors[field_name] = str(e)

        self._update_error_display()
        self.field_changed.emit(field_name, value)
        self.validation_changed.emit(self.is_valid())

    def _get_field_label_text(self, field_name: str) -> Optional[str]:
        """Attempt to get the label text for a field for more descriptive errors."""
        return field_name

    def _update_error_display(self):
        """Update error message display with animation."""
        # 修正：使用 self._state.validation_errors
        if self._state.validation_errors:
            error_text = "\n".join(self._state.validation_errors.values())
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

    def validate(self) -> bool:
        """Validate all fields in the group."""
        self._state.validation_errors.clear()

        for field_name in self._required_fields:
            if field_name not in self._fields:
                continue
            widget = self._fields[field_name]
            value = self._get_field_value(widget)
            if self._is_empty_value(value):
                label = self._get_field_label_text(field_name) or field_name
                self._state.validation_errors[field_name] = f"{label} is required."

        for field_name, validator_list in self._validators.items():
            if field_name not in self._fields:
                continue
            if field_name in self._state.validation_errors:
                continue

            if validator_list:
                validator_func = validator_list[0]
                widget = self._fields[field_name]
                value = self._get_field_value(widget)
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
                            self._state.validation_errors[field_name] = custom_message
                        else:
                            self._state.validation_errors[
                                field_name] = f"Invalid value for {label_text}."
                except Exception as e:
                    self._state.validation_errors[field_name] = str(e)

        self._update_error_display()
        is_group_valid = len(self._state.validation_errors) == 0
        self.validation_changed.emit(is_group_valid)
        return is_group_valid

    def is_valid(self) -> bool:
        """Check if all fields are currently considered valid based on last validation."""
        return len(self._state.validation_errors) == 0

    def get_field_value(self, field_name: str) -> Any:
        """Get current value of a specific field."""
        widget = self._fields[field_name]
        return self._get_field_value(widget)

    # 移除与 QWidget 参数签名冲突的 _get_field_value(str)，如需获取值请用 get_field_value

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
            widget = self._fields[field_name]
            values[field_name] = self._get_field_value(widget)
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
        self._state.validation_errors.clear()
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
