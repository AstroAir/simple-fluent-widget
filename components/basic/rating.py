"""
Fluent Design Style Rating Component
"""

from PySide6.QtWidgets import QWidget
# QRect removed
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, Property, QByteArray
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QBrush
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional


class FluentRating(QWidget):
    """Fluent Design style rating component"""

    # Signals
    ratingChanged = Signal(int)  # Emitted when rating changes
    hoverChanged = Signal(int)   # Emitted when hover state changes
    hover_scaleChanged = Signal(float)
    pressed_scaleChanged = Signal(float)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._max_rating = 5
        self._current_rating = 0
        self._hover_rating = 0
        self._star_size = 24
        self._spacing = 4
        self._editable = True
        self._show_text = True
        self._star_style = "star"  # "star", "heart", "thumb"

        # Animation properties
        self._hover_scale = 1.0
        self._pressed_scale = 1.0

        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setMouseTracking(True)
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if self._editable else Qt.CursorShape.ArrowCursor)

        # Calculate widget size
        width = self._max_rating * self._star_size + \
            (self._max_rating - 1) * self._spacing
        height = self._star_size
        self.setFixedSize(width, height)

    def _setup_style(self):
        """Setup style"""
        # Styles are handled in paintEvent
        pass

    def _setup_animations(self):
        """Setup animations"""
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_scale"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentAnimation.EASE_OUT)

        self._press_animation = QPropertyAnimation(
            self, QByteArray(b"pressed_scale"))
        self._press_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._press_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def _get_hover_scale(self) -> float:
        return self._hover_scale

    def _set_hover_scale(self, value: float):
        if self._hover_scale == value:
            return
        self._hover_scale = value
        self.hover_scaleChanged.emit(self._hover_scale)
        self.update()

    hover_scale = Property(float, _get_hover_scale,
                           _set_hover_scale, None, "", notify=hover_scaleChanged)

    def _get_pressed_scale(self) -> float:
        return self._pressed_scale

    def _set_pressed_scale(self, value: float):
        if self._pressed_scale == value:
            return
        self._pressed_scale = value
        self.pressed_scaleChanged.emit(self._pressed_scale)
        self.update()

    pressed_scale = Property(float, _get_pressed_scale,
                             _set_pressed_scale, None, "", notify=pressed_scaleChanged)

    def setMaxRating(self, max_rating: int):
        """Set maximum rating"""
        self._max_rating = max_rating
        self._setup_ui()
        self.update()

    def getMaxRating(self) -> int:
        """Get maximum rating"""
        return self._max_rating

    def setRating(self, rating: int):
        """Set current rating"""
        rating = max(0, min(rating, self._max_rating))
        if rating != self._current_rating:
            self._current_rating = rating
            self.ratingChanged.emit(rating)
            self.update()

    def getRating(self) -> int:
        """Get current rating"""
        return self._current_rating

    def setEditable(self, editable: bool):
        """Set whether rating is editable"""
        self._editable = editable
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if editable else Qt.CursorShape.ArrowCursor)
        self.setMouseTracking(editable)

    def isEditable(self) -> bool:
        """Check if rating is editable"""
        return self._editable

    def setStarSize(self, size: int):
        """Set star size"""
        self._star_size = size
        self._setup_ui()
        self.update()

    def getStarSize(self) -> int:
        """Get star size"""
        return self._star_size

    def setSpacing(self, spacing: int):
        """Set spacing between stars"""
        self._spacing = spacing
        self._setup_ui()
        self.update()

    def getSpacing(self) -> int:
        """Get spacing between stars"""
        return self._spacing

    def setStarStyle(self, style: str):
        """Set star style: 'star', 'heart', 'thumb'"""
        if style in ["star", "heart", "thumb"]:
            self._star_style = style
            self.update()

    def getStarStyle(self) -> str:
        """Get star style"""
        return self._star_style

    def paintEvent(self, _event):
        """Paint the rating stars"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = theme_manager

        # Colors
        filled_color = theme.get_color('primary')
        empty_color = theme.get_color('border')
        hover_color = theme.get_color('primary').lighter(120)

        for i in range(self._max_rating):
            # Calculate star position
            x = i * (self._star_size + self._spacing)
            y = 0

            # Determine star state
            current_item_color: QColor
            filled: bool
            if self._hover_rating > 0 and i < self._hover_rating:
                current_item_color = hover_color
                filled = True
            elif i < self._current_rating:
                current_item_color = filled_color
                filled = True
            else:
                current_item_color = empty_color
                filled = False

            # Apply scaling for hover/press effects
            scale = 1.0
            # Apply hover scale if the item is part of the current hover selection
            if self._hover_rating > 0 and i < self._hover_rating:
                scale = self._get_hover_scale()  # Get the actual float value
            # Apply pressed scale if the item is part of the current rating and mouse is pressed (implicitly handled by animation start)
            # For simplicity, we'll rely on the animation to set the pressed_scale property
            # If a more direct visual feedback on press is needed for non-animated items, this logic might need adjustment.
            # However, the current animation setup triggers on press for the *selected* rating.

            # Draw star
            self._draw_star(painter, x, y, self._star_size,
                            current_item_color, filled, scale)

    def _draw_star(self, painter: QPainter, x: int, y: int, size: int,
                   color: QColor, filled: bool, scale: float = 1.0):
        """Draw a star shape"""
        painter.save()

        # Apply scaling
        if scale != 1.0:
            center_x = x + size / 2
            center_y = y + size / 2
            painter.translate(center_x, center_y)
            painter.scale(scale, scale)
            painter.translate(-center_x, -center_y)

        if self._star_style == "star":
            self._draw_star_shape(painter, x, y, size, color, filled)
        elif self._star_style == "heart":
            self._draw_heart_shape(painter, x, y, size, color, filled)
        elif self._star_style == "thumb":
            self._draw_thumb_shape(painter, x, y, size, color, filled)

        painter.restore()

    def _draw_star_shape(self, painter: QPainter, x: int, y: int, size: int,
                         color: QColor, filled: bool):
        """Draw a star shape"""
        # Star points (normalized to 0-1)
        star_points = [
            (0.5, 0.0),      # Top point
            (0.618, 0.345),  # Upper right
            (1.0, 0.345),    # Right point
            (0.691, 0.595),  # Lower right inner
            (0.809, 1.0),    # Bottom right
            (0.5, 0.755),    # Bottom inner
            (0.191, 1.0),    # Bottom left
            (0.309, 0.595),  # Lower left inner
            (0.0, 0.345),    # Left point
            (0.382, 0.345),  # Upper left inner
        ]

        # Scale points to actual size
        points = []
        for px, py in star_points:
            points.append((x + px * size, y + py * size))

        # Create path
        path = QPainterPath()
        path.moveTo(points[0][0], points[0][1])
        for point in points[1:]:
            path.lineTo(point[0], point[1])
        path.closeSubpath()

        # Draw star
        if filled:
            painter.fillPath(path, QBrush(color))

        painter.setPen(QPen(color, 1.5))
        painter.drawPath(path)

    def _draw_heart_shape(self, painter: QPainter, x: int, y: int, size: int,
                          color: QColor, filled: bool):
        """Draw a heart shape"""
        path = QPainterPath()

        # Heart shape (simplified)
        cx = x + size / 2

        # Control points for a more rounded heart
        cp1x_offset = size * 0.4
        cp1y_offset = size * 0.5
        cp2x_offset = size * 0.1
        cp2y_offset = size * 0.6

        # Bottom point of the heart
        bottom_y = y + size * 0.9

        # Left curve
        path.moveTo(cx, y + size * 0.25)  # Top indent
        path.cubicTo(cx - cp1x_offset, y - cp1y_offset * 0.1,  # Top-left control
                     cx - cp2x_offset * 2, y + cp2y_offset * 0.5,  # Mid-left control
                     cx, bottom_y)                  # Bottom point

        # Right curve
        path.cubicTo(cx + cp2x_offset * 2, y + cp2y_offset * 0.5,  # Mid-right control
                     cx + cp1x_offset, y - cp1y_offset * 0.1,  # Top-right control
                     cx, y + size * 0.25)  # Back to Top indent

        # Draw heart
        if filled:
            painter.fillPath(path, QBrush(color))

        painter.setPen(QPen(color, 1.5))
        painter.drawPath(path)

    def _draw_thumb_shape(self, painter: QPainter, x: int, y: int, size: int,
                          color: QColor, filled: bool):
        """Draw a thumbs up shape"""
        # Simplified thumb shape - using a rounded rect for the main part
        # and a small circle for the thumb itself.
        path = QPainterPath()

        # Main fist part (rounded rectangle)
        fist_height = size * 0.6
        fist_width = size * 0.5
        fist_x = x + size * 0.3
        fist_y = y + size * 0.4
        path.addRoundedRect(fist_x, fist_y, fist_width,
                            fist_height, size * 0.1, size * 0.1)

        # Thumb part (circle or oval)
        thumb_cx = x + size * 0.25
        thumb_cy = y + size * 0.25
        thumb_radius_x = size * 0.15
        thumb_radius_y = size * 0.20

        # Create a path for the thumb to rotate it slightly
        thumb_path = QPainterPath()
        thumb_path.addEllipse(thumb_cx - thumb_radius_x, thumb_cy -
                              thumb_radius_y, 2 * thumb_radius_x, 2 * thumb_radius_y)

        # Transform for rotation
        transform = painter.transform()
        painter.translate(thumb_cx, thumb_cy)
        painter.rotate(-30)  # Rotate thumb slightly
        painter.translate(-thumb_cx, -thumb_cy)

        path.addPath(thumb_path)
        painter.setTransform(transform)  # Reset transform for main drawing

        if filled:
            painter.fillPath(path, QBrush(color))

        painter.setPen(QPen(color, 1.5))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if not self._editable:
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            rating = self._get_rating_from_position(event.position().toPoint())
            if rating > 0:
                self.setRating(rating)

                # Press animation
                self._press_animation.stop()
                self._press_animation.setStartValue(
                    self.pressed_scale)  # Start from current scale
                self._press_animation.setEndValue(0.9)
                self._press_animation.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, _event):
        """Handle mouse release"""
        if not self._editable:
            super().mouseReleaseEvent(_event)
            return

        # Release animation
        self._press_animation.stop()
        self._press_animation.setStartValue(
            self.pressed_scale)  # Start from current scale
        self._press_animation.setEndValue(1.0)
        self._press_animation.start()
        super().mouseReleaseEvent(_event)

    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if not self._editable:
            super().mouseMoveEvent(event)
            return

        rating = self._get_rating_from_position(event.position().toPoint())
        if rating != self._hover_rating:
            self._hover_rating = rating
            self.hoverChanged.emit(rating)

            # Hover animation
            self._hover_animation.stop()
            self._hover_animation.setStartValue(
                self.hover_scale)  # Start from current scale
            if rating > 0:
                self._hover_animation.setEndValue(1.1)
            else:
                self._hover_animation.setEndValue(1.0)
            self._hover_animation.start()

            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, _event):
        """Handle mouse leave"""
        if not self._editable:
            super().leaveEvent(_event)
            return

        self._hover_rating = 0
        self.hoverChanged.emit(0)

        # Reset hover animation
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self.hover_scale)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()

        self.update()
        super().leaveEvent(_event)

    def _get_rating_from_position(self, pos):
        """Get rating value from mouse position"""
        if pos.y() < 0 or pos.y() > self.height():  # Check against widget height
            return 0

        for i in range(self._max_rating):
            star_x_start = i * (self._star_size + self._spacing)
            star_x_end = star_x_start + self._star_size
            # Consider the whole clickable area of the star, including spacing for the previous one
            # More accurately, check if pos.x() is within the bounds of the current star
            if star_x_start <= pos.x() < star_x_end:
                return i + 1
            # If click is in spacing after last star, still count as last star
            elif i == self._max_rating - 1 and pos.x() >= star_x_end:
                return i + 1

        return 0

    def _on_theme_changed(self, _=None):  # Added default for signal argument
        """Handle theme change"""
        self.update()
