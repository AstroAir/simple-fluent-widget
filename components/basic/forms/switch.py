"""
Fluent Design Switch Component

Implements a modern toggle switch with smooth animations and various sizes.
Based on Windows 11 Fluent Design principles.
"""

from typing import List, Optional
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QRect, Property, QByteArray
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics

from core.theme import theme_manager


class FluentSwitch(QWidget):
    """
    Modern toggle switch with smooth animations and multiple sizes.

    Features:
    - Smooth thumb animation
    - Multiple sizes (small, medium, large)
    - Disabled state support
    - Custom colors
    - On/off text labels
    - Keyboard navigation
    - **Optimized rendering and state management**
    """

    # Signals
    toggled = Signal(bool)
    stateChanged = Signal(int)  # Compatible with QCheckBox interface
    thumbPositionChanged = Signal(float)  # Signal for property notification

    # Size presets
    SIZE_SMALL = "small"
    SIZE_MEDIUM = "medium"
    SIZE_LARGE = "large"

    def __init__(self,
                 text: str = "",
                 checked: bool = False,
                 size: str = SIZE_MEDIUM,
                 on_text: str = "",
                 off_text: str = "",
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._checked = checked
        self._enabled = True  # Keep track of enabled state internally
        self._hovered = False
        self._pressed = False
        self._text = text
        self._on_text = on_text
        self._off_text = off_text
        self._size = size
        self._thumb_position = 1.0 if checked else 0.0

        # Size configurations
        self._size_configs = {
            self.SIZE_SMALL: {
                'track_width': 40,
                'track_height': 20,
                'thumb_size': 16,
                'font_size': 12
            },
            self.SIZE_MEDIUM: {
                'track_width': 50,
                'track_height': 24,
                'thumb_size': 20,
                'font_size': 14
            },
            self.SIZE_LARGE: {
                'track_width': 60,
                'track_height': 28,
                'thumb_size': 24,
                'font_size': 16
            }
        }

        # Caching flags and storage
        self._colors_dirty = True  # Flag to indicate colors need recalculation
        self._text_metrics_dirty = True  # Flag to indicate text metrics need recalculation
        self._cached_colors = {}  # Store for cached colors
        self._cached_track_rect = None  # Cache for track rectangle
        self._cached_text_metrics = {}  # Store for cached text metrics
        self._prev_thumb_rect = None  # Previous thumb rectangle for optimized drawing

        self._setup_ui()
        self._setup_animation()
        self._connect_theme()
        self._update_colors()  # Initial color calculation
        self._update_text_metrics()  # Initial text metrics calculation
        self.setEnabled(True)  # Initialize QWidget's enabled state

    def _setup_ui(self):
        """Setup UI elements"""
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_size()  # Calculate component size

    def _setup_animation(self):
        """Setup animation with optimized settings"""
        self._thumb_animation = QPropertyAnimation(
            self, QByteArray(b"thumbPosition"))
        self._thumb_animation.setDuration(150)
        self._thumb_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Optimize animation for performance
        # self._thumb_animation.setUpdateInterval(33)  # ~30fps instead of default 60fps

    def _connect_theme(self):
        """Connect to theme changes"""
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self):
        """Handle theme changes"""
        self._colors_dirty = True  # Mark colors as needing refresh
        self.update()

    def _update_colors(self):
        """Update cached colors based on current theme and state"""
        if not theme_manager:
            self._colors_dirty = False
            return

        # Cache all theme colors at once instead of fetching on every paint
        self._cached_colors = {
            'track_checked': theme_manager.get_color("primary"),
            'thumb_checked': QColor(255, 255, 255),
            'track_unchecked_enabled': theme_manager.get_color("surface_variant"),
            'thumb_unchecked_enabled': theme_manager.get_color("outline"),
            'text_enabled': theme_manager.get_color("on_surface"),
            'on_primary_text': theme_manager.get_color("on_primary"),
            'on_surface_variant_text': theme_manager.get_color("on_surface_variant"),
            'shadow': theme_manager.get_color("shadow"),
        }

        # Set fallback shadow if needed
        if not self._cached_colors['shadow'].isValid():
            self._cached_colors['shadow'] = QColor(0, 0, 0, 30)

        # Create derived colors to avoid recalculation during painting
        track_unchecked_disabled = QColor(
            self._cached_colors['track_unchecked_enabled'])
        track_unchecked_disabled.setAlpha(100)
        self._cached_colors['track_unchecked_disabled'] = track_unchecked_disabled

        thumb_unchecked_disabled = QColor(
            self._cached_colors['thumb_unchecked_enabled'])
        thumb_unchecked_disabled.setAlpha(150)
        self._cached_colors['thumb_unchecked_disabled'] = thumb_unchecked_disabled

        text_disabled = QColor(self._cached_colors['text_enabled'])
        text_disabled.setAlpha(128)
        self._cached_colors['text_disabled'] = text_disabled

        self._colors_dirty = False

    def _update_text_metrics(self):
        """Cache text metrics to avoid recalculating them on every paint"""
        if not self._text_metrics_dirty:
            return

        config = self._size_configs[self._size]
        font = QFont()
        font.setPointSize(config['font_size'])
        fm = QFontMetrics(font)

        # Calculate and cache main text metrics
        if self._text:
            text_width = fm.horizontalAdvance(self._text)
            text_height = fm.height()
        else:
            text_width = 0
            text_height = 0

        self._cached_text_metrics = {
            'main_font': font,
            'text_width': text_width,
            'text_height': text_height,
        }

        # Create and cache font for On/Off text
        small_font = QFont()
        small_font.setPointSize(max(8, config['font_size'] - 4))
        self._cached_text_metrics['small_font'] = small_font

        self._text_metrics_dirty = False

    def _update_size(self):
        """Update component size using cached metrics when possible"""
        config = self._size_configs[self._size]
        track_width = config['track_width']
        track_height = config['track_height']

        # Calculate text size using cached metrics when available
        if self._text:
            if self._text_metrics_dirty:
                self._update_text_metrics()

            text_width = self._cached_text_metrics['text_width']
            text_height = self._cached_text_metrics['text_height']

            # Calculate total widget size
            total_width = track_width + 8 + text_width
            total_height = max(track_height, text_height)

            self.setFixedSize(total_width, total_height)
        else:
            self.setFixedSize(track_width, track_height)

        # Invalidate the track rect cache since size changed
        self._cached_track_rect = None

    # Getter for thumbPosition property
    def _get_thumbPosition(self) -> float:
        return self._thumb_position

    # Setter for thumbPosition property
    def _set_thumbPosition(self, value: float):
        if self._thumb_position != value:
            self._thumb_position = value
            self.update()
            self.thumbPositionChanged.emit(self._thumb_position)

    # Define the Qt Property with notification signal
    thumbPosition = Property(float, _get_thumbPosition,
                             _set_thumbPosition, None, "", notify=thumbPositionChanged)

    def _get_track_rect(self) -> QRect:
        """Get cached track rectangle"""
        if not self._cached_track_rect:
            config = self._size_configs[self._size]
            track_width = config['track_width']
            track_height = config['track_height']
            y = (self.height() - track_height) // 2
            self._cached_track_rect = QRect(0, y, track_width, track_height)
        return self._cached_track_rect

    def _get_thumb_rect(self) -> QRect:
        """Get thumb rectangle based on current position"""
        config = self._size_configs[self._size]
        thumb_size = config['thumb_size']
        track_rect = self._get_track_rect()

        # Calculate thumb position
        thumb_margin = 2
        max_x = track_rect.width() - thumb_size - thumb_margin
        thumb_x = thumb_margin + (max_x - thumb_margin) * self._thumb_position
        thumb_y = track_rect.y() + (track_rect.height() - thumb_size) // 2

        return QRect(int(thumb_x), thumb_y, thumb_size, thumb_size)

    def isChecked(self) -> bool:
        """Get checked state"""
        return self._checked

    def setChecked(self, checked: bool):
        """Set checked state with efficient updates"""
        if self._checked != checked:
            self._checked = checked
            self._animate_thumb()
            self.toggled.emit(checked)
            self.stateChanged.emit(2 if checked else 0)
            self.update()

    def toggle(self):
        """Toggle the state"""
        self.setChecked(not self._checked)

    def setText(self, text: str):
        """Set text with efficient updates"""
        if self._text != text:
            self._text = text
            self._text_metrics_dirty = True
            self._update_size()
            self.update()

    def text(self) -> str:
        """Get the text"""
        return self._text

    def setOnText(self, text: str):
        """Set 'on' text"""
        if self._on_text != text:
            self._on_text = text
            self.update()

    def setOffText(self, text: str):
        """Set 'off' text"""
        if self._off_text != text:
            self._off_text = text
            self.update()

    def setSize(self, size: str):
        """Set size with efficient updates"""
        if size in self._size_configs and self._size != size:
            self._size = size
            self._text_metrics_dirty = True
            self._cached_track_rect = None
            self._update_size()
            self.update()

    def setEnabled(self, enabled: bool):
        """Set enabled state with efficient updates"""
        if self._enabled != enabled:
            super().setEnabled(enabled)
            self._enabled = enabled
            self.update()

    def _animate_thumb(self):
        """Animate thumb position changes"""
        target_pos = 1.0 if self._checked else 0.0

        self._thumb_animation.stop()
        self._thumb_animation.setStartValue(self._thumb_position)
        self._thumb_animation.setEndValue(target_pos)
        self._thumb_animation.start()

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton and self._enabled:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.MouseButton.LeftButton and self._pressed:
            self._pressed = False
            if self.rect().contains(event.pos()) and self._enabled:
                self.toggle()
            self.update()
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter events"""
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave events"""
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def keyPressEvent(self, event):
        """Handle keyboard events"""
        if self._enabled and event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.toggle()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, _event):
        """Optimized paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Update cached resources when needed
        if self._colors_dirty:
            self._update_colors()

        if self._text_metrics_dirty:
            self._update_text_metrics()

        # Skip painting if colors aren't available
        if not self._cached_colors:
            return

        # Calculate current colors based on state for efficient reuse
        if self._checked:
            current_track_color = QColor(self._cached_colors['track_checked'])
            current_thumb_color = QColor(self._cached_colors['thumb_checked'])
            if not self._enabled:
                current_track_color.setAlpha(100)  # Dim when disabled
        else:  # Unchecked
            if self._enabled:
                current_track_color = QColor(
                    self._cached_colors['track_unchecked_enabled'])
                current_thumb_color = QColor(
                    self._cached_colors['thumb_unchecked_enabled'])
            else:
                current_track_color = QColor(
                    self._cached_colors['track_unchecked_disabled'])
                current_thumb_color = QColor(
                    self._cached_colors['thumb_unchecked_disabled'])

        # Apply hover and pressed effects efficiently
        if self._enabled:
            if self._pressed:
                current_track_color = current_track_color.darker(110)
                if not self._checked:  # Only darken thumb if not white
                    current_thumb_color = current_thumb_color.darker(105)
            elif self._hovered:
                current_track_color = current_track_color.lighter(110)
                if not self._checked:  # Only lighten thumb if not white
                    current_thumb_color = current_thumb_color.lighter(105)

        # Draw track
        track_rect = self._get_track_rect()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(current_track_color))
        painter.drawRoundedRect(
            track_rect, track_rect.height() // 2, track_rect.height() // 2)

        # Draw thumb
        thumb_rect = self._get_thumb_rect()

        # Thumb shadow (with cached shadow color)
        if self._enabled:
            shadow_rect = thumb_rect.adjusted(1, 1, 1, 1)
            painter.setBrush(QBrush(self._cached_colors['shadow']))
            painter.drawEllipse(shadow_rect)

        # Thumb body
        painter.setBrush(QBrush(current_thumb_color))
        painter.drawEllipse(thumb_rect)

        # Draw text (using cached fonts and metrics)
        if self._text:
            painter.setFont(self._cached_text_metrics['main_font'])
            painter.setPen(QPen(
                self._cached_colors['text_enabled'] if self._enabled else self._cached_colors['text_disabled']))

            text_x = track_rect.right() + 8
            text_rect = QRect(text_x, 0, self.width() - text_x, self.height())
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft |
                             Qt.AlignmentFlag.AlignVCenter, self._text)

        # Draw switch text (ON/OFF labels)
        if self._on_text or self._off_text:
            painter.setFont(self._cached_text_metrics['small_font'])

            on_off_text_color_base = self._cached_colors[
                'on_primary_text'] if self._checked else self._cached_colors['on_surface_variant_text']
            current_on_off_text_color = QColor(on_off_text_color_base)

            if not self._enabled:
                current_on_off_text_color.setAlpha(128)  # Dim if disabled

            painter.setPen(QPen(current_on_off_text_color))

            display_text = self._on_text if self._checked else self._off_text
            if display_text:
                painter.drawText(
                    track_rect, Qt.AlignmentFlag.AlignCenter, display_text)

        # Store current thumb rect for optimizing next paint
        self._prev_thumb_rect = thumb_rect


class FluentSwitchGroup(QWidget):
    """
    Switch group to manage multiple related switches
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._switches: List[FluentSwitch] = []
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)

    def addSwitch(self, switch: FluentSwitch):
        """Add a switch to the group"""
        self._switches.append(switch)
        self._layout.addWidget(switch)

    def removeSwitch(self, switch: FluentSwitch):
        """Remove a switch from the group"""
        if switch in self._switches:
            self._switches.remove(switch)
            self._layout.removeWidget(switch)
            switch.setParent(None)

    def getSwitches(self) -> list[FluentSwitch]:
        """Get all switches in the group"""
        return self._switches.copy()

    def setEnabled(self, enabled: bool):
        """Set enabled state for the whole group"""
        super().setEnabled(enabled)
        for switch in self._switches:
            switch.setEnabled(enabled)
