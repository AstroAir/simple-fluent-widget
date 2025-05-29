"""
Fluent Design style progress bars and slider components
"""

from PySide6.QtWidgets import QProgressBar, QSlider, QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, Property, QByteArray, QEasingCurve
from PySide6.QtGui import QPainter, QBrush, QPen, QLinearGradient, QPaintEvent
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import FluentRevealEffect, FluentMicroInteraction, FluentTransition
from typing import Optional


class FluentProgressBar(QProgressBar):
    """Fluent Design style progress bar"""

    # Add signal for property notification
    animationPositionChanged = Signal(float)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._is_indeterminate = False
        self._animation_position = 0.0
        self._progress_animation = None
        self._indeterminate_animation = None

        self.setMinimumHeight(8)  # Slightly taller for better visibility
        self.setMaximumHeight(8)
        self.setTextVisible(False)

        self._setup_style()
        self._setup_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style with enhanced visual design"""
        theme = theme_manager

        style_sheet = f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {theme.get_color('border').name()};
                text-align: center;
                box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme.get_color('primary').name()},
                    stop:0.5 {theme.get_color('primary').lighter(110).name()},
                    stop:1 {theme.get_color('primary').lighter(120).name()});
                border-radius: 4px;
                margin: 0px;
                transition: all 0.3s ease;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup animations with enhanced curves"""
        # Progress value change animation
        self._progress_animation = QPropertyAnimation(
            self, QByteArray(b"value"))
        self._progress_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._progress_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)

        # Indeterminate state animation
        self._indeterminate_animation = QPropertyAnimation(
            self, QByteArray(b"animationPosition"))
        self._indeterminate_animation.setDuration(1800)  # Slightly faster
        self._indeterminate_animation.setLoopCount(-1)  # Infinite loop
        self._indeterminate_animation.setEasingCurve(
            QEasingCurve.Type.Linear)
        self._indeterminate_animation.valueChanged.connect(self.update)

    def _get_animation_position(self) -> float:
        """Get animation position"""
        return self._animation_position

    def _set_animation_position(self, value: float):
        """Set animation position"""
        if self._animation_position != value:
            self._animation_position = value
            self.animationPositionChanged.emit(value)
            self.update()

    # Fixed Property declaration with notify signal
    animationPosition = Property(float, _get_animation_position, _set_animation_position, None, "",
                                 notify=animationPositionChanged)

    def set_value_animated(self, value: int):
        """Set progress value with enhanced animation"""
        if self._progress_animation:
            self._progress_animation.setStartValue(self.value())
            self._progress_animation.setEndValue(value)
            self._progress_animation.start()

            # Add subtle scale effect when progress changes significantly
            if abs(value - self.value()) > 10:
                FluentMicroInteraction.pulse_animation(self, scale=1.02)

    def set_indeterminate(self, indeterminate: bool):
        """Set indeterminate state with smooth transition"""
        if self._is_indeterminate != indeterminate:
            self._is_indeterminate = indeterminate

            if indeterminate:
                # Fade in effect when starting indeterminate
                FluentRevealEffect.fade_in(
                    self, duration=FluentAnimation.DURATION_FAST)

                if self._indeterminate_animation:
                    self._indeterminate_animation.setStartValue(0.0)
                    self._indeterminate_animation.setEndValue(1.0)
                    self._indeterminate_animation.start()
            else:
                if self._indeterminate_animation:
                    self._indeterminate_animation.stop()
                self._animation_position = 0.0
                self.update()

    def paintEvent(self, event: QPaintEvent):
        """Custom paint with enhanced visuals"""
        if self._is_indeterminate:
            self._paint_indeterminate(event)
        else:
            super().paintEvent(event)

    def _paint_indeterminate(self, _):
        """Paint indeterminate state progress bar with enhanced effects"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        theme = theme_manager

        # Draw background with subtle shadow
        painter.setBrush(QBrush(theme.get_color('border')))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 4, 4)

        # Draw moving progress chunk with enhanced gradient
        chunk_width = rect.width() * 0.35  # Slightly wider
        chunk_x = (rect.width() - chunk_width) * self._animation_position

        chunk_rect = rect.adjusted(
            int(chunk_x), 1, int(chunk_x - rect.width() + chunk_width), -1)

        # Enhanced gradient with more stops
        gradient = QLinearGradient(chunk_rect.topLeft(), chunk_rect.topRight())
        primary_color = theme.get_color('primary')
        gradient.setColorAt(0, primary_color.lighter(140))
        gradient.setColorAt(0.3, primary_color)
        gradient.setColorAt(0.7, primary_color.lighter(110))
        gradient.setColorAt(1, primary_color.lighter(140))

        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(chunk_rect, 3, 3)

        # Add subtle glow effect
        glow_color = primary_color
        glow_color.setAlpha(50)
        painter.setBrush(QBrush(glow_color))
        painter.drawRoundedRect(chunk_rect.adjusted(-2, -1, 2, 1), 4, 4)

    def _on_theme_changed(self, _):
        """Handle theme change with smooth transition"""
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_FAST)
        self._setup_style()


class FluentProgressRing(QWidget):
    """Fluent Design style circular progress ring"""

    # Add signal for property notification
    rotationAngleChanged = Signal(float)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._value = 0
        self._maximum = 100
        self._is_indeterminate = False
        self._rotation_angle = 0.0
        self._ring_animation = None

        self.setFixedSize(48, 48)  # Slightly larger for better visibility

        self._setup_animations()
        theme_manager.theme_changed.connect(self.update)

    def _setup_animations(self):
        """Setup animations with enhanced curves"""
        self._ring_animation = QPropertyAnimation(
            self, QByteArray(b"rotationAngle"))
        # Slightly slower for smoother feel
        self._ring_animation.setDuration(2200)
        self._ring_animation.setLoopCount(-1)
        self._ring_animation.setEasingCurve(
            QEasingCurve.Type.Linear)
        self._ring_animation.valueChanged.connect(self.update)

    def _get_rotation_angle(self) -> float:
        """Get rotation angle"""
        return self._rotation_angle

    def _set_rotation_angle(self, angle: float):
        """Set rotation angle"""
        if self._rotation_angle != angle:
            self._rotation_angle = angle
            self.rotationAngleChanged.emit(angle)
            self.update()

    # Fixed Property declaration with notify signal
    rotationAngle = Property(float, _get_rotation_angle, _set_rotation_angle, None, "",
                             notify=rotationAngleChanged)

    def set_value(self, value: int):
        """Set progress value with animation"""
        old_value = self._value
        self._value = max(0, min(value, self._maximum))

        # Add pulse effect for significant changes
        if abs(self._value - old_value) > 10:
            FluentMicroInteraction.pulse_animation(self, scale=1.05)

        self.update()

    def set_maximum(self, maximum: int):
        """Set maximum value"""
        self._maximum = maximum
        self.update()

    def set_indeterminate(self, indeterminate: bool):
        """Set indeterminate state with enhanced transitions"""
        if self._is_indeterminate != indeterminate:
            self._is_indeterminate = indeterminate

            if indeterminate:
                # Scale in effect when starting
                FluentRevealEffect.scale_in(
                    self, duration=FluentAnimation.DURATION_FAST)

                if self._ring_animation:
                    self._ring_animation.setStartValue(0)
                    self._ring_animation.setEndValue(360)
                    self._ring_animation.start()
            else:
                if self._ring_animation:
                    self._ring_animation.stop()
                self._rotation_angle = 0.0
                self.update()

    def paintEvent(self, _):
        """Paint progress ring with enhanced visuals"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(6, 6, -6, -6)  # More padding for glow
        theme = theme_manager

        # Draw background ring with subtle shadow
        painter.setPen(QPen(theme.get_color('border'), 4, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect)

        # Draw progress ring with enhanced styling
        primary_color = theme.get_color('primary')

        if self._is_indeterminate:
            # Indeterminate state: rotating arc segment with gradient
            gradient_pen = QPen(
                primary_color, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(gradient_pen)

            # Create a subtle glow effect
            glow_color = primary_color
            glow_color.setAlpha(80)
            glow_pen = QPen(glow_color, 6, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap)
            painter.setPen(glow_pen)
            painter.drawArc(rect.adjusted(-1, -1, 1, 1),
                            int((self._rotation_angle - 90) * 16), int(120 * 16))

            # Main arc
            painter.setPen(gradient_pen)
            painter.drawArc(
                rect, int((self._rotation_angle - 90) * 16), int(120 * 16))
        else:
            # Determinate state: draw arc segment based on progress value
            if self._maximum > 0:
                angle = 360 * self._value / self._maximum

                # Draw glow first
                glow_color = primary_color
                glow_color.setAlpha(60)
                glow_pen = QPen(
                    glow_color, 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
                painter.setPen(glow_pen)
                painter.drawArc(rect.adjusted(-1, -1, 1, 1), -
                                90 * 16, int(-angle * 16))

                # Main progress arc
                main_pen = QPen(primary_color, 4,
                                Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
                painter.setPen(main_pen)
                painter.drawArc(rect, -90 * 16, int(-angle * 16))


class FluentSlider(QSlider):
    """Fluent Design style slider with enhanced interactions"""

    value_changing = Signal(int)  # Value change during dragging

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent: Optional[QWidget] = None):
        super().__init__(orientation, parent)

        self._is_dragging = False
        self._thumb_animation = None

        self.setMinimumHeight(36 if orientation ==
                              Qt.Orientation.Horizontal else 140)

        self._setup_style()
        self._setup_animations()

        # Connect signals
        self.sliderPressed.connect(self._on_slider_pressed)
        self.sliderReleased.connect(self._on_slider_released)
        self.sliderMoved.connect(self.value_changing.emit)

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style with enhanced visual design"""
        theme = theme_manager

        if self.orientation() == Qt.Orientation.Horizontal:
            style_sheet = f"""
                QSlider::groove:horizontal {{
                    border: none;
                    height: 6px;
                    background: {theme.get_color('border').name()};
                    border-radius: 3px;
                    box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
                }}
                QSlider::handle:horizontal {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {theme.get_color('surface').lighter(105).name()},
                        stop:1 {theme.get_color('surface').name()});
                    border: 3px solid {theme.get_color('primary').name()};
                    width: 20px;
                    margin: -8px 0;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    transition: all 0.2s ease;
                }}
                QSlider::handle:horizontal:hover {{
                    background: {theme.get_color('accent_light').name()};
                    border-width: 4px;
                    width: 24px;
                    margin: -10px 0;
                    border-radius: 12px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    transform: scale(1.1);
                }}
                QSlider::handle:horizontal:pressed {{
                    background: {theme.get_color('primary').name()};
                    border-color: {theme.get_color('primary').darker(120).name()};
                    transform: scale(0.95);
                }}
                QSlider::sub-page:horizontal {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {theme.get_color('primary').name()},
                        stop:0.5 {theme.get_color('primary').lighter(105).name()},
                        stop:1 {theme.get_color('primary').lighter(110).name()});
                    border-radius: 3px;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                }}
            """
        else:
            style_sheet = f"""
                QSlider::groove:vertical {{
                    border: none;
                    width: 6px;
                    background: {theme.get_color('border').name()};
                    border-radius: 3px;
                    box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
                }}
                QSlider::handle:vertical {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {theme.get_color('surface').lighter(105).name()},
                        stop:1 {theme.get_color('surface').name()});
                    border: 3px solid {theme.get_color('primary').name()};
                    height: 20px;
                    margin: 0 -8px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    transition: all 0.2s ease;
                }}
                QSlider::handle:vertical:hover {{
                    background: {theme.get_color('accent_light').name()};
                    border-width: 4px;
                    height: 24px;
                    margin: 0 -10px;
                    border-radius: 12px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                }}
                QSlider::sub-page:vertical {{
                    background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                        stop:0 {theme.get_color('primary').name()},
                        stop:0.5 {theme.get_color('primary').lighter(105).name()},
                        stop:1 {theme.get_color('primary').lighter(110).name()});
                    border-radius: 3px;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                }}
            """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup animations"""
        self._thumb_animation = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self._thumb_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._thumb_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)

    def _on_slider_pressed(self):
        """Slider pressed with micro-interaction"""
        self._is_dragging = True
        FluentMicroInteraction.button_press(self, scale=0.98)

    def _on_slider_released(self):
        """Slider released with micro-interaction"""
        self._is_dragging = False
        FluentMicroInteraction.pulse_animation(self, scale=1.02)

    def enterEvent(self, event):
        """Enhanced hover effect"""
        super().enterEvent(event)
        FluentMicroInteraction.hover_glow(self, intensity=0.1)

    def _on_theme_changed(self, _):
        """Handle theme change with smooth transition"""
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_FAST)
        self._setup_style()


class FluentRangeSlider(QWidget):
    """Dual-end range slider with enhanced interactions"""

    range_changed = Signal(int, int)  # min_value, max_value

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._min_value = 0
        self._max_value = 100
        self._range_min = 20
        self._range_max = 80

        self._dragging_min = False
        self._dragging_max = False
        self._last_mouse_x = 0

        self.setMinimumHeight(40)  # Taller for better interaction
        self.setMinimumWidth(220)

        theme_manager.theme_changed.connect(self.update)

    def set_range(self, minimum: int, maximum: int):
        """Set total range with validation"""
        self._min_value = minimum
        self._max_value = maximum

        # Ensure current values are within new range
        self._range_min = max(self._min_value, min(
            self._range_min, self._max_value))
        self._range_max = max(self._min_value, min(
            self._range_max, self._max_value))

        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_FAST)
        self.update()

    def set_values(self, range_min: int, range_max: int):
        """Set selected range with animation"""
        old_min, old_max = self._range_min, self._range_max

        self._range_min = max(self._min_value, min(range_min, self._max_value))
        self._range_max = max(self._min_value, min(range_max, self._max_value))

        if self._range_min > self._range_max:
            self._range_min, self._range_max = self._range_max, self._range_min

        # Add pulse effect for significant changes
        if abs(self._range_min - old_min) > 5 or abs(self._range_max - old_max) > 5:
            FluentMicroInteraction.pulse_animation(self, scale=1.02)

        self.update()
        self.range_changed.emit(self._range_min, self._range_max)

    def get_values(self) -> tuple:
        """Get selected range"""
        return self._range_min, self._range_max

    def paintEvent(self, _):
        """Paint range slider with enhanced visuals"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        theme = theme_manager

        # Calculate track area with more padding
        track_y = rect.height() // 2 - 3
        track_rect = rect.adjusted(20, track_y, -20, -track_y)

        # Draw background track with shadow
        shadow_rect = track_rect.adjusted(0, 1, 0, 1)
        shadow_color = theme.get_color('border').darker(120)
        shadow_color.setAlpha(50)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(shadow_rect, 3, 3)

        # Main track
        painter.setBrush(QBrush(theme.get_color('border')))
        painter.drawRoundedRect(track_rect, 3, 3)

        # Calculate selected area
        if self._max_value > self._min_value:
            total_width = track_rect.width()
            min_pos = (self._range_min - self._min_value) / \
                (self._max_value - self._min_value)
            max_pos = (self._range_max - self._min_value) / \
                (self._max_value - self._min_value)

            selected_left = track_rect.left() + total_width * min_pos
            selected_width = total_width * (max_pos - min_pos)

            # Draw selected area with enhanced gradient
            selected_rect = track_rect.adjusted(int(selected_left - track_rect.left()), 0,
                                                int(selected_left + selected_width - track_rect.right()), 0)

            gradient = QLinearGradient(
                selected_rect.topLeft(), selected_rect.topRight())
            primary_color = theme.get_color('primary')
            gradient.setColorAt(0, primary_color)
            gradient.setColorAt(0.5, primary_color.lighter(110))
            gradient.setColorAt(1, primary_color)

            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(selected_rect, 3, 3)

            # Draw thumbs with enhanced styling
            self._draw_thumb(painter, selected_left, rect.height() // 2,
                             self._dragging_min, theme)
            self._draw_thumb(painter, selected_left + selected_width, rect.height() // 2,
                             self._dragging_max, theme)

    def _draw_thumb(self, painter: QPainter, x: float, y: float,
                    is_pressed: bool, theme):
        """Draw thumb with enhanced styling"""
        radius = 12 if is_pressed else 10

        # Draw shadow
        shadow_color = theme.get_color('shadow')
        shadow_color.setAlpha(80)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(x - radius + 1), int(y - radius + 2),
                            (radius + 1) * 2, (radius + 1) * 2)

        # Draw thumb with gradient
        thumb_gradient = QLinearGradient(0, y - radius, 0, y + radius)
        thumb_gradient.setColorAt(0, theme.get_color('surface').lighter(110))
        thumb_gradient.setColorAt(1, theme.get_color('surface'))

        painter.setBrush(QBrush(thumb_gradient))
        painter.setPen(QPen(theme.get_color(
            'primary'), 3 if is_pressed else 2))
        painter.drawEllipse(int(x - radius), int(y - radius),
                            radius * 2, radius * 2)

        # Inner highlight
        highlight_color = theme.get_color('surface').lighter(120)
        highlight_color.setAlpha(150)
        painter.setBrush(QBrush(highlight_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(x - radius // 3), int(y - radius // 2),
                            radius // 2, radius // 3)

    def mousePressEvent(self, event):
        """Mouse press with enhanced feedback"""
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.position().x()

            # Check which thumb was clicked
            rect = self.rect()
            track_rect = rect.adjusted(20, 0, -20, 0)

            if self._max_value > self._min_value:
                total_width = track_rect.width()
                min_pos = track_rect.left() + total_width * (self._range_min -
                                                             self._min_value) / (self._max_value - self._min_value)
                max_pos = track_rect.left() + total_width * (self._range_max -
                                                             self._min_value) / (self._max_value - self._min_value)

                min_distance = abs(x - min_pos)
                max_distance = abs(x - max_pos)

                if min_distance < max_distance and min_distance < 20:
                    self._dragging_min = True
                    FluentMicroInteraction.button_press(self, scale=0.98)
                elif max_distance < 20:
                    self._dragging_max = True
                    FluentMicroInteraction.button_press(self, scale=0.98)

                self._last_mouse_x = x
                self.update()

    def mouseMoveEvent(self, event):
        """Mouse move with smooth updates"""
        if self._dragging_min or self._dragging_max:
            x = event.position().x()
            rect = self.rect()
            track_rect = rect.adjusted(20, 0, -20, 0)

            # Calculate new value
            if self._max_value > self._min_value:
                relative_pos = (x - track_rect.left()) / track_rect.width()
                new_value = self._min_value + relative_pos * \
                    (self._max_value - self._min_value)
                new_value = max(self._min_value, min(
                    new_value, self._max_value))

                if self._dragging_min:
                    self._range_min = min(new_value, self._range_max)
                elif self._dragging_max:
                    self._range_max = max(new_value, self._range_min)

                self.update()
                self.range_changed.emit(
                    int(self._range_min), int(self._range_max))

    def mouseReleaseEvent(self, _):
        """Mouse release with feedback"""
        if self._dragging_min or self._dragging_max:
            FluentMicroInteraction.pulse_animation(self, scale=1.02)

        self._dragging_min = False
        self._dragging_max = False
        self.update()

    def enterEvent(self, event):
        """Enhanced hover effect"""
        super().enterEvent(event)
        FluentMicroInteraction.hover_glow(self, intensity=0.05)


class FluentProgressIndicator(QWidget):
    """Enhanced progress indicator composite control"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI with enhanced styling"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Title and percentage
        header_layout = QHBoxLayout()

        self.title_label = QLabel("Progress")
        self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 600;
                color: {theme_manager.get_color('text_primary').name()};
                letter-spacing: 0.5px;
            }}
        """)

        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {theme_manager.get_color('text_secondary').name()};
                background-color: {theme_manager.get_color('surface_variant').name()};
                padding: 4px 8px;
                border-radius: 4px;
            }}
        """)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.percentage_label)

        # Progress bar with enhanced styling
        self.progress_bar = FluentProgressBar()

        layout.addLayout(header_layout)
        layout.addWidget(self.progress_bar)

        # Connect signals
        self.progress_bar.valueChanged.connect(self._update_percentage)

        # Initial reveal animation
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_MEDIUM)

    def set_title(self, title: str):
        """Set title with animation"""
        if self.title_label.text() != title:
            self.title_label.setText(title)
            FluentRevealEffect.fade_in(
                self.title_label, duration=FluentAnimation.DURATION_FAST)

    def set_value(self, value: int):
        """Set progress value with enhanced feedback"""
        old_value = self.progress_bar.value()
        self.progress_bar.set_value_animated(value)

        # Add celebratory animation when reaching 100%
        if value == 100 and old_value < 100:
            FluentMicroInteraction.pulse_animation(
                self.percentage_label, scale=1.2)

    def set_indeterminate(self, indeterminate: bool):
        """Set indeterminate state with enhanced feedback"""
        self.progress_bar.set_indeterminate(indeterminate)

        if indeterminate:
            self.percentage_label.setText("Processing...")
            FluentRevealEffect.fade_in(
                self.percentage_label, duration=FluentAnimation.DURATION_FAST)
        else:
            self._update_percentage(self.progress_bar.value())

    def _update_percentage(self, value: int):
        """Update percentage display with animation"""
        if not self.progress_bar._is_indeterminate:
            percentage = value * 100 // self.progress_bar.maximum()
            new_text = f"{percentage}%"

            if self.percentage_label.text() != new_text:
                self.percentage_label.setText(new_text)
                FluentMicroInteraction.scale_animation(
                    self.percentage_label, scale=1.1)
