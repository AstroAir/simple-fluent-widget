"""
Fluent Design AutoSuggestBox Component
An input field with intelligent autocomplete suggestions
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
                               QListWidgetItem, QLabel, QFrame, QSizePolicy)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QIcon, QFont, QKeyEvent
from PySide6.QtCore import QPropertyAnimation  # 修复类型未定义
from core.theme import theme_manager
from core.enhanced_base import FluentBaseWidget
from core.enhanced_animations import FluentTransition
from typing import Optional, List, Any, Callable


class FluentSuggestionItem:
    """Represents a suggestion item with metadata"""

    def __init__(self, text: str, data: Any = None, icon: Optional[QIcon] = None):
        self.text = text
        self.data = data  # Additional data associated with the suggestion
        self.icon = icon
        self.score = 0.0  # Relevance score for filtering


class FluentAutoSuggestBox(FluentBaseWidget):
    """
    Fluent Design AutoSuggestBox Component

    An intelligent input field that provides autocomplete suggestions as users type:
    - Fuzzy matching and scoring
    - Custom suggestion sources
    - Keyboard navigation
    - Theme-consistent styling
    - Smooth animations
    """

    # Signals
    text_changed = Signal(str)  # Emitted when text changes
    # Emitted when suggestion is chosen
    suggestion_selected = Signal(str, object)
    query_submitted = Signal(str)  # Emitted when Enter is pressed

    def __init__(self, parent: Optional[QWidget] = None,
                 placeholder_text: str = "Type to search...",
                 max_suggestions: int = 8):
        super().__init__(parent)

        # Properties
        self._placeholder_text = placeholder_text
        self._max_suggestions = max_suggestions
        self._text = ""
        self._header_text = ""
        self._description_text = ""

        # Suggestion configuration
        self._min_query_length = 1
        self._suggestion_delay = 200  # ms delay before showing suggestions
        self._fuzzy_matching = True
        self._case_sensitive = False

        # Data sources
        self._static_suggestions: List[FluentSuggestionItem] = []
        self._dynamic_source: Optional[Callable[[
            str], List[FluentSuggestionItem]]] = None

        # State
        self._is_suggestions_visible = False
        self._selected_index = -1
        self._current_suggestions: List[FluentSuggestionItem] = []

        # UI Elements (initialized in _setup_ui)
        self._main_layout: QVBoxLayout
        self._header_label: Optional[QLabel] = None
        self._input_container: QFrame
        self._input_field: QLineEdit
        self._suggestions_popup: QFrame
        self._suggestions_list: QListWidget
        self._description_label: Optional[QLabel] = None

        # Timers
        self._suggestion_timer = QTimer()
        self._suggestion_timer.setSingleShot(True)
        self._suggestion_timer.setInterval(self._suggestion_delay)
        self._suggestion_timer.timeout.connect(self._update_suggestions)

        # Animations
        self._popup_animation: Optional[QPropertyAnimation] = None

        # Setup
        self._setup_ui()
        self._connect_signals()

        # Setup style after everything else is initialized
        QTimer.singleShot(0, self._setup_style)

    def _setup_ui(self):
        """Setup the UI layout"""
        # Main vertical layout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(4)

        # Header label (optional)
        if self._header_text:
            self._header_label = QLabel(self._header_text)
            self._header_label.setFont(
                QFont("Segoe UI", 11, QFont.Weight.DemiBold))
            self._main_layout.addWidget(self._header_label)

        # Input container frame
        self._input_container = QFrame()
        self._input_container.setFrameStyle(QFrame.Shape.NoFrame)
        self._input_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        input_layout = QHBoxLayout(self._input_container)
        input_layout.setContentsMargins(12, 8, 12, 8)
        input_layout.setSpacing(8)

        # Input field
        self._input_field = QLineEdit()
        self._input_field.setPlaceholderText(self._placeholder_text)
        self._input_field.setFrame(False)
        self._input_field.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._input_field.setMinimumHeight(24)

        input_layout.addWidget(self._input_field)
        self._main_layout.addWidget(self._input_container)

        # Suggestions popup (initially hidden)
        self._setup_suggestions_popup()

        # Description label (optional)
        if self._description_text:
            self._description_label = QLabel(self._description_text)
            self._description_label.setFont(QFont("Segoe UI", 10))
            self._description_label.setWordWrap(True)
            self._main_layout.addWidget(self._description_label)

    def _setup_suggestions_popup(self):
        """Setup the suggestions popup list"""
        self._suggestions_popup = QFrame()
        self._suggestions_popup.setFrameStyle(QFrame.Shape.StyledPanel)
        self._suggestions_popup.setWindowFlags(Qt.WindowType.Popup)
        self._suggestions_popup.hide()

        popup_layout = QVBoxLayout(self._suggestions_popup)
        popup_layout.setContentsMargins(1, 1, 1, 1)
        popup_layout.setSpacing(0)

        # Suggestions list
        self._suggestions_list = QListWidget()
        self._suggestions_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._suggestions_list.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._suggestions_list.setMaximumHeight(
            200)  # Max height for the popup

        popup_layout.addWidget(self._suggestions_list)

    def _setup_style(self):
        """Apply Fluent Design styling"""
        theme = theme_manager

        # Input container style
        input_style = f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
            }}
            QFrame:hover {{
                border-color: {theme.get_color('primary').lighter(150).name()};
                background-color: {theme.get_color('accent_light').name()};
            }}
            QFrame:focus-within {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
            }}
        """

        # Input field style
        field_style = f"""
            QLineEdit {{
                background: transparent;
                border: none;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()}40;
            }}
            QLineEdit::placeholder {{
                color: {theme.get_color('text_secondary').name()};
            }}
        """

        # Suggestions popup style
        popup_style = f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
            }}
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
                font-size: 14px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border: none;
                color: {theme.get_color('text_primary').name()};
            }}
            QListWidget::item:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QListWidget::item:selected {{
                background-color: {theme.get_color('primary').name()};
                color: {theme.get_color('text_on_primary').name()};
            }}
        """

        self._input_container.setStyleSheet(input_style)
        self._input_field.setStyleSheet(field_style)
        self._suggestions_popup.setStyleSheet(popup_style)

        # Header and description styles
        if self._header_label:
            self._header_label.setStyleSheet(f"""
                QLabel {{ color: {theme.get_color('text_primary').name()}; }}
            """)

        if self._description_label:
            self._description_label.setStyleSheet(f"""
                QLabel {{ color: {theme.get_color('text_secondary').name()}; }}
            """)

    def _connect_signals(self):
        """Connect signals and slots"""
        # Input field signals
        self._input_field.textChanged.connect(self._on_text_changed)
        self._input_field.returnPressed.connect(self._on_query_submitted)

        # Install event filter for key navigation
        self._input_field.installEventFilter(self)

        # Suggestions list signals
        self._suggestions_list.itemClicked.connect(self._on_suggestion_clicked)

        # Theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self):
        """Handle theme changes"""
        self._setup_style()

    def _on_text_changed(self, text: str):
        """Handle text changes in input field"""
        self._text = text
        self.text_changed.emit(text)

        # Start suggestion timer
        if len(text) >= self._min_query_length:
            self._suggestion_timer.start()
        else:
            self._hide_suggestions()

    def _on_query_submitted(self):
        """Handle query submission (Enter pressed)"""
        if self._is_suggestions_visible and self._selected_index >= 0:
            # Select highlighted suggestion
            self._select_suggestion(self._selected_index)
        else:
            # Submit current query
            self.query_submitted.emit(self._text)
            self._hide_suggestions()

    def _on_suggestion_clicked(self, item: QListWidgetItem):
        """Handle suggestion item clicked"""
        index = self._suggestions_list.row(item)
        self._select_suggestion(index)

    def _update_suggestions(self):
        """Update and show suggestions based on current text"""
        query = self._text.strip()
        if len(query) < self._min_query_length:
            self._hide_suggestions()
            return

        # Collect suggestions from all sources
        suggestions = []

        # Static suggestions
        for item in self._static_suggestions:
            score = self._calculate_match_score(query, item.text)
            if score > 0:
                item.score = score
                suggestions.append(item)

        # Dynamic suggestions
        if self._dynamic_source:
            try:
                dynamic_suggestions = self._dynamic_source(query)
                for item in dynamic_suggestions:
                    if isinstance(item, str):
                        item = FluentSuggestionItem(item)
                    item.score = self._calculate_match_score(query, item.text)
                    if item.score > 0:
                        suggestions.append(item)
            except Exception:
                pass  # Ignore errors from dynamic source

        # Sort by score and limit results
        suggestions.sort(key=lambda x: x.score, reverse=True)
        suggestions = suggestions[:self._max_suggestions]

        self._current_suggestions = suggestions
        self._populate_suggestions_list()

        if suggestions:
            self._show_suggestions()
        else:
            self._hide_suggestions()

    def _calculate_match_score(self, query: str, text: str) -> float:
        """Calculate match score between query and text"""
        if not query or not text:
            return 0.0

        if not self._case_sensitive:
            query = query.lower()
            text = text.lower()

        # Exact match gets highest score
        if query == text:
            return 100.0

        # Starts with query gets high score
        if text.startswith(query):
            return 90.0 - (len(text) - len(query)) * 0.1

        # Contains query gets medium score
        if query in text:
            return 70.0 - text.index(query) * 0.5

        # Fuzzy matching
        if self._fuzzy_matching:
            return self._fuzzy_match_score(query, text)

        return 0.0

    def _fuzzy_match_score(self, query: str, text: str) -> float:
        """Calculate fuzzy match score"""
        if len(query) > len(text):
            return 0.0

        score = 0.0
        query_pos = 0

        for i, char in enumerate(text):
            if query_pos < len(query) and char == query[query_pos]:
                # Character match - higher score for earlier matches
                score += 10.0 * (1.0 - i / len(text))
                query_pos += 1

        # Bonus for matching all characters
        if query_pos == len(query):
            score += 20.0
        else:
            score *= query_pos / len(query)  # Partial match penalty

        return min(score, 60.0)  # Cap fuzzy score below exact matches

    def _populate_suggestions_list(self):
        """Populate the suggestions list widget"""
        self._suggestions_list.clear()

        for suggestion in self._current_suggestions:
            item = QListWidgetItem()
            item.setText(suggestion.text)

            if suggestion.icon:
                item.setIcon(suggestion.icon)

            self._suggestions_list.addItem(item)

        self._selected_index = -1

    def _show_suggestions(self):
        """Show the suggestions popup"""
        if self._is_suggestions_visible:
            return

        # Position popup below input field
        container_rect = self._input_container.geometry()
        global_pos = self._input_container.mapToGlobal(
            container_rect.bottomLeft())

        self._suggestions_popup.setFixedWidth(container_rect.width())
        self._suggestions_popup.move(global_pos)
        self._suggestions_popup.show()

        self._is_suggestions_visible = True

        # Animate popup appearance
        if self._popup_animation:
            if hasattr(self._popup_animation, 'stop'):
                self._popup_animation.stop()

        # Create animation with proper FluentTransition usage
        try:
            self._popup_animation = FluentTransition.create_transition(
                self._suggestions_popup,
                FluentTransition.FADE,
                150,
                FluentTransition.EASE_SMOOTH
            )
            if self._popup_animation:
                self._popup_animation.setStartValue(0.0)
                self._popup_animation.setEndValue(1.0)
                self._popup_animation.start()
        except Exception:
            # Fallback if animation fails
            self._suggestions_popup.setWindowOpacity(1.0)

    def _hide_suggestions(self):
        """Hide the suggestions popup"""
        if not self._is_suggestions_visible:
            return

        self._suggestions_popup.hide()
        self._is_suggestions_visible = False
        self._selected_index = -1

    def _select_suggestion(self, index: int):
        """Select and apply a suggestion"""
        if 0 <= index < len(self._current_suggestions):
            suggestion = self._current_suggestions[index]
            self._input_field.setText(suggestion.text)
            self._text = suggestion.text

            self.suggestion_selected.emit(suggestion.text, suggestion.data)
            self._hide_suggestions()

    def eventFilter(self, obj, event) -> bool:
        """Handle key events for navigation"""
        if obj == self._input_field and event.type() == event.Type.KeyPress:
            key_event = QKeyEvent(event)

            if self._is_suggestions_visible:
                if key_event.key() == Qt.Key.Key_Down:
                    self._navigate_suggestions(1)
                    return True
                elif key_event.key() == Qt.Key.Key_Up:
                    self._navigate_suggestions(-1)
                    return True
                elif key_event.key() == Qt.Key.Key_Escape:
                    self._hide_suggestions()
                    return True

        return super().eventFilter(obj, event)

    def _navigate_suggestions(self, direction: int):
        """Navigate through suggestions with arrow keys"""
        if not self._current_suggestions:
            return

        new_index = self._selected_index + direction

        # Wrap around navigation
        if new_index < 0:
            new_index = len(self._current_suggestions) - 1
        elif new_index >= len(self._current_suggestions):
            new_index = 0

        self._selected_index = new_index
        self._suggestions_list.setCurrentRow(new_index)

    # Public API

    def get_text(self) -> str:
        """Get the current text"""
        return self._text

    def set_text(self, text: str):
        """Set the text"""
        self._input_field.setText(text)
        self._text = text

    def clear(self):
        """Clear the input"""
        self.set_text("")
        self._hide_suggestions()

    def set_placeholder_text(self, text: str):
        """Set the placeholder text"""
        self._placeholder_text = text
        self._input_field.setPlaceholderText(text)

    def set_header_text(self, text: str):
        """Set the header text"""
        self._header_text = text
        if self._header_label:
            self._header_label.setText(text)
            self._header_label.setVisible(bool(text))

    def set_description_text(self, text: str):
        """Set the description text"""
        self._description_text = text
        if self._description_label:
            self._description_label.setText(text)
            self._description_label.setVisible(bool(text))

    def add_static_suggestions(self, suggestions: List[str]):
        """Add static suggestions"""
        for suggestion in suggestions:
            if isinstance(suggestion, str):
                self._static_suggestions.append(
                    FluentSuggestionItem(suggestion))
            else:
                self._static_suggestions.append(suggestion)

    def set_dynamic_source(self, source: Callable[[str], List[FluentSuggestionItem]]):
        """Set dynamic suggestion source function"""
        self._dynamic_source = source

    def set_max_suggestions(self, count: int):
        """Set maximum number of suggestions to show"""
        self._max_suggestions = max(1, count)

    def set_min_query_length(self, length: int):
        """Set minimum query length before showing suggestions"""
        self._min_query_length = max(0, length)

    def set_fuzzy_matching(self, enabled: bool):
        """Enable or disable fuzzy matching"""
        self._fuzzy_matching = enabled

    def set_case_sensitive(self, sensitive: bool):
        """Set case sensitivity for matching"""
        self._case_sensitive = sensitive


# Export classes
__all__ = [
    'FluentAutoSuggestBox',
    'FluentSuggestionItem'
]
