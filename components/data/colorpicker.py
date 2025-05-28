"""
Fluent Design Style Color Picker Component
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                               QPushButton, QSlider, QLineEdit, QFrame, QColorDialog)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QRect, Property, QByteArray, QPoint
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QMouseEvent
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional, List
import math


class FluentColorButton(QPushButton):
    """Individual color button for color palette"""

    colorSelected = Signal(QColor)

    def __init__(self, color: QColor, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._color = color
        self._is_selected = False
        self._hover_scale = 1.0

        self.setFixedSize(32, 32)
        self.clicked.connect(lambda: self.colorSelected.emit(self._color))

        self._setup_animations()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animations(self):
        """Setup animations"""
        self._hover_animation = QPropertyAnimation(self, QByteArray(b"hover_scale"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def _setup_style(self):
        """Setup style"""
        self.setStyleSheet("""
            FluentColorButton {
                border: 2px solid transparent;
                border-radius: 6px;
            }
            FluentColorButton:hover {
                border-color: #666;
            }
        """)

    def _get_hover_scale(self):
        return self._hover_scale

    def _set_hover_scale(self, value):
        self._hover_scale = value
        self.update()

    hover_scale = Property(float, _get_hover_scale, _set_hover_scale, None, "")

    def setColor(self, color: QColor):
        """Set the button color"""
        self._color = color
        self.update()

    def getColor(self) -> QColor:
        """Get the button color"""
        return self._color

    def setSelected(self, selected: bool):
        """Set selection state"""
        self._is_selected = selected
        self.update()

    def isSelected(self) -> bool:
        """Check if button is selected"""
        return self._is_selected

    def enterEvent(self, event):
        """Handle mouse enter"""
        super().enterEvent(event)
        self._hover_animation.setStartValue(self._hover_scale)
        self._hover_animation.setEndValue(1.1)
        self._hover_animation.start()

    def leaveEvent(self, event):
        """Handle mouse leave"""
        super().leaveEvent(event)
        self._hover_animation.setStartValue(self._hover_scale)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()

    def paintEvent(self, _event):
        """Paint the color button"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate scaled rect
        rect = self.rect()
        if self._hover_scale != 1.0:
            center = rect.center()
            scaled_width = int(rect.width() * self._hover_scale)
            scaled_height = int(rect.height() * self._hover_scale)
            # Create QRect with integer coordinates for QPainter
            rect = QRect(0, 0, scaled_width, scaled_height)
            rect.moveCenter(center)


        # Draw color
        # Adjust for border to be drawn inside this rect
        color_rect = rect.adjusted(2, 2, -2, -2)
        painter.fillRect(color_rect, QBrush(self._color))

        # Draw border
        border_color = QColor("#333") if self._is_selected else QColor("#999")
        border_width = 3 if self._is_selected else 1
        painter.setPen(QPen(border_color, border_width))
        painter.drawRect(color_rect)


    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentColorWheel(QWidget):
    """Color wheel for HSV selection"""

    colorChanged = Signal(QColor)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._hue = 0.0
        self._saturation = 1.0
        self._value = 1.0
        self._wheel_radius = 80
        self._wheel_thickness = 20

        self.setFixedSize(200, 200)
        self.setMouseTracking(True)

    def setColor(self, color: QColor):
        """Set the current color"""
        if isinstance(color, QColor) and color.isValid():
            # In PySide6, getHsvF() doesn't return a tuple but individual values via separate method calls
            h = color.hsvHueF()
            s = color.hsvSaturationF()
            v = color.valueF()
            self._hue = h if h >= 0.0 else 0.0 # Ensure hue is not -1
            self._saturation = s
            self._value = v
            self.update()
        # else: consider logging an error if color is invalid or not QColor

    def getColor(self) -> QColor:
        """Get the current color"""
        color = QColor()
        color.setHsvF(self._hue, self._saturation, self._value, 1.0) # Alpha is 1.0 by default
        return color

    def paintEvent(self, _event):
        """Paint the color wheel"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()
        outer_radius = self._wheel_radius
        inner_radius = outer_radius - self._wheel_thickness

        # Draw color wheel
        for angle_deg in range(360):
            hue = angle_deg / 360.0
            color = QColor()
            color.setHsvF(hue, 1.0, 1.0) # Full saturation and value for wheel

            painter.setPen(QPen(color, 2)) # Pen width 2 for thicker lines

            start_angle_rad = math.radians(angle_deg)
            # end_angle was unused, removed calculation

            # Draw a line segment for the wheel
            x1 = center.x() + inner_radius * math.cos(start_angle_rad)
            y1 = center.y() + inner_radius * math.sin(start_angle_rad)
            x2 = center.x() + outer_radius * math.cos(start_angle_rad)
            y2 = center.y() + outer_radius * math.sin(start_angle_rad)

            painter.drawLine(QPoint(int(x1), int(y1)), QPoint(int(x2), int(y2)))


        # Draw current hue indicator
        current_angle_rad = self._hue * 2 * math.pi # Hue is [0,1), angle is [0, 2pi)
        indicator_x = center.x() + (outer_radius + 5) * math.cos(current_angle_rad)
        indicator_y = center.y() + (outer_radius + 5) * math.sin(current_angle_rad)


        painter.setPen(QPen(QColor(Qt.GlobalColor.black), 2))
        painter.setBrush(QBrush(QColor(Qt.GlobalColor.white)))
        painter.drawEllipse(QPoint(int(indicator_x), int(indicator_y)), 4, 4)


        # Draw saturation/value triangle
        self._draw_sv_triangle(painter, center, inner_radius - 10)

    def _draw_sv_triangle(self, painter: QPainter, center: QPoint, max_radius: int):
        """Draw saturation/value selection triangle"""
        # Triangle points are typically at 0, 120, 240 degrees relative to hue
        # For simplicity, this example might use a fixed orientation or simplified geometry
        # A common approach is an equilateral triangle.
        # The current hue defines the color at one vertex (full saturation, full value).
        # Other vertices are black (value=0) and white (saturation=0).

        # Simplified representation:
        # Base color for gradients
        base_hue_color = QColor()
        base_hue_color.setHsvF(self._hue, 1.0, 1.0)

        # Define triangle vertices (example for an equilateral triangle)
        # Top point (current hue, S=1, V=1)
        # For simplicity, let's draw a square for S/V selection as in many pickers
        sv_rect_size = max_radius * 2 * 0.7 # Approximate size
        sv_rect_top_left_x = center.x() - sv_rect_size / 2
        sv_rect_top_left_y = center.y() - sv_rect_size / 2
        sv_rect = QRect(int(sv_rect_top_left_x), int(sv_rect_top_left_y), int(sv_rect_size), int(sv_rect_size))

        # Draw saturation gradient (horizontal: white to hue_color)
        for i in range(int(sv_rect.width())):
            s = i / sv_rect.width()
            grad_color = QColor()
            grad_color.setHsvF(self._hue, s, self._value) # Use current value for this sweep
            painter.setPen(QPen(grad_color))
            painter.drawLine(sv_rect.left() + i, sv_rect.top(), sv_rect.left() + i, sv_rect.bottom())

        # Draw value gradient (vertical: black to transparent overlay or mixed)
        # This is more complex to do correctly with QPainter without shaders
        # A common way is to draw a black to transparent gradient over the saturation gradient

        # Draw current S/V indicator
        # Map S (0-1) to x-coordinate and V (0-1) to y-coordinate within sv_rect
        indicator_sv_x = sv_rect.left() + self._saturation * sv_rect.width()
        indicator_sv_y = sv_rect.top() + (1.0 - self._value) * sv_rect.height() # V=1 is top, V=0 is bottom

        painter.setPen(QPen(QColor(Qt.GlobalColor.black) if self._value > 0.5 else QColor(Qt.GlobalColor.white), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPoint(int(indicator_sv_x), int(indicator_sv_y)), 3, 3)


    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        self._update_color_from_position(event.position().toPoint())

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move"""
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._update_color_from_position(event.position().toPoint())

    def _update_color_from_position(self, pos: QPoint):
        """Update color based on mouse position"""
        center = self.rect().center()
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()
        distance = math.sqrt(dx * dx + dy * dy)

        # Check if in wheel area (for Hue)
        outer_radius = self._wheel_radius
        inner_radius = outer_radius - self._wheel_thickness

        if inner_radius <= distance <= outer_radius:
            angle_rad = math.atan2(dy, dx) # Range: -pi to pi
            # Normalize angle to [0, 2*pi) then to hue [0, 1)
            current_hue = (angle_rad + math.pi) / (2 * math.pi)
            if current_hue < 0.0: # Should not happen with (angle + pi)
                current_hue += 1.0
            current_hue = min(max(current_hue, 0.0), 1.0) # Clamp

            if abs(self._hue - current_hue) > 1e-3 : # Update only if changed significantly
                self._hue = current_hue
                self.colorChanged.emit(self.getColor())
                self.update()
        else:
            # Check if in SV area (simplified square for this example)
            sv_rect_size = (inner_radius - 10) * 2 * 0.7
            sv_rect_top_left_x = center.x() - sv_rect_size / 2
            sv_rect_top_left_y = center.y() - sv_rect_size / 2
            sv_rect = QRect(int(sv_rect_top_left_x), int(sv_rect_top_left_y), int(sv_rect_size), int(sv_rect_size))

            if sv_rect.contains(pos):
                relative_x = pos.x() - sv_rect.left()
                relative_y = pos.y() - sv_rect.top()

                new_s = min(max(relative_x / sv_rect.width(), 0.0), 1.0)
                new_v = 1.0 - min(max(relative_y / sv_rect.height(), 0.0), 1.0) # V is inverted

                if abs(self._saturation - new_s) > 1e-3 or abs(self._value - new_v) > 1e-3:
                    self._saturation = new_s
                    self._value = new_v
                    self.colorChanged.emit(self.getColor())
                    self.update()


class FluentColorPicker(QWidget):
    """Complete color picker widget"""

    colorChanged = Signal(QColor)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._current_color = QColor("#0078d4")
        self._predefined_colors: List[QColor] = [
            QColor("#FF6B6B"), QColor("#4ECDC4"), QColor("#45B7D1"), QColor("#96CEB4"),
            QColor("#FECA57"), QColor("#FF9FF3"), QColor("#54A0FF"), QColor("#5F27CD"),
            QColor("#00D2D3"), QColor("#FF9F43"), QColor("#10AC84"), QColor("#EE5A6F"),
            QColor("#0078d4"), QColor("#005a9e"), QColor("#004578"), QColor("#002c4a"),
            QColor("#6264A7"), QColor("#8764B8"), QColor("#8E8CD8"), QColor("#B4A7D6"),
            QColor("#D13438"), QColor("#FF4B4B"), QColor("#FF6B6B"), QColor("#FF9999")
        ]

        self._setup_ui()
        self._setup_style()
        self.setColor(self._current_color) # Initialize all displays

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        self._setup_current_color(layout)
        self._setup_color_wheel(layout)
        self._setup_rgb_sliders(layout)
        self._setup_predefined_colors(layout)
        self._setup_hex_input(layout)
        self._setup_buttons(layout)

    def _setup_current_color(self, layout: QVBoxLayout):
        """Setup current color display"""
        self._color_display = QFrame()
        self._color_display.setFixedHeight(60)
        self._color_display.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken) # Example style
        layout.addWidget(self._color_display)

    def _setup_color_wheel(self, layout: QVBoxLayout):
        """Setup color wheel"""
        wheel_layout = QHBoxLayout()
        wheel_layout.addStretch()
        self._color_wheel = FluentColorWheel()
        self._color_wheel.colorChanged.connect(self._on_wheel_or_slider_changed) # Connect to unified handler
        wheel_layout.addWidget(self._color_wheel)
        wheel_layout.addStretch()
        layout.addLayout(wheel_layout)

    def _setup_rgb_sliders(self, layout: QVBoxLayout):
        """Setup RGB sliders"""
        rgb_group = QFrame()
        rgb_layout = QGridLayout(rgb_group)
        self._rgb_sliders = {}
        self._rgb_labels = {}

        for i, component in enumerate(['R', 'G', 'B']):
            label = QLabel(component + ":")
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 255)
            slider.valueChanged.connect(self._on_rgb_slider_changed) # Specific handler

            value_label = QLabel("0")
            value_label.setMinimumWidth(30)

            rgb_layout.addWidget(label, i, 0)
            rgb_layout.addWidget(slider, i, 1)
            rgb_layout.addWidget(value_label, i, 2)

            self._rgb_sliders[component] = slider
            self._rgb_labels[component] = value_label
        layout.addWidget(rgb_group)

    def _setup_predefined_colors(self, layout: QVBoxLayout):
        """Setup predefined color palette"""
        palette_label = QLabel("预设颜色:")
        layout.addWidget(palette_label)
        palette_widget = QWidget()
        palette_layout = QGridLayout(palette_widget)
        palette_layout.setSpacing(4)
        rows, cols = 3, 8
        for i, color_val in enumerate(self._predefined_colors[:rows * cols]):
            btn = FluentColorButton(color_val)
            btn.colorSelected.connect(self._on_predefined_color_selected)
            palette_layout.addWidget(btn, i // cols, i % cols)
        layout.addWidget(palette_widget)

    def _setup_hex_input(self, layout: QVBoxLayout):
        """Setup hex color input"""
        hex_layout = QHBoxLayout()
        hex_label = QLabel("十六进制:")
        self._hex_input = QLineEdit()
        self._hex_input.setPlaceholderText("#RRGGBB")
        self._hex_input.textChanged.connect(self._on_hex_changed)
        hex_layout.addWidget(hex_label)
        hex_layout.addWidget(self._hex_input)
        layout.addLayout(hex_layout)

    def _setup_buttons(self, layout: QVBoxLayout):
        """Setup action buttons"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        more_btn = QPushButton("更多颜色...")
        more_btn.clicked.connect(self._open_color_dialog)
        button_layout.addWidget(more_btn)
        layout.addLayout(button_layout)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager
        self._update_color_display() # Update display with current color
        # Apply stylesheet (simplified, ensure theme colors are valid QColor names or hex)
        self.setStyleSheet(f"""
            QLabel {{ color: {theme.get_color('text_primary').name()}; font-family: "Segoe UI", sans-serif; }}
            QLineEdit {{ background-color: {theme.get_color('surface').name()}; border: 1px solid {theme.get_color('border').name()}; border-radius: 4px; padding: 6px 8px; color: {theme.get_color('text_primary').name()}; }}
            QSlider::groove:horizontal {{ border: 1px solid {theme.get_color('border').name()}; height: 6px; border-radius: 3px; background: {theme.get_color('background').name()}; }}
            QSlider::handle:horizontal {{ background: {theme.get_color('primary').name()}; border: 1px solid {theme.get_color('border').name()}; width: 16px; border-radius: 8px; margin: -5px 0; }}
        """)

    def setColor(self, color: QColor):
        """Set the current color and update all UI elements."""
        if isinstance(color, QColor) and color.isValid() and self._current_color != color:
            self._current_color = color
            self._update_all_displays()
            self.colorChanged.emit(self._current_color)

    def getColor(self) -> QColor:
        """Get the current color"""
        return self._current_color

    def _update_color_display(self):
        if hasattr(self, '_color_display'):
            self._color_display.setStyleSheet(f"background-color: {self._current_color.name()}; border: 1px solid #ccc; border-radius: 4px;")

    def _update_all_displays(self):
        """Update all UI components to reflect the current color."""
        self._update_color_display()

        # RGB Sliders and Labels
        if hasattr(self, '_rgb_sliders'):
            for component in ['R', 'G', 'B']:
                slider = self._rgb_sliders[component]
                label = self._rgb_labels[component]
                value = getattr(self._current_color, component.lower())()
                slider.blockSignals(True)
                slider.setValue(value)
                slider.blockSignals(False)
                label.setText(str(value))

        # Hex Input
        if hasattr(self, '_hex_input'):
            self._hex_input.blockSignals(True)
            self._hex_input.setText(self._current_color.name().upper())
            self._hex_input.blockSignals(False)

        # Color Wheel
        if hasattr(self, '_color_wheel'):
            self._color_wheel.blockSignals(True)
            self._color_wheel.setColor(self._current_color)
            self._color_wheel.blockSignals(False)

    def _on_wheel_or_slider_changed(self, color: QColor):
        """Unified handler for color changes from wheel or future complex sliders."""
        self.setColor(color)

    def _on_rgb_slider_changed(self):
        """Handle RGB slider direct interaction."""
        r = self._rgb_sliders['R'].value()
        g = self._rgb_sliders['G'].value()
        b = self._rgb_sliders['B'].value()
        self.setColor(QColor(r, g, b))


    def _on_predefined_color_selected(self, color: QColor):
        self.setColor(color)

    def _on_hex_changed(self, text: str):
        if text.startswith('#') and (len(text) == 7 or len(text) == 9): # Support #RRGGBB and #AARRGGBB
            new_color = QColor(text)
            if new_color.isValid():
                self.setColor(new_color)

    def _open_color_dialog(self):
        color = QColorDialog.getColor(self._current_color, self, "选择颜色")
        if color.isValid():
            self.setColor(color)

    def _on_theme_changed(self, _):
        self._setup_style()
        self._update_all_displays() # Ensure colors update with theme
