import pytest
import sys
import os
import math
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QTimer, QPropertyAnimation, QByteArray, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPaintEvent, QMouseEvent, QWheelEvent
from PySide6.QtTest import QTest
from core.theme import theme_manager as real_theme_manager
from core.enhanced_base import FluentLayoutBuilder

# Add the parent directory to the path for relative import if necessary
# Assuming the test file is components/data/test_visualization.py
# and the module is components/data/visualization.py
# The parent directory 'data' is a package (__init__.py exists)
# So we can use relative import
try:
    # Mock theme_manager if not available to allow tests to run
    class MockThemeManager:
        def get_color(self, color_name: str) -> QColor:
            # Return a default color or a color based on name for testing
            color_map = {
                'surface': QColor(243, 242, 241), # f3f2f1
                'border': QColor(225, 223, 221),  # e1dfdd
                'primary': QColor(0, 120, 212),   # 0078d4
                'accent': QColor(0, 153, 188),    # 0099bc
                'text_primary': QColor(50, 49, 48), # 323130
            }
            return color_map.get(color_name, QColor(0, 0, 0)) # Default to black
        
        def get_font(self, font_name: str) -> str:
            return "Arial" # Default font
            
        @property
        def theme_changed(self) -> Signal:
            # Create a dummy signal for testing connections
            if not hasattr(self, '_theme_changed_signal'):
                 self._theme_changed_signal = Signal()
            return self._theme_changed_signal

    # Attempt to import the real theme_manager, fallback to mock
    try:
        theme_manager = real_theme_manager
    except ImportError:
        theme_manager = MockThemeManager()
        print("Warning: core.theme not found, using mock theme_manager for visualization tests.")


    # Attempt to import FluentLayoutBuilder, fallback to simple QVBoxLayout
    try:
    except ImportError:
        class FluentLayoutBuilder:
            @staticmethod
            def create_vertical_layout():
                return QVBoxLayout()
        print("Warning: core.enhanced_base not found, using simple QVBoxLayout for visualization tests.")


    from .visualization import (
        FluentTreeMapItem, FluentTreeMap, TreeMapConfig, TreeMapLayout,
        FluentNetworkNode, FluentNetworkEdge, FluentNetworkGraph, NetworkConfig, NetworkLayout,
        NodeID, PositionTuple
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


class TestFluentTreeMapItem:

    def test_initialization(self, qapp):
        """Test FluentTreeMapItem initialization."""
        item = FluentTreeMapItem("Root", 100)
        assert item.label == "Root"
        assert item.value == 100.0
        assert item.color is None
        assert item.children == []
        assert item.parent is None
        assert item.rect == QRectF()

        color = QColor(255, 0, 0)
        item_with_color = FluentTreeMapItem("Node", 50, color=color)
        assert item_with_color.color == color

    def test_add_child(self, qapp):
        """Test add_child method."""
        root = FluentTreeMapItem("Root", 100)
        child1 = FluentTreeMapItem("Child 1", 30)
        child2 = FluentTreeMapItem("Child 2", 70)

        root.add_child(child1)
        root.add_child(child2)

        assert len(root.children) == 2
        assert root.children[0] == child1
        assert root.children[1] == child2
        assert child1.parent == root
        assert child2.parent == root

    def test_total_value(self, qapp):
        """Test total_value method."""
        root = FluentTreeMapItem("Root", 0) # Root value doesn't contribute to children's total
        child1 = FluentTreeMapItem("Child 1", 30)
        child2 = FluentTreeMapItem("Child 2", 70)
        grandchild = FluentTreeMapItem("Grandchild", 20)

        root.add_child(child1)
        child1.add_child(grandchild)
        root.add_child(child2)

        assert grandchild.total_value() == 20.0
        assert child1.total_value() == 20.0 # Only grandchild value
        assert child2.total_value() == 70.0
        assert root.total_value() == 90.0 # Sum of children's total values (20 + 70)

        # Test item with no children
        single_item = FluentTreeMapItem("Single", 50)
        assert single_item.total_value() == 50.0

    def test_depth(self, qapp):
        """Test depth method."""
        root = FluentTreeMapItem("Root", 100)
        child1 = FluentTreeMapItem("Child 1", 30)
        child2 = FluentTreeMapItem("Child 2", 70)
        grandchild = FluentTreeMapItem("Grandchild", 20)

        root.add_child(child1)
        child1.add_child(grandchild)
        root.add_child(child2)

        assert root.depth() == 0
        assert child1.depth() == 1
        assert child2.depth() == 1
        assert grandchild.depth() == 2


class TestFluentTreeMap:

    def test_initialization_default(self, qapp, widget_cleanup):
        """Test FluentTreeMap initialization with default config."""
        treemap = FluentTreeMap()
        widget_cleanup.append(treemap)

        assert isinstance(treemap, FluentTreeMap)
        assert isinstance(treemap, QWidget)
        assert isinstance(treemap._config, TreeMapConfig)
        assert treemap._config.layout_algorithm == TreeMapLayout.SQUARIFIED
        assert treemap._root_item is None
        assert treemap._current_view is None
        assert isinstance(treemap._layout, QVBoxLayout) # Or FluentLayoutBuilder result
        assert treemap.minimumSize().width() == 200
        assert treemap.minimumSize().height() == 200
        assert hasattr(treemap, 'itemClicked') # Check signal exists

    def test_initialization_config(self, qapp, widget_cleanup):
        """Test FluentTreeMap initialization with custom config."""
        config = TreeMapConfig(
            padding=5,
            layout_algorithm=TreeMapLayout.SLICE_AND_DICE,
            enable_drill_down=False
        )
        treemap = FluentTreeMap(config=config)
        widget_cleanup.append(treemap)

        assert treemap._config.padding == 5
        assert treemap._config.layout_algorithm == TreeMapLayout.SLICE_AND_DICE
        assert treemap._config.enable_drill_down is False

    def test_set_data(self, qapp, widget_cleanup):
        """Test set_data method."""
        treemap = FluentTreeMap()
        widget_cleanup.append(treemap)

        root = FluentTreeMapItem("Root", 100)
        child1 = root.add_child(FluentTreeMapItem("Child 1", 30))

        treemap