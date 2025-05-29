"""
Fluent Design Style Toggle Switch Component
Provides an elegant toggle switch control for binary options
"""

from PySide6.QtWidgets import QWidget, QCheckBox
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QRect, QEasingCurve, Property, QByteArray, QSize
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPaintEvent
from core.theme import theme_manager  # ThemeMode import removed
from typing import Optional


class FluentToggleSwitch(QCheckBox):
    """Fluent Design Style Toggle Switch

    Features:
    - Smooth animation when toggling state
    - Adaptive theme colors
    - Optional label text
    - Customizable enabled/disabled states
    """

    stateChanged = Signal(bool)  # True for checked, False for unchecked
    thumbPositionChanged = Signal()  # Signal for thumbPosition property

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        # Appearance properties
        self._track_height = 14
        self._thumb_size = 18
        self._thumb_margin = 2
        self._thumb_position = 0.0  # Ensure it's float for animation

        # Setup animation
        self._thumb_animation = QPropertyAnimation(
            self, QByteArray(b"thumbPosition"))
        self._thumb_animation.setDuration(150)
        self._thumb_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Connect state changes
        self.clicked.connect(self._handle_toggle)
        if theme_manager:  # Check if theme_manager is available
            theme_manager.theme_changed.connect(self._on_theme_changed)

        # Initial setup
        self.setMinimumWidth(46)
        self._update_thumb_position_from_state()  # Initialize thumb position
        self._on_theme_changed()

    def _update_thumb_position_from_state(self):
        """Update internal thumb position based on checked state without animation."""
        self._thumb_position = 1.0 if self.isChecked() else 0.0
        self.update()

    def _handle_toggle(self):
        """Handle toggle action with animation"""
        self._thumb_animation.stop()
        target_value = 1.0 if self.isChecked() else 0.0
        if self._thumb_position != target_value:  # Only animate if position needs to change
            # Start from current visual position
            self._thumb_animation.setStartValue(self._thumb_position)
            self._thumb_animation.setEndValue(target_value)
            self._thumb_animation.start()
        else:  # If already at target, just ensure internal state is correct and emit signal
            self._set_thumb_position(target_value)
        self.stateChanged.emit(self.isChecked())

    def sizeHint(self) -> QSize:
        """Suggest an appropriate size for the widget"""
        width = 46 if not self.text() else self.fontMetrics(
        ).horizontalAdvance(self.text()) + 46 + 8  # Adjust for text
        height = max(self._thumb_size + self._thumb_margin * 2, 20)
        return QSize(width, height)

    def paintEvent(self, _event: QPaintEvent):  # Renamed event to _event
        """Draw the toggle switch"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = theme_manager  # Assuming theme_manager is always available after __init__ check
        track_width = 32

        # Calculate toggle track rect
        track_rect = QRect(0,
                           (self.height() - self._track_height) // 2,
                           track_width,
                           self._track_height)

        # Draw text if present
        if self.text():
            text_color = theme.get_color('text_primary') if self.isEnabled(
            ) else theme.get_color('text_disabled')
            painter.setPen(QPen(text_color))
            font = painter.font()
            # font.setPointSize(10) # Example: set font size if needed
            painter.setFont(font)

            text_rect = self.rect()
            text_rect.setLeft(track_width + 8)  # Space between toggle and text
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft |
                             Qt.AlignmentFlag.AlignVCenter, self.text())

        # Draw track
        if self.isEnabled():
            if self.isChecked():
                track_color = theme.get_color('primary')
            else:
                track_color = theme.get_color('border')
        else:
            # Use a more distinct disabled color, ensure theme provides 'disabled_bg' or similar
            disabled_track_color_checked = theme.get_color(
                'disabled_bg')  # Or primary.darker(120)
            disabled_track_color_unchecked = theme.get_color(
                'disabled_bg')  # Or border
            track_color = disabled_track_color_checked if self.isChecked(
            ) else disabled_track_color_unchecked

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(
            track_rect, self._track_height // 2, self._track_height // 2)

        # Calculate thumb position
        # The thumb moves from margin to track_width - thumb_size - margin
        thumb_travel_range = track_width - \
            self._thumb_size - (self._thumb_margin * 2)
        thumb_x_offset = self._thumb_margin + \
            (thumb_travel_range * self._thumb_position)

        thumb_y = (self.height() - self._thumb_size) // 2

        # Draw thumb
        if self.isEnabled():
            # Access theme mode directly from theme_manager's attribute
            current_mode_name = theme_manager._current_mode.name if hasattr(
                theme_manager._current_mode, 'name') else "LIGHT"
            thumb_color = QColor(
                "white") if current_mode_name == "LIGHT" else QColor(45, 45, 45)
        else:
            # Use a disabled text or specific thumb disabled color
            thumb_color = theme.get_color('disabled_text')

        painter.setBrush(QBrush(thumb_color))
        painter.setPen(QPen(theme.get_color('border')))  # Thumb border
        painter.drawEllipse(int(thumb_x_offset), int(
            thumb_y), self._thumb_size, self._thumb_size)

        painter.end()

    def _on_theme_changed(self):
        """Handle theme changes"""
        self.update()

    def setChecked(self, checked: bool):
        """Override setChecked to handle animation correctly."""
        current_checked_state = self.isChecked()
        super().setChecked(checked)  # Call base class to update state
        if current_checked_state != checked:  # Only trigger if state actually changed
            self._handle_toggle()  # Trigger animation and emit stateChanged
            self.update()  # Ensure repaint

    def set_checked_without_animation(self, checked: bool):
        """Set checked state without animation and without emitting stateChanged directly from here."""
        is_different = self.isChecked() != checked
        self.blockSignals(True)
        super().setChecked(checked)  # Use super to avoid recursion if we override setChecked
        self._thumb_position = 1.0 if checked else 0.0
        self.blockSignals(False)
        if is_different:  # If state truly changed, update UI and emit our own stateChanged
            self.update()
            # self.stateChanged.emit(checked) # Do not emit here, let setChecked handle it or specific user actions

    # Property for animation
    def _get_thumb_position(self) -> float:
        return self._thumb_position

    def _set_thumb_position(self, pos: float):
        if self._thumb_position != pos:
            self._thumb_position = pos
            self.update()
            self.thumbPositionChanged.emit()  # Emit signal when position changes

    thumbPosition = Property(float, _get_thumb_position,
                             _set_thumb_position, None, "", notify=thumbPositionChanged)
