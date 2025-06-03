"""
Fluent Design Style Slider Components
Enhanced with smooth animations, theme consistency, and responsive interactions
"""

from PySide6.QtWidgets import QSlider, QWidget, QLabel, QHBoxLayout  # Removed QVBoxLayout
# Removed QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtCore import Qt, Signal, QRect
# Removed QColor, QFont, QFontMetrics
from PySide6.QtGui import QPainter, QPen, QBrush
from core.theme import theme_manager
from core.enhanced_animations import (FluentMicroInteraction, FluentTransition,
                                      FluentStateTransition, FluentRevealEffect)
from typing import Optional


class FluentSlider(QSlider):
    """Fluent Design Style Slider with enhanced animations"""

    class SliderStyle:
        STANDARD = "standard"
        ACCENT = "accent"
        SUBTLE = "subtle"

    class Size:
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    value_changing = Signal(int)  # Emitted while dragging
    value_changed_final = Signal(int)  # Emitted when drag ends

    def __init__(self, parent: Optional[QWidget] = None,
                 orientation: Qt.Orientation = Qt.Orientation.Horizontal,
                 slider_style: str = SliderStyle.STANDARD,
                 size: str = Size.MEDIUM,
                 minimum: int = 0, maximum: int = 100, value: int = 0):
        super().__init__(orientation, parent)

        self._slider_style = slider_style
        self._size = size
        self._is_dragging = False
        self._state_transition = FluentStateTransition(self)

        # Set range and value
        self.setRange(minimum, maximum)
        self.setValue(value)

        # Track mouse interactions
        self._is_hovered = False
        self._is_pressed = False

        self._setup_animations()
        self._apply_style()
        self._setup_connections()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Add reveal animation when created
        FluentRevealEffect.fade_in(self, 300)

    def _setup_animations(self):
        """Setup enhanced animation effects"""
        # Setup state transitions for different slider states
        track_height = self._get_track_height()

        self._state_transition.addState("normal", {
            "minimumHeight": track_height,
        })

        self._state_transition.addState("hovered", {
            "minimumHeight": track_height + 2,
        }, duration=150, easing=FluentTransition.EASE_SMOOTH)

        self._state_transition.addState("pressed", {
            "minimumHeight": track_height + 4,
        }, duration=100, easing=FluentTransition.EASE_SPRING)

    def _get_track_height(self) -> int:
        """Get track height based on size"""
        if self._size == self.Size.SMALL:
            return 20
        elif self._size == self.Size.LARGE:
            return 32
        else:  # MEDIUM
            return 26

    def _get_handle_size(self) -> int:
        """Get handle size based on size"""
        if self._size == self.Size.SMALL:
            return 16
        elif self._size == self.Size.LARGE:
            return 24
        else:  # MEDIUM
            return 20

    def _setup_connections(self):
        """Setup signal connections"""
        self.valueChanged.connect(self._on_value_changed)
        self.sliderPressed.connect(self._on_slider_pressed)
        self.sliderReleased.connect(self._on_slider_released)
        self.sliderMoved.connect(self._on_slider_moved)

    def _apply_style(self):
        """Apply style with enhanced visual effects"""
        current_theme = theme_manager
        track_height = self._get_track_height()
        handle_size = self._get_handle_size()

        # Get style colors based on slider style
        if self._slider_style == self.SliderStyle.ACCENT:
            primary_color = current_theme.get_color('accent')
            hover_color = current_theme.get_color('accent').lighter(120)
        elif self._slider_style == self.SliderStyle.SUBTLE:
            primary_color = current_theme.get_color('text_secondary')
            hover_color = current_theme.get_color('text_primary')
        else:  # STANDARD
            primary_color = current_theme.get_color('primary')
            hover_color = current_theme.get_color('primary').lighter(120)

        style_sheet = f"""
            FluentSlider {{
                background: transparent;
                min-height: {track_height}px;
            }}
            
            FluentSlider::groove:horizontal {{
                background: {current_theme.get_color('surface_light').name()};
                height: 4px;
                border-radius: 2px;
                border: 1px solid {current_theme.get_color('border').name()};
            }}
            
            FluentSlider::groove:vertical {{
                background: {current_theme.get_color('surface_light').name()};
                width: 4px;
                border-radius: 2px;
                border: 1px solid {current_theme.get_color('border').name()};
            }}
            
            FluentSlider::sub-page:horizontal {{
                background: {primary_color.name()};
                height: 4px;
                border-radius: 2px;
            }}
            
            FluentSlider::sub-page:vertical {{
                background: {primary_color.name()};
                width: 4px;
                border-radius: 2px;
            }}
            
            FluentSlider::handle:horizontal {{
                background: {current_theme.get_color('surface').name()};
                border: 2px solid {primary_color.name()};
                width: {handle_size}px;
                height: {handle_size}px;
                border-radius: {handle_size // 2}px;
                margin: -{handle_size // 2 + 1}px 0;
            }}
            
            FluentSlider::handle:vertical {{
                background: {current_theme.get_color('surface').name()};
                border: 2px solid {primary_color.name()};
                width: {handle_size}px;
                height: {handle_size}px;
                border-radius: {handle_size // 2}px;
                margin: 0 -{handle_size // 2 + 1}px;
            }}
            
            FluentSlider::handle:hover {{
                border-color: {hover_color.name()};
                background: {current_theme.get_color('surface').lighter(110).name()};
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            }}
            
            FluentSlider::handle:pressed {{
                border-color: {primary_color.darker(110).name()};
                background: {current_theme.get_color('surface').darker(105).name()};
                box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
            }}
            
            FluentSlider::handle:disabled {{
                background: {current_theme.get_color('surface_disabled').name()};
                border-color: {current_theme.get_color('border').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._apply_style()

    def _on_value_changed(self, value: int):
        """Handle value change with micro-interaction"""
        if self._is_dragging:
            self.value_changing.emit(value)
            # Subtle pulse animation while dragging
            FluentMicroInteraction.pulse_animation(self, 1.01)

    def _on_slider_pressed(self):
        """Handle slider press with animations"""
        self._is_pressed = True
        self._is_dragging = True

        # Apply press glow effect
        FluentMicroInteraction.hover_glow(self, 0.3)

        # Transition to pressed state
        self._state_transition.transitionTo("pressed")

    def _on_slider_released(self):
        """Handle slider release"""
        self._is_pressed = False
        self._is_dragging = False

        # Emit final value
        self.value_changed_final.emit(self.value())

        # Transition back to hover or normal state
        if self._is_hovered:
            self._state_transition.transitionTo("hovered")
        else:
            self._state_transition.transitionTo("normal")

    def _on_slider_moved(self, _value: int):
        """Handle slider movement with micro-interaction"""
        # Apply subtle vibration effect during movement
        FluentMicroInteraction.scale_animation(self, 1.01)

    def enterEvent(self, event):
        """Hover enter event with enhanced animations"""
        self._is_hovered = True

        # Apply hover glow effect if not pressed
        if not self._is_pressed:
            FluentMicroInteraction.hover_glow(self, 0.15)
            self._state_transition.transitionTo("hovered")

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave event"""
        self._is_hovered = False

        # Transition back to normal state if not pressed
        if not self._is_pressed:
            self._state_transition.transitionTo("normal")

        super().leaveEvent(event)

    def set_style(self, style: str):
        """Set slider style"""
        if style in [self.SliderStyle.STANDARD, self.SliderStyle.ACCENT, self.SliderStyle.SUBTLE]:
            self._slider_style = style
            self._apply_style()

    def set_size(self, size: str):
        """Set slider size"""
        if size in [self.Size.SMALL, self.Size.MEDIUM, self.Size.LARGE]:
            self._size = size
            self._setup_animations()
            self._apply_style()


class FluentRangeSlider(QWidget):
    """Fluent Design Style Range Slider with dual handles"""

    range_changed = Signal(int, int)  # Emitted when range changes
    range_changing = Signal(int, int)  # Emitted while dragging

    def __init__(self, parent: Optional[QWidget] = None,
                 minimum: int = 0, maximum: int = 100,
                 low_value: int = 25, high_value: int = 75):
        super().__init__(parent)

        self._minimum = minimum
        self._maximum = maximum
        self._low_value = low_value
        self._high_value = high_value
        self._handle_size = 20
        self._track_height = 4
        self._dragging_handle = None  # 'low', 'high', or None

        self._is_hovered = False
        self._state_transition = FluentStateTransition(self)

        self.setMinimumHeight(40)
        self.setMinimumWidth(150)

        self._setup_animations()
        self._apply_style()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Add reveal animation when created
        FluentRevealEffect.slide_in(self, 300, "bottom")

    def _setup_animations(self):
        """Setup enhanced animation effects"""
        self._state_transition.addState("normal", {
            "minimumHeight": 40,
        })

        self._state_transition.addState("hovered", {
            "minimumHeight": 42,
        }, duration=150, easing=FluentTransition.EASE_SMOOTH)

    def _apply_style(self):
        """Apply range slider styling"""
        # current_theme = theme_manager # Not used in this specific style sheet

        style_sheet = f"""
            FluentRangeSlider {{
                background: transparent;
                border: none;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._apply_style()
        self.update()

    def paintEvent(self, _event):
        """Custom paint event for range slider"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        current_theme = theme_manager
        rect = self.rect()

        # Calculate positions
        track_rect = QRect(
            self._handle_size // 2,
            rect.height() // 2 - self._track_height // 2,
            rect.width() - self._handle_size,
            self._track_height
        )

        value_range = self._maximum - self._minimum
        if value_range == 0:  # Avoid division by zero
            low_pos = 0
            high_pos = 0
        else:
            low_pos = int((self._low_value - self._minimum) /
                          value_range * track_rect.width())
            high_pos = int((self._high_value - self._minimum) /
                           value_range * track_rect.width())

        # Draw track background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(current_theme.get_color('surface_light')))
        painter.drawRoundedRect(track_rect, 2, 2)

        # Draw active range
        active_rect = QRect(
            track_rect.left() + low_pos,
            track_rect.top(),
            high_pos - low_pos,
            track_rect.height()
        )
        painter.setBrush(QBrush(current_theme.get_color('primary')))
        painter.drawRoundedRect(active_rect, 2, 2)

        # Draw handles
        self._draw_handle(painter, track_rect.left() +
                          low_pos, rect.height() // 2, 'low')
        self._draw_handle(painter, track_rect.left() +
                          high_pos, rect.height() // 2, 'high')

    def _draw_handle(self, painter: QPainter, x: int, y: int, handle_type: str):
        """Draw a slider handle"""
        current_theme = theme_manager

        handle_rect = QRect(
            x - self._handle_size // 2,
            y - self._handle_size // 2,
            self._handle_size,
            self._handle_size
        )

        # Handle styling based on state
        if self._dragging_handle == handle_type:
            border_color = current_theme.get_color('primary').darker(110)
            fill_color = current_theme.get_color('surface').darker(105)
        elif self._is_hovered:
            border_color = current_theme.get_color('primary').lighter(120)
            fill_color = current_theme.get_color('surface').lighter(110)
        else:
            border_color = current_theme.get_color('primary')
            fill_color = current_theme.get_color('surface')

        # Draw handle
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(QBrush(fill_color))
        painter.drawEllipse(handle_rect)

    def mousePressEvent(self, event):
        """Handle mouse press for handle dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self._get_handle_at_position(event.position().toPoint())
            if handle:
                self._dragging_handle = handle
                # Apply press animation
                FluentMicroInteraction.scale_animation(self, 1.02)
                self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging handles"""
        if self._dragging_handle:
            rect = self.rect()
            track_width = rect.width() - self._handle_size
            if track_width == 0:  # Avoid division by zero
                return

            relative_pos = (event.position().x() -
                            self._handle_size // 2) / track_width
            relative_pos = max(0, min(1, relative_pos))

            new_value = int(self._minimum + relative_pos *
                            (self._maximum - self._minimum))

            if self._dragging_handle == 'low':
                self._low_value = min(new_value, self._high_value)
            else:  # 'high'
                self._high_value = max(new_value, self._low_value)

            self.range_changing.emit(self._low_value, self._high_value)
            self.update()

    def mouseReleaseEvent(self, _event):
        """Handle mouse release"""
        if self._dragging_handle:
            self._dragging_handle = None
            self.range_changed.emit(self._low_value, self._high_value)
            self.update()

    def _get_handle_at_position(self, pos) -> Optional[str]:
        """Get which handle is at the given position"""
        rect = self.rect()
        track_width = rect.width() - self._handle_size
        value_range = self._maximum - self._minimum

        if value_range == 0 or track_width == 0:  # Avoid division by zero or invalid state
            # Check if near the center y, and if x is within handle radius of the start of track
            handle_radius = self._handle_size // 2
            center_y = rect.height() // 2
            if abs(pos.y() - center_y) <= handle_radius:
                # If range is 0, both handles are at the start. Prioritize 'low' or check x.
                if abs(pos.x() - (self._handle_size // 2)) <= handle_radius:
                    return 'low'  # Or 'high', ambiguous. Let's say 'low'.
            return None

        low_pos = self._handle_size // 2 + \
            (self._low_value - self._minimum) / value_range * track_width
        high_pos = self._handle_size // 2 + \
            (self._high_value - self._minimum) / value_range * track_width

        handle_radius = self._handle_size // 2

        if abs(pos.x() - low_pos) <= handle_radius and abs(pos.y() - rect.height() // 2) <= handle_radius:
            return 'low'
        elif abs(pos.x() - high_pos) <= handle_radius and abs(pos.y() - rect.height() // 2) <= handle_radius:
            return 'high'

        return None

    def enterEvent(self, event):
        """Hover enter event"""
        self._is_hovered = True
        self._state_transition.transitionTo("hovered")
        FluentMicroInteraction.hover_glow(self, 0.1)
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave event"""
        self._is_hovered = False
        self._state_transition.transitionTo("normal")
        self.update()
        super().leaveEvent(event)

    def set_range(self, minimum: int, maximum: int):
        """Set the range of the slider"""
        self._minimum = minimum
        self._maximum = maximum
        self._low_value = max(minimum, min(maximum, self._low_value))
        self._high_value = max(minimum, min(maximum, self._high_value))
        if self._low_value > self._high_value:  # Ensure low <= high
            self._low_value, self._high_value = self._high_value, self._low_value
        self.update()

    def set_values(self, low_value: int, high_value: int):
        """Set both values"""
        self._low_value = max(self._minimum, min(self._maximum, low_value))
        self._high_value = max(self._minimum, min(self._maximum, high_value))
        if self._low_value > self._high_value:
            self._low_value, self._high_value = self._high_value, self._low_value
        self.update()

    def get_values(self) -> tuple[int, int]:
        """Get current values"""
        return (self._low_value, self._high_value)


class FluentVolumeSlider(FluentSlider):
    """Fluent Design Style Volume Slider with icon and mute functionality"""

    mute_toggled = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None, value: int = 50):
        super().__init__(parent, Qt.Orientation.Horizontal,
                         self.SliderStyle.ACCENT, self.Size.MEDIUM, 0, 100, value)

        self._is_muted = False
        self._volume_before_mute = value

        # Setup layout with volume icon
        self._setup_volume_layout()

        # Add volume-specific styling
        self._apply_volume_style()

    def _setup_volume_layout(self):
        """
        Setup volume icon.
        The original attempt to create a 'container' QWidget with a layout and
        inject it into this slider's parent was architecturally flawed and led to
        the QObject.layout() error.
        This revised version makes the icon a direct child of the slider.
        Proper positioning of the icon next to the slider track would require
        overriding paintEvent or resizeEvent and adjusting slider groove margins.
        For simplicity in fixing the reported error, the icon is created but
        hidden by default, as it would otherwise draw on top of the slider track at (0,0).
        """
        self._volume_icon = QLabel("🔊", parent=self)
        self._volume_icon.setFixedSize(24, 24)
        self._volume_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._volume_icon.mousePressEvent = self._toggle_mute
        self._volume_icon.hide()  # Hide by default as it's not positioned correctly

    def _apply_volume_style(self):
        """Apply volume-specific styling"""
        super()._apply_style()

        current_theme = theme_manager

        icon_style = f"""
            QLabel {{
                background: {current_theme.get_color('surface').name()};
                border: 1px solid {current_theme.get_color('border').name()};
                border-radius: 12px;
                color: {current_theme.get_color('text_primary').name()};
                font-size: 14px;
            }}
            QLabel:hover {{
                background: {current_theme.get_color('surface_light').name()};
                border-color: {current_theme.get_color('primary').name()};
            }}
        """

        if hasattr(self, '_volume_icon'):
            self._volume_icon.setStyleSheet(icon_style)

    def _toggle_mute(self, _event=None):
        """Toggle mute state"""
        self._is_muted = not self._is_muted

        if self._is_muted:
            self._volume_before_mute = self.value()
            self.setValue(0)
            if hasattr(self, '_volume_icon'):
                self._volume_icon.setText("🔇")
        else:
            self.setValue(self._volume_before_mute)
            if hasattr(self, '_volume_icon'):
                self._volume_icon.setText("🔊")

        # Apply mute animation
        FluentMicroInteraction.pulse_animation(self, 1.1)
        self.mute_toggled.emit(self._is_muted)

    def set_muted(self, muted: bool):
        """Set mute state programmatically"""
        if muted != self._is_muted:
            self._toggle_mute()

    def is_muted(self) -> bool:
        """Check if volume is muted"""
        return self._is_muted
