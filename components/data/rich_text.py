"""
Enhanced Masked Input and Rich Text Editor for Fluent Design
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QTextEdit, QToolBar, QFrame, QSizePolicy,
                               QColorDialog, QFontComboBox, QComboBox, QPushButton,
                               QMenu, QDialog)
from PySide6.QtCore import Qt, Signal, QRegularExpression, QSize
from PySide6.QtGui import (QAction, QValidator, QTextCharFormat, QFont, QColor, QTextCursor,
                           QRegularExpressionValidator, QTextListFormat, QTextBlockFormat,
                           QTextDocumentFragment)
from core.theme import theme_manager
from typing import Optional, Dict, Any


class FluentMaskedInput(QLineEdit):
    """Fluent Design Style Masked Input Field

    Features:
    - Input conforming to specific patterns
    - Visual cues for input format
    - Common mask presets for date, phone, etc.
    - Customizable input validation
    """

    # Common mask presets
    class Masks:
        DATE = "00/00/0000"
        TIME = "00:00"
        DATETIME = "00/00/0000 00:00"
        PHONE_US = "(000) 000-0000"
        PHONE_INTL = "+00 000 000 0000"
        SSN = "000-00-0000"
        IP_ADDRESS = "000.000.000.000"
        CREDIT_CARD = "0000 0000 0000 0000"

    valueChanged = Signal(str)  # Emitted when value changes and is valid

    def __init__(self, parent: Optional[QWidget] = None,
                 mask: str = "", placeholder: str = ""):
        super().__init__(parent)

        self._mask = mask
        self._placeholder = placeholder
        self._prompt_char = "_"
        self._input_mask_chars = {
            "0": "[0-9]",     # Digit
            "9": "[0-9 ]",    # Digit or space
            "#": "[0-9+-]",   # Digit or sign
            "A": "[A-Za-z]",  # Letter
            "a": "[A-Za-z ]",  # Letter or space
            "N": "[A-Za-z0-9]",  # Alphanumeric
            "X": "[A-Fa-f0-9]",  # Hex
            "&": "."          # Any character
        }

        # Setup mask
        if mask:
            self.set_mask(mask)

        # Set placeholder text
        if placeholder:
            self.setPlaceholderText(placeholder)

        # Apply styling
        self._apply_style()

        # Connect signals
        self.textChanged.connect(self._on_text_changed)
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _apply_style(self):
        """Apply styling to the masked input"""
        theme = theme_manager

        style_sheet = f"""
            FluentMaskedInput {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                selection-background-color: {theme.get_color('primary').name()}40;
            }}
            
            FluentMaskedInput:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
                padding: 7px 11px;
            }}
            
            FluentMaskedInput:disabled {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_disabled').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self):
        """Handle theme changes"""
        self._apply_style()

    def set_mask(self, mask: str, prompt_char: str = "_"):
        """Set the input mask

        Args:
            mask: Mask pattern using Qt's input mask format
            prompt_char: Character to show for empty positions
        """
        self._mask = mask
        self._prompt_char = prompt_char

        # Apply Qt's input mask
        self.setInputMask(mask)
        self.setCursorPosition(0)

    def set_validation_mask(self, pattern: str, input_mask: str = ""):
        """Set validation using a regex pattern

        Args:
            pattern: Regular expression pattern
            input_mask: Optional Qt input mask to provide visual cues
        """
        if input_mask:
            self.setInputMask(input_mask)

        # Create and set validator
        regex = QRegularExpression(pattern)
        validator = QRegularExpressionValidator(regex, self)
        self.setValidator(validator)

    def _on_text_changed(self, text: str):
        """Handle text changes with validation"""
        # Only emit valueChanged if the text is valid (fully matches the mask)
        if self.hasAcceptableInput() and text != self.inputMask():
            self.valueChanged.emit(self.text())

    def get_unmasked_value(self) -> str:
        """Get the value without mask characters

        Returns:
            Text with only the user input, no mask characters
        """
        text = self.text()

        # Remove non-alphanumeric characters if a mask is set
        if self._mask:
            result = ""
            for c in text:
                if c.isalnum():  # Only keep alphanumeric characters
                    result += c
            return result

        return text

    def set_preset_mask(self, preset_name: str):
        """Set a preset mask

        Args:
            preset_name: Name of the preset from Masks class
        """
        if not hasattr(self.Masks, preset_name):
            return

        preset_mask = getattr(self.Masks, preset_name)
        self.set_mask(preset_mask)


class FluentRichTextEditor(QWidget):
    """Fluent Design Style Rich Text Editor
    
    A QWidget-based rich text editor that follows the Fluent Design guidelines.
    Provides text formatting, styling, and editing capabilities.
    """
    
    #: Signal emitted when text content changes
    textChanged = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Main layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Create toolbar
        self._create_toolbar()

        # Create text edit
        self._text_edit = QTextEdit(self)
        self._text_edit.textChanged.connect(self.textChanged)

        # Add widgets to layout
        self._layout.addWidget(self._toolbar)
        self._layout.addWidget(self._text_edit)

        # Set minimum size
        self.setMinimumSize(300, 200)

        # Apply styling
        self._apply_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _create_toolbar(self):
        """Create and configure the formatting toolbar"""
        self._toolbar = QToolBar(self)
        self._toolbar.setIconSize(QSize(16, 16))

        # Text style actions
        self._action_bold = QAction("Bold", self)
        self._action_bold.setCheckable(True)
        self._action_bold.setShortcut("Ctrl+B")
        self._action_bold.triggered.connect(self._format_bold)

        self._action_italic = QAction("Italic", self)
        self._action_italic.setCheckable(True)
        self._action_italic.setShortcut("Ctrl+I")
        self._action_italic.triggered.connect(self._format_italic)

        self._action_underline = QAction("Underline", self)
        self._action_underline.setCheckable(True)
        self._action_underline.setShortcut("Ctrl+U")
        self._action_underline.triggered.connect(self._format_underline)

        # Font family combo box
        self._font_combobox = QFontComboBox(self)
        self._font_combobox.currentFontChanged.connect(
            self._format_font_family)

        # Font size combo box
        self._font_size_combobox = QComboBox(self)
        font_sizes = ["8", "9", "10", "11", "12", "14", "16",
                      "18", "20", "22", "24", "28", "36", "48", "72"]
        self._font_size_combobox.addItems(font_sizes)
        self._font_size_combobox.setCurrentIndex(4)  # Default to 12pt
        self._font_size_combobox.currentTextChanged.connect(
            self._format_font_size)

        # Paragraph alignment actions
        self._action_align_left = QAction("Align Left", self)
        self._action_align_left.setCheckable(True)
        self._action_align_left.triggered.connect(
            lambda: self._format_alignment(Qt.AlignmentFlag.AlignLeft))

        self._action_align_center = QAction("Align Center", self)
        self._action_align_center.setCheckable(True)
        self._action_align_center.triggered.connect(
            lambda: self._format_alignment(Qt.AlignmentFlag.AlignHCenter))

        self._action_align_right = QAction("Align Right", self)
        self._action_align_right.setCheckable(True)
        self._action_align_right.triggered.connect(
            lambda: self._format_alignment(Qt.AlignmentFlag.AlignRight))

        self._action_align_justify = QAction("Justify", self)
        self._action_align_justify.setCheckable(True)
        self._action_align_justify.triggered.connect(
            lambda: self._format_alignment(Qt.AlignmentFlag.AlignJustify))

        # List actions
        self._action_bullet_list = QAction("Bullet List", self)
        self._action_bullet_list.setCheckable(True)
        self._action_bullet_list.triggered.connect(self._format_bullet_list)

        self._action_number_list = QAction("Number List", self)
        self._action_number_list.setCheckable(True)
        self._action_number_list.triggered.connect(self._format_number_list)

        # Color selection
        self._action_text_color = QAction("Text Color", self)
        self._action_text_color.triggered.connect(self._format_text_color)

        # Link action
        self._action_insert_link = QAction("Insert Link", self)
        self._action_insert_link.triggered.connect(self._insert_link)

        # Add actions to toolbar
        self._toolbar.addAction(self._action_bold)
        self._toolbar.addAction(self._action_italic)
        self._toolbar.addAction(self._action_underline)
        self._toolbar.addSeparator()
        self._toolbar.addWidget(self._font_combobox)
        self._toolbar.addWidget(self._font_size_combobox)
        self._toolbar.addSeparator()
        self._toolbar.addAction(self._action_align_left)
        self._toolbar.addAction(self._action_align_center)
        self._toolbar.addAction(self._action_align_right)
        self._toolbar.addAction(self._action_align_justify)
        self._toolbar.addSeparator()
        self._toolbar.addAction(self._action_bullet_list)
        self._toolbar.addAction(self._action_number_list)
        self._toolbar.addSeparator()
        self._toolbar.addAction(self._action_text_color)
        self._toolbar.addAction(self._action_insert_link)

    def _apply_style(self):
        """Apply styling to the rich text editor"""
        theme = theme_manager

        # Style the toolbar
        toolbar_style = f"""
            QToolBar {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
                padding: 4px;
                spacing: 2px;
            }}
            
            QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px;
            }}
            
            QToolButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('border').name()};
            }}
            
            QToolButton:checked {{
                background-color: {theme.get_color('accent_medium').name()};
                border-color: {theme.get_color('primary').name()};
            }}
        """

        # Style the text edit
        textedit_style = f"""
            QTextEdit {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-top: none;
                font-size: 14px;
                selection-background-color: {theme.get_color('primary').name()}40;
            }}
        """

        # Style the combo boxes
        combobox_style = f"""
            QComboBox {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 2px 8px;
                min-height: 24px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 16px;
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

        # Combine styles
        self._toolbar.setStyleSheet(toolbar_style)
        self._text_edit.setStyleSheet(textedit_style)
        self._font_combobox.setStyleSheet(combobox_style)
        self._font_size_combobox.setStyleSheet(combobox_style)

    def _on_theme_changed(self):
        """Handle theme changes"""
        self._apply_style()

    def _format_bold(self):
        """Toggle bold formatting"""
        fmt = QTextCharFormat()
        fmt.setFontWeight(
            QFont.Weight.Bold if self._action_bold.isChecked() else QFont.Weight.Normal)
        self._merge_format(fmt)

    def _format_italic(self):
        """Toggle italic formatting"""
        fmt = QTextCharFormat()
        fmt.setFontItalic(self._action_italic.isChecked())
        self._merge_format(fmt)

    def _format_underline(self):
        """Toggle underline formatting"""
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self._action_underline.isChecked())
        self._merge_format(fmt)

    def _format_font_family(self, font: QFont):
        """Set font family"""
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family())
        self._merge_format(fmt)

    def _format_font_size(self, size: str):
        """Set font size"""
        fmt = QTextCharFormat()
        fmt.setFontPointSize(float(size))
        self._merge_format(fmt)

    def _format_alignment(self, alignment):
        """Set paragraph alignment"""
        self._text_edit.setAlignment(alignment)

    def _format_text_color(self):
        """Change text color"""
        color = QColorDialog.getColor(
            self._text_edit.textColor(),
            self,
            "Select Text Color"
        )

        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self._merge_format(fmt)

    def _format_bullet_list(self):
        """Toggle bullet list"""
        cursor = self._text_edit.textCursor()
        list_format = QTextListFormat()

        if self._action_bullet_list.isChecked():
            list_format.setStyle(QTextListFormat.Style.ListDisc)
            list_format.setIndent(1)
            cursor.createList(list_format)
        else:
            current_list = cursor.currentList()
            if current_list:
                current_list.setFormat(QTextListFormat())

        self._text_edit.setFocus()

    def _format_number_list(self):
        """Toggle numbered list"""
        cursor = self._text_edit.textCursor()
        list_format = QTextListFormat()

        if self._action_number_list.isChecked():
            list_format.setStyle(QTextListFormat.Style.ListDecimal)
            list_format.setIndent(1)
            cursor.createList(list_format)
        else:
            current_list = cursor.currentList()
            if current_list:
                current_list.setFormat(QTextListFormat())

        self._text_edit.setFocus()

    def _insert_link(self):
        """Insert hyperlink"""
        # Get link text and URL
        cursor = self._text_edit.textCursor()
        selected_text = cursor.selectedText()

        # Simple implementation - in a real app, you'd show a dialog
        link_text = selected_text if selected_text else "link text"
        link_url = "http://example.com"

        # Insert link
        cursor.insertHtml(f'<a href="{link_url}">{link_text}</a>')
        self._text_edit.setFocus()

    def _merge_format(self, fmt: QTextCharFormat):
        """Apply formatting to selected text"""
        cursor = self._text_edit.textCursor()

        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)
        else:
            self._text_edit.mergeCurrentCharFormat(fmt)

        self._text_edit.setFocus()

    def set_html(self, html: str):
        """Set HTML content

        Args:
            html: HTML content to set
        """
        self._text_edit.setHtml(html)

    def get_html(self) -> str:
        """Get content as HTML
        
        Returns:
            str: The editor content as HTML
        """
        return self._text_edit.toHtml()

    def set_plain_text(self, text: str):
        """Set plain text content

        Args:
            text: Plain text content to set
        """
        self._text_edit.setPlainText(text)

    def get_plain_text(self) -> str:
        """Get content as plain text
        
        Returns:
            str: The editor content as plain text
        """
        return self._text_edit.toPlainText()

    def clear(self):
        """Clear all content"""
        self._text_edit.clear()
        self._text_edit.clear()


class FluentLinkDialog(QDialog):
    """Dialog for inserting links in rich text editor"""

    def __init__(self, parent: Optional[QWidget] = None,
                 initial_text: str = "", initial_url: str = ""):
        super().__init__(parent)

        self._setup_ui()
        self._setup_appearance()

        # Set initial values
        if initial_text:
            self._text_edit.setText(initial_text)
        if initial_url:
            self._url_edit.setText(initial_url)

    def _setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Insert Link")
        self.setModal(True)
        self.resize(400, 150)

        layout = QVBoxLayout(self)

        # Text input
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text:"))
        self._text_edit = QLineEdit(self)
        text_layout.addWidget(self._text_edit)
        layout.addLayout(text_layout)

        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self._url_edit = QLineEdit(self)
        self._url_edit.setPlaceholderText("http://example.com")
        url_layout.addWidget(self._url_edit)
        layout.addLayout(url_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self._ok_button = QPushButton("OK", self)
        self._ok_button.clicked.connect(self.accept)
        self._cancel_button = QPushButton("Cancel", self)
        self._cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self._ok_button)
        button_layout.addWidget(self._cancel_button)
        layout.addLayout(button_layout)

    def _setup_appearance(self):
        """Setup dialog appearance"""
        theme = theme_manager

        style_sheet = f"""
            QDialog {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
            }}
            
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                min-width: 50px;
            }}
            
            QLineEdit {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 4px 8px;
            }}
            
            QPushButton {{
                background-color: {theme.get_color('primary').name()};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: {theme.get_color('primary').darker(110).name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def get_link_data(self) -> Dict[str, str]:
        """Get the entered link data"""
        return {
            'text': self._text_edit.text(),
            'url': self._url_edit.text()
        }
