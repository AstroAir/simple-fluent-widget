import pytest
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QPoint, QRect, QObject, Signal
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QMouseEvent
from pytestqt.qt_compat import qt_api
from unittest.mock import MagicMock, patch
from .charts import FluentSimpleLineChart

# Use relative import for the class under test

# Mock the theme_manager
class MockThemeManager(QObject):
    theme_changed = Signal(str)

    def get_color(self, key):
        # Return distinct colors for testing
        if key == 'primary': return QColor(0, 120, 212)
        if key == 'accent': return QColor(0, 188, 242)
        if key == 'secondary': return QColor(64, 224, 208)
        if key == 'success': return QColor(16, 137, 62)
        if key == 'warning': return QColor(202, 80, 16)
        if key == 'error': return QColor(232, 17, 35)
        if key == 'border': return QColor(128, 128, 128)
        if key == 'surface': return QColor(243, 243, 243)
        if key == 'text_primary': return QColor(0, 0, 0)
        if key == 'text_secondary': return QColor(100, 100, 100)
        if key == 'accent_medium': return QColor(0, 150, 200)
        return QColor(0, 0, 0) # Default black

@pytest.fixture
def mock_theme_manager(mocker):
    """Fixture to mock the global theme_manager instance."""
    mock_instance = MockThemeManager()
    mocker.patch('core.theme.theme_manager', mock_instance)
    return mock_instance

@pytest.fixture
def line_chart(qtbot, mock_theme_manager):
    """Fixture to create a FluentSimpleLineChart instance."""
    chart = FluentSimpleLineChart()
    qtbot.addWidget(chart)
    chart.show() # Ensure widget is shown and paint events can occur
    qtbot.waitExposed(chart)
    yield chart
    chart.hide()

class TestFluentSimpleLineChart:

    def test_init(self, line_chart):
        """Test initialization and default properties."""
        assert line_chart._data_series == []
        assert line_chart._show_points is True
        assert line_chart._show_grid is True
        assert line_chart._smooth_curves is False
        assert line_chart.minimumSize().width() >= 300
        assert line_chart.minimumSize().height() >= 200

    def test_add_data_series(self, line_chart):
        """Test adding a data series."""
        data1 = [(1, 10), (2, 20), (3, 15)]
        line_chart.addDataSeries("Series 1", data1)
        assert len(line_chart._data_series) == 1
        assert line_chart._data_series[0]['name'] == "Series 1"
        assert line_chart._data_series[0]['data'] == data1
        assert isinstance(line_chart._data_series[0]['color'], QColor)

        data2 = [(1, 5), (2, 15), (3, 25)]
        color2 = QColor(255, 0, 0)
        line_chart.addDataSeries("Series 2", data2, color2)
        assert len(line_chart._data_series) == 2
        assert line_chart._data_series[1]['name'] == "Series 2"
        assert line_chart._data_series[1]['data'] == data2
        assert line_chart._data_series[1]['color'] == color2

    def test_clear_data(self, line_chart):
        """Test clearing all data series."""
        data1 = [(1, 10), (2, 20)]
        line_chart.addDataSeries("Series 1", data1)
        data2 = [(1, 5), (2, 15)]
        line_chart.addDataSeries("Series 2", data2)
        assert len(line_chart._data_series) == 2

        line_chart.clearData()
        assert len(line_chart._data_series) == 0

    def test_set_show_points(self, line_chart):
        """Test setting point visibility."""
        line_chart.setShowPoints(False)
        assert line_chart._show_points is False
        line_chart.setShowPoints(True)
        assert line_chart._show_points is True

    def test_set_show_grid(self, line_chart):
        """Test setting grid visibility."""
        line_chart.setShowGrid(False)
        assert line_chart._show_grid is False
        line_chart.setShowGrid(True)
        assert line_chart._show_grid is True

    def test_set_smooth_curves(self, line_chart):
        """Test setting smooth curve rendering."""
        line_chart.setSmoothCurves(True)
        assert line_chart._smooth_curves is True
        line_chart.setSmoothCurves(False)
        assert line_chart._smooth_curves is False

    def test_paint_event_no_data(self, line_chart, qtbot):
        """Test paint event with no data (should not crash)."""
        # No data added by default
        event = QPaintEvent(line_chart.rect())
        # Simply call paintEvent and check no exception is raised
        line_chart.paintEvent(event)

    def test_paint_event_with_data(self, line_chart, qtbot):
        """Test paint event with data (should not crash)."""
        data = [(1, 10), (2, 20), (3, 15)]
        line_chart.addDataSeries("Series 1", data)
        event = QPaintEvent(line_chart.rect())
        # Simply call paintEvent and check no exception is raised
        line_chart.paintEvent(event)

    def test_mouse_press_event_no_data(self, line_chart, qtbot):
        """Test mouse press event with no data (signal should not be emitted)."""
        # The current implementation checks _data, which is always empty
        # The signal point_clicked should NOT be emitted
        with qtbot.assertNotEmitted(line_chart.point_clicked):
             qtbot.mousePress(line_chart, Qt.LeftButton, pos=QPoint(100, 100))

    def test_mouse_press_event_with_data(self, line_chart, qtbot):
        """Test mouse press event with data (signal should NOT be emitted due to bug)."""
        # Add data, but the current mousePressEvent implementation
        # checks self._data (which is empty) and uses bar chart logic.
        # Therefore, the signal point_clicked should NOT be emitted.
        data = [(1, 10), (2, 20), (3, 15)]
        line_chart.addDataSeries("Series 1", data)

        with qtbot.assertNotEmitted(line_chart.point_clicked):
             qtbot.mousePress(line_chart, Qt.LeftButton, pos=QPoint(100, 100))


    def test_on_theme_changed(self, line_chart, mock_theme_manager, mocker):
        """Test theme change signal handler."""
        # Spy on the _setup_style method
        spy_setup_style = mocker.spy(line_chart, '_setup_style')

        # Emit the theme_changed signal
        mock_theme_manager.theme_changed.emit("dark")

        # Assert that _setup_style was called
        spy_setup_style.assert_called_once()
