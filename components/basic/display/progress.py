"""
Enhanced Fluent Design Progress Components
Provides modern, performant progress indicators with smooth animations,
theme integration, and responsive behavior following QFluentWidget patterns.
"""

from PySide6.QtWidgets import (
    QProgressBar, QSlider, QWidget, QGraphicsDropShadowEffect)
from PySide6.QtCore import (Qt, Signal, QPropertyAnimation, Property, QByteArray,
                            QEasingCurve, QTimer, QRect, QSequentialAnimationGroup,
                            QAbstractAnimation, QPoint, QPauseAnimation)
from PySide6.QtGui import (QPainter, QBrush, QPen, QLinearGradient, QPaintEvent, QRadialGradient,
                           QColor, QPainterPath, QFont, QFontMetrics)
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import FluentRevealEffect, FluentTransition
from typing import Optional
import weakref
import math


class FluentProgressBar(QProgressBar):
    """Enhanced Fluent Design progress bar with modern styling and smooth animations"""

    # Fluent Design signals
    animationPositionChanged = Signal(float)
    glowIntensityChanged = Signal(float)
    pulseScaleChanged = Signal(float)
    valueAnimationFinished = Signal()
    stateChanged = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Fluent Design state management
        self._state = 'normal'
        self._is_indeterminate = False
        self._animation_position = 0.0
        self._glow_intensity = 0.0
        self._pulse_scale = 1.0
        self._hover_opacity = 0.0

        # Visual properties aligned with Fluent Design
        self._corner_radius = 4
        self._track_height = 4
        self._is_hovering = False
        self._show_percentage = False

        # Performance optimization
        self._cached_geometry = QRect()
        self._needs_repaint = True
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._update_animation_cache)
        self._animation_timer.setInterval(16)  # 60 FPS

        # Animation management
        self._animation_refs = weakref.WeakSet()
        self._progress_animation = None
        self._indeterminate_animation = None
        self._glow_animation = None
        self._pulse_animation = None
        self._hover_animation = None

        # Fluent Design sizing
        self.setMinimumHeight(4)
        self.setMaximumHeight(4)
        self.setTextVisible(False)

        self._setup_fluent_style()
        self._setup_animations()
        self._setup_mouse_tracking()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def __del__(self):
        """Ensure proper cleanup"""
        self._cleanup_animations()

    def _cleanup_animations(self):
        """Clean up animations and timers"""
        if hasattr(self, '_animation_timer') and self._animation_timer:
            self._animation_timer.stop()

        for animation in list(self._animation_refs):
            if animation and animation.state() == QAbstractAnimation.State.Running:
                animation.stop()
        self._animation_refs.clear()

    def _setup_fluent_style(self):
        """Setup Fluent Design visual styling"""
        theme = theme_manager

        # Fluent Design color palette
        primary_color = theme.get_color('primary')
        control_fill = theme.get_color('control_fill_default')
        control_stroke = theme.get_color('control_stroke_default')

        # Modern Fluent Design styling with subtle effects
        style_sheet = f"""
            QProgressBar {{
                border: none;
                border-radius: {self._corner_radius}px;
                background-color: {control_fill.name()};
                text-align: center;
                height: {self._track_height}px;
                margin: 0px;
            }}
            QProgressBar::chunk {{
                background-color: {primary_color.name()};
                border-radius: {self._corner_radius}px;
                border: none;
                margin: 0px;
            }}
        """

        self.setStyleSheet(style_sheet)
        self._needs_repaint = True

    def _setup_animations(self):
        """Setup Fluent Design animation system"""
        # Value animation with Fluent easing
        self._progress_animation = QPropertyAnimation(
            self, QByteArray(b"value"))
        self._progress_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._progress_animation.finished.connect(
            self.valueAnimationFinished.emit)
        self._animation_refs.add(self._progress_animation)

        # Indeterminate animation with smooth motion
        self._indeterminate_animation = QPropertyAnimation(
            self, QByteArray(b"animationPosition"))
        self._indeterminate_animation.setDuration(2000)
        self._indeterminate_animation.setLoopCount(-1)
        self._indeterminate_animation.setEasingCurve(
            QEasingCurve.Type.InOutSine)
        self._indeterminate_animation.valueChanged.connect(
            self._on_animation_frame)
        self._animation_refs.add(self._indeterminate_animation)

        # Hover animation for interactive feedback
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hoverOpacity"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._animation_refs.add(self._hover_animation)

        # Glow effect for milestones
        self._glow_animation = QPropertyAnimation(
            self, QByteArray(b"glowIntensity"))
        self._glow_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._glow_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._animation_refs.add(self._glow_animation)

        # Pulse for completion
        self._pulse_animation = QPropertyAnimation(
            self, QByteArray(b"pulseScale"))
        self._pulse_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._pulse_animation.setEasingCurve(QEasingCurve.Type.OutBack)
        self._animation_refs.add(self._pulse_animation)

    def _setup_mouse_tracking(self):
        """Enable mouse tracking for hover effects"""
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def _update_animation_cache(self):
        """Update animation cache for smooth performance"""
        if self._needs_repaint or self.geometry() != self._cached_geometry:
            self._cached_geometry = self.geometry()
            self._needs_repaint = False
            self.update()

    def _on_animation_frame(self):
        """Optimized animation frame update"""
        if not self._animation_timer.isActive():
            self._animation_timer.start()

    # Enhanced property system with Fluent Design properties
    def _get_animation_position(self) -> float:
        return self._animation_position

    def _set_animation_position(self, value: float):
        if abs(self._animation_position - value) > 0.001:
            self._animation_position = value
            self.animationPositionChanged.emit(value)
            self._needs_repaint = True

    def _get_glow_intensity(self) -> float:
        return self._glow_intensity

    def _set_glow_intensity(self, value: float):
        if abs(self._glow_intensity - value) > 0.001:
            new_value = max(0.0, min(1.0, value))
            if abs(self._glow_intensity - new_value) > 0.001:
                self._glow_intensity = new_value
                self.glowIntensityChanged.emit(new_value)
                self._needs_repaint = True

    def _get_pulse_scale(self) -> float:
        return self._pulse_scale

    def _set_pulse_scale(self, value: float):
        if abs(self._pulse_scale - value) > 0.001:
            new_value = max(0.9, min(1.1, value))
            if abs(self._pulse_scale - new_value) > 0.001:
                self._pulse_scale = new_value
                self.pulseScaleChanged.emit(new_value)
                self._needs_repaint = True

    def _get_hover_opacity(self) -> float:
        return self._hover_opacity

    def _set_hover_opacity(self, value: float):
        if abs(self._hover_opacity - value) > 0.001:
            new_value = max(0.0, min(1.0, value))
            if abs(self._hover_opacity - new_value) > 0.001:
                self._hover_opacity = new_value
                self._needs_repaint = True

    # Property declarations
    animationPosition = Property(float, _get_animation_position, _set_animation_position,
                                 None, "Animation position for indeterminate progress")
    glowIntensity = Property(float, _get_glow_intensity, _set_glow_intensity,
                             None, "Glow intensity for visual effects")
    pulseScale = Property(float, _get_pulse_scale, _set_pulse_scale,
                          None, "Pulse scale for animation effects")
    hoverOpacity = Property(float, _get_hover_opacity, _set_hover_opacity,
                            None, "Hover opacity effect")

    def set_value_animated(self, value: int, duration: Optional[int] = None):
        """Set progress value with Fluent Design animation"""
        old_value = self.value()
        new_value = max(self.minimum(), min(value, self.maximum()))

        if old_value == new_value:
            return

        if self._progress_animation:
            self._progress_animation.stop()
            self._progress_animation.setStartValue(old_value)
            self._progress_animation.setEndValue(new_value)

            if duration:
                self._progress_animation.setDuration(duration)
            else:
                # Adaptive duration based on change magnitude
                value_diff = abs(new_value - old_value)
                if value_diff > 50:
                    self._progress_animation.setDuration(
                        FluentAnimation.DURATION_SLOW)
                elif value_diff > 25:
                    self._progress_animation.setDuration(
                        FluentAnimation.DURATION_MEDIUM)
                else:
                    self._progress_animation.setDuration(
                        FluentAnimation.DURATION_FAST)

            self._progress_animation.start()
            self._handle_milestone_effects(old_value, new_value)

    def _handle_milestone_effects(self, old_value: int, new_value: int):
        """Handle Fluent Design milestone celebrations"""
        milestones = [25, 50, 75, 100]

        for milestone in milestones:
            if old_value < milestone <= new_value:
                if milestone == 100:
                    self._animate_completion()
                else:
                    self._animate_milestone(milestone)

    def _animate_milestone(self, milestone: int):
        """Animate milestone achievement with subtle effects"""
        # Gentle glow for milestone
        if self._glow_animation:
            self._glow_animation.setStartValue(0.0)
            self._glow_animation.setEndValue(0.4)
            self._glow_animation.setDuration(FluentAnimation.DURATION_FAST)

            def fade_glow():
                if self._glow_animation:
                    self._glow_animation.finished.disconnect()
                    self._glow_animation.setStartValue(0.4)
                    self._glow_animation.setEndValue(0.0)
                    self._glow_animation.setDuration(
                        FluentAnimation.DURATION_MEDIUM)
                    self._glow_animation.start()

            self._glow_animation.finished.connect(fade_glow)
            self._glow_animation.start()

    def _animate_completion(self):
        """Fluent Design completion animation"""
        # Completion pulse animation
        if self._pulse_animation:
            self._pulse_animation.setStartValue(1.0)
            self._pulse_animation.setEndValue(1.05)
            self._pulse_animation.setDuration(FluentAnimation.DURATION_FAST)

            def return_to_normal():
                if self._pulse_animation:
                    self._pulse_animation.finished.disconnect()
                    self._pulse_animation.setStartValue(1.05)
                    self._pulse_animation.setEndValue(1.0)
                    self._pulse_animation.setDuration(
                        FluentAnimation.DURATION_FAST)
                    self._pulse_animation.start()

            self._pulse_animation.finished.connect(return_to_normal)
            self._pulse_animation.start()

        # Completion glow
        if self._glow_animation:
            self._glow_animation.setStartValue(0.0)
            self._glow_animation.setEndValue(0.8)
            self._glow_animation.setDuration(FluentAnimation.DURATION_MEDIUM)

            def fade_completion_glow():
                if self._glow_animation:
                    self._glow_animation.finished.disconnect()
                    self._glow_animation.setStartValue(0.8)
                    self._glow_animation.setEndValue(0.0)
                    self._glow_animation.setDuration(
                        FluentAnimation.DURATION_SLOW)
                    self._glow_animation.start()

            self._glow_animation.finished.connect(fade_completion_glow)
            self._glow_animation.start()

    def set_indeterminate(self, indeterminate: bool):
        """Set indeterminate state with Fluent transitions"""
        if self._is_indeterminate == indeterminate:
            return

        self._is_indeterminate = indeterminate
        old_state = self._state

        if indeterminate:
            self._state = 'indeterminate'
            if self._indeterminate_animation:
                self._indeterminate_animation.setStartValue(0.0)
                self._indeterminate_animation.setEndValue(1.0)
                self._indeterminate_animation.start()
        else:
            self._state = 'normal'
            if self._indeterminate_animation:
                self._indeterminate_animation.stop()
            self._animation_position = 0.0
            self._needs_repaint = True

        self.stateChanged.emit(self._state)

    def set_state(self, state: str):
        """Set progress state with Fluent visual feedback"""
        valid_states = ['normal', 'indeterminate',
                        'paused', 'error', 'success']
        if state not in valid_states:
            return

        old_state = self._state
        self._state = state
        self._update_state_appearance()
        self.stateChanged.emit(state)

    def _update_state_appearance(self):
        """Update appearance based on current state"""
        self._needs_repaint = True
        self.update()

    def set_show_percentage(self, show: bool):
        """Enable/disable percentage text display"""
        self._show_percentage = show
        self.setTextVisible(show)
        if show:
            self.setMinimumHeight(20)
            self.setMaximumHeight(20)
        else:
            self.setMinimumHeight(4)
            self.setMaximumHeight(4)

    def enterEvent(self, event):
        """Fluent Design hover enter effect"""
        super().enterEvent(event)
        self._is_hovering = True

        if self._hover_animation:
            self._hover_animation.stop()
            self._hover_animation.setStartValue(self._hover_opacity)
            self._hover_animation.setEndValue(0.1)
            self._hover_animation.start()

    def leaveEvent(self, event):
        """Fluent Design hover leave effect"""
        super().leaveEvent(event)
        self._is_hovering = False

        if self._hover_animation:
            self._hover_animation.stop()
            self._hover_animation.setStartValue(self._hover_opacity)
            self._hover_animation.setEndValue(0.0)
            self._hover_animation.start()

    def paintEvent(self, event: QPaintEvent):
        """Enhanced Fluent Design paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        theme = theme_manager

        # Apply pulse scale transform
        if abs(self._pulse_scale - 1.0) > 0.01:
            center = rect.center()
            painter.save()
            painter.translate(center)
            painter.scale(self._pulse_scale, self._pulse_scale)
            painter.translate(-center)

        # Draw progress based on state
        if self._is_indeterminate:
            self._paint_indeterminate_progress(painter, rect, theme)
        else:
            self._paint_determinate_progress(painter, rect, theme)

        # Draw percentage text if enabled
        if self._show_percentage and not self._is_indeterminate:
            self._paint_percentage_text(painter, rect, theme)

        if abs(self._pulse_scale - 1.0) > 0.01:
            painter.restore()

        # Draw glow effect
        if self._glow_intensity > 0.01:
            self._paint_glow_effect(painter, rect, theme)

    def _paint_determinate_progress(self, painter: QPainter, rect: QRect, theme):
        """Paint determinate progress with Fluent Design styling"""
        painter.setPen(Qt.PenStyle.NoPen)

        # Background track
        track_rect = QRect(0, rect.height() // 2 - self._track_height // 2,
                           rect.width(), self._track_height)

        # Control fill color from theme
        control_fill = theme.get_color('control_fill_default')
        if self._is_hovering:
            control_fill = theme.get_color('control_fill_secondary')

        painter.setBrush(QBrush(control_fill))
        painter.drawRoundedRect(
            track_rect, self._corner_radius, self._corner_radius)

        # Progress fill
        if self.maximum() > self.minimum() and self.value() > self.minimum():
            progress_width = int((self.value() - self.minimum()) /
                                 (self.maximum() - self.minimum()) * track_rect.width())

            if progress_width > 0:
                progress_rect = QRect(track_rect.x(), track_rect.y(),
                                      progress_width, track_rect.height())

                # State-based colors
                fill_color = self._get_state_color(theme)

                # Add hover effect
                if self._hover_opacity > 0:
                    hover_color = fill_color.lighter(110)
                    fill_color = self._blend_colors(
                        fill_color, hover_color, self._hover_opacity)

                painter.setBrush(QBrush(fill_color))
                painter.drawRoundedRect(
                    progress_rect, self._corner_radius, self._corner_radius)

    def _paint_indeterminate_progress(self, painter: QPainter, rect: QRect, theme):
        """Paint indeterminate progress with Fluent animation"""
        painter.setPen(Qt.PenStyle.NoPen)

        # Background track
        track_rect = QRect(0, rect.height() // 2 - self._track_height // 2,
                           rect.width(), self._track_height)

        control_fill = theme.get_color('control_fill_default')
        painter.setBrush(QBrush(control_fill))
        painter.drawRoundedRect(
            track_rect, self._corner_radius, self._corner_radius)

        # Animated progress dot
        dot_width = int(track_rect.width() * 0.3)  # 30% of track width
        dot_position = int((track_rect.width() - dot_width)
                           * self._animation_position)

        dot_rect = QRect(track_rect.x() + dot_position, track_rect.y(),
                         dot_width, track_rect.height())

        fill_color = self._get_state_color(theme)
        painter.setBrush(QBrush(fill_color))
        painter.drawRoundedRect(
            dot_rect, self._corner_radius, self._corner_radius)

    def _paint_percentage_text(self, painter: QPainter, rect: QRect, theme):
        """Paint percentage text with Fluent typography"""
        if self.maximum() <= self.minimum():
            return

        percentage = int((self.value() - self.minimum()) /
                         (self.maximum() - self.minimum()) * 100)
        text = f"{percentage}%"

        # Fluent Design font
        font = QFont("Segoe UI", 9)
        font.setWeight(QFont.Weight.Normal)
        painter.setFont(font)

        # Text color from theme
        text_color = theme.get_color('text_primary')
        painter.setPen(QPen(text_color))

        # Center text
        font_metrics = QFontMetrics(font)
        text_rect = font_metrics.boundingRect(text)
        x = (rect.width() - text_rect.width()) // 2
        y = rect.height() // 2 + text_rect.height() // 2 - 2

        painter.drawText(x, y, text)

    def _paint_glow_effect(self, painter: QPainter, rect: QRect, theme):
        """Paint glow effect for milestones"""
        if self._glow_intensity <= 0.01:
            return

        glow_color = self._get_state_color(theme)
        glow_color.setAlpha(int(self._glow_intensity * 60))

        # Glow around the entire progress bar
        glow_rect = rect.adjusted(-2, -1, 2, 1)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow_color))
        painter.drawRoundedRect(
            glow_rect, self._corner_radius + 2, self._corner_radius + 2)

    def _get_state_color(self, theme) -> QColor:
        """Get color based on current state"""
        state_colors = {
            'normal': theme.get_color('accent_default'),
            'indeterminate': theme.get_color('accent_default'),
            'paused': theme.get_color('text_secondary'),
            'error': QColor('#c42b1c'),  # Fluent error red
            'success': QColor('#107c10')  # Fluent success green
        }
        return state_colors.get(self._state, theme.get_color('accent_default'))

    def _blend_colors(self, color1: QColor, color2: QColor, ratio: float) -> QColor:
        """Blend two colors with given ratio"""
        r = int(color1.red() * (1 - ratio) + color2.red() * ratio)
        g = int(color1.green() * (1 - ratio) + color2.green() * ratio)
        b = int(color1.blue() * (1 - ratio) + color2.blue() * ratio)
        a = int(color1.alpha() * (1 - ratio) + color2.alpha() * ratio)
        return QColor(r, g, b, a)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme changes with Fluent transitions"""
        self._setup_fluent_style()

        # Smooth transition on theme change
        fade_out = FluentRevealEffect.fade_out(
            self, duration=FluentAnimation.DURATION_FAST)

        def apply_and_fade_in():
            self.update()
            FluentRevealEffect.fade_in(
                self, duration=FluentAnimation.DURATION_FAST)

        if fade_out:
            fade_out.finished.connect(apply_and_fade_in)
        else:
            apply_and_fade_in()

    # Public API methods for better integration
    def set_corner_radius(self, radius: int):
        """Set corner radius for customization"""
        if radius >= 0:
            self._corner_radius = radius
            self._setup_fluent_style()

    def set_track_height(self, height: int):
        """Set track height for customization"""
        if height > 0:
            self._track_height = height
            self.setMinimumHeight(height)
            self.setMaximumHeight(height)
            self._setup_fluent_style()

    def pause_animation(self):
        """Pause all animations"""
        if self._progress_animation and self._progress_animation.state() == QAbstractAnimation.State.Running:
            self._progress_animation.pause()
        if self._indeterminate_animation and self._indeterminate_animation.state() == QAbstractAnimation.State.Running:
            self._indeterminate_animation.pause()
        self.set_state('paused')

    def resume_animation(self):
        """Resume paused animations"""
        if self._progress_animation and self._progress_animation.state() == QAbstractAnimation.State.Paused:
            self._progress_animation.resume()
        if self._indeterminate_animation and self._indeterminate_animation.state() == QAbstractAnimation.State.Paused:
            self._indeterminate_animation.resume()
        self.set_state(
            'normal' if not self._is_indeterminate else 'indeterminate')


    def is_indeterminate(self) -> bool:
        """Return whether the progress bar is in indeterminate mode."""
        return self._is_indeterminate

class FluentSlider(QSlider):
    """Enhanced Fluent Design slider with advanced interactions and accessibility"""

    # Enhanced signals for better interactivity
    value_changing = Signal(int)
    drag_started = Signal()
    drag_finished = Signal()
    hover_value_changed = Signal(int)
    animationScaleChanged = Signal(float)
    thumbGlowChanged = Signal(float)

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent: Optional[QWidget] = None):
        super().__init__(orientation, parent)

        # State management
        self._is_dragging = False
        self._is_hovering = False
        self._hover_value = 0
        self._animation_scale = 1.0
        self._thumb_glow = 0.0

        # Enhanced animations
        self._thumb_animation = None
        self._hover_animation = None
        self._glow_animation = None
        self._value_animation = None
        self._animation_refs = weakref.WeakSet()

        # Performance optimizations
        self._cached_groove_rect = QRect()
        self._cached_thumb_rect = QRect()
        self._needs_cache_update = True

        self.setMinimumHeight(40 if orientation ==
                              Qt.Orientation.Horizontal else 160)
        self.setMinimumWidth(160 if orientation ==
                             Qt.Orientation.Horizontal else 40)

        self._setup_style()
        self._setup_animations()
        self._setup_interactions()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def __del__(self):
        """Ensure proper cleanup"""
        self._cleanup_animations()

    def _cleanup_animations(self):
        """Clean up animations for memory efficiency"""
        for animation in list(self._animation_refs):
            if animation and animation.state() == QAbstractAnimation.State.Running:
                animation.stop()
        self._animation_refs.clear()

    def _setup_style(self):
        """Setup enhanced style with theme integration"""
        theme = theme_manager
        primary = theme.get_color('primary')
        surface = theme.get_color('surface')
        border = theme.get_color('border')

        if self.orientation() == Qt.Orientation.Horizontal:
            style_sheet = f"""
                QSlider::groove:horizontal {{
                    border: none;
                    height: 8px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {border.lighter(110).name()},
                        stop:1 {border.name()});
                    border-radius: 4px;
                }}
                QSlider::handle:horizontal {{
                    background: qradialgradient(cx:0.5, cy:0.3, radius:0.8,
                        stop:0 {surface.lighter(120).name()},
                        stop:0.7 {surface.name()},
                        stop:1 {surface.darker(105).name()});
                    border: 3px solid {primary.name()};
                    width: 24px;
                    height: 24px;
                    margin: -10px 0;
                    border-radius: 12px;
                }}
                QSlider::handle:horizontal:hover {{
                    background: qradialgradient(cx:0.5, cy:0.3, radius:0.8,
                        stop:0 {surface.lighter(125).name()},
                        stop:0.7 {surface.lighter(105).name()},
                        stop:1 {surface.name()});
                    border-width: 4px;
                }}
                QSlider::handle:horizontal:pressed {{
                    background: {primary.lighter(110).name()};
                    border-color: {primary.darker(110).name()};
                }}
                QSlider::sub-page:horizontal {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {primary.name()},
                        stop:0.5 {primary.lighter(105).name()},
                        stop:1 {primary.lighter(110).name()});
                    border-radius: 4px;
                }}
                QSlider::add-page:horizontal {{
                    background: {border.name()};
                    border-radius: 4px;
                }}
            """
        else:  # Vertical orientation
            style_sheet = f"""
                QSlider::groove:vertical {{
                    border: none;
                    width: 8px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {border.lighter(110).name()},
                        stop:1 {border.name()});
                    border-radius: 4px;
                }}
                QSlider::handle:vertical {{
                    background: qradialgradient(cx:0.3, cy:0.5, radius:0.8,
                        stop:0 {surface.lighter(120).name()},
                        stop:0.7 {surface.name()},
                        stop:1 {surface.darker(105).name()});
                    border: 3px solid {primary.name()};
                    width: 24px;
                    height: 24px;
                    margin: 0 -10px;
                    border-radius: 12px;
                }}
                QSlider::handle:vertical:hover {{
                    background: qradialgradient(cx:0.3, cy:0.5, radius:0.8,
                        stop:0 {surface.lighter(125).name()},
                        stop:0.7 {surface.lighter(105).name()},
                        stop:1 {surface.name()});
                    border-width: 4px;
                }}
                QSlider::sub-page:vertical {{
                    background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                        stop:0 {primary.name()},
                        stop:0.5 {primary.lighter(105).name()},
                        stop:1 {primary.lighter(110).name()});
                    border-radius: 4px;
                }}
                QSlider::add-page:vertical {{
                    background: {border.name()};
                    border-radius: 4px;
                }}
            """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup enhanced animation system"""
        # Thumb scale animation
        self._thumb_animation = QPropertyAnimation(
            self, QByteArray(b"animationScale"))
        self._thumb_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._thumb_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
        self._animation_refs.add(self._thumb_animation)

        # Hover glow animation
        self._glow_animation = QPropertyAnimation(
            self, QByteArray(b"thumbGlow"))
        self._glow_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._glow_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation_refs.add(self._glow_animation)

        # Value change animation
        self._value_animation = QPropertyAnimation(self, QByteArray(b"value"))
        self._value_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._value_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
        self._animation_refs.add(self._value_animation)

    def _setup_interactions(self):
        """Setup enhanced interactions and signals"""
        self.sliderPressed.connect(self._on_slider_pressed)
        self.sliderReleased.connect(self._on_slider_released)
        self.sliderMoved.connect(self._on_slider_moved)
        self.valueChanged.connect(self._on_value_changed)

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)

    # Enhanced property system
    def _get_animation_scale(self) -> float:
        return self._animation_scale

    def _set_animation_scale(self, scale: float):
        if abs(self._animation_scale - scale) > 0.01:
            new_scale = max(0.8, min(1.3, scale))
            if abs(self._animation_scale - new_scale) > 0.01:
                self._animation_scale = new_scale
                self.animationScaleChanged.emit(new_scale)
                self.update()

    def _get_thumb_glow(self) -> float:
        return self._thumb_glow

    def _set_thumb_glow(self, glow: float):
        if abs(self._thumb_glow - glow) > 0.01:
            new_glow = max(0.0, min(1.0, glow))
            if abs(self._thumb_glow - new_glow) > 0.01:
                self._thumb_glow = new_glow
                self.thumbGlowChanged.emit(new_glow)
                self.update()

    # Property declarations
    animationScale = Property(float, _get_animation_scale,
                              _set_animation_scale, None, "Animation scale")
    thumbGlow = Property(float, _get_thumb_glow,
                         _set_thumb_glow, None, "Thumb glow effect")

    def set_value_animated(self, value: int, duration: Optional[int] = None):
        """Set value with smooth animation"""
        if self._value_animation:
            self._value_animation.stop()
            self._value_animation.setStartValue(self.value())
            self._value_animation.setEndValue(
                max(self.minimum(), min(value, self.maximum())))

            if duration:
                self._value_animation.setDuration(duration)
            else:
                # Dynamic duration based on value change
                value_diff = abs(value - self.value())
                range_size = self.maximum() - self.minimum()
                if range_size > 0:
                    duration = int(FluentAnimation.DURATION_FAST +
                                   (value_diff / range_size) * FluentAnimation.DURATION_MEDIUM)
                    self._value_animation.setDuration(
                        min(duration, FluentAnimation.DURATION_SLOW))

            self._value_animation.start()

    def _on_slider_pressed(self):
        """Enhanced slider press handling"""
        self._is_dragging = True
        self.drag_started.emit()

        # Animate thumb press
        if self._thumb_animation:
            self._thumb_animation.setStartValue(1.0)
            self._thumb_animation.setEndValue(0.95)
            self._thumb_animation.start()

    def _on_slider_released(self):
        """Enhanced slider release handling"""
        self._is_dragging = False
        self.drag_finished.emit()

        # Animate thumb release with bounce
        if self._thumb_animation:
            self._thumb_animation.setStartValue(0.95)
            self._thumb_animation.setEndValue(1.05)
            self._thumb_animation.setEasingCurve(QEasingCurve.Type.OutBack)
            self._thumb_animation.finished.connect(
                self._return_to_normal_scale)
            self._thumb_animation.start()

    def _return_to_normal_scale(self):
        """Return thumb to normal scale"""
        if self._thumb_animation:
            self._thumb_animation.finished.disconnect()
            self._thumb_animation.setStartValue(1.05)
            self._thumb_animation.setEndValue(1.0)
            self._thumb_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
            self._thumb_animation.start()

    def _on_slider_moved(self, value: int):
        """Handle slider movement during drag"""
        self.value_changing.emit(value)

    def _on_value_changed(self, _value: int):
        """Handle value changes with visual feedback"""
        # Add subtle pulse for significant changes
        if not self._is_dragging:
            self._animate_value_feedback()

    def _animate_value_feedback(self):
        """Animate feedback for value changes"""
        if self._glow_animation:
            self._glow_animation.setStartValue(0.0)
            self._glow_animation.setEndValue(0.3)
            self._glow_animation.setDuration(FluentAnimation.DURATION_FAST)

            def fade_glow():
                if self._glow_animation:
                    self._glow_animation.finished.disconnect()
                    self._glow_animation.setStartValue(0.3)
                    self._glow_animation.setEndValue(0.0)
                    self._glow_animation.setDuration(
                        FluentAnimation.DURATION_MEDIUM)
                    self._glow_animation.start()

            self._glow_animation.finished.connect(fade_glow)
            self._glow_animation.start()

    def enterEvent(self, event):
        """Enhanced hover enter effect"""
        super().enterEvent(event)
        self._is_hovering = True

        # Animate glow on hover
        if self._glow_animation and not self._is_dragging:
            self._glow_animation.stop()
            self._glow_animation.setStartValue(self._thumb_glow)
            self._glow_animation.setEndValue(0.2)
            self._glow_animation.setDuration(FluentAnimation.DURATION_FAST)
            self._glow_animation.start()

    def leaveEvent(self, event):
        """Enhanced hover leave effect"""
        super().leaveEvent(event)
        self._is_hovering = False

        # Fade glow on leave
        if self._glow_animation and not self._is_dragging:
            self._glow_animation.stop()
            self._glow_animation.setStartValue(self._thumb_glow)
            self._glow_animation.setEndValue(0.0)
            self._glow_animation.setDuration(FluentAnimation.DURATION_FAST)
            self._glow_animation.start()

    def mouseMoveEvent(self, event):
        """Enhanced mouse move with hover value tracking"""
        super().mouseMoveEvent(event)

        if self._is_hovering and not self._is_dragging:
            # Calculate hover value for tooltip or preview
            if self.orientation() == Qt.Orientation.Horizontal:
                groove_rect = self.rect().adjusted(12, 0, -12, 0)  # Account for handle
                relative_pos = (event.position().x() -
                                groove_rect.x()) / groove_rect.width()
            else:
                groove_rect = self.rect().adjusted(0, 12, 0, -12)
                relative_pos = 1.0 - \
                    (event.position().y() - groove_rect.y()) / groove_rect.height()

            relative_pos = max(0.0, min(1.0, relative_pos))
            hover_value = int(self.minimum() + relative_pos *
                              (self.maximum() - self.minimum()))

            if hover_value != self._hover_value:
                self._hover_value = hover_value
                self.hover_value_changed.emit(hover_value)

    def _apply_theme_and_fade_in(self):
        """Apply theme changes and fade in the widget"""
        self._setup_style()
        self.update()
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_FAST)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme changes with smooth transitions"""
        # Fade out, update style, fade in
        fade_transition = FluentRevealEffect.fade_out(
            self, duration=FluentAnimation.DURATION_FAST)
        if fade_transition:
            fade_transition.finished.connect(self._apply_theme_and_fade_in)
        else:
            self._apply_theme_and_fade_in()


class FluentRangeSlider(QWidget):
    """Enhanced dual-end range slider with advanced interactions and accessibility"""

    # Enhanced signals
    range_changed = Signal(int, int)  # min_value, max_value
    range_changing = Signal(int, int)  # During drag
    min_value_changed = Signal(int)
    max_value_changed = Signal(int)
    drag_started = Signal(str)
    drag_finished = Signal(str)
    thumbScaleMinChanged = Signal(float)
    thumbScaleMaxChanged = Signal(float)
    trackGlowChanged = Signal(float)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Core range properties
        self._min_value = 0
        self._max_value = 100
        self._range_min = 20
        self._range_max = 80
        self._step = 1

        # State management
        self._dragging_min = False
        self._dragging_max = False
        self._hover_thumb = None  # 'min', 'max', or None
        self._last_mouse_pos = QPoint()
        self._focused_thumb = None  # For keyboard navigation

        # Visual enhancement properties
        self._thumb_scale_min = 1.0
        self._thumb_scale_max = 1.0
        self._track_glow = 0.0
        self._animation_refs = weakref.WeakSet()

        # Performance optimization
        self._cached_track_rect = QRect()
        self._cached_thumb_positions = {'min': 0, 'max': 0}
        self._needs_cache_update = True

        # Accessibility
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)

        self.setMinimumHeight(48)
        self.setMinimumWidth(240)
        self.setMouseTracking(True)

        self._setup_animations()
        self._setup_accessibility()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def __del__(self):
        """Ensure proper cleanup"""
        self._cleanup_animations()

    def _cleanup_animations(self):
        """Clean up animations for memory efficiency"""
        for animation in list(self._animation_refs):
            if animation and animation.state() == QAbstractAnimation.State.Running:
                animation.stop()
        self._animation_refs.clear()

    def _setup_animations(self):
        """Setup enhanced animation system"""
        # Thumb scale animations
        self._min_thumb_animation = QPropertyAnimation(
            self, QByteArray(b"thumbScaleMin"))
        self._min_thumb_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._min_thumb_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
        self._animation_refs.add(self._min_thumb_animation)

        self._max_thumb_animation = QPropertyAnimation(
            self, QByteArray(b"thumbScaleMax"))
        self._max_thumb_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._max_thumb_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
        self._animation_refs.add(self._max_thumb_animation)

        # Track glow animation
        self._glow_animation = QPropertyAnimation(
            self, QByteArray(b"trackGlow"))
        self._glow_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._glow_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation_refs.add(self._glow_animation)

    def _setup_accessibility(self):
        """Setup accessibility features"""
        self.setAccessibleName("Range Slider")
        self.setAccessibleDescription(
            f"Dual range slider from {self._min_value} to {self._max_value}")
        self.setToolTip(
            "Use mouse to drag handles or arrow keys to adjust values")

    # Enhanced property system
    def _get_thumb_scale_min(self) -> float:
        return self._thumb_scale_min

    def _set_thumb_scale_min(self, scale: float):
        if abs(self._thumb_scale_min - scale) > 0.01:
            new_scale = max(0.8, min(1.4, scale))
            if abs(self._thumb_scale_min - new_scale) > 0.01:
                self._thumb_scale_min = new_scale
                self.thumbScaleMinChanged.emit(new_scale)
                self.update()

    def _get_thumb_scale_max(self) -> float:
        return self._thumb_scale_max

    def _set_thumb_scale_max(self, scale: float):
        if abs(self._thumb_scale_max - scale) > 0.01:
            new_scale = max(0.8, min(1.4, scale))
            if abs(self._thumb_scale_max - new_scale) > 0.01:
                self._thumb_scale_max = new_scale
                self.thumbScaleMaxChanged.emit(new_scale)
                self.update()

    def _get_track_glow(self) -> float:
        return self._track_glow

    def _set_track_glow(self, glow: float):
        if abs(self._track_glow - glow) > 0.01:
            new_glow = max(0.0, min(1.0, glow))
            if abs(self._track_glow - new_glow) > 0.01:
                self._track_glow = new_glow
                self.trackGlowChanged.emit(new_glow)
                self.update()

    # Property declarations
    thumbScaleMin = Property(float, _get_thumb_scale_min,
                             _set_thumb_scale_min, None, "Minimum thumb scale")
    thumbScaleMax = Property(float, _get_thumb_scale_max,
                             _set_thumb_scale_max, None, "Maximum thumb scale")
    trackGlow = Property(float, _get_track_glow,
                         _set_track_glow, None, "Track glow effect")

    def set_range(self, minimum: int, maximum: int):
        """Set total range with validation and animation"""
        if minimum >= maximum:
            raise ValueError("Minimum must be less than maximum")

        old_min, old_max = self._min_value, self._max_value
        self._min_value = minimum
        self._max_value = maximum

        # Ensure current values are within new range
        self._range_min = max(self._min_value, min(
            self._range_min, self._max_value))
        self._range_max = max(self._min_value, min(
            self._range_max, self._max_value))

        if self._range_min > self._range_max:
            self._range_min, self._range_max = self._range_max, self._range_min

        self._needs_cache_update = True
        self._update_accessibility()

        # Animate range change
        if old_min != minimum or old_max != maximum:
            self._animate_range_change()

        self.update()

    def _animate_range_change(self):
        """Animate visual feedback for range changes"""
        if self._glow_animation:
            self._glow_animation.setStartValue(0.0)
            self._glow_animation.setEndValue(0.4)
            self._glow_animation.setDuration(FluentAnimation.DURATION_FAST)

            def fade_glow():
                if self._glow_animation:
                    self._glow_animation.finished.disconnect()
                    self._glow_animation.setStartValue(0.4)
                    self._glow_animation.setEndValue(0.0)
                    self._glow_animation.setDuration(
                        FluentAnimation.DURATION_MEDIUM)
                    self._glow_animation.start()

            self._glow_animation.finished.connect(fade_glow)
            self._glow_animation.start()

    def set_values(self, range_min: int, range_max: int, animated: bool = True):
        """Set selected range with optional animation and validation"""
        try:
            old_min, old_max = self._range_min, self._range_max

            # Validate and clamp values
            range_min = max(self._min_value, min(range_min, self._max_value))
            range_max = max(self._min_value, min(range_max, self._max_value))

            if range_min > range_max:
                range_min, range_max = range_max, range_min

            self._range_min = range_min
            self._range_max = range_max

            # Trigger milestone effects for significant changes
            if animated and (abs(self._range_min - old_min) > (self._max_value - self._min_value) * 0.1 or
               abs(self._range_max - old_max) > (self._max_value - self._min_value) * 0.1):
                self._animate_value_change()

            self._needs_cache_update = True
            self._update_accessibility()
            self.update()

            if old_min != self._range_min:
                self.min_value_changed.emit(self._range_min)
            if old_max != self._range_max:
                self.max_value_changed.emit(self._range_max)

            self.range_changed.emit(self._range_min, self._range_max)

        except Exception as e:
            print(f"Error setting range values: {e}")

    def _animate_value_change(self):
        """Animate feedback for significant value changes"""
        # Pulse both thumbs
        self._animate_thumb_pulse('min')
        self._animate_thumb_pulse('max')

    def _animate_thumb_pulse(self, thumb: str, scale: float = 1.15):
        """Animate thumb pulse effect"""
        animation = self._min_thumb_animation if thumb == 'min' else self._max_thumb_animation

        if animation:
            animation.stop()
            animation.setStartValue(1.0)
            animation.setEndValue(scale)
            animation.setEasingCurve(QEasingCurve.Type.OutBack)

            def return_to_normal():
                animation.finished.disconnect()
                animation.setStartValue(scale)
                animation.setEndValue(1.0)
                animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
                animation.start()

            animation.finished.connect(return_to_normal)
            animation.start()

    def get_values(self) -> tuple[int, int]:
        """Get selected range"""
        return self._range_min, self._range_max

    def _update_cache(self):
        """Update cached calculations for performance"""
        if not self._needs_cache_update:
            return

        rect = self.rect()
        # Track area with padding for thumbs
        padding = 24
        self._cached_track_rect = rect.adjusted(padding, rect.height() // 2 - 4,
                                                -padding, -rect.height() // 2 + 4)

        # Calculate thumb positions
        if self._max_value > self._min_value:
            total_width = self._cached_track_rect.width()
            min_pos_float = (self._range_min - self._min_value) / \
                (self._max_value - self._min_value)
            max_pos_float = (self._range_max - self._min_value) / \
                (self._max_value - self._min_value)

            self._cached_thumb_positions['min'] = int(
                self._cached_track_rect.left() + total_width * min_pos_float)
            self._cached_thumb_positions['max'] = int(
                self._cached_track_rect.left() + total_width * max_pos_float)

        self._needs_cache_update = False

    def paintEvent(self, _event):
        """Enhanced paint event with optimized rendering and visual effects"""
        self._update_cache()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        theme = theme_manager
        rect = self.rect()

        # Draw track with enhanced styling
        self._draw_track(painter, rect, theme)

        # Draw selected range with glow effects
        self._draw_selected_range(painter, rect, theme)

        # Draw thumbs with enhanced visuals
        self._draw_thumbs(painter, rect, theme)

        # Draw focus indicator if focused
        if self.hasFocus() and self._focused_thumb:
            self._draw_focus_indicator(painter, rect, theme)

    def _draw_track(self, painter: QPainter, rect: QRect, theme):
        """Draw background track with enhanced styling"""
        track_y = rect.height() // 2 - 4
        track_rect = rect.adjusted(24, track_y, -24, -track_y)

        # Draw shadow for depth
        shadow_rect = track_rect.adjusted(0, 2, 0, 2)
        shadow_color = theme.get_color('shadow')
        shadow_color.setAlpha(40)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(shadow_rect, 4, 4)

        # Draw main track with gradient
        gradient = QLinearGradient(
            track_rect.topLeft(), track_rect.bottomRight())
        border_color = theme.get_color('border')
        gradient.setColorAt(0, border_color.lighter(110))
        gradient.setColorAt(0.5, border_color)
        gradient.setColorAt(1, border_color.darker(105))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(track_rect, 4, 4)

    def _draw_selected_range(self, painter: QPainter, rect: QRect, theme):
        """Draw selected range with enhanced visuals and glow effects"""
        if self._max_value <= self._min_value:
            return

        track_y = rect.height() // 2 - 4
        track_rect = rect.adjusted(24, track_y, -24, -track_y)

        # Calculate selected area
        total_width = track_rect.width()
        min_pos = (self._range_min - self._min_value) / \
            (self._max_value - self._min_value)
        max_pos = (self._range_max - self._min_value) / \
            (self._max_value - self._min_value)

        selected_left = track_rect.left() + total_width * min_pos
        selected_width = total_width * (max_pos - min_pos)

        if selected_width <= 0:
            return

        selected_rect = QRect(int(selected_left), track_rect.top(),
                              int(selected_width), track_rect.height())

        # Draw glow effect if active
        if self._track_glow > 0.01:
            glow_rect = selected_rect.adjusted(-6, -3, 6, 3)
            glow_color = theme.get_color('primary')
            glow_color.setAlpha(int(self._track_glow * 80))

            glow_gradient = QLinearGradient(
                glow_rect.topLeft(), glow_rect.bottomRight())
            glow_gradient.setColorAt(
                0, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 0))
            glow_gradient.setColorAt(0.5, glow_color)
            glow_gradient.setColorAt(
                1, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 0))

            painter.setBrush(QBrush(glow_gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(glow_rect, 6, 6)

        # Draw selected range with enhanced gradient
        primary_color = theme.get_color('primary')
        range_gradient = QLinearGradient(
            selected_rect.topLeft(), selected_rect.bottomRight())
        range_gradient.setColorAt(0, primary_color.lighter(115))
        range_gradient.setColorAt(0.5, primary_color)
        range_gradient.setColorAt(1, primary_color.darker(105))

        painter.setBrush(QBrush(range_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(selected_rect, 4, 4)

    def _draw_thumbs(self, painter: QPainter, rect: QRect, theme):
        """Draw thumbs with enhanced styling and animations"""
        if self._max_value <= self._min_value:
            return

        track_y = rect.height() // 2 - 4
        track_rect = rect.adjusted(24, track_y, -24, -track_y)

        # Calculate thumb positions
        total_width = track_rect.width()
        min_pos = (self._range_min - self._min_value) / \
            (self._max_value - self._min_value)
        max_pos = (self._range_max - self._min_value) / \
            (self._max_value - self._min_value)

        min_x = track_rect.left() + total_width * min_pos
        max_x = track_rect.left() + total_width * max_pos
        thumb_y = rect.height() // 2

        # Draw thumbs with scaling and enhanced styling
        self._draw_thumb(painter, min_x, thumb_y, 'min', theme)
        self._draw_thumb(painter, max_x, thumb_y, 'max', theme)

    def _draw_thumb(self, painter: QPainter, x: float, y: float, thumb_type: str, theme):
        """Draw individual thumb with enhanced styling"""
        is_dragging = (thumb_type == 'min' and self._dragging_min) or (
            thumb_type == 'max' and self._dragging_max)
        is_hovering = self._hover_thumb == thumb_type
        is_focused = self._focused_thumb == thumb_type

        # Calculate scale and radius
        scale = self._thumb_scale_min if thumb_type == 'min' else self._thumb_scale_max
        base_radius = 12
        radius = int(base_radius * scale)

        # Enhanced shadow with multiple layers
        shadow_layers = [
            (3, 60),  # Close shadow
            (6, 30),  # Medium shadow
            (12, 15)   # Far shadow
        ]

        shadow_color = theme.get_color('shadow')
        for offset, alpha in shadow_layers:
            layer_color = QColor(shadow_color)
            layer_color.setAlpha(alpha)
            painter.setBrush(QBrush(layer_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(x - radius - offset//2), int(y - radius + offset),
                                (radius + offset//2) * 2, (radius + offset//2) * 2)

        # Draw thumb background with gradient
        thumb_gradient = QRadialGradient(x, y - radius//3, radius)
        surface_color = theme.get_color('surface')

        if is_dragging:
            thumb_gradient.setColorAt(0, surface_color.lighter(125))
            thumb_gradient.setColorAt(0.7, surface_color.lighter(110))
            thumb_gradient.setColorAt(1, surface_color)
        elif is_hovering:
            thumb_gradient.setColorAt(0, surface_color.lighter(120))
            thumb_gradient.setColorAt(0.7, surface_color.lighter(105))
            thumb_gradient.setColorAt(1, surface_color.darker(102))
        else:
            thumb_gradient.setColorAt(0, surface_color.lighter(115))
            thumb_gradient.setColorAt(0.7, surface_color)
            thumb_gradient.setColorAt(1, surface_color.darker(105))

        painter.setBrush(QBrush(thumb_gradient))

        # Enhanced border
        primary_color = theme.get_color('primary')
        border_width = 4 if is_dragging else 3 if is_hovering else 2
        border_color = primary_color.lighter(
            110) if is_hovering else primary_color

        painter.setPen(QPen(border_color, border_width))
        painter.drawEllipse(int(x - radius), int(y - radius),
                            radius * 2, radius * 2)

        # Inner highlight
        if not is_dragging:
            highlight_color = surface_color.lighter(140)
            highlight_color.setAlpha(180)
            painter.setBrush(QBrush(highlight_color))
            painter.setPen(Qt.PenStyle.NoPen)
            highlight_radius = radius // 3
            painter.drawEllipse(int(x - highlight_radius), int(y - radius//2),
                                highlight_radius * 2, highlight_radius)

        # Focus ring
        if is_focused:
            focus_color = theme.get_color('accent')
            focus_color.setAlpha(120)
            painter.setPen(QPen(focus_color, 2, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(int(x - radius - 6), int(y - radius - 6),
                                (radius + 6) * 2, (radius + 6) * 2)

    def _draw_focus_indicator(self, painter: QPainter, rect: QRect, theme):
        """Draw focus indicator for accessibility"""
        if not self._focused_thumb:
            return

        focus_color = theme.get_color('accent')
        focus_color.setAlpha(100)

        painter.setPen(QPen(focus_color, 2, Qt.PenStyle.DashLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 8, 8)

    # Enhanced mouse interaction
    def mousePressEvent(self, event):
        """Enhanced mouse press with better thumb detection"""
        if event.button() != Qt.MouseButton.LeftButton:
            return

        try:
            x = event.position().x()
            y = event.position().y()

            # Check which thumb was clicked with improved detection
            rect = self.rect()
            track_rect = rect.adjusted(24, 0, -24, 0)

            if self._max_value > self._min_value:
                total_width = track_rect.width()
                min_pos = track_rect.left() + total_width * (self._range_min -
                                                             self._min_value) / (self._max_value - self._min_value)
                max_pos = track_rect.left() + total_width * (self._range_max -
                                                             self._min_value) / (self._max_value - self._min_value)

                # Improved thumb detection with distance and priority
                min_distance = math.sqrt(
                    (x - min_pos)**2 + (y - rect.height()//2)**2)
                max_distance = math.sqrt(
                    (x - max_pos)**2 + (y - rect.height()//2)**2)

                thumb_hit_radius = 20

                if min_distance < thumb_hit_radius and max_distance < thumb_hit_radius:
                    # Both thumbs are close, choose the closer one
                    if min_distance < max_distance:
                        self._start_drag('min')
                    else:
                        self._start_drag('max')
                elif min_distance < thumb_hit_radius:
                    self._start_drag('min')
                elif max_distance < thumb_hit_radius:
                    self._start_drag('max')
                else:
                    # Click on track - move nearest thumb
                    if min_distance < max_distance:
                        self._move_thumb_to_position('min', x, track_rect)
                    else:
                        self._move_thumb_to_position('max', x, track_rect)

                self._last_mouse_pos = event.position().toPoint()

        except Exception as e:
            print(f"Error in mouse press: {e}")

    def _start_drag(self, thumb: str):
        """Start dragging a thumb with visual feedback"""
        if thumb == 'min':
            self._dragging_min = True
            self._focused_thumb = 'min'
        else:
            self._dragging_max = True
            self._focused_thumb = 'max'

        self.drag_started.emit(thumb)
        self._animate_thumb_pulse(thumb, 0.95)
        self.update()

    def _move_thumb_to_position(self, thumb: str, x: float, track_rect: QRect):
        """Move thumb to clicked position with animation"""
        if self._max_value <= self._min_value:
            return

        relative_pos = (x - track_rect.left()) / track_rect.width()
        relative_pos = max(0.0, min(1.0, relative_pos))
        new_value = int(self._min_value + relative_pos *
                        (self._max_value - self._min_value))

        if thumb == 'min':
            new_value = min(new_value, self._range_max)
            if new_value != self._range_min:
                self._range_min = new_value
                self.min_value_changed.emit(self._range_min)
                self._animate_thumb_pulse('min')
        else:
            new_value = max(new_value, self._range_min)
            if new_value != self._range_max:
                self._range_max = new_value
                self.max_value_changed.emit(self._range_max)
                self._animate_thumb_pulse('max')

        self._needs_cache_update = True
        self.update()
        self.range_changed.emit(self._range_min, self._range_max)

    def mouseMoveEvent(self, event):
        """Enhanced mouse move with smooth updates and hover detection"""
        try:
            if self._dragging_min or self._dragging_max:
                x = event.position().x()
                rect = self.rect()
                track_rect = rect.adjusted(24, 0, -24, 0)

                # Calculate new value with snapping
                if self._max_value > self._min_value:
                    relative_pos = (x - track_rect.left()) / track_rect.width()
                    relative_pos = max(0.0, min(1.0, relative_pos))
                    new_value = self._min_value + relative_pos * \
                        (self._max_value - self._min_value)

                    # Apply step snapping
                    if self._step > 1:
                        new_value = round(new_value / self._step) * self._step

                    new_value = int(
                        max(self._min_value, min(new_value, self._max_value)))

                    if self._dragging_min:
                        new_value = min(new_value, self._range_max)
                        if new_value != self._range_min:
                            self._range_min = new_value
                            self.min_value_changed.emit(self._range_min)
                    elif self._dragging_max:
                        new_value = max(new_value, self._range_min)
                        if new_value != self._range_max:
                            self._range_max = new_value
                            self.max_value_changed.emit(self._range_max)

                    self._needs_cache_update = True
                    self.update()
                    self.range_changing.emit(self._range_min, self._range_max)
            else:
                # Handle hover detection
                self._update_hover_state(event.position().toPoint())

        except Exception as e:
            print(f"Error in mouse move: {e}")

    def _update_hover_state(self, pos: QPoint):
        """Update hover state for thumbs"""
        if self._max_value <= self._min_value:
            return

        rect = self.rect()
        track_rect = rect.adjusted(24, 0, -24, 0)

        total_width = track_rect.width()
        min_pos = track_rect.left() + total_width * (self._range_min -
                                                     self._min_value) / (self._max_value - self._min_value)
        max_pos = track_rect.left() + total_width * (self._range_max -
                                                     self._min_value) / (self._max_value - self._min_value)

        min_distance = math.sqrt((pos.x() - min_pos) **
                                 2 + (pos.y() - rect.height()//2)**2)
        max_distance = math.sqrt((pos.x() - max_pos) **
                                 2 + (pos.y() - rect.height()//2)**2)

        old_hover = self._hover_thumb
        thumb_hit_radius = 16

        if min_distance < thumb_hit_radius and (max_distance >= thumb_hit_radius or min_distance < max_distance):
            self._hover_thumb = 'min'
        elif max_distance < thumb_hit_radius:
            self._hover_thumb = 'max'
        else:
            self._hover_thumb = None

        if old_hover != self._hover_thumb:
            self.update()
            if self._hover_thumb:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, _event):
        """Enhanced mouse release with feedback"""
        try:
            thumb_type = None
            if self._dragging_min:
                thumb_type = 'min'
                self._dragging_min = False
                self._animate_thumb_pulse('min', 1.05)
            elif self._dragging_max:
                thumb_type = 'max'
                self._dragging_max = False
                self._animate_thumb_pulse('max', 1.05)

            if thumb_type:
                self.drag_finished.emit(thumb_type)

            self.update()

        except Exception as e:
            print(f"Error in mouse release: {e}")

    # Keyboard navigation support
    def keyPressEvent(self, event):
        """Enhanced keyboard navigation for accessibility"""
        try:
            key = event.key()
            modifiers = event.modifiers()

            # Focus management
            if key == Qt.Key.Key_Tab:
                if not self._focused_thumb:
                    self._focused_thumb = 'min'
                elif self._focused_thumb == 'min':
                    self._focused_thumb = 'max'
                else:
                    self._focused_thumb = 'min'
                self.update()
                return

            if not self._focused_thumb:
                self._focused_thumb = 'min'

            # Value adjustment
            step = self._step
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                step *= 10  # Large step
            elif modifiers & Qt.KeyboardModifier.ControlModifier:
                step = max(1, step // 10)  # Fine step

            if key in [Qt.Key.Key_Left, Qt.Key.Key_Down]:
                self._adjust_focused_thumb(-step)
            elif key in [Qt.Key.Key_Right, Qt.Key.Key_Up]:
                self._adjust_focused_thumb(step)
            elif key == Qt.Key.Key_Home:
                self._set_focused_thumb_value(self._min_value)
            elif key == Qt.Key.Key_End:
                self._set_focused_thumb_value(self._max_value)
            else:
                super().keyPressEvent(event)

        except Exception as e:
            print(f"Error in key press: {e}")

    def _adjust_focused_thumb(self, delta: int):
        """Adjust the focused thumb value"""
        if not self._focused_thumb:
            return

        if self._focused_thumb == 'min':
            new_value = max(self._min_value, min(
                self._range_min + delta, self._range_max))
            if new_value != self._range_min:
                self._range_min = new_value
                self.min_value_changed.emit(self._range_min)
                self._animate_thumb_pulse('min')
        else:
            new_value = max(self._range_min, min(
                self._range_max + delta, self._max_value))
            if new_value != self._range_max:
                self._range_max = new_value
                self.max_value_changed.emit(self._range_max)
                self._animate_thumb_pulse('max')

        self._needs_cache_update = True
        self._update_accessibility()
        self.update()
        self.range_changed.emit(self._range_min, self._range_max)

    def _set_focused_thumb_value(self, value: int):
        """Set focused thumb to specific value"""
        if not self._focused_thumb:
            return

        if self._focused_thumb == 'min':
            new_value = max(self._min_value, min(value, self._range_max))
            if new_value != self._range_min:
                self._range_min = new_value
                self.min_value_changed.emit(self._range_min)
                self._animate_thumb_pulse('min')
        else:
            new_value = max(self._range_min, min(value, self._max_value))
            if new_value != self._range_max:
                self._range_max = new_value
                self.max_value_changed.emit(self._range_max)
                self._animate_thumb_pulse('max')

        self._needs_cache_update = True
        self._update_accessibility()
        self.update()
        self.range_changed.emit(self._range_min, self._range_max)

    def focusInEvent(self, event):
        """Handle focus in with visual feedback"""
        super().focusInEvent(event)
        if not self._focused_thumb:
            self._focused_thumb = 'min'
        self.update()

    def focusOutEvent(self, event):
        """Handle focus out"""
        super().focusOutEvent(event)
        self._focused_thumb = None
        self.update()

    def enterEvent(self, event):
        """Enhanced hover effect with glow animation"""
        super().enterEvent(event)
        if self._glow_animation and not (self._dragging_min or self._dragging_max):
            self._glow_animation.stop()
            self._glow_animation.setStartValue(self._track_glow)
            self._glow_animation.setEndValue(0.1)
            self._glow_animation.setDuration(FluentAnimation.DURATION_FAST)
            self._glow_animation.start()

    def leaveEvent(self, event):
        """Enhanced leave effect"""
        super().leaveEvent(event)
        self._hover_thumb = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

        if self._glow_animation and not (self._dragging_min or self._dragging_max):
            self._glow_animation.stop()
            self._glow_animation.setStartValue(self._track_glow)
            self._glow_animation.setEndValue(0.0)
            self._glow_animation.setDuration(FluentAnimation.DURATION_FAST)
            self._glow_animation.start()

    def resizeEvent(self, event):
        """Handle resize with cache invalidation"""
        super().resizeEvent(event)
        self._needs_cache_update = True

    def _update_accessibility(self):
        """Update accessibility information"""
        self.setAccessibleDescription(
            f"Range slider from {self._min_value} to {self._max_value}. "
            f"Current selection: {self._range_min} to {self._range_max}."
        )

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme changes with smooth transitions"""
        fade_out_anim = FluentRevealEffect.fade_out(
            self, duration=FluentAnimation.DURATION_FAST)

        def _apply_and_fade_in():
            self.update()
            FluentRevealEffect.fade_in(
                self, duration=FluentAnimation.DURATION_FAST)

        if fade_out_anim:
            fade_out_anim.finished.connect(_apply_and_fade_in)
        else:
            _apply_and_fade_in()

    # Additional utility methods
    def set_step(self, step: int):
        """Set step size for value changes"""
        if step > 0:
            self._step = step

    def step(self) -> int:
        """Get current step size"""
        return self._step

    def minimum(self) -> int:
        """Get minimum value"""
        return self._min_value

    def maximum(self) -> int:
        """Get maximum value"""
        return self._max_value

    def range_minimum(self) -> int:
        """Get selected range minimum"""
        return self._range_min

    def range_maximum(self) -> int:
        """Get selected range maximum"""
        return self._range_max
