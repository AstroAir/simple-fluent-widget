"""
Fluent Timeline Components Demo
Comprehensive example showcasing all timeline components and features
"""

import sys  # Used by QApplication and sys.exit
import random  # Used by dynamic item generation
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QGroupBox,
    QScrollArea, QLineEdit, QSpinBox, QCheckBox, QTextEdit,
    QTabWidget, QFormLayout,  # QSplitter, QFrame, # Removed QSplitter, QFrame
    QSlider,  # QProgressBar, QListWidget, QListWidgetItem, # Removed these
    QDateTimeEdit
)
# QTimer is used for auto_progress
from PySide6.QtCore import Qt, QTimer, QDateTime
# QPixmap, QPainter, # Removed QPixmap, QPainter
from PySide6.QtGui import QFont, QColor

# Import the timeline components
from components.basic.timeline import FluentTimeline, FluentTimelineItem
from core.theme import theme_manager, ThemeMode


class TimelineDemo(QMainWindow):
    """Main demo window showcasing all timeline components"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Timeline Components Demo")
        self.setGeometry(100, 100, 1400, 1000)

        # Store demo data
        self.demo_timelines = []
        self.sample_events = []
        self.auto_timer = None  # For auto-progress simulation

        # Central widget with scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        # Main layout
        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Fluent Timeline Components Demo")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Theme toggle
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        if theme_manager.get_theme_mode() == ThemeMode.DARK:
            self.theme_combo.setCurrentText("Dark")
        else:
            self.theme_combo.setCurrentText("Light")
        self.theme_combo.currentTextChanged.connect(self._toggle_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        main_layout.addLayout(theme_layout)

        # Create demo sections using tabs
        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_basic_timeline_demo(), "Basic Timeline")
        tab_widget.addTab(self._create_status_demo(), "Status Types")
        tab_widget.addTab(self._create_interactive_demo(),
                          "Interactive Timeline")
        tab_widget.addTab(self._create_real_world_demo(),
                          "Real-World Examples")
        tab_widget.addTab(self._create_dynamic_demo(), "Dynamic Operations")
        tab_widget.addTab(self._create_customization_demo(), "Customization")
        tab_widget.addTab(self._create_performance_demo(), "Performance Test")

        main_layout.addWidget(tab_widget)
        main_layout.addStretch()

        # Setup event logging
        self._setup_event_log(main_layout)

        # Initialize sample data
        self._initialize_sample_data()

    def _log_event_safe_item_access(self, timeline: FluentTimeline, index: int, timeline_name: str):
        """Safely access item and log click event."""
        item = timeline.item(index)
        if item:
            self._log_event(
                timeline_name, f"Clicked item {index}: '{item.title()}'")
        else:
            self._log_event(
                timeline_name, f"Clicked item {index}: (Item not found or invalid)")

    def _create_basic_timeline_demo(self) -> QWidget:
        """Create basic timeline demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Simple timeline
        simple_group = QGroupBox("Simple Timeline")
        simple_layout = QVBoxLayout(simple_group)

        self.basic_timeline = FluentTimeline()
        self.basic_timeline.setObjectName("BasicTimeline")
        self.basic_timeline.setFixedHeight(300)

        now = datetime.now()
        basic_items_data = [
            ("Project Started", "Initial project setup and planning",
             now - timedelta(days=30), FluentTimelineItem.Status.COMPLETED),
            ("Design Phase", "UI/UX design and wireframing", now -
             timedelta(days=20), FluentTimelineItem.Status.COMPLETED),
            ("Development", "Core functionality implementation", now -
             timedelta(days=10), FluentTimelineItem.Status.CURRENT),
            ("Testing", "Quality assurance and bug fixes", now -
             timedelta(days=5), FluentTimelineItem.Status.PENDING),
            ("Deployment", "Production release", now +
             timedelta(days=5), FluentTimelineItem.Status.PENDING)
        ]

        for title, desc, timestamp, status in basic_items_data:
            self.basic_timeline.addItem(title, desc, timestamp, status)

        self.basic_timeline.item_clicked.connect(
            lambda index: self._log_event_safe_item_access(
                self.basic_timeline, index, "Basic Timeline")
        )

        simple_layout.addWidget(self.basic_timeline)
        layout.addWidget(simple_group)

        # Timeline with timestamps
        timestamp_group = QGroupBox("Timeline with Various Timestamps")
        timestamp_layout = QVBoxLayout(timestamp_group)

        self.timestamp_timeline = FluentTimeline()
        self.timestamp_timeline.setObjectName("TimestampTimeline")
        self.timestamp_timeline.setFixedHeight(250)

        timestamp_items_data = [
            ("Just now", "Recent activity", now,
             FluentTimelineItem.Status.CURRENT),
            ("5 minutes ago", "Quick update", now -
             timedelta(minutes=5), FluentTimelineItem.Status.COMPLETED),
            ("1 hour ago", "Major milestone", now -
             timedelta(hours=1), FluentTimelineItem.Status.COMPLETED),
            ("Yesterday", "Daily standup", now - timedelta(days=1),
             FluentTimelineItem.Status.COMPLETED),
            ("Last week", "Sprint planning", now -
             timedelta(days=7), FluentTimelineItem.Status.COMPLETED)
        ]

        for title, desc, timestamp, status in timestamp_items_data:
            self.timestamp_timeline.addItem(title, desc, timestamp, status)

        timestamp_layout.addWidget(self.timestamp_timeline)
        layout.addWidget(timestamp_group)

        # Basic controls
        basic_controls_group = QGroupBox("Basic Controls")
        basic_controls_layout = QVBoxLayout(basic_controls_group)

        controls_row1 = QHBoxLayout()
        scroll_top_btn = QPushButton("Scroll to Top")
        scroll_top_btn.clicked.connect(self.basic_timeline.scrollToTop)
        scroll_bottom_btn = QPushButton("Scroll to Bottom")
        scroll_bottom_btn.clicked.connect(self.basic_timeline.scrollToBottom)
        reverse_order_cb = QCheckBox("Reverse Order")
        reverse_order_cb.toggled.connect(self.basic_timeline.setReverseOrder)
        controls_row1.addWidget(scroll_top_btn)
        controls_row1.addWidget(scroll_bottom_btn)
        controls_row1.addWidget(reverse_order_cb)
        controls_row1.addStretch()
        basic_controls_layout.addLayout(controls_row1)

        controls_row2 = QHBoxLayout()
        scroll_to_item_btn = QPushButton("Scroll to Item")
        self.scroll_item_index = QSpinBox()
        if self.basic_timeline.itemCount() > 0:
            self.scroll_item_index.setRange(
                0, self.basic_timeline.itemCount() - 1)
        else:
            self.scroll_item_index.setRange(0, 0)
            self.scroll_item_index.setEnabled(False)
        self.scroll_item_index.setValue(min(2, self.basic_timeline.itemCount(
        ) - 1 if self.basic_timeline.itemCount() > 0 else 0))

        scroll_to_item_btn.clicked.connect(
            lambda: self.basic_timeline.scrollToItem(
                self.scroll_item_index.value()) if self.basic_timeline.itemCount() > 0 else None
        )
        controls_row2.addWidget(QLabel("Scroll to item:"))
        controls_row2.addWidget(self.scroll_item_index)
        controls_row2.addWidget(scroll_to_item_btn)
        controls_row2.addStretch()
        basic_controls_layout.addLayout(controls_row2)
        layout.addWidget(basic_controls_group)

        return widget

    def _create_status_demo(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        status_group = QGroupBox("All Status Types")
        status_layout = QVBoxLayout(status_group)
        self.status_timeline = FluentTimeline()
        self.status_timeline.setObjectName("StatusTimeline")
        self.status_timeline.setFixedHeight(400)
        status_items_data = [
            ("Pending Task", "This task is waiting to be started",
             FluentTimelineItem.Status.PENDING),
            ("Current Task", "This task is currently in progress",
             FluentTimelineItem.Status.CURRENT),
            ("Completed Task", "This task has been finished successfully",
             FluentTimelineItem.Status.COMPLETED),
            ("Error Task", "This task encountered an error",
             FluentTimelineItem.Status.ERROR),
            ("Warning Task", "This task has a warning condition",
             FluentTimelineItem.Status.WARNING),
        ]
        now = datetime.now()
        for i, (title, desc, status_val) in enumerate(status_items_data):
            timestamp = now - timedelta(hours=i)
            self.status_timeline.addItem(title, desc, timestamp, status_val)
        status_layout.addWidget(self.status_timeline)
        layout.addWidget(status_group)

        status_controls_group = QGroupBox("Interactive Status Controls")
        status_controls_layout = QVBoxLayout(status_controls_group)
        change_controls_layout = QHBoxLayout()
        change_controls_layout.addWidget(QLabel("Item:"))
        self.status_item_selector = QComboBox()
        for i in range(self.status_timeline.itemCount()):
            item = self.status_timeline.item(i)
            if item:
                self.status_item_selector.addItem(f"{i}: {item.title()}")
        change_controls_layout.addWidget(self.status_item_selector)
        change_controls_layout.addWidget(QLabel("New Status:"))
        self.new_status_selector = QComboBox()
        self.new_status_selector.addItems(
            [s.name for s in FluentTimelineItem.Status])
        change_controls_layout.addWidget(self.new_status_selector)
        change_status_btn = QPushButton("Change Status")
        change_status_btn.clicked.connect(self._change_item_status)
        change_controls_layout.addWidget(change_status_btn)
        change_controls_layout.addStretch()
        status_controls_layout.addLayout(change_controls_layout)

        bulk_controls_layout = QHBoxLayout()
        set_all_pending_btn = QPushButton("Set All Pending")
        set_all_pending_btn.clicked.connect(
            lambda: self._set_all_status(FluentTimelineItem.Status.PENDING))
        set_all_completed_btn = QPushButton("Set All Completed")
        set_all_completed_btn.clicked.connect(
            lambda: self._set_all_status(FluentTimelineItem.Status.COMPLETED))
        simulate_progress_btn = QPushButton("Simulate Progress")
        simulate_progress_btn.clicked.connect(self._simulate_progress)
        bulk_controls_layout.addWidget(set_all_pending_btn)
        bulk_controls_layout.addWidget(set_all_completed_btn)
        bulk_controls_layout.addWidget(simulate_progress_btn)
        bulk_controls_layout.addStretch()
        status_controls_layout.addLayout(bulk_controls_layout)
        layout.addWidget(status_controls_group)

        legend_group = QGroupBox("Status Legend")
        legend_layout = QGridLayout(legend_group)
        statuses_legend = [
            ("PENDING", "Task waiting to start", QColor(128, 128, 128)),
            ("CURRENT", "Task in progress", theme_manager.get_color('primary')),
            ("COMPLETED", "Task finished successfully",
             theme_manager.get_color('success')),
            ("ERROR", "Task failed", theme_manager.get_color('error')),
            ("WARNING", "Task has issues", theme_manager.get_color('warning'))
        ]
        for i, (status_name, description, color) in enumerate(statuses_legend):
            color_label = QLabel()
            color_label.setFixedSize(16, 16)
            color_label.setStyleSheet(
                f"background-color: {color.name()}; border-radius: 8px; border: 1px solid {color.darker(120).name()};")
            legend_layout.addWidget(color_label, i, 0)
            legend_layout.addWidget(
                QLabel(f"<b>{status_name.capitalize()}</b>"), i, 1)
            legend_layout.addWidget(QLabel(description), i, 2)
        layout.addWidget(legend_group)
        return widget

    def _create_interactive_demo(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        interactive_group = QGroupBox("Interactive Timeline Builder")
        interactive_layout = QVBoxLayout(interactive_group)
        self.interactive_timeline = FluentTimeline()
        self.interactive_timeline.setObjectName("InteractiveTimeline")
        self.interactive_timeline.setFixedHeight(350)
        self.interactive_timeline.item_clicked.connect(
            self._on_interactive_item_clicked)
        interactive_layout.addWidget(self.interactive_timeline)
        layout.addWidget(interactive_group)

        creation_group = QGroupBox("Create New Timeline Item")
        creation_form_layout = QFormLayout(
            creation_group)  # Renamed to avoid conflict
        self.new_item_title_edit = QLineEdit("New Item")  # Renamed
        creation_form_layout.addRow("Title:", self.new_item_title_edit)
        self.new_item_description_edit = QTextEdit(
            "Item description")  # Renamed
        self.new_item_description_edit.setMaximumHeight(80)
        creation_form_layout.addRow(
            "Description:", self.new_item_description_edit)
        self.new_item_timestamp_edit = QDateTimeEdit(
            QDateTime.currentDateTime())  # Renamed
        creation_form_layout.addRow("Timestamp:", self.new_item_timestamp_edit)
        self.new_item_status_combo = QComboBox()  # Renamed
        self.new_item_status_combo.addItems(
            [s.name for s in FluentTimelineItem.Status])
        creation_form_layout.addRow("Status:", self.new_item_status_combo)

        creation_buttons_layout = QHBoxLayout()
        add_item_btn = QPushButton("Add Item")
        add_item_btn.clicked.connect(self._add_interactive_item)
        insert_item_btn = QPushButton("Insert at Position")
        self.insert_position_spinbox = QSpinBox()  # Renamed
        self.insert_position_spinbox.setRange(0, 0)
        insert_item_btn.clicked.connect(self._insert_interactive_item)
        creation_buttons_layout.addWidget(add_item_btn)
        creation_buttons_layout.addWidget(QLabel("Insert at:"))
        creation_buttons_layout.addWidget(self.insert_position_spinbox)
        creation_buttons_layout.addWidget(insert_item_btn)
        creation_buttons_layout.addStretch()
        creation_form_layout.addRow(creation_buttons_layout)
        layout.addWidget(creation_group)

        operations_group = QGroupBox("Timeline Operations")
        operations_layout = QVBoxLayout(operations_group)
        item_mgmt_layout = QHBoxLayout()
        self.selected_item_index_spinbox = QSpinBox()  # Renamed
        self.selected_item_index_spinbox.setRange(0, 0)
        self.selected_item_index_spinbox.valueChanged.connect(
            self._update_selected_item_info)
        self.remove_item_btn = QPushButton(
            "Remove Selected")  # Made an attribute
        self.remove_item_btn.clicked.connect(self._remove_selected_item)
        clear_all_btn = QPushButton("Clear All")
        clear_all_btn.clicked.connect(self._clear_interactive_timeline)
        item_mgmt_layout.addWidget(QLabel("Selected Item:"))
        item_mgmt_layout.addWidget(self.selected_item_index_spinbox)
        item_mgmt_layout.addWidget(self.remove_item_btn)
        item_mgmt_layout.addWidget(clear_all_btn)
        item_mgmt_layout.addStretch()
        operations_layout.addLayout(item_mgmt_layout)

        self.selected_item_info_label = QLabel("No items")  # Renamed
        self.selected_item_info_label.setWordWrap(True)
        self.selected_item_info_label.setStyleSheet(
            "background-color: #f0f0f0; padding: 8px; border-radius: 4px;")
        operations_layout.addWidget(QLabel("Selected Item Info:"))
        operations_layout.addWidget(self.selected_item_info_label)
        layout.addWidget(operations_group)

        clickable_group = QGroupBox("Clickable Items Demo")
        clickable_layout = QVBoxLayout(clickable_group)
        clickable_info = QLabel(
            "Click on timeline items to interact. Clickable items have a pointer cursor.")
        clickable_layout.addWidget(clickable_info)
        enable_clickable_cb = QCheckBox("Enable Item Clicking")
        enable_clickable_cb.setChecked(True)  # Default to clickable
        enable_clickable_cb.toggled.connect(self._toggle_item_clicking)
        clickable_layout.addWidget(enable_clickable_cb)
        layout.addWidget(clickable_group)

        self._update_interactive_controls_ranges()  # Initial update
        return widget

    def _create_real_world_demo(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        now = datetime.now()

        dev_group = QGroupBox("Software Development Timeline")
        dev_layout = QVBoxLayout(dev_group)
        self.dev_timeline = FluentTimeline()
        self.dev_timeline.setObjectName("DevTimeline")
        self.dev_timeline.setFixedHeight(300)
        dev_milestones = [
            ("Req. Gathering", "Analyzed client needs", now -
             timedelta(days=60), FluentTimelineItem.Status.COMPLETED),
            ("System Design", "Created architecture", now -
             timedelta(days=45), FluentTimelineItem.Status.COMPLETED),
            ("Frontend Dev", "Implemented UI", now -
             timedelta(days=30), FluentTimelineItem.Status.COMPLETED),
            ("Backend Dev", "Built API", now - timedelta(days=15),
             FluentTimelineItem.Status.COMPLETED),
            ("Integration Test", "Testing interactions", now -
             timedelta(days=7), FluentTimelineItem.Status.CURRENT),
            ("UAT", "Client testing", now - timedelta(days=3),
             FluentTimelineItem.Status.PENDING),
            ("Deployment", "Production release", now +
             timedelta(days=5), FluentTimelineItem.Status.PENDING),
        ]
        for title, desc, timestamp, status in dev_milestones:
            self.dev_timeline.addItem(title, desc, timestamp, status)
        dev_layout.addWidget(self.dev_timeline)
        layout.addWidget(dev_group)

        order_group = QGroupBox("Order Processing Timeline")
        order_layout = QVBoxLayout(order_group)
        self.order_timeline = FluentTimeline()
        self.order_timeline.setObjectName("OrderTimeline")
        self.order_timeline.setFixedHeight(250)
        order_steps = [
            ("Order Placed", "Cust. submitted order", now -
             timedelta(hours=2), FluentTimelineItem.Status.COMPLETED),
            ("Payment Verified", "Payment confirmed", now -
             timedelta(hours=1, minutes=45), FluentTimelineItem.Status.COMPLETED),
            ("Inventory Check", "Items confirmed", now - timedelta(hours=1,
             minutes=30), FluentTimelineItem.Status.COMPLETED),
            ("Picking & Packing", "Preparing shipment", now -
             timedelta(minutes=30), FluentTimelineItem.Status.CURRENT),
            ("Shipment", "Package to carrier", now +
             timedelta(hours=2), FluentTimelineItem.Status.PENDING),
            ("Delivery", "Package delivered", now +
             timedelta(days=2), FluentTimelineItem.Status.PENDING)
        ]
        for title, desc, timestamp, status in order_steps:
            self.order_timeline.addItem(title, desc, timestamp, status)
        order_layout.addWidget(self.order_timeline)
        layout.addWidget(order_group)

        # Controls for real-world timelines
        realworld_controls_group = QGroupBox("Real-World Timeline Controls")
        realworld_controls_layout = QVBoxLayout(realworld_controls_group)
        scenario_controls_layout = QHBoxLayout()
        dev_progress_btn = QPushButton("Advance Dev Timeline")
        dev_progress_btn.clicked.connect(
            lambda: self._advance_timeline_progress(self.dev_timeline))
        order_progress_btn = QPushButton("Advance Order Timeline")
        order_progress_btn.clicked.connect(
            lambda: self._advance_timeline_progress(self.order_timeline))
        # project_progress_btn = QPushButton("Advance Project Timeline") # Assuming project_timeline is also defined
        # project_progress_btn.clicked.connect(lambda: self._advance_timeline_progress(self.project_timeline))
        scenario_controls_layout.addWidget(dev_progress_btn)
        scenario_controls_layout.addWidget(order_progress_btn)
        # scenario_controls_layout.addWidget(project_progress_btn)
        scenario_controls_layout.addStretch()
        realworld_controls_layout.addLayout(scenario_controls_layout)

        simulation_layout = QHBoxLayout()
        self.auto_progress_cb = QCheckBox("Auto Progress Simulation")
        self.auto_progress_cb.toggled.connect(self._toggle_auto_progress)
        self.progress_speed_slider = QSlider(
            Qt.Orientation.Horizontal)  # Renamed
        self.progress_speed_slider.setRange(1, 10)  # 1=slow, 10=fast
        self.progress_speed_slider.setValue(3)
        self.progress_speed_slider.setToolTip(
            "Progress speed (1=slow, 10=fast)")
        simulation_layout.addWidget(self.auto_progress_cb)
        simulation_layout.addWidget(QLabel("Speed:"))
        simulation_layout.addWidget(self.progress_speed_slider)
        simulation_layout.addStretch()
        realworld_controls_layout.addLayout(simulation_layout)
        layout.addWidget(realworld_controls_group)

        # self.project_timeline would be defined here if used above
        # For now, it's omitted to match the provided snippet's direct usage

        return widget

    def _create_dynamic_demo(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        dynamic_group = QGroupBox("Dynamic Timeline Operations")
        dynamic_layout = QVBoxLayout(dynamic_group)
        self.dynamic_timeline = FluentTimeline()
        self.dynamic_timeline.setObjectName("DynamicTimeline")
        self.dynamic_timeline.setFixedHeight(350)
        dynamic_layout.addWidget(self.dynamic_timeline)
        layout.addWidget(dynamic_group)

        # This group contains all controls
        operations_group = QGroupBox("Dynamic Operations")
        operations_main_layout = QVBoxLayout(
            operations_group)  # Main layout for this group

        add_operations_layout = QHBoxLayout()
        add_random_btn = QPushButton("Add Random Item")
        add_random_btn.clicked.connect(self._add_random_item)
        add_multiple_btn = QPushButton("Add Multiple Items")
        self.multiple_count_spinbox = QSpinBox()  # Renamed
        self.multiple_count_spinbox.setRange(1, 20)
        self.multiple_count_spinbox.setValue(5)
        add_multiple_btn.clicked.connect(self._add_multiple_items)
        add_operations_layout.addWidget(add_random_btn)
        add_operations_layout.addWidget(add_multiple_btn)
        add_operations_layout.addWidget(QLabel("Count:"))
        add_operations_layout.addWidget(self.multiple_count_spinbox)
        add_operations_layout.addStretch()
        operations_main_layout.addLayout(add_operations_layout)

        remove_operations_layout = QHBoxLayout()
        remove_random_btn = QPushButton("Remove Random Item")
        remove_random_btn.clicked.connect(self._remove_random_item)
        remove_first_btn = QPushButton("Remove First")
        remove_first_btn.clicked.connect(lambda: self._remove_item_at_index(0))
        remove_last_btn = QPushButton("Remove Last")
        remove_last_btn.clicked.connect(self._remove_last_item)
        clear_dynamic_btn = QPushButton("Clear All")
        clear_dynamic_btn.clicked.connect(
            self.dynamic_timeline.clear)  # Direct clear
        remove_operations_layout.addWidget(remove_random_btn)
        remove_operations_layout.addWidget(remove_first_btn)
        remove_operations_layout.addWidget(remove_last_btn)
        remove_operations_layout.addWidget(clear_dynamic_btn)
        remove_operations_layout.addStretch()
        operations_main_layout.addLayout(remove_operations_layout)

        batch_operations_layout = QHBoxLayout()
        shuffle_btn = QPushButton("Shuffle Items")
        shuffle_btn.clicked.connect(self._shuffle_timeline_items)
        reverse_timeline_btn = QPushButton(
            "Toggle Reverse Order")  # Changed label for clarity
        reverse_timeline_btn.clicked.connect(lambda: self.dynamic_timeline.setReverseOrder(
            not self.dynamic_timeline.reverseOrder()))
        batch_operations_layout.addWidget(shuffle_btn)
        batch_operations_layout.addWidget(reverse_timeline_btn)
        batch_operations_layout.addStretch()
        operations_main_layout.addLayout(batch_operations_layout)

        # Add the group with all controls to the main tab layout
        layout.addWidget(operations_group)
        return widget

    # --- Implementation of missing methods ---
    def _toggle_theme(self, theme_name: str):
        if theme_name == "Dark":
            theme_manager.set_theme_mode(ThemeMode.DARK)
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)
        self._log_event("Theme", f"Switched to {theme_name} mode")
        # Force update of legend colors if theme changes
        if hasattr(self, 'status_timeline'):  # Rebuild or update legend in status_demo
            # This is a bit complex, ideally the legend would auto-update or be part of theme_changed signal
            # For simplicity, we might need to reconstruct the legend or update its style sheets.
            # Or, the FluentTimelineItem itself should handle its color based on theme.
            self.status_timeline.update()  # Trigger a repaint, hoping items update their colors

    def _create_customization_demo(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Customization Demo - To be implemented"))
        self._log_event("Demo Setup", "Customization demo tab created (stub).")
        return widget

    def _create_performance_demo(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Performance Test Demo - To be implemented"))
        self._log_event(
            "Demo Setup", "Performance test demo tab created (stub).")
        return widget

    def _setup_event_log(self, parent_layout: QVBoxLayout):
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout(log_group)
        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setPlaceholderText(
            "Timeline events will be logged here...")
        self.event_log.setMaximumHeight(100)  # Adjusted height
        log_layout.addWidget(self.event_log)

        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.event_log.clear)
        log_controls_layout = QHBoxLayout()
        log_controls_layout.addWidget(clear_log_btn)
        log_controls_layout.addStretch()
        log_layout.addLayout(log_controls_layout)

        parent_layout.addWidget(log_group)
        # self._log_event("System", "Event log initialized.") # Log after event_log is assigned

    def _initialize_sample_data(self):
        self.sample_events = [
            ("Initial Commit", "Project repository created.", datetime.now() -
             timedelta(days=7), FluentTimelineItem.Status.COMPLETED),
            ("Alpha Release", "First internal testing version.", datetime.now(
            ) - timedelta(days=3), FluentTimelineItem.Status.CURRENT),
            ("Beta Release", "Public testing phase.", datetime.now() +
             timedelta(days=5), FluentTimelineItem.Status.PENDING),
        ]
        # Example: Populate basic_timeline if it exists and is empty
        if hasattr(self, 'basic_timeline') and self.basic_timeline.itemCount() == 0:
            for title, desc, ts, status in self.sample_events:
                self.basic_timeline.addItem(title, desc, ts, status)
        self._log_event("Data", "Sample data initialized.")

    def _log_event(self, event_type: str, details: str):
        if hasattr(self, 'event_log') and self.event_log is not None:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.event_log.append(f"[{timestamp}] {event_type}: {details}")
            self.event_log.verticalScrollBar().setValue(
                self.event_log.verticalScrollBar().maximum())
        else:
            print(
                f"LOG: [{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {event_type}: {details}")

    def _change_item_status(self):
        if not (hasattr(self, 'status_timeline') and hasattr(self, 'status_item_selector') and hasattr(self, 'new_status_selector')):
            self._log_event("Status Change",
                            "Required widgets not initialized.")
            return

        selected_item_text = self.status_item_selector.currentText()
        if not selected_item_text:
            self._log_event("Status Change", "No item selected.")
            return

        try:
            item_index = int(selected_item_text.split(":")[0])
        except (ValueError, IndexError):
            self._log_event("Status Change",
                            f"Invalid item format: {selected_item_text}")
            return

        new_status_name = self.new_status_selector.currentText()
        try:
            new_status = FluentTimelineItem.Status[new_status_name.upper()]
        except KeyError:
            self._log_event("Status Change",
                            f"Invalid status name: {new_status_name}")
            return

        item = self.status_timeline.item(item_index)
        if item:
            item.setStatus(new_status)
            self._log_event(
                "Status Change", f"Item {item_index} ('{item.title()}') status changed to {new_status_name}")
        else:
            self._log_event("Status Change",
                            f"Item at index {item_index} not found.")

    def _set_all_status(self, status: FluentTimelineItem.Status):
        if not hasattr(self, 'status_timeline'):
            return
        for i in range(self.status_timeline.itemCount()):
            item = self.status_timeline.item(i)
            if item:
                item.setStatus(status)
        self._log_event(
            "Bulk Status", f"All items in StatusTimeline set to {status.name}")

    def _simulate_progress(self):
        if not hasattr(self, 'status_timeline'):
            return

        current_idx = -1
        for i in range(self.status_timeline.itemCount()):
            item = self.status_timeline.item(i)
            if item and item.status() == FluentTimelineItem.Status.CURRENT:
                item.setStatus(FluentTimelineItem.Status.COMPLETED)
                current_idx = i
                break

        next_idx = current_idx + 1
        if 0 <= next_idx < self.status_timeline.itemCount():
            item = self.status_timeline.item(next_idx)
            if item and item.status() == FluentTimelineItem.Status.PENDING:  # Only advance pending tasks
                item.setStatus(FluentTimelineItem.Status.CURRENT)
                self._log_event("Simulate Progress",
                                f"Advanced: '{item.title()}' is now Current.")
                return

        if current_idx != -1 and next_idx >= self.status_timeline.itemCount():
            self._log_event("Simulate Progress", "All tasks completed.")
        elif current_idx == -1:  # No current task, try to start the first pending
            for i in range(self.status_timeline.itemCount()):
                item = self.status_timeline.item(i)
                if item and item.status() == FluentTimelineItem.Status.PENDING:
                    item.setStatus(FluentTimelineItem.Status.CURRENT)
                    self._log_event("Simulate Progress",
                                    f"Started: '{item.title()}' is now Current.")
                    return
            self._log_event("Simulate Progress", "No pending tasks to start.")

    def _on_interactive_item_clicked(self, index: int):
        if not hasattr(self, 'interactive_timeline'):
            return
        item = self.interactive_timeline.item(index)
        if item:
            self._log_event(
                "Interactive Click", f"Clicked item {index}: '{item.title()}' - Status: {item.status().name}")
            if hasattr(self, 'selected_item_index_spinbox'):
                self.selected_item_index_spinbox.setValue(index)
            self._update_selected_item_info(index)
        else:
            self._log_event("Interactive Click",
                            f"Clicked item {index}: (Item not found)")

    def _add_interactive_item(self):
        if not (hasattr(self, 'interactive_timeline') and hasattr(self, 'new_item_title_edit')):
            return
        title = self.new_item_title_edit.text()
        description = self.new_item_description_edit.toPlainText()
        timestamp = self.new_item_timestamp_edit.dateTime().toPython()
        status_name = self.new_item_status_combo.currentText()
        status = FluentTimelineItem.Status[status_name.upper()]

        # Convert float timestamp to datetime
        if isinstance(timestamp, float):
            ts_val = datetime.fromtimestamp(timestamp)
        else:
            ts_val = timestamp

        # Only pass datetime or QDateTime objects
        if not isinstance(ts_val, (datetime, QDateTime)):
            ts_val = None

        self.interactive_timeline.addItem(title, description, ts_val, status)
        self._log_event("Interactive Add", f"Added item: '{title}'")
        self._update_interactive_controls_ranges()

    def _insert_interactive_item(self):
        if not (hasattr(self, 'interactive_timeline') and hasattr(self, 'insert_position_spinbox')):
            return
        position = self.insert_position_spinbox.value()
        title = self.new_item_title_edit.text()
        description = self.new_item_description_edit.toPlainText()
        timestamp = self.new_item_timestamp_edit.dateTime().toPython()
        status_name = self.new_item_status_combo.currentText()
        status = FluentTimelineItem.Status[status_name.upper()]

        # Convert float timestamp to datetime
        if isinstance(timestamp, float):
            ts_val = datetime.fromtimestamp(timestamp)
        else:
            ts_val = timestamp

        # Only pass datetime or QDateTime objects
        if not isinstance(ts_val, (datetime, QDateTime)):
            ts_val = None

        self.interactive_timeline.insertItem(
            position, title, description, ts_val, status)
        self._log_event("Interactive Insert",
                        f"Inserted item: '{title}' at position {position}")
        self._update_interactive_controls_ranges()

    def _update_selected_item_info(self, index: int):
        if not (hasattr(self, 'interactive_timeline') and hasattr(self, 'selected_item_info_label')):
            return

        item = self.interactive_timeline.item(index)
        if not item:
            return

        # Get timestamp info
        ts = item.timestamp()
        if isinstance(ts, datetime):
            time_str = ts.strftime('%Y-%m-%d %H:%M')
        elif isinstance(ts, QDateTime):
            time_str = ts.toString('yyyy-MM-dd HH:mm')
        # Handle case when no items are selected or invalid index
        if self.interactive_timeline.itemCount() == 0:
            self.selected_item_info_label.setText("No items in timeline.")
            return
        elif index < 0 or index >= self.interactive_timeline.itemCount():
            self.selected_item_info_label.setText(
                f"Select an item (Index: {index})")
            return

        # For valid selected item
        if isinstance(ts, QDateTime):
            time_str = ts.toString('yyyy-MM-dd HH:mm')
        else:
            time_str = "No timestamp"

        # Update info label with all details
        self.selected_item_info_label.setText(
            f"<b>Title:</b> {item.title()}<br>"
            f"<b>Desc:</b> {item.description()[:50]}{'...' if len(item.description()) > 50 else ''}<br>"
            f"<b>Status:</b> {item.status().name}<br>"
            f"<b>Time:</b> {time_str}<br>"
        )

    def _remove_selected_item(self):
        if not (hasattr(self, 'interactive_timeline') and hasattr(self, 'selected_item_index_spinbox')):
            return
        if self.interactive_timeline.itemCount() == 0:
            self._log_event("Interactive Remove", "No items to remove.")
            return
        index = self.selected_item_index_spinbox.value()
        item = self.interactive_timeline.item(index)
        if item:
            title = item.title()
            self.interactive_timeline.removeItem(index)
            self._log_event("Interactive Remove",
                            f"Removed item: '{title}' at index {index}")
            self._update_interactive_controls_ranges()
            # Update info for potentially new item at current index or last item
            new_count = self.interactive_timeline.itemCount()
            if new_count == 0:
                self.selected_item_info_label.setText("No items in timeline.")
            else:
                new_index = min(index, new_count - 1)
                # May trigger _update_selected_item_info
                self.selected_item_index_spinbox.setValue(new_index)
                # Explicit call if spinbox value didn't change
                self._update_selected_item_info(new_index)
        else:
            self._log_event("Interactive Remove",
                            f"No item at index {index} to remove.")

    def _clear_interactive_timeline(self):
        if not hasattr(self, 'interactive_timeline'):
            return
        self.interactive_timeline.clear()
        self._log_event("Interactive Clear", "Cleared interactive timeline.")
        self._update_interactive_controls_ranges()
        if hasattr(self, 'selected_item_info_label'):
            self.selected_item_info_label.setText("No items in timeline.")

    def _toggle_item_clicking(self, checked: bool):
        if hasattr(self, 'interactive_timeline'):
            for i in range(self.interactive_timeline.itemCount()):
                item = self.interactive_timeline.item(i)
                if item:
                    item.setClickable(checked)
            self._log_event("Interactive Clickable",
                            f"Item clicking {'enabled' if checked else 'disabled'}.")

    def _update_interactive_controls_ranges(self):
        if not hasattr(self, 'interactive_timeline'):
            return
        count = self.interactive_timeline.itemCount()

        if hasattr(self, 'insert_position_spinbox'):
            # Can insert at the end (index == count)
            self.insert_position_spinbox.setRange(0, max(0, count))
            self.insert_position_spinbox.setEnabled(True)

        if hasattr(self, 'selected_item_index_spinbox'):
            is_enabled = count > 0
            self.selected_item_index_spinbox.setEnabled(is_enabled)
            if is_enabled:
                self.selected_item_index_spinbox.setRange(0, count - 1)
                # If current value is out of new range, adjust it
                if self.selected_item_index_spinbox.value() >= count:
                    self.selected_item_index_spinbox.setValue(
                        max(0, count - 1))
            else:
                self.selected_item_index_spinbox.setRange(
                    0, 0)  # Dummy range when disabled

        if hasattr(self, 'remove_item_btn'):
            self.remove_item_btn.setEnabled(count > 0)

    def _advance_timeline_progress(self, timeline: FluentTimeline):
        if not timeline:
            return

        current_idx = -1
        for i in range(timeline.itemCount()):
            item = timeline.item(i)
            if item and item.status() == FluentTimelineItem.Status.CURRENT:
                item.setStatus(FluentTimelineItem.Status.COMPLETED)
                current_idx = i
                break

        next_idx = current_idx + 1
        if 0 <= next_idx < timeline.itemCount():
            item = timeline.item(next_idx)
            if item and item.status() == FluentTimelineItem.Status.PENDING:
                item.setStatus(FluentTimelineItem.Status.CURRENT)
                self._log_event(
                    "Advance Progress", f"Timeline '{timeline.objectName()}' advanced. '{item.title()}' is Current.")
                return

        if current_idx != -1 and next_idx >= timeline.itemCount():
            self._log_event("Advance Progress",
                            f"Timeline '{timeline.objectName()}' reached end.")
        elif current_idx == -1:  # No current task, try to start the first pending
            for i in range(timeline.itemCount()):
                item = timeline.item(i)
                if item and item.status() == FluentTimelineItem.Status.PENDING:
                    item.setStatus(FluentTimelineItem.Status.CURRENT)
                    self._log_event(
                        "Advance Progress", f"Timeline '{timeline.objectName()}' started. '{item.title()}' is Current.")
                    return
            self._log_event(
                "Advance Progress", f"Timeline '{timeline.objectName()}' no pending tasks to start.")

    def _toggle_auto_progress(self, checked: bool):
        if checked:
            if self.auto_timer is None:
                self.auto_timer = QTimer(self)
                self.auto_timer.timeout.connect(
                    self._auto_advance_all_timelines)

            if hasattr(self, 'progress_speed_slider'):
                speed_value = self.progress_speed_slider.value()
                interval = max(500, 4000 - (speed_value - 1)
                               * 350)  # Adjust timing
                self.auto_timer.start(interval)
                self._log_event("Auto Progress",
                                f"Started with interval {interval}ms.")
            else:
                self.auto_timer.start(2000)  # Default if slider not found
                self._log_event(
                    "Auto Progress", "Started with default interval 2000ms (speed slider not found).")

        else:
            if self.auto_timer and self.auto_timer.isActive():
                self.auto_timer.stop()
                self._log_event("Auto Progress", "Stopped.")

    def _auto_advance_all_timelines(self):
        # Advance real-world timelines
        if hasattr(self, 'dev_timeline'):
            self._advance_timeline_progress(self.dev_timeline)
        if hasattr(self, 'order_timeline'):
            self._advance_timeline_progress(self.order_timeline)
        # if hasattr(self, 'project_timeline'): self._advance_timeline_progress(self.project_timeline) # If project_timeline is added

        # Update timer interval if speed changed
        if self.auto_timer and self.auto_timer.isActive() and hasattr(self, 'progress_speed_slider'):
            speed_value = self.progress_speed_slider.value()
            new_interval = max(500, 4000 - (speed_value - 1) * 350)
            if self.auto_timer.interval() != new_interval:
                self.auto_timer.setInterval(new_interval)
                # self._log_event("Auto Progress", f"Speed changed, new interval {new_interval}ms.") # Can be verbose

    def _add_random_item(self):
        if not hasattr(self, 'dynamic_timeline'):
            return
        titles = ["Random Event", "System Update",
                  "User Action", "Maintenance Task", "Log Entry"]
        descs = ["Automatically generated item.", "Details to be filled.",
                 "Requires attention.", "Scheduled operation."]
        statuses = list(FluentTimelineItem.Status)

        title = random.choice(titles) + f" #{random.randint(1000,9999)}"
        desc = random.choice(descs)
        timestamp = datetime.now() - timedelta(days=random.randint(-10, 0),
                                               hours=random.randint(0, 23), minutes=random.randint(0, 59))
        status = random.choice(statuses)

        self.dynamic_timeline.addItem(title, desc, timestamp, status)
        self._log_event("Dynamic Add", f"Added random item: '{title}'")

    def _add_multiple_items(self):
        if not (hasattr(self, 'dynamic_timeline') and hasattr(self, 'multiple_count_spinbox')):
            return
        count = self.multiple_count_spinbox.value()
        for _ in range(count):
            self._add_random_item()
        self._log_event("Dynamic Add Multiple", f"Added {count} random items.")

    def _remove_random_item(self):
        if not hasattr(self, 'dynamic_timeline') or self.dynamic_timeline.itemCount() == 0:
            self._log_event("Dynamic Remove", "No items to remove.")
            return
        index = random.randint(0, self.dynamic_timeline.itemCount() - 1)
        self._remove_item_at_index(index)  # Reuse existing logic

    def _remove_item_at_index(self, index: int):
        if not hasattr(self, 'dynamic_timeline'):
            return
        if 0 <= index < self.dynamic_timeline.itemCount():
            item = self.dynamic_timeline.item(index)
            title = item.title() if item else "Unknown"
            self.dynamic_timeline.removeItem(index)
            self._log_event("Dynamic Remove Index",
                            f"Removed item: '{title}' at index {index}")
        else:
            self._log_event(
                "Dynamic Remove Index", f"Invalid index: {index} for removal (Count: {self.dynamic_timeline.itemCount()}).")

    def _remove_last_item(self):
        if not hasattr(self, 'dynamic_timeline') or self.dynamic_timeline.itemCount() == 0:
            self._log_event("Dynamic Remove Last", "No items to remove.")
            return
        self._remove_item_at_index(self.dynamic_timeline.itemCount() - 1)

    def _shuffle_timeline_items(self):
        if not hasattr(self, 'dynamic_timeline') or self.dynamic_timeline.itemCount() < 2:
            self._log_event("Dynamic Shuffle", "Not enough items to shuffle.")
            return

        items_data = []
        for i in range(self.dynamic_timeline.itemCount()):
            item = self.dynamic_timeline.item(i)
            # if item: items_data.append(item.to_dict()) # Removed because to_dict doesn't exist

        random.shuffle(items_data)
        self.dynamic_timeline.clear()
        for data in items_data:
            # Assuming from_dict or constructor can take dict
            self.dynamic_timeline.addItem(
                data["title"], data["description"], data["timestamp"], data["status"])
        self._log_event("Dynamic Shuffle",
                        "Shuffled items in dynamic timeline.")

    def closeEvent(self, event):
        """Stop timers when closing the window."""
        if self.auto_timer and self.auto_timer.isActive():
            self.auto_timer.stop()
            self._log_event("System", "Auto progress timer stopped.")
        super().closeEvent(event)

# IMPORTANT: The duplicated TimelineDemo class definition that previously existed
# from around line 679 of the original file MUST BE DELETED.
# The code above should be the *only* TimelineDemo class definition.


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # theme_manager.set_theme_mode(ThemeMode.DARK) # Optional: Set initial theme
    window = TimelineDemo()
    window.show()
    sys.exit(app.exec())
