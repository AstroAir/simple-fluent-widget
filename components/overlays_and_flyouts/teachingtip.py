"""
Fluent Design Teaching Tip Component
Educational overlay that points to specific UI elements
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QFrame, QGraphicsDropShadowEffect, QApplication)
from PySide6.QtCore import Signal, Qt, QTimer, QPoint, QRect, QSize, QPropertyAnimation, QEasingCurve, QByteArray
from PySide6.QtGui import QIcon, QFont, QPainter, QPainterPath, QColor, QPolygon
from core.theme import theme_manager
from core.enhanced_base import FluentBaseWidget
from core.enhanced_animations import FluentTransition
from typing import Optional, Union
from enum import Enum


class TeachingTipPlacement(Enum):
    """Teaching tip placement options"""
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class TeachingTipTail(Enum):
    """Teaching tip tail (pointer) options"""
    AUTO = "auto"
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"
    LEFT_TOP = "left_top"
    LEFT_CENTER = "left_center"
    LEFT_BOTTOM = "left_bottom"
    RIGHT_TOP = "right_top"
    RIGHT_CENTER = "right_center"
    RIGHT_BOTTOM = "right_bottom"
    NONE = "none"


class FluentTeachingTip(FluentBaseWidget):
    """
    Fluent Design Teaching Tip Component

    Educational overlay that provides contextual help:
    - Points to specific UI elements with tail/pointer
    - Rich content with title, subtitle, and actions
    - Auto-positioning with collision detection
    - Smooth show/hide animations
    - Theme-consistent styling
    """

    # Signals
    closed = Signal()  # Emitted when tip is closed
    action_clicked = Signal(str)  # Emitted when action button is clicked

    def __init__(self, parent: Optional[QWidget] = None,
                 title: str = "",
                 subtitle: str = "",
                 target: Optional[QWidget] = None,
                 placement: TeachingTipPlacement = TeachingTipPlacement.BOTTOM):
        super().__init__(parent)

        # Properties
        self._title = title
        self._subtitle = subtitle
        self._target_widget = target
        self._placement = placement
        self._tail_position = TeachingTipTail.AUTO

        # Configuration
        self._show_close_button = True
        self._auto_hide_delay = 0  # 0 = no auto hide
        self._margin = 8  # Distance from target
        self._tail_size = 12
        self._is_light_dismiss = True  # Click outside to dismiss

        # State
        self._is_visible = False
        self._calculated_placement = placement
        self._calculated_tail = TeachingTipTail.AUTO

        # UI Elements
        self._main_container: Optional[QFrame] = None  # type: ignore
        self._content_layout: Optional[QVBoxLayout] = None  # type: ignore
        self._title_label: Optional[QLabel] = None  # type: ignore
        self._subtitle_label: Optional[QLabel] = None  # type: ignore
        self._actions_layout: Optional[QHBoxLayout] = None  # type: ignore
        self._close_button: Optional[QPushButton] = None  # type: ignore

        # Animations
        self._show_animation: Optional[QPropertyAnimation] = None
        self._hide_animation: Optional[QPropertyAnimation] = None

        # Timers
        self._auto_hide_timer = QTimer()
        self._auto_hide_timer.setSingleShot(True)
        self._auto_hide_timer.timeout.connect(self.hide_tip)

        # Setup
        self._setup_ui()
        self._setup_style()
        self._connect_signals()

        # Start hidden
        self.hide()

    def _setup_ui(self):
        """Setup the UI layout"""
        # Set window flags for popup behavior
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(self._tail_size, self._tail_size,
                                       self._tail_size, self._tail_size)
        main_layout.setSpacing(0)

        # Content container with shadow
        self._main_container = QFrame()
        self._main_container.setFrameStyle(QFrame.Shape.NoFrame)

        # Add drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self._main_container.setGraphicsEffect(shadow)

        # Content layout
        self._content_layout = QVBoxLayout(self._main_container)
        self._content_layout.setContentsMargins(16, 12, 16, 12)
        self._content_layout.setSpacing(8)

        # Header layout (title and close button)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # Title
        if self._title:
            self._title_label = QLabel(self._title)
            self._title_label.setFont(
                QFont("Segoe UI", 12, QFont.Weight.DemiBold))
            self._title_label.setWordWrap(True)
            header_layout.addWidget(self._title_label)

        header_layout.addStretch()

        # Close button
        if self._show_close_button:
            self._close_button = QPushButton("✕")
            self._close_button.setFixedSize(20, 20)
            self._close_button.setFlat(True)
            self._close_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self._close_button.setFont(QFont("Segoe UI", 10))
            header_layout.addWidget(self._close_button)

        if header_layout.count() > 0:
            self._content_layout.addLayout(header_layout)

        # Subtitle
        if self._subtitle:
            self._subtitle_label = QLabel(self._subtitle)
            self._subtitle_label.setFont(QFont("Segoe UI", 11))
            self._subtitle_label.setWordWrap(True)
            self._content_layout.addWidget(self._subtitle_label)

        # Actions layout (for future action buttons)
        self._actions_layout = QHBoxLayout()
        self._actions_layout.setSpacing(8)
        self._content_layout.addLayout(self._actions_layout)

        main_layout.addWidget(self._main_container)

    def _setup_style(self):
        """Apply Fluent Design styling"""
        if not self._main_container:
            return

        theme = theme_manager

        # Main container style
        container_style = f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
        """

        # Close button style
        close_button_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 10px;
                color: {theme.get_color('text_secondary').name()};
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                color: {theme.get_color('text_primary').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
        """

        self._main_container.setStyleSheet(container_style)

        if self._close_button:
            self._close_button.setStyleSheet(close_button_style)

        # Text styles
        if self._title_label:
            self._title_label.setStyleSheet(f"""
                QLabel {{ color: {theme.get_color('text_primary').name()}; }}
            """)

        if self._subtitle_label:
            self._subtitle_label.setStyleSheet(f"""
                QLabel {{ color: {theme.get_color('text_secondary').name()}; }}
            """)

    def _connect_signals(self):
        """Connect signals and slots"""
        if self._close_button:
            self._close_button.clicked.connect(self.hide_tip)

        # Theme changes
        theme_manager.theme_changed.connect(self._setup_style)

    def paintEvent(self, event):
        """Custom paint event to draw tail/pointer"""
        super().paintEvent(event)

        if self._tail_position == TeachingTipTail.NONE:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw tail based on position
        self._draw_tail(painter)

    def _draw_tail(self, painter: QPainter):
        """Draw the pointing tail"""
        theme = theme_manager

        # Set colors
        painter.setPen(QColor(theme.get_color('border').name()))
        painter.setBrush(QColor(theme.get_color('surface').name()))

        # Calculate tail position and shape
        if not self._main_container:
            return

        container_rect = self._main_container.geometry()
        tail_points = self._calculate_tail_points(container_rect)

        if tail_points:
            tail_polygon = QPolygon(tail_points)
            painter.drawPolygon(tail_polygon)

    def _calculate_tail_points(self, container_rect: QRect) -> Optional[list]:
        """Calculate tail triangle points based on placement"""
        if self._calculated_tail == TeachingTipTail.NONE:
            return None

        points = []
        tail_size = self._tail_size

        # Determine tail position based on calculated placement
        if self._calculated_placement == TeachingTipPlacement.TOP:
            # Tail points down from bottom of container
            center_x = container_rect.center().x()
            bottom_y = container_rect.bottom()
            points = [
                QPoint(center_x - tail_size//2, bottom_y),
                QPoint(center_x + tail_size//2, bottom_y),
                QPoint(center_x, bottom_y + tail_size)
            ]
        elif self._calculated_placement == TeachingTipPlacement.BOTTOM:
            # Tail points up from top of container
            center_x = container_rect.center().x()
            top_y = container_rect.top()
            points = [
                QPoint(center_x - tail_size//2, top_y),
                QPoint(center_x + tail_size//2, top_y),
                QPoint(center_x, top_y - tail_size)
            ]
        elif self._calculated_placement == TeachingTipPlacement.LEFT:
            # Tail points right from right edge of container
            center_y = container_rect.center().y()
            right_x = container_rect.right()
            points = [
                QPoint(right_x, center_y - tail_size//2),
                QPoint(right_x, center_y + tail_size//2),
                QPoint(right_x + tail_size, center_y)
            ]
        elif self._calculated_placement == TeachingTipPlacement.RIGHT:
            # Tail points left from left edge of container
            center_y = container_rect.center().y()
            left_x = container_rect.left()
            points = [
                QPoint(left_x, center_y - tail_size//2),
                QPoint(left_x, center_y + tail_size//2),
                QPoint(left_x - tail_size, center_y)
            ]

        return points

    def _calculate_position(self) -> QPoint:
        """Calculate optimal position relative to target"""
        if not self._target_widget:
            # Center on screen if no target
            screen = QApplication.primaryScreen().geometry()
            return QPoint(screen.width()//2 - self.width()//2,
                          screen.height()//2 - self.height()//2)

        # Get target widget global position and size
        target_rect = self._target_widget.geometry()
        target_global_pos = self._target_widget.mapToGlobal(
            target_rect.topLeft())
        target_global_rect = QRect(target_global_pos, target_rect.size())

        # Get screen geometry for collision detection
        screen = QApplication.primaryScreen().geometry()

        # Calculate position based on placement
        tip_size = self.sizeHint()
        margin = self._margin + self._tail_size

        # Try preferred placement first
        pos = self._try_placement(
            target_global_rect, tip_size, self._placement, screen, margin)
        if pos:
            self._calculated_placement = self._placement
            return pos

        # Try alternative placements if preferred doesn't fit
        placements = [TeachingTipPlacement.BOTTOM, TeachingTipPlacement.TOP,
                      TeachingTipPlacement.RIGHT, TeachingTipPlacement.LEFT]

        for placement in placements:
            if placement != self._placement:
                pos = self._try_placement(
                    target_global_rect, tip_size, placement, screen, margin)
                if pos:
                    self._calculated_placement = placement
                    return pos

        # Fallback to center if nothing fits
        self._calculated_placement = TeachingTipPlacement.CENTER
        return QPoint(screen.width()//2 - tip_size.width()//2,
                      screen.height()//2 - tip_size.height()//2)

    def _try_placement(self, target_rect: QRect, tip_size: QSize,
                       placement: TeachingTipPlacement, screen: QRect, margin: int) -> Optional[QPoint]:
        """Try to place tip in given position and check if it fits on screen"""

        if placement == TeachingTipPlacement.BOTTOM:
            x = target_rect.center().x() - tip_size.width()//2
            y = target_rect.bottom() + margin
        elif placement == TeachingTipPlacement.TOP:
            x = target_rect.center().x() - tip_size.width()//2
            y = target_rect.top() - tip_size.height() - margin
        elif placement == TeachingTipPlacement.RIGHT:
            x = target_rect.right() + margin
            y = target_rect.center().y() - tip_size.height()//2
        elif placement == TeachingTipPlacement.LEFT:
            x = target_rect.left() - tip_size.width() - margin
            y = target_rect.center().y() - tip_size.height()//2
        else:  # CENTER
            x = target_rect.center().x() - tip_size.width()//2
            y = target_rect.center().y() - tip_size.height()//2

        # Check if position fits on screen
        tip_rect = QRect(x, y, tip_size.width(), tip_size.height())
        if screen.contains(tip_rect):
            return QPoint(x, y)

        return None

    # Public API

    def show_tip(self, animated: bool = True):
        """Show the teaching tip"""
        if self._is_visible:
            return

        # Calculate position
        position = self._calculate_position()
        self.move(position)

        # Show the widget
        self.show()
        self._is_visible = True

        if animated:
            # Animate appearance
            self.setWindowOpacity(0.0)

            self._show_animation = QPropertyAnimation(
                self, QByteArray(b"windowOpacity"))
            self._show_animation.setDuration(200)
            self._show_animation.setStartValue(0.0)
            self._show_animation.setEndValue(1.0)
            self._show_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._show_animation.start()
        else:
            self.setWindowOpacity(1.0)

        # Start auto-hide timer if configured
        if self._auto_hide_delay > 0:
            self._auto_hide_timer.start(self._auto_hide_delay)

    def hide_tip(self, animated: bool = True):
        """Hide the teaching tip"""
        if not self._is_visible:
            return

        self._auto_hide_timer.stop()

        if animated:
            # Animate disappearance
            self._hide_animation = QPropertyAnimation(
                self, QByteArray(b"windowOpacity"))
            self._hide_animation.setDuration(150)
            self._hide_animation.setStartValue(1.0)
            self._hide_animation.setEndValue(0.0)
            self._hide_animation.setEasingCurve(QEasingCurve.Type.InCubic)
            self._hide_animation.finished.connect(self._finish_hide)
            self._hide_animation.start()
        else:
            self._finish_hide()

    def _finish_hide(self):
        """Complete the hiding process"""
        self.hide()
        self._is_visible = False
        self.closed.emit()

    def set_title(self, title: str):
        """Set the title text"""
        self._title = title
        if self._title_label:
            self._title_label.setText(title)
            self._title_label.setVisible(bool(title))

    def set_subtitle(self, subtitle: str):
        """Set the subtitle text"""
        self._subtitle = subtitle
        if self._subtitle_label:
            self._subtitle_label.setText(subtitle)
            self._subtitle_label.setVisible(bool(subtitle))

    def set_target(self, target: QWidget):
        """Set the target widget to point to"""
        self._target_widget = target

    def set_placement(self, placement: TeachingTipPlacement):
        """Set the preferred placement"""
        self._placement = placement

    def add_action_button(self, text: str, action_id: str):
        """Add an action button"""
        if not self._actions_layout:
            return

        button = QPushButton(text)
        button.setProperty("action_id", action_id)
        button.clicked.connect(lambda: self.action_clicked.emit(action_id))

        # Style the button
        theme = theme_manager
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.get_color('primary').name()};
                color: {theme.get_color('text_on_primary').name()};
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('primary').lighter(110).name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('primary').darker(110).name()};
            }}
        """)

        self._actions_layout.addWidget(button)

    def set_auto_hide_delay(self, delay_ms: int):
        """Set auto-hide delay in milliseconds (0 = no auto hide)"""
        self._auto_hide_delay = delay_ms

    def set_light_dismiss(self, enabled: bool):
        """Enable or disable light dismiss (click outside to close)"""
        self._is_light_dismiss = enabled

    def mousePressEvent(self, event):
        """Handle mouse press for light dismiss"""
        if self._is_light_dismiss and event.button() == Qt.MouseButton.LeftButton:
            # Check if click is outside the main container
            if self._main_container and not self._main_container.geometry().contains(event.pos()):
                self.hide_tip()
                return

        super().mousePressEvent(event)


# Convenience functions for showing teaching tips

def show_teaching_tip(target: QWidget, title: str, subtitle: str = "",
                      placement: TeachingTipPlacement = TeachingTipPlacement.BOTTOM,
                      auto_hide_delay: int = 0) -> FluentTeachingTip:
    """Show a simple teaching tip"""
    tip = FluentTeachingTip(
        parent=target.window() if target else None,
        title=title,
        subtitle=subtitle,
        target=target,
        placement=placement
    )

    if auto_hide_delay > 0:
        tip.set_auto_hide_delay(auto_hide_delay)

    tip.show_tip()
    return tip


# Export classes
__all__ = [
    'FluentTeachingTip',
    'TeachingTipPlacement',
    'TeachingTipTail',
    'show_teaching_tip'
]
