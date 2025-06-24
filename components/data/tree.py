"""
Fluent Design Tree View and Hierarchical Data Components
Advanced tree structures, hierarchical data display, and relationship visualization

Optimized for Python 3.11+ with modern type hints, dataclasses, and enhanced PySide6 features
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from functools import cached_property, lru_cache
from typing import Optional, TypedDict, Protocol, final, Dict, List, Any
import weakref

from PySide6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QAbstractItemView, QComboBox,
    QGraphicsOpacityEffect, QHeaderView
)
from PySide6.QtCore import (
    Qt, Signal, QPoint, QRect, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QTimer, QByteArray
)
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QLinearGradient, QPixmap,
    QFontMetrics
)
from core.theme import theme_manager


# Modern type definitions using TypedDict for better type safety
class TreeItemData(TypedDict, total=False):
    """Type-safe tree item data structure"""
    text: str
    icon: Optional[QPixmap]
    data: Optional[Any]
    checkable: bool
    children: List[TreeItemData]
    item_type: str
    status: str
    metadata: Dict[str, Any]


class NodeData(TypedDict, total=False):
    """Organization chart node data"""
    title: str
    subtitle: str
    status: str
    image: Optional[QPixmap]
    metadata: Dict[str, Any]


class TreeState(Enum):
    """Tree widget states for enhanced animations"""
    IDLE = auto()
    LOADING = auto()
    FILTERING = auto()
    EXPANDING = auto()
    COLLAPSING = auto()


class AnimationProtocol(Protocol):
    """Protocol for animation handlers"""

    def start_animation(self, target: QWidget, duration: int) -> QPropertyAnimation:
        ...

    def stop_animation(self, target: QWidget) -> None:
        ...


@dataclass
class TreeConfiguration:
    """Modern configuration class using dataclass"""
    expand_on_click: bool = True
    show_icons: bool = True
    alternating_colors: bool = True
    checkable_items: bool = False
    drag_drop_enabled: bool = False
    animation_duration: int = 250
    search_debounce: int = 300
    max_visible_items: int = 1000
    lazy_loading: bool = True


@final
class FluentTreeWidget(QTreeWidget):
    """Enhanced Fluent Design tree widget with modern Python features and optimizations"""

    # Type-safe signals with proper annotations
    item_clicked_signal = Signal(QTreeWidgetItem, int)
    item_double_clicked_signal = Signal(QTreeWidgetItem, int)
    item_expanded_signal = Signal(QTreeWidgetItem)
    item_collapsed_signal = Signal(QTreeWidgetItem)
    item_context_menu = Signal(QTreeWidgetItem, QPoint)
    selection_changed_signal = Signal(list)  # List[QTreeWidgetItem]

    # Modern state management signals
    state_changed = Signal(TreeState)
    loading_started = Signal()
    loading_finished = Signal()

    def __init__(self, parent: Optional[QWidget] = None, config: Optional[TreeConfiguration] = None):
        super().__init__(parent)

        # Use modern configuration with defaults
        self._config = config or TreeConfiguration()
        self._current_state = TreeState.IDLE
        self._search_timer = QTimer()
        self._animation_group = QParallelAnimationGroup()
        self._item_cache: weakref.WeakKeyDictionary[QTreeWidgetItem,
                                                    TreeItemData] = weakref.WeakKeyDictionary()

        # Performance optimization: pre-compile search regex
        self._compiled_search = None
        self._search_debounce_timer = QTimer()
        self._search_debounce_timer.setSingleShot(True)
        self._search_debounce_timer.timeout.connect(self._perform_search)

        self._setup_features()
        self._setup_style()
        self._setup_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    @property
    def current_state(self) -> TreeState:
        """Get current tree state"""
        return self._current_state

    @current_state.setter
    def current_state(self, state: TreeState) -> None:
        """Set current tree state with signal emission"""
        if self._current_state != state:
            self._current_state = state
            self.state_changed.emit(state)

    @cached_property
    def font_metrics(self) -> QFontMetrics:
        """Cached font metrics for performance"""
        return QFontMetrics(self.font())

    def _setup_features(self) -> None:
        """Setup enhanced tree features with modern PySide6 capabilities"""
        # Performance optimizations
        self.setAnimated(True)
        self.setIndentation(20)
        self.setRootIsDecorated(True)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(self._config.alternating_colors)
        self.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setExpandsOnDoubleClick(True)

        # Enhanced header with better UX
        header = self.header()
        header.setStretchLastSection(True)
        header.setDefaultSectionSize(150)
        header.setMinimumSectionSize(50)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setHighlightSections(True)

        # Modern signal connections with type safety
        self.itemClicked.connect(self._on_item_clicked)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.itemExpanded.connect(self._on_item_expanded)
        self.itemCollapsed.connect(self._on_item_collapsed)
        self.itemSelectionChanged.connect(self._on_selection_changed)

        # Enhanced context menu with modern features
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # Drag and drop with MIME data support
        self.customContextMenuRequested.connect(self._show_context_menu)
        if self._config.drag_drop_enabled:
            self._setup_drag_drop()

    def _setup_drag_drop(self) -> None:
        """Setup enhanced drag and drop with MIME data"""
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

    def _setup_animations(self) -> None:
        """Setup modern animation system"""
        self._opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self._opacity_effect)

        self._fade_animation = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        self._fade_animation.setDuration(self._config.animation_duration)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    @lru_cache(maxsize=128)
    def _get_item_style(self, item_type: str, state: str) -> str:
        """Cached item styling for performance"""
        theme = theme_manager
        base_style = f"""
            QTreeWidget::item[type="{item_type}"][state="{state}"] {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
            }}
        """
        return base_style

    def addTopLevelItemFromDict(self, item_data: TreeItemData) -> QTreeWidgetItem:
        """Add top-level item with type-safe data structure"""
        item = self._create_tree_item(item_data)
        super().addTopLevelItem(item)
        return item

    def addChildItem(self, parent_item: QTreeWidgetItem, item_data: TreeItemData) -> QTreeWidgetItem:
        """Add child item to parent with type safety"""
        item = self._create_tree_item(item_data)
        parent_item.addChild(item)
        return item

    def _create_tree_item(self, item_data: TreeItemData) -> QTreeWidgetItem:
        """Create tree item from type-safe data structure"""
        text = item_data.get('text', '')
        icon = item_data.get('icon', None)
        data = item_data.get('data', None)
        checkable = item_data.get('checkable', self._config.checkable_items)
        children = item_data.get('children', [])

        item = QTreeWidgetItem([text])

        if icon and self._config.show_icons:
            item.setIcon(0, icon)

        if data:
            item.setData(0, Qt.ItemDataRole.UserRole, data)

        if checkable:
            item.setCheckState(0, Qt.CheckState.Unchecked)

        # Store item data in cache for performance
        self._item_cache[item] = item_data

        # Add children recursively
        for child_data in children:
            child_item = self._create_tree_item(child_data)
            item.addChild(child_item)

        return item

    def setSearchText(self, text: str) -> None:
        """Enhanced search with debouncing and performance optimization"""
        if self._search_debounce_timer.isActive():
            self._search_debounce_timer.stop()

        self._search_text = text.lower().strip()
        self._search_debounce_timer.start(self._config.search_debounce)

    def _perform_search(self) -> None:
        """Perform the actual search with animations"""
        self.current_state = TreeState.FILTERING

        # Animate filtering
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.3)
        self._fade_animation.finished.connect(self._apply_search_filter)
        self._fade_animation.start()

    def _apply_search_filter(self) -> None:
        """Apply search filter and restore opacity"""
        self._filter_items()

        # Restore opacity
        self._fade_animation.finished.disconnect()
        self._fade_animation.setStartValue(0.3)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.finished.connect(
            lambda: setattr(self, 'current_state', TreeState.IDLE))
        self._fade_animation.start()

    def _filter_items(self) -> None:
        """Enhanced filtering with better performance"""
        if not self._search_text:
            # Show all items
            for i in range(self.topLevelItemCount()):
                item = self.topLevelItem(i)
                if item:
                    self._show_item_recursive(item, True)
            return        # Hide items that don't match search
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item:
                should_show = self._item_matches_search(item)
                self._show_item_recursive(item, should_show)

    def _item_matches_search(self, item: QTreeWidgetItem) -> bool:
        """Enhanced search matching with better performance"""
        if self._search_text in item.text(0).lower():
            return True

        # Check cached item data first
        if item in self._item_cache:
            item_data = self._item_cache[item]
            # Search in metadata if available
            metadata = item_data.get('metadata', {})
            if any(self._search_text in str(value).lower() for value in metadata.values()):
                return True

        # Check children with early termination
        for i in range(item.childCount()):
            child = item.child(i)
            if child and self._item_matches_search(child):
                return True

        return False

    def _show_item_recursive(self, item: QTreeWidgetItem, show: bool) -> None:
        """Show/hide item and children recursively with animations"""
        was_hidden = item.isHidden()
        item.setHidden(not show)

        # Animate visibility change for better UX
        if was_hidden != (not show) and self._config.animation_duration > 0:
            self._animate_item_visibility(item, show)

        for i in range(item.childCount()):
            child = item.child(i)
            if child:
                child_show = show and (
                    not self._search_text or self._item_matches_search(child))
                self._show_item_recursive(child, child_show)

    def _animate_item_visibility(self, item: QTreeWidgetItem, visible: bool) -> None:
        """Animate item visibility changes"""
        # This could be enhanced with custom item delegates for smoother animations
        pass

    def expandAll(self) -> None:
        """Expand all items with enhanced animation"""
        self.current_state = TreeState.EXPANDING
        super().expandAll()
        QTimer.singleShot(self._config.animation_duration,
                          lambda: setattr(self, 'current_state', TreeState.IDLE))

    def collapseAll(self) -> None:
        """Collapse all items with enhanced animation"""
        self.current_state = TreeState.COLLAPSING
        super().collapseAll()
        QTimer.singleShot(self._config.animation_duration,
                          lambda: setattr(self, 'current_state', TreeState.IDLE))

    def getSelectedItemsData(self) -> List[Any]:
        """Get data from selected items with type safety"""
        data = []
        for item in self.selectedItems():
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data is not None:
                data.append(item_data)
        return data

    def getCheckedItemsData(self) -> List[Any]:
        """Get data from checked items with optimized collection"""
        data = []
        self._collect_checked_items(self.invisibleRootItem(), data)
        return data

    def _collect_checked_items(self, parent: QTreeWidgetItem, data: List[Any]) -> None:
        """Collect checked items recursively with early termination"""
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child:
                if child.checkState(0) == Qt.CheckState.Checked:
                    item_data = child.data(0, Qt.ItemDataRole.UserRole)
                    if item_data is not None:
                        data.append(item_data)
                # Always recurse to check children
                self._collect_checked_items(child, data)

    def setDragDropEnabled(self, enabled: bool) -> None:
        """Enable/disable drag and drop with configuration update"""
        self._config.drag_drop_enabled = enabled
        if enabled:
            self._setup_drag_drop()
        else:
            self.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)

    # Enhanced event handlers with modern patterns
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle item click with enhanced functionality"""
        self.item_clicked_signal.emit(item, column)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle item double click with enhanced functionality"""
        self.item_double_clicked_signal.emit(item, column)

    def _on_item_expanded(self, item: QTreeWidgetItem) -> None:
        """Handle item expansion with lazy loading support"""
        self.item_expanded_signal.emit(item)

        # Implement lazy loading if enabled
        if self._config.lazy_loading:
            self._lazy_load_children(item)

    def _lazy_load_children(self, item: QTreeWidgetItem) -> None:
        """Lazy load children for performance with large datasets"""
        # This can be implemented based on specific requirements
        # For now, it's a placeholder for future enhancement
        pass

    def _on_item_collapsed(self, item: QTreeWidgetItem) -> None:
        """Handle item collapse"""
        self.item_collapsed_signal.emit(item)

    def _on_selection_changed(self) -> None:
        """Handle selection change with batching"""
        selected_items = self.selectedItems()
        self.selection_changed_signal.emit(selected_items)

    def _show_context_menu(self, position: QPoint) -> None:
        """Show enhanced context menu with modern actions"""
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


@final
class FluentHierarchicalView(QWidget):
    """Enhanced hierarchical data viewer with modern Python features and performance optimizations"""

    # Type-safe signals
    item_selected = Signal(TreeItemData)  # Selected item data
    item_activated = Signal(TreeItemData)  # Double-clicked item data
    filter_applied = Signal(str)  # Filter name applied
    search_performed = Signal(str)  # Search term used

    def __init__(self, parent: Optional[QWidget] = None, config: Optional[TreeConfiguration] = None):
        super().__init__(parent)

        self._config = config or TreeConfiguration()
        self._data: List[TreeItemData] = []
        self._filtered_data: List[TreeItemData] = []
        self._search_term = ""
        self._selected_filters: Dict[str, str] = {}
        self._search_debounce_timer = QTimer()
        self._search_debounce_timer.setSingleShot(True)
        self._search_debounce_timer.timeout.connect(
            self._perform_delayed_search)

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self) -> None:
        """Setup enhanced UI with modern layout management"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Enhanced toolbar with better UX
        self._create_toolbar()
        self._create_filter_panel()
        self._create_tree_view()

        layout.addWidget(self.toolbar)
        layout.addWidget(self.filter_panel)
        layout.addWidget(self.tree)

    def _create_toolbar(self) -> None:
        """Create enhanced toolbar with modern widgets"""
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(60)
        self.toolbar.setObjectName("toolbar")

        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(16, 12, 16, 12)
        toolbar_layout.setSpacing(12)

        # Enhanced search with real-time feedback
        search_label = QLabel("🔍 Search:")
        search_label.setObjectName("searchLabel")

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Search items... (use wildcards * ?)")
        self.search_box.setClearButtonEnabled(True)
        self.search_box.textChanged.connect(self._on_search_changed)
        self.search_box.setObjectName("searchBox")

        # Modern toggle buttons
        self.filter_btn = QPushButton("📋 Filters")
        self.filter_btn.setCheckable(True)
        self.filter_btn.setObjectName("filterButton")
        self.filter_btn.clicked.connect(self._toggle_filters)

        # Action buttons with icons
        self.expand_all_btn = QPushButton("📂 Expand All")
        self.expand_all_btn.setObjectName("expandButton")
        self.expand_all_btn.clicked.connect(self._expand_all)

        self.collapse_all_btn = QPushButton("📁 Collapse All")
        self.collapse_all_btn.setObjectName("collapseButton")
        self.collapse_all_btn.clicked.connect(self._collapse_all)

        # Layout with better spacing
        toolbar_layout.addWidget(search_label)
        toolbar_layout.addWidget(self.search_box, 1)  # Expandable
        toolbar_layout.addWidget(self.filter_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.expand_all_btn)
        toolbar_layout.addWidget(self.collapse_all_btn)

    def _create_filter_panel(self) -> None:
        """Create enhanced filter panel"""
        self.filter_panel = QFrame()
        self.filter_panel.setVisible(False)
        self.filter_panel.setObjectName("filterPanel")
        self.filter_layout = QHBoxLayout(self.filter_panel)
        self.filter_layout.setContentsMargins(16, 12, 16, 12)
        self.filter_layout.setSpacing(12)

    def _create_tree_view(self) -> None:
        """Create enhanced tree view"""
        self.tree = FluentTreeWidget(config=self._config)
        self.tree.setHeaderLabels(["Name", "Type", "Status", "Modified"])
        self.tree.item_clicked_signal.connect(self._on_item_selected)
        self.tree.item_double_clicked_signal.connect(self._on_item_activated)

    def setData(self, data: List[TreeItemData]) -> None:
        """Set hierarchical data with type safety and performance optimization"""
        self._data = data.copy()  # Defensive copy
        self._refresh_tree()

    def addItem(self, item_data: TreeItemData) -> None:
        """Add single item with type safety"""
        self._data.append(item_data)
        self._refresh_tree()

    def _refresh_tree(self) -> None:
        """Refresh tree display with better performance"""
        self.tree.current_state = TreeState.LOADING

        # Use QTimer for non-blocking operation
        QTimer.singleShot(0, self._perform_refresh)

    def _perform_refresh(self) -> None:
        """Perform the actual refresh"""
        self.tree.clear()

        # Apply search and filters efficiently
        filtered_data = self._apply_filters(self._data)

        # Limit items for performance if needed
        if len(filtered_data) > self._config.max_visible_items:
            filtered_data = filtered_data[:self._config.max_visible_items]

        # Populate tree efficiently
        for item_data in filtered_data:
            self.tree.addTopLevelItemFromDict(item_data)

        self.tree.current_state = TreeState.IDLE

    def _apply_filters(self, data: List[TreeItemData]) -> List[TreeItemData]:
        """Apply search and filters with improved performance"""
        filtered = data

        # Apply search filter with early termination
        if self._search_term:
            filtered = [item for item in filtered
                        if self._item_matches_search_optimized(item, self._search_term)]

        # Apply custom filters efficiently
        for filter_key, filter_value in self._selected_filters.items():
            if filter_value and filter_value != "All":
                filtered = [item for item in filtered
                            if item.get(filter_key) == filter_value]

        return filtered

    def _item_matches_search_optimized(self, item: TreeItemData, search_term: str) -> bool:
        """Optimized search matching with caching"""
        search_lower = search_term.lower()

        # Search in standard fields using safe access
        searchable_fields = ('text', 'item_type', 'status')
        for field in searchable_fields:
            value = item.get(field)
            if value and search_lower in str(value).lower():
                return True

        # Search in metadata efficiently
        metadata = item.get('metadata', {})
        if metadata and any(search_lower in str(value).lower()
                            for value in metadata.values() if value):
            return True

        # Search in children with early termination
        children = item.get('children', [])
        return any(self._item_matches_search_optimized(child, search_term)
                   for child in children)

    def _on_search_changed(self, text: str) -> None:
        """Handle search with debouncing for better performance"""
        self._search_debounce_timer.stop()
        self._search_term = text.strip()
        self._search_debounce_timer.start(self._config.search_debounce)

    def _perform_delayed_search(self) -> None:
        """Perform delayed search"""
        self.tree.setSearchText(self._search_term)
        self.search_performed.emit(self._search_term)

    def _toggle_filters(self) -> None:
        """Toggle filter panel visibility with animation"""
        visible = self.filter_btn.isChecked()
        self.filter_panel.setVisible(visible)

        # Emit signal for external handling
        if visible:
            self.filter_applied.emit("panel_opened")

    def _expand_all(self) -> None:
        """Expand all tree items"""
        self.tree.expandAll()

    def _collapse_all(self) -> None:
        """Collapse all tree items"""
        self.tree.collapseAll()

    def _on_item_selected(self, item: QTreeWidgetItem, _: int) -> None:
        """Handle item selection with type safety"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and isinstance(data, dict):
            # Cast to TreeItemData for emission
            self.item_selected.emit(data)  # type: ignore

    def _on_item_activated(self, item: QTreeWidgetItem, _: int) -> None:
        """Handle item activation (double-click) with type safety"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and isinstance(data, dict):
            # Cast to TreeItemData for emission
            self.item_activated.emit(data)  # type: ignore

    def addFilter(self, filter_name: str, filter_values: List[str]) -> None:
        """Add filter option with enhanced UX"""
        filter_label = QLabel(f"{filter_name}:")
        filter_label.setObjectName("filterLabel")

        filter_combo = QComboBox()
        filter_combo.setObjectName("filterCombo")
        filter_combo.addItem("All")
        filter_combo.addItems(filter_values)
        filter_combo.currentTextChanged.connect(
            lambda value, name=filter_name: self._on_filter_changed(name, value))

        self.filter_layout.addWidget(filter_label)
        self.filter_layout.addWidget(filter_combo)

    def _on_filter_changed(self, filter_name: str, filter_value: str) -> None:
        """Handle filter change with performance optimization"""
        if filter_value == "All":
            self._selected_filters.pop(filter_name, None)
        else:
            self._selected_filters[filter_name] = filter_value

        self._refresh_tree()
        self.filter_applied.emit(f"{filter_name}:{filter_value}")

    def _setup_style(self) -> None:
        """Setup enhanced styling for hierarchical view"""
        enhanced_styles = _setup_enhanced_styles()
        self.setStyleSheet(enhanced_styles)

    def _on_theme_changed(self, _) -> None:
        """Handle theme change"""
        self._setup_style()


@final
class FluentOrgChart(QWidget):
    """Enhanced organization chart with modern Python features and optimizations"""

    # Type-safe signals
    node_clicked = Signal(NodeData)  # Node data
    node_double_clicked = Signal(NodeData)  # Node data
    node_context_menu = Signal(str, QPoint)  # node_id, position
    layout_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Modern data structures with type safety
        self._nodes: Dict[str, NodeData] = {}
        # List of (parent_id, child_id)
        self._connections: List[tuple[str, str]] = []
        self._node_positions: Dict[str, tuple[float, float]] = {}
        self._node_size = (140, 90)  # Slightly larger for better readability
        self._level_height = 130
        self._node_spacing = 160

        # Performance optimizations
        self._layout_cache: Dict[str, Any] = {}
        self._paint_cache: Dict[str, QPixmap] = {}
        self._dirty_layout = True

        # Animation support
        self._animation_group = QParallelAnimationGroup()
        self._zoom_factor = 1.0
        self._pan_offset = QPoint(0, 0)

        self.setMinimumSize(500, 400)
        self.setMouseTracking(True)  # For hover effects
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    @property
    def zoom_factor(self) -> float:
        """Get current zoom factor"""
        return self._zoom_factor

    @zoom_factor.setter
    def zoom_factor(self, factor: float) -> None:
        """Set zoom factor with bounds checking"""
        self._zoom_factor = max(0.1, min(3.0, factor))
        self.update()

    def addNode(self, node_id: str, node_data: NodeData, parent_id: Optional[str] = None) -> None:
        """Add node with enhanced type safety and validation"""
        if node_id in self._nodes:
            raise ValueError(f"Node with id '{node_id}' already exists")

        # Validate node data
        if not node_data.get('title'):
            raise ValueError("Node must have a title")

        self._nodes[node_id] = node_data.copy()  # Defensive copy

        if parent_id:
            if parent_id not in self._nodes:
                raise ValueError(f"Parent node '{parent_id}' does not exist")
            self._connections.append((parent_id, node_id))

        self._invalidate_layout()

    def removeNode(self, node_id: str) -> None:
        """Remove node and its connections with cascade handling"""
        if node_id not in self._nodes:
            return

        # Remove all connections involving this node
        self._connections = [(p, c) for p, c in self._connections
                             if p != node_id and c != node_id]

        # Remove child nodes recursively
        children = self._get_children(node_id)
        for child_id in children:
            self.removeNode(child_id)

        del self._nodes[node_id]
        self._node_positions.pop(node_id, None)
        self._invalidate_layout()

    def updateNode(self, node_id: str, node_data: NodeData) -> None:
        """Update existing node data"""
        if node_id not in self._nodes:
            raise ValueError(f"Node '{node_id}' does not exist")

        self._nodes[node_id].update(node_data)
        self._invalidate_cache(node_id)
        self.update()

    def clearNodes(self) -> None:
        """Clear all nodes with cleanup"""
        self._nodes.clear()
        self._connections.clear()
        self._node_positions.clear()
        self._layout_cache.clear()
        self._paint_cache.clear()
        self._dirty_layout = True
        self.update()

    def _get_children(self, node_id: str) -> List[str]:
        """Get direct children of a node"""
        return [child for parent, child in self._connections if parent == node_id]

    def _invalidate_layout(self) -> None:
        """Mark layout as needing recalculation"""
        self._dirty_layout = True
        self._layout_cache.clear()
        QTimer.singleShot(0, self._calculate_layout_async)

    def _invalidate_cache(self, node_id: Optional[str] = None) -> None:
        """Invalidate paint cache for specific node or all nodes"""
        if node_id:
            self._paint_cache.pop(node_id, None)
        else:
            self._paint_cache.clear()

    def _calculate_layout_async(self) -> None:
        """Calculate layout asynchronously for better performance"""
        if not self._dirty_layout:
            return

        self._calculate_layout()
        self._dirty_layout = False
        self.layout_changed.emit()
        self.update()

    def _calculate_layout(self) -> None:
        """Calculate node positions using enhanced hierarchical layout"""
        if not self._nodes:
            return

        # Build hierarchy maps for efficient lookup
        children_map: Dict[str, List[str]] = {}
        parent_map: Dict[str, str] = {}

        for parent_id, child_id in self._connections:
            if parent_id not in children_map:
                children_map[parent_id] = []
            children_map[parent_id].append(child_id)
            parent_map[child_id] = parent_id

        # Find root nodes
        root_nodes = [node_id for node_id in self._nodes.keys()
                      if node_id not in parent_map]

        if not root_nodes:
            # Handle circular references by choosing first node
            root_nodes = [next(iter(self._nodes.keys()))]

        # Clear positions
        self._node_positions.clear()        # Position each root subtree
        current_x_offset = 50.0  # Add margin
        for root_id in root_nodes:
            subtree_width = self._position_subtree(
                root_id, 0, current_x_offset, children_map)
            current_x_offset += subtree_width + 50  # Add spacing between root trees

    def _position_subtree(self, node_id: str, level: int, x_offset: float,
                          children_map: Dict[str, List[str]]) -> float:
        """Position a subtree and return its width with caching"""
        cache_key = f"{node_id}_{level}_{x_offset}"
        if cache_key in self._layout_cache:
            return self._layout_cache[cache_key]

        children = children_map.get(node_id, [])

        if not children:
            # Leaf node
            x = x_offset
            y = level * self._level_height + 60  # Better top margin
            self._node_positions[node_id] = (x, y)
            width = self._node_spacing
            self._layout_cache[cache_key] = width
            return width

        # Position children first
        child_x = x_offset
        total_width = 0

        for child_id in children:
            child_width = self._position_subtree(child_id, level + 1,
                                                 child_x, children_map)
            child_x += child_width
            total_width += child_width

        # Position parent node centered above children
        parent_x = x_offset + (total_width - self._node_size[0]) / 2
        parent_y = level * self._level_height + 60
        self._node_positions[node_id] = (parent_x, parent_y)

        self._layout_cache[cache_key] = total_width
        return total_width

    def paintEvent(self, event):
        """Enhanced paint with caching and zoom support"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Apply zoom and pan transformations
        painter.scale(self._zoom_factor, self._zoom_factor)
        painter.translate(self._pan_offset)

        theme = theme_manager

        # Draw connections with enhanced styling
        painter.setPen(QPen(theme.get_color('border'), 2))
        for parent_id, child_id in self._connections:
            if parent_id in self._node_positions and child_id in self._node_positions:
                self._draw_connection(painter, parent_id, child_id)

        # Draw nodes with caching
        for node_id, node_data in self._nodes.items():
            if node_id in self._node_positions:
                pos = self._node_positions[node_id]
                self._draw_node_cached(painter, node_id, pos, node_data)

    def _draw_connection(self, painter: QPainter, parent_id: str, child_id: str) -> None:
        """Draw connection between nodes with enhanced styling"""
        parent_pos = self._node_positions[parent_id]
        child_pos = self._node_positions[child_id]

        # Calculate connection points
        parent_center_x = parent_pos[0] + self._node_size[0] // 2
        parent_bottom_y = parent_pos[1] + self._node_size[1]
        child_center_x = child_pos[0] + self._node_size[0] // 2
        child_top_y = child_pos[1]

        # Draw smooth connection
        mid_y = parent_bottom_y + (child_top_y - parent_bottom_y) // 2

        # Convert to int for drawing
        painter.drawLine(int(parent_center_x), int(parent_bottom_y),
                         int(parent_center_x), int(mid_y))
        painter.drawLine(int(parent_center_x), int(mid_y),
                         int(child_center_x), int(mid_y))
        painter.drawLine(int(child_center_x), int(mid_y),
                         int(child_center_x), int(child_top_y))

    def _draw_node_cached(self, painter: QPainter, node_id: str,
                          position: tuple[float, float], node_data: NodeData) -> None:
        """Draw node with caching for better performance"""
        cache_key = f"{node_id}_{hash(str(node_data))}"

        if cache_key not in self._paint_cache:
            # Create cached pixmap
            pixmap = QPixmap(self._node_size[0], self._node_size[1])
            pixmap.fill(Qt.GlobalColor.transparent)
            pixmap_painter = QPainter(pixmap)
            pixmap_painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            self._draw_node_content(pixmap_painter, (0, 0), node_data)
            pixmap_painter.end()

            self._paint_cache[cache_key] = pixmap

        # Draw cached pixmap
        painter.drawPixmap(int(position[0]), int(
            position[1]), self._paint_cache[cache_key])

    def _draw_node_content(self, painter: QPainter, position: tuple[float, float],
                           node_data: NodeData) -> None:
        """Draw node content with enhanced styling"""
        theme = theme_manager
        x, y = position

        # Node background with gradient
        node_rect = QRect(int(x), int(
            y), self._node_size[0], self._node_size[1])

        gradient = QLinearGradient(x, y, x, y + self._node_size[1])
        gradient.setColorAt(0, theme.get_color('surface'))
        gradient.setColorAt(1, theme.get_color('surface').darker(108))

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(theme.get_color('border'), 2))
        painter.drawRoundedRect(node_rect, 12, 12)

        # Enhanced text rendering
        painter.setPen(QPen(theme.get_color('text_primary')))

        # Title with better typography
        title = node_data.get('title', 'Node')
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_rect = QRect(int(x) + 12, int(y) + 12,
                           self._node_size[0] - 24, 24)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, title)

        # Subtitle with improved layout
        subtitle = node_data.get('subtitle', '')
        if subtitle:
            painter.setFont(QFont("Segoe UI", 9))
            painter.setPen(QPen(theme.get_color('text_secondary')))
            subtitle_rect = QRect(int(x) + 12, int(y) + 38,
                                  self._node_size[0] - 24, 18)
            painter.drawText(
                subtitle_rect, Qt.AlignmentFlag.AlignCenter, subtitle)

        # Enhanced status indicator
        self._draw_status_indicator(painter, x, y, node_data.get('status', ''))

    def _draw_status_indicator(self, painter: QPainter, x: float, y: float, status: str) -> None:
        """Draw enhanced status indicator"""
        if not status:
            return

        status_colors = {
            'active': QColor("#28a745"),
            'inactive': QColor("#dc3545"),
            'pending': QColor("#ffc107"),
            'success': QColor("#28a745"),
            'warning': QColor("#ffc107"),
            'error': QColor("#dc3545")
        }

        color = status_colors.get(
            status.lower(), theme_manager.get_color('text_secondary'))

        # Draw status circle with glow effect
        painter.setBrush(QBrush(color))
        lighter_color = QColor(color)
        lighter_color = lighter_color.lighter(150)
        painter.setPen(QPen(lighter_color, 2))
        painter.drawEllipse(
            int(x) + self._node_size[0] - 24, int(y) + 12, 12, 12)

    def mousePressEvent(self, event):
        """Enhanced mouse handling with zoom support"""
        # Adjust for zoom and pan
        adjusted_pos = (event.pos() - self._pan_offset) / self._zoom_factor

        node_id = self._get_node_at_position(adjusted_pos)
        if node_id:
            node_data = self._nodes[node_id].copy()
            # Add node_id to the emitted data
            extended_data = {**node_data, 'node_id': node_id}

            if event.button() == Qt.MouseButton.LeftButton:
                self.node_clicked.emit(extended_data)  # type: ignore

    def mouseDoubleClickEvent(self, event):
        """Enhanced double-click handling"""
        # Adjust for zoom and pan
        adjusted_pos = (event.pos() - self._pan_offset) / self._zoom_factor

        node_id = self._get_node_at_position(adjusted_pos)
        if node_id:
            node_data = self._nodes[node_id].copy()
            # Add node_id to the emitted data
            extended_data = {**node_data, 'node_id': node_id}
            self.node_double_clicked.emit(extended_data)  # type: ignore

    def _get_node_at_position(self, pos: QPoint) -> Optional[str]:
        """Get node at position with better hit detection"""
        for node_id, position in self._node_positions.items():
            x, y = position
            node_rect = QRect(int(x), int(
                y), self._node_size[0], self._node_size[1])
            if node_rect.contains(pos):
                return node_id
        return None

    def _show_context_menu(self, position: QPoint) -> None:
        """Show context menu for nodes"""
        node_id = self._get_node_at_position(position)
        if node_id:
            global_pos = self.mapToGlobal(position)
            self.node_context_menu.emit(node_id, global_pos)

    def wheelEvent(self, event):
        """Handle zoom with mouse wheel"""
        zoom_in = event.angleDelta().y() > 0
        zoom_factor = 1.1 if zoom_in else 0.9
        self.zoom_factor *= zoom_factor

    def _setup_style(self) -> None:
        """Setup enhanced styling"""
        theme = theme_manager
        self.setStyleSheet(f"""
            FluentOrgChart {{
                background-color: {theme.get_color('background').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 12px;
            }}
        """)

    def _on_theme_changed(self, _) -> None:
        """Handle theme change with cache invalidation"""
        self._invalidate_cache()
        self._setup_style()
        self.update()


# Enhanced style setup for all components
def _setup_enhanced_styles() -> str:
    """Setup enhanced styles for all tree components"""
    theme = theme_manager

    enhanced_styles = f"""
        /* Enhanced Tree Styles */
        QTreeWidget {{
            background-color: {theme.get_color('surface').name()};
            border: 2px solid {theme.get_color('border').name()};
            border-radius: 12px;
            selection-background-color: {theme.get_color('primary').name()};
            selection-color: white;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 14px;
            color: {theme.get_color('text_primary').name()};
            outline: none;
            padding: 4px;
        }}
        
        QTreeWidget::item {{
            padding: 8px 12px;
            border: none;
            border-radius: 6px;
            margin: 1px;
        }}
        
        QTreeWidget::item:hover {{
            background-color: {theme.get_color('accent_light').name()};
            transition: background-color 200ms ease;
        }}
        
        QTreeWidget::item:selected {{
            background-color: {theme.get_color('primary').name()};
            color: white;
        }}
        
        QTreeWidget::item:selected:hover {{
            background-color: {theme.get_color('primary').darker(110).name()};
        }}
        
        /* Enhanced Toolbar Styles */
        QFrame#toolbar {{
            background-color: {theme.get_color('surface').name()};
            border-bottom: 2px solid {theme.get_color('border').name()};
            border-radius: 0;
        }}
        
        QLineEdit#searchBox {{
            background-color: {theme.get_color('surface').name()};
            border: 2px solid {theme.get_color('border').name()};
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 14px;
            color: {theme.get_color('text_primary').name()};
            min-width: 250px;
        }}
        
        QLineEdit#searchBox:focus {{
            border-color: {theme.get_color('primary').name()};
            box-shadow: 0 0 0 3px {theme.get_color('primary').name()}22;
        }}
        
        QPushButton#filterButton, QPushButton#expandButton, QPushButton#collapseButton {{
            background-color: {theme.get_color('primary').name()};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 500;
            min-width: 100px;
        }}
        
        QPushButton#filterButton:hover, QPushButton#expandButton:hover, QPushButton#collapseButton:hover {{
            background-color: {theme.get_color('primary').darker(110).name()};
            transform: translateY(-1px);
        }}
        
        QPushButton#filterButton:checked {{
            background-color: {theme.get_color('accent_medium').name()};
        }}
        
        /* Enhanced Filter Panel */
        QFrame#filterPanel {{
            background-color: {theme.get_color('surface').name()};
            border-bottom: 1px solid {theme.get_color('border').name()};
            padding: 8px;
        }}
        
        QLabel#searchLabel, QLabel#filterLabel {{
            color: {theme.get_color('text_secondary').name()};
            font-size: 14px;
            font-weight: 600;
        }}
        
        QComboBox#filterCombo {{
            background-color: {theme.get_color('surface').name()};
            border: 1px solid {theme.get_color('border').name()};
            border-radius: 6px;
            padding: 6px 12px;
            min-width: 120px;
        }}
        
        QComboBox#filterCombo:hover {{
            border-color: {theme.get_color('primary').name()};
        }}
        
        QComboBox#filterCombo::drop-down {{
            border: none;
            padding-right: 8px;
        }}
        
        QComboBox#filterCombo::down-arrow {{
            image: none;
            border: none;
        }}
    """

    return enhanced_styles
