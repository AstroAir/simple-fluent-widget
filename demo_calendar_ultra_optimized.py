#!/usr/bin/env python3
"""
Ultra-Optimized Calendar Components Demo

Demonstrates the latest optimizations in calendar and date/time picker components:
- Modern Python 3.11+ features
- Performance optimizations with memory pooling
- Enhanced animations and micro-interactions
- Advanced theming and configuration
- Type safety and error handling
"""

import sys
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QGroupBox, QPushButton, QSpinBox, QCheckBox,
    QComboBox, QTextEdit, QSplitter, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, QDate, QTime, QDateTime, Slot
from PySide6.QtGui import QFont, QPalette

# Enhanced error handling for imports
import os
import sys

# Add the current directory to path to allow direct imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Direct import to avoid component package import issues
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'components', 'data'))
    from calendar import (
        OptimizedFluentCalendar, OptimizedFluentDatePicker,
        OptimizedFluentTimePicker, OptimizedFluentDateTimePicker,
        CalendarConfig, CalendarTheme, CalendarStateType,
        WidgetPoolManager, batch_widget_updates
    )
    CALENDAR_AVAILABLE = True
except ImportError as e:
    print(f"Calendar components not available: {e}")
    CALENDAR_AVAILABLE = False
    
    # Fallback classes
    class OptimizedFluentCalendar:
        def __init__(self, *args, **kwargs): pass
    class OptimizedFluentDatePicker:
        def __init__(self, *args, **kwargs): pass
    class OptimizedFluentTimePicker:
        def __init__(self, *args, **kwargs): pass
    class OptimizedFluentDateTimePicker:
        def __init__(self, *args, **kwargs): pass
    class CalendarConfig:
        def __init__(self, **kwargs): pass
    class CalendarTheme:
        def __init__(self, **kwargs): pass

try:
    from core.theme import theme_manager
    THEME_AVAILABLE = True
except ImportError:
    print("Theme manager not available")
    THEME_AVAILABLE = False
    theme_manager = None


class PerformanceMonitor(QWidget):
    """Widget to monitor and display performance metrics"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.metrics = {
            'widget_pool_size': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'render_time': 0.0,
            'memory_usage': 0
        }
        
        # Update metrics every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Performance Metrics")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.metrics_text = QTextEdit()
        self.metrics_text.setMaximumHeight(150)
        self.metrics_text.setReadOnly(True)
        layout.addWidget(self.metrics_text)
    
    @Slot()
    def update_metrics(self):
        """Update performance metrics display"""
        if CALENDAR_AVAILABLE:
            # Get widget pool metrics
            pool_manager = WidgetPoolManager()
            total_widgets = sum(len(pool) for pool in pool_manager._pools.values())
            self.metrics['widget_pool_size'] = total_widgets
        
        # Format metrics display
        metrics_text = f"""
Widget Pool Size: {self.metrics['widget_pool_size']}
Cache Hits: {self.metrics['cache_hits']}
Cache Misses: {self.metrics['cache_misses']}
Avg Render Time: {self.metrics['render_time']:.2f}ms
Memory Usage: {self.metrics['memory_usage']:.1f}MB
Last Updated: {datetime.now().strftime('%H:%M:%S')}
        """.strip()
        
        self.metrics_text.setPlainText(metrics_text)


class CalendarDemoTab(QWidget):
    """Optimized calendar widget demonstration"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Left panel - Calendar
        left_panel = QGroupBox("Ultra-Optimized Calendar")
        left_layout = QVBoxLayout(left_panel)
        
        if CALENDAR_AVAILABLE:
            # Create optimized configuration
            config = CalendarConfig(
                locale="zh_CN",
                enable_animations=True,
                weekend_highlighting=True,
                today_highlighting=True,
                cache_size=256,
                batch_update_threshold=20,
                lazy_loading=True
            )
            
            self.calendar = OptimizedFluentCalendar(config=config)
            self.calendar.dateSelected.connect(self.on_date_selected)
            self.calendar.monthChanged.connect(self.on_month_changed)
            left_layout.addWidget(self.calendar)
        else:
            left_layout.addWidget(QLabel("Calendar not available"))
        
        layout.addWidget(left_panel)
        
        # Right panel - Controls and Info
        right_panel = QGroupBox("Controls & Information")
        right_layout = QVBoxLayout(right_panel)
        
        # Date information
        self.date_info = QLabel("Select a date to see information")
        self.date_info.setWordWrap(True)
        right_layout.addWidget(self.date_info)
        
        # Configuration controls
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout(config_group)
        
        self.animations_cb = QCheckBox("Enable Animations")
        self.animations_cb.setChecked(True)
        self.animations_cb.toggled.connect(self.toggle_animations)
        config_layout.addWidget(self.animations_cb)
        
        self.weekend_cb = QCheckBox("Highlight Weekends")
        self.weekend_cb.setChecked(True)
        self.weekend_cb.toggled.connect(self.toggle_weekend_highlighting)
        config_layout.addWidget(self.weekend_cb)
        
        self.today_cb = QCheckBox("Highlight Today")
        self.today_cb.setChecked(True)
        self.today_cb.toggled.connect(self.toggle_today_highlighting)
        config_layout.addWidget(self.today_cb)
        
        right_layout.addWidget(config_group)
        
        # Theme controls
        theme_group = QGroupBox("Theme Options")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Default", "Dark", "Light", "High Contrast"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(QLabel("Theme:"))
        theme_layout.addWidget(self.theme_combo)
        
        right_layout.addWidget(theme_group)
        right_layout.addStretch()
        
        layout.addWidget(right_panel)
    
    @Slot(QDate)
    def on_date_selected(self, date):
        """Handle date selection"""
        info = f"""
Selected Date: {date.toString('yyyy-MM-dd')}
Day of Week: {date.toString('dddd')}
Week Number: {date.weekNumber()}
Days in Month: {date.daysInMonth()}
Is Valid: {date.isValid()}
Julian Day: {date.toJulianDay()}
        """.strip()
        self.date_info.setText(info)
    
    @Slot(int, int)
    def on_month_changed(self, month, year):
        """Handle month change"""
        print(f"Month changed to: {month}/{year}")
    
    @Slot(bool)
    def toggle_animations(self, enabled):
        """Toggle animation settings"""
        if CALENDAR_AVAILABLE and hasattr(self, 'calendar'):
            self.calendar._config.enable_animations = enabled
    
    @Slot(bool)
    def toggle_weekend_highlighting(self, enabled):
        """Toggle weekend highlighting"""
        if CALENDAR_AVAILABLE and hasattr(self, 'calendar'):
            self.calendar._config.weekend_highlighting = enabled
            self.calendar._update_calendar()
    
    @Slot(bool)
    def toggle_today_highlighting(self, enabled):
        """Toggle today highlighting"""
        if CALENDAR_AVAILABLE and hasattr(self, 'calendar'):
            self.calendar._config.today_highlighting = enabled
            self.calendar._update_calendar()
    
    @Slot(str)
    def change_theme(self, theme_name):
        """Change theme"""
        print(f"Theme changed to: {theme_name}")
        # Theme change implementation would go here


class DatePickerDemoTab(QWidget):
    """Date picker demonstration with validation"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Date picker demo
        picker_group = QGroupBox("Ultra-Optimized Date Picker")
        picker_layout = QVBoxLayout(picker_group)
        
        if CALENDAR_AVAILABLE:
            config = CalendarConfig(
                date_format="yyyy-MM-dd",
                enable_animations=True,
                lazy_loading=True
            )
            
            self.date_picker = OptimizedFluentDatePicker(config=config)
            self.date_picker.dateChanged.connect(self.on_date_changed)
            
            # Connect validation error signal if available
            if hasattr(self.date_picker, 'validationError'):
                self.date_picker.validationError.connect(self.on_validation_error)
            
            picker_layout.addWidget(self.date_picker)
        else:
            picker_layout.addWidget(QLabel("Date picker not available"))
        
        layout.addWidget(picker_group)
        
        # Format options
        format_group = QGroupBox("Format Options")
        format_layout = QVBoxLayout(format_group)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "yyyy-MM-dd",
            "dd/MM/yyyy", 
            "MM/dd/yyyy",
            "yyyy年MM月dd日",
            "dd.MM.yyyy"
        ])
        self.format_combo.currentTextChanged.connect(self.change_format)
        format_layout.addWidget(QLabel("Date Format:"))
        format_layout.addWidget(self.format_combo)
        
        layout.addWidget(format_group)
        
        # Output display
        output_group = QGroupBox("Output & Validation")
        output_layout = QVBoxLayout(output_group)
        
        self.output_label = QLabel("No date selected")
        self.output_label.setWordWrap(True)
        output_layout.addWidget(self.output_label)
        
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: red;")
        self.validation_label.setWordWrap(True)
        output_layout.addWidget(self.validation_label)
        
        layout.addWidget(output_group)
        layout.addStretch()
    
    @Slot(QDate)
    def on_date_changed(self, date):
        """Handle date change"""
        self.output_label.setText(f"Selected: {date.toString()}")
        self.validation_label.clear()
    
    @Slot(str)
    def on_validation_error(self, error):
        """Handle validation error"""
        self.validation_label.setText(f"Validation Error: {error}")
    
    @Slot(str)
    def change_format(self, format_str):
        """Change date format"""
        if CALENDAR_AVAILABLE and hasattr(self, 'date_picker'):
            self.date_picker.setFormat(format_str)


class TimePickerDemoTab(QWidget):
    """Time picker demonstration"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Time picker demo
        picker_group = QGroupBox("Ultra-Optimized Time Picker")
        picker_layout = QVBoxLayout(picker_group)
        
        if CALENDAR_AVAILABLE:
            self.time_picker = OptimizedFluentTimePicker()
            self.time_picker.timeChanged.connect(self.on_time_changed)
            
            # Connect validation error signal if available
            if hasattr(self.time_picker, 'validationError'):
                self.time_picker.validationError.connect(self.on_validation_error)
            
            picker_layout.addWidget(self.time_picker)
        else:
            picker_layout.addWidget(QLabel("Time picker not available"))
        
        layout.addWidget(picker_group)
        
        # Format controls
        format_group = QGroupBox("Format Controls")
        format_layout = QVBoxLayout(format_group)
        
        self.format_24h_cb = QCheckBox("24-Hour Format")
        self.format_24h_cb.setChecked(True)
        self.format_24h_cb.toggled.connect(self.toggle_24h_format)
        format_layout.addWidget(self.format_24h_cb)
        
        self.show_seconds_cb = QCheckBox("Show Seconds")
        self.show_seconds_cb.toggled.connect(self.toggle_seconds)
        format_layout.addWidget(self.show_seconds_cb)
        
        layout.addWidget(format_group)
        
        # Output display
        output_group = QGroupBox("Time Output")
        output_layout = QVBoxLayout(output_group)
        
        self.time_output = QLabel("No time selected")
        output_layout.addWidget(self.time_output)
        
        self.validation_output = QLabel("")
        self.validation_output.setStyleSheet("color: red;")
        output_layout.addWidget(self.validation_output)
        
        layout.addWidget(output_group)
        layout.addStretch()
    
    @Slot(QTime)
    def on_time_changed(self, time):
        """Handle time change"""
        self.time_output.setText(f"Selected: {time.toString()}")
        self.validation_output.clear()
    
    @Slot(str)
    def on_validation_error(self, error):
        """Handle validation error"""
        self.validation_output.setText(f"Validation Error: {error}")
    
    @Slot(bool)
    def toggle_24h_format(self, enabled):
        """Toggle 24-hour format"""
        if CALENDAR_AVAILABLE and hasattr(self, 'time_picker'):
            self.time_picker.setUse24HourFormat(enabled)
    
    @Slot(bool)
    def toggle_seconds(self, enabled):
        """Toggle seconds display"""
        if CALENDAR_AVAILABLE and hasattr(self, 'time_picker'):
            self.time_picker.setShowSeconds(enabled)


class DateTimePickerDemoTab(QWidget):
    """DateTime picker demonstration"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # DateTime picker demo
        picker_group = QGroupBox("Ultra-Optimized DateTime Picker")
        picker_layout = QVBoxLayout(picker_group)
        
        if CALENDAR_AVAILABLE:
            config = CalendarConfig(
                enable_animations=True,
                lazy_loading=True
            )
            
            self.datetime_picker = OptimizedFluentDateTimePicker(config=config)
            self.datetime_picker.dateTimeChanged.connect(self.on_datetime_changed)
            self.datetime_picker.dateChanged.connect(self.on_date_changed)
            self.datetime_picker.timeChanged.connect(self.on_time_changed)
            
            # Connect validation error if available
            if hasattr(self.datetime_picker, 'validationError'):
                self.datetime_picker.validationError.connect(self.on_validation_error)
            
            picker_layout.addWidget(self.datetime_picker)
        else:
            picker_layout.addWidget(QLabel("DateTime picker not available"))
        
        layout.addWidget(picker_group)
        
        # Quick set buttons
        quick_group = QGroupBox("Quick Set Options")
        quick_layout = QHBoxLayout(quick_group)
        
        now_btn = QPushButton("Now")
        now_btn.clicked.connect(self.set_now)
        quick_layout.addWidget(now_btn)
        
        tomorrow_btn = QPushButton("Tomorrow 9 AM")
        tomorrow_btn.clicked.connect(self.set_tomorrow_9am)
        quick_layout.addWidget(tomorrow_btn)
        
        week_btn = QPushButton("Next Week")
        week_btn.clicked.connect(self.set_next_week)
        quick_layout.addWidget(week_btn)
        
        layout.addWidget(quick_group)
        
        # Output display
        output_group = QGroupBox("DateTime Output")
        output_layout = QVBoxLayout(output_group)
        
        self.datetime_output = QLabel("No datetime selected")
        self.datetime_output.setWordWrap(True)
        output_layout.addWidget(self.datetime_output)
        
        self.validation_output = QLabel("")
        self.validation_output.setStyleSheet("color: red;")
        output_layout.addWidget(self.validation_output)
        
        layout.addWidget(output_group)
        layout.addStretch()
    
    @Slot(QDateTime)
    def on_datetime_changed(self, datetime):
        """Handle datetime change"""
        info = f"""
DateTime: {datetime.toString()}
Date: {datetime.date().toString()}
Time: {datetime.time().toString()}
Unix Timestamp: {datetime.toSecsSinceEpoch()}
ISO Format: {datetime.toString(Qt.DateFormat.ISODate)}
        """.strip()
        self.datetime_output.setText(info)
        self.validation_output.clear()
    
    @Slot(QDate)
    def on_date_changed(self, date):
        """Handle date component change"""
        print(f"Date component changed: {date.toString()}")
    
    @Slot(QTime)
    def on_time_changed(self, time):
        """Handle time component change"""
        print(f"Time component changed: {time.toString()}")
    
    @Slot(str)
    def on_validation_error(self, error):
        """Handle validation error"""
        self.validation_output.setText(f"Validation Error: {error}")
    
    @Slot()
    def set_now(self):
        """Set to current datetime"""
        if CALENDAR_AVAILABLE and hasattr(self, 'datetime_picker'):
            self.datetime_picker.setDateTime(QDateTime.currentDateTime())
    
    @Slot()
    def set_tomorrow_9am(self):
        """Set to tomorrow at 9 AM"""
        if CALENDAR_AVAILABLE and hasattr(self, 'datetime_picker'):
            tomorrow = QDate.currentDate().addDays(1)
            time_9am = QTime(9, 0)
            self.datetime_picker.setDateTime(QDateTime(tomorrow, time_9am))
    
    @Slot()
    def set_next_week(self):
        """Set to next week"""
        if CALENDAR_AVAILABLE and hasattr(self, 'datetime_picker'):
            next_week = QDate.currentDate().addDays(7)
            current_time = QTime.currentTime()
            self.datetime_picker.setDateTime(QDateTime(next_week, current_time))


class UltraOptimizedCalendarDemo(QMainWindow):
    """Main demo window showcasing ultra-optimized calendar components"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultra-Optimized Calendar Components Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
        self.setup_menu()
        
        # Performance monitoring
        self.start_performance_monitoring()
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create splitter for main content and performance monitor
        splitter = QSplitter(Qt.Orientation.Vertical)
        central_widget.setLayout(QVBoxLayout())
        central_widget.layout().addWidget(splitter)
        
        # Main tab widget
        self.tab_widget = QTabWidget()
        
        # Add demo tabs
        self.tab_widget.addTab(CalendarDemoTab(), "📅 Calendar")
        self.tab_widget.addTab(DatePickerDemoTab(), "📋 Date Picker") 
        self.tab_widget.addTab(TimePickerDemoTab(), "🕐 Time Picker")
        self.tab_widget.addTab(DateTimePickerDemoTab(), "📅🕐 DateTime Picker")
        
        splitter.addWidget(self.tab_widget)
        
        # Performance monitor
        self.performance_monitor = PerformanceMonitor()
        splitter.addWidget(self.performance_monitor)
        
        # Set splitter proportions
        splitter.setSizes([600, 200])
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Exit", self.close)
        
        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Toggle Performance Monitor", self.toggle_performance_monitor)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.show_about)
    
    def start_performance_monitoring(self):
        """Start performance monitoring"""
        if CALENDAR_AVAILABLE:
            print("Performance monitoring enabled")
            print(f"Widget pool manager initialized: {WidgetPoolManager()}")
    
    @Slot()
    def toggle_performance_monitor(self):
        """Toggle performance monitor visibility"""
        self.performance_monitor.setVisible(not self.performance_monitor.isVisible())
    
    @Slot()
    def show_about(self):
        """Show about dialog"""
        from PySide6.QtWidgets import QMessageBox
        
        about_text = """
Ultra-Optimized Calendar Components Demo

This demo showcases the latest optimizations in calendar and date/time picker components:

✅ Modern Python 3.11+ features (union types, dataclasses, pattern matching)
✅ Performance optimizations with memory pooling and caching
✅ Enhanced animations and micro-interactions  
✅ Advanced theming and configuration options
✅ Type safety and comprehensive error handling
✅ Batch operations and lazy evaluation
✅ Widget pooling for memory efficiency

Built with PySide6 and optimized for production use.
        """
        
        QMessageBox.about(self, "About", about_text.strip())


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Ultra-Optimized Calendar Demo")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Fluent UI Components")
    
    # Apply modern styling
    app.setStyle('Fusion')  # Modern look
    
    # Create and show demo window
    demo = UltraOptimizedCalendarDemo()
    demo.show()
    
    print("Ultra-Optimized Calendar Components Demo started")
    print(f"Calendar components available: {CALENDAR_AVAILABLE}")
    print(f"Theme manager available: {THEME_AVAILABLE}")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
