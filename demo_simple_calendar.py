#!/usr/bin/env python3
"""
Standalone Calendar Demo

A simplified demo that works without complex imports.
"""

import sys
from datetime import datetime, date
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCalendarWidget, QGroupBox, QGridLayout,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, Signal, Slot
from PySide6.QtGui import QFont, QPalette


class SimpleFluentCalendar(QWidget):
    """Simple Fluent-style calendar using QCalendarWidget"""
    
    dateSelected = Signal(QDate)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_fluent_style()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Calendar")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        header.setFont(font)
        layout.addWidget(header)
        
        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.on_date_clicked)
        layout.addWidget(self.calendar)
        
        # Selected date display
        self.date_label = QLabel(f"Selected: {QDate.currentDate().toString()}")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.date_label)
    
    def apply_fluent_style(self):
        """Apply Fluent Design styling"""
        self.setStyleSheet("""
            QWidget {
                background-color: #F3F2F1;
                color: #323130;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QCalendarWidget {
                background-color: white;
                border: 1px solid #EDEBE9;
                border-radius: 4px;
                font-size: 12px;
            }
            QCalendarWidget QToolButton {
                height: 40px;
                width: 120px;
                color: #323130;
                font-size: 14px;
                icon-size: 16px, 16px;
                border: none;
                background-color: transparent;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #F3F2F1;
                border-radius: 2px;
            }
            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #EDEBE9;
                color: #323130;
            }
            QCalendarWidget QSpinBox {
                background-color: white;
                border: 1px solid #EDEBE9;
                border-radius: 2px;
                font-size: 12px;
                color: #323130;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: white;
                color: #323130;
                selection-background-color: #0078D4;
                selection-color: white;
            }
            QLabel {
                font-size: 14px;
                padding: 8px;
            }
        """)
    
    @Slot(QDate)
    def on_date_clicked(self, date):
        self.date_label.setText(f"Selected: {date.toString()}")
        self.dateSelected.emit(date)


class CalendarDemoWindow(QMainWindow):
    """Main demo window"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setWindowTitle("Fluent Calendar Demo")
        self.setFixedSize(800, 600)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Calendar section
        calendar_group = QGroupBox("Calendar")
        calendar_layout = QVBoxLayout(calendar_group)
        
        self.calendar = SimpleFluentCalendar()
        self.calendar.dateSelected.connect(self.on_date_selected)
        calendar_layout.addWidget(self.calendar)
        
        layout.addWidget(calendar_group)
        
        # Info section
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        
        self.info_label = QLabel("Select a date from the calendar")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        # Today button
        today_btn = QPushButton("Go to Today")
        today_btn.clicked.connect(self.go_to_today)
        info_layout.addWidget(today_btn)
        
        info_layout.addStretch()
        layout.addWidget(info_group)
    
    @Slot(QDate)
    def on_date_selected(self, date):
        date_str = date.toString("dddd, MMMM d, yyyy")
        days_from_today = QDate.currentDate().daysTo(date)
        
        if days_from_today == 0:
            relative = "Today"
        elif days_from_today == 1:
            relative = "Tomorrow"
        elif days_from_today == -1:
            relative = "Yesterday"
        elif days_from_today > 0:
            relative = f"In {days_from_today} days"
        else:
            relative = f"{abs(days_from_today)} days ago"
        
        self.info_label.setText(f"Selected Date:\n{date_str}\n\n{relative}")
    
    @Slot()
    def go_to_today(self):
        today = QDate.currentDate()
        self.calendar.calendar.setSelectedDate(today)
        self.on_date_selected(today)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent Calendar Demo")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Fluent UI Components")
    
    # Apply modern styling
    app.setStyle('Fusion')
    
    # Create and show demo window
    demo = CalendarDemoWindow()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
