import pytest
import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QByteArray, QEvent
from PySide6.QtGui import QColor
from PySide6.QtTest import QTest

# Add the parent directory to the path for relative import if necessary
# Assuming the test file is components/data/test_notification.py
# and the module is components/data/notification.py
# The parent directory 'data' is a package (__init__.py exists)
# So we can use relative import
try:
    from .notification import (
        FluentToast, ToastConfig, ToastType, get_safe_color,
        ENHANCED_ANIMATION_AVAILABLE, FluentTransition, FluentMicroInteraction
    )
except ImportError as e:
    pytest.fail(f"Failed to import components: {e}")

# pytest-qt provides the qapp fixture automatically

@pytest.fixture
def widget_cleanup():
    """Fixture to clean up widgets after each test."""
    widgets = []
    yield widgets
    for widget in widgets:
        # Check if widget is a QObject and hasn't been deleted
        if widget is not None and hasattr(widget, 'deleteLater'):
             # Check if it's a QWidget and visible, then close
             if isinstance(widget, QWidget) and widget.isVisible():
                 widget.close()
             # Schedule deletion
             widget.deleteLater()
    QApplication.processEvents() # Process events to ensure widgets are closed/deleted


class TestFluentToast:

    def test_initialization_default(self, qapp, widget_cleanup):
        """Test FluentToast initialization with default config."""
        toast = FluentToast()
        widget_cleanup.append(toast)

        assert isinstance(toast, FluentToast)
        assert isinstance(toast, QFrame)
        assert toast._config.title == ""
        assert toast._config.message == ""
        assert toast._config.toast_type == ToastType.INFO
        assert toast._config.duration == 4000
        assert toast._config.action_text == ""
        assert toast._config.auto_dismiss is True

        assert isinstance(toast._title_label, QLabel)
        assert isinstance(toast._message_label, QLabel)
        assert isinstance(toast._close_button, QPushButton)
        assert toast._action_button is None
        assert isinstance(toast._opacity_effect, QGraphicsOpacityEffect)
        assert isinstance(toast._fade_in_anim, QPropertyAnimation)
        assert isinstance(toast._fade_out_anim, QPropertyAnimation)
        assert isinstance(toast._timer, QTimer)
        assert toast._timer.isSingleShot() is True

    def test_initialization_config(self, qapp, widget_cleanup):
        """Test FluentToast initialization with custom config."""
        config = ToastConfig(
            title="Custom Title",
            message="Custom Message",
            toast_type=ToastType.WARNING,
            duration=2000,
            action_text="Action",
            auto_dismiss=False
        )
        toast = FluentToast(config=config)
        widget_cleanup.append(toast)

        assert toast._config == config
        assert toast._title_label.text() == "Custom Title"
        assert toast._message_label.text() == "Custom Message"
        assert isinstance(toast._action_button, QPushButton)
        assert toast._action_button.text() == "Action"
        assert toast._timer is None # auto_dismiss is False

        # Check theme colors based on type (WARNING)
        theme = toast._get_theme_for_type(ToastType.WARNING)
        assert toast._theme == theme
        # Basic check on stylesheet for colors (can be fragile)
        style_sheet = toast.styleSheet()
        assert theme.border_color in style_sheet
        assert theme.background_color in style_sheet

    def test_initialization_kwargs(self, qapp, widget_cleanup):
        """Test FluentToast initialization with kwargs."""
        toast = FluentToast(
            title="Kwarg Title",
            message="Kwarg Message",
            toast_type=ToastType.ERROR,
            duration=5000,
            action_text="Do It",
            auto_dismiss=True
        )
        widget_cleanup.append(toast)

        assert toast._config.title == "Kwarg Title"
        assert toast._config.message == "Kwarg Message"
        assert toast._config.toast_type == ToastType.ERROR
        assert toast._config.duration == 5000
        assert toast._config.action_text == "Do It"
        assert toast._config.auto_dismiss is True

        assert toast._title_label.text() == "Kwarg Title"
        assert toast._message_label.text() == "Kwarg Message"
        assert isinstance(toast._action_button, QPushButton)
        assert toast._action_button.text() == "Do It"
        assert isinstance(toast._timer, QTimer) # auto_dismiss is True

        # Check theme colors based on type (ERROR)
        theme = toast._get_theme_for_type(ToastType.ERROR)
        assert toast._theme == theme
        style_sheet = toast.styleSheet()
        assert theme.border_color in style_sheet
        assert theme.background_color in style_sheet

    @pytest.mark.parametrize("toast_type, expected_icon_char", [
        (ToastType.INFO, "ℹ"),
        (ToastType.SUCCESS, "✓"),
        (ToastType.WARNING, "⚠"),
        (ToastType.ERROR, "✕"),
    ])
    def test_toast_types_appearance(self, qapp, widget_cleanup, toast_type: ToastType, expected_icon_char: str):
        """Test appearance changes based on ToastType."""
        toast = FluentToast(toast_type=toast_type)
        widget_cleanup.append(toast)

        assert toast._toast_type == toast_type
        assert toast._icon_label.text() == expected_icon_char

        # Check theme colors are applied (basic check)
        theme = toast._get_theme_for_type(toast_type)
        style_sheet = toast.styleSheet()
        assert theme.border_color in style_sheet
        assert theme.background_color in style_sheet

    def test_show_and_auto_dismiss(self, qapp, widget_cleanup):
        """Test show method and auto-dismiss timer."""
        duration = 100 # Short duration for testing
        toast = FluentToast(message="Auto dismiss test", duration=duration, auto_dismiss=True)
        widget_cleanup.append(toast)

        closed_emitted = False
        def on_closed():
            nonlocal closed_emitted
            closed_emitted = True

        toast.closed.connect(on_closed)

        # Toast is initially hidden
        assert not toast.isVisible()

        toast.show()
        QApplication.processEvents() # Process show event

        assert toast.isVisible()
        assert toast._timer is not None
        assert toast._timer.isActive()

        # Wait for the timer to expire + a small buffer
        QTest.qWaitFor(duration + 50)

        # After timer, toast should be dismissed and hidden
        assert not toast.isVisible()
        assert closed_emitted is True
        # The toast should be scheduled for deletion, but might not be deleted yet
        # Checking if it's hidden and closed signal emitted is sufficient.

    def test_dismiss_manual(self, qapp, widget_cleanup):
        """Test manual dismiss method."""
        # Use a long duration or auto_dismiss=False so timer doesn't interfere
        toast = FluentToast(message="Manual dismiss test", duration=10000, auto_dismiss=True)
        widget_cleanup.append(toast)

        closed_emitted = False
        def on_closed():
            nonlocal closed_emitted
            closed_emitted = True

        toast.closed.connect(on_closed)

        toast.show()
        QApplication.processEvents()
        assert toast.isVisible()
        assert toast._timer.isActive()

        toast.dismiss()
        QApplication.processEvents() # Process dismiss event

        # Timer should be stopped
        assert not toast._timer.isActive()

        # Wait for fade-out animation (default 300ms) + buffer
        QTest.qWaitFor(350)

        # After dismissal animation, toast should be hidden
        assert not toast.isVisible()
        assert closed_emitted is True

    def test_action_button(self, qapp, widget_cleanup):
        """Test action button click."""
        toast = FluentToast(message="Action test", action_text="Click Me", duration=10000)
        widget_cleanup.append(toast)

        action_emitted = False
        def on_action():
            nonlocal action_emitted
            action_emitted = True

        closed_emitted = False
        def on_closed():
            nonlocal closed_emitted
            closed_emitted = True

        toast.action_triggered.connect(on_action)
        toast.closed.connect(on_closed)

        toast.show()
        QApplication.processEvents()
        assert toast.isVisible()
        assert isinstance(toast._action_button, QPushButton)

        # Simulate click on the action button
        QTest.mouseClick(toast._action_button, Qt.MouseButton.LeftButton)
        QApplication.processEvents()

        # Wait for dismiss animation
        QTest.qWaitFor(350)

        # Action signal should be emitted, and toast should be dismissed
        assert action_emitted is True
        assert closed_emitted is True
        assert not toast.isVisible()

    def test_set_title_message(self, qapp, widget_cleanup):
        """Test set_title and set_message methods."""
        toast = FluentToast(title="Initial Title", message="Initial Message")
        widget_cleanup.append(toast)

        assert toast._title_label.text() == "Initial Title"
        assert toast._message_label.text() == "Initial Message"

        toast.set_title("New Title")
        toast.set_message("New Message")

        assert toast._title == "New Title" # Check internal state
        assert toast._message == "New Message" # Check internal state
        assert toast._title_label.text() == "New Title" # Check label text
        assert toast._message_label.text() == "New Message" # Check label text

    def test_animation_setup(self, qapp, widget_cleanup):
        """Test if animation objects are created and configured."""
        toast = FluentToast()
        widget_cleanup.append(toast)

        assert isinstance(toast._opacity_effect, QGraphicsOpacityEffect)
        assert toast.graphicsEffect() == toast._opacity_effect

        assert isinstance(toast._fade_in_anim, QPropertyAnimation)
        assert toast._fade_in_anim.targetObject() == toast
        assert toast._fade_in_anim.propertyName() == QByteArray(b"opacity")
        assert toast._fade_in_anim.startValue() == 0.0
        assert toast._fade_in_anim.endValue() == 1.0

        assert isinstance(toast._fade_out_anim, QPropertyAnimation)
        assert toast._fade_out_anim.targetObject() == toast
        assert toast._fade_out_anim.propertyName() == QByteArray(b"opacity")
        assert toast._fade_out_anim.startValue() == 1.0
        assert toast._fade_out_anim.endValue() == 0.0

        # Check if fade_out_anim finished signal is connected
        # This is hard to test directly without inspecting internal Qt connections,
        # but we can check if the slot exists and is callable.
        assert hasattr(toast, '_on_fade_out_finished')
        assert callable(toast._on_fade_out_finished)

    def test_event_filter_close_button(self, qapp, widget_cleanup):
        """Test if event filter is installed on the close button."""
        toast = FluentToast()
        widget_cleanup.append(toast)

        # Check if the toast object is an event filter for the close button
        # This is an indirect check, but verifies the setup call happened.
        # A more robust test would involve mocking QObject.installEventFilter
        # or simulating events and checking side effects (like animation starts),
        # but that's more complex.
        # We can check if the close button has *any* event filters installed.
        # Note: This doesn't guarantee *this specific* event filter is installed,
        # but it's a reasonable check for setup.
        # QObject doesn't expose a public method to list event filters.
        # A simpler check is to see if the eventFilter method is called when
        # an event occurs on the close button.

        filter_called = False
        original_event_filter = toast.eventFilter

        def mock_event_filter(obj, event):
            nonlocal filter_called
            if obj == toast._close_button:
                filter_called = True
            return original_event_filter(obj, event)

        toast.eventFilter = mock_event_filter

        # Simulate a mouse press event on the close button
        # This will trigger the eventFilter method
        QTest.mouseClick(toast._close_button, Qt.MouseButton.LeftButton)
        QApplication.processEvents()

        assert filter_called is True
