"""
Fluent Design Tree View Component
Implements hierarchical data display with consistent styling and behavior
"""

from typing import Optional, List, Dict, Any, Callable, Union
from dataclasses import dataclass
from PySide6.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QStyledItemDelegate, QStyle
)
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QIcon

from components.base.fluent_control_base import FluentControlBase
from components.base.fluent_component_interface import (
    FluentComponentSize
)


@dataclass
class FluentTreeNode:
    """Data structure for tree nodes"""
    text: str
    value: Any = None
    icon: Optional[QIcon] = None
    expanded: bool = False
    selectable: bool = True
    children: Optional[List['FluentTreeNode']] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


class FluentTreeItemDelegate(QStyledItemDelegate):
    """Custom delegate for tree items with Fluent styling"""

    def __init__(self, tree_view, parent=None):
        super().__init__(parent)
        self._tree_view = tree_view

    def paint(self, painter, option, index):
        """Custom paint for tree items"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get item rect
        rect = option.rect

        # Get theme tokens from tree view
        theme_tokens = self._tree_view._theme_tokens

        # Determine colors based on state
        if option.state & QStyle.StateFlag.State_Selected:
            bg_color = theme_tokens.get("primary", QColor("#0078D4"))
            text_color = QColor("#FFFFFF")
        elif option.state & QStyle.StateFlag.State_MouseOver:
            bg_color = theme_tokens.get("accent", QColor("#F3F2F1"))
            text_color = theme_tokens.get("text_primary", QColor("#000000"))
        else:
            bg_color = theme_tokens.get("surface", QColor("#FFFFFF"))
            text_color = theme_tokens.get("text_primary", QColor("#000000"))

        # Draw background
        painter.fillRect(rect, bg_color)

        # Draw text
        painter.setPen(text_color)
        text_rect = rect.adjusted(4, 0, -4, 0)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            index.data(Qt.ItemDataRole.DisplayRole)
        )


class FluentTreeView(FluentControlBase):
    """
    Fluent Design Tree View Component

    Features:
    - Hierarchical data display
    - Custom item styling
    - Context menu support
    - Search functionality
    - Drag and drop support
    - Theme-consistent styling
    """

    # Signals
    item_selected = Signal(object)        # Selected tree node
    item_expanded = Signal(object)        # Expanded tree node
    item_collapsed = Signal(object)       # Collapsed tree node
    item_double_clicked = Signal(object)  # Double-clicked tree node
    context_menu_requested = Signal(object, QPoint)  # Context menu request

    def __init__(self, parent: Optional[QWidget] = None,
                 show_header: bool = True,
                 size: FluentComponentSize = FluentComponentSize.MEDIUM):
        super().__init__(parent)

        # Properties
        self._show_header = show_header
        self._root_nodes: List[FluentTreeNode] = []
        self._item_height = 24
        self._indent_size = 20
        self._search_enabled = False

        # Add missing _size property and methods for compatibility
        self._size = size

        # Setup component
        self._component_type = "FluentTreeView"
        # Provide dummy set_size and set_accessible_role if not present in base
        if not hasattr(self, "set_size"):
            self.set_size = lambda s: setattr(self, "_size", s)
        if not hasattr(self, "set_accessible_role"):
            self.set_accessible_role = lambda role: None

        self.set_size(size)
        self.set_accessible_role("tree")
        self.set_accessible_name("Tree view")

        # Create UI
        self._setup_ui()
        self._setup_connections()
        self._apply_themed_styles()

    def _setup_ui(self):
        """Setup the tree view UI"""
        # Main layout
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setLayout(self._layout)

        # Tree widget
        self._tree_widget = QTreeWidget()
        self._tree_widget.setHeaderHidden(not self._show_header)
        self._tree_widget.setRootIsDecorated(True)
        self._tree_widget.setAlternatingRowColors(False)
        self._tree_widget.setIndentation(self._indent_size)
        self._tree_widget.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)

        # Set custom delegate
        self._delegate = FluentTreeItemDelegate(self)
        self._tree_widget.setItemDelegate(self._delegate)

        # Add to layout
        self._layout.addWidget(self._tree_widget)

        # Set focus proxy
        self.setFocusProxy(self._tree_widget)

    def _setup_connections(self):
        """Setup signal connections"""
        self._tree_widget.itemSelectionChanged.connect(
            self._on_selection_changed)
        self._tree_widget.itemExpanded.connect(self._on_item_expanded)
        self._tree_widget.itemCollapsed.connect(self._on_item_collapsed)
        self._tree_widget.itemDoubleClicked.connect(
            self._on_item_double_clicked)
        self._tree_widget.customContextMenuRequested.connect(
            self._on_context_menu)

    def _apply_themed_styles(self):
        """Apply themed styles"""
        # Get theme colors
        bg_color = self._theme_tokens.get("surface", QColor("#FFFFFF"))
        border_color = self._theme_tokens.get("border", QColor("#CCCCCC"))
        text_color = self._theme_tokens.get("text_primary", QColor("#000000"))
        selection_color = self._theme_tokens.get("primary", QColor("#0078D4"))
        hover_color = self._theme_tokens.get("accent", QColor("#F3F2F1"))

        # Apply styles
        style = f"""
            QTreeWidget {{
                background-color: {bg_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: 6px;
                color: {text_color.name()};
                font-size: {self._theme_tokens.get("font_size", 14)}px;
                outline: none;
                show-decoration-selected: 1;
            }}
            QTreeWidget::item {{
                height: {self._item_height}px;
                border: none;
                padding: 2px;
            }}
            QTreeWidget::item:hover {{
                background-color: {hover_color.name()};
            }}
            QTreeWidget::item:selected {{
                background-color: {selection_color.name()};
                color: white;
            }}
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                border-image: none;
                image: none;
            }}
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                border-image: none;
                image: none;
            }}
        """
        self._tree_widget.setStyleSheet(style)

    def _apply_state_styles(self):
        """Apply state-specific styles"""
        self._apply_themed_styles()

    def get_value(self) -> Optional[FluentTreeNode]:
        """Get selected tree node"""
        selected_items = self._tree_widget.selectedItems()
        if selected_items:
            return selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        return None

    def set_value(self, value: Any) -> None:
        """Set selected tree node by value"""
        if isinstance(value, FluentTreeNode):
            item = self._find_item_by_node(value)
            if item:
                self._tree_widget.setCurrentItem(item)

    def set_data(self, nodes: List[FluentTreeNode]) -> None:
        """Set tree data"""
        self._root_nodes = nodes.copy()
        self._populate_tree()

    def add_root_node(self, node: FluentTreeNode) -> None:
        """Add a root node"""
        self._root_nodes.append(node)
        self._add_tree_item(None, node)

    def remove_root_node(self, node: FluentTreeNode) -> None:
        """Remove a root node"""
        if node in self._root_nodes:
            self._root_nodes.remove(node)
            item = self._find_item_by_node(node)
            if item:
                index = self._tree_widget.indexOfTopLevelItem(item)
                self._tree_widget.takeTopLevelItem(index)

    def clear(self) -> None:
        """Clear all tree data"""
        self._root_nodes.clear()
        self._tree_widget.clear()

    def expand_all(self) -> None:
        """Expand all tree items"""
        self._tree_widget.expandAll()

    def collapse_all(self) -> None:
        """Collapse all tree items"""
        self._tree_widget.collapseAll()

    def get_selected_node(self) -> Optional[FluentTreeNode]:
        """Get currently selected node"""
        return self.get_value()

    def set_selected_node(self, node: FluentTreeNode) -> None:
        """Set selected node"""
        self.set_value(node)

    def find_node(self, predicate: Callable[[FluentTreeNode], bool]) -> Optional[FluentTreeNode]:
        """Find node using predicate"""
        def search_nodes(nodes: List[FluentTreeNode]) -> Optional[FluentTreeNode]:
            for node in nodes:
                if predicate(node):
                    return node
                if node.children:
                    result = search_nodes(node.children)
                    if result:
                        return result
            return None

        return search_nodes(self._root_nodes)

    def set_header_labels(self, labels: List[str]) -> None:
        """Set header labels"""
        self._tree_widget.setHeaderLabels(labels)
        self._tree_widget.setHeaderHidden(False)
        self._show_header = True

    def set_header_visible(self, visible: bool) -> None:
        """Set header visibility"""
        self._show_header = visible
        self._tree_widget.setHeaderHidden(not visible)

    def set_item_height(self, height: int) -> None:
        """Set item height"""
        self._item_height = max(16, height)
        self._apply_themed_styles()

    def set_indent_size(self, size: int) -> None:
        """Set indentation size"""
        self._indent_size = max(10, size)
        self._tree_widget.setIndentation(size)

    def _populate_tree(self) -> None:
        """Populate tree with data"""
        self._tree_widget.clear()
        for node in self._root_nodes:
            self._add_tree_item(None, node)

    def _add_tree_item(self, parent_item: Optional[QTreeWidgetItem],
                       node: FluentTreeNode) -> QTreeWidgetItem:
        """Add tree item for node"""
        from PySide6.QtWidgets import QTreeWidgetItem  # Local import to avoid unused import warning
        if parent_item:
            item = QTreeWidgetItem(parent_item)
        else:
            item = QTreeWidgetItem(self._tree_widget)

        # Set item properties
        item.setText(0, node.text)
        item.setData(0, Qt.ItemDataRole.UserRole, node)

        if node.icon:
            item.setIcon(0, node.icon)

        if not node.selectable:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

        # Add children
        if node.children:
            for child_node in node.children:
                self._add_tree_item(item, child_node)

        # Set expanded state
        if node.expanded:
            item.setExpanded(True)

        return item

    def _find_item_by_node(self, node: FluentTreeNode) -> Optional['QTreeWidgetItem']:
        """Find tree item by node"""
        from PySide6.QtWidgets import QTreeWidgetItem  # Local import to avoid unused import warning

        def search_items(parent_item: Optional[QTreeWidgetItem] = None) -> Optional[QTreeWidgetItem]:
            if parent_item:
                count = parent_item.childCount()
                for i in range(count):
                    child = parent_item.child(i)
                    if child and child.data(0, Qt.ItemDataRole.UserRole) == node:
                        return child
                    result = search_items(child)
                    if result:
                        return result
            else:
                count = self._tree_widget.topLevelItemCount()
                for i in range(count):
                    item = self._tree_widget.topLevelItem(i)
                    if item and item.data(0, Qt.ItemDataRole.UserRole) == node:
                        return item
                    result = search_items(item)
                    if result:
                        return result
            return None

        return search_items()

    def _on_selection_changed(self) -> None:
        """Handle selection change"""
        selected_node = self.get_selected_node()
        if selected_node:
            self.item_selected.emit(selected_node)

    def _on_item_expanded(self, item) -> None:
        """Handle item expansion"""
        node = item.data(0, Qt.ItemDataRole.UserRole)
        if node:
            node.expanded = True
            self.item_expanded.emit(node)

    def _on_item_collapsed(self, item) -> None:
        """Handle item collapse"""
        node = item.data(0, Qt.ItemDataRole.UserRole)
        if node:
            node.expanded = False
            self.item_collapsed.emit(node)

    def _on_item_double_clicked(self, item, column) -> None:
        """Handle item double click"""
        node = item.data(0, Qt.ItemDataRole.UserRole)
        if node:
            self.item_double_clicked.emit(node)

    def _on_context_menu(self, position: QPoint) -> None:
        """Handle context menu request"""
        item = self._tree_widget.itemAt(position)
        if item:
            node = item.data(0, Qt.ItemDataRole.UserRole)
            if node:
                global_pos = self._tree_widget.mapToGlobal(position)
                self.context_menu_requested.emit(node, global_pos)

    def _on_size_changed(self) -> None:
        """Handle size changes"""
        size_map = {
            FluentComponentSize.TINY: 18,
            FluentComponentSize.SMALL: 20,
            FluentComponentSize.MEDIUM: 24,
            FluentComponentSize.LARGE: 28,
            FluentComponentSize.XLARGE: 32
        }
        # Ensure _size exists
        item_size = getattr(self, "_size", FluentComponentSize.MEDIUM)
        self._item_height = size_map.get(item_size, 24)
        self._apply_themed_styles()


# Helper functions for creating tree data

def create_tree_node(text: str, value: Any = None, icon: Optional[QIcon] = None,
                     expanded: bool = False, children: Optional[List[FluentTreeNode]] = None) -> FluentTreeNode:
    """Helper function to create tree nodes"""
    return FluentTreeNode(
        text=text,
        value=value,
        icon=icon,
        expanded=expanded,
        children=children or []
    )


def create_tree_from_dict(data: Union[Dict[str, Any], List[Dict[str, Any]]], text_key: str = "text",
                          children_key: str = "children") -> List[FluentTreeNode]:
    """Helper function to create tree from dictionary data"""
    def create_node(item: Dict[str, Any]) -> FluentTreeNode:
        text = item.get(text_key, "")
        value = item.get("value")
        expanded = item.get("expanded", False)

        children = []
        if children_key in item and item[children_key]:
            children = [create_node(child) for child in item[children_key]]

        return FluentTreeNode(
            text=text,
            value=value,
            expanded=expanded,
            children=children
        )

    if isinstance(data, list):
        return [create_node(item) for item in data]
    else:
        return [create_node(data)]
