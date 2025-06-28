#!/usr/bin/env python3
"""
Fluent Calendar Component Demo

This example demonstrates the usage of FluentCalendar component with various configurations,
including date selection, validation, and theming.
"""

import sys
from pathlib import Path
from datetime import datetime, date

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox, QPushButton
from PySide6.QtCore import Qt


def main():
    """Run the calendar demo application."""
    app = QApplication(sys.argv)
    
    # Import after QApplication is created
    from components.data.input.calendar import OptimizedFluentCalendar
    from PySide6.QtCore import QDate
    
    class CalendarDemo(QMainWindow):
        """Main demo window showcasing Fluent calendar components."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Fluent Calendar Demo")
            self.setGeometry(200, 200, 900, 700)
            
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(20)
            main_layout.setContentsMargins(20, 20, 20, 20)
            
            # Add title
            title = QLabel("Fluent Calendar Components Demo")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
            main_layout.addWidget(title)
            
            # Create basic calendar section
            self.create_basic_calendar(main_layout)
            
            # Create interactive calendar section
            self.create_interactive_calendar(main_layout)
            
            main_layout.addStretch()
        
        def create_basic_calendar(self, parent_layout):
            """Create basic calendar examples."""
            group = QGroupBox("Basic Calendar Widget")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Basic calendar widget
            self.basic_calendar = OptimizedFluentCalendar()
            
            # Set today's date
            today_qdate = QDate.currentDate()
            self.basic_calendar.setSelectedDate(today_qdate)
            
            layout.addWidget(QLabel("Standard Calendar Widget:"))
            layout.addWidget(self.basic_calendar)
            
            # Status label
            self.basic_status = QLabel(f"Selected Date: {today_qdate.toString('yyyy-MM-dd')}")
            layout.addWidget(self.basic_status)
            
            # Connect date selection signal
            self.basic_calendar.dateSelected.connect(self.on_basic_date_changed)
            
            parent_layout.addWidget(group)
        
        def create_interactive_calendar(self, parent_layout):
            """Create interactive calendar examples."""
            group = QGroupBox("Interactive Calendar with Controls")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Interactive calendar widget
            self.interactive_calendar = OptimizedFluentCalendar()
            
            # Control buttons
            control_layout = QHBoxLayout()
            
            today_btn = QPushButton("Go to Today")
            today_btn.clicked.connect(self.go_to_today)
            
            clear_btn = QPushButton("Clear Selection")
            clear_btn.clicked.connect(self.clear_selection)
            
            prev_month_btn = QPushButton("Previous Month")
            prev_month_btn.clicked.connect(self.prev_month)
            
            next_month_btn = QPushButton("Next Month")
            next_month_btn.clicked.connect(self.next_month)
            
            control_layout.addWidget(today_btn)
            control_layout.addWidget(clear_btn)
            control_layout.addWidget(prev_month_btn)
            control_layout.addWidget(next_month_btn)
            control_layout.addStretch()
            
            layout.addWidget(QLabel("Interactive Calendar with Navigation:"))
            layout.addWidget(self.interactive_calendar)
            layout.addLayout(control_layout)
            
            # Status label
            self.interactive_status = QLabel("No date selected")
            layout.addWidget(self.interactive_status)
            
            # Connect signals
            self.interactive_calendar.dateSelected.connect(self.on_interactive_date_changed)
            
            parent_layout.addWidget(group)
        
        def on_basic_date_changed(self, selected_date):
            """Handle basic calendar date change."""
            if selected_date.isValid():
                date_str = selected_date.toString("yyyy-MM-dd")
                self.basic_status.setText(f"Selected Date: {date_str}")
            else:
                self.basic_status.setText("No date selected")
        
        def on_interactive_date_changed(self, selected_date):
            """Handle interactive calendar date change."""
            if selected_date.isValid():
                date_str = selected_date.toString("yyyy-MM-dd")
                day_name = selected_date.toString("dddd")
                self.interactive_status.setText(f"Selected: {date_str} ({day_name})")
            else:
                self.interactive_status.setText("No date selected")
        
        def go_to_today(self):
            """Navigate to today's date."""
            today = QDate.currentDate()
            self.interactive_calendar.setSelectedDate(today)
        
        def clear_selection(self):
            """Clear the calendar selection."""
            self.interactive_calendar.setSelectedDate(QDate())
        
        def prev_month(self):
            """Navigate to previous month."""
            current_date = self.interactive_calendar.selectedDate()
            if not current_date.isValid():
                current_date = QDate.currentDate()
            
            prev_month_date = current_date.addMonths(-1)
            self.interactive_calendar.setCurrentMonthYear(prev_month_date.month(), prev_month_date.year())
        
        def next_month(self):
            """Navigate to next month."""
            current_date = self.interactive_calendar.selectedDate()
            if not current_date.isValid():
                current_date = QDate.currentDate()
            
            next_month_date = current_date.addMonths(1)
            self.interactive_calendar.setCurrentMonthYear(next_month_date.month(), next_month_date.year())
    
    # Set application properties
    app.setApplicationName("Fluent Calendar Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = CalendarDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
