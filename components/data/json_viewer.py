"""
JSON Viewer Components

Advanced JSON viewing and editing components that follow the Fluent Design System.
Includes syntax highlighting, tree view, and validation.
"""

import sys
import json
import re
from typing import Any, Dict, List, Union
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                               QTreeWidget, QTreeWidgetItem, 
                               QPushButton, QLabel, QLineEdit, 
                               QHeaderView, QTabWidget)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import (QFont, QColor, 
                           QTextDocument, QTextCharFormat)

# Import theme manager
try:
    from core.theme import theme_manager
except ImportError:
    theme_manager = None


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """JSON syntax highlighter"""

    def __init__(self, document: QTextDocument):
        super().__init__(document)
        self.setup_highlighting_rules()

    def setup_highlighting_rules(self):
        """Setup syntax highlighting rules"""
        # Get colors from theme
        if theme_manager:
            string_color = theme_manager.get_color('primary')
            number_color = theme_manager.get_color('secondary')
            keyword_color = theme_manager.get_color('tertiary')
            comment_color = theme_manager.get_color('outline')
        else:
            string_color = "#0969da"  # Blue
            number_color = "#cf222e"  # Red
            keyword_color = "#8250df"  # Purple
            comment_color = "#656d76"  # Gray

        # String format
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(string_color))

        # Number format
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor(number_color))

        # Keyword format (true, false, null)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(keyword_color))
        self.keyword_format.setFontWeight(QFont.Weight.Bold)

        # Key format
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor(keyword_color))

        # Brace format
        self.brace_format = QTextCharFormat()
        self.brace_format.setForeground(QColor(comment_color))
        self.brace_format.setFontWeight(QFont.Weight.Bold)

    def highlightBlock(self, text: str):
        """Highlight a block of text"""
        # Highlight strings
        string_pattern = r'"[^"\\]*(\\.[^"\\]*)*"'
        for match in re.finditer(string_pattern, text):
            start, end = match.span()
            # Check if this is a key (followed by :)
            remaining_text = text[end:].strip()
            if remaining_text.startswith(':'):
                self.setFormat(start, end - start, self.key_format)
            else:
                self.setFormat(start, end - start, self.string_format)

        # Highlight numbers
        number_pattern = r'-?\d+\.?\d*([eE][+-]?\d+)?'
        for match in re.finditer(number_pattern, text):
            start, end = match.span()
            # Make sure it's not part of a string
            if not self.is_in_string(text, start):
                self.setFormat(start, end - start, self.number_format)

        # Highlight keywords
        keyword_pattern = r'\b(true|false|null)\b'
        for match in re.finditer(keyword_pattern, text):
            start, end = match.span()
            if not self.is_in_string(text, start):
                self.setFormat(start, end - start, self.keyword_format)

        # Highlight braces and brackets
        brace_pattern = r'[{}[\],]'
        for match in re.finditer(brace_pattern, text):
            start, end = match.span()
            if not self.is_in_string(text, start):
                self.setFormat(start, end - start, self.brace_format)

    def is_in_string(self, text: str, position: int) -> bool:
        """Check if position is inside a string"""
        string_starts = []
        string_ends = []

        # Find all string start and end positions
        for match in re.finditer(r'"', text):
            pos = match.start()
            # Check if it's escaped
            escaped = False
            escape_count = 0
            for i in range(pos - 1, -1, -1):
                if text[i] == '\\':
                    escape_count += 1
                else:
                    break
            escaped = escape_count % 2 == 1

            if not escaped:
                if len(string_starts) == len(string_ends):
                    string_starts.append(pos)
                else:
                    string_ends.append(pos)

        # Check if position is between any string start/end pair
        for i, start in enumerate(string_starts):
            if i < len(string_ends):
                end = string_ends[i]
                if start < position < end:
                    return True

        return False


class FluentJsonTreeWidget(QTreeWidget):
    """JSON tree view widget"""

    item_selected = Signal(str, object)  # path, value

    def __init__(self, parent=None):
        super().__init__(parent)
        self.json_data = None

        self.setup_ui()
        self.apply_theme()

        # Connect to theme changes
        if theme_manager:
            theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup the user interface"""
        self.setHeaderLabels(["Key", "Value", "Type"])
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)

        # Configure header
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # Connect selection signal
        self.itemClicked.connect(self.on_item_clicked)

    def apply_theme(self):
        """Apply the current theme"""
        if not theme_manager:
            return

        bg_color = theme_manager.get_color('surface')
        text_color = theme_manager.get_color('on_surface')
        border_color = theme_manager.get_color('outline')

        self.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {bg_color.name()};
                color: {text_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: 8px;
                gridline-color: {border_color.name()};
                selection-background-color: {theme_manager.get_color('primary_container').name()};
                selection-color: {theme_manager.get_color('on_primary_container').name()};
            }}
            
            QTreeWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {border_color.name()};
            }}
            
            QTreeWidget::item:hover {{
                background-color: {theme_manager.get_color('surface_variant').name()};
            }}
        """)

    def load_json(self, data: Union[str, Dict, List]):
        """Load JSON data into tree"""
        self.clear()

        try:
            if isinstance(data, str):
                self.json_data = json.loads(data)
            else:
                self.json_data = data

            self.populate_tree(self.json_data, self.invisibleRootItem(), "")
            self.expandAll()

        except json.JSONDecodeError as e:
            error_item = QTreeWidgetItem(self)
            error_item.setText(0, "JSON Error")
            error_item.setText(1, str(e))
            error_item.setText(2, "error")

    def populate_tree(self, data: Any, parent: QTreeWidgetItem, path: str):
        """Populate tree with JSON data"""
        if isinstance(data, dict):
            for key, value in data.items():
                item = QTreeWidgetItem(parent)
                item.setText(0, str(key))

                current_path = f"{path}.{key}" if path else key
                item.setData(0, Qt.ItemDataRole.UserRole, current_path)

                if isinstance(value, (dict, list)):
                    item.setText(
                        1, f"{type(value).__name__} ({len(value)} items)")
                    item.setText(2, type(value).__name__)
                    self.populate_tree(value, item, current_path)
                else:
                    item.setText(1, str(value))
                    item.setText(2, type(value).__name__)

        elif isinstance(data, list):
            for i, value in enumerate(data):
                item = QTreeWidgetItem(parent)
                item.setText(0, f"[{i}]")

                current_path = f"{path}[{i}]" if path else f"[{i}]"
                item.setData(0, Qt.ItemDataRole.UserRole, current_path)

                if isinstance(value, (dict, list)):
                    item.setText(
                        1, f"{type(value).__name__} ({len(value)} items)")
                    item.setText(2, type(value).__name__)
                    self.populate_tree(value, item, current_path)
                else:
                    item.setText(1, str(value))
                    item.setText(2, type(value).__name__)

    def on_item_clicked(self, item: QTreeWidgetItem, _column: int):
        """Handle item click"""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path and self.json_data is not None:
            try:
                # Navigate to the value in json_data
                value = self.json_data

                # Parse path
                parts = self.parse_path(path)
                for part in parts:
                    if value is None: # Check if value became None during path traversal
                        break
                    if isinstance(part, int):
                        if isinstance(value, list) and 0 <= part < len(value):
                            value = value[part]
                        else:
                            value = None # Path is invalid
                            break
                    else: # part is a string (key)
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            value = None # Path is invalid
                            break
                
                if value is not None:
                    self.item_selected.emit(path, value)

            except (KeyError, IndexError, TypeError):
                # This might happen if json_data structure is unexpected or path is malformed
                # Or if value becomes something not subscriptable unexpectedly
                pass

    def parse_path(self, path: str) -> List[Union[str, int]]:
        """Parse JSON path into components"""
        parts = []
        current = ""
        in_bracket = False

        for char in path:
            if char == '[':
                if current:
                    parts.append(current)
                    current = ""
                in_bracket = True
            elif char == ']':
                if current.isdigit():
                    parts.append(int(current))
                else: # Should ideally not happen if path is well-formed for list indices
                    parts.append(current) # Keep as string if not a digit inside brackets
                current = ""
                in_bracket = False
            elif char == '.' and not in_bracket:
                if current:
                    parts.append(current)
                    current = ""
            else:
                current += char

        if current:
            # Last part, if it's an index it should have been closed by ']'
            # So, if in_bracket is true here, it's likely a malformed path.
            # However, the original logic handles it as potentially an index.
            if current.isdigit() and in_bracket: # This case might be problematic
                parts.append(int(current))
            else:
                parts.append(current)

        return parts


class FluentJsonViewer(QWidget):
    """
    Comprehensive JSON viewer with text and tree views
    """

    json_changed = Signal(object)  # JSON data
    validation_changed = Signal(bool, str)  # is_valid, error_message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.json_data = None
        self.is_valid = True

        self.setup_ui()
        self.apply_theme()

        # Setup validation timer
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.validate_json)

        # Connect to theme changes
        if theme_manager:
            theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 10, 10, 10)
        toolbar_layout.setSpacing(10)

        # Format button
        self.format_btn = QPushButton("Format JSON")
        self.format_btn.clicked.connect(self.format_json)
        toolbar_layout.addWidget(self.format_btn)

        # Minify button
        self.minify_btn = QPushButton("Minify JSON")
        self.minify_btn.clicked.connect(self.minify_json)
        toolbar_layout.addWidget(self.minify_btn)

        # Validate button
        self.validate_btn = QPushButton("Validate")
        self.validate_btn.clicked.connect(self.validate_json)
        toolbar_layout.addWidget(self.validate_btn)

        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_json)
        toolbar_layout.addWidget(self.clear_btn)

        toolbar_layout.addStretch()

        # Status labels
        self.status_label = QLabel("Ready")
        toolbar_layout.addWidget(self.status_label)

        self.validation_label = QLabel("✓ Valid JSON")
        self.validation_label.setStyleSheet("color: green; font-weight: bold;")
        toolbar_layout.addWidget(self.validation_label)

        layout.addLayout(toolbar_layout)

        # Main content
        self.tab_widget = QTabWidget()

        # Text view tab
        self.text_widget = QWidget()
        text_layout = QVBoxLayout(self.text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)

        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.textChanged.connect(self.on_text_changed)

        # Setup syntax highlighting
        self.highlighter = JsonSyntaxHighlighter(self.text_edit.document())

        text_layout.addWidget(self.text_edit)
        self.tab_widget.addTab(self.text_widget, "Text View")

        # Tree view tab
        self.tree_widget = FluentJsonTreeWidget()
        self.tree_widget.item_selected.connect(self.on_tree_item_selected)
        self.tab_widget.addTab(self.tree_widget, "Tree View")

        layout.addWidget(self.tab_widget)

        # Current selection info
        self.selection_layout = QHBoxLayout()
        self.selection_layout.setContentsMargins(10, 5, 10, 10)

        self.path_label = QLabel("Path: ")
        self.selection_layout.addWidget(self.path_label)

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("Select an item in tree view")
        self.selection_layout.addWidget(self.path_edit)

        layout.addLayout(self.selection_layout)

    def apply_theme(self):
        """Apply the current theme"""
        if not theme_manager:
            return

        bg_color = theme_manager.get_color('surface')
        text_color = theme_manager.get_color('on_surface')
        border_color = theme_manager.get_color('outline')

        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_color.name()};
                color: {text_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                /* line-height: 1.4; */ /* QTextEdit does not have line-height directly */
                padding: 10px;
            }}
            
            QPushButton {{
                background-color: {theme_manager.get_color('primary').name()};
                color: {theme_manager.get_color('on_primary').name()};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {theme_manager.get_color('primary_container').name()};
            }}
            
            QPushButton:pressed {{
                background-color: {theme_manager.get_color('secondary').name()};
            }}
            
            QLineEdit {{
                background-color: {bg_color.name()};
                color: {text_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: 6px;
                padding: 6px;
            }}
            QTabWidget::pane {{
                border-top: 1px solid {border_color.name()};
                background: {bg_color.name()};
            }}
            QTabBar::tab {{
                background: {theme_manager.get_color('surface_variant').name()};
                color: {theme_manager.get_color('on_surface_variant').name()};
                border: 1px solid {border_color.name()};
                border-bottom: none; 
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {bg_color.name()};
                color: {text_color.name()};
                border-bottom: 1px solid {bg_color.name()}; /* Make selected tab blend with pane */
            }}
            QTabBar::tab:hover {{
                background: {theme_manager.get_color('surface_tint').name()};
            }}
        """)
        # Apply theme to child tree widget as well
        self.tree_widget.apply_theme()
        # Re-initialize highlighter as theme colors might have changed
        self.highlighter.setup_highlighting_rules()
        self.highlighter.rehighlight()


    def set_json(self, data: Union[str, Dict, List]):
        """Set JSON data"""
        try:
            if isinstance(data, str):
                self.json_data = json.loads(data)
                formatted_text = json.dumps(
                    self.json_data, indent=2, ensure_ascii=False)
            else:
                self.json_data = data
                formatted_text = json.dumps(data, indent=2, ensure_ascii=False)

            # Update text view
            self.text_edit.setPlainText(formatted_text)

            # Update tree view
            self.tree_widget.load_json(self.json_data)

            # Update status
            self.is_valid = True
            self.validation_label.setText("✓ Valid JSON")
            self.validation_label.setStyleSheet(
                "color: green; font-weight: bold;")
            self.status_label.setText("JSON loaded successfully")

            self.json_changed.emit(self.json_data)
            self.validation_changed.emit(True, "")

        except json.JSONDecodeError as e:
            self.is_valid = False
            self.validation_label.setText(f"✗ Invalid JSON: {e}")
            self.validation_label.setStyleSheet(
                "color: red; font-weight: bold;")
            self.status_label.setText("JSON parse error")

            self.validation_changed.emit(False, str(e))

    def get_json(self) -> Any:
        """Get current JSON data"""
        return self.json_data

    def get_json_text(self) -> str:
        """Get JSON as text"""
        return self.text_edit.toPlainText()

    def on_text_changed(self):
        """Handle text change"""
        # Delay validation to avoid constant parsing
        self.validation_timer.stop()
        self.validation_timer.start(500)  # 500ms delay

    def validate_json(self):
        """Validate current JSON text"""
        text = self.text_edit.toPlainText().strip()

        if not text:
            self.is_valid = True
            self.json_data = None # Ensure json_data is None for empty text
            self.validation_label.setText("Empty")
            self.validation_label.setStyleSheet(
                "color: gray; font-weight: bold;")
            self.status_label.setText("Ready")
            self.tree_widget.clear() # Clear tree view for empty JSON
            self.json_changed.emit(self.json_data)
            self.validation_changed.emit(True, "") # Empty is considered valid
            return

        try:
            self.json_data = json.loads(text)

            # Update tree view
            self.tree_widget.load_json(self.json_data)

            self.is_valid = True
            self.validation_label.setText("✓ Valid JSON")
            self.validation_label.setStyleSheet(
                "color: green; font-weight: bold;")
            self.status_label.setText("JSON is valid")

            self.json_changed.emit(self.json_data)
            self.validation_changed.emit(True, "")

        except json.JSONDecodeError as e:
            self.is_valid = False
            self.json_data = None # Invalid JSON means no valid data
            error_msg = f"Line {e.lineno}, Column {e.colno}: {e.msg}"
            self.validation_label.setText(f"✗ Invalid JSON")
            self.validation_label.setStyleSheet(
                "color: red; font-weight: bold;")
            self.status_label.setText(error_msg)
            # self.tree_widget.clear() # Optionally clear tree on invalid JSON
            self.validation_changed.emit(False, error_msg)

    def format_json(self):
        """Format JSON with proper indentation"""
        if self.is_valid and self.json_data is not None:
            formatted = json.dumps(
                self.json_data, indent=2, ensure_ascii=False)
            self.text_edit.setPlainText(formatted)
            self.status_label.setText("JSON formatted")
        elif not self.text_edit.toPlainText().strip():
             self.status_label.setText("Cannot format empty JSON")
        else:
            self.status_label.setText("Cannot format invalid JSON")


    def minify_json(self):
        """Minify JSON (remove whitespace)"""
        if self.is_valid and self.json_data is not None:
            minified = json.dumps(self.json_data, separators=(
                ',', ':'), ensure_ascii=False)
            self.text_edit.setPlainText(minified)
            self.status_label.setText("JSON minified")
        elif not self.text_edit.toPlainText().strip():
            self.status_label.setText("Cannot minify empty JSON")
        else:
            self.status_label.setText("Cannot minify invalid JSON")


    def clear_json(self):
        """Clear JSON content"""
        self.text_edit.clear()
        self.tree_widget.clear()
        self.path_edit.clear()
        self.json_data = None
        self.is_valid = True
        self.validation_label.setText("Empty")
        self.validation_label.setStyleSheet("color: gray; font-weight: bold;")
        self.status_label.setText("Ready")
        self.json_changed.emit(None)
        self.validation_changed.emit(True, "")


    def on_tree_item_selected(self, path: str, value: Any):
        """Handle tree item selection"""
        self.path_edit.setText(path)

        # Show value details in status
        if isinstance(value, (dict, list)):
            self.status_label.setText(
                f"Selected: {type(value).__name__} with {len(value)} items")
        else:
            self.status_label.setText(
                f"Selected: {type(value).__name__} = {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("JSON Viewer Demo")
    window.setGeometry(100, 100, 1000, 700)

    # Create JSON viewer
    json_viewer = FluentJsonViewer()
    window.setCentralWidget(json_viewer)

    # Load sample JSON
    sample_json = {
        "name": "John Doe",
        "age": 30,
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "zipcode": "10001"
        },
        "hobbies": ["reading", "swimming", "coding"],
        "married": True,
        "children": None,
        "scores": [85.5, 92.0, 78.5]
    }

    json_viewer.set_json(sample_json)

    window.show()
    sys.exit(app.exec())
