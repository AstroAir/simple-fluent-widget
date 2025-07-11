import pytest
import sys
import os
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import QMouseEvent, QColor
from PySide6.QtTest import QTest
import math
from .advanced_charts import FluentScatterChart
from core.theme import theme_manager
from core.theme import FluentThemeManager

# Add the project root to the path for relative imports
# Assuming the test file is in components/data/charts/
# and the core directory is at the project root.
# This might need adjustment based on the actual project structure.
# A more robust way might involve setting PYTHONPATH or using tox.
# For this specific request, we'll assume the structure allows
# a relative import from the parent package 'charts'.
# The __init__.py in the parent directory makes 'charts' a package.

# Relative import from the same package
try:
    # Assuming theme_manager is in core.theme relative to the project root
    # Need to adjust import path if core is not directly under project root
    # Example: from ....core.theme import theme_manager
    # Let's assume core is at the same level as components
    # The example test file uses `from core.theme import FluentThemeManager`
    # which implies `core` is a top-level package.
    # Given the file path d:\Project\simple-fluent-widget\components\data\charts\advanced_charts.py
    # and the test file path components/data/charts/test_advanced_charts.py
    # The import should be relative to the package root, which is likely 'simple-fluent-widget'.
    # So, `core.theme` is correct if simple-fluent-widget is the package root.
    # However, relative import `from .advanced_charts` works because they are in the same package.
    # Importing theme_manager relatively from core might be tricky without knowing the exact package structure.
    # Let's assume theme_manager is accessible via the same mechanism as in the example test file.
    # The example uses `from core.theme import FluentThemeManager`.
    # Let's try importing theme_manager directly as it's used in the class.
except ImportError as e:
    pytest.skip(f"Could not import necessary modules: {e}", allow_module_level=True)


@pytest.fixture(scope="session")
def qapp():
    """Pytest fixture for QApplication."""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    # Ensure theme_manager is initialized if needed by the component's __init__
    # The component code uses `theme_manager` directly, assuming it's a singleton or globally accessible.
    # The example test initializes FluentThemeManager, which likely sets up the global theme_manager.
    # Let's ensure it's initialized here.
    if not hasattr(theme_manager, '_initialized') or not theme_manager._initialized:
         # Assuming FluentThemeManager exists and initializes the singleton
         FluentThemeManager() # Initialize the singleton
         theme_manager._initialized = True # Mark as initialized to avoid re-init

    yield app
    # No need to quit app in session scope for pytest-qt


@pytest.fixture
def scatter_chart(qapp):
    """Pytest fixture for FluentScatterChart."""
    chart = FluentScatterChart()
    chart.resize(400, 300) # Give it a size for layout calculations
    yield chart
    # Clean up the widget after the test
    chart.close()
    del chart
    qapp.processEvents() # Process any pending events


def get_screen_pos(chart_widget: FluentScatterChart, x_val: float, y_val: float) -> QPointF | None:
    """Helper to calculate screen position of a data point."""
    margin = 60
    chart_rect = QRectF(margin, margin, chart_widget.width() - 2 * margin, chart_widget.height() - 2 * margin)
    x_range = chart_widget.x_range
    y_range = chart_widget.y_range

    # Handle zero range to avoid division by zero
    if x_range[1] == x_range[0] or y_range[1] == y_range[0]:
        return None

    x_ratio = (x_val - x_range[0]) / (x_range[1] - x_range[0])
    y_ratio = (y_val - y_range[0]) / (y_range[1] - y_range[0])

    # Clamp ratios to [0, 1] to handle points outside the current range
    x_ratio = max(0.0, min(1.0, x_ratio))
    y_ratio = max(0.0, min(1.0, y_ratio))


    screen_x = chart_rect.left() + x_ratio * chart_rect.width()
    screen_y = chart_rect.bottom() - y_ratio * chart_rect.height() # Y-axis is inverted in screen coordinates

    return QPointF(screen_x, screen_y)


def test_init(scatter_chart):
    """Test initialization of FluentScatterChart."""
    assert isinstance(scatter_chart, FluentScatterChart)
    assert scatter_chart.data_points == []
    assert scatter_chart.x_range == (0, 100)
    assert scatter_chart.y_range == (0, 100)
    assert scatter_chart.show_trend_line is False
    assert scatter_chart.show_grid is True
    assert scatter_chart.point_size_range == (5, 20)
    assert scatter_chart.selected_points == set()
    assert scatter_chart.hover_point is None
    assert scatter_chart.minimumSize().width() >= 300
    assert scatter_chart.minimumSize().height() >= 200

def test_add_point(scatter_chart):
    """Test adding a single data point."""
    initial_count = len(scatter_chart.data_points)
    scatter_chart.add_point(10, 20, size=15, label="Point A")
    assert len(scatter_chart.data_points) == initial_count + 1
    point = scatter_chart.data_points[-1]
    assert point['x'] == 10
    assert point['y'] == 20
    assert point['size'] == 15
    assert point['label'] == "Point A"
    assert isinstance(point['color'], QColor) # Check default color is assigned

def test_set_data(scatter_chart):
    """Test setting multiple data points and auto-ranging."""
    test_data = [
        {'x': 5, 'y': 50, 'size': 10, 'label': 'A'},
        {'x': 15, 'y': 70, 'size': 12, 'label': 'B'},
        {'x': 25, 'y': 30, 'size': 8, 'label': 'C'}
    ]
    scatter_chart.set_data(test_data)
    assert len(scatter_chart.data_points) == 3
    assert scatter_chart.data_points == test_data
    # Check auto-calculated ranges
    assert scatter_chart.x_range == (5, 25)
    assert scatter_chart.y_range == (30, 70)

    # Test setting empty data
    scatter_chart.set_data([])
    assert scatter_chart.data_points == []
    # Ranges should ideally reset or handle empty state gracefully,
    # current implementation keeps the last range or default (0,100) if initially empty.
    # Let's check if it doesn't crash and ranges are handled.
    # The code sets range to (min, max) of empty list, which would raise ValueError.
    # Let's check the fix in the component code (added check for empty list).
    # After fix, it should be (0,0) for empty data.
    assert scatter_chart.x_range == (0, 0)
    assert scatter_chart.y_range == (0, 0)


def test_clear_data(scatter_chart):
    """Test clearing all data points."""
    test_data = [{'x': 10, 'y': 20}, {'x': 30, 'y': 40}]
    scatter_chart.set_data(test_data)
    scatter_chart.selected_points = {0} # Select a point

    scatter_chart.clear_data()
    assert scatter_chart.data_points == []
    assert scatter_chart.selected_points == set()

def test_mouse_move_hover(scatter_chart, qtbot):
    """Test mouse move for hover effects."""
    test_data = [
        {'x': 10, 'y': 20, 'size': 10, 'label': 'A'},
        {'x': 80, 'y': 90, 'size': 10, 'label': 'B'}
    ]
    scatter_chart.set_data(test_data)
    scatter_chart.show() # Widget must be shown to get valid geometry and process events
    qtbot.addWidget(scatter_chart) # Manage widget lifecycle with qtbot

    # Calculate screen position of the first point
    point1_pos = get_screen_pos(scatter_chart, test_data[0]['x'], test_data[0]['y'])
    assert point1_pos is not None

    # Simulate mouse move over the first point
    with qtbot.waitSignal(scatter_chart.pointHovered, timeout=1000) as blocker:
        qtbot.mouseMove(scatter_chart, point1_pos.toPoint())

    assert scatter_chart.hover_point == 0
    assert blocker.args == (test_data[0],) # Check signal arguments

    # Calculate screen position of the second point
    point2_pos = get_screen_pos(scatter_chart, test_data[1]['x'], test_data[1]['y'])
    assert point2_pos is not None

    # Simulate mouse move over the second point
    with qtbot.waitSignal(scatter_chart.pointHovered, timeout=1000) as blocker:
         qtbot.mouseMove(scatter_chart, point2_pos.toPoint())

    assert scatter_chart.hover_point == 1
    assert blocker.args == (test_data[1],) # Check signal arguments

    # Simulate mouse move away from points (e.g., outside chart area)
    outside_pos = QPointF(scatter_chart.width() - 10, scatter_chart.height() - 10)
    qtbot.mouseMove(scatter_chart, outside_pos.toPoint())
    qtbot.wait(50) # Give event loop time to process

    assert scatter_chart.hover_point is None

    # Test hover with no data
    scatter_chart.clear_data()
    qtbot.mouseMove(scatter_chart, point1_pos.toPoint()) # Simulate move where a point used to be
    qtbot.wait(50)
    assert scatter_chart.hover_point is None # Should remain None

def test_mouse_press_click_single(scatter_chart, qtbot):
    """Test mouse click for single point selection."""
    test_data = [
        {'x': 10, 'y': 20, 'size': 10, 'label': 'A'},
        {'x': 80, 'y': 90, 'size': 10, 'label': 'B'}
    ]
    scatter_chart.set_data(test_data)
    scatter_chart.show()
    qtbot.addWidget(scatter_chart)

    # Calculate screen position of the first point
    point1_pos = get_screen_pos(scatter_chart, test_data[0]['x'], test_data[0]['y'])
    assert point1_pos is not None

    # Simulate mouse move to hover over the point first
    qtbot.mouseMove(scatter_chart, point1_pos.toPoint())
    qtbot.wait(50) # Wait for hover to register
    assert scatter_chart.hover_point == 0

    # Simulate mouse click on the hovered point
    with qtbot.waitSignal(scatter_chart.pointClicked, timeout=1000) as clicked_blocker, \
         qtbot.waitSignal(scatter_chart.selectionChanged, timeout=1000) as selection_blocker:
        qtbot.mousePress(scatter_chart, Qt.LeftButton, pos=point1_pos.toPoint())
        qtbot.mouseRelease(scatter_chart, Qt.LeftButton, pos=point1_pos.toPoint())

    assert scatter_chart.selected_points == {0}
    assert clicked_blocker.args == (test_data[0],)
    assert selection_blocker.args == ([test_data[0]],)

    # Simulate click on the second point (single select should replace)
    point2_pos = get_screen_pos(scatter_chart, test_data[1]['x'], test_data[1]['y'])
    assert point2_pos is not None
    qtbot.mouseMove(scatter_chart, point2_pos.toPoint())
    qtbot.wait(50)
    assert scatter_chart.hover_point == 1

    with qtbot.waitSignal(scatter_chart.pointClicked, timeout=1000) as clicked_blocker, \
         qtbot.waitSignal(scatter_chart.selectionChanged, timeout=1000) as selection_blocker:
        qtbot.mousePress(scatter_chart, Qt.LeftButton, pos=point2_pos.toPoint())
        qtbot.mouseRelease(scatter_chart, Qt.LeftButton, pos=point2_pos.toPoint())

    assert scatter_chart.selected_points == {1}
    assert clicked_blocker.args == (test_data[1],)
    assert selection_blocker.args == ([test_data[1]],)

def test_mouse_press_click_multi(scatter_chart, qtbot):
    """Test mouse click with Ctrl modifier for multi-point selection."""
    test_data = [
        {'x': 10, 'y': 20, 'size': 10, 'label': 'A'},
        {'x': 40, 'y': 50, 'size': 10, 'label': 'B'},
        {'x': 80, 'y': 90, 'size': 10, 'label': 'C'}
    ]
    scatter_chart.set_data(test_data)
    scatter_chart.show()
    qtbot.addWidget(scatter_chart)

    point1_pos = get_screen_pos(scatter_chart, test_data[0]['x'], test_data[0]['y'])
    point2_pos = get_screen_pos(scatter_chart, test_data[1]['x'], test_data[1]['y'])
    point3_pos = get_screen_pos(scatter_chart, test_data[2]['x'], test_data[2]['y'])
    assert point1_pos and point2_pos and point3_pos

    # Click point 1 (single select initially)
    qtbot.mouseMove(scatter_chart, point1_pos.toPoint())
    qtbot.wait(50)
    with qtbot.waitSignal(scatter_chart.selectionChanged, timeout=1000):
        qtbot.mousePress(scatter_chart, Qt.LeftButton, pos=point1_pos.toPoint())
        qtbot.mouseRelease(scatter_chart, Qt.LeftButton, pos=point1_pos.toPoint())
    assert scatter_chart.selected_points == {0}

    # Ctrl+Click point 2 (add to selection)
    qtbot.mouseMove(scatter_chart, point2_pos.toPoint())
    qtbot.wait(50)
    with qtbot.waitSignal(scatter_chart.selectionChanged, timeout=1000):
        qtbot.mousePress(scatter_chart, Qt.LeftButton, Qt.ControlModifier, pos=point2_pos.toPoint())
        qtbot.mouseRelease(scatter_chart, Qt.LeftButton, Qt.ControlModifier, pos=point2_pos.toPoint())
    assert scatter_chart.selected_points == {0, 1}

    # Ctrl+Click point 3 (add to selection)
    qtbot.mouseMove(scatter_chart, point3_pos.toPoint())
    qtbot.wait(50)
    with qtbot.waitSignal(scatter_chart.selectionChanged, timeout=1000):
        qtbot.mousePress(scatter_chart, Qt.LeftButton, Qt.ControlModifier, pos=point3_pos.toPoint())
        qtbot.mouseRelease(scatter_chart, Qt.LeftButton, Qt.ControlModifier, pos=point3_pos.toPoint())
    assert scatter_chart.selected_points == {0, 1, 2}

    # Ctrl+Click point 1 again (remove from selection)
    qtbot.mouseMove(scatter_chart, point1_pos.toPoint())
    qtbot.wait(50)
    with qtbot.waitSignal(scatter_chart.selectionChanged, timeout=1000):
        qtbot.mousePress(scatter_chart, Qt.LeftButton, Qt.ControlModifier, pos=point1_pos.toPoint())
        qtbot.mouseRelease(scatter_chart, Qt.LeftButton, Qt.ControlModifier, pos=point1_pos.toPoint())
    assert scatter_chart.selected_points == {1, 2}

def test_paint_event_no_data(scatter_chart, qtbot):
    """Test paintEvent with no data (should not crash)."""
    scatter_chart.show()
    qtbot.addWidget(scatter_chart)
    # Simply calling update and processing events should not raise an exception
    scatter_chart.update()
    qtbot.wait(50) # Give paint event time to process

def test_paint_event_with_data(scatter_chart, qtbot):
    """Test paintEvent with data (should not crash)."""
    test_data = [{'x': 10, 'y': 20}, {'x': 80, 'y': 90}]
    scatter_chart.set_data(test_data)
    scatter_chart.show()
    qtbot.addWidget(scatter_chart)
    # Simply calling update and processing events should not raise an exception
    scatter_chart.update()
    qtbot.wait(50) # Give paint event time to process

def test_trend_line_property(scatter_chart):
    """Test setting show_trend_line property."""
    assert scatter_chart.show_trend_line is False
    scatter_chart.show_trend_line = True
    assert scatter_chart.show_trend_line is True
    scatter_chart.show_trend_line = False
    assert scatter_chart.show_trend_line is False

# Note: Testing if draw_trend_line is *actually* called during paintEvent
# would require mocking QPainter or the draw_trend_line method, which is
# more complex and often considered integration testing rather than unit testing.
# We test the property setting and assume paintEvent uses the property correctly.

def test_apply_theme(scatter_chart):
    """Test apply_theme method."""
    # This test checks if the stylesheet is updated.
    # It relies on theme_manager providing a color name.
    scatter_chart.apply_theme()
    stylesheet = scatter_chart.styleSheet()
    assert f"background-color: {theme_manager.get_color('surface').name()};" in stylesheet
    assert f"border: 1px solid {theme_manager.get_color('border').name()};" in stylesheet
    assert "border-radius: 8px;" in stylesheet
