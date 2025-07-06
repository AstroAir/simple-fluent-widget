"""
Comprehensive Data Input Components Demo

This demo showcases all data input components available in the simple-fluent-widget library,
including color pickers, calendar widgets, and enhanced entry fields.

Features demonstrated:
- Color picker widgets with different styles
- Calendar and date selection
- Enhanced text entry with validation
- Event handling and data binding
- Best practices for data input UX
"""

import sys
from datetime import datetime, date
from typing import Any, Dict, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QGroupBox,
    QScrollArea, QFrame, QSpacerItem, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, QDate, pyqtSignal, Signal
from PySide6.QtGui import QColor, QPalette, QFont

# Import fluent components with fallbacks
try:
    from components.data.input.colorpicker import FluentColorPicker, FluentColorWheel, FluentColorButton
    FLUENT_COLOR_AVAILABLE = True
except ImportError:
    print("Warning: Fluent color picker components not available")
    FLUENT_COLOR_AVAILABLE = False

try:
    from components.data.input.calendar import FluentCalendar, FluentDatePicker
    FLUENT_CALENDAR_AVAILABLE = True
except ImportError:
    print("Warning: Fluent calendar components not available")
    FLUENT_CALENDAR_AVAILABLE = False

try:
    from components.data.input.entry import FluentLineEdit, FluentTextEdit, FluentPasswordEdit
    FLUENT_ENTRY_AVAILABLE = True
except ImportError:
    print("Warning: Fluent entry components not available")
    FLUENT_ENTRY_AVAILABLE = False

try:
    from components.layout.containers import FluentCard
    FLUENT_CARD_AVAILABLE = True
except ImportError:
    FLUENT_CARD_AVAILABLE = False


class DataInputDemo(QMainWindow):
    """Main demo window showcasing data input components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Input Components Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Data storage for demo
        self.demo_data = {
            'selected_color': QColor(100, 150, 200),
            'selected_date': QDate.currentDate(),
            'user_text': '',
            'validated_input': ''
        }
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Data Input Components Demo")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        main_layout.addWidget(scroll)
        
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        content_layout = QVBoxLayout(content_widget)
        
        # Create demo sections
        self.create_color_picker_section(content_layout)
        self.create_calendar_section(content_layout)
        self.create_entry_fields_section(content_layout)
        self.create_validation_section(content_layout)
        self.create_data_summary_section(content_layout)
        
        # Add stretch to push content to top
        content_layout.addStretch()
        
        # Status bar
        self.statusBar().showMessage("Ready - Select colors, dates, and enter text to see live updates")
        
    def create_color_picker_section(self, parent_layout):
        """Create color picker demonstration section."""
        group = QGroupBox("Color Picker Components")
        layout = QGridLayout(group)
        
        if FLUENT_COLOR_AVAILABLE:
            # Fluent Color Picker
            layout.addWidget(QLabel("Fluent Color Picker:"), 0, 0)
            try:
                self.color_picker = FluentColorPicker()
                self.color_picker.setCurrentColor(self.demo_data['selected_color'])
                layout.addWidget(self.color_picker, 0, 1)
            except Exception as e:
                layout.addWidget(QLabel(f"Error: {str(e)}"), 0, 1)
                self.color_picker = None
            
            # Fluent Color Wheel
            layout.addWidget(QLabel("Fluent Color Wheel:"), 1, 0)
            try:
                self.color_wheel = FluentColorWheel()
                self.color_wheel.setCurrentColor(self.demo_data['selected_color'])
                layout.addWidget(self.color_wheel, 1, 1)
            except Exception as e:
                layout.addWidget(QLabel(f"Error: {str(e)}"), 1, 1)
                self.color_wheel = None
            
            # Fluent Color Button
            layout.addWidget(QLabel("Fluent Color Button:"), 2, 0)
            try:
                self.color_button = FluentColorButton()
                self.color_button.setColor(self.demo_data['selected_color'])
                layout.addWidget(self.color_button, 2, 1)
            except Exception as e:
                layout.addWidget(QLabel(f"Error: {str(e)}"), 2, 1)
                self.color_button = None
        else:
            # Fallback color controls
            layout.addWidget(QLabel("Color Selection:"), 0, 0)
            self.color_button = QPushButton("Select Color")
            self.color_button.clicked.connect(self.select_color_fallback)
            layout.addWidget(self.color_button, 0, 1)
        
        # Color preview
        layout.addWidget(QLabel("Selected Color:"), 3, 0)
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(100, 30)
        self.color_preview.setStyleSheet("border: 1px solid black;")
        self.update_color_preview()
        layout.addWidget(self.color_preview, 3, 1)
        
        parent_layout.addWidget(group)
        
    def create_calendar_section(self, parent_layout):
        """Create calendar and date picker demonstration section."""
        group = QGroupBox("Calendar and Date Components")
        layout = QGridLayout(group)
        
        if FLUENT_CALENDAR_AVAILABLE:
            # Fluent Calendar
            layout.addWidget(QLabel("Fluent Calendar:"), 0, 0)
            try:
                self.calendar = FluentCalendar()
                self.calendar.setSelectedDate(self.demo_data['selected_date'])
                layout.addWidget(self.calendar, 0, 1, 1, 2)
            except Exception as e:
                layout.addWidget(QLabel(f"Error: {str(e)}"), 0, 1)
                self.calendar = None
            
            # Fluent Date Picker
            layout.addWidget(QLabel("Fluent Date Picker:"), 1, 0)
            try:
                self.date_picker = FluentDatePicker()
                self.date_picker.setDate(self.demo_data['selected_date'])
                layout.addWidget(self.date_picker, 1, 1)
            except Exception as e:
                layout.addWidget(QLabel(f"Error: {str(e)}"), 1, 1)
                self.date_picker = None
        else:
            # Fallback date controls
            from PySide6.QtWidgets import QCalendarWidget, QDateEdit
            
            layout.addWidget(QLabel("Calendar:"), 0, 0)
            self.calendar = QCalendarWidget()
            self.calendar.setSelectedDate(self.demo_data['selected_date'])
            layout.addWidget(self.calendar, 0, 1, 1, 2)
            
            layout.addWidget(QLabel("Date Picker:"), 1, 0)
            self.date_picker = QDateEdit()
            self.date_picker.setDate(self.demo_data['selected_date'])
            self.date_picker.setCalendarPopup(True)
            layout.addWidget(self.date_picker, 1, 1)
        
        # Date display
        layout.addWidget(QLabel("Selected Date:"), 2, 0)
        self.date_display = QLabel()
        self.update_date_display()
        layout.addWidget(self.date_display, 2, 1)
        
        parent_layout.addWidget(group)
        
    def create_entry_fields_section(self, parent_layout):
        """Create text entry fields demonstration section."""
        group = QGroupBox("Text Entry Components")
        layout = QGridLayout(group)
        
        if FLUENT_ENTRY_AVAILABLE:
            # Fluent Line Edit
            layout.addWidget(QLabel("Fluent Line Edit:"), 0, 0)
            try:
                self.fluent_line_edit = FluentLineEdit()
                self.fluent_line_edit.setPlaceholderText("Enter single line text...")
                layout.addWidget(self.fluent_line_edit, 0, 1)
            except Exception as e:
                layout.addWidget(QLabel(f"Error: {str(e)}"), 0, 1)
                self.fluent_line_edit = None
            
            # Fluent Text Edit
            layout.addWidget(QLabel("Fluent Text Edit:"), 1, 0)
            try:
                self.fluent_text_edit = FluentTextEdit()
                self.fluent_text_edit.setPlaceholderText("Enter multi-line text...")
                self.fluent_text_edit.setMaximumHeight(100)
                layout.addWidget(self.fluent_text_edit, 1, 1)
            except Exception as e:
                layout.addWidget(QLabel(f"Error: {str(e)}"), 1, 1)
                self.fluent_text_edit = None
            
            # Fluent Password Edit
            layout.addWidget(QLabel("Fluent Password Edit:"), 2, 0)
            try:
                self.fluent_password_edit = FluentPasswordEdit()
                self.fluent_password_edit.setPlaceholderText("Enter password...")
                layout.addWidget(self.fluent_password_edit, 2, 1)
            except Exception as e:
                layout.addWidget(QLabel(f"Error: {str(e)}"), 2, 1)
                self.fluent_password_edit = None
        else:
            # Fallback entry controls
            layout.addWidget(QLabel("Line Edit:"), 0, 0)
            self.fluent_line_edit = QLineEdit()
            self.fluent_line_edit.setPlaceholderText("Enter single line text...")
            layout.addWidget(self.fluent_line_edit, 0, 1)
            
            layout.addWidget(QLabel("Text Edit:"), 1, 0)
            self.fluent_text_edit = QTextEdit()
            self.fluent_text_edit.setPlaceholderText("Enter multi-line text...")
            self.fluent_text_edit.setMaximumHeight(100)
            layout.addWidget(self.fluent_text_edit, 1, 1)
            
            layout.addWidget(QLabel("Password Edit:"), 2, 0)
            self.fluent_password_edit = QLineEdit()
            self.fluent_password_edit.setPlaceholderText("Enter password...")
            self.fluent_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            layout.addWidget(self.fluent_password_edit, 2, 1)
        
        parent_layout.addWidget(group)
        
    def create_validation_section(self, parent_layout):
        """Create input validation demonstration section."""
        group = QGroupBox("Input Validation Examples")
        layout = QGridLayout(group)
        
        # Email validation
        layout.addWidget(QLabel("Email:"), 0, 0)
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("user@example.com")
        self.email_edit.textChanged.connect(self.validate_email)
        layout.addWidget(self.email_edit, 0, 1)
        
        self.email_status = QLabel("Enter email address")
        layout.addWidget(self.email_status, 0, 2)
        
        # Number validation
        layout.addWidget(QLabel("Number (1-100):"), 1, 0)
        self.number_edit = QLineEdit()
        self.number_edit.setPlaceholderText("50")
        self.number_edit.textChanged.connect(self.validate_number)
        layout.addWidget(self.number_edit, 1, 1)
        
        self.number_status = QLabel("Enter number between 1 and 100")
        layout.addWidget(self.number_status, 1, 2)
        
        # Required field
        layout.addWidget(QLabel("Required Field:"), 2, 0)
        self.required_edit = QLineEdit()
        self.required_edit.setPlaceholderText("This field is required")
        self.required_edit.textChanged.connect(self.validate_required)
        layout.addWidget(self.required_edit, 2, 1)
        
        self.required_status = QLabel("Field is required")
        layout.addWidget(self.required_status, 2, 2)
        
        parent_layout.addWidget(group)
        
    def create_data_summary_section(self, parent_layout):
        """Create data summary section showing current values."""
        group = QGroupBox("Current Data Summary")
        layout = QVBoxLayout(group)
        
        self.data_summary = QTextEdit()
        self.data_summary.setMaximumHeight(150)
        self.data_summary.setReadOnly(True)
        layout.addWidget(self.data_summary)
        
        # Update button
        update_btn = QPushButton("Update Summary")
        update_btn.clicked.connect(self.update_data_summary)
        layout.addWidget(update_btn)
        
        # Clear button
        clear_btn = QPushButton("Clear All Inputs")
        clear_btn.clicked.connect(self.clear_all_inputs)
        layout.addWidget(clear_btn)
        
        parent_layout.addWidget(group)
        
        # Initial summary update
        self.update_data_summary()
        
    def connect_signals(self):
        """Connect signals for real-time updates."""
        # Color picker signals
        if hasattr(self, 'color_picker') and self.color_picker:
            try:
                if hasattr(self.color_picker, 'colorChanged'):
                    self.color_picker.colorChanged.connect(self.on_color_changed)
            except Exception:
                pass
        
        if hasattr(self, 'color_wheel') and self.color_wheel:
            try:
                if hasattr(self.color_wheel, 'colorChanged'):
                    self.color_wheel.colorChanged.connect(self.on_color_changed)
            except Exception:
                pass
        
        if hasattr(self, 'color_button') and self.color_button:
            try:
                if hasattr(self.color_button, 'colorChanged'):
                    self.color_button.colorChanged.connect(self.on_color_changed)
            except Exception:
                pass
        
        # Calendar signals
        if hasattr(self, 'calendar') and self.calendar:
            if hasattr(self.calendar, 'selectionChanged'):
                self.calendar.selectionChanged.connect(self.on_date_changed)
            elif hasattr(self.calendar, 'clicked'):
                self.calendar.clicked.connect(self.on_date_changed)
        
        if hasattr(self, 'date_picker') and self.date_picker:
            if hasattr(self.date_picker, 'dateChanged'):
                self.date_picker.dateChanged.connect(self.on_date_changed)
        
        # Text entry signals
        if hasattr(self, 'fluent_line_edit') and self.fluent_line_edit:
            self.fluent_line_edit.textChanged.connect(self.on_text_changed)
        
        if hasattr(self, 'fluent_text_edit') and self.fluent_text_edit:
            if hasattr(self.fluent_text_edit, 'textChanged'):
                self.fluent_text_edit.textChanged.connect(self.on_text_changed)
    
    def on_color_changed(self, color):
        """Handle color selection changes."""
        if isinstance(color, QColor):
            self.demo_data['selected_color'] = color
            self.update_color_preview()
            self.statusBar().showMessage(f"Color changed to: {color.name()}")
    
    def on_date_changed(self, date=None):
        """Handle date selection changes."""
        if hasattr(self.calendar, 'selectedDate'):
            selected = self.calendar.selectedDate()
        elif hasattr(self.date_picker, 'date'):
            selected = self.date_picker.date()
        else:
            selected = QDate.currentDate()
        
        self.demo_data['selected_date'] = selected
        self.update_date_display()
        self.statusBar().showMessage(f"Date changed to: {selected.toString()}")
    
    def on_text_changed(self):
        """Handle text input changes."""
        sender = self.sender()
        if sender == self.fluent_line_edit:
            self.demo_data['user_text'] = sender.text()
            self.statusBar().showMessage(f"Text updated: {sender.text()[:20]}...")
    
    def select_color_fallback(self):
        """Fallback color selection dialog."""
        from PySide6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(self.demo_data['selected_color'], self)
        if color.isValid():
            self.demo_data['selected_color'] = color
            self.update_color_preview()
            self.on_color_changed(color)
    
    def update_color_preview(self):
        """Update the color preview display."""
        color = self.demo_data['selected_color']
        self.color_preview.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid black;"
        )
        self.color_preview.setText(f"{color.name()}")
    
    def update_date_display(self):
        """Update the date display."""
        date = self.demo_data['selected_date']
        self.date_display.setText(date.toString("dddd, MMMM d, yyyy"))
    
    def validate_email(self, text):
        """Validate email input."""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not text:
            self.email_status.setText("Enter email address")
            self.email_status.setStyleSheet("color: gray;")
        elif re.match(email_pattern, text):
            self.email_status.setText("✓ Valid email")
            self.email_status.setStyleSheet("color: green;")
        else:
            self.email_status.setText("✗ Invalid email format")
            self.email_status.setStyleSheet("color: red;")
    
    def validate_number(self, text):
        """Validate number input."""
        if not text:
            self.number_status.setText("Enter number between 1 and 100")
            self.number_status.setStyleSheet("color: gray;")
        else:
            try:
                value = float(text)
                if 1 <= value <= 100:
                    self.number_status.setText(f"✓ Valid number: {value}")
                    self.number_status.setStyleSheet("color: green;")
                else:
                    self.number_status.setText("✗ Number must be between 1 and 100")
                    self.number_status.setStyleSheet("color: red;")
            except ValueError:
                self.number_status.setText("✗ Invalid number format")
                self.number_status.setStyleSheet("color: red;")
    
    def validate_required(self, text):
        """Validate required field."""
        if not text.strip():
            self.required_status.setText("✗ Field is required")
            self.required_status.setStyleSheet("color: red;")
        else:
            self.required_status.setText("✓ Field completed")
            self.required_status.setStyleSheet("color: green;")
    
    def update_data_summary(self):
        """Update the data summary display."""
        summary = []
        summary.append("=== Current Input Data ===\n")
        
        # Color data
        color = self.demo_data['selected_color']
        summary.append(f"Selected Color: {color.name()} (RGB: {color.red()}, {color.green()}, {color.blue()})")
        
        # Date data
        date = self.demo_data['selected_date']
        summary.append(f"Selected Date: {date.toString('yyyy-MM-dd')} ({date.toString('dddd')})")
        
        # Text data
        if hasattr(self, 'fluent_line_edit') and self.fluent_line_edit:
            text = self.fluent_line_edit.text()
            summary.append(f"Line Edit Text: '{text}' ({len(text)} characters)")
        
        if hasattr(self, 'fluent_text_edit') and self.fluent_text_edit:
            if hasattr(self.fluent_text_edit, 'toPlainText'):
                text = self.fluent_text_edit.toPlainText()
            else:
                text = self.fluent_text_edit.text() if hasattr(self.fluent_text_edit, 'text') else ""
            lines = text.count('\n') + 1 if text else 0
            summary.append(f"Text Edit Content: {len(text)} characters, {lines} lines")
        
        # Validation status
        summary.append("\n=== Validation Status ===")
        summary.append(f"Email: {self.email_status.text()}")
        summary.append(f"Number: {self.number_status.text()}")
        summary.append(f"Required: {self.required_status.text()}")
        
        # Tips
        summary.append("\n=== Usage Tips ===")
        summary.append("• Colors can be selected using different picker styles")
        summary.append("• Date selection supports both calendar and dropdown picker")
        summary.append("• Text inputs support real-time validation")
        summary.append("• All components provide accessible keyboard navigation")
        
        self.data_summary.setText('\n'.join(summary))
    
    def clear_all_inputs(self):
        """Clear all input fields."""
        # Reset to defaults
        self.demo_data['selected_color'] = QColor(100, 150, 200)
        self.demo_data['selected_date'] = QDate.currentDate()
        
        # Clear text inputs
        if hasattr(self, 'fluent_line_edit') and self.fluent_line_edit:
            self.fluent_line_edit.clear()
        if hasattr(self, 'fluent_text_edit') and self.fluent_text_edit:
            if hasattr(self.fluent_text_edit, 'clear'):
                self.fluent_text_edit.clear()
        if hasattr(self, 'fluent_password_edit') and self.fluent_password_edit:
            self.fluent_password_edit.clear()
        
        # Clear validation inputs
        self.email_edit.clear()
        self.number_edit.clear()
        self.required_edit.clear()
        
        # Update displays
        self.update_color_preview()
        self.update_date_display()
        self.update_data_summary()
        
        self.statusBar().showMessage("All inputs cleared")


def main():
    """Main function to run the demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Data Input Components Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Simple Fluent Widget")
    
    # Create and show the demo
    demo = DataInputDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
