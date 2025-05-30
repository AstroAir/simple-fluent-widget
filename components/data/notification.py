"""
Fluent Design Style Information and Status Components
Enhanced notification systems and complex status indicators
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                               QGraphicsOpacityEffect, QSizePolicy, QPushButton)
from PySide6.QtCore import (Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve,
                            QByteArray, Property, QEvent)
from PySide6.QtGui import (QPainter, QColor, QBrush,
                           QPen, QPaintEvent, QRadialGradient)
from core.theme import theme_manager
from core.enhanced_animations import FluentTransition, FluentMicroInteraction
from typing import Optional
from enum import Enum


class FluentToast(QFrame):
    """**Fluent Design Toast Notification**

    Features:
    - Multiple notification types (info, success, warning, error)
    - Auto-dismiss with configurable duration
    - Optional action button
    - Smooth fade in/out animations
    """

    class ToastType(Enum):
        """Toast notification types"""
        INFO = "info"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"

    closed = Signal()
    action_triggered = Signal()

    def __init__(self, parent: Optional[QWidget] = None,
                 title: str = "", message: str = "",
                 toast_type: ToastType = ToastType.INFO,
                 duration: int = 4000,
                 action_text: str = ""):
        super().__init__(parent)

        self._title = title
        self._message = message
        self._toast_type = toast_type
        self._duration = duration
        self._action_text = action_text

        # Setup UI
        self._setup_ui()

        # Setup appearance
        self._setup_appearance()

        # Setup animations
        self._setup_animations()

        # Setup auto-dismiss timer
        if duration > 0:
            self._timer = QTimer(self)
            self._timer.setSingleShot(True)
            self._timer.timeout.connect(self.dismiss)
        else:
            self._timer = None

    def _setup_ui(self):
        """Setup toast UI components"""
        # Main layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 12, 16, 12)
        self._layout.setSpacing(8)

        # Header layout (icon + title)
        self._header_layout = QHBoxLayout()
        self._header_layout.setContentsMargins(0, 0, 0, 0)
        self._header_layout.setSpacing(8)

        # Icon label
        self._icon_label = QLabel(self)
        self._icon_label.setFixedSize(16, 16)
        self._header_layout.addWidget(self._icon_label)

        # Title label
        self._title_label = QLabel(self._title, self)
        font = self._title_label.font()
        font.setBold(True)
        self._title_label.setFont(font)
        self._header_layout.addWidget(self._title_label)

        # Close button
        self._close_button = QPushButton("✕", self)
        self._close_button.setFixedSize(16, 16)
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_button.clicked.connect(self.dismiss)
        self._header_layout.addWidget(self._close_button)

        # Message label
        self._message_label = QLabel(self._message, self)
        self._message_label.setWordWrap(True)

        # Action button (if action text provided)
        if self._action_text:
            self._action_button = QPushButton(self._action_text, self)
            self._action_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self._action_button.clicked.connect(self._on_action_triggered)
            self._action_layout = QHBoxLayout()
            self._action_layout.setContentsMargins(0, 0, 0, 0)
            self._action_layout.addStretch()
            self._action_layout.addWidget(self._action_button)
        else:
            self._action_button = None
            self._action_layout = None

        # Add layouts to main layout
        self._layout.addLayout(self._header_layout)
        self._layout.addWidget(self._message_label)
        if self._action_button and self._action_layout:
            self._layout.addLayout(self._action_layout)

        # Set frame properties
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setMinimumWidth(300)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Minimum)

    def _setup_appearance(self):
        """Setup toast appearance based on type"""
        theme = theme_manager

        # Set icon and colors based on toast type
        icon_char = "ℹ"
        border_color = theme.get_color('primary').name()
        bg_color = theme.get_color('accent_light').name()

        if self._toast_type == FluentToast.ToastType.INFO:
            icon_char = "ℹ"
            border_color = theme.get_color('primary').name()
            bg_color = theme.get_color('accent_light').name()
        elif self._toast_type == FluentToast.ToastType.SUCCESS:
            icon_char = "✓"
            border_color = "#0f7b0f"  # Green
            bg_color = "#e6f7e6"      # Light green
        elif self._toast_type == FluentToast.ToastType.WARNING:
            icon_char = "⚠"
            border_color = "#ffc83d"  # Amber
            bg_color = "#fff8e6"      # Light amber
        elif self._toast_type == FluentToast.ToastType.ERROR:
            icon_char = "✕"
            border_color = "#e81123"  # Red
            bg_color = "#fde7e9"      # Light red

        # Set icon
        font = self._icon_label.font()
        font.setPointSize(12)
        self._icon_label.setFont(font)
        self._icon_label.setText(icon_char)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set style
        style_sheet = f"""
            FluentToast {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-left: 4px solid {border_color};
                border-radius: 4px;
            }}
            
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                background-color: transparent;
                border: none;
            }}
            
            QPushButton#closeButton {{
                background-color: transparent;
                color: {theme.get_color('text_secondary').name()};
                border: none;
                border-radius: 8px;
                font-size: 12px;
            }}
            
            QPushButton#closeButton:hover {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
            
            QPushButton#actionButton {{
                background-color: transparent;
                color: {theme.get_color('primary').name()};
                border: none;
                padding: 4px 8px;
                font-weight: bold;
            }}
            
            QPushButton#actionButton:hover {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
        """

        # Apply style
        self.setStyleSheet(style_sheet)

        if self._action_button:
            self._action_button.setObjectName("actionButton")
        self._close_button.setObjectName("closeButton")

    def _setup_animations(self):
        """Setup enhanced entrance and exit animations"""
        # Create opacity effect
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        # Create fade in animation with spring easing
        self._fade_in_anim = FluentTransition.create_transition(
            self,
            FluentTransition.FADE,
            duration=300,
            easing=FluentTransition.EASE_SPRING
        )
        self._fade_in_anim.setStartValue(0.0)
        self._fade_in_anim.setEndValue(1.0)

        # Create fade out animation with elastic easing
        self._fade_out_anim = FluentTransition.create_transition(
            self,
            FluentTransition.FADE,
            duration=300,
            easing=FluentTransition.EASE_ELASTIC
        )
        self._fade_out_anim.setStartValue(1.0)
        self._fade_out_anim.setEndValue(0.0)
        self._fade_out_anim.finished.connect(self._on_fade_out_finished)

        # Add micro-interaction to close button
        self._close_button.installEventFilter(self)

    def show(self):
        """Show toast with animation"""
        super().show()
        self._fade_in_anim.start()

        # Start auto-dismiss timer if needed
        if self._timer and self._duration > 0:
            self._timer.start(self._duration)

    def dismiss(self):
        """Dismiss toast with animation"""
        if self._timer and self._timer.isActive():
            self._timer.stop()

        self._fade_out_anim.start()

    def _on_action_triggered(self):
        """Handle action button click"""
        self.action_triggered.emit()
        self.dismiss()

    def _on_fade_out_finished(self):
        """Handle fade out animation completion"""
        self.hide()
        self.closed.emit()
        self.deleteLater()

    def eventFilter(self, obj, event):
        """Handle micro-interactions for close button"""
        if obj == self._close_button:
            if event.type() == QEvent.Type.Enter:
                FluentMicroInteraction.hover_glow(obj, intensity=0.3).start()
            elif event.type() == QEvent.Type.Leave:
                FluentMicroInteraction.hover_glow(obj, intensity=0.0).start()
            elif event.type() == QEvent.Type.MouseButtonPress:
                FluentMicroInteraction.button_press(obj, scale=0.95)
        return super().eventFilter(obj, event)

    def set_message(self, message: str):
        """Update message text"""
        self._message = message
        self._message_label.setText(message)

    def set_title(self, title: str):
        """Update title text"""
        self._title = title
        self._title_label.setText(title)


class FluentNotificationCenter(QWidget):
    """Fluent Design Style Notification Center

    Features:
    - Centralized notification management
    - Stacked notifications with proper spacing
    - Position control (top-right, bottom-right, etc.)
    - Notification queue with priority
    """

    class Position(Enum):
        """Notification position options"""
        TOP_RIGHT = 0
        TOP_LEFT = 1
        BOTTOM_RIGHT = 2
        BOTTOM_LEFT = 3
        TOP_CENTER = 4
        BOTTOM_CENTER = 5

    def __init__(self, parent: Optional[QWidget] = None,
                 position: Position = Position.TOP_RIGHT,
                 max_visible: int = 5,
                 spacing: int = 10):
        super().__init__(parent)

        self._position = position
        self._max_visible = max_visible
        self._spacing = spacing
        self._notifications = []  # Active notifications
        self._queue = []          # Queued notifications

        # Setup UI
        self._setup_ui()

        # No background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Hide by default
        self.hide()

    def _setup_ui(self):
        """Setup notification center UI"""
        # Main layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(self._spacing)

        # Add stretch based on position
        if self._position in [self.Position.BOTTOM_RIGHT, self.Position.BOTTOM_LEFT, self.Position.BOTTOM_CENTER]:
            self._layout.addStretch()

    def _calculate_position(self):
        """Calculate position based on parent and selected position"""
        parent = self.parent()
        if not parent or not isinstance(parent, QWidget):
            return

        # Get parent geometry
        parent_rect = parent.rect()

        # Calculate position
        x = 20  # default value
        y = 20  # default value

        if self._position == self.Position.TOP_RIGHT:
            x = parent_rect.width() - self.width() - 20
            y = 20
        elif self._position == self.Position.TOP_LEFT:
            x = 20
            y = 20
        elif self._position == self.Position.BOTTOM_RIGHT:
            x = parent_rect.width() - self.width() - 20
            y = parent_rect.height() - self.height() - 20
        elif self._position == self.Position.BOTTOM_LEFT:
            x = 20
            y = parent_rect.height() - self.height() - 20
        elif self._position == self.Position.TOP_CENTER:
            x = (parent_rect.width() - self.width()) // 2
            y = 20
        elif self._position == self.Position.BOTTOM_CENTER:
            x = (parent_rect.width() - self.width()) // 2
            y = parent_rect.height() - self.height() - 20

        # Set position
        self.move(x, y)

    def show_notification(self, title: str, message: str,
                          toast_type: FluentToast.ToastType = FluentToast.ToastType.INFO,
                          duration: int = 4000, action_text: str = "",
                          priority: bool = False):
        """Show notification

        Args:
            title: Notification title
            message: Notification message
            toast_type: Notification type (INFO, SUCCESS, WARNING, ERROR)
            duration: Auto-dismiss duration in ms (0 for no auto-dismiss)
            action_text: Optional action button text
            priority: Whether to show immediately, bypassing queue
        """
        # Create toast
        toast = FluentToast(
            self, title, message, toast_type, duration, action_text
        )

        # Connect signals
        toast.closed.connect(lambda: self._remove_notification(toast))

        # If we can show it now
        if len(self._notifications) < self._max_visible or priority:
            self._add_notification(toast, priority)
        else:
            # Add to queue
            self._queue.append(toast)

    def _add_notification(self, toast: FluentToast, priority: bool = False):
        """Add notification to display"""
        if priority and len(self._notifications) >= self._max_visible:
            # Remove oldest notification to make room
            oldest = self._notifications[0]
            oldest.dismiss()

        # Add to layout and list
        if self._position in [self.Position.BOTTOM_RIGHT, self.Position.BOTTOM_LEFT, self.Position.BOTTOM_CENTER]:
            self._layout.insertWidget(self._layout.count() - 1, toast)
        else:
            self._layout.addWidget(toast)

        self._notifications.append(toast)

        # Show notification and notification center
        if not self.isVisible():
            self.show()
            self._calculate_position()

        toast.show()

    def _remove_notification(self, toast: FluentToast):
        """Remove notification from display"""
        if toast in self._notifications:
            self._notifications.remove(toast)
            self._layout.removeWidget(toast)

            # Process queue if any
            if self._queue and len(self._notifications) < self._max_visible:
                next_toast = self._queue.pop(0)
                self._add_notification(next_toast)

            # Hide notification center if empty
            if not self._notifications:
                self.hide()

    def set_position(self, position: Position):
        """Set notification center position"""
        self._position = position

        # Reconfigure layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self._spacing)

        # Add stretch based on new position
        if self._position in [self.Position.BOTTOM_RIGHT, self.Position.BOTTOM_LEFT, self.Position.BOTTOM_CENTER]:
            self._layout.addStretch()

            # Move active notifications
            for toast in self._notifications:
                self._layout.removeWidget(toast)
                layout.insertWidget(layout.count() - 1, toast)
        else:
            # Move active notifications
            for toast in self._notifications:
                self._layout.removeWidget(toast)
                layout.addWidget(toast)

        # Set new layout
        self._layout = layout
        self.setLayout(layout)

        # Recalculate position
        if self.isVisible():
            self._calculate_position()

    def clear_all(self):
        """Clear all notifications"""
        # Dismiss active notifications
        # Use copy to avoid modification during iteration
        for toast in self._notifications[:]:
            toast.dismiss()

        # Clear queue
        self._queue.clear()


class FluentStatusBadge(QWidget):
    """Fluent Design Style Status Badge

    Features:
    - Multiple status types (online, busy, away, offline, custom)
    - Animated transitions between states
    - Customizable colors and sizes
    """

    class Status(Enum):
        """Status types"""
        ONLINE = "online"
        BUSY = "busy"
        AWAY = "away"
        OFFLINE = "offline"
        CUSTOM = "custom"

    def __init__(self, parent: Optional[QWidget] = None,
                 status: Status = Status.OFFLINE,
                 size: int = 12,
                 animated: bool = True,
                 show_border: bool = True):
        super().__init__(parent)

        self._status = status
        self._size = size
        self._animated = animated
        self._show_border = show_border
        self._custom_color = None
        self._pulse_value = 0.0

        # Set size
        border = 2 if show_border else 0
        self.setFixedSize(size + border * 2, size + border * 2)

        # Setup animation if enabled
        if animated:
            self._setup_animation()

        # Update color mappings when theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animation(self):
        """Setup enhanced pulse animation with spring effect"""
        self._animation = QPropertyAnimation(self, QByteArray(b"pulseValue"))
        self._animation.setDuration(2000)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.setLoopCount(-1)
        self._animation.setEasingCurve(FluentTransition.EASE_SPRING)

        # Start animation for animated statuses
        if self._status in [self.Status.ONLINE, self.Status.BUSY]:
            self._animation.start()

    def paintEvent(self, event: QPaintEvent):
        """Paint the status badge"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get colors based on status
        if self._status == self.Status.CUSTOM and self._custom_color:
            color = self._custom_color
        else:
            color = self._get_status_color(self._status)

        # Paint border if enabled
        if self._show_border:
            border_width = 2
            # Border color based on theme
            border_color = QColor("white")

            painter.setPen(QPen(border_color, border_width))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(1, 1, self.width() - 2, self.height() - 2)

        # Calculate inner circle position
        border = 2 if self._show_border else 0
        x = border
        y = border
        w = self._size
        h = self._size

        # Paint status indicator
        if self._animated and (self._status == self.Status.ONLINE or self._status == self.Status.BUSY):
            # Create gradient for animated pulse effect
            gradient = QRadialGradient(x + w / 2, y + h / 2, w / 2)

            # Pulse effect based on animation value
            base_opacity = 0.7 + 0.3 * (1.0 - self._pulse_value)
            gradient.setColorAt(
                0, QColor(color.red(), color.green(), color.blue(), 255))
            gradient.setColorAt(0.7, QColor(
                color.red(), color.green(), color.blue(), int(255 * base_opacity)))
            gradient.setColorAt(1, QColor(
                color.red(), color.green(), color.blue(), int(255 * base_opacity * 0.5)))

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
        else:
            # Solid color for non-animated statuses
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)

        # Draw status indicator
        painter.drawEllipse(x, y, w, h)
        painter.end()

    def _get_status_color(self, status: Status) -> QColor:
        """Get color for status"""
        theme = theme_manager

        if status == self.Status.ONLINE:
            return QColor("#0f7b0f")  # Green
        elif status == self.Status.BUSY:
            return QColor("#e81123")  # Red
        elif status == self.Status.AWAY:
            return QColor("#ffc83d")  # Amber
        elif status == self.Status.OFFLINE:
            return QColor(theme.get_color('border').darker(120).name())
        else:
            return QColor(theme.get_color('primary').name())

    def set_status(self, status: Status, color: Optional[QColor] = None):
        """Set status and optionally custom color for custom status"""
        prev_status = self._status
        self._status = status

        if status == self.Status.CUSTOM:
            self._custom_color = color or QColor(
                theme_manager.get_color('primary'))

        # Update animation state
        if self._animated:
            was_animated = prev_status in [
                self.Status.ONLINE, self.Status.BUSY]
            will_animate = status in [self.Status.ONLINE, self.Status.BUSY]

            if not was_animated and will_animate:
                self._animation.start()
            elif was_animated and not will_animate:
                self._animation.stop()

        self.update()

    def _on_theme_changed(self):
        """Handle theme changes"""
        self.update()

    # Property for animation
    def _get_pulse_value(self):
        return self._pulse_value

    def _set_pulse_value(self, value):
        self._pulse_value = value
        self.update()

    pulseValue = Property(float, _get_pulse_value, _set_pulse_value, "", "")
