"""
Enhanced Fluent Design Style Rating Component
Implements modern PySide6 features with smooth animations, responsive design,
and optimized performance following QFluentWidget patterns.
"""

from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect, QSizePolicy
from PySide6.QtCore import (Qt, Signal, QPropertyAnimation, Property, QByteArray,
                            QParallelAnimationGroup, QSequentialAnimationGroup, QTimer,
                            QEasingCurve, QRect, QRectF, QPointF)
from PySide6.QtGui import (QPainter, QPainterPath, QColor, QPen, QBrush, QLinearGradient,
                           QRadialGradient, QFont, QFontMetrics, QPalette)
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import FluentRevealEffect, FluentMicroInteraction, FluentTransition
from typing import Optional, List, Callable, Dict, Any


class EnhancedFluentRating(QWidget):
    """
    Enhanced Fluent Design style rating component with modern features:

    Features:
    - Smooth animated transitions with performance optimization
    - Dynamic theme harmonization across all states
    - Memory-efficient widget lifecycle management
    - Responsive layout with fluid animations
    - Advanced micro-interactions and accessibility
    - Dynamic content loading with optimized repainting
    """

    # Enhanced signals
    ratingChanged = Signal(int)
    hoverChanged = Signal(int)
    animationFinished = Signal()
    themeUpdated = Signal()

    # Animation property signals
    hover_scaleChanged = Signal(float)
    pressed_scaleChanged = Signal(float)
    glow_intensityChanged = Signal(float)
    rotation_angleChanged = Signal(float)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Core properties
        self._max_rating = 5
        self._current_rating = 0
        self._hover_rating = 0
        self._star_size = 32
        self._spacing = 8
        self._editable = True
        self._read_only = False
        self._star_style = "star"

        # Animation properties
        self._hover_scale = 1.0
        self._pressed_scale = 1.0
        self._glow_intensity = 0.0
        self._rotation_angle = 0.0

        # Performance flags
        self._animation_enabled = True
        self._cache_enabled = True

        # Animation storage
        self._animations: Dict[str, QPropertyAnimation] = {}
        self._animation_groups: Dict[str, Any] = {}

        # Cached objects
        self._cached_colors: Dict[str, QColor] = {}
        self._cached_gradients: Dict[str, Any] = {}
        self._cached_paths: Dict[str, QPainterPath] = {}

        # Initialize
        self._init_component()

    def _init_component(self):
        """Initialize all component aspects"""
        self._setup_properties()
        self._setup_ui()
        self._setup_theme()
        self._setup_animations()
        self._setup_accessibility()
        self._connect_signals()
        self._play_entrance_animation()

    def _setup_properties(self):
        """Setup widget properties"""
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _setup_ui(self):
        """Setup UI layout"""
        self._update_cursor()
        self._calculate_size()

    def _calculate_size(self):
        """Calculate optimal widget size"""
        width = self._max_rating * self._star_size + \
            (self._max_rating - 1) * self._spacing + 16
        height = self._star_size + 16
        self.setMinimumSize(width, height)
        self.setFixedSize(width, height)

    def _update_cursor(self):
        """Update cursor based on state"""
        if self._editable and not self._read_only:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def _setup_theme(self):
        """Setup theme integration"""
        self._cache_theme_colors()
        self._cache_gradients()
        self._apply_styles()

    def _cache_theme_colors(self):
        """Cache theme colors for performance"""
        if not theme_manager:
            # Fallback colors
            self._cached_colors.update({
                'primary': QColor('#0078d4'),
                'border': QColor('#d1d1d1'),
                'surface': QColor('#ffffff'),
            })
            return

        self._cached_colors.update({
            'primary': theme_manager.get_color('primary'),
            'secondary': theme_manager.get_color('secondary'),
            'surface': theme_manager.get_color('surface'),
            'border': theme_manager.get_color('border'),
            'text_primary': theme_manager.get_color('text_primary'),
        })

        # Create variants
        primary = self._cached_colors['primary']
        self._cached_colors.update({
            'primary_hover': primary.lighter(115),
            'primary_pressed': primary.darker(110),
            'primary_glow': QColor(primary.red(), primary.green(), primary.blue(), 80),
            'empty_star': self._cached_colors['border'].lighter(130),
        })

    def _cache_gradients(self):
        """Cache gradient objects"""
        primary = self._cached_colors['primary']

        # Filled star gradient
        filled = QLinearGradient(0, 0, 0, self._star_size)
        filled.setColorAt(0, primary.lighter(120))
        filled.setColorAt(0.5, primary)
        filled.setColorAt(1, primary.darker(110))
        self._cached_gradients['filled'] = filled

        # Hover gradient
        hover = QLinearGradient(0, 0, 0, self._star_size)
        hover_color = self._cached_colors['primary_hover']
        hover.setColorAt(0, hover_color.lighter(130))
        hover.setColorAt(0.5, hover_color)
        hover.setColorAt(1, hover_color.darker(105))
        self._cached_gradients['hover'] = hover

    def _apply_styles(self):
        """Apply widget styles"""
        background = self._cached_colors.get('surface', QColor('#ffffff'))
        primary = self._cached_colors.get('primary', QColor('#0078d4'))

        self.setStyleSheet(f"""
            EnhancedFluentRating {{
                background-color: {background.name()};
                border-radius: 8px;
                padding: 4px;
            }}
            EnhancedFluentRating:focus {{
                border: 2px solid {primary.name()};
            }}
        """)

    def _setup_animations(self):
        """Setup animation system"""
        # Hover scale animation
        hover_anim = QPropertyAnimation(self, QByteArray(b"hover_scale"))
        hover_anim.setDuration(FluentAnimation.DURATION_FAST)
        hover_anim.setEasingCurve(FluentTransition.EASE_SPRING)
        self._animations['hover_scale'] = hover_anim

        # Press animation
        press_anim = QPropertyAnimation(self, QByteArray(b"pressed_scale"))
        press_anim.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
        press_anim.setEasingCurve(FluentTransition.EASE_CRISP)
        self._animations['press'] = press_anim

        # Glow animation
        glow_anim = QPropertyAnimation(self, QByteArray(b"glow_intensity"))
        glow_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
        glow_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        self._animations['glow'] = glow_anim

        # Rotation animation
        rotation_anim = QPropertyAnimation(self, QByteArray(b"rotation_angle"))
        rotation_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
        rotation_anim.setEasingCurve(FluentTransition.EASE_ELASTIC)
        self._animations['rotation'] = rotation_anim

    def _setup_accessibility(self):
        """Setup accessibility features"""
        self.setAccessibleName("Rating Component")
        self._update_accessibility()

    def _update_accessibility(self):
        """Update accessibility description"""
        self.setAccessibleDescription(
            f"Rating: {self._current_rating} out of {self._max_rating} stars"
        )

    def _connect_signals(self):
        """Connect signals"""
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _play_entrance_animation(self):
        """Play entrance animation"""
        if self._animation_enabled:
            FluentRevealEffect.fade_in(
                self, duration=FluentAnimation.DURATION_MEDIUM)

    # Property implementations
    def _get_hover_scale(self) -> float:
        return self._hover_scale

    def _set_hover_scale(self, value: float):
        if abs(self._hover_scale - value) > 0.001:
            self._hover_scale = value
            self.hover_scaleChanged.emit(value)
            self._schedule_update()

    hover_scale = Property(float, _get_hover_scale,
                           _set_hover_scale, None, "", notify=hover_scaleChanged)

    def _get_pressed_scale(self) -> float:
        return self._pressed_scale

    def _set_pressed_scale(self, value: float):
        if abs(self._pressed_scale - value) > 0.001:
            self._pressed_scale = value
            self.pressed_scaleChanged.emit(value)
            self._schedule_update()

    pressed_scale = Property(float, _get_pressed_scale,
                             _set_pressed_scale, None, "", notify=pressed_scaleChanged)

    def _get_glow_intensity(self) -> float:
        return self._glow_intensity

    def _set_glow_intensity(self, value: float):
        if abs(self._glow_intensity - value) > 0.001:
            self._glow_intensity = value
            self.glow_intensityChanged.emit(value)
            self._schedule_update()

    glow_intensity = Property(float, _get_glow_intensity,
                              _set_glow_intensity, None, "", notify=glow_intensityChanged)

    def _get_rotation_angle(self) -> float:
        return self._rotation_angle

    def _set_rotation_angle(self, value: float):
        if abs(self._rotation_angle - value) > 0.001:
            self._rotation_angle = value
            self.rotation_angleChanged.emit(value)
            self._schedule_update()

    rotation_angle = Property(float, _get_rotation_angle,
                              _set_rotation_angle, None, "", notify=rotation_angleChanged)

    def _schedule_update(self):
        """Schedule optimized update"""
        if not hasattr(self, '_update_timer'):
            self._update_timer = QTimer(self)
            self._update_timer.setSingleShot(True)
            self._update_timer.timeout.connect(self.update)
            self._update_timer.setInterval(16)  # 60 FPS

        if not self._update_timer.isActive():
            self._update_timer.start()

    # Public API
    def setMaxRating(self, max_rating: int):
        """Set maximum rating"""
        if max_rating <= 0 or max_rating == self._max_rating:
            return

        self._max_rating = max_rating
        if self._current_rating > max_rating:
            self.setRating(max_rating)

        self._calculate_size()
        self._update_accessibility()
        self.update()

    def getMaxRating(self) -> int:
        return self._max_rating

    def setRating(self, rating: int):
        """Set current rating"""
        rating = max(0, min(rating, self._max_rating))
        if rating != self._current_rating:
            old_rating = self._current_rating
            self._current_rating = rating

            self._play_rating_feedback(old_rating, rating)
            self.ratingChanged.emit(rating)
            self._update_accessibility()
            self._schedule_update()

    def getRating(self) -> int:
        return self._current_rating

    def setEditable(self, editable: bool):
        """Set editable state"""
        if self._editable != editable:
            self._editable = editable
            self._update_cursor()
            self.setMouseTracking(editable)

            if not editable:
                self._hover_rating = 0
                self._hover_scale = 1.0
                self._schedule_update()

    def isEditable(self) -> bool:
        return self._editable

    def setStarStyle(self, style: str):
        """Set star style"""
        valid_styles = ["star", "heart", "thumb"]
        if style in valid_styles and style != self._star_style:
            self._star_style = style
            self._cached_paths.clear()
            self.update()

    def getStarStyle(self) -> str:
        return self._star_style

    def setStarSize(self, size: int):
        """Set star size"""
        if size > 0 and size != self._star_size:
            self._star_size = size
            self._calculate_size()
            self._cached_paths.clear()
            self._cache_gradients()
            self.update()

    def getStarSize(self) -> int:
        return self._star_size

    def _play_rating_feedback(self, old_rating: int, new_rating: int):
        """Play rating change feedback"""
        if not self._animation_enabled:
            return

        if new_rating > old_rating:
            if new_rating >= 4:
                # High rating celebration
                if 'rotation' in self._animations:
                    anim = self._animations['rotation']
                    anim.setStartValue(0.0)
                    anim.setEndValue(360.0)
                    anim.start()
            else:
                FluentMicroInteraction.pulse_animation(self, scale=1.1)
        elif new_rating < old_rating:
            FluentMicroInteraction.shake_animation(self, intensity=3)

    # Paint event with optimized rendering
    def paintEvent(self, event):
        """Paint the rating component"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get colors
        filled_color = self._cached_colors.get('primary', QColor('#0078d4'))
        empty_color = self._cached_colors.get('empty_star', QColor('#d1d1d1'))
        hover_color = self._cached_colors.get(
            'primary_hover', filled_color.lighter(115))

        # Draw stars
        for i in range(self._max_rating):
            x = 8 + i * (self._star_size + self._spacing)
            y = 8

            # Determine state
            is_filled = i < self._current_rating
            is_hovered = self._hover_rating > 0 and i < self._hover_rating

            # Apply transforms
            painter.save()

            # Scale transform
            scale = 1.0
            if is_hovered:
                scale = self._hover_scale
            elif is_filled and self._pressed_scale != 1.0:
                scale = self._pressed_scale

            if scale != 1.0:
                center_x = x + self._star_size / 2
                center_y = y + self._star_size / 2
                painter.translate(center_x, center_y)
                painter.scale(scale, scale)
                painter.translate(-center_x, -center_y)

            # Rotation transform
            if self._rotation_angle != 0.0:
                center_x = x + self._star_size / 2
                center_y = y + self._star_size / 2
                painter.translate(center_x, center_y)
                painter.rotate(self._rotation_angle)
                painter.translate(-center_x, -center_y)

            # Draw glow if needed
            if (is_filled or is_hovered) and self._glow_intensity > 0:
                self._draw_star_glow(painter, x, y)

            # Draw star
            color = hover_color if is_hovered else (
                filled_color if is_filled else empty_color)
            self._draw_star(painter, x, y, color, is_filled or is_hovered)

            painter.restore()

    def _draw_star_glow(self, painter: QPainter, x: int, y: int):
        """Draw glow effect"""
        glow_color = self._cached_colors.get(
            'primary_glow', QColor(0, 120, 212, 80))
        glow_color.setAlpha(int(glow_color.alpha() * self._glow_intensity))

        glow_size = int(self._star_size * 1.3)
        glow_x = x - (glow_size - self._star_size) // 2
        glow_y = y - (glow_size - self._star_size) // 2

        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.PenStyle.NoPen)

        if self._star_style == "star":
            path = self._get_star_path(glow_x, glow_y, glow_size)
        else:
            path = self._get_star_path(
                glow_x, glow_y, glow_size)  # Simplified for now

        painter.drawPath(path)

    def _draw_star(self, painter: QPainter, x: int, y: int, color: QColor, filled: bool):
        """Draw individual star"""
        if self._star_style == "star":
            path = self._get_star_path(x, y, self._star_size)
        elif self._star_style == "heart":
            path = self._get_heart_path(x, y, self._star_size)
        else:  # thumb
            path = self._get_thumb_path(x, y, self._star_size)

        if filled:
            if 'filled' in self._cached_gradients:
                painter.setBrush(QBrush(self._cached_gradients['filled']))
            else:
                painter.setBrush(QBrush(color))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.setPen(QPen(color, 2.0, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawPath(path)

    def _get_star_path(self, x: int, y: int, size: int) -> QPainterPath:
        """Get cached star path"""
        cache_key = f"star_{x}_{y}_{size}"
        if cache_key in self._cached_paths:
            return self._cached_paths[cache_key]

        path = QPainterPath()

        # Star points (optimized coordinates)
        points = [
            (0.5, 0.0), (0.63, 0.35), (1.0, 0.35), (0.68, 0.58),
            (0.82, 1.0), (0.5, 0.75), (0.18, 1.0), (0.32, 0.58),
            (0.0, 0.35), (0.37, 0.35)
        ]

        # Scale points
        scaled_points = [(x + px * size, y + py * size) for px, py in points]

        path.moveTo(scaled_points[0][0], scaled_points[0][1])
        for point in scaled_points[1:]:
            path.lineTo(point[0], point[1])
        path.closeSubpath()

        self._cached_paths[cache_key] = path
        return path

    def _get_heart_path(self, x: int, y: int, size: int) -> QPainterPath:
        """Get heart path"""
        path = QPainterPath()
        cx = x + size / 2

        # Heart shape
        path.moveTo(cx, y + size * 0.3)
        path.cubicTo(cx - size * 0.45, y, cx - size * 0.45,
                     y + size * 0.6, cx, y + size * 0.85)
        path.cubicTo(cx + size * 0.45, y + size * 0.6, cx +
                     size * 0.45, y, cx, y + size * 0.3)

        return path

    def _get_thumb_path(self, x: int, y: int, size: int) -> QPainterPath:
        """Get thumb path"""
        path = QPainterPath()

        # Simplified thumb shape
        thumb_rect = QRectF(x + size * 0.2, y + size *
                            0.3, size * 0.6, size * 0.6)
        path.addRoundedRect(thumb_rect, size * 0.1, size * 0.1)

        # Add thumb extension
        thumb_ext = QRectF(x + size * 0.1, y + size *
                           0.1, size * 0.3, size * 0.4)
        path.addRoundedRect(thumb_ext, size * 0.05, size * 0.05)

        return path

    # Event handlers
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if not self._editable or self._read_only:
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            rating = self._get_rating_from_position(event.position().toPoint())
            if rating > 0:
                # Press feedback
                if 'press' in self._animations:
                    anim = self._animations['press']
                    anim.setStartValue(1.0)
                    anim.setEndValue(0.95)
                    anim.start()

                self.setRating(rating)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if not self._editable or self._read_only:
            super().mouseReleaseEvent(event)
            return

        # Release animation
        if 'press' in self._animations:
            anim = self._animations['press']
            anim.setStartValue(self._pressed_scale)
            anim.setEndValue(1.0)
            anim.start()

        super().mouseReleaseEvent(event)

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
            if 'hover_scale' in self._animations:
                anim = self._animations['hover_scale']
                anim.setStartValue(self._hover_scale)
                anim.setEndValue(1.15 if rating > 0 else 1.0)
                anim.start()

            # Glow animation
            if 'glow' in self._animations:
                anim = self._animations['glow']
                anim.setStartValue(self._glow_intensity)
                anim.setEndValue(0.8 if rating > 0 else 0.0)
                anim.start()

        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave"""
        if self._editable:
            self._hover_rating = 0
            self.hoverChanged.emit(0)

            # Exit animations
            if 'hover_scale' in self._animations:
                anim = self._animations['hover_scale']
                anim.setStartValue(self._hover_scale)
                anim.setEndValue(1.0)
                anim.start()

            if 'glow' in self._animations:
                anim = self._animations['glow']
                anim.setStartValue(self._glow_intensity)
                anim.setEndValue(0.0)
                anim.start()

        super().leaveEvent(event)

    def keyPressEvent(self, event):
        """Handle keyboard input"""
        if not self._editable or self._read_only:
            super().keyPressEvent(event)
            return

        if event.key() in [Qt.Key.Key_Left, Qt.Key.Key_Down]:
            new_rating = max(0, self._current_rating - 1)
            self.setRating(new_rating)
            event.accept()
        elif event.key() in [Qt.Key.Key_Right, Qt.Key.Key_Up]:
            new_rating = min(self._max_rating, self._current_rating + 1)
            self.setRating(new_rating)
            event.accept()
        elif event.key() >= Qt.Key.Key_1 and event.key() <= Qt.Key.Key_9:
            rating = event.key() - Qt.Key.Key_1 + 1
            if rating <= self._max_rating:
                self.setRating(rating)
                event.accept()
        else:
            super().keyPressEvent(event)

    def _get_rating_from_position(self, pos) -> int:
        """Get rating from mouse position"""
        if pos.y() < 0 or pos.y() > self.height():
            return 0

        for i in range(self._max_rating):
            star_x = 8 + i * (self._star_size + self._spacing)
            star_end = star_x + self._star_size

            if star_x <= pos.x() <= star_end:
                return i + 1

        return 0

    def _on_theme_changed(self):
        """Handle theme change"""
        self._cache_theme_colors()
        self._cache_gradients()
        self._apply_styles()
        self._cached_paths.clear()
        self.themeUpdated.emit()
        self.update()

    # Cleanup
    def closeEvent(self, event):
        """Clean up resources"""
        # Stop all animations
        for anim in self._animations.values():
            if anim.state() == QPropertyAnimation.State.Running:
                anim.stop()

        # Clear caches
        self._cached_colors.clear()
        self._cached_gradients.clear()
        self._cached_paths.clear()

        super().closeEvent(event)
