"""
Fluent Design Style Text Input Components
"""

from PySide6.QtWidgets import QLineEdit, QTextEdit, QWidget, QVBoxLayout
from PySide6.QtCore import Signal, QPropertyAnimation, QByteArray
from PySide6.QtGui import QFocusEvent
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional


class FluentLineEdit(QLineEdit):
    """Fluent Design Style Single Line Text Input"""

    def __init__(self, parent: Optional[QWidget] = None,
                 placeholder: str = ""):
        super().__init__(parent)

        self._is_focused = False
        self._border_animation = None

        # Set basic properties
        if placeholder:
            self.setPlaceholderText(placeholder)

        self.setMinimumHeight(32)
        self._apply_style()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _apply_style(self):
        """Apply style"""
        theme = theme_manager

        style_sheet = f"""
            FluentLineEdit {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()}40;
            }}
            FluentLineEdit:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
                padding: 7px 11px;
            }}
            FluentLineEdit:disabled {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_disabled').name()};
                border-color: {theme.get_color('text_disabled').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def focusInEvent(self, event: QFocusEvent):
        """Focus in event with animation effect"""
        self._is_focused = True

        # Create border animation
        if not self._border_animation:
            self._border_animation = QPropertyAnimation(
                self, QByteArray(b"geometry"))
            self._border_animation.setDuration(FluentAnimation.DURATION_FAST)
            self._border_animation.setEasingCurve(FluentAnimation.EASE_OUT)

        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        """Focus out event with animation effect"""
        self._is_focused = False
        super().focusOutEvent(event)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._apply_style()


class FluentTextEdit(QTextEdit):
    """Fluent Design Style Multi-line Text Input"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._apply_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _apply_style(self):
        """Apply style"""
        theme = theme_manager

        style_sheet = f"""
            FluentTextEdit {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()}40;
            }}
            FluentTextEdit:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._apply_style()


class FluentPasswordEdit(FluentLineEdit):
    """Password Input Field"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent, "Enter password")
        self.setEchoMode(QLineEdit.EchoMode.Password)


class FluentSearchBox(QWidget):
    """Search Box Component"""

    search_triggered = Signal(str)
    text_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._setup_ui()
        self._apply_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.line_edit = FluentLineEdit(placeholder="Search...")
        layout.addWidget(self.line_edit)

        # Connect signals
        self.line_edit.textChanged.connect(self.text_changed.emit)
        self.line_edit.returnPressed.connect(
            lambda: self.search_triggered.emit(self.line_edit.text())
        )

    def _apply_style(self):
        """Apply search box style"""
        # Add search icon
        icon_style = f"""
            background-image: url(:/icons/search.svg);
            background-repeat: no-repeat;
            background-position: left center;
            padding-left: 32px;
        """

        current_style = self.line_edit.styleSheet()
        self.line_edit.setStyleSheet(current_style + icon_style)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._apply_style()

    def text(self) -> str:
        """Get text content"""
        return self.line_edit.text()

    def set_text(self, text: str):
        """Set text content"""
        self.line_edit.setText(text)

    def clear(self):
        """Clear text"""
        self.line_edit.clear()
