#!/usr/bin/env python3
"""
Demo for Optimized Calendar Components

This demo showcases the enhanced calendar components with modern Python features,
performance optimizations, and improved user experience.
"""

import sys
from pathlib import Path

# Add the project root to the path first
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QTabWidget, QLabel, QGroupBox, QCheckBox, QComboBox, QPushButton,
    QTextEdit, QScrollArea, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QTime, QDateTime, Slot
from PySide6.QtGui import QFont

# Import optimized calendar components with error handling
try:
    from components.data.calendar import (
        OptimizedFluentCalendar,
        OptimizedFluentDatePicker,
        OptimizedFluentTimePicker,
        OptimizedFluentDateTimePicker,
        CalendarConfig,
        CalendarTheme,
        FluentCalendar,  # Backward compatibility
        FluentDatePicker,  # Backward compatibility
        FluentTimePicker,  # Backward compatibility
        FluentDateTimePicker  # Backward compatibility
    )
    CALENDAR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import calendar components: {e}")
    CALENDAR_AVAILABLE = False


class CalendarDemoWindow(QMainWindow):
    """Main demo window for calendar components"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimized Fluent Calendar Components Demo")
        self.setMinimumSize(1000, 700)
        
        # Check if calendar components are available
        if not CALENDAR_AVAILABLE:
            self._show_error_message()
            return
        
        # Configuration for demo
        self.config = CalendarConfig(
            show_week_numbers=False,
            first_day_of_week=0,  # Sunday
            date_format="yyyy-MM-dd",
            enable_animations=True,
            weekend_highlighting=True,
            today_highlighting=True,
            locale="zh_CN"
        )
        
        self._setup_ui()
        self._setup_connections()
        
        # Center the window
        self._center_window()

    def _show_error_message(self):
        """Show error message if components are not available"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        error_label = QLabel(
            "Calendar components could not be loaded.\n"
            "Please check the component imports and dependencies."
        )
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("color: red; font-size: 16px; padding: 20px;")
        layout.addWidget(error_label)

    def _setup_ui(self):
        """Setup the demo UI"""
        if not CALENDAR_AVAILABLE:
            return
            
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title = QLabel("Optimized Fluent Calendar Components")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        description = QLabel(
            "Showcasing modern Python 3.11+ features, performance optimizations, "
            "and enhanced user experience in calendar components."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)
        
        # Tab widget for different demos
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create demo tabs
        self._create_calendar_tab()
        self._create_date_picker_tab()
        self._create_time_picker_tab()
        self._create_datetime_picker_tab()
        self._create_configuration_tab()
        
        # Status bar for events
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(120)
        self.status_text.setPlaceholderText("Component events will appear here...")
        layout.addWidget(QLabel("Event Log:"))
        layout.addWidget(self.status_text)

    def _create_calendar_tab(self):
        """Create calendar component demo tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Calendar section
        calendar_group = QGroupBox("Optimized Fluent Calendar")
        calendar_layout = QVBoxLayout(calendar_group)
        
        # Calendar widget
        self.calendar = OptimizedFluentCalendar(config=self.config)
        calendar_layout.addWidget(self.calendar)
        
        # Calendar info
        info_layout = QHBoxLayout()
        self.calendar_info = QLabel("Selected: None")
        info_layout.addWidget(self.calendar_info)
        info_layout.addStretch()
        calendar_layout.addLayout(info_layout)
        
        layout.addWidget(calendar_group)
        
        # Comparison section
        comparison_group = QGroupBox("Performance Comparison")
        comparison_layout = QVBoxLayout(comparison_group)
        
        comparison_text = QLabel(
            "• Optimized rendering with batch updates\n"
            "• Cached month/day names for better performance\n"
            "• Enhanced state management with dataclass patterns\n"
            "• Modern Python type hints and error handling\n"
            "• Context managers for efficient batch operations"
        )
        comparison_layout.addWidget(comparison_text)
        
        layout.addWidget(comparison_group)
        layout.addStretch()
        
        tab.setWidget(content)
        tab.setWidgetResizable(True)
        self.tab_widget.addTab(tab, "Calendar")

    def _create_date_picker_tab(self):
        """Create date picker demo tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Date picker section
        picker_group = QGroupBox("Optimized Fluent Date Picker")
        picker_layout = QVBoxLayout(picker_group)
        
        # Date picker widget
        self.date_picker = OptimizedFluentDatePicker(config=self.config)
        picker_layout.addWidget(self.date_picker)
        
        # Date picker controls
        controls_layout = QHBoxLayout()
        
        # Format selector
        controls_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "yyyy-MM-dd",
            "dd/MM/yyyy", 
            "MM-dd-yyyy",
            "yyyy年MM月dd日"
        ])
        controls_layout.addWidget(self.format_combo)
        
        # Set today button
        today_btn = QPushButton("Set Today")
        today_btn.clicked.connect(lambda: self.date_picker.setDate(QDate.currentDate()))
        controls_layout.addWidget(today_btn)
        
        controls_layout.addStretch()
        picker_layout.addLayout(controls_layout)
        
        # Date picker info
        self.date_picker_info = QLabel("Selected: None")
        picker_layout.addWidget(self.date_picker_info)
        
        layout.addWidget(picker_group)
        
        # Features section
        features_group = QGroupBox("Enhanced Features")
        features_layout = QVBoxLayout(features_group)
        
        features_text = QLabel(
            "• Enhanced date validation with user feedback\n"
            "• Smart calendar popup positioning\n"
            "• Keyboard navigation support\n"
            "• Lazy initialization for better performance\n"
            "• Error styling for invalid input\n"
            "• Configurable date formats"
        )
        features_layout.addWidget(features_text)
        
        layout.addWidget(features_group)
        layout.addStretch()
        
        tab.setWidget(content)
        tab.setWidgetResizable(True)
        self.tab_widget.addTab(tab, "Date Picker")

    def _create_time_picker_tab(self):
        """Create time picker demo tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Time picker section
        picker_group = QGroupBox("Optimized Fluent Time Picker")
        picker_layout = QVBoxLayout(picker_group)
        
        # Time picker widget
        self.time_picker = OptimizedFluentTimePicker(config=self.config)
        picker_layout.addWidget(self.time_picker)
        
        # Time picker controls
        controls_layout = QHBoxLayout()
        
        # 24-hour format checkbox
        self.format_24h_cb = QCheckBox("24-hour format")
        self.format_24h_cb.setChecked(True)
        controls_layout.addWidget(self.format_24h_cb)
        
        # Show seconds checkbox
        self.show_seconds_cb = QCheckBox("Show seconds")
        controls_layout.addWidget(self.show_seconds_cb)
        
        # Set current time button
        current_time_btn = QPushButton("Set Current Time")
        current_time_btn.clicked.connect(lambda: self.time_picker.setTime(QTime.currentTime()))
        controls_layout.addWidget(current_time_btn)
        
        controls_layout.addStretch()
        picker_layout.addLayout(controls_layout)
        
        # Time picker info
        self.time_picker_info = QLabel("Selected: None")
        picker_layout.addWidget(self.time_picker_info)
        
        layout.addWidget(picker_group)
        
        # Optimizations section
        optimizations_group = QGroupBox("Performance Optimizations")
        optimizations_layout = QVBoxLayout(optimizations_group)
        
        optimizations_text = QLabel(
            "• Cached control references for faster access\n"
            "• Signal blocking during batch updates\n"
            "• Context managers for efficient state changes\n"
            "• Enhanced validation with error feedback\n"
            "• Memory-efficient state management\n"
            "• Tooltip support for better UX"
        )
        optimizations_layout.addWidget(optimizations_text)
        
        layout.addWidget(optimizations_group)
        layout.addStretch()
        
        tab.setWidget(content)
        tab.setWidgetResizable(True)
        self.tab_widget.addTab(tab, "Time Picker")

    def _create_datetime_picker_tab(self):
        """Create datetime picker demo tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # DateTime picker section
        picker_group = QGroupBox("Optimized Fluent DateTime Picker")
        picker_layout = QVBoxLayout(picker_group)
        
        # DateTime picker widget
        self.datetime_picker = OptimizedFluentDateTimePicker(config=self.config)
        picker_layout.addWidget(self.datetime_picker)
        
        # DateTime picker controls
        controls_layout = QHBoxLayout()
        
        # Set current datetime button
        current_dt_btn = QPushButton("Set Current DateTime")
        current_dt_btn.clicked.connect(
            lambda: self.datetime_picker.setDateTime(QDateTime.currentDateTime())
        )
        controls_layout.addWidget(current_dt_btn)
        
        # Preset buttons
        tomorrow_btn = QPushButton("Tomorrow 9:00 AM")
        tomorrow_btn.clicked.connect(self._set_tomorrow_9am)
        controls_layout.addWidget(tomorrow_btn)
        
        controls_layout.addStretch()
        picker_layout.addLayout(controls_layout)
        
        # DateTime picker info
        self.datetime_picker_info = QLabel("Selected: None")
        picker_layout.addWidget(self.datetime_picker_info)
        
        layout.addWidget(picker_group)
        
        # Architecture section
        architecture_group = QGroupBox("Modern Architecture")
        architecture_layout = QVBoxLayout(architecture_group)
        
        architecture_text = QLabel(
            "• Type-safe API with modern Python annotations\n"
            "• Dataclass-based configuration system\n"
            "• Protocol-based interfaces for extensibility\n"
            "• Cached properties for performance\n"
            "• Context managers for batch operations\n"
            "• Enhanced error handling and validation"
        )
        architecture_layout.addWidget(architecture_text)
        
        layout.addWidget(architecture_group)
        layout.addStretch()
        
        tab.setWidget(content)
        tab.setWidgetResizable(True)
        self.tab_widget.addTab(tab, "DateTime Picker")

    def _create_configuration_tab(self):
        """Create configuration demo tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Configuration section
        config_group = QGroupBox("Component Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Configuration options
        options_layout = QVBoxLayout()
        
        # Animation toggle
        self.animations_cb = QCheckBox("Enable animations")
        self.animations_cb.setChecked(self.config.enable_animations)
        options_layout.addWidget(self.animations_cb)
        
        # Weekend highlighting
        self.weekend_cb = QCheckBox("Highlight weekends")
        self.weekend_cb.setChecked(self.config.weekend_highlighting)
        options_layout.addWidget(self.weekend_cb)
        
        # Today highlighting
        self.today_cb = QCheckBox("Highlight today")
        self.today_cb.setChecked(self.config.today_highlighting)
        options_layout.addWidget(self.today_cb)
        
        # First day of week
        first_day_layout = QHBoxLayout()
        first_day_layout.addWidget(QLabel("First day of week:"))
        self.first_day_combo = QComboBox()
        self.first_day_combo.addItems(["Sunday", "Monday"])
        first_day_layout.addWidget(self.first_day_combo)
        first_day_layout.addStretch()
        options_layout.addLayout(first_day_layout)
        
        # Locale selection
        locale_layout = QHBoxLayout()
        locale_layout.addWidget(QLabel("Locale:"))
        self.locale_combo = QComboBox()
        self.locale_combo.addItems(["zh_CN", "en_US"])
        locale_layout.addWidget(self.locale_combo)
        locale_layout.addStretch()
        options_layout.addLayout(locale_layout)
        
        config_layout.addLayout(options_layout)
        
        # Apply button
        apply_btn = QPushButton("Apply Configuration")
        apply_btn.clicked.connect(self._apply_configuration)
        config_layout.addWidget(apply_btn)
        
        layout.addWidget(config_group)
        
        # Technical details section
        tech_group = QGroupBox("Technical Implementation")
        tech_layout = QVBoxLayout(tech_group)
        
        tech_text = QLabel(
            "Modern Python 3.11+ Features Used:\n\n"
            "• Union type syntax (X | Y instead of Union[X, Y])\n"
            "• Dataclasses with frozen and field options\n"
            "• Enhanced pattern matching with match statements\n"
            "• Structural pattern matching for validation\n"
            "• Generic type annotations with TypeVar\n"
            "• Protocol-based typing for duck typing\n"
            "• Cached properties with @cached_property\n"
            "• Context managers with @contextmanager\n"
            "• Type aliases with TypeAlias annotation\n"
            "• Final annotations for constants\n"
            "• Enhanced exception groups\n"
            "• Performance optimizations with __slots__\n"
            "• Weak references for memory management\n"
            "• LRU caching for frequently accessed data\n"
            "• Async-compatible signal handling"
        )
        tech_text.setWordWrap(True)
        tech_layout.addWidget(tech_text)
        
        layout.addWidget(tech_group)
        layout.addStretch()
        
        tab.setWidget(content)
        tab.setWidgetResizable(True)
        self.tab_widget.addTab(tab, "Configuration")    def _setup_connections(self):
        """Setup signal connections"""
        if not CALENDAR_AVAILABLE:
            return
            
        # Calendar connections
        if hasattr(self, 'calendar'):
            self.calendar.dateSelected.connect(self._on_calendar_date_selected)
            self.calendar.monthChanged.connect(self._on_calendar_month_changed)
        
        # Date picker connections
        if hasattr(self, 'date_picker'):
            self.date_picker.dateChanged.connect(self._on_date_picker_changed)
            self.date_picker.validationError.connect(self._on_validation_error)
        
        if hasattr(self, 'format_combo'):
            self.format_combo.currentTextChanged.connect(self._on_format_changed)
        
        # Time picker connections
        if hasattr(self, 'time_picker'):
            self.time_picker.timeChanged.connect(self._on_time_picker_changed)
            self.time_picker.validationError.connect(self._on_validation_error)
        
        if hasattr(self, 'format_24h_cb'):
            self.format_24h_cb.toggled.connect(self.time_picker.setUse24HourFormat)
        
        if hasattr(self, 'show_seconds_cb'):
            self.show_seconds_cb.toggled.connect(self.time_picker.setShowSeconds)
        
        # DateTime picker connections
        if hasattr(self, 'datetime_picker'):
            self.datetime_picker.dateTimeChanged.connect(self._on_datetime_picker_changed)
            self.datetime_picker.validationError.connect(self._on_validation_error)

    @Slot(QDate)
    def _on_calendar_date_selected(self, date: QDate):
        """Handle calendar date selection"""
        self.calendar_info.setText(f"Selected: {date.toString('yyyy-MM-dd dddd')}")
        self._log_event(f"Calendar: Date selected - {date.toString('yyyy-MM-dd')}")

    @Slot(int, int)
    def _on_calendar_month_changed(self, month: int, year: int):
        """Handle calendar month change"""
        self._log_event(f"Calendar: Month changed to {month}/{year}")

    @Slot(QDate)
    def _on_date_picker_changed(self, date: QDate):
        """Handle date picker change"""
        self.date_picker_info.setText(f"Selected: {date.toString('yyyy-MM-dd dddd')}")
        self._log_event(f"Date Picker: Date changed to {date.toString('yyyy-MM-dd')}")

    @Slot(QTime)
    def _on_time_picker_changed(self, time: QTime):
        """Handle time picker change"""
        self.time_picker_info.setText(f"Selected: {time.toString('hh:mm:ss')}")
        self._log_event(f"Time Picker: Time changed to {time.toString('hh:mm:ss')}")

    @Slot(QDateTime)
    def _on_datetime_picker_changed(self, datetime: QDateTime):
        """Handle datetime picker change"""
        self.datetime_picker_info.setText(f"Selected: {datetime.toString('yyyy-MM-dd hh:mm:ss')}")
        self._log_event(f"DateTime Picker: DateTime changed to {datetime.toString('yyyy-MM-dd hh:mm:ss')}")

    @Slot(str)
    def _on_validation_error(self, error: str):
        """Handle validation errors"""
        self._log_event(f"Validation Error: {error}")

    @Slot(str)
    def _on_format_changed(self, format_str: str):
        """Handle format change"""
        self.date_picker.setFormat(format_str)
        self._log_event(f"Date format changed to: {format_str}")

    @Slot()
    def _set_tomorrow_9am(self):
        """Set datetime to tomorrow 9 AM"""
        tomorrow = QDate.currentDate().addDays(1)
        nine_am = QTime(9, 0)
        datetime = QDateTime(tomorrow, nine_am)
        self.datetime_picker.setDateTime(datetime)

    @Slot()
    def _apply_configuration(self):
        """Apply configuration changes"""
        # Update configuration
        self.config.enable_animations = self.animations_cb.isChecked()
        self.config.weekend_highlighting = self.weekend_cb.isChecked()
        self.config.today_highlighting = self.today_cb.isChecked()
        self.config.first_day_of_week = 0 if self.first_day_combo.currentText() == "Sunday" else 1
        self.config.locale = self.locale_combo.currentText()
        
        self._log_event("Configuration applied - restart demo to see all changes")

    def _log_event(self, message: str):
        """Log an event to the status text"""
        current_text = self.status_text.toPlainText()
        new_text = f"{message}\n{current_text}"
        # Keep only last 20 lines
        lines = new_text.split('\n')[:20]
        self.status_text.setPlainText('\n'.join(lines))

    def _center_window(self):
        """Center the window on screen"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())


def main():
    """Main function to run the demo"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Optimized Calendar Components Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Fluent Widget Project")
    
    # Create and show the demo window
    window = CalendarDemoWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
