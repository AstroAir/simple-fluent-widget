"""
Fluent Design Data Entry Components
Advanced input fields, editors, and form controls
"""

from PySide6.QtWidgets import (QWidget, QLineEdit, QTextEdit, QComboBox, QDateEdit,
                               QTimeEdit, QDateTimeEdit, QSpinBox, QDoubleSpinBox,
                               QSlider, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                               QCompleter, QListWidget, QListWidgetItem, QScrollArea,
                               QCheckBox, QRadioButton, QButtonGroup, QGroupBox,
                               QGridLayout, QPushButton, QFileDialog, QProgressBar)
from PySide6.QtCore import (Qt, Signal, QDate, QTime, QDateTime, QTimer, QRegularExpression,
                            QStringListModel, QPropertyAnimation, QEasingCurve, QRect)
from PySide6.QtGui import (QValidator, QRegularExpressionValidator, QFont, QPixmap,
                           QIcon, QPainter, QColor, QBrush, QPen, QLinearGradient)
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional, List, Dict, Any, Callable
import re


class FluentMaskedLineEdit(QLineEdit):
    """Fluent Design style masked input field"""

    def __init__(self, mask: str = "", placeholder: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._mask_pattern = mask
        self._original_placeholder = placeholder
        self._mask_chars = {'#': r'\d', 'A': r'[A-Za-z]', '*': r'.'}

        self.setPlaceholderText(placeholder)
        self._setup_style()
        self._setup_validator()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def setInputMask(self, mask: str):
        """Set input mask pattern

        Args:
            mask: Mask pattern (# = digit, A = letter, * = any)
                 Example: "##/##/####" for date, "(###) ###-####" for phone
        """
        self._mask_pattern = mask
        self._setup_validator()
        self._update_placeholder()

    def _setup_validator(self):
        """Setup input validator based on mask"""
        if not self._mask_pattern:
            return

        # Convert mask to regex
        regex_pattern = ""
        for char in self._mask_pattern:
            if char in self._mask_chars:
                regex_pattern += self._mask_chars[char]
            else:
                regex_pattern += re.escape(char)

        validator = QRegularExpressionValidator(
            QRegularExpression(regex_pattern))
        self.setValidator(validator)

    def _update_placeholder(self):
        """Update placeholder to show mask"""
        if self._mask_pattern:
            placeholder = self._mask_pattern.replace(
                '#', '0').replace('A', 'A').replace('*', 'X')
            self.setPlaceholderText(
                f"{self._original_placeholder} ({placeholder})")
        else:
            self.setPlaceholderText(self._original_placeholder)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentMaskedLineEdit {{
                background-color: {theme.get_color('surface').name()};
                border: 2px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()};
                selection-color: white;
            }}
            FluentMaskedLineEdit:focus {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('surface').name()};
            }}
            FluentMaskedLineEdit:hover {{
                border-color: {theme.get_color('primary').lighter(130).name()};
            }}
            FluentMaskedLineEdit:disabled {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_disabled').name()};
                border-color: {theme.get_color('border').darker(120).name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentAutoCompleteEdit(QLineEdit):
    """Fluent Design style auto-complete input field"""

    item_selected = Signal(str)

    def __init__(self, suggestions: Optional[List[str]] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._suggestions = suggestions or []
        self._filtered_suggestions = []
        self._setup_completer()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def setSuggestions(self, suggestions: List[str]):
        """Set suggestion list"""
        self._suggestions = suggestions
        self._setup_completer()

    def addSuggestion(self, suggestion: str):
        """Add a suggestion"""
        if suggestion not in self._suggestions:
            self._suggestions.append(suggestion)
            self._setup_completer()

    def _setup_completer(self):
        """Setup auto-completer"""
        if self._suggestions:
            model = QStringListModel(self._suggestions)
            completer = QCompleter(model)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)

            # Style the completer popup
            completer.popup().setStyleSheet(f"""
                QListView {{
                    background-color: {theme_manager.get_color('surface').name()};
                    border: 1px solid {theme_manager.get_color('border').name()};
                    border-radius: 6px;
                    selection-background-color: {theme_manager.get_color('primary').name()};
                    selection-color: white;
                    font-size: 14px;
                    padding: 4px;
                }}
                QListView::item {{
                    padding: 6px 12px;
                    border-radius: 4px;
                }}
                QListView::item:hover {{
                    background-color: {theme_manager.get_color('accent_light').name()};
                }}
            """)

            completer.activated.connect(self.item_selected.emit)
            self.setCompleter(completer)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentAutoCompleteEdit {{
                background-color: {theme.get_color('surface').name()};
                border: 2px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()};
                selection-color: white;
            }}
            FluentAutoCompleteEdit:focus {{
                border-color: {theme.get_color('primary').name()};
            }}
            FluentAutoCompleteEdit:hover {{
                border-color: {theme.get_color('primary').lighter(130).name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self._setup_completer()


class FluentRichTextEditor(QWidget):
    """Fluent Design style rich text editor"""

    text_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(40)
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(8, 4, 8, 4)
        toolbar_layout.setSpacing(4)

        # Bold button
        self.bold_btn = QPushButton("B")
        self.bold_btn.setFixedSize(28, 28)
        self.bold_btn.setCheckable(True)
        self.bold_btn.setFont(QFont("", 10, QFont.Weight.Bold))
        self.bold_btn.clicked.connect(self._toggle_bold)

        # Italic button
        self.italic_btn = QPushButton("I")
        self.italic_btn.setFixedSize(28, 28)
        self.italic_btn.setCheckable(True)
        self.italic_btn.setFont(QFont("", 10, QFont.Weight.Normal))
        self.italic_btn.clicked.connect(self._toggle_italic)

        # Underline button
        self.underline_btn = QPushButton("U")
        self.underline_btn.setFixedSize(28, 28)
        self.underline_btn.setCheckable(True)
        self.underline_btn.setFont(QFont("", 10, QFont.Weight.Normal))
        self.underline_btn.clicked.connect(self._toggle_underline)

        # Font size combo
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(
            ["8", "10", "12", "14", "16", "18", "20", "24"])
        self.font_size_combo.setCurrentText("14")
        self.font_size_combo.currentTextChanged.connect(self._change_font_size)

        toolbar_layout.addWidget(self.bold_btn)
        toolbar_layout.addWidget(self.italic_btn)
        toolbar_layout.addWidget(self.underline_btn)
        toolbar_layout.addWidget(QFrame())  # Separator
        toolbar_layout.addWidget(QLabel("Size:"))
        toolbar_layout.addWidget(self.font_size_combo)
        toolbar_layout.addStretch()

        # Text editor
        self.text_edit = QTextEdit()
        self.text_edit.textChanged.connect(self._on_text_changed)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.text_edit)

    def _toggle_bold(self):
        """Toggle bold formatting"""
        if self.bold_btn.isChecked():
            self.text_edit.setFontWeight(QFont.Weight.Bold)
        else:
            self.text_edit.setFontWeight(QFont.Weight.Normal)

    def _toggle_italic(self):
        """Toggle italic formatting"""
        self.text_edit.setFontItalic(self.italic_btn.isChecked())

    def _toggle_underline(self):
        """Toggle underline formatting"""
        self.text_edit.setFontUnderline(self.underline_btn.isChecked())

    def _change_font_size(self, size_text: str):
        """Change font size"""
        try:
            size = int(size_text)
            self.text_edit.setFontPointSize(size)
        except ValueError:
            pass

    def _on_text_changed(self):
        """Handle text change"""
        self.text_changed.emit(self.text_edit.toHtml())

    def getText(self) -> str:
        """Get plain text"""
        return self.text_edit.toPlainText()

    def getHtml(self) -> str:
        """Get HTML text"""
        return self.text_edit.toHtml()

    def setText(self, text: str):
        """Set plain text"""
        self.text_edit.setPlainText(text)

    def setHtml(self, html: str):
        """Set HTML text"""
        self.text_edit.setHtml(html)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        # Toolbar style
        toolbar_style = f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                color: {theme.get_color('text_primary').name()};
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('border').name()};
            }}
            QPushButton:checked {{
                background-color: {theme.get_color('primary').name()};
                color: white;
            }}
            QComboBox {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 60px;
            }}
            QLabel {{
                color: {theme.get_color('text_secondary').name()};
                font-size: 12px;
            }}
        """

        # Text editor style
        editor_style = f"""
            QTextEdit {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-top: none;
                color: {theme.get_color('text_primary').name()};
                font-size: 14px;
                font-family: "Segoe UI", sans-serif;
                selection-background-color: {theme.get_color('primary').name()};
                selection-color: white;
            }}
            QTextEdit:focus {{
                border-color: {theme.get_color('primary').name()};
            }}
        """

        self.toolbar.setStyleSheet(toolbar_style)
        self.text_edit.setStyleSheet(editor_style)

        # Widget container style
        self.setStyleSheet(f"""
            FluentRichTextEditor {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
            }}
        """)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentDateTimePicker(QWidget):
    """Fluent Design style date/time picker"""

    date_changed = Signal(QDate)
    time_changed = Signal(QTime)
    datetime_changed = Signal(QDateTime)

    class PickerMode:
        DATE_ONLY = "date"
        TIME_ONLY = "time"
        DATETIME = "datetime"

    def __init__(self, mode: str = PickerMode.DATETIME, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._mode = mode
        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        if self._mode in [self.PickerMode.DATE_ONLY, self.PickerMode.DATETIME]:
            self.date_edit = QDateEdit()
            self.date_edit.setDate(QDate.currentDate())
            self.date_edit.setCalendarPopup(True)
            self.date_edit.dateChanged.connect(self._on_date_changed)
            layout.addWidget(self.date_edit)

        if self._mode in [self.PickerMode.TIME_ONLY, self.PickerMode.DATETIME]:
            self.time_edit = QTimeEdit()
            self.time_edit.setTime(QTime.currentTime())
            self.time_edit.timeChanged.connect(self._on_time_changed)
            layout.addWidget(self.time_edit)

    def _on_date_changed(self, date: QDate):
        """Handle date change"""
        self.date_changed.emit(date)
        if hasattr(self, 'time_edit'):
            datetime = QDateTime(date, self.time_edit.time())
            self.datetime_changed.emit(datetime)

    def _on_time_changed(self, time: QTime):
        """Handle time change"""
        self.time_changed.emit(time)
        if hasattr(self, 'date_edit'):
            datetime = QDateTime(self.date_edit.date(), time)
            self.datetime_changed.emit(datetime)

    def getDate(self) -> QDate:
        """Get selected date"""
        if hasattr(self, 'date_edit'):
            return self.date_edit.date()
        return QDate()

    def getTime(self) -> QTime:
        """Get selected time"""
        if hasattr(self, 'time_edit'):
            return self.time_edit.time()
        return QTime()

    def getDateTime(self) -> QDateTime:
        """Get selected datetime"""
        if hasattr(self, 'date_edit') and hasattr(self, 'time_edit'):
            return QDateTime(self.date_edit.date(), self.time_edit.time())
        elif hasattr(self, 'date_edit'):
            return QDateTime(self.date_edit.date(), QTime())
        elif hasattr(self, 'time_edit'):
            return QDateTime(QDate(), self.time_edit.time())
        return QDateTime()

    def setDate(self, date: QDate):
        """Set date"""
        if hasattr(self, 'date_edit'):
            self.date_edit.setDate(date)

    def setTime(self, time: QTime):
        """Set time"""
        if hasattr(self, 'time_edit'):
            self.time_edit.setTime(time)

    def setDateTime(self, datetime: QDateTime):
        """Set datetime"""
        if hasattr(self, 'date_edit'):
            self.date_edit.setDate(datetime.date())
        if hasattr(self, 'time_edit'):
            self.time_edit.setTime(datetime.time())

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QDateEdit, QTimeEdit {{
                background-color: {theme.get_color('surface').name()};
                border: 2px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                min-width: 120px;
            }}
            QDateEdit:focus, QTimeEdit:focus {{
                border-color: {theme.get_color('primary').name()};
            }}
            QDateEdit:hover, QTimeEdit:hover {{
                border-color: {theme.get_color('primary').lighter(130).name()};
            }}
            QDateEdit::drop-down, QTimeEdit::drop-down {{
                border: none;
                background-color: transparent;
                width: 20px;
            }}
            QDateEdit::down-arrow, QTimeEdit::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {theme.get_color('text_secondary').name()};
                margin-right: 8px;
            }}
            QCalendarWidget {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
            QCalendarWidget QTableView {{
                background-color: {theme.get_color('surface').name()};
                selection-background-color: {theme.get_color('primary').name()};
                selection-color: white;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentSlider(QWidget):
    """Fluent Design style slider with value display"""

    value_changed = Signal(int)

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._orientation = orientation
        self._show_value = True
        self._show_ticks = True

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        if self._orientation == Qt.Orientation.Horizontal:
            layout = QVBoxLayout(self)
        else:
            layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.slider = QSlider(self._orientation)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self._on_value_changed)

        self.value_label = QLabel("50")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setMinimumWidth(40)

        if self._orientation == Qt.Orientation.Horizontal:
            layout.addWidget(self.slider)
            layout.addWidget(self.value_label)
        else:
            layout.addWidget(self.value_label)
            layout.addWidget(self.slider)

    def _on_value_changed(self, value: int):
        """Handle value change"""
        if self._show_value:
            self.value_label.setText(str(value))
        self.value_changed.emit(value)

    def setValue(self, value: int):
        """Set slider value"""
        self.slider.setValue(value)

    def setRange(self, minimum: int, maximum: int):
        """Set value range"""
        self.slider.setRange(minimum, maximum)

    def setShowValue(self, show: bool):
        """Set value display visibility"""
        self._show_value = show
        self.value_label.setVisible(show)

    def value(self) -> int:
        """Get current value"""
        return self.slider.value()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QSlider::groove:horizontal {{
                background-color: {theme.get_color('border').name()};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background-color: {theme.get_color('primary').name()};
                border: 2px solid white;
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: -7px 0;
            }}
            QSlider::handle:horizontal:hover {{
                background-color: {theme.get_color('primary').lighter(110).name()};
            }}
            QSlider::handle:horizontal:pressed {{
                background-color: {theme.get_color('primary').darker(110).name()};
            }}
            QSlider::sub-page:horizontal {{
                background-color: {theme.get_color('primary').name()};
                border-radius: 3px;
            }}
            QSlider::groove:vertical {{
                background-color: {theme.get_color('border').name()};
                width: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:vertical {{
                background-color: {theme.get_color('primary').name()};
                border: 2px solid white;
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: 0 -7px;
            }}
            QSlider::sub-page:vertical {{
                background-color: {theme.get_color('primary').name()};
                border-radius: 3px;
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                font-size: 12px;
                font-weight: 600;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentFileSelector(QWidget):
    """Fluent Design style file selector"""

    file_selected = Signal(str)  # file_path
    files_selected = Signal(list)  # file_paths

    def __init__(self, multi_select: bool = False, file_filter: str = "All Files (*)",
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._multi_select = multi_select
        self._file_filter = file_filter
        self._selected_files = []

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.file_display = QLineEdit()
        self.file_display.setReadOnly(True)
        self.file_display.setPlaceholderText("No file selected")

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.clicked.connect(self._browse_files)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedWidth(60)
        self.clear_btn.clicked.connect(self._clear_selection)
        self.clear_btn.setEnabled(False)

        layout.addWidget(self.file_display)
        layout.addWidget(self.browse_btn)
        layout.addWidget(self.clear_btn)

    def _browse_files(self):
        """Browse for files"""
        if self._multi_select:
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Files", "", self._file_filter)
            if files:
                self._selected_files = files
                self.file_display.setText(f"{len(files)} files selected")
                self.clear_btn.setEnabled(True)
                self.files_selected.emit(files)
        else:
            file, _ = QFileDialog.getOpenFileName(
                self, "Select File", "", self._file_filter)
            if file:
                self._selected_files = [file]
                self.file_display.setText(
                    file.split('/')[-1])  # Show filename only
                self.clear_btn.setEnabled(True)
                self.file_selected.emit(file)

    def _clear_selection(self):
        """Clear file selection"""
        self._selected_files = []
        self.file_display.clear()
        self.file_display.setPlaceholderText("No file selected")
        self.clear_btn.setEnabled(False)

    def getSelectedFiles(self) -> List[str]:
        """Get selected file paths"""
        return self._selected_files.copy()

    def getSelectedFile(self) -> str:
        """Get first selected file path"""
        return self._selected_files[0] if self._selected_files else ""

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QLineEdit {{
                background-color: {theme.get_color('surface').name()};
                border: 2px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
            }}
            QPushButton {{
                background-color: {theme.get_color('primary').name()};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('primary').darker(110).name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('primary').darker(120).name()};
            }}
            QPushButton:disabled {{
                background-color: {theme.get_color('border').name()};
                color: {theme.get_color('text_disabled').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
