import sys
import os
import pytest
from unittest.mock import Mock, patch, call
from abc import abstractmethod
from PySide6.QtGui import QPainter, QColor, QPaintEvent, QKeyEvent
from components.dialogs.base_dialog import FluentBaseDialog, DialogSize, DialogType, ButtonRole, FluentDialogBuilder
from core.theme import theme_manager

# filepath: d:\Project\simple-fluent-widget\tests\components\dialogs\test_base_dialog.py

from PySide6.QtWidgets import (QApplication, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFrame, QGraphicsOpacityEffect,
                               QGraphicsDropShadowEffect)
from PySide6.QtCore import (Qt, QEasingCurve, QPropertyAnimation, Signal,
                            QByteArray, QTimer, QSize, QRect, QPoint)

# Add the project root directory to the path for relative import
# Assuming the test file is in tests/components/dialogs/
# and the source is in components/dialogs/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Import the classes and enums to test
# Assuming FluentControlBase and FluentThemeAware are in ..base.fluent_control_base
# from components.base.fluent_control_base import FluentControlBase, FluentThemeAware
# Assuming theme_manager is in core.theme


# Create a concrete subclass for testing the abstract FluentBaseDialog
class ConcreteFluentBaseDialog(FluentBaseDialog):
    def accept(self):
        """Concrete implementation for testing."""
        self.done(QDialog.DialogCode.Accepted)

    def reject(self):
        """Concrete implementation for testing."""
        self.done(QDialog.DialogCode.Rejected)


@pytest.fixture(scope="session")
def app_fixture():
    """Provides a QApplication instance for the test session."""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()

@pytest.fixture(scope="function")
def base_dialog_fixture(app_fixture, request):
    """Provides a ConcreteFluentBaseDialog instance and a list to track widgets for cleanup."""
    # Create a parent widget for the dialog
    parent_widget = QWidget()
    # ConcreteFluentBaseDialog is a QDialog subclass
    dialog = ConcreteFluentBaseDialog(parent_widget)
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

@pytest.fixture(scope="function")
def dialog_builder_fixture(app_fixture, request):
    """Provides a FluentDialogBuilder instance."""
    # No widgets to clean up directly from the builder itself
    return FluentDialogBuilder()


class TestDialogEnums:
    """Unit tests for Dialog enums."""

    def test_dialog_size_values(self):
        """Test DialogSize enum values."""
        assert DialogSize.SMALL.value == (320, 200)
        assert DialogSize.MEDIUM.value == (480, 320)
        assert DialogSize.LARGE.value == (640, 480)
        assert DialogSize.EXTRA_LARGE.value == (800, 600)
        assert DialogSize.CUSTOM.value is None

    def test_dialog_type_values(self):
        """Test DialogType enum values."""
        assert DialogType.MODAL.value == "modal"
        assert DialogType.MODELESS.value == "modeless"
        assert DialogType.POPUP.value == "popup"
        assert DialogType.OVERLAY.value == "overlay"

    def test_button_role_values(self):
        """Test ButtonRole enum values."""
        assert ButtonRole.PRIMARY.value == "primary"
        assert ButtonRole.SECONDARY.value == "secondary"
        assert ButtonRole.DESTRUCTIVE.value == "destructive"
        assert ButtonRole.CANCEL.value == "cancel"
        assert ButtonRole.CLOSE.value == "close"


class TestFluentBaseDialog:
    """Unit tests for FluentBaseDialog (using ConcreteFluentBaseDialog)."""

    @patch('components.dialogs.base_dialog.QDialog.__init__', return_value=None)
    @patch('components.dialogs.base_dialog.FluentControlBase.__init__', return_value=None)
    @patch('components.dialogs.base_dialog.FluentThemeAware.__init__', return_value=None)
    @patch.object(ConcreteFluentBaseDialog, '_setup_dialog_properties')
    @patch.object(ConcreteFluentBaseDialog, '_create_layout')
    @patch.object(ConcreteFluentBaseDialog, '_setup_styling')
    @patch.object(ConcreteFluentBaseDialog, '_setup_animations')
    @patch.object(ConcreteFluentBaseDialog, '_setup_keyboard_handling')
    @patch.object(ConcreteFluentBaseDialog, 'apply_theme')
    @patch('components.dialogs.base_dialog.theme_manager')
    def test_init(self, mock_theme_manager, mock_apply_theme, mock_setup_keyboard, mock_setup_animations, mock_setup_styling, mock_create_layout, mock_setup_properties, mock_theme_aware_init, mock_control_base_init, mock_qdialog_init, base_dialog_fixture):
        """Test initialization."""
        dialog, widgets, parent_widget = base_dialog_fixture

        # Re-initialize to use mocks
        mock_qdialog_init.reset_mock()
        mock_control_base_init.reset_mock()
        mock_theme_aware_init.reset_mock()
        mock_setup_properties.reset_mock()
        mock_create_layout.reset_mock()
        mock_setup_styling.reset_mock()
        mock_setup_animations.reset_mock()
        mock_setup_keyboard.reset_mock()
        mock_apply_theme.reset_mock()
        mock_theme_manager.theme_changed.connect.reset_mock()

        # Test default parameters
        dialog.__init__(parent=parent_widget)
        mock_qdialog_init.assert_called_once_with(dialog, parent_widget) # QDialog takes self as first arg
        mock_control_base_init.assert_called_once_with(dialog) # Base classes take self as first arg
        mock_theme_aware_init.assert_called_once_with(dialog)
        assert dialog._title == ""
        assert dialog._dialog_type == DialogType.MODAL
        assert dialog._size_preset == DialogSize.MEDIUM
        assert dialog._custom_size is None
        assert dialog._content_widgets == []
        assert dialog._buttons == {}
        assert dialog._button_layout is None # Created in _create_layout
        assert dialog._entrance_animation is None # Created in _setup_animations
        assert dialog._exit_animation is None # Created in _setup_animations
        assert dialog._is_animating is False
        assert dialog._escape_closes is True
        assert dialog._enter_accepts is True
        assert dialog._focus_chain == []

        mock_setup_properties.assert_called_once()
        mock_create_layout.assert_called_once()
        mock_setup_styling.assert_called_once()
        mock_setup_animations.assert_called_once()
        mock_setup_keyboard.assert_called_once()
        mock_apply_theme.assert_called_once()
        mock_theme_manager.theme_changed.connect.assert_called_once_with(dialog.apply_theme)

        # Test custom parameters
        mock_qdialog_init.reset_mock()
        mock_control_base_init.reset_mock()
        mock_theme_aware_init.reset_mock()
        mock_setup_properties.reset_mock()
        mock_create_layout.reset_mock()
        mock_setup_styling.reset_mock()
        mock_setup_animations.reset_mock()
        mock_setup_keyboard.reset_mock()
        mock_apply_theme.reset_mock()
        mock_theme_manager.theme_changed.connect.reset_mock()

        dialog.__init__(parent=parent_widget, title="Test Title", dialog_type=DialogType.POPUP, size_preset=DialogSize.LARGE)
        mock_qdialog_init.assert_called_once_with(dialog, parent_widget)
        mock_control_base_init.assert_called_once_with(dialog)
        mock_theme_aware_init.assert_called_once_with(dialog)
        assert dialog._title == "Test Title"
        assert dialog._dialog_type == DialogType.POPUP
        assert dialog._size_preset == DialogSize.LARGE
        assert dialog._custom_size is None

        # Test theme_manager connection handling
        with patch('components.dialogs.base_dialog.theme_manager', None):
             mock_qdialog_init.reset_mock()
             mock_control_base_init.reset_mock()
             mock_theme_aware_init.reset_mock()
             mock_setup_properties.reset_mock()
             mock_create_layout.reset_mock()
             mock_setup_styling.reset_mock()
             mock_setup_animations.reset_mock()
             mock_setup_keyboard.reset_mock()
             mock_apply_theme.reset_mock()
             # No theme_changed attribute on None, should not raise error
             dialog.__init__(parent=parent_widget)
             mock_apply_theme.assert_called_once() # apply_theme is still called

    @patch.object(ConcreteFluentBaseDialog, 'setWindowFlags')
    @patch.object(ConcreteFluentBaseDialog, 'setAttribute')
    @patch.object(ConcreteFluentBaseDialog, 'setModal')
    @patch.object(ConcreteFluentBaseDialog, 'setMinimumSize')
    @patch.object(ConcreteFluentBaseDialog, 'resize')
    def test__setup_dialog_properties(self, mock_resize, mock_set_min_size, mock_set_modal, mock_set_attribute, mock_set_window_flags, base_dialog_fixture):
        """Test _setup_dialog_properties sets window flags, attributes, and size."""
        dialog, widgets, parent_widget = base_dialog_fixture

        # Test MODAL dialog
        dialog._dialog_type = DialogType.MODAL
        dialog._size_preset = DialogSize.MEDIUM
        mock_set_window_flags.reset_mock()
        mock_set_attribute.reset_mock()
        mock_set_modal.reset_mock()
        mock_set_min_size.reset_mock()
        mock_resize.reset_mock()

        dialog._setup_dialog_properties()
        expected_flags = Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        mock_set_window_flags.assert_called_once_with(expected_flags)
        mock_set_attribute.assert_called_once_with(Qt.WidgetAttribute.WA_TranslucentBackground)
        mock_set_modal.assert_called_once_with(True)
        mock_set_min_size.assert_called_once_with(480, 320)
        mock_resize.assert_called_once_with(480, 320)

        # Test POPUP dialog
        dialog._dialog_type = DialogType.POPUP
        dialog._size_preset = DialogSize.SMALL
        mock_set_window_flags.reset_mock()
        mock_set_attribute.reset_mock()
        mock_set_modal.reset_mock()
        mock_set_min_size.reset_mock()
        mock_resize.reset_mock()

        dialog._setup_dialog_properties()
        expected_flags = Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        mock_set_window_flags.assert_called_once_with(expected_flags)
        mock_set_attribute.assert_called_once_with(Qt.WidgetAttribute.WA_TranslucentBackground)
        mock_set_modal.assert_called_once_with(False)
        mock_set_min_size.assert_called_once_with(320, 200)
        mock_resize.assert_called_once_with(320, 200)

        # Test OVERLAY dialog
        dialog._dialog_type = DialogType.OVERLAY
        dialog._size_preset = DialogSize.LARGE
        mock_set_window_flags.reset_mock()
        mock_set_attribute.reset_mock()
        mock_set_modal.reset_mock()
        mock_set_min_size.reset_mock()
        mock_resize.reset_mock()

        dialog._setup_dialog_properties()
        expected_flags = Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip
        mock_set_window_flags.assert_called_once_with(expected_flags)
        mock_set_attribute.assert_called_once_with(Qt.WidgetAttribute.WA_TranslucentBackground)
        mock_set_modal.assert_called_once_with(True)
        mock_set_min_size.assert_called_once_with(640, 480)
        mock_resize.assert_called_once_with(640, 480)

        # Test MODELESS dialog (no extra flags except Dialog)
        dialog._dialog_type = DialogType.MODELESS
        dialog._size_preset = DialogSize.EXTRA_LARGE
        mock_set_window_flags.reset_mock()
        mock_set_attribute.reset_mock()
        mock_set_modal.reset_mock()
        mock_set_min_size.reset_mock()
        mock_resize.reset_mock()

        dialog._setup_dialog_properties()
        expected_flags = Qt.WindowType.Dialog
        mock_set_window_flags.assert_called_once_with(expected_flags)
        mock_set_attribute.assert_called_once_with(Qt.WidgetAttribute.WA_TranslucentBackground)
        mock_set_modal.assert_called_once_with(False) # Default for QDialog
        mock_set_min_size.assert_called_once_with(800, 600)
        mock_resize.assert_called_once_with(800, 600)

        # Test CUSTOM size
        dialog._size_preset = DialogSize.CUSTOM
        dialog._custom_size = QSize(100, 100) # Should not happen in _setup, but test logic
        mock_set_window_flags.reset_mock()
        mock_set_attribute.reset_mock()
        mock_set_modal.reset_mock()
        mock_set_min_size.reset_mock()
        mock_resize.reset_mock()

        dialog._setup_dialog_properties()
        mock_set_min_size.assert_not_called() # Size is not set from preset if CUSTOM
        mock_resize.assert_not_called()

    @patch('components.dialogs.base_dialog.QVBoxLayout')
    @patch('components.dialogs.base_dialog.QFrame')
    @patch('components.dialogs.base_dialog.QGraphicsDropShadowEffect')
    @patch.object(ConcreteFluentBaseDialog, '_create_title_section')
    @patch.object(ConcreteFluentBaseDialog, '_create_button_section')
    def test__create_layout(self, mock_create_button_section, mock_create_title_section, mock_shadow_effect_class, mock_qframe_class, mock_qvboxlayout_class, base_dialog_fixture):
        """Test _create_layout sets up the main layout structure."""
        dialog, widgets, parent_widget = base_dialog_fixture

        mock_main_layout = Mock(spec=QVBoxLayout)
        mock_container_layout = Mock(spec=QVBoxLayout)
        mock_content_layout = Mock(spec=QVBoxLayout)
        mock_qvboxlayout_class.side_effect = [mock_main_layout, mock_container_layout, mock_content_layout]

        mock_content_container = Mock(spec=QFrame)
        mock_content_area = Mock(spec=QFrame)
        mock_qframe_class.side_effect = [mock_content_container, mock_content_area]

        mock_shadow_effect = Mock(spec=QGraphicsDropShadowEffect)
        mock_shadow_effect_class.return_value = mock_shadow_effect

        # Call the method directly
        mock_qvboxlayout_class.reset_mock()
        mock_qframe_class.reset_mock()
        mock_shadow_effect_class.reset_mock()
        mock_create_title_section.reset_mock()
        mock_create_button_section.reset_mock()

        dialog._create_layout()

        # Check main layout setup
        mock_qvboxlayout_class.assert_any_call(dialog)
        mock_main_layout.setContentsMargins.assert_called_once_with(20, 20, 20, 20)
        mock_main_layout.addWidget.assert_called_once_with(mock_content_container)
        assert dialog.layout() == mock_main_layout # Check dialog's layout is set

        # Check content container setup
        mock_qframe_class.assert_any_call()
        mock_content_container.setObjectName.assert_called_once_with("dialogContainer")
        mock_content_container.setFrameStyle.assert_called_once_with(QFrame.Shape.NoFrame)
        mock_shadow_effect_class.assert_called_once()
        mock_shadow_effect.setBlurRadius.assert_called_once_with(20)
        mock_shadow_effect.setColor.assert_called_once() # Cannot easily check QColor content
        mock_shadow_effect.setOffset.assert_called_once_with(0, 8)
        mock_content_container.setGraphicsEffect.assert_called_once_with(mock_shadow_effect)
        assert dialog.content_container == mock_content_container
        assert dialog.shadow_effect == mock_shadow_effect

        # Check container layout setup
        mock_qvboxlayout_class.assert_any_call(mock_content_container)
        mock_container_layout.setContentsMargins.assert_called_once_with(24, 24, 24, 24)
        mock_container_layout.setSpacing.assert_called_once_with(16)
        assert dialog.container_layout == mock_container_layout

        # Check title section creation
        mock_create_title_section.assert_called_once()

        # Check content area setup
        mock_qframe_class.assert_any_call()
        mock_content_area.setObjectName.assert_called_once_with("contentArea")
        mock_qvboxlayout_class.assert_any_call(mock_content_area)
        mock_content_layout.setContentsMargins.assert_called_once_with(0, 0, 0, 0)
        mock_content_layout.setSpacing.assert_called_once_with(12)
        mock_container_layout.addWidget.assert_any_call(mock_content_area, 1) # Added with stretch 1
        assert dialog.content_area == mock_content_area
        assert dialog.content_layout == mock_content_layout

        # Check button section creation
        mock_create_button_section.assert_called_once()

    @patch('components.dialogs.base_dialog.QLabel')
    def test__create_title_section(self, mock_qlabel_class, base_dialog_fixture):
        """Test _create_title_section creates title label if title is set."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_label = Mock(spec=QLabel)
        mock_qlabel_class.return_value = mock_label

        # Ensure container_layout exists
        dialog.container_layout = Mock(spec=QVBoxLayout)

        # Test with title
        dialog._title = "My Dialog Title"
        mock_qlabel_class.reset_mock()
        dialog.container_layout.addWidget.reset_mock()
        dialog._create_title_section()
        mock_qlabel_class.assert_called_once_with("My Dialog Title")
        mock_label.setObjectName.assert_called_once_with("dialogTitle")
        dialog.container_layout.addWidget.assert_called_once_with(mock_label)
        assert hasattr(dialog, 'title_label')
        assert dialog.title_label == mock_label

        # Test without title
        dialog._title = ""
        # Remove title_label if it exists from previous test
        if hasattr(dialog, 'title_label'): del dialog.title_label
        mock_qlabel_class.reset_mock()
        dialog.container_layout.addWidget.reset_mock()
        dialog._create_title_section()
        mock_qlabel_class.assert_not_called()
        dialog.container_layout.addWidget.assert_not_called()
        assert not hasattr(dialog, 'title_label')

    @patch('components.dialogs.base_dialog.QFrame')
    @patch('components.dialogs.base_dialog.QHBoxLayout')
    def test__create_button_section(self, mock_qhboxlayout_class, mock_qframe_class, base_dialog_fixture):
        """Test _create_button_section creates button container and layout."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_button_container = Mock(spec=QFrame)
        mock_qframe_class.return_value = mock_button_container
        mock_button_layout = Mock(spec=QHBoxLayout)
        mock_qhboxlayout_class.return_value = mock_button_layout

        # Ensure container_layout exists
        dialog.container_layout = Mock(spec=QVBoxLayout)

        # Call the method directly
        mock_qframe_class.reset_mock()
        mock_qhboxlayout_class.reset_mock()
        dialog.container_layout.addWidget.reset_mock()

        dialog._create_button_section()

        mock_qframe_class.assert_called_once()
        mock_button_container.setObjectName.assert_called_once_with("buttonContainer")
        assert dialog.button_container == mock_button_container

        mock_qhboxlayout_class.assert_called_once_with(mock_button_container)
        mock_button_layout.setContentsMargins.assert_called_once_with(0, 16, 0, 0)
        mock_button_layout.setSpacing.assert_called_once_with(12)
        mock_button_layout.addStretch.assert_called_once()
        assert dialog._button_layout == mock_button_layout

        dialog.container_layout.addWidget.assert_called_once_with(mock_button_container)

    @patch.object(ConcreteFluentBaseDialog, 'setStyleSheet')
    def test__setup_styling(self, mock_set_style_sheet, base_dialog_fixture):
        """Test _setup_styling sets the stylesheet."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_set_style_sheet.reset_mock()

        dialog._setup_styling()

        mock_set_style_sheet.assert_called_once()
        # Cannot easily check the exact stylesheet content in a unit test

    @patch('components.dialogs.base_dialog.QGraphicsOpacityEffect')
    @patch('components.dialogs.base_dialog.QPropertyAnimation')
    def test__setup_animations(self, mock_animation_class, mock_opacity_effect_class, base_dialog_fixture):
        """Test _setup_animations sets up opacity effect and animations."""
        dialog, widgets, parent_widget = base_dialog_fixture

        mock_opacity_effect = Mock(spec=QGraphicsOpacityEffect)
        mock_opacity_effect_class.return_value = mock_opacity_effect

        mock_entrance_anim = Mock(spec=QPropertyAnimation)
        mock_entrance_anim.finished = Mock(spec=Qt.Signal)
        mock_exit_anim = Mock(spec=QPropertyAnimation)
        mock_exit_anim.finished = Mock(spec=Qt.Signal)
        mock_animation_class.side_effect = [mock_entrance_anim, mock_exit_anim]

        # Call the method directly
        mock_opacity_effect_class.reset_mock()
        mock_animation_class.reset_mock()
        dialog.setGraphicsEffect = Mock() # Mock the setGraphicsEffect call

        dialog._setup_animations()

        mock_opacity_effect_class.assert_called_once()
        dialog.setGraphicsEffect.assert_called_once_with(mock_opacity_effect)
        assert dialog.opacity_effect == mock_opacity_effect

        # Check entrance animation setup
        mock_animation_class.assert_any_call(mock_opacity_effect, QByteArray(b"opacity"))
        mock_entrance_anim.setDuration.assert_called_once_with(250)
        mock_entrance_anim.setEasingCurve.assert_called_once_with(QEasingCurve.Type.OutCubic)
        mock_entrance_anim.finished.connect.assert_called_once_with(dialog._on_entrance_finished)
        assert dialog._entrance_animation == mock_entrance_anim

        # Check exit animation setup
        mock_animation_class.assert_any_call(mock_opacity_effect, QByteArray(b"opacity"))
        mock_exit_anim.setDuration.assert_called_once_with(200)
        mock_exit_anim.setEasingCurve.assert_called_once_with(QEasingCurve.Type.OutCubic)
        mock_exit_anim.finished.connect.assert_called_once_with(dialog._on_exit_finished)
        assert dialog._exit_animation == mock_exit_anim

    @patch.object(ConcreteFluentBaseDialog, 'setFocusPolicy')
    def test__setup_keyboard_handling(self, mock_set_focus_policy, base_dialog_fixture):
        """Test _setup_keyboard_handling sets focus policy."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_set_focus_policy.reset_mock()

        dialog._setup_keyboard_handling()

        mock_set_focus_policy.assert_called_once_with(Qt.FocusPolicy.StrongFocus)

    @patch.object(QVBoxLayout, 'addWidget')
    def test_add_content_widget(self, mock_add_widget, base_dialog_fixture, mocker):
        """Test add_content_widget adds widget and emits signal."""
        dialog, widgets, parent_widget = base_dialog_fixture
        widget = Mock(spec=QWidget)
        mock_signal_emit = mocker.Mock()
        dialog.content_changed.emit = mock_signal_emit

        # Ensure content_layout exists
        dialog.content_layout = Mock(spec=QVBoxLayout)
        dialog.content_layout.addWidget = mock_add_widget

        dialog.add_content_widget(widget, stretch=5)

        assert widget in dialog._content_widgets
        mock_add_widget.assert_called_once_with(widget, 5)
        mock_signal_emit.assert_called_once()

    @patch.object(QVBoxLayout, 'insertWidget')
    def test_insert_content_widget(self, mock_insert_widget, base_dialog_fixture, mocker):
        """Test insert_content_widget inserts widget and emits signal."""
        dialog, widgets, parent_widget = base_dialog_fixture
        widget1 = Mock(spec=QWidget)
        widget2 = Mock(spec=QWidget)
        mock_signal_emit = mocker.Mock()
        dialog.content_changed.emit = mock_signal_emit

        # Ensure content_layout exists
        dialog.content_layout = Mock(spec=QVBoxLayout)
        dialog.content_layout.insertWidget = mock_insert_widget

        dialog._content_widgets = [widget1] # Add initial widget

        dialog.insert_content_widget(0, widget2)

        assert dialog._content_widgets == [widget2, widget1]
        mock_insert_widget.assert_called_once_with(0, widget2)
        mock_signal_emit.assert_called_once()

    @patch.object(QVBoxLayout, 'removeWidget')
    def test_remove_content_widget(self, mock_remove_widget, base_dialog_fixture, mocker):
        """Test remove_content_widget removes widget and emits signal."""
        dialog, widgets, parent_widget = base_dialog_fixture
        widget1 = Mock(spec=QWidget)
        widget2 = Mock(spec=QWidget)
        mock_signal_emit = mocker.Mock()
        dialog.content_changed.emit = mock_signal_emit

        # Ensure content_layout exists
        dialog.content_layout = Mock(spec=QVBoxLayout)
        dialog.content_layout.removeWidget = mock_remove_widget

        dialog._content_widgets = [widget1, widget2] # Add initial widgets

        widget1.setParent = Mock() # Mock setParent for removal

        dialog.remove_content_widget(widget1)

        assert widget1 not in dialog._content_widgets
        assert widget2 in dialog._content_widgets
        mock_remove_widget.assert_called_once_with(widget1)
        widget1.setParent.assert_called_once_with(None)
        mock_signal_emit.assert_called_once()

        # Test removing non-existent widget
        mock_remove_widget.reset_mock()
        widget1.setParent.reset_mock()
        mock_signal_emit.reset_mock()
        widget3 = Mock(spec=QWidget)
        dialog.remove_content_widget(widget3)
        assert widget3 not in dialog._content_widgets # Was never there
        assert len(dialog._content_widgets) == 1 # Count remains 1
        mock_remove_widget.assert_not_called() # Layout method not called
        widget3.setParent.assert_not_called()
        mock_signal_emit.assert_not_called()

    @patch('components.dialogs.base_dialog.QPushButton')
    @patch.object(QHBoxLayout, 'addWidget')
    @patch.object(QHBoxLayout, 'insertWidget')
    def test_add_button(self, mock_insert_widget, mock_add_widget, mock_qpushbutton_class, base_dialog_fixture, mocker):
        """Test add_button creates button, connects signals, and adds to layout."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_button = Mock(spec=QPushButton)
        mock_button.clicked = Mock(spec=Qt.Signal) # Mock the clicked signal
        mock_qpushbutton_class.return_value = mock_button

        # Ensure button_layout exists
        dialog._button_layout = Mock(spec=QHBoxLayout)
        dialog._button_layout.addWidget = mock_add_widget
        dialog._button_layout.insertWidget = mock_insert_widget

        mock_button_clicked_signal_emit = mocker.Mock()
        dialog.button_clicked.emit = mock_button_clicked_signal_emit

        mock_callback = mocker.Mock()

        # Test adding a PRIMARY button
        mock_qpushbutton_class.reset_mock()
        mock_add_widget.reset_mock()
        mock_insert_widget.reset_mock()
        mock_button_clicked_signal_emit.reset_mock()
        mock_callback.reset_mock()

        button_primary = dialog.add_button("OK", ButtonRole.PRIMARY, callback=mock_callback, enabled=False)

        mock_qpushbutton_class.assert_called_once_with("OK")
        mock_button.setProperty.assert_called_once_with("role", "primary")
        mock_button.setEnabled.assert_called_once_with(False)
        mock_button.clicked.connect.assert_any_call(mock_callback) # Connect callback
        mock_button.clicked.connect.assert_any_call(mocker.ANY) # Connect lambda for button_clicked signal
        mock_add_widget.assert_called_once_with(mock_button) # Primary added at the end
        mock_insert_widget.assert_not_called()
        assert "primary" in dialog._buttons
        assert dialog._buttons["primary"] == mock_button
        assert button_primary == mock_button

        # Simulate button click to check button_clicked signal
        mock_button.clicked.emit()
        mock_button_clicked_signal_emit.assert_called_once_with("primary", mock_button)

        # Test adding a CANCEL button
        mock_qpushbutton_class.reset_mock()
        mock_add_widget.reset_mock()
        mock_insert_widget.reset_mock()
        mock_button_clicked_signal_emit.reset_mock()
        mock_callback.reset_mock() # Reset callback mock if needed

        button_cancel = dialog.add_button("Cancel", ButtonRole.CANCEL)

        mock_qpushbutton_class.assert_called_once_with("Cancel")
        mock_button.setProperty.assert_called_once_with("role", "cancel")
        mock_button.setEnabled.assert_called_once_with(True) # Default enabled
        # No callback provided, so only lambda connected
        mock_button.clicked.connect.assert_called_once_with(mocker.ANY)
        mock_add_widget.assert_not_called()
        mock_insert_widget.assert_called_once_with(0, mock_button) # Cancel inserted at index 0
        assert "cancel" in dialog._buttons
        assert dialog._buttons["cancel"] == mock_button
        assert button_cancel == mock_button

        # Simulate button click
        mock_button.clicked.emit()
        mock_button_clicked_signal_emit.assert_called_once_with("cancel", mock_button)

        # Test adding a SECONDARY button
        mock_qpushbutton_class.reset_mock()
        mock_add_widget.reset_mock()
        mock_insert_widget.reset_mock()
        mock_button_clicked_signal_emit.reset_mock()

        button_secondary = dialog.add_button("More", ButtonRole.SECONDARY)
        mock_add_widget.assert_called_once_with(mock_button) # Secondary added at the end
        mock_insert_widget.assert_not_called()
        assert "secondary" in dialog._buttons

    def test_get_button(self, base_dialog_fixture):
        """Test get_button returns button by role."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_primary_button = Mock(spec=QPushButton)
        mock_cancel_button = Mock(spec=QPushButton)
        dialog._buttons = {
            "primary": mock_primary_button,
            "cancel": mock_cancel_button
        }

        assert dialog.get_button(ButtonRole.PRIMARY) == mock_primary_button
        assert dialog.get_button(ButtonRole.CANCEL) == mock_cancel_button
        assert dialog.get_button(ButtonRole.SECONDARY) is None # Button not added

    def test_set_button_enabled(self, base_dialog_fixture):
        """Test set_button_enabled enables/disables button."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_primary_button = Mock(spec=QPushButton)
        mock_cancel_button = Mock(spec=QPushButton)
        dialog._buttons = {
            "primary": mock_primary_button,
            "cancel": mock_cancel_button
        }

        # Test enabling primary button
        mock_primary_button.setEnabled.reset_mock()
        dialog.set_button_enabled(ButtonRole.PRIMARY, True)
        mock_primary_button.setEnabled.assert_called_once_with(True)

        # Test disabling cancel button
        mock_cancel_button.setEnabled.reset_mock()
        dialog.set_button_enabled(ButtonRole.CANCEL, False)
        mock_cancel_button.setEnabled.assert_called_once_with(False)

        # Test setting enabled state for non-existent button
        dialog.set_button_enabled(ButtonRole.SECONDARY, True) # Should not raise error

    @patch('components.dialogs.base_dialog.QLabel')
    def test_set_title(self, mock_qlabel_class, base_dialog_fixture):
        """Test set_title updates title property and label."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_label = Mock(spec=QLabel)
        # Simulate title_label existing
        dialog.title_label = mock_label

        dialog.set_title("New Title")
        assert dialog._title == "New Title"
        mock_label.setText.assert_called_once_with("New Title")

        # Test setting title before title_label is created
        del dialog.title_label # Remove the mock label
        dialog.set_title("Another Title")
        assert dialog._title == "Another Title"
        # setText should not be called as title_label doesn't exist
        mock_label.setText.assert_called_once_with("New Title") # Still has old call count

    @patch.object(ConcreteFluentBaseDialog, 'resize')
    @patch.object(ConcreteFluentBaseDialog, 'size_changed')
    def test_set_custom_size(self, mock_size_changed_signal, mock_resize, base_dialog_fixture):
        """Test set_custom_size updates size properties and emits signal."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_size_changed_signal.emit = Mock() # Mock the signal emit

        dialog.set_custom_size(500, 400)

        assert dialog._size_preset == DialogSize.CUSTOM
        assert dialog._custom_size == QSize(500, 400)
        mock_resize.assert_called_once_with(500, 400)
        mock_size_changed_signal.emit.assert_called_once_with(QSize(500, 400))

    @patch.object(ConcreteFluentBaseDialog, 'show')
    @patch.object(ConcreteFluentBaseDialog, '_center_on_parent')
    @patch.object(QPropertyAnimation, 'start')
    @patch.object(QGraphicsOpacityEffect, 'setOpacity')
    @patch.object(ConcreteFluentBaseDialog, 'dialog_opened')
    def test_show_animated(self, mock_dialog_opened_signal, mock_set_opacity, mock_anim_start, mock_center_on_parent, mock_show, base_dialog_fixture):
        """Test show_animated shows dialog, centers, and starts animation."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_dialog_opened_signal.emit = Mock() # Mock the signal emit

        # Ensure animation objects exist
        dialog.opacity_effect = Mock(spec=QGraphicsOpacityEffect)
        dialog._entrance_animation = Mock(spec=QPropertyAnimation)

        # Test when not animating
        dialog._is_animating = False
        mock_show.reset_mock()
        mock_center_on_parent.reset_mock()
        mock_set_opacity.reset_mock()
        mock_anim_start.reset_mock()
        mock_dialog_opened_signal.emit.reset_mock()

        dialog.show_animated()

        assert dialog._is_animating is True
        mock_show.assert_called_once()
        mock_center_on_parent.assert_called_once()
        mock_set_opacity.assert_called_once_with(0.0)
        dialog._entrance_animation.setStartValue.assert_called_once_with(0.0)
        dialog._entrance_animation.setEndValue.assert_called_once_with(1.0)
        mock_anim_start.assert_called_once()
        mock_dialog_opened_signal.emit.assert_called_once()

        # Test when already animating
        mock_show.reset_mock()
        mock_center_on_parent.reset_mock()
        mock_set_opacity.reset_mock()
        mock_anim_start.reset_mock()
        mock_dialog_opened_signal.emit.reset_mock()

        dialog.show_animated() # Call again while _is_animating is True

        mock_show.assert_not_called()
        mock_center_on_parent.assert_not_called()
        mock_set_opacity.assert_not_called()
        mock_anim_start.assert_not_called()
        mock_dialog_opened_signal.emit.assert_not_called()

        # Test when animation objects are None (e.g., _setup_animations not called)
        dialog._is_animating = False # Reset state
        dialog.opacity_effect = None
        dialog._entrance_animation = None
        mock_show.reset_mock()
        mock_center_on_parent.reset_mock()
        mock_set_opacity.reset_mock()
        mock_anim_start.reset_mock()
        mock_dialog_opened_signal.emit.reset_mock()

        dialog.show_animated()
        assert dialog._is_animating is True # Still sets animating flag
        mock_show.assert_called_once()
        mock_center_on_parent.assert_called_once()
        mock_set_opacity.assert_not_called() # No effect to set opacity on
        mock_anim_start.assert_not_called() # No animation to start
        mock_dialog_opened_signal.emit.assert_called_once()


    @patch.object(QPropertyAnimation, 'start')
    @patch.object(ConcreteFluentBaseDialog, '_on_exit_finished')
    def test_close_animated(self, mock_on_exit_finished, mock_anim_start, base_dialog_fixture):
        """Test close_animated starts exit animation or calls finish directly."""
        dialog, widgets, parent_widget = base_dialog_fixture

        # Ensure exit animation object exists
        dialog._exit_animation = Mock(spec=QPropertyAnimation)

        # Test when not animating
        dialog._is_animating = False
        mock_anim_start.reset_mock()
        mock_on_exit_finished.reset_mock()

        dialog.close_animated(QDialog.DialogCode.Accepted)

        assert dialog._is_animating is True
        assert dialog._exit_result == QDialog.DialogCode.Accepted
        dialog._exit_animation.setStartValue.assert_called_once_with(1.0)
        dialog._exit_animation.setEndValue.assert_called_once_with(0.0)
        mock_anim_start.assert_called_once()
        mock_on_exit_finished.assert_not_called() # Should be called by animation finished signal

        # Test when already animating
        mock_anim_start.reset_mock()
        mock_on_exit_finished.reset_mock()
        dialog.close_animated(QDialog.DialogCode.Rejected) # Call again while _is_animating is True
        mock_anim_start.assert_not_called()
        mock_on_exit_finished.assert_not_called()

        # Test when exit animation object is None
        dialog._is_animating = False # Reset state
        dialog._exit_animation = None
        mock_anim_start.reset_mock()
        mock_on_exit_finished.reset_mock()

        dialog.close_animated(QDialog.DialogCode.Accepted)
        assert dialog._is_animating is True # Still sets animating flag
        assert dialog._exit_result == QDialog.DialogCode.Accepted
        mock_anim_start.assert_not_called()
        mock_on_exit_finished.assert_called_once() # Should call finish directly

    @patch.object(ConcreteFluentBaseDialog, 'parent', return_value=Mock(spec=QWidget))
    @patch.object(QWidget, 'geometry', return_value=QRect(100, 100, 800, 600)) # Parent geometry
    @patch.object(ConcreteFluentBaseDialog, 'width', return_value=400) # Dialog width
    @patch.object(ConcreteFluentBaseDialog, 'height', return_value=300) # Dialog height
    @patch.object(ConcreteFluentBaseDialog, 'move')
    def test__center_on_parent(self, mock_move, mock_dialog_height, mock_dialog_width, mock_parent_geometry, mock_parent_method, base_dialog_fixture):
        """Test _center_on_parent centers the dialog."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_parent = mock_parent_method.return_value # Get the mocked parent widget

        # Test with a parent widget
        mock_move.reset_mock()
        dialog._center_on_parent()
        # Parent center: (100 + 800/2, 100 + 600/2) = (500, 400)
        # Dialog position: (500 - 400/2, 400 - 300/2) = (500 - 200, 400 - 150) = (300, 250)
        mock_move.assert_called_once_with(300, 250)

        # Test without a parent widget
        mock_parent_method.return_value = None # No parent
        mock_move.reset_mock()
        dialog._center_on_parent()
        mock_move.assert_not_called() # Should not move if no parent

        # Test with a non-QWidget parent (e.g., QObject)
        mock_parent_method.return_value = Mock(spec=QObject) # Not a QWidget
        mock_move.reset_mock()
        dialog._center_on_parent()
        mock_move.assert_not_called() # Should not move if parent is not QWidget

    def test__on_entrance_finished(self, base_dialog_fixture):
        """Test _on_entrance_finished resets animating flag."""
        dialog, widgets, parent_widget = base_dialog_fixture
        dialog._is_animating = True
        dialog._on_entrance_finished()
        assert dialog._is_animating is False

    @patch.object(ConcreteFluentBaseDialog, 'dialog_closed')
    @patch.object(ConcreteFluentBaseDialog, 'done')
    def test__on_exit_finished(self, mock_done, mock_dialog_closed_signal, base_dialog_fixture):
        """Test _on_exit_finished resets animating flag, emits signal, and calls done."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_dialog_closed_signal.emit = Mock() # Mock the signal emit

        dialog._is_animating = True
        dialog._exit_result = QDialog.DialogCode.Accepted # Simulate result set by close_animated

        dialog._on_exit_finished()

        assert dialog._is_animating is False
        mock_dialog_closed_signal.emit.assert_called_once_with(QDialog.DialogCode.Accepted)
        mock_done.assert_called_once_with(QDialog.DialogCode.Accepted)

        # Test with default result if _exit_result is not set
        dialog._is_animating = True
        if hasattr(dialog, '_exit_result'): del dialog._exit_result # Remove attribute
        mock_dialog_closed_signal.emit.reset_mock()
        mock_done.reset_mock()

        dialog._on_exit_finished()
        assert dialog._is_animating is False
        mock_dialog_closed_signal.emit.assert_called_once_with(QDialog.DialogCode.Rejected)
        mock_done.assert_called_once_with(QDialog.DialogCode.Rejected)


    @patch.object(ConcreteFluentBaseDialog, 'close_animated')
    @patch.object(ConcreteFluentBaseDialog, 'get_button')
    @patch('components.dialogs.base_dialog.QDialog.keyPressEvent') # Patch super call
    def test_keyPressEvent(self, mock_super_key_press, mock_get_button, mock_close_animated, base_dialog_fixture):
        """Test keyPressEvent handles Escape and Enter keys."""
        dialog, widgets, parent_widget = base_dialog_fixture

        # Test Escape key closes dialog
        mock_event_escape = Mock(spec=QKeyEvent)
        mock_event_escape.key.return_value = Qt.Key.Key_Escape
        dialog._escape_closes = True
        mock_close_animated.reset_mock()
        mock_super_key_press.reset_mock()

        dialog.keyPressEvent(mock_event_escape)
        mock_close_animated.assert_called_once_with(QDialog.DialogCode.Rejected)
        mock_super_key_press.assert_not_called() # Event is handled

        # Test Escape key ignored if _escape_closes is False
        mock_close_animated.reset_mock()
        mock_super_key_press.reset_mock()
        dialog._escape_closes = False
        dialog.keyPressEvent(mock_event_escape)
        mock_close_animated.assert_not_called()
        mock_super_key_press.assert_called_once_with(mock_event_escape) # Event passed to super

        # Test Enter key triggers primary button
        mock_event_enter = Mock(spec=QKeyEvent)
        mock_event_enter.key.return_value = Qt.Key.Key_Enter
        dialog._enter_accepts = True
        mock_primary_button = Mock(spec=QPushButton)
        mock_primary_button.isEnabled.return_value = True
        mock_get_button.return_value = mock_primary_button
        mock_primary_button.click.reset_mock()
        mock_super_key_press.reset_mock()

        dialog.keyPressEvent(mock_event_enter)
        mock_get_button.assert_called_once_with(ButtonRole.PRIMARY)
        mock_primary_button.isEnabled.assert_called_once()
        mock_primary_button.click.assert_called_once()
        mock_super_key_press.assert_not_called() # Event is handled

        # Test Return key triggers primary button
        mock_event_return = Mock(spec=QKeyEvent)
        mock_event_return.key.return_value = Qt.Key.Key_Return
        mock_get_button.reset_mock()
        mock_primary_button.isEnabled.reset_mock()
        mock_primary_button.click.reset_mock()
        mock_super_key_press.reset_mock()

        dialog.keyPressEvent(mock_event_return)
        mock_get_button.assert_called_once_with(ButtonRole.PRIMARY)
        mock_primary_button.isEnabled.assert_called_once()
        mock_primary_button.click.assert_called_once()
        mock_super_key_press.assert_not_called() # Event is handled

        # Test Enter key ignored if _enter_accepts is False
        mock_get_button.reset_mock()
        mock_primary_button.isEnabled.reset_mock()
        mock_primary_button.click.reset_mock()
        mock_super_key_press.reset_mock()
        dialog._enter_accepts = False
        dialog.keyPressEvent(mock_event_enter)
        mock_get_button.assert_not_called()
        mock_primary_button.isEnabled.assert_not_called()
        mock_primary_button.click.assert_not_called()
        mock_super_key_press.assert_called_once_with(mock_event_enter) # Event passed to super

        # Test Enter key ignored if primary button is disabled
        mock_get_button.reset_mock()
        mock_primary_button.isEnabled.reset_mock()
        mock_primary_button.click.reset_mock()
        mock_super_key_press.reset_mock()
        dialog._enter_accepts = True
        mock_primary_button.isEnabled.return_value = False # Button disabled
        dialog.keyPressEvent(mock_event_enter)
        mock_get_button.assert_called_once_with(ButtonRole.PRIMARY)
        mock_primary_button.isEnabled.assert_called_once()
        mock_primary_button.click.assert_not_called() # Button not clicked
        mock_super_key_press.assert_called_once_with(mock_event_enter) # Event passed to super

        # Test Enter key ignored if no primary button exists
        mock_get_button.reset_mock()
        mock_get_button.return_value = None # No primary button
        mock_super_key_press.reset_mock()
        dialog._enter_accepts = True
        dialog.keyPressEvent(mock_event_enter)
        mock_get_button.assert_called_once_with(ButtonRole.PRIMARY)
        mock_super_key_press.assert_called_once_with(mock_event_enter) # Event passed to super

        # Test other keys
        mock_event_other = Mock(spec=QKeyEvent)
        mock_event_other.key.return_value = Qt.Key.Key_A
        mock_super_key_press.reset_mock()
        dialog.keyPressEvent(mock_event_other)
        mock_super_key_press.assert_called_once_with(mock_event_other) # Event passed to super

    @patch('components.dialogs.base_dialog.QPainter')
    @patch.object(ConcreteFluentBaseDialog, 'get_theme_color', return_value='#80000000') # Mock theme color
    @patch.object(ConcreteFluentBaseDialog, 'rect', return_value=QRect(0, 0, 100, 100)) # Mock dialog rect
    @patch('components.dialogs.base_dialog.QDialog.paintEvent') # Patch super call
    def test_paintEvent(self, mock_super_paint, mock_rect, mock_get_theme_color, mock_painter_class, base_dialog_fixture):
        """Test paintEvent draws backdrop for modal/overlay dialogs."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_painter = Mock(spec=QPainter)
        mock_painter_class.return_value = mock_painter
        mock_event = Mock(spec=QPaintEvent)

        # Test MODAL dialog
        dialog._dialog_type = DialogType.MODAL
        mock_painter_class.reset_mock()
        mock_get_theme_color.reset_mock()
        mock_painter.fillRect.reset_mock()
        mock_super_paint.reset_mock()

        dialog.paintEvent(mock_event)

        mock_painter_class.assert_called_once_with(dialog)
        mock_get_theme_color.assert_called_once_with('dialog-backdrop', '#80000000')
        mock_painter.fillRect.assert_called_once()
        fill_rect_args = mock_painter.fillRect.call_args[0]
        assert fill_rect_args[0] == mock_rect.return_value
        assert isinstance(fill_rect_args[1], QColor)
        assert fill_rect_args[1].name() == '#80000000' # Check color name
        mock_super_paint.assert_called_once_with(mock_event)

        # Test OVERLAY dialog
        dialog._dialog_type = DialogType.OVERLAY
        mock_painter_class.reset_mock()
        mock_get_theme_color.reset_mock()
        mock_painter.fillRect.reset_mock()
        mock_super_paint.reset_mock()

        dialog.paintEvent(mock_event)

        mock_painter_class.assert_called_once_with(dialog)
        mock_get_theme_color.assert_called_once_with('dialog-backdrop', '#80000000')
        mock_painter.fillRect.assert_called_once()
        mock_super_paint.assert_called_once_with(mock_event)

        # Test MODELESS dialog (no backdrop)
        dialog._dialog_type = DialogType.MODELESS
        mock_painter_class.reset_mock()
        mock_get_theme_color.reset_mock()
        mock_painter.fillRect.reset_mock()
        mock_super_paint.reset_mock()

        dialog.paintEvent(mock_event)

        mock_painter_class.assert_called_once_with(dialog)
        mock_get_theme_color.assert_not_called() # No backdrop, no theme color lookup
        mock_painter.fillRect.assert_not_called()
        mock_super_paint.assert_called_once_with(mock_event)

        # Test POPUP dialog (no backdrop)
        dialog._dialog_type = DialogType.POPUP
        mock_painter_class.reset_mock()
        mock_get_theme_color.reset_mock()
        mock_painter.fillRect.reset_mock()
        mock_super_paint.reset_mock()

        dialog.paintEvent(mock_event)

        mock_painter_class.assert_called_once_with(dialog)
        mock_get_theme_color.assert_not_called()
        mock_painter.fillRect.assert_not_called()
        mock_super_paint.assert_called_once_with(mock_event)


    @patch.object(ConcreteFluentBaseDialog, 'setStyleSheet')
    @patch.object(ConcreteFluentBaseDialog, 'get_current_theme')
    @patch.object(ConcreteFluentBaseDialog, 'theme_applied')
    def test_apply_theme(self, mock_theme_applied_signal, mock_get_current_theme, mock_set_style_sheet, base_dialog_fixture):
        """Test apply_theme updates stylesheet with theme variables."""
        dialog, widgets, parent_widget = base_dialog_fixture
        mock_theme_applied_signal.emit = Mock() # Mock the signal emit

        # Mock theme data
        mock_theme = {
            'surface_primary': '#111111',
            'stroke_default': '#222222',
            'backdrop': '#333333',
            'text_primary': '#444444',
            'accent_default': '#555555',
            # ... other keys
        }
        mock_get_current_theme.return_value = mock_theme

        # Simulate initial stylesheet with var()
        initial_style = """
            #dialogContainer {
                background-color: var(--dialog-background, #f9f9f9);
                border: 1px solid var(--dialog-border, #e1e1e1);
            }
            #dialogTitle {
                color: var(--text-primary, #323130);
            }
            FluentBaseDialog {
                background: transparent;
            }
        """
        dialog.styleSheet = Mock(return_value=initial_style) # Mock the getter

        mock_set_style_sheet.reset_mock()
        mock_theme_applied_signal.emit.reset_mock()

        dialog.apply_theme()

        # Check if setStyleSheet was called
        mock_set_style_sheet.assert_called_once()

        # Check the content of the stylesheet passed to setStyleSheet
        actual_style = mock_set_style_sheet.call_args[0][0]

        # Check if variables were replaced correctly
        assert 'background-color: #111111; /* var(--dialog-background, #f9f9f9);' in actual_style
        assert 'border: 1px solid #222222; /* var(--dialog-border, #e1e1e1);' in actual_style
        assert 'color: #444444; /* var(--text-primary, #323130);' in actual_style
        # Check that variables not in the mock theme use their fallback (or are unchanged if no fallback)
        assert 'background: transparent;' in actual_style # This line doesn't use var()

        # Check signal emitted
        mock_theme_applied_signal.emit.assert_called_once()

        # Test case where get_current_theme returns None
        mock_get_current_theme.return_value = None
        mock_set_style_sheet.reset_mock()
        mock_theme_applied_signal.emit.reset_mock()

        dialog.apply_theme()
        mock_set_style_sheet.assert_not_called() # Stylesheet not applied if theme is invalid
        mock_theme_applied_signal.emit.assert_not_called()


    def test_abstract_methods(self, base_dialog_fixture):
        """Test that the concrete subclass implements abstract methods."""
        dialog, widgets, parent_widget = base_dialog_fixture
        # The fixture provides ConcreteFluentBaseDialog, which implements accept/reject
        # We just need to ensure they exist and can be called.
        dialog.accept()
        dialog.reject()
        # No specific behavior to assert here beyond not raising NotImplementedError

class TestFluentDialogBuilder:
    """Unit tests for FluentDialogBuilder."""

    @patch('components.dialogs.base_dialog.FluentBaseDialog.__init__', return_value=None) # Patch the base dialog init
    @patch.object(ConcreteFluentBaseDialog, 'add_content_widget')
    @patch.object(ConcreteFluentBaseDialog, 'add_button')
    def test_build(self, mock_add_button, mock_add_content_widget, mock_dialog_init, dialog_builder_fixture, mocker):
        """Test build method creates dialog and adds content/buttons."""
        builder = dialog_builder_fixture
        mock_parent = Mock(spec=QWidget)

        # Use the concrete dialog class for the builder
        builder._dialog_class = ConcreteFluentBaseDialog

        # Configure builder
        builder.title("Builder Title")
        builder.modal()
        builder.size(DialogSize.LARGE)
        widget1 = Mock(spec=QWidget)
        widget2 = Mock(spec=QWidget)
        builder.add_content(widget1)
        builder.add_content(widget2)
        mock_callback_ok = mocker.Mock()
        mock_callback_cancel = mocker.Mock()
        builder.add_button("OK", ButtonRole.PRIMARY, mock_callback_ok)
        builder.add_button("Cancel", ButtonRole.CANCEL, mock_callback_cancel)

        # Mock the dialog instance that will be returned by the patched init
        mock_dialog_instance = Mock(spec=ConcreteFluentBaseDialog)
        mock_dialog_init.return_value = None # Ensure init returns None
        # Need to manually set the methods that the builder calls on the dialog instance
        mock_dialog_instance.add_content_widget = mock_add_content_widget
        mock_dialog_instance.add_button = mock_add_button

        # Patch the class instantiation itself to return our mock instance
        with patch('components.dialogs.base_dialog.ConcreteFluentBaseDialog', return_value=mock_dialog_instance) as mock_dialog_class:
             # Build the dialog
             dialog = builder.build(mock_parent)

             # Check if the dialog class was instantiated correctly
             mock_dialog_class.assert_called_once_with(
                 mock_parent, "Builder Title", DialogType.MODAL, DialogSize.LARGE
             )

             # Check if content widgets were added
             mock_add_content_widget.assert_has_calls([call(widget1), call(widget2)])
             assert mock_add_content_widget.call_count == 2

             # Check if buttons were added
             mock_add_button.assert_has_calls([
                 call("OK", ButtonRole.PRIMARY, mock_callback_ok),
                 call("Cancel", ButtonRole.CANCEL, mock_callback_cancel)
             ])
             assert mock_add_button.call_count == 2

             # Check that the returned object is the mock dialog instance
             assert dialog == mock_dialog_instance

    def test_builder_chaining(self, dialog_builder_fixture):
        """Test that builder methods return self for chaining."""
        builder = dialog_builder_fixture
        chained_builder = builder.title("").modal().size(DialogSize.SMALL).add_button("", ButtonRole.PRIMARY).add_content(Mock(spec=QWidget))
        assert chained_builder is builder
