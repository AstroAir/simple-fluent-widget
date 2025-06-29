"""
FluentContentDialog - A modal dialog container following Fluent Design principles

Features:
- Modal overlay with backdrop
- Fluent Design styling with proper elevation
- Customizable title and content areas
- Primary and secondary action buttons
- Keyboard navigation and ESC key support
- Smooth entrance/exit animations
- Theme-aware styling
"""

from typing import Optional, Callable
from PySide6.QtWidgets import QLabel, QWidget, QDialog
from PySide6.QtCore import Signal

from .base_dialog import FluentBaseDialog, DialogType, DialogSize, ButtonRole


class FluentContentDialog(FluentBaseDialog):
    """
    A modal dialog container with Fluent Design styling.

    Provides a modern dialog interface with proper backdrop, elevation,
    and smooth animations following Fluent Design principles.
    """

    # Signals
    primary_button_clicked = Signal()
    secondary_button_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None, title: str = "", content: str = ""):
        super().__init__(parent, title, DialogType.MODAL, DialogSize.MEDIUM)

        self._content = content
        self._primary_button_text = "OK"
        self._secondary_button_text = "Cancel"
        self._primary_button_callback: Optional[Callable] = None
        self._secondary_button_callback: Optional[Callable] = None

        self._init_content()
        self._init_buttons()

    def _init_content(self):
        """Initialize the content area."""
        if self._content:
            self.content_label = QLabel(self._content)
            self.content_label.setObjectName("contentLabel")
            self.content_label.setWordWrap(True)
            self.add_content_widget(self.content_label)

    def _init_buttons(self):
        """Initialize dialog buttons."""
        # Add secondary button (Cancel)
        self.secondary_button = self.add_button(
            self._secondary_button_text,
            ButtonRole.CANCEL,
            self._on_secondary_clicked
        )

        # Add primary button (OK)
        self.primary_button = self.add_button(
            self._primary_button_text,
            ButtonRole.PRIMARY,
            self._on_primary_clicked
        )

    def _on_primary_clicked(self):
        """Handle primary button click."""
        self.primary_button_clicked.emit()
        if self._primary_button_callback:
            self._primary_button_callback()
        self.accept()

    def _on_secondary_clicked(self):
        """Handle secondary button click."""
        self.secondary_button_clicked.emit()
        if self._secondary_button_callback:
            self._secondary_button_callback()
        self.reject()

    def accept(self):
        """Accept the dialog."""
        self.close_animated(QDialog.DialogCode.Accepted)

    def reject(self):
        """Reject the dialog."""
        self.close_animated(QDialog.DialogCode.Rejected)

    # Property setters and getters
    def set_content(self, content: str):
        """Set dialog content."""
        self._content = content
        if hasattr(self, 'content_label'):
            self.content_label.setText(content)

    def set_primary_button_text(self, text: str):
        """Set primary button text."""
        self._primary_button_text = text
        if hasattr(self, 'primary_button'):
            self.primary_button.setText(text)

    def set_secondary_button_text(self, text: str):
        """Set secondary button text."""
        self._secondary_button_text = text
        if hasattr(self, 'secondary_button'):
            self.secondary_button.setText(text)

    def set_primary_button_callback(self, callback: Callable):
        """Set primary button callback."""
        self._primary_button_callback = callback

    def set_secondary_button_callback(self, callback: Callable):
        """Set secondary button callback."""
        self._secondary_button_callback = callback


def show_content_dialog(parent: Optional[QWidget] = None,
                        title: str = "Dialog",
                        content: str = "",
                        primary_text: str = "OK",
                        secondary_text: str = "Cancel",
                        primary_callback: Optional[Callable] = None,
                        secondary_callback: Optional[Callable] = None) -> FluentContentDialog:
    """
    Convenience function to show a content dialog.

    Args:
        parent: Parent widget
        title: Dialog title
        content: Dialog content text
        primary_text: Primary button text
        secondary_text: Secondary button text
        primary_callback: Callback for primary button
        secondary_callback: Callback for secondary button

    Returns:
        FluentContentDialog instance
    """
    dialog = FluentContentDialog(parent, title, content)
    dialog.set_primary_button_text(primary_text)
    dialog.set_secondary_button_text(secondary_text)

    if primary_callback:
        dialog.set_primary_button_callback(primary_callback)
    if secondary_callback:
        dialog.set_secondary_button_callback(secondary_callback)

    dialog.show_animated()
    return dialog
