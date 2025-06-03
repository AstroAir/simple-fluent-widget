"""
FluentAlert Components Example
Comprehensive demonstration of all alert and notification features
"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QGridLayout, QFormLayout, QGroupBox,
                               QPushButton, QLabel, QTextEdit, QLineEdit, QSpinBox,
                               QComboBox, QCheckBox,
                               QSlider, QTabWidget,
                               QProgressBar)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from components.basic.alert import (EnhancedFluentAlert, EnhancedFluentNotification,
                                    EnhancedFluentNotification, AlertType)
from core.theme import theme_manager


class NotificationManager:
    """Manages notifications positioning and lifecycle"""

    def __init__(self):
        self.notifications = []
        self.max_notifications = 5

    def show_notification(self, notification):
        """Show notification with proper positioning"""
        # Remove old notifications if limit exceeded
        if len(self.notifications) >= self.max_notifications:
            oldest = self.notifications.pop(0)
            oldest.close_with_animation()

        # Position new notification
        self._position_notification(notification)
        self.notifications.append(notification)

        # Connect close signal to cleanup
        notification.closed.connect(
            lambda: self._remove_notification(notification))

    def _position_notification(self, notification):
        """Position notification in the stack"""
        screen = QApplication.primaryScreen().geometry()
        base_x = screen.width() - notification.width() - 20
        base_y = screen.height() - 20

        # Stack notifications
        for i, existing in enumerate(self.notifications):
            base_y -= existing.height() + 10

        notification.move(base_x, base_y - notification.height())

    def _remove_notification(self, notification):
        """Remove notification from management"""
        if notification in self.notifications:
            self.notifications.remove(notification)
            # Reposition remaining notifications
            self._reposition_notifications()

    def _reposition_notifications(self):
        """Reposition all notifications after removal"""
        screen = QApplication.primaryScreen().geometry()
        base_x = screen.width() - 370
        base_y = screen.height() - 20

        for notification in reversed(self.notifications):
            notification.move(base_x, base_y - notification.height())
            base_y -= notification.height() + 10


class AlertDemoWidget(QWidget):
    """Widget demonstrating alert functionalities"""

    def __init__(self):
        super().__init__()
        self.notification_manager = NotificationManager()
        self.message_bars = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title = QLabel("FluentAlert Component Showcase")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Create tabs for different features
        tab_widget = QTabWidget()

        # Basic Alerts Tab
        tab_widget.addTab(self._create_basic_alerts_tab(), "Basic Alerts")

        # Notifications Tab
        tab_widget.addTab(self._create_notifications_tab(), "Notifications")

        # Message Bars Tab
        tab_widget.addTab(self._create_message_bars_tab(), "Message Bars")

        # Advanced Features Tab
        tab_widget.addTab(
            self._create_advanced_features_tab(), "Advanced Features")

        # Interactive Demo Tab
        tab_widget.addTab(self._create_interactive_demo_tab(),
                          "Interactive Demo")

        layout.addWidget(tab_widget)

    def _create_basic_alerts_tab(self):
        """Create basic alerts demonstration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Control panel
        control_group = QGroupBox("Alert Controls")
        control_layout = QGridLayout(control_group)

        # Alert type selection
        control_layout.addWidget(QLabel("Alert Type:"), 0, 0)
        self.alert_type_combo = QComboBox()
        self.alert_type_combo.addItems(["Info", "Success", "Warning", "Error"])
        control_layout.addWidget(self.alert_type_combo, 0, 1)

        # Title and message inputs
        control_layout.addWidget(QLabel("Title:"), 1, 0)
        self.alert_title_input = QLineEdit("Sample Alert Title")
        control_layout.addWidget(self.alert_title_input, 1, 1)

        control_layout.addWidget(QLabel("Message:"), 2, 0)
        self.alert_message_input = QTextEdit(
            "This is a sample alert message that demonstrates the alert functionality.")
        self.alert_message_input.setMaximumHeight(80)
        control_layout.addWidget(self.alert_message_input, 2, 1)

        # Options
        self.alert_closable_check = QCheckBox("Closable")
        self.alert_closable_check.setChecked(True)
        control_layout.addWidget(self.alert_closable_check, 3, 0)

        self.alert_action_check = QCheckBox("Action Button")
        control_layout.addWidget(self.alert_action_check, 3, 1)

        self.alert_action_text = QLineEdit("Action")
        self.alert_action_text.setEnabled(False)
        self.alert_action_check.toggled.connect(
            self.alert_action_text.setEnabled)
        control_layout.addWidget(self.alert_action_text, 4, 1)

        # Timeout
        control_layout.addWidget(QLabel("Auto-close (ms):"), 5, 0)
        self.alert_timeout_spin = QSpinBox()
        self.alert_timeout_spin.setRange(0, 30000)
        self.alert_timeout_spin.setValue(0)
        self.alert_timeout_spin.setSpecialValueText("No timeout")
        control_layout.addWidget(self.alert_timeout_spin, 5, 1)

        # Create alert button
        create_alert_btn = QPushButton("Create Alert")
        create_alert_btn.clicked.connect(self._create_sample_alert)
        create_alert_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        control_layout.addWidget(create_alert_btn, 6, 0, 1, 2)

        layout.addWidget(control_group)

        # Quick examples
        examples_group = QGroupBox("Quick Examples")
        examples_layout = QGridLayout(examples_group)

        # Predefined alert examples
        examples = [
            ("Info Alert", AlertType.INFO, "Information",
             "This is an informational message."),
            ("Success Alert", AlertType.SUCCESS, "Success!",
             "Operation completed successfully."),
            ("Warning Alert", AlertType.WARNING,
             "Warning", "Please review your input."),
            ("Error Alert", AlertType.ERROR, "Error",
             "An error occurred during processing.")
        ]

        for i, (btn_text, alert_type, title, message) in enumerate(examples):
            btn = QPushButton(btn_text)
            btn.clicked.connect(lambda checked, t=alert_type, tit=title, msg=message:
                                self._create_predefined_alert(t, tit, msg))
            examples_layout.addWidget(btn, i // 2, i % 2)

        layout.addWidget(examples_group)

        # Alert display area
        self.alert_display_area = QVBoxLayout()
        alert_container = QGroupBox("Active Alerts")
        alert_container.setLayout(self.alert_display_area)
        layout.addWidget(alert_container)

        return widget

    def _create_notifications_tab(self):
        """Create notifications demonstration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Notification controls
        control_group = QGroupBox("Notification Controls")
        control_layout = QFormLayout(control_group)

        # Notification type
        self.notif_type_combo = QComboBox()
        self.notif_type_combo.addItems(["Info", "Success", "Warning", "Error"])
        control_layout.addRow("Type:", self.notif_type_combo)

        # Title and message
        self.notif_title_input = QLineEdit("Notification Title")
        control_layout.addRow("Title:", self.notif_title_input)

        self.notif_message_input = QLineEdit("This is a notification message.")
        control_layout.addRow("Message:", self.notif_message_input)

        # Options
        self.notif_closable_check = QCheckBox("Closable")
        self.notif_closable_check.setChecked(True)
        control_layout.addRow(self.notif_closable_check)

        self.notif_clickable_check = QCheckBox("Clickable")
        control_layout.addRow(self.notif_clickable_check)

        # Timeout
        self.notif_timeout_spin = QSpinBox()
        self.notif_timeout_spin.setRange(1000, 30000)
        self.notif_timeout_spin.setValue(5000)
        self.notif_timeout_spin.setSuffix(" ms")
        control_layout.addRow("Timeout:", self.notif_timeout_spin)

        # Create notification button
        create_notif_btn = QPushButton("Show Notification")
        create_notif_btn.clicked.connect(self._create_notification)
        create_notif_btn.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0e6e0e;
            }
        """)
        control_layout.addRow(create_notif_btn)

        layout.addWidget(control_group)

        # Batch notifications
        batch_group = QGroupBox("Batch Notifications")
        batch_layout = QGridLayout(batch_group)

        batch_buttons = [
            ("Show Info Series", self._show_info_series),
            ("Show Mixed Types", self._show_mixed_notifications),
            ("Stress Test", self._stress_test_notifications),
            ("Clear All", self._clear_all_notifications)
        ]

        for i, (text, handler) in enumerate(batch_buttons):
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            batch_layout.addWidget(btn, i // 2, i % 2)

        layout.addWidget(batch_group)

        # Notification statistics
        stats_group = QGroupBox("Notification Statistics")
        stats_layout = QFormLayout(stats_group)

        self.active_notifications_label = QLabel("0")
        stats_layout.addRow("Active Notifications:",
                            self.active_notifications_label)

        self.total_shown_label = QLabel("0")
        stats_layout.addRow("Total Shown:", self.total_shown_label)

        # Update stats timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_stats)
        self.stats_timer.start(500)

        self.total_notifications_shown = 0

        layout.addWidget(stats_group)

        return widget

    def _create_message_bars_tab(self):
        """Create message bars demonstration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Message bar controls
        control_group = QGroupBox("Message Bar Controls")
        control_layout = QFormLayout(control_group)

        # Message type
        self.msgbar_type_combo = QComboBox()
        self.msgbar_type_combo.addItems(
            ["Info", "Success", "Warning", "Error"])
        control_layout.addRow("Type:", self.msgbar_type_combo)

        # Message
        self.msgbar_message_input = QLineEdit(
            "This is a message bar notification.")
        control_layout.addRow("Message:", self.msgbar_message_input)

        # Options
        self.msgbar_closable_check = QCheckBox("Closable")
        self.msgbar_closable_check.setChecked(True)
        control_layout.addRow(self.msgbar_closable_check)

        self.msgbar_action_check = QCheckBox("Action Button")
        control_layout.addRow(self.msgbar_action_check)

        self.msgbar_action_text = QLineEdit("Retry")
        self.msgbar_action_text.setEnabled(False)
        self.msgbar_action_check.toggled.connect(
            self.msgbar_action_text.setEnabled)
        control_layout.addRow("Action Text:", self.msgbar_action_text)

        # Create message bar button
        create_msgbar_btn = QPushButton("Add Message Bar")
        create_msgbar_btn.clicked.connect(self._create_message_bar)
        create_msgbar_btn.setStyleSheet("""
            QPushButton {
                background-color: #ca5010;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4440e;
            }
        """)
        control_layout.addRow(create_msgbar_btn)

        layout.addWidget(control_group)

        # Quick message bar examples
        examples_group = QGroupBox("Quick Examples")
        examples_layout = QGridLayout(examples_group)

        examples = [
            ("Connection Lost", AlertType.ERROR,
             "Connection to server lost. Check your internet connection."),
            ("File Saved", AlertType.SUCCESS,
             "Document has been saved successfully."),
            ("Low Storage", AlertType.WARNING,
             "Storage space is running low. Consider cleaning up files."),
            ("New Update", AlertType.INFO,
             "A new version is available. Click to download.")
        ]

        for i, (btn_text, msg_type, message) in enumerate(examples):
            btn = QPushButton(btn_text)
            btn.clicked.connect(lambda checked, t=msg_type, m=message:
                                self._create_predefined_message_bar(t, m))
            examples_layout.addWidget(btn, i // 2, i % 2)

        layout.addWidget(examples_group)

        # Message bar display area
        self.msgbar_display_area = QVBoxLayout()
        msgbar_container = QGroupBox("Active Message Bars")
        msgbar_container.setLayout(self.msgbar_display_area)
        layout.addWidget(msgbar_container)

        # Clear all message bars button
        clear_msgbars_btn = QPushButton("Clear All Message Bars")
        clear_msgbars_btn.clicked.connect(self._clear_all_message_bars)
        layout.addWidget(clear_msgbars_btn)

        return widget

    def _create_advanced_features_tab(self):
        """Create advanced features demonstration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Theme integration
        theme_group = QGroupBox("Theme Integration")
        theme_layout = QGridLayout(theme_group)

        theme_demo_btn = QPushButton("Test Theme Changes")
        theme_demo_btn.clicked.connect(self._demo_theme_changes)
        theme_layout.addWidget(theme_demo_btn, 0, 0)

        layout.addWidget(theme_group)

        # Animation controls
        animation_group = QGroupBox("Animation Controls")
        animation_layout = QFormLayout(animation_group)

        # Animation speed
        self.animation_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.animation_speed_slider.setRange(100, 2000)
        self.animation_speed_slider.setValue(400)
        self.animation_speed_label = QLabel("400ms")
        self.animation_speed_slider.valueChanged.connect(
            lambda v: self.animation_speed_label.setText(f"{v}ms"))

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(self.animation_speed_slider)
        speed_layout.addWidget(self.animation_speed_label)
        animation_layout.addRow("Animation Speed:", speed_layout)

        # Test animation button
        test_animation_btn = QPushButton("Test Animation Speed")
        test_animation_btn.clicked.connect(self._test_animation_speed)
        animation_layout.addRow(test_animation_btn)

        layout.addWidget(animation_group)

        # Event handling demo
        events_group = QGroupBox("Event Handling")
        events_layout = QVBoxLayout(events_group)

        # Event log
        self.event_log = QTextEdit()
        self.event_log.setMaximumHeight(200)
        self.event_log.setReadOnly(True)
        events_layout.addWidget(QLabel("Event Log:"))
        events_layout.addWidget(self.event_log)

        # Create alert with events
        create_event_alert_btn = QPushButton("Create Alert with Event Logging")
        create_event_alert_btn.clicked.connect(self._create_event_alert)
        events_layout.addWidget(create_event_alert_btn)

        # Clear log
        clear_log_btn = QPushButton("Clear Event Log")
        clear_log_btn.clicked.connect(self.event_log.clear)
        events_layout.addWidget(clear_log_btn)

        layout.addWidget(events_group)

        # Performance monitoring
        performance_group = QGroupBox("Performance Monitoring")
        performance_layout = QFormLayout(performance_group)

        self.render_time_label = QLabel("0ms")
        performance_layout.addRow("Last Render Time:", self.render_time_label)

        self.memory_usage_label = QLabel("0 KB")
        performance_layout.addRow("Estimated Memory:", self.memory_usage_label)

        # Performance test
        perf_test_btn = QPushButton("Run Performance Test")
        perf_test_btn.clicked.connect(self._run_performance_test)
        performance_layout.addRow(perf_test_btn)

        layout.addWidget(performance_group)

        return widget

    def _create_interactive_demo_tab(self):
        """Create interactive demo tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Scenario selector
        scenario_group = QGroupBox("Demo Scenarios")
        scenario_layout = QGridLayout(scenario_group)

        scenarios = [
            ("App Update Available", self._demo_app_update),
            ("Form Validation", self._demo_form_validation),
            ("File Operations", self._demo_file_operations),
            ("Network Status", self._demo_network_status),
            ("User Onboarding", self._demo_user_onboarding),
            ("Error Recovery", self._demo_error_recovery)
        ]

        for i, (name, handler) in enumerate(scenarios):
            btn = QPushButton(name)
            btn.clicked.connect(handler)
            scenario_layout.addWidget(btn, i // 2, i % 2)

        layout.addWidget(scenario_group)

        # Simulation controls
        simulation_group = QGroupBox("Simulation Controls")
        simulation_layout = QFormLayout(simulation_group)

        # Auto demo checkbox
        self.auto_demo_check = QCheckBox("Auto Demo Mode")
        self.auto_demo_check.toggled.connect(self._toggle_auto_demo)
        simulation_layout.addRow(self.auto_demo_check)

        # Demo interval
        self.demo_interval_spin = QSpinBox()
        self.demo_interval_spin.setRange(1, 60)
        self.demo_interval_spin.setValue(10)
        self.demo_interval_spin.setSuffix(" seconds")
        simulation_layout.addRow("Demo Interval:", self.demo_interval_spin)

        # Auto demo timer
        self.auto_demo_timer = QTimer()
        self.auto_demo_timer.timeout.connect(self._run_auto_demo)

        layout.addWidget(simulation_group)

        # Demo status
        status_group = QGroupBox("Demo Status")
        status_layout = QVBoxLayout(status_group)

        self.demo_status_label = QLabel("Ready for demo")
        self.demo_status_label.setStyleSheet(
            "color: #0078d4; font-weight: bold;")
        status_layout.addWidget(self.demo_status_label)

        # Progress bar for timed demos
        self.demo_progress = QProgressBar()
        self.demo_progress.setVisible(False)
        status_layout.addWidget(self.demo_progress)

        layout.addWidget(status_group)

        return widget

    # Event handlers for basic alerts
    def _create_sample_alert(self):
        """Create a sample alert based on current settings"""
        alert_types = {
            "Info": AlertType.INFO,
            "Success": AlertType.SUCCESS,
            "Warning": AlertType.WARNING,
            "Error": AlertType.ERROR
        }

        alert_type = alert_types[self.alert_type_combo.currentText()]
        title = self.alert_title_input.text()
        message = self.alert_message_input.toPlainText()
        closable = self.alert_closable_check.isChecked()
        action_text = self.alert_action_text.text(
        ) if self.alert_action_check.isChecked() else ""
        timeout = self.alert_timeout_spin.value()

        alert = EnhancedFluentAlert(
            title=title,
            message=message,
            alert_type=alert_type,
            closable=closable,
            action_text=action_text,
            timeout=timeout if timeout > 0 else 0
        )

        # Connect events for demonstration
        alert.closed.connect(lambda: self._log_event("Alert closed"))
        if action_text:
            alert.action_clicked.connect(
                lambda: self._log_event("Alert action clicked"))

        # Add to display area
        self.alert_display_area.addWidget(alert)
        self._log_event(f"Created {alert_type.value} alert: {title}")

    def _create_predefined_alert(self, alert_type, title, message):
        """Create a predefined alert"""
        alert = EnhancedFluentAlert(
            title=title,
            message=message,
            alert_type=alert_type,
            closable=True
        )

        alert.closed.connect(lambda: self._log_event(
            f"Predefined alert closed: {title}"))
        self.alert_display_area.addWidget(alert)
        self._log_event(f"Created predefined alert: {title}")

    # Event handlers for notifications
    def _create_notification(self):
        """Create a notification based on current settings"""
        notif_types = {
            "Info": AlertType.INFO,
            "Success": AlertType.SUCCESS,
            "Warning": AlertType.WARNING,
            "Error": AlertType.ERROR
        }

        notif_type = notif_types[self.notif_type_combo.currentText()]
        title = self.notif_title_input.text()
        message = self.notif_message_input.text()
        closable = self.notif_closable_check.isChecked()
        clickable = self.notif_clickable_check.isChecked()
        timeout = self.notif_timeout_spin.value()

        notification = EnhancedFluentNotification(
            title=title,
            message=message,
            notification_type=notif_type,
            timeout=timeout,
            closable=closable,
            clickable=clickable
        )

        # Connect events
        notification.closed.connect(
            lambda: self._log_event("Notification closed"))
        if clickable:
            notification.clicked.connect(
                lambda: self._log_event("Notification clicked"))

        self.notification_manager.show_notification(notification)
        self.total_notifications_shown += 1
        self._log_event(f"Created notification: {title}")

    def _show_info_series(self):
        """Show a series of info notifications"""
        messages = [
            ("Step 1", "Initializing system components..."),
            ("Step 2", "Loading user preferences..."),
            ("Step 3", "Connecting to services..."),
            ("Complete", "System ready for use!")
        ]

        for i, (title, message) in enumerate(messages):
            QTimer.singleShot(i * 1500, lambda t=title,
                              m=message: self._create_timed_notification(t, m))

    def _create_timed_notification(self, title, message):
        """Create a timed notification"""
        notification = EnhancedFluentNotification(
            title=title,
            message=message,
            notification_type=AlertType.INFO,
            timeout=3000
        )
        self.notification_manager.show_notification(notification)
        self.total_notifications_shown += 1

    def _show_mixed_notifications(self):
        """Show mixed type notifications"""
        notifications_data = [
            ("Upload Started", "File upload initiated", AlertType.INFO),
            ("Upload Progress", "50% complete", AlertType.INFO),
            ("Upload Complete", "File uploaded successfully", AlertType.SUCCESS),
            ("Backup Created", "Automatic backup created", AlertType.INFO)
        ]

        for i, (title, message, notif_type) in enumerate(notifications_data):
            QTimer.singleShot(i * 1000, lambda t=title, m=message, nt=notif_type:
                              self._create_mixed_notification(t, m, nt))

    def _create_mixed_notification(self, title, message, notif_type):
        """Create a mixed type notification"""
        notification = EnhancedFluentNotification(
            title=title,
            message=message,
            notification_type=notif_type,
            timeout=4000
        )
        self.notification_manager.show_notification(notification)
        self.total_notifications_shown += 1

    def _stress_test_notifications(self):
        """Stress test with many notifications"""
        for i in range(10):
            QTimer.singleShot(
                i * 200, lambda idx=i: self._create_stress_notification(idx))

    def _create_stress_notification(self, index):
        """Create a stress test notification"""
        types = [AlertType.INFO, AlertType.SUCCESS,
                 AlertType.WARNING, AlertType.ERROR]
        notif_type = types[index % len(types)]

        notification = EnhancedFluentNotification(
            title=f"Test Notification {index + 1}",
            message=f"This is stress test notification number {index + 1}",
            notification_type=notif_type,
            timeout=2000
        )
        self.notification_manager.show_notification(notification)
        self.total_notifications_shown += 1

    def _clear_all_notifications(self):
        """Clear all active notifications"""
        for notification in self.notification_manager.notifications[:]:
            notification.close_with_animation()
        self._log_event("Cleared all notifications")

    def _update_stats(self):
        """Update notification statistics"""
        active_count = len(self.notification_manager.notifications)
        self.active_notifications_label.setText(str(active_count))
        self.total_shown_label.setText(str(self.total_notifications_shown))

    # Event handlers for message bars
    def _create_message_bar(self):
        """Create a message bar based on current settings"""
        msgbar_types = {
            "Info": AlertType.INFO,
            "Success": AlertType.SUCCESS,
            "Warning": AlertType.WARNING,
            "Error": AlertType.ERROR
        }

        msgbar_type = msgbar_types[self.msgbar_type_combo.currentText()]
        message = self.msgbar_message_input.text()
        closable = self.msgbar_closable_check.isChecked()
        action_text = self.msgbar_action_text.text(
        ) if self.msgbar_action_check.isChecked() else ""

        msgbar = EnhancedFluentNotification(
            message=message,
            notification_type=msgbar_type,
            closable=closable,
            action_text=action_text
        )

        # Connect events
        msgbar.closed.connect(lambda: self._remove_message_bar(msgbar))
        if action_text:
            msgbar.clicked.connect(
                lambda: self._log_event("Message bar action clicked"))

        self.msgbar_display_area.addWidget(msgbar)
        self.message_bars.append(msgbar)
        self._log_event(f"Created message bar: {message}")

    def _create_predefined_message_bar(self, msg_type, message):
        """Create a predefined message bar"""
        msgbar = EnhancedFluentNotification(
            message=message,
            notification_type=msg_type,
            closable=True,
            action_text="Action" if msg_type in [
                AlertType.ERROR, AlertType.WARNING] else ""
        )

        msgbar.closed.connect(lambda: self._remove_message_bar(msgbar))
        if msgbar._action_text:
            msgbar.clicked.connect(
                lambda: self._log_event("Message bar action clicked"))

        self.msgbar_display_area.addWidget(msgbar)
        self.message_bars.append(msgbar)
        self._log_event(f"Created predefined message bar: {message}")

    def _remove_message_bar(self, msgbar):
        """Remove message bar from tracking"""
        if msgbar in self.message_bars:
            self.message_bars.remove(msgbar)
        self._log_event("Message bar removed")

    def _clear_all_message_bars(self):
        """Clear all message bars"""
        for msgbar in self.message_bars[:]:
            msgbar.hide()
            msgbar.setParent(None)
        self.message_bars.clear()
        self._log_event("Cleared all message bars")

    # Advanced features handlers
    def _demo_theme_changes(self):
        """Demonstrate theme changes"""
        # Create alerts in both themes
        alert1 = EnhancedFluentAlert(
            "Theme Test", "This alert will change with the theme", AlertType.INFO)
        self.alert_display_area.addWidget(alert1)

        # Toggle theme after a delay
        QTimer.singleShot(2000, lambda: self._toggle_theme_demo())

    def _toggle_theme_demo(self):
        """Toggle theme for demonstration"""
        # This would toggle the theme if theme manager supports it
        self._log_event("Theme toggled for demonstration")

    def _test_animation_speed(self):
        """Test custom animation speed"""
        speed = self.animation_speed_slider.value()

        # Create alert with custom timing (this would need to be implemented in the alert class)
        alert = EnhancedFluentAlert(
            "Animation Test",
            f"This alert uses {speed}ms animation timing",
            AlertType.INFO,
            timeout=3000
        )
        self.alert_display_area.addWidget(alert)
        self._log_event(f"Tested animation speed: {speed}ms")

    def _create_event_alert(self):
        """Create alert with comprehensive event logging"""
        alert = EnhancedFluentAlert(
            "Event Test Alert",
            "This alert logs all events for demonstration",
            AlertType.INFO,
            action_text="Test Action"
        )

        # Connect all possible events
        alert.closed.connect(lambda: self._log_event("EVENT: Alert closed"))
        alert.action_clicked.connect(
            lambda: self._log_event("EVENT: Action button clicked"))

        self.alert_display_area.addWidget(alert)
        self._log_event("EVENT: Alert created with event logging")

    def _run_performance_test(self):
        """Run performance test"""
        import time

        start_time = time.time()

        # Create multiple alerts quickly
        for i in range(5):
            alert = EnhancedFluentAlert(
                f"Performance Test {i+1}", "Testing rendering performance", AlertType.INFO)
            self.alert_display_area.addWidget(alert)

        end_time = time.time()
        render_time = (end_time - start_time) * 1000

        self.render_time_label.setText(f"{render_time:.2f}ms")
        self.memory_usage_label.setText(
            f"{len(self.message_bars) * 50} KB")  # Estimated

        self._log_event(f"Performance test completed: {render_time:.2f}ms")

    # Interactive demo handlers
    def _demo_app_update(self):
        """Demo app update scenario"""
        self.demo_status_label.setText("Demo: App Update Scenario")

        # Show update notification
        notification = EnhancedFluentNotification(
            "Update Available",
            "A new version of the app is available",
            AlertType.INFO,
            timeout=0,
            clickable=True
        )
        notification.clicked.connect(lambda: self._continue_update_demo())
        self.notification_manager.show_notification(notification)

        self._log_event("Started app update demo")

    def _continue_update_demo(self):
        """Continue update demo"""
        # Show download progress
        msgbar = EnhancedFluentNotification(
            "Downloading update... 45%",
            notification_type=AlertType.INFO,
            closable=False
        )
        self.msgbar_display_area.addWidget(msgbar)

        # Complete after delay
        QTimer.singleShot(3000, lambda: self._complete_update_demo(msgbar))

    def _complete_update_demo(self, msgbar):
        """Complete update demo"""
        msgbar.setMessage("Update downloaded successfully!")
        msgbar.setMessageType(AlertType.SUCCESS)

        QTimer.singleShot(2000, lambda: msgbar.hide())
        self._log_event("Completed app update demo")

    def _demo_form_validation(self):
        """Demo form validation scenario"""
        self.demo_status_label.setText("Demo: Form Validation")

        # Show validation errors
        errors = [
            "Email field is required",
            "Password must be at least 8 characters",
            "Please accept terms and conditions"
        ]

        for i, error in enumerate(errors):
            QTimer.singleShot(
                i * 1000, lambda e=error: self._show_validation_error(e))

    def _show_validation_error(self, error):
        """Show validation error"""
        alert = EnhancedFluentAlert("Validation Error", error,
                            AlertType.ERROR, timeout=3000)
        self.alert_display_area.addWidget(alert)

    def _demo_file_operations(self):
        """Demo file operations scenario"""
        self.demo_status_label.setText("Demo: File Operations")

        operations = [
            ("File upload started", AlertType.INFO),
            ("Upload 50% complete", AlertType.INFO),
            ("Upload completed successfully", AlertType.SUCCESS),
            ("File saved to cloud", AlertType.SUCCESS)
        ]

        for i, (message, msg_type) in enumerate(operations):
            QTimer.singleShot(i * 1500, lambda m=message,
                              t=msg_type: self._show_file_operation(m, t))

    def _show_file_operation(self, message, msg_type):
        """Show file operation notification"""
        notification = EnhancedFluentNotification(
            "File Operation",
            message,
            msg_type,
            timeout=2000
        )
        self.notification_manager.show_notification(notification)

    def _demo_network_status(self):
        """Demo network status changes"""
        self.demo_status_label.setText("Demo: Network Status")

        # Simulate network issues
        msgbar1 = EnhancedFluentNotification(
            title="Connection lost",
            message="Network connection interrupted",
            notification_type=AlertType.ERROR,
            action_text="Retry")
        self.msgbar_display_area.addWidget(msgbar1)

        QTimer.singleShot(3000, lambda: self._restore_connection(msgbar1))

    def _restore_connection(self, msgbar):
        """Restore connection demo"""
        msgbar.setMessage("Connection restored")
        msgbar.setMessageType(AlertType.SUCCESS)
        QTimer.singleShot(2000, lambda: msgbar.hide())

    def _demo_user_onboarding(self):
        """Demo user onboarding flow"""
        self.demo_status_label.setText("Demo: User Onboarding")

        steps = [
            "Welcome to the application!",
            "Let's set up your profile",
            "Choose your preferences",
            "Setup complete!"
        ]

        for i, step in enumerate(steps):
            QTimer.singleShot(
                i * 2000, lambda s=step: self._show_onboarding_step(s))

    def _show_onboarding_step(self, step):
        """Show onboarding step"""
        notification = EnhancedFluentNotification(
            "Onboarding",
            step,
            AlertType.INFO,
            timeout=1800
        )
        self.notification_manager.show_notification(notification)

    def _demo_error_recovery(self):
        """Demo error recovery scenario"""
        self.demo_status_label.setText("Demo: Error Recovery")

        # Show error
        error_alert = EnhancedFluentAlert(
            "Operation Failed",
            "The operation could not be completed due to a network error.",
            AlertType.ERROR,
            action_text="Retry"
        )
        error_alert.action_clicked.connect(lambda: self._retry_operation())
        self.alert_display_area.addWidget(error_alert)

    def _retry_operation(self):
        """Retry operation demo"""
        # Show retry in progress
        msgbar = EnhancedFluentNotification(
            title="Operation in progress",
            message="Retrying operation...",
            notification_type=AlertType.INFO
        )
        self.msgbar_display_area.addWidget(msgbar)

        # Show success
        QTimer.singleShot(2000, lambda: self._show_retry_success(msgbar))

    def _show_retry_success(self, msgbar):
        """Show retry success"""
        msgbar.setMessage("Operation completed successfully!")
        msgbar.setMessageType(AlertType.SUCCESS)
        QTimer.singleShot(2000, lambda: msgbar.hide())

    def _toggle_auto_demo(self, enabled):
        """Toggle auto demo mode"""
        if enabled:
            interval = self.demo_interval_spin.value() * 1000
            self.auto_demo_timer.start(interval)
            self.demo_status_label.setText("Auto Demo: Active")
        else:
            self.auto_demo_timer.stop()
            self.demo_status_label.setText("Auto Demo: Inactive")

    def _run_auto_demo(self):
        """Run automated demo"""
        demos = [
            self._demo_app_update,
            self._demo_form_validation,
            self._demo_file_operations,
            self._demo_network_status
        ]

        import random
        demo = random.choice(demos)
        demo()

    def _log_event(self, event):
        """Log event to event log"""
        if hasattr(self, 'event_log'):
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.event_log.append(f"[{timestamp}] {event}")


class AlertExampleWindow(QMainWindow):
    """Main window for alert examples"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FluentAlert Components - Complete Demo")
        self.setGeometry(100, 100, 1400, 900)

        # Create central widget
        central_widget = AlertDemoWidget()
        self.setCentralWidget(central_widget)

        # Apply theme
        # theme_manager.apply_theme_to_widget(self)

        # Status bar
        self.statusBar().showMessage("Ready - Explore all alert and notification features")


def main():
    """Run the alert example application"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("FluentAlert Demo")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Fluent Widget Examples")

    # Create and show window
    window = AlertExampleWindow()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
