import unittest
from unittest.mock import patch, Mock
from typing import Optional, Callable
from PySide6.QtWidgets import QApplication, QWidget, QDialog, QLabel, QFrame, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from .message_dialog import FluentMessageDialog, MessageType, MessageResult, show_information_dialog, show_warning_dialog, show_error_dialog, show_question_dialog, show_success_dialog

# filepath: components/dialogs/test_message_dialog.py

# Import necessary modules

# Import PySide6 modules

# Import the classes and functions to be tested using relative import
# Assuming ButtonRole is needed for button tests
from .base_dialog import ButtonRole

# Define the test class inheriting from unittest.TestCase


class TestFluentMessageDialog(unittest.TestCase):

    # Class method to set up QApplication once
    @classmethod
    def setUpClass(cls):
        # Check if QApplication instance already exists
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    # Method to set up before each test
    def setUp(self):
        # Create a new FluentMessageDialog instance for each test
        self.dialog = FluentMessageDialog()
        # Create a parent widget (optional but good practice)
        self.parent = QWidget()

    # Method to clean up after each test
    def tearDown(self):
        # Close the dialog if it exists
        if self.dialog:
            self.dialog.close()
        # Close the parent widget if it exists
        if self.parent:
            self.parent.close()
        # Process events to ensure widgets are properly closed
        QApplication.processEvents()

    # Test case for the __init__ method
    def test_init(self):
        # Assert that the dialog is an instance of FluentMessageDialog
        self.assertIsInstance(self.dialog, FluentMessageDialog)
        # Assert initial values of key attributes
        self.assertEqual(self.dialog._message_type, MessageType.INFORMATION)
        self.assertEqual(self.dialog._message_text, "")
        self.assertIsNone(self.dialog._result_callback)
        # Check container layout margins (specific to this dialog)
        margins = self.dialog.container_layout.contentsMargins()
        self.assertEqual(margins.left(), 24)
        self.assertEqual(margins.top(), 16)
        self.assertEqual(margins.right(), 24)
        self.assertEqual(margins.bottom(), 24)

    # Test case for the show_message method
    @patch('components.dialogs.message_dialog.FluentMessageDialog.exec', return_value=QDialog.DialogCode.Accepted)
    @patch('components.dialogs.message_dialog.FluentMessageDialog._setup_content')
    @patch('components.dialogs.message_dialog.FluentMessageDialog._setup_buttons_for_type')
    @patch('components.dialogs.message_dialog.FluentMessageDialog.set_title')
    def test_show_message(self, mock_set_title, mock_setup_buttons, mock_setup_content, mock_exec):
        # Define test parameters
        title = "Test Title"
        message = "Test Message"
        message_type = MessageType.WARNING
        callback = Mock()

        # Call show_message
        result_code = self.dialog.show_message(
            title, message, message_type, callback)

        # Assert that internal attributes are set correctly
        self.assertEqual(self.dialog._message_type, message_type)
        self.assertEqual(self.dialog._message_text, message)
        self.assertEqual(self.dialog._result_callback, callback)

        # Assert that helper methods are called
        mock_set_title.assert_called_once_with(title)
        mock_setup_content.assert_called_once()
        mock_setup_buttons.assert_called_once_with(message_type)
        mock_exec.assert_called_once()

        # Assert that the return value is from exec()
        self.assertEqual(result_code, QDialog.DialogCode.Accepted)

    # Test case for the _setup_content method
    @patch('components.dialogs.message_dialog.FluentMessageDialog._get_icon_for_type', return_value=QIcon())
    # Patch the base class method
    @patch('components.dialogs.base_dialog.FluentBaseDialog.add_content_widget')
    def test_setup_content(self, mock_add_content_widget, mock_get_icon):
        # Set message type and text
        self.dialog._message_type = MessageType.INFORMATION
        self.dialog._message_text = "Content Test Message"

        # Call _setup_content
        self.dialog._setup_content()

        # Assert that _get_icon_for_type is called
        mock_get_icon.assert_called_once_with(MessageType.INFORMATION)

        # Assert that add_content_widget is called with a QFrame
        mock_add_content_widget.assert_called_once()
        added_widget = mock_add_content_widget.call_args[0][0]
        self.assertIsInstance(added_widget, QFrame)

        # Check the layout and its children within the added frame
        content_layout = added_widget.layout()
        self.assertIsInstance(content_layout, QHBoxLayout)
        self.assertEqual(content_layout.count(), 2)  # Icon and message labels

        # Find the icon and message labels
        icon_label = content_layout.itemAt(0).widget()
        message_label = content_layout.itemAt(1).widget()

        self.assertIsInstance(icon_label, QLabel)
        self.assertIsInstance(message_label, QLabel)

        # Check properties of the message label
        self.assertEqual(message_label.text(), "Content Test Message")
        self.assertTrue(message_label.wordWrap())
        self.assertEqual(message_label.objectName(), "messageLabel")

        # Check properties of the icon label (size, pixmap is harder to check directly)
        self.assertEqual(icon_label.fixedSize().width(), 32)
        self.assertEqual(icon_label.fixedSize().height(), 32)
        # Check that a pixmap was set (even if it's the mocked empty one)
        self.assertFalse(icon_label.pixmap().isNull())

    # Test case for the _get_icon_for_type method
    # This test focuses on ensuring an QIcon is returned and basic drawing calls are made (via mocking QPainter)

    @patch('components.dialogs.message_dialog.QPainter')
    @patch('components.dialogs.message_dialog.QPixmap')
    def test_get_icon_for_type(self, mock_qpixmap, mock_qpainter):
        # Mock QPixmap and QPainter instances
        mock_pixmap_instance = Mock(spec=QPixmap)
        mock_qpixmap.return_value = mock_pixmap_instance
        mock_painter_instance = Mock(spec=QPainter)
        mock_qpainter.return_value = mock_painter_instance

        # Test for each message type
        for msg_type in MessageType:
            with self.subTest(msg_type=msg_type):
                # Reset mocks for each subtest
                mock_qpixmap.reset_mock()
                mock_qpainter.reset_mock()
                mock_pixmap_instance.reset_mock()
                mock_painter_instance.reset_mock()

                # Call the method
                icon = self.dialog._get_icon_for_type(msg_type)

                # Assert that a QIcon is returned
                self.assertIsInstance(icon, QIcon)

                # Assert that QPixmap and QPainter were used
                mock_qpixmap.assert_called_once_with(32, 32)
                mock_painter_instance.begin.assert_called_once_with(
                    mock_pixmap_instance)
                mock_painter_instance.end.assert_called_once()

                # Assert that drawing methods were called (ellipse and text)
                mock_painter_instance.drawEllipse.assert_called_once()
                mock_painter_instance.drawText.assert_called_once()

                # Check specific calls for a type (e.g., INFORMATION)
                if msg_type == MessageType.INFORMATION:
                    # Check brush color (approximate check)
                    painter_brush_color = mock_painter_instance.setBrush.call_args[0][0]
                    self.assertIsInstance(painter_brush_color, QColor)
                    # Check text drawn (approximate check)
                    drawn_text = mock_painter_instance.drawText.call_args[0][2]
                    self.assertEqual(drawn_text, "i")  # Symbol for INFORMATION

    # Test case for the _setup_buttons_for_type method
    # Patch the base class method
    @patch('components.dialogs.base_dialog.FluentBaseDialog.add_button')
    def test_setup_buttons_for_type(self, mock_add_button):
        # Test QUESTION type
        mock_add_button.reset_mock()
        self.dialog._setup_buttons_for_type(MessageType.QUESTION)
        self.assertEqual(mock_add_button.call_count, 2)
        # Check calls for QUESTION (order might vary, check arguments)
        calls = mock_add_button.call_args_list
        self.assertIn(unittest.mock.call(
            "No", ButtonRole.CANCEL, unittest.mock.ANY), calls)
        self.assertIn(unittest.mock.call(
            "Yes", ButtonRole.PRIMARY, unittest.mock.ANY), calls)

        # Test ERROR type
        mock_add_button.reset_mock()
        self.dialog._setup_buttons_for_type(MessageType.ERROR)
        self.assertEqual(mock_add_button.call_count, 1)
        mock_add_button.assert_called_once_with(
            "OK", ButtonRole.PRIMARY, unittest.mock.ANY)

        # Test INFORMATION type (default case)
        mock_add_button.reset_mock()
        self.dialog._setup_buttons_for_type(MessageType.INFORMATION)
        self.assertEqual(mock_add_button.call_count, 2)
        # Check calls for INFORMATION (order might vary, check arguments)
        calls = mock_add_button.call_args_list
        self.assertIn(unittest.mock.call(
            "Cancel", ButtonRole.CANCEL, unittest.mock.ANY), calls)
        self.assertIn(unittest.mock.call(
            "OK", ButtonRole.PRIMARY, unittest.mock.ANY), calls)

        # Test WARNING type (default case)
        mock_add_button.reset_mock()
        self.dialog._setup_buttons_for_type(MessageType.WARNING)
        self.assertEqual(mock_add_button.call_count, 2)
        calls = mock_add_button.call_args_list
        self.assertIn(unittest.mock.call(
            "Cancel", ButtonRole.CANCEL, unittest.mock.ANY), calls)
        self.assertIn(unittest.mock.call(
            "OK", ButtonRole.PRIMARY, unittest.mock.ANY), calls)

        # Test SUCCESS type (default case)
        mock_add_button.reset_mock()
        self.dialog._setup_buttons_for_type(MessageType.SUCCESS)
        self.assertEqual(mock_add_button.call_count, 2)
        calls = mock_add_button.call_args_list
        self.assertIn(unittest.mock.call(
            "Cancel", ButtonRole.CANCEL, unittest.mock.ANY), calls)
        self.assertIn(unittest.mock.call(
            "OK", ButtonRole.PRIMARY, unittest.mock.ANY), calls)

    # Test case for the _finish_with_result method

    @patch('components.dialogs.message_dialog.FluentMessageDialog.accept')
    @patch('components.dialogs.message_dialog.FluentMessageDialog.reject')
    def test_finish_with_result(self, mock_reject, mock_accept):
        # Mock the result_ready signal emit method
        mock_emit = Mock()
        self.dialog.result_ready.emit = mock_emit

        # Test with OK result and callback
        mock_callback = Mock()
        self.dialog._result_callback = mock_callback
        self.dialog._finish_with_result(MessageResult.OK)
        mock_emit.assert_called_once_with(MessageResult.OK.value)
        mock_callback.assert_called_once_with(MessageResult.OK)
        mock_accept.assert_called_once()
        mock_reject.assert_not_called()

        # Reset mocks
        mock_emit.reset_mock()
        mock_callback.reset_mock()
        mock_accept.reset_mock()
        mock_reject.reset_mock()

        # Test with YES result and no callback
        self.dialog._result_callback = None
        self.dialog._finish_with_result(MessageResult.YES)
        mock_emit.assert_called_once_with(MessageResult.YES.value)
        mock_callback.assert_not_called()
        mock_accept.assert_called_once()
        mock_reject.assert_not_called()

        # Reset mocks
        mock_emit.reset_mock()
        mock_callback.reset_mock()
        mock_accept.reset_mock()
        mock_reject.reset_mock()

        # Test with CANCEL result and callback
        mock_callback = Mock()
        self.dialog._result_callback = mock_callback
        self.dialog._finish_with_result(MessageResult.CANCEL)
        mock_emit.assert_called_once_with(MessageResult.CANCEL.value)
        mock_callback.assert_called_once_with(MessageResult.CANCEL)
        mock_accept.assert_not_called()
        mock_reject.assert_called_once()

        # Reset mocks
        mock_emit.reset_mock()
        mock_callback.reset_mock()
        mock_accept.reset_mock()
        mock_reject.reset_mock()

        # Test with NO result and no callback
        self.dialog._result_callback = None
        self.dialog._finish_with_result(MessageResult.NO)
        mock_emit.assert_called_once_with(MessageResult.NO.value)
        mock_callback.assert_not_called()
        mock_accept.assert_not_called()
        mock_reject.assert_called_once()

        # Reset mocks
        mock_emit.reset_mock()
        mock_callback.reset_mock()
        mock_accept.reset_mock()
        mock_reject.reset_mock()

        # Test with CLOSE result (should also reject) and callback
        mock_callback = Mock()
        self.dialog._result_callback = mock_callback
        self.dialog._finish_with_result(MessageResult.CLOSE)
        mock_emit.assert_called_once_with(MessageResult.CLOSE.value)
        mock_callback.assert_called_once_with(MessageResult.CLOSE)
        mock_accept.assert_not_called()
        mock_reject.assert_called_once()

    # Test case for the accept method

    # Patch the base class method
    @patch('components.dialogs.base_dialog.FluentBaseDialog.close_animated')
    def test_accept(self, mock_close_animated):
        # Call accept
        self.dialog.accept()
        # Assert close_animated is called with Accepted code
        mock_close_animated.assert_called_once_with(
            QDialog.DialogCode.Accepted)

    # Test case for the reject method
    # Patch the base class method
    @patch('components.dialogs.base_dialog.FluentBaseDialog.close_animated')
    def test_reject(self, mock_close_animated):
        # Call reject
        self.dialog.reject()
        # Assert close_animated is called with Rejected code
        mock_close_animated.assert_called_once_with(
            QDialog.DialogCode.Rejected)

    # Test case for show_information_dialog convenience function
    @patch('components.dialogs.message_dialog.FluentMessageDialog')
    def test_show_information_dialog(self, mock_dialog_class):
        # Mock the dialog instance and its show_message method
        mock_dialog_instance = Mock()
        mock_dialog_class.return_value = mock_dialog_instance
        # Simulate dialog execution
        mock_dialog_instance.show_message.return_value = QDialog.DialogCode.Accepted

        # Define test parameters
        title = "Info Title"
        message = "Info Message"
        callback = Mock()

        # Call the convenience function
        dialog_returned = show_information_dialog(
            self.parent, title, message, callback)

        # Assert that FluentMessageDialog was instantiated with the parent
        mock_dialog_class.assert_called_once_with(self.parent)
        # Assert that show_message was called with correct arguments
        mock_dialog_instance.show_message.assert_called_once_with(
            title, message, MessageType.INFORMATION, callback
        )
        # Assert that the dialog instance is returned
        self.assertEqual(dialog_returned, mock_dialog_instance)

    # Test case for show_warning_dialog convenience function
    @patch('components.dialogs.message_dialog.FluentMessageDialog')
    def test_show_warning_dialog(self, mock_dialog_class):
        mock_dialog_instance = Mock()
        mock_dialog_class.return_value = mock_dialog_instance
        mock_dialog_instance.show_message.return_value = QDialog.DialogCode.Accepted

        title = "Warning Title"
        message = "Warning Message"
        callback = Mock()

        dialog_returned = show_warning_dialog(
            self.parent, title, message, callback)

        mock_dialog_class.assert_called_once_with(self.parent)
        mock_dialog_instance.show_message.assert_called_once_with(
            title, message, MessageType.WARNING, callback
        )
        self.assertEqual(dialog_returned, mock_dialog_instance)

    # Test case for show_error_dialog convenience function
    @patch('components.dialogs.message_dialog.FluentMessageDialog')
    def test_show_error_dialog(self, mock_dialog_class):
        mock_dialog_instance = Mock()
        mock_dialog_class.return_value = mock_dialog_instance
        mock_dialog_instance.show_message.return_value = QDialog.DialogCode.Accepted

        title = "Error Title"
        message = "Error Message"
        callback = Mock()

        dialog_returned = show_error_dialog(
            self.parent, title, message, callback)

        mock_dialog_class.assert_called_once_with(self.parent)
        mock_dialog_instance.show_message.assert_called_once_with(
            title, message, MessageType.ERROR, callback
        )
        self.assertEqual(dialog_returned, mock_dialog_instance)

    # Test case for show_question_dialog convenience function
    @patch('components.dialogs.message_dialog.FluentMessageDialog')
    def test_show_question_dialog(self, mock_dialog_class):
        mock_dialog_instance = Mock()
        mock_dialog_class.return_value = mock_dialog_instance
        mock_dialog_instance.show_message.return_value = QDialog.DialogCode.Accepted

        title = "Question Title"
        message = "Question Message"
        callback = Mock()

        dialog_returned = show_question_dialog(
            self.parent, title, message, callback)

        mock_dialog_class.assert_called_once_with(self.parent)
        mock_dialog_instance.show_message.assert_called_once_with(
            title, message, MessageType.QUESTION, callback
        )
        self.assertEqual(dialog_returned, mock_dialog_instance)

    # Test case for show_success_dialog convenience function
    @patch('components.dialogs.message_dialog.FluentMessageDialog')
    def test_show_success_dialog(self, mock_dialog_class):
        mock_dialog_instance = Mock()
        mock_dialog_class.return_value = mock_dialog_instance
        mock_dialog_instance.show_message.return_value = QDialog.DialogCode.Accepted

        title = "Success Title"
        message = "Success Message"
        callback = Mock()

        dialog_returned = show_success_dialog(
            self.parent, title, message, callback)

        mock_dialog_class.assert_called_once_with(self.parent)
        mock_dialog_instance.show_message.assert_called_once_with(
            title, message, MessageType.SUCCESS, callback
        )
        self.assertEqual(dialog_returned, mock_dialog_instance)


# Boilerplate to run the tests
if __name__ == '__main__':
    unittest.main()
