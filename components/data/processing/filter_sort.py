"""
Fluent Design Style Data Filtering and Sorting Utilities - Fully Optimized

Modern data filtering and sorting components for list and table views.
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

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QToolButton, QComboBox, QMenu, QApplication)
from PySide6.QtCore import (Qt, Signal, QSortFilterProxyModel, QModelIndex, 
                            QPersistentModelIndex, QTimer)
from PySide6.QtGui import QAction, QStandardItem

# Enhanced error handling for dependencies
try:
    from core.theme import theme_manager
    THEME_AVAILABLE = True
except ImportError:
    theme_manager = None
    THEME_AVAILABLE = False

try:
    from components.basic.forms.button import FluentButton
    from components.basic.forms.textbox import FluentLineEdit
    FLUENT_COMPONENTS_AVAILABLE = True
except ImportError:
    from PySide6.QtWidgets import QPushButton as FluentButton
    from PySide6.QtWidgets import QLineEdit as FluentLineEdit
    FLUENT_COMPONENTS_AVAILABLE = False


# Modern type aliases for better readability
FilterCallback: TypeAlias = Callable[[str, str], None]
SortCallback: TypeAlias = Callable[[str, bool], None]
CustomFilterFunction: TypeAlias = Callable[[QModelIndex, str], bool]
CategoryList: TypeAlias = list[str]
SortFieldDict: TypeAlias = dict[str, str]


# Modern enums for better type safety
class FilterStyle(Enum):
    """Filter component styles"""
    COMPACT = auto()
    EXPANDED = auto()
    MINIMAL = auto()


class SortDirection(Enum):
    """Sort direction enumeration"""
    ASCENDING = auto()
    DESCENDING = auto()


class FilterState(Enum):
    """Filter component states"""
    IDLE = auto()
    FILTERING = auto()
    CLEARING = auto()
    ERROR = auto()


# Configuration dataclasses with slots for memory efficiency
@dataclass(slots=True, frozen=True)
class FilterConfig:
    """Immutable configuration for filter components"""
    placeholder_text: str = "Filter items..."
    enable_categories: bool = True
    enable_clear_button: bool = True
    case_sensitive: bool = False
    debounce_delay: int = 300
    max_history_items: int = 20
    animation_duration: int = 200


@dataclass(slots=True, frozen=True)
class SortConfig:
    """Immutable configuration for sort components"""
    default_field: str = ""
    default_ascending: bool = True
    show_direction_indicators: bool = True
    enable_multi_column_sort: bool = False
    animation_duration: int = 200


@dataclass(slots=True)
class FilterSortState:
    """Mutable state container for filter/sort operations"""
    current_filter: str = ""
    current_category: str = ""
    current_sort_field: str = ""
    sort_ascending: bool = True
    filter_history: list[str] = field(default_factory=list)
    last_update_time: float = field(default_factory=time.time)


# Protocols for theme and behavior management
class FilterSortTheme(Protocol):
    """Protocol for theme management in filter/sort components"""
    
    def get_color(self, color_name: str) -> str:
        """Get theme color by name"""
        ...
        
    @property
    def theme_changed(self) -> Signal:
        """Signal emitted when theme changes"""
        ...


class FilterFunction(Protocol):
    """Protocol for custom filter functions"""
    
    def __call__(self, index: QModelIndex, pattern: str) -> bool:
        """Filter function implementation"""
        ...


# Performance optimization utilities
class StyleCache:
    """Cache manager for computed styles"""
    
    _cache: dict[str, str] = {}
    _cache_keys: weakref.WeakSet = weakref.WeakSet()
    
    @classmethod
    @lru_cache(maxsize=64)
    def get_style(cls, component_type: str, theme_name: str, **kwargs) -> str:
        """Get cached style with LRU caching"""
        cache_key = f"{component_type}_{theme_name}_{hash(frozenset(kwargs.items()))}"
        return cls._cache.get(cache_key, "")
    
    @classmethod
    def set_style(cls, cache_key: str, style: str) -> None:
        """Set cached style"""
        cls._cache[cache_key] = style
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached styles"""
        cls._cache.clear()


@contextmanager
def batch_ui_updates(*widgets: QWidget):
    """Context manager for batching UI updates"""
    for widget in widgets:
        if widget:
            widget.setUpdatesEnabled(False)
    try:
        yield
    finally:
        for widget in widgets:
            if widget:
                widget.setUpdatesEnabled(True)


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
class FluentFilterBar(QWidget):
    """Fluent Design Style Filter Bar - Fully Optimized

    Modern filter bar with enhanced features:
    - Search input with dynamic filtering
    - Filter category selector with type safety
    - Clear filters button with animations
    - Support for custom filter functions
    - Performance optimizations with caching
    - Modern configuration system
    """

    filterChanged = Signal(str, str)  # (filter_text, category)

    def __init__(self, parent: Optional[QWidget] = None,
                 categories: Optional[CategoryList] = None,
                 config: Optional[FilterConfig] = None):
        super().__init__(parent)

        # Configuration with defaults
        self._config = config or FilterConfig()
        self._state = FilterSortState()
        
        # Debounce timer for performance
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_filter_changed)

        # Setup layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

        # Create search input with modern initialization
        self._search_input = self._create_search_input()
        
        # Create category selector if categories provided
        self._category_selector = self._create_category_selector(categories) if categories else None

        # Create clear button with modern styling
        self._clear_button = self._create_clear_button()

        # Setup layout order
        self._setup_layout()
        
        # Setup styling and connections
        self._apply_style()
        self._setup_connections()

    def _create_search_input(self) -> Union[FluentLineEdit, QWidget]:
        """Create search input with proper initialization"""
        # This will be either the real FluentLineEdit or QLineEdit alias
        search_input = FluentLineEdit(self)
        search_input.setPlaceholderText(self._config.placeholder_text)
        search_input.setMinimumWidth(200)
        return search_input

    def _create_category_selector(self, categories: CategoryList) -> QComboBox:
        """Create category selector with modern styling"""
        selector = QComboBox()
        selector.addItem("All")
        selector.addItems(categories)
        selector.setMinimumWidth(100)
        return selector

    def _create_clear_button(self) -> Union[FluentButton, QWidget]:
        """Create clear button with fallback styling"""
        button = FluentButton("Clear")
        button.setMinimumWidth(60)
        
        # Apply Fluent styling if available - safer approach
        if FLUENT_COMPONENTS_AVAILABLE:
            try:
                # Use duck typing instead of hasattr for better safety
                if hasattr(button, 'set_style'):
                    button_style = getattr(FluentButton, 'ButtonStyle', None)
                    if button_style and hasattr(button_style, 'SUBTLE'):
                        button.set_style(button_style.SUBTLE)  # type: ignore
            except (AttributeError, TypeError):
                pass
        
        return button

    def _setup_layout(self) -> None:
        """Setup widget layout"""
        if self._category_selector:
            self._layout.addWidget(self._category_selector)
        
        self._layout.addWidget(self._search_input)
        self._layout.addWidget(self._clear_button)
        self._layout.addStretch()

    def _setup_connections(self) -> None:
        """Setup signal connections"""
        # Use type assertions for method calls
        if hasattr(self._search_input, 'textChanged'):
            self._search_input.textChanged.connect(self._on_text_changed)  # type: ignore
        
        if hasattr(self._clear_button, 'clicked'):
            self._clear_button.clicked.connect(self.clear_filters)  # type: ignore
        
        if self._category_selector:
            self._category_selector.currentTextChanged.connect(self._on_category_changed)
        
        # Connect theme changes safely
        if THEME_AVAILABLE and theme_manager and hasattr(theme_manager, 'theme_changed'):
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_combobox_style(self, combobox: QComboBox) -> None:
        """Setup ComboBox styling with safe theme access"""
        style_sheet = f"""
            QComboBox {{
                background-color: {get_theme_color('surface', '#FFFFFF')};
                color: {get_theme_color('text_primary', '#000000')};
                border: 1px solid {get_theme_color('border', '#D1D1D1')};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 14px;
                min-height: 32px;
            }}
            
            QComboBox:hover {{
                border-color: {get_theme_color('primary', '#0078D4')};
            }}
            
            QComboBox:focus {{
                border: 2px solid {get_theme_color('primary', '#0078D4')};
                padding: 3px 7px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
                subcontrol-position: right center;
                subcontrol-origin: padding;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {get_theme_color('surface', '#FFFFFF')};
                color: {get_theme_color('text_primary', '#000000')};
                border: 1px solid {get_theme_color('border', '#D1D1D1')};
                selection-background-color: {get_theme_color('primary', '#0078D4')}40;
                selection-color: {get_theme_color('text_primary', '#000000')};
                outline: none;
            }}
        """
        combobox.setStyleSheet(style_sheet)

    def _apply_style(self) -> None:
        """Apply styles to the filter bar with caching"""
        if self._category_selector:
            self._setup_combobox_style(self._category_selector)

    def _on_theme_changed(self) -> None:
        """Handle theme changes with cache clearing"""
        StyleCache.clear_cache()
        self._apply_style()

    def _on_text_changed(self, text: str) -> None:
        """Handle text changes with debouncing"""
        self._state.current_filter = text
        
        # Add to history if not empty and not duplicate
        if text and (not self._state.filter_history or text != self._state.filter_history[-1]):
            self._state.filter_history.append(text)
            # Limit history size
            if len(self._state.filter_history) > self._config.max_history_items:
                self._state.filter_history.pop(0)
        
        # Debounce the signal emission
        self._debounce_timer.start(self._config.debounce_delay)

    def _on_category_changed(self, category: str) -> None:
        """Handle category changes"""
        self._state.current_category = "" if category == "All" else category
        self._emit_filter_changed()

    def _emit_filter_changed(self) -> None:
        """Emit filter changed signal"""
        self._state.last_update_time = time.time()
        self.filterChanged.emit(self._state.current_filter, self._state.current_category)

    def clear_filters(self) -> None:
        """Clear all active filters with batch updates"""
        widgets_to_update: list[QWidget] = [self._search_input]  # type: ignore
        if self._category_selector:
            widgets_to_update.append(self._category_selector)
            
        with batch_ui_updates(*widgets_to_update):
            if hasattr(self._search_input, 'clear'):
                self._search_input.clear()  # type: ignore
            if self._category_selector:
                self._category_selector.setCurrentIndex(0)

        self._state.current_filter = ""
        self._state.current_category = ""
        self.filterChanged.emit("", "")

    @cached_property
    def filter_history(self) -> list[str]:
        """Get filter history (cached property)"""
        return self._state.filter_history.copy()

    def get_current_filter(self) -> tuple[str, str]:
        """Get current filter settings with modern tuple annotation"""
        return (self._state.current_filter, self._state.current_category)

    def set_filter_text(self, text: str) -> None:
        """Programmatically set filter text"""
        if hasattr(self._search_input, 'setText'):
            self._search_input.setText(text)  # type: ignore

    def set_category(self, category: str) -> None:
        """Programmatically set category"""
        if self._category_selector:
            index = self._category_selector.findText(category)
            if index >= 0:
                self._category_selector.setCurrentIndex(index)


@final
class FluentSortingMenu(QMenu):
    """Fluent Design Style Sorting Menu - Fully Optimized

    Modern sorting menu with enhanced features:
    - Sort direction (ascending/descending) with visual indicators
    - Multiple sort fields with type safety
    - Performance optimizations and caching
    - Safe theme integration
    """

    sortChanged = Signal(str, bool)  # (field, ascending)

    def __init__(self, parent: Optional[QWidget] = None,
                 fields: Optional[list[dict[str, str]]] = None,
                 config: Optional[SortConfig] = None):
        """
        Initialize sorting menu

        Args:
            parent: Parent widget
            fields: List of dictionaries with 'name' and 'display' keys
                   e.g. [{'name': 'date', 'display': 'Date'}]
            config: Sort configuration
        """
        super().__init__(parent)

        self._config = config or SortConfig()
        self._fields = fields or []
        self._state = FilterSortState()
        self._state.current_sort_field = self._config.default_field
        self._state.sort_ascending = self._config.default_ascending

        self._setup_menu()
        self._apply_style()
        self._setup_connections()

    def _setup_menu(self) -> None:
        """Setup menu items with modern patterns"""
        # Add sort direction submenu
        self.direction_menu = QMenu("Sort Direction", self)

        self.asc_action = QAction("Ascending ↑", self)
        self.asc_action.setCheckable(True)
        self.asc_action.setChecked(self._state.sort_ascending)
        self.asc_action.triggered.connect(lambda: self._on_direction_changed(True))

        self.desc_action = QAction("Descending ↓", self)
        self.desc_action.setCheckable(True)
        self.desc_action.setChecked(not self._state.sort_ascending)
        self.desc_action.triggered.connect(lambda: self._on_direction_changed(False))

        self.direction_menu.addAction(self.asc_action)
        self.direction_menu.addAction(self.desc_action)

        # Add separator
        self.addMenu(self.direction_menu)
        self.addSeparator()

        # Add field actions with proper lambda binding
        self._field_actions: list[QAction] = []
        for field in self._fields:
            action = QAction(field["display"], self)
            action.setCheckable(True)
            action.setData(field["name"])
            # Proper lambda binding to avoid closure issues
            field_name = field["name"]
            action.triggered.connect(lambda checked=False, name=field_name: self._on_field_changed(name))
            self._field_actions.append(action)
            self.addAction(action)

        # Set default selection if fields exist
        if self._fields and self._config.default_field:
            for action in self._field_actions:
                if action.data() == self._config.default_field:
                    action.setChecked(True)
                    break
        elif self._fields:
            self._field_actions[0].setChecked(True)
            self._state.current_sort_field = self._fields[0]["name"]

    def _setup_connections(self) -> None:
        """Setup signal connections safely"""
        if THEME_AVAILABLE and theme_manager and hasattr(theme_manager, 'theme_changed'):
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _apply_style(self) -> None:
        """Apply menu styling with safe theme access"""
        style_sheet = f"""
            QMenu {{
                background-color: {get_theme_color('surface', '#FFFFFF')};
                border: 1px solid {get_theme_color('border', '#D1D1D1')};
                border-radius: 4px;
                padding: 4px 0px;
                font-size: 14px;
            }}
            
            QMenu::item {{
                padding: 6px 32px 6px 20px;
                color: {get_theme_color('text_primary', '#000000')};
            }}
            
            QMenu::item:selected {{
                background-color: {get_theme_color('accent_light', '#F5F5F5')};
            }}
            
            QMenu::indicator {{
                width: 18px;
                height: 18px;
                padding-left: 4px;
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {get_theme_color('border', '#D1D1D1')};
                margin: 4px 0px;
            }}
        """
        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self) -> None:
        """Handle theme changes with cache clearing"""
        StyleCache.clear_cache()
        self._apply_style()

    def _on_direction_changed(self, ascending: bool) -> None:
        """Handle sort direction change with state management"""
        self._state.sort_ascending = ascending
        self._state.last_update_time = time.time()

        # Update checkable actions
        self.asc_action.setChecked(ascending)
        self.desc_action.setChecked(not ascending)

        # Emit signal
        self.sortChanged.emit(self._state.current_sort_field, self._state.sort_ascending)

    def _on_field_changed(self, field: str) -> None:
        """Handle sort field change with proper state management"""
        prev_field = self._state.current_sort_field
        self._state.current_sort_field = field
        self._state.last_update_time = time.time()

        # Update checkable actions
        for action in self._field_actions:
            action.setChecked(action.data() == field)

        # If the field actually changed, emit the signal
        if prev_field != field:
            self.sortChanged.emit(self._state.current_sort_field, self._state.sort_ascending)

    def get_current_sort(self) -> tuple[str, bool]:
        """Get current sort settings with modern tuple annotation"""
        return (self._state.current_sort_field, self._state.sort_ascending)

    def set_sort_field(self, field: str) -> None:
        """Programmatically set sort field"""
        for action in self._field_actions:
            if action.data() == field:
                action.setChecked(True)
                self._state.current_sort_field = field
                break

    def set_sort_direction(self, ascending: bool) -> None:
        """Programmatically set sort direction"""
        self._state.sort_ascending = ascending
        self.asc_action.setChecked(ascending)
        self.desc_action.setChecked(not ascending)


@final
class FluentFilterSortHeader(QWidget):
    """Combined filter and sort header for data views - Fully Optimized

    Modern header component with enhanced features:
    - Integrated filter bar with debouncing
    - Sort button with dropdown menu
    - Responsive layout design
    - Performance optimizations
    - Safe theme integration
    """

    filterChanged = Signal(str, str)  # (filter_text, category)
    sortChanged = Signal(str, bool)  # (field, ascending)

    def __init__(self, parent: Optional[QWidget] = None,
                 filter_categories: Optional[CategoryList] = None,
                 sort_fields: Optional[list[dict[str, str]]] = None,
                 filter_config: Optional[FilterConfig] = None,
                 sort_config: Optional[SortConfig] = None):
        super().__init__(parent)

        # Store configurations
        self._filter_config = filter_config or FilterConfig()
        self._sort_config = sort_config or SortConfig()

        # Setup layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

        # Create components
        self._create_components(filter_categories, sort_fields)
        self._setup_layout()
        self._setup_connections()
        self._apply_style()

    def _create_components(self, filter_categories: Optional[CategoryList], 
                          sort_fields: Optional[list[dict[str, str]]]) -> None:
        """Create child components"""
        # Create filter bar
        self._filter_bar = FluentFilterBar(
            self, 
            categories=filter_categories, 
            config=self._filter_config
        )

        # Create sort button
        self._sort_button = QToolButton(self)
        self._sort_button.setText("Sort")
        self._sort_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        # Create sort menu
        self._sort_menu = FluentSortingMenu(
            self, 
            fields=sort_fields, 
            config=self._sort_config
        )
        self._sort_button.setMenu(self._sort_menu)

    def _setup_layout(self) -> None:
        """Setup widget layout"""
        self._layout.addWidget(self._filter_bar)
        self._layout.addWidget(self._sort_button)

    def _setup_connections(self) -> None:
        """Setup signal connections"""
        self._filter_bar.filterChanged.connect(self._on_filter_changed)
        self._sort_menu.sortChanged.connect(self._on_sort_changed)
        
        # Connect theme changes safely
        if THEME_AVAILABLE and theme_manager and hasattr(theme_manager, 'theme_changed'):
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _apply_style(self) -> None:
        """Apply styling to the header with safe theme access"""
        # Style the sort button
        sort_button_style = f"""
            QToolButton {{
                background-color: {get_theme_color('surface', '#FFFFFF')};
                color: {get_theme_color('text_primary', '#000000')};
                border: 1px solid {get_theme_color('border', '#D1D1D1')};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 14px;
                min-height: 32px;
                min-width: 60px;
            }}
            
            QToolButton:hover {{
                border-color: {get_theme_color('primary', '#0078D4')};
                background-color: {get_theme_color('accent_light', '#F5F5F5')};
            }}
            
            QToolButton::menu-indicator {{
                width: 16px;
                height: 16px;
                subcontrol-position: right center;
                subcontrol-origin: padding;
            }}
        """
        self._sort_button.setStyleSheet(sort_button_style)

    def _on_theme_changed(self) -> None:
        """Handle theme changes with cache clearing"""
        StyleCache.clear_cache()
        self._apply_style()

    def _on_filter_changed(self, text: str, category: str) -> None:
        """Handle filter changes"""
        self.filterChanged.emit(text, category)

    def _on_sort_changed(self, field: str, ascending: bool) -> None:
        """Handle sort changes"""
        self.sortChanged.emit(field, ascending)

    def clear_filters(self) -> None:
        """Clear all active filters"""
        self._filter_bar.clear_filters()

    def get_current_filter(self) -> tuple[str, str]:
        """Get current filter settings"""
        return self._filter_bar.get_current_filter()

    def get_current_sort(self) -> tuple[str, bool]:
        """Get current sort settings"""
        return self._sort_menu.get_current_sort()

    def set_filter_text(self, text: str) -> None:
        """Programmatically set filter text"""
        self._filter_bar.set_filter_text(text)

    def set_sort_field(self, field: str) -> None:
        """Programmatically set sort field"""
        self._sort_menu.set_sort_field(field)

    def set_sort_direction(self, ascending: bool) -> None:
        """Programmatically set sort direction"""
        self._sort_menu.set_sort_direction(ascending)


@final
class FluentFilterProxyModel(QSortFilterProxyModel):
    """Enhanced filter proxy model for Fluent components - Fully Optimized

    Modern proxy model with enhanced features:
    - Multi-column filtering with performance optimization
    - Case insensitive matching with caching
    - Custom filter predicates with type safety
    - Column visibility control
    - Batch update support
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._filter_columns: list[int] = []
        self._filter_function: Optional[CustomFilterFunction] = None
        self._visible_columns: Optional[list[int]] = None
        
        # Performance optimization flags
        self._batch_mode = False
        self._pending_invalidation = False

        # Set default filter settings
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterKeyColumn(-1)  # Filter all columns

    @contextmanager
    def batch_filter_updates(self):
        """Context manager for batch filter updates"""
        self._batch_mode = True
        try:
            yield
        finally:
            self._batch_mode = False
            if self._pending_invalidation:
                self.invalidateFilter()
                self._pending_invalidation = False

    def set_filter_columns(self, columns: list[int]) -> None:
        """Set which columns to consider for filtering"""
        self._filter_columns = columns
        self._invalidate_filter()

    def set_filter_function(self, func: CustomFilterFunction) -> None:
        """Set custom filter function with type safety

        Args:
            func: Function that takes a source model index and filter string,
                  and returns True if item matches the filter
        """
        self._filter_function = func
        self._invalidate_filter()

    def set_visible_columns(self, columns: list[int]) -> None:
        """Set which columns should be visible"""
        self._visible_columns = columns
        self._invalidate_filter()

    def _invalidate_filter(self) -> None:
        """Invalidate filter with batch support"""
        if self._batch_mode:
            self._pending_invalidation = True
        else:
            self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, 
                        source_parent: QModelIndex | QPersistentModelIndex) -> bool:
        """Determine if a row should be included in the filtered result"""
        # Get filter pattern
        pattern = self.filterRegularExpression().pattern()

        # If no filter, accept row
        if not pattern:
            return True

        # Performance optimization: ensure we have a valid QModelIndex
        parent_index = source_parent
        if isinstance(source_parent, QPersistentModelIndex):
            # Convert QPersistentModelIndex to QModelIndex properly
            if source_parent.isValid():
                model = source_parent.model()
                parent_index = model.index(source_parent.row(), source_parent.column(), source_parent.parent()) if model else QModelIndex()
            else:
                parent_index = QModelIndex()

        # Determine columns to check
        if self._filter_columns:
            columns_to_check = self._filter_columns
        else:
            # Check all columns
            columns_to_check = range(self.sourceModel().columnCount(parent_index))

        # Use custom filter function if provided
        if self._filter_function:
            for column in columns_to_check:
                index = self.sourceModel().index(source_row, column, parent_index)
                if self._filter_function(index, pattern):
                    return True
            return False

        # Default filtering: check if any column contains the pattern
        for column in columns_to_check:
            index = self.sourceModel().index(source_row, column, parent_index)
            data = self.sourceModel().data(index)
            if data is not None and pattern.lower() in str(data).lower():
                return True

        return False

    def filterAcceptsColumn(self, source_column: int, 
                           source_parent: QModelIndex | QPersistentModelIndex) -> bool:
        """Determine if a column should be visible"""
        if self._visible_columns is not None:
            return source_column in self._visible_columns
        return super().filterAcceptsColumn(source_column, source_parent)


# Export all components for easy import
__all__ = [
    # Main classes
    'FluentFilterBar',
    'FluentSortingMenu', 
    'FluentFilterSortHeader',
    'FluentFilterProxyModel',
    
    # Configuration classes
    'FilterConfig',
    'SortConfig',
    'FilterSortState',
    
    # Enums
    'FilterStyle',
    'SortDirection', 
    'FilterState',
    
    # Protocols
    'FilterSortTheme',
    'FilterFunction',
    
    # Utilities
    'StyleCache',
    'batch_ui_updates',
    'get_theme_color',
    
    # Type aliases
    'FilterCallback',
    'SortCallback',
    'CustomFilterFunction',
    'CategoryList',
    'SortFieldDict',
]
