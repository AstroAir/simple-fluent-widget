"""
Fluent Design Style Color Picker Component - Optimized

Advanced color picker with modern Python features and enhanced UX.
Optimized for Python 3.11+ with:
- Union type syntax (|)
- Dataclasses and protocols
- Enhanced pattern matching
- Type safety improvements
- Performance optimizations
- Better error handling
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol, TypeVar, Generic, Union, Optional, Sequence, Callable, List
from collections.abc import Iterable
from functools import lru_cache, cached_property
from contextlib import contextmanager

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QSlider, QLineEdit, QFrame, QColorDialog,
    QToolTip, QGraphicsOpacityEffect, QSizePolicy
)
from PySide6.QtCore import (
    Qt, Signal, QPropertyAnimation, QRect, Property, QByteArray, 
    QPoint, QParallelAnimationGroup, QTimer, QEasingCurve,
    Slot, QSize, QAbstractAnimation, QSequentialAnimationGroup
)
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPen, QMouseEvent, QLinearGradient,
    QRadialGradient, QPainterPath, QFontMetrics, QValidator,
    QRegularExpressionValidator
)

# Enhanced imports with better error handling
try:
    from core.theme import theme_manager
    THEME_AVAILABLE = True
except ImportError:
    theme_manager = None
    THEME_AVAILABLE = False

try:
    from core.animation import FluentAnimation
    from core.enhanced_animations import FluentTransition, FluentMicroInteraction
    ANIMATIONS_AVAILABLE = True
except ImportError:
    # Null object pattern for missing animations
    class AnimationProxy:
        def __getattr__(self, name: str) -> Callable[..., None]:
            return lambda *args, **kwargs: None
    
    ANIMATIONS_AVAILABLE = False
    FluentAnimation = AnimationProxy()
    FluentTransition = AnimationProxy()
    FluentMicroInteraction = AnimationProxy()


# Modern type aliases
ColorValue = Union[QColor, str, tuple[int, int, int], tuple[int, int, int, int]]
AnimationGroup = Union[QParallelAnimationGroup, QSequentialAnimationGroup]

# Generic type variables
T = TypeVar('T')
C = TypeVar('C', bound=QColor)


class ColorValidationProtocol(Protocol):
    """Protocol for color validation functions"""
    def __call__(self, color: QColor) -> bool: ...


class ColorFormat(Enum):
    """Supported color formats"""
    RGB = auto()
    RGBA = auto()
    HSV = auto()
    HSL = auto()
    HEX = auto()
    CMYK = auto()


@dataclass(slots=True, frozen=True)
class ColorConstraints:
    """Immutable color constraints for validation"""
    alpha_enabled: bool = True
    min_brightness: float = 0.0
    max_brightness: float = 1.0
    allowed_formats: tuple[ColorFormat, ...] = field(default_factory=lambda: tuple(ColorFormat))
    custom_validator: Optional[ColorValidationProtocol] = None


@dataclass(slots=True)
class ColorState:
    """Mutable color state management"""
    current: QColor = field(default_factory=lambda: QColor("#0078d4"))
    previous: QColor = field(default_factory=lambda: QColor("#0078d4"))
    format_preference: ColorFormat = ColorFormat.HEX
    constraints: ColorConstraints = field(default_factory=ColorConstraints)
    
    def update_color(self, new_color: QColor) -> bool:
        """Update color with validation"""
        if self.is_valid_color(new_color):
            self.previous = self.current
            self.current = new_color
            return True
        return False
    
    def is_valid_color(self, color: QColor) -> bool:
        """Validate color against constraints"""
        if not color.isValid():
            return False
            
        if self.constraints.custom_validator:
            return self.constraints.custom_validator(color)
            
        # Built-in validation
        brightness = color.valueF()
        return (self.constraints.min_brightness <= brightness <= self.constraints.max_brightness)


class FluentColorButton(QPushButton):
    """Individual color button with enhanced animations and accessibility"""

    colorSelected = Signal(QColor)
    colorHovered = Signal(QColor)  # New signal for hover feedback

    def __init__(self, color: QColor, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._color_state = ColorState(current=color)
        self._is_selected = False
        self._hover_scale = 1.0
        self._animation_duration = 200  # Optimized duration

        self.setFixedSize(36, 36)  # Slightly larger for better touch targets
        self.setToolTip(f"Color: {color.name()}")  # Accessibility
        self.setAccessibleName(f"Color button {color.name()}")
        
        self._setup_animations()
        self._setup_style()
        self._connect_signals()

    def _setup_animations(self) -> None:
        """Setup modern animations with enhanced easing"""
        # Hover animation with modern easing
        self._hover_animation = QPropertyAnimation(self, QByteArray(b"hover_scale"))
        self._hover_animation.setDuration(self._animation_duration)
        
        if ANIMATIONS_AVAILABLE:
            self._hover_animation.setEasingCurve(getattr(FluentTransition, 'EASE_SPRING', QEasingCurve.Type.OutBack))
        else:
            self._hover_animation.setEasingCurve(QEasingCurve.Type.OutQuart)

        # Press animation group for coordinated effects
        self._press_animation_group = QParallelAnimationGroup(self)
        
        # Scale animation
        self._press_scale_anim = QPropertyAnimation(self, QByteArray(b"hover_scale"))
        self._press_scale_anim.setDuration(self._animation_duration // 2)
        self._press_scale_anim.setEasingCurve(QEasingCurve.Type.OutQuart)
        
        self._press_animation_group.addAnimation(self._press_scale_anim)

    def _setup_style(self) -> None:
        """Setup modern styling with theme integration"""
        base_style = """
            FluentColorButton {
                border: 2px solid transparent;
                border-radius: 8px;
                background: transparent;
            }
            FluentColorButton:hover {
                border-color: rgba(255, 255, 255, 0.3);
            }
            FluentColorButton:focus {
                border-color: #0078d4;
                outline: none;
            }
        """
        
        if THEME_AVAILABLE and theme_manager:
            try:
                accent_color = theme_manager.get_color('primary').name()
                base_style += f"""
                    FluentColorButton:focus {{
                        border-color: {accent_color};
                    }}
                """
            except Exception:
                pass  # Fallback to default
                
        self.setStyleSheet(base_style)

    def _connect_signals(self) -> None:
        """Connect signals with modern error handling"""
        try:
            self.clicked.connect(lambda: self.colorSelected.emit(self._color_state.current))
            
            if THEME_AVAILABLE and theme_manager and hasattr(theme_manager, 'theme_changed'):
                theme_manager.theme_changed.connect(self._on_theme_changed)
        except (AttributeError, RuntimeError) as e:
            print(f"Warning: Could not connect signals in FluentColorButton: {e}")

    # Property for animations (using modern Property API)
    def _get_hover_scale(self) -> float:
        return self._hover_scale

    def _set_hover_scale(self, value: float) -> None:
        self._hover_scale = value
        self.update()    # Property for animations (using correct Property API signature)
    hover_scale = Property(float, _get_hover_scale, _set_hover_scale, None, "Hover scale factor")

    def set_color(self, color: QColor) -> None:
        """Set button color with validation"""
        if self._color_state.update_color(color):
            self.setToolTip(f"Color: {color.name()}")
            self.update()

    def get_color(self) -> QColor:
        """Get current color"""
        return self._color_state.current

    def set_selected(self, selected: bool) -> None:
        """Set selection state with visual feedback"""
        if self._is_selected != selected:
            self._is_selected = selected
            self._animate_selection_change()
            self.update()

    def is_selected(self) -> bool:
        """Check selection state"""
        return self._is_selected

    def _animate_selection_change(self) -> None:
        """Animate selection state change"""
        if ANIMATIONS_AVAILABLE:
            try:
                FluentMicroInteraction.pulse_animation(self, scale=1.1 if self._is_selected else 1.0)
            except Exception:
                pass

    # Modern event handlers with enhanced animations
    def enterEvent(self, event) -> None:
        """Handle mouse enter with smooth animation"""
        super().enterEvent(event)
        if not self._is_selected:
            self._hover_animation.setStartValue(self._hover_scale)
            self._hover_animation.setEndValue(1.1)
            self._hover_animation.start()
            self.colorHovered.emit(self._color_state.current)

    def leaveEvent(self, event) -> None:
        """Handle mouse leave with smooth animation"""
        super().leaveEvent(event)
        if not self._is_selected:
            self._hover_animation.setStartValue(self._hover_scale)
            self._hover_animation.setEndValue(1.0)
            self._hover_animation.start()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press with enhanced animation"""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            if ANIMATIONS_AVAILABLE:
                try:
                    FluentMicroInteraction.button_press(self, scale=0.95)
                except Exception:
                    # Fallback animation
                    self._press_scale_anim.setStartValue(self._hover_scale)
                    self._press_scale_anim.setEndValue(0.95)
                    self._press_animation_group.start()

    def paintEvent(self, event) -> None:
        """Enhanced paint with modern effects"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        
        # Apply hover scale transformation
        if self._hover_scale != 1.0 and not self._is_selected:
            center = rect.center()
            scaled_size = int(min(rect.width(), rect.height()) * self._hover_scale)
            scaled_rect = QRect(0, 0, scaled_size, scaled_size)
            scaled_rect.moveCenter(center)
            rect = scaled_rect

        # Draw shadow for selected state
        if self._is_selected:
            shadow_rect = rect.adjusted(-2, -2, 2, 2)
            painter.fillRect(shadow_rect, QColor(0, 0, 0, 30))

        # Draw main color
        color_rect = rect.adjusted(2, 2, -2, -2)
        painter.fillRect(color_rect, self._color_state.current)

        # Draw border with state-based color
        border_color = self._get_border_color()
        border_width = 3 if self._is_selected else 1
        painter.setPen(QPen(border_color, border_width))
        painter.drawRoundedRect(color_rect, 6, 6)

        # Focus indicator
        if self.hasFocus():
            painter.setPen(QPen(QColor("#0078d4"), 2, Qt.PenStyle.DashLine))
            painter.drawRoundedRect(rect.adjusted(-1, -1, 1, 1), 8, 8)

    @lru_cache(maxsize=8)  # Cache border colors for performance
    def _get_border_color(self) -> QColor:
        """Get appropriate border color based on state"""
        if self._is_selected:
            if THEME_AVAILABLE and theme_manager:
                try:
                    return theme_manager.get_color('primary')
                except (AttributeError, TypeError):
                    pass
            return QColor("#0078d4")
        elif self.underMouse():
            return QColor("#666666")
        else:
            return QColor("#999999")

    @Slot()
    def _on_theme_changed(self) -> None:
        """Handle theme changes"""
        self._get_border_color.cache_clear()  # Clear color cache
        self._setup_style()
        self.update()


class FluentColorWheel(QWidget):
    """Enhanced color wheel with modern interaction patterns"""

    colorChanged = Signal(QColor)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self._color_state = ColorState()
        self._wheel_radius = 85  # Slightly larger for better UX
        self._wheel_thickness = 25
        self._sv_size = 0.7  # Relative size of saturation/value area
        
        self.setFixedSize(220, 220)  # Slightly larger
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def set_color(self, color: QColor) -> None:
        """Set current color with validation"""
        if self._color_state.update_color(color):
            self.update()

    def get_color(self) -> QColor:
        """Get current color"""
        return self._color_state.current

    def paintEvent(self, event) -> None:
        """Enhanced paint with better anti-aliasing"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        center = self.rect().center()
        self._draw_color_wheel(painter, center)
        self._draw_sv_square(painter, center)

    def _draw_color_wheel(self, painter: QPainter, center: QPoint) -> None:
        """Draw the color wheel with better performance"""
        outer_radius = self._wheel_radius
        inner_radius = outer_radius - self._wheel_thickness

        # Draw wheel segments with cached gradients
        for angle_deg in range(0, 360, 2):  # Step by 2 for better performance
            hue = angle_deg / 360.0
            color = QColor.fromHsvF(hue, 1.0, 1.0)

            angle_rad = math.radians(angle_deg)
            
            # Calculate line endpoints
            x1 = center.x() + inner_radius * math.cos(angle_rad)
            y1 = center.y() + inner_radius * math.sin(angle_rad)
            x2 = center.x() + outer_radius * math.cos(angle_rad)
            y2 = center.y() + outer_radius * math.sin(angle_rad)

            painter.setPen(QPen(color, 3))  # Thicker lines for better visual
            painter.drawLine(QPoint(int(x1), int(y1)), QPoint(int(x2), int(y2)))

        # Draw hue indicator
        current_angle = self._color_state.current.hsvHueF() * 2 * math.pi
        indicator_x = center.x() + (outer_radius + 8) * math.cos(current_angle)
        indicator_y = center.y() + (outer_radius + 8) * math.sin(current_angle)

        painter.setPen(QPen(QColor(Qt.GlobalColor.white), 3))
        painter.setBrush(QBrush(self._color_state.current))
        painter.drawEllipse(QPoint(int(indicator_x), int(indicator_y)), 6, 6)

    def _draw_sv_square(self, painter: QPainter, center: QPoint) -> None:
        """Draw saturation/value selection square"""
        sv_size = int((self._wheel_radius - self._wheel_thickness - 15) * self._sv_size * 2)
        sv_rect = QRect(
            center.x() - sv_size // 2,
            center.y() - sv_size // 2,
            sv_size,
            sv_size
        )

        # Create gradients for better visual quality
        current_hue = self._color_state.current.hsvHueF()
        
        # Horizontal saturation gradient (white to pure hue)
        for x in range(sv_rect.width()):
            saturation = x / sv_rect.width()
            for y in range(sv_rect.height()):
                value = 1.0 - (y / sv_rect.height())
                
                if (x + y) % 4 == 0:  # Sample every 4th pixel for performance
                    color = QColor.fromHsvF(current_hue, saturation, value)
                    painter.setPen(QPen(color))
                    painter.drawPoint(sv_rect.left() + x, sv_rect.top() + y)

        # Draw current S/V indicator
        s = self._color_state.current.hsvSaturationF()
        v = self._color_state.current.valueF()
        
        indicator_x = sv_rect.left() + int(s * sv_rect.width())
        indicator_y = sv_rect.top() + int((1.0 - v) * sv_rect.height())

        # Adaptive indicator color based on background
        indicator_color = QColor(Qt.GlobalColor.white) if v < 0.5 else QColor(Qt.GlobalColor.black)
        painter.setPen(QPen(indicator_color, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPoint(indicator_x, indicator_y), 4, 4)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press with improved hit detection"""
        self._update_color_from_position(event.position().toPoint())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse drag"""
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._update_color_from_position(event.position().toPoint())

    def _update_color_from_position(self, pos: QPoint) -> None:
        """Update color based on mouse position with improved precision"""
        center = self.rect().center()
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()
        distance = math.sqrt(dx * dx + dy * dy)

        # Check wheel area (hue selection)
        outer_radius = self._wheel_radius
        inner_radius = outer_radius - self._wheel_thickness

        if inner_radius <= distance <= outer_radius:
            # Update hue
            angle = math.atan2(dy, dx)
            hue = (angle + math.pi) / (2 * math.pi)
            if hue < 0:
                hue += 1.0
            
            new_color = QColor.fromHsvF(
                hue,
                self._color_state.current.hsvSaturationF(),
                self._color_state.current.valueF()
            )
            
            if self._color_state.update_color(new_color):
                self.colorChanged.emit(self._color_state.current)
                self.update()

        else:
            # Check S/V square
            sv_size = int((self._wheel_radius - self._wheel_thickness - 15) * self._sv_size * 2)
            sv_rect = QRect(
                center.x() - sv_size // 2,
                center.y() - sv_size // 2,
                sv_size,
                sv_size
            )

            if sv_rect.contains(pos):
                # Update saturation and value
                relative_x = pos.x() - sv_rect.left()
                relative_y = pos.y() - sv_rect.top()
                
                saturation = max(0.0, min(1.0, relative_x / sv_rect.width()))
                value = max(0.0, min(1.0, 1.0 - (relative_y / sv_rect.height())))
                
                new_color = QColor.fromHsvF(
                    self._color_state.current.hsvHueF(),
                    saturation,
                    value
                )
                
                if self._color_state.update_color(new_color):
                    self.colorChanged.emit(self._color_state.current)
                    self.update()


class FluentColorPicker(QWidget):
    """Complete modern color picker with all features"""

    colorChanged = Signal(QColor)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._color_state = ColorState()
        
        # Modern predefined color palette with better accessibility
        self._predefined_colors: List[QColor] = [
            # Primary colors
            QColor("#FF6B6B"), QColor("#4ECDC4"), QColor("#45B7D1"), QColor("#96CEB4"),
            QColor("#FECA57"), QColor("#FF9FF3"), QColor("#54A0FF"), QColor("#5F27CD"),
            # Secondary colors  
            QColor("#00D2D3"), QColor("#FF9F43"), QColor("#10AC84"), QColor("#EE5A6F"),
            QColor("#0078d4"), QColor("#005a9e"), QColor("#004578"), QColor("#002c4a"),
            # Accent colors
            QColor("#6264A7"), QColor("#8764B8"), QColor("#8E8CD8"), QColor("#B4A7D6"),
            QColor("#D13438"), QColor("#FF4B4B"), QColor("#FF6B6B"), QColor("#FF9999")
        ]

        self._setup_ui()
        self._setup_style()
        self.set_color(self._color_state.current)  # Initialize displays

        # Connect theme manager if available
        if THEME_AVAILABLE and theme_manager and hasattr(theme_manager, 'theme_changed'):
            try:
                theme_manager.theme_changed.connect(self._on_theme_changed)
            except (AttributeError, RuntimeError):
                pass  # Graceful fallback

    def _setup_ui(self) -> None:
        """Setup modern UI layout"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        self._setup_current_color(layout)
        self._setup_color_wheel(layout)
        self._setup_rgb_sliders(layout)
        self._setup_predefined_colors(layout)
        self._setup_hex_input(layout)
        self._setup_buttons(layout)

    def _setup_current_color(self, layout: QVBoxLayout) -> None:
        """Setup current color display with preview"""
        self._color_display = QFrame()
        self._color_display.setFixedHeight(80)  # Taller for better visibility
        self._color_display.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        layout.addWidget(self._color_display)

    def _setup_color_wheel(self, layout: QVBoxLayout) -> None:
        """Setup enhanced color wheel"""
        wheel_layout = QHBoxLayout()
        wheel_layout.addStretch()
        
        self._color_wheel = FluentColorWheel()
        self._color_wheel.colorChanged.connect(self._on_wheel_color_changed)
        
        wheel_layout.addWidget(self._color_wheel)
        wheel_layout.addStretch()
        layout.addLayout(wheel_layout)

    def _setup_rgb_sliders(self, layout: QVBoxLayout) -> None:
        """Setup RGB sliders with improved layout"""
        rgb_group = QFrame()
        rgb_layout = QGridLayout(rgb_group)
        rgb_layout.setSpacing(8)
        
        self._rgb_sliders = {}
        self._rgb_labels = {}

        for i, (component, color) in enumerate([('R', '#ff4444'), ('G', '#44ff44'), ('B', '#4444ff')]):
            label = QLabel(f"{component}:")
            label.setMinimumWidth(20)
            
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 255)
            slider.valueChanged.connect(self._on_rgb_slider_changed)
            
            value_label = QLabel("0")
            value_label.setMinimumWidth(35)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

            rgb_layout.addWidget(label, i, 0)
            rgb_layout.addWidget(slider, i, 1)
            rgb_layout.addWidget(value_label, i, 2)

            self._rgb_sliders[component] = slider
            self._rgb_labels[component] = value_label

        layout.addWidget(rgb_group)

    def _setup_predefined_colors(self, layout: QVBoxLayout) -> None:
        """Setup predefined color palette with better organization"""
        palette_label = QLabel("预设颜色:")
        palette_label.setStyleSheet("font-weight: bold; margin-bottom: 4px;")
        layout.addWidget(palette_label)
        
        palette_widget = QWidget()
        palette_layout = QGridLayout(palette_widget)
        palette_layout.setSpacing(6)
        
        rows, cols = 3, 8
        for i, color_val in enumerate(self._predefined_colors[:rows * cols]):
            btn = FluentColorButton(color_val)
            btn.colorSelected.connect(self._on_predefined_color_selected)
            palette_layout.addWidget(btn, i // cols, i % cols)
            
        layout.addWidget(palette_widget)

    def _setup_hex_input(self, layout: QVBoxLayout) -> None:
        """Setup hex input with validation"""
        hex_layout = QHBoxLayout()
        hex_label = QLabel("十六进制:")
        hex_label.setMinimumWidth(70)
        
        self._hex_input = QLineEdit()
        self._hex_input.setPlaceholderText("#RRGGBB")
        self._hex_input.setMaxLength(7)
        self._hex_input.textChanged.connect(self._on_hex_changed)
        
        hex_layout.addWidget(hex_label)
        hex_layout.addWidget(self._hex_input)
        layout.addLayout(hex_layout)

    def _setup_buttons(self, layout: QVBoxLayout) -> None:
        """Setup action buttons"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        more_btn = QPushButton("更多颜色...")
        more_btn.clicked.connect(self._open_color_dialog)
        more_btn.setMinimumWidth(100)
        
        button_layout.addWidget(more_btn)
        layout.addLayout(button_layout)

    def _setup_style(self) -> None:
        """Setup style with theme fallbacks"""
        self._update_color_display()  # Update display with current color
        
        # Default colors
        default_colors = {
            'text_primary': '#000000',
            'surface': '#ffffff', 
            'border': '#d1d1d1',
            'background': '#f5f5f5',
            'primary': '#0078d4'
        }
        
        # Get theme colors with fallbacks
        if THEME_AVAILABLE and theme_manager:
            try:
                colors = {
                    key: theme_manager.get_color(key).name()
                    for key in default_colors.keys()
                }
            except (AttributeError, TypeError):
                colors = default_colors
        else:
            colors = default_colors
            
        # Apply stylesheet with safe color values
        self.setStyleSheet(f"""
            QLabel {{ 
                color: {colors['text_primary']}; 
                font-family: "Segoe UI", sans-serif; 
            }}
            QLineEdit {{ 
                background-color: {colors['surface']}; 
                border: 1px solid {colors['border']}; 
                border-radius: 4px; 
                padding: 6px 8px; 
                color: {colors['text_primary']}; 
            }}
            QSlider::groove:horizontal {{ 
                border: 1px solid {colors['border']}; 
                height: 6px; 
                border-radius: 3px; 
                background: {colors['background']}; 
            }}
            QSlider::handle:horizontal {{ 
                background: {colors['primary']}; 
                border: 1px solid {colors['border']}; 
                width: 16px; 
                border-radius: 8px; 
                margin: -5px 0; 
            }}
        """)

    def set_color(self, color: QColor) -> None:
        """Set current color and update all UI elements"""
        if isinstance(color, QColor) and color.isValid():
            if self._color_state.update_color(color):
                self._update_all_displays()
                self.colorChanged.emit(self._color_state.current)

    def get_color(self) -> QColor:
        """Get current color"""
        return self._color_state.current

    def _update_color_display(self) -> None:
        """Update the color preview display"""
        if hasattr(self, '_color_display'):
            color_name = self._color_state.current.name()
            self._color_display.setStyleSheet(f"""
                QFrame {{
                    background-color: {color_name};
                    border: 2px solid #ccc;
                    border-radius: 6px;
                }}
            """)

    def _update_all_displays(self) -> None:
        """Update all UI components to reflect current color"""
        self._update_color_display()

        # Update RGB sliders and labels
        if hasattr(self, '_rgb_sliders'):
            color = self._color_state.current
            for component in ['R', 'G', 'B']:
                slider = self._rgb_sliders[component]
                label = self._rgb_labels[component]
                value = getattr(color, component.lower())()
                
                slider.blockSignals(True)
                slider.setValue(value)
                slider.blockSignals(False)
                label.setText(str(value))

        # Update hex input
        if hasattr(self, '_hex_input'):
            self._hex_input.blockSignals(True)
            self._hex_input.setText(self._color_state.current.name().upper())
            self._hex_input.blockSignals(False)

        # Update color wheel
        if hasattr(self, '_color_wheel'):
            self._color_wheel.blockSignals(True)
            self._color_wheel.set_color(self._color_state.current)
            self._color_wheel.blockSignals(False)

    @Slot(QColor)
    def _on_wheel_color_changed(self, color: QColor) -> None:
        """Handle color wheel changes"""
        self.set_color(color)

    @Slot()
    def _on_rgb_slider_changed(self) -> None:
        """Handle RGB slider changes"""
        if hasattr(self, '_rgb_sliders'):
            r = self._rgb_sliders['R'].value()
            g = self._rgb_sliders['G'].value()
            b = self._rgb_sliders['B'].value()
            self.set_color(QColor(r, g, b))

    @Slot(QColor)
    def _on_predefined_color_selected(self, color: QColor) -> None:
        """Handle predefined color selection with animation"""
        self.set_color(color)
        
        # Add subtle feedback animation
        if ANIMATIONS_AVAILABLE:
            try:
                FluentMicroInteraction.pulse_animation(self, scale=1.02)
            except Exception:
                pass

    @Slot(str)
    def _on_hex_changed(self, text: str) -> None:
        """Handle hex input changes with validation"""
        text = text.strip().upper()
        if text.startswith('#') and len(text) in (7, 9):  # #RRGGBB or #AARRGGBB
            color = QColor(text)
            if color.isValid():
                self.set_color(color)

    @Slot()
    def _open_color_dialog(self) -> None:
        """Open system color dialog"""
        color = QColorDialog.getColor(
            self._color_state.current, 
            self, 
            "选择颜色",
            QColorDialog.ColorDialogOption.ShowAlphaChannel  # Support alpha
        )
        if color.isValid():
            self.set_color(color)

    @Slot()
    def _on_theme_changed(self) -> None:
        """Handle theme changes"""
        self._setup_style()
        self._update_all_displays()
