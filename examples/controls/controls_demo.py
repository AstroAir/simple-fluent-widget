"""
Comprehensive Controls Demo

This demo showcases all control components available in the simple-fluent-widget library,
including pickers, media controls, and other interactive control elements.

Features demonstrated:
- Date and time pickers with various modes
- Color and file pickers
- Range controls and selection widgets
- Media playback controls
- Interactive control configurations
"""

import sys
from datetime import datetime, date, time
from typing import Any, Dict, List, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QGroupBox,
    QScrollArea, QFrame, QSpacerItem, QSizePolicy, QMessageBox, QTabWidget,
    QSplitter, QSlider, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
    QDateEdit, QTimeEdit, QDateTimeEdit, QProgressBar, QDial, QListWidget,
    QListWidgetItem, QFileDialog, QColorDialog
)
from PySide6.QtCore import Qt, QTimer, Signal, QDate, QTime, QDateTime, QSize
from PySide6.QtGui import QColor, QPalette, QFont, QIcon, QPixmap

# Import fluent controls with fallbacks
try:
    from components.controls.picker.datetime import (
        FluentCalendar, FluentDatePicker, FluentTimePicker, FluentDateTimePicker
    )
    FLUENT_DATETIME_AVAILABLE = True
except ImportError:
    print("Warning: Fluent date/time picker components not available")
    FLUENT_DATETIME_AVAILABLE = False

try:
    from components.basic.forms.button import FluentButton
    FLUENT_BUTTON_AVAILABLE = True
except ImportError:
    FLUENT_BUTTON_AVAILABLE = False

try:
    from components.layout.containers import FluentCard
    FLUENT_CARD_AVAILABLE = True
except ImportError:
    FLUENT_CARD_AVAILABLE = False


class FallbackDateTimePicker(QWidget):
    """Fallback date/time picker when fluent components are not available."""
    
    valueChanged = Signal(object)
    
    def __init__(self, picker_type="datetime"):
        super().__init__()
        self.picker_type = picker_type
        self.current_value = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup fallback picker UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(f"Standard {self.picker_type.title()} Picker")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Control based on type
        if self.picker_type == "date":
            self.control = QDateEdit()
            self.control.setDate(QDate.currentDate())
            self.control.dateChanged.connect(self.on_value_changed)
        elif self.picker_type == "time":
            self.control = QTimeEdit()
            self.control.setTime(QTime.currentTime())
            self.control.timeChanged.connect(self.on_value_changed)
        else:  # datetime
            self.control = QDateTimeEdit()
            self.control.setDateTime(QDateTime.currentDateTime())
            self.control.dateTimeChanged.connect(self.on_value_changed)
            
        self.control.setStyleSheet("""
            QDateEdit, QTimeEdit, QDateTimeEdit {
                background-color: white;
                border: 2px solid #e1dfdd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                min-height: 20px;
            }
            QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {
                border-color: #0078d4;
            }
        """)
        
        layout.addWidget(self.control)
        
        # Value display
        self.value_label = QLabel("Current value: ")
        self.value_label.setStyleSheet("color: #605e5c; font-size: 12px;")
        layout.addWidget(self.value_label)
        
        self.on_value_changed()
        
    def on_value_changed(self):
        """Handle value change."""
        if self.picker_type == "date":
            self.current_value = self.control.date()
            self.value_label.setText(f"Current value: {self.current_value.toString()}")
        elif self.picker_type == "time":
            self.current_value = self.control.time()
            self.value_label.setText(f"Current value: {self.current_value.toString()}")
        else:
            self.current_value = self.control.dateTime()
            self.value_label.setText(f"Current value: {self.current_value.toString()}")
            
        self.valueChanged.emit(self.current_value)
        
    def getValue(self):
        """Get current value."""
        return self.current_value


class FallbackCalendar(QWidget):
    """Fallback calendar when fluent components are not available."""
    
    dateChanged = Signal(QDate)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup fallback calendar UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Standard Calendar")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Calendar widget
        from PySide6.QtWidgets import QCalendarWidget
        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 2px solid #e1dfdd;
                border-radius: 4px;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #f3f2f1;
            }
            QCalendarWidget QToolButton {
                color: #323130;
                background-color: transparent;
                border: none;
                padding: 4px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #e1dfdd;
                border-radius: 2px;
            }
        """)
        
        self.calendar.clicked.connect(self.on_date_clicked)
        layout.addWidget(self.calendar)
        
        # Selected date display
        self.date_label = QLabel(f"Selected: {self.calendar.selectedDate().toString()}")
        self.date_label.setStyleSheet("color: #605e5c; font-size: 12px;")
        layout.addWidget(self.date_label)
        
    def on_date_clicked(self, date):
        """Handle date selection."""
        self.date_label.setText(f"Selected: {date.toString()}")
        self.dateChanged.emit(date)


class FallbackColorPicker(QWidget):
    """Fallback color picker when fluent components are not available."""
    
    colorChanged = Signal(QColor)
    
    def __init__(self):
        super().__init__()
        self.current_color = QColor(0, 120, 212)  # Fluent blue
        self.setup_ui()
        
    def setup_ui(self):
        """Setup fallback color picker UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Standard Color Picker")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Color display
        self.color_display = QFrame()
        self.color_display.setFixedHeight(40)
        self.color_display.setStyleSheet(f"""
            QFrame {{
                background-color: {self.current_color.name()};
                border: 2px solid #e1dfdd;
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.color_display)
        
        # Pick color button
        pick_button = QPushButton("Pick Color")
        pick_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        pick_button.clicked.connect(self.pick_color)
        layout.addWidget(pick_button)
        
        # Color info
        self.color_label = QLabel(f"RGB: {self.current_color.name()}")
        self.color_label.setStyleSheet("color: #605e5c; font-size: 12px;")
        layout.addWidget(self.color_label)
        
    def pick_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(self.current_color, self, "Select Color")
        if color.isValid():
            self.current_color = color
            self.color_display.setStyleSheet(f"""
                QFrame {{
                    background-color: {color.name()};
                    border: 2px solid #e1dfdd;
                    border-radius: 4px;
                }}
            """)
            self.color_label.setText(f"RGB: {color.name()}")
            self.colorChanged.emit(color)


class FallbackMediaControls(QWidget):
    """Fallback media controls when fluent components are not available."""
    
    playbackChanged = Signal(str)  # play, pause, stop
    positionChanged = Signal(int)
    volumeChanged = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.is_playing = False
        self.position = 0
        self.volume = 50
        self.duration = 100
        self.setup_ui()
        
    def setup_ui(self):
        """Setup fallback media controls UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Media Controls")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(40, 40)
        self.play_button.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.play_button)
        
        stop_button = QPushButton("⏹")
        stop_button.setFixedSize(40, 40)
        stop_button.clicked.connect(self.stop)
        controls_layout.addWidget(stop_button)
        
        layout.addLayout(controls_layout)
        
        # Progress bar
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("00:00"))
        
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, self.duration)
        self.progress_slider.setValue(self.position)
        self.progress_slider.valueChanged.connect(self.set_position)
        progress_layout.addWidget(self.progress_slider)
        
        progress_layout.addWidget(QLabel("01:40"))
        layout.addLayout(progress_layout)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("🔊"))
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.volume)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel(f"{self.volume}%")
        volume_layout.addWidget(self.volume_label)
        layout.addLayout(volume_layout)
        
        # Style buttons
        button_style = """
            QPushButton {
                background-color: #f3f2f1;
                border: 1px solid #e1dfdd;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e1dfdd;
            }
            QPushButton:pressed {
                background-color: #d2d0ce;
            }
        """
        self.play_button.setStyleSheet(button_style)
        stop_button.setStyleSheet(button_style)
        
    def toggle_play(self):
        """Toggle play/pause."""
        self.is_playing = not self.is_playing
        self.play_button.setText("⏸" if self.is_playing else "▶")
        self.playbackChanged.emit("play" if self.is_playing else "pause")
        
    def stop(self):
        """Stop playback."""
        self.is_playing = False
        self.play_button.setText("▶")
        self.position = 0
        self.progress_slider.setValue(0)
        self.playbackChanged.emit("stop")
        
    def set_position(self, position):
        """Set playback position."""
        self.position = position
        self.positionChanged.emit(position)
        
    def set_volume(self, volume):
        """Set volume level."""
        self.volume = volume
        self.volume_label.setText(f"{volume}%")
        self.volumeChanged.emit(volume)


class ControlsDemo(QMainWindow):
    """Main demo window showcasing control components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controls Demo - simple-fluent-widget")
        self.setGeometry(100, 100, 1400, 900)
        
        # Demo state
        self.selected_date = QDate.currentDate()
        self.selected_time = QTime.currentTime()
        self.selected_color = QColor(0, 120, 212)
        
        self.setup_ui()
        self.setup_interactions()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Controls Components Demo")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #323130; margin: 20px;")
        layout.addWidget(title)
        
        # Create tab widget for different control categories
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e1dfdd;
                background-color: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #f3f2f1;
                border: 1px solid #e1dfdd;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background-color: #e1dfdd;
            }
        """)
        
        # Add tabs
        self.tab_widget.addTab(self.create_datetime_tab(), "Date & Time")
        self.tab_widget.addTab(self.create_color_tab(), "Color & Selection")
        self.tab_widget.addTab(self.create_range_tab(), "Range Controls")
        self.tab_widget.addTab(self.create_media_tab(), "Media Controls")
        self.tab_widget.addTab(self.create_interactive_tab(), "Interactive")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.statusBar().showMessage("Controls Demo - Explore different control components")
        
    def create_datetime_tab(self):
        """Create date and time controls tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        
        # Calendar widget
        calendar_group = QGroupBox("Calendar")
        calendar_layout = QVBoxLayout(calendar_group)
        
        if FLUENT_DATETIME_AVAILABLE:
            try:
                self.calendar = FluentCalendar()
                self.calendar.dateChanged.connect(self.on_date_selected)
            except Exception as e:
                print(f"Error creating FluentCalendar: {e}")
                self.calendar = FallbackCalendar()
                self.calendar.dateChanged.connect(self.on_date_selected)
        else:
            self.calendar = FallbackCalendar()
            self.calendar.dateChanged.connect(self.on_date_selected)
            
        calendar_layout.addWidget(self.calendar)
        scroll_layout.addWidget(calendar_group, 0, 0, 2, 1)
        
        # Date picker
        date_group = QGroupBox("Date Picker")
        date_layout = QVBoxLayout(date_group)
        
        if FLUENT_DATETIME_AVAILABLE:
            try:
                self.date_picker = FluentDatePicker()
                self.date_picker.valueChanged.connect(self.on_date_changed)
            except Exception as e:
                print(f"Error creating FluentDatePicker: {e}")
                self.date_picker = FallbackDateTimePicker("date")
                self.date_picker.valueChanged.connect(self.on_date_changed)
        else:
            self.date_picker = FallbackDateTimePicker("date")
            self.date_picker.valueChanged.connect(self.on_date_changed)
            
        date_layout.addWidget(self.date_picker)
        scroll_layout.addWidget(date_group, 0, 1)
        
        # Time picker
        time_group = QGroupBox("Time Picker")
        time_layout = QVBoxLayout(time_group)
        
        if FLUENT_DATETIME_AVAILABLE:
            try:
                self.time_picker = FluentTimePicker()
                self.time_picker.valueChanged.connect(self.on_time_changed)
            except Exception as e:
                print(f"Error creating FluentTimePicker: {e}")
                self.time_picker = FallbackDateTimePicker("time")
                self.time_picker.valueChanged.connect(self.on_time_changed)
        else:
            self.time_picker = FallbackDateTimePicker("time")
            self.time_picker.valueChanged.connect(self.on_time_changed)
            
        time_layout.addWidget(self.time_picker)
        scroll_layout.addWidget(time_group, 1, 1)
        
        # DateTime picker
        datetime_group = QGroupBox("DateTime Picker")
        datetime_layout = QVBoxLayout(datetime_group)
        
        if FLUENT_DATETIME_AVAILABLE:
            try:
                self.datetime_picker = FluentDateTimePicker()
                self.datetime_picker.valueChanged.connect(self.on_datetime_changed)
            except Exception as e:
                print(f"Error creating FluentDateTimePicker: {e}")
                self.datetime_picker = FallbackDateTimePicker("datetime")
                self.datetime_picker.valueChanged.connect(self.on_datetime_changed)
        else:
            self.datetime_picker = FallbackDateTimePicker("datetime")
            self.datetime_picker.valueChanged.connect(self.on_datetime_changed)
            
        datetime_layout.addWidget(self.datetime_picker)
        scroll_layout.addWidget(datetime_group, 0, 2, 2, 1)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return tab
        
    def create_color_tab(self):
        """Create color and selection controls tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        
        # Color picker
        color_group = QGroupBox("Color Picker")
        color_layout = QVBoxLayout(color_group)
        
        self.color_picker = FallbackColorPicker()
        self.color_picker.colorChanged.connect(self.on_color_changed)
        color_layout.addWidget(self.color_picker)
        scroll_layout.addWidget(color_group, 0, 0)
        
        # File picker simulation
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        file_button = QPushButton("Select File")
        file_button.clicked.connect(self.select_file)
        file_layout.addWidget(file_button)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #605e5c; font-size: 12px;")
        file_layout.addWidget(self.file_label)
        
        scroll_layout.addWidget(file_group, 0, 1)
        
        # Combo box selection
        combo_group = QGroupBox("Dropdown Selection")
        combo_layout = QVBoxLayout(combo_group)
        
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Option 1", "Option 2", "Option 3", "Custom Option"])
        self.combo_box.currentTextChanged.connect(self.on_combo_changed)
        self.combo_box.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 2px solid #e1dfdd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox:focus {
                border-color: #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #605e5c;
            }
        """)
        combo_layout.addWidget(self.combo_box)
        
        self.combo_label = QLabel(f"Selected: {self.combo_box.currentText()}")
        self.combo_label.setStyleSheet("color: #605e5c; font-size: 12px;")
        combo_layout.addWidget(self.combo_label)
        
        scroll_layout.addWidget(combo_group, 1, 0)
        
        # List selection
        list_group = QGroupBox("List Selection")
        list_layout = QVBoxLayout(list_group)
        
        self.list_widget = QListWidget()
        self.list_widget.setMaximumHeight(150)
        for i in range(5):
            item = QListWidgetItem(f"List Item {i+1}")
            self.list_widget.addItem(item)
        
        self.list_widget.itemClicked.connect(self.on_list_item_clicked)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 2px solid #e1dfdd;
                border-radius: 4px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f3f2f1;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-left: 3px solid #0078d4;
            }
            QListWidget::item:hover {
                background-color: #f3f2f1;
            }
        """)
        list_layout.addWidget(self.list_widget)
        
        self.list_label = QLabel("No item selected")
        self.list_label.setStyleSheet("color: #605e5c; font-size: 12px;")
        list_layout.addWidget(self.list_label)
        
        scroll_layout.addWidget(list_group, 1, 1)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return tab
        
    def create_range_tab(self):
        """Create range and numeric controls tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        
        # Slider controls
        slider_group = QGroupBox("Slider Controls")
        slider_layout = QVBoxLayout(slider_group)
        
        # Horizontal slider
        h_slider_layout = QHBoxLayout()
        h_slider_layout.addWidget(QLabel("Horizontal:"))
        self.h_slider = QSlider(Qt.Orientation.Horizontal)
        self.h_slider.setRange(0, 100)
        self.h_slider.setValue(50)
        self.h_slider.valueChanged.connect(self.on_h_slider_changed)
        h_slider_layout.addWidget(self.h_slider)
        self.h_slider_label = QLabel("50")
        h_slider_layout.addWidget(self.h_slider_label)
        slider_layout.addLayout(h_slider_layout)
        
        # Vertical slider
        v_slider_layout = QHBoxLayout()
        v_slider_layout.addWidget(QLabel("Vertical:"))
        self.v_slider = QSlider(Qt.Orientation.Vertical)
        self.v_slider.setRange(0, 100)
        self.v_slider.setValue(25)
        self.v_slider.setFixedHeight(100)
        self.v_slider.valueChanged.connect(self.on_v_slider_changed)
        v_slider_layout.addWidget(self.v_slider)
        self.v_slider_label = QLabel("25")
        v_slider_layout.addWidget(self.v_slider_label)
        v_slider_layout.addStretch()
        slider_layout.addLayout(v_slider_layout)
        
        scroll_layout.addWidget(slider_group, 0, 0)
        
        # Spin box controls
        spin_group = QGroupBox("Numeric Input")
        spin_layout = QVBoxLayout(spin_group)
        
        # Integer spin box
        int_layout = QHBoxLayout()
        int_layout.addWidget(QLabel("Integer:"))
        self.int_spin = QSpinBox()
        self.int_spin.setRange(-100, 100)
        self.int_spin.setValue(0)
        self.int_spin.valueChanged.connect(self.on_int_spin_changed)
        int_layout.addWidget(self.int_spin)
        self.int_spin_label = QLabel("0")
        int_layout.addWidget(self.int_spin_label)
        spin_layout.addLayout(int_layout)
        
        # Double spin box
        double_layout = QHBoxLayout()
        double_layout.addWidget(QLabel("Decimal:"))
        self.double_spin = QDoubleSpinBox()
        self.double_spin.setRange(-10.0, 10.0)
        self.double_spin.setValue(0.0)
        self.double_spin.setDecimals(2)
        self.double_spin.setSingleStep(0.1)
        self.double_spin.valueChanged.connect(self.on_double_spin_changed)
        double_layout.addWidget(self.double_spin)
        self.double_spin_label = QLabel("0.00")
        double_layout.addWidget(self.double_spin_label)
        spin_layout.addLayout(double_layout)
        
        scroll_layout.addWidget(spin_group, 0, 1)
        
        # Dial control
        dial_group = QGroupBox("Dial Control")
        dial_layout = QVBoxLayout(dial_group)
        
        self.dial = QDial()
        self.dial.setRange(0, 360)
        self.dial.setValue(180)
        self.dial.valueChanged.connect(self.on_dial_changed)
        dial_layout.addWidget(self.dial)
        
        self.dial_label = QLabel("180°")
        self.dial_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dial_layout.addWidget(self.dial_label)
        
        scroll_layout.addWidget(dial_group, 1, 0)
        
        # Progress indicators
        progress_group = QGroupBox("Progress Indicators")
        progress_layout = QVBoxLayout(progress_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(70)
        progress_layout.addWidget(QLabel("Progress Bar:"))
        progress_layout.addWidget(self.progress_bar)
        
        # Progress control
        progress_control_layout = QHBoxLayout()
        progress_btn_minus = QPushButton("-10")
        progress_btn_minus.clicked.connect(lambda: self.change_progress(-10))
        progress_control_layout.addWidget(progress_btn_minus)
        
        progress_btn_plus = QPushButton("+10")
        progress_btn_plus.clicked.connect(lambda: self.change_progress(10))
        progress_control_layout.addWidget(progress_btn_plus)
        
        progress_layout.addLayout(progress_control_layout)
        
        scroll_layout.addWidget(progress_group, 1, 1)
        
        # Style all controls
        control_style = """
            QSlider::groove:horizontal {
                background: #e1dfdd;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: none;
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::groove:vertical {
                background: #e1dfdd;
                width: 4px;
                border-radius: 2px;
            }
            QSlider::handle:vertical {
                background: #0078d4;
                border: none;
                height: 16px;
                margin: 0 -6px;
                border-radius: 8px;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: white;
                border: 2px solid #e1dfdd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                min-height: 20px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #0078d4;
            }
            QDial {
                background-color: #f3f2f1;
                border: 2px solid #e1dfdd;
                border-radius: 50px;
            }
            QProgressBar {
                background-color: #e1dfdd;
                border: none;
                border-radius: 8px;
                height: 16px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 8px;
            }
        """
        
        for widget in [self.h_slider, self.v_slider, self.int_spin, self.double_spin, 
                      self.dial, self.progress_bar]:
            widget.setStyleSheet(control_style)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return tab
        
    def create_media_tab(self):
        """Create media controls tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Media player controls
        media_group = QGroupBox("Media Player")
        media_layout = QVBoxLayout(media_group)
        
        self.media_controls = FallbackMediaControls()
        self.media_controls.playbackChanged.connect(self.on_playback_changed)
        self.media_controls.positionChanged.connect(self.on_position_changed)
        self.media_controls.volumeChanged.connect(self.on_volume_changed)
        media_layout.addWidget(self.media_controls)
        
        scroll_layout.addWidget(media_group)
        
        # Media information
        info_group = QGroupBox("Media Information")
        info_layout = QVBoxLayout(info_group)
        
        self.media_info = QLabel("Sample Track\nArtist: Demo Artist\nAlbum: Demo Album\nDuration: 1:40")
        self.media_info.setStyleSheet("""
            QLabel {
                background-color: #f3f2f1;
                border: 1px solid #e1dfdd;
                border-radius: 4px;
                padding: 16px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        info_layout.addWidget(self.media_info)
        
        scroll_layout.addWidget(info_group)
        
        # Media status
        status_group = QGroupBox("Playback Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Status: Stopped")
        self.position_label = QLabel("Position: 0:00")
        self.volume_status_label = QLabel("Volume: 50%")
        
        for label in [self.status_label, self.position_label, self.volume_status_label]:
            label.setStyleSheet("color: #605e5c; font-size: 14px; margin: 4px;")
            status_layout.addWidget(label)
            
        scroll_layout.addWidget(status_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return tab
        
    def create_interactive_tab(self):
        """Create interactive controls demonstration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Interactive controls
        interactive_group = QGroupBox("Interactive Controls")
        interactive_layout = QGridLayout(interactive_group)
        
        # Checkboxes
        checkbox_layout = QVBoxLayout()
        checkbox_layout.addWidget(QLabel("Options:"))
        
        self.checkbox1 = QCheckBox("Enable notifications")
        self.checkbox1.setChecked(True)
        self.checkbox1.stateChanged.connect(self.on_checkbox_changed)
        checkbox_layout.addWidget(self.checkbox1)
        
        self.checkbox2 = QCheckBox("Auto-save")
        self.checkbox2.stateChanged.connect(self.on_checkbox_changed)
        checkbox_layout.addWidget(self.checkbox2)
        
        self.checkbox3 = QCheckBox("Dark mode")
        self.checkbox3.stateChanged.connect(self.on_checkbox_changed)
        checkbox_layout.addWidget(self.checkbox3)
        
        interactive_layout.addLayout(checkbox_layout, 0, 0)
        
        # Buttons demonstration
        button_layout = QVBoxLayout()
        button_layout.addWidget(QLabel("Actions:"))
        
        if FLUENT_BUTTON_AVAILABLE:
            try:
                action_btn = FluentButton("Fluent Action")
            except:
                action_btn = QPushButton("Standard Action")
        else:
            action_btn = QPushButton("Standard Action")
            
        action_btn.clicked.connect(self.perform_action)
        button_layout.addWidget(action_btn)
        
        reset_btn = QPushButton("Reset All")
        reset_btn.clicked.connect(self.reset_all_controls)
        button_layout.addWidget(reset_btn)
        
        info_btn = QPushButton("Show Info")
        info_btn.clicked.connect(self.show_control_info)
        button_layout.addWidget(info_btn)
        
        interactive_layout.addLayout(button_layout, 0, 1)
        
        scroll_layout.addWidget(interactive_group)
        
        # Control state display
        state_group = QGroupBox("Control States")
        state_layout = QVBoxLayout(state_group)
        
        self.state_display = QTextEdit()
        self.state_display.setMaximumHeight(200)
        self.state_display.setReadOnly(True)
        self.state_display.setPlainText("Control states will be displayed here...")
        self.state_display.setStyleSheet("""
            QTextEdit {
                background-color: #f3f2f1;
                border: 1px solid #e1dfdd;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                padding: 8px;
            }
        """)
        state_layout.addWidget(self.state_display)
        
        scroll_layout.addWidget(state_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return tab
        
    def setup_interactions(self):
        """Set up component interactions and demonstrations."""
        # Timer for updating states
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_control_states)
        self.update_timer.start(1000)  # Update every second
        
    # Event handlers
    def on_date_selected(self, date):
        """Handle date selection."""
        self.selected_date = date
        self.statusBar().showMessage(f"Date selected: {date.toString()}")
        
    def on_date_changed(self, date):
        """Handle date picker change."""
        self.selected_date = date
        self.statusBar().showMessage(f"Date changed: {date}")
        
    def on_time_changed(self, time):
        """Handle time picker change."""
        self.selected_time = time
        self.statusBar().showMessage(f"Time changed: {time}")
        
    def on_datetime_changed(self, datetime):
        """Handle datetime picker change."""
        self.statusBar().showMessage(f"DateTime changed: {datetime}")
        
    def on_color_changed(self, color):
        """Handle color picker change."""
        self.selected_color = color
        self.statusBar().showMessage(f"Color changed: {color.name()}")
        
    def select_file(self):
        """Handle file selection."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
        if file_path:
            import os
            filename = os.path.basename(file_path)
            self.file_label.setText(f"Selected: {filename}")
            self.statusBar().showMessage(f"File selected: {filename}")
        
    def on_combo_changed(self, text):
        """Handle combo box change."""
        self.combo_label.setText(f"Selected: {text}")
        self.statusBar().showMessage(f"Combo selection: {text}")
        
    def on_list_item_clicked(self, item):
        """Handle list item click."""
        self.list_label.setText(f"Selected: {item.text()}")
        self.statusBar().showMessage(f"List selection: {item.text()}")
        
    def on_h_slider_changed(self, value):
        """Handle horizontal slider change."""
        self.h_slider_label.setText(str(value))
        
    def on_v_slider_changed(self, value):
        """Handle vertical slider change."""
        self.v_slider_label.setText(str(value))
        
    def on_int_spin_changed(self, value):
        """Handle integer spin box change."""
        self.int_spin_label.setText(str(value))
        
    def on_double_spin_changed(self, value):
        """Handle double spin box change."""
        self.double_spin_label.setText(f"{value:.2f}")
        
    def on_dial_changed(self, value):
        """Handle dial change."""
        self.dial_label.setText(f"{value}°")
        
    def change_progress(self, delta):
        """Change progress bar value."""
        new_value = max(0, min(100, self.progress_bar.value() + delta))
        self.progress_bar.setValue(new_value)
        
    def on_playback_changed(self, state):
        """Handle media playback change."""
        self.status_label.setText(f"Status: {state.title()}")
        
    def on_position_changed(self, position):
        """Handle media position change."""
        minutes = position // 60
        seconds = position % 60
        self.position_label.setText(f"Position: {minutes}:{seconds:02d}")
        
    def on_volume_changed(self, volume):
        """Handle volume change."""
        self.volume_status_label.setText(f"Volume: {volume}%")
        
    def on_checkbox_changed(self):
        """Handle checkbox state change."""
        states = []
        if self.checkbox1.isChecked():
            states.append("Notifications enabled")
        if self.checkbox2.isChecked():
            states.append("Auto-save enabled")
        if self.checkbox3.isChecked():
            states.append("Dark mode enabled")
            
        self.statusBar().showMessage(f"Options: {', '.join(states) if states else 'None'}")
        
    def perform_action(self):
        """Perform demo action."""
        QMessageBox.information(self, "Action", "Demo action performed successfully!")
        
    def reset_all_controls(self):
        """Reset all controls to default values."""
        # Reset sliders
        self.h_slider.setValue(50)
        self.v_slider.setValue(25)
        
        # Reset spin boxes
        self.int_spin.setValue(0)
        self.double_spin.setValue(0.0)
        
        # Reset dial
        self.dial.setValue(180)
        
        # Reset progress
        self.progress_bar.setValue(70)
        
        # Reset checkboxes
        self.checkbox1.setChecked(True)
        self.checkbox2.setChecked(False)
        self.checkbox3.setChecked(False)
        
        self.statusBar().showMessage("All controls reset to defaults")
        
    def show_control_info(self):
        """Show information about current control states."""
        info = f"""
Control States Summary:

Date & Time:
- Selected Date: {self.selected_date.toString()}
- Selected Time: {self.selected_time.toString()}
- Selected Color: {self.selected_color.name()}

Range Controls:
- Horizontal Slider: {self.h_slider.value()}
- Vertical Slider: {self.v_slider.value()}
- Integer Spin: {self.int_spin.value()}
- Double Spin: {self.double_spin.value():.2f}
- Dial: {self.dial.value()}°
- Progress: {self.progress_bar.value()}%

Interactive:
- Notifications: {'Enabled' if self.checkbox1.isChecked() else 'Disabled'}
- Auto-save: {'Enabled' if self.checkbox2.isChecked() else 'Disabled'}
- Dark mode: {'Enabled' if self.checkbox3.isChecked() else 'Disabled'}

Media:
- Volume: {self.media_controls.volume}%
- Position: {self.media_controls.position}
- Playing: {'Yes' if self.media_controls.is_playing else 'No'}
        """
        
        QMessageBox.information(self, "Control Information", info.strip())
        
    def update_control_states(self):
        """Update control states display."""
        states = {
            "DateTime": {
                "date": self.selected_date.toString(),
                "time": self.selected_time.toString(),
                "color": self.selected_color.name()
            },
            "Range": {
                "h_slider": self.h_slider.value(),
                "v_slider": self.v_slider.value(),
                "int_spin": self.int_spin.value(),
                "double_spin": self.double_spin.value(),
                "dial": self.dial.value(),
                "progress": self.progress_bar.value()
            },
            "Interactive": {
                "notifications": self.checkbox1.isChecked(),
                "autosave": self.checkbox2.isChecked(),
                "darkmode": self.checkbox3.isChecked()
            },
            "Media": {
                "volume": self.media_controls.volume,
                "position": self.media_controls.position,
                "playing": self.media_controls.is_playing
            }
        }
        
        import json
        self.state_display.setPlainText(json.dumps(states, indent=2))


def main():
    """Main function to run the controls demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Controls Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("simple-fluent-widget")
    
    # Create and show demo
    demo = ControlsDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
