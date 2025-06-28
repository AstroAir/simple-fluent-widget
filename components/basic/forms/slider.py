"""
Fluent Design Style Slider Components
Enhanced with smooth animations, theme consistency, and responsive interactions
Optimized for performance
"""

from PySide6.QtWidgets import QSlider, QWidget, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QPen, QBrush
from core.theme import theme_manager
from core.enhanced_animations import (FluentMicroInteraction, FluentTransition,
                                      FluentStateTransition, FluentRevealEffect)
from typing import Optional
from functools import lru_cache


class FluentSlider(QSlider):
    """Fluent Design Style Slider with enhanced animations and optimized performance"""

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

        # Cache for style calculations
        self._cached_style = None
        self._cached_theme = None

        self._setup_animations()
        self._apply_style()
        self._setup_connections()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Add reveal animation when created
        FluentRevealEffect.fade_in(self, 300)

    @lru_cache(maxsize=8)
    def _get_track_height(self) -> int:
        """Get track height based on size with caching"""
        if self._size == self.Size.SMALL:
            return 20
        elif self._size == self.Size.LARGE:
            return 32
        else:  # MEDIUM
            return 26

    @lru_cache(maxsize=8)
    def _get_handle_size(self) -> int:
        """Get handle size based on size with caching"""
        if self._size == self.Size.SMALL:
            return 16
        elif self._size == self.Size.LARGE:
            return 24
        else:  # MEDIUM
            return 20

    def _setup_animations(self):
        """Setup optimized animation effects"""
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

    def _setup_connections(self):
        """Setup optimized signal connections"""
        self.valueChanged.connect(self._on_value_changed)
        self.sliderPressed.connect(self._on_slider_pressed)
        self.sliderReleased.connect(self._on_slider_released)
        self.sliderMoved.connect(self._on_slider_moved)

    def _apply_style(self):
        """Apply style with optimized calculations"""
        current_theme = theme_manager

        # Only recalculate if theme or style has changed
        if self._cached_theme == current_theme and self._cached_style == self._slider_style:
            return

        self._cached_theme = current_theme
        self._cached_style = self._slider_style

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

        # Pre-calculate color names for efficiency
        primary_name = primary_color.name()
        hover_name = hover_color.name()
        primary_darker = primary_color.darker(110).name()
        surface = current_theme.get_color('surface').name()
        surface_light = current_theme.get_color('surface_light').name()
        border = current_theme.get_color('border').name()
        surface_lighter = current_theme.get_color(
            'surface').lighter(110).name()
        surface_darker = current_theme.get_color('surface').darker(105).name()
        surface_disabled = current_theme.get_color('surface_disabled').name()

        style_sheet = f"""
            FluentSlider {{
                background: transparent;
                min-height: {track_height}px;
            }}
            
            FluentSlider::groove:horizontal {{
                background: {surface_light};
                height: 4px;
                border-radius: 2px;
                border: 1px solid {border};
            }}
            
            FluentSlider::groove:vertical {{
                background: {surface_light};
                width: 4px;
                border-radius: 2px;
                border: 1px solid {border};
            }}
            
            FluentSlider::sub-page:horizontal {{
                background: {primary_name};
                height: 4px;
                border-radius: 2px;
            }}
            
            FluentSlider::sub-page:vertical {{
                background: {primary_name};
                width: 4px;
                border-radius: 2px;
            }}
            
            FluentSlider::handle:horizontal {{
                background: {surface};
                border: 2px solid {primary_name};
                width: {handle_size}px;
                height: {handle_size}px;
                border-radius: {handle_size // 2}px;
                margin: -{handle_size // 2 + 1}px 0;
            }}
            
            FluentSlider::handle:vertical {{
                background: {surface};
                border: 2px solid {primary_name};
                width: {handle_size}px;
                height: {handle_size}px;
                border-radius: {handle_size // 2}px;
                margin: 0 -{handle_size // 2 + 1}px;
            }}
            
            FluentSlider::handle:hover {{
                border-color: {hover_name};
                background: {surface_lighter};
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            }}
            
            FluentSlider::handle:pressed {{
                border-color: {primary_darker};
                background: {surface_darker};
                box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
            }}
            
            FluentSlider::handle:disabled {{
                background: {surface_disabled};
                border-color: {border};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change efficiently"""
        self._cached_theme = None
        self._apply_style()

    def _on_value_changed(self, value: int):
        """Handle value change with optimized micro-interaction"""
        if self._is_dragging:
            self.value_changing.emit(value)
            FluentMicroInteraction.pulse_animation(self, 1.01)

    def _on_slider_pressed(self):
        """Handle slider press with optimized animations"""
        self._is_pressed = True
        self._is_dragging = True

        FluentMicroInteraction.hover_glow(self, 0.3)
        self._state_transition.transitionTo("pressed")

    def _on_slider_released(self):
        """Handle slider release with optimized transitions"""
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
        """Handle slider movement with optimized micro-interaction"""
        # Use lighter animation for better performance
        FluentMicroInteraction.scale_animation(self, 1.01)

    def enterEvent(self, event):
        """Hover enter event with optimized animations"""
        self._is_hovered = True

        if not self._is_pressed:
            FluentMicroInteraction.hover_glow(self, 0.15)
            self._state_transition.transitionTo("hovered")

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave event with optimized transitions"""
        self._is_hovered = False

        if not self._is_pressed:
            self._state_transition.transitionTo("normal")

        super().leaveEvent(event)

    def set_style(self, style: str):
        """Set slider style efficiently"""
        if style in [self.SliderStyle.STANDARD, self.SliderStyle.ACCENT, self.SliderStyle.SUBTLE]:
            if self._slider_style != style:
                self._slider_style = style
                self._cached_style = None  # Reset style cache
                self._apply_style()

    def set_size(self, size: str):
        """Set slider size efficiently"""
        if size in [self.Size.SMALL, self.Size.MEDIUM, self.Size.LARGE]:
            if self._size != size:
                self._size = size

                # Clear cached calculations
                self._get_track_height.cache_clear()
                self._get_handle_size.cache_clear()

                self._setup_animations()
                self._apply_style()


class FluentRangeSlider(QWidget):
    """Optimized Fluent Design Style Range Slider with dual handles"""

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

        # Cache for layout calculations
        self._track_rect = None
        self._low_handle_pos = None
        self._high_handle_pos = None
        self._value_range = None
        self._cached_theme = None

        self.setMinimumHeight(40)
        self.setMinimumWidth(150)

        self._setup_animations()
        self._apply_style()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Add reveal animation when created
        FluentRevealEffect.slide_in(self, 300, "bottom")

    def _setup_animations(self):
        """Setup optimized animation effects"""
        self._state_transition.addState("normal", {
            "minimumHeight": 40,
        })

        self._state_transition.addState("hovered", {
            "minimumHeight": 42,
        }, duration=150, easing=FluentTransition.EASE_SMOOTH)

    def _apply_style(self):
        """Apply range slider styling efficiently"""
        current_theme = theme_manager

        # Only update if theme changed
        if self._cached_theme == current_theme:
            return

        self._cached_theme = current_theme
        self.setStyleSheet(
            "FluentRangeSlider { background: transparent; border: none; }")

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change efficiently"""
        self._cached_theme = None
        self._apply_style()
        self.update()

    def _calculate_layout(self):
        """Pre-calculate layout values to optimize paint event"""
        rect = self.rect()

        # Calculate track rectangle
        self._track_rect = QRect(
            self._handle_size // 2,
            rect.height() // 2 - self._track_height // 2,
            rect.width() - self._handle_size,
            self._track_height
        )

        # Calculate value range once
        self._value_range = self._maximum - self._minimum

        # Calculate handle positions
        if self._value_range == 0:  # Avoid division by zero
            self._low_handle_pos = 0
            self._high_handle_pos = 0
        else:
            self._low_handle_pos = int((self._low_value - self._minimum) /
                                       self._value_range * self._track_rect.width())
            self._high_handle_pos = int((self._high_value - self._minimum) /
                                        self._value_range * self._track_rect.width())

        # Cache the center y-coordinate for handle drawing
        self._center_y = rect.height() // 2

    def paintEvent(self, _event):
        """Optimized paint event for range slider"""
        # Pre-calculate all layout values
        self._calculate_layout()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        current_theme = theme_manager

        # Get colors once and reuse
        surface_light = current_theme.get_color('surface_light')
        primary_color = current_theme.get_color('primary')

        # Draw track background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(surface_light))
        if (
            self._track_rect is not None
            and self._low_handle_pos is not None
            and self._high_handle_pos is not None
        ):
            painter.drawRoundedRect(self._track_rect, 2, 2)

            # Draw active range
            active_rect = QRect(
                self._track_rect.left() + self._low_handle_pos,
                self._track_rect.top(),
                self._high_handle_pos - self._low_handle_pos,
                self._track_rect.height()
            )
            painter.setBrush(QBrush(primary_color))
            painter.drawRoundedRect(active_rect, 2, 2)

            # Draw handles
            self._draw_handle(painter, self._track_rect.left(
            ) + self._low_handle_pos, self._center_y, 'low')
            self._draw_handle(painter, self._track_rect.left(
            ) + self._high_handle_pos, self._center_y, 'high')

    def _draw_handle(self, painter: QPainter, x: int, y: int, handle_type: str):
        """Draw a slider handle with optimized styling"""
        current_theme = theme_manager

        # Optimize rect calculation
        half_size = self._handle_size // 2
        handle_rect = QRect(
            x - half_size,
            y - half_size,
            self._handle_size,
            self._handle_size
        )

        # Get colors once and reuse
        primary = current_theme.get_color('primary')
        surface = current_theme.get_color('surface')

        # Handle styling based on state
        if self._dragging_handle == handle_type:
            border_color = primary.darker(110)
            fill_color = surface.darker(105)
        elif self._is_hovered:
            border_color = primary.lighter(120)
            fill_color = surface.lighter(110)
        else:
            border_color = primary
            fill_color = surface

        # Draw handle with minimal state changes
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(QBrush(fill_color))
        painter.drawEllipse(handle_rect)

    def mousePressEvent(self, event):
        """Handle mouse press for handle dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self._get_handle_at_position(event.position().toPoint())
            if handle:
                self._dragging_handle = handle
                FluentMicroInteraction.scale_animation(self, 1.02)
                self.update()

    def mouseMoveEvent(self, event):
        """Optimized mouse move for dragging handles"""
        if not self._dragging_handle:
            return

        rect = self.rect()
        track_width = rect.width() - self._handle_size
        if track_width <= 0:  # Avoid division by zero
            return

        # Optimize calculation of position
        x_pos = event.position().x()
        relative_pos = max(
            0, min(1, (x_pos - self._handle_size // 2) / track_width))
        new_value = int(self._minimum + relative_pos *
                        (self._maximum - self._minimum))

        # Only update if value actually changed
        if self._dragging_handle == 'low':
            if self._low_value != min(new_value, self._high_value):
                self._low_value = min(new_value, self._high_value)
                self.range_changing.emit(self._low_value, self._high_value)
                self.update()
        else:  # 'high'
            if self._high_value != max(new_value, self._low_value):
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
        """Optimized handle hit testing"""
        # Calculate layout if not already done
        if self._track_rect is None:
            self._calculate_layout()

        # Early exit for invalid states
        if (
            self._track_rect is None
            or self._low_handle_pos is None
            or self._high_handle_pos is None
            or self._value_range == 0
            or self._track_rect.width() == 0
        ):
            handle_radius = self._handle_size // 2
            if abs(pos.y() - self._center_y) <= handle_radius and abs(pos.x() - (self._handle_size // 2)) <= handle_radius:
                return 'low'
            return None

        # Handle radius for hit testing
        handle_radius = self._handle_size // 2
        center_y = self._center_y

        # Calculate distance once and reuse
        y_dist = abs(pos.y() - center_y)
        if y_dist > handle_radius:
            return None

        # Test low handle
        low_pos = self._track_rect.left() + self._low_handle_pos
        if abs(pos.x() - low_pos) <= handle_radius:
            return 'low'

        # Test high handle
        high_pos = self._track_rect.left() + self._high_handle_pos
        if abs(pos.x() - high_pos) <= handle_radius:
            return 'high'

        return None

    def enterEvent(self, event):
        """Optimized hover enter event"""
        self._is_hovered = True
        self._state_transition.transitionTo("hovered")
        FluentMicroInteraction.hover_glow(self, 0.1)
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Optimized hover leave event"""
        self._is_hovered = False
        self._state_transition.transitionTo("normal")
        self.update()
        super().leaveEvent(event)

    def set_range(self, minimum: int, maximum: int):
        """Set the range efficiently"""
        if minimum != self._minimum or maximum != self._maximum:
            self._minimum = minimum
            self._maximum = maximum

            # Update values to stay in range
            self._low_value = max(minimum, min(maximum, self._low_value))
            self._high_value = max(minimum, min(maximum, self._high_value))

            # Ensure low <= high
            if self._low_value > self._high_value:
                self._low_value, self._high_value = self._high_value, self._low_value

            # Reset cached calculations
            self._track_rect = None
            self._value_range = None
            self.update()

    def set_values(self, low_value: int, high_value: int):
        """Set both values efficiently"""
        update_needed = False

        new_low = max(self._minimum, min(self._maximum, low_value))
        if new_low != self._low_value:
            self._low_value = new_low
            update_needed = True

        new_high = max(self._minimum, min(self._maximum, high_value))
        if new_high != self._high_value:
            self._high_value = new_high
            update_needed = True

        # Ensure low <= high
        if self._low_value > self._high_value:
            self._low_value, self._high_value = self._high_value, self._low_value
            update_needed = True

        if update_needed:
            # Reset cached handle positions
            self._low_handle_pos = None
            self._high_handle_pos = None
            self.update()

    def get_values(self) -> tuple[int, int]:
        """Get current values"""
        return (self._low_value, self._high_value)


class FluentVolumeSlider(QWidget):
    """Optimized Fluent Design Style Volume Slider with icon and mute functionality"""

    value_changing = Signal(int)  # Emitted while dragging
    value_changed_final = Signal(int)  # Emitted when drag ends
    mute_toggled = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None, value: int = 50):
        super().__init__(parent)

        # Setup layout with both slider and icon
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)

        # Create volume icon
        self._volume_icon = QLabel("🔊", self)
        self._volume_icon.setFixedSize(24, 24)
        self._volume_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._volume_icon.setCursor(Qt.CursorShape.PointingHandCursor)

        # Create the slider as a separate widget
        self._slider = FluentSlider(
            self,
            Qt.Orientation.Horizontal,
            FluentSlider.SliderStyle.ACCENT,
            FluentSlider.Size.MEDIUM,
            0, 100, value
        )

        # Add widgets to layout in proper order
        self._layout.addWidget(self._volume_icon)
        self._layout.addWidget(self._slider, 1)  # Slider gets stretch factor

        # State tracking
        self._is_muted = False
        self._volume_before_mute = value

        # Setup connections and styling
        self._setup_connections()
        self._apply_volume_style()

        # Add reveal animation when created
        FluentRevealEffect.fade_in(self, 300)

    def _setup_connections(self):
        """Setup optimized signal connections"""
        # Connect slider signals
        self._slider.value_changing.connect(self.value_changing.emit)
        self._slider.value_changed_final.connect(self.value_changed_final.emit)

        # Connect icon click for mute toggle
        self._volume_icon.mousePressEvent = self._toggle_mute

    def _apply_volume_style(self):
        """Apply volume-specific styling efficiently"""
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

        self._volume_icon.setStyleSheet(icon_style)

        # Apply a container style for proper alignment
        self.setStyleSheet("""
            FluentVolumeSlider {
                background: transparent;
                border: none;
            }
        """)

    def _toggle_mute(self, _event=None):
        """Toggle mute state efficiently"""
        self._is_muted = not self._is_muted

        if self._is_muted:
            self._volume_before_mute = self._slider.value()
            self._slider.setValue(0)
            self._volume_icon.setText("🔇")
        else:
            self._slider.setValue(self._volume_before_mute)
            self._volume_icon.setText("🔊")

        # Apply mute animation
        FluentMicroInteraction.pulse_animation(self._volume_icon, 1.1)
        self.mute_toggled.emit(self._is_muted)

    def set_muted(self, muted: bool):
        """Set mute state programmatically"""
        if muted != self._is_muted:
            self._toggle_mute()

    def is_muted(self) -> bool:
        """Check if volume is muted"""
        return self._is_muted

    def value(self) -> int:
        """Get current volume value"""
        return self._slider.value()

    def setValue(self, value: int):
        """Set volume value"""
        self._slider.setValue(value)

        # Update mute state if needed
        if value > 0 and self._is_muted:
            self.set_muted(False)
        elif value == 0 and not self._is_muted:
            self.set_muted(True)
