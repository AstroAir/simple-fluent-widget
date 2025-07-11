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

    # Predefined mask patterns using Enum, mapping mask characters to regex patterns
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

    # Signals emitted by the widget
    valueChanged = Signal(str)  # Emitted when value changes and is valid
    validationChanged = Signal(ValidationState)  # Emitted when validation state changes

    def __init__(self, parent: Optional[QWidget] = None,
                 mask_type: Optional[MaskType] = None,
                 custom_mask: str = "",
                 placeholder: str = ""):
        super().__init__(parent)

        # Store configuration and state
        self._mask_type = mask_type
        self._custom_mask = custom_mask
        self._placeholder = placeholder
        self._prompt_char = "_"  # Default prompt character for the mask
        self._validation_state = ValidationState()
        self._theme_animation = get_theme_aware_animation() # Animation helper

        # Cache for compiled regex patterns used in validation
        self._pattern_cache: Dict[str, re.Pattern] = {}

        # Setup the input mask based on provided type or custom string
        if mask_type:
            self.set_mask_type(mask_type)
        elif custom_mask:
            self.set_custom_mask(custom_mask)

        # Set placeholder text if provided
        if placeholder:
            self.setPlaceholderText(placeholder)

        # Apply initial styling and connect theme change signal
        self._apply_modern_style()

        # Connect signals for text changes and theme updates
        self.textChanged.connect(self._on_text_changed)
        theme_manager.theme_changed.connect(self._apply_modern_style)

    def _apply_modern_style(self):
        """Apply modern styling with theme integration"""
        theme = theme_manager

        # Stop any existing focus animation before creating a new one
        if hasattr(self, '_focus_animation'):
            self._focus_animation.stop()

        # Create a theme-aware color animation for the border on focus
        self._focus_animation = self._theme_animation.create_theme_aware_color_animation(
            self, "styleSheet", "primary", duration=200
        )

        # Define the stylesheet using theme colors
        style_sheet = f"""
            OptimizedFluentMaskedInput {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
                selection-background-color: {theme.get_color('primary').name()}30; /* Semi-transparent primary color */
            }}

            OptimizedFluentMaskedInput:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
                padding: 9px 13px; /* Adjust padding to keep size consistent with wider border */
                box-shadow: 0 0 0 3px {theme.get_color('primary').name()}20; /* Subtle focus ring */
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
        self._custom_mask = "" # Clear custom mask if type is set
        self.setInputMask(mask_type.value) # Apply the Qt input mask string
        self.setCursorPosition(0) # Move cursor to the beginning
        self._validate_current_input() # Validate the initial state

    def set_custom_mask(self, mask: str, prompt_char: str = "_"):
        """Set custom input mask with validation

        Args:
            mask: Mask pattern using Qt's input mask format
            prompt_char: Character to show for empty positions
        """
        self._custom_mask = mask
        self._mask_type = None # Clear mask type if custom mask is set
        self._prompt_char = prompt_char
        self.setInputMask(mask) # Apply the custom Qt input mask
        self.setCursorPosition(0) # Move cursor to the beginning
        self._validate_current_input() # Validate the initial state

    @lru_cache(maxsize=32)
    def _get_compiled_pattern(self, pattern: str) -> re.Pattern:
        """Get compiled regex pattern with caching for performance

        Args:
            pattern: Regular expression pattern

        Returns:
            Compiled regex pattern
        """
        # Compile regex patterns and cache them for repeated use
        return re.compile(pattern)

    def set_validation_pattern(self, pattern: str, input_mask: str = ""):
        """Set validation using a regex pattern with caching

        Args:
            pattern: Regular expression pattern
            input_mask: Optional Qt input mask for visual cues
        """
        if input_mask:
            self.setInputMask(input_mask)

        # Create a QRegularExpressionValidator with the compiled pattern
        validator = QRegularExpressionValidator(
            QRegularExpression(pattern), self)
        self.setValidator(validator)

    def _on_text_changed(self, text: str):
        """Handle text changes with validation and state updates"""
        # Re-validate the input whenever the text changes
        self._validate_current_input()

        # Only emit valueChanged signal if the current text is valid and not just the mask itself
        if self._validation_state.is_valid and text != self.inputMask():
            self.valueChanged.emit(self.get_unmasked_value())

    def _validate_current_input(self):
        """Validate current input and update state"""
        text = self.text()
        input_mask = self.inputMask()

        if not input_mask:
            # If no mask is set, the input is always considered valid and complete
            self._validation_state = ValidationState(
                is_valid=True, completion_percentage=1.0)
        else:
            # Calculate completion percentage based on filled mask characters
            total_chars = len(
                [c for c in input_mask if c in self._mask_patterns]) # Count mask placeholder characters
            filled_chars = len([c for c in text if c.isalnum()]) # Count alphanumeric characters entered by user
            completion = filled_chars / total_chars if total_chars > 0 else 0.0 # Calculate percentage

            # Check if the input is acceptable according to the mask and fully complete
            is_valid = self.hasAcceptableInput() and completion == 1.0

            # Update the internal validation state
            self._validation_state = ValidationState(
                is_valid=is_valid,
                completion_percentage=completion,
                error_message="" if is_valid else "Input incomplete or invalid" # Set error message if invalid
            )

        # Emit the validationChanged signal with the updated state
        self.validationChanged.emit(self._validation_state)

    def get_unmasked_value(self) -> str:
        """Get the value without mask characters using optimized approach

        Returns:
            Text with only the user input, no mask characters
        """
        text = self.text()

        # If a mask is applied, remove non-alphanumeric characters (which are typically mask literals)
        if self._custom_mask or self._mask_type:
            return ''.join(c for c in text if c.isalnum())

        # If no mask, return the raw text
        return text

    @property
    def validation_state(self) -> ValidationState:
        """Get current validation state"""
        return self._validation_state

    @contextmanager
    def batch_update(self):
        """Context manager for batch updates to improve performance

        Blocks signals during the 'with' block and unblocks/validates afterwards.
        """
        self.blockSignals(True) # Block signals to prevent multiple updates
        try:
            yield # Execute code within the 'with' block
        finally:
            self.blockSignals(False) # Unblock signals
            self._validate_current_input() # Validate after the batch update

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
        # Check if the preset name exists in the Masks class
        if not hasattr(self.Masks, preset_name):
            return

        # Get the mask string from the Masks class and set it as a custom mask
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

    # Signals emitted by the editor
    textChanged = Signal() # Emitted when the text content changes
    formattingChanged = Signal(FormattingAction) # Emitted when formatting is applied
    selectionChanged = Signal(str)  # Emitted when the text selection changes

    def __init__(self, parent: Optional[QWidget] = None, config: Optional[EditorConfig] = None):
        super().__init__(parent)

        # Load configuration or use default
        self._config = config or EditorConfig()
        self._theme_animation = get_theme_aware_animation() # Animation helper
        self._active_formats: set[FormattingAction] = set() # Keep track of currently active formats
        self._format_cache: Dict[str, QTextCharFormat] = {} # Cache for text formats

        # Setup auto-save timer
        self._auto_save_timer = QTimer()
        self._auto_save_timer.timeout.connect(self._auto_save) # Connect timeout signal to auto-save method
        # Start the timer if auto-save interval is positive
        if self._config.auto_save_interval > 0:
            self._auto_save_timer.start(self._config.auto_save_interval)

        # Setup the user interface, actions, and connections
        self._setup_modern_ui()
        self._setup_actions()
        self._setup_connections()

        # Apply initial styling and connect theme change signal
        self._apply_modern_style()
        theme_manager.theme_changed.connect(self._apply_modern_style)

    def _setup_modern_ui(self):
        """Setup UI using modern FluentLayoutBuilder"""
        # Create the main vertical layout with no spacing
        main_layout = FluentLayoutBuilder.create_vertical_layout(spacing=0)
        self.setLayout(main_layout)

        # Create and add the toolbar if enabled in config
        if self._config.enable_toolbar:
            self._toolbar = QToolBar(self)
            self._toolbar.setFixedHeight(self._config.toolbar_height)
            self._toolbar.setMovable(False) # Prevent toolbar from being moved
            self._toolbar.setFloatable(False) # Prevent toolbar from floating
            main_layout.addWidget(self._toolbar)

        # Create the main text editing area
        self._text_edit = QTextEdit(self)
        self._text_edit.setUndoRedoEnabled(True) # Enable undo/redo functionality

        # Set the maximum number of undo steps
        document = self._text_edit.document()
        document.setMaximumBlockCount(self._config.max_undo_steps)

        # Connect text and selection change signals
        self._text_edit.textChanged.connect(self.textChanged)
        self._text_edit.selectionChanged.connect(self._on_selection_changed)

        # Add the text edit widget to the main layout
        main_layout.addWidget(self._text_edit)

        # Set a minimum size for the editor widget
        self.setMinimumSize(300, 200)

    def _setup_actions(self):
        """Setup formatting actions using modern approach"""
        # Only setup actions if the toolbar is enabled
        if not self._config.enable_toolbar:
            return

        # Dictionary to store actions, mapped by FormattingAction enum
        self._actions: Dict[FormattingAction, QAction] = {}

        # --- Text Style Actions ---
        # Bold action
        bold_action = QAction("Bold", self)
        bold_action.setCheckable(True) # Make the action checkable (toggle state)
        bold_action.setShortcut("Ctrl+B") # Set keyboard shortcut
        # Connect triggered signal to apply_formatting with BOLD action
        bold_action.triggered.connect(
            lambda: self._apply_formatting(FormattingAction.BOLD))
        self._actions[FormattingAction.BOLD] = bold_action # Store action
        self._toolbar.addAction(bold_action) # Add action to toolbar

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

        self._toolbar.addSeparator() # Add a visual separator in the toolbar

        # --- Font Selection ---
        # Font family combo box
        self._font_combobox = QFontComboBox(self)
        # Connect currentFontChanged signal to format_font_family method
        self._font_combobox.currentFontChanged.connect(
            self._format_font_family)
        self._toolbar.addWidget(self._font_combobox) # Add widget to toolbar

        # Font size combo box
        self._font_size_combobox = QComboBox(self)
        font_sizes = ["8", "9", "10", "11", "12", "14", "16",
                      "18", "20", "22", "24", "28", "36", "48", "72"]
        self._font_size_combobox.addItems(font_sizes) # Populate with standard sizes
        self._font_size_combobox.setCurrentIndex(4)  # Default to 12pt (index 4)
        # Connect currentTextChanged signal to format_font_size method
        self._font_size_combobox.currentTextChanged.connect(
            self._format_font_size)
        self._toolbar.addWidget(self._font_size_combobox) # Add widget to toolbar

        self._toolbar.addSeparator() # Add a visual separator

        # --- Alignment Actions ---
        # Iterate through alignment actions and create/add them
        for action_type, alignment in [
            (FormattingAction.ALIGN_LEFT, Qt.AlignmentFlag.AlignLeft),
            (FormattingAction.ALIGN_CENTER, Qt.AlignmentFlag.AlignHCenter),
            (FormattingAction.ALIGN_RIGHT, Qt.AlignmentFlag.AlignRight),
            (FormattingAction.ALIGN_JUSTIFY, Qt.AlignmentFlag.AlignJustify),
        ]:
            # Create action with title derived from enum name
            action = QAction(action_type.name.replace('_', ' ').title(), self)
            action.setCheckable(True) # Alignment actions are checkable
            # Connect triggered signal to format_alignment, passing the alignment flag
            # Use lambda with default argument to capture the correct alignment value
            action.triggered.connect(
                lambda _checked, a=alignment: self._format_alignment(a))
            self._actions[action_type] = action # Store action
            self._toolbar.addAction(action) # Add action to toolbar

        self._toolbar.addSeparator() # Add a visual separator

        # --- List Actions ---
        # Bullet list action
        bullet_action = QAction("Bullet List", self)
        bullet_action.setCheckable(True)
        bullet_action.triggered.connect(
            lambda: self._apply_formatting(FormattingAction.BULLET_LIST))
        self._actions[FormattingAction.BULLET_LIST] = bullet_action
        self._toolbar.addAction(bullet_action)

        # Number list action
        number_action = QAction("Number List", self)
        number_action.setCheckable(True)
        number_action.triggered.connect(
            lambda: self._apply_formatting(FormattingAction.NUMBER_LIST))
        self._actions[FormattingAction.NUMBER_LIST] = number_action
        self._toolbar.addAction(number_action)

        self._toolbar.addSeparator() # Add a visual separator

        # --- Color and Link Actions ---
        # Text color action
        color_action = QAction("Text Color", self)
        color_action.triggered.connect(self._format_text_color) # Connect to color selection method
        self._toolbar.addAction(color_action)

        # Insert link action
        link_action = QAction("Insert Link", self)
        link_action.triggered.connect(self._insert_link) # Connect to link dialog method
        self._toolbar.addAction(link_action)

    def _setup_connections(self):
        """Setup signal connections"""
        # Connect cursor position changes to update action states (e.g., bold button checked state)
        self._text_edit.cursorPositionChanged.connect(
            self._update_action_states)

        # Connect text changes to reset the auto-save timer if auto-save is enabled
        if self._config.auto_save_interval > 0:
            self._text_edit.textChanged.connect(self._reset_auto_save_timer)

    def _apply_modern_style(self):
        """Apply modern styling with theme integration"""
        theme = theme_manager

        # Style the toolbar if it exists
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

        # Style the text edit widget
        textedit_style = f"""
            QTextEdit {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-top: none; /* Remove top border to blend with toolbar */
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
                selection-background-color: {theme.get_color('primary').name()}30;
                padding: 12px;
            }}

            QTextEdit:focus {{
                border-color: {theme.get_color('primary').name()};
                outline: none; /* Remove default focus outline */
            }}
        """
        self._text_edit.setStyleSheet(textedit_style)

        # Style the combo boxes (font family and size) if they exist
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
        # Create a QTextCharFormat object
        fmt = QTextCharFormat()

        # Apply formatting based on the format_key string
        if "bold" in format_key:
            fmt.setFontWeight(QFont.Weight.Bold)
        if "italic" in format_key:
            fmt.setFontItalic(True)
        if "underline" in format_key:
            fmt.setFontUnderline(True)

        return fmt # Return the configured format

    def _apply_formatting(self, action: FormattingAction):
        """Apply formatting using enum-based approach with caching"""
        # Apply formatting based on the action type
        if action == FormattingAction.BOLD:
            fmt = QTextCharFormat()
            # Toggle bold state: if currently bold, make normal; otherwise, make bold
            is_bold = action in self._active_formats
            fmt.setFontWeight(
                QFont.Weight.Normal if is_bold else QFont.Weight.Bold)
            self._merge_format_with_animation(fmt) # Apply format with animation

        elif action == FormattingAction.ITALIC:
            fmt = QTextCharFormat()
            # Toggle italic state
            is_italic = action in self._active_formats
            fmt.setFontItalic(not is_italic)
            self._merge_format_with_animation(fmt)

        elif action == FormattingAction.UNDERLINE:
            fmt = QTextCharFormat()
            # Toggle underline state
            is_underlined = action in self._active_formats
            fmt.setFontUnderline(not is_underlined)
            self._merge_format_with_animation(fmt)

        elif action == FormattingAction.BULLET_LIST:
            self._format_bullet_list() # Call specific list formatting method

        elif action == FormattingAction.NUMBER_LIST:
            self._format_number_list() # Call specific list formatting method

        # Update the set of active formats based on the toggle action
        if action in self._active_formats:
            self._active_formats.remove(action)
        else:
            self._active_formats.add(action)

        # Update the UI state of toolbar buttons
        self._update_action_states()
        # Emit signal indicating formatting has changed
        self.formattingChanged.emit(action)

    def _merge_format_with_animation(self, fmt: QTextCharFormat):
        """Apply formatting with subtle animation"""
        cursor = self._text_edit.textCursor()

        # Apply format to the current selection or current character if no selection
        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)
            # Trigger a simple animation for visual feedback on selection
            if self._config.enable_animations:
                self._create_format_feedback_animation()
        else:
            self._text_edit.mergeCurrentCharFormat(fmt) # Apply format to the character at cursor

    def _create_format_feedback_animation(self):
        """Create subtle feedback animation for formatting changes"""
        # Only run animation if enabled in config
        if not self._config.enable_animations:
            return

        # Create a theme-aware color animation for the text edit's style sheet
        # This provides a brief visual cue when formatting is applied
        animation = self._theme_animation.create_theme_aware_color_animation(
            self._text_edit, "styleSheet", "accent_light", duration=150
        )
        animation.start() # Start the animation

    def _format_font_family(self, font: QFont):
        """Set font family with caching"""
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family()) # Set the font family from the selected font
        self._merge_format_with_animation(fmt) # Apply the format

    def _format_font_size(self, size: str):
        """Set font size with validation"""
        try:
            size_value = float(size) # Convert size string to float
            fmt = QTextCharFormat()
            fmt.setFontPointSize(size_value) # Set the font point size
            self._merge_format_with_animation(fmt) # Apply the format
        except ValueError:
            pass  # If conversion fails (invalid size), ignore the input

    def _format_alignment(self, alignment: Qt.AlignmentFlag):
        """Set paragraph alignment"""
        self._text_edit.setAlignment(alignment) # Apply the specified alignment to the current block
        self._create_format_feedback_animation() # Provide visual feedback

    def _format_text_color(self):
        """Change text color with validation"""
        # Open a color dialog to allow the user to select a color
        color = QColorDialog.getColor(
            self._text_edit.textColor(), # Start with the current text color
            self, # Parent widget
            "Select Text Color" # Dialog title
        )

        # If the user selected a valid color (didn't cancel)
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color) # Set the foreground color in the format
            self._merge_format_with_animation(fmt) # Apply the format

    def _format_bullet_list(self):
        """Toggle bullet list with optimized approach"""
        cursor = self._text_edit.textCursor()
        list_format = QTextListFormat() # Create a list format object

        # Check if bullet list formatting is currently active
        is_bullet_active = FormattingAction.BULLET_LIST in self._active_formats

        if not is_bullet_active:
            # If not active, create a new bullet list
            list_format.setStyle(QTextListFormat.Style.ListDisc) # Set style to bullet disc
            list_format.setIndent(1) # Set indentation level
            cursor.createList(list_format) # Apply list format to current block(s)
        else:
            # If active, remove the list formatting from the current block
            current_list = cursor.currentList() # Get the list the cursor is in
            if current_list:
                current_list.removeItem(cursor.blockNumber()) # Remove the current block from the list

        self._create_format_feedback_animation() # Provide visual feedback

    def _format_number_list(self):
        """Toggle numbered list with optimized approach"""
        cursor = self._text_edit.textCursor()
        list_format = QTextListFormat() # Create a list format object

        # Check if number list formatting is currently active
        is_number_active = FormattingAction.NUMBER_LIST in self._active_formats

        if not is_number_active:
            # If not active, create a new numbered list
            list_format.setStyle(QTextListFormat.Style.ListDecimal) # Set style to decimal numbers
            list_format.setIndent(1) # Set indentation level
            cursor.createList(list_format) # Apply list format to current block(s)
        else:
            # If active, remove the list formatting from the current block
            current_list = cursor.currentList() # Get the list the cursor is in
            if current_list:
                current_list.removeItem(cursor.blockNumber()) # Remove the current block from the list

        self._create_format_feedback_animation() # Provide visual feedback

    def _insert_link(self):
        """Insert hyperlink using modern dialog"""
        cursor = self._text_edit.textCursor()
        selected_text = cursor.selectedText() # Get the currently selected text

        # Create and show the link dialog, pre-populating with selected text
        dialog = OptimizedFluentLinkDialog(self, initial_text=selected_text)

        # If the dialog was accepted (OK button clicked)
        if dialog.exec():
            link_data = dialog.get_link_data() # Get the text and URL from the dialog
            # Insert the link as HTML at the cursor's position
            cursor.insertHtml(
                f'<a href="{link_data["url"]}">{link_data["text"]}</a>')
            self._create_format_feedback_animation() # Provide visual feedback

    def _update_action_states(self):
        """Update action states based on current cursor position"""
        # Only update if the toolbar is enabled
        if not self._config.enable_toolbar:
            return

        cursor = self._text_edit.textCursor()
        format = cursor.charFormat() # Get the character format at the cursor's position

        # --- Update Text Style Action States ---
        # Update bold action checked state
        if FormattingAction.BOLD in self._actions:
            is_bold = format.fontWeight() == QFont.Weight.Bold
            self._actions[FormattingAction.BOLD].setChecked(is_bold)

        # Update italic action checked state
        if FormattingAction.ITALIC in self._actions:
            self._actions[FormattingAction.ITALIC].setChecked(
                format.fontItalic())

        # Update underline action checked state
        if FormattingAction.UNDERLINE in self._actions:
            self._actions[FormattingAction.UNDERLINE].setChecked(
                format.fontUnderline())

        # --- Update Font Selection Widget States ---
        # Update font selections if the combo boxes exist
        if hasattr(self, '_font_combobox'):
            # Use batch update context manager to prevent signal loops
            with self._batch_update():
                # Update font family combo box
                font_family = format.fontFamily()
                if font_family:
                    self._font_combobox.setCurrentFont(QFont(font_family))

                # Update font size combo box
                font_size = format.fontPointSize()
                if font_size > 0:
                    # Find the index of the current font size in the combo box items
                    size_index = self._font_size_combobox.findText(
                        str(int(font_size)))
                    if size_index >= 0:
                        self._font_size_combobox.setCurrentIndex(size_index)

    def _on_selection_changed(self):
        """Handle selection change"""
        cursor = self._text_edit.textCursor()
        selected_text = cursor.selectedText() # Get the currently selected text
        self.selectionChanged.emit(selected_text) # Emit signal with selected text
        self._update_action_states() # Update toolbar action states based on new selection

    @contextmanager
    def _batch_update(self):
        """Context manager for batch updates"""
        # Block signals to prevent multiple updates during the 'with' block
        self.blockSignals(True)
        try:
            yield # Execute code within the 'with' block
        finally:
            self.blockSignals(False) # Unblock signals

    def _reset_auto_save_timer(self):
        """Reset auto-save timer when text changes"""
        # Restart the timer if auto-save is enabled
        if self._config.auto_save_interval > 0:
            self._auto_save_timer.start(self._config.auto_save_interval)

    def _auto_save(self):
        """Auto-save functionality (override in subclasses)"""
        # This is a placeholder method. Subclasses should override this
        # to implement actual saving logic (e.g., saving to a file or database).
        pass # Default implementation does nothing

    # Public API methods
    def set_html(self, html: str):
        """Set HTML content"""
        self._text_edit.setHtml(html) # Set the editor's content from HTML string

    def get_html(self) -> str:
        """Get content as HTML"""
        return self._text_edit.toHtml() # Return the editor's content as HTML string

    def set_plain_text(self, text: str):
        """Set plain text content"""
        self._text_edit.setPlainText(text) # Set the editor's content from plain text string

    def get_plain_text(self) -> str:
        """Get content as plain text"""
        return self._text_edit.toPlainText() # Return the editor's content as plain text string

    def clear(self):
        """Clear all content"""
        self._text_edit.clear() # Clear the text edit content
        self._active_formats.clear() # Clear the set of active formats
        self._format_cache.clear() # Clear the format cache

    @property
    def config(self) -> EditorConfig:
        """Get editor configuration"""
        return self._config # Return the current editor configuration

# Legacy alias for backward compatibility
class FluentRichTextEditor(OptimizedFluentRichTextEditor):
    pass


class OptimizedFluentLinkDialog(QDialog):
    """Optimized dialog for inserting links in rich text editor with modern features"""

    def __init__(self, parent: Optional[QWidget] = None,
                 initial_text: str = "", initial_url: str = ""):
        super().__init__(parent)

        # Setup the dialog's UI, appearance, and validation
        self._setup_ui()
        self._setup_appearance()
        self._setup_validation()

        # Set initial values for the text and URL fields if provided
        if initial_text:
            self._text_edit.setText(initial_text)
        if initial_url:
            self._url_edit.setText(initial_url)

        # Update the state of the OK button based on initial input
        self._update_ok_button_state()

    def _setup_ui(self):
        """Setup dialog UI using modern layout"""
        self.setWindowTitle("Insert Link") # Set the window title
        self.setModal(True) # Make the dialog modal (blocks parent window)
        self.resize(500, 180) # Set a default size for the dialog

        # Use FluentLayoutBuilder for consistent styling and layout
        main_layout = FluentLayoutBuilder.create_vertical_layout(
            spacing=16, margins=(20, 20, 20, 20)) # Create main layout with spacing and margins
        self.setLayout(main_layout) # Set the main layout for the dialog

        # --- Text Input ---
        # Create a container and form layout for the text input
        text_container, text_form_layout = FluentLayoutBuilder.create_form_layout(
            label_width=60) # Form layout with a fixed label width
        text_label = QLabel("Text:") # Label for the text input
        self._text_edit = QLineEdit(self) # Line edit for the link text
        self._text_edit.setPlaceholderText("Link text (e.g., 'Click here')") # Placeholder text
        text_form_layout.addWidget(text_label, 0, 0) # Add label to form layout (row 0, col 0)
        text_form_layout.addWidget(self._text_edit, 0, 1) # Add line edit to form layout (row 0, col 1)
        main_layout.addWidget(text_container) # Add the container to the main layout

        # --- URL Input ---
        # Create a container and form layout for the URL input
        url_container, url_form_layout = FluentLayoutBuilder.create_form_layout(
            label_width=60) # Form layout with a fixed label width
        url_label = QLabel("URL:") # Label for the URL input
        self._url_edit = QLineEdit(self) # Line edit for the URL
        self._url_edit.setPlaceholderText("https://example.com") # Placeholder text
        url_form_layout.addWidget(url_label, 0, 0) # Add label to form layout (row 0, col 0)
        url_form_layout.addWidget(self._url_edit, 0, 1) # Add line edit to form layout (row 0, col 1)
        main_layout.addWidget(url_container) # Add the container to the main layout

        # --- Buttons ---
        # Create a horizontal layout for the buttons
        button_layout = FluentLayoutBuilder.create_horizontal_layout()
        button_layout.addStretch() # Add a stretchable space to push buttons to the right

        # Create OK and Cancel buttons using FluentStandardButton
        self._ok_button = FluentStandardButton(
            "OK", variant=FluentStandardButton.PRIMARY) # Primary variant for OK button
        self._ok_button.clicked.connect(self._on_ok_clicked) # Connect clicked signal to handler
        self._cancel_button = FluentStandardButton("Cancel") # Default variant for Cancel button
        self._cancel_button.clicked.connect(self.reject) # Connect clicked signal to reject dialog

        # Add buttons to the button layout
        button_layout.addWidget(self._cancel_button)
        button_layout.addWidget(self._ok_button)
        main_layout.addLayout(button_layout) # Add the button layout to the main layout

    def _setup_validation(self):
        """Setup input validation"""
        # Connect text change signals of both line edits to the state update method
        # This ensures the OK button state is updated whenever text changes
        self._text_edit.textChanged.connect(self._update_ok_button_state)
        self._url_edit.textChanged.connect(self._update_ok_button_state)

        # Set up a QRegularExpressionValidator for the URL input
        # This pattern allows http/https URLs or simple domain/path strings
        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$|^[^\s/$.?#].[^\s]*$"
        self._url_validator = QRegularExpressionValidator(
            QRegularExpression(url_pattern))
        self._url_edit.setValidator(self._url_validator) # Apply the validator to the URL line edit

    def _update_ok_button_state(self):
        """Update OK button state based on input validation"""
        # Check if both text and URL fields have non-empty content after stripping whitespace
        text_valid = bool(self._text_edit.text().strip())
        url_valid = bool(self._url_edit.text().strip())

        # Enable the OK button only if both the text and URL fields are valid (not empty)
        self._ok_button.setEnabled(text_valid and url_valid)

    def _on_ok_clicked(self):
        """Handle OK button click with validation"""
        url_text = self._url_edit.text().strip() # Get the URL text and strip whitespace

        # Auto-add 'https://' protocol if the URL text is not empty and doesn't start with http or https
        if url_text and not url_text.startswith(('http://', 'https://')):
            url_text = 'https://' + url_text
            self._url_edit.setText(url_text) # Update the URL line edit with the corrected URL

        self.accept() # Accept the dialog (closes it with result code Accepted)

    def _setup_appearance(self):
        """Setup dialog appearance with modern styling"""
        theme = theme_manager # Get the current theme manager

        # Define the stylesheet for the dialog and its widgets
        style_sheet = f"""
            OptimizedFluentLinkDialog {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
            }}

            QLabel {{
                color: {theme.get_color('text_primary').name()};
                font-weight: 500; /* Medium font weight */
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
                padding: 7px 11px; /* Adjust padding for wider border */
                outline: none;
            }}

            QLineEdit:invalid {{
                border-color: {theme.get_color('error', '#ff4444').name()}; /* Error color for invalid input */
            }}
        """

        self.setStyleSheet(style_sheet) # Apply the stylesheet to the dialog

    def get_link_data(self) -> Dict[str, str]:
        """Get the entered link data with validation"""
        url_text = self._url_edit.text().strip() # Get the URL text and strip whitespace

        # Ensure the URL has a protocol (http or https) before returning
        if url_text and not url_text.startswith(('http://', 'https://')):
            url_text = 'https://' + url_text

        # Return a dictionary containing the link text and URL
        return {
            'text': self._text_edit.text().strip(), # Get text and strip whitespace
            'url': url_text # Return the potentially corrected URL
        }

# Legacy alias for backward compatibility
class FluentLinkDialog(OptimizedFluentLinkDialog):
    pass
