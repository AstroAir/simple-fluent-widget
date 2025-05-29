"""
Fluent Design Style Rating Component
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, Property, QByteArray
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QBrush
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import FluentRevealEffect, FluentMicroInteraction, FluentTransition
from typing import Optional


class FluentRating(QWidget):
    """Fluent Design style rating component with enhanced animations"""

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
        self._star_size = 28  # Slightly larger for better interaction
        self._spacing = 6     # More spacing for better visual separation
        self._editable = True
        self._show_text = True
        self._star_style = "star"  # "star", "heart", "thumb"

        # Animation properties
        self._hover_scale = 1.0
        self._pressed_scale = 1.0

        # Animation instances
        self._hover_animation = None
        self._press_animation = None
        self._rating_change_animation = None

        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

        # Initial reveal animation
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_MEDIUM)

    def _setup_ui(self):
        """Setup UI with enhanced sizing"""
        self.setMouseTracking(True)
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if self._editable else Qt.CursorShape.ArrowCursor)

        # Calculate widget size with proper padding
        width = self._max_rating * self._star_size + \
            (self._max_rating - 1) * self._spacing + 8  # Extra padding
        height = self._star_size + 8  # Extra vertical padding
        self.setFixedSize(width, height)

    def _setup_style(self):
        """Setup enhanced visual styling"""
        # Add subtle shadow effect
        self.setStyleSheet("""
            FluentRating {
                background-color: transparent;
                border-radius: 8px;
                padding: 4px;
            }
        """)

    def _setup_animations(self):
        """Setup enhanced animations with smoother curves"""
        # Hover animation with spring easing
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_scale"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentTransition.EASE_SPRING)

        # Press animation with crisp response
        self._press_animation = QPropertyAnimation(
            self, QByteArray(b"pressed_scale"))
        self._press_animation.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
        self._press_animation.setEasingCurve(FluentTransition.EASE_CRISP)

        # Rating change animation for celebration effect
        self._rating_change_animation = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self._rating_change_animation.setDuration(
            FluentAnimation.DURATION_FAST)
        self._rating_change_animation.setEasingCurve(
            FluentTransition.EASE_BOUNCE)

    def _get_hover_scale(self) -> float:
        return self._hover_scale

    def _set_hover_scale(self, value: float):
        if self._hover_scale != value:
            self._hover_scale = value
            self.hover_scaleChanged.emit(self._hover_scale)
            self.update()

    # Fixed Property declaration with notify signal
    hover_scale = Property(float, _get_hover_scale,
                           _set_hover_scale, None, "", notify=hover_scaleChanged)

    def _get_pressed_scale(self) -> float:
        return self._pressed_scale

    def _set_pressed_scale(self, value: float):
        if self._pressed_scale != value:
            self._pressed_scale = value
            self.pressed_scaleChanged.emit(self._pressed_scale)
            self.update()

    # Fixed Property declaration with notify signal
    pressed_scale = Property(float, _get_pressed_scale,
                             _set_pressed_scale, None, "", notify=pressed_scaleChanged)

    def setMaxRating(self, max_rating: int):
        """Set maximum rating with smooth transition"""
        if max_rating != self._max_rating:
            self._max_rating = max_rating
            # Ensure current rating doesn't exceed new max
            if self._current_rating > max_rating:
                self.setRating(max_rating)

            # Animate the layout change
            FluentRevealEffect.scale_in(
                self, duration=FluentAnimation.DURATION_FAST)
            self._setup_ui()
            self.update()

    def getMaxRating(self) -> int:
        """Get maximum rating"""
        return self._max_rating

    def setRating(self, rating: int):
        """Set current rating with enhanced feedback"""
        rating = max(0, min(rating, self._max_rating))
        if rating != self._current_rating:
            old_rating = self._current_rating
            self._current_rating = rating

            # Enhanced feedback for rating changes
            if rating > old_rating:
                # Positive feedback - pulse animation
                FluentMicroInteraction.pulse_animation(self, scale=1.1)
            elif rating < old_rating:
                # Negative feedback - subtle shake
                FluentMicroInteraction.shake_animation(self, intensity=3)

            # Staggered reveal effect for filled stars
            self._animate_rating_change(old_rating, rating)

            self.ratingChanged.emit(rating)
            self.update()

    def _animate_rating_change(self, old_rating: int, new_rating: int):
        """Animate rating changes with staggered effects"""
        # Create staggered animation for stars that changed state
        changed_stars = []
        for i in range(min(old_rating, new_rating), max(old_rating, new_rating)):
            # We can't easily animate individual stars since they're painted, not separate widgets
            # Instead, we'll create a subtle overall effect
            pass

        # Overall celebration effect for high ratings
        if new_rating >= 4:
            FluentRevealEffect.scale_in(
                self, duration=FluentAnimation.DURATION_FAST)

    def getRating(self) -> int:
        """Get current rating"""
        return self._current_rating

    def setEditable(self, editable: bool):
        """Set whether rating is editable with visual feedback"""
        if self._editable != editable:
            self._editable = editable
            self.setCursor(
                Qt.CursorShape.PointingHandCursor if editable else Qt.CursorShape.ArrowCursor)
            self.setMouseTracking(editable)

            # Visual feedback for editability change
            if editable:
                FluentRevealEffect.fade_in(
                    self, duration=FluentAnimation.DURATION_FAST)
            else:
                # Reset hover state when becoming non-editable
                self._hover_rating = 0
                self._hover_scale = 1.0
                self.update()

    def isEditable(self) -> bool:
        """Check if rating is editable"""
        return self._editable

    def setStarSize(self, size: int):
        """Set star size with smooth transition"""
        if size != self._star_size:
            self._star_size = size
            FluentRevealEffect.scale_in(
                self, duration=FluentAnimation.DURATION_FAST)
            self._setup_ui()
            self.update()

    def getStarSize(self) -> int:
        """Get star size"""
        return self._star_size

    def setSpacing(self, spacing: int):
        """Set spacing between stars with transition"""
        if spacing != self._spacing:
            self._spacing = spacing
            FluentRevealEffect.scale_in(
                self, duration=FluentAnimation.DURATION_FAST)
            self._setup_ui()
            self.update()

    def getSpacing(self) -> int:
        """Get spacing between stars"""
        return self._spacing

    def setStarStyle(self, style: str):
        """Set star style with smooth transition"""
        if style in ["star", "heart", "thumb"] and style != self._star_style:
            self._star_style = style
            FluentRevealEffect.fade_in(
                self, duration=FluentAnimation.DURATION_MEDIUM)
            self.update()

    def getStarStyle(self) -> str:
        """Get star style"""
        return self._star_style

    def paintEvent(self, _event):
        """Paint the rating stars with enhanced visuals"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = theme_manager

        # Enhanced colors with better contrast
        filled_color = theme.get_color('primary')
        empty_color = theme.get_color('border').lighter(120)
        hover_color = theme.get_color('primary').lighter(130)

        # Add subtle glow colors
        filled_glow = QColor(filled_color)
        filled_glow.setAlpha(50)
        hover_glow = QColor(hover_color)
        hover_glow.setAlpha(80)

        for i in range(self._max_rating):
            # Calculate star position with padding
            x = 4 + i * (self._star_size + self._spacing)  # Add left padding
            y = 4  # Add top padding

            # Determine star state and colors
            current_item_color: QColor
            glow_color: QColor
            filled: bool

            if self._hover_rating > 0 and i < self._hover_rating:
                current_item_color = hover_color
                glow_color = hover_glow
                filled = True
            elif i < self._current_rating:
                current_item_color = filled_color
                glow_color = filled_glow
                filled = True
            else:
                current_item_color = empty_color
                glow_color = QColor(0, 0, 0, 0)  # No glow for empty stars
                filled = False

            # Apply scaling for hover/press effects
            scale = 1.0
            if self._hover_rating > 0 and i < self._hover_rating:
                scale = self._hover_scale
            elif i < self._current_rating and self._pressed_scale != 1.0:
                scale = self._pressed_scale

            # Draw glow effect first (for filled/hovered stars)
            if filled and glow_color.alpha() > 0:
                self._draw_star_glow(
                    painter, x, y, self._star_size, glow_color, scale * 1.2)

            # Draw main star
            self._draw_star(painter, x, y, self._star_size,
                            current_item_color, filled, scale)

    def _draw_star_glow(self, painter: QPainter, x: int, y: int, size: int,
                        glow_color: QColor, scale: float = 1.0):
        """Draw glow effect behind star"""
        painter.save()

        # Apply scaling
        if scale != 1.0:
            center_x = x + size / 2
            center_y = y + size / 2
            painter.translate(center_x, center_y)
            painter.scale(scale, scale)
            painter.translate(-center_x, -center_y)

        # Draw enlarged, transparent version for glow
        glow_size = int(size * 1.2)
        glow_x = x - (glow_size - size) // 2
        glow_y = y - (glow_size - size) // 2

        if self._star_style == "star":
            self._draw_star_shape(painter, glow_x, glow_y,
                                  glow_size, glow_color, True)
        elif self._star_style == "heart":
            self._draw_heart_shape(
                painter, glow_x, glow_y, glow_size, glow_color, True)
        elif self._star_style == "thumb":
            self._draw_thumb_shape(
                painter, glow_x, glow_y, glow_size, glow_color, True)

        painter.restore()

    def _draw_star(self, painter: QPainter, x: int, y: int, size: int,
                   color: QColor, filled: bool, scale: float = 1.0):
        """Draw a star shape with enhanced styling"""
        painter.save()

        # Apply scaling with smooth center-based transformation
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
        """Draw a star shape with enhanced geometry"""
        # Improved star points for better visual appeal
        star_points = [
            (0.5, 0.0),      # Top point
            (0.63, 0.35),    # Upper right
            (1.0, 0.35),     # Right point
            (0.68, 0.58),    # Lower right inner
            (0.82, 1.0),     # Bottom right
            (0.5, 0.75),     # Bottom inner
            (0.18, 1.0),     # Bottom left
            (0.32, 0.58),    # Lower left inner
            (0.0, 0.35),     # Left point
            (0.37, 0.35),    # Upper left inner
        ]

        # Scale points to actual size
        points = []
        for px, py in star_points:
            points.append((x + px * size, y + py * size))

        # Create path with smoother curves
        path = QPainterPath()
        path.moveTo(points[0][0], points[0][1])
        for point in points[1:]:
            path.lineTo(point[0], point[1])
        path.closeSubpath()

        # Enhanced drawing with gradient-like effect
        if filled:
            # Create subtle gradient effect for filled stars
            brush = QBrush(color)
            painter.fillPath(path, brush)

            # Add inner highlight
            highlight_color = color.lighter(130)
            highlight_color.setAlpha(100)
            painter.setPen(QPen(highlight_color, 0.5))

            # Draw smaller inner star for highlight
            inner_size = size * 0.6
            inner_x = x + (size - inner_size) / 2
            inner_y = y + (size - inner_size) / 2

            inner_points = []
            # Only outer points for inner highlight
            for px, py in star_points[:5]:
                inner_points.append(
                    (inner_x + px * inner_size, inner_y + py * inner_size))

            inner_path = QPainterPath()
            inner_path.moveTo(inner_points[0][0], inner_points[0][1])
            for point in inner_points[1:]:
                inner_path.lineTo(point[0], point[1])
            inner_path.closeSubpath()

            painter.drawPath(inner_path)

        # Main outline with enhanced styling
        outline_pen = QPen(color, 2.0, Qt.PenStyle.SolidLine,
                           Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(outline_pen)
        painter.drawPath(path)

    def _draw_heart_shape(self, painter: QPainter, x: int, y: int, size: int,
                          color: QColor, filled: bool):
        """Draw a heart shape with enhanced curves"""
        path = QPainterPath()

        # Enhanced heart shape with better proportions
        cx = x + size / 2

        # Improved control points for smoother curves
        cp1x_offset = size * 0.45
        cp1y_offset = size * 0.4
        cp2x_offset = size * 0.15
        cp2y_offset = size * 0.6

        bottom_y = y + size * 0.85

        # Left curve - enhanced
        path.moveTo(cx, y + size * 0.3)
        path.cubicTo(cx - cp1x_offset, y,
                     cx - cp2x_offset * 3, y + cp2y_offset * 0.4,
                     cx, bottom_y)

        # Right curve - enhanced
        path.cubicTo(cx + cp2x_offset * 3, y + cp2y_offset * 0.4,
                     cx + cp1x_offset, y,
                     cx, y + size * 0.3)

        # Enhanced drawing
        if filled:
            painter.fillPath(path, QBrush(color))

            # Add inner glow effect
            inner_color = color.lighter(140)
            inner_color.setAlpha(80)
            painter.setBrush(QBrush(inner_color))

            # Smaller inner heart
            inner_path = QPainterPath()
            inner_cx = cx
            inner_size = size * 0.7
            inner_offset_x = size * 0.35
            inner_offset_y = size * 0.3
            inner_bottom = y + size * 0.8

            inner_path.moveTo(inner_cx, y + size * 0.35)
            inner_path.cubicTo(inner_cx - inner_offset_x, y + size * 0.1,
                               inner_cx - size * 0.1, y + size * 0.45,
                               inner_cx, inner_bottom)
            inner_path.cubicTo(inner_cx + size * 0.1, y + size * 0.45,
                               inner_cx + inner_offset_x, y + size * 0.1,
                               inner_cx, y + size * 0.35)

            painter.fillPath(inner_path, QBrush(inner_color))

        # Enhanced outline
        outline_pen = QPen(color, 2.0, Qt.PenStyle.SolidLine,
                           Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(outline_pen)
        painter.drawPath(path)

    def _draw_thumb_shape(self, painter: QPainter, x: int, y: int, size: int,
                          color: QColor, filled: bool):
        """Draw a thumbs up shape with enhanced details"""
        path = QPainterPath()

        # Enhanced thumb proportions
        fist_height = size * 0.65
        fist_width = size * 0.55
        fist_x = x + size * 0.25
        fist_y = y + size * 0.35

        # Main fist with better rounding
        fist_rect = path.addRoundedRect(fist_x, fist_y, fist_width, fist_height,
                                        size * 0.08, size * 0.08)

        # Enhanced thumb geometry
        thumb_cx = x + size * 0.2
        thumb_cy = y + size * 0.2
        thumb_radius_x = size * 0.18
        thumb_radius_y = size * 0.25

        # Thumb path with rotation
        thumb_path = QPainterPath()
        thumb_path.addEllipse(thumb_cx - thumb_radius_x, thumb_cy - thumb_radius_y,
                              2 * thumb_radius_x, 2 * thumb_radius_y)

        # Apply rotation transform for thumb
        transform = painter.transform()
        painter.translate(thumb_cx, thumb_cy)
        painter.rotate(-25)  # Better angle
        painter.translate(-thumb_cx, -thumb_cy)

        path.addPath(thumb_path)
        painter.setTransform(transform)

        # Enhanced drawing
        if filled:
            painter.fillPath(path, QBrush(color))

            # Add finger detail lines
            painter.setPen(QPen(color.darker(120), 1.0))
            for i in range(2):
                line_y = fist_y + fist_height * 0.3 + i * fist_height * 0.25
                painter.drawLine(int(fist_x + fist_width * 0.1), int(line_y),
                                 int(fist_x + fist_width * 0.9), int(line_y))

        # Enhanced outline
        outline_pen = QPen(color, 2.0, Qt.PenStyle.SolidLine,
                           Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(outline_pen)
        painter.drawPath(path)

    def mousePressEvent(self, event):
        """Handle mouse press with enhanced feedback"""
        if not self._editable:
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            rating = self._get_rating_from_position(event.position().toPoint())
            if rating > 0:
                # Enhanced press feedback
                FluentMicroInteraction.button_press(self, scale=0.95)

                # Press animation for visual feedback
                if self._press_animation:
                    self._press_animation.stop()
                    self._press_animation.setStartValue(self._pressed_scale)
                    self._press_animation.setEndValue(0.9)
                    self._press_animation.start()

                self.setRating(rating)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, _event):
        """Handle mouse release with enhanced feedback"""
        if not self._editable:
            super().mouseReleaseEvent(_event)
            return

        # Enhanced release animation
        if self._press_animation:
            self._press_animation.stop()
            self._press_animation.setStartValue(self._pressed_scale)
            self._press_animation.setEndValue(1.0)
            self._press_animation.setEasingCurve(FluentTransition.EASE_SPRING)
            self._press_animation.start()

        super().mouseReleaseEvent(_event)

    def mouseMoveEvent(self, event):
        """Handle mouse move with enhanced hover effects"""
        if not self._editable:
            super().mouseMoveEvent(event)
            return

        rating = self._get_rating_from_position(event.position().toPoint())
        if rating != self._hover_rating:
            old_hover = self._hover_rating
            self._hover_rating = rating
            self.hoverChanged.emit(rating)

            # Enhanced hover animation with micro-interactions
            if self._hover_animation:
                self._hover_animation.stop()
                self._hover_animation.setStartValue(self._hover_scale)

                if rating > 0:
                    # Hover in - scale up with glow
                    self._hover_animation.setEndValue(1.15)
                    self._hover_animation.setEasingCurve(
                        FluentTransition.EASE_SPRING)

                    # Add subtle glow effect
                    FluentMicroInteraction.hover_glow(self, intensity=0.1)
                else:
                    # Hover out - return to normal
                    self._hover_animation.setEndValue(1.0)
                    self._hover_animation.setEasingCurve(
                        FluentTransition.EASE_SMOOTH)

                self._hover_animation.start()
            self.update()

        super().mouseMoveEvent(event)

    def leaveEvent(self, _event):
        """Handle mouse leave with smooth transition"""
        if not self._editable:
            super().leaveEvent(_event)
            return

        self._hover_rating = 0
        self.hoverChanged.emit(0)

        # Smooth exit animation
        if self._hover_animation:
            self._hover_animation.stop()
            self._hover_animation.setStartValue(self._hover_scale)
            self._hover_animation.setEndValue(1.0)
            self._hover_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
            self._hover_animation.start()

        self.update()
        super().leaveEvent(_event)

    def enterEvent(self, event):
        """Handle mouse enter with welcome effect"""
        if self._editable:
            FluentRevealEffect.fade_in(
                self, duration=FluentAnimation.DURATION_FAST)
        super().enterEvent(event)

    def _get_rating_from_position(self, pos):
        """Get rating value from mouse position with enhanced hit detection"""
        if pos.y() < 0 or pos.y() > self.height():
            return 0

        # Enhanced hit detection with padding consideration
        for i in range(self._max_rating):
            # Account for padding
            star_x_start = 4 + i * (self._star_size + self._spacing)
            star_x_end = star_x_start + self._star_size

            # More forgiving hit detection - include some spacing
            hit_area_start = star_x_start - \
                (self._spacing // 2 if i > 0 else 0)
            hit_area_end = star_x_end + \
                (self._spacing // 2 if i < self._max_rating - 1 else 0)

            if hit_area_start <= pos.x() <= hit_area_end:
                return i + 1

        return 0

    def _on_theme_changed(self, _=None):
        """Handle theme change with smooth transition"""
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_MEDIUM)
        self.update()

    def resizeEvent(self, event):
        """Handle resize with smooth transition"""
        super().resizeEvent(event)
        if event.oldSize().isValid():
            FluentRevealEffect.scale_in(
                self, duration=FluentAnimation.DURATION_FAST)
