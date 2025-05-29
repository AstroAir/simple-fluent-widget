"""
Fluent Design Loading Components

Implements various loading indicators with smooth animations.
Based on Windows 11 Fluent Design principles.
"""

from typing import Optional
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import (Qt, QPropertyAnimation, QRect, Property, QEasingCurve,
                            QParallelAnimationGroup, QByteArray, Signal, QPoint)
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QConicalGradient, QPaintEvent

from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import FluentTransition, FluentRevealEffect


class FluentSpinner(QWidget):
    """
    Circular spinning loading indicator.
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
        """Set up animation."""
        self._rotation_animation = QPropertyAnimation(
            self, QByteArray(b"angle"))
        self._rotation_animation.setDuration(1200)
        self._rotation_animation.setStartValue(0)
        self._rotation_animation.setEndValue(360)
        self._rotation_animation.setLoopCount(-1)  # Infinite loop
        self._rotation_animation.setEasingCurve(QEasingCurve.Type.Linear)

    def _connect_theme(self):
        """Connect to theme changes."""
        if theme_manager:
            theme_manager.theme_changed.connect(self.update)

    def getAngle(self) -> int:
        return self._angle

    def setAngle(self, value: int):
        new_angle = value % 360
        if self._angle != new_angle:
            self._angle = new_angle
            self.angleChanged.emit()
            self.update()

    angle = Property(int, getAngle, setAngle, None, "", notify=angleChanged)

    def start(self):
        """Start spinning."""
        if not self._running:
            self._running = True
            self._rotation_animation.start()

    def stop(self):
        """Stop spinning."""
        if self._running:
            self._running = False
            self._rotation_animation.stop()

    def isRunning(self) -> bool:
        """Check if running."""
        return self._running

    def setSize(self, size: int):
        """Set indicator size."""
        self._size = size
        self.setFixedSize(size, size)
        self.update()

    def setLineWidth(self, width: int):
        """Set line width."""
        self._line_width = width
        self.update()

    def setColor(self, color: QColor):
        """Set indicator color."""
        self._color = color
        self.update()

    def paintEvent(self, _event: QPaintEvent):
        """Paint the spinner."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        current_color = self._color if self._color else theme_manager.get_color(
            'accent')

        gradient = QConicalGradient(
            self._size / 2, self._size / 2, self._angle)
        gradient.setColorAt(0.0, QColor(current_color.red(),
                            current_color.green(), current_color.blue(), 0))
        gradient.setColorAt(0.7, QColor(current_color.red(),
                            current_color.green(), current_color.blue(), 180))
        gradient.setColorAt(1.0, current_color)

        painter.setPen(QPen(QBrush(gradient), self._line_width,
                       Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

        rect = QRect(self._line_width // 2, self._line_width // 2,
                     self._size - self._line_width, self._size - self._line_width)
        painter.drawArc(rect, 0, 270 * 16)  # 270 degree arc


class FluentDotLoader(QWidget):
    """
    Dot-style loading indicator with a traveling highlight.
    """
    phaseChanged = Signal()

    def __init__(self,
                 dot_count: int = 3,
                 dot_size: int = 8,
                 spacing: int = 4,
                 color: Optional[QColor] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._dot_count = max(1, dot_count)
        self._dot_size = dot_size
        self._spacing = spacing
        self._color = color
        self._phase = 0.0
        self._running = False

        width = self._dot_count * self._dot_size + \
            (self._dot_count - 1) * self._spacing
        self.setFixedSize(width, self._dot_size)

        self._setup_animation()
        self._connect_theme()

    def _setup_animation(self):
        """Set up animation."""
        self._phase_animation = QPropertyAnimation(self, QByteArray(b"phase"))
        self._phase_animation.setDuration(
            self._dot_count * 400)  # Adjust speed as needed
        self._phase_animation.setStartValue(0.0)
        self._phase_animation.setEndValue(float(self._dot_count))
        self._phase_animation.setLoopCount(-1)
        self._phase_animation.setEasingCurve(QEasingCurve.Type.Linear)

    def _connect_theme(self):
        """Connect to theme changes."""
        if theme_manager:
            theme_manager.theme_changed.connect(self.update)

    def getPhase(self) -> float:
        return self._phase

    def setPhase(self, value: float):
        if self._phase != value:
            self._phase = value
            self.phaseChanged.emit()
            self.update()

    phase = Property(float, getPhase, setPhase, None, "", notify=phaseChanged)

    def start(self):
        """Start animation."""
        if not self._running:
            self._running = True
            self._phase_animation.start()

    def stop(self):
        """Stop animation."""
        if self._running:
            self._running = False
            self._phase_animation.stop()

    def isRunning(self) -> bool:
        """Check if running."""
        return self._running

    def paintEvent(self, _event: QPaintEvent):
        """Paint the dots."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        current_color = self._color if self._color else theme_manager.get_color(
            'accent')
        painter.setPen(Qt.PenStyle.NoPen)

        # SPREAD determines how many dots are affected by the "highlight"
        # A smaller SPREAD means a sharper highlight.
        SPREAD = 1.0
        MIN_OPACITY = 70  # out of 255
        MAX_OPACITY = 255

        current_highlight_pos = self._phase % self._dot_count

        for i in range(self._dot_count):
            x = i * (self._dot_size + self._spacing)
            y = 0  # (self.height() - self._dot_size) / 2 # Center vertically

            # Calculate distance from current dot to the highlight position
            # This handles wrap-around for a circular effect.
            diff = abs(current_highlight_pos - i)
            distance = min(diff, self._dot_count - diff)

            # Calculate opacity based on distance
            # The further the dot, the lower the opacity
            opacity_factor = max(0.0, 1.0 - distance / SPREAD)
            opacity = MIN_OPACITY + \
                (MAX_OPACITY - MIN_OPACITY) * opacity_factor
            opacity = int(max(MIN_OPACITY, min(MAX_OPACITY, opacity)))

            dot_color = QColor(
                current_color.red(), current_color.green(), current_color.blue(), opacity)
            painter.setBrush(QBrush(dot_color))
            painter.drawEllipse(x, y, self._dot_size, self._dot_size)


class FluentProgressRing(QWidget):
    """
    Ring-style progress indicator.
    Supports determinate and indeterminate modes.
    """
    angleChanged = Signal()
    progressValueChanged = Signal(float)  # Renamed from valueChanged
    indeterminateChanged = Signal(bool)

    def __init__(self,
                 size: int = 48,
                 line_width: int = 4,
                 indeterminate: bool = False,
                 value: float = 0.0,  # Renamed to initial_value for clarity
                 color: Optional[QColor] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._size = size
        self._line_width = line_width
        self._indeterminate = indeterminate
        self._progress_value = max(0.0, min(1.0, value))
        self._color = color
        self._angle = 0
        self._running = False  # For indeterminate animation

        self._value_animation: Optional[QPropertyAnimation] = None

        self.setFixedSize(size, size)
        self._setup_animation()
        self._connect_theme()

        if self._indeterminate:
            self.start()

    def _setup_animation(self):
        """Set up animations."""
        self._rotation_animation = QPropertyAnimation(
            self, QByteArray(b"angle"))
        self._rotation_animation.setDuration(2000)
        self._rotation_animation.setStartValue(0)
        self._rotation_animation.setEndValue(360)
        self._rotation_animation.setLoopCount(-1)
        self._rotation_animation.setEasingCurve(QEasingCurve.Type.Linear)

    def _connect_theme(self):
        """Connect to theme changes."""
        if theme_manager:
            theme_manager.theme_changed.connect(self.update)

    def getAngle(self) -> int:
        return self._angle

    def setAngle(self, value: int):
        new_angle = value % 360
        if self._angle != new_angle:
            self._angle = new_angle
            self.angleChanged.emit()
            self.update()

    angle = Property(int, getAngle, setAngle, None, "", notify=angleChanged)

    def getProgressValue(self) -> float:
        return self._progress_value

    def setProgressValue(self, value: float):
        new_value = max(0.0, min(1.0, value))
        if self._progress_value != new_value:
            self._progress_value = new_value
            self.progressValueChanged.emit(self._progress_value)
            self.update()

    progressValue = Property(
        float, getProgressValue, setProgressValue, None, "", notify=progressValueChanged)

    def start(self):
        """Start animation (for indeterminate mode)."""
        if self._indeterminate and not self._running:
            self._running = True
            self._rotation_animation.start()

    def stop(self):
        """Stop animation (for indeterminate mode)."""
        if self._running:
            self._running = False
            self._rotation_animation.stop()

    def setValue(self, value: float, animate: bool = True):
        """Set progress value (0.0-1.0)."""
        new_value = max(0.0, min(1.0, value))
        if self.isIndeterminate():
            self.setIndeterminate(False)  # Switch to determinate mode

        if self._value_animation and self._value_animation.state() == QPropertyAnimation.State.Running:
            self._value_animation.stop()

        if animate and self.getProgressValue() != new_value:
            self._value_animation = QPropertyAnimation(
                self, QByteArray(b"progressValue"))
            self._value_animation.setDuration(FluentAnimation.DURATION_FAST)
            self._value_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
            self._value_animation.setStartValue(self.getProgressValue())
            self._value_animation.setEndValue(new_value)
            self._value_animation.start(
                QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        else:
            self.setProgressValue(new_value)

    def value(self) -> float:
        """Get current progress value."""
        return self.getProgressValue()

    def setIndeterminate(self, indeterminate: bool):
        """Set indeterminate mode."""
        if self._indeterminate != indeterminate:
            self._indeterminate = indeterminate
            self.indeterminateChanged.emit(self._indeterminate)
            if indeterminate:
                self.start()
            else:
                self.stop()
            self.update()

    def isIndeterminate(self) -> bool:
        """Check if in indeterminate mode."""
        return self._indeterminate

    def paintEvent(self, _event: QPaintEvent):
        """Paint the progress ring."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        current_color = self._color if self._color else theme_manager.get_color(
            'accent')
        bg_color = theme_manager.get_color('border')

        painter.setPen(QPen(bg_color, self._line_width,
                       Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))  # Changed to FlatCap for cleaner look

        rect = QRect(self._line_width // 2, self._line_width // 2,
                     self._size - self._line_width, self._size - self._line_width)
        painter.drawEllipse(rect)

        if self._indeterminate:
            gradient = QConicalGradient(
                self._size / 2, self._size / 2, self._angle)
            gradient.setColorAt(0.0, QColor(
                current_color.red(), current_color.green(), current_color.blue(), 0))
            gradient.setColorAt(0.8, current_color)
            gradient.setColorAt(1.0, QColor(
                current_color.red(), current_color.green(), current_color.blue(), 0))

            painter.setPen(QPen(QBrush(gradient), self._line_width,
                           Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(rect, 0, 120 * 16)  # 120 degree arc
        else:
            painter.setPen(QPen(current_color, self._line_width,
                           Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            span_angle = int(360 * self.getProgressValue() * 16)
            painter.drawArc(rect, 90 * 16, -span_angle)  # Start from top


class FluentLoadingOverlay(QWidget):
    """
    Loading overlay with a spinner and optional text.
    """

    def __init__(self,
                 parent: Optional[QWidget] = None,
                 text: str = "Loading...",
                 spinner_size: int = 48):
        super().__init__(parent)

        self._text = text
        self._spinner_size = spinner_size

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(0.0)  # Start fully transparent

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._setup_ui()
        self._connect_theme()

        if parent and isinstance(parent, QWidget):
            self.resize(parent.size())
            parent.installEventFilter(self)

    def _setup_ui(self):
        """Set up UI elements."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        self._spinner = FluentSpinner(self._spinner_size, parent=self)
        layout.addWidget(self._spinner, 0, Qt.AlignmentFlag.AlignCenter)

        if self._text:
            self._label = QLabel(self._text, self)
            self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self._label)

    def _connect_theme(self):
        """Connect to theme changes."""
        if theme_manager:
            theme_manager.theme_changed.connect(self._update_style)
        self._update_style()

    def _update_style(self):
        """Update styles based on theme."""
        if hasattr(self, '_label') and self._label and theme_manager:
            text_color = theme_manager.get_color('text_primary')
            self._label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color.name()};
                    font-size: 14px;
                    font-weight: 500;
                }}
            """)
        self.update()

    def show(self):
        """Show the overlay with a fade-in animation."""
        parent_widget = self.parent()
        if isinstance(parent_widget, QWidget):
            self.resize(parent_widget.size())
            self.move(parent_widget.mapToGlobal(QPoint(0, 0)))

        super().show()  # Show the widget first
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_FAST)
        self._spinner.start()

    def hide(self):
        """Hide the overlay with a fade-out animation."""
        self._spinner.stop()

        fade_out_anim = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        fade_out_anim.setDuration(FluentAnimation.DURATION_FAST)
        fade_out_anim.setStartValue(self._opacity_effect.opacity())
        fade_out_anim.setEndValue(0.0)
        fade_out_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        fade_out_anim.finished.connect(super().hide)  # Hide after animation
        fade_out_anim.start(
            QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def setText(self, text: str):
        """Set the loading text."""
        self._text = text
        if hasattr(self, '_label') and self._label:
            self._label.setText(text)

    def eventFilter(self, watched_obj, event):
        """Filter events from parent to resize/reposition overlay."""
        parent_widget = self.parentWidget()
        if watched_obj == parent_widget and parent_widget is not None:
            if event.type() == event.Type.Resize:
                self.resize(parent_widget.size())
            elif event.type() == event.Type.Move:
                if self.isVisible():  # Only move if visible
                    self.move(parent_widget.mapToGlobal(QPoint(0, 0)))
        return super().eventFilter(watched_obj, event)

    def paintEvent(self, _event: QPaintEvent):
        """Paint the semi-transparent background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if theme_manager:
            main_background_color = theme_manager.get_color('background')
            is_dark_theme = main_background_color.lightnessF() < 0.5
            bg_color = QColor(0, 0, 0, 120) if is_dark_theme else QColor(
                255, 255, 255, 200)
        else:
            bg_color = QColor(255, 255, 255, 200)  # Default light overlay

        painter.fillRect(self.rect(), bg_color)


class FluentPulseLoader(QWidget):
    """
    Pulsing dot loading indicator.
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
        """Set up pulsing animation."""
        self._scale_animation = QPropertyAnimation(
            self, QByteArray(b"scaleValue"))
        self._scale_animation.setDuration(1000)
        self._scale_animation.setStartValue(0.8)
        self._scale_animation.setEndValue(1.2)
        # FluentTransition.EASE_SMOOTH is OutCubic, InOutQuad is good for pulse
        self._scale_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._opacity_animation = QPropertyAnimation(
            self, QByteArray(b"opacityValue"))
        self._opacity_animation.setDuration(1000)
        self._opacity_animation.setStartValue(1.0)
        self._opacity_animation.setEndValue(0.3)
        self._opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._animation_group = QParallelAnimationGroup(self)
        self._animation_group.addAnimation(self._scale_animation)
        self._animation_group.addAnimation(self._opacity_animation)
        self._animation_group.setLoopCount(-1)

    def _connect_theme(self):
        """Connect to theme changes."""
        if theme_manager:
            theme_manager.theme_changed.connect(self.update)

    def getScaleValue(self) -> float:
        return self._scale

    def setScaleValue(self, value: float):
        if self._scale != value:
            self._scale = value
            self.scaleValueChanged.emit(self._scale)
            self.update()

    scaleValue = Property(float, getScaleValue, setScaleValue,
                          None, "", notify=scaleValueChanged)

    def getOpacityValue(self) -> float:
        return self._opacity

    def setOpacityValue(self, value: float):
        if self._opacity != value:
            self._opacity = value
            self.opacityValueChanged.emit(self._opacity)
            self.update()

    opacityValue = Property(
        float, getOpacityValue, setOpacityValue, None, "", notify=opacityValueChanged)

    def start(self):
        """Start pulsing animation."""
        if not self._running:
            self._running = True
            self._animation_group.start()

    def stop(self):
        """Stop pulsing animation."""
        if self._running:
            self._running = False
            self._animation_group.stop()

    def paintEvent(self, _event: QPaintEvent):
        """Paint the pulsing dot."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        current_color = self._color if self._color else theme_manager.get_color(
            'accent')

        paint_color = QColor(current_color)
        paint_color.setAlphaF(self._opacity)

        scaled_size = int(self._size * self._scale)
        x = (self._size - scaled_size) // 2
        y = (self._size - scaled_size) // 2

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(paint_color))
        painter.drawEllipse(x, y, scaled_size, scaled_size)
