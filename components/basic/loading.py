"""
Fluent Design Loading Components

Implements various loading indicators with smooth animations.
Based on Windows 11 Fluent Design principles.
"""

from typing import Optional
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, QTimer, QRect, Property, QEasingCurve, QParallelAnimationGroup, QByteArray, Signal, QPoint
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QConicalGradient

from core.theme import theme_manager


class FluentSpinner(QWidget):
    """
    圆形旋转加载指示器
    """
    angleChanged = Signal()

    def __init__(self,
                 size: int = 32,
                 line_width: int = 3,
                 color: Optional[QColor] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._size = size
        self._line_width = line_width
        self._color = color
        self._angle = 0
        self._running = False

        self.setFixedSize(size, size)
        self._setup_animation()
        self._connect_theme()

    def _setup_animation(self):
        """设置动画"""
        self._rotation_animation = QPropertyAnimation(
            self, QByteArray(b"angle"))
        self._rotation_animation.setDuration(1200)
        self._rotation_animation.setStartValue(0)
        self._rotation_animation.setEndValue(360)
        self._rotation_animation.setLoopCount(-1)  # 无限循环
        self._rotation_animation.setEasingCurve(QEasingCurve.Type.Linear)

    def _connect_theme(self):
        """连接主题"""
        if theme_manager:
            theme_manager.theme_changed.connect(self.update)

    def getAngle(self):
        return self._angle

    def setAngle(self, value):
        new_angle = value % 360
        if self._angle != new_angle:
            self._angle = new_angle
            self.angleChanged.emit()
        self.update()

    angle = Property(int, getAngle, setAngle, None, "", notify=angleChanged)

    def start(self):
        """开始旋转"""
        if not self._running:
            self._running = True
            self._rotation_animation.start()

    def stop(self):
        """停止旋转"""
        if self._running:
            self._running = False
            self._rotation_animation.stop()

    def isRunning(self) -> bool:
        """是否正在运行"""
        return self._running

    def setSize(self, size: int):
        """设置尺寸"""
        self._size = size
        self.setFixedSize(size, size)
        self.update()

    def setLineWidth(self, width: int):
        """设置线宽"""
        self._line_width = width
        self.update()

    def setColor(self, color: QColor):
        """设置颜色"""
        self._color = color
        self.update()

    def paintEvent(self, _):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 获取颜色
        current_color = self._color if self._color else theme_manager.get_color(
            'accent')

        # 创建渐变
        gradient = QConicalGradient(
            self._size / 2, self._size / 2, self._angle)
        gradient.setColorAt(0.0, QColor(current_color.red(),
                            current_color.green(), current_color.blue(), 0))
        gradient.setColorAt(0.7, QColor(current_color.red(),
                            current_color.green(), current_color.blue(), 180))
        gradient.setColorAt(1.0, current_color)

        # 绘制圆弧
        painter.setPen(QPen(QBrush(gradient), self._line_width,
                       Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

        rect = QRect(self._line_width // 2, self._line_width // 2,
                     self._size - self._line_width, self._size - self._line_width)
        painter.drawArc(rect, 0, 270 * 16)  # 270度圆弧


class FluentDotLoader(QWidget):
    """
    点状加载指示器
    """

    def __init__(self,
                 dot_count: int = 3,
                 dot_size: int = 8,
                 spacing: int = 4,
                 color: Optional[QColor] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._dot_count = dot_count
        self._dot_size = dot_size
        self._spacing = spacing
        self._color = color
        self._current_dot = 0
        self._running = False

        # 计算尺寸
        width = dot_count * dot_size + (dot_count - 1) * spacing
        self.setFixedSize(width, dot_size)

        self._setup_animation()
        self._connect_theme()

    def _setup_animation(self):
        """设置动画"""
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate_next)
        self._timer.setInterval(300)

    def _connect_theme(self):
        """连接主题"""
        if theme_manager:
            theme_manager.theme_changed.connect(self.update)

    def start(self):
        """开始动画"""
        if not self._running:
            self._running = True
            self._timer.start()

    def stop(self):
        """停止动画"""
        if self._running:
            self._running = False
            self._timer.stop()

    def isRunning(self) -> bool:
        """是否正在运行"""
        return self._running

    def _animate_next(self):
        """动画到下一个点"""
        self._current_dot = (self._current_dot + 1) % self._dot_count
        self.update()

    def paintEvent(self, _):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 获取颜色
        current_color = self._color if self._color else theme_manager.get_color(
            'accent')

        # 绘制点
        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(self._dot_count):
            x = i * (self._dot_size + self._spacing)
            y = 0

            # 当前活动点使用完整透明度，其他点使用较低透明度
            if i == self._current_dot:
                dot_color = current_color
            else:
                dot_color = QColor(
                    current_color.red(), current_color.green(), current_color.blue(), 80)

            painter.setBrush(QBrush(dot_color))
            painter.drawEllipse(x, y, self._dot_size, self._dot_size)


class FluentProgressRing(QWidget):
    """
    环形进度指示器
    """
    angleChanged = Signal()
    valueChanged = Signal(float)
    indeterminateChanged = Signal(bool)

    def __init__(self,
                 size: int = 48,
                 line_width: int = 4,
                 indeterminate: bool = False,
                 value: float = 0.0,
                 color: Optional[QColor] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._size = size
        self._line_width = line_width
        self._indeterminate = indeterminate
        self._value = max(0.0, min(1.0, value))
        self._color = color
        self._angle = 0
        self._running = False

        self.setFixedSize(size, size)
        self._setup_animation()
        self._connect_theme()

    def _setup_animation(self):
        """设置动画"""
        self._rotation_animation = QPropertyAnimation(
            self, QByteArray(b"angle"))
        self._rotation_animation.setDuration(2000)
        self._rotation_animation.setStartValue(0)
        self._rotation_animation.setEndValue(360)
        self._rotation_animation.setLoopCount(-1)
        self._rotation_animation.setEasingCurve(QEasingCurve.Type.Linear)

    def _connect_theme(self):
        """连接主题"""
        if theme_manager:
            theme_manager.theme_changed.connect(self.update)

    def getAngle(self):
        return self._angle

    def setAngle(self, value):
        new_angle = value % 360
        if self._angle != new_angle:
            self._angle = new_angle
            self.angleChanged.emit()
        self.update()

    angle = Property(int, getAngle, setAngle, None, "", notify=angleChanged)

    def start(self):
        """开始动画（仅不确定模式）"""
        if self._indeterminate and not self._running:
            self._running = True
            self._rotation_animation.start()

    def stop(self):
        """停止动画"""
        if self._running:
            self._running = False
            self._rotation_animation.stop()

    def setValue(self, value: float):
        """设置进度值（0.0-1.0）"""
        new_value = max(0.0, min(1.0, value))
        if self._value != new_value:
            self._value = new_value
            self.valueChanged.emit(self._value)
        self.update()

    def value(self) -> float:
        """获取进度值"""
        return self._value

    def setIndeterminate(self, indeterminate: bool):
        """设置不确定模式"""
        if self._indeterminate != indeterminate:
            self._indeterminate = indeterminate
            self.indeterminateChanged.emit(self._indeterminate)
            if indeterminate:
                self.start()
            else:
                self.stop()
            self.update()

    def isIndeterminate(self) -> bool:
        """是否为不确定模式"""
        return self._indeterminate

    def paintEvent(self, _):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 获取颜色
        current_color = self._color if self._color else theme_manager.get_color(
            'accent')

        # 背景圆环
        bg_color = theme_manager.get_color('border')
        painter.setPen(QPen(bg_color, self._line_width,
                       Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

        rect = QRect(self._line_width // 2, self._line_width // 2,
                     self._size - self._line_width, self._size - self._line_width)
        painter.drawEllipse(rect)

        # 进度圆弧
        if self._indeterminate:
            # 不确定模式：旋转的部分圆弧
            gradient = QConicalGradient(
                self._size / 2, self._size / 2, self._angle)
            gradient.setColorAt(0.0, QColor(
                current_color.red(), current_color.green(), current_color.blue(), 0))
            gradient.setColorAt(0.8, current_color)
            gradient.setColorAt(1.0, QColor(
                current_color.red(), current_color.green(), current_color.blue(), 0))

            painter.setPen(QPen(QBrush(gradient), self._line_width,
                           Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(rect, 0, 120 * 16)  # 120度圆弧
        else:
            # 确定模式：显示具体进度
            painter.setPen(QPen(current_color, self._line_width,
                           Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            span_angle = int(360 * self._value * 16)
            painter.drawArc(rect, 90 * 16, -span_angle)  # 从顶部开始


class FluentLoadingOverlay(QWidget):
    """
    加载遮罩层
    """

    def __init__(self,
                 parent: Optional[QWidget] = None,
                 text: str = "加载中...",
                 spinner_size: int = 48):
        super().__init__(parent)

        self._text = text
        self._spinner_size = spinner_size

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._setup_ui()
        self._connect_theme()

        if parent:
            if isinstance(parent, QWidget):
                self.resize(parent.size())
            parent.installEventFilter(self)

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # 加载指示器
        self._spinner = FluentSpinner(self._spinner_size, parent=self)
        layout.addWidget(self._spinner, 0, Qt.AlignmentFlag.AlignCenter)

        # 文本标签
        if self._text:
            self._label = QLabel(self._text, self)
            self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self._label)

    def _connect_theme(self):
        """连接主题"""
        if theme_manager:
            theme_manager.theme_changed.connect(self._update_style)
        self._update_style()  # Initial style update

    def _update_style(self):
        """更新样式"""
        if hasattr(self, '_label') and self._label and theme_manager:
            text_color = theme_manager.get_color('text_primary')
            self._label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color.name()};
                    font-size: 14px;
                    font-weight: 500;
                }}
            """)
        self.update()  # Ensure paintEvent is called to update background

    def show(self):
        """显示遮罩层"""
        parent_widget = self.parent()
        if isinstance(parent_widget, QWidget):
            self.resize(parent_widget.size())
            self.move(parent_widget.mapToGlobal(QPoint(0, 0)))
        super().show()
        self._spinner.start()

    def hide(self):
        """隐藏遮罩层"""
        self._spinner.stop()
        super().hide()

    def setText(self, text: str):
        """设置文本"""
        self._text = text
        if hasattr(self, '_label') and self._label:
            self._label.setText(text)

    def eventFilter(self, watched_obj, event):
        """事件过滤器"""
        parent_widget = self.parentWidget()  # QWidget or None
        if watched_obj == parent_widget and parent_widget is not None:
            if event.type() == event.Type.Resize:
                self.resize(parent_widget.size())
            elif event.type() == event.Type.Move:
                self.move(parent_widget.mapToGlobal(QPoint(0, 0)))
        return super().eventFilter(watched_obj, event)

    def paintEvent(self, _):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 半透明背景
        if theme_manager:
            # Determine background color based on theme's main background lightness
            # Assuming 'background' is a color defined in the theme
            main_background_color = theme_manager.get_color('background')
            is_dark_theme = main_background_color.lightnessF() < 0.5  # lightnessF is 0.0-1.0

            if is_dark_theme:
                bg_color = QColor(0, 0, 0, 120)  # Dark overlay for dark themes
            else:
                # Light overlay for light themes
                bg_color = QColor(255, 255, 255, 200)
        else:
            # Fallback if theme_manager is not available
            bg_color = QColor(255, 255, 255, 200)

        painter.fillRect(self.rect(), bg_color)


class FluentPulseLoader(QWidget):
    """
    脉冲加载指示器
    """
    scaleValueChanged = Signal(float)
    opacityValueChanged = Signal(float)

    def __init__(self,
                 size: int = 40,
                 color: Optional[QColor] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._size = size
        self._color = color
        self._scale = 0.8
        self._opacity = 1.0
        self._running = False

        self.setFixedSize(size, size)
        self._setup_animation()
        self._connect_theme()

    def _setup_animation(self):
        """设置动画"""
        self._scale_animation = QPropertyAnimation(
            self, QByteArray(b"scaleValue"))
        self._scale_animation.setDuration(1000)
        self._scale_animation.setStartValue(0.8)
        self._scale_animation.setEndValue(1.2)
        self._scale_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._opacity_animation = QPropertyAnimation(
            self, QByteArray(b"opacityValue"))
        self._opacity_animation.setDuration(1000)
        self._opacity_animation.setStartValue(1.0)
        self._opacity_animation.setEndValue(0.3)
        self._opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # 创建平行动画组
        self._animation_group = QParallelAnimationGroup(self)
        self._animation_group.addAnimation(self._scale_animation)
        self._animation_group.addAnimation(self._opacity_animation)
        self._animation_group.setLoopCount(-1)

    def _connect_theme(self):
        """连接主题"""
        if theme_manager:
            theme_manager.theme_changed.connect(self.update)

    def getScaleValue(self):
        return self._scale

    def setScaleValue(self, value):
        if self._scale != value:
            self._scale = value
            self.scaleValueChanged.emit(self._scale)
        self.update()

    scaleValue = Property(float, getScaleValue, setScaleValue,
                          None, "", notify=scaleValueChanged)

    def getOpacityValue(self):
        return self._opacity

    def setOpacityValue(self, value):
        if self._opacity != value:
            self._opacity = value
            self.opacityValueChanged.emit(self._opacity)
        self.update()

    opacityValue = Property(
        float, getOpacityValue, setOpacityValue, None, "", notify=opacityValueChanged)

    def start(self):
        """开始动画"""
        if not self._running:
            self._running = True
            self._animation_group.start()

    def stop(self):
        """停止动画"""
        if self._running:
            self._running = False
            self._animation_group.stop()

    def paintEvent(self, _):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 获取颜色
        current_color = self._color if self._color else theme_manager.get_color(
            'accent')

        # 应用透明度
        paint_color = QColor(current_color)  # Create a copy to modify alpha
        paint_color.setAlphaF(self._opacity)

        # 计算缩放后的尺寸
        scaled_size = int(self._size * self._scale)
        x = (self._size - scaled_size) // 2
        y = (self._size - scaled_size) // 2

        # 绘制圆形
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(paint_color))
        painter.drawEllipse(x, y, scaled_size, scaled_size)
