import sys
import os
import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QSizePolicy
from PySide6.QtCore import QRect, QSize, Qt, QTimer
from PySide6.QtTest import QTest

# filepath: d:\Project\simple-fluent-widget\tests\components\layout\test_grid.py


# Add the project root directory to the path for relative import
# Assuming the test file is in tests/components/layout/
# and the source is in components/layout/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Import the classes and enums to test
from components.layout.grid import (
    FluentGrid, FluentGridItem, GridSpacing, GridItemAlignment, FluentGridBuilder
)
# Assuming FluentBaseWidget is in core/enhanced_base.py
# from core.enhanced_base import FluentBaseWidget


@pytest.fixture(scope="session")
def app_fixture():
    """Provides a QApplication instance for the test session."""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()

@pytest.fixture(scope="function")
def grid_fixture(app_fixture, request):
    """Provides a FluentGrid instance and a list to track widgets for cleanup."""
    # Create a parent widget for the grid
    parent_widget = QWidget()
    grid = FluentGrid(parent_widget)
    widgets_to_clean = [parent_widget] # Track parent widget for cleanup

    def cleanup():
        """Cleans up widgets and the grid after each test."""
        # Widgets added to the grid are parented to the grid's internal container widget
        # Deleting the parent widget should clean up its children (the grid and its contents)
        for widget in widgets_to_clean:
             if widget and hasattr(widget, 'setParent'):
                 widget.setParent(None)
                 widget.deleteLater() # Schedule for deletion

        # Process events to allow deletion to occur
        QApplication.processEvents()

    request.addfinalizer(cleanup)

    return grid, widgets_to_clean, parent_widget

class TestFluentGridItem:
    """Unit tests for FluentGridItem."""

    def test_init(self):
        widget = QWidget()
        item = FluentGridItem(widget, column_span=2, row_span=3)

        assert item.widget == widget
        assert item.column_span == 2
        assert item.row_span == 3
        assert item.min_width == 0
        assert item.preferred_width == 200
        assert item.max_width == -1
        assert item.alignment == GridItemAlignment.STRETCH # Default

class TestFluentGrid:
    """Unit tests for FluentGrid using pytest."""

    def create_widget(self, widgets_list, size_hint=QSize(50, 50)):
        """Helper to create a mock QWidget with a sizeHint and track it for cleanup."""
        widget = QWidget()
        # Mock sizeHint for layout calculations if needed, though grid doesn't use it directly
        # widget.sizeHint = Mock(return_value=size_hint)
        widgets_list.append(widget)
        return widget

    def test_init(self, grid_fixture):
        """Test initialization."""
        grid, widgets, parent_widget = grid_fixture
        assert isinstance(grid, FluentGrid)
        assert grid.parent() == parent_widget
        assert grid._min_column_width == 200 # Default
        assert grid._max_columns == -1 # Default
        assert grid._spacing == GridSpacing.MEDIUM # Default
        assert grid._item_alignment == GridItemAlignment.STRETCH # Default
        assert grid._current_columns == 1 # Initial
        assert len(grid._items) == 0
        assert len(grid._item_widgets) == 0
        assert isinstance(grid._scroll_area, QScrollArea)
        assert isinstance(grid._grid_container, QWidget)
        assert isinstance(grid._grid_layout, QGridLayout)
        assert grid._grid_layout.spacing() == GridSpacing.MEDIUM.value
        assert isinstance(grid._resize_timer, QTimer)
        assert grid._resize_timer.isSingleShot()
        assert grid._resize_timer.interval() == 100

    @patch.object(FluentGrid, '_rebuild_layout')
    def test_add_item(self, mock_rebuild_layout, grid_fixture):
        """Test adding an item."""
        grid, widgets, parent_widget = grid_fixture
        widget = self.create_widget(widgets)
        item = grid.add_item(widget, column_span=2, alignment=GridItemAlignment.CENTER)

        assert len(grid._items) == 1
        assert len(grid._item_widgets) == 1
        assert grid._items[0] == item
        assert grid._item_widgets[0] == widget
        assert item.widget == widget
        assert item.column_span == 2
        assert item.row_span == 1 # Default
        assert item.alignment == GridItemAlignment.CENTER
        mock_rebuild_layout.assert_called_once()

    @patch.object(FluentGrid, '_rebuild_layout')
    def test_remove_item(self, mock_rebuild_layout, grid_fixture):
        """Test removing an item."""
        grid, widgets, parent_widget = grid_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        item1 = grid.add_item(widget1)
        item2 = grid.add_item(widget2)
        mock_rebuild_layout.reset_mock() # Reset call count after adding

        grid.remove_item(widget1)

        assert len(grid._items) == 1
        assert len(grid._item_widgets) == 1
        assert grid._items[0] == item2
        assert grid._item_widgets[0] == widget2
        assert widget1.parent() is None
        mock_rebuild_layout.assert_called_once()

        # Remove non-existent widget
        mock_rebuild_layout.reset_mock()
        widget3 = self.create_widget(widgets)
        grid.remove_item(widget3)
        assert len(grid._items) == 1 # Count remains the same
        mock_rebuild_layout.assert_not_called() # Layout not rebuilt

    @patch.object(FluentGrid, '_rebuild_layout')
    def test_clear_items(self, mock_rebuild_layout, grid_fixture):
        """Test clearing all items."""
        grid, widgets, parent_widget = grid_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        grid.add_item(widget1)
        grid.add_item(widget2)
        mock_rebuild_layout.reset_mock() # Reset call count after adding

        grid.clear_items()

        assert len(grid._items) == 0
        assert len(grid._item_widgets) == 0
        assert widget1.parent() is None
        assert widget2.parent() is None
        mock_rebuild_layout.assert_called_once()

    def test_get_item_count(self, grid_fixture):
        """Test getting item count."""
        grid, widgets, parent_widget = grid_fixture
        assert grid.get_item_count() == 0
        grid.add_item(self.create_widget(widgets))
        assert grid.get_item_count() == 1
        grid.add_item(self.create_widget(widgets))
        assert grid.get_item_count() == 2
        grid.remove_item(grid._item_widgets[0])
        assert grid.get_item_count() == 1

    def test_get_item_at(self, grid_fixture):
        """Test getting item at index."""
        grid, widgets, parent_widget = grid_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        item1 = grid.add_item(widget1)
        item2 = grid.add_item(widget2)

        assert grid.get_item_at(0) == item1
        assert grid.get_item_at(1) == item2
        assert grid.get_item_at(2) is None # Out of bounds
        assert grid.get_item_at(-1) is None # Out of bounds

    def test_find_item(self, grid_fixture):
        """Test finding an item by widget."""
        grid, widgets, parent_widget = grid_fixture
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        item1 = grid.add_item(widget1)
        grid.add_item(widget2)

        assert grid.find_item(widget1) == item1
        assert grid.find_item(widget2) != item1 # Should find item2, but checking it's not item1 is enough
        assert grid.find_item(QWidget()) is None # Non-existent widget

    @patch.object(FluentGrid, '_rebuild_layout')
    def test_set_item_span(self, mock_rebuild_layout, grid_fixture):
        """Test setting item span."""
        grid, widgets, parent_widget = grid_fixture
        widget = self.create_widget(widgets)
        item = grid.add_item(widget, column_span=1, row_span=1)
        mock_rebuild_layout.reset_mock()

        grid.set_item_span(widget, column_span=3, row_span=2)

        assert item.column_span == 3
        assert item.row_span == 2
        mock_rebuild_layout.assert_called_once()

        # Set span for non-existent widget
        mock_rebuild_layout.reset_mock()
        grid.set_item_span(QWidget(), column_span=5)
        mock_rebuild_layout.assert_not_called()

    @patch.object(FluentGrid, '_update_layout')
    def test_set_min_column_width(self, mock_update_layout, grid_fixture):
        """Test setting minimum column width."""
        grid, widgets, parent_widget = grid_fixture
        grid.set_min_column_width(300)
        assert grid._min_column_width == 300
        mock_update_layout.assert_called_once()

    @patch.object(FluentGrid, '_update_layout')
    def test_set_max_columns(self, mock_update_layout, grid_fixture):
        """Test setting maximum columns."""
        grid, widgets, parent_widget = grid_fixture
        grid.set_max_columns(4)
        assert grid._max_columns == 4
        mock_update_layout.assert_called_once()

    def test_set_spacing(self, grid_fixture):
        """Test setting spacing."""
        grid, widgets, parent_widget = grid_fixture
        grid.set_spacing(GridSpacing.LARGE)
        assert grid._spacing == GridSpacing.LARGE
        assert grid._grid_layout.spacing() == GridSpacing.LARGE.value

    def test_set_item_alignment(self, grid_fixture):
        """Test setting default item alignment."""
        grid, widgets, parent_widget = grid_fixture
        grid.set_item_alignment(GridItemAlignment.CENTER)
        assert grid._item_alignment == GridItemAlignment.CENTER

    @patch.object(FluentGrid, '_update_layout')
    def test_set_breakpoints(self, mock_update_layout, grid_fixture):
        """Test setting breakpoints."""
        grid, widgets, parent_widget = grid_fixture
        new_breakpoints = {0: 1, 800: 3}
        grid.set_breakpoints(new_breakpoints)
        assert grid._breakpoints == new_breakpoints
        mock_update_layout.assert_called_once()

    def test_get_current_columns(self, grid_fixture):
        """Test getting current columns."""
        grid, widgets, parent_widget = grid_fixture
        # Initial columns is 1
        assert grid.get_current_columns() == 1
        # Layout update would change this, but we test the property directly

    @patch.object(QScrollArea, 'viewport')
    def test__calculate_optimal_columns(self, mock_viewport, grid_fixture):
        """Test _calculate_optimal_columns logic."""
        grid, widgets, parent_widget = grid_fixture

        # Test with default settings
        mock_viewport.return_value.width.return_value = 500 # Available width
        assert grid._calculate_optimal_columns() == 2 # 500 // 200 = 2.5 -> 2

        # Test with breakpoints
        grid.set_breakpoints({0: 1, 400: 2, 800: 4})
        grid.set_min_column_width(100) # Min width 100

        mock_viewport.return_value.width.return_value = 300 # Width 300
        # From breakpoints: 300 >= 0 -> 1, 300 >= 400 -> False. Breakpoint columns = 1
        # From width: 300 // 100 = 3. Width columns = 3
        # Min(1, 3) = 1.
        assert grid._calculate_optimal_columns() == 1

        mock_viewport.return_value.width.return_value = 600 # Width 600
        # From breakpoints: 600 >= 400 -> 2. Breakpoint columns = 2
        # From width: 600 // 100 = 6. Width columns = 6
        # Min(2, 6) = 2.
        assert grid._calculate_optimal_columns() == 2

        mock_viewport.return_value.width.return_value = 900 # Width 900
        # From breakpoints: 900 >= 800 -> 4. Breakpoint columns = 4
        # From width: 900 // 100 = 9. Width columns = 9
        # Min(4, 9) = 4.
        assert grid._calculate_optimal_columns() == 4

        # Test with max_columns
        grid.set_max_columns(3)
        mock_viewport.return_value.width.return_value = 900 # Width 900
        # Calculated without max: 4
        # With max: min(4, 3) = 3
        assert grid._calculate_optimal_columns() == 3

        # Test with width less than min_column_width
        grid.set_min_column_width(300)
        grid.set_max_columns(-1)
        grid.set_breakpoints({0: 1})
        mock_viewport.return_value.width.return_value = 150 # Width 150
        # From breakpoints: 150 >= 0 -> 1. Breakpoint columns = 1
        # From width: 150 // 300 = 0. max(1, 0) = 1. Width columns = 1
        # Min(1, 1) = 1.
        assert grid._calculate_optimal_columns() == 1

    @patch.object(FluentGrid, '_rebuild_layout')
    @patch.object(FluentGrid, '_calculate_optimal_columns')
    def test__update_layout(self, mock_calculate_columns, mock_rebuild_layout, grid_fixture, mocker):
        """Test _update_layout triggers rebuild and signal."""
        grid, widgets, parent_widget = grid_fixture
        mock_signal = mocker.Mock()
        grid.layout_changed.connect(mock_signal)

        # Initial columns is 1
        assert grid._current_columns == 1

        # Case 1: Columns change
        mock_calculate_columns.return_value = 3
        grid._update_layout()
        assert grid._current_columns == 3
        mock_rebuild_layout.assert_called_once()
        mock_signal.emit.assert_called_once()

        # Case 2: Columns do not change
        mock_rebuild_layout.reset_mock()
        mock_signal.reset_mock()
        mock_calculate_columns.return_value = 3 # Still 3
        grid._update_layout()
        assert grid._current_columns == 3
        mock_rebuild_layout.assert_not_called()
        mock_signal.emit.assert_not_called()

    @patch.object(QTimer, 'start')
    def test_resizeEvent(self, mock_timer_start, grid_fixture):
        """Test resizeEvent starts the timer."""
        grid, widgets, parent_widget = grid_fixture
        event = Mock(spec=QResizeEvent)
        grid.resizeEvent(event)
        mock_timer_start.assert_called_once()

    @patch.object(QGridLayout, 'addWidget')
    @patch.object(QGridLayout, 'takeAt', return_value=Mock(widget=Mock(setParent=Mock()))) # Mock clearing layout
    @patch.object(QGridLayout, 'count', side_effect=[2, 1, 0, 0]) # Simulate layout having items then being empty
    @patch.object(FluentGrid, '_apply_item_alignment')
    def test__rebuild_layout(self, mock_apply_alignment, mock_count, mock_takeat, mock_addwidget, grid_fixture):
        """Test _rebuild_layout correctly places items."""
        grid, widgets, parent_widget = grid_fixture

        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        widget3 = self.create_widget(widgets)

        # Add items with different spans
        grid.add_item(widget1, column_span=1)
        grid.add_item(widget2, column_span=2)
        grid.add_item(widget3, column_span=1)

        # Set current columns to 3
        grid._current_columns = 3

        # Manually trigger rebuild (add_item calls it, but we want to test the logic directly)
        # Need to reset mocks called by add_item
        mock_addwidget.reset_mock()
        mock_takeat.reset_mock()
        mock_count.side_effect = [3, 2, 1, 0, 0] # Simulate layout having 3 items initially
        mock_apply_alignment.reset_mock()

        grid._rebuild_layout()

        # Check if layout was cleared
        assert mock_takeat.call_count == 3 # Called for each item initially in the layout

        # Check if addWidget was called for each item with correct positions and spans
        # Item 1: col=0, span=1. Fits. row=0, col=0. Next col=1.
        # Item 2: col=1, span=2. Fits (1+2=3 <= 3). row=0, col=1. Next col=3.
        # Item 3: col=3, span=1. Does not fit (3+1 > 3). New row. row=1, col=0. Next col=1.
        mock_addwidget.assert_any_call(widget1, 0, 0, 1, 1)
        mock_addwidget.assert_any_call(widget2, 0, 1, 1, 2)
        mock_addwidget.assert_any_call(widget3, 1, 0, 1, 1)
        assert mock_addwidget.call_count == 3

        # Check if alignment was applied
        assert mock_apply_alignment.call_count == 3

        # Check column stretches (mocking setColumnStretch is hard, skip for now)
        # assert grid._grid_layout.setColumnStretch.call_count == 3 # Assuming 3 columns

    def test__apply_item_alignment(self, grid_fixture):
        """Test _apply_item_alignment sets size policy."""
        grid, widgets, parent_widget = grid_fixture
        widget = self.create_widget(widgets)
        item = FluentGridItem(widget) # Create item directly for testing

        # Test STRETCH
        item.alignment = GridItemAlignment.STRETCH
        grid._apply_item_alignment(item)
        assert widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding
        assert widget.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Expanding

        # Test START
        item.alignment = GridItemAlignment.START
        grid._apply_item_alignment(item)
        assert widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Preferred
        assert widget.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Preferred

        # Test CENTER
        item.alignment = GridItemAlignment.CENTER
        grid._apply_item_alignment(item)
        assert widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Preferred
        assert widget.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Preferred

        # Test END
        item.alignment = GridItemAlignment.END
        grid._apply_item_alignment(item)
        assert widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Preferred
        assert widget.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Preferred

    def test__setup_widget_click_handler_qwidget(self, grid_fixture, mocker):
        """Test click handler for a standard QWidget."""
        grid, widgets, parent_widget = grid_fixture
        widget = self.create_widget(widgets)
        mock_signal_emit = mocker.Mock()
        grid.item_clicked.emit = mock_signal_emit # Mock the signal emit

        # Store original mousePressEvent
        original_mouse_press = widget.mousePressEvent

        grid._setup_widget_click_handler(widget)

        # Check if mousePressEvent was wrapped
        assert widget.mousePressEvent != original_mouse_press

        # Simulate a mouse press event
        event = Mock(spec=QResizeEvent) # Use QResizeEvent as a generic QEvent mock
        widget.mousePressEvent(event)

        # Check if the signal was emitted with the correct widget
        mock_signal_emit.assert_called_once_with(widget)

    def test__setup_widget_click_handler_qpushbutton(self, grid_fixture, mocker):
        """Test click handler for a widget with a 'clicked' signal."""
        grid, widgets, parent_widget = grid_fixture
        button = QPushButton() # QPushButton has a 'clicked' signal
        widgets.append(button) # Track for cleanup
        mock_signal_emit = mocker.Mock()
        grid.item_clicked.emit = mock_signal_emit # Mock the signal emit

        # Mock the button's clicked signal
        mock_button_clicked = mocker.Mock()
        button.clicked = mock_button_clicked
        mock_button_clicked.connect = mocker.Mock()

        grid._setup_widget_click_handler(button)

        # Check if the layout's signal was connected to the button's clicked signal
        mock_button_clicked.connect.assert_called_once()
        # The lambda connects the button's clicked signal to grid.item_clicked.emit(button)
        # We can't easily check the lambda content directly, but we know connect was called.

        # Simulate the button being clicked (this would trigger the lambda)
        # We can't easily simulate the Qt signal directly in a unit test without QTest.click
        # But we can check that the mousePressEvent was NOT overridden for QPushButton
        assert not hasattr(button, 'original_mouse_press') # Should not store original

    @patch.object(FluentGrid, '_update_layout')
    def test_force_layout_update(self, mock_update_layout, grid_fixture):
        """Test force_layout_update calls _update_layout."""
        grid, widgets, parent_widget = grid_fixture
        grid.force_layout_update()
        mock_update_layout.assert_called_once()


class TestFluentGridBuilder:
    """Unit tests for FluentGridBuilder."""

    def test_builder_methods(self):
        """Test builder methods set properties."""
        builder = FluentGridBuilder()
        builder.with_min_column_width(150)
        builder.with_max_columns(3)
        builder.with_spacing(GridSpacing.LARGE)
        builder.with_breakpoints({0: 1, 600: 2})

        assert builder._min_column_width == 150
        assert builder._max_columns == 3
        assert builder._spacing == GridSpacing.LARGE
        assert builder._breakpoints == {0: 1, 600: 2}

    def test_builder_add_item(self):
        """Test builder add_item method."""
        builder = FluentGridBuilder()
        widget1 = QWidget()
        widget2 = QWidget()

        builder.add_item(widget1, column_span=2)
        builder.add_item(widget2, row_span=3, alignment=GridItemAlignment.END)

        assert len(builder._items) == 2
        assert builder._items[0]['widget'] == widget1
        assert builder._items[0]['column_span'] == 2
        assert builder._items[0]['row_span'] == 1 # Default
        assert builder._items[0]['alignment'] == GridItemAlignment.STRETCH # Default

        assert builder._items[1]['widget'] == widget2
        assert builder._items[1]['column_span'] == 1 # Default
        assert builder._items[1]['row_span'] == 3
        assert builder._items[1]['alignment'] == GridItemAlignment.END

    @patch('components.layout.grid.FluentGrid.__init__', return_value=None) # Mock Grid init
    @patch.object(FluentGrid, 'set_spacing')
    @patch.object(FluentGrid, 'set_breakpoints')
    @patch.object(FluentGrid, 'add_item')
    def test_builder_build(self, mock_add_item, mock_set_breakpoints, mock_set_spacing, mock_grid_init):
        """Test builder build method."""
        builder = FluentGridBuilder()
        widget1 = QWidget()
        widget2 = QWidget()

        builder.with_min_column_width(150)
        builder.with_max_columns(3)
        builder.with_spacing(GridSpacing.LARGE)
        builder.with_breakpoints({0: 1, 600: 2})
        builder.add_item(widget1, column_span=2)
        builder.add_item(widget2, row_span=3, alignment=GridItemAlignment.END)

        parent = QWidget()
        grid = builder.build(parent)

        # Check if FluentGrid was initialized correctly
        mock_grid_init.assert_called_once_with(parent, 150, 3)

        # Check if properties were set
        mock_set_spacing.assert_called_once_with(GridSpacing.LARGE)
        mock_set_breakpoints.assert_called_once_with({0: 1, 600: 2})

        # Check if items were added
        assert mock_add_item.call_count == 2
        mock_add_item.assert_any_call(widget=widget1, column_span=2, row_span=1, alignment=GridItemAlignment.STRETCH)
        mock_add_item.assert_any_call(widget=widget2, column_span=1, row_span=3, alignment=GridItemAlignment.END)

        # Check return type
        assert isinstance(grid, FluentGrid)

    @patch('components.layout.grid.FluentGrid.__init__', return_value=None) # Mock Grid init
    @patch.object(FluentGrid, 'set_spacing')
    @patch.object(FluentGrid, 'set_breakpoints')
    @patch.object(FluentGrid, 'add_item')
    def test_builder_build_defaults(self, mock_add_item, mock_set_breakpoints, mock_set_spacing, mock_grid_init):
        """Test builder build with default properties."""
        builder = FluentGridBuilder()
        widget = QWidget()
        builder.add_item(widget)

        grid = builder.build() # No parent

        # Check if FluentGrid was initialized with defaults
        mock_grid_init.assert_called_once_with(None, 200, -1)

        # Check if default spacing was set
        mock_set_spacing.assert_called_once_with(GridSpacing.MEDIUM)

        # Check if breakpoints were NOT set if empty
        mock_set_breakpoints.assert_not_called()

        # Check if item was added with defaults
        mock_add_item.assert_called_once_with(widget=widget, column_span=1, row_span=1, alignment=GridItemAlignment.STRETCH)

        assert isinstance(grid, FluentGrid)