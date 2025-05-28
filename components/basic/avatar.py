"""
Fluent Design Avatar Component
User avatar display with various styles and sizes
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QSize, Property, QPropertyAnimation, QByteArray
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QPixmap, QFont,
                           QPainterPath)
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional
from enum import Enum
import hashlib


class FluentAvatar(QWidget):
    """Fluent Design avatar component"""

    class Size(Enum):
        SMALL = 24
        MEDIUM = 32
        LARGE = 40
        XLARGE = 56
        XXLARGE = 72

    class Shape(Enum):
        CIRCLE = "circle"
        ROUNDED_SQUARE = "rounded_square"
        SQUARE = "square"

    class Style(Enum):
        PHOTO = "photo"
        INITIALS = "initials"
        ICON = "icon"
        PLACEHOLDER = "placeholder"

    # Signals
    clicked = Signal()

    def __init__(self, size: Size = Size.MEDIUM, shape: Shape = Shape.CIRCLE,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._size = size
        self._shape = shape
        self._style = self.Style.PLACEHOLDER
        self._pixmap = None
        self._initials = ""
        self._name = ""
        self._icon = ""
        self._clickable = False
        self._border_width = 0
        self._border_color = None
        self._background_color = None
        self._hover_progress = 0.0
        self._press_progress = 0.0

        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setFixedSize(self._size.value, self._size.value)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def _setup_style(self):
        """Setup style"""
        if self._background_color is None:
            self._bg_color = theme_manager.get_color('accent_light')
        else:
            self._bg_color = self._background_color

        if self._border_color is None:
            self._border_col = theme_manager.get_color('border')
        else:
            self._border_col = self._border_color

        self.update()

    def _setup_animations(self):
        """Setup animations"""
        # 修复：使用 QByteArray 代替字节字符串
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_progress"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentAnimation.EASE_OUT)

        # 修复：使用 QByteArray 代替字节字符串
        self._press_animation = QPropertyAnimation(
            self, QByteArray(b"press_progress"))
        self._press_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._press_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def paintEvent(self, event):
        """Custom paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()

        # Create clipping path
        path = QPainterPath()
        if self._shape == self.Shape.CIRCLE:
            path.addEllipse(rect)
        elif self._shape == self.Shape.ROUNDED_SQUARE:
            corner_radius = min(rect.width(), rect.height()) * 0.2
            path.addRoundedRect(rect, corner_radius, corner_radius)
        else:  # SQUARE
            path.addRect(rect)

        painter.setClipPath(path)

        # Draw background
        self._draw_background(painter, rect)

        # Draw content
        if self._style == self.Style.PHOTO and self._pixmap:
            self._draw_photo(painter, rect)
        elif self._style == self.Style.INITIALS and self._initials:
            self._draw_initials(painter, rect)
        elif self._style == self.Style.ICON and self._icon:
            self._draw_icon(painter, rect)
        else:
            self._draw_placeholder(painter, rect)

        # Draw border
        if self._border_width > 0:
            self._draw_border(painter, rect, path)

        # Draw hover/press effects
        if self._clickable:
            self._draw_interaction_effects(painter, rect, path)

    def _draw_background(self, painter: QPainter, rect):
        """Draw background"""
        if self._style == self.Style.PHOTO and self._pixmap:
            # Photo background is handled in _draw_photo
            return

        # Generate background color based on name/initials
        if self._name or self._initials:
            bg_color = self._generate_color_from_string(
                self._name or self._initials)
        else:
            bg_color = self._bg_color

        painter.fillRect(rect, bg_color)

    def _draw_photo(self, painter: QPainter, rect):
        """Draw photo"""
        if not self._pixmap:
            return

        # Scale pixmap to fit
        scaled_pixmap = self._pixmap.scaled(
            rect.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        # Center the pixmap
        x = (rect.width() - scaled_pixmap.width()) // 2
        y = (rect.height() - scaled_pixmap.height()) // 2

        painter.drawPixmap(x, y, scaled_pixmap)

    def _draw_initials(self, painter: QPainter, rect):
        """Draw initials"""
        # Set font
        font = QFont()
        font_size = max(8, int(rect.height() * 0.4))
        font.setPointSize(font_size)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)

        # Set text color
        painter.setPen(QPen(QColor(255, 255, 255)))

        # Draw text
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._initials)

    def _draw_icon(self, painter: QPainter, rect):
        """Draw icon"""
        # For now, draw a simple person icon
        icon_size = int(rect.height() * 0.6)
        icon_rect = rect.adjusted(
            (rect.width() - icon_size) // 2,
            (rect.height() - icon_size) // 2,
            -(rect.width() - icon_size) // 2,
            -(rect.height() - icon_size) // 2
        )

        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))

        # Draw simple person silhouette
        head_rect = icon_rect.adjusted(
            icon_size // 4, 0, -icon_size // 4, -icon_size // 2
        )
        painter.drawEllipse(head_rect)

        body_rect = icon_rect.adjusted(
            0, icon_size // 3, 0, 0
        )
        painter.drawEllipse(body_rect)

    def _draw_placeholder(self, painter: QPainter, rect):
        """Draw placeholder"""
        self._draw_icon(painter, rect)

    def _draw_border(self, painter: QPainter, rect_obj, path: QPainterPath):
        """Draw border"""
        painter.setClipping(False)

        pen = QPen(self._border_col, self._border_width)
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawPath(path)

    def _draw_interaction_effects(self, painter: QPainter, rect_obj, path: QPainterPath):
        """Draw hover and press effects"""
        if self._hover_progress > 0 or self._press_progress > 0:
            painter.setClipping(False)

            # Overlay color
            overlay_color = QColor(
                255, 255, 255, int(30 * self._hover_progress))
            if self._press_progress > 0:
                overlay_color = QColor(0, 0, 0, int(20 * self._press_progress))

            painter.fillPath(path, overlay_color)

    def _generate_color_from_string(self, text: str) -> QColor:
        """Generate a consistent color from string"""
        # Create hash from text
        hash_object = hashlib.md5(text.encode())
        hex_dig = hash_object.hexdigest()

        # Extract RGB values
        r = int(hex_dig[0:2], 16)
        g = int(hex_dig[2:4], 16)
        b = int(hex_dig[4:6], 16)

        # Adjust for better contrast
        r = (r % 180) + 75
        g = (g % 180) + 75
        b = (b % 180) + 75

        return QColor(r, g, b)

    def _get_hover_progress(self):
        return self._hover_progress

    def _set_hover_progress(self, value):
        self._hover_progress = value
        self.update()

    def _get_press_progress(self):
        return self._press_progress

    def _set_press_progress(self, value):
        self._press_progress = value
        self.update()

    # 修复：添加缺少的 user 和 notify 参数
    hover_progress = Property(
        float, _get_hover_progress, _set_hover_progress, None, "", user=True)
    press_progress = Property(
        float, _get_press_progress, _set_press_progress, None, "", user=True)

    def setSize(self, size: Size):
        """Set avatar size"""
        self._size = size
        self.setFixedSize(size.value, size.value)
        self.update()

    # 修复：重命名方法以避免与基类方法冲突，或使返回类型兼容
    def avatarSize(self) -> Size:
        """Get avatar size"""
        return self._size

    # 基类方法保持不变，不覆盖
    def size(self) -> QSize:
        """返回组件大小"""
        return super().size()

    def setShape(self, shape: Shape):
        """Set avatar shape"""
        self._shape = shape
        self.update()

    def shape(self) -> Shape:
        """Get avatar shape"""
        return self._shape

    def setPixmap(self, pixmap: QPixmap):
        """Set avatar photo"""
        self._pixmap = pixmap
        self._style = self.Style.PHOTO
        self.update()

    def pixmap(self) -> Optional[QPixmap]:
        """Get avatar photo"""
        return self._pixmap

    def setInitials(self, initials: str):
        """Set avatar initials"""
        self._initials = initials.upper()[:2]  # Max 2 characters
        self._style = self.Style.INITIALS
        self.update()

    def initials(self) -> str:
        """Get avatar initials"""
        return self._initials

    def setName(self, name: str):
        """Set name and auto-generate initials"""
        self._name = name

        # Auto-generate initials
        if name:
            parts = name.strip().split()
            if len(parts) >= 2:
                self._initials = (parts[0][0] + parts[-1][0]).upper()
            elif len(parts) == 1:
                self._initials = parts[0][:2].upper()
            else:
                self._initials = ""

            self._style = self.Style.INITIALS
        else:
            self._initials = ""
            self._style = self.Style.PLACEHOLDER

        self.update()

    def name(self) -> str:
        """Get name"""
        return self._name

    def setIcon(self, icon: str):
        """Set avatar icon"""
        self._icon = icon
        self._style = self.Style.ICON
        self.update()

    def icon(self) -> str:
        """Get avatar icon"""
        return self._icon

    def setClickable(self, clickable: bool):
        """Set whether avatar is clickable"""
        self._clickable = clickable
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if clickable else Qt.CursorShape.ArrowCursor)

    def isClickable(self) -> bool:
        """Check if avatar is clickable"""
        return self._clickable

    def setBorderWidth(self, width: int):
        """Set border width"""
        self._border_width = max(0, width)
        self.update()

    def borderWidth(self) -> int:
        """Get border width"""
        return self._border_width

    def setBorderColor(self, color: QColor):
        """Set border color"""
        self._border_color = color
        self._setup_style()

    def borderColor(self) -> QColor:
        """Get border color"""
        return self._border_color if self._border_color else self._border_col

    def setBackgroundColor(self, color: QColor):
        """Set background color"""
        self._background_color = color
        self._setup_style()

    def backgroundColor(self) -> QColor:
        """Get background color"""
        return self._background_color if self._background_color else self._bg_color

    def enterEvent(self, event):
        """Handle mouse enter"""
        if self._clickable:
            self._hover_animation.setStartValue(self._hover_progress)
            self._hover_animation.setEndValue(1.0)
            self._hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave"""
        if self._clickable:
            self._hover_animation.setStartValue(self._hover_progress)
            self._hover_animation.setEndValue(0.0)
            self._hover_animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self._press_animation.setStartValue(self._press_progress)
            self._press_animation.setEndValue(1.0)
            self._press_animation.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self._press_animation.setStartValue(self._press_progress)
            self._press_animation.setEndValue(0.0)
            self._press_animation.start()

            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit()

        super().mouseReleaseEvent(event)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentAvatarGroup(QWidget):
    """Group of avatars with overflow handling"""

    def __init__(self, max_visible: int = 5, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._avatars: list[FluentAvatar] = []
        self._max_visible = max_visible
        self._spacing = 4
        self._overlap = 8
        self._size = FluentAvatar.Size.MEDIUM

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)  # We'll handle spacing manually

        self._update_layout()

    def _setup_style(self):
        """Setup style"""
        style_sheet = f"""
            FluentAvatarGroup {{
                background-color: transparent;
            }}
        """

        self.setStyleSheet(style_sheet)

    def addAvatar(self, avatar: FluentAvatar):
        """Add avatar to group"""
        avatar.setSize(self._size)
        self._avatars.append(avatar)
        self._update_layout()

    def removeAvatar(self, avatar: FluentAvatar):
        """Remove avatar from group"""
        if avatar in self._avatars:
            self._avatars.remove(avatar)
            avatar.setParent(None)
            self._update_layout()

    def clear(self):
        """Clear all avatars"""
        for avatar in self._avatars:
            avatar.setParent(None)
        self._avatars.clear()
        self._update_layout()

    def setMaxVisible(self, max_visible: int):
        """Set maximum visible avatars"""
        self._max_visible = max(1, max_visible)
        self._update_layout()

    def maxVisible(self) -> int:
        """Get maximum visible avatars"""
        return self._max_visible

    def setSize(self, size: FluentAvatar.Size):
        """Set avatar size"""
        self._size = size
        for avatar in self._avatars:
            avatar.setSize(size)
        self._update_layout()

    # 修复：重命名方法或修改返回类型
    def avatarSize(self) -> FluentAvatar.Size:
        """Get avatar size"""
        return self._size

    # 不覆盖基类的 size() 方法
    def size(self) -> QSize:
        """返回组件大小"""
        return super().size()

    def setOverlap(self, overlap: int):
        """Set avatar overlap"""
        self._overlap = max(0, overlap)
        self._update_layout()

    def overlap(self) -> int:
        """Get avatar overlap"""
        return self._overlap

    def _update_layout(self):
        """Update layout of avatars"""
        # Clear existing layout
        for i in reversed(range(self._layout.count())):
            item = self._layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    self._layout.removeWidget(widget)

        visible_count = min(len(self._avatars), self._max_visible)
        overflow_count = max(0, len(self._avatars) - self._max_visible)

        # Add visible avatars
        for i in range(visible_count):
            avatar = self._avatars[i]
            avatar.setParent(self)
            self._layout.addWidget(avatar)

            # Add negative spacing for overlap (except for the first item)
            if i > 0:
                self._layout.addSpacing(-self._overlap)

        # Add overflow indicator if needed
        if overflow_count > 0:
            overflow_avatar = FluentAvatar(
                self._size, FluentAvatar.Shape.CIRCLE, self)
            overflow_avatar.setInitials(f"+{overflow_count}")
            overflow_avatar.setBackgroundColor(
                theme_manager.get_color('text_secondary'))

            if visible_count > 0:
                self._layout.addSpacing(-self._overlap)
            self._layout.addWidget(overflow_avatar)

        self._layout.addStretch()

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self._update_layout()
