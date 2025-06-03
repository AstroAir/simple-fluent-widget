"""
Fluent Design Style Stepper Components
Enhanced with smooth animations, theme consistency, and responsive interactions
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                               QPushButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QBrush, QFont
from core.theme import theme_manager
from core.enhanced_animations import (FluentMicroInteraction, FluentTransition,
                                      FluentStateTransition, FluentRevealEffect)
from typing import Optional, List, Dict


class FluentStepper(QWidget):
    """Fluent Design Style Step Progress Indicator"""

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

        self._setup_ui()
        self._apply_style()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Add reveal animation when created
        FluentRevealEffect.fade_in(self, 400)

    def _setup_ui(self):
        """Setup the stepper UI"""
        if self._style == self.StepperStyle.HORIZONTAL:
            self._layout = QHBoxLayout(self)
        else:
            self._layout = QVBoxLayout(self)

        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(0)

    def add_step(self, title: str, description: str = "",
                 state: str = StepState.PENDING):
        """Add a step to the stepper"""
        step_data = {
            'title': title,
            'description': description,
            'state': state,
            'widget': None
        }

        self._steps.append(step_data)
        self._create_step_widget(len(self._steps) - 1)

        # Add connector if not the first step
        if len(self._steps) > 1:
            self._add_connector(len(self._steps) - 2)

    def _create_step_widget(self, index: int):
        """Create widget for a step"""
        step_data = self._steps[index]

        step_widget = FluentStepWidget(
            index + 1,
            step_data['title'],
            step_data['description'],
            step_data['state'],
            self._style
        )

        step_widget.clicked.connect(lambda: self._on_step_clicked(index))
        step_data['widget'] = step_widget

        self._layout.addWidget(step_widget)

    def _add_connector(self, index: int):
        """Add connector line between steps"""
        connector = FluentStepConnector(self._style)

        # Insert connector between steps
        if self._style == self.StepperStyle.HORIZONTAL:
            self._layout.insertWidget(index * 2 + 1, connector)
        else:
            self._layout.insertWidget(index * 2 + 1, connector)

    def _on_step_clicked(self, index: int):
        """Handle step click"""
        if self._clickable_steps:
            old_step = self._current_step
            self._current_step = index
            self._update_step_states()

            self.step_clicked.emit(index)
            if old_step != index:
                self.step_changed.emit(index)

    def _update_step_states(self):
        """Update step states based on current step"""
        for i, step_data in enumerate(self._steps):
            widget = step_data['widget']
            if widget:
                if i < self._current_step:
                    widget.set_state(self.StepState.COMPLETED)
                elif i == self._current_step:
                    widget.set_state(self.StepState.ACTIVE)
                else:
                    widget.set_state(self.StepState.PENDING)

    def _apply_style(self):
        """Apply stepper styling"""
        # current_theme = theme_manager # Not used directly in this method

        style_sheet = f"""
            FluentStepper {{
                background: transparent;
                border: none;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._apply_style()
        for step_data in self._steps:
            if step_data['widget']:
                step_data['widget']._apply_style()

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
            if self._steps[index]['widget']:
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


class FluentStepWidget(QWidget):
    """Individual step widget in the stepper"""

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

        self._is_hovered = False
        self._state_transition = FluentStateTransition(self)

        self._setup_ui()
        self._setup_animations()
        self._apply_style()

    def _setup_ui(self):
        """Setup step widget UI"""
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
        self._indicator.setStyleSheet("border-radius: 16px;")

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
        """Setup animations for the step widget"""
        self._state_transition.addState("normal", {})
        self._state_transition.addState("hovered", {},
                                        duration=150,
                                        easing=FluentTransition.EASE_SMOOTH)

    def _update_indicator(self):
        """Update the step indicator based on state"""
        if self._state == FluentStepper.StepState.COMPLETED:
            self._indicator.setText("✓")
        elif self._state == FluentStepper.StepState.ERROR:
            self._indicator.setText("✗")
        else:
            self._indicator.setText(str(self._number))

    def _apply_style(self):
        """Apply styling to the step widget"""
        current_theme = theme_manager

        # Get colors based on state
        if self._state == FluentStepper.StepState.ACTIVE:
            bg_color = current_theme.get_color('primary')
            text_color = current_theme.get_color('text_on_accent')
            title_color = current_theme.get_color('text_primary')
        elif self._state == FluentStepper.StepState.COMPLETED:
            bg_color = current_theme.get_color('success')
            text_color = current_theme.get_color('text_on_accent')
            title_color = current_theme.get_color('text_primary')
        elif self._state == FluentStepper.StepState.ERROR:
            bg_color = current_theme.get_color('error')
            text_color = current_theme.get_color('text_on_accent')
            title_color = current_theme.get_color('error')
        else:  # PENDING
            bg_color = current_theme.get_color('surface_light')
            text_color = current_theme.get_color('text_secondary')
            title_color = current_theme.get_color('text_secondary')

        indicator_style = f"""
            QLabel {{
                background-color: {bg_color.name()};
                color: {text_color.name()};
                border: 2px solid {bg_color.name()};
                border-radius: 16px;
                font-weight: bold;
                font-size: 12px;
            }}
        """

        title_style = f"""
            QLabel {{
                color: {title_color.name()};
                background: transparent;
                border: none;
            }}
        """

        self._indicator.setStyleSheet(indicator_style)
        self._title_label.setStyleSheet(title_style)

        if hasattr(self, '_description_label'):
            desc_style = f"""
                QLabel {{
                    color: {current_theme.get_color('text_secondary').name()};
                    background: transparent;
                    border: none;
                }}
            """
            self._description_label.setStyleSheet(desc_style)

        # Widget style
        widget_style = f"""
            FluentStepWidget {{
                background: transparent;
                border: none;
                border-radius: 8px;
            }}
            FluentStepWidget:hover {{
                background: {current_theme.get_color('surface_light').name()};
            }}
        """

        self.setStyleSheet(widget_style)

    def set_state(self, state: str):
        """Set the step state"""
        if state != self._state:
            self._state = state
            self._update_indicator()
            self._apply_style()

            # Add state change animation
            FluentMicroInteraction.pulse_animation(self._indicator, 1.2)

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            FluentMicroInteraction.scale_animation(self, 0.98)
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Handle hover enter"""
        self._is_hovered = True
        self._state_transition.transitionTo("hovered")
        FluentMicroInteraction.hover_glow(self, 0.1)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle hover leave"""
        self._is_hovered = False
        self._state_transition.transitionTo("normal")
        super().leaveEvent(event)


class FluentStepConnector(QWidget):
    """Connector line between steps"""

    def __init__(self, stepper_style: str = FluentStepper.StepperStyle.HORIZONTAL,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._stepper_style = stepper_style

        if stepper_style == FluentStepper.StepperStyle.HORIZONTAL:
            self.setFixedSize(40, 2)
        else:
            self.setFixedSize(2, 40)

        self._apply_style()

    def _apply_style(self):
        """Apply connector styling"""
        current_theme = theme_manager

        style_sheet = f"""
            FluentStepConnector {{
                background-color: {current_theme.get_color('border').name()};
                border: none;
            }}
        """

        self.setStyleSheet(style_sheet)

    def paintEvent(self, _event):
        """Custom paint for connector"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        current_theme = theme_manager

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(current_theme.get_color('border')))
        painter.drawRect(self.rect())


class FluentNumericStepper(QWidget):
    """Fluent Design Style Numeric Input Stepper"""

    value_changed = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None,
                 minimum: int = 0, maximum: int = 100, value: int = 0, step: int = 1):
        super().__init__(parent)

        self._minimum = minimum
        self._maximum = maximum
        self._current_value = value
        self._step = step

        self._setup_ui()
        self._apply_style()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Add reveal animation when created
        FluentRevealEffect.scale_in(self, 200)

    def _setup_ui(self):
        """Setup numeric stepper UI"""
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

        self._update_buttons()

    def _apply_style(self):
        """Apply numeric stepper styling"""
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
        """Handle theme change"""
        self._apply_style()

    def _decrease_value(self):
        """Decrease the value"""
        new_value = max(self._minimum, self._current_value - self._step)
        if new_value != self._current_value:
            self._current_value = new_value
            self._value_label.setText(str(self._current_value))
            self._update_buttons()
            self.value_changed.emit(self._current_value)

            # Add decrease animation
            FluentMicroInteraction.scale_animation(self._value_label, 0.9)

    def _increase_value(self):
        """Increase the value"""
        new_value = min(self._maximum, self._current_value + self._step)
        if new_value != self._current_value:
            self._current_value = new_value
            self._value_label.setText(str(self._current_value))
            self._update_buttons()
            self.value_changed.emit(self._current_value)

            # Add increase animation
            FluentMicroInteraction.scale_animation(self._value_label, 1.1)

    def _update_buttons(self):
        """Update button enabled state"""
        self._decrease_btn.setEnabled(self._current_value > self._minimum)
        self._increase_btn.setEnabled(self._current_value < self._maximum)

    def set_value(self, value: int):
        """Set the current value"""
        value = max(self._minimum, min(self._maximum, value))
        if value != self._current_value:
            self._current_value = value
            self._value_label.setText(str(self._current_value))
            self._update_buttons()

    def get_value(self) -> int:
        """Get the current value"""
        return self._current_value

    def set_range(self, minimum: int, maximum: int):
        """Set the value range"""
        self._minimum = minimum
        self._maximum = maximum
        self.set_value(self._current_value)  # Re-validate current value

    def set_step(self, step: int):
        """Set the step size"""
        self._step = max(1, step)
