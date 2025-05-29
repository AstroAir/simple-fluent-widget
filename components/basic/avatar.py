"""
Fluent Design Avatar Component
User avatar display with various styles and sizes
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QSize, Property, QPropertyAnimation, QByteArray, QTimer
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QPixmap, QFont,
                           QPainterPath, QPaintEvent, QEnterEvent)
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                      FluentRevealEffect, FluentSequence)
from typing import Optional
from enum import Enum
import hashlib


class FluentAvatar(QWidget):
    """Fluent Design avatar component with enhanced animations"""

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
        self._scale_progress = 1.0

        self._setup_ui()
        self._setup_style()
        self._setup_enhanced_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI components"""
        self.setFixedSize(self._size.value, self._size.value)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def _setup_style(self):
        """Setup component style"""
        if self._background_color is None:
            self._bg_color = theme_manager.get_color('accent_light')
        else:
            self._bg_color = self._background_color

        if self._border_color is None:
            self._border_col = theme_manager.get_color('border')
        else:
            self._border_col = self._border_color

        self.update()

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system"""
        # Enhanced hover animation
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_progress"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)

        # Enhanced press animation
        self._press_animation = QPropertyAnimation(
            self, QByteArray(b"press_progress"))
        self._press_animation.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
        self._press_animation.setEasingCurve(FluentTransition.EASE_CRISP)

        # Scale animation for interactions
        self._scale_animation = QPropertyAnimation(
            self, QByteArray(b"scale_progress"))
        self._scale_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._scale_animation.setEasingCurve(FluentTransition.EASE_SPRING)

        # Entrance animation
        QTimer.singleShot(50, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation with enhanced effects"""
        entrance_sequence = FluentSequence(self)

        # Fade in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self, 300))
        entrance_sequence.addPause(100)

        # Scale in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.scale_in(self, 250))

        entrance_sequence.start()

    def paintEvent(self, event: QPaintEvent):
        """Custom paint event with enhanced rendering"""
        _ = event  # Mark parameter as used

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()

        # Apply scale transformation for animations
        if self._scale_progress != 1.0:
            center = rect.center()
            painter.translate(center)
            painter.scale(self._scale_progress, self._scale_progress)
            painter.translate(-center)

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

        # Draw background with enhanced styling
        self._draw_background(painter, rect)

        # Draw content based on style
        if self._style == self.Style.PHOTO and self._pixmap:
            self._draw_photo(painter, rect)
        elif self._style == self.Style.INITIALS and self._initials:
            self._draw_initials(painter, rect)
        elif self._style == self.Style.ICON and self._icon:
            self._draw_icon(painter, rect)
        else:
            self._draw_placeholder(painter, rect)

        # Draw border with enhanced styling
        if self._border_width > 0:
            self._draw_border(painter, rect, path)

        # Draw enhanced interaction effects
        if self._clickable:
            self._draw_interaction_effects(painter, rect, path)

    def _draw_background(self, painter: QPainter, rect):
        """Draw background with enhanced styling"""
        if self._style == self.Style.PHOTO and self._pixmap:
            # Photo background is handled in _draw_photo
            return

        # Generate background color based on name/initials
        if self._name or self._initials:
            bg_color = self._generate_color_from_string(
                self._name or self._initials)
        else:
            bg_color = self._bg_color

        # Apply hover effect to background
        if self._hover_progress > 0:
            overlay_color = QColor(
                255, 255, 255, int(20 * self._hover_progress))
            bg_color = self._blend_colors(bg_color, overlay_color)

        painter.fillRect(rect, bg_color)

    def _draw_photo(self, painter: QPainter, rect):
        """Draw photo with enhanced rendering"""
        if not self._pixmap:
            return

        # Scale pixmap to fit with smooth transformation
        scaled_pixmap = self._pixmap.scaled(
            rect.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        # Center the pixmap
        x = (rect.width() - scaled_pixmap.width()) // 2
        y = (rect.height() - scaled_pixmap.height()) // 2

        # Apply opacity based on hover state
        if self._hover_progress > 0:
            painter.setOpacity(0.9 + 0.1 * self._hover_progress)

        painter.drawPixmap(x, y, scaled_pixmap)
        painter.setOpacity(1.0)

    def _draw_initials(self, painter: QPainter, rect):
        """Draw initials with enhanced typography"""
        # Set enhanced font
        font = QFont()
        font_size = max(8, int(rect.height() * 0.4))
        font.setPointSize(font_size)
        font.setWeight(QFont.Weight.Bold)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        painter.setFont(font)

        # Set text color with hover effect
        text_color = QColor(255, 255, 255)
        if self._hover_progress > 0:
            text_color.setAlpha(int(255 * (0.8 + 0.2 * self._hover_progress)))

        painter.setPen(QPen(text_color))

        # Draw text with enhanced alignment
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._initials)

    def _draw_icon(self, painter: QPainter, rect):
        """Draw icon with enhanced styling"""
        # Enhanced icon size calculation
        icon_size = int(rect.height() * 0.6)
        icon_rect = rect.adjusted(
            (rect.width() - icon_size) // 2,
            (rect.height() - icon_size) // 2,
            -(rect.width() - icon_size) // 2,
            -(rect.height() - icon_size) // 2
        )

        # Enhanced pen with hover effect
        pen_color = QColor(255, 255, 255)
        if self._hover_progress > 0:
            pen_color.setAlpha(int(255 * (0.8 + 0.2 * self._hover_progress)))

        painter.setPen(QPen(pen_color, 2))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))

        # Draw enhanced person silhouette
        head_rect = icon_rect.adjusted(
            icon_size // 4, 0, -icon_size // 4, -icon_size // 2
        )
        painter.drawEllipse(head_rect)

        body_rect = icon_rect.adjusted(
            0, icon_size // 3, 0, 0
        )
        painter.drawEllipse(body_rect)

    def _draw_placeholder(self, painter: QPainter, rect):
        """Draw placeholder with enhanced styling"""
        self._draw_icon(painter, rect)

    def _draw_border(self, painter: QPainter, rect, path: QPainterPath):
        """Draw border with enhanced styling"""
        _ = rect  # Mark parameter as used

        painter.setClipping(False)

        # Enhanced border with hover effect
        border_color = self._border_col
        if self._hover_progress > 0:
            border_color = border_color.lighter(
                int(110 + 20 * self._hover_progress))

        pen = QPen(border_color, self._border_width)
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawPath(path)

    def _draw_interaction_effects(self, painter: QPainter, rect, path: QPainterPath):
        """Draw enhanced hover and press effects"""
        _ = rect  # Mark parameter as used

        if self._hover_progress > 0 or self._press_progress > 0:
            painter.setClipping(False)

            # Enhanced overlay effects
            if self._press_progress > 0:
                # Press effect: darker overlay
                overlay_color = QColor(0, 0, 0, int(30 * self._press_progress))
                painter.fillPath(path, overlay_color)
            elif self._hover_progress > 0:
                # Hover effect: lighter overlay with subtle glow
                overlay_color = QColor(
                    255, 255, 255, int(25 * self._hover_progress))
                painter.fillPath(path, overlay_color)

    def _generate_color_from_string(self, text: str) -> QColor:
        """Generate a consistent color from string with enhanced algorithm"""
        # Create hash from text
        hash_object = hashlib.md5(text.encode())
        hex_dig = hash_object.hexdigest()

        # Extract RGB values with better distribution
        r = int(hex_dig[0:2], 16)
        g = int(hex_dig[2:4], 16)
        b = int(hex_dig[4:6], 16)

        # Enhanced color adjustment for better contrast and aesthetics
        r = (r % 150) + 80
        g = (g % 150) + 80
        b = (b % 150) + 80

        # Ensure color isn't too dark or too light
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        if luminance < 100:
            # Too dark, lighten it
            r = min(255, r + 50)
            g = min(255, g + 50)
            b = min(255, b + 50)
        elif luminance > 200:
            # Too light, darken it
            r = max(0, r - 50)
            g = max(0, g - 50)
            b = max(0, b - 50)

        return QColor(r, g, b)

    def _blend_colors(self, base: QColor, overlay: QColor) -> QColor:
        """Blend two colors with alpha blending"""
        alpha = overlay.alpha() / 255.0
        inv_alpha = 1.0 - alpha

        r = int(overlay.red() * alpha + base.red() * inv_alpha)
        g = int(overlay.green() * alpha + base.green() * inv_alpha)
        b = int(overlay.blue() * alpha + base.blue() * inv_alpha)

        return QColor(r, g, b)

    # Enhanced property getters and setters
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

    def _get_scale_progress(self):
        return self._scale_progress

    def _set_scale_progress(self, value):
        self._scale_progress = value
        self.update()

    # Enhanced Qt properties
    hover_progress = Property(
        float, _get_hover_progress, _set_hover_progress, None, "")
    press_progress = Property(
        float, _get_press_progress, _set_press_progress, None, "")
    scale_progress = Property(
        float, _get_scale_progress, _set_scale_progress, None, "")

    # Public API methods with enhanced functionality
    def setSize(self, size: Size):
        """Set avatar size with animation"""
        if self._size != size:
            self._size = size

            # Animate size change
            old_size = self.size()
            new_size = QSize(size.value, size.value)

            size_animation = QPropertyAnimation(self, QByteArray(b"size"))
            size_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
            size_animation.setEasingCurve(FluentTransition.EASE_SPRING)
            size_animation.setStartValue(old_size)
            size_animation.setEndValue(new_size)
            size_animation.finished.connect(
                lambda: self.setFixedSize(new_size))
            size_animation.start()

    def avatarSize(self) -> Size:
        """Get avatar size"""
        return self._size

    def size(self) -> QSize:
        """Get widget size"""
        return super().size()

    def setShape(self, shape: Shape):
        """Set avatar shape with transition"""
        if self._shape != shape:
            self._shape = shape
            # Add subtle transition effect
            FluentMicroInteraction.pulse_animation(self, 1.05)

    def shape(self) -> Shape:
        """Get avatar shape"""
        return self._shape

    def setPixmap(self, pixmap: QPixmap):
        """Set avatar photo with transition"""
        self._pixmap = pixmap
        self._style = self.Style.PHOTO

        # Add reveal transition
        FluentRevealEffect.fade_in(self, 300)

    def pixmap(self) -> Optional[QPixmap]:
        """Get avatar photo"""
        return self._pixmap

    def setInitials(self, initials: str):
        """Set avatar initials with transition"""
        new_initials = initials.upper()[:2]
        if self._initials != new_initials:
            self._initials = new_initials
            self._style = self.Style.INITIALS

            # Add transition effect
            FluentMicroInteraction.pulse_animation(self, 1.03)

    def initials(self) -> str:
        """Get avatar initials"""
        return self._initials

    def setName(self, name: str):
        """Set name and auto-generate initials with transition"""
        if self._name != name:
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

            # Add transition effect
            FluentMicroInteraction.pulse_animation(self, 1.03)

    def name(self) -> str:
        """Get name"""
        return self._name

    def setIcon(self, icon: str):
        """Set avatar icon with transition"""
        if self._icon != icon:
            self._icon = icon
            self._style = self.Style.ICON

            # Add transition effect
            FluentMicroInteraction.pulse_animation(self, 1.03)

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
        """Set border width with transition"""
        new_width = max(0, width)
        if self._border_width != new_width:
            self._border_width = new_width
            FluentMicroInteraction.pulse_animation(self, 1.02)

    def borderWidth(self) -> int:
        """Get border width"""
        return self._border_width

    def setBorderColor(self, color: QColor):
        """Set border color with transition"""
        self._border_color = color
        self._setup_style()
        FluentMicroInteraction.pulse_animation(self, 1.02)

    def borderColor(self) -> QColor:
        """Get border color"""
        return self._border_color if self._border_color else self._border_col

    def setBackgroundColor(self, color: QColor):
        """Set background color with transition"""
        self._background_color = color
        self._setup_style()
        FluentMicroInteraction.pulse_animation(self, 1.02)

    def backgroundColor(self) -> QColor:
        """Get background color"""
        return self._background_color if self._background_color else self._bg_color

    # Enhanced event handlers
    def enterEvent(self, event: QEnterEvent):
        """Handle mouse enter with enhanced animation"""
        if self._clickable:
            # Enhanced hover animation
            self._hover_animation.setStartValue(self._hover_progress)
            self._hover_animation.setEndValue(1.0)
            self._hover_animation.start()

            # Subtle scale effect
            self._scale_animation.setStartValue(self._scale_progress)
            self._scale_animation.setEndValue(1.05)
            self._scale_animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave with enhanced animation"""
        if self._clickable:
            # Return to normal state
            self._hover_animation.setStartValue(self._hover_progress)
            self._hover_animation.setEndValue(0.0)
            self._hover_animation.start()

            # Return to normal scale
            self._scale_animation.setStartValue(self._scale_progress)
            self._scale_animation.setEndValue(1.0)
            self._scale_animation.start()

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press with enhanced animation"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            # Enhanced press animation
            self._press_animation.setStartValue(self._press_progress)
            self._press_animation.setEndValue(1.0)
            self._press_animation.start()

            # Scale down effect
            FluentMicroInteraction.button_press(self, 0.95)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release with enhanced animation"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            # Release animation
            self._press_animation.setStartValue(self._press_progress)
            self._press_animation.setEndValue(0.0)
            self._press_animation.start()

            if self.rect().contains(event.position().toPoint()):
                # Add ripple effect before emitting signal
                FluentMicroInteraction.ripple_effect(self)
                QTimer.singleShot(100, self.clicked.emit)

        super().mouseReleaseEvent(event)

    def _on_theme_changed(self, _):
        """Handle theme change with transition"""
        self._setup_style()
        FluentMicroInteraction.pulse_animation(self, 1.02)


class FluentAvatarGroup(QWidget):
    """Group of avatars with overflow handling and enhanced animations"""

    def __init__(self, max_visible: int = 5, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._avatars: list[FluentAvatar] = []
        self._max_visible = max_visible
        self._spacing = 4
        self._overlap = 8
        self._size = FluentAvatar.Size.MEDIUM

        self._setup_ui()
        self._setup_style()
        self._setup_enhanced_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI components"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)  # Handle spacing manually

        self._update_layout()

    def _setup_style(self):
        """Setup component style"""
        self.setStyleSheet("""
            FluentAvatarGroup {
                background-color: transparent;
            }
        """)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system"""
        # Entrance animation for the group
        QTimer.singleShot(100, self._show_group_entrance)

    def _show_group_entrance(self):
        """Show group entrance with staggered animation"""
        if self._avatars:
            FluentRevealEffect.staggered_reveal(list(self._avatars), 150)

    def addAvatar(self, avatar: FluentAvatar):
        """Add avatar to group with animation"""
        avatar.setSize(self._size)
        self._avatars.append(avatar)

        # Add entrance animation for new avatar
        avatar.setParent(self)
        FluentRevealEffect.scale_in(avatar, 300)

        QTimer.singleShot(350, self._update_layout)

    def removeAvatar(self, avatar: FluentAvatar):
        """Remove avatar from group with animation"""
        if avatar in self._avatars:
            # Animate removal
            exit_sequence = FluentSequence(self)
            exit_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(avatar, 0.0))
            exit_sequence.addPause(200)
            exit_sequence.addCallback(lambda: self._complete_removal(avatar))
            exit_sequence.start()

    def _complete_removal(self, avatar: FluentAvatar):
        """Complete avatar removal"""
        self._avatars.remove(avatar)
        avatar.setParent(None)
        self._update_layout()

    def clear(self):
        """Clear all avatars with animation"""
        if self._avatars:
            # Animate all avatars out
            for i, avatar in enumerate(self._avatars):
                QTimer.singleShot(
                    i * 100, lambda a=avatar: FluentMicroInteraction.scale_animation(a, 0.0))

            # Clear after animations
            QTimer.singleShot(len(self._avatars) * 100 +
                              300, self._complete_clear)

    def _complete_clear(self):
        """Complete clearing all avatars"""
        for avatar in self._avatars:
            avatar.setParent(None)
        self._avatars.clear()
        self._update_layout()

    def setMaxVisible(self, max_visible: int):
        """Set maximum visible avatars with transition"""
        new_max = max(1, max_visible)
        if self._max_visible != new_max:
            self._max_visible = new_max
            self._update_layout_animated()

    def maxVisible(self) -> int:
        """Get maximum visible avatars"""
        return self._max_visible

    def setSize(self, size: FluentAvatar.Size):
        """Set avatar size with transition"""
        if self._size != size:
            self._size = size

            # Animate size change for all avatars
            for avatar in self._avatars:
                avatar.setSize(size)

            QTimer.singleShot(200, self._update_layout)

    def avatarSize(self) -> FluentAvatar.Size:
        """Get avatar size"""
        return self._size

    def size(self) -> QSize:
        """Get widget size"""
        return super().size()

    def setOverlap(self, overlap: int):
        """Set avatar overlap with transition"""
        new_overlap = max(0, overlap)
        if self._overlap != new_overlap:
            self._overlap = new_overlap
            self._update_layout_animated()

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

        # Add visible avatars with enhanced positioning
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

            # Add entrance animation for overflow indicator
            FluentRevealEffect.scale_in(overflow_avatar, 200)

        self._layout.addStretch()

    def _update_layout_animated(self):
        """Update layout with animation"""
        # Add transition effect
        FluentMicroInteraction.pulse_animation(self, 1.02)
        QTimer.singleShot(150, self._update_layout)

    def _on_theme_changed(self, _):
        """Handle theme change with transition"""
        self._setup_style()
        self._update_layout_animated()
