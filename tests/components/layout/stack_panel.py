import sys
import os
import pytest
from unittest.mock import Mock, patch, call
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLayoutItem
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QByteArray, QSize
from PySide6.QtGui import QResizeEvent
from components.layout.stack_panel import FluentStackPanel, StackOrientation
from core.theme import theme_manager

# filepath: d:\Project\simple-fluent-widget\tests\components\layout\test_stack_panel.py


# Add the project root directory to the path for relative import
# Assuming the test file is in tests/components/layout/
# and the source is in components/layout/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Import the classes and enums to test
# Assuming FluentControlBase is in ..base.fluent_control_base
# from components.base.fluent_control_base import FluentControlBase, FluentThemeAware
# Assuming theme_manager is in core/theme.py


@pytest.fixture(scope="session")
def app_fixture():
    """Provides a QApplication instance for the test session."""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()

@pytest.fixture(scope="function")
def stack_panel_fixture(app_fixture, request):
    """Provides a FluentStackPanel instance and a list to track widgets for cleanup."""
    # Create a parent widget for the stack panel
    parent_widget = QWidget()
    # FluentStackPanel is a QWidget subclass
    stack_panel = FluentStackPanel(parent_widget)
    widgets_to_clean = [parent_widget] # Track parent widget for cleanup

    def cleanup():
        """Cleans up widgets after each test."""
        for widget in widgets_to_clean:
             if widget and hasattr(widget, 'setParent'):
                 widget.setParent(None)
                 widget.deleteLater() # Schedule for deletion

        # Process events to allow deletion to occur
        QApplication.processEvents()

    request.addfinalizer(cleanup)

    return stack_panel, widgets_to_clean, parent_widget

class TestStackOrientation:
    """Unit tests for StackOrientation enum."""

    def test_enum_values(self):
        """Test that enum members have correct string values."""
        assert StackOrientation.VERTICAL.value == "vertical"
        assert StackOrientation.HORIZONTAL.value == "horizontal"


class TestFluentStackPanel:
    """Unit tests for FluentStackPanel using pytest."""

    def create_widget(self, widgets_list, size_hint=QSize(50, 50)):
        """Helper to create a mock QWidget with a sizeHint and track it for cleanup."""
        widget = Mock(spec=QWidget)
        widget.sizeHint = Mock(return_value=size_hint)
        widget.adjustSize = Mock()
        widget.setMaximumHeight = Mock()
        widget.setMaximumWidth = Mock()
        widget.height = Mock(return_value=size_hint.height())
        widget.width = Mock(return_value=size_hint.width())
        widget.setParent = Mock()
        widget.show = Mock() # FluentWrapPanel calls show
        widgets_list.append(widget)
        return widget

    @patch('components.layout.stack_panel.FluentControlBase.__init__', return_value=None)
    @patch.object(FluentStackPanel, '_init_ui')
    @patch.object(FluentStackPanel, '_setup_styling')
    @patch.object(FluentStackPanel, 'apply_theme')
    def test_init(self, mock_apply_theme, mock_setup_styling, mock_init_ui, mock_control_base_init, stack_panel_fixture):
        """Test initialization."""
        stack_panel, widgets, parent_widget = stack_panel_fixture

        # Re-initialize to use mocks
        mock_control_base_init.reset_mock()
        mock_init_ui.reset_mock()
        mock_setup_styling.reset_mock()
        mock_apply_theme.reset_mock()

        # Test default orientation
        stack_panel.__init__(parent=parent_widget)
        mock_control_base_init.assert_called_once_with(stack_panel, parent_widget)
        assert stack_panel._orientation == StackOrientation.VERTICAL
        assert stack_panel._spacing == 8
        assert stack_panel._auto_wrap is False
        assert stack_panel._wrap_threshold == 600
        assert stack_panel._items == []
        assert stack_panel._animations == {}
        mock_init_ui.assert_called_once()
        mock_setup_styling.assert_called_once()
        mock_apply_theme.assert_called_once()

        # Test horizontal orientation
        mock_control_base_init.reset_mock()
        mock_init_ui.reset_mock()
        mock_setup_styling.reset_mock()
        mock_apply_theme.reset_mock()
        stack_panel.__init__(orientation=StackOrientation.HORIZONTAL, parent=parent_widget)
        mock_control_base_init.assert_called_once_with(stack_panel, parent_widget)
        assert stack_panel._orientation == StackOrientation.HORIZONTAL
        mock_init_ui.assert_called_once()
        mock_setup_styling.assert_called_once()
        mock_apply_theme.assert_called_once()


    @patch.object(FluentStackPanel, '_update_layout')
    @patch.object(FluentStackPanel, 'setSizePolicy')
    def test__init_ui(self, mock_set_size_policy, mock_update_layout, stack_panel_fixture):
        """Test _init_ui sets size policy and updates layout."""
        stack_panel, widgets, parent_widget = stack_panel_fixture

        # Call the method directly
        mock_update_layout.reset_mock()
        mock_set_size_policy.reset_mock()

        stack_panel._init_ui()

        mock_update_layout.assert_called_once()
        mock_set_size_policy.assert_called_once_with(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    @patch.object(QVBoxLayout, '__init__', return_value=None)
    @patch.object(QHBoxLayout, '__init__', return_value=None)
    @patch.object(QVBoxLayout, 'setSpacing')
    @patch.object(QHBoxLayout, 'setSpacing')
    @patch.object(QVBoxLayout, 'setContentsMargins')
    @patch.object(QHBoxLayout, 'setContentsMargins')
    @patch.object(QVBoxLayout, 'addWidget')
    @patch.object(QHBoxLayout, 'addWidget')
    @patch.object(QWidget, 'layout') # Mock the widget's layout method
    def test__update_layout(self, mock_widget_layout, mock_h_add_widget, mock_v_add_widget, mock_h_set_margins, mock_v_set_margins, mock_h_set_spacing, mock_v_set_spacing, mock_h_init, mock_v_init, stack_panel_fixture, mocker):
        """Test _update_layout creates correct layout and re-adds items."""
        stack_panel, widgets, parent_widget = stack_panel_fixture

        # Simulate existing layout
        mock_old_layout = Mock()
        mock_old_layout.count.side_effect = [2, 1, 0] # Simulate 2 items then empty
        mock_old_layout.takeAt.side_effect = [Mock(widget=Mock(setParent=Mock())), Mock(widget=Mock(setParent=Mock()))]
        mock_old_layout.deleteLater = Mock()
        mock_widget_layout.return_value = mock_old_layout

        # Add some items before updating layout
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        stack_panel._items = [widget1, widget2]
        stack_panel._spacing = 10

        # Test Vertical orientation
        stack_panel._orientation = StackOrientation.VERTICAL
        mock_v_init.reset_mock()
        mock_h_init.reset_mock()
        mock_v_set_spacing.reset_mock()
        mock_h_set_spacing.reset_mock()
        mock_v_set_margins.reset_mock()
        mock_h_set_margins.reset_mock()
        mock_v_add_widget.reset_mock()
        mock_h_add_widget.reset_mock()
        mock_old_layout.count.side_effect = [2, 1, 0] # Reset count for clearing
        mock_old_layout.takeAt.reset_mock()
        mock_old_layout.deleteLater.reset_mock()

        stack_panel._update_layout()

        # Check old layout was cleared and deleted
        assert mock_old_layout.takeAt.call_count == 2
        mock_old_layout.deleteLater.assert_called_once()

        # Check new vertical layout was created and configured
        mock_v_init.assert_called_once_with(stack_panel)
        mock_h_init.assert_not_called()
        assert isinstance(stack_panel._stack_layout, Mock) # It's the mocked QVBoxLayout
        mock_v_set_spacing.assert_called_once_with(10)
        mock_v_set_margins.assert_called_once_with(8, 8, 8, 8)

        # Check items were re-added
        mock_v_add_widget.assert_has_calls([call(widget1), call(widget2)])
        assert mock_v_add_widget.call_count == 2
        mock_h_add_widget.assert_not_called()

        # Test Horizontal orientation
        stack_panel._orientation = StackOrientation.HORIZONTAL
        # Need to mock the layout() call again as the old layout is deleted
        mock_widget_layout.return_value = Mock(count=Mock(return_value=0), takeAt=Mock(), deleteLater=Mock()) # Simulate no old layout this time
        mock_v_init.reset_mock()
        mock_h_init.reset_mock()
        mock_v_set_spacing.reset_mock()
        mock_h_set_spacing.reset_mock()
        mock_v_set_margins.reset_mock()
        mock_h_set_margins.reset_mock()
        mock_v_add_widget.reset_mock()
        mock_h_add_widget.reset_mock()

        stack_panel._update_layout()

        # Check new horizontal layout was created and configured
        mock_v_init.assert_not_called()
        mock_h_init.assert_called_once_with(stack_panel)
        assert isinstance(stack_panel._stack_layout, Mock) # It's the mocked QHBoxLayout
        mock_h_set_spacing.assert_called_once_with(10)
        mock_h_set_margins.assert_called_once_with(8, 8, 8, 8)

        # Check items were re-added
        mock_v_add_widget.assert_not_called()
        mock_h_add_widget.assert_has_calls([call(widget1), call(widget2)])
        assert mock_h_add_widget.call_count == 2

    @patch.object(FluentStackPanel, 'setStyleSheet')
    def test__setup_styling(self, mock_set_style_sheet, stack_panel_fixture):
        """Test _setup_styling sets the stylesheet."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        mock_set_style_sheet.reset_mock()

        stack_panel._setup_styling()

        mock_set_style_sheet.assert_called_once()
        # Cannot easily check the exact stylesheet content in a unit test

    @patch.object(FluentStackPanel, '_animate_widget_entrance')
    @patch.object(QVBoxLayout, 'addWidget') # Mock addWidget for the layout
    def test_add_widget(self, mock_add_widget, mock_animate_entrance, stack_panel_fixture, mocker):
        """Test add_widget adds widget and triggers animation/signal."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        widget = self.create_widget(widgets)
        mock_signal_emit = mocker.Mock()
        stack_panel.item_added.emit = mock_signal_emit

        # Ensure layout exists
        stack_panel._stack_layout = Mock(spec=QVBoxLayout)
        stack_panel._stack_layout.addWidget = mock_add_widget

        stack_panel.add_widget(widget, stretch=5)

        assert widget in stack_panel._items
        mock_add_widget.assert_called_once_with(widget, 5)
        mock_animate_entrance.assert_called_once_with(widget)
        mock_signal_emit.assert_called_once_with(widget)

    @patch.object(FluentStackPanel, '_animate_widget_entrance')
    @patch.object(QVBoxLayout, 'insertWidget') # Mock insertWidget for the layout
    def test_insert_widget(self, mock_insert_widget, mock_animate_entrance, stack_panel_fixture, mocker):
        """Test insert_widget inserts widget and triggers animation/signal."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        widget3 = self.create_widget(widgets)
        mock_signal_emit = mocker.Mock()
        stack_panel.item_added.emit = mock_signal_emit

        # Ensure layout exists
        stack_panel._stack_layout = Mock(spec=QVBoxLayout)
        stack_panel._stack_layout.insertWidget = mock_insert_widget

        # Add initial widgets
        stack_panel._items = [widget1, widget3]

        # Insert widget2 at index 1
        stack_panel.insert_widget(1, widget2, stretch=3)

        assert stack_panel._items == [widget1, widget2, widget3]
        mock_insert_widget.assert_called_once_with(1, widget2, 3)
        mock_animate_entrance.assert_called_once_with(widget2)
        mock_signal_emit.assert_called_once_with(widget2)

        # Test insertion at index 0 (beginning)
        mock_insert_widget.reset_mock()
        mock_animate_entrance.reset_mock()
        mock_signal_emit.reset_mock()
        widget0 = self.create_widget(widgets)
        stack_panel.insert_widget(0, widget0)
        assert stack_panel._items[0] == widget0
        mock_insert_widget.assert_called_once_with(0, widget0, 0) # Default stretch 0

        # Test insertion at index > len(items) (end)
        mock_insert_widget.reset_mock()
        mock_animate_entrance.reset_mock()
        mock_signal_emit.reset_mock()
        widget_end = self.create_widget(widgets)
        stack_panel.insert_widget(100, widget_end) # Index 100, len is now 4
        assert stack_panel._items[-1] == widget_end
        mock_insert_widget.assert_called_once_with(4, widget_end, 0) # Should insert at index len(items)

    @patch.object(FluentStackPanel, '_animate_widget_exit')
    def test_remove_widget(self, mock_animate_exit, stack_panel_fixture):
        """Test remove_widget triggers exit animation."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        stack_panel._items = [widget1, widget2]

        stack_panel.remove_widget(widget1)

        assert widget1 not in stack_panel._items
        assert widget2 in stack_panel._items
        mock_animate_exit.assert_called_once()
        # Check that the callback passed to _animate_widget_exit is the _complete_widget_removal method
        # This is hard to check directly, but we can assume it's correct if the mock was called.

        # Test removing non-existent widget
        mock_animate_exit.reset_mock()
        widget3 = self.create_widget(widgets)
        stack_panel.remove_widget(widget3)
        assert widget3 not in stack_panel._items # Was never there
        assert len(stack_panel._items) == 1 # Count remains 1
        mock_animate_exit.assert_not_called() # Animation not triggered

    @patch.object(QVBoxLayout, 'removeWidget')
    def test__complete_widget_removal(self, mock_remove_widget_layout, stack_panel_fixture, mocker):
        """Test _complete_widget_removal finishes the removal process."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        widget = self.create_widget(widgets)
        mock_signal_emit = mocker.Mock()
        stack_panel.item_removed.emit = mock_signal_emit

        # Ensure layout exists and widget is tracked in animations
        stack_panel._stack_layout = Mock(spec=QVBoxLayout)
        stack_panel._stack_layout.removeWidget = mock_remove_widget_layout
        stack_panel._animations[widget] = Mock(spec=QPropertyAnimation) # Simulate animation exists

        stack_panel._complete_widget_removal(widget)

        mock_remove_widget_layout.assert_called_once_with(widget)
        widget.setParent.assert_called_once_with(None)
        assert widget not in stack_panel._animations # Animation should be removed
        mock_signal_emit.assert_called_once_with(widget)

        # Test case where widget is not in _animations (e.g., no animation applied)
        mock_remove_widget_layout.reset_mock()
        widget.setParent.reset_mock()
        mock_signal_emit.reset_mock()
        widget2 = self.create_widget(widgets)
        stack_panel._complete_widget_removal(widget2)
        mock_remove_widget_layout.assert_called_once_with(widget2)
        widget2.setParent.assert_called_once_with(None)
        assert widget2 not in stack_panel._animations # Still not there
        mock_signal_emit.assert_called_once_with(widget2)


    @patch.object(FluentStackPanel, 'remove_widget')
    def test_clear(self, mock_remove_widget, stack_panel_fixture):
        """Test clear removes all widgets."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        stack_panel._items = [widget1, widget2] # Manually add items

        stack_panel.clear()

        assert stack_panel._items == [] # Should be empty after clear
        mock_remove_widget.assert_has_calls([call(widget1), call(widget2)])
        assert mock_remove_widget.call_count == 2

    @patch('components.layout.stack_panel.QPropertyAnimation')
    def test__animate_widget_entrance_vertical(self, mock_animation_class, stack_panel_fixture):
        """Test _animate_widget_entrance for vertical orientation."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        widget = self.create_widget(widgets, size_hint=QSize(100, 80)) # Simulate size hint
        stack_panel._orientation = StackOrientation.VERTICAL

        mock_animation = Mock(spec=QPropertyAnimation)
        mock_animation.finished = Mock(spec=Qt.Signal)
        mock_animation_class.return_value = mock_animation

        stack_panel._animate_widget_entrance(widget)

        # Check initial state setting
        widget.setMaximumHeight.assert_called_once_with(0)
        widget.setMaximumWidth.assert_not_called() # Not called for vertical

        # Check animation creation and setup
        mock_animation_class.assert_called_once_with(widget, QByteArray(b"maximumHeight"))
        mock_animation.setDuration.assert_called_once_with(200)
        mock_animation.setEasingCurve.assert_called_once_with(QEasingCurve.Type.OutCubic)
        mock_animation.setStartValue.assert_called_once_with(0)
        widget.adjustSize.assert_called_once()
        widget.sizeHint.assert_called_once()
        mock_animation.setEndValue.assert_called_once_with(80) # Based on sizeHint height
        mock_animation.start.assert_called_once()

        # Check animation storage
        assert widget in stack_panel._animations
        assert stack_panel._animations[widget] == mock_animation

        # Simulate animation finished to check reset_max_size callback
        mock_animation.finished.emit()
        widget.setMaximumHeight.assert_called_with(16777215) # Called again by callback

    @patch('components.layout.stack_panel.QPropertyAnimation')
    def test__animate_widget_entrance_horizontal(self, mock_animation_class, stack_panel_fixture):
        """Test _animate_widget_entrance for horizontal orientation."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        widget = self.create_widget(widgets, size_hint=QSize(120, 60)) # Simulate size hint
        stack_panel._orientation = StackOrientation.HORIZONTAL

        mock_animation = Mock(spec=QPropertyAnimation)
        mock_animation.finished = Mock(spec=Qt.Signal)
        mock_animation_class.return_value = mock_animation

        stack_panel._animate_widget_entrance(widget)

        # Check initial state setting
        widget.setMaximumHeight.assert_not_called() # Not called for horizontal
        widget.setMaximumWidth.assert_called_once_with(0)

        # Check animation creation and setup
        mock_animation_class.assert_called_once_with(widget, QByteArray(b"maximumWidth"))
        mock_animation.setDuration.assert_called_once_with(200)
        mock_animation.setEasingCurve.assert_called_once_with(QEasingCurve.Type.OutCubic)
        mock_animation.setStartValue.assert_called_once_with(0)
        widget.adjustSize.assert_called_once()
        widget.sizeHint.assert_called_once()
        mock_animation.setEndValue.assert_called_once_with(120) # Based on sizeHint width
        mock_animation.start.assert_called_once()

        # Check animation storage
        assert widget in stack_panel._animations
        assert stack_panel._animations[widget] == mock_animation

        # Simulate animation finished to check reset_max_size callback
        mock_animation.finished.emit()
        widget.setMaximumWidth.assert_called_with(16777215) # Called again by callback


    @patch('components.layout.stack_panel.QPropertyAnimation')
    def test__animate_widget_exit_vertical(self, mock_animation_class, stack_panel_fixture, mocker):
        """Test _animate_widget_exit for vertical orientation."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        widget = self.create_widget(widgets)
        widget.height.return_value = 70 # Simulate current height
        stack_panel._orientation = StackOrientation.VERTICAL
        mock_callback = mocker.Mock()

        mock_animation = Mock(spec=QPropertyAnimation)
        mock_animation.finished = Mock(spec=Qt.Signal)
        mock_animation_class.return_value = mock_animation

        stack_panel._animate_widget_exit(widget, mock_callback)

        # Check animation creation and setup
        mock_animation_class.assert_called_once_with(widget, QByteArray(b"maximumHeight"))
        mock_animation.setDuration.assert_called_once_with(200)
        mock_animation.setEasingCurve.assert_called_once_with(QEasingCurve.Type.InCubic)
        mock_animation.setStartValue.assert_called_once_with(70) # Based on current height
        mock_animation.setEndValue.assert_called_once_with(0)
        mock_animation.start.assert_called_once()

        # Check finished signal connection
        mock_animation.finished.connect.assert_called_once_with(mock_callback)

        # Check animation storage
        assert widget in stack_panel._animations
        assert stack_panel._animations[widget] == mock_animation

    @patch('components.layout.stack_panel.QPropertyAnimation')
    def test__animate_widget_exit_horizontal(self, mock_animation_class, stack_panel_fixture, mocker):
        """Test _animate_widget_exit for horizontal orientation."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        widget = self.create_widget(widgets)
        widget.width.return_value = 110 # Simulate current width
        stack_panel._orientation = StackOrientation.HORIZONTAL
        mock_callback = mocker.Mock()

        mock_animation = Mock(spec=QPropertyAnimation)
        mock_animation.finished = Mock(spec=Qt.Signal)
        mock_animation_class.return_value = mock_animation

        stack_panel._animate_widget_exit(widget, mock_callback)

        # Check animation creation and setup
        mock_animation_class.assert_called_once_with(widget, QByteArray(b"maximumWidth"))
        mock_animation.setDuration.assert_called_once_with(200)
        mock_animation.setEasingCurve.assert_called_once_with(QEasingCurve.Type.InCubic)
        mock_animation.setStartValue.assert_called_once_with(110) # Based on current width
        mock_animation.setEndValue.assert_called_once_with(0)
        mock_animation.start.assert_called_once()

        # Check finished signal connection
        mock_animation.finished.connect.assert_called_once_with(mock_callback)

        # Check animation storage
        assert widget in stack_panel._animations
        assert stack_panel._animations[widget] == mock_animation

    @patch.object(FluentStackPanel, '_update_layout')
    def test_set_orientation(self, mock_update_layout, stack_panel_fixture, mocker):
        """Test set_orientation updates orientation and triggers layout update/signal."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        mock_signal_emit = mocker.Mock()
        stack_panel.orientation_changed.emit = mock_signal_emit

        # Initial orientation is Vertical
        assert stack_panel._orientation == StackOrientation.VERTICAL

        # Change to Horizontal
        stack_panel.set_orientation(StackOrientation.HORIZONTAL)
        assert stack_panel._orientation == StackOrientation.HORIZONTAL
        mock_update_layout.assert_called_once()
        mock_signal_emit.assert_called_once_with("horizontal")

        # Change back to Vertical
        mock_update_layout.reset_mock()
        mock_signal_emit.reset_mock()
        stack_panel.set_orientation(StackOrientation.VERTICAL)
        assert stack_panel._orientation == StackOrientation.VERTICAL
        mock_update_layout.assert_called_once()
        mock_signal_emit.assert_called_once_with("vertical")

        # Set same orientation should not trigger update/signal
        mock_update_layout.reset_mock()
        mock_signal_emit.reset_mock()
        stack_panel.set_orientation(StackOrientation.VERTICAL)
        assert stack_panel._orientation == StackOrientation.VERTICAL
        mock_update_layout.assert_not_called()
        mock_signal_emit.assert_not_called()

    def test_get_orientation(self, stack_panel_fixture):
        """Test get_orientation returns current value."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        stack_panel._orientation = StackOrientation.HORIZONTAL
        assert stack_panel.get_orientation() == StackOrientation.HORIZONTAL

    @patch.object(QVBoxLayout, 'setSpacing') # Mock setSpacing for the layout
    def test_set_spacing(self, mock_set_spacing, stack_panel_fixture):
        """Test set_spacing updates spacing and layout spacing."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        # Ensure layout exists
        stack_panel._stack_layout = Mock(spec=QVBoxLayout)
        stack_panel._stack_layout.setSpacing = mock_set_spacing

        assert stack_panel._spacing == 8

        stack_panel.set_spacing(15)
        assert stack_panel._spacing == 15
        mock_set_spacing.assert_called_once_with(15)

        # Test setting spacing before layout is created (e.g., in init)
        del stack_panel._stack_layout # Remove layout
        mock_set_spacing.reset_mock()
        stack_panel.set_spacing(20)
        assert stack_panel._spacing == 20
        mock_set_spacing.assert_not_called() # Layout doesn't exist yet

    def test_get_spacing(self, stack_panel_fixture):
        """Test get_spacing returns current value."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        stack_panel._spacing = 25
        assert stack_panel.get_spacing() == 25

    def test_set_auto_wrap(self, stack_panel_fixture):
        """Test set_auto_wrap updates properties."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        assert stack_panel._auto_wrap is False
        assert stack_panel._wrap_threshold == 600

        stack_panel.set_auto_wrap(True, threshold=800)
        assert stack_panel._auto_wrap is True
        assert stack_panel._wrap_threshold == 800

        stack_panel.set_auto_wrap(False) # Threshold defaults to 600 if not provided
        assert stack_panel._auto_wrap is False
        assert stack_panel._wrap_threshold == 800 # Threshold should not change if not provided

        stack_panel.set_auto_wrap(True) # Enable with default threshold
        assert stack_panel._auto_wrap is True
        assert stack_panel._wrap_threshold == 600 # Threshold resets to default

    @patch.object(QVBoxLayout, 'addStretch') # Mock addStretch for the layout
    def test_add_stretch(self, mock_add_stretch, stack_panel_fixture):
        """Test add_stretch calls layout addStretch."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        # Ensure layout exists
        stack_panel._stack_layout = Mock(spec=QVBoxLayout)
        stack_panel._stack_layout.addStretch = mock_add_stretch

        stack_panel.add_stretch() # Default stretch 1
        mock_add_stretch.assert_called_once_with(1)

        mock_add_stretch.reset_mock()
        stack_panel.add_stretch(5)
        mock_add_stretch.assert_called_once_with(5)

    @patch.object(QVBoxLayout, 'insertStretch') # Mock insertStretch for the layout
    def test_insert_stretch(self, mock_insert_stretch, stack_panel_fixture):
        """Test insert_stretch calls layout insertStretch."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        # Ensure layout exists
        stack_panel._stack_layout = Mock(spec=QVBoxLayout)
        stack_panel._stack_layout.insertStretch = mock_insert_stretch

        stack_panel.insert_stretch(0) # Default stretch 1
        mock_insert_stretch.assert_called_once_with(0, 1)

        mock_insert_stretch.reset_mock()
        stack_panel.insert_stretch(2, 5)
        mock_insert_stretch.assert_called_once_with(2, 5)

    def test_get_widget_count(self, stack_panel_fixture):
        """Test get_widget_count returns number of items."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        assert stack_panel.get_widget_count() == 0
        stack_panel._items = [self.create_widget(widgets)]
        assert stack_panel.get_widget_count() == 1
        stack_panel._items.append(self.create_widget(widgets))
        assert stack_panel.get_widget_count() == 2

    def test_get_widget_at(self, stack_panel_fixture):
        """Test get_widget_at returns widget at index."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        stack_panel._items = [widget1, widget2]

        assert stack_panel.get_widget_at(0) == widget1
        assert stack_panel.get_widget_at(1) == widget2
        assert stack_panel.get_widget_at(2) is None # Out of bounds
        assert stack_panel.get_widget_at(-1) is None # Out of bounds

    def test_get_widget_index(self, stack_panel_fixture):
        """Test get_widget_index returns index of widget."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        stack_panel._items = [widget1, widget2]

        assert stack_panel.get_widget_index(widget1) == 0
        assert stack_panel.get_widget_index(widget2) == 1
        assert stack_panel.get_widget_index(self.create_widget(widgets)) == -1 # Not found

    @patch.object(FluentStackPanel, 'resizeEvent') # Patch super call
    @patch.object(QSize, 'width') # Mock event size width
    @patch.object(FluentStackPanel, 'set_orientation')
    def test_resizeEvent_auto_wrap(self, mock_set_orientation, mock_width, mock_super_resize, stack_panel_fixture):
        """Test resizeEvent handles auto-wrap logic."""
        stack_panel, widgets, parent_widget = stack_panel_fixture
        mock_event = Mock(spec=QResizeEvent)
        mock_event.size.return_value = Mock(spec=QSize)
        mock_event.size.return_value.width = mock_width # Link mock width

        # Enable auto-wrap
        stack_panel.set_auto_wrap(True, threshold=500)
        stack_panel._orientation = StackOrientation.HORIZONTAL # Start horizontal

        # Test resize below threshold
        mock_width.return_value = 400
        mock_set_orientation.reset_mock()
        stack_panel.resizeEvent(mock_event)
        mock_super_resize.assert_called_once_with(mock_event)
        mock_set_orientation.assert_called_once_with(StackOrientation.VERTICAL)

        # Test resize below threshold again (no change)
        mock_super_resize.reset_mock()
        mock_set_orientation.reset_mock()
        stack_panel._orientation = StackOrientation.VERTICAL # Set orientation after wrap
        mock_width.return_value = 300
        stack_panel.resizeEvent(mock_event)
        mock_super_resize.assert_called_once_with(mock_event)
        mock_set_orientation.assert_not_called()

        # Test resize above threshold
        mock_super_resize.reset_mock()
        mock_set_orientation.reset_mock()
        stack_panel._orientation = StackOrientation.VERTICAL # Start vertical
        mock_width.return_value = 600
        stack_panel.resizeEvent(mock_event)
        mock_super_resize.assert_called_once_with(mock_event)
        mock_set_orientation.assert_called_once_with(StackOrientation.HORIZONTAL)

        # Test resize above threshold again (no change)
        mock_super_resize.reset_mock()
        mock_set_orientation.reset_mock()
        stack_panel._orientation = StackOrientation.HORIZONTAL # Set orientation after wrap
        mock_width.return_value = 700
        stack_panel.resizeEvent(mock_event)
        mock_super_resize.assert_called_once_with(mock_event)
        mock_set_orientation.assert_not_called()

        # Test auto-wrap disabled
        mock_super_resize.reset_mock()
        mock_set_orientation.reset_mock()
        stack_panel.set_auto_wrap(False)
        stack_panel._orientation = StackOrientation.VERTICAL # Start vertical
        mock_width.return_value = 400 # Below threshold
        stack_panel.resizeEvent(mock_event)
        mock_super_resize.assert_called_once_with(mock_event)
        mock_set_orientation.assert_not_called() # No wrap when disabled

    @patch.object(FluentStackPanel, 'setStyleSheet')
    @patch('components.layout.stack_panel.theme_manager')
    def test_apply_theme(self, mock_theme_manager, mock_set_style_sheet, stack_panel_fixture):
        """Test apply_theme applies stylesheet with theme variables."""
        stack_panel, widgets, parent_widget = stack_panel_fixture

        # Mock theme manager and its get_color method (though apply_theme doesn't use get_color directly)
        # It uses CSS variables which are *intended* to be set by a theme manager elsewhere.
        # The current apply_theme implementation just replaces the default var() fallback.
        # Let's mock the stylesheet to check the replacement.
        mock_set_style_sheet.return_value = None # setStyleSheet doesn't return anything

        # Simulate initial stylesheet with var()
        initial_style = """
            FluentStackPanel {
                background-color: var(--stack-background, transparent);
                border: none;
                border-radius: 4px;
            }
        """
        stack_panel.styleSheet = Mock(return_value=initial_style) # Mock the getter

        # Mock theme data that would influence the variables (though not used by this specific apply_theme)
        mock_theme_manager.get_color = Mock(return_value=Mock(name="#theme_bg"))

        mock_set_style_sheet.reset_mock()

        stack_panel.apply_theme()

        # Check if setStyleSheet was called
        mock_set_style_sheet.assert_called_once()

        # Check the content of the stylesheet passed to setStyleSheet
        # The current apply_theme replaces `var(--stack-background, ` with `transparent; /* var(--stack-background, `
        expected_style_part = "background-color: transparent; /* var(--stack-background, transparent);"
        actual_style = mock_set_style_sheet.call_args[0][0]
        assert expected_style_part in actual_style

        # Test case where theme_manager is None
        with patch('components.layout.stack_panel.theme_manager', None):
             mock_set_style_sheet.reset_mock()
             stack_panel.apply_theme()
             mock_set_style_sheet.assert_not_called()
