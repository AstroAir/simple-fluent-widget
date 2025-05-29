"""
Fluent Design Style Badge and Tag Components
Badges, tags and status indicators for informational displays
"""

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy, QPushButton
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from core.theme import theme_manager, ThemeMode
from core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                      FluentRevealEffect, FluentSequence)
from typing import Optional


class FluentBadge(QWidget):
    """Fluent Design Style Badge

    Features:
    - Multiple badge types (default, info, success, warning, error)
    - Customizable content (text or count)
    - Dot mode for simple status indication
    - Enhanced animations and interactions
    """

    class BadgeType:
        DEFAULT = "default"
        INFO = "info"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"

    def __init__(self, parent: Optional[QWidget] = None,
                 badge_type: str = BadgeType.DEFAULT,
                 text: str = "", dot: bool = False):
        super().__init__(parent)

        self._badge_type = badge_type
        self._text = text
        self._dot_mode = dot

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 2, 4, 2)

        self._label = QLabel(text)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set font for label
        font = self._label.font()
        font.setPointSize(9)
        self._label.setFont(font)

        self._layout.addWidget(self._label)

        # Set size policy
        if dot:
            self.setFixedSize(8, 8)
            self._label.setVisible(False)
            self._layout.setContentsMargins(0, 0, 0, 0)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Minimum,
                               QSizePolicy.Policy.Fixed)
            self.setMinimumHeight(20)

        self._setup_enhanced_animations()
        self._apply_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system"""
        # Entrance animation
        QTimer.singleShot(50, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation with enhanced effects"""
        entrance_sequence = FluentSequence(self)

        # Fade in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self, 250))
        entrance_sequence.addPause(50)

        # Scale in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.scale_in(self, 200))

        entrance_sequence.start()

    def _apply_style(self):
        """Apply badge style based on type"""
        theme = theme_manager

        # Define colors based on badge type
        if self._badge_type == self.BadgeType.DEFAULT:
            bg_color = theme.get_color('border').name()
            text_color = theme.get_color('text_primary').name()
        elif self._badge_type == self.BadgeType.INFO:
            bg_color = theme.get_color('primary').name()
            text_color = "white" if theme._current_mode == ThemeMode.LIGHT else theme.get_color(
                'background').name()
        elif self._badge_type == self.BadgeType.SUCCESS:
            bg_color = "#0f7b0f"  # Green
            text_color = "white"
        elif self._badge_type == self.BadgeType.WARNING:
            bg_color = "#ffc83d"  # Amber
            text_color = theme.get_color('text_primary').name()
        elif self._badge_type == self.BadgeType.ERROR:
            bg_color = "#e81123"  # Red
            text_color = "white"
        else:
            bg_color = theme.get_color('border').name()
            text_color = theme.get_color('text_primary').name()

        if self._dot_mode:
            style_sheet = f"""
                FluentBadge {{
                    background-color: {bg_color};
                    border-radius: 4px;
                    transition: all 0.2s ease;
                }}
                FluentBadge:hover {{
                    transform: scale(1.1);
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
                }}
            """
        else:
            style_sheet = f"""
                FluentBadge {{
                    background-color: {bg_color};
                    border-radius: 10px;
                    padding: 2px 8px;
                    transition: all 0.2s ease;
                }}
                FluentBadge:hover {{
                    transform: translateY(-1px);
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
                }}
                QLabel {{
                    color: {text_color};
                    background-color: transparent;
                    border: none;
                }}
            """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme changes with transition"""
        self._apply_style()
        FluentMicroInteraction.pulse_animation(self, 1.02)

    def setText(self, text: str):
        """Set badge text with transition"""
        self._text = text
        self._label.setText(text)

        # Add transition effect
        FluentMicroInteraction.pulse_animation(self._label, 1.05)

        # Adjust size for number-only content
        try:
            value = int(text)
            if value < 10:
                self.setFixedWidth(20)
            elif value < 100:
                self.setFixedWidth(28)
            else:
                self.setMinimumWidth(32)
        except ValueError:
            self.setMinimumWidth(10)
            self.setSizePolicy(QSizePolicy.Policy.Minimum,
                               QSizePolicy.Policy.Fixed)

    def setBadgeType(self, badge_type: str):
        """Set badge type with transition"""
        if self._badge_type != badge_type:
            self._badge_type = badge_type
            self._apply_style()
            FluentMicroInteraction.pulse_animation(self, 1.03)

    def setDotMode(self, dot: bool):
        """Set dot mode with transition"""
        if self._dot_mode != dot:
            self._dot_mode = dot

            # Animate transition
            transition_sequence = FluentSequence(self)
            transition_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self, 0.8))
            transition_sequence.addPause(150)
            transition_sequence.addCallback(self._apply_dot_mode_changes)
            transition_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self, 1.0))
            transition_sequence.start()

    def _apply_dot_mode_changes(self):
        """Apply dot mode changes"""
        if self._dot_mode:
            self.setFixedSize(8, 8)
            self._label.setVisible(False)
            self._layout.setContentsMargins(0, 0, 0, 0)
        else:
            self._label.setVisible(True)
            self._layout.setContentsMargins(4, 2, 4, 2)
            self.setSizePolicy(QSizePolicy.Policy.Minimum,
                               QSizePolicy.Policy.Fixed)
            self.setMinimumHeight(20)

        self._apply_style()

    def enterEvent(self, event):
        """Handle mouse enter with enhanced animation"""
        FluentMicroInteraction.hover_glow(self, 0.1)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave with enhanced animation"""
        FluentMicroInteraction.hover_glow(self, -0.1)
        super().leaveEvent(event)


class FluentTag(QWidget):
    """Fluent Design Style Tag

    Features:
    - Multiple tag variants (default, outline, filled)
    - Customizable colors
    - Optional close button
    - Click event support
    - Enhanced animations and interactions
    """

    clicked = Signal()
    closed = Signal()

    class TagVariant:
        DEFAULT = "default"
        OUTLINE = "outline"
        FILLED = "filled"

    def __init__(self, text: str = "", parent: Optional[QWidget] = None,
                 variant: str = TagVariant.DEFAULT, closable: bool = False):
        super().__init__(parent)

        self._text = text
        self._variant = variant
        self._closable = closable
        self._color = None  # Custom color if set

        # Setup UI
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 4, 8, 4)
        self._layout.setSpacing(4)

        self._label = QLabel(text)

        # Set font for label
        font = self._label.font()
        font.setPointSize(10)
        self._label.setFont(font)

        self._layout.addWidget(self._label)

        if closable:
            self._close_btn = QPushButton()
            self._close_btn.setFixedSize(16, 16)
            self._close_btn.clicked.connect(self._on_close_clicked)
            self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._layout.addWidget(self._close_btn)

        # Set cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Minimum,
                           QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(26)

        self._setup_enhanced_animations()
        self._apply_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system"""
        # Entrance animation
        QTimer.singleShot(75, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation with enhanced effects"""
        entrance_sequence = FluentSequence(self)

        # Slide in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.slide_in(self, 300, "up"))
        entrance_sequence.addPause(100)

        # Subtle pulse effect
        entrance_sequence.addCallback(
            lambda: FluentMicroInteraction.pulse_animation(self, 1.02))

        entrance_sequence.start()

    def _apply_style(self):
        """Apply tag style based on variant"""
        theme = theme_manager

        # Get colors
        if self._color:
            primary_color = self._color
        else:
            primary_color = theme.get_color('primary').name()

        text_color = theme.get_color('text_primary').name()
        bg_color = theme.get_color('surface').name()

        # Define style based on variant
        if self._variant == self.TagVariant.DEFAULT:
            style_sheet = f"""
                FluentTag {{
                    background-color: {bg_color};
                    border: 1px solid {theme.get_color('border').name()};
                    border-radius: 13px;
                    transition: all 0.2s ease;
                }}
                FluentTag:hover {{
                    border-color: {primary_color};
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                QLabel {{
                    color: {text_color};
                    background-color: transparent;
                    border: none;
                }}
            """
        elif self._variant == self.TagVariant.OUTLINE:
            style_sheet = f"""
                FluentTag {{
                    background-color: transparent;
                    border: 1px solid {primary_color};
                    border-radius: 13px;
                    transition: all 0.2s ease;
                }}
                FluentTag:hover {{
                    background-color: rgba({self._hex_to_rgb(primary_color)}, 0.1);
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                QLabel {{
                    color: {primary_color};
                    background-color: transparent;
                    border: none;
                }}
            """
        elif self._variant == self.TagVariant.FILLED:
            text_color = "white" if theme._current_mode == ThemeMode.LIGHT else theme.get_color(
                'background').name()
            style_sheet = f"""
                FluentTag {{
                    background-color: {primary_color};
                    border: none;
                    border-radius: 13px;
                    transition: all 0.2s ease;
                }}
                FluentTag:hover {{
                    background-color: {self._lighten_color(primary_color, 0.1)};
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }}
                QLabel {{
                    color: {text_color};
                    background-color: transparent;
                    border: none;
                }}
            """
        else:
            style_sheet = ""

        # Add close button style
        if self._closable:
            close_icon_color = text_color
            if self._variant == self.TagVariant.FILLED:
                close_icon_color = text_color
            elif self._variant == self.TagVariant.OUTLINE:
                close_icon_color = primary_color

            style_sheet += f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 8px;
                    color: {close_icon_color};
                    font-family: "Segoe UI Symbol";
                    font-size: 12px;
                    transition: all 0.2s ease;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 0, 0, 0.1);
                    transform: scale(1.1);
                }}
                QPushButton:pressed {{
                    transform: scale(0.9);
                }}
            """

        self.setStyleSheet(style_sheet)

        # Set close button text if exists
        if self._closable:
            self._close_btn.setText("✕")

    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB string"""
        hex_color = hex_color.lstrip('#')
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"{r}, {g}, {b}"
        except (ValueError, IndexError):
            return "0, 0, 0"

    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Lighten a hex color by a factor"""
        hex_color = hex_color.lstrip('#')
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))

            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return hex_color

    def _on_theme_changed(self, _):
        """Handle theme changes with transition"""
        self._apply_style()
        FluentMicroInteraction.pulse_animation(self, 1.02)

    def _on_close_clicked(self):
        """Handle close button click with enhanced animation"""
        # Add close animation sequence
        close_sequence = FluentSequence(self)

        # Scale down animation
        close_sequence.addCallback(
            lambda: FluentMicroInteraction.scale_animation(self, 0.8))
        close_sequence.addPause(150)

        # Fade out animation
        close_sequence.addCallback(lambda: FluentRevealEffect.fade_in(
            self, 200))  # Using fade_in in reverse
        close_sequence.addPause(200)

        # Complete removal
        close_sequence.addCallback(self._complete_close)

        close_sequence.start()

    def _complete_close(self):
        """Complete the close operation"""
        self.closed.emit()
        self.hide()

    def setText(self, text: str):
        """Set tag text with transition"""
        self._text = text
        self._label.setText(text)
        FluentMicroInteraction.pulse_animation(self._label, 1.03)

    def setColor(self, color: str):
        """Set custom tag color with transition"""
        self._color = color
        self._apply_style()
        FluentMicroInteraction.pulse_animation(self, 1.02)

    def setVariant(self, variant: str):
        """Set tag variant with transition"""
        if self._variant != variant:
            self._variant = variant
            self._apply_style()
            FluentMicroInteraction.pulse_animation(self, 1.03)

    def mousePressEvent(self, event):
        """Handle mouse press event with enhanced animation"""
        FluentMicroInteraction.button_press(self, 0.95)
        super().mousePressEvent(event)
        self.clicked.emit()

    def enterEvent(self, event):
        """Handle mouse enter with enhanced animation"""
        FluentMicroInteraction.hover_glow(self, 0.1)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave with enhanced animation"""
        FluentMicroInteraction.hover_glow(self, -0.1)
        super().leaveEvent(event)


class FluentStatusIndicator(QWidget):
    """Enhanced status indicator with animations"""

    class Status:
        ONLINE = "online"
        OFFLINE = "offline"
        BUSY = "busy"
        AWAY = "away"
        UNKNOWN = "unknown"

    def __init__(self, status: str = Status.UNKNOWN, size: int = 12,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._status = status
        self._size = size

        self.setFixedSize(size, size)
        self._setup_enhanced_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system"""
        # Breathing animation for some statuses
        if self._status in [self.Status.ONLINE, self.Status.BUSY]:
            QTimer.singleShot(100, self._start_breathing_animation)

        # Entrance animation
        QTimer.singleShot(50, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation"""
        FluentRevealEffect.scale_in(self, 200)

    def _start_breathing_animation(self):
        """Start subtle breathing animation"""
        FluentMicroInteraction.pulse_animation(self, 1.1)

        # Repeat breathing animation
        breathing_timer = QTimer(self)
        breathing_timer.timeout.connect(
            lambda: FluentMicroInteraction.pulse_animation(self, 1.05))
        breathing_timer.start(3000)  # Every 3 seconds

    def _get_status_color(self) -> str:
        """Get color based on status"""
        colors = {
            self.Status.ONLINE: "#0f7b0f",    # Green
            self.Status.OFFLINE: "#666666",   # Gray
            self.Status.BUSY: "#e81123",      # Red
            self.Status.AWAY: "#ffc83d",      # Amber
            self.Status.UNKNOWN: "#999999"    # Light gray
        }
        return colors.get(self._status, colors[self.Status.UNKNOWN])

    def paintEvent(self, event):
        """Custom paint with enhanced styling"""
        from PySide6.QtGui import QPainter, QBrush

        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw status indicator
        color = self._get_status_color()
        brush = QBrush(color)
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)

        # Draw circle
        painter.drawEllipse(0, 0, self._size, self._size)

    def setStatus(self, status: str):
        """Set status with transition"""
        if self._status != status:
            old_status = self._status
            self._status = status

            # Add transition effect
            transition_sequence = FluentSequence(self)
            transition_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self, 0.8))
            transition_sequence.addPause(100)
            transition_sequence.addCallback(self.update)
            transition_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self, 1.0))
            transition_sequence.start()

            # Update breathing animation
            if status in [self.Status.ONLINE, self.Status.BUSY] and old_status not in [self.Status.ONLINE, self.Status.BUSY]:
                QTimer.singleShot(200, self._start_breathing_animation)

    def setSize(self, size: int):
        """Set indicator size with animation"""
        if self._size != size:
            self._size = size
            old_size = self.size()
            new_size = (size, size)

            # Animate size change
            FluentMicroInteraction.scale_animation(
                self, size / old_size.width())
            QTimer.singleShot(200, lambda: self.setFixedSize(*new_size))

    def _on_theme_changed(self, _):
        """Handle theme changes"""
        self.update()
        FluentMicroInteraction.pulse_animation(self, 1.02)
