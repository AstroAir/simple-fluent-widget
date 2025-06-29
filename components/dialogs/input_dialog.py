"""
FluentInputDialog - Input dialogs for collecting user input

Features:
- Text input with validation
- Number input with range validation  
- Multi-line text input
- Password input with masking
- Combobox selection
- Date/Time input
- File path input
- Custom validation support
- Real-time validation feedback
"""

from typing import Optional, Callable, Any, Union, List
from enum import Enum
from datetime import datetime, date

from PySide6.QtWidgets import (QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
                               QComboBox, QDateEdit, QTimeEdit, QDateTimeEdit,
                               QLabel, QVBoxLayout, QFrame, QHBoxLayout, QPushButton,
                               QFileDialog, QWidget, QDialog)
from PySide6.QtCore import Signal, QDate, QTime, QDateTime
from PySide6.QtGui import QValidator

from .base_dialog import FluentBaseDialog, DialogType, DialogSize, ButtonRole


class InputType(Enum):
    """Input field type enumeration."""
    TEXT = "text"
    MULTILINE_TEXT = "multiline_text"
    PASSWORD = "password"
    INTEGER = "integer"
    DOUBLE = "double"
    COMBOBOX = "combobox"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    FILE_PATH = "file_path"
    FOLDER_PATH = "folder_path"


class FluentInputDialog(FluentBaseDialog):
    """
    A flexible input dialog with Fluent Design styling.

    Supports various input types with validation and real-time feedback.
    """

    # Signals
    value_changed = Signal(object)  # Input value changed
    validation_changed = Signal(bool)  # Validation state changed
    input_accepted = Signal(object)  # Input accepted with value

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent, "", DialogType.MODAL, DialogSize.MEDIUM)

        self._input_type = InputType.TEXT
        self._input_widget: Any = None  # Can be any widget type based on input_type
        self._validation_label: Optional[QLabel] = None
        self._validator: Optional[Callable] = None
        self._is_valid = True

        # Input configuration
        self._placeholder = ""
        self._default_value: Any = None
        self._items: List[str] = []  # For combobox
        self._min_value: Optional[Union[int, float]] = None
        self._max_value: Optional[Union[int, float]] = None
        self._file_filter = "All Files (*)"

        # Setup default buttons
        self._setup_default_buttons()

    def _setup_default_buttons(self):
        """Setup default OK/Cancel buttons."""
        self.add_button("Cancel", ButtonRole.CANCEL, self.reject)
        self.ok_button = self.add_button("OK", ButtonRole.PRIMARY, self.accept)

        # Initially disable OK button
        self.set_button_enabled(ButtonRole.PRIMARY, False)

    def setup_input(self,
                    title: str,
                    label: str,
                    input_type: InputType = InputType.TEXT,
                    default_value: Any = None,
                    placeholder: str = "",
                    validator: Optional[Callable] = None,
                    **kwargs) -> 'FluentInputDialog':
        """
        Setup the input dialog configuration.

        Args:
            title: Dialog title
            label: Input field label
            input_type: Type of input field
            default_value: Default input value
            placeholder: Placeholder text
            validator: Custom validation function
            **kwargs: Additional configuration options

        Returns:
            Self for method chaining
        """
        self.set_title(title)
        self._input_type = input_type
        self._default_value = default_value
        self._placeholder = placeholder
        self._validator = validator

        # Extract kwargs
        self._items = kwargs.get('items', [])
        self._min_value = kwargs.get('min_value')
        self._max_value = kwargs.get('max_value')
        self._file_filter = kwargs.get('file_filter', "All Files (*)")

        self._create_input_content(label)
        return self

    def _create_input_content(self, label: str):
        """Create the input content area."""
        # Clear existing content
        for widget in self._content_widgets:
            self.remove_content_widget(widget)

        # Create content frame
        content_frame = QFrame()
        layout = QVBoxLayout(content_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Add label
        if label:
            label_widget = QLabel(label)
            label_widget.setObjectName("inputLabel")
            layout.addWidget(label_widget)

        # Create input widget based on type
        self._input_widget = self._create_input_widget()
        layout.addWidget(self._input_widget)

        # Add validation feedback label
        self._validation_label = QLabel()
        self._validation_label.setObjectName("validationLabel")
        self._validation_label.setWordWrap(True)
        self._validation_label.hide()
        layout.addWidget(self._validation_label)

        self.add_content_widget(content_frame)

        # Set default value and connect validation
        self._set_default_value()
        self._connect_validation()

    def _create_input_widget(self) -> QWidget:
        """Create the appropriate input widget."""
        if self._input_type == InputType.TEXT:
            widget = QLineEdit()
            widget.setPlaceholderText(self._placeholder)

        elif self._input_type == InputType.MULTILINE_TEXT:
            widget = QTextEdit()
            widget.setPlaceholderText(self._placeholder)
            widget.setMaximumHeight(120)

        elif self._input_type == InputType.PASSWORD:
            widget = QLineEdit()
            widget.setEchoMode(QLineEdit.EchoMode.Password)
            widget.setPlaceholderText(self._placeholder)

        elif self._input_type == InputType.INTEGER:
            widget = QSpinBox()
            if self._min_value is not None:
                widget.setMinimum(int(self._min_value))
            if self._max_value is not None:
                widget.setMaximum(int(self._max_value))

        elif self._input_type == InputType.DOUBLE:
            widget = QDoubleSpinBox()
            widget.setDecimals(2)
            if self._min_value is not None:
                widget.setMinimum(float(self._min_value))
            if self._max_value is not None:
                widget.setMaximum(float(self._max_value))

        elif self._input_type == InputType.COMBOBOX:
            widget = QComboBox()
            widget.addItems(self._items)
            widget.setEditable(True)
            widget.setPlaceholderText(self._placeholder)

        elif self._input_type == InputType.DATE:
            widget = QDateEdit()
            widget.setDate(QDate.currentDate())
            widget.setCalendarPopup(True)

        elif self._input_type == InputType.TIME:
            widget = QTimeEdit()
            widget.setTime(QTime.currentTime())

        elif self._input_type == InputType.DATETIME:
            widget = QDateTimeEdit()
            widget.setDateTime(QDateTime.currentDateTime())
            widget.setCalendarPopup(True)

        elif self._input_type in (InputType.FILE_PATH, InputType.FOLDER_PATH):
            widget = self._create_file_path_widget()

        else:
            widget = QLineEdit()
            widget.setPlaceholderText(self._placeholder)

        widget.setObjectName("inputWidget")
        return widget

    def _create_file_path_widget(self) -> QWidget:
        """Create file/folder path input widget."""
        container = QFrame()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Path display
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText(
            self._placeholder or "Select path...")
        self._path_edit.setReadOnly(True)
        layout.addWidget(self._path_edit, 1)

        # Browse button
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_path)
        layout.addWidget(browse_btn)

        return container

    def _browse_path(self):
        """Browse for file or folder path."""
        if self._input_type == InputType.FILE_PATH:
            path, _ = QFileDialog.getOpenFileName(
                self, "Select File", "", self._file_filter)
        else:  # FOLDER_PATH
            path = QFileDialog.getExistingDirectory(
                self, "Select Folder")

        if path:
            self._path_edit.setText(path)
            self._validate_input()

    def _set_default_value(self):
        """Set the default value for the input widget."""
        if self._default_value is None:
            return

        if self._input_type == InputType.TEXT:
            self._input_widget.setText(str(self._default_value))
        elif self._input_type == InputType.MULTILINE_TEXT:
            self._input_widget.setPlainText(str(self._default_value))
        elif self._input_type == InputType.PASSWORD:
            self._input_widget.setText(str(self._default_value))
        elif self._input_type == InputType.INTEGER:
            self._input_widget.setValue(int(self._default_value))
        elif self._input_type == InputType.DOUBLE:
            self._input_widget.setValue(float(self._default_value))
        elif self._input_type == InputType.COMBOBOX:
            self._input_widget.setCurrentText(str(self._default_value))
        elif self._input_type == InputType.DATE:
            if isinstance(self._default_value, date):
                qdate = QDate(self._default_value.year,
                              self._default_value.month, self._default_value.day)
                self._input_widget.setDate(qdate)
        elif self._input_type == InputType.TIME:
            if isinstance(self._default_value, datetime):
                time_val = self._default_value.time()
                qtime = QTime(time_val.hour, time_val.minute, time_val.second)
                self._input_widget.setTime(qtime)
        elif self._input_type == InputType.DATETIME:
            if isinstance(self._default_value, datetime):
                qdate = QDate(self._default_value.year,
                              self._default_value.month, self._default_value.day)
                qtime = QTime(self._default_value.hour,
                              self._default_value.minute, self._default_value.second)
                qdatetime = QDateTime(qdate, qtime)
                self._input_widget.setDateTime(qdatetime)
        elif self._input_type in (InputType.FILE_PATH, InputType.FOLDER_PATH):
            self._path_edit.setText(str(self._default_value))

    def _connect_validation(self):
        """Connect validation signals."""
        if self._input_type == InputType.TEXT:
            self._input_widget.textChanged.connect(self._validate_input)
        elif self._input_type == InputType.MULTILINE_TEXT:
            self._input_widget.textChanged.connect(self._validate_input)
        elif self._input_type == InputType.PASSWORD:
            self._input_widget.textChanged.connect(self._validate_input)
        elif self._input_type == InputType.INTEGER:
            self._input_widget.valueChanged.connect(self._validate_input)
        elif self._input_type == InputType.DOUBLE:
            self._input_widget.valueChanged.connect(self._validate_input)
        elif self._input_type == InputType.COMBOBOX:
            self._input_widget.currentTextChanged.connect(self._validate_input)
        elif self._input_type == InputType.DATE:
            self._input_widget.dateChanged.connect(self._validate_input)
        elif self._input_type == InputType.TIME:
            self._input_widget.timeChanged.connect(self._validate_input)
        elif self._input_type == InputType.DATETIME:
            self._input_widget.dateTimeChanged.connect(self._validate_input)
        elif self._input_type in (InputType.FILE_PATH, InputType.FOLDER_PATH):
            self._path_edit.textChanged.connect(self._validate_input)

        # Initial validation
        self._validate_input()

    def _validate_input(self):
        """Validate the current input."""
        value = self.get_value()
        old_valid = self._is_valid

        # Basic validation
        self._is_valid = True
        error_message = ""

        # Check if value is required and empty
        if self._input_type in (InputType.TEXT, InputType.PASSWORD) and not value:
            self._is_valid = False
            error_message = "This field is required."
        elif self._input_type == InputType.MULTILINE_TEXT and not value.strip():
            self._is_valid = False
            error_message = "This field is required."
        elif self._input_type in (InputType.FILE_PATH, InputType.FOLDER_PATH) and not value:
            self._is_valid = False
            error_message = "Please select a path."

        # Custom validation
        if self._is_valid and self._validator:
            try:
                result = self._validator(value)
                if result is False:
                    self._is_valid = False
                    error_message = "Invalid input."
                elif isinstance(result, str):
                    self._is_valid = False
                    error_message = result
            except Exception as e:
                self._is_valid = False
                error_message = str(e)

        # Update UI
        self._update_validation_ui(error_message)

        # Update OK button state
        self.set_button_enabled(ButtonRole.PRIMARY, self._is_valid)

        # Emit signals
        if old_valid != self._is_valid:
            self.validation_changed.emit(self._is_valid)
        self.value_changed.emit(value)

    def _update_validation_ui(self, error_message: str):
        """Update validation UI feedback."""
        if error_message and self._validation_label:
            self._validation_label.setText(error_message)
            self._validation_label.setStyleSheet("""
                QLabel {
                    color: #d13438;
                    font-size: 12px;
                    padding: 4px 0;
                }
            """)
            self._validation_label.show()
        elif self._validation_label:
            self._validation_label.hide()

    def get_value(self) -> Any:
        """Get the current input value."""
        if not self._input_widget:
            return None

        if self._input_type == InputType.TEXT:
            return self._input_widget.text()
        elif self._input_type == InputType.MULTILINE_TEXT:
            return self._input_widget.toPlainText()
        elif self._input_type == InputType.PASSWORD:
            return self._input_widget.text()
        elif self._input_type == InputType.INTEGER:
            return self._input_widget.value()
        elif self._input_type == InputType.DOUBLE:
            return self._input_widget.value()
        elif self._input_type == InputType.COMBOBOX:
            return self._input_widget.currentText()
        elif self._input_type == InputType.DATE:
            return self._input_widget.date().toPython()
        elif self._input_type == InputType.TIME:
            return self._input_widget.time().toPython()
        elif self._input_type == InputType.DATETIME:
            return self._input_widget.dateTime().toPython()
        elif self._input_type in (InputType.FILE_PATH, InputType.FOLDER_PATH):
            return self._path_edit.text()

        return None

    def accept(self):
        """Accept the dialog if input is valid."""
        if self._is_valid:
            value = self.get_value()
            self.input_accepted.emit(value)
            self.close_animated(QDialog.DialogCode.Accepted)

    def reject(self):
        """Reject the dialog."""
        self.close_animated(QDialog.DialogCode.Rejected)


# Convenience functions for common input types
def get_text_input(parent: Optional[QWidget] = None,
                   title: str = "Enter Text",
                   label: str = "Text:",
                   default: str = "",
                   placeholder: str = "",
                   validator: Optional[Callable] = None) -> tuple[str, bool]:
    """Get text input from user."""
    dialog = FluentInputDialog(parent)
    dialog.setup_input(title, label, InputType.TEXT,
                       default, placeholder, validator)

    result = dialog.exec()
    return dialog.get_value() if result == QDialog.DialogCode.Accepted else "", result == QDialog.DialogCode.Accepted


def get_password_input(parent: Optional[QWidget] = None,
                       title: str = "Enter Password",
                       label: str = "Password:",
                       validator: Optional[Callable] = None) -> tuple[str, bool]:
    """Get password input from user."""
    dialog = FluentInputDialog(parent)
    dialog.setup_input(title, label, InputType.PASSWORD, validator=validator)

    result = dialog.exec()
    return dialog.get_value() if result == QDialog.DialogCode.Accepted else "", result == QDialog.DialogCode.Accepted


def get_number_input(parent: Optional[QWidget] = None,
                     title: str = "Enter Number",
                     label: str = "Value:",
                     default: Union[int, float] = 0,
                     min_value: Optional[Union[int, float]] = None,
                     max_value: Optional[Union[int, float]] = None,
                     decimals: bool = False) -> tuple[Union[int, float], bool]:
    """Get number input from user."""
    dialog = FluentInputDialog(parent)
    input_type = InputType.DOUBLE if decimals else InputType.INTEGER
    dialog.setup_input(title, label, input_type, default,
                       min_value=min_value, max_value=max_value)

    result = dialog.exec()
    return dialog.get_value() if result == QDialog.DialogCode.Accepted else (0.0 if decimals else 0), result == QDialog.DialogCode.Accepted


def get_choice_input(parent: Optional[QWidget] = None,
                     title: str = "Select Item",
                     label: str = "Choice:",
                     items: Optional[List[str]] = None,
                     default: str = "") -> tuple[str, bool]:
    """Get choice input from user."""
    dialog = FluentInputDialog(parent)
    dialog.setup_input(title, label, InputType.COMBOBOX,
                       default, items=items or [])

    result = dialog.exec()
    return dialog.get_value() if result == QDialog.DialogCode.Accepted else "", result == QDialog.DialogCode.Accepted


def get_file_path(parent: Optional[QWidget] = None,
                  title: str = "Select File",
                  label: str = "File:",
                  file_filter: str = "All Files (*)") -> tuple[str, bool]:
    """Get file path from user."""
    dialog = FluentInputDialog(parent)
    dialog.setup_input(title, label, InputType.FILE_PATH,
                       file_filter=file_filter)

    result = dialog.exec()
    return dialog.get_value() if result == QDialog.DialogCode.Accepted else "", result == QDialog.DialogCode.Accepted


def get_folder_path(parent: Optional[QWidget] = None,
                    title: str = "Select Folder",
                    label: str = "Folder:") -> tuple[str, bool]:
    """Get folder path from user."""
    dialog = FluentInputDialog(parent)
    dialog.setup_input(title, label, InputType.FOLDER_PATH)

    result = dialog.exec()
    return dialog.get_value() if result == QDialog.DialogCode.Accepted else "", result == QDialog.DialogCode.Accepted
