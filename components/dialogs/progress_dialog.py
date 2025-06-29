"""
FluentProgressDialog - Progress dialogs for long-running operations

Features:
- Determinate and indeterminate progress
- Cancellable operations
- Sub-task progress with details
- Estimated time remaining
- Fluent Design styling
- Real-time updates
- Multiple progress bars for complex operations
"""

from typing import Optional, Callable
from enum import Enum

from PySide6.QtWidgets import (QLabel, QProgressBar, QVBoxLayout, QFrame,
                               QWidget, QHBoxLayout)
from PySide6.QtCore import Signal, QTimer

from .base_dialog import FluentBaseDialog, DialogType, DialogSize, ButtonRole


class ProgressMode(Enum):
    """Progress dialog mode enumeration."""
    DETERMINATE = "determinate"
    INDETERMINATE = "indeterminate"
    SUBTASK = "subtask"


class FluentProgressDialog(FluentBaseDialog):
    """
    A progress dialog with Fluent Design styling.

    Provides progress feedback for long-running operations with
    optional cancellation support.
    """

    # Signals
    cancelled = Signal()
    progress_changed = Signal(int)  # Progress value changed
    detail_changed = Signal(str)   # Detail text changed

    def __init__(self, parent: Optional[QWidget] = None,
                 title: str = "Please wait",
                 message: str = "Processing...",
                 cancelable: bool = True):
        super().__init__(parent, title, DialogType.MODAL, DialogSize.MEDIUM)

        self._message = message
        self._cancelable = cancelable
        self._is_cancelled = False
        self._progress_mode = ProgressMode.DETERMINATE

        # Progress tracking
        self._current_progress = 0
        self._max_progress = 100
        self._detail_text = ""
        self._subtask_text = ""

        # Time estimation
        self._start_time: Optional[float] = None
        self._estimated_total_time: Optional[float] = None

        self._setup_content()
        self._setup_buttons()

        # Auto-hide on completion
        self._auto_close_on_complete = False
        self._auto_close_delay = 2000  # ms

    def _setup_content(self):
        """Setup the progress dialog content."""
        content_frame = QFrame()
        layout = QVBoxLayout(content_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Main message
        self.message_label = QLabel(self._message)
        self.message_label.setObjectName("progressMessage")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        # Main progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("mainProgressBar")
        self.progress_bar.setRange(0, self._max_progress)
        self.progress_bar.setValue(self._current_progress)
        layout.addWidget(self.progress_bar)

        # Detail label
        self.detail_label = QLabel()
        self.detail_label.setObjectName("progressDetail")
        self.detail_label.setWordWrap(True)
        self.detail_label.hide()  # Initially hidden
        layout.addWidget(self.detail_label)

        # Subtask progress (optional)
        self.subtask_frame = QFrame()
        subtask_layout = QVBoxLayout(self.subtask_frame)
        subtask_layout.setContentsMargins(0, 8, 0, 0)
        subtask_layout.setSpacing(8)

        self.subtask_label = QLabel()
        self.subtask_label.setObjectName("subtaskLabel")
        self.subtask_label.setWordWrap(True)
        subtask_layout.addWidget(self.subtask_label)

        self.subtask_progress = QProgressBar()
        self.subtask_progress.setObjectName("subtaskProgressBar")
        self.subtask_progress.setMaximumHeight(8)
        subtask_layout.addWidget(self.subtask_progress)

        layout.addWidget(self.subtask_frame)
        self.subtask_frame.hide()  # Initially hidden

        # Time estimation
        self.time_label = QLabel()
        self.time_label.setObjectName("timeLabel")
        self.time_label.hide()  # Initially hidden
        layout.addWidget(self.time_label)

        self.add_content_widget(content_frame)

        # Apply custom styling
        self._apply_progress_styling()

    def _setup_buttons(self):
        """Setup dialog buttons."""
        if self._cancelable:
            self.cancel_button = self.add_button(
                "Cancel", ButtonRole.CANCEL, self._on_cancel_clicked)

    def _apply_progress_styling(self):
        """Apply custom styling for progress elements."""
        style = """
            #progressMessage {
                font-size: 14px;
                color: var(--text-primary, #323130);
                margin-bottom: 8px;
            }
            
            #mainProgressBar {
                height: 6px;
                border: none;
                border-radius: 3px;
                background-color: var(--control-stroke-default, #e1e1e1);
            }
            
            #mainProgressBar::chunk {
                background-color: var(--accent-default, #0078d4);
                border-radius: 3px;
            }
            
            #progressDetail {
                font-size: 12px;
                color: var(--text-secondary, #605e5c);
                margin-top: 4px;
            }
            
            #subtaskLabel {
                font-size: 12px;
                color: var(--text-secondary, #605e5c);
            }
            
            #subtaskProgressBar {
                height: 4px;
                border: none;
                border-radius: 2px;
                background-color: var(--control-stroke-default, #e1e1e1);
            }
            
            #subtaskProgressBar::chunk {
                background-color: var(--accent-light, #deecf9);
                border-radius: 2px;
            }
            
            #timeLabel {
                font-size: 11px;
                color: var(--text-tertiary, #8a8886);
                margin-top: 8px;
            }
        """

        current_style = self.styleSheet()
        self.setStyleSheet(current_style + style)

    def set_progress_mode(self, mode: ProgressMode):
        """Set the progress mode."""
        self._progress_mode = mode

        if mode == ProgressMode.INDETERMINATE:
            self.progress_bar.setRange(0, 0)  # Indeterminate
        elif mode == ProgressMode.DETERMINATE:
            self.progress_bar.setRange(0, self._max_progress)
        elif mode == ProgressMode.SUBTASK:
            self.subtask_frame.show()

    def set_progress(self, value: int, detail: str = ""):
        """Set progress value and optional detail text."""
        self._current_progress = max(0, min(value, self._max_progress))
        self.progress_bar.setValue(self._current_progress)

        if detail != self._detail_text:
            self._detail_text = detail
            if detail:
                self.detail_label.setText(detail)
                self.detail_label.show()
            else:
                self.detail_label.hide()
            self.detail_changed.emit(detail)

        self.progress_changed.emit(self._current_progress)

        # Update time estimation
        self._update_time_estimation()

        # Auto-complete if at 100%
        if self._current_progress >= self._max_progress:
            self._on_completion()

    def set_subtask_progress(self, value: int, max_value: int, text: str = ""):
        """Set subtask progress."""
        if not self.subtask_frame.isVisible():
            self.subtask_frame.show()

        self.subtask_progress.setRange(0, max_value)
        self.subtask_progress.setValue(value)

        if text != self._subtask_text:
            self._subtask_text = text
            self.subtask_label.setText(text)

    def set_message(self, message: str):
        """Update the main message."""
        self._message = message
        self.message_label.setText(message)

    def set_detail(self, detail: str):
        """Set detail text."""
        self.set_progress(self._current_progress, detail)

    def set_range(self, min_value: int, max_value: int):
        """Set progress range."""
        self._max_progress = max_value
        self.progress_bar.setRange(min_value, max_value)

    def start_timing(self):
        """Start time estimation."""
        import time
        self._start_time = time.time()
        self.time_label.show()

    def _update_time_estimation(self):
        """Update time estimation display."""
        if not self._start_time or self._current_progress == 0:
            return

        import time
        elapsed = time.time() - self._start_time

        if self._current_progress > 0:
            # Estimate total time based on current progress
            progress_ratio = self._current_progress / self._max_progress
            estimated_total = elapsed / progress_ratio
            remaining = estimated_total - elapsed

            if remaining > 0:
                if remaining < 60:
                    time_text = f"About {int(remaining)} seconds remaining"
                elif remaining < 3600:
                    minutes = int(remaining / 60)
                    time_text = f"About {minutes} minute{'s' if minutes != 1 else ''} remaining"
                else:
                    hours = int(remaining / 3600)
                    time_text = f"About {hours} hour{'s' if hours != 1 else ''} remaining"

                self.time_label.setText(time_text)

    def _on_completion(self):
        """Handle progress completion."""
        if self._auto_close_on_complete:
            QTimer.singleShot(self._auto_close_delay, self.accept)
        else:
            # Update to completion state
            if self._cancelable:
                self.cancel_button.setText("Close")

    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        if self._current_progress >= self._max_progress:
            # Progress complete, close dialog
            self.accept()
        else:
            # Cancel operation
            self._is_cancelled = True
            self.cancelled.emit()
            self.reject()

    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self._is_cancelled

    def set_auto_close_on_complete(self, auto_close: bool, delay: int = 2000):
        """Set whether to auto-close on completion."""
        self._auto_close_on_complete = auto_close
        self._auto_close_delay = delay

    def accept(self):
        """Accept the dialog."""
        self.close_animated(self.DialogCode.Accepted)

    def reject(self):
        """Reject the dialog."""
        self.close_animated(self.DialogCode.Rejected)


def show_progress_dialog(parent: Optional[QWidget] = None,
                         title: str = "Please wait",
                         message: str = "Processing...",
                         cancelable: bool = True,
                         indeterminate: bool = False) -> FluentProgressDialog:
    """
    Show a progress dialog.

    Args:
        parent: Parent widget
        title: Dialog title
        message: Progress message
        cancelable: Whether operation can be cancelled
        indeterminate: Whether progress is indeterminate

    Returns:
        FluentProgressDialog instance
    """
    dialog = FluentProgressDialog(parent, title, message, cancelable)

    if indeterminate:
        dialog.set_progress_mode(ProgressMode.INDETERMINATE)

    dialog.show_animated()
    return dialog


class ProgressContext:
    """Context manager for progress dialogs."""

    def __init__(self, parent: Optional[QWidget] = None,
                 title: str = "Please wait",
                 message: str = "Processing...",
                 cancelable: bool = True):
        self.dialog = FluentProgressDialog(parent, title, message, cancelable)
        self.dialog.start_timing()

    def __enter__(self) -> FluentProgressDialog:
        self.dialog.show_animated()
        return self.dialog

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.dialog.is_cancelled():
            self.dialog.set_progress(100)
            if exc_type is None:
                # Success
                QTimer.singleShot(500, self.dialog.accept)
            else:
                # Error occurred
                self.dialog.set_message("An error occurred.")
                self.dialog.set_detail(
                    str(exc_val) if exc_val else "Unknown error")
                QTimer.singleShot(2000, self.dialog.reject)
