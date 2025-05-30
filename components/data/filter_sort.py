"""
Fluent Design Style Data Filtering and Sorting Utilities
Components for filtering, sorting and data manipulation in list and table views
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QToolButton, QComboBox, QMenu)
from PySide6.QtCore import Qt, Signal, QSortFilterProxyModel, QModelIndex, QPersistentModelIndex
from PySide6.QtGui import QAction, QStandardItem
from core.theme import theme_manager
from ..basic.button import FluentButton
from ..basic.textbox import FluentLineEdit
from typing import Optional, List, Dict, Callable, Union


class FluentFilterBar(QWidget):
    """Fluent Design Style Filter Bar

    Features:
    - Search input with dynamic filtering
    - Filter category selector
    - Clear filters button
    - Support for custom filter functions
    """

    filterChanged = Signal(str, str)  # (filter_text, category)

    def __init__(self, parent: Optional[QWidget] = None,
                 categories: Optional[List[str]] = None,
                 placeholder: str = "Filter items..."):
        super().__init__(parent)

        self._current_filter = ""
        self._current_category = ""

        # Setup layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

        # Create search input
        self._search_input = FluentLineEdit(self, placeholder=placeholder)
        self._search_input.textChanged.connect(self._on_filter_changed)
        self._search_input.setMinimumWidth(200)

        # Create category selector if categories provided
        if categories and len(categories) > 0:
            self._category_selector = QComboBox()
            self._category_selector.addItem("All")
            self._category_selector.addItems(categories)
            self._category_selector.currentTextChanged.connect(
                self._on_category_changed)
            self._category_selector.setMinimumWidth(100)
            self._setup_combobox_style(self._category_selector)

            self._layout.addWidget(self._category_selector)
        else:
            self._category_selector = None

        # Add search input
        self._layout.addWidget(self._search_input)

        # Create clear button
        self._clear_button = FluentButton(
            "Clear", style=FluentButton.ButtonStyle.SUBTLE)
        self._clear_button.setMinimumWidth(60)
        self._clear_button.clicked.connect(self.clear_filters)

        self._layout.addWidget(self._clear_button)
        self._layout.addStretch()

        # Setup styling
        self._apply_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_combobox_style(self, combobox: QComboBox):
        """Setup ComboBox styling"""
        theme = theme_manager

        style_sheet = f"""
            QComboBox {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 14px;
                min-height: 32px;
            }}
            
            QComboBox:hover {{
                border-color: {theme.get_color('primary').name()};
            }}
            
            QComboBox:focus {{
                border: 2px solid {theme.get_color('primary').name()};
                padding: 3px 7px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
                subcontrol-position: right center;
                subcontrol-origin: padding;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                selection-background-color: {theme.get_color('primary').name()}40;
                selection-color: {theme.get_color('text_primary').name()};
                outline: none;
            }}
        """

        combobox.setStyleSheet(style_sheet)

    def _apply_style(self):
        """Apply styles to the filter bar"""
        # Mostly handled by individual components
        self._clear_button.set_style(FluentButton.ButtonStyle.SUBTLE)
        if self._category_selector:
            self._setup_combobox_style(self._category_selector)

    def _on_theme_changed(self):
        """Handle theme changes"""
        self._apply_style()

    def _on_filter_changed(self, text: str):
        """Handle filter text changes"""
        self._current_filter = text
        category = self._category_selector.currentText() if self._category_selector else ""
        if category == "All":
            category = ""

        self.filterChanged.emit(text, category)

    def _on_category_changed(self, category: str):
        """Handle category changes"""
        self._current_category = "" if category == "All" else category
        self.filterChanged.emit(self._current_filter, self._current_category)

    def clear_filters(self):
        """Clear all active filters"""
        self._search_input.clear()
        if self._category_selector:
            self._category_selector.setCurrentIndex(0)

        self._current_filter = ""
        self._current_category = ""
        self.filterChanged.emit("", "")

    def get_current_filter(self) -> tuple:
        """Get current filter settings"""
        return (self._current_filter, self._current_category)


class FluentSortingMenu(QMenu):
    """Fluent Design Style Sorting Menu

    Features:
    - Sort direction (ascending/descending)
    - Multiple sort fields
    - Visual indicators for current sort
    """

    sortChanged = Signal(str, bool)  # (field, ascending)

    def __init__(self, parent: Optional[QWidget] = None,
                 fields: Optional[List[Dict[str, str]]] = None):
        """
        Initialize sorting menu

        Args:
            parent: Parent widget
            fields: List of dictionaries with 'name' and 'display' keys
                   e.g. [{'name': 'date', 'display': 'Date'}]
        """
        super().__init__(parent)

        self._current_field = ""
        self._ascending = True
        self._fields = fields or []

        self._setup_menu()

        # Apply styling
        self._apply_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_menu(self):
        """Setup menu items"""
        # Add sort direction submenu
        self.direction_menu = QMenu("Sort Direction")

        self.asc_action = QAction("Ascending", self)
        self.asc_action.setCheckable(True)
        self.asc_action.setChecked(True)
        self.asc_action.triggered.connect(
            lambda: self._on_direction_changed(True))

        self.desc_action = QAction("Descending", self)
        self.desc_action.setCheckable(True)
        self.desc_action.triggered.connect(
            lambda: self._on_direction_changed(False))

        self.direction_menu.addAction(self.asc_action)
        self.direction_menu.addAction(self.desc_action)

        # Add separator
        self.addMenu(self.direction_menu)
        self.addSeparator()

        # Add field actions
        self._field_actions = []
        for field in self._fields:
            action = QAction(field["display"], self)
            action.setCheckable(True)
            action.setData(field["name"])
            # Fix lambda function to properly capture field name
            field_name = field["name"]
            action.triggered.connect(
                lambda triggered=False, f=field_name: self._on_field_changed(f))
            self._field_actions.append(action)
            self.addAction(action)

        # Set default selection if fields exist
        if self._fields:
            self._field_actions[0].setChecked(True)
            self._current_field = self._fields[0]["name"]

    def _apply_style(self):
        """Apply menu styling"""
        theme = theme_manager

        style_sheet = f"""
            QMenu {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 4px 0px;
                font-size: 14px;
            }}
            
            QMenu::item {{
                padding: 6px 32px 6px 20px;
                color: {theme.get_color('text_primary').name()};
            }}
            
            QMenu::item:selected {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            
            QMenu::indicator {{
                width: 18px;
                height: 18px;
                padding-left: 4px;
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {theme.get_color('border').name()};
                margin: 4px 0px;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self):
        """Handle theme changes"""
        self._apply_style()

    def _on_direction_changed(self, ascending: bool):
        """Handle sort direction change"""
        self._ascending = ascending

        # Update checkable actions
        self.asc_action.setChecked(ascending)
        self.desc_action.setChecked(not ascending)

        # Emit signal
        self.sortChanged.emit(self._current_field, self._ascending)

    def _on_field_changed(self, field: str):
        """Handle sort field change"""
        prev_field = self._current_field
        self._current_field = field

        # Update checkable actions
        for action in self._field_actions:
            if action.data() != field:
                action.setChecked(False)
            else:
                action.setChecked(True)

        # If the field actually changed, emit the signal
        if prev_field != field:
            self.sortChanged.emit(self._current_field, self._ascending)

    def get_current_sort(self) -> tuple:
        """Get current sort settings"""
        return (self._current_field, self._ascending)


class FluentFilterSortHeader(QWidget):
    """Combined filter and sort header for data views

    Features:
    - Integrated filter bar
    - Sort button with menu
    - Optional column visibility toggle
    - Compact design for data views
    """

    filterChanged = Signal(str, str)  # (filter_text, category)
    sortChanged = Signal(str, bool)  # (field, ascending)

    def __init__(self, parent: Optional[QWidget] = None,
                 filter_categories: Optional[List[str]] = None,
                 sort_fields: Optional[List[Dict[str, str]]] = None):
        super().__init__(parent)

        # Setup layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

        # Create filter bar
        self._filter_bar = FluentFilterBar(self, categories=filter_categories)
        self._filter_bar.filterChanged.connect(self._on_filter_changed)

        # Create sort button
        self._sort_button = QToolButton(self)
        self._sort_button.setText("Sort")
        self._sort_button.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup)
        self._sort_menu = FluentSortingMenu(self, fields=sort_fields)
        self._sort_menu.sortChanged.connect(self._on_sort_changed)
        self._sort_button.setMenu(self._sort_menu)

        # Add widgets to layout
        self._layout.addWidget(self._filter_bar)
        self._layout.addWidget(self._sort_button)

        # Setup styling
        self._apply_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _apply_style(self):
        """Apply styling to the header"""
        theme = theme_manager

        # Style the sort button
        sort_button_style = f"""
            QToolButton {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 14px;
                min-height: 32px;
                min-width: 60px;
            }}
            
            QToolButton:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
            }}
            
            QToolButton::menu-indicator {{
                width: 16px;
                height: 16px;
                subcontrol-position: right center;
                subcontrol-origin: padding;
            }}
        """

        self._sort_button.setStyleSheet(sort_button_style)

    def _on_theme_changed(self):
        """Handle theme changes"""
        self._apply_style()

    def _on_filter_changed(self, text: str, category: str):
        """Handle filter changes"""
        self.filterChanged.emit(text, category)

    def _on_sort_changed(self, field: str, ascending: bool):
        """Handle sort changes"""
        self.sortChanged.emit(field, ascending)

    def clear_filters(self):
        """Clear all active filters"""
        self._filter_bar.clear_filters()

    def get_current_filter(self) -> tuple:
        """Get current filter settings"""
        return self._filter_bar.get_current_filter()

    def get_current_sort(self) -> tuple:
        """Get current sort settings"""
        return self._sort_menu.get_current_sort()


class FluentFilterProxyModel(QSortFilterProxyModel):
    """Enhanced filter proxy model for Fluent components

    Features:
    - Multi-column filtering
    - Case insensitive matching
    - Custom filter predicates
    - Column visibility control
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._filter_columns = []  # Columns to filter
        self._filter_function = None  # Optional custom filter function
        self._visible_columns = None  # Optional column visibility control

        # Set default filter settings
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterKeyColumn(-1)  # Filter all columns

    def set_filter_columns(self, columns: List[int]):
        """Set which columns to consider for filtering"""
        self._filter_columns = columns
        self.invalidateFilter()

    def set_filter_function(self, func: Callable[[QModelIndex, str], bool]):
        """Set custom filter function

        Args:
            func: Function that takes a source model index and filter string,
                  and returns True if item matches the filter
        """
        self._filter_function = func
        self.invalidateFilter()

    def set_visible_columns(self, columns: List[int]):
        """Set which columns should be visible"""
        self._visible_columns = columns
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        """Determine if a row should be included in the filtered result"""
        # Get filter pattern
        pattern = self.filterRegularExpression().pattern()

        # If no filter, accept row
        if not pattern:
            return True

        # If specific columns set, only check those
        if self._filter_columns:
            columns_to_check = self._filter_columns
        else:
            # Check all columns
            columns_to_check = range(
                self.sourceModel().columnCount(source_parent))

        # If using custom filter function
        if self._filter_function:
            for column in columns_to_check:
                index = self.sourceModel().index(source_row, column, source_parent)
                if self._filter_function(index, pattern):
                    return True
            return False

        # Default filtering: check if any column contains the pattern
        for column in columns_to_check:
            index = self.sourceModel().index(source_row, column, source_parent)
            data = self.sourceModel().data(index)
            if data is not None and pattern.lower() in str(data).lower():
                return True

        return False
