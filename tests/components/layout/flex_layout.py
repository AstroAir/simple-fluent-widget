import sys
import os
import pytest
from unittest.mock import Mock, patch # Import patch

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QRect, QSize # Removed Qt, Signal
# Removed from PySide6.QtTest import QTest

# Add the project root directory to the path for relative import
# Assuming the test file is in tests/components/layout/
# and the source is in components/layout/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Import the class and enums to test
from components.layout.flex_layout import (
    FluentFlexLayout, FlexDirection, FlexWrap, JustifyContent, AlignItems, AlignContent # Removed FlexItem
)
# Assuming FluentLayoutBase is in components/layout/layout_base.py
# from components.layout.layout_base import FluentLayoutBase


@pytest.fixture(scope="session")
def app_fixture():
    """Provides a QApplication instance for the test session."""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()

@pytest.fixture(scope="function")
def flex_layout_fixture(app_fixture, request): # app_fixture is used here
    """Provides a FluentFlexLayout instance and a list to track widgets for cleanup."""
    # Create a parent widget for the layout
    parent_widget = QWidget()
    flex_layout = FluentFlexLayout(parent_widget)
    widgets_to_clean = [parent_widget] # Track parent widget for cleanup

    def cleanup():
        """Cleans up widgets and the layout after each test."""
        # Widgets added to the layout are parented to the layout's parent widget
        # Deleting the parent widget should clean up its children (the widgets in the layout)
        for widget in widgets_to_clean:
             if widget and hasattr(widget, 'setParent'):
                 widget.setParent(None)
                 widget.deleteLater() # Schedule for deletion

        # The layout itself is parented to parent_widget, so it should be cleaned up
        # if flex_layout:
        #      flex_layout.deleteLater() # Schedule flex_layout for deletion

        # Process events to allow deletion to occur
        QApplication.processEvents()

    request.addfinalizer(cleanup)

    return flex_layout, widgets_to_clean, parent_widget

class TestFluentFlexLayout:
    """Unit tests for FluentFlexLayout using pytest."""

    def create_widget(self, widgets_list, size_hint=QSize(50, 50)):
        """Helper to create a mock QWidget with a sizeHint and track it for cleanup."""
        widget = QWidget()
        # Mock sizeHint for layout calculations
        widget.sizeHint = Mock(return_value=size_hint)
        widgets_list.append(widget)
        return widget

    def test_init(self, flex_layout_fixture):
        """Test initialization."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets, parent_widget used
        assert isinstance(flex_layout, FluentFlexLayout)
        assert flex_layout.parent() == parent_widget
        assert len(flex_layout._flex_items) == 0
        assert flex_layout._flex_direction == FlexDirection.ROW
        assert flex_layout._flex_wrap == FlexWrap.NO_WRAP
        assert flex_layout._justify_content == JustifyContent.FLEX_START
        assert flex_layout._align_items == AlignItems.STRETCH
        assert flex_layout._align_content == AlignContent.STRETCH
        assert flex_layout._row_gap == 0
        assert flex_layout._column_gap == 0

    def test_add_widget(self, flex_layout_fixture):
        """Test adding a widget."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets, parent_widget used
        widget = self.create_widget(widgets)
        flex_layout.add_widget(widget, flex_grow=1, flex_basis=100)

        assert len(flex_layout._flex_items) == 1
        item = flex_layout._flex_items[0]
        assert item.widget == widget
        assert item.flex_grow == 1
        assert item.flex_shrink == 1 # Default
        assert item.flex_basis == 100
        assert item.align_self is None
        assert widget.parent() == parent_widget # Widget is parented to layout's parent

    def test_remove_widget(self, flex_layout_fixture):
        """Test removing a widget."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets, parent_widget used
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        flex_layout.add_widget(widget1)
        flex_layout.add_widget(widget2)

        assert len(flex_layout._flex_items) == 2
        flex_layout.remove_widget(widget1)
        assert len(flex_layout._flex_items) == 1
        assert flex_layout._flex_items[0].widget == widget2
        assert widget1.parent() is None # Widget should be unparented

    def test_set_get_flex_direction(self, flex_layout_fixture, mocker):
        """Test setting and getting flex direction."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets, parent_widget used
        mock_signal = mocker.Mock()
        flex_layout.flex_direction_changed.connect(mock_signal)

        flex_layout.set_flex_direction(FlexDirection.COLUMN)
        assert flex_layout.get_flex_direction() == FlexDirection.COLUMN
        mock_signal.emit.assert_called_once_with(FlexDirection.COLUMN)

        # Setting the same value should not emit signal
        mock_signal.reset_mock()
        flex_layout.set_flex_direction(FlexDirection.COLUMN)
        mock_signal.emit.assert_not_called()

    def test_set_get_flex_wrap(self, flex_layout_fixture, mocker):
        """Test setting and getting flex wrap."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets, parent_widget used
        mock_signal = mocker.Mock()
        flex_layout.wrap_changed.connect(mock_signal)

        flex_layout.set_flex_wrap(FlexWrap.WRAP)
        assert flex_layout.get_flex_wrap() == FlexWrap.WRAP
        mock_signal.emit.assert_called_once_with(FlexWrap.WRAP)

        # Setting the same value should not emit signal
        mock_signal.reset_mock()
        flex_layout.set_flex_wrap(FlexWrap.WRAP)
        mock_signal.emit.assert_not_called()

    def test_set_get_justify_content(self, flex_layout_fixture):
        """Test setting and getting justify content."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets, parent_widget used
        flex_layout.set_justify_content(JustifyContent.CENTER)
        assert flex_layout.get_justify_content() == JustifyContent.CENTER

    def test_set_get_align_items(self, flex_layout_fixture):
        """Test setting and getting align items."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets, parent_widget used
        flex_layout.set_align_items(AlignItems.CENTER)
        assert flex_layout.get_align_items() == AlignItems.CENTER

    def test_set_get_gap(self, flex_layout_fixture):
        """Test setting and getting gap."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets, parent_widget used
        flex_layout.set_gap(10)
        assert flex_layout.get_gap() == (10, 10)
        flex_layout.set_gap(5, 15)
        assert flex_layout.get_gap() == (5, 15)

    def test_update_item_flex(self, flex_layout_fixture):
        """Test updating flex properties of an existing item."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets used
        widget1 = self.create_widget(widgets)
        widget2 = self.create_widget(widgets)
        flex_layout.add_widget(widget1, flex_grow=0, flex_shrink=1, flex_basis="auto")
        flex_layout.add_widget(widget2)

        flex_layout.update_item_flex(widget1, flex_grow=2, flex_basis=200, align_self=AlignItems.CENTER)

        item1 = flex_layout._flex_items[0]
        assert item1.flex_grow == 2
        assert item1.flex_shrink == 1 # Unchanged
        assert item1.flex_basis == 200
        assert item1.align_self == AlignItems.CENTER

        # Update non-existent widget
        widget3 = self.create_widget(widgets)
        flex_layout.update_item_flex(widget3, flex_grow=5) # Should do nothing
        assert len(flex_layout._flex_items) == 2 # Count remains the same

    @pytest.mark.parametrize("direction", [FlexDirection.ROW, FlexDirection.COLUMN])
    @pytest.mark.parametrize("wrap", [FlexWrap.NO_WRAP, FlexWrap.WRAP])
    @pytest.mark.parametrize("justify", [JustifyContent.FLEX_START, JustifyContent.CENTER, JustifyContent.FLEX_END])
    @pytest.mark.parametrize("align_items", [AlignItems.FLEX_START, AlignItems.CENTER, AlignItems.FLEX_END, AlignItems.STRETCH])
    @pytest.mark.parametrize("gap", [0, 10])
    @pytest.mark.parametrize("num_widgets", [1, 3, 5])
    @pytest.mark.parametrize("container_size", [QSize(300, 300), QSize(600, 400)])
    def test_layout_combinations(self, flex_layout_fixture, mocker, direction, wrap, justify, align_items, gap, num_widgets, container_size):
        """Test various combinations of flex properties."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets used

        # Mock contentsRect
        mocker.patch.object(flex_layout, 'contentsRect', return_value=QRect(0, 0, container_size.width(), container_size.height()))

        flex_layout.set_flex_direction(direction)
        flex_layout.set_flex_wrap(wrap)
        flex_layout.set_justify_content(justify)
        flex_layout.set_align_items(align_items)
        flex_layout.set_gap(gap)

        # Add widgets with varying size hints and flex properties
        widget_size_hints = [QSize(50 + i*10, 40 + i*5) for i in range(num_widgets)]
        flex_properties = [
            (i % 2, (i+1) % 2, "auto", None) for i in range(num_widgets) # Simple grow/shrink/basis
        ]

        for i in range(num_widgets):
            widget = self.create_widget(widgets, size_hint=widget_size_hints[i])
            grow, shrink, basis, align_self = flex_properties[i]
            flex_layout.add_widget(widget, flex_grow=grow, flex_shrink=shrink, flex_basis=basis, align_self=align_self)

        # Manually trigger layout update
        flex_layout._perform_layout_update()

        # Basic checks:
        # 1. All widgets should have a geometry set.
        # 2. Widgets should be within the container bounds.
        container_rect = flex_layout.contentsRect()
        container_rect.adjust(
            flex_layout._padding.left(), flex_layout._padding.top(),
            -flex_layout._padding.right(), -flex_layout._padding.bottom()
        )

        for item in flex_layout._flex_items:
            widget = item.widget
            assert not widget.geometry().isNull()
            assert container_rect.contains(widget.geometry(), True) # Check if widget is inside container

        # More detailed checks would require implementing the full flexbox algorithm
        # in the test, which is complex. The above provides a basic sanity check
        # that layout happens and widgets are placed within bounds.
        # Specific tests for grow/shrink/alignment/wrapping are better done
        # by mocking internal methods or checking calculated_size/target_rect
        # after specific layout steps.

    # Add specific tests for key layout behaviors

    @pytest.mark.parametrize("flex_grow, expected_widths", [
        ([0, 0], [50, 50]), # No grow
        ([1, 0], [150, 50]), # First grows
        ([0, 1], [50, 150]), # Second grows
        ([1, 1], [100, 100]), # Both grow equally
        ([1, 2], [83, 117]), # Grow proportionally (approx)
    ])
    @patch.object(FluentFlexLayout, 'contentsRect', return_value=QRect(0, 0, 200, 100))
    def test_layout_row_grow(self, mock_contents_rect, flex_layout_fixture, flex_grow, expected_widths): # mock_contents_rect used
        """Test flex-grow in ROW direction."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets used
        flex_layout.set_flex_direction(FlexDirection.ROW)
        flex_layout.set_gap(0) # Simplify calculation

        widget1 = self.create_widget(widgets, size_hint=QSize(50, 50))
        widget2 = self.create_widget(widgets, size_hint=QSize(50, 50))

        flex_layout.add_widget(widget1, flex_grow=flex_grow[0])
        flex_layout.add_widget(widget2, flex_grow=flex_grow[1])

        flex_layout._perform_layout_update()

        # Check calculated sizes after resolving flexible lengths
        # This is a more precise check than geometry() which depends on _position_widgets
        flex_layout._resolve_flex_basis(200, 100)
        flex_layout._collect_flex_lines(200, 100)
        flex_layout._resolve_flexible_lengths()

        assert len(flex_layout._lines) == 1
        line = flex_layout._lines[0]
        assert len(line) == 2

        # Allow for small integer division differences
        assert line[0].calculated_size.width() == pytest.approx(expected_widths[0], abs=1)
        assert line[1].calculated_size.width() == pytest.approx(expected_widths[1], abs=1)

    @pytest.mark.parametrize("flex_shrink, expected_widths", [
        ([1, 1], [25, 25]), # Both shrink equally from base 50, total deficit 50
        ([2, 1], [17, 33]), # Shrink proportionally (approx)
    ])
    @patch.object(FluentFlexLayout, 'contentsRect', return_value=QRect(0, 0, 50, 100)) # Container smaller than base size (50+50=100)
    def test_layout_row_shrink(self, mock_contents_rect, flex_layout_fixture, flex_shrink, expected_widths): # mock_contents_rect used
        """Test flex-shrink in ROW direction."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets used
        flex_layout.set_flex_direction(FlexDirection.ROW)
        flex_layout.set_gap(0) # Simplify calculation

        widget1 = self.create_widget(widgets, size_hint=QSize(50, 50))
        widget2 = self.create_widget(widgets, size_hint=QSize(50, 50))

        flex_layout.add_widget(widget1, flex_shrink=flex_shrink[0])
        flex_layout.add_widget(widget2, flex_shrink=flex_shrink[1])

        flex_layout._perform_layout_update()

        # Check calculated sizes after resolving flexible lengths
        flex_layout._resolve_flex_basis(50, 100)
        flex_layout._collect_flex_lines(50, 100)
        flex_layout._resolve_flexible_lengths()

        assert len(flex_layout._lines) == 1
        line = flex_layout._lines[0]
        assert len(line) == 2

        # Allow for small integer division differences
        assert line[0].calculated_size.width() == pytest.approx(expected_widths[0], abs=1)
        assert line[1].calculated_size.width() == pytest.approx(expected_widths[1], abs=1)

    @patch.object(FluentFlexLayout, 'contentsRect', return_value=QRect(0, 0, 120, 100)) # Container width 120
    def test_layout_row_wrap(self, mock_contents_rect, flex_layout_fixture, mocker): # mock_contents_rect used
        """Test wrapping in ROW direction."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets used
        flex_layout.set_flex_direction(FlexDirection.ROW)
        flex_layout.set_flex_wrap(FlexWrap.WRAP)
        flex_layout.set_gap(10) # Gap between items and lines

        # Widgets with size hint 50x50
        widget1 = self.create_widget(widgets, size_hint=QSize(50, 50))
        widget2 = self.create_widget(widgets, size_hint=QSize(50, 50))
        widget3 = self.create_widget(widgets, size_hint=QSize(50, 50))

        flex_layout.add_widget(widget1)
        flex_layout.add_widget(widget2)
        flex_layout.add_widget(widget3)

        mock_wrapped_signal = mocker.Mock()
        flex_layout.items_wrapped.connect(mock_wrapped_signal)

        flex_layout._perform_layout_update()

        # Container width is 120. Items are 50 wide. Gap is 10.
        # Line 1: widget1 (50) + gap (10) + widget2 (50) = 110. Fits.
        # Line 2: widget3 (50). Fits.
        assert len(flex_layout._lines) == 2
        assert flex_layout._lines[0][0].widget == widget1
        assert flex_layout._lines[0][1].widget == widget2
        assert flex_layout._lines[1][0].widget == widget3

        # Check geometries (approximate positions)
        # Line 1: x=0, y=0, width=50, height=50 (widget1)
        #         x=60, y=0, width=50, height=50 (widget2)
        # Line 2: x=0, y=60, width=50, height=50 (widget3)
        assert widget1.geometry() == QRect(0, 0, 50, 50)
        assert widget2.geometry() == QRect(60, 0, 50, 50)
        assert widget3.geometry() == QRect(0, 60, 50, 50)

        mock_wrapped_signal.emit.assert_called_once_with(True)

    @patch.object(FluentFlexLayout, 'contentsRect', return_value=QRect(0, 0, 300, 100)) # Container width 300
    def test_layout_row_justify_center(self, mock_contents_rect, flex_layout_fixture): # mock_contents_rect used
        """Test justify-content CENTER in ROW direction."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets used
        flex_layout.set_flex_direction(FlexDirection.ROW)
        flex_layout.set_justify_content(JustifyContent.CENTER)
        flex_layout.set_gap(10)

        # Two widgets with size hint 50x50
        widget1 = self.create_widget(widgets, size_hint=QSize(50, 50))
        widget2 = self.create_widget(widgets, size_hint=QSize(50, 50))

        flex_layout.add_widget(widget1)
        flex_layout.add_widget(widget2)

        flex_layout._perform_layout_update()

        # Total size of items + gap = 50 + 10 + 50 = 110
        # Container width = 300
        # Free space = 300 - 110 = 190
        # Center offset = 190 // 2 = 95
        # Widget1 x = 95
        # Widget2 x = 95 + 50 + 10 = 155
        assert widget1.geometry().x() == 95
        assert widget2.geometry().x() == 155

    @patch.object(FluentFlexLayout, 'contentsRect', return_value=QRect(0, 0, 300, 100)) # Container width 300
    def test_layout_row_align_items_center(self, mock_contents_rect, flex_layout_fixture): # mock_contents_rect used
        """Test align-items CENTER in ROW direction."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets used
        flex_layout.set_flex_direction(FlexDirection.ROW)
        flex_layout.set_align_items(AlignItems.CENTER)
        flex_layout.set_gap(0)

        # Widget 1: 50x50, Widget 2: 50x80
        widget1 = self.create_widget(widgets, size_hint=QSize(50, 50))
        widget2 = self.create_widget(widgets, size_hint=QSize(50, 80))

        flex_layout.add_widget(widget1)
        flex_layout.add_widget(widget2)

        flex_layout._perform_layout_update()

        # Line height is determined by the tallest item (widget2, 80)
        # Container height = 100
        # Widget1 height = 50. Center offset = (80 - 50) // 2 = 15
        # Widget2 height = 80. Center offset = (80 - 80) // 2 = 0
        assert widget1.geometry().height() == 50
        assert widget1.geometry().y() == 15 # Centered within the line height (80)

        assert widget2.geometry().height() == 80
        assert widget2.geometry().y() == 0 # Centered within the line height (80)

    @patch.object(FluentFlexLayout, 'contentsRect', return_value=QRect(0, 0, 300, 100)) # Container width 300
    def test_layout_row_align_self(self, mock_contents_rect, flex_layout_fixture): # mock_contents_rect used
        """Test align-self overriding align-items in ROW direction."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets used
        flex_layout.set_flex_direction(FlexDirection.ROW)
        flex_layout.set_align_items(AlignItems.CENTER) # Default alignment is Center
        flex_layout.set_gap(0)

        # Widget 1: 50x50 (should be centered by default)
        # Widget 2: 50x80 (align-self FLEX_END)
        widget1 = self.create_widget(widgets, size_hint=QSize(50, 50))
        widget2 = self.create_widget(widgets, size_hint=QSize(50, 80))

        flex_layout.add_widget(widget1)
        flex_layout.add_widget(widget2, align_self=AlignItems.FLEX_END)

        flex_layout._perform_layout_update()

        # Line height is determined by the tallest item (widget2, 80)
        # Container height = 100
        # Widget1 height = 50. Center offset (due to align-items) = (80 - 50) // 2 = 15
        # Widget2 height = 80. End offset (due to align-self) = 80 - 80 = 0 (relative to line start)
        # The line starts at y=0 in this simple case.
        assert widget1.geometry().height() == 50
        assert widget1.geometry().y() == 15 # Centered within the line height (80)

        assert widget2.geometry().height() == 80
        assert widget2.geometry().y() == 0 # Aligned to the end of the line (y=0 + 80 - 80)

    @patch.object(FluentFlexLayout, 'contentsRect', return_value=QRect(0, 0, 300, 100)) # Container width 300
    def test_layout_row_gap(self, mock_contents_rect, flex_layout_fixture): # mock_contents_rect used
        """Test gap in ROW direction."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets used
        flex_layout.set_flex_direction(FlexDirection.ROW)
        flex_layout.set_gap(10, 20) # row_gap=10, column_gap=20

        # Two widgets with size hint 50x50
        widget1 = self.create_widget(widgets, size_hint=QSize(50, 50))
        widget2 = self.create_widget(widgets, size_hint=QSize(50, 50))

        flex_layout.add_widget(widget1)
        flex_layout.add_widget(widget2)

        flex_layout._perform_layout_update()

        # In ROW, main axis gap is column_gap (20)
        # Widget1 x = 0
        # Widget2 x = 0 + 50 (widget1 width) + 20 (column_gap) = 70
        assert widget1.geometry().x() == 0
        assert widget2.geometry().x() == 70

    @patch.object(FluentFlexLayout, 'contentsRect', return_value=QRect(0, 0, 100, 300)) # Container height 300
    def test_layout_column_gap(self, mock_contents_rect, flex_layout_fixture): # mock_contents_rect used
        """Test gap in COLUMN direction."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets used
        flex_layout.set_flex_direction(FlexDirection.COLUMN)
        flex_layout.set_gap(10, 20) # row_gap=10, column_gap=20

        # Two widgets with size hint 50x50
        widget1 = self.create_widget(widgets, size_hint=QSize(50, 50))
        widget2 = self.create_widget(widgets, size_hint=QSize(50, 50))

        flex_layout.add_widget(widget1)
        flex_layout.add_widget(widget2)

        flex_layout._perform_layout_update()

        # In COLUMN, main axis gap is row_gap (10)
        # Widget1 y = 0
        # Widget2 y = 0 + 50 (widget1 height) + 10 (row_gap) = 60
        assert widget1.geometry().y() == 0
        assert widget2.geometry().y() == 60

    @patch.object(FluentFlexLayout, 'contentsRect', return_value=QRect(0, 0, 120, 100)) # Container width 120
    def test_items_wrapped_signal(self, mock_contents_rect, flex_layout_fixture, mocker): # mock_contents_rect used
        """Test if items_wrapped signal is emitted correctly."""
        flex_layout, widgets, parent_widget = flex_layout_fixture # widgets used
        flex_layout.set_flex_direction(FlexDirection.ROW)
        flex_layout.set_flex_wrap(FlexWrap.WRAP)
        flex_layout.set_gap(10)

        # Widgets with size hint 50x50
        widget1 = self.create_widget(widgets, size_hint=QSize(50, 50))
        widget2 = self.create_widget(widgets, size_hint=QSize(50, 50))
        widget3 = self.create_widget(widgets, size_hint=QSize(50, 50))

        flex_layout.add_widget(widget1)
        flex_layout.add_widget(widget2)
        flex_layout.add_widget(widget3)

        mock_wrapped_signal = mocker.Mock()
        flex_layout.items_wrapped.connect(mock_wrapped_signal)

        # Add widgets - should cause wrapping
        flex_layout._perform_layout_update()
        mock_wrapped_signal.emit.assert_called_once_with(True)

        # Change wrap to NO_WRAP - should not wrap
        mock_wrapped_signal.reset_mock()
        flex_layout.set_flex_wrap(FlexWrap.NO_WRAP)
        flex_layout._perform_layout_update()
        mock_wrapped_signal.emit.assert_called_once_with(False)

        # Change wrap back to WRAP - should wrap again
        mock_wrapped_signal.reset_mock()
        flex_layout.set_flex_wrap(FlexWrap.WRAP)
        flex_layout._perform_layout_update()
        mock_wrapped_signal.emit.assert_called_once_with(True)

    # Note: More exhaustive tests for all combinations of justify-content,
    # align-items, align-content, flex-basis types, and reverse directions
    # would require implementing a significant portion of the flexbox algorithm
    # within the tests themselves or relying heavily on mocking internal
    # calculation methods (_calculate_main_axis_positions, _calculate_line_cross_position, etc.).
    # The tests above cover the core concepts and property interactions.