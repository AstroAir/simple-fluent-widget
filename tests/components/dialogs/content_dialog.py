import sys
import os
import pytest
from unittest.mock import Mock, patch, call
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QDialog
from PySide6.QtCore import Signal
from components.dialogs.content_dialog import FluentContentDialog, DialogType, DialogSize, ButtonRole, show_content_dialog
from components.dialogs.base_dialog import FluentBaseDialog

# filepath: d:\Project\simple-fluent-widget\tests\components\dialogs\test_content_dialog.py


# Add the project root directory to the path for relative import
# Assuming the test file is in tests/components/dialogs/
# and the source is in components/dialogs/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Import the classes, enums, and function to test
# Assuming FluentBaseDialog is in .base_dialog


@pytest.fixture(scope="session")
def app_fixture():
    """Provides a QApplication instance for the test session."""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()

@pytest.fixture(scope="function")
def content_dialog_fixture(app_fixture, request):
    """Provides a FluentContentDialog instance and a list to track widgets for cleanup."""
    # Create a parent widget for the dialog
    parent_widget = QWidget()
    # FluentContentDialog is a QDialog subclass
    dialog = FluentContentDialog(parent_widget)
    widgets_to_clean = [parent_widget, dialog] # Track widgets for cleanup

    def cleanup():
        """Cleans up widgets after each test."""
        for widget in widgets_to_clean:
             if widget and hasattr(widget, 'setParent'):
                 widget.setParent(None)
                 widget.deleteLater() # Schedule for deletion

        # Process events to allow deletion to occur
        QApplication.processEvents()

    request.addfinalizer(cleanup)

    return dialog, widgets_to_clean, parent_widget


class TestFluentContentDialog:
    """Unit tests for FluentContentDialog."""

    @patch('components.dialogs.content_dialog.FluentBaseDialog.__init__', return_value=None)
    @patch.object(FluentContentDialog, '_init_content')
    @patch.object(FluentContentDialog, '_init_buttons')
    def test_init(self, mock_init_buttons, mock_init_content, mock_base_init, content_dialog_fixture):
        """Test initialization."""
        dialog, widgets, parent_widget = content_dialog_fixture

        # Re-initialize to use mocks
        mock_base_init.reset_mock()
        mock_init_content.reset_mock()
        mock_init_buttons.reset_mock()

        # Test default parameters
        dialog.__init__(parent=parent_widget)
        mock_base_init.assert_called_once_with(dialog, parent_widget, DialogType.MODAL, DialogSize.MEDIUM)
        assert dialog._content == ""
        assert dialog._primary_button_text == "OK"
        assert dialog._secondary_button_text == "Cancel"
        assert dialog._primary_button_callback is None
        assert dialog._secondary_button_callback is None
        mock_init_content.assert_called_once()
        mock_init_buttons.assert_called_once()

        # Test custom parameters
        mock_base_init.reset_mock()
        mock_init_content.reset_mock()
        mock_init_buttons.reset_mock()
        mock_callback1 = Mock()
        mock_callback2 = Mock()

        dialog.__init__(parent=parent_widget, title="Test Title", content="Test Content")
        mock_base_init.assert_called_once_with(dialog, parent_widget, DialogType.MODAL, DialogSize.MEDIUM)
        assert dialog._content == "Test Content"
        assert dialog._primary_button_text == "OK" # Defaults still used
        assert dialog._secondary_button_text == "Cancel" # Defaults still used
        assert dialog._primary_button_callback is None
        assert dialog._secondary_button_callback is None
        mock_init_content.assert_called_once()
        mock_init_buttons.assert_called_once()

    @patch('components.dialogs.content_dialog.QLabel')
    @patch.object(FluentContentDialog, 'add_content_widget')
    def test__init_content(self, mock_add_content_widget, mock_qlabel_class, content_dialog_fixture):
        """Test _init_content creates and adds content label."""
        dialog, widgets, parent_widget = content_dialog_fixture
        mock_label = Mock(spec=QLabel)
        mock_qlabel_class.return_value = mock_label

        # Test with content
        dialog._content = "Some content text"
        mock_qlabel_class.reset_mock()
        mock_add_content_widget.reset_mock()
        dialog._init_content()
        mock_qlabel_class.assert_called_once_with("Some content text")
        mock_label.setObjectName.assert_called_once_with("contentLabel")
        mock_label.setWordWrap.assert_called_once_with(True)
        mock_add_content_widget.assert_called_once_with(mock_label)
        assert hasattr(dialog, 'content_label')
        assert dialog.content_label == mock_label

        # Test without content
        dialog._content = ""
        # Remove content_label if it exists from previous test
        if hasattr(dialog, 'content_label'): del dialog.content_label
        mock_qlabel_class.reset_mock()
        mock_add_content_widget.reset_mock()
        dialog._init_content()
        mock_qlabel_class.assert_not_called()
        mock_add_content_widget.assert_not_called()
        assert not hasattr(dialog, 'content_label')

    @patch.object(FluentContentDialog, 'add_button')
    def test__init_buttons(self, mock_add_button, content_dialog_fixture):
        """Test _init_buttons adds primary and secondary buttons."""
        dialog, widgets, parent_widget = content_dialog_fixture
        mock_secondary_button = Mock(spec=QPushButton)
        mock_primary_button = Mock(spec=QPushButton)
        mock_add_button.side_effect = [mock_secondary_button, mock_primary_button]

        dialog._primary_button_text = "Yes"
        dialog._secondary_button_text = "No"

        # Call the method directly
        mock_add_button.reset_mock()

        dialog._init_buttons()

        mock_add_button.assert_has_calls([
            call("No", ButtonRole.CANCEL, dialog._on_secondary_clicked),
            call("Yes", ButtonRole.PRIMARY, dialog._on_primary_clicked)
        ])
        assert mock_add_button.call_count == 2
        assert hasattr(dialog, 'secondary_button')
        assert dialog.secondary_button == mock_secondary_button
        assert hasattr(dialog, 'primary_button')
        assert dialog.primary_button == mock_primary_button

    @patch.object(FluentContentDialog, 'primary_button_clicked')
    @patch.object(FluentContentDialog, 'accept')
    def test__on_primary_clicked(self, mock_accept, mock_signal, content_dialog_fixture, mocker):
        """Test _on_primary_clicked emits signal, calls callback, and accepts."""
        dialog, widgets, parent_widget = content_dialog_fixture
        mock_signal.emit = Mock() # Mock the signal emit
        mock_callback = mocker.Mock()

        # Test with callback
        dialog._primary_button_callback = mock_callback
        mock_signal.emit.reset_mock()
        mock_callback.reset_mock()
        mock_accept.reset_mock()

        dialog._on_primary_clicked()

        mock_signal.emit.assert_called_once()
        mock_callback.assert_called_once()
        mock_accept.assert_called_once()

        # Test without callback
        dialog._primary_button_callback = None
        mock_signal.emit.reset_mock()
        mock_callback.reset_mock()
        mock_accept.reset_mock()

        dialog._on_primary_clicked()

        mock_signal.emit.assert_called_once()
        mock_callback.assert_not_called()
        mock_accept.assert_called_once()

    @patch.object(FluentContentDialog, 'secondary_button_clicked')
    @patch.object(FluentContentDialog, 'reject')
    def test__on_secondary_clicked(self, mock_reject, mock_signal, content_dialog_fixture, mocker):
        """Test _on_secondary_clicked emits signal, calls callback, and rejects."""
        dialog, widgets, parent_widget = content_dialog_fixture
        mock_signal.emit = Mock() # Mock the signal emit
        mock_callback = mocker.Mock()

        # Test with callback
        dialog._secondary_button_callback = mock_callback
        mock_signal.emit.reset_mock()
        mock_callback.reset_mock()
        mock_reject.reset_mock()

        dialog._on_secondary_clicked()

        mock_signal.emit.assert_called_once()
        mock_callback.assert_called_once()
        mock_reject.assert_called_once()

        # Test without callback
        dialog._secondary_button_callback = None
        mock_signal.emit.reset_mock()
        mock_callback.reset_mock()
        mock_reject.reset_mock()

        dialog._on_secondary_clicked()

        mock_signal.emit.assert_called_once()
        mock_callback.assert_not_called()
        mock_reject.assert_called_once()

    @patch.object(FluentContentDialog, 'close_animated')
    def test_accept(self, mock_close_animated, content_dialog_fixture):
        """Test accept calls close_animated with Accepted result."""
        dialog, widgets, parent_widget = content_dialog_fixture
        mock_close_animated.reset_mock()
        dialog.accept()
        mock_close_animated.assert_called_once_with(QDialog.DialogCode.Accepted)

    @patch.object(FluentContentDialog, 'close_animated')
    def test_reject(self, mock_close_animated, content_dialog_fixture):
        """Test reject calls close_animated with Rejected result."""
        dialog, widgets, parent_widget = content_dialog_fixture
        mock_close_animated.reset_mock()
        dialog.reject()
        mock_close_animated.assert_called_once_with(QDialog.DialogCode.Rejected)

    @patch('components.dialogs.content_dialog.QLabel')
    def test_set_content(self, mock_qlabel_class, content_dialog_fixture):
        """Test set_content updates content property and label text."""
        dialog, widgets, parent_widget = content_dialog_fixture
        mock_label = Mock(spec=QLabel)
        # Simulate content_label existing
        dialog.content_label = mock_label

        dialog.set_content("New Content")
        assert dialog._content == "New Content"
        mock_label.setText.assert_called_once_with("New Content")

        # Test setting content before content_label is created
        del dialog.content_label # Remove the mock label
        dialog.set_content("Another Content")
        assert dialog._content == "Another Content"
        # setText should not be called as content_label doesn't exist
        mock_label.setText.assert_called_once_with("New Content") # Still has old call count

    @patch('components.dialogs.content_dialog.QPushButton')
    def test_set_primary_button_text(self, mock_qpushbutton_class, content_dialog_fixture):
        """Test set_primary_button_text updates property and button text."""
        dialog, widgets, parent_widget = content_dialog_fixture
        mock_button = Mock(spec=QPushButton)
        # Simulate primary_button existing
        dialog.primary_button = mock_button

        dialog.set_primary_button_text("Save")
        assert dialog._primary_button_text == "Save"
        mock_button.setText.assert_called_once_with("Save")

        # Test setting text before primary_button is created
        del dialog.primary_button
        dialog.set_primary_button_text("Apply")
        assert dialog._primary_button_text == "Apply"
        mock_button.setText.assert_called_once_with("Save") # Still has old call count

    @patch('components.dialogs.content_dialog.QPushButton')
    def test_set_secondary_button_text(self, mock_qpushbutton_class, content_dialog_fixture):
        """Test set_secondary_button_text updates property and button text."""
        dialog, widgets, parent_widget = content_dialog_fixture
        mock_button = Mock(spec=QPushButton)
        # Simulate secondary_button existing
        dialog.secondary_button = mock_button

        dialog.set_secondary_button_text("Close")
        assert dialog._secondary_button_text == "Close"
        mock_button.setText.assert_called_once_with("Close")

        # Test setting text before secondary_button is created
        del dialog.secondary_button
        dialog.set_secondary_button_text("Dismiss")
        assert dialog._secondary_button_text == "Dismiss"
        mock_button.setText.assert_called_once_with("Close") # Still has old call count

    def test_set_primary_button_callback(self, content_dialog_fixture, mocker):
        """Test set_primary_button_callback sets the callback."""
        dialog, widgets, parent_widget = content_dialog_fixture
        mock_callback = mocker.Mock()
        dialog.set_primary_button_callback(mock_callback)
        assert dialog._primary_button_callback == mock_callback

    def test_set_secondary_button_callback(self, content_dialog_fixture, mocker):
        """Test set_secondary_button_callback sets the callback."""
        dialog, widgets, parent_widget = content_dialog_fixture
        mock_callback = mocker.Mock()
        dialog.set_secondary_button_callback(mock_callback)
        assert dialog._secondary_button_callback == mock_callback


class TestShowContentDialogFunction:
    """Unit tests for the show_content_dialog convenience function."""

    @patch('components.dialogs.content_dialog.FluentContentDialog')
    def test_show_content_dialog(self, mock_dialog_class, app_fixture, mocker):
        """Test show_content_dialog creates, configures, and shows the dialog."""
        mock_parent = Mock(spec=QWidget)
        mock_dialog_instance = Mock(spec=FluentContentDialog)
        mock_dialog_instance.set_primary_button_text = Mock()
        mock_dialog_instance.set_secondary_button_text = Mock()
        mock_dialog_instance.set_primary_button_callback = Mock()
        mock_dialog_instance.set_secondary_button_callback = Mock()
        mock_dialog_instance.show_animated = Mock()

        mock_dialog_class.return_value = mock_dialog_instance

        mock_primary_callback = mocker.Mock()
        mock_secondary_callback = mocker.Mock()

        # Call the function
        dialog = show_content_dialog(
            parent=mock_parent,
            title="Function Title",
            content="Function Content",
            primary_text="Yes",
            secondary_text="No",
            primary_callback=mock_primary_callback,
            secondary_callback=mock_secondary_callback
        )

        # Check if dialog was instantiated correctly
        mock_dialog_class.assert_called_once_with(
            mock_parent, "Function Title", "Function Content"
        )

        # Check if button texts were set
        mock_dialog_instance.set_primary_button_text.assert_called_once_with("Yes")
        mock_dialog_instance.set_secondary_button_text.assert_called_once_with("No")

        # Check if callbacks were set
        mock_dialog_instance.set_primary_button_callback.assert_called_once_with(mock_primary_callback)
        mock_dialog_instance.set_secondary_button_callback.assert_called_once_with(mock_secondary_callback)

        # Check if show_animated was called
        mock_dialog_instance.show_animated.assert_called_once()

        # Check if the dialog instance was returned
        assert dialog == mock_dialog_instance

        # Test without callbacks
        mock_dialog_class.reset_mock()
        mock_dialog_instance.set_primary_button_callback.reset_mock()
        mock_dialog_instance.set_secondary_button_callback.reset_mock()
        mock_dialog_class.return_value = mock_dialog_instance

        show_content_dialog(
            parent=mock_parent,
            title="No Callback Title",
            content="No Callback Content",
            primary_text="OK",
            secondary_text="Cancel",
            primary_callback=None,
            secondary_callback=None
        )
        mock_dialog_instance.set_primary_button_callback.assert_not_called()
        mock_dialog_instance.set_secondary_button_callback.assert_not_called()