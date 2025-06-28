"""
 Fluent Design Avatar Component
Modern avatar display with advanced animations, theming, and performance optimizations
"""

import math
import hashlib
from functools import lru_cache
from typing import Optional
from enum import Enum
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QGraphicsDropShadowEffect,
                              QGraphicsEffect, QGraphicsOpacityEffect)
from PySide6.QtCore import (Qt, Signal, QSize, Property, QPropertyAnimation,
                           QParallelAnimationGroup, QByteArray, QPoint,
                           QEasingCurve, QTimer, QObject, QEvent, QRect)
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QPixmap, QFont,
                            QPainterPath, QPaintEvent, QEnterEvent, QResizeEvent,
                            QLinearGradient, QFontMetrics, QMouseEvent, QFocusEvent,
                            QCloseEvent)
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                      FluentRevealEffect, FluentSequence)
from core.base import FluentBaseWidget
from typing import Optional, List
from enum import Enum
import hashlib
from functools import lru_cache


class AvatarPresence(Enum):
    """Avatar presence status indicators"""
    NONE = "none"
    AVAILABLE = "available"
    BUSY = "busy"
    AWAY = "away"
    DO_NOT_DISTURB = "do_not_disturb"
    OFFLINE = "offline"


class AvatarActivity(Enum):
    """Avatar activity indicators"""
    NONE = "none"
    TYPING = "typing"
    RECORDING = "recording"
    STREAMING = "streaming"


class FluentAvatar(FluentBaseWidget):
    """ Fluent Design avatar component with modern animations and features"""
    
    # Change notification signals
    hoverProgressChanged = Signal(float)
    pressProgressChanged = Signal(float)
    scaleProgressChanged = Signal(float)
    glowProgressChanged = Signal(float)
    presenceProgressChanged = Signal(float)
    loadingProgressChanged = Signal(float)
    """ Fluent Design avatar component with modern animations and features"""

    def setText(self, text: str):
        """Set the text displayed in the avatar"""
        self._text = text
        self.update()
    
    def animateGlow(self):
        """Animate glow effect"""
        self._glow_animation = self._create_animation('glow', 'glow_progress', 200)
        self._glow_animation.setStartValue(0.0)
        self._glow_animation.setEndValue(1.0)
        self._glow_animation.start()
    
    def animatePulse(self):
        """Animate pulse effect"""
        self._scale_animation = self._create_animation('scale', 'scale_progress', 150)
        self._scale_animation.setStartValue(1.0)
        self._scale_animation.setEndValue(1.1)
        self._scale_animation.start()
    
    def animateBounce(self):
        """Animate bounce effect"""
        self._bounce_animation = self._create_animation('bounce', 'scale_progress', 300)
        self._bounce_animation.setStartValue(1.0)
        self._bounce_animation.setEndValue(0.8)
        self._bounce_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        self._bounce_animation.start()

    class Size(Enum):
        TINY = 16
        SMALL = 24
        MEDIUM = 32
        LARGE = 40
        XLARGE = 56
        XXLARGE = 72
        XXXLARGE = 96

    class Shape(Enum):
        CIRCLE = "circle"
        ROUNDED_SQUARE = "rounded_square"
        SQUARE = "square"
        HEXAGON = "hexagon"

    class Style(Enum):
        PHOTO = "photo"
        INITIALS = "initials"
        ICON = "icon"
        PLACEHOLDER = "placeholder"
        GRADIENT = "gradient"

    #  signals
    clicked = Signal()
    double_clicked = Signal()
    hovered = Signal(bool)  # True for enter, False for leave
    presence_changed = Signal(AvatarPresence)
    activity_changed = Signal(AvatarActivity)
    size_changed = Signal(Size)
    photo_loaded = Signal(bool)  # True for success, False for failure
    
    def __init__(self, size: Size = Size.MEDIUM, shape: Shape = Shape.CIRCLE,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Core properties
        self._size = size
        self._shape = shape
        self._style = self.Style.PLACEHOLDER
        self._pixmap = None
        self._initials = ""
        self._name = ""
        self._icon = ""
        self._presence = AvatarPresence.NONE
        self._activity = AvatarActivity.NONE

        #  interaction properties
        self._clickable = False
        self._double_clickable = False
        self._hover_enabled = True
        self._focus_enabled = True

        # Visual properties
        self._border_width = 0
        self._border_color = None
        self._background_color = None
        self._custom_gradient = None
        self._shadow_enabled = True
        self._glow_enabled = False

        # Animation state properties
        self._hover_progress = 0.0
        self._press_progress = 0.0
        self._scale_progress = 1.0
        self._glow_progress = 0.0
        self._presence_progress = 0.0
        self._loading_progress = 0.0
        self._position_animation = None        # Performance optimization
        self._cached_pixmap = None
        self._cached_colors = {}
        self._paint_cache_valid = False
        self._last_paint_size = QSize()

        # Initialize state
        self._text = ""
        self._is_disposing = False
        self._timers = []
        
        # Initialize animation containers (animations will be created later)
        self._animation_group = None
        self._animations = {}  # Store animations by name

        # Enhanced UI setup
        self._setup_ui()
        self._setup_enhanced_theming()
        self._setup_advanced_animations()
        self._setup_accessibility()
        self._setup_performance_monitoring()

        # Connect to theme manager
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Responsive layout support
        if parent:
            parent.installEventFilter(self)

    def _setup_ui(self):
        """Setup  UI components with responsive design"""
        # Calculate responsive size
        base_size = self._size.value
        parent_widget = self.parentWidget()
        if parent_widget:
            parent_size = parent_widget.size()
            if parent_size.width() < 400:  # Mobile/compact view
                base_size = int(base_size * 0.8)

        self.setFixedSize(base_size, base_size)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)        # Enhanced shadow effect
        if self._shadow_enabled:
            self._setup_shadow_effect()

    def _setup_shadow_effect(self):
        """Setup enhanced shadow effects"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def _setup_enhanced_theming(self):
        """Setup enhanced theming system with caching"""
        self._update_theme_colors()
        self._setup_responsive_styles()

    def _update_theme_colors(self):
        """Update and cache theme colors for performance"""
        theme = theme_manager

        # Cache frequently used colors
        self._cached_colors = {
            'accent': QColor(theme.get_color('primary')),
            'accent_light': QColor(theme.get_color('accent_light')),
            'background': QColor(theme.get_color('background')),
            'surface': QColor(theme.get_color('surface')),
            'border': QColor(theme.get_color('border')),
            'text_primary': QColor(theme.get_color('text_primary')),
            'text_secondary': QColor(theme.get_color('text_secondary')),
        }
        
        # Apply theme-specific adjustments
        if self._background_color is None:
            self._bg_color = self._cached_colors['accent_light']
        else:
            self._bg_color = self._background_color

        if self._border_color is None:
            self._border_col = self._cached_colors['border']
        else:
            self._border_col = self._border_color
            
        self._invalidate_paint_cache()

    def _setup_responsive_styles(self):
        """Setup responsive styling based on size and context"""        # Adjust border width based on size
        if self._size.value <= 24 and self._border_width == 0:
            self._border_width = 1
        elif self._size.value >= 56 and self._border_width == 0:
            self._border_width = 2

    def _setup_advanced_animations(self):
        """Setup advanced animation system with performance optimization"""
        # Create animation group for coordinated animations
        self._animation_group = QParallelAnimationGroup(self)
        
        # Enhanced hover animation with spring easing
        self._hover_animation = QPropertyAnimation(self, QByteArray(b"hover_progress"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentTransition.EASE_SPRING)
        
        # Enhanced press animation with crisp response
        self._press_animation = QPropertyAnimation(self, QByteArray(b"press_progress"))
        self._press_animation.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
        self._press_animation.setEasingCurve(FluentTransition.EASE_CRISP)

        # Scale animation for smooth interactions
        self._scale_animation = QPropertyAnimation(self, QByteArray(b"scale_progress"))
        self._scale_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._scale_animation.setEasingCurve(FluentTransition.EASE_SPRING)

        # Glow animation for special states
        self._glow_animation = QPropertyAnimation(self, QByteArray(b"glow_progress"))
        self._glow_animation.setDuration(800)
        self._glow_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._glow_animation.setLoopCount(-1)  # Infinite loop for glow effect
        
        # Presence indicator animation
        self._presence_animation = QPropertyAnimation(self, QByteArray(b"presence_progress"))
        self._presence_animation.setDuration(400)
        self._presence_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
        
        # Loading animation
        self._loading_animation = QPropertyAnimation(self, QByteArray(b"loading_progress"))
        self._loading_animation.setDuration(1200)
        self._loading_animation.setEasingCurve(QEasingCurve.Type.Linear)
        self._loading_animation.setLoopCount(-1)

        # Store animations for easy access
        self._animations.update({
            'hover': self._hover_animation,
            'press': self._press_animation,
            'scale': self._scale_animation,
            'glow': self._glow_animation,
            'presence': self._presence_animation,
            'loading': self._loading_animation
        })

        # Schedule entrance animation (delayed to ensure widget is ready)
        QTimer.singleShot(50, self._schedule_entrance_animation)

    def _schedule_entrance_animation(self):
        """Schedule entrance animation with staggered timing"""
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self._show_entrance_animation)
        timer.start(50)
        self._timers.append(timer)

    def _show_entrance_animation(self):
        """ entrance animation with multiple effects"""
        if self._is_disposing:
            return
            
        entrance_sequence = FluentSequence(self)
        
        # Initial state
        self._scale_progress = 0.3
        self.setProperty("opacity", 0.0)
        
        # Fade and scale in
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self, 300))
        entrance_sequence.addPause(50)
        entrance_sequence.addCallback(
            lambda: self._animate_scale(0.3, 1.0, 350))
        
        # Add subtle bounce for larger avatars
        if self._size.value >= 40:
            entrance_sequence.addPause(200)
            entrance_sequence.addCallback(
                lambda: FluentMicroInteraction.pulse_animation(self, 1.05))
        
        entrance_sequence.start()

    def _animate_scale(self, start: float, end: float, duration: int):
        """Animate scale with custom parameters"""
        self._scale_animation.stop()
        self._scale_animation.setStartValue(start)
        self._scale_animation.setEndValue(end)
        self._scale_animation.setDuration(duration)
        self._scale_animation.start()

    def _setup_accessibility(self):
        """Setup accessibility features"""
        self.setAccessibleName("Avatar")
        self.setAccessibleDescription("User avatar image")
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus if self._focus_enabled else Qt.FocusPolicy.NoFocus)

    def _setup_performance_monitoring(self):
        """Setup performance monitoring and optimization"""
        # Install resize event filter for responsive updates
        self.installEventFilter(self)
        
        # Schedule periodic cache cleanup
        cleanup_timer = QTimer(self)
        cleanup_timer.timeout.connect(self._cleanup_cache)
        cleanup_timer.start(30000)  # Every 30 seconds
        self._timers.append(cleanup_timer)

    def paintEvent(self, event: QPaintEvent):
        """ paint event with optimized rendering and caching"""
        if self._is_disposing:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = self.rect()
        
        # Performance optimization: skip painting if rect is invalid
        if rect.isEmpty():
            return

        # Apply scale transformation for smooth animations
        if self._scale_progress != 1.0:
            center = rect.center()
            painter.translate(center)
            painter.scale(self._scale_progress, self._scale_progress)
            painter.translate(-center)

        # Create  clipping path with shape support
        path = self._create_shape_path(rect)
        painter.setClipPath(path)

        # Draw layered components with  styling
        self._draw__background(painter, rect)
        self._draw_content(painter, rect)
        
        # Draw overlays and effects
        if self._border_width > 0:
            self._draw__border(painter, rect, path)
        
        if self._clickable and (self._hover_progress > 0 or self._press_progress > 0):
            self._draw_interaction_effects(painter, rect, path)
            
        if self._glow_enabled and self._glow_progress > 0:
            self._draw_glow_effect(painter, rect, path)
            
        if self._presence != AvatarPresence.NONE:
            self._draw_presence_indicator(painter, rect)
            
        if self._activity != AvatarActivity.NONE:
            self._draw_activity_indicator(painter, rect)

    def _create_shape_path(self, rect: QRect) -> QPainterPath:
        """Create  shape path with more shape options"""
        path = QPainterPath()
        
        if self._shape == self.Shape.CIRCLE:
            path.addEllipse(rect)
        elif self._shape == self.Shape.ROUNDED_SQUARE:
            corner_radius = min(rect.width(), rect.height()) * 0.25
            path.addRoundedRect(rect, corner_radius, corner_radius)
        elif self._shape == self.Shape.HEXAGON:
            self._create_hexagon_path(path, rect)
        else:  # SQUARE
            path.addRect(rect)
            
        return path

    def _create_hexagon_path(self, path: QPainterPath, rect: QRect):
        """Create hexagon shape path"""
        center_x = rect.center().x()
        center_y = rect.center().y()
        radius = min(rect.width(), rect.height()) / 2 * 0.9
        
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append(QPoint(int(x), int(y)))
        
        if points:
            path.moveTo(points[0])
            for point in points[1:]:
                path.lineTo(point)
            path.closeSubpath()

    def _draw__background(self, painter: QPainter, rect: QRect):
        """Draw background with  gradient and effects"""
        if self._style == self.Style.PHOTO and self._pixmap:
            return  # Photo handles its own background
        
        # Create gradient background for  visual appeal
        if self._style == self.Style.GRADIENT or self._custom_gradient:
            self._draw_gradient_background(painter, rect)
        else:
            self._draw_solid_background(painter, rect)

    def _draw_gradient_background(self, painter: QPainter, rect: QRect):
        """Draw gradient background"""
        if self._custom_gradient:
            gradient = self._custom_gradient
        else:
            # Generate gradient from name/initials
            if self._name or self._initials:
                primary_color = self._generate_color_from_string(self._name or self._initials)
                secondary_color = primary_color.lighter(120)
            else:
                primary_color = self._cached_colors['accent']
                secondary_color = self._cached_colors['accent_light']
            
            gradient = QLinearGradient(0, 0, rect.width(), rect.height())
            gradient.setColorAt(0, primary_color)
            gradient.setColorAt(1, secondary_color)
        
        painter.fillRect(rect, QBrush(gradient))

    def _draw_solid_background(self, painter: QPainter, rect: QRect):
        """Draw solid color background with enhancements"""
        # Generate or use cached background color
        if self._name or self._initials:
            bg_color = self._get_cached_color(self._name or self._initials)
        else:
            bg_color = self._bg_color

        # Apply hover effect
        if self._hover_progress > 0:
            overlay_color = QColor(255, 255, 255, int(25 * self._hover_progress))
            bg_color = self._blend_colors(bg_color, overlay_color)

        painter.fillRect(rect, bg_color)

    @lru_cache(maxsize=100)
    def _get_cached_color(self, text: str) -> QColor:
        """Get cached color for text with LRU caching"""
        return self._generate_color_from_string(text)

    def _draw_content(self, painter: QPainter, rect: QRect):
        """Draw main content based on style"""
        if self._style == self.Style.PHOTO and self._pixmap:
            self._draw__photo(painter, rect)
        elif self._style == self.Style.INITIALS and self._initials:
            self._draw__initials(painter, rect)
        elif self._style == self.Style.ICON and self._icon:
            self._draw__icon(painter, rect)
        else:
            self._draw__placeholder(painter, rect)

    def _invalidate_paint_cache(self):
        """Invalidate paint cache to force repaint"""
        self._paint_cache_valid = False
        self.update()

    def _cleanup_cache(self):
        """Cleanup cached resources"""
        if not self._is_disposing:
            # Clear cached pixmap if not in use
            if self._cached_pixmap and self._style != self.Style.PHOTO:
                self._cached_pixmap = None
            
            # Clear color cache if theme changed
            if self._cached_colors and len(self._cached_colors) > 10:
                self._cached_colors.clear()
                self._update_theme_colors()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """ event filter for responsive behavior"""
        if obj == self.parentWidget() and event.type() == QEvent.Type.Resize:
            self._handle_parent_resize()
        elif obj == self and event.type() == QEvent.Type.Resize:
            if isinstance(event, QResizeEvent):
                self._handle_self_resize(event)
        return super().eventFilter(obj, event)

    def _handle_parent_resize(self):
        """Handle parent widget resize for responsive design"""
        parent_widget = self.parentWidget()
        if parent_widget:
            parent_size = parent_widget.size()
            # Adjust size for mobile/compact views
            if parent_size.width() < 400:
                scale_factor = 0.8
            elif parent_size.width() > 1200:
                scale_factor = 1.1
            else:
                scale_factor = 1.0
            
            new_size = int(self._size.value * scale_factor)
            if self.width() != new_size:
                self.setFixedSize(new_size, new_size)

    def _handle_self_resize(self, event: QResizeEvent):
        """Handle self resize events"""
        if event.size() != self._last_paint_size:
            self._last_paint_size = event.size()
            self._invalidate_paint_cache()
            if self._shadow_enabled:
                self._setup_shadow_effect()  # Adjust shadow for new size

    def _draw__photo(self, painter: QPainter, rect: QRect):
        """Draw photo with  rendering and caching"""
        if not self._pixmap:
            return

        # Use cached scaled pixmap for performance
        if not self._cached_pixmap or self._cached_pixmap.size() != rect.size():
            self._cached_pixmap = self._pixmap.scaled(
                rect.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )

        # Center the pixmap
        x = (rect.width() - self._cached_pixmap.width()) // 2
        y = (rect.height() - self._cached_pixmap.height()) // 2

        # Apply effects based on interaction state
        if self._hover_progress > 0:
            painter.setOpacity(0.85 + 0.15 * self._hover_progress)
        if self._press_progress > 0:
            painter.setOpacity(0.7 + 0.3 * (1 - self._press_progress))

        painter.drawPixmap(x, y, self._cached_pixmap)
        painter.setOpacity(1.0)

    def _draw__initials(self, painter: QPainter, rect: QRect):
        """Draw initials with  typography and effects"""
        # Calculate responsive font size
        base_font_size = max(8, int(rect.height() * 0.35))
        
        # Adjust font size for different avatar sizes
        if self._size.value <= 24:
            font_size = max(8, int(base_font_size * 0.9))
        elif self._size.value >= 72:
            font_size = int(base_font_size * 1.1)
        else:
            font_size = base_font_size

        #  font with better readability
        font = QFont("Segoe UI", font_size)
        font.setWeight(QFont.Weight.Bold)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
        painter.setFont(font)

        #  text color with better contrast
        text_color = self._get_optimal_text_color(rect)
        
        # Apply interaction effects
        if self._hover_progress > 0:
            text_color = self._apply_hover_to_color(text_color, self._hover_progress)
        if self._press_progress > 0:
            text_color = self._apply_press_to_color(text_color, self._press_progress)

        painter.setPen(QPen(text_color))

        #  text rendering with metrics-based positioning
        font_metrics = QFontMetrics(font)
        text_rect = font_metrics.boundingRect(self._initials)
        
        # Center text precisely
        x = rect.center().x() - text_rect.width() // 2
        y = rect.center().y() + font_metrics.ascent() // 2
        
        painter.drawText(x, y, self._initials)

    def _get_optimal_text_color(self, rect: QRect) -> QColor:
        """Get optimal text color based on background"""
        # Calculate background luminance for better contrast
        bg_color = self._get_background_color_at_center(rect)
        luminance = 0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue()
        
        # Return high contrast color
        if luminance > 127:
            return QColor(40, 40, 40)  # Dark text on light background
        else:
            return QColor(255, 255, 255)  # Light text on dark background

    def _get_background_color_at_center(self, rect: QRect) -> QColor:
        """Get background color at center for contrast calculation"""
        if self._name or self._initials:
            return self._get_cached_color(self._name or self._initials)
        return self._bg_color

    def _apply_hover_to_color(self, color: QColor, progress: float) -> QColor:
        """Apply hover effect to color"""
        new_color = QColor(color)
        alpha = int(255 * (0.8 + 0.2 * progress))
        new_color.setAlpha(alpha)
        return new_color

    def _apply_press_to_color(self, color: QColor, progress: float) -> QColor:
        """Apply press effect to color"""
        new_color = QColor(color)
        alpha = int(255 * (0.6 + 0.4 * (1 - progress)))
        new_color.setAlpha(alpha)
        return new_color

    def _draw__icon(self, painter: QPainter, rect: QRect):
        """Draw icon with  styling and animations"""
        # Responsive icon sizing
        if self._size.value <= 24:
            icon_size = int(rect.height() * 0.55)
        elif self._size.value >= 72:
            icon_size = int(rect.height() * 0.65)
        else:
            icon_size = int(rect.height() * 0.6)
            
        icon_rect = QRect(
            rect.center().x() - icon_size // 2,
            rect.center().y() - icon_size // 2,
            icon_size,
            icon_size
        )

        #  pen with optimal color
        pen_color = self._get_optimal_text_color(rect)
        
        # Apply interaction effects
        if self._hover_progress > 0:
            pen_color = self._apply_hover_to_color(pen_color, self._hover_progress)
        if self._press_progress > 0:
            pen_color = self._apply_press_to_color(pen_color, self._press_progress)

        pen_width = max(1, int(icon_size / 12))
        painter.setPen(QPen(pen_color, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))

        # Draw  person silhouette
        self._draw_person_icon(painter, icon_rect)

    def _draw_person_icon(self, painter: QPainter, icon_rect: QRect):
        """Draw  person icon"""
        # Head (circle)
        head_size = int(icon_rect.height() * 0.35)
        head_rect = QRect(
            icon_rect.center().x() - head_size // 2,
            icon_rect.top() + int(icon_rect.height() * 0.1),
            head_size,
            head_size
        )
        painter.drawEllipse(head_rect)

        # Body (rounded rectangle)
        body_width = int(icon_rect.width() * 0.7)
        body_height = int(icon_rect.height() * 0.45)
        body_rect = QRect(
            icon_rect.center().x() - body_width // 2,
            head_rect.bottom() + int(icon_rect.height() * 0.05),
            body_width,
            body_height
        )
        
        # Draw body as rounded rectangle for better appearance
        body_radius = min(body_width, body_height) // 4
        painter.drawRoundedRect(body_rect, body_radius, body_radius)

    def _draw__placeholder(self, painter: QPainter, rect: QRect):
        """Draw placeholder with  styling"""
        self._draw__icon(painter, rect)

    def _draw__border(self, painter: QPainter, rect: QRect, path: QPainterPath):
        """Draw border with  styling and effects"""
        painter.setClipping(False)

        # Get border color with theme support
        border_color = self._border_col
        
        # Apply interaction effects
        if self._hover_progress > 0:
            border_color = border_color.lighter(int(110 + 15 * self._hover_progress))
        if self._press_progress > 0:
            border_color = border_color.darker(int(110 + 10 * self._press_progress))

        #  pen with adaptive width
        adaptive_width = max(1, int(self._border_width * (rect.width() / 32.0)))
        pen = QPen(border_color, adaptive_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawPath(path)

    def _draw_glow_effect(self, painter: QPainter, rect: QRect, path: QPainterPath):
        """Draw glow effect for special states"""
        if self._glow_progress <= 0:
            return
            
        painter.setClipping(False)
        
        # Create glow effect
        glow_color = QColor(self._cached_colors['accent'])
        glow_color.setAlpha(int(100 * self._glow_progress))
        
        # Draw multiple glow layers
        for i in range(3):
            glow_width = (i + 1) * 2
            glow_pen = QPen(glow_color, glow_width)
            painter.setPen(glow_pen)
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawPath(path)

    def _draw_presence_indicator(self, painter: QPainter, rect: QRect):
        """Draw presence status indicator"""
        if self._presence == AvatarPresence.NONE or self._presence_progress <= 0:
            return
            
        painter.setClipping(False)
        
        # Calculate indicator position and size
        indicator_size = max(6, int(rect.width() * 0.25))
        margin = max(2, int(indicator_size * 0.1))
        
        indicator_rect = QRect(
            rect.right() - indicator_size - margin,
            rect.bottom() - indicator_size - margin,
            indicator_size,
            indicator_size
        )
        
        # Get presence color
        presence_color = self._get_presence_color()
        presence_color.setAlpha(int(255 * self._presence_progress))
        
        # Draw indicator with border
        painter.setBrush(QBrush(presence_color))
        painter.setPen(QPen(self._cached_colors['surface'], 2))
        painter.drawEllipse(indicator_rect)

    def _get_presence_color(self) -> QColor:
        """Get color for presence status"""
        presence_colors = {
            AvatarPresence.AVAILABLE: QColor(107, 165, 57),
            AvatarPresence.BUSY: QColor(196, 43, 28),
            AvatarPresence.AWAY: QColor(255, 185, 0),
            AvatarPresence.DO_NOT_DISTURB: QColor(180, 0, 0),
            AvatarPresence.OFFLINE: QColor(138, 141, 145),
        }
        return presence_colors.get(self._presence, QColor(138, 141, 145))

    def _draw_activity_indicator(self, painter: QPainter, rect: QRect):
        """Draw activity indicator (typing, recording, etc.)"""
        if self._activity == AvatarActivity.NONE:
            return
            
        painter.setClipping(False)
        
        # Activity indicator position (top-right)
        indicator_size = max(4, int(rect.width() * 0.15))
        margin = max(1, int(indicator_size * 0.1))
        
        indicator_rect = QRect(
            rect.right() - indicator_size - margin,
            rect.top() + margin,
            indicator_size,
            indicator_size
        )
        
        # Get activity color and draw animated indicator
        activity_color = self._get_activity_color()
        
        # Add pulsing animation for activity
        pulse_alpha = int(255 * (0.6 + 0.4 * abs(self._loading_progress - 0.5) * 2))
        activity_color.setAlpha(pulse_alpha)
        
        painter.setBrush(QBrush(activity_color))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawEllipse(indicator_rect)

    def _get_activity_color(self) -> QColor:
        """Get color for activity status"""
        activity_colors = {
            AvatarActivity.TYPING: QColor(0, 120, 215),
            AvatarActivity.RECORDING: QColor(196, 43, 28),
            AvatarActivity.STREAMING: QColor(107, 165, 57),
        }
        return activity_colors.get(self._activity, QColor(0, 120, 215))
        
    def _draw_interaction_effects(self, painter: QPainter, rect: QRect, path: QPainterPath):
        """Draw  hover and press effects with modern styling"""
        if self._hover_progress <= 0 and self._press_progress <= 0:
            return
            
        painter.setClipping(False)

        #  overlay effects with better blending
        if self._press_progress > 0:
            # Press effect: subtle dark overlay with pulse
            overlay_color = QColor(0, 0, 0, int(25 * self._press_progress))
            painter.fillPath(path, overlay_color)
            
            # Add inner glow effect for press
            glow_color = QColor(self._cached_colors['accent'])
            glow_color.setAlpha(int(40 * self._press_progress))
            glow_pen = QPen(glow_color, 2)
            painter.setPen(glow_pen)
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawPath(path)
            
        elif self._hover_progress > 0:
            # Hover effect: lighter overlay with subtle animation
            overlay_color = QColor(255, 255, 255, int(20 * self._hover_progress))
            painter.fillPath(path, overlay_color)

    def _generate_color_from_string(self, text: str) -> QColor:
        """Generate a consistent color from string with  algorithm"""
        # Create hash from text
        hash_object = hashlib.md5(text.encode())
        hex_dig = hash_object.hexdigest()

        # Extract RGB values with better distribution
        r = int(hex_dig[0:2], 16)
        g = int(hex_dig[2:4], 16)
        b = int(hex_dig[4:6], 16)

        #  color adjustment for better contrast and aesthetics
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

    #  property getters and setters with validation
    def _get_hover_progress(self) -> float:
        return self._hover_progress

    def _set_hover_progress(self, value: float):
        value = max(0.0, min(1.0, value))  # Clamp between 0 and 1
        if self._hover_progress != value:
            self._hover_progress = value
            self.update()

    def _get_press_progress(self) -> float:
        return self._press_progress

    def _set_press_progress(self, value: float):
        value = max(0.0, min(1.0, value))
        if self._press_progress != value:
            self._press_progress = value
            self.update()

    def _get_scale_progress(self) -> float:
        return self._scale_progress

    def _set_scale_progress(self, value: float):
        value = max(0.1, min(2.0, value))  # Reasonable scale limits
        if self._scale_progress != value:
            self._scale_progress = value
            self.update()

    def _get_glow_progress(self) -> float:
        return self._glow_progress

    def _set_glow_progress(self, value: float):
        value = max(0.0, min(1.0, value))
        if self._glow_progress != value:
            self._glow_progress = value
            self.update()

    def _get_presence_progress(self) -> float:
        return self._presence_progress

    def _set_presence_progress(self, value: float):
        value = max(0.0, min(1.0, value))
        if self._presence_progress != value:
            self._presence_progress = value
            self.update()

    def _get_loading_progress(self) -> float:
        return self._loading_progress

    def _set_loading_progress(self, value: float):        # Allow values from 0 to 1 with wrapping for continuous animation
        while value > 1.0:
            value -= 1.0
        while value < 0.0:
            value += 1.0
        if self._loading_progress != value:
            self._loading_progress = value
            self.update()

    # Animation properties
    hover_progress = Property(float, _get_hover_progress, _set_hover_progress, "hover", "")
    press_progress = Property(float, _get_press_progress, _set_press_progress, "press", "")
    scale_progress = Property(float, _get_scale_progress, _set_scale_progress, "scale", "")
    glow_progress = Property(float, _get_glow_progress, _set_glow_progress, "glow", "")
    presence_progress = Property(float, _get_presence_progress, _set_presence_progress, "presence", "")
    loading_progress = Property(float, _get_loading_progress, _set_loading_progress, "loading", "")

    #  public API methods with validation and animation
    def setSize(self, size: Size):
        """Set avatar size with smooth animation and responsive adjustments"""
        if not isinstance(size, self.Size):
            raise ValueError("Size must be an instance of FluentAvatar.Size")
            
        if self._size != size:
            self._size = size

            # Calculate responsive size
            base_size = size.value
            parent_widget = self.parentWidget()
            if parent_widget:
                parent_size = parent_widget.size()
                if parent_size.width() < 400:
                    base_size = int(base_size * 0.8)
                elif parent_size.width() > 1200:
                    base_size = int(base_size * 1.1)

            # Animate size change with smooth transition
            old_widget_size = self.size()
            new_widget_size = QSize(base_size, base_size)

            if hasattr(self, '_size_animation'):
                self._size_animation.stop()
            
            self._size_animation = QPropertyAnimation(self, QByteArray(b"size"))
            self._size_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
            self._size_animation.setEasingCurve(FluentTransition.EASE_SPRING)
            self._size_animation.setStartValue(old_widget_size)
            self._size_animation.setEndValue(new_widget_size)
            self._size_animation.finished.connect(
                lambda: self._complete_size_change(new_widget_size))
            self._size_animation.start()
            
            # Update cached resources
            self._cached_pixmap = None
            self._invalidate_paint_cache()
            
            # Emit signal
            self.size_changed.emit(size)    
            
    def _complete_size_change(self, new_size: QSize):
        """Complete size change operation"""
        self.setFixedSize(new_size)
        self._setup_responsive_styles()
        if self._shadow_enabled:
            self._setup_shadow_effect()

    def avatarSize(self) -> Size:
        """Get current avatar size"""
        return self._size

    def setShape(self, shape: Shape):
        """Set avatar shape with smooth transition"""
        if not isinstance(shape, self.Shape):
            raise ValueError("Shape must be an instance of FluentAvatar.Shape")
            
        if self._shape != shape:
            self._shape = shape
            # Add transition effect with shape morphing
            if not self._is_disposing:
                FluentMicroInteraction.pulse_animation(self, 1.08)
            self._invalidate_paint_cache()

    def shape(self) -> Shape:
        """Get current avatar shape"""
        return self._shape

    def setPixmap(self, pixmap: Optional[QPixmap]):
        """Set avatar photo with  loading and transition"""
        if pixmap and not pixmap.isNull():
            self._pixmap = pixmap
            self._cached_pixmap = None  # Clear cache
            self._style = self.Style.PHOTO
            
            # Add loading animation
            self._start_loading_animation()
            
            # Simulate loading delay for smooth transition
            QTimer.singleShot(150, lambda: self._complete_photo_loading(True))
        else:
            self._pixmap = None
            self._cached_pixmap = None
            self._style = self.Style.PLACEHOLDER
            self._complete_photo_loading(False)

    def _start_loading_animation(self):
        """Start loading animation"""
        if hasattr(self, '_loading_animation'):
            self._loading_animation.setStartValue(0.0)
            self._loading_animation.setEndValue(1.0)
            self._loading_animation.start()

    def _complete_photo_loading(self, success: bool):
        """Complete photo loading process"""
        if hasattr(self, '_loading_animation'):
            self._loading_animation.stop()
        
        # Add reveal transition
        FluentRevealEffect.fade_in(self, 300)
        
        # Emit signal
        self.photo_loaded.emit(success)

    def pixmap(self) -> Optional[QPixmap]:
        """Get current avatar photo"""
        return self._pixmap

    def setInitials(self, initials: str):
        """Set avatar initials with validation and transition"""
        if not isinstance(initials, str):
            initials = str(initials)
            
        new_initials = initials.strip().upper()[:2]
        if self._initials != new_initials:
            self._initials = new_initials
            self._style = self.Style.INITIALS if new_initials else self.Style.PLACEHOLDER
              # Clear cached colors for regeneration
            if hasattr(self, '_get_cached_color'):
                self._get_cached_color.cache_clear()
            
            # Add transition effect
            if not self._is_disposing:
                FluentMicroInteraction.pulse_animation(self, 1.05)
            self._invalidate_paint_cache()

    def initials(self) -> str:
        """Get current avatar initials"""
        return self._initials

    def setName(self, name: str):
        """Set name and auto-generate initials with  logic"""
        if not isinstance(name, str):
            name = str(name)
            
        name = name.strip()
        if self._name != name:
            self._name = name

            #  initials generation
            if name:
                self._generate_initials_from_name(name)
                self._style = self.Style.INITIALS
            else:
                self._initials = ""
                self._style = self.Style.PLACEHOLDER

            # Clear cached colors
            if hasattr(self, '_get_cached_color'):
                self._get_cached_color.cache_clear()
              # Update accessibility
            self.setAccessibleName(f"Avatar for {name}" if name else "Avatar")
            
            # Add transition effect
            if not self._is_disposing:
                FluentMicroInteraction.pulse_animation(self, 1.05)
            self._invalidate_paint_cache()

    def _generate_initials_from_name(self, name: str):
        """Generate initials from name with  logic"""
        # Remove common prefixes and suffixes
        prefixes = ['mr.', 'mrs.', 'ms.', 'dr.', 'prof.']
        suffixes = ['jr.', 'sr.', 'ii', 'iii', 'iv']
        
        name_lower = name.lower()
        for prefix in prefixes:
            if name_lower.startswith(prefix):
                name = name[len(prefix):].strip()
                break
        
        for suffix in suffixes:
            if name_lower.endswith(suffix):
                name = name[:-len(suffix)].strip()
                break
        
        # Split and generate initials
        parts = [part.strip() for part in name.split() if part.strip()]
        if len(parts) >= 2:
            # First and last name
            self._initials = (parts[0][0] + parts[-1][0]).upper()
        elif len(parts) == 1:
            # Single name - take first two characters
            self._initials = parts[0][:2].upper()
        else:
            self._initials = ""

    def name(self) -> str:
        """Get current name"""
        return self._name

    def setPresence(self, presence: AvatarPresence):
        """Set presence status with animation"""
        if not isinstance(presence, AvatarPresence):
            raise ValueError("Presence must be an instance of AvatarPresence")
            
        if self._presence != presence:
            self._presence = presence
            
            # Animate presence indicator
            if presence != AvatarPresence.NONE:
                self._presence_animation.setStartValue(0.0)
                self._presence_animation.setEndValue(1.0)
                self._presence_animation.start()
            else:
                self._presence_animation.setStartValue(self._presence_progress)
                self._presence_animation.setEndValue(0.0)
                self._presence_animation.start()
            
            # Update accessibility
            if presence != AvatarPresence.NONE:
                self.setAccessibleDescription(f"Avatar with {presence.value} status")
            
            self.presence_changed.emit(presence)

    def presence(self) -> AvatarPresence:
        """Get current presence status"""
        return self._presence

    def setActivity(self, activity: AvatarActivity):
        """Set activity status with animation"""
        if not isinstance(activity, AvatarActivity):
            raise ValueError("Activity must be an instance of AvatarActivity")
            
        if self._activity != activity:
            self._activity = activity
            
            # Start or stop activity animation
            if activity != AvatarActivity.NONE:
                if hasattr(self, '_loading_animation'):
                    self._loading_animation.setStartValue(0.0)
                    self._loading_animation.setEndValue(1.0)
                    self._loading_animation.start()
            else:
                if hasattr(self, '_loading_animation'):
                    self._loading_animation.stop()
            
            self.activity_changed.emit(activity)

    def activity(self) -> AvatarActivity:
        """Get current activity status"""
        return self._activity

    def setClickable(self, clickable: bool):
        """Set whether avatar is clickable with  interaction"""
        if self._clickable != clickable:
            self._clickable = clickable
            self.setCursor(
                Qt.CursorShape.PointingHandCursor if clickable 
                else Qt.CursorShape.ArrowCursor
            )
            
            # Update accessibility
            if clickable:
                self.setAccessibleDescription(
                    self.accessibleDescription() + " (clickable)")
            
            # Enable/disable hover effects
            self._hover_enabled = clickable

    def isClickable(self) -> bool:
        """Check if avatar is clickable"""
        return self._clickable

    def setDoubleClickable(self, double_clickable: bool):
        """Set whether avatar accepts double clicks"""
        self._double_clickable = double_clickable

    def isDoubleClickable(self) -> bool:
        """Check if avatar accepts double clicks"""
        return self._double_clickable

    def setGlowEnabled(self, enabled: bool):
        """Enable or disable glow effect"""
        if self._glow_enabled != enabled:
            self._glow_enabled = enabled
            if enabled:
                # Start glow animation
                if hasattr(self, '_glow_animation'):
                    self._glow_animation.setStartValue(0.0)
                    self._glow_animation.setEndValue(1.0)
                    self._glow_animation.start()
            else:
                # Stop glow animation
                if hasattr(self, '_glow_animation'):
                    self._glow_animation.stop()
                    self._glow_progress = 0.0
                    self.update()

    def isGlowEnabled(self) -> bool:
        """Check if glow effect is enabled"""
        return self._glow_enabled

    def setShadowEnabled(self, enabled: bool):
        """Enable or disable shadow effect"""
        if self._shadow_enabled != enabled:
            self._shadow_enabled = enabled
            if enabled:
                self._setup_shadow_effect()
            else:
                # Clear the graphics effect
                current_effect = self.graphicsEffect()
                if current_effect:
                    effect = self.graphicsEffect()
                    old_effect = self.graphicsEffect()
                    if old_effect:
                        # Use empty graphics effect instead of None
                        # Create new transparent effect
                        new_effect = QGraphicsOpacityEffect(self)
                        new_effect.setOpacity(0.0)
                        
                        # Replace old effect safely
                        current_effect = self.graphicsEffect()
                        if current_effect:
                            current_effect.setEnabled(False)
                        self.setGraphicsEffect(new_effect)
                        if current_effect:
                            current_effect.deleteLater()
                        pass  # Graphics effect already set above
                        # No need for additional cleanup - already handled above    def isShadowEnabled(self) -> bool:
        """Check if shadow effect is enabled"""
        return self._shadow_enabled
    
    def setBorderWidth(self, width: int):
        """Set border width with transition"""
        new_width = max(0, width)
        if self._border_width != new_width:
            self._border_width = new_width
            if not self._is_disposing:
                FluentMicroInteraction.pulse_animation(self, 1.02)
            self.update()

    def borderWidth(self) -> int:
        """Get border width"""
        return self._border_width

    def setBorderColor(self, color: Optional[QColor]):
        """Set border color with transition"""
        if self._border_color != color:
            self._border_color = color
            self._update_theme_colors()
            if not self._is_disposing:
                FluentMicroInteraction.pulse_animation(self, 1.02)    
                
    def borderColor(self) -> QColor:
        """Get border color"""
        return self._border_color if self._border_color else self._border_col

    def setBackgroundColor(self, color: Optional[QColor]):
        """Set background color with transition"""
        if self._background_color != color:
            self._background_color = color
            self._update_theme_colors()
            if not self._is_disposing:
                FluentMicroInteraction.pulse_animation(self, 1.02)

    def backgroundColor(self) -> QColor:
        """Get background color"""
        return self._background_color if self._background_color else self._bg_color

    def setCustomGradient(self, gradient: Optional[QLinearGradient]):
        """Set custom gradient for background"""
        self._custom_gradient = gradient
        if gradient:
            self._style = self.Style.GRADIENT
        self._invalidate_paint_cache()

    def customGradient(self) -> Optional[QLinearGradient]:
        """Get custom gradient"""
        return self._custom_gradient

    #  event handlers with improved responsiveness
    def enterEvent(self, event: QEnterEvent):
        """Handle mouse enter with  animation and accessibility"""
        if self._clickable and self._hover_enabled and not self._is_disposing:
            #  hover animation with spring easing
            self._hover_animation.stop()
            self._hover_animation.setStartValue(self._hover_progress)
            self._hover_animation.setEndValue(1.0)
            self._hover_animation.start()

            # Subtle scale effect for better feedback
            self._scale_animation.stop()
            self._scale_animation.setStartValue(self._scale_progress)
            self._scale_animation.setEndValue(1.08)
            self._scale_animation.start()
            
            # Emit hover signal
            self.hovered.emit(True)

        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        """Handle mouse leave with smooth return animation"""
        if self._clickable and self._hover_enabled and not self._is_disposing:
            # Return to normal state with smooth animation
            self._hover_animation.stop()
            self._hover_animation.setStartValue(self._hover_progress)
            self._hover_animation.setEndValue(0.0)
            self._hover_animation.start()

            # Return to normal scale
            self._scale_animation.stop()
            self._scale_animation.setStartValue(self._scale_progress)
            self._scale_animation.setEndValue(1.0)
            self._scale_animation.start()
            
            # Emit hover signal
            self.hovered.emit(False)

        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press with  feedback"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton and not self._is_disposing:
            #  press animation with immediate feedback
            self._press_animation.stop()
            self._press_animation.setStartValue(self._press_progress)
            self._press_animation.setEndValue(1.0)
            self._press_animation.start()

            # Scale down effect for tactile feedback
            if not self._is_disposing:
                FluentMicroInteraction.button_press(self, 0.92)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release with  interaction feedback"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton and not self._is_disposing:
            # Release animation            self._press_animation.stop()
            self._press_animation.setStartValue(self._press_progress)
            self._press_animation.setEndValue(0.0)
            self._press_animation.start()

            if self.rect().contains(event.position().toPoint()):
                # Add ripple effect before emitting signal
                if not self._is_disposing:
                    FluentMicroInteraction.ripple_effect(self)
                QTimer.singleShot(80, self.clicked.emit)

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle double click events"""
        if (self._double_clickable and event.button() == Qt.MouseButton.LeftButton 
            and not self._is_disposing):
            #  double-click animation
            if not self._is_disposing:
                FluentMicroInteraction.pulse_animation(self, 1.15)
            self.double_clicked.emit()
        
        super().mouseDoubleClickEvent(event)

    def focusInEvent(self, event: QFocusEvent):
        """ focus in event with visual feedback"""
        if self._focus_enabled and not self._is_disposing:
            # Add focus glow effect
            if hasattr(self, '_glow_animation'):
                self._glow_animation.stop()
                self._glow_animation.setStartValue(0.0)
                self._glow_animation.setEndValue(0.7)
                self._glow_animation.setLoopCount(1)
                self._glow_animation.start()
            
            # Subtle scale animation for focus
            FluentMicroInteraction.pulse_animation(self, 1.03)
        
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        """ focus out event"""
        if self._focus_enabled and not self._is_disposing:
            # Remove focus glow
            if hasattr(self, '_glow_animation'):
                self._glow_animation.stop()
                self._glow_progress = 0.0
                self.update()
        
        super().focusOutEvent(event)

    def resizeEvent(self, event: QResizeEvent):
        """Handle resize events for responsive behavior"""
        super().resizeEvent(event)
        if event.size() != event.oldSize():
            self._invalidate_paint_cache()
            
            # Update shadow effect for new size
            if self._shadow_enabled:
                QTimer.singleShot(50, self._setup_shadow_effect)

    def _on_theme_changed(self, _=None):
        """Handle theme change with smooth transition"""
        if not self._is_disposing:
            self._update_theme_colors()
            # Add subtle transition animation
            FluentMicroInteraction.pulse_animation(self, 1.03)

    def closeEvent(self, event: QCloseEvent):
        """Handle close event with proper cleanup"""
        self._dispose_resources()
        super().closeEvent(event)

    def _dispose_resources(self):
        """Dispose of resources and cleanup animations"""
        self._is_disposing = True
        
        # Stop all animations
        if hasattr(self, '_animation_group') and self._animation_group:
            self._animation_group.stop()
        
        if hasattr(self, '_glow_animation'):
            self._glow_animation.stop()
        
        if hasattr(self, '_loading_animation'):
            self._loading_animation.stop()
        
        if hasattr(self, '_presence_animation'):
            self._presence_animation.stop()
        
        # Clean up timers
        for timer in self._timers:
            if timer and timer.isActive():
                timer.stop()
        self._timers.clear()
        
        # Clear cached resources
        self._cached_pixmap = None
        self._cached_colors.clear()
        
        # Disconnect from theme manager
        try:
            theme_manager.theme_changed.disconnect(self._on_theme_changed)
        except:
            pass


class FluentAvatarGroup(QWidget):
    """ group of avatars with advanced animations and responsive design"""

    # Signals
    avatar_clicked = Signal(int)  # Index of clicked avatar
    overflow_clicked = Signal()
    group_hovered = Signal(bool)

    def __init__(self, max_visible: int = 5, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Core properties
        self._avatars: List[FluentAvatar] = []
        self._max_visible = max_visible
        self._spacing = 4
        self._overlap = 8
        self._size = FluentAvatar.Size.MEDIUM
        self._direction = Qt.LayoutDirection.LeftToRight
        
        #  properties
        self._hover_enabled = True
        self._stack_depth = 3  # Visual depth for overlapping
        self._animation_stagger = 100  # ms between avatar animations
        self._compact_mode = False
        
        # Animation state
        self._group_hover_progress = 0.0
        self._expansion_progress = 0.0
        
        # Performance optimization
        self._layout_cache_valid = False
        self._last_container_size = QSize()
        
        # Lifecycle management
        self._is_disposing = False
        self._timers: List[QTimer] = []

        self._setup_ui()
        self._setup__theming()
        self._setup_group_animations()

        # Connect to theme manager
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup  UI components with responsive layout"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)  # Handle spacing manually for better control

        # Setup responsive behavior
        self.installEventFilter(self)
        
        self._update_layout()

    def _setup__theming(self):
        """Setup  theming system"""
        pass  # Simplified theming setup

    def _setup_group_animations(self):
        """Setup group-level animation system"""
        # Group hover animation
        self._group_hover_animation = QPropertyAnimation(self, QByteArray(b"group_hover_progress"))
        self._group_hover_animation.setDuration(200)
        self._group_hover_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
        
        # Group expansion animation
        self._expansion_animation = QPropertyAnimation(self, QByteArray(b"expansion_progress"))
        self._expansion_animation.setDuration(300)
        self._expansion_animation.setEasingCurve(FluentTransition.EASE_SPRING)

        # Schedule entrance animation
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self._show_group_entrance)
        timer.start(150)
        self._timers.append(timer)

    def _show_group_entrance(self):
        """Show group entrance with staggered reveal animation"""
        if self._avatars and not self._is_disposing:
            # Create staggered entrance animation
            for i, avatar in enumerate(self._avatars):
                delay = i * self._animation_stagger
                timer = QTimer(self)
                timer.setSingleShot(True)
                timer.timeout.connect(lambda a=avatar: FluentRevealEffect.scale_in(a, 250))
                timer.start(delay)
                self._timers.append(timer)

    def addAvatar(self, avatar: FluentAvatar) -> int:
        """Add avatar to group with  animation and return index"""
        if not isinstance(avatar, FluentAvatar):
            raise ValueError("Avatar must be an instance of FluentAvatar")
            
        avatar.setSize(self._size)
        avatar.setParent(self)
        
        # Connect avatar signals
        avatar.clicked.connect(lambda: self._on_avatar_clicked(len(self._avatars)))
        
        self._avatars.append(avatar)
        
        # Add entrance animation for new avatar
        FluentRevealEffect.scale_in(avatar, 300)
        
        # Update layout with slight delay for smooth animation
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self._update_layout_animated)
        timer.start(350)
        self._timers.append(timer)
        
        return len(self._avatars) - 1

    def removeAvatar(self, index: int):
        """Remove avatar at index with smooth animation"""
        if 0 <= index < len(self._avatars):
            avatar = self._avatars[index]
            
            # Animate removal
            sequence = FluentSequence(self)
            def scale_down():
                """Scale down animation callback"""
                avatar._scale_progress = 0.0
                avatar.update()
            sequence.addCallback(scale_down)
            sequence.addPause(250)
            sequence.addCallback(lambda: self._complete_avatar_removal(avatar))
            sequence.start()

    def _complete_avatar_removal(self, avatar: FluentAvatar):
        """Complete avatar removal process"""
        if avatar in self._avatars:
            # Disconnect signals
            try:
                avatar.clicked.disconnect()
            except:
                pass
            
            self._avatars.remove(avatar)
            avatar.setParent(None)
            avatar.deleteLater()
            
            self._update_layout_animated()

    def removeAvatarByInstance(self, avatar: FluentAvatar):
        """Remove specific avatar instance"""
        try:
            index = self._avatars.index(avatar)
            self.removeAvatar(index)
        except ValueError:
            pass

    def clear(self):
        """Clear all avatars with coordinated animation"""
        if self._avatars:
            # Animate all avatars out with staggered timing
            for i, avatar in enumerate(self._avatars):
                delay = i * 80
                timer = QTimer(self)
                timer.setSingleShot(True)
                timer.timeout.connect(
                    lambda a=avatar: setattr(a, '_scale_progress', 0.0) or a.update())
                timer.start(delay)
                self._timers.append(timer)

            # Complete clearing after animations
            total_delay = len(self._avatars) * 80 + 300
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(self._complete_clear)
            timer.start(total_delay)
            self._timers.append(timer)

    def _complete_clear(self):
        """Complete clearing all avatars"""
        for avatar in self._avatars:
            try:
                avatar.clicked.disconnect()
            except:
                pass
            avatar.setParent(None)
            avatar.deleteLater()
        self._avatars.clear()
        self._update_layout()

    def _on_avatar_clicked(self, index: int):
        """Handle avatar click events"""
        self.avatar_clicked.emit(index)

    #  property management
    def setMaxVisible(self, max_visible: int):
        """Set maximum visible avatars with smooth transition"""
        new_max = max(1, max_visible)
        if self._max_visible != new_max:
            self._max_visible = new_max
            self._update_layout_animated()

    def maxVisible(self) -> int:
        """Get maximum visible avatars"""
        return self._max_visible

    def setSize(self, size: FluentAvatar.Size):
        """Set avatar size for all avatars with coordinated animation"""
        if self._size != size:
            self._size = size

            # Animate size change for all visible avatars
            for i, avatar in enumerate(self._avatars):
                delay = i * 50  # Staggered size change
                timer = QTimer(self)
                timer.setSingleShot(True)
                timer.timeout.connect(lambda a=avatar, s=size: a.setSize(s))
                timer.start(delay)
                self._timers.append(timer)

            # Update layout after size changes
            total_delay = len(self._avatars) * 50 + 200
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(self._update_layout)
            timer.start(total_delay)
            self._timers.append(timer)

    def avatarSize(self) -> FluentAvatar.Size:
        """Get current avatar size"""
        return self._size

    def setOverlap(self, overlap: int):
        """Set avatar overlap with smooth transition"""
        new_overlap = max(0, min(overlap, self._size.value // 2))
        if self._overlap != new_overlap:
            self._overlap = new_overlap
            self._update_layout_animated()

    def overlap(self) -> int:
        """Get current avatar overlap"""
        return self._overlap

    def setDirection(self, direction: Qt.LayoutDirection):
        """Set layout direction (left-to-right or right-to-left)"""
        if self._direction != direction:
            self._direction = direction
            self._update_layout_animated()

    def direction(self) -> Qt.LayoutDirection:
        """Get current layout direction"""
        return self._direction

    def setCompactMode(self, compact: bool):
        """Enable or disable compact mode for smaller screens"""
        if self._compact_mode != compact:
            self._compact_mode = compact
            if compact:
                self._overlap = max(self._overlap, self._size.value // 3)
                self._max_visible = min(self._max_visible, 3)
            self._update_layout_animated()

    def isCompactMode(self) -> bool:
        """Check if compact mode is enabled"""
        return self._compact_mode

    def avatarAt(self, index: int) -> Optional[FluentAvatar]:
        """Get avatar at specific index"""
        if 0 <= index < len(self._avatars):
            return self._avatars[index]
        return None

    def avatarCount(self) -> int:
        """Get total number of avatars"""
        return len(self._avatars)

    def visibleAvatarCount(self) -> int:
        """Get number of currently visible avatars"""
        return min(len(self._avatars), self._max_visible)

    def _update_layout(self):
        """Update layout of avatars with  positioning"""
        if self._is_disposing:
            return
            
        # Clear existing layout
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item and item.widget():
                item.widget().setParent(None)

        visible_count = min(len(self._avatars), self._max_visible)
        overflow_count = max(0, len(self._avatars) - self._max_visible)

        if visible_count == 0:
            return

        # Calculate responsive spacing
        effective_overlap = self._overlap
        if self._compact_mode:
            effective_overlap = int(self._overlap * 1.2)

        # Add visible avatars with  z-order and positioning
        avatars_to_show = self._avatars[:visible_count]
        if self._direction == Qt.LayoutDirection.RightToLeft:
            avatars_to_show = list(reversed(avatars_to_show))

        for i, avatar in enumerate(avatars_to_show):
            avatar.setParent(self)
            avatar.show()
            
            # Set z-order for proper overlapping
            z_order = self._stack_depth - i if i < self._stack_depth else 0
            avatar.raise_() if z_order > 0 else avatar.lower()
            
            self._layout.addWidget(avatar)

            # Add negative spacing for overlap (except for the first item)
            if i > 0:
                self._layout.addSpacing(-effective_overlap)

        # Add overflow indicator if needed
        if overflow_count > 0:
            overflow_avatar = self._create_overflow_indicator(overflow_count)
            if overflow_avatar:
                if visible_count > 0:
                    self._layout.addSpacing(-effective_overlap)
                self._layout.addWidget(overflow_avatar)

        self._layout.addStretch()
        self._layout_cache_valid = True

    def _create_overflow_indicator(self, count: int) -> Optional[FluentAvatar]:
        """Create overflow indicator avatar"""
        try:
            overflow_avatar = FluentAvatar(self._size, FluentAvatar.Shape.CIRCLE, self)
            overflow_avatar.setInitials(f"+{count}")
            overflow_avatar.setBackgroundColor(theme_manager.get_color('text_secondary'))
            overflow_avatar.setClickable(True)
            overflow_avatar.clicked.connect(self.overflow_clicked.emit)
            
            # Add entrance animation
            FluentRevealEffect.scale_in(overflow_avatar, 200)
            
            return overflow_avatar
        except Exception as e:
            print(f"Error creating overflow indicator: {e}")
            return None

    def _update_layout_animated(self):
        """Update layout with smooth transition animation"""
        if not self._is_disposing:
            # Add subtle transition effect
            FluentMicroInteraction.pulse_animation(self, 1.02)
            
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(self._update_layout)
            timer.start(100)
            self._timers.append(timer)

    #  property getters and setters for animations
    def _get_group_hover_progress(self) -> float:
        return self._group_hover_progress

    def _set_group_hover_progress(self, value: float):
        value = max(0.0, min(1.0, value))
        if self._group_hover_progress != value:
            self._group_hover_progress = value
            self.update()

    def _get_expansion_progress(self) -> float:
        return self._expansion_progress

    def _set_expansion_progress(self, value: float):
        value = max(0.0, min(1.0, value))
        if self._expansion_progress != value:
            self._expansion_progress = value
            self._update_avatar_positions()

    def _update_avatar_positions(self):
        """Update avatar positions based on expansion progress"""
        if self._expansion_progress > 0:
            # Animate avatars to spread out
            base_spacing = self._spacing
            expanded_spacing = base_spacing * (1 + self._expansion_progress * 2)
            
            for i, avatar in enumerate(self._avatars[:self._max_visible]):
                if i > 0:
                    # Animate position change
                    current_pos = avatar.pos()
                    new_x = current_pos.x() + int(expanded_spacing * i)
                    target_pos = QPoint(new_x, current_pos.y())
                    
                    # Use smooth animation for position change
                    if hasattr(avatar, '_position_animation'):
                        # Create position animation with proper initialization
                        animation = QPropertyAnimation(avatar, QByteArray(b"pos"), avatar)
                        animation.setDuration(200)
                        animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
                        animation.setEndValue(target_pos)
                        
                        # Store animation and start
                        if hasattr(avatar, '_position_animation') and avatar._position_animation:
                            avatar._position_animation.stop()
                        setattr(avatar, '_position_animation', animation)
                        animation.start()

    # Qt properties for animations
    # Group properties
    # Group animation properties
    group_hover_progress = Property(float, _get_group_hover_progress, _set_group_hover_progress,
                                  "group_hover", "")
    expansion_progress = Property(float, _get_expansion_progress, _set_expansion_progress,
                                "expansion", "")

    #  event handlers
    def enterEvent(self, event: QEnterEvent):
        """Handle mouse enter with group animation"""
        if self._hover_enabled and not self._is_disposing:
            self._group_hover_animation.setStartValue(self._group_hover_progress)
            self._group_hover_animation.setEndValue(1.0)
            self._group_hover_animation.start()
            
            # Start expansion animation for better interaction
            self._expansion_animation.setStartValue(self._expansion_progress)
            self._expansion_animation.setEndValue(0.3)
            self._expansion_animation.start()
            
            self.group_hovered.emit(True)
        
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave with return animation"""
        if self._hover_enabled and not self._is_disposing:
            self._group_hover_animation.setStartValue(self._group_hover_progress)
            self._group_hover_animation.setEndValue(0.0)
            self._group_hover_animation.start()
            
            # Return to normal spacing
            self._expansion_animation.setStartValue(self._expansion_progress)
            self._expansion_animation.setEndValue(0.0)
            self._expansion_animation.start()
            
            self.group_hovered.emit(False)
        
        super().leaveEvent(event)

    def resizeEvent(self, event: QResizeEvent):
        """Handle resize events for responsive behavior"""
        super().resizeEvent(event)
        
        if event.size() != self._last_container_size:
            self._last_container_size = event.size()
            
            # Check if we need to switch to compact mode
            if event.size().width() < 300 and not self._compact_mode:
                self.setCompactMode(True)
            elif event.size().width() >= 400 and self._compact_mode:
                self.setCompactMode(False)
            
            # Invalidate layout cache
            self._layout_cache_valid = False
            
            # Update layout with responsive adjustments
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(self._update_layout)
            timer.start(100)
            self._timers.append(timer)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """ event filter for responsive behavior"""
        if obj == self and event.type() == QEvent.Type.LayoutRequest:
            if not self._layout_cache_valid:
                self._update_layout()
        
        return super().eventFilter(obj, event)

    def _on_theme_changed(self, _):
        """Handle theme change with group transition"""
        if not self._is_disposing:
            # Update all avatars with staggered animation
            for i, avatar in enumerate(self._avatars):
                delay = i * 30
                timer = QTimer(self)
                timer.setSingleShot(True)
                timer.timeout.connect(
                    lambda a=avatar: setattr(a, '_scale_progress', 1.02) or a.update())
                timer.start(delay)
                self._timers.append(timer)

    def closeEvent(self, event):
        """Handle close event with proper cleanup"""
        self._dispose_resources()
        super().closeEvent(event)

    def _dispose_resources(self):
        """Dispose of group resources and cleanup"""
        self._is_disposing = True
        
        # Stop all animations
        if hasattr(self, '_group_hover_animation'):
            self._group_hover_animation.stop()
        if hasattr(self, '_expansion_animation'):
            self._expansion_animation.stop()
        
        # Clean up timers
        for timer in self._timers:
            if timer and timer.isActive():
                timer.stop()
        self._timers.clear()
        
        # Dispose of all avatars
        for avatar in self._avatars:
            if hasattr(avatar, '_dispose_resources'):
                avatar._dispose_resources()
        
        # Disconnect from theme manager
        try:
            theme_manager.theme_changed.disconnect(self._on_theme_changed)
        except:
            pass
