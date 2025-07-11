import sys
import os
import pytest
from unittest.mock import Mock
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QRect, QSize, Signal
from PySide6.QtTest import QTest
from components.layout.dock_panel import FluentDockPanel, DockPosition, DockItem

# filepath: d:\Project\simple-fluent-widget\tests\components\layout\dock_panel.py


# Add the project root directory to the path for absolute import
# Assuming the test file is in tests/components/layout/
# and the source is in components/layout/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Import the class and enum to test using absolute import
# Assuming FluentLayoutBase is in components/layout/layout_base.py
# from components.layout.layout_base import FluentLayoutBase


@pytest.fixture(scope="session")
def app_fixture():
    """Provides a QApplication instance for the test session."""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()

@pytest.fixture(scope="function")
def dock_panel_fixture(app_fixture, request):
    """Provides a FluentDockPanel instance and a list to track widgets for cleanup."""
    dock_panel = FluentDockPanel()
    widgets_to_clean = []

    def cleanup():
        """Cleans up widgets and the dock panel after each test."""
        for widget in widgets_to_clean:
             if widget and hasattr(widget, 'setParent'):
                 widget.setParent(None)
                 widget.deleteLater() # Schedule for deletion

        if dock_panel:
             dock_panel.deleteLater() # Schedule dock_panel for deletion

        # Process events to allow deletion to occur
        QApplication.processEvents()

    request.addfinalizer(cleanup)

    return dock_panel, widgets_to_clean

class TestFluentDockPanel:
    """Unit tests for FluentDockPanel using pytest."""

    def create_widget(self, widgets_list, size_hint=QSize(50, 50)):
        """Helper to create a mock QWidget with a sizeHint and track it for cleanup."""
        widget = QWidget()
        # Mock sizeHint for layout calculations
        widget.sizeHint = Mock(return_value=size_hint)
        widgets_list.append(widget)
        return widget

    def test_init(self, dock_panel_fixture):
        """Test initialization."""
        dock_panel, widgets = dock_panel_fixture
        assert isinstance(dock_panel, FluentDockPanel)
        assert len(dock_panel._dock_items) == 0
        assert dock_panel._fill_widget is None
        assert dock_panel._splitter_width == 6
        assert dock_panel._mobile_stack_threshold == 768
        assert dock_panel._mobile_mode is False

    def test_add_dock_widget_dock(self, dock_panel_fixture):
        """Test adding a widget to a dock position."""
        dock_panel, widgets = dock_panel_fixture
        widget = self.create_widget(widgets)
        dock_item = dock_panel.add_dock_widget(widget, DockPosition.LEFT)

        assert isinstance(dock_item, DockItem)
        assert len(dock_panel._dock_items) == 1
        assert dock_panel._dock_items[0].widget == widget
        assert dock_panel._dock_items[0].position == DockPosition.LEFT
        assert widget.parent() == dock_panel
        assert dock_panel._fill_widget is None

    def test_add_dock_widget_fill(self, dock_panel_fixture):
        """Test adding a widget to the fill position."""
        dock_panel, widgets = dock_panel_fixture
        widget = self.create_widget(widgets)
        dock_item = dock_panel.add_dock_widget(widget, DockPosition.FILL)

        assert isinstance(dock_item, DockItem)
        assert len(dock_panel._dock_items) == 0
        assert dock_panel._fill_widget == widget
        assert widget.parent() == dock_panel

    def test_add_dock_widget_replace_fill(self, dock_panel_fixture):
        """Test adding a second widget to fill replaces the first."""
        dock_panel, widgets = dock_panel_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        dock_panel.add_dock_widget(widget1, DockPosition.FILL)
        dock_panel.add_dock_widget(widget2, DockPosition.FILL)

        assert dock_panel._fill_widget == widget2
        # Old fill widget should be unparented
        assert widget1.parent() is None

    def test_remove_dock_widget_dock(self, dock_panel_fixture):
        """Test removing a docked widget."""
        dock_panel, widgets = dock_panel_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        dock_panel.add_dock_widget(widget1, DockPosition.LEFT)
        dock_panel.add_dock_widget(widget2, DockPosition.RIGHT)

        assert len(dock_panel._dock_items) == 2
        dock_panel.remove_dock_widget(widget1)
        assert len(dock_panel._dock_items) == 1
        assert dock_panel._dock_items[0].widget == widget2
        assert widget1.parent() is None

    def test_remove_dock_widget_fill(self, dock_panel_fixture):
        """Test removing the fill widget."""
        dock_panel, widgets = dock_panel_fixture
        widget = self.create_widget(widgets)
        dock_panel.add_dock_widget(widget, DockPosition.FILL)

        assert dock_panel._fill_widget is not None
        dock_panel.remove_dock_widget(widget)
        assert dock_panel._fill_widget is None
        assert widget.parent() is None

    def test_remove_dock_widget_non_existent(self, dock_panel_fixture):
        """Test removing a widget that isn't in the panel."""
        dock_panel, widgets = dock_panel_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        dock_panel.add_dock_widget(widget1, DockPosition.LEFT)
        initial_count = len(dock_panel._dock_items)
        initial_fill = dock_panel._fill_widget

        dock_panel.remove_dock_widget(widget2)  # widget2 is not added

        assert len(dock_panel._dock_items) == initial_count
        assert dock_panel._fill_widget == initial_fill

    def test_set_dock_position_dock_to_dock(self, dock_panel_fixture, mocker):
        """Test changing position from one dock to another."""
        dock_panel, widgets = dock_panel_fixture
        widget = self.create_widget(widgets)
        item = dock_panel.add_dock_widget(widget, DockPosition.LEFT)
        mock_signal = mocker.Mock()
        dock_panel.dock_position_changed.connect(mock_signal)

        dock_panel.set_dock_position(widget, DockPosition.RIGHT)

        assert item.position == DockPosition.RIGHT
        assert len(dock_panel._dock_items) == 1
        mock_signal.emit.assert_called_once_with(widget, DockPosition.RIGHT)

    def test_set_dock_position_dock_to_fill(self, dock_panel_fixture, mocker):
        """Test moving a docked widget to fill."""
        dock_panel, widgets = dock_panel_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        dock_panel.add_dock_widget(widget1, DockPosition.LEFT)
        dock_panel.add_dock_widget(
            widget2, DockPosition.FILL)  # widget2 is initially fill
        mock_signal = mocker.Mock()
        dock_panel.dock_position_changed.connect(mock_signal)

        dock_panel.set_dock_position(widget1, DockPosition.FILL)

        assert len(dock_panel._dock_items) == 0  # widget1 removed from items
        assert dock_panel._fill_widget == widget1  # widget1 is now fill
        # Old fill widget (widget2) is unparented
        assert widget2.parent() is None
        mock_signal.emit.assert_called_once_with(widget1, DockPosition.FILL)

    def test_set_dock_position_fill_to_dock(self, dock_panel_fixture, mocker):
        """Test moving the fill widget to a dock position."""
        dock_panel, widgets = dock_panel_fixture
        widget = self.create_widget(widgets)
        dock_panel.add_dock_widget(widget, DockPosition.FILL)
        mock_signal = mocker.Mock()
        dock_panel.dock_position_changed.connect(mock_signal)

        dock_panel.set_dock_position(widget, DockPosition.BOTTOM)

        assert dock_panel._fill_widget is None  # Fill widget is gone
        assert len(dock_panel._dock_items) == 1  # Widget added to items
        assert dock_panel._dock_items[0].widget == widget
        assert dock_panel._dock_items[0].position == DockPosition.BOTTOM
        mock_signal.emit.assert_called_once_with(widget, DockPosition.BOTTOM)

    def test_get_dock_position(self, dock_panel_fixture):
        """Test getting the dock position."""
        dock_panel, widgets = dock_panel_fixture
        widget_left = self.create_widget(widgets)
        widget_fill = self.create_widget(widgets)
        widget_other = self.create_widget(widgets)

        dock_panel.add_dock_widget(widget_left, DockPosition.LEFT)
        dock_panel.add_dock_widget(widget_fill, DockPosition.FILL)

        assert dock_panel.get_dock_position(widget_left) == DockPosition.LEFT
        assert dock_panel.get_dock_position(widget_fill) == DockPosition.FILL
        assert dock_panel.get_dock_position(widget_other) is None  # Not in panel

    def test_set_dock_size(self, dock_panel_fixture, mocker):
        """Test setting the size of a docked widget."""
        dock_panel, widgets = dock_panel_fixture
        widget = self.create_widget(widgets)
        item = dock_panel.add_dock_widget(
            widget, DockPosition.LEFT, size=-1, min_size=10, max_size=100)
        mock_signal = mocker.Mock()
        dock_panel.dock_size_changed.connect(mock_signal)

        # Set size within constraints
        dock_panel.set_dock_size(widget, 50)
        assert item.size == 50
        mock_signal.emit.assert_called_once_with(widget, 50)
        mock_signal.reset_mock()

        # Set size below min
        dock_panel.set_dock_size(widget, 5)
        assert item.size == 10  # Should be clamped to min_size
        mock_signal.emit.assert_called_once_with(widget, 10)
        mock_signal.reset_mock()

        # Set size above max
        dock_panel.set_dock_size(widget, 150)
        assert item.size == 100  # Should be clamped to max_size
        mock_signal.emit.assert_called_once_with(widget, 100)
        mock_signal.reset_mock()

        # Set size to current size (should not emit signal)
        dock_panel.set_dock_size(widget, 100)
        assert item.size == 100
        mock_signal.emit.assert_not_called()

    def test_get_dock_size(self, dock_panel_fixture):
        """Test getting the size of a docked widget."""
        dock_panel, widgets = dock_panel_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        dock_panel.add_dock_widget(widget1, DockPosition.LEFT, size=75)
        dock_panel.add_dock_widget(widget2, DockPosition.RIGHT, size=-1)

        assert dock_panel.get_dock_size(widget1) == 75
        assert dock_panel.get_dock_size(widget2) == -1
        assert dock_panel.get_dock_size(
            self.create_widget(widgets)) == -1  # Not in panel

    def test_collapse_dock(self, dock_panel_fixture, mocker):
        """Test collapsing a docked widget."""
        dock_panel, widgets = dock_panel_fixture
        widget = self.create_widget(widgets)
        item = dock_panel.add_dock_widget(
            widget, DockPosition.LEFT, size=100)
        mock_signal = mocker.Mock()
        dock_panel.dock_collapsed.connect(mock_signal)

        assert widget.isVisible() is True
        dock_panel.collapse_dock(widget)

        assert item.size == 0
        assert widget.isVisible() is False
        mock_signal.emit.assert_called_once_with(widget)

    def test_expand_dock(self, dock_panel_fixture, mocker):
        """Test expanding a collapsed docked widget."""
        dock_panel, widgets = dock_panel_fixture
        widget = self.create_widget(widgets, size_hint=QSize(60, 70))
        item = dock_panel.add_dock_widget(
            widget, DockPosition.LEFT, size=0)
        widget.hide()  # Manually hide after adding
        mock_signal = mocker.Mock()
        dock_panel.dock_expanded.connect(mock_signal)

        assert widget.isVisible() is False
        assert item.size == 0

        # Expand with specific size
        dock_panel.expand_dock(widget, size=80)
        assert item.size == 80
        assert widget.isVisible() is True
        mock_signal.emit.assert_called_once_with(widget)
        mock_signal.reset_mock()

        # Collapse again
        dock_panel.collapse_dock(widget)
        assert widget.isVisible() is False
        assert item.size == 0

        # Expand with size=-1 (should use sizeHint width for LEFT/RIGHT)
        dock_panel.expand_dock(widget, size=-1)
        assert item.size == 60  # Uses width from sizeHint
        assert widget.isVisible() is True
        mock_signal.emit.assert_called_once_with(widget)

        # Test expand with size=-1 for TOP/BOTTOM (should use sizeHint height)
        widget_top = self.create_widget(widgets, size_hint=QSize(60, 70))
        item_top = dock_panel.add_dock_widget(
            widget_top, DockPosition.TOP, size=0)
        widget_top.hide()
        dock_panel.expand_dock(widget_top, size=-1)
        assert item_top.size == 70  # Uses height from sizeHint

    def test_layout_desktop_mode(self, dock_panel_fixture, mocker):
        """Test layout calculation in desktop mode."""
        dock_panel, widgets = dock_panel_fixture
        # Mock contentsRect and QWidget.sizeHint for layout calculations
        mocker.patch.object(FluentDockPanel, 'contentsRect', return_value=QRect(0, 0, 800, 600))
        # Default sizeHint for created widgets is handled by create_widget mock

        widget_left1 = self.create_widget(widgets, size_hint=QSize(50, 50))
        widget_left2 = self.create_widget(widgets, size_hint=QSize(60, 60))
        widget_top = self.create_widget(widgets, size_hint=QSize(70, 70))
        widget_right = self.create_widget(widgets, size_hint=QSize(80, 80))
        widget_bottom = self.create_widget(widgets, size_hint=QSize(90, 90))
        widget_fill = self.create_widget(widgets)

        dock_panel.set_spacing(5)
        dock_panel.set_splitter_width(10)

        dock_panel.add_dock_widget(
            widget_left1, DockPosition.LEFT, size=50)  # Fixed size
        dock_panel.add_dock_widget(
            widget_left2, DockPosition.LEFT)  # Auto size (60)
        dock_panel.add_dock_widget(
            widget_top, DockPosition.TOP)  # Auto size (70)
        dock_panel.add_dock_widget(
            widget_right, DockPosition.RIGHT)  # Auto size (80)
        dock_panel.add_dock_widget(
            widget_bottom, DockPosition.BOTTOM)  # Auto size (90)
        dock_panel.add_dock_widget(widget_fill, DockPosition.FILL)

        # Manually trigger layout update (in real app, this is async)
        dock_panel._perform_layout_update()

        # Expected sizes: left1=50, left2=60, top=70, right=80, bottom=90
        # Spacing = 5, Splitter = 10
        # Container: 800x600

        # Left area: (50 + 5 + 60) = 115 wide
        expected_left_width = 50 + dock_panel._spacing + 60
        assert dock_panel._left_area == QRect(0, 0, expected_left_width, 600)
        # Remaining width: 800 - 115 - splitter(10) = 675

        # Right area: 80 wide
        expected_right_width = 80
        assert dock_panel._right_area == QRect(
            800 - expected_right_width, 0, expected_right_width, 600)
        # Remaining width: 675 - 80 - splitter(10) = 585

        # Top area: 70 high
        expected_top_height = 70
        assert dock_panel._top_area == QRect(
            expected_left_width + dock_panel._splitter_width, 0, 585, expected_top_height)
        # Remaining height: 600 - 70 - splitter(10) = 520

        # Bottom area: 90 high
        expected_bottom_height = 90
        assert dock_panel._bottom_area == QRect(
            expected_left_width + dock_panel._splitter_width, 600 - expected_bottom_height, 585, expected_bottom_height)
        # Remaining height: 520 - 90 - splitter(10) = 420

        # Center area
        expected_center_rect = QRect(
            expected_left_width + dock_panel._splitter_width,
            expected_top_height + dock_panel._splitter_width,
            585,  # Remaining width
            420  # Remaining height
        )
        assert dock_panel._center_area == expected_center_rect

        # Check widget geometries (basic check)
        assert widget_left1.geometry() == QRect(0, 0, 50, 600)
        assert widget_left2.geometry() == QRect(
            50 + dock_panel._spacing, 0, 60, 600)
        assert widget_top.geometry() == QRect(
            expected_left_width + dock_panel._splitter_width, 0, 585, 70)
        assert widget_right.geometry() == QRect(800 - 80, 0, 80, 600)
        assert widget_bottom.geometry() == QRect(
            expected_left_width + dock_panel._splitter_width, 600 - 90, 585, 90)
        assert widget_fill.geometry() == expected_center_rect

    def test_layout_mobile_mode(self, dock_panel_fixture, mocker):
        """Test layout calculation in mobile mode."""
        dock_panel, widgets = dock_panel_fixture
        # Mock contentsRect and QWidget.sizeHint for layout calculations
        mocker.patch.object(FluentDockPanel, 'contentsRect', return_value=QRect(0, 0, 400, 600)) # Mobile width
        # Default sizeHint for created widgets is handled by create_widget mock

        widget_left = self.create_widget(widgets, size_hint=QSize(50, 50))
        widget_right = self.create_widget(widgets, size_hint=QSize(60, 60))
        widget_top = self.create_widget(widgets, size_hint=QSize(70, 70))
        widget_bottom = self.create_widget(widgets, size_hint=QSize(80, 80))
        widget_fill = self.create_widget(widgets)

        dock_panel.set_spacing(5)
        dock_panel.set_mobile_threshold(500)  # Set threshold below 400

        dock_panel.add_dock_widget(widget_left, DockPosition.LEFT)
        dock_panel.add_dock_widget(widget_right, DockPosition.RIGHT)
        dock_panel.add_dock_widget(widget_top, DockPosition.TOP)
        dock_panel.add_dock_widget(widget_bottom, DockPosition.BOTTOM)
        dock_panel.add_dock_widget(widget_fill, DockPosition.FILL)

        # Manually trigger layout update
        dock_panel._perform_layout_update()

        assert dock_panel.is_mobile_mode() is True

        # In mobile mode, all docks should become TOP/BOTTOM and stack vertically
        # Original LEFT (widget_left) becomes TOP, sizeHint height = 50
        # Original RIGHT (widget_right) becomes BOTTOM, sizeHint height = 60
        # Original TOP (widget_top) stays TOP, sizeHint height = 70
        # Original BOTTOM (widget_bottom) stays BOTTOM, sizeHint height = 80

        # Order in _dock_items is preserved: left, right, top, bottom
        # Mobile layout stacks them in this order based on the list order.
        # The _adjust_for_mobile_mode changes the position property, but not the order in the list.
        # The _layout_mobile_mode iterates through _dock_items and stacks visible ones.
        # Heights: widget_left=50, widget_right=60, widget_top=70, widget_bottom=80
        # Total dock height = 50 + 5 + 60 + 5 + 70 + 5 + 80 = 275 (4 docks, 3 spacings)
        # Available height = 600

        # Check adjusted positions (these are changed by _adjust_for_mobile_mode)
        assert dock_panel._dock_items[0].position == DockPosition.TOP # Original LEFT
        assert dock_panel._dock_items[1].position == DockPosition.BOTTOM # Original RIGHT
        assert dock_panel._dock_items[2].position == DockPosition.TOP # Original TOP
        assert dock_panel._dock_items[3].position == DockPosition.BOTTOM # Original BOTTOM

        # Check widget geometries (stacked vertically)
        current_y = 0
        assert widget_left.geometry() == QRect(0, current_y, 400, 50)
        current_y += 50 + dock_panel._spacing  # 55
        assert widget_right.geometry() == QRect(0, current_y, 400, 60)
        current_y += 60 + dock_panel._spacing  # 120
        assert widget_top.geometry() == QRect(0, current_y, 400, 70)
        current_y += 70 + dock_panel._spacing  # 195
        assert widget_bottom.geometry() == QRect(0, current_y, 400, 80)
        current_y += 80 + dock_panel._spacing  # 280

        # Center area takes remaining space
        expected_center_rect = QRect(0, current_y, 400, max(
            0, 600 - current_y))  # 600 - 280 = 320
        assert dock_panel._center_area == expected_center_rect
        assert widget_fill.geometry() == expected_center_rect

    def test_calculate_dock_size(self, dock_panel_fixture):
        """Test _calculate_dock_size method."""
        dock_panel, widgets = dock_panel_fixture
        widget_fixed = self.create_widget(widgets)
        item_fixed = DockItem(widget_fixed, DockPosition.LEFT, size=75)

        widget_auto = self.create_widget(widgets, size_hint=QSize(60, 80))
        item_auto = DockItem(widget_auto, DockPosition.TOP,
                             size=-1, min_size=20, max_size=100)

        # Fixed size
        assert dock_panel._calculate_dock_size(
            item_fixed, 200, True) == 75  # Within available
        assert dock_panel._calculate_dock_size(
            item_fixed, 50, True) == 50  # Clamped by available

        # Auto size (width for LEFT/RIGHT)
        assert dock_panel._calculate_dock_size(
            item_auto, 200, True) == 60  # Uses sizeHint width
        assert dock_panel._calculate_dock_size(
            item_auto, 40, True) == 40  # Clamped by available
        item_auto.min_size = 70
        assert dock_panel._calculate_dock_size(
            item_auto, 200, True) == 70  # Clamped by min_size
        item_auto.min_size = 20  # Reset
        item_auto.max_size = 50
        assert dock_panel._calculate_dock_size(
            item_auto, 200, True) == 50  # Clamped by max_size
        item_auto.max_size = 100  # Reset

        # Auto size (height for TOP/BOTTOM)
        assert dock_panel._calculate_dock_size(
            item_auto, 200, False) == 80  # Uses sizeHint height
        assert dock_panel._calculate_dock_size(
            item_auto, 40, False) == 40  # Clamped by available
        item_auto.min_size = 90
        assert dock_panel._calculate_dock_size(
            item_auto, 200, False) == 90  # Clamped by min_size
        item_auto.min_size = 20  # Reset
        item_auto.max_size = 70
        assert dock_panel._calculate_dock_size(
            item_auto, 200, False) == 70  # Clamped by max_size

    def test_mobile_mode_switching(self, dock_panel_fixture):
        """Test mobile mode threshold and switching."""
        dock_panel, widgets = dock_panel_fixture
        dock_panel.set_mobile_threshold(500)
        assert dock_panel.get_mobile_threshold() == 500

        # Start in desktop mode (width > threshold)
        dock_panel._mobile_mode = False
        widget_left = self.create_widget(widgets)
        dock_panel.add_dock_widget(widget_left, DockPosition.LEFT)
        assert dock_panel._dock_items[0].position == DockPosition.LEFT

        # Switch to mobile mode (width < threshold)
        dock_panel._update_mobile_mode(400)
        assert dock_panel.is_mobile_mode() is True
        # Check if horizontal docks were adjusted
        # LEFT should become TOP
        assert dock_panel._dock_items[0].position == DockPosition.TOP

        # Switch back to desktop mode (width >= threshold)
        dock_panel._update_mobile_mode(600)
        assert dock_panel.is_mobile_mode() is False
        # Note: The current implementation does NOT revert the position when switching back.
        # This might be a design choice or a potential area for improvement.
        # Testing the current behavior: position remains TOP.
        assert dock_panel._dock_items[0].position == DockPosition.TOP

    def test_splitter_width(self, dock_panel_fixture):
        """Test setting and getting splitter width."""
        dock_panel, widgets = dock_panel_fixture
        assert dock_panel.get_splitter_width() == 6
        dock_panel.set_splitter_width(10)
        assert dock_panel.get_splitter_width() == 10
        dock_panel.set_splitter_width(-5)  # Should be clamped
        assert dock_panel.get_splitter_width() == 0

    def test_get_dock_items(self, dock_panel_fixture):
        """Test getting the list of dock items."""
        dock_panel, widgets = dock_panel_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        item1 = dock_panel.add_dock_widget(widget1, DockPosition.LEFT)
        item2 = dock_panel.add_dock_widget(widget2, DockPosition.RIGHT)

        items = dock_panel.get_dock_items()
        assert len(items) == 2
        assert item1 in items
        assert item2 in items
        # Should return a copy
        assert items is not dock_panel._dock_items

    def test_get_fill_widget(self, dock_panel_fixture):
        """Test getting the fill widget."""
        dock_panel, widgets = dock_panel_fixture
        assert dock_panel.get_fill_widget() is None
        widget = self.create_widget(widgets)
        dock_panel.add_dock_widget(widget, DockPosition.FILL)
        assert dock_panel.get_fill_widget() == widget

    def test_signals_emitted(self, dock_panel_fixture, mocker):
        """Test if signals are emitted correctly."""
        dock_panel, widgets = dock_panel_fixture
        widget = self.create_widget(widgets)
        item = dock_panel.add_dock_widget(
            widget, DockPosition.LEFT, size=100)

        mock_pos_changed = mocker.Mock()
        mock_size_changed = mocker.Mock()
        mock_collapsed = mocker.Mock()
        mock_expanded = mocker.Mock()

        dock_panel.dock_position_changed.connect(mock_pos_changed)
        dock_panel.dock_size_changed.connect(mock_size_changed)
        dock_panel.dock_collapsed.connect(mock_collapsed)
        dock_panel.dock_expanded.connect(mock_expanded)

        # Test dock_position_changed
        dock_panel.set_dock_position(widget, DockPosition.RIGHT)
        mock_pos_changed.emit.assert_called_once_with(
            widget, DockPosition.RIGHT)

        # Test dock_size_changed
        dock_panel.set_dock_size(widget, 150)  # Change size
        mock_size_changed.emit.assert_called_once_with(widget, 150)

        # Test dock_collapsed
        dock_panel.collapse_dock(widget)
        mock_collapsed.emit.assert_called_once_with(widget)

        # Test dock_expanded
        dock_panel.expand_dock(widget, 100)
        mock_expanded.emit.assert_called_once_with(widget)