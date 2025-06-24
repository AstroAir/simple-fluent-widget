"""
Enhanced Masked Input and Rich Text Editor for Fluent Design

Modern implementation using latest Python features and PySide6 best practices.
Includes dataclasses, enums, protocols, type hints, and performance optimizations.
"""

import re
from dataclasses import dataclass
from enum import Enum, auto
from functools import lru_cache
from contextlib import contextmanager
from typing import (Protocol, Optional, Dict,
                    Union, TypeAlias, Final, Callable)

from PySide6.QtWidgets import (QWidget, QLabel, QLineEdit,
                               QTextEdit, QToolBar,
                               QColorDialog, QFontComboBox, QComboBox, QDialog)
from PySide6.QtCore import (Qt, Signal, QRegularExpression, QTimer)
from PySide6.QtGui import (QAction, QTextCharFormat, QFont, QColor,
                           QRegularExpressionValidator, QTextListFormat, QTextBlockFormat)

from core.theme import theme_manager
from core.enhanced_base import FluentLayoutBuilder, FluentStandardButton
from core.enhanced_animations import get_theme_aware_animation


# Type aliases for better readability
TextFormat: TypeAlias = Union[QTextCharFormat,
                              QTextListFormat, QTextBlockFormat]
FormatAction: TypeAlias = Callable[[], None]


class MaskType(Enum):
    """Enumeration of common mask types"""
    DATE = "00/00/0000"
    TIME = "00:00"
    DATETIME = "00/00/0000 00:00"
    PHONE_US = "(000) 000-0000"
    PHONE_INTL = "+00 000 000 0000"
    SSN = "000-00-0000"
    IP_ADDRESS = "000.000.000.000"
    CREDIT_CARD = "0000 0000 0000 0000"


class FormattingAction(Enum):
    """Enumeration of text formatting actions"""
    BOLD = auto()
    ITALIC = auto()
    UNDERLINE = auto()
    STRIKETHROUGH = auto()
    ALIGN_LEFT = auto()
    ALIGN_CENTER = auto()
    ALIGN_RIGHT = auto()
    ALIGN_JUSTIFY = auto()
    BULLET_LIST = auto()
    NUMBER_LIST = auto()
    INCREASE_INDENT = auto()
    DECREASE_INDENT = auto()


@dataclass(frozen=True)
class MaskCharacter:
    """Configuration for mask characters"""
    char: str
    pattern: str


@dataclass
class EditorConfig:
    """Configuration for rich text editor"""
    enable_toolbar: bool = True
    toolbar_height: int = 40
    enable_animations: bool = True
    animation_duration: int = 250
    auto_save_interval: int = 5000  # milliseconds
    max_undo_steps: int = 100


@dataclass
class ValidationState:
    """Mask input validation state"""
    is_valid: bool = True
    error_message: str = ""
    completion_percentage: float = 0.0


class MaskInputTheme(Protocol):
    """Protocol for theme management in mask input"""

    def get_color(self, name: str) -> QColor: ...
    def theme_changed(self) -> Signal: ...


class TextEditorTheme(Protocol):
    """Protocol for theme management in rich text editor"""

    def get_color(self, name: str) -> QColor: ...
    def theme_changed(self) -> Signal: ...


class OptimizedFluentMaskedInput(QLineEdit):
    """Optimized Fluent Design Masked Input Field with modern Python features

    Features:
    - Modern dataclass-based configuration
    - Enum-based mask types for better type safety
    - Performance optimizations with caching
    - Enhanced validation with Protocol typing
    - Context manager for batch operations
    """

    # Predefined mask patterns using Enum
    _mask_patterns: Final[Dict[str, str]] = {
        "0": r"[0-9]",         # Digit
        "9": r"[0-9 ]",        # Digit or space
        "#": r"[0-9+-]",       # Digit or sign
        "A": r"[A-Za-z]",      # Letter
        "a": r"[A-Za-z ]",     # Letter or space
        "N": r"[A-Za-z0-9]",   # Alphanumeric
        "X": r"[A-Fa-f0-9]",   # Hex
        "&": r"."              # Any character
    }

    valueChanged = Signal(str)  # Emitted when value changes and is valid
    # Emitted when validation state changes
    validationChanged = Signal(ValidationState)

    def __init__(self, parent: Optional[QWidget] = None,
                 mask_type: Optional[MaskType] = None,
                 custom_mask: str = "",
                 placeholder: str = ""):
        super().__init__(parent)

        self._mask_type = mask_type
        self._custom_mask = custom_mask
        self._placeholder = placeholder
        self._prompt_char = "_"
        self._validation_state = ValidationState()
        self._theme_animation = get_theme_aware_animation()

        # Cache for compiled regex patterns
        self._pattern_cache: Dict[str, re.Pattern] = {}

        # Setup mask
        if mask_type:
            self.set_mask_type(mask_type)
        elif custom_mask:
            self.set_custom_mask(custom_mask)

        # Set placeholder text
        if placeholder:
            self.setPlaceholderText(placeholder)

        # Apply styling
        self._apply_modern_style()

        # Connect signals
        self.textChanged.connect(self._on_text_changed)
        theme_manager.theme_changed.connect(self._apply_modern_style)

    def _apply_modern_style(self):
        """Apply modern styling with theme integration"""
        theme = theme_manager

        # Create theme-aware color animation for focus
        if hasattr(self, '_focus_animation'):
            self._focus_animation.stop()

        self._focus_animation = self._theme_animation.create_theme_aware_color_animation(
            self, "styleSheet", "primary", duration=200
        )

        style_sheet = f"""
            OptimizedFluentMaskedInput {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
                selection-background-color: {theme.get_color('primary').name()}30;
            }}
            
            OptimizedFluentMaskedInput:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
                padding: 9px 13px;
                box-shadow: 0 0 0 3px {theme.get_color('primary').name()}20;
            }}
            
            OptimizedFluentMaskedInput:disabled {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_disabled').name()};
                border-color: {theme.get_color('border').darker(120).name()};
            }}
            
            OptimizedFluentMaskedInput:hover:!focus {{
                border-color: {theme.get_color('primary').lighter(120).name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def set_mask_type(self, mask_type: MaskType):
        """Set mask using predefined type with enum safety

        Args:
            mask_type: MaskType enum value
        """
        self._mask_type = mask_type
        self._custom_mask = ""
        self.setInputMask(mask_type.value)
        self.setCursorPosition(0)
        self._validate_current_input()

    def set_custom_mask(self, mask: str, prompt_char: str = "_"):
        """Set custom input mask with validation

        Args:
            mask: Mask pattern using Qt's input mask format
            prompt_char: Character to show for empty positions
        """
        self._custom_mask = mask
        self._mask_type = None
        self._prompt_char = prompt_char
        self.setInputMask(mask)
        self.setCursorPosition(0)
        self._validate_current_input()

    @lru_cache(maxsize=32)
    def _get_compiled_pattern(self, pattern: str) -> re.Pattern:
        """Get compiled regex pattern with caching for performance

        Args:
            pattern: Regular expression pattern

        Returns:
            Compiled regex pattern
        """
        return re.compile(pattern)

    def set_validation_pattern(self, pattern: str, input_mask: str = ""):
        """Set validation using a regex pattern with caching

        Args:
            pattern: Regular expression pattern
            input_mask: Optional Qt input mask for visual cues
        """
        if input_mask:
            self.setInputMask(input_mask)

        # Use cached compiled pattern
        compiled_pattern = self._get_compiled_pattern(pattern)
        validator = QRegularExpressionValidator(
            QRegularExpression(pattern), self)
        self.setValidator(validator)

    def _on_text_changed(self, text: str):
        """Handle text changes with validation and state updates"""
        self._validate_current_input()

        # Only emit valueChanged if the text is valid
        if self._validation_state.is_valid and text != self.inputMask():
            self.valueChanged.emit(self.get_unmasked_value())

    def _validate_current_input(self):
        """Validate current input and update state"""
        text = self.text()
        input_mask = self.inputMask()

        if not input_mask:
            # No mask validation
            self._validation_state = ValidationState(
                is_valid=True, completion_percentage=1.0)
        else:
            # Calculate completion percentage
            total_chars = len(
                [c for c in input_mask if c in self._mask_patterns])
            filled_chars = len([c for c in text if c.isalnum()])
            completion = filled_chars / total_chars if total_chars > 0 else 0.0

            is_valid = self.hasAcceptableInput() and completion == 1.0

            self._validation_state = ValidationState(
                is_valid=is_valid,
                completion_percentage=completion,
                error_message="" if is_valid else "Input incomplete or invalid"
            )

        self.validationChanged.emit(self._validation_state)

    def get_unmasked_value(self) -> str:
        """Get the value without mask characters using optimized approach

        Returns:
            Text with only the user input, no mask characters
        """
        text = self.text()

        # Use cached regex for better performance
        if self._custom_mask or self._mask_type:
            # Remove non-alphanumeric characters efficiently
            return ''.join(c for c in text if c.isalnum())

        return text

    @property
    def validation_state(self) -> ValidationState:
        """Get current validation state"""
        return self._validation_state

    @contextmanager
    def batch_update(self):
        """Context manager for batch updates to improve performance"""
        self.blockSignals(True)
        try:
            yield
        finally:
            self.blockSignals(False)
            self._validate_current_input()


# Legacy alias for backward compatibility
class FluentMaskedInput(OptimizedFluentMaskedInput):
    """Legacy alias for backward compatibility"""

    # Expose old Masks class for compatibility
    class Masks:
        DATE = "00/00/0000"
        TIME = "00:00"
        DATETIME = "00/00/0000 00:00"
        PHONE_US = "(000) 000-0000"
        PHONE_INTL = "+00 000 000 0000"
        SSN = "000-00-0000"
        IP_ADDRESS = "000.000.000.000"
        CREDIT_CARD = "0000 0000 0000 0000"

    def set_preset_mask(self, preset_name: str):
        """Set a preset mask (legacy method)

        Args:
            preset_name: Name of the preset from Masks class
        """
        if not hasattr(self.Masks, preset_name):
            return

        preset_mask = getattr(self.Masks, preset_name)
        self.set_custom_mask(preset_mask)


class OptimizedFluentRichTextEditor(QWidget):
    """Optimized Fluent Design Rich Text Editor with modern Python features

    Features:
    - Modern dataclass-based configuration
    - Enum-based formatting actions for type safety
    - Performance optimizations with caching
    - Enhanced animations using theme-aware system
    - Protocol-based theme integration
    - Context managers for batch operations
    """

    # Signals
    textChanged = Signal()
    formattingChanged = Signal(FormattingAction)
    selectionChanged = Signal(str)  # Selected text

    def __init__(self, parent: Optional[QWidget] = None, config: Optional[EditorConfig] = None):
        super().__init__(parent)

        self._config = config or EditorConfig()
        self._theme_animation = get_theme_aware_animation()
        self._active_formats: set[FormattingAction] = set()
        self._format_cache: Dict[str, QTextCharFormat] = {}

        # Auto-save timer
        self._auto_save_timer = QTimer()
        self._auto_save_timer.timeout.connect(self._auto_save)
        if self._config.auto_save_interval > 0:
            self._auto_save_timer.start(self._config.auto_save_interval)

        # Setup UI using FluentLayoutBuilder
        self._setup_modern_ui()
        self._setup_actions()
        self._setup_connections()        # Apply styling
        self._apply_modern_style()
        theme_manager.theme_changed.connect(self._apply_modern_style)

    def _setup_modern_ui(self):
        """Setup UI using modern FluentLayoutBuilder"""
        # Main layout
        main_layout = FluentLayoutBuilder.create_vertical_layout(spacing=0)
        self.setLayout(main_layout)

        # Create toolbar if enabled
        if self._config.enable_toolbar:
            self._toolbar = QToolBar(self)
            self._toolbar.setFixedHeight(self._config.toolbar_height)
            self._toolbar.setMovable(False)
            self._toolbar.setFloatable(False)
            main_layout.addWidget(self._toolbar)

        # Create text edit
        self._text_edit = QTextEdit(self)
        self._text_edit.setUndoRedoEnabled(True)

        # Set maximum undo steps
        document = self._text_edit.document()
        document.setMaximumBlockCount(self._config.max_undo_steps)

        self._text_edit.textChanged.connect(self.textChanged)
        self._text_edit.selectionChanged.connect(self._on_selection_changed)

        main_layout.addWidget(self._text_edit)

        # Set minimum size
        self.setMinimumSize(300, 200)

    def _setup_actions(self):
        """Setup formatting actions using modern approach"""
        if not self._config.enable_toolbar:
            return

        # Text style actions with enum mapping
        self._actions: Dict[FormattingAction, QAction] = {}

        # Bold action
        bold_action = QAction("Bold", self)
        bold_action.setCheckable(True)
        bold_action.setShortcut("Ctrl+B")
        bold_action.triggered.connect(
            lambda: self._apply_formatting(FormattingAction.BOLD))
        self._actions[FormattingAction.BOLD] = bold_action
        self._toolbar.addAction(bold_action)

        # Italic action
        italic_action = QAction("Italic", self)
        italic_action.setCheckable(True)
        italic_action.setShortcut("Ctrl+I")
        italic_action.triggered.connect(
            lambda: self._apply_formatting(FormattingAction.ITALIC))
        self._actions[FormattingAction.ITALIC] = italic_action
        self._toolbar.addAction(italic_action)

        # Underline action
        underline_action = QAction("Underline", self)
        underline_action.setCheckable(True)
        underline_action.setShortcut("Ctrl+U")
        underline_action.triggered.connect(
            lambda: self._apply_formatting(FormattingAction.UNDERLINE))
        self._actions[FormattingAction.UNDERLINE] = underline_action
        self._toolbar.addAction(underline_action)

        self._toolbar.addSeparator()

        # Font family combo box
        self._font_combobox = QFontComboBox(self)
        self._font_combobox.currentFontChanged.connect(
            self._format_font_family)
        self._toolbar.addWidget(self._font_combobox)

        # Font size combo box
        self._font_size_combobox = QComboBox(self)
        font_sizes = ["8", "9", "10", "11", "12", "14", "16",
                      "18", "20", "22", "24", "28", "36", "48", "72"]
        self._font_size_combobox.addItems(font_sizes)
        self._font_size_combobox.setCurrentIndex(4)  # Default to 12pt
        self._font_size_combobox.currentTextChanged.connect(
            self._format_font_size)
        self._toolbar.addWidget(self._font_size_combobox)

        self._toolbar.addSeparator()

        # Alignment actions
        for action_type, alignment in [
            (FormattingAction.ALIGN_LEFT, Qt.AlignmentFlag.AlignLeft),
            (FormattingAction.ALIGN_CENTER, Qt.AlignmentFlag.AlignHCenter),
            (FormattingAction.ALIGN_RIGHT, Qt.AlignmentFlag.AlignRight),
            (FormattingAction.ALIGN_JUSTIFY, Qt.AlignmentFlag.AlignJustify),
        ]:
            action = QAction(action_type.name.replace('_', ' ').title(), self)
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked, a=alignment: self._format_alignment(a))
            self._actions[action_type] = action
            self._toolbar.addAction(action)

        self._toolbar.addSeparator()

        # List actions
        bullet_action = QAction("Bullet List", self)
        bullet_action.setCheckable(True)
        bullet_action.triggered.connect(
            lambda: self._apply_formatting(FormattingAction.BULLET_LIST))
        self._actions[FormattingAction.BULLET_LIST] = bullet_action
        self._toolbar.addAction(bullet_action)

        number_action = QAction("Number List", self)
        number_action.setCheckable(True)
        number_action.triggered.connect(
            lambda: self._apply_formatting(FormattingAction.NUMBER_LIST))
        self._actions[FormattingAction.NUMBER_LIST] = number_action
        self._toolbar.addAction(number_action)

        self._toolbar.addSeparator()

        # Color and link actions
        color_action = QAction("Text Color", self)
        color_action.triggered.connect(self._format_text_color)
        self._toolbar.addAction(color_action)

        link_action = QAction("Insert Link", self)
        link_action.triggered.connect(self._insert_link)
        self._toolbar.addAction(link_action)

    def _setup_connections(self):
        """Setup signal connections"""
        # Update action states when cursor position changes
        self._text_edit.cursorPositionChanged.connect(
            self._update_action_states)

        # Auto-save connection
        if self._config.auto_save_interval > 0:
            self._text_edit.textChanged.connect(self._reset_auto_save_timer)

    def _apply_modern_style(self):
        """Apply modern styling with theme integration"""
        theme = theme_manager

        # Style the toolbar
        if hasattr(self, '_toolbar'):
            toolbar_style = f"""
                QToolBar {{
                    background-color: {theme.get_color('surface').name()};
                    border-bottom: 1px solid {theme.get_color('border').name()};
                    padding: 6px;
                    spacing: 4px;
                }}
                
                QToolButton {{
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 6px;
                    padding: 6px;
                    min-width: 32px;
                    min-height: 32px;
                }}
                
                QToolButton:hover {{
                    background-color: {theme.get_color('accent_light').name()};
                    border-color: {theme.get_color('border').name()};
                }}
                
                QToolButton:checked {{
                    background-color: {theme.get_color('accent_medium').name()};
                    border-color: {theme.get_color('primary').name()};
                    color: {theme.get_color('primary').name()};
                }}
            """
            self._toolbar.setStyleSheet(toolbar_style)

        # Style the text edit
        textedit_style = f"""
            QTextEdit {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-top: none;
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
                selection-background-color: {theme.get_color('primary').name()}30;
                padding: 12px;
            }}
            
            QTextEdit:focus {{
                border-color: {theme.get_color('primary').name()};
                outline: none;
            }}
        """
        self._text_edit.setStyleSheet(textedit_style)

        # Style combo boxes
        if hasattr(self, '_font_combobox'):
            combobox_style = f"""
                QComboBox {{
                    background-color: {theme.get_color('surface').name()};
                    color: {theme.get_color('text_primary').name()};
                    border: 1px solid {theme.get_color('border').name()};
                    border-radius: 4px;
                    padding: 4px 8px;
                    min-height: 24px;
                    min-width: 100px;
                }}
                
                QComboBox::drop-down {{
                    border: none;
                    width: 20px;
                }}
                
                QComboBox QAbstractItemView {{
                    background-color: {theme.get_color('surface').name()};
                    color: {theme.get_color('text_primary').name()};
                    border: 1px solid {theme.get_color('border').name()};
                    selection-background-color: {theme.get_color('primary').name()}30;
                    selection-color: {theme.get_color('text_primary').name()};
                    outline: none;
                }}
            """
            self._font_combobox.setStyleSheet(combobox_style)
            self._font_size_combobox.setStyleSheet(combobox_style)

    @lru_cache(maxsize=64)
    def _get_cached_format(self, format_key: str) -> QTextCharFormat:
        """Get cached text format for performance"""
        fmt = QTextCharFormat()

        if "bold" in format_key:
            fmt.setFontWeight(QFont.Weight.Bold)
        if "italic" in format_key:
            fmt.setFontItalic(True)
        if "underline" in format_key:
            fmt.setFontUnderline(True)

        return fmt

    def _apply_formatting(self, action: FormattingAction):
        """Apply formatting using enum-based approach with caching"""
        cursor = self._text_edit.textCursor()

        # Create or get cached format
        format_key = action.name.lower()

        if action == FormattingAction.BOLD:
            fmt = QTextCharFormat()
            is_bold = action in self._active_formats
            fmt.setFontWeight(
                QFont.Weight.Normal if is_bold else QFont.Weight.Bold)
            self._merge_format_with_animation(fmt)

        elif action == FormattingAction.ITALIC:
            fmt = QTextCharFormat()
            is_italic = action in self._active_formats
            fmt.setFontItalic(not is_italic)
            self._merge_format_with_animation(fmt)

        elif action == FormattingAction.UNDERLINE:
            fmt = QTextCharFormat()
            is_underlined = action in self._active_formats
            fmt.setFontUnderline(not is_underlined)
            self._merge_format_with_animation(fmt)

        elif action == FormattingAction.BULLET_LIST:
            self._format_bullet_list()

        elif action == FormattingAction.NUMBER_LIST:
            self._format_number_list()        # Update active formats
        if action in self._active_formats:
            self._active_formats.remove(action)
        else:
            self._active_formats.add(action)

        # Update UI state
        self._update_action_states()
        self.formattingChanged.emit(action)

    def _merge_format_with_animation(self, fmt: QTextCharFormat):
        """Apply formatting with subtle animation"""
        cursor = self._text_edit.textCursor()

        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)
            # Simple opacity animation for feedback
            if self._config.enable_animations:
                self._create_format_feedback_animation()
        else:
            self._text_edit.mergeCurrentCharFormat(fmt)

    def _create_format_feedback_animation(self):
        """Create subtle feedback animation for formatting changes"""
        if not self._config.enable_animations:
            return

        # Create theme-aware animation for feedback
        animation = self._theme_animation.create_theme_aware_color_animation(
            self._text_edit, "styleSheet", "accent_light", duration=150
        )
        animation.start()

    def _format_font_family(self, font: QFont):
        """Set font family with caching"""
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family())
        self._merge_format_with_animation(fmt)

    def _format_font_size(self, size: str):
        """Set font size with validation"""
        try:
            size_value = float(size)
            fmt = QTextCharFormat()
            fmt.setFontPointSize(size_value)
            self._merge_format_with_animation(fmt)
        except ValueError:
            pass  # Invalid size, ignore

    def _format_alignment(self, alignment: Qt.AlignmentFlag):
        """Set paragraph alignment"""
        self._text_edit.setAlignment(alignment)
        self._create_format_feedback_animation()

    def _format_text_color(self):
        """Change text color with validation"""
        color = QColorDialog.getColor(
            self._text_edit.textColor(),
            self,
            "Select Text Color"
        )

        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self._merge_format_with_animation(fmt)

    def _format_bullet_list(self):
        """Toggle bullet list with optimized approach"""
        cursor = self._text_edit.textCursor()
        list_format = QTextListFormat()

        is_bullet_active = FormattingAction.BULLET_LIST in self._active_formats

        if not is_bullet_active:
            list_format.setStyle(QTextListFormat.Style.ListDisc)
            list_format.setIndent(1)
            cursor.createList(list_format)
        else:
            current_list = cursor.currentList()
            if current_list:
                current_list.removeItem(cursor.blockNumber())

        self._create_format_feedback_animation()

    def _format_number_list(self):
        """Toggle numbered list with optimized approach"""
        cursor = self._text_edit.textCursor()
        list_format = QTextListFormat()

        is_number_active = FormattingAction.NUMBER_LIST in self._active_formats

        if not is_number_active:
            list_format.setStyle(QTextListFormat.Style.ListDecimal)
            list_format.setIndent(1)
            cursor.createList(list_format)
        else:
            current_list = cursor.currentList()
            if current_list:
                current_list.removeItem(cursor.blockNumber())

        self._create_format_feedback_animation()

    def _insert_link(self):
        """Insert hyperlink using modern dialog"""
        cursor = self._text_edit.textCursor()
        selected_text = cursor.selectedText()

        dialog = OptimizedFluentLinkDialog(self, initial_text=selected_text)

        if dialog.exec():
            link_data = dialog.get_link_data()
            cursor.insertHtml(
                f'<a href="{link_data["url"]}">{link_data["text"]}</a>')
            self._create_format_feedback_animation()

    def _update_action_states(self):
        """Update action states based on current cursor position"""
        if not self._config.enable_toolbar:
            return

        cursor = self._text_edit.textCursor()
        format = cursor.charFormat()

        # Update bold state
        if FormattingAction.BOLD in self._actions:
            is_bold = format.fontWeight() == QFont.Weight.Bold
            self._actions[FormattingAction.BOLD].setChecked(is_bold)

        # Update italic state
        if FormattingAction.ITALIC in self._actions:
            self._actions[FormattingAction.ITALIC].setChecked(
                format.fontItalic())

        # Update underline state
        if FormattingAction.UNDERLINE in self._actions:
            self._actions[FormattingAction.UNDERLINE].setChecked(
                format.fontUnderline())

        # Update font selections
        if hasattr(self, '_font_combobox'):
            with self._batch_update():
                font_family = format.fontFamily()
                if font_family:
                    self._font_combobox.setCurrentFont(QFont(font_family))

                font_size = format.fontPointSize()
                if font_size > 0:
                    size_index = self._font_size_combobox.findText(
                        str(int(font_size)))
                    if size_index >= 0:
                        self._font_size_combobox.setCurrentIndex(size_index)

    def _on_selection_changed(self):
        """Handle selection change"""
        cursor = self._text_edit.textCursor()
        selected_text = cursor.selectedText()
        self.selectionChanged.emit(selected_text)
        self._update_action_states()

    @contextmanager
    def _batch_update(self):
        """Context manager for batch updates"""
        self.blockSignals(True)
        try:
            yield
        finally:
            self.blockSignals(False)

    def _reset_auto_save_timer(self):
        """Reset auto-save timer when text changes"""
        if self._config.auto_save_interval > 0:
            self._auto_save_timer.start(self._config.auto_save_interval)

    def _auto_save(self):
        """Auto-save functionality (override in subclasses)"""
        # Default implementation does nothing
        # Subclasses can override to implement actual saving
        pass

    # Public API methods
    def set_html(self, html: str):
        """Set HTML content"""
        self._text_edit.setHtml(html)

    def get_html(self) -> str:
        """Get content as HTML"""
        return self._text_edit.toHtml()

    def set_plain_text(self, text: str):
        """Set plain text content"""
        self._text_edit.setPlainText(text)

    def get_plain_text(self) -> str:
        """Get content as plain text"""
        return self._text_edit.toPlainText()

    def clear(self):
        """Clear all content"""
        self._text_edit.clear()
        self._active_formats.clear()
        self._format_cache.clear()

    @property
    def config(self) -> EditorConfig:
        """Get editor configuration"""
        return self._config


# Legacy alias for backward compatibility
class FluentRichTextEditor(OptimizedFluentRichTextEditor):
    """Legacy alias for backward compatibility"""
    pass


class OptimizedFluentLinkDialog(QDialog):
    """Optimized dialog for inserting links in rich text editor with modern features"""

    def __init__(self, parent: Optional[QWidget] = None,
                 initial_text: str = "", initial_url: str = ""):
        super().__init__(parent)

        self._setup_ui()
        self._setup_appearance()
        self._setup_validation()

        # Set initial values
        if initial_text:
            self._text_edit.setText(initial_text)
        if initial_url:
            self._url_edit.setText(initial_url)

        # Update button state
        self._update_ok_button_state()

    def _setup_ui(self):
        """Setup dialog UI using modern layout"""
        self.setWindowTitle("Insert Link")
        self.setModal(True)
        self.resize(500, 180)

        # Use FluentLayoutBuilder for consistent styling
        main_layout = FluentLayoutBuilder.create_vertical_layout(
            spacing=16, margins=(20, 20, 20, 20))
        self.setLayout(main_layout)

        # Text input with improved layout
        text_container, text_form_layout = FluentLayoutBuilder.create_form_layout(
            label_width=60)
        text_label = QLabel("Text:")
        self._text_edit = QLineEdit(self)
        self._text_edit.setPlaceholderText("Link text (e.g., 'Click here')")
        text_form_layout.addWidget(text_label, 0, 0)
        text_form_layout.addWidget(self._text_edit, 0, 1)
        main_layout.addWidget(text_container)

        # URL input with improved layout
        url_container, url_form_layout = FluentLayoutBuilder.create_form_layout(
            label_width=60)
        url_label = QLabel("URL:")
        self._url_edit = QLineEdit(self)
        self._url_edit.setPlaceholderText("https://example.com")
        url_form_layout.addWidget(url_label, 0, 0)
        url_form_layout.addWidget(self._url_edit, 0, 1)
        # Buttons with proper spacing
        main_layout.addWidget(url_container)
        button_layout = FluentLayoutBuilder.create_horizontal_layout()
        button_layout.addStretch()

        self._ok_button = FluentStandardButton(
            "OK", variant=FluentStandardButton.PRIMARY)
        self._ok_button.clicked.connect(self._on_ok_clicked)
        self._cancel_button = FluentStandardButton("Cancel")
        self._cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self._cancel_button)
        button_layout.addWidget(self._ok_button)
        main_layout.addLayout(button_layout)

    def _setup_validation(self):
        """Setup input validation"""
        # Connect text change signals to update validation
        self._text_edit.textChanged.connect(self._update_ok_button_state)
        self._url_edit.textChanged.connect(self._update_ok_button_state)

        # Set up URL validation pattern
        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$|^[^\s/$.?#].[^\s]*$"
        self._url_validator = QRegularExpressionValidator(
            QRegularExpression(url_pattern))
        self._url_edit.setValidator(self._url_validator)

    def _update_ok_button_state(self):
        """Update OK button state based on input validation"""
        text_valid = bool(self._text_edit.text().strip())
        url_valid = bool(self._url_edit.text().strip())

        # Enable OK button only if both fields have content
        self._ok_button.setEnabled(text_valid and url_valid)

    def _on_ok_clicked(self):
        """Handle OK button click with validation"""
        url_text = self._url_edit.text().strip()

        # Auto-add protocol if missing
        if url_text and not url_text.startswith(('http://', 'https://')):
            url_text = 'https://' + url_text
            self._url_edit.setText(url_text)

        self.accept()

    def _setup_appearance(self):
        """Setup dialog appearance with modern styling"""
        theme = theme_manager

        style_sheet = f"""
            OptimizedFluentLinkDialog {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
            }}
            
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                font-weight: 500;
                font-size: 14px;
            }}
            
            QLineEdit {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
            }}
            
            QLineEdit:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
                padding: 7px 11px;
                outline: none;
            }}
            
            QLineEdit:invalid {{
                border-color: {theme.get_color('error', '#ff4444').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def get_link_data(self) -> Dict[str, str]:
        """Get the entered link data with validation"""
        url_text = self._url_edit.text().strip()

        # Ensure URL has protocol
        if url_text and not url_text.startswith(('http://', 'https://')):
            url_text = 'https://' + url_text

        return {
            'text': self._text_edit.text().strip(),
            'url': url_text
        }


# Legacy alias for backward compatibility
class FluentLinkDialog(OptimizedFluentLinkDialog):
    """Legacy alias for backward compatibility"""
    pass
