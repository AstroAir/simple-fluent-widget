"""
Fluent Design Search Box Component
Specialized search input with search icon, clear button, and suggestions
"""

from typing import Optional, List, Callable, Any
from PySide6.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QPushButton,
                               QListWidget, QListWidgetItem, QVBoxLayout,
                               QFrame)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QIcon, QPainter, QPen, QColor, QPixmap

from components.base.fluent_control_base import FluentControlBase
from components.base.fluent_component_interface import (
    FluentComponentSize
)


class FluentSearchBox(FluentControlBase):
    """
    Fluent Design Search Box Component

    Features:
    - Search icon and clear button
    - Real-time search suggestions
    - Customizable placeholder text
    - Theme-consistent styling
    - Keyboard navigation support
    """

    # Signals
    search_requested = Signal(str)     # Emitted when search is requested
    text_changed = Signal(str)         # Emitted when text changes
    suggestion_selected = Signal(str)  # Emitted when suggestion is selected
    cleared = Signal()                 # Emitted when search is cleared

    def __init__(self, parent: Optional[QWidget] = None,
                 placeholder: str = "Search...",
                 size: FluentComponentSize = FluentComponentSize.MEDIUM):
        super().__init__(parent)

        # Properties
        self._placeholder = placeholder
        self._suggestions: List[str] = []
        self._is_suggestions_visible = False
        self._search_delay = 300  # ms
        self._min_search_length = 1

        # Add missing _size property
        self._size = size

        # Setup component
        self._component_type = "FluentSearchBox"
        self.set_placeholder(self._placeholder)
        self.set_accessible_name("Search input")

        # Create UI elements
        self._setup_ui()
        self._setup_connections()
        self._apply_themed_styles()
        self._on_size_changed()  # Ensure initial sizing

    def set_size(self, size: FluentComponentSize):
        """Set the size of the search box."""
        self._size = size
        self._on_size_changed()

    def get_size(self) -> FluentComponentSize:
        """Get the current size of the search box."""
        return self._size

    def set_accessible_role(self, role: str):
        """Set the accessible role for the widget (for compatibility)."""
        # PySide6 does not have setAccessibleRole, so this is a no-op or can be extended for custom accessibility
        pass

    def _setup_ui(self):
        """Setup the search box UI"""
        # Main layout
        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        self.setLayout(self._main_layout)

        # Search input container
        self._input_container = QFrame()
        self._input_layout = QHBoxLayout()
        self._input_layout.setContentsMargins(8, 6, 8, 6)
        self._input_layout.setSpacing(6)
        self._input_container.setLayout(self._input_layout)

        # Search icon
        self._search_icon = QPushButton()
        self._search_icon.setFlat(True)
        self._search_icon.setFixedSize(20, 20)
        self._search_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_search_icon()

        # Text input
        self._text_input = QLineEdit()
        self._text_input.setPlaceholderText(self._placeholder)
        self._text_input.setFrame(False)

        # Clear button
        self._clear_button = QPushButton()
        self._clear_button.setFlat(True)
        self._clear_button.setFixedSize(20, 20)
        self._clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_button.setVisible(False)
        self._setup_clear_icon()

        # Add to layout
        self._input_layout.addWidget(self._search_icon)
        self._input_layout.addWidget(self._text_input, 1)
        self._input_layout.addWidget(self._clear_button)
        self._main_layout.addWidget(self._input_container)

        # Suggestions list
        self._suggestions_list = QListWidget()
        self._suggestions_list.setVisible(False)
        self._suggestions_list.setMaximumHeight(200)
        self._main_layout.addWidget(self._suggestions_list)

        # Search timer
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)

        # Set focus policy
        self.setFocusProxy(self._text_input)

    def _setup_search_icon(self):
        """Setup search icon"""
        # Create simple search icon using QPainter
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw search icon
        pen = QPen(QColor("#666666"), 2)
        painter.setPen(pen)
        painter.drawEllipse(2, 2, 8, 8)
        painter.drawLine(9, 9, 14, 14)
        painter.end()

        self._search_icon.setIcon(QIcon(pixmap))

    def _setup_clear_icon(self):
        """Setup clear icon"""
        # Create simple X icon using QPainter
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw X icon
        pen = QPen(QColor("#666666"), 2)
        painter.setPen(pen)
        painter.drawLine(4, 4, 12, 12)
        painter.drawLine(12, 4, 4, 12)
        painter.end()

        self._clear_button.setIcon(QIcon(pixmap))

    def _setup_connections(self):
        """Setup signal connections"""
        self._text_input.textChanged.connect(self._on_text_changed)
        self._text_input.returnPressed.connect(self._on_search_requested)
        self._search_icon.clicked.connect(self._on_search_requested)
        self._clear_button.clicked.connect(self._on_clear_requested)
        self._search_timer.timeout.connect(self._on_search_timer)
        self._suggestions_list.itemClicked.connect(self._on_suggestion_clicked)

        # Install event filter for escape key
        self._text_input.installEventFilter(self)
        self._suggestions_list.installEventFilter(self)

    def _apply_themed_styles(self):
        """Apply themed styles"""
        # Get theme colors
        bg_color = self._theme_tokens.get("surface", QColor("#FFFFFF"))
        border_color = self._theme_tokens.get("border", QColor("#CCCCCC"))
        text_color = self._theme_tokens.get("text_primary", QColor("#000000"))
        radius = self._theme_tokens.get("corner_radius", 6)

        # Apply styles to container
        container_style = f"""
            QFrame {{
                background-color: {bg_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: {radius}px;
            }}
            QFrame:focus-within {{
                border-color: {self._theme_tokens.get("primary", QColor("#0078D4")).name()};
                border-width: 2px;
            }}
        """
        self._input_container.setStyleSheet(container_style)

        # Apply styles to text input
        input_style = f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {text_color.name()};
                font-size: {self._theme_tokens.get("font_size", 14)}px;
            }}
        """
        self._text_input.setStyleSheet(input_style)

        # Apply styles to suggestions list
        suggestions_style = f"""
            QListWidget {{
                background-color: {bg_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: {radius}px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {border_color.lighter(150).name()};
            }}
            QListWidget::item:hover {{
                background-color: {self._theme_tokens.get("accent", QColor("#F3F2F1")).name()};
            }}
            QListWidget::item:selected {{
                background-color: {self._theme_tokens.get("primary", QColor("#0078D4")).name()};
                color: white;
            }}
        """
        self._suggestions_list.setStyleSheet(suggestions_style)

    def _apply_state_styles(self):
        """Apply state-specific styles"""
        self._apply_themed_styles()

    def get_value(self) -> str:
        """Get current search text"""
        return self._text_input.text()

    def set_value(self, value: Any) -> None:
        """Set search text"""
        if isinstance(value, str):
            self._text_input.setText(value)

    def get_text(self) -> str:
        """Get current search text"""
        return self._text_input.text()

    def set_text(self, text: str) -> None:
        """Set search text"""
        self._text_input.setText(text)

    def get_placeholder(self) -> str:
        """Get placeholder text"""
        return self._placeholder

    def set_placeholder(self, placeholder: str) -> None:
        """Set placeholder text"""
        self._placeholder = placeholder
        self._text_input.setPlaceholderText(placeholder)

    def set_suggestions(self, suggestions: List[str]) -> None:
        """Set search suggestions"""
        self._suggestions = suggestions.copy()
        self._update_suggestions_list()

    def add_suggestion(self, suggestion: str) -> None:
        """Add a search suggestion"""
        if suggestion not in self._suggestions:
            self._suggestions.append(suggestion)
            self._update_suggestions_list()

    def clear_suggestions(self) -> None:
        """Clear all suggestions"""
        self._suggestions.clear()
        self._suggestions_list.clear()
        self._hide_suggestions()

    def set_search_delay(self, delay: int) -> None:
        """Set search delay in milliseconds"""
        self._search_delay = max(0, delay)

    def set_min_search_length(self, length: int) -> None:
        """Set minimum search length"""
        self._min_search_length = max(0, length)

    def clear(self) -> None:
        """Clear search text"""
        self._text_input.clear()
        self._hide_suggestions()
        self.cleared.emit()

    def _update_suggestions_list(self) -> None:
        """Update suggestions list based on current text"""
        current_text = self._text_input.text().lower()
        if len(current_text) < self._min_search_length:
            self._hide_suggestions()
            return

        # Filter suggestions
        filtered_suggestions = [
            s for s in self._suggestions
            if current_text in s.lower()
        ]

        if filtered_suggestions:
            self._show_suggestions(filtered_suggestions)
        else:
            self._hide_suggestions()

    def _show_suggestions(self, suggestions: List[str]) -> None:
        """Show suggestions list"""
        self._suggestions_list.clear()
        for suggestion in suggestions[:10]:  # Limit to 10 suggestions
            item = QListWidgetItem(suggestion)
            self._suggestions_list.addItem(item)

        self._suggestions_list.setVisible(True)
        self._is_suggestions_visible = True

    def _hide_suggestions(self) -> None:
        """Hide suggestions list"""
        self._suggestions_list.setVisible(False)
        self._is_suggestions_visible = False

    def _on_text_changed(self, text: str) -> None:
        """Handle text change"""
        # Show/hide clear button
        self._clear_button.setVisible(bool(text))

        # Start search timer
        if self._search_delay > 0:
            self._search_timer.start(self._search_delay)
        else:
            self._update_suggestions_list()

        self.text_changed.emit(text)

    def _on_search_timer(self) -> None:
        """Handle search timer timeout"""
        self._update_suggestions_list()

    def _on_search_requested(self) -> None:
        """Handle search request"""
        text = self._text_input.text().strip()
        if text:
            self._hide_suggestions()
            self.search_requested.emit(text)

    def _on_clear_requested(self) -> None:
        """Handle clear request"""
        self.clear()

    def _on_suggestion_clicked(self, item: QListWidgetItem) -> None:
        """Handle suggestion click"""
        suggestion = item.text()
        self._text_input.setText(suggestion)
        self._hide_suggestions()
        self.suggestion_selected.emit(suggestion)
        self.search_requested.emit(suggestion)

    def eventFilter(self, obj, event) -> bool:
        """Handle key events for navigation"""
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                if self._is_suggestions_visible:
                    self._hide_suggestions()
                    return True
            elif event.key() == Qt.Key.Key_Down:
                if not self._is_suggestions_visible and self._suggestions:
                    self._update_suggestions_list()
                elif self._is_suggestions_visible:
                    self._suggestions_list.setFocus()
                    return True
            elif event.key() == Qt.Key.Key_Up:
                if self._is_suggestions_visible:
                    self._suggestions_list.setFocus()
                    return True

        return super().eventFilter(obj, event)

    def _on_size_changed(self) -> None:
        """Handle size changes"""
        size_map = {
            FluentComponentSize.TINY: (16, 24),
            FluentComponentSize.SMALL: (18, 28),
            FluentComponentSize.MEDIUM: (20, 32),
            FluentComponentSize.LARGE: (22, 36),
            FluentComponentSize.XLARGE: (24, 40)
        }
        icon_size, height = size_map.get(self._size, (20, 32))

        self._search_icon.setFixedSize(icon_size, icon_size)
        self._clear_button.setFixedSize(icon_size, icon_size)
        self._input_container.setMinimumHeight(height)

        # Update font size
        font = self._text_input.font()
        font.setPixelSize(self._theme_tokens.get("font_size", 14))
        self._text_input.setFont(font)
