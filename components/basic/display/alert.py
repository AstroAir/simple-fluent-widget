"""
Enhanced Fluent Design Alert and Notification Components

Implements modern alerts, notifications, and message bars with:
- Smooth spring-based animations
- Performance optimizations with object pooling
- Enhanced accessibility and keyboard navigation
- Better theme integration with dynamic colors
- Modern PySide6 features and patterns

Based on Windows 11 Fluent Design principles.
"""

from typing import Optional, Dict, List, Callable, Any, Union
from enum import Enum
from weakref import WeakSet
import gc
from PySide6.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                               QPushButton, QFrame, QGraphicsOpacityEffect,
                               QApplication, QAbstractButton, QSizePolicy,
                               QStyle)
from PySide6.QtCore import (Qt, QPropertyAnimation, QTimer, Signal, Property,
                            QPoint, QByteArray, QEasingCurve, QParallelAnimationGroup,
                            QSequentialAnimationGroup, QObject, QRect, QSize,
                            QAbstractAnimation, Slot, QEvent)
from PySide6.QtGui import (QColor, QKeySequence, QFontMetrics, QPainter,
                           QLinearGradient, QBrush, QPen, QFont, QPixmap,
                           QAccessibleEvent, QPalette, QShortcut)

# Enhanced imports for modern features
from core.theme import theme_manager, ThemeMode
from core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                      FluentRevealEffect, FluentSequence)


class AlertType(Enum):
    """Enhanced alert type enumeration with semantic meanings"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"  # New: For system-critical alerts
    NEUTRAL = "neutral"    # New: For neutral information


class AlertPriority(Enum):
    """Alert priority levels for better UX management"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class AlertObjectPool:
    """Object pool for performance optimization with frequent alerts"""

    def __init__(self, max_size: int = 50):
        self._pool: List[QWidget] = []
        self._max_size = max_size
        self._active_alerts: WeakSet = WeakSet()

    def get_alert(self, alert_class: type) -> QWidget:
        """Get an alert instance from pool or create new one"""
        # Try to reuse from pool
        for i, alert in enumerate(self._pool):
            if type(alert) == alert_class and not alert.isVisible():
                self._pool.pop(i)
                self._active_alerts.add(alert)
                return alert        # Create new if pool is empty or no suitable instance
        new_alert = alert_class()
        self._active_alerts.add(new_alert)
        return new_alert

    def return_alert(self, alert: QWidget):
        """Return alert to pool for reuse"""
        if alert in self._active_alerts:
            self._active_alerts.discard(alert)

        # Check if the alert object is still valid before attempting to use it
        try:
            if alert and not alert.isHidden():
                if len(self._pool) < self._max_size:
                    # Reset alert state safely
                    alert.hide()
                    alert.setParent(None)
                    self._pool.append(alert)
                else:
                    # Pool is full, allow garbage collection
                    alert.deleteLater()
        except RuntimeError:
            # Object already deleted, just remove from tracking
            pass

    def cleanup(self):
        """Clean up unused alerts"""
        # Remove alerts that are no longer needed
        self._pool = [alert for alert in self._pool if not alert.isVisible()]
        gc.collect()


class AlertManager(QObject):
    """Global alert manager for coordinated alert display"""

    alert_shown = Signal(QWidget)
    alert_hidden = Signal(QWidget)

    def __init__(self):
        super().__init__()
        self._active_alerts: List[QWidget] = []
        self._notification_queue: List[Dict[str, Any]] = []
        self._max_concurrent = 5
        self._pool = AlertObjectPool()

    def show_alert(self, alert: QWidget, priority: AlertPriority = AlertPriority.NORMAL):
        """Show alert with priority management"""
        if len(self._active_alerts) >= self._max_concurrent:
            if priority.value >= AlertPriority.HIGH.value:
                # Remove lowest priority alert
                self._remove_lowest_priority_alert()
            else:
                # Queue for later
                self._notification_queue.append({
                    'alert': alert,
                    'priority': priority
                })
                return

        self._active_alerts.append(alert)
        
        # Connect to the alert's destroyed signal
        alert.destroyed.connect(lambda a=alert: self._on_alert_closed(a))
        
        self.alert_shown.emit(alert)

    def _remove_lowest_priority_alert(self):
        """Remove the alert with lowest priority"""
        if self._active_alerts:
            # For now, remove the oldest alert (FIFO)
            # Could be enhanced with actual priority tracking
            oldest_alert = self._active_alerts.pop(0)
            oldest_alert.close()

    def _on_alert_closed(self, alert: QWidget):
        """Handle alert closure and show queued alerts"""
        if alert in self._active_alerts:
            self._active_alerts.remove(alert)

        self._pool.return_alert(alert)
        self.alert_hidden.emit(alert)

        # Show next queued alert
        if self._notification_queue:
            next_alert_data = self._notification_queue.pop(0)
            self.show_alert(
                next_alert_data['alert'], next_alert_data['priority'])


# Global alert manager instance
alert_manager = AlertManager()


class EnhancedFluentAlert(QFrame):
    """
    Enhanced modern alert component with superior animations and performance

    Features:
    - Spring-based physics animations
    - Accessibility support with screen readers
    - Keyboard navigation
    - Performance optimizations
    - Dynamic theme adaptation
    - Modern PySide6 patterns
    """

    # Enhanced signals
    closed = Signal()
    action_clicked = Signal()
    animation_started = Signal(str)  # animation_type
    animation_finished = Signal(str)
    focus_changed = Signal(bool)

    def __init__(self,
                 title: str = "",
                 message: str = "",
                 alert_type: AlertType = AlertType.INFO,
                 priority: AlertPriority = AlertPriority.NORMAL,
                 closable: bool = True,
                 action_text: str = "",
                 timeout: int = 0,  # 0 means no auto-close
                 auto_dismiss: bool = True,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Core properties
        self._title = title
        self._message = message
        self._alert_type = alert_type
        self._priority = priority
        self._closable = closable
        self._action_text = action_text
        self._timeout = timeout
        self._auto_dismiss = auto_dismiss

        # Animation state
        self._is_animating = False
        self._opacity_value = 1.0
        self._scale_factor_value = 1.0
        self._original_geometry = QRect()

        # Performance optimization
        self._animations_cache: Dict[str, QPropertyAnimation] = {}
        self._lazy_loaded = False

        # Accessibility
        self.setAccessibleName(f"{alert_type.value.title()} Alert")
        self.setAccessibleDescription(f"{title}: {message}")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._setup_ui()
        self._setup_enhanced_animations()
        self._setup_accessibility()
        self._connect_theme()
        self._setup_keyboard_shortcuts()        # Register with alert manager
        alert_manager.show_alert(self, priority)

        if timeout > 0:
            QTimer.singleShot(timeout, self.close_with_animation)

    def closeEvent(self, event):
        """Handle close event properly to prevent object lifecycle issues"""
        # Ensure all animations are stopped before closing
        if hasattr(self, '_current_animations'):
            for anim in self._current_animations:
                if anim and anim.state() == QAbstractAnimation.State.Running:
                    anim.stop()
        
        # Stop animation groups
        if hasattr(self, '_entrance_group'):
            self._entrance_group.stop()
        if hasattr(self, '_exit_group'):
            self._exit_group.stop()
        
        # Emit closed signal before actual close
        self.closed.emit()
        
        # Call parent close event
        super().closeEvent(event)

    def _setup_ui(self):
        """Setup UI components with modern design patterns"""
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Fixed)

        # Main layout with proper spacing
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(16)

        # Icon with enhanced styling
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(28, 28)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setAccessibleName("Alert Icon")
        main_layout.addWidget(self._icon_label)

        # Content layout with better spacing
        content_layout = QVBoxLayout()
        content_layout.setSpacing(6)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Title with enhanced typography
        if self._title:
            self._title_label = QLabel(self._title)
            self._title_label.setWordWrap(True)
            self._title_label.setAccessibleName("Alert Title")
            self._title_label.setSizePolicy(
                QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            content_layout.addWidget(self._title_label)

        # Message with enhanced readability
        if self._message:
            self._message_label = QLabel(self._message)
            self._message_label.setWordWrap(True)
            self._message_label.setAccessibleName("Alert Message")
            self._message_label.setSizePolicy(
                QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            content_layout.addWidget(self._message_label)

        main_layout.addLayout(content_layout, 1)

        # Action button with enhanced interaction
        if self._action_text:
            self._action_button = QPushButton(self._action_text)
            self._action_button.clicked.connect(self.action_clicked.emit)
            self._action_button.clicked.connect(self._on_action_button_clicked)
            self._action_button.setAccessibleName(
                f"Action: {self._action_text}")
            self._action_button.setDefault(True)  # Make it the default action
            main_layout.addWidget(self._action_button)

        # Close button with enhanced accessibility
        if self._closable:
            self._close_button = QPushButton("✕")
            self._close_button.setFixedSize(28, 28)
            self._close_button.clicked.connect(self.close_with_animation)
            self._close_button.clicked.connect(self._on_close_button_clicked)
            self._close_button.setAccessibleName("Close Alert")
            self._close_button.setToolTip("Close this alert")
            main_layout.addWidget(self._close_button)

        self._update_style()

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system with better coordination"""
        # Animation state tracking to prevent conflicts
        self._current_animations = set()
        self._animation_group = QParallelAnimationGroup(self)
        
        # Create graphics effect for opacity
        self._opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self._opacity_effect)

        # Enhanced fade animation with smoother easing
        self._fade_animation = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        self._fade_animation.setDuration(300)  # Reduced duration to prevent jitter
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)  # Smoother easing
        self._fade_animation.finished.connect(self._on_fade_finished)

        # Slide animation for entrance/exit (using pos instead of geometry)
        self._slide_animation = QPropertyAnimation(self, QByteArray(b"pos"))
        self._slide_animation.setDuration(400)
        self._slide_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Animation group for coordinated animations
        self._entrance_group = QParallelAnimationGroup(self)
        self._exit_group = QSequentialAnimationGroup(self)        # Start reveal animation
        self._setup_reveal_sequence()

    def _setup_reveal_sequence(self):
        """Setup sophisticated entrance animation sequence"""
        # Set initial state
        self._opacity_effect.setOpacity(0.0)
        self._is_animating = True

        # Show and start entrance animations
        QTimer.singleShot(50, self._start_entrance_animation)

    def _start_entrance_animation(self):
        """Start the entrance animation sequence"""
        # Position alert if it has a parent that's a QWidget
        parent = self.parent()
        if parent and isinstance(parent, QWidget):
            parent_rect = parent.geometry()
            final_pos = QPoint(
                (parent_rect.width() - self.width()) // 2,
                max(20, (parent_rect.height() - self.height()) // 4)
            )
            start_pos = QPoint(final_pos.x(), -self.height() - 50)

            self.move(start_pos)
            self.show()

            # Start slide animation
            self._slide_animation.setStartValue(start_pos)
            self._slide_animation.setEndValue(final_pos)
            self._slide_animation.start()
        else:
            self.show()

        # Start fade in
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.start()

        # Add attention effect after entrance
        QTimer.singleShot(600, self._add_attention_bounce)

    def _add_attention_bounce(self):
        """Add subtle bounce effect to draw attention"""
        if hasattr(self, '_action_button'):
            FluentMicroInteraction.pulse_animation(self._action_button, 1.05)

        # Slight scale pulse for the entire alert
        QTimer.singleShot(
            200, lambda: FluentMicroInteraction.pulse_animation(self, 1.02))

    def _setup_accessibility(self):
        """Setup accessibility features"""
        # Ensure proper tab order
        if hasattr(self, '_action_button') and hasattr(self, '_close_button'):
            self.setTabOrder(self._action_button, self._close_button)

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for accessibility"""
        if self._closable:
            # Escape key to close
            escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
            escape_shortcut.activated.connect(self.close_with_animation)

        if hasattr(self, '_action_button'):
            # Enter key for action
            enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
            enter_shortcut.activated.connect(self._action_button.click)

    def _connect_theme(self):
        """Connect theme updates"""
        theme_manager.theme_changed.connect(self._update_style)
        self._update_style()

    def _get_colors(self) -> tuple[QColor, QColor, QColor]:
        """Get enhanced colors based on alert type with better contrast"""
        theme = theme_manager

        if self._alert_type == AlertType.INFO:
            return (QColor(0, 120, 215), QColor(240, 248, 255), QColor(0, 90, 158))
        elif self._alert_type == AlertType.SUCCESS:
            return (QColor(16, 124, 16), QColor(240, 248, 240), QColor(12, 100, 12))
        elif self._alert_type == AlertType.WARNING:
            return (QColor(255, 185, 0), QColor(255, 252, 240), QColor(200, 145, 0))
        elif self._alert_type == AlertType.ERROR:
            return (QColor(196, 43, 28), QColor(255, 245, 245), QColor(160, 30, 20))
        elif self._alert_type == AlertType.CRITICAL:
            return (QColor(139, 0, 0), QColor(255, 240, 240), QColor(100, 0, 0))
        elif self._alert_type == AlertType.NEUTRAL:
            return (QColor(128, 128, 128), QColor(248, 248, 248), QColor(96, 96, 96))
        else:
            return (QColor(theme.get_color('accent')), QColor(theme.get_color('background')), QColor(theme.get_color('text_primary')))

    def _update_style(self):
        """Update component styles with enhanced theming"""
        accent_color, bg_color, text_color = self._get_colors()
        theme = theme_manager

        # Dynamic color adaptation based on theme
        if theme._current_mode == ThemeMode.DARK:
            bg_color = bg_color.darker(200)
            text_color = text_color.lighter(150)

        bg_color.setAlpha(240)

        # Modern container style with subtle shadows and gradients
        self.setStyleSheet(f"""            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, {bg_color.alpha()}),
                    stop:1 rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, {max(200, bg_color.alpha() - 40)}));
                border: 1px solid rgba({accent_color.red()}, {accent_color.green()}, {accent_color.blue()}, 180);
                border-radius: 12px;
            }}
            QFrame:hover {{
                border: 1px solid rgba({accent_color.red()}, {accent_color.green()}, {accent_color.blue()}, 220);
            }}
        """)

        # Enhanced typography styles
        if hasattr(self, '_title_label'):
            self._title_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color.name()};
                    font-weight: 700;
                    font-size: 15px;
                    background: transparent;
                    letter-spacing: 0.5px;
                }}
            """)

        if hasattr(self, '_message_label'):
            self._message_label.setStyleSheet(f"""
                QLabel {{
                    color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 200);
                    font-size: 13px;
                    background: transparent;
                    line-height: 1.4;
                }}
            """)

        # Modern button styles
        if hasattr(self, '_action_button'):
            self._action_button.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {accent_color.lighter(110).name()},
                        stop:1 {accent_color.name()});
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                }}                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {accent_color.lighter(120).name()},
                        stop:1 {accent_color.lighter(110).name()});
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {accent_color.name()},
                        stop:1 {accent_color.darker(110).name()});
                }}
            """)

        if hasattr(self, '_close_button'):
            self._close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color.name()};
                    border: none;
                    border-radius: 14px;
                    font-size: 16px;
                    font-weight: bold;
                }}                QPushButton:hover {{
                    background-color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 40);
                }}
                QPushButton:pressed {{
                    background-color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 60);
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
            AlertType.ERROR: "✗",
            AlertType.CRITICAL: "⚡",
            AlertType.NEUTRAL: "○"
        }

        icon_text = icon_map.get(self._alert_type, "ℹ")
        accent_color, _, _ = self._get_colors()

        self._icon_label.setText(icon_text)
        self._icon_label.setStyleSheet(f"""
            QLabel {{
                color: {accent_color.name()};
                font-size: 20px;
                font-weight: bold;
                background: transparent;        }}
        """)

    def _on_action_button_clicked(self):
        """Handle action button click with enhanced micro-interaction"""
        if hasattr(self, '_action_button'):
            FluentMicroInteraction.button_press(self._action_button)

    def _on_close_button_clicked(self):
        """Handle close button click with enhanced micro-interaction"""
        if hasattr(self, '_close_button'):
            FluentMicroInteraction.scale_animation(self._close_button, 0.8)

    def _on_fade_finished(self):
        """Enhanced fade animation completion handler"""
        if self._fade_animation.endValue() == 0.0:
            self.hide()
            self.closed.emit()

    def close_with_animation(self):
        """Close with improved exit animation sequence"""
        if self._is_animating:
            return  # Prevent multiple concurrent close animations
            
        self._is_animating = True
        
        # Stop any running animations first
        if hasattr(self, '_current_animations'):
            for anim in self._current_animations:
                if anim and anim.state() == QAbstractAnimation.State.Running:
                    anim.stop()
        
        # Create coordinated exit animation
        self._exit_group.clear()
        
        # Add fade out animation to the group
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._exit_group.addAnimation(self._fade_animation)
        
        # Connect completion signal
        self._exit_group.finished.connect(self._on_exit_animation_finished)
          # Start the coordinated exit
        self._exit_group.start()

    def _on_exit_animation_finished(self):
        """Handle exit animation completion"""
        self._is_animating = False
        self.hide()
        self.closed.emit()

    def _start_fade_out(self):
        """Start enhanced fade out animation"""
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.start()

    def _start_slide_out(self):
        """Start slide out animation"""
        current_pos = self.pos()
        end_pos = QPoint(current_pos.x(), -self.height() - 50)

        self._slide_animation.setStartValue(current_pos)
        self._slide_animation.setEndValue(end_pos)
        self._slide_animation.start()

    # Enhanced public API methods
    def setTitle(self, title: str):
        """Set alert title with smooth update"""
        self._title = title
        if hasattr(self, '_title_label'):
            self._title_label.setText(title)
            FluentMicroInteraction.pulse_animation(self._title_label, 1.03)

    def setMessage(self, message: str):
        """Set alert message with smooth update"""
        self._message = message
        if hasattr(self, '_message_label'):
            self._message_label.setText(message)
            FluentMicroInteraction.pulse_animation(self._message_label, 1.02)

    def setAlertType(self, alert_type: AlertType):
        """Set alert type with smooth transition"""
        old_type = self._alert_type
        self._alert_type = alert_type

        # Update accessibility
        self.setAccessibleName(f"{alert_type.value.title()} Alert")

        # Animate the change
        if old_type != alert_type:
            FluentMicroInteraction.pulse_animation(self, 1.05)
            QTimer.singleShot(150, self._update_style)
        else:
            self._update_style()

    def focusInEvent(self, event):
        """Enhanced focus in event with visual feedback"""
        self.focus_changed.emit(True)
        FluentMicroInteraction.pulse_animation(self, 1.02)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Enhanced focus out event"""
        self.focus_changed.emit(False)
        super().focusOutEvent(event)


# Enhanced Notification Class
class EnhancedFluentNotification(QWidget):
    """
    Enhanced floating notification component with modern animations and features
    """

    closed = Signal()
    clicked = Signal()
    priority_changed = Signal(AlertPriority)

    def __init__(self,
                 title: str = "",
                 message: str = "",
                 notification_type: AlertType = AlertType.INFO,
                 priority: AlertPriority = AlertPriority.NORMAL,
                 timeout: int = 5000,
                 closable: bool = True,
                 clickable: bool = False,
                 action_text: str = "",
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._message = message
        self._notification_type = notification_type
        self._priority = priority
        self._timeout = timeout
        self._closable = closable
        self._clickable = clickable
        self._action_text = action_text

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._setup_ui()
        self._setup_enhanced_animations()
        self._connect_theme()

        if timeout > 0:
            QTimer.singleShot(timeout, self.close_with_animation)

    def _setup_ui(self):
        """Setup enhanced UI components"""
        # Main container with modern styling
        self._container = QFrame()
        self._container.setFrameStyle(QFrame.Shape.NoFrame)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._container)

        container_layout = QHBoxLayout(self._container)
        container_layout.setContentsMargins(20, 16, 20, 16)
        container_layout.setSpacing(16)

        # Icon with priority-based sizing
        icon_size = 24 if self._priority.value <= 2 else 32
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(icon_size, icon_size)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self._icon_label)

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

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

        # Action button (if specified)
        if self._action_text:
            self._action_button = QPushButton(self._action_text)
            self._action_button.clicked.connect(self._on_action_clicked)
            container_layout.addWidget(self._action_button)

        # Close button
        if self._closable:
            self._close_button = QPushButton("✕")
            self._close_button.setFixedSize(24, 24)
            self._close_button.clicked.connect(self.close_with_animation)
            container_layout.addWidget(self._close_button)

        # Click event
        if self._clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Dynamic width based on priority
        base_width = 320 if self._priority.value <= 2 else 380
        self.setFixedWidth(base_width)
        self.adjustSize()

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system"""
        self._opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self._opacity_effect)

        # Enhanced animations with priority-based durations
        duration_multiplier = 1.0 + (self._priority.value - 1) * 0.2

        self._fade_animation = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        self._fade_animation.setDuration(int(350 * duration_multiplier))
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutBack)
        self._fade_animation.finished.connect(self._on_animation_finished)

        self._slide_animation = QPropertyAnimation(self, QByteArray(b"pos"))
        self._slide_animation.setDuration(int(400 * duration_multiplier))
        self._slide_animation.setEasingCurve(QEasingCurve.Type.OutBack)

        # Show notification with enhanced entrance
        QTimer.singleShot(50, self.show_notification)

    def _connect_theme(self):
        """Connect theme updates"""
        theme_manager.theme_changed.connect(self._update_style)
        self._update_style()

    def _update_style(self):
        """Update component styles with enhanced theming"""
        theme = theme_manager
        accent_color, _, _ = self._get_colors()

        # Modern container style with priority-based enhancement
        if theme._current_mode == ThemeMode.DARK:
            bg_color = QColor(35, 35, 35)
            border_color = QColor(80, 80, 80)
        else:
            bg_color = QColor(255, 255, 255)
            border_color = QColor(200, 200, 200)

        # Priority-based visual enhancements
        if self._priority.value >= 3:
            bg_color = bg_color.lighter(105)
            border_color = accent_color

        self._container.setStyleSheet(f"""            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, 250),
                    stop:1 rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, 235));
                border: 1px solid rgba({border_color.red()}, {border_color.green()}, {border_color.blue()}, 200);
                border-radius: 12px;
            }}
        """)

        self._update_text_styles()
        self._update_button_styles()
        self._update_icon()

    def _update_text_styles(self):
        """Update text component styles"""
        theme = theme_manager
        text_color = QColor(theme.get_color('text_primary'))

        self._title_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color.name()};
                font-weight: 700;
                font-size: 14px;
                background: transparent;
            }}
        """)

        if hasattr(self, '_message_label'):
            self._message_label.setStyleSheet(f"""
                QLabel {{
                    color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 180);
                    font-size: 12px;
                    background: transparent;
                    line-height: 1.3;
                }}
            """)

    def _update_button_styles(self):
        """Update button component styles"""
        theme = theme_manager
        accent_color, _, _ = self._get_colors()
        text_color = QColor(theme.get_color('text_primary'))

        if hasattr(self, '_action_button'):
            self._action_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {accent_color.name()};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: 600;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {accent_color.lighter(110).name()};
                }}
                QPushButton:pressed {{
                    background-color: {accent_color.darker(110).name()};
                }}
            """)

        if hasattr(self, '_close_button'):
            self._close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color.name()};
                    border: none;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 40);
                }}
                QPushButton:pressed {{
                    background-color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 60);
                }}
            """)

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
        elif self._notification_type == AlertType.CRITICAL:
            return (QColor(139, 0, 0), QColor(255, 240, 240), QColor(100, 0, 0))
        else:
            theme = theme_manager
            return (QColor(theme.get_color('accent')), QColor(theme.get_color('background')), QColor(theme.get_color('text_primary')))

    def _update_icon(self):
        """Update icon with enhanced styling"""
        icon_map = {
            AlertType.INFO: "ℹ",
            AlertType.SUCCESS: "✓",
            AlertType.WARNING: "⚠",
            AlertType.ERROR: "✗",
            AlertType.CRITICAL: "⚡",
            AlertType.NEUTRAL: "○"
        }

        icon_text = icon_map.get(self._notification_type, "ℹ")
        accent_color, _, _ = self._get_colors()

        # Priority-based icon styling
        font_size = 18 if self._priority.value <= 2 else 22

        self._icon_label.setText(icon_text)
        self._icon_label.setStyleSheet(f"""
            QLabel {{
                color: {accent_color.name()};
                font-size: {font_size}px;
                font-weight: bold;
                background: transparent;
            }}
        """)

    def _on_action_clicked(self):
        """Handle action button click"""
        FluentMicroInteraction.button_press(self._action_button)
        self.clicked.emit()

    def show_notification(self):
        """Show notification with enhanced entrance animation"""
        screen_geometry = QApplication.primaryScreen().geometry()

        # Priority-based positioning
        margin = 20 if self._priority.value <= 2 else 30

        start_pos = QPoint(screen_geometry.width() - self.width() - margin,
                           screen_geometry.height() + 100)
        end_pos = QPoint(screen_geometry.width() - self.width() - margin,
                         screen_geometry.height() - self.height() - margin)

        self.move(start_pos)
        self.show()

        # Enhanced entrance sequence
        self._slide_animation.setStartValue(start_pos)
        self._slide_animation.setEndValue(end_pos)
        self._slide_animation.start()

        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.start()

        # Priority-based attention effects
        if self._priority.value >= 3:
            QTimer.singleShot(
                500, lambda: FluentMicroInteraction.pulse_animation(self, 1.05))

    def close_with_animation(self):
        """Close with enhanced exit animation"""
        current_pos = self.pos()
        end_pos = QPoint(current_pos.x() + 400, current_pos.y())

        self._slide_animation.setStartValue(current_pos)
        self._slide_animation.setEndValue(end_pos)
        self._slide_animation.start()

        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.start()

    def _on_animation_finished(self):
        """Animation completed handler"""
        if self._fade_animation.endValue() == 0.0:
            self.close()
            self.closed.emit()

    def mousePressEvent(self, event):
        """Enhanced mouse press event"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            FluentMicroInteraction.ripple_effect(self)
            self.clicked.emit()
        super().mousePressEvent(event)    # Enhanced public API
    def setPriority(self, priority: AlertPriority):
        """Set notification priority with visual update"""
        if self._priority != priority:
            self._priority = priority
            self.priority_changed.emit(priority)
            self._update_style()
            FluentMicroInteraction.pulse_animation(self, 1.03)

    def setMessage(self, message: str):
        """Set notification message with smooth update"""
        self._message = message
        if hasattr(self, '_message_label'):
            self._message_label.setText(message)
            FluentMicroInteraction.pulse_animation(self._message_label, 1.02)

    def setMessageType(self, notification_type: AlertType):
        """Set notification type with smooth transition"""
        old_type = self._notification_type
        self._notification_type = notification_type

        # Animate the change
        if old_type != notification_type:
            FluentMicroInteraction.pulse_animation(self, 1.05)
            QTimer.singleShot(150, self._update_style)
        else:
            self._update_style()


# Enhanced Message Bar Class
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
        self._setup_animations()
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

    def _setup_animations(self):
        """Setup animations"""
        # Reveal animation
        QTimer.singleShot(50, lambda: self._show_with_animation())

    def _show_with_animation(self):
        """Show with slide-in animation"""
        if not hasattr(self, '_slide_animation'):
            self._slide_animation = QPropertyAnimation(self, QByteArray(b"maximumHeight"))
            self._slide_animation.setDuration(300)
            self._slide_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Start collapsed and expand
        self.setMaximumHeight(0)
        target_height = self.sizeHint().height()
        self._slide_animation.setStartValue(0)
        self._slide_animation.setEndValue(target_height)
        self._slide_animation.start()

    def _connect_theme(self):
        """Connect theme updates"""
        theme_manager.theme_changed.connect(self._update_style)
        self._update_style()

    def _update_style(self):
        """Update component styles"""
        accent_color, bg_color, text_color = self._get_colors()

        # Adjust background color transparency
        bg_color.setAlpha(200)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, {bg_color.alpha()});
                border-left: 4px solid {accent_color.name()};
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
                }}
                QPushButton:hover {{
                    background-color: rgba({accent_color.red()}, {accent_color.green()}, {accent_color.blue()}, 30);
                }}
                QPushButton:pressed {{
                    background-color: rgba({accent_color.red()}, {accent_color.green()}, {accent_color.blue()}, 50);
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
                }}
                QPushButton:hover {{
                    background-color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 30);
                }}
                QPushButton:pressed {{
                    background-color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 50);
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
        """Update icon"""
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
        """Handle action button click"""
        pass  # Placeholder for micro-interaction

    def _on_close_button_clicked(self):
        """Handle close button click"""
        pass  # Placeholder for micro-interaction

    def _close_clicked(self):
        """Close button clicked"""
        if hasattr(self, '_slide_animation'):
            self._slide_animation.setStartValue(self.height())
            self._slide_animation.setEndValue(0)
            self._slide_animation.finished.connect(self._finish_close)
            self._slide_animation.start()
        else:
            self._finish_close()

    def _finish_close(self):
        """Finish close operation"""
        self.hide()
        self.closed.emit()

    def setMessage(self, message: str):
        """Set message"""
        self._message = message
        self._message_label.setText(message)

    def setMessageType(self, message_type: AlertType):
        """Set message type"""
        self._message_type = message_type
        self._update_style()


# Convenience factory functions
def create_info_alert(title: str, message: str, **kwargs) -> EnhancedFluentAlert:
    """Create an info alert with enhanced features"""
    return EnhancedFluentAlert(title, message, AlertType.INFO, **kwargs)


def create_success_alert(title: str, message: str, **kwargs) -> EnhancedFluentAlert:
    """Create a success alert with enhanced features"""
    return EnhancedFluentAlert(title, message, AlertType.SUCCESS, **kwargs)


def create_warning_alert(title: str, message: str, **kwargs) -> EnhancedFluentAlert:
    """Create a warning alert with enhanced features"""
    return EnhancedFluentAlert(title, message, AlertType.WARNING, **kwargs)


def create_error_alert(title: str, message: str, **kwargs) -> EnhancedFluentAlert:
    """Create an error alert with enhanced features"""
    return EnhancedFluentAlert(title, message, AlertType.ERROR, **kwargs)


def create_critical_alert(title: str, message: str, **kwargs) -> EnhancedFluentAlert:
    """Create a critical alert with enhanced features"""
    return EnhancedFluentAlert(title, message, AlertType.CRITICAL,
                               priority=AlertPriority.URGENT, **kwargs)


def show_notification(title: str, message: str, notification_type: AlertType = AlertType.INFO,
                      priority: AlertPriority = AlertPriority.NORMAL, **kwargs) -> EnhancedFluentNotification:
    """Show an enhanced notification"""
    notification = EnhancedFluentNotification(
        title, message, notification_type, priority, **kwargs)
    return notification
