"""
Base Components for Fluent Widget System

Provides common functionality and patterns to reduce code duplication.
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QByteArray
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QMouseEvent

from .theme import theme_manager
from .animation import FluentAnimation, AnimationHelper


class FluentBaseWidget(QWidget):
    """Base widget class with common Fluent Design features"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._is_hovered = False
        self._is_pressed = False
        self._is_focused = False
        self._animations: Dict[str, QPropertyAnimation] = {}
        self._animation_helper = AnimationHelper(self)

        self._setup_base()
        self._connect_signals()

    def _setup_base(self):
        """Setup base widget properties"""
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def _connect_signals(self):
        """Connect theme manager signals"""
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self):
        """Handle theme change"""
        self.update()

    def _create_animation(self, name: str, target_property: str,
                          duration: int = FluentAnimation.DURATION_MEDIUM,
                          easing: QEasingCurve.Type = FluentAnimation.EASE_OUT) -> QPropertyAnimation:
        """Create and store an animation"""
        animation = QPropertyAnimation(
            self, QByteArray(target_property.encode()))
        animation.setDuration(duration)
        animation.setEasingCurve(easing)
        self._animations[name] = animation
        return animation

    def _start_animation(self, name: str, start_value: Any, end_value: Any):
        """Start a named animation"""
        if name in self._animations:
            animation = self._animations[name]
            animation.setStartValue(start_value)
            animation.setEndValue(end_value)
            animation.start()

    def _get_theme_color(self, color_name: str) -> QColor:
        """Get color from theme"""
        return theme_manager.get_color(color_name)

    def _apply_hover_effect(self, painter: QPainter, rect, base_color: QColor,
                            hover_intensity: float = 0.1):
        """Apply hover effect to a color"""
        if self._is_hovered:
            hover_color = base_color.lighter(int(100 + hover_intensity * 100))
            painter.setBrush(QBrush(hover_color))
        else:
            painter.setBrush(QBrush(base_color))

    def enterEvent(self, event):
        """Mouse enter event"""
        self._is_hovered = True
        self._animation_helper.add_breathing_effect()
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Mouse leave event"""
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)

    def focusInEvent(self, event):
        """Focus in event"""
        self._is_focused = True
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Focus out event"""
        self._is_focused = False
        self.update()
        super().focusOutEvent(event)


class FluentBaseButton(FluentBaseWidget):
    """Base button class with common button functionality"""

    clicked = Signal()

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._text = text
        self._enabled = True
        self._checkable = False
        self._checked = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)

        self._setup_button_animations()

    def _setup_button_animations(self):
        """Setup button-specific animations"""
        self._create_animation("scale", "geometry",
                               FluentAnimation.DURATION_FAST,
                               FluentAnimation.EASE_OUT_BACK)

    def setText(self, text: str):
        """Set button text"""
        self._text = text
        self.update()

    def text(self) -> str:
        """Get button text"""
        return self._text

    def setEnabled(self, enabled: bool):
        """Set enabled state"""
        self._enabled = enabled
        super().setEnabled(enabled)
        self.setCursor(Qt.CursorShape.PointingHandCursor if enabled
                       else Qt.CursorShape.ForbiddenCursor)
        self.update()

    def isEnabled(self) -> bool:
        """Check if button is enabled"""
        return self._enabled

    def setCheckable(self, checkable: bool):
        """Set if button is checkable"""
        self._checkable = checkable

    def isCheckable(self) -> bool:
        """Check if button is checkable"""
        return self._checkable

    def setChecked(self, checked: bool):
        """Set checked state"""
        if self._checkable:
            self._checked = checked
            self.update()

    def isChecked(self) -> bool:
        """Check if button is checked"""
        return self._checked

    def mousePressEvent(self, event: QMouseEvent):
        """Mouse press event"""
        if self._enabled and event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self._animation_helper.add_click_ripple()
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Mouse release event"""
        if self._enabled and self._is_pressed and event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = False

            if self._checkable:
                self._checked = not self._checked

            self.clicked.emit()
            self.update()

        super().mouseReleaseEvent(event)


class FluentBaseToggle(FluentBaseWidget):
    """Base class for toggle components (switches, checkboxes, etc.)"""

    toggled = Signal(bool)
    stateChanged = Signal(int)

    def __init__(self, checked: bool = False, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._checked = checked
        self._enabled = True

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)

        self._setup_toggle_animations()

    def _setup_toggle_animations(self):
        """Setup toggle-specific animations"""
        self._create_animation("toggle", "geometry",
                               FluentAnimation.DURATION_MEDIUM,
                               FluentAnimation.EASE_OUT)

    def setChecked(self, checked: bool):
        """Set checked state"""
        if self._checked != checked:
            self._checked = checked
            self.toggled.emit(checked)
            self.stateChanged.emit(2 if checked else 0)
            self._animate_toggle()
            self.update()

    def isChecked(self) -> bool:
        """Check if toggle is checked"""
        return self._checked

    def setEnabled(self, enabled: bool):
        """Set enabled state"""
        self._enabled = enabled
        super().setEnabled(enabled)
        self.setCursor(Qt.CursorShape.PointingHandCursor if enabled
                       else Qt.CursorShape.ForbiddenCursor)
        self.update()

    def isEnabled(self) -> bool:
        """Check if toggle is enabled"""
        return self._enabled

    def _animate_toggle(self):
        """Animate toggle state change - override in subclasses"""
        pass

    def mousePressEvent(self, event: QMouseEvent):
        """Mouse press event"""
        if self._enabled and event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Mouse release event"""
        if self._enabled and self._is_pressed and event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = False
            self.setChecked(not self._checked)

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        """Handle keyboard navigation"""
        if self._enabled and event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return):
            self.setChecked(not self._checked)
        else:
            super().keyPressEvent(event)


class FluentBaseContainer(FluentBaseWidget):
    """Base container class with common layout functionality"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._border_radius = 8
        self._border_width = 1
        self._padding = 16

    def setBorderRadius(self, radius: int):
        """Set border radius"""
        self._border_radius = radius
        self.update()

    def setBorderWidth(self, width: int):
        """Set border width"""
        self._border_width = width
        self.update()

    def setPadding(self, padding: int):
        """Set padding"""
        self._padding = padding
        self.update()

    def _draw_background(self, painter: QPainter, rect, background_color: Optional[QColor] = None):
        """Draw container background"""
        if background_color is None:
            background_color = self._get_theme_color('surface')

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Apply hover effect
        self._apply_hover_effect(painter, rect, background_color)

        # Draw border
        border_color = self._get_theme_color('border')
        painter.setPen(QPen(border_color, self._border_width))

        # Draw rounded rectangle
        painter.drawRoundedRect(rect, self._border_radius, self._border_radius)
