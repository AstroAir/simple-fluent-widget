import unittest
from unittest.mock import patch
from typing import Optional, Callable, Any, Union, List
from PySide6.QtWidgets import QApplication, QWidget, QDialog
from PySide6.QtCore import Qt, QDate, QTime, QDateTime
from components.dialogs.input_dialog import FluentInputDialog, InputType, get_text_input, get_password_input, get_number_input, get_choice_input, get_file_path, get_folder_path

# filepath: components/dialogs/test_input_dialog.py




class TestFluentInputDialog(unittest.TestCase):
    """Test suite for FluentInputDialog."""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up for each test."""
        self.dialog = FluentInputDialog()
        self.parent = QWidget()

    def tearDown(self):
        """Tear down after each test."""
        if self.dialog:
            self.dialog.close()
        if self.parent:
            self.parent.close()

    def test_init(self):
        """Test the initialization of FluentInputDialog."""
        self.assertIsInstance(self.dialog, FluentInputDialog)
        self.assertEqual(self.dialog._input_type, InputType.TEXT)
        self.assertIsNone(self.dialog._input_widget)
        self.assertIsNone(self.dialog._validator)
        self.assertTrue(self.dialog._is_valid)
        self.assertEqual(self.dialog._placeholder, "")
        self.assertIsNone(self.dialog._default_value)
        self.assertEqual(self.dialog._items, [])
        self.assertIsNone(self.dialog._min_value)
        self.assertIsNone(self.dialog._max_value)
        self.assertEqual(self.dialog._file_filter, "All Files (*)")

    def test_setup_default_buttons(self):
        """Test the setup of default buttons."""
        self.dialog._setup_default_buttons()
        self.assertIsNotNone(self.dialog.ok_button)
        self.assertFalse(self.dialog.ok_button.isEnabled())

    def test_setup_input(self):
        """Test the setup_input method."""
        title = "Test Title"
        label = "Test Label"
        input_type = InputType.INTEGER
        default_value = 10
        placeholder = "Test Placeholder"
        validator = lambda x: x > 5
        items = ["A", "B", "C"]
        min_value = 0
        max_value = 100
        file_filter = "*.txt"

        self.dialog.setup_input(title, label, input_type, default_value,
                                placeholder, validator, items=items,
                                min_value=min_value, max_value=max_value,
                                file_filter=file_filter)

        self.assertEqual(self.dialog.windowTitle(), title)
        self.assertEqual(self.dialog._input_type, input_type)
        self.assertEqual(self.dialog._default_value, default_value)
        self.assertEqual(self.dialog._placeholder, placeholder)
        self.assertEqual(self.dialog._validator, validator)
        self.assertEqual(self.dialog._items, items)
        self.assertEqual(self.dialog._min_value, min_value)
        self.assertEqual(self.dialog._max_value, max_value)
        self.assertEqual(self.dialog._file_filter, file_filter)
        self.assertIsNotNone(self.dialog._input_widget)

    def test_create_input_content(self):
        """Test the _create_input_content method."""
        label = "Test Label"
        self.dialog.setup_input("Title", label)  # setup_input must be called first
        self.dialog._create_input_content(label)
        self.assertIsNotNone(self.dialog._input_widget)
        self.assertIsNotNone(self.dialog._validation_label)

    def test_create_input_widget_text(self):
        """Test creating a text input widget."""
        self.dialog._input_type = InputType.TEXT
        widget = self.dialog._create_input_widget()
        self.assertIsInstance(widget, QLineEdit)

    def test_create_input_widget_multiline_text(self):
        """Test creating a multiline text input widget."""
        self.dialog._input_type = InputType.MULTILINE_TEXT
        widget = self.dialog._create_input_widget()
        self.assertIsInstance(widget, QTextEdit)

    def test_create_input_widget_password(self):
        """Test creating a password input widget."""
        self.dialog._input_type = InputType.PASSWORD
        widget = self.dialog._create_input_widget()
        self.assertIsInstance(widget, QLineEdit)
        self.assertEqual(widget.echoMode(), QLineEdit.EchoMode.Password)

    def test_create_input_widget_integer(self):
        """Test creating an integer input widget."""
        self.dialog._input_type = InputType.INTEGER
        self.dialog._min_value = 0
        self.dialog._max_value = 100
        widget = self.dialog._create_input_widget()
        self.assertIsInstance(widget, QSpinBox)
        self.assertEqual(widget.minimum(), 0)
        self.assertEqual(widget.maximum(), 100)

    def test_create_input_widget_double(self):
        """Test creating a double input widget."""
        self.dialog._input_type = InputType.DOUBLE
        self.dialog._min_value = 0.0
        self.dialog._max_value = 100.0
        widget = self.dialog._create_input_widget()
        self.assertIsInstance(widget, QDoubleSpinBox)
        self.assertEqual(widget.minimum(), 0.0)
        self.assertEqual(widget.maximum(), 100.0)

    def test_create_input_widget_combobox(self):
        """Test creating a combobox input widget."""
        self.dialog._input_type = InputType.COMBOBOX
        self.dialog._items = ["A", "B", "C"]
        widget = self.dialog._create_input_widget()
        self.assertIsInstance(widget, QComboBox)
        self.assertEqual(widget.count(), 3)

    def test_create_input_widget_date(self):
        """Test creating a date input widget."""
        self.dialog._input_type = InputType.DATE
        widget = self.dialog._create_input_widget()
        self.assertIsInstance(widget, QDateEdit)
        self.assertTrue(widget.calendarPopup())

    def test_create_input_widget_time(self):
        """Test creating a time input widget."""
        self.dialog._input_type = InputType.TIME
        widget = self.dialog._create_input_widget()
        self.assertIsInstance(widget, QTimeEdit)

    def test_create_input_widget_datetime(self):
        """Test creating a datetime input widget."""
        self.dialog._input_type = InputType.DATETIME
        widget = self.dialog._create_input_widget()
        self.assertIsInstance(widget, QDateTimeEdit)
        self.assertTrue(widget.calendarPopup())

    def test_create_input_widget_file_path(self):
        """Test creating a file path input widget."""
        self.dialog._input_type = InputType.FILE_PATH
        widget = self.dialog._create_input_widget()
        self.assertIsInstance(widget, QWidget)  # Should return the container QFrame

    def test_create_input_widget_folder_path(self):
        """Test creating a folder path input widget."""
        self.dialog._input_type = InputType.FOLDER_PATH
        widget = self.dialog._create_input_widget()
        self.assertIsInstance(widget, QWidget)  # Should return the container QFrame

    @patch('components.dialogs.input_dialog.QFileDialog.getOpenFileName', return_value=("test_file.txt", "All Files (*)"))
    def test_browse_path_file_path(self, mock_open_file):
        """Test browsing for a file path."""
        self.dialog._input_type = InputType.FILE_PATH
        self.dialog._create_input_content("label")
        self.dialog._browse_path()
        self.assertEqual(self.dialog._path_edit.text(), "test_file.txt")

    @patch('components.dialogs.input_dialog.QFileDialog.getExistingDirectory', return_value="test_folder")
    def test_browse_path_folder_path(self, mock_existing_dir):
        """Test browsing for a folder path."""
        self.dialog._input_type = InputType.FOLDER_PATH
        self.dialog._create_input_content("label")
        self.dialog._browse_path()
        self.assertEqual(self.dialog._path_edit.text(), "test_folder")

    def test_set_default_value_text(self):
        """Test setting the default value for a text input."""
        self.dialog._input_type = InputType.TEXT
        self.dialog._create_input_widget()
        self.dialog._default_value = "Test"
        self.dialog._set_default_value()
        self.assertEqual(self.dialog._input_widget.text(), "Test")

    def test_set_default_value_multiline_text(self):
        """Test setting the default value for a multiline text input."""
        self.dialog._input_type = InputType.MULTILINE_TEXT
        self.dialog._create_input_widget()
        self.dialog._default_value = "Test\nMultiline"
        self.dialog._set_default_value()
        self.assertEqual(self.dialog._input_widget.toPlainText(), "Test\nMultiline")

    def test_set_default_value_password(self):
        """Test setting the default value for a password input."""
        self.dialog._input_type = InputType.PASSWORD
        self.dialog._create_input_widget()
        self.dialog._default_value = "password"
        self.dialog._set_default_value()
        self.assertEqual(self.dialog._input_widget.text(), "password")

    def test_set_default_value_integer(self):
        """Test setting the default value for an integer input."""
        self.dialog._input_type = InputType.INTEGER
        self.dialog._create_input_widget()
        self.dialog._default_value = 50
        self.dialog._set_default_value()
        self.assertEqual(self.dialog._input_widget.value(), 50)

    def test_set_default_value_double(self):
        """Test setting the default value for a double input."""
        self.dialog._input_type = InputType.DOUBLE
        self.dialog._create_input_widget()
        self.dialog._default_value = 3.14
        self.dialog._set_default_value()
        self.assertEqual(self.dialog._input_widget.value(), 3.14)

    def test_set_default_value_combobox(self):
        """Test setting the default value for a combobox input."""
        self.dialog._input_type = InputType.COMBOBOX
        self.dialog._items = ["A", "B", "C"]
        self.dialog._create_input_widget()
        self.dialog._default_value = "B"
        self.dialog._set_default_value()
        self.assertEqual(self.dialog._input_widget.currentText(), "B")

    def test_set_default_value_date(self):
        """Test setting the default value for a date input."""
        self.dialog._input_type = InputType.DATE
        self.dialog._create_input_widget()
        self.dialog._default_value = date(2024, 1, 1)
        self.dialog._set_default_value()
        self.assertEqual(self.dialog._input_widget.date(), QDate(2024, 1, 1))

    def test_set_default_value_time(self):
        """Test setting the default value for a time input."""
        self.dialog._input_type = InputType.TIME
        self.dialog._create_input_widget()
        self.dialog._default_value = datetime(2024, 1, 1, 10, 30, 0)
        self.dialog._set_default_value()
        self.assertEqual(self.dialog._input_widget.time(), QTime(10, 30, 0))

    def test_set_default_value_datetime(self):
        """Test setting the default value for a datetime input."""
        self.dialog._input_type = InputType.DATETIME
        self.dialog._create_input_widget()
        self.dialog._default_value = datetime(2024, 1, 1, 10, 30, 0)
        self.dialog._set_default_value()
        self.assertEqual(self.dialog._input_widget.dateTime(), QDateTime(QDate(2024, 1, 1), QTime(10, 30, 0)))

    def test_set_default_value_file_path(self):
        """Test setting the default value for a file path input."""
        self.dialog._input_type = InputType.FILE_PATH
        self.dialog._create_input_widget()
        self.dialog._default_value = "/path/to/file.txt"
        self.dialog._set_default_value()
        self.assertEqual(self.dialog._path_edit.text(), "/path/to/file.txt")

    def test_set_default_value_folder_path(self):
        """Test setting the default value for a folder path input."""
        self.dialog._input_type = InputType.FOLDER_PATH
        self.dialog._create_input_widget()
        self.dialog._default_value = "/path/to/folder"
        self.dialog._set_default_value()
        self.assertEqual(self.dialog._path_edit.text(), "/path/to/folder")

    def test_connect_validation_text(self):
        """Test connecting validation for text input."""
        self.dialog._input_type = InputType.TEXT
        self.dialog._create_input_widget()
        self.dialog._connect_validation()
        self.assertTrue(self.dialog._input_widget.textChanged.receivers() > 0)

    def test_connect_validation_multiline_text(self):
        """Test connecting validation for multiline text input."""
        self.dialog._input_type = InputType.MULTILINE_TEXT
        self.dialog._create_input_widget()
        self.dialog._connect_validation()
        self.assertTrue(self.dialog._input_widget.textChanged.receivers() > 0)

    def test_connect_validation_password(self):
        """Test connecting validation for password input."""
        self.dialog._input_type = InputType.PASSWORD
        self.dialog._create_input_widget()
        self.dialog._connect_validation()
        self.assertTrue(self.dialog._input_widget.textChanged.receivers() > 0)

    def test_connect_validation_integer(self):
        """Test connecting validation for integer input."""
        self.dialog._input_type = InputType.INTEGER
        self.dialog._create_input_widget()
        self.dialog._connect_validation()
        self.assertTrue(self.dialog._input_widget.valueChanged.receivers() > 0)

    def test_connect_validation_double(self):
        """Test connecting validation for double input."""
        self.dialog._input_type = InputType.DOUBLE
        self.dialog._create_input_widget()
        self.dialog._connect_validation()
        self.assertTrue(self.dialog._input_widget.valueChanged.receivers() > 0)

    def test_connect_validation_combobox(self):
        """Test connecting validation for combobox input."""
        self.dialog._input_type = InputType.COMBOBOX
        self.dialog._create_input_widget()
        self.dialog._connect_validation()
        self.assertTrue(self.dialog._input_widget.currentTextChanged.receivers() > 0)

    def test_connect_validation_date(self):
        """Test connecting validation for date input."""
        self.dialog._input_type = InputType.DATE
        self.dialog._create_input_widget()
        self.dialog._connect_validation()
        self.assertTrue(self.dialog._input_widget.dateChanged.receivers() > 0)

    def test_connect_validation_time(self):
        """Test connecting validation for time input."""
        self.dialog._input_type = InputType.TIME
        self.dialog._create_input_widget()
        self.dialog._connect_validation()
        self.assertTrue(self.dialog._input_widget.timeChanged.receivers() > 0)

    def test_connect_validation_datetime(self):
        """Test connecting validation for datetime input."""
        self.dialog._input_type = InputType.DATETIME
        self.dialog._create_input_widget()
        self.dialog._connect_validation()
        self.assertTrue(self.dialog._input_widget.dateTimeChanged.receivers() > 0)

    def test_connect_validation_file_path(self):
        """Test connecting validation for file path input."""
        self.dialog._input_type = InputType.FILE_PATH
        self.dialog._create_input_content("label")
        self.dialog._connect_validation()
        self.assertTrue(self.dialog._path_edit.textChanged.receivers() > 0)

    def test_connect_validation_folder_path(self):
        """Test connecting validation for folder path input."""
        self.dialog._input_type = InputType.FOLDER_PATH
        self.dialog._create_input_content("label")
        self.dialog._connect_validation()
        self.assertTrue(self.dialog._path_edit.textChanged.receivers() > 0)

    def test_validate_input_text_required(self):
        """Test validating a required text input."""
        self.dialog._input_type = InputType.TEXT
        self.dialog._create_input_widget()
        self.dialog._connect_validation()
        self.dialog._input_widget.setText("")
        self.dialog._validate_input()
        self.assertFalse(self.dialog._is_valid)

    def test_validate_input_multiline_text_required(self):
        """Test validating a required multiline text input."""
        self.dialog._input_type = InputType.MULTILINE_TEXT
        self.dialog._create_input_widget()
        self.dialog._connect_validation()
        self.dialog._input_widget.setPlainText("  ")
        self.dialog._validate_input()
        self.assertFalse(self.dialog._is_valid)

    def test_validate_input_password_required(self):
        """Test validating a required password input."""
        self.dialog._input_type = InputType.PASSWORD
        self.dialog._create_input_widget()
        self.dialog._connect_validation()
        self.dialog._input_widget.setText("")
        self.dialog._validate_input()
        self.assertFalse(self.dialog._is_valid)

    def test_validate_input_file_path_required(self):
        """Test validating a required file path input."""
        self.dialog._input_type = InputType.FILE_PATH
        self.dialog._create_input_content("label")
        self.dialog._connect_validation()
        self.dialog._path_edit.setText("")
        self.dialog._validate_input()
        self.assertFalse(self.dialog._is_valid)

    def test_validate_input_folder_path_required(self):
        """Test validating a required folder path input."""
        self.dialog._input_type = InputType.FOLDER_PATH
        self.dialog._create_input_content("label")
        self.dialog._connect_validation()
        self.dialog._path_edit.setText("")
        self.dialog._validate_input()
        self.assertFalse(self.dialog._is_valid)

    def test_validate_input_custom_validator_valid(self):
        """Test validating with a custom validator that returns True."""
        self.dialog._input_type = InputType.TEXT
        self.dialog._create_input_widget()
        self.dialog._validator = lambda x: True
        self.dialog._connect_validation()
        self.dialog._input_widget.setText("Test")
        self.dialog._validate_input()
        self.assertTrue(self.dialog._is_valid)

    def test_validate_input_custom_validator_invalid_false(self):
        """Test validating with a custom validator that returns False."""
        self.dialog._input_type = InputType.TEXT
        self.dialog._create_input_widget()
        self.dialog._validator = lambda x: False
        self.dialog._connect_validation()
        self.dialog._input_widget.setText("Test")
        self.dialog._validate_input()
        self.assertFalse(self.dialog._is_valid)

    def test_validate_input_custom_validator_invalid_string(self):
        """Test validating with a custom validator that returns an error string."""
        self.dialog._input_type = InputType.TEXT
        self.dialog._create_input_widget()
        self.dialog._validator = lambda x: "Invalid input"
        self.dialog._connect_validation()
        self.dialog._input_widget.setText("Test")
        self.dialog._validate_input()
        self.assertFalse(self.dialog._is_valid)
        self.assertEqual(self.dialog._validation_label.text(), "Invalid input")

    def test_validate_input_custom_validator_exception(self):
        """Test validating with a custom validator that raises an exception."""
        self.dialog._input_type = InputType.TEXT
        self.dialog._create_input_widget()
        self.dialog._validator = lambda x: raise ValueError("Test error")
        self.dialog._connect_validation()
        self.dialog._input_widget.setText("Test")
        self.dialog._validate_input()
        self.assertFalse(self.dialog._is_valid)

    def test_update_validation_ui_error(self):
        """Test updating the validation UI with an error message."""
        self.dialog._create_input_content("label")
        self.dialog._update_validation_ui("Test error")
        self.assertTrue(self.dialog._validation_label.isVisible())
        self.assertEqual(self.dialog._validation_label.text(), "Test error")

    def test_update_validation_ui_no_error(self):
        """Test updating the validation UI with no error message."""
        self.dialog._create_input_content("label")
        self.dialog._update_validation_ui("")
        self.assertFalse(self.dialog._validation_label.isVisible())

    def test_get_value_text(self):
        """Test getting the value of a text input."""
        self.dialog._input_type = InputType.TEXT
        self.dialog._create_input_widget()
        self.dialog._input_widget.setText("Test")
        self.assertEqual(self.dialog.get_value(), "Test")

    def test_get_value_multiline_text(self):
        """Test getting the value of a multiline text input."""
        self.dialog._input_type = InputType.MULTILINE_TEXT
        self.dialog._create_input_widget()
        self.dialog._input_widget.setPlainText("Test\nMultiline")
        self.assertEqual(self.dialog.get_value(), "Test\nMultiline")

    def test_get_value_password(self):
        """Test getting the value of a password input."""
        self.dialog._input_type = InputType.PASSWORD
        self.dialog._create_input_widget()
        self.dialog._input_widget.setText("password")
        self.assertEqual(self.dialog.get_value(), "password")

    def test_get_value_integer(self):
        """Test getting the value of an integer input."""
        self.dialog._input_type = InputType.INTEGER
        self.dialog._create_input_widget()
        self.dialog._input_widget.setValue(50)
        self.assertEqual(self.dialog.get_value(), 50)

    def test_get_value_double(self):
        """Test getting the value of a double input."""
        self.dialog._input_type = InputType.DOUBLE
        self.dialog._create_input_widget()
        self.dialog._input_widget.setValue(3.14)
        self.assertEqual(self.dialog.get_value(), 3.14)

    def test_get_value_combobox(self):
        """Test getting the value of a combobox input."""
        self.dialog._input_type = InputType.COMBOBOX
        self.dialog._create_input_widget()
        self.dialog._input_widget.addItem("A")
        self.dialog._input_widget.setCurrentText("A")
        self.assertEqual(self.dialog.get_value(), "A")

    def test_get_value_date(self):
        """Test getting the value of a date input."""
        self.dialog._input_type = InputType.DATE
        self.dialog._create_input_widget()
        self.dialog._input_widget.setDate(QDate(2024, 1, 1))
        self.assertEqual(self.dialog.get_value(), date(2024, 1, 1))

    def test_get_value_time(self):
        """Test getting the value of a time input."""
        self.dialog._input_type = InputType.TIME
        self.dialog._create_input_widget()
        self.dialog._input_widget.setTime(QTime(10, 30, 0))
        self.assertEqual(self.dialog.get_value(), QTime(10, 30, 0).toPython())

    def test_get_value_datetime(self):
        """Test getting the value of a datetime input."""
        self.dialog._input_type = InputType.DATETIME
        self.dialog._create_input_widget()
        self.dialog._input_widget.setDateTime(QDateTime(QDate(2024, 1, 1), QTime(10, 30, 0)))
        self.assertEqual(self.dialog.get_value(), QDateTime(QDate(2024, 1, 1), QTime(10, 30, 0)).toPython())

    def test_get_value_file_path(self):
        """Test getting the value of a file path input."""
        self.dialog._input_type = InputType.FILE_PATH
        self.dialog._create_input_content("label")
        self.dialog._path_edit.setText("/path/to/file.txt")
        self.assertEqual(self.dialog.get_value(), "/path/to/file.txt")

    def test_get_value_folder_path(self):
        """Test getting the value of a folder path input."""
        self.dialog._input_type = InputType.FOLDER_PATH
        self.dialog._create_input_content("label")
        self.dialog._path_edit.setText("/path/to/folder")
        self.assertEqual(self.dialog.get_value(), "/path/to/folder")

    @patch('components.dialogs.input_dialog.FluentInputDialog.get_value', return_value="test_value")
    @patch('components.dialogs.input_dialog.QDialog.close')
    def test_accept(self, mock_close, mock_get_value):
        """Test accepting the dialog."""
        self.dialog._is_valid = True
        self.dialog.accept()
        self.assertTrue(mock_close.called)

    @patch('components.dialogs.input_dialog.QDialog.close')
    def test_reject(self, mock_close):
        """Test rejecting the dialog."""
        self.dialog.reject()
        self.assertTrue(mock_close.called)

    @patch('components.dialogs.input_dialog.FluentInputDialog.exec', return_value=QDialog.DialogCode.Accepted)
    def test_get_text_input(self, mock_exec):
        """Test the get_text_input function."""
        result, accepted = get_text_input(self.parent, "Title", "Label", "Default", "Placeholder")
        self.assertTrue(accepted)

    @patch('components.dialogs.input_dialog.FluentInputDialog.exec', return_value=QDialog.DialogCode.Accepted)
    def test_get_password_input(self, mock_exec):
        """Test the get_password_input function."""
        result, accepted = get_password_input(self.parent, "Title", "Label")
        self.assertTrue(accepted)

    @patch('components.dialogs.input_dialog.FluentInputDialog.exec', return_value=QDialog.DialogCode.Accepted)
    def test_get_number_input(self, mock_exec):
        """Test the get_number_input function."""
        result, accepted = get_number_input(self.parent, "Title", "Label", 0, 0, 100, False)
        self.assertTrue(accepted)

    @patch('components.dialogs.input_dialog.FluentInputDialog.exec', return_value=QDialog.DialogCode.Accepted)
    def test_get_choice_input(self, mock_exec):
        """Test the get_choice_input function."""
        result, accepted = get_choice_input(self.parent, "Title", "Label", ["A", "B"], "A")
        self.assertTrue(accepted)

    @patch('components.dialogs.input_dialog.FluentInputDialog.exec', return_value=QDialog.DialogCode.Accepted)
    def test_get_file_path(self, mock_exec):
        """Test the get_file_path function."""
        result, accepted = get_file_path(self.parent, "Title", "Label", "*.txt")
        self.assertTrue(accepted)

    @patch('components.dialogs.input_dialog.FluentInputDialog.exec', return_value=QDialog.DialogCode.Accepted)
    def test_get_folder_path(self, mock_exec):
        """Test the get_folder_path function."""
        result, accepted = get_folder_path(self.parent, "Title", "Label")
        self.assertTrue(accepted)


if __name__ == '__main__':
    unittest.main()