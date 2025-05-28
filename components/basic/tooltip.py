"""
Fluent Design Style Tooltip Component
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QPainterPath, QFont, QFontMetrics
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional


class FluentTooltip(QWidget):
    """Fluent Design style tooltip"""
    
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
        shadow.setColor(theme_manager.get_color('shadow'))
        self.setGraphicsEffect(shadow)
    
    def _setup_style(self):
        """Setup style"""
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
        self._show_timer.timeout.connect(self._show_tooltip)
        
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._hide_tooltip)
    
    def _setup_animations(self):
        """Setup animations"""
        self._fade_animation = QPropertyAnimation(self, b"opacity")
        self._fade_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._fade_animation.setEasingCurve(FluentAnimation.EASE_OUT)
    
    def _get_opacity(self):
        return self._opacity
    
    def _set_opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)
    
    opacity = Property(float, _get_opacity, _set_opacity)
    
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
        """Show tooltip at position"""
        self._hide_timer.stop()
        
        # Adjust size to content
        self.adjustSize()
        
        # Position tooltip
        screen = self.screen().availableGeometry() if self.screen() else None
        if screen:
            # Ensure tooltip stays within screen bounds
            x = position.x()
            y = position.y() - self.height() - 10
            
            if x + self.width() > screen.right():
                x = screen.right() - self.width()
            if x < screen.left():
                x = screen.left()
            if y < screen.top():
                y = position.y() + 25
            
            self.move(x, y)
        else:
            self.move(position.x(), position.y() - self.height() - 10)
        
        # Start show timer
        self._show_timer.start(self._show_delay)
    
    def hideTooltip(self):
        """Hide tooltip"""
        self._show_timer.stop()
        self._hide_tooltip()
    
    def showDelayed(self, position: QPoint):
        """Show tooltip with delay"""
        self._hide_timer.stop()
        self.move(position.x(), position.y() - self.height() - 10)
        self._show_timer.start(self._show_delay)
    
    def _show_tooltip(self):
        """Internal method to show tooltip"""
        self.show()
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.start()
        
        # Start hide timer
        if self._hide_delay > 0:
            self._hide_timer.start(self._hide_delay)
    
    def _hide_tooltip(self):
        """Internal method to hide tooltip"""
        self._fade_animation.setStartValue(self._opacity)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.finished.connect(self.hide)
        self._fade_animation.start()
    
    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class TooltipMixin:
    """Mixin class to add tooltip functionality to any widget"""
    
    def __init__(self):
        self._tooltip = None
        self._tooltip_text = ""
    
    def setTooltipText(self, text: str):
        """Set tooltip text"""
        self._tooltip_text = text
        if not self._tooltip:
            self._tooltip = FluentTooltip(text, self.parent() if hasattr(self, 'parent') else None)
    
    def enterEvent(self, event):
        """Handle mouse enter event"""
        if self._tooltip_text and self._tooltip:
            global_pos = self.mapToGlobal(self.rect().bottomLeft())
            self._tooltip.showTooltip(global_pos)
        super().enterEvent(event) if hasattr(super(), 'enterEvent') else None
    
    def leaveEvent(self, event):
        """Handle mouse leave event"""
        if self._tooltip:
            self._tooltip.hideTooltip()
        super().leaveEvent(event) if hasattr(super(), 'leaveEvent') else None
