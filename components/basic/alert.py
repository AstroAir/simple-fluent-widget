"""
Fluent Design Alert and Notification Components

Implements alerts, notifications, and message bars with various styles.
Based on Windows 11 Fluent Design principles.
"""

from typing import Optional
from enum import Enum
from PySide6.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                               QPushButton, QFrame, QGraphicsOpacityEffect, QApplication)
from PySide6.QtCore import (Qt, QPropertyAnimation, QTimer, Signal,
                            QPoint, QByteArray)
from PySide6.QtGui import QColor

# Fix import issues
from core.theme import theme_manager, ThemeMode
from core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                      FluentRevealEffect, FluentSequence)


class AlertType(Enum):
    """Alert type enumeration"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class FluentAlert(QFrame):
    """
    Modern alert component with enhanced animations
    """

    # Signals
    closed = Signal()
    action_clicked = Signal()

    def __init__(self,
                 title: str = "",
                 message: str = "",
                 alert_type: AlertType = AlertType.INFO,
                 closable: bool = True,
                 action_text: str = "",
                 timeout: int = 0,  # 0 means no auto-close
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._message = message
        self._alert_type = alert_type
        self._closable = closable
        self._action_text = action_text
        self._timeout = timeout

        self._setup_ui()
        self._setup_enhanced_animations()
        self._connect_theme()

        if timeout > 0:
            QTimer.singleShot(timeout, self.close_with_animation)

    def _setup_ui(self):
        """Setup UI components"""
        self.setFrameStyle(QFrame.Shape.NoFrame)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(12)

        # Icon
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(24, 24)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self._icon_label)

        # Content layout
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        # Title
        if self._title:
            self._title_label = QLabel(self._title)
            self._title_label.setWordWrap(True)
            content_layout.addWidget(self._title_label)

        # Message
        if self._message:
            self._message_label = QLabel(self._message)
            self._message_label.setWordWrap(True)
            content_layout.addWidget(self._message_label)

        main_layout.addLayout(content_layout, 1)

        # Action button
        if self._action_text:
            self._action_button = QPushButton(self._action_text)
            self._action_button.clicked.connect(self.action_clicked.emit)
            self._action_button.clicked.connect(self._on_action_button_clicked)
            main_layout.addWidget(self._action_button)

        # Close button
        if self._closable:
            self._close_button = QPushButton("×")
            self._close_button.setFixedSize(24, 24)
            self._close_button.clicked.connect(self.close_with_animation)
            self._close_button.clicked.connect(self._on_close_button_clicked)
            main_layout.addWidget(self._close_button)

        self._update_style()

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system"""
        self._opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self._opacity_effect)

        # Enhanced fade animation with better easing
        self._fade_animation = FluentTransition.create_transition(
            self, FluentTransition.FADE, 400, FluentTransition.EASE_SPRING)
        self._fade_animation.finished.connect(self._on_fade_finished)

        # Reveal animation sequence
        self._reveal_sequence = FluentSequence(self)

        # Add reveal effect
        self._reveal_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self, 300))
        self._reveal_sequence.addPause(100)
        self._reveal_sequence.addCallback(
            lambda: FluentRevealEffect.slide_in(self, 250, "up"))

        # Start reveal animation
        QTimer.singleShot(50, self._reveal_sequence.start)

    def _connect_theme(self):
        """Connect theme updates"""
        theme_manager.theme_changed.connect(self._update_style)

    def _get_colors(self) -> tuple[QColor, QColor, QColor]:
        """Get colors based on alert type"""
        theme = theme_manager

        if self._alert_type == AlertType.INFO:
            return (QColor(0, 120, 215), QColor(240, 248, 255), QColor(0, 90, 158))
        elif self._alert_type == AlertType.SUCCESS:
            return (QColor(16, 124, 16), QColor(240, 248, 240), QColor(12, 100, 12))
        elif self._alert_type == AlertType.WARNING:
            return (QColor(255, 185, 0), QColor(255, 252, 240), QColor(200, 145, 0))
        elif self._alert_type == AlertType.ERROR:
            return (QColor(196, 43, 28), QColor(255, 245, 245), QColor(160, 30, 20))
        else:
            return (QColor(theme.get_color('accent')), QColor(theme.get_color('background')), QColor(theme.get_color('text_primary')))

    def _update_style(self):
        """Update component styles"""
        accent_color, bg_color, text_color = self._get_colors()
        theme = theme_manager

        # Adjust background color transparency
        if theme._current_mode == ThemeMode.DARK:
            bg_color = bg_color.darker(200)
        bg_color.setAlpha(230)

        # Main container style
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, {bg_color.alpha()});
                border: 1px solid rgba({accent_color.red()}, {accent_color.green()}, {accent_color.blue()}, 150);
                border-radius: 8px;
            }}
        """)

        # Title style
        if hasattr(self, '_title_label'):
            self._title_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color.name()};
                    font-weight: 600;
                    font-size: 14px;
                    background: transparent;
                }}
            """)

        # Message style - Fixed variable name consistency
        if hasattr(self, '_message_label'):
            self._message_label.setStyleSheet(f"""
                QLabel {{
                    color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 180);
                    font-size: 13px;
                    background: transparent;
                }}
            """)

        # Action button style
        if hasattr(self, '_action_button'):
            self._action_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {accent_color.name()};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: 500;
                    transition: all 0.2s ease;
                }}
                QPushButton:hover {{
                    background-color: {accent_color.lighter(110).name()};
                    transform: translateY(-1px);
                }}
                QPushButton:pressed {{
                    background-color: {accent_color.darker(110).name()};
                    transform: translateY(0px);
                }}
            """)

        # Close button style - Fixed variable name consistency
        if hasattr(self, '_close_button'):
            self._close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color.name()};
                    border: none;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: bold;
                    transition: all 0.2s ease;
                }}
                QPushButton:hover {{
                    background-color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 30);
                    transform: scale(1.1);
                }}
                QPushButton:pressed {{
                    background-color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 50);
                    transform: scale(0.95);
                }}
            """)

        # Update icon
        self._update_icon()

    def _update_icon(self):
        """Update icon with enhanced styling"""
        icon_map = {
            AlertType.INFO: "ℹ",
            AlertType.SUCCESS: "✓",
            AlertType.WARNING: "⚠",
            AlertType.ERROR: "✗"
        }

        icon_text = icon_map.get(self._alert_type, "ℹ")
        accent_color, _, _ = self._get_colors()

        self._icon_label.setText(icon_text)
        self._icon_label.setStyleSheet(f"""
            QLabel {{
                color: {accent_color.name()};
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }}
        """)

    def _on_action_button_clicked(self):
        """Handle action button click with micro-interaction"""
        if hasattr(self, '_action_button'):
            FluentMicroInteraction.button_press(self._action_button)

    def _on_close_button_clicked(self):
        """Handle close button click with micro-interaction"""
        if hasattr(self, '_close_button'):
            FluentMicroInteraction.scale_animation(self._close_button, 0.8)

    def _on_fade_finished(self):
        """Fade animation completed"""
        if self._fade_animation.endValue() == 0.0:
            self.hide()
            self.closed.emit()

    def close_with_animation(self):
        """Close with enhanced animation"""
        # Create exit sequence
        exit_sequence = FluentSequence(self)
        exit_sequence.addCallback(
            lambda: FluentMicroInteraction.scale_animation(self, 0.9))
        exit_sequence.addPause(100)
        exit_sequence.addCallback(self._start_fade_out)
        exit_sequence.start()

    def _start_fade_out(self):
        """Start fade out animation"""
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.start()

    def setTitle(self, title: str):
        """Set alert title"""
        self._title = title
        if hasattr(self, '_title_label'):
            self._title_label.setText(title)

    def setMessage(self, message: str):
        """Set alert message"""
        self._message = message
        if hasattr(self, '_message_label'):
            self._message_label.setText(message)

    def setAlertType(self, alert_type: AlertType):
        """Set alert type"""
        self._alert_type = alert_type
        self._update_style()


class FluentNotification(QWidget):
    """
    Floating notification component with enhanced animations
    """

    closed = Signal()
    clicked = Signal()

    def __init__(self,
                 title: str = "",
                 message: str = "",
                 notification_type: AlertType = AlertType.INFO,
                 timeout: int = 5000,
                 closable: bool = True,
                 clickable: bool = False,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._message = message
        self._notification_type = notification_type
        self._timeout = timeout
        self._closable = closable
        self._clickable = clickable

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._setup_ui()
        self._setup_enhanced_animations()
        self._connect_theme()

        if timeout > 0:
            QTimer.singleShot(timeout, self.close_with_animation)

    def _setup_ui(self):
        """Setup UI components"""
        # Main container
        self._container = QFrame()
        self._container.setFrameStyle(QFrame.Shape.NoFrame)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._container)

        container_layout = QHBoxLayout(self._container)
        container_layout.setContentsMargins(16, 12, 16, 12)
        container_layout.setSpacing(12)

        # Icon
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(32, 32)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self._icon_label)

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)

        # Title
        self._title_label = QLabel(self._title)
        self._title_label.setWordWrap(True)
        content_layout.addWidget(self._title_label)

        # Message
        if self._message:
            self._message_label = QLabel(self._message)
            self._message_label.setWordWrap(True)
            content_layout.addWidget(self._message_label)

        container_layout.addLayout(content_layout, 1)

        # Close button
        if self._closable:
            self._close_button = QPushButton("×")
            self._close_button.setFixedSize(24, 24)
            self._close_button.clicked.connect(self.close_with_animation)
            self._close_button.clicked.connect(self._on_close_button_clicked)
            container_layout.addWidget(self._close_button)

        # Click event
        if self._clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setFixedWidth(350)
        self.adjustSize()

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system"""
        self._opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self._opacity_effect)

        # Enhanced animations
        self._fade_animation = FluentTransition.create_transition(
            self, FluentTransition.FADE, 350, FluentTransition.EASE_SPRING)
        self._fade_animation.finished.connect(self._on_animation_finished)

        self._slide_animation = QPropertyAnimation(self, QByteArray(b"pos"))
        self._slide_animation.setDuration(400)
        self._slide_animation.setEasingCurve(FluentTransition.EASE_SPRING)

        # Show notification with enhanced entrance
        QTimer.singleShot(50, self.show_notification)

    def _connect_theme(self):
        """Connect theme updates"""
        theme_manager.theme_changed.connect(self._update_style)
        self._update_style()

    def _update_style(self):
        """Update component styles"""
        theme = theme_manager
        accent_color, _, _ = self._get_colors()

        # Main container style
        if theme._current_mode == ThemeMode.DARK:
            bg_color_container = QColor(45, 45, 45)
            border_color_container = QColor(70, 70, 70)
        else:
            bg_color_container = QColor(255, 255, 255)
            border_color_container = QColor(220, 220, 220)

        self._container.setStyleSheet(f"""
            QFrame {{
                background-color: rgba({bg_color_container.red()}, {bg_color_container.green()}, {bg_color_container.blue()}, 245);
                border: 1px solid rgba({border_color_container.red()}, {border_color_container.green()}, {border_color_container.blue()}, 180);
                border-radius: 8px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            }}
        """)

        # Title style
        self._title_label.setStyleSheet(f"""
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                font-weight: 600;
                font-size: 14px;
                background: transparent;
            }}
        """)

        # Message style - Fixed variable name consistency
        if hasattr(self, '_message_label'):
            msg_text_color = QColor(theme.get_color('text_primary'))
            self._message_label.setStyleSheet(f"""
                QLabel {{
                    color: rgba({msg_text_color.red()}, {msg_text_color.green()}, {msg_text_color.blue()}, 180);
                    font-size: 12px;
                    background: transparent;
                }}
            """)

        # Close button style - Fixed variable name consistency
        if hasattr(self, '_close_button'):
            close_btn_text_color = QColor(theme.get_color('text_primary'))
            self._close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {close_btn_text_color.name()};
                    border: none;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: bold;
                    transition: all 0.2s ease;
                }}
                QPushButton:hover {{
                    background-color: rgba({close_btn_text_color.red()}, {close_btn_text_color.green()}, {close_btn_text_color.blue()}, 30);
                    transform: scale(1.1);
                }}
                QPushButton:pressed {{
                    background-color: rgba({close_btn_text_color.red()}, {close_btn_text_color.green()}, {close_btn_text_color.blue()}, 50);
                    transform: scale(0.9);
                }}
            """)

        # Update icon
        self._update_icon(accent_color)

    def _get_colors(self) -> tuple[QColor, QColor, QColor]:
        """Get colors based on notification type"""
        if self._notification_type == AlertType.INFO:
            return (QColor(0, 120, 215), QColor(240, 248, 255), QColor(0, 90, 158))
        elif self._notification_type == AlertType.SUCCESS:
            return (QColor(16, 124, 16), QColor(240, 248, 240), QColor(12, 100, 12))
        elif self._notification_type == AlertType.WARNING:
            return (QColor(255, 185, 0), QColor(255, 252, 240), QColor(200, 145, 0))
        elif self._notification_type == AlertType.ERROR:
            return (QColor(196, 43, 28), QColor(255, 245, 245), QColor(160, 30, 20))
        else:
            theme = theme_manager
            return (QColor(theme.get_color('accent')), QColor(theme.get_color('background')), QColor(theme.get_color('text_primary')))

    def _update_icon(self, accent_color: QColor):
        """Update icon with enhanced styling"""
        icon_map = {
            AlertType.INFO: "ℹ",
            AlertType.SUCCESS: "✓",
            AlertType.WARNING: "⚠",
            AlertType.ERROR: "✗"
        }

        icon_text = icon_map.get(self._notification_type, "ℹ")

        self._icon_label.setText(icon_text)
        self._icon_label.setStyleSheet(f"""
            QLabel {{
                color: {accent_color.name()};
                font-size: 20px;
                font-weight: bold;
                background: transparent;
            }}
        """)

    def _on_close_button_clicked(self):
        """Handle close button click with micro-interaction"""
        if hasattr(self, '_close_button'):
            FluentMicroInteraction.button_press(self._close_button, 0.8)

    def show_notification(self):
        """Show notification with enhanced entrance animation"""
        # Position at screen bottom-right
        screen_geometry = QApplication.primaryScreen().geometry()
        start_pos = QPoint(screen_geometry.width() - self.width() - 20,
                           screen_geometry.height() + 100)

        end_pos = QPoint(screen_geometry.width() - self.width() - 20,
                         screen_geometry.height() - self.height() - 20)

        self.move(start_pos)
        self.show()

        # Enhanced entrance sequence
        entrance_sequence = FluentSequence(self)

        # Slide in animation
        entrance_sequence.addCallback(
            lambda: self._start_slide_animation(start_pos, end_pos))
        entrance_sequence.addPause(50)

        # Fade in animation
        entrance_sequence.addCallback(lambda: self._start_fade_in())
        entrance_sequence.addPause(100)

        # Subtle bounce effect
        entrance_sequence.addCallback(
            lambda: FluentMicroInteraction.pulse_animation(self, 1.02))

        entrance_sequence.start()

    def _start_slide_animation(self, start_pos: QPoint, end_pos: QPoint):
        """Start slide animation"""
        self._slide_animation.setStartValue(start_pos)
        self._slide_animation.setEndValue(end_pos)
        self._slide_animation.start()

    def _start_fade_in(self):
        """Start fade in animation"""
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.start()

    def close_with_animation(self):
        """Close with enhanced exit animation"""
        # Enhanced exit sequence
        exit_sequence = FluentSequence(self)

        # Scale down slightly
        exit_sequence.addCallback(
            lambda: FluentMicroInteraction.scale_animation(self, 0.95))
        exit_sequence.addPause(100)

        # Slide out and fade
        current_pos = self.pos()
        end_pos = QPoint(current_pos.x() + 400, current_pos.y())

        exit_sequence.addCallback(
            lambda: self._start_slide_out(current_pos, end_pos))
        exit_sequence.addCallback(lambda: self._start_fade_out())

        exit_sequence.start()

    def _start_slide_out(self, start_pos: QPoint, end_pos: QPoint):
        """Start slide out animation"""
        self._slide_animation.setStartValue(start_pos)
        self._slide_animation.setEndValue(end_pos)
        self._slide_animation.start()

    def _start_fade_out(self):
        """Start fade out animation"""
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.start()

    def _on_animation_finished(self):
        """Animation completed handler"""
        if self._fade_animation.endValue() == 0.0:
            self.close()
            self.closed.emit()

    def mousePressEvent(self, event):
        """Enhanced mouse press event with micro-interaction"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            FluentMicroInteraction.ripple_effect(self)
            self.clicked.emit()
        super().mousePressEvent(event)


class FluentMessageBar(QFrame):
    """
    Enhanced message bar component with modern animations
    """

    closed = Signal()
    action_clicked = Signal()

    def __init__(self,
                 message: str = "",
                 message_type: AlertType = AlertType.INFO,
                 closable: bool = True,
                 action_text: str = "",
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._message = message
        self._message_type = message_type
        self._closable = closable
        self._action_text = action_text

        self.setFrameStyle(QFrame.Shape.NoFrame)
        self._setup_ui()
        self._setup_enhanced_animations()
        self._connect_theme()

    def _setup_ui(self):
        """Setup UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # Icon
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(20, 20)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._icon_label)

        # Message
        self._message_label = QLabel(self._message)
        self._message_label.setWordWrap(True)
        layout.addWidget(self._message_label, 1)

        # Action button
        if self._action_text:
            self._action_button = QPushButton(self._action_text)
            self._action_button.clicked.connect(self.action_clicked.emit)
            self._action_button.clicked.connect(self._on_action_button_clicked)
            layout.addWidget(self._action_button)

        # Close button
        if self._closable:
            self._close_button = QPushButton("×")
            self._close_button.setFixedSize(20, 20)
            self._close_button.clicked.connect(self._close_clicked)
            self._close_button.clicked.connect(self._on_close_button_clicked)
            layout.addWidget(self._close_button)

    def _setup_enhanced_animations(self):
        """Setup enhanced animations"""
        # Reveal animation
        QTimer.singleShot(
            50, lambda: FluentRevealEffect.slide_in(self, 300, "down"))

    def _connect_theme(self):
        """Connect theme updates"""
        theme_manager.theme_changed.connect(self._update_style)
        self._update_style()

    def _update_style(self):
        """Update component styles with enhanced styling"""
        accent_color, bg_color, text_color = self._get_colors()

        # Adjust background color transparency
        bg_color.setAlpha(200)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, {bg_color.alpha()});
                border-left: 4px solid {accent_color.name()};
                transition: all 0.3s ease;
            }}
            QFrame:hover {{
                background-color: rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, {min(255, bg_color.alpha() + 20)});
            }}
        """)

        # Update sub-components
        self._update_icon()

        # Message style
        self._message_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color.name()};
                font-size: 13px;
                background: transparent;
            }}
        """)

        # Action button style
        if hasattr(self, '_action_button'):
            self._action_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {accent_color.name()};
                    border: 1px solid {accent_color.name()};
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                    transition: all 0.2s ease;
                }}
                QPushButton:hover {{
                    background-color: rgba({accent_color.red()}, {accent_color.green()}, {accent_color.blue()}, 30);
                    transform: translateY(-1px);
                }}
                QPushButton:pressed {{
                    transform: translateY(0px);
                }}
            """)

        # Close button style
        if hasattr(self, '_close_button'):
            self._close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color.name()};
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    transition: all 0.2s ease;
                }}
                QPushButton:hover {{
                    background-color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 30);
                    transform: scale(1.1);
                }}
                QPushButton:pressed {{
                    transform: scale(0.9);
                }}
            """)

    def _get_colors(self) -> tuple[QColor, QColor, QColor]:
        """Get colors based on message type"""
        if self._message_type == AlertType.INFO:
            return (QColor(0, 120, 215), QColor(240, 248, 255), QColor(0, 90, 158))
        elif self._message_type == AlertType.SUCCESS:
            return (QColor(16, 124, 16), QColor(240, 248, 240), QColor(12, 100, 12))
        elif self._message_type == AlertType.WARNING:
            return (QColor(255, 185, 0), QColor(255, 252, 240), QColor(200, 145, 0))
        elif self._message_type == AlertType.ERROR:
            return (QColor(196, 43, 28), QColor(255, 245, 245), QColor(160, 30, 20))
        else:
            theme = theme_manager
            return (QColor(theme.get_color('accent')), QColor(theme.get_color('background')), QColor(theme.get_color('text_primary')))

    def _update_icon(self):
        """Update icon with enhanced styling"""
        icon_map = {
            AlertType.INFO: "ℹ",
            AlertType.SUCCESS: "✓",
            AlertType.WARNING: "⚠",
            AlertType.ERROR: "✗"
        }

        icon_text = icon_map.get(self._message_type, "ℹ")
        accent_color, _, _ = self._get_colors()

        self._icon_label.setText(icon_text)
        self._icon_label.setStyleSheet(f"""
            QLabel {{
                color: {accent_color.name()};
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }}
        """)

    def _on_action_button_clicked(self):
        """Handle action button click with micro-interaction"""
        if hasattr(self, '_action_button'):
            FluentMicroInteraction.button_press(self._action_button)

    def _on_close_button_clicked(self):
        """Handle close button click with micro-interaction"""
        if hasattr(self, '_close_button'):
            FluentMicroInteraction.scale_animation(self._close_button, 0.8)

    def _close_clicked(self):
        """Close button clicked with enhanced animation"""
        # Enhanced close sequence
        close_sequence = FluentSequence(self)
        close_sequence.addCallback(
            lambda: FluentMicroInteraction.scale_animation(self, 0.95))
        close_sequence.addPause(100)
        close_sequence.addCallback(self._finish_close)
        close_sequence.start()

    def _finish_close(self):
        """Finish close operation"""
        self.hide()
        self.closed.emit()

    def setMessage(self, message: str):
        """Set message with animation"""
        self._message = message
        self._message_label.setText(message)
        # Add subtle pulse to indicate change
        FluentMicroInteraction.pulse_animation(self._message_label, 1.02)

    def setMessageType(self, message_type: AlertType):
        """Set message type with transition"""
        self._message_type = message_type
        self._update_style()
        # Add transition effect
        FluentMicroInteraction.pulse_animation(self, 1.01)
