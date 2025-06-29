"""
Fluent Design Teaching Tip Component
A contextual help tooltip that provides guidance and information
"""

from typing import Optional, Union, Callable
from enum import Enum

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QGraphicsDropShadowEffect,
                               QSizePolicy, QApplication)
from PySide6.QtCore import (Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve,
                            QSize, QRect, QPoint, QByteArray)
from PySide6.QtGui import QFont, QIcon, QColor

from ..base.fluent_control_base import FluentControlBase, FluentThemeAware


class TeachingTipPlacement(Enum):
    """Teaching tip placement options"""
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    AUTO = "auto"  # Automatically choose best placement


class TeachingTipIcon(Enum):
    """Pre-defined teaching tip icons"""
    NONE = "none"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    LIGHTBULB = "lightbulb"
    QUESTION = "question"


class FluentTeachingTip(QFrame, FluentControlBase, FluentThemeAware):
    """
    Fluent Design Teaching Tip Component

    A contextual help component that provides guidance, tips, and information
    near UI elements, following Fluent Design principles.

    Features:
    - Smart positioning relative to target elements
    - Multiple placement options with auto-adjustment
    - Rich content support (title, subtitle, actions)
    - Icon support with pre-defined icons
    - Dismissible with light-dismiss or explicit close
    - Smooth animations for show/hide
    - Theme integration
    - Accessibility support
    - Auto-hide with timer
    """

    # Signals
    shown = Signal()  # Teaching tip shown
    hidden = Signal()  # Teaching tip hidden
    action_clicked = Signal(str)  # Action button clicked
    dismissed = Signal()  # Teaching tip dismissed

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        FluentControlBase.__init__(self)
        FluentThemeAware.__init__(self)

        # Core properties
        self._title = ""
        self._subtitle = ""
        self._icon = TeachingTipIcon.NONE
        self._custom_icon: Optional[QIcon] = None
        self._placement = TeachingTipPlacement.AUTO
        self._target_widget: Optional[QWidget] = None

        # Content
        self._actions = []  # List of (text, callback) tuples
        self._is_light_dismiss_enabled = True
        self._auto_hide_duration = 0  # 0 = no auto-hide

        # UI state
        self._is_visible = False
        self._is_animating = False

        # Initialize UI components - will be set in _setup_ui
        self._container: Optional[QFrame] = None
        self._header_layout: Optional[QHBoxLayout] = None
        self._icon_label: Optional[QLabel] = None
        self._title_label: Optional[QLabel] = None
        self._subtitle_label: Optional[QLabel] = None
        self._actions_layout: Optional[QHBoxLayout] = None
        self._close_button: Optional[QPushButton] = None

        # Initialize animations - will be set in _setup_animations
        self._show_animation: Optional[QPropertyAnimation] = None
        self._hide_animation: Optional[QPropertyAnimation] = None

        # Timers
        self._auto_hide_timer = QTimer()
        self._auto_hide_timer.setSingleShot(True)
        self._auto_hide_timer.timeout.connect(self.hide)

        # Setup UI
        self._setup_ui()
        self._setup_styling()
        self._setup_connections()
        self._setup_accessibility()
        self._setup_animations()

        # Apply theme
        self.apply_theme()

        # Initially hidden
        self.hide()

    def _setup_ui(self):
        """Setup the user interface"""
        # Set window flags for popup behavior
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(0)

        # Container frame for content
        self._container = QFrame()
        self._container.setFrameStyle(QFrame.Shape.NoFrame)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self._container.setGraphicsEffect(shadow)

        main_layout.addWidget(self._container)

        # Container layout
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(16, 12, 16, 12)
        container_layout.setSpacing(8)

        # Header section (icon + title + close button)
        self._setup_header_section(container_layout)

        # Subtitle section
        self._setup_subtitle_section(container_layout)

        # Actions section
        self._setup_actions_section(container_layout)

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Preferred)

    def _setup_header_section(self, parent_layout: QVBoxLayout):
        """Setup the header section with icon, title, and close button"""
        self._header_layout = QHBoxLayout()
        self._header_layout.setSpacing(8)

        # Icon label
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(24, 24)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.hide()  # Initially hidden
        self._header_layout.addWidget(self._icon_label)

        # Title label
        self._title_label = QLabel()
        self._title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        self._title_label.setWordWrap(True)
        self._header_layout.addWidget(self._title_label, 1)

        # Close button
        self._close_button = QPushButton("×")
        self._close_button.setFixedSize(24, 24)
        self._close_button.setFont(QFont("Segoe UI", 12))
        self._close_button.setFlat(True)
        self._header_layout.addWidget(self._close_button)

        parent_layout.addLayout(self._header_layout)

    def _setup_subtitle_section(self, parent_layout: QVBoxLayout):
        """Setup the subtitle section"""
        self._subtitle_label = QLabel()
        self._subtitle_label.setFont(QFont("Segoe UI", 12))
        self._subtitle_label.setWordWrap(True)
        self._subtitle_label.hide()  # Initially hidden
        parent_layout.addWidget(self._subtitle_label)

    def _setup_actions_section(self, parent_layout: QVBoxLayout):
        """Setup the actions section"""
        self._actions_layout = QHBoxLayout()
        self._actions_layout.setSpacing(8)
        self._actions_layout.addStretch()  # Right-align buttons
        parent_layout.addLayout(self._actions_layout)

    def _setup_styling(self):
        """Setup component styling"""
        theme = self.get_current_theme()
        if not theme:
            return

        # Get theme colors
        bg_color = theme.get('surface_primary', '#f3f3f3')
        border_color = theme.get('stroke_default', '#e1e1e1')
        text_color = theme.get('text_primary', '#323130')
        secondary_text = theme.get('text_secondary', '#605e5c')

        # Container styling
        if self._container:
            self._container.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                }}
            """)

        # Title styling
        if self._title_label:
            self._title_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    background-color: transparent;
                }}
            """)

        # Subtitle styling
        if self._subtitle_label:
            self._subtitle_label.setStyleSheet(f"""
                QLabel {{
                    color: {secondary_text};
                    background-color: transparent;
                }}
            """)

        # Close button styling
        if self._close_button:
            self._close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 12px;
                    color: {secondary_text};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 0, 0, 0.1);
                }}
                QPushButton:pressed {{
                    background-color: rgba(0, 0, 0, 0.2);
                }}
            """)

    def _setup_connections(self):
        """Setup signal connections"""
        # Close button
        if self._close_button:
            self._close_button.clicked.connect(self.dismiss)

    def _setup_accessibility(self):
        """Setup accessibility features"""
        self.setAccessibleName("Teaching tip")
        if self._title_label:
            self._title_label.setAccessibleName("Teaching tip title")
        if self._subtitle_label:
            self._subtitle_label.setAccessibleName("Teaching tip content")
        if self._close_button:
            self._close_button.setAccessibleName("Close teaching tip")

    def _setup_animations(self):
        """Setup animations for show/hide"""
        # Show animation (fade in + scale)
        self._show_animation = QPropertyAnimation(
            self, QByteArray(b"windowOpacity"))
        self._show_animation.setDuration(250)
        self._show_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._show_animation.setStartValue(0.0)
        self._show_animation.setEndValue(1.0)
        self._show_animation.finished.connect(self._on_show_animation_finished)

        # Hide animation (fade out)
        self._hide_animation = QPropertyAnimation(
            self, QByteArray(b"windowOpacity"))
        self._hide_animation.setDuration(150)
        self._hide_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self._hide_animation.setStartValue(1.0)
        self._hide_animation.setEndValue(0.0)
        self._hide_animation.finished.connect(self._on_hide_animation_finished)

    def _is_child_widget(self, widget: QWidget) -> bool:
        """Check if widget is a child of this teaching tip"""
        parent = widget
        while parent:
            if parent == self:
                return True
            parent = parent.parent()
        return False

    def _on_show_animation_finished(self):
        """Handle show animation finished"""
        self._is_animating = False
        self.shown.emit()

        # Start auto-hide timer if configured
        if self._auto_hide_duration > 0:
            self._auto_hide_timer.start(self._auto_hide_duration)

    def _on_hide_animation_finished(self):
        """Handle hide animation finished"""
        self._is_animating = False
        self._is_visible = False
        super().hide()
        self.hidden.emit()

    def _calculate_position(self) -> QPoint:
        """Calculate optimal position based on target and placement"""
        if not self._target_widget:
            # Center on screen if no target
            screen = QApplication.primaryScreen().geometry()
            tip_size = self.sizeHint()
            x = (screen.width() - tip_size.width()) // 2
            y = (screen.height() - tip_size.height()) // 2
            return QPoint(x, y)

        # Get target widget global position and size
        target_rect = QRect(
            self._target_widget.mapToGlobal(QPoint(0, 0)),
            self._target_widget.size()
        )

        tip_size = self.sizeHint()
        screen = QApplication.primaryScreen().geometry()

        # Calculate position based on placement
        if self._placement == TeachingTipPlacement.AUTO:
            placement = self._determine_best_placement(
                target_rect, tip_size, screen)
        else:
            placement = self._placement

        return self._calculate_position_for_placement(target_rect, tip_size, placement)

    def _determine_best_placement(self, target_rect: QRect, tip_size: QSize, screen: QRect) -> TeachingTipPlacement:
        """Determine the best placement to avoid clipping"""
        # Check available space in each direction
        space_top = target_rect.top() - screen.top()
        space_bottom = screen.bottom() - target_rect.bottom()
        space_left = target_rect.left() - screen.left()
        space_right = screen.right() - target_rect.right()

        # Prefer bottom, then top, then right, then left
        if space_bottom >= tip_size.height():
            return TeachingTipPlacement.BOTTOM
        elif space_top >= tip_size.height():
            return TeachingTipPlacement.TOP
        elif space_right >= tip_size.width():
            return TeachingTipPlacement.RIGHT
        elif space_left >= tip_size.width():
            return TeachingTipPlacement.LEFT
        else:
            # Not enough space anywhere, use bottom as fallback
            return TeachingTipPlacement.BOTTOM

    def _calculate_position_for_placement(self, target_rect: QRect, tip_size: QSize,
                                          placement: TeachingTipPlacement) -> QPoint:
        """Calculate position for specific placement"""
        margin = 8  # Gap between target and tip

        if placement == TeachingTipPlacement.BOTTOM:
            x = target_rect.center().x() - tip_size.width() // 2
            y = target_rect.bottom() + margin
        elif placement == TeachingTipPlacement.TOP:
            x = target_rect.center().x() - tip_size.width() // 2
            y = target_rect.top() - tip_size.height() - margin
        elif placement == TeachingTipPlacement.RIGHT:
            x = target_rect.right() + margin
            y = target_rect.center().y() - tip_size.height() // 2
        elif placement == TeachingTipPlacement.LEFT:
            x = target_rect.left() - tip_size.width() - margin
            y = target_rect.center().y() - tip_size.height() // 2
        elif placement == TeachingTipPlacement.TOP_LEFT:
            x = target_rect.left()
            y = target_rect.top() - tip_size.height() - margin
        elif placement == TeachingTipPlacement.TOP_RIGHT:
            x = target_rect.right() - tip_size.width()
            y = target_rect.top() - tip_size.height() - margin
        elif placement == TeachingTipPlacement.BOTTOM_LEFT:
            x = target_rect.left()
            y = target_rect.bottom() + margin
        elif placement == TeachingTipPlacement.BOTTOM_RIGHT:
            x = target_rect.right() - tip_size.width()
            y = target_rect.bottom() + margin
        else:
            # Fallback to bottom center
            x = target_rect.center().x() - tip_size.width() // 2
            y = target_rect.bottom() + margin

        return QPoint(x, y)

    def _update_icon(self):
        """Update the icon display"""
        if not self._icon_label:
            return

        if self._icon == TeachingTipIcon.NONE and not self._custom_icon:
            self._icon_label.hide()
            return

        # Show icon label
        self._icon_label.show()

        if self._custom_icon:
            # Use custom icon
            self._icon_label.setPixmap(self._custom_icon.pixmap(24, 24))
        else:
            # Use pre-defined icon
            icon_text = self._get_icon_text(self._icon)
            self._icon_label.setText(icon_text)
            self._icon_label.setFont(QFont("Segoe UI Symbol", 16))

    def _get_icon_text(self, icon: TeachingTipIcon) -> str:
        """Get text representation of pre-defined icons"""
        icon_map = {
            TeachingTipIcon.INFO: "ℹ️",
            TeachingTipIcon.WARNING: "⚠️",
            TeachingTipIcon.ERROR: "❌",
            TeachingTipIcon.SUCCESS: "✅",
            TeachingTipIcon.LIGHTBULB: "💡",
            TeachingTipIcon.QUESTION: "❓"
        }
        return icon_map.get(icon, "")

    def _update_actions(self):
        """Update the actions buttons"""
        if not self._actions_layout:
            return

        # Clear existing action buttons
        while self._actions_layout.count() > 1:  # Keep the stretch
            item = self._actions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add action buttons
        for action_text, callback in self._actions:
            button = QPushButton(action_text)
            button.setFont(QFont("Segoe UI", 10))

            # Style action button
            theme = self.get_current_theme()
            if theme:
                accent_color = theme.get('accent_default', '#0078d4')
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {accent_color};
                        border: none;
                        border-radius: 4px;
                        color: white;
                        padding: 6px 12px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(0, 0, 0, 0.1);
                    }}
                    QPushButton:pressed {{
                        background-color: rgba(0, 0, 0, 0.2);
                    }}
                """)

            # Connect callback
            if callback:
                button.clicked.connect(lambda: callback())

            # Connect action signal
            button.clicked.connect(
                lambda: self.action_clicked.emit(action_text))

            self._actions_layout.insertWidget(
                self._actions_layout.count() - 1, button)

    # Public API
    def set_title(self, title: str):
        """Set the title text"""
        self._title = title
        if self._title_label:
            self._title_label.setText(title)
            self._title_label.setVisible(bool(title))

    def get_title(self) -> str:
        """Get the title text"""
        return self._title

    def set_subtitle(self, subtitle: str):
        """Set the subtitle text"""
        self._subtitle = subtitle
        if self._subtitle_label:
            self._subtitle_label.setText(subtitle)
            self._subtitle_label.setVisible(bool(subtitle))

    def get_subtitle(self) -> str:
        """Get the subtitle text"""
        return self._subtitle

    def set_icon(self, icon: Union[TeachingTipIcon, QIcon]):
        """Set the icon"""
        if isinstance(icon, TeachingTipIcon):
            self._icon = icon
            self._custom_icon = None
        else:
            self._icon = TeachingTipIcon.NONE
            self._custom_icon = icon
        self._update_icon()

    def get_icon(self) -> Union[TeachingTipIcon, QIcon]:
        """Get the icon"""
        return self._custom_icon if self._custom_icon else self._icon

    def set_placement(self, placement: TeachingTipPlacement):
        """Set the placement relative to target"""
        self._placement = placement

    def get_placement(self) -> TeachingTipPlacement:
        """Get the placement"""
        return self._placement

    def set_target(self, widget: QWidget):
        """Set the target widget to position relative to"""
        self._target_widget = widget

    def get_target(self) -> Optional[QWidget]:
        """Get the target widget"""
        return self._target_widget

    def add_action(self, text: str, callback: Optional[Callable] = None):
        """Add an action button"""
        self._actions.append((text, callback))
        self._update_actions()

    def clear_actions(self):
        """Clear all action buttons"""
        self._actions.clear()
        self._update_actions()

    def set_light_dismiss_enabled(self, enabled: bool):
        """Enable or disable light dismiss (click outside to close)"""
        self._is_light_dismiss_enabled = enabled

    def is_light_dismiss_enabled(self) -> bool:
        """Check if light dismiss is enabled"""
        return self._is_light_dismiss_enabled

    def set_auto_hide_duration(self, duration_ms: int):
        """Set auto-hide duration in milliseconds (0 = no auto-hide)"""
        self._auto_hide_duration = max(0, duration_ms)

    def get_auto_hide_duration(self) -> int:
        """Get auto-hide duration"""
        return self._auto_hide_duration

    def show_at(self, target_widget: QWidget, placement: Optional[TeachingTipPlacement] = None):
        """Show the teaching tip at the specified target widget"""
        self.set_target(target_widget)
        if placement:
            self.set_placement(placement)
        self.show()

    def show(self):
        """Show the teaching tip with animation"""
        if self._is_visible or self._is_animating:
            return

        # Position the tip
        position = self._calculate_position()
        self.move(position)

        # Show without animation first
        self.setWindowOpacity(0.0)
        super().show()

        # Start show animation
        self._is_visible = True
        self._is_animating = True
        if self._show_animation:
            self._show_animation.start()

    def hide(self):
        """Hide the teaching tip with animation"""
        if not self._is_visible or self._is_animating:
            return

        # Stop auto-hide timer
        self._auto_hide_timer.stop()

        # Start hide animation
        self._is_animating = True
        if self._hide_animation:
            self._hide_animation.start()

    def dismiss(self):
        """Dismiss the teaching tip and emit dismissed signal"""
        self.dismissed.emit()
        self.hide()

    def is_showing(self) -> bool:
        """Check if the teaching tip is currently visible"""
        return self._is_visible

    def apply_theme(self):
        """Apply the current theme to the component."""
        self._setup_styling()
        self._update_actions()  # Re-style action buttons

    # Properties
    title = property(get_title, set_title)
    subtitle = property(get_subtitle, set_subtitle)
    placement = property(get_placement, set_placement)
    target = property(get_target, set_target)
