"""
Fluent Design Status and Notification Components
Status indicators, progress trackers, notifications, and informational displays
"""

from PySide6.QtWidgets import (QWidget, QLabel, QFrame, QVBoxLayout, QHBoxLayout,
                               QGraphicsOpacityEffect, QScrollArea, QPushButton,
                               QSizePolicy)
from PySide6.QtCore import (Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve,
                           QRect, QPoint, QByteArray)
from PySide6.QtGui import (QPainter, QColor, QBrush, QPen, QFont, QIcon,
                          QPaintEvent)
from core.theme import theme_manager
from typing import Optional, List, Tuple
from enum import Enum


class NotificationLevel(Enum):
    """Notification levels"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class FluentStatusIndicator(QWidget):
    """Fluent Design style status indicator"""
    
    def __init__(self, status: str = "inactive", size: int = 12, 
                 animated: bool = True, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._status = status
        self._size = size
        self._animated = animated
        self._pulse_value = 0.0
        
        self.setFixedSize(size + 4, size + 4)
        
        if animated:
            self._setup_animation()
        
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animation(self):
        """Setup pulse animation"""
        self._animation = QPropertyAnimation(self, QByteArray(b"pulse_value"))
        self._animation.setDuration(1500)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._animation.setLoopCount(-1)  # Infinite loop
        
        if self._status in ["active", "success", "warning", "error"]:
            self._animation.start()

    def setStatus(self, status: str):
        """Set status
        
        Args:
            status: One of 'active', 'inactive', 'success', 'warning', 'error', 'pending'
        """
        self._status = status
        
        if hasattr(self, '_animation'):
            if status in ["active", "success", "warning", "error"]:
                self._animation.start()
            else:
                self._animation.stop()
        
        self.update()

    def getStatus(self) -> str:
        """Get current status"""
        return self._status

    def setPulseValue(self, value: float):
        """Set pulse animation value"""
        self._pulse_value = value
        self.update()

    def getPulseValue(self) -> float:
        """Get pulse animation value"""
        return self._pulse_value

    # Property for animation
    pulse_value = property(getPulseValue, setPulseValue)

    def paintEvent(self, event: QPaintEvent):
        """Paint status indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = theme_manager
        rect = self.rect()
        center = rect.center()
        radius = self._size // 2
        
        # Status color mapping
        status_colors = {
            "active": QColor("#28a745"),     # Green
            "inactive": theme.get_color('border'),
            "success": QColor("#28a745"),    # Green
            "warning": QColor("#ffc107"),    # Yellow
            "error": QColor("#dc3545"),      # Red
            "pending": QColor("#17a2b8"),    # Blue
            "info": theme.get_color('primary')
        }
        
        color = status_colors.get(self._status, theme.get_color('border'))
        
        # Draw main indicator
        if self._animated and self._status in ["active", "success", "warning", "error"]:
            # Animated pulse effect
            pulse_radius = radius + (self._pulse_value * radius * 0.5)
            pulse_opacity = 1.0 - self._pulse_value
            
            # Draw pulse ring
            pulse_color = QColor(color)
            pulse_color.setAlphaF(pulse_opacity * 0.6)
            painter.setBrush(QBrush(pulse_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, int(pulse_radius), int(pulse_radius))
        
        # Draw main circle
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(120), 1))
        painter.drawEllipse(center, radius, radius)
        
        # Inner highlight for active states
        if self._status in ["active", "success"]:
            highlight_color = QColor(255, 255, 255, 100)
            painter.setBrush(QBrush(highlight_color))
            painter.setPen(Qt.PenStyle.NoPen)
            highlight_radius = radius // 2
            highlight_offset = radius // 3
            painter.drawEllipse(center.x() - highlight_offset, 
                              center.y() - highlight_offset,
                              highlight_radius, highlight_radius)

    def _setup_style(self):
        """Setup style"""
        self.setStyleSheet("""
            FluentStatusIndicator {
                background-color: transparent;
            }
        """)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self.update()


class FluentProgressTracker(QWidget):
    """Fluent Design style progress tracker for multi-step processes"""
    
    step_clicked = Signal(int)  # Step index
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._steps = []
        self._current_step = 0
        self._orientation = Qt.Orientation.Horizontal
        
        self.setMinimumSize(300, 60)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def addStep(self, title: str, description: str = "", icon: Optional[QIcon] = None):
        """Add step to tracker"""
        step_data = {
            'title': title,
            'description': description,
            'icon': icon,
            'status': 'pending'  # pending, active, completed, error
        }
        self._steps.append(step_data)
        self.update()

    def setStepStatus(self, index: int, status: str):
        """Set step status
        
        Args:
            index: Step index
            status: One of 'pending', 'active', 'completed', 'error'
        """
        if 0 <= index < len(self._steps):
            self._steps[index]['status'] = status
            self.update()

    def setCurrentStep(self, index: int):
        """Set current active step"""
        if 0 <= index < len(self._steps):
            # Update step statuses
            for i, step in enumerate(self._steps):
                if i < index:
                    step['status'] = 'completed'
                elif i == index:
                    step['status'] = 'active'
                else:
                    step['status'] = 'pending'
            
            self._current_step = index
            self.update()

    def getCurrentStep(self) -> int:
        """Get current step index"""
        return self._current_step

    def getStepCount(self) -> int:
        """Get total number of steps"""
        return len(self._steps)

    def nextStep(self):
        """Move to next step"""
        if self._current_step < len(self._steps) - 1:
            self.setCurrentStep(self._current_step + 1)

    def previousStep(self):
        """Move to previous step"""
        if self._current_step > 0:
            self.setCurrentStep(self._current_step - 1)

    def paintEvent(self, event: QPaintEvent):
        """Paint progress tracker"""
        if not self._steps:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = theme_manager
        rect = self.rect()
        
        step_width = rect.width() / len(self._steps)
        circle_radius = 20
        line_y = rect.height() // 2
        
        # Status colors
        status_colors = {
            'pending': theme.get_color('border'),
            'active': theme.get_color('primary'),
            'completed': QColor("#28a745"),
            'error': QColor("#dc3545")
        }
        
        # Draw connecting lines
        if len(self._steps) > 1:
            for i in range(len(self._steps) - 1):
                start_x = (i + 0.5) * step_width + circle_radius
                end_x = (i + 1.5) * step_width - circle_radius
                
                # Line color based on completion
                if self._steps[i]['status'] == 'completed':
                    line_color = status_colors['completed']
                else:
                    line_color = theme.get_color('border')
                
                painter.setPen(QPen(line_color, 3))
                painter.drawLine(int(start_x), line_y, int(end_x), line_y)
        
        # Draw step circles and labels
        for i, step in enumerate(self._steps):
            center_x = (i + 0.5) * step_width
            center_y = line_y
            
            status = step['status']
            color = status_colors[status]
            
            # Draw circle
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(120), 2))
            painter.drawEllipse(int(center_x - circle_radius), 
                              int(center_y - circle_radius),
                              circle_radius * 2, circle_radius * 2)
            
            # Draw step number or icon
            painter.setPen(QPen(QColor("white")))
            painter.setFont(QFont("", 11, QFont.Weight.Bold))
            
            if step['icon'] and not step['icon'].isNull():
                # Draw icon (simplified - just draw step number for now)
                painter.drawText(QRect(int(center_x - circle_radius), 
                                     int(center_y - circle_radius),
                                     circle_radius * 2, circle_radius * 2),
                               Qt.AlignmentFlag.AlignCenter, str(i + 1))
            else:
                painter.drawText(QRect(int(center_x - circle_radius), 
                                     int(center_y - circle_radius),
                                     circle_radius * 2, circle_radius * 2),
                               Qt.AlignmentFlag.AlignCenter, str(i + 1))
            
            # Draw step title
            painter.setPen(QPen(theme.get_color('text_primary')))
            painter.setFont(QFont("", 10, QFont.Weight.Bold))
            
            title_rect = QRect(int(center_x - step_width // 2), 
                             int(center_y + circle_radius + 8),
                             int(step_width), 20)
            painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, step['title'])
            
            # Draw step description
            if step['description']:
                painter.setPen(QPen(theme.get_color('text_secondary')))
                painter.setFont(QFont("", 8))
                
                desc_rect = QRect(int(center_x - step_width // 2), 
                                int(center_y + circle_radius + 28),
                                int(step_width), 16)
                painter.drawText(desc_rect, Qt.AlignmentFlag.AlignCenter, 
                               step['description'])

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if not self._steps:
            return
            
        step_width = self.width() / len(self._steps)
        clicked_step = int(event.pos().x() // step_width)
        
        if 0 <= clicked_step < len(self._steps):
            self.step_clicked.emit(clicked_step)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager
        self.setStyleSheet(f"""
            FluentProgressTracker {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
        """)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self.update()


class FluentNotification(QFrame):
    """Fluent Design style notification widget"""
    
    closed = Signal()
    action_clicked = Signal(str)  # Action name
    
    def __init__(self, title: str, message: str, level: NotificationLevel = NotificationLevel.INFO,
                 auto_hide: bool = True, duration: int = 5000, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._title = title
        self._message = message
        self._level = level
        self._auto_hide = auto_hide
        self._duration = duration
        self._actions = []
        
        self.setFixedHeight(80)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self._setup_ui()
        self._setup_style()
        
        if auto_hide:
            self._setup_auto_hide()
        
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_level_icon()
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        self.title_label = QLabel(self._title)
        self.title_label.setFont(QFont("", 12, QFont.Weight.Bold))
        
        self.message_label = QLabel(self._message)
        self.message_label.setFont(QFont("", 10))
        self.message_label.setWordWrap(True)
        
        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.message_label)
        
        # Actions area
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(8)
        
        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.clicked.connect(self._close_notification)
        
        layout.addWidget(self.icon_label)
        layout.addLayout(content_layout)
        layout.addLayout(self.actions_layout)
        layout.addWidget(self.close_btn)

    def _set_level_icon(self):
        """Set icon based on notification level"""
        # For now, use text symbols. In a real implementation, you'd use actual icons
        icons = {
            NotificationLevel.INFO: "ℹ",
            NotificationLevel.SUCCESS: "✓",
            NotificationLevel.WARNING: "⚠",
            NotificationLevel.ERROR: "✕"
        }
        
        self.icon_label.setText(icons.get(self._level, "ℹ"))
        self.icon_label.setFont(QFont("", 14, QFont.Weight.Bold))

    def addActionButton(self, action_name: str, action_text: str):
        """Add action button (renamed to avoid conflict with QWidget.addAction)"""
        action_btn = QPushButton(action_text)
        action_btn.clicked.connect(lambda: self._on_action_clicked(action_name))
        
        self._actions.append((action_name, action_btn))
        self.actions_layout.addWidget(action_btn)

    def _on_action_clicked(self, action_name: str):
        """Handle action click"""
        self.action_clicked.emit(action_name)

    def _setup_auto_hide(self):
        """Setup auto-hide timer"""
        self._hide_timer = QTimer()
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._close_notification)
        self._hide_timer.start(self._duration)

    def _close_notification(self):
        """Close notification with animation"""
        self.closed.emit()
        
        # Fade out animation
        effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(effect)
        
        self._fade_animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
        self._fade_animation.setDuration(300)
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.finished.connect(self.deleteLater)
        self._fade_animation.start()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager
        
        # Level-specific colors
        level_colors = {
            NotificationLevel.INFO: theme.get_color('primary'),
            NotificationLevel.SUCCESS: QColor("#28a745"),
            NotificationLevel.WARNING: QColor("#ffc107"),
            NotificationLevel.ERROR: QColor("#dc3545")
        }
        
        accent_color = level_colors.get(self._level, theme.get_color('primary'))
        
        style_sheet = f"""
            FluentNotification {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-left: 4px solid {accent_color.name()};
                border-radius: 8px;
                margin: 4px;
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                background-color: transparent;
                border: none;
            }}
            QPushButton {{
                background-color: {accent_color.name()};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {accent_color.darker(110).name()};
            }}
        """
        
        # Special style for close button
        close_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {theme.get_color('text_secondary').name()};
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                color: {theme.get_color('text_primary').name()};
            }}
        """
        
        self.setStyleSheet(style_sheet)
        self.close_btn.setStyleSheet(close_style)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentNotificationManager(QWidget):
    """Notification manager for displaying notifications"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._notifications = []
        self._max_notifications = 5
        
        self._setup_ui()
        self._setup_style()
        
        # Position at top-right of parent
        if parent:
            self._position_manager()
        
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setFixedWidth(350)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area for notifications
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.notifications_widget = QWidget()
        self.notifications_layout = QVBoxLayout(self.notifications_widget)
        self.notifications_layout.setContentsMargins(0, 0, 0, 0)
        self.notifications_layout.setSpacing(0)
        self.notifications_layout.addStretch()
        
        self.scroll_area.setWidget(self.notifications_widget)
        layout.addWidget(self.scroll_area)

    def showNotification(self, title: str, message: str, 
                        level: NotificationLevel = NotificationLevel.INFO,
                        auto_hide: bool = True, duration: int = 5000,
                        actions: Optional[List[Tuple[str, str]]] = None) -> FluentNotification:
        """Show notification
        
        Args:
            title: Notification title
            message: Notification message
            level: Notification level
            auto_hide: Auto-hide after duration
            duration: Auto-hide duration in milliseconds
            actions: List of (action_name, action_text) tuples
        
        Returns:
            Created notification widget
        """
        notification = FluentNotification(title, message, level, auto_hide, duration)
        notification.closed.connect(lambda: self._remove_notification(notification))
        
        # Add actions
        if actions:
            for action_name, action_text in actions:
                notification.addActionButton(action_name, action_text)
        
        # Add to layout (insert at top)
        self.notifications_layout.insertWidget(0, notification)
        self._notifications.insert(0, notification)
        
        # Remove old notifications if too many
        while len(self._notifications) > self._max_notifications:
            old_notification = self._notifications.pop()
            old_notification.deleteLater()
        
        # Slide-in animation
        self._animate_notification_in(notification)
        
        return notification

    def _animate_notification_in(self, notification: FluentNotification):
        """Animate notification sliding in"""
        # Start from the right
        original_pos = notification.pos()
        notification.move(self.width(), original_pos.y())
        notification.show()
        
        # Animate to original position
        animation = QPropertyAnimation(notification, QByteArray(b"pos"))
        animation.setDuration(300)
        animation.setStartValue(QPoint(self.width(), original_pos.y()))
        animation.setEndValue(original_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()

    def _remove_notification(self, notification: FluentNotification):
        """Remove notification from manager"""
        if notification in self._notifications:
            self._notifications.remove(notification)

    def _position_manager(self):
        """Position manager relative to parent"""
        parent_widget = self.parent()
        if parent_widget and isinstance(parent_widget, QWidget):
            parent_rect = parent_widget.rect()
            self.move(parent_rect.width() - self.width() - 20, 20)

    def clearAll(self):
        """Clear all notifications"""
        for notification in self._notifications.copy():
            notification._close_notification()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager
        
        style_sheet = f"""
            FluentNotificationManager {{
                background-color: transparent;
            }}
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """
        
        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentBadge(QLabel):
    """Fluent Design style badge for displaying counts or status"""
    
    def __init__(self, text: str = "", color: Optional[QColor] = None, 
                 parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        
        self._color = color
        self._pulse_enabled = False
        
        self._setup_style()
        self._size_to_content()
        
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def setText(self, text: str):
        """Set badge text"""
        super().setText(text)
        self._size_to_content()

    def setColor(self, color: QColor):
        """Set badge color"""
        self._color = color
        self._setup_style()

    def setPulseEnabled(self, enabled: bool):
        """Enable pulse animation"""
        self._pulse_enabled = enabled
        if enabled:
            self._setup_pulse_animation()
        else:
            if hasattr(self, '_pulse_animation'):
                self._pulse_animation.stop()

    def _size_to_content(self):
        """Size badge to fit content"""
        text = self.text()
        if not text:
            self.hide()
            return
        
        self.show()
        
        # Calculate size based on text
        metrics = self.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()
        
        # Minimum size for single characters
        min_size = 20
        width = max(min_size, text_width + 12)
        height = max(min_size, text_height + 6)
        
        self.setFixedSize(width, height)

    def _setup_pulse_animation(self):
        """Setup pulse animation"""
        if not hasattr(self, '_pulse_effect'):
            self._pulse_effect = QGraphicsOpacityEffect()
            self.setGraphicsEffect(self._pulse_effect)
        
        self._pulse_animation = QPropertyAnimation(self._pulse_effect, QByteArray(b"opacity"))
        self._pulse_animation.setDuration(1000)
        self._pulse_animation.setStartValue(0.5)
        self._pulse_animation.setEndValue(1.0)
        self._pulse_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse_animation.setLoopCount(-1)
        self._pulse_animation.start()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager
        
        color = self._color if self._color else theme.get_color('primary')
        text_color = "white" if color.lightness() < 128 else "black"
        
        style_sheet = f"""
            FluentBadge {{
                background-color: {color.name()};
                color: {text_color};
                border: none;
                border-radius: 10px;
                font-size: 11px;
                font-weight: bold;
                text-align: center;
                padding: 2px 6px;
            }}
        """
        
        self.setStyleSheet(style_sheet)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
