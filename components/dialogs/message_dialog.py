"""
FluentMessageDialog - Simple message dialogs following Fluent Design principles

Features:
- Simple message display with icon support
- Fluent Design styling with proper elevation
- Common dialog types (Information, Warning, Error, Question)
- Customizable buttons with built-in presets
- Keyboard navigation support
- Theme-aware styling
"""

from typing import Optional, Callable
from enum import Enum
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QFrame, QDialog
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor

from .base_dialog import FluentBaseDialog, DialogType, DialogSize, ButtonRole


class MessageType(Enum):
    """Message dialog type enumeration."""
    INFORMATION = "information"
    WARNING = "warning"
    ERROR = "error"
    QUESTION = "question"
    SUCCESS = "success"


class MessageResult(Enum):
    """Message dialog result enumeration."""
    OK = "ok"
    CANCEL = "cancel"
    YES = "yes"
    NO = "no"
    CLOSE = "close"


class FluentMessageDialog(FluentBaseDialog):
    """
    A simple message dialog with Fluent Design styling.

    Provides preset dialog types with appropriate icons and styling
    following Fluent Design principles.
    """

    # Signals
    result_ready = Signal(str)  # Emits the result as string

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent, "", DialogType.MODAL, DialogSize.SMALL)

        self._message_type = MessageType.INFORMATION
        self._message_text = ""
        self._result_callback: Optional[Callable] = None

        # Remove default title padding since we'll have our own layout
        self.container_layout.setContentsMargins(24, 16, 24, 24)

    def show_message(self,
                     title: str,
                     message: str,
                     message_type: MessageType = MessageType.INFORMATION,
                     result_callback: Optional[Callable] = None) -> int:
        """
        Show a message dialog.

        Args:
            title: Dialog title
            message: Message content
            message_type: Type of dialog (determines icon and buttons)
            result_callback: Callback function for result

        Returns:
            Dialog result code
        """
        self._message_type = message_type
        self._message_text = message
        self._result_callback = result_callback

        self.set_title(title)
        self._setup_content()
        self._setup_buttons_for_type(message_type)

        return self.exec()

    def _setup_content(self):
        """Setup the dialog content with icon and message"""
        # Clear existing content
        for widget in self._content_widgets:
            self.remove_content_widget(widget)

        # Create content container with icon and message
        content_frame = QFrame()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        # Add icon
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_pixmap = self._get_icon_for_type(
            self._message_type).pixmap(32, 32)
        icon_label.setPixmap(icon_pixmap)
        content_layout.addWidget(icon_label)

        # Add message
        message_label = QLabel(self._message_text)
        message_label.setWordWrap(True)
        message_label.setObjectName("messageLabel")
        content_layout.addWidget(message_label, 1)

        self.add_content_widget(content_frame)

    def _get_icon_for_type(self, message_type: MessageType) -> QIcon:
        """Get appropriate icon for message type."""
        # Create simple colored circle icons for different types
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color_map = {
            MessageType.INFORMATION: QColor("#0078d4"),
            MessageType.WARNING: QColor("#f7b500"),
            MessageType.ERROR: QColor("#d13438"),
            MessageType.QUESTION: QColor("#0078d4"),
            MessageType.SUCCESS: QColor("#107c10"),
        }

        color = color_map.get(message_type, QColor("#0078d4"))
        painter.setBrush(color)
        painter.setPen(QColor(0, 0, 0, 0))  # No pen
        painter.drawEllipse(4, 4, 24, 24)

        # Add symbol based on type
        painter.setPen(QColor("white"))
        painter.setFont(painter.font())

        symbol_map = {
            MessageType.INFORMATION: "i",
            MessageType.WARNING: "!",
            MessageType.ERROR: "×",
            MessageType.QUESTION: "?",
            MessageType.SUCCESS: "✓",
        }

        symbol = symbol_map.get(message_type, "i")
        painter.drawText(16 - 4, 16 + 4, symbol)
        painter.end()

        return QIcon(pixmap)

    def _setup_buttons_for_type(self, message_type: MessageType):
        """Setup appropriate buttons for message type."""
        # Clear existing buttons
        for role, button in self._buttons.items():
            button.setParent(None)
        self._buttons.clear()

        if message_type == MessageType.QUESTION:
            self.add_button("No", ButtonRole.CANCEL,
                            lambda: self._finish_with_result(MessageResult.NO))
            self.add_button("Yes", ButtonRole.PRIMARY,
                            lambda: self._finish_with_result(MessageResult.YES))
        elif message_type == MessageType.ERROR:
            self.add_button("OK", ButtonRole.PRIMARY,
                            lambda: self._finish_with_result(MessageResult.OK))
        else:
            self.add_button("Cancel", ButtonRole.CANCEL,
                            lambda: self._finish_with_result(MessageResult.CANCEL))
            self.add_button("OK", ButtonRole.PRIMARY,
                            lambda: self._finish_with_result(MessageResult.OK))

    def _finish_with_result(self, result: MessageResult):
        """Finish dialog with specific result."""
        self.result_ready.emit(result.value)
        if self._result_callback:
            self._result_callback(result)

        if result in (MessageResult.OK, MessageResult.YES):
            self.accept()
        else:
            self.reject()

    def accept(self):
        """Accept the dialog."""
        self.close_animated(QDialog.DialogCode.Accepted)

    def reject(self):
        """Reject the dialog."""
        self.close_animated(QDialog.DialogCode.Rejected)


# Convenience functions for common dialog types
def show_information_dialog(parent: Optional[QWidget] = None,
                            title: str = "Information",
                            message: str = "",
                            callback: Optional[Callable] = None) -> FluentMessageDialog:
    """Show an information dialog."""
    dialog = FluentMessageDialog(parent)
    dialog.show_message(title, message, MessageType.INFORMATION, callback)
    return dialog


def show_warning_dialog(parent: Optional[QWidget] = None,
                        title: str = "Warning",
                        message: str = "",
                        callback: Optional[Callable] = None) -> FluentMessageDialog:
    """Show a warning dialog."""
    dialog = FluentMessageDialog(parent)
    dialog.show_message(title, message, MessageType.WARNING, callback)
    return dialog


def show_error_dialog(parent: Optional[QWidget] = None,
                      title: str = "Error",
                      message: str = "",
                      callback: Optional[Callable] = None) -> FluentMessageDialog:
    """Show an error dialog."""
    dialog = FluentMessageDialog(parent)
    dialog.show_message(title, message, MessageType.ERROR, callback)
    return dialog


def show_question_dialog(parent: Optional[QWidget] = None,
                         title: str = "Question",
                         message: str = "",
                         callback: Optional[Callable] = None) -> FluentMessageDialog:
    """Show a question dialog."""
    dialog = FluentMessageDialog(parent)
    dialog.show_message(title, message, MessageType.QUESTION, callback)
    return dialog


def show_success_dialog(parent: Optional[QWidget] = None,
                        title: str = "Success",
                        message: str = "",
                        callback: Optional[Callable] = None) -> FluentMessageDialog:
    """Show a success dialog."""
    dialog = FluentMessageDialog(parent)
    dialog.show_message(title, message, MessageType.SUCCESS, callback)
    return dialog
