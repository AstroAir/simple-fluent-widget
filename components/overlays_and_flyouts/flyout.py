"""
Fluent Design Flyout Component
A lightweight popup container that appears above other content
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                               QFrame, QGraphicsDropShadowEffect,
                               QApplication)
from PySide6.QtCore import (Qt, Signal, QSize, QPropertyAnimation, QTimer,
                            QRect, QPoint, QEasingCurve, QParallelAnimationGroup,
                            QByteArray)
from PySide6.QtGui import QColor
from core.theme import theme_manager
from typing import Optional, Union
from enum import Enum


class FlyoutPlacement(Enum):
    """Flyout placement options"""
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"


class FlyoutShowMode(Enum):
    """How the flyout should be shown"""
    STANDARD = "standard"      # Show on click/interaction
    AUTO = "auto"             # Show automatically with hover
    TRANSIENT = "transient"   # Show briefly then hide
    PERSISTENT = "persistent"  # Stay open until manually closed


class FluentFlyout(QWidget):
    """
    Fluent Design Flyout Component

    A lightweight popup that can contain any content and appears
    above other UI elements. Supports:
    - Smart positioning relative to target
    - Smooth animations
    - Auto-hide behavior
    - Custom content
    - Theme consistency
    - Light dismiss
    """

    # Signals
    opened = Signal()
    closed = Signal()
    about_to_hide = Signal()

    def __init__(self, content: Optional[QWidget] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Properties
        self._content_widget = content
        self._target_widget: Optional[QWidget] = None
        self._placement = FlyoutPlacement.BOTTOM
        self._show_mode = FlyoutShowMode.STANDARD
        self._is_open = False
        self._light_dismiss = True
        self._border_thickness = 1
        self._corner_radius = 8
        self._elevation = 32
        self._auto_hide_delay = 3000  # milliseconds
        self._animation_duration = 200

        # Sizing
        self._min_width = 200
        self._max_width = 480
        self._min_height = 100
        self._max_height = 600

        # UI Elements (initialized in _setup_ui)
        self._container: QFrame
        self._content_layout: QVBoxLayout
        self._shadow_effect: QGraphicsDropShadowEffect

        # Animations (initialized in _setup_animations)
        self._fade_animation: QPropertyAnimation
        self._scale_animation: QPropertyAnimation
        self._animation_group: QParallelAnimationGroup

        # Timers
        self._auto_hide_timer = QTimer()
        self._auto_hide_timer.setSingleShot(True)
        self._auto_hide_timer.timeout.connect(self.hide_flyout)

        # Setup
        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        # Hide initially
        self.hide()

        # Make this a top-level window for proper layering
        self.setWindowFlags(Qt.WindowType.Popup |
                            Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def _setup_ui(self):
        """Setup the UI structure"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)  # Shadow margin

        # Container frame
        self._container = QFrame()
        self._container.setFrameShape(QFrame.Shape.Box)
        self._container.setObjectName("flyoutContainer")

        # Content layout inside container
        self._content_layout = QVBoxLayout(self._container)
        self._content_layout.setContentsMargins(12, 12, 12, 12)
        self._content_layout.setSpacing(8)

        # Add content widget if provided
        if self._content_widget:
            self._content_layout.addWidget(self._content_widget)

        main_layout.addWidget(self._container)

        # Set constraints
        self.setMinimumSize(self._min_width, self._min_height)
        self.setMaximumSize(self._max_width, self._max_height)

    def _setup_style(self):
        """Apply Fluent Design styling"""
        theme = theme_manager

        style = f"""
            FluentFlyout {{
                background: transparent;
            }}
            
            #flyoutContainer {{
                background-color: {theme.get_color('surface').name()};
                border: {self._border_thickness}px solid {theme.get_color('border').name()};
                border-radius: {self._corner_radius}px;
            }}
        """

        self.setStyleSheet(style)

    def _setup_shadow(self):
        """Setup drop shadow effect"""
        if not hasattr(self, '_shadow_effect') or self._shadow_effect is None:
            self._shadow_effect = QGraphicsDropShadowEffect()
            self._shadow_effect.setBlurRadius(self._elevation)
            self._shadow_effect.setOffset(0, 4)
            self._shadow_effect.setColor(QColor(0, 0, 0, 80))
        self._container.setGraphicsEffect(self._shadow_effect)

    def _setup_animations(self):
        """Setup entrance and exit animations"""
        # Animation group
        self._animation_group = QParallelAnimationGroup(self)

        # Fade animation
        self._fade_animation = QPropertyAnimation(
            self, QByteArray(b"windowOpacity"))
        self._fade_animation.setDuration(self._animation_duration)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Scale animation (simulate from smaller to full size)
        self._scale_animation = QPropertyAnimation(
            self._container, QByteArray(b"geometry"))
        self._scale_animation.setDuration(self._animation_duration)
        self._scale_animation.setEasingCurve(QEasingCurve.Type.OutBack)

        # Add to group
        self._animation_group.addAnimation(self._fade_animation)
        self._animation_group.addAnimation(self._scale_animation)

        # Connect signals
        self._animation_group.finished.connect(self._on_animation_finished)

    def _calculate_position(self, target_rect: QRect) -> QPoint:
        """Calculate the optimal position for the flyout"""
        screen = QApplication.primaryScreen().geometry()
        flyout_size = self.sizeHint()

        # Default position
        pos = QPoint()

        if self._placement == FlyoutPlacement.BOTTOM:
            pos.setX(target_rect.center().x() - flyout_size.width() // 2)
            pos.setY(target_rect.bottom() + 8)
        elif self._placement == FlyoutPlacement.TOP:
            pos.setX(target_rect.center().x() - flyout_size.width() // 2)
            pos.setY(target_rect.top() - flyout_size.height() - 8)
        elif self._placement == FlyoutPlacement.RIGHT:
            pos.setX(target_rect.right() + 8)
            pos.setY(target_rect.center().y() - flyout_size.height() // 2)
        elif self._placement == FlyoutPlacement.LEFT:
            pos.setX(target_rect.left() - flyout_size.width() - 8)
            pos.setY(target_rect.center().y() - flyout_size.height() // 2)
        elif self._placement == FlyoutPlacement.CENTER:
            pos.setX(target_rect.center().x() - flyout_size.width() // 2)
            pos.setY(target_rect.center().y() - flyout_size.height() // 2)

        # Ensure flyout stays within screen bounds
        if pos.x() < screen.left():
            pos.setX(screen.left() + 8)
        elif pos.x() + flyout_size.width() > screen.right():
            pos.setX(screen.right() - flyout_size.width() - 8)

        if pos.y() < screen.top():
            pos.setY(screen.top() + 8)
        elif pos.y() + flyout_size.height() > screen.bottom():
            pos.setY(screen.bottom() - flyout_size.height() - 8)

        return pos

    def _on_animation_finished(self):
        """Handle animation completion"""
        if not self._is_open:
            self.hide()
            self.closed.emit()

    def _start_auto_hide_timer(self):
        """Start the auto-hide timer if configured"""
        if self._show_mode == FlyoutShowMode.TRANSIENT and self._auto_hide_delay > 0:
            self._auto_hide_timer.start(self._auto_hide_delay)

    # Public API

    def set_content(self, widget: QWidget):
        """Set the content widget"""
        # Remove existing content
        if self._content_widget:
            self._content_layout.removeWidget(self._content_widget)

        self._content_widget = widget
        if widget:
            self._content_layout.addWidget(widget)

    def get_content(self) -> Optional[QWidget]:
        """Get the content widget"""
        return self._content_widget

    def set_placement(self, placement: FlyoutPlacement):
        """Set the flyout placement relative to target"""
        self._placement = placement

    def set_show_mode(self, mode: FlyoutShowMode):
        """Set the show mode"""
        self._show_mode = mode

    def set_light_dismiss(self, enabled: bool):
        """Enable or disable light dismiss (clicking outside closes)"""
        self._light_dismiss = enabled

    def set_auto_hide_delay(self, delay_ms: int):
        """Set auto-hide delay in milliseconds"""
        self._auto_hide_delay = delay_ms

    def show_at(self, target: Union[QWidget, QPoint, QRect]):
        """Show the flyout at the specified target"""
        if isinstance(target, QWidget):
            self._target_widget = target
            target_rect = QRect(target.mapToGlobal(
                QPoint(0, 0)), target.size())
        elif isinstance(target, QPoint):
            target_rect = QRect(target, QSize(1, 1))
        elif isinstance(target, QRect):
            target_rect = target
        else:
            return

        # Calculate position
        position = self._calculate_position(target_rect)
        self.move(position)

        # Setup shadow
        self._setup_shadow()

        # Show and animate
        self._is_open = True
        self.show()

        # Setup animations
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)

        # Scale animation from center
        current_geometry = self._container.geometry()
        start_geometry = QRect(
            current_geometry.center(),
            QSize(1, 1)
        )
        self._scale_animation.setStartValue(start_geometry)
        self._scale_animation.setEndValue(current_geometry)

        # Start animations
        self._animation_group.start()

        # Start auto-hide timer
        self._start_auto_hide_timer()

        self.opened.emit()

    def hide_flyout(self):
        """Hide the flyout with animation"""
        if not self._is_open:
            return

        self._is_open = False
        self.about_to_hide.emit()

        # Stop auto-hide timer
        self._auto_hide_timer.stop()

        # Setup exit animations
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)

        # Scale animation to center
        current_geometry = self._container.geometry()
        end_geometry = QRect(
            current_geometry.center(),
            QSize(1, 1)
        )
        self._scale_animation.setStartValue(current_geometry)
        self._scale_animation.setEndValue(end_geometry)

        # Start exit animations
        self._animation_group.start()

    def is_open(self) -> bool:
        """Check if the flyout is currently open"""
        return self._is_open

    def mousePressEvent(self, event):
        """Handle mouse press for light dismiss"""
        if self._light_dismiss and not self._container.geometry().contains(event.pos()):
            self.hide_flyout()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape and self._light_dismiss:
            self.hide_flyout()
        super().keyPressEvent(event)


class FluentFlyoutBuilder:
    """Builder class for creating flyouts with fluent API"""

    def __init__(self):
        self._flyout = FluentFlyout()

    def with_content(self, widget: QWidget):
        """Set the content widget"""
        self._flyout.set_content(widget)
        return self

    def with_placement(self, placement: FlyoutPlacement):
        """Set the placement"""
        self._flyout.set_placement(placement)
        return self

    def with_show_mode(self, mode: FlyoutShowMode):
        """Set the show mode"""
        self._flyout.set_show_mode(mode)
        return self

    def with_light_dismiss(self, enabled: bool = True):
        """Enable light dismiss"""
        self._flyout.set_light_dismiss(enabled)
        return self

    def with_auto_hide(self, delay_ms: int):
        """Set auto-hide delay"""
        self._flyout.set_auto_hide_delay(delay_ms)
        return self

    def build(self) -> FluentFlyout:
        """Build and return the flyout"""
        return self._flyout


# Convenience functions
def show_flyout_at_widget(content: QWidget, target: QWidget,
                          placement: FlyoutPlacement = FlyoutPlacement.BOTTOM) -> FluentFlyout:
    """Show a flyout with content at the specified widget"""
    flyout = (FluentFlyoutBuilder()
              .with_content(content)
              .with_placement(placement)
              .build())
    flyout.show_at(target)
    return flyout


def show_tooltip_flyout(text: str, target: QWidget,
                        placement: FlyoutPlacement = FlyoutPlacement.TOP) -> FluentFlyout:
    """Show a simple text flyout (enhanced tooltip)"""
    label = QLabel(text)
    label.setWordWrap(True)
    label.setMaximumWidth(300)

    flyout = (FluentFlyoutBuilder()
              .with_content(label)
              .with_placement(placement)
              .with_show_mode(FlyoutShowMode.TRANSIENT)
              .with_auto_hide(2000)
              .build())
    flyout.show_at(target)
    return flyout


# Export classes
__all__ = [
    'FluentFlyout',
    'FluentFlyoutBuilder',
    'FlyoutPlacement',
    'FlyoutShowMode',
    'show_flyout_at_widget',
    'show_tooltip_flyout'
]
