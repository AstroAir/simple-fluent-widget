"""
JSON Viewer Components

Advanced JSON viewing and editing components that follow the Fluent Design System.
Includes syntax highlighting, tree view, and validation with modern Python features.
"""

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Union, Optional, Protocol, TypeAlias, Final
from contextlib import contextmanager

from PySide6.QtWidgets import (QWidget,
                               QTreeWidget, QTreeWidgetItem,
                               QHeaderView)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (QFont, QColor, QSyntaxHighlighter,
                           QTextDocument, QTextCharFormat)

# Import enhanced components
from core.theme import theme_manager


# Type aliases for better readability
JsonData: TypeAlias = Union[Dict[str, Any],
                            List[Any], str, int, float, bool, None]
JsonPath: TypeAlias = str


class JsonHighlightRule(Enum):
    """JSON syntax highlighting rules"""
    STRING = auto()
    NUMBER = auto()
    KEYWORD = auto()
    KEY = auto()
    BRACE = auto()
    OPERATOR = auto()


@dataclass(frozen=True)
class JsonSyntaxConfig:
    """Configuration for JSON syntax highlighting"""
    string_color: str = "#0969da"
    number_color: str = "#cf222e"
    keyword_color: str = "#8250df"
    key_color: str = "#8250df"
    brace_color: str = "#656d76"
    operator_color: str = "#656d76"

    def get_color(self, rule: JsonHighlightRule) -> str:
        """Get color for a highlighting rule"""
        return {
            JsonHighlightRule.STRING: self.string_color,
            JsonHighlightRule.NUMBER: self.number_color,
            JsonHighlightRule.KEYWORD: self.keyword_color,
            JsonHighlightRule.KEY: self.key_color,
            JsonHighlightRule.BRACE: self.brace_color,
            JsonHighlightRule.OPERATOR: self.operator_color,
        }[rule]


@dataclass
class JsonTreeConfig:
    """Configuration for JSON tree widget"""
    max_value_length: int = 100
    auto_expand_depth: int = 2
    enable_alternating_colors: bool = True
    show_type_column: bool = True


@dataclass
class ValidationState:
    """JSON validation state"""
    is_valid: bool = True
    error_message: str = ""
    line_number: Optional[int] = None
    column_number: Optional[int] = None


class JsonViewerTheme(Protocol):
    """Protocol for theme management in JSON viewer"""

    def get_color(self, name: str) -> QColor: ...
    def theme_changed(self) -> Signal: ...


class OptimizedJsonSyntaxHighlighter(QSyntaxHighlighter):
    """Optimized JSON syntax highlighter with caching and modern features"""

    # Compiled regex patterns for better performance
    _patterns: Final[Dict[JsonHighlightRule, re.Pattern]] = {
        JsonHighlightRule.STRING: re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'),
        JsonHighlightRule.NUMBER: re.compile(r'-?\d+\.?\d*([eE][+-]?\d+)?'),
        JsonHighlightRule.KEYWORD: re.compile(r'\b(true|false|null)\b'),
        JsonHighlightRule.BRACE: re.compile(r'[{}[\],:]'),
    }

    def __init__(self, document: QTextDocument, theme: Optional[JsonViewerTheme] = None):
        super().__init__(document)
        self._theme = theme or theme_manager
        self._config = JsonSyntaxConfig()
        self._formats: Dict[JsonHighlightRule, QTextCharFormat] = {}
        self._setup_highlighting_rules()

        # Cache for string positions to avoid repeated computation
        self._string_positions_cache: Dict[str, List[tuple[int, int]]] = {}

    def _setup_highlighting_rules(self):
        """Setup syntax highlighting rules with theme integration"""
        if hasattr(self._theme, 'get_color'):
            try:
                # Use theme colors if available
                self._config = JsonSyntaxConfig(
                    string_color=self._theme.get_color('primary').name(),
                    number_color=self._theme.get_color('secondary').name(),
                    keyword_color=self._theme.get_color('tertiary').name(),
                    key_color=self._theme.get_color('tertiary').name(),
                    brace_color=self._theme.get_color('outline').name(),
                    operator_color=self._theme.get_color('outline').name(),
                )
            except (AttributeError, KeyError):
                # Fall back to default colors
                pass

        # Create text formats
        for rule in JsonHighlightRule:
            fmt = QTextCharFormat()
            color = self._config.get_color(rule)
            fmt.setForeground(QColor(color))

            if rule in (JsonHighlightRule.KEYWORD, JsonHighlightRule.BRACE):
                fmt.setFontWeight(QFont.Weight.Bold)

            self._formats[rule] = fmt

    # Fix: Changed return type hint to match the cache type
    def _find_string_positions(self, text: str) -> List[tuple[int, int]]:
        """Find string positions with caching"""
        # Check cache first
        # Fix: Return the list directly from the cache
        if text in self._string_positions_cache:
            return self._string_positions_cache[text]

        positions = []
        for match in self._patterns[JsonHighlightRule.STRING].finditer(text):
            positions.append(match.span())

        # Store in cache
        # Fix: Store the list directly in the cache
        self._string_positions_cache[text] = positions
        # Fix: Return the list directly
        return positions

    def _is_in_string(self, text: str, position: int) -> bool:
        """Optimized check if position is inside a string"""
        string_positions = self._find_string_positions(text)
        return any(start < position < end for start, end in string_positions)

    def highlightBlock(self, text: str):
        """Highlight a block of text with optimization"""
        if not text.strip():
            return

        # Highlight strings first and determine if they are keys
        string_positions = self._find_string_positions(text)
        for start, end in string_positions:
            # Check if this is a key (followed by :)
            remaining_text = text[end:].strip()
            rule = JsonHighlightRule.KEY if remaining_text.startswith(
                ':') else JsonHighlightRule.STRING
            self.setFormat(start, end - start, self._formats[rule])

        # Highlight numbers (avoid strings)
        for match in self._patterns[JsonHighlightRule.NUMBER].finditer(text):
            start, end = match.span()
            if not self._is_in_string(text, start):
                self.setFormat(start, end - start,
                               self._formats[JsonHighlightRule.NUMBER])

        # Highlight keywords (avoid strings)
        for match in self._patterns[JsonHighlightRule.KEYWORD].finditer(text):
            start, end = match.span()
            if not self._is_in_string(text, start):
                self.setFormat(start, end - start,
                               self._formats[JsonHighlightRule.KEYWORD])

        # Highlight braces and operators (avoid strings)
        for match in self._patterns[JsonHighlightRule.BRACE].finditer(text):
            start, end = match.span()
            if not self._is_in_string(text, start):
                self.setFormat(start, end - start,
                               self._formats[JsonHighlightRule.BRACE])

    def update_theme(self):
        """Update highlighting when theme changes"""
        self._setup_highlighting_rules()
        self._string_positions_cache.clear()
        self.rehighlight()


# Backward compatibility aliases
JsonSyntaxHighlighter = OptimizedJsonSyntaxHighlighter


class OptimizedJsonTreeWidget(QTreeWidget):
    """Optimized JSON tree view widget with modern features"""

    item_selected = Signal(str, object)  # path, value
    item_double_clicked = Signal(str, object)  # path, value

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._config = JsonTreeConfig()
        self._json_data: Optional[JsonData] = None
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Setup the tree widget UI"""
        headers = ["Key", "Value"]
        if self._config.show_type_column:
            headers.append("Type")

        self.setHeaderLabels(headers)
        self.setAlternatingRowColors(self._config.enable_alternating_colors)
        self.setExpandsOnDoubleClick(False)
        self.setSortingEnabled(True)

        # Configure header
        header = self.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def _setup_connections(self):
        """Setup signal connections"""
        self.itemClicked.connect(self._on_item_clicked)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

    def _on_item_clicked(self, item: QTreeWidgetItem):
        """Handle item click"""
        if item:
            path = self._get_item_path(item)
            value = item.data(0, Qt.ItemDataRole.UserRole)
            self.item_selected.emit(path, value)

    def _on_item_double_clicked(self, item: QTreeWidgetItem):
        """Handle item double click"""
        if item:
            path = self._get_item_path(item)
            value = item.data(0, Qt.ItemDataRole.UserRole)
            self.item_double_clicked.emit(path, value)

    def _get_item_path(self, item: QTreeWidgetItem) -> str:
        """Get the JSON path for an item"""
        path_parts = []
        current = item

        while current and current.parent():
            parent = current.parent()
            if parent:
                # Get the key from the item
                key = current.text(0)
                path_parts.append(key)
            current = parent

        path_parts.reverse()
        return ".".join(path_parts) if path_parts else ""

    def _get_type_name(self, value: Any) -> str:
        """Get human-readable type name"""
        type_map = {
            dict: "Object",
            list: "Array",
            str: "String",
            int: "Number",
            float: "Number",
            bool: "Boolean",
            type(None): "Null"
        }
        return type_map.get(type(value), str(type(value).__name__))

    def _format_value(self, value: Any) -> str:
        """Format value for display with length limit"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (dict, list)):
            count = len(value)
            type_name = "object" if isinstance(value, dict) else "array"
            return f"{type_name} ({count} items)"
        else:
            str_value = str(value)
            if len(str_value) > self._config.max_value_length:
                return str_value[:self._config.max_value_length] + "..."
            return str_value

    def _create_tree_item(self, key: str, value: Any, parent: Optional[QTreeWidgetItem] = None) -> QTreeWidgetItem:
        """Create a tree widget item"""
        if parent:
            item = QTreeWidgetItem(parent)
        else:
            item = QTreeWidgetItem(self)

        # Set key and value
        item.setText(0, key)
        item.setText(1, self._format_value(value))

        if self._config.show_type_column:
            item.setText(2, self._get_type_name(value))

        # Store original value
        item.setData(0, Qt.ItemDataRole.UserRole, value)

        # Set icon and styling based on type
        if isinstance(value, dict):
            item.setExpanded(False)
        elif isinstance(value, list):
            item.setExpanded(False)

        return item

    def _populate_tree_recursive(self, data: Any, parent: Optional[QTreeWidgetItem] = None, depth: int = 0):
        """Recursively populate the tree"""
        if isinstance(data, dict):
            for key, value in data.items():
                item = self._create_tree_item(str(key), value, parent)

                if isinstance(value, (dict, list)) and value:
                    self._populate_tree_recursive(value, item, depth + 1)

                # Auto-expand based on config
                if depth < self._config.auto_expand_depth:
                    item.setExpanded(True)

        elif isinstance(data, list):
            for i, value in enumerate(data):
                item = self._create_tree_item(f"[{i}]", value, parent)

                if isinstance(value, (dict, list)) and value:
                    self._populate_tree_recursive(value, item, depth + 1)

                # Auto-expand based on config
                if depth < self._config.auto_expand_depth:
                    item.setExpanded(True)

    def set_json_data(self, data: JsonData):
        """Set JSON data to display"""
        self._json_data = data
        self.clear()

        try:
            if data is not None:
                with self._batch_updates():
                    if isinstance(data, (dict, list)):
                        self._populate_tree_recursive(data)
                    else:
                        # Single value
                        self._create_tree_item("value", data)
        except Exception as e:
            self._show_error(f"Error displaying JSON data: {e}")

    @contextmanager
    def _batch_updates(self):
        """Context manager for batch updates"""
        self.setUpdatesEnabled(False)
        try:
            yield
        finally:
            self.setUpdatesEnabled(True)

    def _show_error(self, message: str):
        """Show error in tree view"""
        error_item = QTreeWidgetItem(self)
        error_item.setText(0, "Error")
        error_item.setText(1, message)
        if self._config.show_type_column:
            error_item.setText(2, "Error")

    def expand_all_recursive(self):
        """Expand all items recursively"""
        def expand_recursive(item: QTreeWidgetItem, depth: int):
            item.setExpanded(True)
            for i in range(item.childCount()):
                child = item.child(i)
                if child:
                    expand_recursive(child, depth + 1)

        with self._batch_updates():
            for i in range(self.topLevelItemCount()):
                top_item = self.topLevelItem(i)
                if top_item:
                    expand_recursive(top_item, 0)

    def collapse_all_recursive(self):
        """Collapse all items recursively"""
        def collapse_recursive(item: QTreeWidgetItem):
            item.setExpanded(False)
            for i in range(item.childCount()):
                child = item.child(i)
                if child:
                    collapse_recursive(child)

        with self._batch_updates():
            for i in range(self.topLevelItemCount()):
                top_item = self.topLevelItem(i)
                if top_item:
                    collapse_recursive(top_item)

    def search_items(self, query: str) -> List[QTreeWidgetItem]:
        """Search for items matching query"""
        if not query:
            return []

        matching_items = []
        query_lower = query.lower()

        def search_recursive(item: QTreeWidgetItem):
            # Check key and value
            key = item.text(0).lower()
            value = item.text(1).lower()

            if query_lower in key or query_lower in value:
                matching_items.append(item)

            # Search children
            for i in range(item.childCount()):
                child = item.child(i)
                if child:
                    search_recursive(child)

        for i in range(self.topLevelItemCount()):
            top_item = self.topLevelItem(i)
            if top_item:
                search_recursive(top_item)

        return matching_items

    def highlight_search_results(self, items: List[QTreeWidgetItem]):
        """Highlight search results"""
        # Clear previous highlights
        self.clearSelection()

        # Select matching items
        for item in items:
            item.setSelected(True)

        # Scroll to first match
        if items:
            self.scrollToItem(items[0])
