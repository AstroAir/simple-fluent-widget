"""
Fluent Design style progress bars and slider components
"""

from PySide6.QtWidgets import QProgressBar, QSlider, QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, Property, QByteArray
from PySide6.QtGui import QPainter, QBrush, QPen, QLinearGradient, QPaintEvent
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional


class FluentProgressBar(QProgressBar):
    """Fluent Design style progress bar"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._is_indeterminate = False
        self._animation_position = 0.0
        self._progress_animation = None
        self._indeterminate_animation = None

        self.setMinimumHeight(6)
        self.setMaximumHeight(6)
        self.setTextVisible(False)

        self._setup_style()
        self._setup_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background-color: {theme.get_color('border').name()};
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme.get_color('primary').name()},
                    stop:1 {theme.get_color('primary').lighter(120).name()});
                border-radius: 3px;
                margin: 0px;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup animations"""
        # Progress value change animation
        self._progress_animation = QPropertyAnimation(self, QByteArray(b"value"))
        self._progress_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._progress_animation.setEasingCurve(FluentAnimation.EASE_OUT)

        # Indeterminate state animation
        self._indeterminate_animation = QPropertyAnimation(
            self, QByteArray(b"animationPosition"))
        self._indeterminate_animation.setDuration(2000)
        self._indeterminate_animation.setLoopCount(-1)  # Infinite loop
        self._indeterminate_animation.valueChanged.connect(self.update)

    def _get_animation_position(self):
        """Get animation position"""
        return self._animation_position

    def _set_animation_position(self, value):
        """Set animation position"""
        self._animation_position = value
        self.update()

    # 修复 Property 装饰器语法
    animationPosition = Property(float, _get_animation_position, _set_animation_position)

    def set_value_animated(self, value: int):
        """Set progress value with animation"""
        if self._progress_animation:
            self._progress_animation.setStartValue(self.value())
            self._progress_animation.setEndValue(value)
            self._progress_animation.start()

    def set_indeterminate(self, indeterminate: bool):
        """Set indeterminate state"""
        self._is_indeterminate = indeterminate

        if indeterminate:
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
        """Custom paint"""
        if self._is_indeterminate:
            self._paint_indeterminate(event)
        else:
            super().paintEvent(event)

    def _paint_indeterminate(self, _):
        """Paint indeterminate state progress bar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        theme = theme_manager

        # Draw background
        painter.setBrush(QBrush(theme.get_color('border')))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 3, 3)

        # Draw moving progress chunk
        chunk_width = rect.width() * 0.3
        chunk_x = (rect.width() - chunk_width) * self._animation_position

        chunk_rect = rect.adjusted(
            int(chunk_x), 0, int(chunk_x - rect.width() + chunk_width), 0)

        # Create gradient
        gradient = QLinearGradient(chunk_rect.topLeft(), chunk_rect.topRight())
        gradient.setColorAt(0, theme.get_color('primary'))
        gradient.setColorAt(1, theme.get_color('primary').lighter(120))

        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(chunk_rect, 3, 3)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentProgressRing(QWidget):
    """Fluent Design style circular progress ring"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._value = 0
        self._maximum = 100
        self._is_indeterminate = False
        self._rotation_angle = 0
        self._ring_animation = None

        self.setFixedSize(40, 40)

        self._setup_animations()
        theme_manager.theme_changed.connect(self.update)

    def _setup_animations(self):
        """Setup animations"""
        self._ring_animation = QPropertyAnimation(self, QByteArray(b"rotationAngle"))
        self._ring_animation.setDuration(2000)
        self._ring_animation.setLoopCount(-1)
        self._ring_animation.valueChanged.connect(self.update)

    def _get_rotation_angle(self):
        """Get rotation angle"""
        return self._rotation_angle

    def _set_rotation_angle(self, angle):
        """Set rotation angle"""
        self._rotation_angle = angle
        self.update()

    # 修复 Property 装饰器语法
    rotationAngle = Property(float, _get_rotation_angle, _set_rotation_angle)

    def set_value(self, value: int):
        """Set progress value"""
        self._value = max(0, min(value, self._maximum))
        self.update()

    def set_maximum(self, maximum: int):
        """Set maximum value"""
        self._maximum = maximum
        self.update()

    def set_indeterminate(self, indeterminate: bool):
        """Set indeterminate state"""
        self._is_indeterminate = indeterminate

        if indeterminate:
            if self._ring_animation:
                self._ring_animation.setStartValue(0)
                self._ring_animation.setEndValue(360)
                self._ring_animation.start()
        else:
            if self._ring_animation:
                self._ring_animation.stop()
            self._rotation_angle = 0
            self.update()

    def paintEvent(self, _):
        """Paint progress ring"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(4, 4, -4, -4)
        theme = theme_manager

        # Draw background ring
        painter.setPen(QPen(theme.get_color('border'), 3, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect)

        # Draw progress ring
        if self._is_indeterminate:
            # Indeterminate state: rotating arc segment
            painter.setPen(QPen(theme.get_color('primary'), 3, Qt.PenStyle.SolidLine))
            painter.drawArc(rect, int((self._rotation_angle - 90) * 16), int(90 * 16))
        else:
            # Determinate state: draw arc segment based on progress value
            if self._maximum > 0:
                angle = 360 * self._value / self._maximum
                painter.setPen(QPen(theme.get_color('primary'), 3, Qt.PenStyle.SolidLine))
                painter.drawArc(rect, -90 * 16, int(-angle * 16))


class FluentSlider(QSlider):
    """Fluent Design style slider"""

    value_changing = Signal(int)  # Value change during dragging

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent: Optional[QWidget] = None):
        super().__init__(orientation, parent)

        self._is_dragging = False
        self._thumb_animation = None

        self.setMinimumHeight(32 if orientation == Qt.Orientation.Horizontal else 120)

        self._setup_style()
        self._setup_animations()

        # Connect signals
        self.sliderPressed.connect(self._on_slider_pressed)
        self.sliderReleased.connect(self._on_slider_released)
        self.sliderMoved.connect(self.value_changing.emit)

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        if self.orientation() == Qt.Orientation.Horizontal:
            style_sheet = f"""
                QSlider::groove:horizontal {{
                    border: none;
                    height: 4px;
                    background: {theme.get_color('border').name()};
                    border-radius: 2px;
                }}
                QSlider::handle:horizontal {{
                    background: {theme.get_color('surface').name()};
                    border: 2px solid {theme.get_color('primary').name()};
                    width: 16px;
                    margin: -7px 0;
                    border-radius: 8px;
                }}
                QSlider::handle:horizontal:hover {{
                    background: {theme.get_color('accent_light').name()};
                    border-width: 3px;
                    width: 18px;
                    margin: -8px 0;
                    border-radius: 9px;
                }}
                QSlider::handle:horizontal:pressed {{
                    background: {theme.get_color('primary').name()};
                    border-color: {theme.get_color('primary').darker(120).name()};
                }}
                QSlider::sub-page:horizontal {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {theme.get_color('primary').name()},
                        stop:1 {theme.get_color('primary').lighter(110).name()});
                    border-radius: 2px;
                }}
            """
        else:
            style_sheet = f"""
                QSlider::groove:vertical {{
                    border: none;
                    width: 4px;
                    background: {theme.get_color('border').name()};
                    border-radius: 2px;
                }}
                QSlider::handle:vertical {{
                    background: {theme.get_color('surface').name()};
                    border: 2px solid {theme.get_color('primary').name()};
                    height: 16px;
                    margin: 0 -7px;
                    border-radius: 8px;
                }}
                QSlider::handle:vertical:hover {{
                    background: {theme.get_color('accent_light').name()};
                    border-width: 3px;
                    height: 18px;
                    margin: 0 -8px;
                    border-radius: 9px;
                }}
                QSlider::sub-page:vertical {{
                    background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                        stop:0 {theme.get_color('primary').name()},
                        stop:1 {theme.get_color('primary').lighter(110).name()});
                    border-radius: 2px;
                }}
            """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup animations"""
        self._thumb_animation = QPropertyAnimation(self, QByteArray(b"geometry"))
        self._thumb_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._thumb_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def _on_slider_pressed(self):
        """Slider pressed"""
        self._is_dragging = True

    def _on_slider_released(self):
        """Slider released"""
        self._is_dragging = False

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentRangeSlider(QWidget):
    """Dual-end range slider"""

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

        self.setMinimumHeight(32)
        self.setMinimumWidth(200)

        theme_manager.theme_changed.connect(self.update)

    def set_range(self, minimum: int, maximum: int):
        """Set total range"""
        self._min_value = minimum
        self._max_value = maximum
        self.update()

    def set_values(self, range_min: int, range_max: int):
        """Set selected range"""
        self._range_min = max(self._min_value, min(range_min, self._max_value))
        self._range_max = max(self._min_value, min(range_max, self._max_value))

        if self._range_min > self._range_max:
            self._range_min, self._range_max = self._range_max, self._range_min

        self.update()
        self.range_changed.emit(self._range_min, self._range_max)

    def get_values(self) -> tuple:
        """Get selected range"""
        return self._range_min, self._range_max

    def paintEvent(self, _):
        """Paint range slider"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        theme = theme_manager

        # Calculate track area
        track_y = rect.height() // 2 - 2
        track_rect = rect.adjusted(16, track_y, -16, -track_y)

        # Draw background track
        painter.setBrush(QBrush(theme.get_color('border')))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(track_rect, 2, 2)

        # Calculate selected area
        if self._max_value > self._min_value:
            total_width = track_rect.width()
            min_pos = (self._range_min - self._min_value) / (self._max_value - self._min_value)
            max_pos = (self._range_max - self._min_value) / (self._max_value - self._min_value)

            selected_left = track_rect.left() + total_width * min_pos
            selected_width = total_width * (max_pos - min_pos)

            # Draw selected area
            selected_rect = track_rect.adjusted(int(selected_left - track_rect.left()), 0,
                                                int(selected_left + selected_width - track_rect.right()), 0)

            gradient = QLinearGradient(selected_rect.topLeft(), selected_rect.topRight())
            gradient.setColorAt(0, theme.get_color('primary'))
            gradient.setColorAt(1, theme.get_color('primary').lighter(110))

            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(selected_rect, 2, 2)

            # Draw thumbs
            self._draw_thumb(painter, selected_left, rect.height() // 2, self._dragging_min)
            self._draw_thumb(painter, selected_left + selected_width, rect.height() // 2, self._dragging_max)

    def _draw_thumb(self, painter: QPainter, x: float, y: float, is_pressed: bool):
        """Draw thumb"""
        theme = theme_manager

        radius = 9 if is_pressed else 8

        painter.setBrush(QBrush(theme.get_color('surface')))
        painter.setPen(QPen(theme.get_color('primary'), 2))

        painter.drawEllipse(int(x - radius), int(y - radius), radius * 2, radius * 2)

    def mousePressEvent(self, event):
        """Mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            x = event.position().x()

            # Check which thumb was clicked
            rect = self.rect()
            track_rect = rect.adjusted(16, 0, -16, 0)

            if self._max_value > self._min_value:
                total_width = track_rect.width()
                min_pos = track_rect.left() + total_width * (self._range_min - self._min_value) / (self._max_value - self._min_value)
                max_pos = track_rect.left() + total_width * (self._range_max - self._min_value) / (self._max_value - self._min_value)

                min_distance = abs(x - min_pos)
                max_distance = abs(x - max_pos)

                if min_distance < max_distance and min_distance < 16:
                    self._dragging_min = True
                elif max_distance < 16:
                    self._dragging_max = True

                self._last_mouse_x = x
                self.update()

    def mouseMoveEvent(self, event):
        """Mouse move"""
        if self._dragging_min or self._dragging_max:
            x = event.position().x()
            rect = self.rect()
            track_rect = rect.adjusted(16, 0, -16, 0)

            # Calculate new value
            if self._max_value > self._min_value:
                relative_pos = (x - track_rect.left()) / track_rect.width()
                new_value = self._min_value + relative_pos * (self._max_value - self._min_value)
                new_value = max(self._min_value, min(new_value, self._max_value))

                if self._dragging_min:
                    self._range_min = min(new_value, self._range_max)
                elif self._dragging_max:
                    self._range_max = max(new_value, self._range_min)

                self.update()
                self.range_changed.emit(int(self._range_min), int(self._range_max))

    def mouseReleaseEvent(self, _):
        """Mouse release"""
        self._dragging_min = False
        self._dragging_max = False
        self.update()


class FluentProgressIndicator(QWidget):
    """Progress indicator composite control"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # 标题和百分比
        header_layout = QHBoxLayout()

        self.title_label = QLabel("进度")
        self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {theme_manager.get_color('text_primary').name()};
            }}
        """)

        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {theme_manager.get_color('text_secondary').name()};
            }}
        """)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.percentage_label)

        # 进度条
        self.progress_bar = FluentProgressBar()

        layout.addLayout(header_layout)
        layout.addWidget(self.progress_bar)

        # 连接信号
        self.progress_bar.valueChanged.connect(self._update_percentage)

    def set_title(self, title: str):
        """**设置标题**"""
        self.title_label.setText(title)

    def set_value(self, value: int):
        """**设置进度值**"""
        self.progress_bar.set_value_animated(value)

    def set_indeterminate(self, indeterminate: bool):
        """**设置不确定状态**"""
        self.progress_bar.set_indeterminate(indeterminate)
        if indeterminate:
            self.percentage_label.setText("...")

    def _update_percentage(self, value: int):
        """更新百分比显示"""
        if not self.progress_bar._is_indeterminate:
            percentage = value * 100 // self.progress_bar.maximum()
            self.percentage_label.setText(f"{percentage}%")
