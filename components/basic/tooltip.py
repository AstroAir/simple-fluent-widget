"""
Fluent Design Style Tooltip Component
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, Property, QByteArray, Signal
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional


class FluentTooltip(QWidget):
    """Fluent Design style tooltip"""

    opacityChanged = Signal()

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._text = text
        self._show_delay = 500  # ms
        self._hide_delay = 3000  # ms
        self._show_timer = QTimer()
        self._hide_timer = QTimer()
        self._opacity = 0.0

        self._setup_ui()
        self._setup_style()
        self._setup_timers()
        self._setup_animations()

        # Set window flags
        self.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setMaximumWidth(300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        self._label = QLabel(self._text)
        self._label.setWordWrap(True)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self._label)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 2)
        if theme_manager:
            shadow.setColor(theme_manager.get_color('shadow'))
        self.setGraphicsEffect(shadow)

    def _setup_style(self):
        """Setup style"""
        if not theme_manager:
            return
        theme = theme_manager

        style_sheet = f"""
            FluentTooltip {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                font-size: 12px;
                font-family: "Segoe UI", sans-serif;
                background: transparent;
                border: none;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_timers(self):
        """Setup timers"""
        self._show_timer.setSingleShot(True)
        self._show_timer.timeout.connect(self._show_tooltip_animated)

        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._hide_tooltip_animated)

    def _setup_animations(self):
        """Setup animations"""
        self._fade_animation = QPropertyAnimation(self, QByteArray(b"opacity"))
        self._fade_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._fade_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def _get_opacity(self) -> float:
        return self._opacity

    def _set_opacity(self, value: float):
        if self._opacity != value:
            self._opacity = value
            self.setWindowOpacity(value)
            self.opacityChanged.emit()

    opacity = Property(float, _get_opacity, _set_opacity,
                       None, "", notify=opacityChanged)

    def setText(self, text: str):
        """Set tooltip text"""
        self._text = text
        self._label.setText(text)
        self.adjustSize()

    def getText(self) -> str:
        """Get tooltip text"""
        return self._text

    def setShowDelay(self, delay: int):
        """Set show delay in milliseconds"""
        self._show_delay = delay

    def setHideDelay(self, delay: int):
        """Set hide delay in milliseconds"""
        self._hide_delay = delay

    def showTooltip(self, position: QPoint):
        """Show tooltip at position after a delay."""
        self._hide_timer.stop()  # Stop any pending hide

        self.adjustSize()  # Adjust size to content first

        # Position tooltip
        screen_geom = self.screen().availableGeometry() if self.screen() else None
        x = position.x()
        y = position.y() - self.height() - 10  # Default above the point

        if screen_geom:
            if x + self.width() > screen_geom.right():
                x = screen_geom.right() - self.width()
            if x < screen_geom.left():
                x = screen_geom.left()
            if y < screen_geom.top():  # If too high, show below the point
                y = position.y() + 25
            if y + self.height() > screen_geom.bottom():  # If too low (when shown below), adjust
                y = screen_geom.bottom() - self.height()

        self.move(x, y)

        if self._show_delay > 0:
            self._show_timer.start(self._show_delay)
        else:
            self._show_tooltip_animated()  # Show immediately if no delay

    def hideTooltip(self):
        """Hide tooltip, possibly after a delay if it's currently showing."""
        self._show_timer.stop()  # Stop any pending show
        if self.isVisible() and self._opacity > 0:  # If fully or partially visible
            # No separate hide delay, hide animation starts immediately
            self._hide_tooltip_animated()
        else:  # If not visible or already fading out, just ensure it's hidden
            self.hide()
            self._set_opacity(0.0)

    def _show_tooltip_animated(self):
        """Internal method to show tooltip with animation"""
        self.show()
        self._fade_animation.stop()
        self._fade_animation.setStartValue(
            self._opacity)  # Start from current opacity
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.start()

        if self._hide_delay > 0:  # If auto-hide is configured
            self._hide_timer.start(self._hide_delay)

    def _hide_tooltip_animated(self):
        """Internal method to hide tooltip with animation"""
        self._fade_animation.stop()
        self._fade_animation.setStartValue(
            self._opacity)  # Start from current opacity
        self._fade_animation.setEndValue(0.0)

        # Disconnect previous connection to avoid multiple hides
        try:
            self._fade_animation.finished.disconnect(self.hide)
        except RuntimeError:  # No connection to disconnect
            pass
        self._fade_animation.finished.connect(self.hide)
        self._fade_animation.start()

    def _on_theme_changed(self, _=None):  # Parameter name changed to _
        """Handle theme change"""
        self._setup_style()
        # Update shadow color if theme changes
        if theme_manager:
            current_effect = self.graphicsEffect()
            # Ensure the effect is a QGraphicsDropShadowEffect before calling setColor
            if isinstance(current_effect, QGraphicsDropShadowEffect):
                current_effect.setColor(theme_manager.get_color('shadow'))


class TooltipMixin:
    """Mixin class to add tooltip functionality to any QWidget"""

    def __init__(self, *args, **kwargs):  # Allow args and kwargs for super().__init__
        # Ensure super().__init__ is called for the class this mixin is combined with
        # This line might need to be called by the class using the mixin if it has its own __init__
        # For a pure mixin, it might not call super().__init__ itself directly here.
        # Or, it assumes it's part of a chain that does.
        # super(TooltipMixin, self).__init__(*args, **kwargs) # Be careful with direct super() in mixin __init__

        self._tooltip_widget: Optional[FluentTooltip] = None
        self._tooltip_text_content: str = ""

    def setTooltipText(self, text: str):
        """Set tooltip text"""
        self._tooltip_text_content = text
        if not self._tooltip_widget and isinstance(self, QWidget):
            # Determine parent for the tooltip
            parent_widget = self.parentWidget()
            self._tooltip_widget = FluentTooltip(
                text, parent=None)  # Tooltips are top-level
            # but logically associated

    def enterEvent(self, event):
        """Handle mouse enter event"""
        if isinstance(self, QWidget):  # Ensure self is a QWidget
            if self._tooltip_text_content and self._tooltip_widget:
                # Position tooltip relative to the widget self is mixed into
                global_pos = self.mapToGlobal(self.rect().bottomLeft())
                # Adjust position slightly to avoid overlap and give space for cursor
                adjusted_pos = QPoint(global_pos.x(), global_pos.y() + 5)
                self._tooltip_widget.showTooltip(adjusted_pos)

            # Call super() for the class this mixin is part of
            s = super()
            if hasattr(s, 'enterEvent'):
                s.enterEvent(event)  # type: ignore

    def leaveEvent(self, event):
        """Handle mouse leave event"""
        if isinstance(self, QWidget):  # Ensure self is a QWidget
            if self._tooltip_widget:
                self._tooltip_widget.hideTooltip()

            # Call super() for the class this mixin is part of
            s = super()
            if hasattr(s, 'leaveEvent'):
                s.leaveEvent(event)  # type: ignore

    def toolTipText(self) -> str:
        """Get the current tooltip text."""
        return self._tooltip_text_content
