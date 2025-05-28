#!/usr/bin/env python3
"""
Calendar and Date/Time Picker Components for Fluent UI

This module provides modern calendar and date/time picker components following Fluent Design principles.
Includes FluentCalendar, FluentDatePicker, FluentTimePicker, and FluentDateTimePicker components.
"""

from typing import Optional, Union
from datetime import datetime, date, time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QFrame, QLineEdit, QTimeEdit, QDateEdit,
    QCalendarWidget, QStackedWidget, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QDate, QTime, QDateTime, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPainter, QPen, QBrush, QColor, QMouseEvent, QIcon, QPixmap
from core.theme import theme_manager


class FluentCalendar(QWidget):
    """
    Modern calendar widget with Fluent Design styling
    
    Features:
    - Month/year navigation
    - Today highlighting
    - Selected date highlighting
    - Weekend highlighting
    - Hover effects
    - Smooth animations
    """
    
    # Signals
    dateClicked = Signal(QDate)
    dateSelected = Signal(QDate)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._selected_date = QDate.currentDate()
        self._today = QDate.currentDate()
        self._current_month = self._today.month()
        self._current_year = self._today.year()
        self._hovered_date = None
        
        self.setup_ui()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def setup_ui(self):
        """Setup the calendar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header with navigation
        self.setup_header(layout)
        
        # Day of week labels
        self.setup_day_labels(layout)
        
        # Calendar grid
        self.setup_calendar_grid(layout)
        
        # Update calendar
        self.update_calendar()
    
    def setup_header(self, layout: QVBoxLayout):
        """Setup header with month/year navigation"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Previous month button
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(32, 32)
        self.prev_btn.clicked.connect(self.previous_month)
        header_layout.addWidget(self.prev_btn)
        
        # Month/Year display
        self.month_year_label = QLabel()
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        self.month_year_label.setFont(font)
        self.month_year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.month_year_label, 1)
        
        # Next month button
        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(32, 32)
        self.next_btn.clicked.connect(self.next_month)
        header_layout.addWidget(self.next_btn)
        
        layout.addLayout(header_layout)
    
    def setup_day_labels(self, layout: QVBoxLayout):
        """Setup day of week labels"""
        days_layout = QHBoxLayout()
        days_layout.setSpacing(0)
        
        day_names = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        for day_name in day_names:
            label = QLabel(day_name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedHeight(32)
            font = QFont()
            font.setWeight(QFont.Weight.Bold)
            label.setFont(font)
            days_layout.addWidget(label)
        
        layout.addLayout(days_layout)
    
    def setup_calendar_grid(self, layout: QVBoxLayout):
        """Setup calendar grid"""
        self.calendar_widget = QWidget()
        self.calendar_layout = QGridLayout(self.calendar_widget)
        self.calendar_layout.setSpacing(2)
        self.calendar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create 6x7 grid for calendar days
        self.day_buttons = []
        for row in range(6):
            button_row = []
            for col in range(7):
                btn = CalendarDayButton()
                btn.setFixedSize(40, 40)
                btn.clicked.connect(self.on_day_clicked)
                self.calendar_layout.addWidget(btn, row, col)
                button_row.append(btn)
            self.day_buttons.append(button_row)
        
        layout.addWidget(self.calendar_widget)
    
    def update_calendar(self):
        """Update calendar display"""
        # Update month/year label
        month_names = [
            "一月", "二月", "三月", "四月", "五月", "六月",
            "七月", "八月", "九月", "十月", "十一月", "十二月"
        ]
        self.month_year_label.setText(f"{self._current_year}年 {month_names[self._current_month - 1]}")
        
        # Get first day of month
        first_day = QDate(self._current_year, self._current_month, 1)
        days_in_month = first_day.daysInMonth()
        start_day = first_day.dayOfWeek() % 7  # Sunday = 0
        
        # Clear all buttons first
        for row in self.day_buttons:
            for btn in row:
                btn.reset()
        
        # Fill in the days
        day = 1
        for row in range(6):
            for col in range(7):
                btn = self.day_buttons[row][col]
                cell_index = row * 7 + col
                
                if cell_index < start_day or day > days_in_month:
                    # Empty cell or previous/next month
                    btn.setVisible(False)
                else:
                    # Current month day
                    btn.setVisible(True)
                    btn.setDay(day)
                    
                    current_date = QDate(self._current_year, self._current_month, day)
                    
                    # Check if today
                    if current_date == self._today:
                        btn.setIsToday(True)
                    
                    # Check if selected
                    if current_date == self._selected_date:
                        btn.setIsSelected(True)
                    
                    # Check if weekend
                    if col == 0 or col == 6:  # Sunday or Saturday
                        btn.setIsWeekend(True)
                    
                    day += 1
        
        self.apply_theme()
    
    def on_day_clicked(self):
        """Handle day button click"""
        sender = self.sender()
        if isinstance(sender, CalendarDayButton) and sender.day() > 0:
            selected_date = QDate(self._current_year, self._current_month, sender.day())
            self.setSelectedDate(selected_date)
            self.dateClicked.emit(selected_date)
            self.dateSelected.emit(selected_date)
    
    def previous_month(self):
        """Go to previous month"""
        if self._current_month == 1:
            self._current_month = 12
            self._current_year -= 1
        else:
            self._current_month -= 1
        self.update_calendar()
    
    def next_month(self):
        """Go to next month"""
        if self._current_month == 12:
            self._current_month = 1
            self._current_year += 1
        else:
            self._current_month += 1
        self.update_calendar()
    
    def selectedDate(self) -> QDate:
        """Get selected date"""
        return self._selected_date
    
    def setSelectedDate(self, date: QDate):
        """Set selected date"""
        self._selected_date = date
        self._current_month = date.month()
        self._current_year = date.year()
        self.update_calendar()
    
    def apply_theme(self):
        """Apply current theme"""
        bg_color = theme_manager.get_color('surface')
        text_color = theme_manager.get_color('on_surface')
        primary_color = theme_manager.get_color('primary')
        
        self.setStyleSheet(f"""
            FluentCalendar {{
                background-color: {bg_color};
                border: 1px solid {theme_manager.get_color('outline')};
                border-radius: 12px;
            }}
            QPushButton {{
                background-color: {theme_manager.get_color('surface_variant')};
                color: {text_color};
                border: none;
                border-radius: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('on_primary')};
            }}
            QLabel {{
                color: {text_color};
            }}
        """)
        
        # Update day buttons theme
        for row in self.day_buttons:
            for btn in row:
                btn.apply_theme()


class CalendarDayButton(QPushButton):
    """Individual day button for calendar"""
    
    def __init__(self):
        super().__init__()
        self._day = 0
        self._is_today = False
        self._is_selected = False
        self._is_weekend = False
        self._is_hovered = False
        
        self.setMouseTracking(True)
    
    def setDay(self, day: int):
        """Set day number"""
        self._day = day
        self.setText(str(day))
    
    def day(self) -> int:
        """Get day number"""
        return self._day
    
    def setIsToday(self, is_today: bool):
        """Set if this is today"""
        self._is_today = is_today
    
    def setIsSelected(self, is_selected: bool):
        """Set if this is selected"""
        self._is_selected = is_selected
    
    def setIsWeekend(self, is_weekend: bool):
        """Set if this is weekend"""
        self._is_weekend = is_weekend
    
    def reset(self):
        """Reset button state"""
        self._day = 0
        self._is_today = False
        self._is_selected = False
        self._is_weekend = False
        self._is_hovered = False
        self.setText("")
    
    def enterEvent(self, event):
        """Handle mouse enter"""
        self._is_hovered = True
        self.apply_theme()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        self._is_hovered = False
        self.apply_theme()
        super().leaveEvent(event)
    
    def apply_theme(self):
        """Apply theme based on state"""
        if not self.isVisible() or self._day == 0:
            return
        
        bg_color = theme_manager.get_color('surface')
        text_color = theme_manager.get_color('on_surface')
        
        # Determine colors based on state
        if self._is_selected:
            bg_color = theme_manager.get_color('primary')
            text_color = theme_manager.get_color('on_primary')
        elif self._is_today:
            bg_color = theme_manager.get_color('secondary_container')
            text_color = theme_manager.get_color('on_secondary_container')
        elif self._is_hovered:
            bg_color = theme_manager.get_color('surface_variant')
            text_color = theme_manager.get_color('on_surface_variant')
        elif self._is_weekend:
            text_color = theme_manager.get_color('error')
        
        self.setStyleSheet(f"""
            CalendarDayButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 20px;
                font-weight: {"bold" if self._is_today or self._is_selected else "normal"};
            }}
        """)


class FluentDatePicker(QWidget):
    """
    Modern date picker widget with calendar popup
    
    Features:
    - Input field with date formatting
    - Calendar popup
    - Keyboard navigation
    - Date validation
    """
    
    # Signals
    dateChanged = Signal(QDate)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._date = QDate.currentDate()
        self._format = "yyyy-MM-dd"
        
        self.setup_ui()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def setup_ui(self):
        """Setup the date picker UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Date input field
        self.date_edit = QLineEdit()
        self.date_edit.setText(self._date.toString(self._format))
        self.date_edit.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.date_edit)
        
        # Calendar button
        self.calendar_btn = QPushButton("📅")
        self.calendar_btn.setFixedSize(32, 32)
        self.calendar_btn.clicked.connect(self.show_calendar)
        layout.addWidget(self.calendar_btn)
        
        # Calendar popup (initially hidden)
        self.calendar_popup = None
    
    def show_calendar(self):
        """Show calendar popup"""
        if self.calendar_popup is None:
            self.calendar_popup = CalendarPopup(self)
            self.calendar_popup.calendar.dateSelected.connect(self.on_date_selected)
        
        self.calendar_popup.setDate(self._date)
        self.calendar_popup.show_at_widget(self)
    
    def on_date_selected(self, date: QDate):
        """Handle date selection from calendar"""
        self.setDate(date)
        if self.calendar_popup:
            self.calendar_popup.hide()
    
    def on_text_changed(self, text: str):
        """Handle text change in input field"""
        try:
            date = QDate.fromString(text, self._format)
            if date.isValid():
                self._date = date
                self.dateChanged.emit(date)
        except:
            pass
    
    def date(self) -> QDate:
        """Get current date"""
        return self._date
    
    def setDate(self, date: QDate):
        """Set current date"""
        if date.isValid():
            self._date = date
            self.date_edit.setText(date.toString(self._format))
            self.dateChanged.emit(date)
    
    def format(self) -> str:
        """Get date format"""
        return self._format
    
    def setFormat(self, format_str: str):
        """Set date format"""
        self._format = format_str
        self.date_edit.setText(self._date.toString(self._format))
    
    def apply_theme(self):
        """Apply current theme"""
        bg_color = theme_manager.get_color('surface')
        text_color = theme_manager.get_color('on_surface')
        
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {theme_manager.get_color('outline')};
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {theme_manager.get_color('primary')};
            }}
            QPushButton {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('on_primary')};
                border: none;
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('primary_hover')};
            }}
        """)


class CalendarPopup(QWidget):
    """Calendar popup window"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setup_ui()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def setup_ui(self):
        """Setup popup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Shadow frame
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.Shape.Box)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        
        # Calendar
        self.calendar = FluentCalendar()
        frame_layout.addWidget(self.calendar)
        
        layout.addWidget(self.frame)
    
    def setDate(self, date: QDate):
        """Set calendar date"""
        self.calendar.setSelectedDate(date)
    
    def show_at_widget(self, widget: QWidget):
        """Show popup below the given widget"""
        global_pos = widget.mapToGlobal(widget.rect().bottomLeft())
        self.move(global_pos.x(), global_pos.y() + 4)
        self.show()
    
    def apply_theme(self):
        """Apply current theme"""
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme_manager.get_color('surface')};
                border: 1px solid {theme_manager.get_color('outline')};
                border-radius: 12px;
            }}
        """)


class FluentTimePicker(QWidget):
    """
    Modern time picker widget
    
    Features:
    - Hour/minute/second selection
    - 12/24 hour format support
    - Spin box controls
    - Time validation
    """
    
    # Signals
    timeChanged = Signal(QTime)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._time = QTime.currentTime()
        self._use_24_hour = True
        self._show_seconds = False
        
        self.setup_ui()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def setup_ui(self):
        """Setup time picker UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Hour spinbox
        self.hour_spin = QSpinBox()
        self.hour_spin.setMinimum(0 if self._use_24_hour else 1)
        self.hour_spin.setMaximum(23 if self._use_24_hour else 12)
        self.hour_spin.setValue(self._time.hour())
        self.hour_spin.valueChanged.connect(self.on_time_changed)
        layout.addWidget(self.hour_spin)
        
        layout.addWidget(QLabel(":"))
        
        # Minute spinbox
        self.minute_spin = QSpinBox()
        self.minute_spin.setMinimum(0)
        self.minute_spin.setMaximum(59)
        self.minute_spin.setValue(self._time.minute())
        self.minute_spin.valueChanged.connect(self.on_time_changed)
        layout.addWidget(self.minute_spin)
        
        # Second spinbox (optional)
        self.second_label = QLabel(":")
        self.second_spin = QSpinBox()
        self.second_spin.setMinimum(0)
        self.second_spin.setMaximum(59)
        self.second_spin.setValue(self._time.second())
        self.second_spin.valueChanged.connect(self.on_time_changed)
        
        layout.addWidget(self.second_label)
        layout.addWidget(self.second_spin)
        
        # AM/PM combo (for 12-hour format)
        self.ampm_combo = QComboBox()
        self.ampm_combo.addItems(["AM", "PM"])
        self.ampm_combo.currentTextChanged.connect(self.on_time_changed)
        layout.addWidget(self.ampm_combo)
        
        # Update visibility
        self.update_format()
    
    def on_time_changed(self):
        """Handle time change"""
        hour = self.hour_spin.value()
        minute = self.minute_spin.value()
        second = self.second_spin.value() if self._show_seconds else 0
        
        # Handle AM/PM conversion
        if not self._use_24_hour:
            is_pm = self.ampm_combo.currentText() == "PM"
            if hour == 12:
                hour = 0 if not is_pm else 12
            elif is_pm:
                hour += 12
        
        new_time = QTime(hour, minute, second)
        if new_time.isValid():
            self._time = new_time
            self.timeChanged.emit(new_time)
    
    def time(self) -> QTime:
        """Get current time"""
        return self._time
    
    def setTime(self, time: QTime):
        """Set current time"""
        if time.isValid():
            self._time = time
            self.update_controls()
    
    def use24HourFormat(self) -> bool:
        """Check if using 24-hour format"""
        return self._use_24_hour
    
    def setUse24HourFormat(self, use_24_hour: bool):
        """Set 24-hour format usage"""
        self._use_24_hour = use_24_hour
        self.update_format()
        self.update_controls()
    
    def showSeconds(self) -> bool:
        """Check if showing seconds"""
        return self._show_seconds
    
    def setShowSeconds(self, show_seconds: bool):
        """Set seconds visibility"""
        self._show_seconds = show_seconds
        self.update_format()
    
    def update_format(self):
        """Update format-related UI"""
        # Update hour range
        self.hour_spin.setMinimum(0 if self._use_24_hour else 1)
        self.hour_spin.setMaximum(23 if self._use_24_hour else 12)
        
        # Show/hide seconds
        self.second_label.setVisible(self._show_seconds)
        self.second_spin.setVisible(self._show_seconds)
        
        # Show/hide AM/PM
        self.ampm_combo.setVisible(not self._use_24_hour)
    
    def update_controls(self):
        """Update control values"""
        hour = self._time.hour()
        
        if self._use_24_hour:
            self.hour_spin.setValue(hour)
        else:
            # Convert to 12-hour format
            if hour == 0:
                self.hour_spin.setValue(12)
                self.ampm_combo.setCurrentText("AM")
            elif hour < 12:
                self.hour_spin.setValue(hour)
                self.ampm_combo.setCurrentText("AM")
            elif hour == 12:
                self.hour_spin.setValue(12)
                self.ampm_combo.setCurrentText("PM")
            else:
                self.hour_spin.setValue(hour - 12)
                self.ampm_combo.setCurrentText("PM")
        
        self.minute_spin.setValue(self._time.minute())
        self.second_spin.setValue(self._time.second())
    
    def apply_theme(self):
        """Apply current theme"""
        bg_color = theme_manager.get_color('surface')
        text_color = theme_manager.get_color('on_surface')
        
        self.setStyleSheet(f"""
            QSpinBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {theme_manager.get_color('outline')};
                border-radius: 6px;
                padding: 4px;
                min-width: 40px;
            }}
            QSpinBox:focus {{
                border-color: {theme_manager.get_color('primary')};
            }}
            QComboBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {theme_manager.get_color('outline')};
                border-radius: 6px;
                padding: 4px;
                min-width: 50px;
            }}
            QComboBox:focus {{
                border-color: {theme_manager.get_color('primary')};
            }}
            QLabel {{
                color: {text_color};
                font-weight: bold;
            }}
        """)


class FluentDateTimePicker(QWidget):
    """
    Combined date and time picker widget
    
    Features:
    - Date picker with calendar
    - Time picker with spinboxes
    - Combined datetime output
    - Flexible formatting
    """
    
    # Signals
    dateTimeChanged = Signal(QDateTime)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._datetime = QDateTime.currentDateTime()
        
        self.setup_ui()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def setup_ui(self):
        """Setup datetime picker UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Date picker
        self.date_picker = FluentDatePicker()
        self.date_picker.setDate(self._datetime.date())
        self.date_picker.dateChanged.connect(self.on_date_changed)
        layout.addWidget(self.date_picker)
        
        # Time picker
        self.time_picker = FluentTimePicker()
        self.time_picker.setTime(self._datetime.time())
        self.time_picker.timeChanged.connect(self.on_time_changed)
        layout.addWidget(self.time_picker)
    
    def on_date_changed(self, date: QDate):
        """Handle date change"""
        self._datetime.setDate(date)
        self.dateTimeChanged.emit(self._datetime)
    
    def on_time_changed(self, time: QTime):
        """Handle time change"""
        self._datetime.setTime(time)
        self.dateTimeChanged.emit(self._datetime)
    
    def dateTime(self) -> QDateTime:
        """Get current datetime"""
        return self._datetime
    
    def setDateTime(self, datetime: QDateTime):
        """Set current datetime"""
        if datetime.isValid():
            self._datetime = datetime
            self.date_picker.setDate(datetime.date())
            self.time_picker.setTime(datetime.time())
    
    def date(self) -> QDate:
        """Get current date"""
        return self._datetime.date()
    
    def setDate(self, date: QDate):
        """Set current date"""
        self._datetime.setDate(date)
        self.date_picker.setDate(date)
    
    def time(self) -> QTime:
        """Get current time"""
        return self._datetime.time()
    
    def setTime(self, time: QTime):
        """Set current time"""
        self._datetime.setTime(time)
        self.time_picker.setTime(time)
    
    def use24HourFormat(self) -> bool:
        """Check if using 24-hour format"""
        return self.time_picker.use24HourFormat()
    
    def setUse24HourFormat(self, use_24_hour: bool):
        """Set 24-hour format usage"""
        self.time_picker.setUse24HourFormat(use_24_hour)
    
    def showSeconds(self) -> bool:
        """Check if showing seconds"""
        return self.time_picker.showSeconds()
    
    def setShowSeconds(self, show_seconds: bool):
        """Set seconds visibility"""
        self.time_picker.setShowSeconds(show_seconds)
    
    def apply_theme(self):
        """Apply current theme"""
        # Theme is applied by child components
        pass


# Export all classes
__all__ = [
    'FluentCalendar',
    'FluentDatePicker', 
    'FluentTimePicker',
    'FluentDateTimePicker',
    'CalendarDayButton',
    'CalendarPopup'
]
