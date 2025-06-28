"""
Fluent Design Style Date Time Picker Components with Enhanced Animations
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QCalendarWidget, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, Signal, QDate, QTime, QDateTime, QTimer
from PySide6.QtGui import QFont
from core.theme import theme_manager
from core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                      FluentRevealEffect, FluentSequence, FluentStateTransition)
from core.animation import FluentAnimation
from components.basic.forms.button import FluentButton
from typing import Optional


class FluentCalendar(QCalendarWidget):
    """**Fluent Design Style Calendar with Enhanced Animations**"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._setup_animations()
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animations(self):
        """Setup enhanced animation system"""
        # Setup state transitions for calendar
        self._state_transition = FluentStateTransition(self)

        # Define calendar states
        self._state_transition.addState("normal", {
            "minimumWidth": 300,
            "minimumHeight": 200,
        })

        self._state_transition.addState("expanded", {
            "minimumWidth": 320,
            "minimumHeight": 220,
        }, duration=200, easing=FluentTransition.EASE_SPRING)

        # Entrance animation with delay
        QTimer.singleShot(100, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation with enhanced effects"""
        entrance_sequence = FluentSequence(self)

        # Fade in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self, 400))
        entrance_sequence.addPause(150)

        # Scale in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.scale_in(self, 300))

        entrance_sequence.start()

    def showEvent(self, event):
        """Enhanced show event with animation"""
        super().showEvent(event)

        # Apply subtle entrance animation if not already shown
        if not hasattr(self, '_animation_shown'):
            self._animation_shown = True
            FluentRevealEffect.slide_in(self, 250, "up")

    def enterEvent(self, event):
        """Enhanced hover effect"""
        super().enterEvent(event)
        if self.isEnabled():
            self._state_transition.transitionTo("expanded")
            FluentMicroInteraction.hover_glow(self, intensity=0.1)

    def leaveEvent(self, event):
        """Enhanced leave effect"""
        super().leaveEvent(event)
        if self.isEnabled():
            self._state_transition.transitionTo("normal")

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QCalendarWidget {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
            }}
            QCalendarWidget QAbstractItemView {{
                background-color: transparent;
                border: none;
                selection-background-color: {theme.get_color('primary').name()};
                selection-color: white;
                alternate-background-color: {theme.get_color('accent_light').name()};
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                color: {theme.get_color('text_primary').name()};
            }}
            QCalendarWidget QWidget {{
                alternate-background-color: {theme.get_color('surface').name()};
            }}
            QCalendarWidget QToolButton {{
                background-color: transparent;
                color: {theme.get_color('text_primary').name()};
                border: none;
                border-radius: 4px;
                padding: 4px;
                margin: 2px;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QCalendarWidget QToolButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QCalendarWidget QSpinBox {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 4px;
                color: {theme.get_color('text_primary').name()};
            }}
            QCalendarWidget QMenu {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, theme_name: str):
        """Theme change handler"""
        # Suppress unused parameter warning
        _ = theme_name
        self._setup_style()


class FluentTimePicker(QWidget):
    """**Fluent Design Style Time Picker with Enhanced Animations**"""

    time_changed = Signal(QTime)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._current_time = QTime.currentTime()
        self._setup_animations()
        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animations(self):
        """Setup enhanced animation system"""
        # Setup state transitions for time picker
        self._state_transition = FluentStateTransition(self)

        self._state_transition.addState("normal", {
            "minimumHeight": 200,
        })

        self._state_transition.addState("focused", {
            "minimumHeight": 210,
        }, duration=200, easing=FluentTransition.EASE_SMOOTH)

        # Entrance animation
        QTimer.singleShot(150, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation with enhanced effects"""
        entrance_sequence = FluentSequence(self)

        # Slide in from bottom
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.slide_in(self, 350, "down"))
        entrance_sequence.addPause(100)

        # Subtle pulse effect
        entrance_sequence.addCallback(
            lambda: FluentMicroInteraction.pulse_animation(self, 1.02))

        entrance_sequence.start()

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Time display
        self.time_display = QLabel()
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_display.setFont(QFont("", 24, QFont.Weight.Bold))

        # Time control area
        control_layout = QHBoxLayout()

        # Hour control
        hour_layout = QVBoxLayout()
        hour_layout.setSpacing(8)

        self.hour_up_btn = QPushButton("▲")
        self.hour_up_btn.setFixedSize(32, 24)
        self.hour_up_btn.clicked.connect(self._increase_hour)
        # Add micro-interaction for button press
        self.hour_up_btn.mousePressEvent = lambda e: self._handle_button_press(
            self.hour_up_btn, e)

        self.hour_label = QLabel("00")
        self.hour_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hour_label.setFont(QFont("", 18, QFont.Weight.Bold))

        self.hour_down_btn = QPushButton("▼")
        self.hour_down_btn.setFixedSize(32, 24)
        self.hour_down_btn.clicked.connect(self._decrease_hour)
        self.hour_down_btn.mousePressEvent = lambda e: self._handle_button_press(
            self.hour_down_btn, e)

        hour_layout.addWidget(self.hour_up_btn)
        hour_layout.addWidget(self.hour_label)
        hour_layout.addWidget(self.hour_down_btn)

        # Minute control
        minute_layout = QVBoxLayout()
        minute_layout.setSpacing(8)

        self.minute_up_btn = QPushButton("▲")
        self.minute_up_btn.setFixedSize(32, 24)
        self.minute_up_btn.clicked.connect(self._increase_minute)
        self.minute_up_btn.mousePressEvent = lambda e: self._handle_button_press(
            self.minute_up_btn, e)

        self.minute_label = QLabel("00")
        self.minute_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minute_label.setFont(QFont("", 18, QFont.Weight.Bold))

        self.minute_down_btn = QPushButton("▼")
        self.minute_down_btn.setFixedSize(32, 24)
        self.minute_down_btn.clicked.connect(self._decrease_minute)
        self.minute_down_btn.mousePressEvent = lambda e: self._handle_button_press(
            self.minute_down_btn, e)

        minute_layout.addWidget(self.minute_up_btn)
        minute_layout.addWidget(self.minute_label)
        minute_layout.addWidget(self.minute_down_btn)

        # Second control
        second_layout = QVBoxLayout()
        second_layout.setSpacing(8)

        self.second_up_btn = QPushButton("▲")
        self.second_up_btn.setFixedSize(32, 24)
        self.second_up_btn.clicked.connect(self._increase_second)
        self.second_up_btn.mousePressEvent = lambda e: self._handle_button_press(
            self.second_up_btn, e)

        self.second_label = QLabel("00")
        self.second_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.second_label.setFont(QFont("", 18, QFont.Weight.Bold))

        self.second_down_btn = QPushButton("▼")
        self.second_down_btn.setFixedSize(32, 24)
        self.second_down_btn.clicked.connect(self._decrease_second)
        self.second_down_btn.mousePressEvent = lambda e: self._handle_button_press(
            self.second_down_btn, e)

        second_layout.addWidget(self.second_up_btn)
        second_layout.addWidget(self.second_label)
        second_layout.addWidget(self.second_down_btn)

        # Separators
        colon1 = QLabel(":")
        colon1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        colon1.setFont(QFont("", 18, QFont.Weight.Bold))

        colon2 = QLabel(":")
        colon2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        colon2.setFont(QFont("", 18, QFont.Weight.Bold))

        control_layout.addStretch()
        control_layout.addLayout(hour_layout)
        control_layout.addWidget(colon1)
        control_layout.addLayout(minute_layout)
        control_layout.addWidget(colon2)
        control_layout.addLayout(second_layout)
        control_layout.addStretch()

        layout.addWidget(self.time_display)
        layout.addLayout(control_layout)

        self._update_display()

    def _handle_button_press(self, button, event):
        """Handle button press with micro-interaction"""
        # Call original mouse press event
        QPushButton.mousePressEvent(button, event)
        # Add micro-interaction
        FluentMicroInteraction.button_press(button, scale=0.92)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentTimePicker {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
            }}
            QPushButton {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                color: {theme.get_color('text_primary').name()};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('primary').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _animate_value_change(self, label: QLabel, new_value: str):
        """Animate value change with enhanced effects"""
        # Create quick pulse animation for value change feedback
        FluentMicroInteraction.pulse_animation(label, scale=1.1)

        # Update the label text
        label.setText(new_value)

    def _increase_hour(self):
        """Increase hour with animation"""
        hour = self._current_time.hour()
        hour = (hour + 1) % 24
        self._current_time = QTime(
            hour, self._current_time.minute(), self._current_time.second())
        self._update_display()
        self._animate_value_change(self.hour_label, f"{hour:02d}")
        self.time_changed.emit(self._current_time)

    def _decrease_hour(self):
        """Decrease hour with animation"""
        hour = self._current_time.hour()
        hour = (hour - 1) % 24
        self._current_time = QTime(
            hour, self._current_time.minute(), self._current_time.second())
        self._update_display()
        self._animate_value_change(self.hour_label, f"{hour:02d}")
        self.time_changed.emit(self._current_time)

    def _increase_minute(self):
        """Increase minute with animation"""
        minute = self._current_time.minute()
        minute = (minute + 1) % 60
        self._current_time = QTime(
            self._current_time.hour(), minute, self._current_time.second())
        self._update_display()
        self._animate_value_change(self.minute_label, f"{minute:02d}")
        self.time_changed.emit(self._current_time)

    def _decrease_minute(self):
        """Decrease minute with animation"""
        minute = self._current_time.minute()
        minute = (minute - 1) % 60
        self._current_time = QTime(
            self._current_time.hour(), minute, self._current_time.second())
        self._update_display()
        self._animate_value_change(self.minute_label, f"{minute:02d}")
        self.time_changed.emit(self._current_time)

    def _increase_second(self):
        """Increase second with animation"""
        second = self._current_time.second()
        second = (second + 1) % 60
        self._current_time = QTime(
            self._current_time.hour(), self._current_time.minute(), second)
        self._update_display()
        self._animate_value_change(self.second_label, f"{second:02d}")
        self.time_changed.emit(self._current_time)

    def _decrease_second(self):
        """Decrease second with animation"""
        second = self._current_time.second()
        second = (second - 1) % 60
        self._current_time = QTime(
            self._current_time.hour(), self._current_time.minute(), second)
        self._update_display()
        self._animate_value_change(self.second_label, f"{second:02d}")
        self.time_changed.emit(self._current_time)

    def _update_display(self):
        """Update display"""
        self.time_display.setText(self._current_time.toString("hh:mm:ss"))
        self.hour_label.setText(f"{self._current_time.hour():02d}")
        self.minute_label.setText(f"{self._current_time.minute():02d}")
        self.second_label.setText(f"{self._current_time.second():02d}")

    def showEvent(self, event):
        """Enhanced show event with animation"""
        super().showEvent(event)
        self._state_transition.transitionTo("focused")

    def hideEvent(self, event):
        """Enhanced hide event"""
        super().hideEvent(event)
        self._state_transition.transitionTo("normal")

    def set_time(self, time: QTime):
        """**Set time with smooth animation**"""
        self._current_time = time
        self._update_display()
        # Add subtle animation for time change
        FluentMicroInteraction.pulse_animation(self.time_display, scale=1.05)

    def get_time(self) -> QTime:
        """**Get time**"""
        return self._current_time

    def _on_theme_changed(self, theme_name: str):
        """Theme change handler"""
        # Suppress unused parameter warning
        _ = theme_name
        self._setup_style()


class FluentDateTimePicker(QWidget):
    """**Fluent Design Style DateTime Picker with Enhanced Animations**"""

    datetime_changed = Signal(QDateTime)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._current_datetime = QDateTime.currentDateTime()
        self._setup_animations()
        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animations(self):
        """Setup enhanced animation system"""
        # Setup state transitions
        self._state_transition = FluentStateTransition(self)

        self._state_transition.addState("normal", {
            "minimumWidth": 350,
            "minimumHeight": 400,
        })

        self._state_transition.addState("expanded", {
            "minimumWidth": 370,
            "minimumHeight": 420,
        }, duration=250, easing=FluentTransition.EASE_SPRING)

        # Tab transition animation
        self._tab_transition_active = False

        # Entrance animation
        QTimer.singleShot(200, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation with staggered effects"""
        entrance_sequence = FluentSequence(self)

        # Fade in the whole component
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self, 450))
        entrance_sequence.addPause(100)

        # Scale in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.scale_in(self, 300))
        entrance_sequence.addPause(150)

        # Animate header separately
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.slide_in(self.datetime_label, 200, "up"))

        entrance_sequence.start()

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header showing current datetime
        header = QWidget()
        header.setFixedHeight(60)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 8, 16, 8)

        self.datetime_label = QLabel()
        self.datetime_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.datetime_label.setFont(QFont("", 16, QFont.Weight.Bold))

        header_layout.addWidget(self.datetime_label)

        # Tab buttons
        tab_layout = QHBoxLayout()

        self.date_tab_btn = FluentButton(
            "Date", style=FluentButton.ButtonStyle.PRIMARY)
        self.time_tab_btn = FluentButton(
            "Time", style=FluentButton.ButtonStyle.SECONDARY)

        self.date_tab_btn.clicked.connect(lambda: self._switch_tab("date"))
        self.time_tab_btn.clicked.connect(lambda: self._switch_tab("time"))

        tab_layout.addWidget(self.date_tab_btn)
        tab_layout.addWidget(self.time_tab_btn)

        # Content area
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Calendar
        self.calendar = FluentCalendar()
        self.calendar.selectionChanged.connect(self._on_date_changed)

        # Time picker
        self.time_picker = FluentTimePicker()
        self.time_picker.time_changed.connect(self._on_time_changed)
        self.time_picker.setVisible(False)

        content_layout.addWidget(self.calendar)
        content_layout.addWidget(self.time_picker)

        layout.addWidget(header)
        layout.addLayout(tab_layout)
        layout.addWidget(self.content_widget)

        self._update_display()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentDateTimePicker {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
            QWidget {{
                background-color: {theme.get_color('surface').name()};
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _switch_tab(self, tab_type: str):
        """Switch tab with enhanced animation"""
        if self._tab_transition_active:
            return  # Prevent multiple simultaneous transitions

        self._tab_transition_active = True

        # Create transition sequence
        transition_sequence = FluentSequence(self)

        if tab_type == "date":
            # Fade out time picker, fade in calendar
            transition_sequence.addCallback(
                lambda: FluentTransition.create_transition(
                    self.time_picker, FluentTransition.FADE, 150).setEndValue(0.0) or
                FluentTransition.create_transition(
                        self.time_picker, FluentTransition.FADE, 150).start())

            transition_sequence.addCallback(
                lambda: (self.time_picker.setVisible(False),
                         self.calendar.setVisible(True)))

            transition_sequence.addCallback(
                lambda: FluentTransition.create_transition(
                    self.calendar, FluentTransition.FADE, 150).setEndValue(1.0) or
                FluentTransition.create_transition(
                        self.calendar, FluentTransition.FADE, 150).start())

            # Update button styles
            self.date_tab_btn.set_style(FluentButton.ButtonStyle.PRIMARY)
            self.time_tab_btn.set_style(FluentButton.ButtonStyle.SECONDARY)

        else:
            # Fade out calendar, fade in time picker
            transition_sequence.addCallback(
                lambda: FluentTransition.create_transition(
                    self.calendar, FluentTransition.FADE, 150).setEndValue(0.0) or
                FluentTransition.create_transition(
                        self.calendar, FluentTransition.FADE, 150).start())

            transition_sequence.addCallback(
                lambda: (self.calendar.setVisible(False),
                         self.time_picker.setVisible(True)))

            transition_sequence.addCallback(
                lambda: FluentTransition.create_transition(
                    self.time_picker, FluentTransition.FADE, 150).setEndValue(1.0) or
                FluentTransition.create_transition(
                        self.time_picker, FluentTransition.FADE, 150).start())

            # Update button styles
            self.date_tab_btn.set_style(FluentButton.ButtonStyle.SECONDARY)
            self.time_tab_btn.set_style(FluentButton.ButtonStyle.PRIMARY)

        # Add completion callback
        transition_sequence.addCallback(lambda: setattr(
            self, '_tab_transition_active', False))
        transition_sequence.start()

    def _on_date_changed(self):
        """Date change handler with animation"""
        selected_date = self.calendar.selectedDate()
        current_time = self._current_datetime.time()
        self._current_datetime = QDateTime(selected_date, current_time)
        self._update_display()

        # Animate datetime label update
        FluentMicroInteraction.pulse_animation(self.datetime_label, scale=1.03)

        self.datetime_changed.emit(self._current_datetime)

    def _on_time_changed(self, time: QTime):
        """Time change handler with animation"""
        current_date = self._current_datetime.date()
        self._current_datetime = QDateTime(current_date, time)
        self._update_display()

        # Animate datetime label update
        FluentMicroInteraction.pulse_animation(self.datetime_label, scale=1.03)

        self.datetime_changed.emit(self._current_datetime)

    def _update_display(self):
        """Update display"""
        self.datetime_label.setText(
            self._current_datetime.toString("yyyy-MM-dd hh:mm:ss")
        )

        # Update child components
        self.calendar.setSelectedDate(self._current_datetime.date())
        self.time_picker.set_time(self._current_datetime.time())

    def showEvent(self, event):
        """Enhanced show event with animation"""
        super().showEvent(event)
        self._state_transition.transitionTo("expanded")

    def hideEvent(self, event):
        """Enhanced hide event"""
        super().hideEvent(event)
        self._state_transition.transitionTo("normal")

    def set_datetime(self, datetime: QDateTime):
        """**Set datetime with smooth animation**"""
        self._current_datetime = datetime
        self._update_display()

        # Add subtle animation for datetime change
        FluentMicroInteraction.scale_animation(self, scale=1.02)

    def get_datetime(self) -> QDateTime:
        """**Get datetime**"""
        return self._current_datetime

    def _on_theme_changed(self, theme_name: str):
        """Theme change handler"""
        # Suppress unused parameter warning
        _ = theme_name
        self._setup_style()


class FluentDatePicker(QWidget):
    """**Simplified Date Picker with Enhanced Animations**"""

    date_changed = Signal(QDate)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._current_date = QDate.currentDate()
        self._setup_animations()
        self._setup_ui()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animations(self):
        """Setup enhanced animation system"""
        # Setup state transitions
        self._state_transition = FluentStateTransition(self)

        self._state_transition.addState("normal", {
            "minimumWidth": 300,
            "minimumHeight": 200,
        })

        self._state_transition.addState("focused", {
            "minimumWidth": 310,
            "minimumHeight": 210,
        }, duration=200, easing=FluentTransition.EASE_SMOOTH)

        # Entrance animation
        QTimer.singleShot(75, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation with enhanced effects"""
        entrance_sequence = FluentSequence(self)

        # Slide in from left
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.slide_in(self, 300, "left"))
        entrance_sequence.addPause(100)

        # Subtle scale effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.scale_in(self.calendar, 250))

        entrance_sequence.start()

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Simplified calendar
        self.calendar = FluentCalendar()
        self.calendar.setMinimumSize(300, 200)
        self.calendar.selectionChanged.connect(self._on_date_changed)

        layout.addWidget(self.calendar)

    def _on_date_changed(self):
        """Date change handler with animation"""
        self._current_date = self.calendar.selectedDate()

        # Add subtle feedback animation
        FluentMicroInteraction.pulse_animation(self.calendar, scale=1.01)

        self.date_changed.emit(self._current_date)

    def showEvent(self, event):
        """Enhanced show event with animation"""
        super().showEvent(event)
        self._state_transition.transitionTo("focused")

    def hideEvent(self, event):
        """Enhanced hide event"""
        super().hideEvent(event)
        self._state_transition.transitionTo("normal")

    def set_date(self, date: QDate):
        """**Set date with animation**"""
        self._current_date = date
        self.calendar.setSelectedDate(date)

        # Add subtle animation for date change
        FluentMicroInteraction.scale_animation(self.calendar, scale=1.02)

    def get_date(self) -> QDate:
        """**Get date**"""
        return self._current_date

    def _on_theme_changed(self, theme_name: str):
        """Theme change handler"""
        # Suppress unused parameter warning
        _ = theme_name
        # No style changes needed for this simplified component
        pass
