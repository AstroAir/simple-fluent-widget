"""
Fluent Design Tree View and Hierarchical Data Components
Advanced tree structures, hierarchical data display, and relationship visualization
"""

from PySide6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame,
                               QAbstractItemView, QComboBox)
from PySide6.QtCore import Qt, Signal, QPoint, QRect
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QLinearGradient
from core.theme import theme_manager
from typing import Optional, List, Dict, Any


class FluentTreeWidget(QTreeWidget):
    """Fluent Design style tree widget with advanced features"""

    item_clicked_signal = Signal(QTreeWidgetItem, int)
    item_double_clicked_signal = Signal(QTreeWidgetItem, int)
    item_expanded_signal = Signal(QTreeWidgetItem)
    item_collapsed_signal = Signal(QTreeWidgetItem)
    item_context_menu = Signal(QTreeWidgetItem, QPoint)
    selection_changed_signal = Signal(list)  # List of selected items

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._search_text = ""
        self._expand_on_click = True
        self._show_icons = True
        self._alternating_colors = True
        self._checkable_items = False
        self._drag_drop_enabled = False

        self._setup_features()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_features(self):
        """Setup tree features"""
        # Enable various features
        self.setAnimated(True)
        self.setIndentation(20)
        self.setRootIsDecorated(True)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(self._alternating_colors)
        self.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setExpandsOnDoubleClick(True)

        # Header configuration
        self.header().setStretchLastSection(True)
        self.header().setDefaultSectionSize(150)

        # Connect signals
        self.itemClicked.connect(self._on_item_clicked)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.itemExpanded.connect(self._on_item_expanded)
        self.itemCollapsed.connect(self._on_item_collapsed)
        self.itemSelectionChanged.connect(self._on_selection_changed)

        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def addTopLevelItemFromDict(self, item_data: Dict[str, Any]) -> QTreeWidgetItem:
        """Add top-level item with data

        Args:
            item_data: Dictionary with 'text', 'icon', 'data', 'checkable', 'children'
        """
        item = self._create_tree_item(item_data)
        super().addTopLevelItem(item)
        return item

    def addChildItem(self, parent_item: QTreeWidgetItem,
                     item_data: Dict[str, Any]) -> QTreeWidgetItem:
        """Add child item to parent"""
        item = self._create_tree_item(item_data)
        parent_item.addChild(item)
        return item

    def _create_tree_item(self, item_data: Dict[str, Any]) -> QTreeWidgetItem:
        """Create tree item from data"""
        text = item_data.get('text', '')
        icon = item_data.get('icon', None)
        data = item_data.get('data', None)
        checkable = item_data.get('checkable', self._checkable_items)
        children = item_data.get('children', [])

        item = QTreeWidgetItem([text])

        if icon and self._show_icons:
            item.setIcon(0, icon)

        if data:
            item.setData(0, Qt.ItemDataRole.UserRole, data)

        if checkable:
            item.setCheckState(0, Qt.CheckState.Unchecked)

        # Add children recursively
        for child_data in children:
            child_item = self._create_tree_item(child_data)
            item.addChild(child_item)

        return item

    def setSearchText(self, text: str):
        """Filter tree items by search text"""
        self._search_text = text.lower()
        self._filter_items()

    def _filter_items(self):
        """Filter tree items based on search text"""
        if not self._search_text:
            # Show all items
            for i in range(self.topLevelItemCount()):
                item = self.topLevelItem(i)
                if item:
                    self._show_item_recursive(item, True)
            return

        # Hide items that don't match search
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item:
                should_show = self._item_matches_search(item)
                self._show_item_recursive(item, should_show)

    def _item_matches_search(self, item: QTreeWidgetItem) -> bool:
        """Check if item matches search text"""
        if self._search_text in item.text(0).lower():
            return True

        # Check children
        for i in range(item.childCount()):
            child = item.child(i)
            if child and self._item_matches_search(child):
                return True

        return False

    def _show_item_recursive(self, item: QTreeWidgetItem, show: bool):
        """Show/hide item and children recursively"""
        item.setHidden(not show)
        for i in range(item.childCount()):
            child = item.child(i)
            if child:
                child_show = show and (not self._search_text or
                                       self._item_matches_search(child))
                self._show_item_recursive(child, child_show)

    def expandAll(self):
        """Expand all items with animation"""
        super().expandAll()

    def collapseAll(self):
        """Collapse all items"""
        super().collapseAll()

    def getSelectedItemsData(self) -> List[Any]:
        """Get data from selected items"""
        data = []
        for item in self.selectedItems():
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data:
                data.append(item_data)
        return data

    def getCheckedItemsData(self) -> List[Any]:
        """Get data from checked items"""
        data = []
        self._collect_checked_items(self.invisibleRootItem(), data)
        return data

    def _collect_checked_items(self, parent: QTreeWidgetItem, data: List[Any]):
        """Collect checked items recursively"""
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child and child.checkState(0) == Qt.CheckState.Checked:
                item_data = child.data(0, Qt.ItemDataRole.UserRole)
                if item_data:
                    data.append(item_data)
            if child:
                self._collect_checked_items(child, data)

    def setDragDropEnabled(self, enabled: bool):
        """Enable/disable drag and drop"""
        self._drag_drop_enabled = enabled
        if enabled:
            self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        else:
            self.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)

    def _on_item_clicked(self, item: QTreeWidgetItem, _: int):
        """Handle item click"""
        self.item_clicked_signal.emit(item, 0)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, _: int):
        """Handle item double click"""
        self.item_double_clicked_signal.emit(item, 0)

    def _on_item_expanded(self, item: QTreeWidgetItem):
        """Handle item expansion"""
        self.item_expanded_signal.emit(item)

    def _on_item_collapsed(self, item: QTreeWidgetItem):
        """Handle item collapse"""
        self.item_collapsed_signal.emit(item)

    def _on_selection_changed(self):
        """Handle selection change"""
        self.selection_changed_signal.emit(self.selectedItems())

    def _show_context_menu(self, position: QPoint):
        """Show context menu"""
        item = self.itemAt(position)
        if item:
            global_pos = self.mapToGlobal(position)
            self.item_context_menu.emit(item, global_pos)

    def _setup_style(self):
        """Setup tree style"""
        theme = theme_manager

        style_sheet = f"""
            QTreeWidget {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                selection-background-color: {theme.get_color('primary').name()};
                selection-color: white;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                outline: none;
            }}
            QTreeWidget::item {{
                padding: 6px;
                border: none;
                border-bottom: 1px solid transparent;
            }}
            QTreeWidget::item:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-radius: 4px;
            }}
            QTreeWidget::item:selected {{
                background-color: {theme.get_color('primary').name()};
                color: white;
                border-radius: 4px;
            }}
            QTreeWidget::item:selected:hover {{
                background-color: {theme.get_color('primary').darker(110).name()};
            }}
            QTreeWidget::branch {{
                background-color: transparent;
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
            QTreeWidget::branch:has-children:!has-siblings:closed:hover,
            QTreeWidget::branch:closed:has-children:has-siblings:hover,
            QTreeWidget::branch:open:has-children:!has-siblings:hover,
            QTreeWidget::branch:open:has-children:has-siblings:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-radius: 2px;
            }}
            QHeaderView::section {{
                background-color: {theme.get_color('surface').name()};
                border: none;
                border-bottom: 2px solid {theme.get_color('primary').name()};
                border-right: 1px solid {theme.get_color('border').name()};
                padding: 8px;
                font-weight: 600;
                color: {theme.get_color('text_primary').name()};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {theme.get_color('background').name()};
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {theme.get_color('border').name()};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme.get_color('text_secondary').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentHierarchicalView(QWidget):
    """Advanced hierarchical data viewer with search and filtering"""

    item_selected = Signal(dict)  # Selected item data
    item_activated = Signal(dict)  # Double-clicked item data

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._data = []
        self._filtered_data = []
        self._search_term = ""
        self._selected_filters = {}

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(8)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search items...")
        self.search_box.textChanged.connect(self._on_search_changed)

        # Filter button
        self.filter_btn = QPushButton("Filters")
        self.filter_btn.setCheckable(True)
        self.filter_btn.clicked.connect(self._toggle_filters)

        # Expand/collapse buttons
        self.expand_all_btn = QPushButton("Expand All")
        self.expand_all_btn.clicked.connect(self._expand_all)

        self.collapse_all_btn = QPushButton("Collapse All")
        self.collapse_all_btn.clicked.connect(self._collapse_all)

        toolbar_layout.addWidget(QLabel("Search:"))
        toolbar_layout.addWidget(self.search_box)
        toolbar_layout.addWidget(self.filter_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.expand_all_btn)
        toolbar_layout.addWidget(self.collapse_all_btn)

        # Filter panel (initially hidden)
        self.filter_panel = QFrame()
        self.filter_panel.setVisible(False)
        self.filter_layout = QHBoxLayout(self.filter_panel)
        self.filter_layout.setContentsMargins(12, 8, 12, 8)

        # Tree widget
        self.tree = FluentTreeWidget()
        self.tree.setHeaderLabels(["Name", "Type", "Status", "Modified"])
        self.tree.item_clicked_signal.connect(self._on_item_selected)
        self.tree.item_double_clicked_signal.connect(self._on_item_activated)

        layout.addWidget(toolbar)
        layout.addWidget(self.filter_panel)
        layout.addWidget(self.tree)

    def setData(self, data: List[Dict[str, Any]]):
        """Set hierarchical data

        Args:
            data: List of hierarchical data dictionaries
        """
        self._data = data
        self._refresh_tree()

    def addItem(self, item_data: Dict[str, Any]):
        """Add single item"""
        self._data.append(item_data)
        self._refresh_tree()

    def _refresh_tree(self):
        """Refresh tree display"""
        self.tree.clear()

        # Apply search and filters
        filtered_data = self._apply_filters(self._data)

        # Populate tree
        for item_data in filtered_data:
            self.tree.addTopLevelItemFromDict(item_data)

    def _apply_filters(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply search and filters to data"""
        filtered = data

        # Apply search filter
        if self._search_term:
            filtered = [item for item in filtered
                        if self._item_matches_search(item, self._search_term)]

        # Apply custom filters
        for filter_key, filter_value in self._selected_filters.items():
            if filter_value:
                filtered = [item for item in filtered
                            if item.get(filter_key) == filter_value]

        return filtered

    def _item_matches_search(self, item: Dict[str, Any], search_term: str) -> bool:
        """Check if item matches search term"""
        search_lower = search_term.lower()

        # Search in text fields
        searchable_fields = ['text', 'name', 'title', 'description']
        for field in searchable_fields:
            if field in item and search_lower in str(item[field]).lower():
                return True

        # Search in children
        children = item.get('children', [])
        return any(self._item_matches_search(child, search_term) for child in children)

    def _on_search_changed(self, text: str):
        """Handle search text change"""
        self._search_term = text
        self.tree.setSearchText(text)

    def _toggle_filters(self):
        """Toggle filter panel visibility"""
        self.filter_panel.setVisible(self.filter_btn.isChecked())

    def _expand_all(self):
        """Expand all tree items"""
        self.tree.expandAll()

    def _collapse_all(self):
        """Collapse all tree items"""
        self.tree.collapseAll()

    def _on_item_selected(self, item: QTreeWidgetItem, _: int):
        """Handle item selection"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            self.item_selected.emit(data)

    def _on_item_activated(self, item: QTreeWidgetItem, _: int):
        """Handle item activation (double-click)"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            self.item_activated.emit(data)

    def addFilter(self, filter_name: str, filter_values: List[str]):
        """Add filter option"""
        filter_label = QLabel(f"{filter_name}:")
        filter_combo = QComboBox()
        filter_combo.addItem("All")
        filter_combo.addItems(filter_values)
        filter_combo.currentTextChanged.connect(
            lambda value, name=filter_name: self._on_filter_changed(name, value))

        self.filter_layout.addWidget(filter_label)
        self.filter_layout.addWidget(filter_combo)

    def _on_filter_changed(self, filter_name: str, filter_value: str):
        """Handle filter change"""
        if filter_value == "All":
            self._selected_filters.pop(filter_name, None)
        else:
            self._selected_filters[filter_name] = filter_value

        self._refresh_tree()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
            QLineEdit {{
                background-color: {theme.get_color('surface').name()};
                border: 2px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                min-width: 200px;
            }}
            QLineEdit:focus {{
                border-color: {theme.get_color('primary').name()};
            }}
            QPushButton {{
                background-color: {theme.get_color('primary').name()};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('primary').darker(110).name()};
            }}
            QPushButton:checked {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QLabel {{
                color: {theme.get_color('text_secondary').name()};
                font-size: 14px;
                font-weight: 500;
            }}
            QComboBox {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 100px;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentOrgChart(QWidget):
    """Organization chart widget for displaying hierarchical relationships"""

    node_clicked = Signal(dict)  # Node data
    node_double_clicked = Signal(dict)  # Node data

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._nodes = {}  # id -> node_data
        self._connections = []  # List of (parent_id, child_id) tuples
        self._node_positions = {}  # id -> (x, y)
        self._node_size = (120, 80)
        self._level_height = 120
        self._node_spacing = 140

        self.setMinimumSize(400, 300)

        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def addNode(self, node_id: str, node_data: Dict[str, Any], parent_id: Optional[str] = None):
        """Add node to organization chart

        Args:
            node_id: Unique node identifier
            node_data: Node data (title, subtitle, image, etc.)
            parent_id: Parent node ID (None for root)
        """
        self._nodes[node_id] = node_data

        if parent_id and parent_id in self._nodes:
            self._connections.append((parent_id, node_id))

        self._calculate_layout()
        self.update()

    def removeNode(self, node_id: str):
        """Remove node and its connections"""
        if node_id in self._nodes:
            del self._nodes[node_id]

            # Remove connections
            self._connections = [(p, c) for p, c in self._connections
                                 if p != node_id and c != node_id]

            self._calculate_layout()
            self.update()

    def clearNodes(self):
        """Clear all nodes"""
        self._nodes.clear()
        self._connections.clear()
        self._node_positions.clear()
        self.update()

    def _calculate_layout(self):
        """Calculate node positions using hierarchical layout"""
        if not self._nodes:
            return

        # Find root nodes (nodes with no parents)
        children_map = {}
        for parent_id, child_id in self._connections:
            if parent_id not in children_map:
                children_map[parent_id] = []
            children_map[parent_id].append(child_id)

        parent_map = {child: parent for parent, child in self._connections}
        root_nodes = [node_id for node_id in self._nodes.keys()
                      if node_id not in parent_map]

        if not root_nodes:
            # If no clear hierarchy, treat first node as root
            # This check is safe because we return early if self._nodes is empty
            root_nodes = [list(self._nodes.keys())[0]]

        # Calculate positions level by level
        self._node_positions.clear()

        current_x_offset = 0.0
        for root_id in root_nodes:
            # Ensure multiple root nodes are laid out side-by-side
            subtree_width = self._position_subtree(
                root_id, 0, current_x_offset, children_map)
            current_x_offset += subtree_width

    def _position_subtree(self, node_id: str, level: int, x_offset: float,
                          children_map: Dict[str, List[str]]) -> float:
        """Position a subtree and return its width"""
        children = children_map.get(node_id, [])

        if not children:
            # Leaf node
            x = x_offset
            y = level * self._level_height + 40
            self._node_positions[node_id] = (x, y)
            return self._node_spacing

        # Position children first
        child_x = x_offset
        total_width = 0

        for child_id in children:
            child_width = self._position_subtree(child_id, level + 1,
                                                 child_x, children_map)
            child_x += child_width
            total_width += child_width

        # Position parent node centered above children
        # Fixed: Use _node_size[0] for centering
        parent_x = x_offset + (total_width - self._node_size[0]) / 2
        parent_y = level * self._level_height + 40
        self._node_positions[node_id] = (parent_x, parent_y)

        return total_width

    def paintEvent(self, event):  # Renamed _ to event for clarity, though _ is fine
        """Paint organization chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = theme_manager

        # Draw connections first
        painter.setPen(QPen(theme.get_color('border'), 2))
        for parent_id, child_id in self._connections:
            if parent_id in self._node_positions and child_id in self._node_positions:
                parent_pos = self._node_positions[parent_id]
                child_pos = self._node_positions[child_id]

                # Draw connection line
                parent_center_x = parent_pos[0] + self._node_size[0] // 2
                parent_bottom_y = parent_pos[1] + self._node_size[1]
                child_center_x = child_pos[0] + self._node_size[0] // 2
                child_top_y = child_pos[1]

                # Draw L-shaped connection
                mid_y = parent_bottom_y + (child_top_y - parent_bottom_y) // 2

                painter.drawLine(parent_center_x, parent_bottom_y,
                                 parent_center_x, mid_y)
                painter.drawLine(parent_center_x, mid_y,
                                 child_center_x, mid_y)
                painter.drawLine(child_center_x, mid_y,
                                 child_center_x, child_top_y)

        # Draw nodes
        for node_id, node_data in self._nodes.items():
            if node_id in self._node_positions:
                pos = self._node_positions[node_id]
                self._draw_node(painter, pos, node_data)

    def _draw_node(self, painter: QPainter, position: tuple, node_data: Dict[str, Any]):
        """Draw a single node"""
        theme = theme_manager
        x, y = position

        # Node background
        node_rect = QRect(int(x), int(
            y), self._node_size[0], self._node_size[1])

        # Create gradient background
        gradient = QLinearGradient(x, y, x, y + self._node_size[1])
        gradient.setColorAt(0, theme.get_color('surface'))
        gradient.setColorAt(1, theme.get_color('surface').darker(105))

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(theme.get_color('border'), 2))
        painter.drawRoundedRect(node_rect, 8, 8)

        # Node content
        painter.setPen(QPen(theme.get_color('text_primary')))

        # Title
        title = node_data.get('title', 'Node')
        painter.setFont(QFont("", 11, QFont.Weight.Bold))
        title_rect = QRect(int(x) + 8, int(y) + 8, self._node_size[0] - 16, 20)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, title)

        # Subtitle
        subtitle = node_data.get('subtitle', '')
        if subtitle:
            painter.setFont(QFont("", 9))
            painter.setPen(QPen(theme.get_color('text_secondary')))
            subtitle_rect = QRect(int(x) + 8, int(y) + 30,
                                  self._node_size[0] - 16, 16)
            painter.drawText(
                subtitle_rect, Qt.AlignmentFlag.AlignCenter, subtitle)

        # Status indicator
        status = node_data.get('status', '')
        if status:
            status_color = {
                'active': QColor("#28a745"),
                'inactive': QColor("#dc3545"),
                'pending': QColor("#ffc107")
            }.get(status.lower(), theme.get_color('text_secondary'))

            painter.setBrush(QBrush(status_color))
            # Use a non-stroking pen or set to Qt.NoPen for solid fill
            painter.setPen(QPen(status_color))
            painter.drawEllipse(
                int(x) + self._node_size[0] - 20, int(y) + 8, 8, 8)

    def mousePressEvent(self, event):
        """Handle mouse press"""
        for node_id, position in self._node_positions.items():
            x, y = position
            node_rect = QRect(int(x), int(
                y), self._node_size[0], self._node_size[1])

            if node_rect.contains(event.pos()):
                node_data = self._nodes[node_id].copy()  # Emit a copy
                node_data['id'] = node_id

                if event.button() == Qt.MouseButton.LeftButton:
                    self.node_clicked.emit(node_data)
                break

    def mouseDoubleClickEvent(self, event):
        """Handle mouse double click"""
        for node_id, position in self._node_positions.items():
            x, y = position
            node_rect = QRect(int(x), int(
                y), self._node_size[0], self._node_size[1])

            if node_rect.contains(event.pos()):
                node_data = self._nodes[node_id].copy()  # Emit a copy
                node_data['id'] = node_id
                self.node_double_clicked.emit(node_data)
                break

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager
        self.setStyleSheet(f"""
            FluentOrgChart {{
                background-color: {theme.get_color('background').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
        """)

    def _on_theme_changed(self, _):  # Renamed to _ as it's unused
        """Handle theme change"""
        self._setup_style()
        self.update()
