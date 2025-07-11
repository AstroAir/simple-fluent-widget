import sys
import pytest
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtTest import QTest

# Assuming the provided code is in a file named `fluent_layout_components.py`
from components.layout.additional_layouts import (
    FluentUniformGrid,
    FluentMasonryLayout,
    FluentAdaptiveLayout,
    FluentCanvas,
)

# Fixture to manage the QApplication instance for the test session


@pytest.fixture(scope="session")
def qapp():
    """Creates a QApplication instance for the entire test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

# --- Test FluentUniformGrid ---


@pytest.fixture
def uniform_grid_setup(qapp):
    """Fixture for setting up the FluentUniformGrid tests."""
    parent = QWidget()
    parent.resize(800, 600)
    layout = FluentUniformGrid(parent=parent)
    parent.setLayout(layout)
    yield parent, layout
    parent.deleteLater()


class TestFluentUniformGrid:
    """Unit tests for the FluentUniformGrid class using pytest."""

    def test_initialization(self, uniform_grid_setup):
        """Test the initial state of the layout."""
        parent, layout = uniform_grid_setup
        assert layout.get_rows() == 0
        assert layout.get_columns() == 0
        assert layout.get_first_column() == 0
        assert len(layout._items) == 0

    def test_add_and_remove_widget(self, uniform_grid_setup):
        """Test adding and removing widgets."""
        parent, layout = uniform_grid_setup
        widget1 = QLabel("Widget 1")
        widget2 = QLabel("Widget 2")

        layout.add_widget(widget1)
        assert len(layout._items) == 1
        assert widget1 in layout._items

        layout.add_widget(widget2)
        assert len(layout._items) == 2
        assert widget2 in layout._items

        layout.remove_widget(widget1)
        assert len(layout._items) == 1
        assert widget1 not in layout._items
        assert widget1.parent() is None

    def test_insert_widget(self, uniform_grid_setup):
        """Test inserting a widget at a specific index."""
        parent, layout = uniform_grid_setup
        widget1 = QLabel("Widget 1")
        widget2 = QLabel("Widget 2")
        widget3 = QLabel("Widget 3")

        layout.add_widget(widget1)
        layout.add_widget(widget3)
        layout.insert_widget(1, widget2)

        assert len(layout._items) == 3
        assert layout._items == [widget1, widget2, widget3]

    def test_grid_calculation_auto(self, uniform_grid_setup):
        """Test automatic grid dimension calculation."""
        parent, layout = uniform_grid_setup
        for i in range(9):
            layout.add_widget(QLabel(f"Widget {i+1}"))

        rows, cols = layout._calculate_grid_dimensions()
        assert rows == 3
        assert cols == 3

    def test_grid_calculation_fixed_rows(self, uniform_grid_setup):
        """Test grid calculation with a fixed number of rows."""
        parent, layout = uniform_grid_setup
        layout.set_rows(2)
        for i in range(8):
            layout.add_widget(QLabel(f"Widget {i+1}"))

        rows, cols = layout._calculate_grid_dimensions()
        assert rows == 2
        assert cols == 4

    def test_grid_calculation_fixed_columns(self, uniform_grid_setup):
        """Test grid calculation with a fixed number of columns."""
        parent, layout = uniform_grid_setup
        layout.set_columns(3)
        for i in range(7):
            layout.add_widget(QLabel(f"Widget {i+1}"))

        rows, cols = layout._calculate_grid_dimensions()
        assert rows == 3
        assert cols == 3

    def test_layout_update(self, uniform_grid_setup):
        """Test if the widgets are positioned correctly."""
        parent, layout = uniform_grid_setup
        layout.set_rows(2)
        layout.set_columns(2)
        layout.set_spacing(10)

        widgets = [QLabel("1"), QLabel("2"), QLabel("3"), QLabel("4")]
        for w in widgets:
            layout.add_widget(w)

        layout._perform_layout_update()
        QTest.qWait(100)

        # 800x600 parent, 2x2 grid, 10 spacing
        # Cell Width: (800 - 10) / 2 = 395
        # Cell Height: (600 - 10) / 2 = 295
        assert widgets[0].geometry() == QRect(0, 0, 395, 295)
        assert widgets[1].geometry() == QRect(405, 0, 395, 295)
        assert widgets[2].geometry() == QRect(0, 305, 395, 295)
        assert widgets[3].geometry() == QRect(405, 305, 395, 295)


# --- Test FluentMasonryLayout ---

@pytest.fixture
def masonry_layout_setup(qapp):
    """Fixture for setting up the FluentMasonryLayout tests."""
    parent = QWidget()
    parent.resize(830, 600)  # Width for 4 columns of 200 with 10 spacing
    layout = FluentMasonryLayout(parent=parent, column_width=200)
    layout.set_spacing(10)
    parent.setLayout(layout)
    yield parent, layout
    parent.deleteLater()


class TestFluentMasonryLayout:
    """Unit tests for the FluentMasonryLayout class using pytest."""

    def test_initialization(self, masonry_layout_setup):
        """Test initial state."""
        parent, layout = masonry_layout_setup
        assert layout.get_column_width() == 200
        assert len(layout._items) == 0

    def test_add_and_remove_widget(self, masonry_layout_setup):
        """Test adding and removing widgets."""
        parent, layout = masonry_layout_setup
        widget = QLabel("Test")
        layout.add_widget(widget)
        assert len(layout._items) == 1
        layout.remove_widget(widget)
        assert len(layout._items) == 0
        assert widget.parent() is None

    def test_layout_logic(self, masonry_layout_setup):
        """Test the masonry layout logic."""
        parent, layout = masonry_layout_setup
        widgets = [
            QLabel("Short"),
            QLabel("Taller\nWidget"),
            QLabel("Medium"),
            QLabel("Another\nTall\nOne"),
            QLabel("Small"),
        ]
        # Set fixed heights for predictable testing
        widgets[0].setFixedSize(200, 100)
        widgets[1].setFixedSize(200, 200)
        widgets[2].setFixedSize(200, 150)
        widgets[3].setFixedSize(200, 250)
        widgets[4].setFixedSize(200, 80)

        for w in widgets:
            layout.add_widget(w)

        QTest.qWait(100)  # Wait for the throttled layout update

        # Expected layout (spacing=10, col_width=200)
        # Col 1: 100 | Col 2: 200 | Col 3: 150 | Col 4: 250
        # Next widget goes to Col 1.
        assert layout.get_column_count() == 4
        assert widgets[0].pos().x() == 0
        assert widgets[1].pos().x() == 210
        assert widgets[2].pos().x() == 420
        assert widgets[3].pos().x() == 630
        assert widgets[4].pos().x() == 0      # Shortest column
        assert widgets[4].pos().y() == 110    # Below first widget + spacing

# --- Test FluentAdaptiveLayout ---


@pytest.fixture
def adaptive_layout_setup(qapp):
    """Fixture for setting up the FluentAdaptiveLayout tests."""
    parent = QWidget()
    layout = FluentAdaptiveLayout(parent=parent)
    parent.setLayout(layout)
    for i in range(4):
        layout.add_widget(QLabel(f"Widget {i+1}"))
    yield parent, layout
    parent.deleteLater()


class TestFluentAdaptiveLayout:
    """Unit tests for the FluentAdaptiveLayout class using pytest."""

    @pytest.mark.parametrize("size, expected_type, expected_props", [
        (QSize(400, 600), 'stack', {'direction': 'vertical'}),
        (QSize(800, 600), 'grid', {'columns': 2}),
        (QSize(1400, 800), 'grid', {'columns': 4}),
    ])
    def test_breakpoint_changes(self, adaptive_layout_setup, size, expected_type, expected_props):
        """Test layout changes based on breakpoints."""
        parent, layout = adaptive_layout_setup
        parent.resize(size)
        layout.resizeEvent(None)  # Trigger update
        QTest.qWait(100)

        current_breakpoint = layout.get_current_breakpoint()
        strategy = layout._layout_strategies[current_breakpoint]

        assert strategy['layout_type'] == expected_type
        for prop, value in expected_props.items():
            assert strategy[prop] == value

# --- Test FluentCanvas ---


@pytest.fixture
def canvas_setup(qapp):
    """Fixture for setting up the FluentCanvas tests."""
    parent = QWidget()
    parent.resize(800, 600)
    layout = FluentCanvas(parent=parent)
    parent.setLayout(layout)
    yield parent, layout
    parent.deleteLater()


class TestFluentCanvas:
    """Unit tests for the FluentCanvas class using pytest."""

    def test_add_and_remove_widget(self, canvas_setup):
        """Test adding a widget with specific geometry."""
        parent, layout = canvas_setup
        widget = QLabel("Canvas Widget")
        layout.add_widget(widget, x=50, y=100, width=150, height=80)

        assert widget in layout._positioned_widgets
        assert widget.geometry() == QRect(50, 100, 150, 80)

        layout.remove_widget(widget)
        assert widget not in layout._positioned_widgets
        assert widget.parent() is None

    def test_widget_modification(self, canvas_setup):
        """Test modifying widget properties."""
        parent, layout = canvas_setup
        widget = QLabel("Movable")
        layout.add_widget(widget, x=10, y=10)

        layout.set_widget_position(widget, 20, 30)
        assert layout.get_widget_position(widget) == (20, 30)
        assert widget.pos().x() == 20
        assert widget.pos().y() == 30

        layout.set_widget_size(widget, 200, 100)
        assert layout.get_widget_size(widget) == (200, 100)
        assert widget.size() == QSize(200, 100)

        layout.set_widget_geometry(widget, 50, 60, 250, 150)
        assert widget.geometry() == QRect(50, 60, 250, 150)

    def test_z_index(self, canvas_setup):
        """Test the z-index (stacking order) of widgets."""
        parent, layout = canvas_setup
        widget1 = QLabel("Back")
        widget2 = QLabel("Front")
        widget3 = QLabel("Middle")

        layout.add_widget(widget1, z_index=0)
        layout.add_widget(widget2, z_index=2)
        layout.add_widget(widget3, z_index=1)
        layout._update_z_order()

        assert layout._z_order == [widget1, widget3, widget2]

        layout.set_z_index(widget1, 3)
        layout._update_z_order()
        assert layout._z_order == [widget3, widget2, widget1]

    def test_animated_move(self, canvas_setup):
        """Test the animated movement of a widget."""
        parent, layout = canvas_setup
        widget = QLabel("Animator")
        layout.add_widget(widget, x=0, y=0, width=50, height=50)

        layout.move_widget_animated(widget, 100, 150, duration=50)
        QTest.qWait(100)  # Wait for animation to finish

        assert widget.geometry() == QRect(100, 150, 50, 50)
        assert layout._positioned_widgets[widget] == QRect(100, 150, 50, 50)
