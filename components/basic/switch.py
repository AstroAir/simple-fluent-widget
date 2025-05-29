"""
Fluent Design Switch Component

Implements a modern toggle switch with smooth animations and various sizes.
Based on Windows 11 Fluent Design principles.
"""

from typing import List, Optional
# Removed: Callable, math
from PySide6.QtWidgets import QWidget, QHBoxLayout
# Removed: QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QRect, Property, QByteArray
# Removed: QTimer, pyqtSignal, QParallelAnimationGroup
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics
# Removed: QLinearGradient

from core.theme import theme_manager
# Removed: FluentAnimation


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
    """

    # 信号
    toggled = Signal(bool)
    stateChanged = Signal(int)  # 兼容QCheckBox接口
    thumbPositionChanged = Signal(float)  # Signal for property notification

    # 尺寸预设
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

        # 尺寸配置
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

        self._setup_ui()
        self._setup_animation()
        self._connect_theme()
        self.setEnabled(True)  # Initialize QWidget's enabled state

    def _setup_ui(self):
        """设置UI"""
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 计算组件尺寸
        self._update_size()

    def _setup_animation(self):
        """设置动画"""
        self._thumb_animation = QPropertyAnimation(
            self, QByteArray(b"thumbPosition"))
        self._thumb_animation.setDuration(150)
        self._thumb_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _connect_theme(self):
        """连接主题"""
        if theme_manager:
            theme_manager.theme_changed.connect(self.update)

    def _update_size(self):
        """更新组件尺寸"""
        config = self._size_configs[self._size]
        track_width = config['track_width']
        track_height = config['track_height']

        # 计算文本尺寸
        if self._text:
            font = QFont()
            font.setPointSize(config['font_size'])
            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(self._text)
            text_height = fm.height()

            # 组件总尺寸
            total_width = track_width + 8 + text_width
            total_height = max(track_height, text_height)

            self.setFixedSize(total_width, total_height)
        else:
            self.setFixedSize(track_width, track_height)

    # Getter for thumbPosition property
    def _get_thumbPosition(self) -> float:
        return self._thumb_position

    # Setter for thumbPosition property
    def _set_thumbPosition(self, value: float):
        if self._thumb_position != value:
            self._thumb_position = value
            self.update()
            self.thumbPositionChanged.emit(self._thumb_position)

    thumbPosition = Property(float, _get_thumbPosition,
                             _set_thumbPosition, None, "", notify=thumbPositionChanged)

    def isChecked(self) -> bool:
        """获取选中状态"""
        return self._checked

    def setChecked(self, checked: bool):
        """设置选中状态"""
        if self._checked != checked:
            self._checked = checked
            self._animate_thumb()
            self.toggled.emit(checked)
            self.stateChanged.emit(2 if checked else 0)
            self.update()  # Ensure repaint after state change

    def toggle(self):
        """切换状态"""
        self.setChecked(not self._checked)

    def setText(self, text: str):
        """设置文本"""
        self._text = text
        self._update_size()
        self.update()

    def text(self) -> str:
        """获取文本"""
        return self._text

    def setOnText(self, text: str):
        """设置开启文本"""
        self._on_text = text
        self.update()

    def setOffText(self, text: str):
        """设置关闭文本"""
        self._off_text = text
        self.update()

    def setSize(self, size: str):
        """设置尺寸"""
        if size in self._size_configs:
            self._size = size
            self._update_size()
            self.update()

    # Override setEnabled to update internal state and repaint
    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self._enabled = enabled
        self.update()

    def _animate_thumb(self):
        """动画切换滑块"""
        target_pos = 1.0 if self._checked else 0.0

        self._thumb_animation.stop()
        self._thumb_animation.setStartValue(self._thumb_position)
        self._thumb_animation.setEndValue(target_pos)
        self._thumb_animation.start()

    def _get_track_rect(self) -> QRect:
        """获取轨道矩形"""
        config = self._size_configs[self._size]
        track_width = config['track_width']
        track_height = config['track_height']

        y = (self.height() - track_height) // 2
        return QRect(0, y, track_width, track_height)

    def _get_thumb_rect(self) -> QRect:
        """获取滑块矩形"""
        config = self._size_configs[self._size]
        thumb_size = config['thumb_size']
        track_rect = self._get_track_rect()

        # 计算滑块位置
        thumb_margin = 2
        max_x = track_rect.width() - thumb_size - thumb_margin
        thumb_x = thumb_margin + (max_x - thumb_margin) * self._thumb_position
        thumb_y = track_rect.y() + (track_rect.height() - thumb_size) // 2

        return QRect(int(thumb_x), thumb_y, thumb_size, thumb_size)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton and self._enabled:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton and self._pressed:
            self._pressed = False
            if self.rect().contains(event.pos()) and self._enabled:
                self.toggle()
            self.update()
        super().mouseReleaseEvent(event)

    def enterEvent(self, _event):  # Parameter event is not used
        """鼠标进入事件"""
        self._hovered = True
        self.update()
        super().enterEvent(_event)  # Call superclass method

    def leaveEvent(self, _event):  # Parameter event is not used
        """鼠标离开事件"""
        self._hovered = False
        self.update()
        super().leaveEvent(_event)  # Call superclass method

    def keyPressEvent(self, event):
        """键盘按下事件"""
        if self._enabled and event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.toggle()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, _event):  # Parameter event is not used
        """Paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Reference the event parameter to avoid warning
        _ = _event

        if not theme_manager:
            return

        # Base colors
        track_color_checked = theme_manager.get_color("primary")
        thumb_color_checked = QColor(255, 255, 255)

        track_color_unchecked_enabled = theme_manager.get_color(
            "surface_variant")
        thumb_color_unchecked_enabled = theme_manager.get_color("outline")

        # Disabled colors (approximations, ideally from theme)
        track_color_unchecked_disabled = QColor(track_color_unchecked_enabled)
        track_color_unchecked_disabled.setAlpha(100)  # More transparent
        thumb_color_unchecked_disabled = QColor(thumb_color_unchecked_enabled)
        thumb_color_unchecked_disabled.setAlpha(150)  # More transparent

        text_color_enabled = theme_manager.get_color("on_surface")
        text_color_disabled = QColor(text_color_enabled)
        text_color_disabled.setAlpha(128)

        current_track_color: QColor
        current_thumb_color: QColor

        if self._checked:
            current_track_color = QColor(track_color_checked)
            current_thumb_color = QColor(thumb_color_checked)
            if not self._enabled:
                current_track_color.setAlpha(100)  # Dim primary when disabled
                # Thumb remains white but on a dimmed track
        else:  # Unchecked
            if self._enabled:
                current_track_color = QColor(track_color_unchecked_enabled)
                current_thumb_color = QColor(thumb_color_unchecked_enabled)
            else:
                current_track_color = QColor(track_color_unchecked_disabled)
                current_thumb_color = QColor(thumb_color_unchecked_disabled)

        # Hover and pressed effects
        if self._enabled:
            if self._pressed:
                current_track_color = current_track_color.darker(110)
                if not self._checked:  # Only darken thumb if it's not the white one
                    current_thumb_color = current_thumb_color.darker(105)
            elif self._hovered:
                current_track_color = current_track_color.lighter(110)
                if not self._checked:  # Only lighten thumb if it's not the white one
                    current_thumb_color = current_thumb_color.lighter(105)

        # Draw track
        track_rect = self._get_track_rect()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(current_track_color))
        painter.drawRoundedRect(
            track_rect, track_rect.height() // 2, track_rect.height() // 2)

        # Draw thumb
        thumb_rect = self._get_thumb_rect()

        # Thumb shadow (Only if enabled and theme is light, or a subtle shadow always)
        if self._enabled:  # Simple shadow for enabled state
            shadow_rect = thumb_rect.adjusted(1, 1, 1, 1)
            shadow_color = theme_manager.get_color(
                "shadow")  # Assuming a shadow color exists
            if not shadow_color.isValid():  # Fallback shadow
                shadow_color = QColor(0, 0, 0, 30)
            painter.setBrush(QBrush(shadow_color))
            painter.drawEllipse(shadow_rect)

        # Thumb body
        painter.setBrush(QBrush(current_thumb_color))
        painter.drawEllipse(thumb_rect)

        # Draw text
        if self._text:
            config = self._size_configs[self._size]
            font = QFont()
            font.setPointSize(config['font_size'])
            painter.setFont(font)

            current_text_color = text_color_enabled if self._enabled else text_color_disabled
            painter.setPen(QPen(current_text_color))

            text_x = track_rect.right() + 8
            text_rect = QRect(text_x, 0, self.width() - text_x, self.height())
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft |
                             Qt.AlignmentFlag.AlignVCenter, self._text)

        # Draw switch text
        if self._on_text or self._off_text:
            config = self._size_configs[self._size]
            font = QFont()
            # Smaller font for inner text
            font.setPointSize(max(8, config['font_size'] - 4))
            painter.setFont(font)

            on_off_text_color_base: QColor
            if self._checked:
                on_off_text_color_base = theme_manager.get_color(
                    "on_primary")  # Text on primary color
            else:
                on_off_text_color_base = theme_manager.get_color(
                    "on_surface_variant")  # Text on surface_variant

            current_on_off_text_color = QColor(on_off_text_color_base)
            if not self._enabled:
                current_on_off_text_color.setAlpha(128)  # Dim if disabled

            painter.setPen(QPen(current_on_off_text_color))

            display_text = self._on_text if self._checked else self._off_text
            if display_text:
                painter.drawText(
                    track_rect, Qt.AlignmentFlag.AlignCenter, display_text)


class FluentSwitchGroup(QWidget):
    """
    开关组，管理多个相关的开关
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._switches: List[FluentSwitch] = []
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)

    def addSwitch(self, switch: FluentSwitch):
        """添加开关"""
        self._switches.append(switch)
        self._layout.addWidget(switch)

    def removeSwitch(self, switch: FluentSwitch):
        """移除开关"""
        if switch in self._switches:
            self._switches.remove(switch)
            self._layout.removeWidget(switch)
            # Or switch.deleteLater() if group owns them
            switch.setParent(None)

    def getSwitches(self) -> list[FluentSwitch]:
        """获取所有开关"""
        return self._switches.copy()

    def setEnabled(self, enabled: bool):
        """设置组启用状态"""
        super().setEnabled(enabled)
        for switch in self._switches:
            switch.setEnabled(enabled)
