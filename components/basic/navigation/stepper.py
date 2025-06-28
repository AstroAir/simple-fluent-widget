"""
Fluent Design Style Stepper Components
Enhanced with smooth animations, theme consistency, and responsive interactions
Optimized for performance and efficiency
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                               QPushButton)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, Property, QByteArray
from PySide6.QtGui import QPainter, QBrush, QFont, QColor
from core.theme import theme_manager
from core.enhanced_animations import (FluentMicroInteraction, FluentRevealEffect)
from typing import Optional, List, Dict
from functools import lru_cache


class FluentStepper(QWidget):
    """Fluent Design Style Step Progress Indicator - Optimized"""

    class StepState:
        PENDING = "pending"
        ACTIVE = "active"
        COMPLETED = "completed"
        ERROR = "error"

    class StepperStyle:
        HORIZONTAL = "horizontal"
        VERTICAL = "vertical"

    step_changed = Signal(int)  # Emitted when current step changes
    step_clicked = Signal(int)  # Emitted when a step is clicked

    def __init__(self, parent: Optional[QWidget] = None,
                 style: str = StepperStyle.HORIZONTAL):
        super().__init__(parent)

        self._style = style
        self._steps: List[Dict] = []
        self._current_step = 0
        self._clickable_steps = True
        self._widgets_created = False
        self._connectors = []  # Store connector widgets

        self._setup_ui()
        self._apply_style()

        # Connect theme change signal - use direct connection for efficiency
        theme_manager.theme_changed.connect(self._on_theme_changed,
                                            Qt.ConnectionType.DirectConnection)

        # Add reveal animation when created
        FluentRevealEffect.fade_in(self, 400)

    def _setup_ui(self):
        """Setup the stepper UI - optimized"""
        if self._style == self.StepperStyle.HORIZONTAL:
            self._layout = QHBoxLayout(self)
        else:
            self._layout = QVBoxLayout(self)

        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

    def add_step(self, title: str, description: str = "",
                 state: str = StepState.PENDING):
        """Add a step to the stepper without creating widgets immediately"""
        step_data = {
            'title': title,
            'description': description,
            'state': state,
            'widget': None
        }

        self._steps.append(step_data)
        self._widgets_created = False

    def _create_widgets(self):
        """Create all step widgets at once - batch creation"""
        if self._widgets_created:
            return

        # Clear existing layout - more efficient than individual updates
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._connectors = []  # Reset connectors list

        # Create all widgets at once
        for i, step_data in enumerate(self._steps):
            step_widget = FluentStepWidget(
                i + 1,
                step_data['title'],
                step_data['description'],
                step_data['state'],
                self._style
            )

            step_widget.clicked.connect(
                lambda idx=i: self._on_step_clicked(idx))
            step_data['widget'] = step_widget

            # Add widget to layout
            self._layout.addWidget(step_widget)

            # Add connector if not the last step
            if i < len(self._steps) - 1:
                connector = FluentStepConnector(self._style)
                self._layout.addWidget(connector)
                self._connectors.append(connector)

        self._widgets_created = True
        self._update_step_states()

    def _on_step_clicked(self, index: int):
        """Handle step click - optimized"""
        if self._clickable_steps:
            old_step = self._current_step
            self._current_step = index
            self._update_step_states()

            self.step_clicked.emit(index)
            if old_step != index:
                self.step_changed.emit(index)

    def _update_step_states(self):
        """Update step states based on current step - optimized"""
        if not self._widgets_created:
            self._create_widgets()

        for i, step_data in enumerate(self._steps):
            widget = step_data['widget']
            if widget:
                if i < self._current_step:
                    state = self.StepState.COMPLETED
                elif i == self._current_step:
                    state = self.StepState.ACTIVE
                else:
                    state = self.StepState.PENDING

                if step_data['state'] != state:
                    step_data['state'] = state
                    widget.set_state(state)

    @lru_cache(maxsize=4)  # Cache style sheet to avoid regeneration
    def _get_style_sheet(self):
        """Get cached style sheet"""
        return """
            FluentStepper {
                background: transparent;
                border: none;
            }
        """

    def _apply_style(self):
        """Apply stepper styling - cached for performance"""
        self.setStyleSheet(self._get_style_sheet())

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change - optimized to minimize updates"""
        # Clear style sheet cache to ensure fresh styles
        self._get_style_sheet.cache_clear()
        self._apply_style()

        # Update child widgets
        if self._widgets_created:
            for step_data in self._steps:
                if step_data['widget']:
                    step_data['widget']._apply_style()

            for connector in self._connectors:
                connector._apply_style()

    def set_current_step(self, index: int):
        """Set the current step programmatically"""
        if 0 <= index < len(self._steps):
            old_step = self._current_step
            self._current_step = index
            self._update_step_states()

            if old_step != index:
                self.step_changed.emit(index)

    def get_current_step(self) -> int:
        """Get current step index"""
        return self._current_step

    def set_step_state(self, index: int, state: str):
        """Set state for a specific step"""
        if 0 <= index < len(self._steps):
            self._steps[index]['state'] = state

            if self._widgets_created and self._steps[index]['widget']:
                self._steps[index]['widget'].set_state(state)

    def set_clickable(self, clickable: bool):
        """Set whether steps are clickable"""
        self._clickable_steps = clickable

    def next_step(self):
        """Go to next step"""
        if self._current_step < len(self._steps) - 1:
            self.set_current_step(self._current_step + 1)

    def previous_step(self):
        """Go to previous step"""
        if self._current_step > 0:
            self.set_current_step(self._current_step - 1)

    def showEvent(self, event):
        """Ensure widgets are created when shown"""
        if not self._widgets_created and self._steps:
            self._create_widgets()
        super().showEvent(event)


class FluentStepWidget(QWidget):
    """Individual step widget in the stepper - optimized"""

    clicked = Signal()

    def __init__(self, number: int, title: str, description: str = "",
                 state: str = FluentStepper.StepState.PENDING,
                 stepper_style: str = FluentStepper.StepperStyle.HORIZONTAL,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._number = number
        self._title = title
        self._description = description
        self._state = state
        self._stepper_style = stepper_style

        self._opacity = 0.0
        self._style_cache = {}  # Cache for style sheets

        self._setup_ui()
        self._setup_animations()
        self._apply_style()

        # Enable mouse tracking for better hover handling
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def _setup_ui(self):
        """Setup step widget UI - optimized"""
        if self._stepper_style == FluentStepper.StepperStyle.HORIZONTAL:
            layout = QVBoxLayout(self)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            layout = QHBoxLayout(self)
            layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Step indicator (circle with number or icon)
        self._indicator = QLabel()
        self._indicator.setFixedSize(32, 32)
        self._indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Step content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)

        self._title_label = QLabel(self._title)
        self._title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))

        content_layout.addWidget(self._title_label)

        if self._description:
            self._description_label = QLabel(self._description)
            self._description_label.setFont(QFont("Segoe UI", 8))
            self._description_label.setWordWrap(True)
            content_layout.addWidget(self._description_label)

        content_widget = QWidget()
        content_widget.setLayout(content_layout)

        layout.addWidget(self._indicator)
        layout.addWidget(content_widget)

        self._update_indicator()

    def _setup_animations(self):
        """Setup animations for the step widget - optimized"""
        # Add property animation for hover effect
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_opacity"))
        self._hover_animation.setDuration(150)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _update_indicator(self):
        """Update the step indicator based on state"""
        if self._state == FluentStepper.StepState.COMPLETED:
            self._indicator.setText("✓")
        elif self._state == FluentStepper.StepState.ERROR:
            self._indicator.setText("✗")
        else:
            self._indicator.setText(str(self._number))

    def _get_indicator_style(self):
        """Get cached indicator style sheet"""
        current_theme = theme_manager

        # Get colors based on state
        if self._state == FluentStepper.StepState.ACTIVE:
            bg_color = current_theme.get_color('primary')
            text_color = current_theme.get_color('text_on_accent')
        elif self._state == FluentStepper.StepState.COMPLETED:
            bg_color = current_theme.get_color('success')
            text_color = current_theme.get_color('text_on_accent')
        elif self._state == FluentStepper.StepState.ERROR:
            bg_color = current_theme.get_color('error')
            text_color = current_theme.get_color('text_on_accent')
        else:  # PENDING
            bg_color = current_theme.get_color('surface_light')
            text_color = current_theme.get_color('text_secondary')

        cache_key = f"indicator_{self._state}"

        if cache_key not in self._style_cache:
            self._style_cache[cache_key] = f"""
                QLabel {{
                    background-color: {bg_color.name()};
                    color: {text_color.name()};
                    border: 2px solid {bg_color.name()};
                    border-radius: 16px;
                    font-weight: bold;
                    font-size: 12px;
                }}
            """

        return self._style_cache[cache_key]

    def _apply_style(self):
        """Apply styling to the step widget - optimized with caching"""
        # Clear style cache on style application
        self._style_cache = {}
        current_theme = theme_manager

        # Get indicator styles
        self._indicator.setStyleSheet(self._get_indicator_style())

        # Get styles based on state
        if self._state == FluentStepper.StepState.ACTIVE:
            title_color = current_theme.get_color('text_primary')
        elif self._state == FluentStepper.StepState.COMPLETED:
            title_color = current_theme.get_color('text_primary')
        elif self._state == FluentStepper.StepState.ERROR:
            title_color = current_theme.get_color('error')
        else:  # PENDING
            title_color = current_theme.get_color('text_secondary')

        # Apply title style
        self._title_label.setStyleSheet(f"""
            QLabel {{
                color: {title_color.name()};
                background: transparent;
                border: none;
            }}
        """)

        # Apply description style if exists
        if hasattr(self, '_description_label'):
            self._description_label.setStyleSheet(f"""
                QLabel {{
                    color: {current_theme.get_color('text_secondary').name()};
                    background: transparent;
                    border: none;
                }}
            """)

    def set_state(self, state: str):
        """Set the step state - optimized"""
        if state != self._state:
            self._state = state
            self._update_indicator()
            self._apply_style()

            # Add state change animation - but only once
            FluentMicroInteraction.pulse_animation(self._indicator, 1.2)

    def get_hover_opacity(self):
        """Getter for hover opacity property"""
        return self._opacity

    def set_hover_opacity(self, opacity):
        """Setter for hover opacity property"""
        if self._opacity != opacity:
            self._opacity = opacity
            self.update()  # Only update when value changes

    # Define the Qt property
    hover_opacity = Property(float, get_hover_opacity,
                             set_hover_opacity, None, "")

    def mousePressEvent(self, event):
        """Handle mouse press - optimized"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Use property animation for better performance
            FluentMicroInteraction.scale_animation(self, 0.98)
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Handle hover enter - with property animation"""
        # Setup and start fade-in animation
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._opacity)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle hover leave - with property animation"""
        # Setup and start fade-out animation
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._opacity)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        """Custom paint to handle hover effect with less overhead"""
        super().paintEvent(event)

        # Only draw hover effect if opacity is non-zero
        if self._opacity > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Get theme color with opacity
            current_theme = theme_manager
            hover_color = current_theme.get_color('surface_light')
            hover_color.setAlphaF(self._opacity * 0.2)  # Adjust opacity

            painter.setBrush(QBrush(hover_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(self.rect(), 8, 8)


class FluentStepConnector(QWidget):
    """Connector line between steps - optimized"""

    def __init__(self, stepper_style: str = FluentStepper.StepperStyle.HORIZONTAL,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._stepper_style = stepper_style
        self._cached_brush = None

        # Set fixed size based on style for better performance
        if stepper_style == FluentStepper.StepperStyle.HORIZONTAL:
            self.setFixedSize(40, 2)
        else:
            self.setFixedSize(2, 40)

        self._apply_style()

    def _apply_style(self):
        """Apply connector styling - optimized"""
        current_theme = theme_manager

        # Cache brush for painting
        self._cached_brush = QBrush(current_theme.get_color('border'))
        self.update()

    def paintEvent(self, _event):
        """Custom paint for connector - optimized"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Use cached brush
        if not self._cached_brush:
            self._cached_brush = QBrush(theme_manager.get_color('border'))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._cached_brush)
        painter.drawRect(self.rect())


class FluentNumericStepper(QWidget):
    """Fluent Design Style Numeric Input Stepper - Optimized"""

    value_changed = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None,
                 minimum: int = 0, maximum: int = 100, value: int = 0, step: int = 1):
        super().__init__(parent)

        self._minimum = minimum
        self._maximum = maximum
        self._current_value = value
        self._step = step

        # Cache for button enabled states
        self._decrease_enabled = False
        self._increase_enabled = False

        self._setup_ui()
        self._apply_style()

        # Connect theme change signal - use direct connection
        theme_manager.theme_changed.connect(self._on_theme_changed,
                                            Qt.ConnectionType.DirectConnection)

        # Add reveal animation when created
        FluentRevealEffect.scale_in(self, 200)

    def _setup_ui(self):
        """Setup numeric stepper UI - optimized"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Decrease button
        self._decrease_btn = QPushButton("−")
        self._decrease_btn.setFixedSize(28, 28)
        self._decrease_btn.clicked.connect(self._decrease_value)

        # Value display
        self._value_label = QLabel(str(self._current_value))
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._value_label.setMinimumWidth(50)

        # Increase button
        self._increase_btn = QPushButton("+")
        self._increase_btn.setFixedSize(28, 28)
        self._increase_btn.clicked.connect(self._increase_value)

        layout.addWidget(self._decrease_btn)
        layout.addWidget(self._value_label)
        layout.addWidget(self._increase_btn)

        # Initial button state update
        self._update_buttons()

    def _apply_style(self):
        """Apply numeric stepper styling - optimized"""
        current_theme = theme_manager

        button_style = f"""
            QPushButton {{
                background-color: {current_theme.get_color('surface').name()};
                border: 1px solid {current_theme.get_color('border').name()};
                color: {current_theme.get_color('text_primary').name()};
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {current_theme.get_color('surface_light').name()};
                border-color: {current_theme.get_color('primary').name()};
            }}
            QPushButton:pressed {{
                background-color: {current_theme.get_color('surface').darker(110).name()};
            }}
            QPushButton:disabled {{
                background-color: {current_theme.get_color('surface_disabled').name()};
                color: {current_theme.get_color('text_disabled').name()};
                border-color: {current_theme.get_color('border').name()};
            }}
        """

        label_style = f"""
            QLabel {{
                background-color: {current_theme.get_color('surface').name()};
                border: 1px solid {current_theme.get_color('border').name()};
                border-left: none;
                border-right: none;
                color: {current_theme.get_color('text_primary').name()};
                font-size: 12px;
                padding: 4px 8px;
            }}
        """

        self._decrease_btn.setStyleSheet(button_style)
        self._increase_btn.setStyleSheet(button_style)
        self._value_label.setStyleSheet(label_style)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change - optimized"""
        self._apply_style()

    def _decrease_value(self):
        """Decrease the value - optimized"""
        new_value = max(self._minimum, self._current_value - self._step)
        if new_value != self._current_value:
            self._current_value = new_value
            self._value_label.setText(str(self._current_value))
            self._update_buttons_if_needed()
            self.value_changed.emit(self._current_value)

            # Use property animation for smoother visual effect
            FluentMicroInteraction.scale_animation(self._value_label, 0.95)

    def _increase_value(self):
        """Increase the value - optimized"""
        new_value = min(self._maximum, self._current_value + self._step)
        if new_value != self._current_value:
            self._current_value = new_value
            self._value_label.setText(str(self._current_value))
            self._update_buttons_if_needed()
            self.value_changed.emit(self._current_value)

            # Use property animation for smoother visual effect
            FluentMicroInteraction.scale_animation(self._value_label, 1.05)

    def _update_buttons_if_needed(self):
        """Update button enabled state only if needed"""
        decrease_should_be_enabled = self._current_value > self._minimum
        increase_should_be_enabled = self._current_value < self._maximum

        if decrease_should_be_enabled != self._decrease_enabled:
            self._decrease_enabled = decrease_should_be_enabled
            self._decrease_btn.setEnabled(decrease_should_be_enabled)

        if increase_should_be_enabled != self._increase_enabled:
            self._increase_enabled = increase_should_be_enabled
            self._increase_btn.setEnabled(increase_should_be_enabled)

    def _update_buttons(self):
        """Initial button state setup"""
        self._decrease_enabled = self._current_value > self._minimum
        self._increase_enabled = self._current_value < self._maximum

        self._decrease_btn.setEnabled(self._decrease_enabled)
        self._increase_btn.setEnabled(self._increase_enabled)

    def set_value(self, value: int):
        """Set the current value - optimized"""
        value = max(self._minimum, min(self._maximum, value))
        if value != self._current_value:
            self._current_value = value
            self._value_label.setText(str(self._current_value))
            self._update_buttons_if_needed()

    def get_value(self) -> int:
        """Get the current value"""
        return self._current_value

    def set_range(self, minimum: int, maximum: int):
        """Set the value range"""
        self._minimum = minimum
        self._maximum = maximum

        # Re-validate current value within new range
        old_value = self._current_value
        new_value = max(self._minimum, min(self._maximum, self._current_value))

        if new_value != old_value:
            self._current_value = new_value
            self._value_label.setText(str(self._current_value))

        # Update button states for new range
        self._update_buttons_if_needed()

    def set_step(self, step: int):
        """Set the step size"""
        self._step = max(1, step)
