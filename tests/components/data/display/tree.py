import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any
from PySide6.QtWidgets import QApplication, QWidget, QTreeWidgetItem, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPoint, QByteArray, QAbstractItemView
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtTest import QTest
from core.theme import FluentThemeManager

# filepath: components/data/display/test_tree.py


# Add the project root to the path for core imports if necessary
# Assuming the test file is in components/data/display/
# and core is in the parent directory of components
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the classes to be tested using relative import
try:
    from .tree import (
        FluentTreeWidget, FluentHierarchicalView, FluentOrgChart,
        TreeConfiguration, TreeItemData, NodeData, TreeState,
        _setup_enhanced_styles # Need to mock this or ensure theme_manager works
    )
    # Mock theme_manager if it's not a real dependency or for isolation
    # Assuming core.theme.theme_manager exists and has get_color and theme_changed
    # Create a dummy theme manager for tests if the real one isn't fully functional
    class DummyThemeManager:
        def get_color(self, color_name: str) -> QColor:
            colors = {
                'surface': QColor(Qt.GlobalColor.white),
                'border': QColor(Qt.GlobalColor.gray),
                'primary': QColor(Qt.GlobalColor.blue),
                'accent_light': QColor(Qt.GlobalColor.lightGray),
                'text_primary': QColor(Qt.GlobalColor.black),
                'text_secondary': QColor(Qt.GlobalColor.darkGray),
                'background': QColor(Qt.GlobalColor.lightGray),
                'primary_dark': QColor(Qt.GlobalColor.darkBlue),
                'accent_medium': QColor(Qt.GlobalColor.darkCyan),
            }
            return colors.get(color_name, QColor(Qt.GlobalColor.black))

        @property
        def theme_changed(self):
            # Return a dummy signal
            class DummySignal:
                def connect(self, slot): pass
                def disconnect(self, slot): pass
            return DummySignal()

    # Replace the real theme_manager with the dummy one for tests
    # This requires patching the import or the object after import
    # A simpler approach for unit tests is to mock the dependency where it's used
    # However, the class uses it directly in _setup_style, so patching might be needed
    # Let's try patching theme_manager in the test methods that call _setup_style
    # Or, assume FluentThemeManager is importable and functional enough for basic color getting.
    # The test example imports FluentThemeManager, so let's assume it's available.
    # If it causes issues, we'll need to patch.

    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import components for testing: {e}")
    COMPONENTS_AVAILABLE = False


@unittest.skipUnless(COMPONENTS_AVAILABLE, "Components not available")
class TestFluentTreeWidget(unittest.TestCase):
    """Unit tests for FluentTreeWidget"""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up each test"""
        self.widget = FluentTreeWidget()
        self.widgets = [self.widget] # Keep track for cleanup

    def tearDown(self):
        """Clean up after each test"""
        for widget in self.widgets:
            if widget and hasattr(widget, 'close'):
                widget.close()
        QApplication.processEvents()

    def test_init(self):
        """Test initialization and default config"""
        self.assertIsInstance(self.widget, FluentTreeWidget)
        self.assertIsInstance(self.widget._config, TreeConfiguration)
        self.assertEqual(self.widget.current_state, TreeState.IDLE)
        self.assertTrue(self.widget.isAnimated())
        self.assertEqual(self.widget.indentation(), 20)
        self.assertTrue(self.widget.rootIsDecorated())
        self.assertTrue(self.widget.uniformRowHeights())
        self.assertEqual(self.widget.selectionMode(), QAbstractItemView.SelectionMode.ExtendedSelection)
        self.assertTrue(self.widget.expandsOnDoubleClick())
        self.assertIsNotNone(self.widget.graphicsEffect())
        self.assertIsInstance(self.widget.graphicsEffect(), QGraphicsOpacityEffect)

    def test_set_header_labels(self):
        """Test setting header labels"""
        headers = ["Col1", "Col2", "Col3"]
        self.widget.setHeaderLabels(headers)
        self.assertEqual(self.widget.columnCount(), 3)
        self.assertEqual(self.widget.headerItem().text(0), "Col1")
        self.assertEqual(self.widget.headerItem().text(1), "Col2")
        self.assertEqual(self.widget.headerItem().text(2), "Col3")

    def test_add_top_level_item_from_dict(self):
        """Test adding a top-level item from dict"""
        item_data: TreeItemData = {"text": "Root Item", "data": 123, "checkable": True}
        item = self.widget.addTopLevelItemFromDict(item_data)

        self.assertIsInstance(item, QTreeWidgetItem)
        self.assertEqual(self.widget.topLevelItemCount(), 1)
        self.assertEqual(item.text(0), "Root Item")
        self.assertEqual(item.data(0, Qt.ItemDataRole.UserRole), 123)
        self.assertEqual(item.checkState(0), Qt.CheckState.Unchecked)
        self.assertIn(item, self.widget._item_cache)
        self.assertEqual(self.widget._item_cache[item]['text'], "Root Item")

    def test_add_child_item(self):
        """Test adding a child item"""
        root_data: TreeItemData = {"text": "Root"}
        root_item = self.widget.addTopLevelItemFromDict(root_data)

        child_data: TreeItemData = {"text": "Child", "data": 456}
        child_item = self.widget.addChildItem(root_item, child_data)

        self.assertIsInstance(child_item, QTreeWidgetItem)
        self.assertEqual(root_item.childCount(), 1)
        self.assertEqual(root_item.child(0), child_item)
        self.assertEqual(child_item.text(0), "Child")
        self.assertEqual(child_item.data(0, Qt.ItemDataRole.UserRole), 456)
        self.assertIn(child_item, self.widget._item_cache)

    def test_add_item_with_children_from_dict(self):
        """Test adding an item with nested children from dict"""
        data: TreeItemData = {
            "text": "Parent",
            "children": [
                {"text": "Child1", "data": "c1"},
                {"text": "Child2", "checkable": True}
            ]
        }
        item = self.widget.addTopLevelItemFromDict(data)

        self.assertEqual(self.widget.topLevelItemCount(), 1)
        self.assertEqual(item.childCount(), 2)
        child1 = item.child(0)
        child2 = item.child(1)

        self.assertEqual(child1.text(0), "Child1")
        self.assertEqual(child1.data(0, Qt.ItemDataRole.UserRole), "c1")
        self.assertEqual(child2.text(0), "Child2")
        self.assertEqual(child2.checkState(0), Qt.CheckState.Unchecked) # checkable=True in data

    def test_clear(self):
        """Test clearing all items"""
        self.widget.addTopLevelItemFromDict({"text": "Item1"})
        self.widget.addTopLevelItemFromDict({"text": "Item2"})
        self.assertEqual(self.widget.topLevelItemCount(), 2)

        self.widget.clear()
        self.assertEqual(self.widget.topLevelItemCount(), 0)
        self.assertEqual(len(self.widget._item_cache), 0) # Cache should be cleared

    @patch.object(FluentTreeWidget, '_filter_items')
    def test_set_search_text_debouncing(self, mock_filter_items):
        """Test search text debouncing"""
        self.widget._config = TreeConfiguration(search_debounce=50) # Short debounce for test
        self.widget.setSearchText("test")
        mock_filter_items.assert_not_called() # Should wait for debounce

        QTest.qWait(100) # Wait longer than debounce time
        mock_filter_items.assert_called_once()

        # Test setting text again before debounce
        mock_filter_items.reset_mock()
        self.widget.setSearchText("test2")
        self.widget.setSearchText("test3")
        mock_filter_items.assert_not_called()
        QTest.qWait(100)
        mock_filter_items.assert_called_once() # Only called once after the last change

    def test_filter_items(self):
        """Test filtering logic"""
        self.widget.setHeaderLabels(["Name"])
        item1 = self.widget.addTopLevelItemFromDict({"text": "Apple"})
        item2 = self.widget.addTopLevelItemFromDict({"text": "Banana"})
        item3 = self.widget.addTopLevelItemFromDict({"text": "Cherry"})
        child_data: TreeItemData = {"text": "Red Apple"}
        child_item = self.widget.addChildItem(item1, child_data)

        # Test filter "apple"
        self.widget._search_text = "apple"
        self.widget._filter_items()
        self.assertFalse(item1.isHidden())
        self.assertFalse(child_item.isHidden())
        self.assertTrue(item2.isHidden())
        self.assertTrue(item3.isHidden())

        # Test filter "cherry"
        self.widget._search_text = "cherry"
        self.widget._filter_items()
        self.assertTrue(item1.isHidden())
        self.assertTrue(child_item.isHidden())
        self.assertTrue(item2.isHidden())
        self.assertFalse(item3.isHidden())

        # Test empty filter
        self.widget._search_text = ""
        self.widget._filter_items()
        self.assertFalse(item1.isHidden())
        self.assertFalse(child_item.isHidden())
        self.assertFalse(item2.isHidden())
        self.assertFalse(item3.isHidden())

    def test_item_matches_search(self):
        """Test item matching search logic"""
        self.widget.setHeaderLabels(["Name"])
        item_data: TreeItemData = {"text": "Test Item", "metadata": {"id": "123", "tags": ["important", "urgent"]}}
        item = self.widget._create_tree_item(item_data) # Use internal method to get item with cache

        self.widget._search_text = "test"
        self.assertTrue(self.widget._item_matches_search(item))

        self.widget._search_text = "item"
        self.assertTrue(self.widget._item_matches_search(item))

        self.widget._search_text = "123" # Search in metadata
        self.assertTrue(self.widget._item_matches_search(item))

        self.widget._search_text = "urgent" # Search in metadata list
        self.assertTrue(self.widget._item_matches_search(item))

        self.widget._search_text = "nonexistent"
        self.assertFalse(self.widget._item_matches_search(item))

        # Test child matching
        parent_data: TreeItemData = {"text": "Parent"}
        parent_item = self.widget._create_tree_item(parent_data)
        child_data: TreeItemData = {"text": "Child Item"}
        child_item = self.widget._create_tree_item(child_data)
        parent_item.addChild(child_item)
        self.widget._item_cache[parent_item] = parent_data # Manually add to cache if not using add...FromDict

        self.widget._search_text = "child"
        self.assertTrue(self.widget._item_matches_search(parent_item)) # Parent matches if child matches

        self.widget._search_text = "parent"
        self.assertTrue(self.widget._item_matches_search(parent_item))

        self.widget._search_text = "nonexistent"
        self.assertFalse(self.widget._item_matches_search(parent_item))

    def test_expand_collapse_all(self):
        """Test expandAll and collapseAll"""
        self.widget.setHeaderLabels(["Name"])
        root1 = self.widget.addTopLevelItemFromDict({"text": "Root1"})
        child1 = self.widget.addChildItem(root1, {"text": "Child1"})
        grandchild1 = self.widget.addChildItem(child1, {"text": "Grandchild1"})
        root2 = self.widget.addTopLevelItemFromDict({"text": "Root2"})

        self.assertFalse(root1.isExpanded())
        self.assertFalse(child1.isExpanded())
        self.assertFalse(root2.isExpanded())

        self.widget.expandAll()
        QApplication.processEvents() # Process events for animation/state update
        self.assertTrue(root1.isExpanded())
        self.assertTrue(child1.isExpanded())
        self.assertTrue(root2.isExpanded())

        self.widget.collapseAll()
        QApplication.processEvents()
        self.assertFalse(root1.isExpanded())
        self.assertFalse(child1.isExpanded())
        self.assertFalse(root2.isExpanded())

    def test_get_selected_items_data(self):
        """Test getting data from selected items"""
        self.widget.setHeaderLabels(["Name"])
        item1 = self.widget.addTopLevelItemFromDict({"text": "Item1", "data": {"id": 1}})
        item2 = self.widget.addTopLevelItemFromDict({"text": "Item2", "data": {"id": 2}})
        item3 = self.widget.addTopLevelItemFromDict({"text": "Item3", "data": {"id": 3}})

        self.widget.setItemSelected(item1, True)
        self.widget.setItemSelected(item3, True)

        selected_data = self.widget.getSelectedItemsData()
        # Order might vary depending on selection order, check content
        self.assertEqual(len(selected_data), 2)
        self.assertIn({"id": 1}, selected_data)
        self.assertIn({"id": 3}, selected_data)
        self.assertNotIn({"id": 2}, selected_data)

    def test_get_checked_items_data(self):
        """Test getting data from checked items"""
        self.widget.setHeaderLabels(["Name"])
        item1 = self.widget.addTopLevelItemFromDict({"text": "Item1", "data": {"id": 1}, "checkable": True})
        item2 = self.widget.addTopLevelItemFromDict({"text": "Item2", "data": {"id": 2}, "checkable": True})
        item3 = self.widget.addTopLevelItemFromDict({"text": "Item3", "data": {"id": 3}, "checkable": True})
        child_item = self.widget.addChildItem(item1, {"text": "Child", "data": {"id": 4}, "checkable": True})

        item1.setCheckState(0, Qt.CheckState.Checked)
        child_item.setCheckState(0, Qt.CheckState.Checked)
        item3.setCheckState(0, Qt.CheckState.PartiallyChecked) # Should not be included

        checked_data = self.widget.getCheckedItemsData()
        self.assertEqual(len(checked_data), 2)
        self.assertIn({"id": 1}, checked_data)
        self.assertIn({"id": 4}, checked_data)
        self.assertNotIn({"id": 2}, checked_data)
        self.assertNotIn({"id": 3}, checked_data)

    def test_set_drag_drop_enabled(self):
        """Test enabling/disabling drag and drop"""
        self.widget.setDragDropEnabled(True)
        self.assertEqual(self.widget.dragDropMode(), QAbstractItemView.DragDropMode.InternalMove)
        self.assertTrue(self.widget.dragEnabled())
        self.assertTrue(self.widget.acceptDrops())

        self.widget.setDragDropEnabled(False)
        self.assertEqual(self.widget.dragDropMode(), QAbstractItemView.DragDropMode.NoDragDrop)
        # Note: dragEnabled and acceptDrops might not be explicitly set to False by Qt
        # when mode is NoDragDrop, but the mode itself disables the behavior.

    def test_item_clicked_signal(self):
        """Test item_clicked_signal emission"""
        self.widget.setHeaderLabels(["Name"])
        item = self.widget.addTopLevelItemFromDict({"text": "Click Me"})
        col = 0
        clicked_item = None
        clicked_col = -1

        def on_item_clicked(item, col):
            nonlocal clicked_item, clicked_col
            clicked_item = item
            clicked_col = col

        self.widget.item_clicked_signal.connect(on_item_clicked)

        # Simulate a click on the item
        item_rect = self.widget.visualItemRect(item)
        click_pos = item_rect.center()
        QTest.mouseClick(self.widget.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, click_pos)

        self.assertEqual(clicked_item, item)
        self.assertEqual(clicked_col, col)

    def test_item_double_clicked_signal(self):
        """Test item_double_clicked_signal emission"""
        self.widget.setHeaderLabels(["Name"])
        item = self.widget.addTopLevelItemFromDict({"text": "Double Click Me"})
        col = 0
        double_clicked_item = None
        double_clicked_col = -1

        def on_item_double_clicked(item, col):
            nonlocal double_clicked_item, double_clicked_col
            double_clicked_item = item
            double_clicked_col = col

        self.widget.item_double_clicked_signal.connect(on_item_double_clicked)

        # Simulate a double click on the item
        item_rect = self.widget.visualItemRect(item)
        click_pos = item_rect.center()
        QTest.mouseDClick(self.widget.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, click_pos)

        self.assertEqual(double_clicked_item, item)
        self.assertEqual(double_clicked_col, col)

    def test_item_expanded_collapsed_signals(self):
        """Test item_expanded_signal and item_collapsed_signal emission"""
        self.widget.setHeaderLabels(["Name"])
        root = self.widget.addTopLevelItemFromDict({"text": "Root"})
        child = self.widget.addChildItem(root, {"text": "Child"})

        expanded_item = None
        collapsed_item = None

        def on_expanded(item):
            nonlocal expanded_item
            expanded_item = item

        def on_collapsed(item):
            nonlocal collapsed_item
            collapsed_item = item

        self.widget.item_expanded_signal.connect(on_expanded)
        self.widget.item_collapsed_signal.connect(on_collapsed)

        root.setExpanded(True)
        QApplication.processEvents()
        self.assertEqual(expanded_item, root)
        self.assertIsNone(collapsed_item)

        expanded_item = None # Reset
        root.setExpanded(False)
        QApplication.processEvents()
        self.assertIsNone(expanded_item)
        self.assertEqual(collapsed_item, root)

    def test_selection_changed_signal(self):
        """Test selection_changed_signal emission"""
        self.widget.setHeaderLabels(["Name"])
        item1 = self.widget.addTopLevelItemFromDict({"text": "Item1"})
        item2 = self.widget.addTopLevelItemFromDict({"text": "Item2"})

        selected_items_list = None

        def on_selection_changed(items):
            nonlocal selected_items_list
            selected_items_list = items

        self.widget.selection_changed_signal.connect(on_selection_changed)

        self.widget.setItemSelected(item1, True)
        QApplication.processEvents()
        self.assertEqual(selected_items_list, [item1])

        self.widget.setItemSelected(item2, True)
        QApplication.processEvents()
        # Order might vary, check content
        self.assertIn(item1, selected_items_list)
        self.assertIn(item2, selected_items_list)
        self.assertEqual(len(selected_items_list), 2)

        self.widget.setItemSelected(item1, False)
        QApplication.processEvents()
        self.assertEqual(selected_items_list, [item2])

    def test_item_context_menu_signal(self):
        """Test item_context_menu signal emission"""
        self.widget.setHeaderLabels(["Name"])
        item = self.widget.addTopLevelItemFromDict({"text": "Context Menu"})

        context_item = None
        context_pos = None

        def on_context_menu(item, pos):
            nonlocal context_item, context_pos
            context_item = item
            context_pos = pos

        self.widget.item_context_menu.connect(on_context_menu)

        # Simulate a right click on the item
        item_rect = self.widget.visualItemRect(item)
        click_pos = item_rect.center()
        # Need to map to global position for the signal
        global_pos = self.widget.mapToGlobal(click_pos)

        # QTest.mouseClick doesn't trigger customContextMenuRequested directly
        # We can emit the signal manually for testing purposes
        self.widget.customContextMenuRequested.emit(click_pos)

        self.assertEqual(context_item, item)
        # Check if the position is close to the expected global position
        self.assertAlmostEqual(context_pos.x(), global_pos.x(), delta=5)
        self.assertAlmostEqual(context_pos.y(), global_pos.y(), delta=5)

    def test_state_changed_signal(self):
        """Test state_changed signal emission"""
        states = []

        def on_state_changed(state):
            states.append(state)

        self.widget.state_changed.connect(on_state_changed)

        self.widget.current_state = TreeState.LOADING
        self.widget.current_state = TreeState.FILTERING
        self.widget.current_state = TreeState.IDLE

        self.assertEqual(states, [TreeState.LOADING, TreeState.FILTERING, TreeState.IDLE])

    def test_get_item_path(self):
        """Test getting item path"""
        self.widget.setHeaderLabels(["Name"])
        root = self.widget.addTopLevelItemFromDict({"text": "Root"})
        child1 = self.widget.addChildItem(root, {"text": "Child1"})
        grandchild1 = self.widget.addChildItem(child1, {"text": "Grandchild1"})
        root2 = self.widget.addTopLevelItemFromDict({"text": "Root2"})

        self.assertEqual(self.widget.get_item_path(root), "Root")
        self.assertEqual(self.widget.get_item_path(child1), "Root/Child1")
        self.assertEqual(self.widget.get_item_path(grandchild1), "Root/Child1/Grandchild1")
        self.assertEqual(self.widget.get_item_path(root2), "Root2")

    @patch.object(FluentTreeWidget, '_setup_style')
    def test_on_theme_changed(self, mock_setup_style):
        """Test theme change handling"""
        # Simulate theme change signal
        self.widget._on_theme_changed("") # The slot expects a string argument

        mock_setup_style.assert_called_once()


@unittest.skipUnless(COMPONENTS_AVAILABLE, "Components not available")
class TestFluentHierarchicalView(unittest.TestCase):
    """Unit tests for FluentHierarchicalView"""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up each test"""
        # Patch _setup_enhanced_styles to avoid dependency on theme_manager during init
        with patch('components.data.display.tree._setup_enhanced_styles', return_value=""):
             self.widget = FluentHierarchicalView()
        self.widgets = [self.widget] # Keep track for cleanup

    def tearDown(self):
        """Clean up after each test"""
        for widget in self.widgets:
            if widget and hasattr(widget, 'close'):
                widget.close()
        QApplication.processEvents()

    def test_init(self):
        """Test initialization and UI setup"""
        self.assertIsInstance(self.widget, FluentHierarchicalView)
        self.assertIsInstance(self.widget._config, TreeConfiguration)
        self.assertIsNotNone(self.widget.toolbar)
        self.assertIsNotNone(self.widget.filter_panel)
        self.assertIsNotNone(self.widget.tree)
        self.assertFalse(self.widget.filter_panel.isVisible())
        self.assertIsInstance(self.widget.search_box, QLineEdit)
        self.assertIsInstance(self.widget.filter_btn, QPushButton)
        self.assertIsInstance(self.widget.expand_all_btn, QPushButton)
        self.assertIsInstance(self.widget.collapse_all_btn, QPushButton)

    def test_set_data(self):
        """Test setting data"""
        data: List[TreeItemData] = [
            {"text": "Item1", "data": 1},
            {"text": "Item2", "children": [{"text": "Child2", "data": 2}]}
        ]
        self.widget.setData(data)
        # Wait for the async refresh to complete
        QTest.qWait(100) # Adjust wait time if needed

        self.assertEqual(self.widget.tree.topLevelItemCount(), 2)
        item1 = self.widget.tree.topLevelItem(0)
        item2 = self.widget.tree.topLevelItem(1)
        self.assertEqual(item1.text(0), "Item1")
        self.assertEqual(item2.text(0), "Item2")
        self.assertEqual(item2.childCount(), 1)
        self.assertEqual(item2.child(0).text(0), "Child2")

    def test_add_item(self):
        """Test adding a single item"""
        initial_data: List[TreeItemData] = [{"text": "Item1"}]
        self.widget.setData(initial_data)
        QTest.qWait(100)
        self.assertEqual(self.widget.tree.topLevelItemCount(), 1)

        new_item_data: TreeItemData = {"text": "New Item", "data": 99}
        self.widget.addItem(new_item_data)
        QTest.qWait(100) # Wait for refresh

        self.assertEqual(self.widget.tree.topLevelItemCount(), 2)
        # Check if the new item is present (order might vary)
        found = False
        for i in range(self.widget.tree.topLevelItemCount()):
            item = self.widget.tree.topLevelItem(i)
            if item.text(0) == "New Item" and item.data(0, Qt.ItemDataRole.UserRole) == 99:
                found = True
                break
        self.assertTrue(found)

    def test_add_filter(self):
        """Test adding a filter option"""
        filter_name = "Status"
        filter_values = ["Active", "Inactive"]
        self.widget.addFilter(filter_name, filter_values)

        # Check if label and combo box are added
        layout_items = [self.widget.filter_layout.itemAt(i).widget() for i in range(self.widget.filter_layout.count())]
        labels = [w for w in layout_items if isinstance(w, QLabel)]
        combos = [w for w in layout_items if isinstance(w, QComboBox)]

        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0].text(), "Status:")
        self.assertEqual(len(combos), 1)
        self.assertEqual(combos[0].count(), 3) # All + 2 values
        self.assertEqual(combos[0].itemText(0), "All")
        self.assertEqual(combos[0].itemText(1), "Active")
        self.assertEqual(combos[0].itemText(2), "Inactive")

    def test_filter_data(self):
        """Test applying filters"""
        data: List[TreeItemData] = [
            {"text": "Task A", "status": "Active"},
            {"text": "Task B", "status": "Inactive"},
            {"text": "Task C", "status": "Active"},
        ]
        self.widget.setData(data)
        QTest.qWait(100) # Wait for initial refresh
        self.assertEqual(self.widget.tree.topLevelItemCount(), 3)

        self.widget.addFilter("status", ["Active", "Inactive"])
        QTest.qWait(100) # Wait for filter UI to be added

        # Find the status combo box
        status_combo = None
        for i in range(self.widget.filter_layout.count()):
            widget = self.widget.filter_layout.itemAt(i).widget()
            if isinstance(widget, QComboBox) and widget.objectName() == "filterCombo":
                status_combo = widget
                break
        self.assertIsNotNone(status_combo)

        # Select "Active"
        status_combo.setCurrentText("Active")
        QTest.qWait(200) # Wait for filter change signal and refresh

        self.assertEqual(self.widget.tree.topLevelItemCount(), 2)
        items = [self.widget.tree.topLevelItem(i).text(0) for i in range(self.widget.tree.topLevelItemCount())]
        self.assertIn("Task A", items)
        self.assertIn("Task C", items)
        self.assertNotIn("Task B", items)

        # Select "Inactive"
        status_combo.setCurrentText("Inactive")
        QTest.qWait(200) # Wait for filter change signal and refresh

        self.assertEqual(self.widget.tree.topLevelItemCount(), 1)
        items = [self.widget.tree.topLevelItem(i).text(0) for i in range(self.widget.tree.topLevelItemCount())]
        self.assertIn("Task B", items)
        self.assertNotIn("Task A", items)
        self.assertNotIn("Task C", items)

        # Select "All"
        status_combo.setCurrentText("All")
        QTest.qWait(200) # Wait for filter change signal and refresh
        self.assertEqual(self.widget.tree.topLevelItemCount(), 3)


    def test_search_data(self):
        """Test applying search filter"""
        data: List[TreeItemData] = [
            {"text": "Apple Pie"},
            {"text": "Banana Bread"},
            {"text": "Cherry Cake"},
            {"text": "Apple Juice"},
        ]
        self.widget.setData(data)
        QTest.qWait(100) # Wait for initial refresh
        self.assertEqual(self.widget.tree.topLevelItemCount(), 4)

        # Search for "apple"
        self.widget.search_box.setText("apple")
        QTest.qWait(self.widget._config.search_debounce + 100) # Wait for debounce and refresh

        # Check visibility in the underlying tree widget
        # FluentTreeWidget hides items, it doesn't remove them
        visible_items = [self.widget.tree.topLevelItem(i).text(0)
                         for i in range(self.widget.tree.topLevelItemCount())
                         if not self.widget.tree.topLevelItem(i).isHidden()]

        self.assertEqual(len(visible_items), 2)
        self.assertIn("Apple Pie", visible_items)
        self.assertIn("Apple Juice", visible_items)
        self.assertNotIn("Banana Bread", visible_items)
        self.assertNotIn("Cherry Cake", visible_items)

        # Clear search
        self.widget.search_box.setText("")
        QTest.qWait(self.widget._config.search_debounce + 100) # Wait for debounce and refresh

        visible_items = [self.widget.tree.topLevelItem(i).text(0)
                         for i in range(self.widget.tree.topLevelItemCount())
                         if not self.widget.tree.topLevelItem(i).isHidden()]
        self.assertEqual(len(visible_items), 4) # All items should be visible again

    def test_toggle_filters(self):
        """Test toggling filter panel visibility"""
        self.assertFalse(self.widget.filter_panel.isVisible())

        self.widget.filter_btn.click()
        self.assertTrue(self.widget.filter_panel.isVisible())

        self.widget.filter_btn.click()
        self.assertFalse(self.widget.filter_panel.isVisible())

    @patch.object(FluentTreeWidget, 'expandAll')
    def test_expand_all_button(self, mock_expand_all):
        """Test expand all button"""
        self.widget.expand_all_btn.click()
        mock_expand_all.assert_called_once()

    @patch.object(FluentTreeWidget, 'collapseAll')
    def test_collapse_all_button(self, mock_collapse_all):
        """Test collapse all button"""
        self.widget.collapse_all_btn.click()
        mock_collapse_all.assert_called_once()

    def test_item_selected_signal(self):
        """Test item_selected signal emission"""
        data: List[TreeItemData] = [{"text": "Select Me", "data": {"id": 123}}]
        self.widget.setData(data)
        QTest.qWait(100) # Wait for refresh

        selected_data = None
        def on_item_selected(data):
            nonlocal selected_data
            selected_data = data

        self.widget.item_selected.connect(on_item_selected)

        item = self.widget.tree.topLevelItem(0)
        item_rect = self.widget.tree.visualItemRect(item)
        click_pos = item_rect.center()
        QTest.mouseClick(self.widget.tree.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, click_pos)
        QApplication.processEvents() # Process selection change signal

        self.assertEqual(selected_data, {"text": "Select Me", "data": {"id": 123}})

    def test_item_activated_signal(self):
        """Test item_activated signal emission"""
        data: List[TreeItemData] = [{"text": "Activate Me", "data": {"id": 456}}]
        self.widget.setData(data)
        QTest.qWait(100) # Wait for refresh

        activated_data = None
        def on_item_activated(data):
            nonlocal activated_data
            activated_data = data

        self.widget.item_activated.connect(on_item_activated)

        item = self.widget.tree.topLevelItem(0)
        item_rect = self.widget.tree.visualItemRect(item)
        click_pos = item_rect.center()
        QTest.mouseDClick(self.widget.tree.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, click_pos)
        QApplication.processEvents() # Process double click signal

        self.assertEqual(activated_data, {"text": "Activate Me", "data": {"id": 456}})

    def test_search_performed_signal(self):
        """Test search_performed signal emission"""
        search_term = None
        def on_search_performed(term):
            nonlocal search_term
            search_term = term

        self.widget.search_performed.connect(on_search_performed)

        self.widget.search_box.setText("test search")
        QTest.qWait(self.widget._config.search_debounce + 100) # Wait for debounce

        self.assertEqual(search_term, "test search")

    def test_filter_applied_signal(self):
        """Test filter_applied signal emission"""
        applied_filter = None
        def on_filter_applied(filter_info):
            nonlocal applied_filter
            applied_filter = filter_info

        self.widget.filter_applied.connect(on_filter_applied)

        # Test panel toggle
        self.widget.filter_btn.click()
        self.assertEqual(applied_filter, "panel_opened")

        # Test filter change
        self.widget.addFilter("Status", ["Active"])
        QTest.qWait(100) # Wait for filter UI
        status_combo = None
        for i in range(self.widget.filter_layout.count()):
            widget = self.widget.filter_layout.itemAt(i).widget()
            if isinstance(widget, QComboBox) and widget.objectName() == "filterCombo":
                status_combo = widget
                break
        self.assertIsNotNone(status_combo)

        status_combo.setCurrentText("Active")
        QTest.qWait(200) # Wait for filter change signal

        self.assertEqual(applied_filter, "Status:Active")

    @patch('components.data.display.tree._setup_enhanced_styles', return_value="")
    def test_on_theme_changed(self, mock_setup_enhanced_styles):
        """Test theme change handling"""
        # Simulate theme change signal
        self.widget._on_theme_changed("") # The slot expects an argument

        mock_setup_enhanced_styles.assert_called_once()
        # Verify style sheet is updated (difficult to assert the exact stylesheet)
        # We rely on the mock call for this test.


@unittest.skipUnless(COMPONENTS_AVAILABLE, "Components not available")
class TestFluentOrgChart(unittest.TestCase):
    """Unit tests for FluentOrgChart"""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up each test"""
        # Patch _setup_enhanced_styles to avoid dependency on theme_manager during init
        with patch('components.data.display.tree._setup_enhanced_styles', return_value=""):
             self.widget = FluentOrgChart()
        self.widgets = [self.widget] # Keep track for cleanup

    def tearDown(self):
        """Clean up after each test"""
        for widget in self.widgets:
            if widget and hasattr(widget, 'close'):
                widget.close()
        QApplication.processEvents()

    def test_init(self):
        """Test initialization"""
        self.assertIsInstance(self.widget, FluentOrgChart)
        self.assertEqual(len(self.widget._nodes), 0)
        self.assertEqual(len(self.widget._connections), 0)
        self.assertEqual(len(self.widget._node_positions), 0)
        self.assertEqual(self.widget._zoom_factor, 1.0)
        self.assertEqual(self.widget._pan_offset, QPoint(0, 0))
        self.assertTrue(self.widget._dirty_layout) # Should be dirty initially

    @patch.object(FluentOrgChart, '_invalidate_layout')
    def test_add_node(self, mock_invalidate_layout):
        """Test adding nodes"""
        node1_data: NodeData = {"title": "Node 1"}
        self.widget.addNode("node1", node1_data)
        self.assertEqual(len(self.widget._nodes), 1)
        self.assertEqual(self.widget._nodes["node1"]["title"], "Node 1")
        self.assertEqual(len(self.widget._connections), 0)
        mock_invalidate_layout.assert_called_once()

        mock_invalidate_layout.reset_mock()
        node2_data: NodeData = {"title": "Node 2"}
        self.widget.addNode("node2", node2_data, parent_id="node1")
        self.assertEqual(len(self.widget._nodes), 2)
        self.assertEqual(self.widget._nodes["node2"]["title"], "Node 2")
        self.assertEqual(len(self.widget._connections), 1)
        self.assertIn(("node1", "node2"), self.widget._connections)
        mock_invalidate_layout.assert_called_once()

        # Test adding node with existing ID
        with self.assertRaises(ValueError):
            self.widget.addNode("node1", {"title": "Duplicate"})

        # Test adding child to non-existent parent
        with self.assertRaises(ValueError):
            self.widget.addNode("node3", {"title": "Node 3"}, parent_id="nonexistent")

        # Test adding node without title (validation)
        with self.assertRaises(ValueError):
             self.widget.addNode("node4", {})

    @patch.object(FluentOrgChart, '_invalidate_layout')
    def test_remove_node(self, mock_invalidate_layout):
        """Test removing nodes"""
        self.widget.addNode("root", {"title": "Root"})
        self.widget.addNode("child1", {"title": "Child 1"}, parent_id="root")
        self.widget.addNode("child2", {"title": "Child 2"}, parent_id="root")
        self.widget.addNode("grandchild1", {"title": "Grandchild 1"}, parent_id="child1")
        mock_invalidate_layout.reset_mock() # Reset after setup

        self.assertEqual(len(self.widget._nodes), 4)
        self.assertEqual(len(self.widget._connections), 3)

        # Remove a leaf node
        self.widget.removeNode("child2")
        self.assertEqual(len(self.widget._nodes), 3)
        self.assertNotIn("child2", self.widget._nodes)
        self.assertEqual(len(self.widget._connections), 2)
        self.assertNotIn(("root", "child2"), self.widget._connections)
        mock_invalidate_layout.assert_called_once()

        mock_invalidate_layout.reset_mock()
        # Remove a node with children (cascade)
        self.widget.removeNode("child1")
        self.assertEqual(len(self.widget._nodes), 1)
        self.assertIn("root", self.widget._nodes)
        self.assertNotIn("child1", self.widget._nodes)
        self.assertNotIn("grandchild1", self.widget._nodes)
        self.assertEqual(len(self.widget._connections), 0)
        mock_invalidate_layout.assert_called_once()

        # Test removing non-existent node (should do nothing)
        mock_invalidate_layout.reset_mock()
        self.widget.removeNode("nonexistent")
        self.assertEqual(len(self.widget._nodes), 1)
        self.assertEqual(len(self.widget._connections), 0)
        mock_invalidate_layout.assert_not_called()

    @patch.object(FluentOrgChart, '_invalidate_cache')
    def test_update_node(self, mock_invalidate_cache):
        """Test updating node data"""
        self.widget.addNode("node1", {"title": "Old Title"})
        mock_invalidate_cache.reset_mock() # Reset after addNode calls it

        new_data: NodeData = {"title": "New Title", "status": "Active"}
        self.widget.updateNode("node1", new_data)

        self.assertEqual(self.widget._nodes["node1"]["title"], "New Title")
        self.assertEqual(self.widget._nodes["node1"]["status"], "Active")
        mock_invalidate_cache.assert_called_once_with("node1")

        # Test updating non-existent node
        with self.assertRaises(ValueError):
            self.widget.updateNode("nonexistent", {"title": "Update"})

    @patch.object(FluentOrgChart, '_invalidate_layout')
    def test_clear_nodes(self, mock_invalidate_layout):
        """Test clearing all nodes"""
        self.widget.addNode("root", {"title": "Root"})
        self.widget.addNode("child", {"title": "Child"}, parent_id="root")
        self.widget._node_positions = {"root": (0,0), "child": (100,100)} # Simulate positions
        self.widget._layout_cache = {"key": "value"}
        self.widget._paint_cache = {"key": QPixmap()}
        mock_invalidate_layout.reset_mock() # Reset after addNode calls it

        self.widget.clearNodes()

        self.assertEqual(len(self.widget._nodes), 0)
        self.assertEqual(len(self.widget._connections), 0)
        self.assertEqual(len(self.widget._node_positions), 0)
        self.assertEqual(len(self.widget._layout_cache), 0)
        self.assertEqual(len(self.widget._paint_cache), 0)
        self.assertTrue(self.widget._dirty_layout)
        mock_invalidate_layout.assert_called_once()

    def test_zoom_factor(self):
        """Test zoom factor property"""
        self.widget.zoom_factor = 1.5
        self.assertEqual(self.widget.zoom_factor, 1.5)

        self.widget.zoom_factor = 0.05 # Below min
        self.assertEqual(self.widget.zoom_factor, 0.1)

        self.widget.zoom_factor = 5.0 # Above max
        self.assertEqual(self.widget.zoom_factor, 3.0)

    @patch.object(FluentOrgChart, 'update')
    def test_calculate_layout(self, mock_update):
        """Test layout calculation (basic check)"""
        self.widget.addNode("root", {"title": "Root"})
        self.widget.addNode("child1", {"title": "Child 1"}, parent_id="root")
        self.widget.addNode("child2", {"title": "Child 2"}, parent_id="root")
        self.widget.addNode("grandchild1", {"title": "Grandchild 1"}, parent_id="child1")

        # Trigger layout calculation (it's async, so we need to wait or call directly)
        # Calling directly for unit test isolation
        self.widget._calculate_layout()

        self.assertTrue(len(self.widget._node_positions) > 0)
        self.assertIn("root", self.widget._node_positions)
        self.assertIn("child1", self.widget._node_positions)
        self.assertIn("child2", self.widget._node_positions)
        self.assertIn("grandchild1", self.widget._node_positions)

        # Check relative positions (approximate)
        root_pos = self.widget._node_positions["root"]
        child1_pos = self.widget._node_positions["child1"]
        child2_pos = self.widget._node_positions["child2"]
        grandchild1_pos = self.widget._node_positions["grandchild1"]

        self.assertLess(root_pos[1], child1_pos[1]) # Root is above children
        self.assertLess(root_pos[1], child2_pos[1])
        self.assertLess(child1_pos[1], grandchild1_pos[1]) # Child is above grandchild

        # Children should be roughly side-by-side
        self.assertNotEqual(child1_pos[0], child2_pos[0])

        # Root should be roughly centered above its children
        # This is harder to test precisely without knowing the exact layout algorithm output
        # We'll skip precise coordinate checks for robustness.

        # Ensure update is called after async layout completes
        # This is handled by _calculate_layout_async, which calls update()
        # We called _calculate_layout directly, so update() isn't called here.
        # A better test would involve waiting for _calculate_layout_async.
        # Let's test the signal instead.

    def test_layout_changed_signal(self):
        """Test layout_changed signal emission"""
        layout_changed_called = False
        def on_layout_changed():
            nonlocal layout_changed_called
            layout_changed_called = True

        self.widget.layout_changed.connect(on_layout_changed)

        self.widget.addNode("root", {"title": "Root"})
        # addNode calls _invalidate_layout which calls _calculate_layout_async
        # _calculate_layout_async emits layout_changed after calculation
        QTest.qWait(100) # Wait for async layout

        self.assertTrue(layout_changed_called)

    def test_mouse_press_click_signal(self):
        """Test mouse click and node_clicked signal"""
        self.widget.addNode("node1", {"title": "Node 1"})
        self.widget._calculate_layout() # Calculate layout so node_positions is populated
        QTest.qWait(100) # Wait for layout async if needed

        node_pos = self.widget._node_positions.get("node1")
        self.assertIsNotNone(node_pos, "Node position not calculated")

        clicked_data = None
        def on_node_clicked(data):
            nonlocal clicked_data
            clicked_data = data

        self.widget.node_clicked.connect(on_node_clicked)

        # Simulate click on the node's center
        click_pos = QPoint(int(node_pos[0] + self.widget._node_size[0] // 2),
                           int(node_pos[1] + self.widget._node_size[1] // 2))

        QTest.mouseClick(self.widget, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, click_pos)
        QApplication.processEvents()

        self.assertIsNotNone(clicked_data)
        self.assertEqual(clicked_data.get("node_id"), "node1")
        self.assertEqual(clicked_data.get("title"), "Node 1")

        # Simulate click outside the node
        clicked_data = None # Reset
        click_pos_outside = QPoint(10, 10)
        QTest.mouseClick(self.widget, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, click_pos_outside)
        QApplication.processEvents()
        self.assertIsNone(clicked_data) # Signal should not be emitted

    def test_mouse_double_click_signal(self):
        """Test mouse double click and node_double_clicked signal"""
        self.widget.addNode("node1", {"title": "Node 1"})
        self.widget._calculate_layout() # Calculate layout
        QTest.qWait(100)

        node_pos = self.widget._node_positions.get("node1")
        self.assertIsNotNone(node_pos)

        double_clicked_data = None
        def on_node_double_clicked(data):
            nonlocal double_clicked_data
            double_clicked_data = data

        self.widget.node_double_clicked.connect(on_node_double_clicked)

        # Simulate double click on the node's center
        click_pos = QPoint(int(node_pos[0] + self.widget._node_size[0] // 2),
                           int(node_pos[1] + self.widget._node_size[1] // 2))

        QTest.mouseDClick(self.widget, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, click_pos)
        QApplication.processEvents()

        self.assertIsNotNone(double_clicked_data)
        self.assertEqual(double_clicked_data.get("node_id"), "node1")
        self.assertEqual(double_clicked_data.get("title"), "Node 1")

    def test_wheel_event_zoom(self):
        """Test wheel event for zooming"""
        initial_zoom = self.widget.zoom_factor
        self.widget.wheelEvent(MagicMock(angleDelta=MagicMock(y=lambda: 120))) # Simulate scroll up
        self.assertGreater(self.widget.zoom_factor, initial_zoom)

        initial_zoom = self.widget.zoom_factor
        self.widget.wheelEvent(MagicMock(angleDelta=MagicMock(y=lambda: -120))) # Simulate scroll down
        self.assertLess(self.widget.zoom_factor, initial_zoom)

    def test_node_context_menu_signal(self):
        """Test node_context_menu signal emission"""
        self.widget.addNode("node1", {"title": "Node 1"})
        self.widget._calculate_layout() # Calculate layout
        QTest.qWait(100)

        node_pos = self.widget._node_positions.get("node1")
        self.assertIsNotNone(node_pos)

        context_node_id = None
        context_pos = None

        def on_context_menu(node_id, pos):
            nonlocal context_node_id, context_pos
            context_node_id = node_id
            context_pos = pos

        self.widget.node_context_menu.connect(on_context_menu)

        # Simulate right click on the node's center
        click_pos = QPoint(int(node_pos[0] + self.widget._node_size[0] // 2),
                           int(node_pos[1] + self.widget._node_size[1] // 2))
        global_pos = self.widget.mapToGlobal(click_pos)

        # Emit the signal manually as QTest doesn't trigger customContextMenuRequested
        self.widget.customContextMenuRequested.emit(click_pos)
        QApplication.processEvents()

        self.assertEqual(context_node_id, "node1")
        self.assertAlmostEqual(context_pos.x(), global_pos.x(), delta=5)
        self.assertAlmostEqual(context_pos.y(), global_pos.y(), delta=5)

    @patch.object(FluentOrgChart, '_invalidate_cache')
    @patch.object(FluentOrgChart, '_setup_style')
    def test_on_theme_changed(self, mock_setup_style, mock_invalidate_cache):
        """Test theme change handling"""
        # Simulate theme change signal
        self.widget._on_theme_changed("") # The slot expects an argument

        mock_invalidate_cache.assert_called_once_with(None)
        mock_setup_style.assert_called_once()
        # Verify update is called (difficult to mock update itself without side effects)
        # We rely on the fact that _on_theme_changed calls update() at the end.


if __name__ == '__main__':
    # Initialize QApplication for testing if not already running
    if not QApplication.instance():
        app = QApplication(sys.argv)

    unittest.main()