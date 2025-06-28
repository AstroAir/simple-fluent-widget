"""
Fluent Design Style Table and List Components - Fully Optimized

Modern table, list, and data grid components with enhanced features.
Optimized for Python 3.11+ with:
- Union type syntax (|) 
- Dataclasses and protocols
- Enhanced pattern matching
- Type safety improvements
- Performance optimizations
- Better error handling
- Modern component integration
"""

from __future__ import annotations

import time
import weakref
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import lru_cache, cached_property
from contextlib import contextmanager
from typing import (Optional, List, Dict, Callable, Union, Protocol, 
                    TypeAlias, Final, Any, final)

from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
                               QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout,
                               QHBoxLayout, QAbstractItemView, QHeaderView)
from PySide6.QtCore import Qt, Signal, Slot, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QColor

# Enhanced error handling for dependencies
try:
    from core.theme import theme_manager
    THEME_AVAILABLE = True
except ImportError:
    theme_manager = None
    THEME_AVAILABLE = False

try:
    from core.enhanced_animations import (FluentMicroInteraction, FluentTransition,
                                          FluentStateTransition, FluentRevealEffect)
    ANIMATIONS_AVAILABLE = True
except ImportError:
    # Create null objects for missing animation classes
    class AnimationProxy:
        def __getattr__(self, name: str) -> Callable[..., None]:
            return lambda *args, **kwargs: None
    
    ANIMATIONS_AVAILABLE = False
    FluentMicroInteraction = AnimationProxy()
    FluentTransition = AnimationProxy()
    FluentStateTransition = AnimationProxy()
    FluentRevealEffect = AnimationProxy()

try:
    from components.basic.forms.button import FluentButton
    from components.basic.forms.textbox import FluentLineEdit
    FLUENT_COMPONENTS_AVAILABLE = True
except ImportError:
    from PySide6.QtWidgets import QPushButton as FluentButton
    from PySide6.QtWidgets import QLineEdit as FluentLineEdit
    FLUENT_COMPONENTS_AVAILABLE = False


# Modern type aliases for better readability
TableData: TypeAlias = list[list[str]]
HeaderData: TypeAlias = list[str]
ItemData: TypeAlias = Any
TableCallback: TypeAlias = Callable[[int], None]
FilterFunction: TypeAlias = Callable[[str, str], bool]


# Modern enums for better type safety
class TableStyle(Enum):
    """Table component styles"""
    STANDARD = auto()
    COMPACT = auto()
    COMFORTABLE = auto()


class SelectionMode(Enum):
    """Selection mode enumeration"""
    SINGLE = auto()
    MULTIPLE = auto()
    EXTENDED = auto()
    NONE = auto()


class SortOrder(Enum):
    """Sort order enumeration"""
    ASCENDING = auto()
    DESCENDING = auto()
    NONE = auto()


# Configuration dataclasses with slots for memory efficiency
@dataclass(slots=True, frozen=True)
class TableConfig:
    """Immutable configuration for table components"""
    show_grid: bool = True
    alternating_rows: bool = True
    selection_mode: SelectionMode = SelectionMode.SINGLE
    sort_enabled: bool = True
    filter_enabled: bool = True
    animation_duration: int = 200
    row_height: int = 35
    header_height: int = 40


@dataclass(slots=True, frozen=True)
class ListConfig:
    """Immutable configuration for list components"""
    selection_mode: SelectionMode = SelectionMode.SINGLE
    spacing: int = 2
    item_padding: int = 12
    item_margin: int = 2
    border_radius: int = 8
    animation_duration: int = 150
    enable_hover_effects: bool = True
    enable_selection_animation: bool = True


@dataclass(slots=True, frozen=True)
class TreeConfig:
    """Configuration for FluentTreeWidget"""
    item_padding: int = 6
    item_margin: int = 1
    indentation: int = 20
    border_radius: int = 8
    animation_duration: int = 200
    enable_animations: bool = True
    show_root_decoration: bool = True


@dataclass(slots=True, frozen=True)
class DataGridConfig:
    """Configuration for FluentDataGrid"""
    toolbar_spacing: int = 8
    toolbar_margins: tuple[int, int, int, int] = (8, 8, 8, 8)
    search_box_width: int = 300
    enable_search: bool = True
    enable_sort: bool = True
    enable_filter: bool = True


@dataclass(slots=True)
class TableState:
    """Mutable state container for table operations"""
    current_sort_column: int = -1
    sort_order: SortOrder = SortOrder.NONE
    filter_text: str = ""
    selected_rows: list[int] = field(default_factory=list)
    last_update_time: float = field(default_factory=time.time)


# Additional state containers for enhanced functionality  
@dataclass(slots=True)
class ListState:
    """State container for FluentListWidget"""
    selected_items: list[int] = field(default_factory=list)
    hover_item: int = -1
    is_focused: bool = False
    animation_running: bool = False
    last_update: float = field(default_factory=time.time)


@dataclass(slots=True)
class TreeState:
    """State container for FluentTreeWidget"""
    expanded_items: set[str] = field(default_factory=set)
    selected_items: list[str] = field(default_factory=list)
    hover_item: str = ""
    is_focused: bool = False
    last_update: float = field(default_factory=time.time)


@dataclass(slots=True)
class DataGridState:
    """State container for FluentDataGrid"""
    current_filter: str = ""
    sort_column: int = -1
    sort_order: Qt.SortOrder = Qt.SortOrder.AscendingOrder
    selected_rows: list[int] = field(default_factory=list)
    is_editing: bool = False
    last_update: float = field(default_factory=time.time)


# Protocols for theme and behavior management
class TableTheme(Protocol):
    """Protocol for theme management in table components"""
    
    def get_color(self, color_name: str) -> QColor:
        """Get theme color by name"""
        ...
        
    @property
    def theme_changed(self) -> Signal:
        """Signal emitted when theme changes"""
        ...


# Performance optimization utilities
class TableStyleCache:
    """Cache manager for computed table styles"""
    
    _cache: dict[str, str] = {}
    
    @classmethod
    @lru_cache(maxsize=32)
    def get_table_style(cls, component_type: str, theme_name: str) -> str:
        """Get cached table style with LRU caching"""
        cache_key = f"{component_type}_{theme_name}"
        return cls._cache.get(cache_key, "")
    
    @classmethod
    def set_style(cls, cache_key: str, style: str) -> None:
        """Set cached style"""
        cls._cache[cache_key] = style
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached styles"""
        cls._cache.clear()


# Context managers for enhanced operations
@contextmanager
def ListUpdateContext(list_widget: QListWidget):
    """Context manager for bulk list updates"""
    list_widget.setUpdatesEnabled(False)
    try:
        yield list_widget
    finally:
        list_widget.setUpdatesEnabled(True)


@contextmanager
def TreeUpdateContext(tree_widget: QTreeWidget):
    """Context manager for bulk tree updates"""
    tree_widget.setUpdatesEnabled(False)
    try:
        yield tree_widget
    finally:
        tree_widget.setUpdatesEnabled(True)


@contextmanager
def batch_table_updates(*tables: QWidget):
    """Context manager for batching table updates"""
    for table in tables:
        if table:
            table.setUpdatesEnabled(False)
    try:
        yield
    finally:
        for table in tables:
            if table:
                table.setUpdatesEnabled(True)


# Safe theme access utility
def get_theme_color(color_name: str, fallback: str = "#000000") -> str:
    """Safely get theme color with fallback"""
    if THEME_AVAILABLE and theme_manager:
        try:
            return theme_manager.get_color(color_name).name()
        except (AttributeError, KeyError):
            pass
    return fallback



@final
class FluentTableWidget(QTableWidget):
    """Fluent Design Style Table - Fully Optimized

    Modern table widget with enhanced features:
    - Enhanced animations and transitions
    - Configurable behavior and styling
    - Performance optimizations with caching
    - Safe theme integration
    - Type-safe data operations
    """

    # Modern signals with type hints
    rowSelectionChanged = Signal(int)
    tableDataChanged = Signal()  # Renamed to avoid conflict

    def __init__(self, rows: int = 0, columns: int = 0, 
                 parent: Optional[QWidget] = None,
                 config: Optional[TableConfig] = None):
        super().__init__(rows, columns, parent)

        # Configuration and state
        self._config = config or TableConfig()
        self._state = TableState()
        self._is_hovered = False

        # Setup components
        self._setup_enhanced_animations()
        self._setup_style()
        self._setup_behavior()
        self._setup_connections()

        # Add reveal animation when created
        if ANIMATIONS_AVAILABLE:
            try:
                FluentRevealEffect.reveal_fade(self, self._config.animation_duration)
            except (AttributeError, TypeError):
                pass

    def _setup_enhanced_animations(self) -> None:
        """Setup enhanced animation effects"""
        if ANIMATIONS_AVAILABLE:
            try:
                # Skip animations for now due to proxy issues
                self._state_transition = None
            except (AttributeError, TypeError):
                pass

    def _setup_style(self) -> None:
        """Setup style with safe theme access and caching"""
        style_sheet = f"""
            QTableWidget {{
                background-color: {get_theme_color('surface', '#FFFFFF')};
                border: 1px solid {get_theme_color('border', '#D1D1D1')};
                border-radius: 8px;
                gridline-color: {get_theme_color('border', '#D1D1D1')};
                selection-background-color: {get_theme_color('accent_light', '#F5F5F5')};
                selection-color: {get_theme_color('text_primary', '#000000')};
                font-size: 14px;
                color: {get_theme_color('text_primary', '#000000')};
            }}
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {get_theme_color('primary', '#0078D4')}40;
                color: {get_theme_color('text_primary', '#000000')};
            }}
            QTableWidget::item:hover {{
                background-color: {get_theme_color('accent_light', '#F5F5F5')};
            }}
            QHeaderView::section {{
                background-color: {get_theme_color('surface', '#FFFFFF')};
                border: none;
                border-bottom: 2px solid {get_theme_color('primary', '#0078D4')};
                border-right: 1px solid {get_theme_color('border', '#D1D1D1')};
                padding: 8px;
                font-weight: 600;
                color: {get_theme_color('text_primary', '#000000')};
            }}
            QHeaderView::section:hover {{
                background-color: {get_theme_color('accent_light', '#F5F5F5')};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {get_theme_color('background', '#F8F8F8')};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {get_theme_color('border', '#D1D1D1')};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {get_theme_color('text_secondary', '#666666')};
            }}
        """
        
        self.setStyleSheet(style_sheet)
        
        # Cache the style for performance
        TableStyleCache.set_style(
            f"FluentTableWidget_{get_theme_color('primary')}", 
            style_sheet
        )

    def _setup_behavior(self) -> None:
        """Setup behavior with configuration"""
        self.setAlternatingRowColors(self._config.alternating_rows)
        
        # Map enum to Qt values
        selection_mode_map = {
            SelectionMode.SINGLE: QAbstractItemView.SelectionMode.SingleSelection,
            SelectionMode.MULTIPLE: QAbstractItemView.SelectionMode.MultiSelection,
            SelectionMode.EXTENDED: QAbstractItemView.SelectionMode.ExtendedSelection,
            SelectionMode.NONE: QAbstractItemView.SelectionMode.NoSelection,
        }
        
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(selection_mode_map[self._config.selection_mode])
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(self._config.show_grid)
        
        # Set heights from config
        self.verticalHeader().setDefaultSectionSize(self._config.row_height)
        self.horizontalHeader().setDefaultSectionSize(self._config.header_height)

    def _setup_connections(self) -> None:
        """Setup signal connections safely"""
        self.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Connect theme changes safely
        if THEME_AVAILABLE and theme_manager and hasattr(theme_manager, 'theme_changed'):
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_selection_changed(self) -> None:
        """Handle selection changes"""
        selected_rows = list(set(item.row() for item in self.selectedItems()))
        self._state.selected_rows = selected_rows
        self._state.last_update_time = time.time()
        
        if selected_rows:
            self.rowSelectionChanged.emit(selected_rows[0])

    def add_data_row(self, data: list[str]) -> None:
        """Add data row with type safety"""
        row = self.rowCount()
        self.insertRow(row)

        with batch_table_updates(self):
            for col, text in enumerate(data):
                if col < self.columnCount():
                    item = QTableWidgetItem(str(text))
                    self.setItem(row, col, item)
        
        self.tableDataChanged.emit()

    def add_data_rows(self, data: TableData) -> None:
        """Add multiple data rows efficiently"""
        if not data:
            return
            
        start_row = self.rowCount()
        self.setRowCount(start_row + len(data))
        
        with batch_table_updates(self):
            for row_idx, row_data in enumerate(data):
                actual_row = start_row + row_idx
                for col, text in enumerate(row_data):
                    if col < self.columnCount():
                        item = QTableWidgetItem(str(text))
                        self.setItem(actual_row, col, item)
        
        self.tableDataChanged.emit()

    def set_headers(self, headers: HeaderData) -> None:
        """Set headers with type safety"""
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    def clear_data(self) -> None:
        """Clear data efficiently"""
        with batch_table_updates(self):
            self.setRowCount(0)
        self._state.selected_rows.clear()
        self.tableDataChanged.emit()

    def get_row_data(self, row: int) -> list[str]:
        """Get data from specific row"""
        if row < 0 or row >= self.rowCount():
            return []
        
        data = []
        for col in range(self.columnCount()):
            item = self.item(row, col)
            data.append(item.text() if item else "")
        return data

    def get_selected_row_data(self) -> list[list[str]]:
        """Get data from selected rows"""
        return [self.get_row_data(row) for row in self._state.selected_rows]

    def sort_by_column(self, column: int, order: SortOrder = SortOrder.ASCENDING) -> None:
        """Sort table by column with enum support"""
        if column < 0 or column >= self.columnCount():
            return
            
        qt_order = Qt.SortOrder.AscendingOrder if order == SortOrder.ASCENDING else Qt.SortOrder.DescendingOrder
        self.sortByColumn(column, qt_order)
        
        self._state.current_sort_column = column
        self._state.sort_order = order

    @cached_property
    def current_state(self) -> TableState:
        """Get current table state (cached property)"""
        return self._state

    def _on_theme_changed(self, theme_name: str = "") -> None:
        """Theme change handler with cache clearing"""
        TableStyleCache.clear_cache()
        self._setup_style()


class FluentListWidget(QListWidget):
    """**Fluent Design Style List Widget**
    
    Modern, type-safe list widget with enhanced configuration and state management.
    Uses Python 3.11+ features for optimal performance and maintainability.
    """
    
    # Type-safe signals
    item_activated = Signal(int)  # Emits item index
    selection_changed = Signal(list)  # Emits list of selected indices
    
    def __init__(self, 
                 parent: Optional[QWidget] = None,
                 config: Optional[ListConfig] = None):
        super().__init__(parent)
        
        # Configuration and state
        self._config = config or ListConfig()
        self._state = ListState()
        
        self._setup_widget()
        self._setup_style()
        self._setup_behavior()
        self._setup_connections()

    @final
    def _setup_widget(self) -> None:
        """Initialize widget properties"""
        # Selection configuration
        selection_mode_map = {
            SelectionMode.SINGLE: QAbstractItemView.SelectionMode.SingleSelection,
            SelectionMode.MULTIPLE: QAbstractItemView.SelectionMode.MultiSelection,
            SelectionMode.EXTENDED: QAbstractItemView.SelectionMode.ExtendedSelection,
            SelectionMode.NONE: QAbstractItemView.SelectionMode.NoSelection,
        }
        self.setSelectionMode(selection_mode_map[self._config.selection_mode])
        
        # Visual configuration
        self.setSpacing(self._config.spacing)
        self.setAlternatingRowColors(False)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    @final
    def _setup_style(self) -> None:
        """Setup style with safe theme access and caching"""
        style_sheet = f"""
            QListWidget {{
                background-color: {get_theme_color('surface', '#FFFFFF')};
                border: 1px solid {get_theme_color('border', '#D1D1D1')};
                border-radius: {self._config.border_radius}px;
                font-size: 14px;
                color: {get_theme_color('text_primary', '#000000')};
                outline: none;
                selection-background-color: transparent;
            }}
            QListWidget::item {{
                padding: {self._config.item_padding}px;
                border: none;
                border-radius: 4px;
                margin: {self._config.item_margin}px;
                background-color: transparent;
            }}
            QListWidget::item:selected {{
                background-color: {get_theme_color('primary', '#0078D4')};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {get_theme_color('accent_light', '#F5F5F5')};
            }}
            QListWidget::item:selected:hover {{
                background-color: {get_theme_color('primary_dark', '#106EBE')};
            }}
        """
        self.setStyleSheet(style_sheet)

    @final
    def _setup_behavior(self) -> None:
        """Setup widget behavior"""
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Enable smooth scrolling
        self.verticalScrollBar().setSingleStep(1)

    @final
    def _setup_connections(self) -> None:
        """Setup signal connections"""
        # Safe theme manager connection
        if THEME_AVAILABLE and theme_manager and hasattr(theme_manager, 'theme_changed'):
            theme_manager.theme_changed.connect(self._on_theme_changed)
            
        # Internal signal connections
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemClicked.connect(self._on_item_clicked)

    def add_item_with_icon(self, text: str, icon: Optional[QIcon] = None, data: Any = None) -> QListWidgetItem:
        """**Add item with icon and optional data**"""
        item = QListWidgetItem(text)
        if icon:
            item.setIcon(icon)
        if data:
            item.setData(Qt.ItemDataRole.UserRole, data)

        self.addItem(item)
        return item
        
    @Slot()
    def _on_selection_changed(self) -> None:
        """Handle selection changes"""
        selected_items = [self.row(item) for item in self.selectedItems()]
        self._state.selected_items = selected_items
        self._state.last_update = time.time()
        self.selection_changed.emit(selected_items)
        
    @Slot()
    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle item clicks"""
        if item:
            index = self.row(item)
            self.item_activated.emit(index)
    
    # Public API with type safety
    @cached_property
    def config(self) -> ListConfig:
        """Get widget configuration (immutable)"""
        return self._config
        
    @cached_property 
    def current_state(self) -> ListState:
        """Get current widget state"""
        return self._state
        
    def add_items(self, items: list[str]) -> None:
        """Add multiple items efficiently"""
        with ListUpdateContext(self):
            for item_text in items:
                self.addItem(item_text)
                
    def get_selected_text_items(self) -> list[str]:
        """Get text of all selected items"""
        return [item.text() for item in self.selectedItems()]

    @Slot()
    def _on_theme_changed(self, theme_name: str = "") -> None:
        """Theme change handler with cache clearing"""
        # Suppress unused parameter warning
        _ = theme_name
        TableStyleCache.clear_cache()
        self._setup_style()


class FluentTreeWidget(QTreeWidget):
    """**Fluent Design Style Tree Widget**
    
    Modern, type-safe tree widget with enhanced configuration and state management.
    Features hierarchical data display with smooth animations and modern styling.
    """
    
    # Type-safe signals
    item_expanded_changed = Signal(str, bool)  # item path, is_expanded
    item_selection_changed = Signal(list)  # list of selected item paths
    
    def __init__(self, 
                 parent: Optional[QWidget] = None,
                 config: Optional[TreeConfig] = None):
        super().__init__(parent)
        
        # Configuration and state
        self._config = config or TreeConfig()
        self._state = TreeState()
        
        self._setup_widget()
        self._setup_style()
        self._setup_behavior()
        self._setup_connections()

    @final
    def _setup_widget(self) -> None:
        """Initialize widget properties"""
        # Tree configuration
        self.setIndentation(self._config.indentation)
        self.setRootIsDecorated(self._config.show_root_decoration)
        
        # Animation settings
        if self._config.enable_animations:
            self.setAnimated(True)
        
        # Header settings
        self.header().setVisible(False)

    @final
    def _setup_style(self) -> None:
        """Setup style with safe theme access and configuration"""
        style_sheet = f"""
            QTreeWidget {{
                background-color: {get_theme_color('surface', '#FFFFFF')};
                border: 1px solid {get_theme_color('border', '#D1D1D1')};
                border-radius: {self._config.border_radius}px;
                font-size: 14px;
                color: {get_theme_color('text_primary', '#000000')};
                outline: none;
                selection-background-color: transparent;
            }}
            QTreeWidget::item {{
                padding: {self._config.item_padding}px;
                border: none;
                border-radius: 4px;
                margin: {self._config.item_margin}px;
                background-color: transparent;
            }}
            QTreeWidget::item:selected {{
                background-color: {get_theme_color('primary', '#0078D4')};
                color: white;
            }}
            QTreeWidget::item:hover {{
                background-color: {get_theme_color('accent_light', '#F5F5F5')};
            }}
            QTreeWidget::item:selected:hover {{
                background-color: {get_theme_color('primary_dark', '#106EBE')};
            }}
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                image: url(:/icons/chevron_right.svg);
                background-color: transparent;
            }}
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                image: url(:/icons/chevron_down.svg);
                background-color: transparent;
            }}
        """
        self.setStyleSheet(style_sheet)

    @final
    def _setup_behavior(self) -> None:
        """Setup widget behavior"""
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Enable smooth scrolling
        self.verticalScrollBar().setSingleStep(1)
        
        # Selection behavior
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    @final
    def _setup_connections(self) -> None:
        """Setup signal connections"""
        # Safe theme manager connection
        if THEME_AVAILABLE and theme_manager and hasattr(theme_manager, 'theme_changed'):
            theme_manager.theme_changed.connect(self._on_theme_changed)
            
        # Internal signal connections
        self.itemExpanded.connect(self._on_item_expanded)
        self.itemCollapsed.connect(self._on_item_collapsed)
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def add_tree_item(self, text: str, parent: Optional[QTreeWidgetItem] = None,
                      icon: Optional[QIcon] = None, data: Any = None) -> QTreeWidgetItem:
        """**Add tree item with enhanced functionality**"""
        item = QTreeWidgetItem([text])

        if icon:
            item.setIcon(0, icon)
        if data:
            item.setData(0, Qt.ItemDataRole.UserRole, data)

        if parent:
            parent.addChild(item)
        else:
            self.addTopLevelItem(item)

        return item
    
    def get_item_path(self, item: QTreeWidgetItem) -> str:
        """Get the full path of an item"""
        path_parts = []
        current = item
        while current:
            path_parts.append(current.text(0))
            current = current.parent()
        return "/".join(reversed(path_parts))
    
    @Slot(QTreeWidgetItem)
    def _on_item_expanded(self, item: QTreeWidgetItem) -> None:
        """Handle item expansion"""
        path = self.get_item_path(item)
        self._state.expanded_items.add(path)
        self._state.last_update = time.time()
        self.item_expanded_changed.emit(path, True)
        
    @Slot(QTreeWidgetItem)
    def _on_item_collapsed(self, item: QTreeWidgetItem) -> None:
        """Handle item collapse"""
        path = self.get_item_path(item)
        self._state.expanded_items.discard(path)
        self._state.last_update = time.time()
        self.item_expanded_changed.emit(path, False)
        
    @Slot()
    def _on_selection_changed(self) -> None:
        """Handle selection changes"""
        selected_paths = [self.get_item_path(item) for item in self.selectedItems()]
        self._state.selected_items = selected_paths
        self._state.last_update = time.time()
        self.item_selection_changed.emit(selected_paths)
    
    # Public API with type safety
    @cached_property
    def config(self) -> TreeConfig:
        """Get widget configuration (immutable)"""
        return self._config
        
    @cached_property 
    def current_state(self) -> TreeState:
        """Get current widget state"""
        return self._state
        
    def expand_all_animated(self) -> None:
        """Expand all items with animation if enabled"""
        if self._config.enable_animations:
            self.expandAll()
        else:
            self.expandAll()
            
    def collapse_all_animated(self) -> None:
        """Collapse all items with animation if enabled"""
        if self._config.enable_animations:
            self.collapseAll()
        else:
            self.collapseAll()

    @Slot()
    def _on_theme_changed(self, theme_name: str = "") -> None:
        """Theme change handler with cache clearing"""
        # Suppress unused parameter warning
        _ = theme_name
        TableStyleCache.clear_cache()
        self._setup_style()


class FluentDataGrid(QWidget):
    """**Advanced Data Grid**
    
    Modern, comprehensive data grid with search, filtering, sorting and CRUD operations.
    Features type-safe configuration, state management, and enhanced user experience.
    """
    
    # Type-safe signals
    data_changed = Signal()
    selection_changed = Signal(list)  # selected row indices
    item_edited = Signal(int, int, str)  # row, column, new_value
    
    def __init__(self, 
                 parent: Optional[QWidget] = None,
                 config: Optional[DataGridConfig] = None):
        super().__init__(parent)

        # Configuration and state
        self._config = config or DataGridConfig()
        self._state = DataGridState()
        
        # Data storage
        self._data: list[list[str]] = []
        self._headers: list[str] = []
        self._filtered_data: list[list[str]] = []

        self._setup_ui()
        self._setup_style()
        self._setup_connections()

    @final
    def _setup_ui(self) -> None:
        """Setup user interface with modern layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self._config.toolbar_spacing)

        # Toolbar setup
        if self._config.enable_search or self._config.enable_sort:
            toolbar = self._create_toolbar()
            layout.addWidget(toolbar)

        # Table setup
        self.table = FluentTableWidget()
        layout.addWidget(self.table)
        
    def _create_toolbar(self) -> QWidget:
        """Create toolbar with search and action buttons"""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        margins = self._config.toolbar_margins
        toolbar_layout.setContentsMargins(*margins)

        if self._config.enable_search:
            # Search box with modern setup
            self.search_box = FluentLineEdit()
            self.search_box.setPlaceholderText("Search...")
            self.search_box.setMaximumWidth(self._config.search_box_width)
            toolbar_layout.addWidget(self.search_box)

        toolbar_layout.addStretch()

        # Action buttons with clean styling
        self.add_btn = FluentButton("Add")
        self.edit_btn = FluentButton("Edit")
        self.delete_btn = FluentButton("Delete")

        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.edit_btn)
        toolbar_layout.addWidget(self.delete_btn)
        
        return toolbar

    @final
    def _setup_connections(self) -> None:
        """Setup signal connections and event handlers"""
        # Safe theme manager connection
        if THEME_AVAILABLE and theme_manager and hasattr(theme_manager, 'theme_changed'):
            theme_manager.theme_changed.connect(self._on_theme_changed)
            
        # Connect search functionality if enabled
        if self._config.enable_search and hasattr(self, 'search_box'):
            self.search_box.textChanged.connect(self._filter_data)
            
        # Connect table signals
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Connect action buttons
        if hasattr(self, 'add_btn'):
            self.add_btn.clicked.connect(self._on_add_clicked)
        if hasattr(self, 'edit_btn'):  
            self.edit_btn.clicked.connect(self._on_edit_clicked)
        if hasattr(self, 'delete_btn'):
            self.delete_btn.clicked.connect(self._on_delete_clicked)

    @final
    def _setup_style(self) -> None:
        """Setup style with safe theme access and modern styling"""
        style_sheet = f"""
            FluentDataGrid {{
                background-color: {get_theme_color('background', '#F5F5F5')};
                border-radius: 8px;
            }}
            QWidget {{
                background-color: {get_theme_color('surface', '#FFFFFF')};
                border: 1px solid {get_theme_color('border', '#D1D1D1')};
                border-radius: 8px;
                padding: 4px;
            }}
            QWidget:hover {{
                border-color: {get_theme_color('primary_light', '#40E0D0')};
            }}
        """
        self.setStyleSheet(style_sheet)

    # Data management methods with type safety
    def set_data(self, headers: list[str], data: list[list[str]]) -> None:
        """**Set grid data with type-safe parameters**"""
        self._headers = headers
        self._data = data
        self._filtered_data = data.copy()
        self._state.last_update = time.time()

        self.table.set_headers(headers)
        self._update_table()
        self.data_changed.emit()

    def add_row(self, row_data: list[str]) -> None:
        """Add a new row to the grid"""
        self._data.append(row_data)
        self._apply_current_filter()
        self._state.last_update = time.time()
        self.data_changed.emit()

    def remove_selected_rows(self) -> bool:
        """Remove selected rows and return success status"""
        selected_rows = self._get_selected_row_indices()
        if not selected_rows:
            return False
            
        # Sort in reverse order to maintain indices
        for row_index in sorted(selected_rows, reverse=True):
            if 0 <= row_index < len(self._data):
                del self._data[row_index]
                
        self._apply_current_filter()
        self._state.last_update = time.time()
        self.data_changed.emit()
        return True

    def get_selected_data(self) -> list[list[str]]:
        """Get data from selected rows"""
        selected_rows = self._get_selected_row_indices()
        return [self._data[i] for i in selected_rows if 0 <= i < len(self._data)]

    @final
    def _update_table(self) -> None:
        """Update table display with current filtered data"""
        self.table.clear_data()
        for row_data in self._filtered_data:
            self.table.add_data_row(row_data)

    @final
    def _apply_current_filter(self) -> None:
        """Apply current filter to update filtered data"""
        if hasattr(self, 'search_box'):
            filter_text = self.search_box.text()
            self._filter_data(filter_text)
        else:
            self._filtered_data = self._data.copy()
            self._update_table()

    @Slot(str)
    def _filter_data(self, text: str) -> None:
        """Filter data based on search text"""
        self._state.current_filter = text
        
        if not text.strip():
            self._filtered_data = self._data.copy()
        else:
            text_lower = text.lower()
            self._filtered_data = [
                row for row in self._data
                if any(text_lower in str(cell).lower() for cell in row)
            ]
        
        self._update_table()
        self._state.last_update = time.time()

    def _get_selected_row_indices(self) -> list[int]:
        """Get indices of selected rows in the original data"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return []
            
        selected_rows = list({item.row() for item in selected_items})
        # Map from filtered data indices to original data indices  
        original_indices = []
        for filtered_index in selected_rows:
            if 0 <= filtered_index < len(self._filtered_data):
                filtered_row = self._filtered_data[filtered_index]
                try:
                    original_index = self._data.index(filtered_row)
                    original_indices.append(original_index)
                except ValueError:
                    continue
                    
        return original_indices

    @Slot()
    def _on_theme_changed(self, theme_name: str = "") -> None:
        """Theme change handler with cache clearing"""
        _ = theme_name  # Suppress unused parameter warning
        TableStyleCache.clear_cache()
        self._setup_style()

    # Signal handlers
    @Slot()
    def _on_selection_changed(self) -> None:
        """Handle table selection changes"""
        selected_indices = self._get_selected_row_indices()
        self._state.selected_rows = selected_indices
        self._state.last_update = time.time()
        self.selection_changed.emit(selected_indices)

    @Slot()
    def _on_add_clicked(self) -> None:
        """Handle add button click"""
        # Placeholder for add functionality
        pass

    @Slot()
    def _on_edit_clicked(self) -> None:
        """Handle edit button click"""
        selected_rows = self._get_selected_row_indices()
        if selected_rows:
            self._state.is_editing = True
            # Placeholder for edit functionality

    @Slot()
    def _on_delete_clicked(self) -> None:
        """Handle delete button click"""
        self.remove_selected_rows()
