"""
Fluent Design Style Toggle Switch Component
Provides an elegant toggle switch control for binary options
"""

from PySide6.QtWidgets import QWidget, QCheckBox
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QRect, QEasingCurve, Property
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPaintEvent
from core.theme import theme_manager
from typing import Optional


class FluentToggleSwitch(QCheckBox):
    """Fluent Design Style Toggle Switch
    
    Features:
    - Smooth animation when toggling state
    - Adaptive theme colors
    - Optional label text
    - Customizable enabled/disabled states
    """
    
    stateChanged = Signal(bool)  # True for checked, False for unchecked
    
    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        
        # Appearance properties
        self._track_height = 14
        self._thumb_size = 18
        self._thumb_margin = 2
        self._thumb_position = 0
        
        # Setup animation
        self._thumb_animation = QPropertyAnimation(self, b"thumbPosition")
        self._thumb_animation.setDuration(150)
        self._thumb_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Connect state changes
        self.clicked.connect(self._handle_toggle)
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Initial setup
        self.setMinimumWidth(46)
        self._on_theme_changed()
    
    def _handle_toggle(self):
        """Handle toggle action with animation"""
        self._thumb_animation.stop()
        if self.isChecked():
            self._thumb_animation.setEndValue(1.0)
        else:
            self._thumb_animation.setEndValue(0.0)
        self._thumb_animation.start()
        self.stateChanged.emit(self.isChecked())
    
    def sizeHint(self):
        """Suggest an appropriate size for the widget"""
        width = 46 if not self.text() else 80
        height = max(self._thumb_size + self._thumb_margin * 2, 20)
        return Qt.QSize(width, height)
    
    def paintEvent(self, event: QPaintEvent):
        """Draw the toggle switch"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        theme = theme_manager
        track_width = 32
        
        # Draw text if present
        if self.text():
            text_color = theme.get_color('text_primary') if self.isEnabled() else theme.get_color('text_disabled')
            painter.setPen(QPen(text_color))
            font = painter.font()
            painter.setFont(font)
            
            text_rect = self.rect()
            text_rect.setLeft(track_width + 8)
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.text())
        
        # Calculate toggle track rect
        track_rect = QRect(0, 
                          (self.height() - self._track_height) // 2, 
                          track_width, 
                          self._track_height)
        
        # Draw track
        if self.isEnabled():
            if self.isChecked():
                track_color = theme.get_color('primary')
            else:
                track_color = theme.get_color('border')
        else:
            track_color = theme.get_color('border').darker(120) if self.isChecked() else theme.get_color('border')
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(track_rect, self._track_height // 2, self._track_height // 2)
        
        # Calculate thumb position
        track_width_adjusted = track_width - self._thumb_size - self._thumb_margin * 2
        thumb_x = self._thumb_margin + track_width_adjusted * self._thumb_position
        thumb_y = (self.height() - self._thumb_size) // 2
        
        # Draw thumb
        if self.isEnabled():
            thumb_color = QColor("white") if theme.current_mode.name == "LIGHT" else QColor(45, 45, 45)
        else:
            thumb_color = QColor(200, 200, 200)
        
        painter.setBrush(QBrush(thumb_color))
        painter.setPen(QPen(theme.get_color('border')))
        painter.drawEllipse(thumb_x, thumb_y, self._thumb_size, self._thumb_size)
        
        painter.end()
    
    def _on_theme_changed(self):
        """Handle theme changes"""
        self.update()
    
    def set_checked_without_animation(self, checked: bool):
        """Set checked state without animation"""
        self.blockSignals(True)
        self.setChecked(checked)
        self._thumb_position = 1.0 if checked else 0.0
        self.blockSignals(False)
        self.update()
    
    # Property for animation
    def _get_thumb_position(self):
        return self._thumb_position
    
    def _set_thumb_position(self, pos):
        self._thumb_position = pos
        self.update()
    
    thumbPosition = Property(float, _get_thumb_position, _set_thumb_position)
