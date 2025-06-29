"""
Fluent Design Number Box Component
A specialized numeric input with spinner controls and validation
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton,
                               QLabel, QSizePolicy)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QFont, QDoubleValidator
from core.theme import theme_manager
from core.enhanced_base import FluentBaseWidget
from typing import Optional


class FluentNumberValidator(QDoubleValidator):
    """Custom validator for number input with enhanced features"""

    def __init__(self, minimum: float = 0.0, maximum: float = 100.0,
                 decimals: int = 2, parent=None):
        super().__init__(minimum, maximum, decimals, parent)
        self.setNotation(QDoubleValidator.Notation.StandardNotation)


class FluentNumberBox(FluentBaseWidget):
    """
    Fluent Design Number Box Component

    A specialized input control for numeric values with:
    - Spinner buttons for increment/decrement
    - Validation and constraints
    - Formatting options
    - Keyboard shortcuts
    - Smooth animations
    - Theme consistency
    """

    # Signals
    value_changed = Signal(float)  # Emitted when value changes
    minimum_changed = Signal(float)
    maximum_changed = Signal(float)

    def __init__(self, parent: Optional[QWidget] = None,
                 value: float = 0.0,
                 minimum: float = 0.0,
                 maximum: float = 100.0,
                 step: float = 1.0,
                 decimals: int = 0):
        super().__init__(parent)

        # Properties
        self._value = value
        self._minimum = minimum
        self._maximum = maximum
        self._step = step
        self._decimals = decimals
        self._placeholder_text = ""
        self._header_text = ""
        self._description_text = ""
        self._is_wrap_enabled = False
        self._validation_mode = "LostFocus"  # or "WhileTyping"

        # Formatting
        self._number_formatter = None
        self._text_alignment = Qt.AlignmentFlag.AlignRight
        self._spinner_placement = "Compact"  # or "Inline"

        # State
        self._is_valid = True
        self._original_value = value
        self._is_editing = False
        self._style_setup_needed = True

        # UI Elements (initialized in _setup_ui)
        self._main_layout: QHBoxLayout
        self._input_field: QLineEdit
        self._spin_up_button: QPushButton
        self._spin_down_button: QPushButton
        self._header_label: Optional[QLabel] = None
        self._description_label: Optional[QLabel] = None

        # Validation
        self._validator: FluentNumberValidator

        # Timers
        self._validation_timer = QTimer()
        self._validation_timer.setSingleShot(True)
        self._validation_timer.setInterval(500)
        self._validation_timer.timeout.connect(self._validate_input)

        # Spin repeat timer
        self._spin_timer = QTimer()
        self._spin_timer.setInterval(100)
        self._spin_timer.timeout.connect(self._repeat_spin)
        self._spin_direction = 0

        # Setup
        self._setup_ui()
        self._setup_validation()
        self._connect_signals()

        # Set initial value
        self.set_value(value)

        # Setup style - defer until later to avoid QApplication requirement during import
        self._style_setup_needed = True

    def _setup_ui(self):
        """Setup the UI layout"""
        # Main vertical layout for header, control, and description
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)

        # Header label (optional)
        if self._header_text:
            self._header_label = QLabel(self._header_text)
            self._header_label.setFont(
                QFont("Segoe UI", 11, QFont.Weight.DemiBold))
            main_layout.addWidget(self._header_label)

        # Control layout (input + spinners)
        self._main_layout = QHBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # Input field
        self._input_field = QLineEdit()
        self._input_field.setAlignment(self._text_alignment)
        self._input_field.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._input_field.setMinimumHeight(32)

        if self._placeholder_text:
            self._input_field.setPlaceholderText(self._placeholder_text)

        self._main_layout.addWidget(self._input_field)

        # Spinner buttons
        self._setup_spinner_buttons()

        control_widget = QWidget()
        control_widget.setLayout(self._main_layout)
        main_layout.addWidget(control_widget)

        # Description label (optional)
        if self._description_text:
            self._description_label = QLabel(self._description_text)
            self._description_label.setFont(QFont("Segoe UI", 10))
            self._description_label.setWordWrap(True)
            main_layout.addWidget(self._description_label)

    def _setup_spinner_buttons(self):
        """Setup the spinner buttons"""
        # Spinner container
        spinner_layout = QVBoxLayout()
        spinner_layout.setContentsMargins(1, 1, 1, 1)
        spinner_layout.setSpacing(0)

        # Up button
        self._spin_up_button = QPushButton("▲")
        self._spin_up_button.setFixedSize(20, 15)
        self._spin_up_button.setFont(QFont("Segoe UI", 8))
        self._spin_up_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Down button
        self._spin_down_button = QPushButton("▼")
        self._spin_down_button.setFixedSize(20, 15)
        self._spin_down_button.setFont(QFont("Segoe UI", 8))
        self._spin_down_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        spinner_layout.addWidget(self._spin_up_button)
        spinner_layout.addWidget(self._spin_down_button)

        spinner_widget = QWidget()
        spinner_widget.setLayout(spinner_layout)
        spinner_widget.setFixedWidth(20)

        self._main_layout.addWidget(spinner_widget)

    def _setup_validation(self):
        """Setup input validation"""
        self._validator = FluentNumberValidator(
            self._minimum, self._maximum, self._decimals, self)
        self._input_field.setValidator(self._validator)

    def _ensure_style_setup(self):
        """Ensure style is set up when needed"""
        if self._style_setup_needed:
            self._setup_style()

    def showEvent(self, event):
        """Handle show event to setup style when widget becomes visible"""
        super().showEvent(event)
        self._ensure_style_setup()

    def _setup_style(self):
        """Apply Fluent Design styling"""
        # Mark that style has been set up
        self._style_setup_needed = False

        theme = theme_manager

        # Main number box style
        input_style = f"""
            QLineEdit {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px 0px 0px 6px;
                padding: 6px 8px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()}40;
            }}
            QLineEdit:hover {{
                border-color: {theme.get_color('primary').lighter(150).name()};
                background-color: {theme.get_color('accent_light').name()};
            }}
            QLineEdit:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
                padding: 5px 7px;
                background-color: {theme.get_color('surface').name()};
            }}
            QLineEdit:disabled {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_disabled').name()};
                border-color: {theme.get_color('border').name()};
            }}
        """

        # Spinner buttons style
        button_style = f"""
            QPushButton {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                color: {theme.get_color('text_primary').name()};
                font-size: 8px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('primary').lighter(150).name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
                border-color: {theme.get_color('primary').name()};
            }}
            QPushButton:disabled {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_disabled').name()};
                border-color: {theme.get_color('border').name()};
            }}
        """

        # Apply rounded corners for spinner buttons
        up_button_style = button_style + """
            QPushButton { border-radius: 0px 6px 0px 0px; border-bottom: none; }
        """
        down_button_style = button_style + """
            QPushButton { border-radius: 0px 0px 6px 0px; }
        """

        self._input_field.setStyleSheet(input_style)
        self._spin_up_button.setStyleSheet(up_button_style)
        self._spin_down_button.setStyleSheet(down_button_style)

        # Header and description styles
        if self._header_label:
            self._header_label.setStyleSheet(f"""
                QLabel {{ color: {theme.get_color('text_primary').name()}; }}
            """)

        if self._description_label:
            self._description_label.setStyleSheet(f"""
                QLabel {{ color: {theme.get_color('text_secondary').name()}; }}
            """)

    def _connect_signals(self):
        """Connect signals and slots"""
        # Input field signals
        self._input_field.textChanged.connect(self._on_text_changed)
        self._input_field.editingFinished.connect(self._on_editing_finished)

        # Spinner button signals
        self._spin_up_button.pressed.connect(self._start_spin_up)
        self._spin_up_button.released.connect(self._stop_spin)
        self._spin_down_button.pressed.connect(self._start_spin_down)
        self._spin_down_button.released.connect(self._stop_spin)

        # Theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self):
        """Handle theme changes"""
        self._setup_style()

    def _on_text_changed(self):
        """Handle text changes"""
        if self._validation_mode == "WhileTyping":
            self._validation_timer.start()

    def _on_editing_finished(self):
        """Handle editing finished"""
        self._validate_and_update_value()

    def focusOutEvent(self, event):
        """Handle focus out event"""
        self._validate_and_update_value()
        super().focusOutEvent(event)

    def _validate_input(self):
        """Validate the current input"""
        text = self._input_field.text().strip()

        if not text:
            self._is_valid = False
            return

        try:
            value = float(text)
            self._is_valid = self._minimum <= value <= self._maximum
        except ValueError:
            self._is_valid = False

        self._update_validation_style()

    def _update_validation_style(self):
        """Update the visual style based on validation state"""
        if not self._is_valid:
            # Add error styling
            error_style = self._input_field.styleSheet() + f"""
                QLineEdit {{ border-color: {theme_manager.get_color('error').name()}; }}
            """
            self._input_field.setStyleSheet(error_style)
        else:
            # Reset to normal styling
            self._setup_style()

    def _validate_and_update_value(self):
        """Validate input and update value"""
        text = self._input_field.text().strip()

        if not text:
            # Reset to original value if empty
            self.set_value(self._original_value)
            return

        try:
            value = float(text)
            self.set_value(value)
        except ValueError:
            # Reset to current valid value
            self.set_value(self._value)

    def _format_value(self, value: float) -> str:
        """Format the value for display"""
        if self._decimals == 0:
            return str(int(value))
        else:
            return f"{value:.{self._decimals}f}"

    def _start_spin_up(self):
        """Start spinning up"""
        self._spin_direction = 1
        self._spin_once()
        self._spin_timer.start()

    def _start_spin_down(self):
        """Start spinning down"""
        self._spin_direction = -1
        self._spin_once()
        self._spin_timer.start()

    def _stop_spin(self):
        """Stop spinning"""
        self._spin_timer.stop()
        self._spin_direction = 0

    def _repeat_spin(self):
        """Repeat spin action"""
        self._spin_once()

    def _spin_once(self):
        """Perform one spin increment/decrement"""
        if self._spin_direction != 0:
            new_value = self._value + (self._step * self._spin_direction)
            self.set_value(new_value)

    # Public API

    def get_value(self) -> float:
        """Get the current numeric value"""
        return self._value

    def set_value(self, value: float):
        """Set the numeric value"""
        # Clamp to range
        if self._is_wrap_enabled:
            # Wrap around
            range_size = self._maximum - self._minimum
            if range_size > 0:
                value = ((value - self._minimum) % range_size) + self._minimum
        else:
            # Clamp to bounds
            value = max(self._minimum, min(self._maximum, value))

        if value != self._value:
            self._value = value

            # Update text field without triggering signals
            self._input_field.blockSignals(True)
            self._input_field.setText(self._format_value(value))
            self._input_field.blockSignals(False)

            self.value_changed.emit(value)

        # Update button states
        self._update_button_states()

    def _update_button_states(self):
        """Update spinner button enabled states"""
        if not self._is_wrap_enabled:
            self._spin_up_button.setEnabled(self._value < self._maximum)
            self._spin_down_button.setEnabled(self._value > self._minimum)
        else:
            self._spin_up_button.setEnabled(True)
            self._spin_down_button.setEnabled(True)

    def set_minimum(self, minimum: float):
        """Set the minimum value"""
        self._minimum = minimum
        if self._validator:
            self._validator.setBottom(minimum)
        if self._value < minimum:
            self.set_value(minimum)
        self.minimum_changed.emit(minimum)

    def get_minimum(self) -> float:
        """Get the minimum value"""
        return self._minimum

    def set_maximum(self, maximum: float):
        """Set the maximum value"""
        self._maximum = maximum
        if self._validator:
            self._validator.setTop(maximum)
        if self._value > maximum:
            self.set_value(maximum)
        self.maximum_changed.emit(maximum)

    def get_maximum(self) -> float:
        """Get the maximum value"""
        return self._maximum

    def set_step(self, step: float):
        """Set the step increment"""
        self._step = step

    def get_step(self) -> float:
        """Get the step increment"""
        return self._step

    def set_decimals(self, decimals: int):
        """Set the number of decimal places"""
        self._decimals = decimals
        if self._validator:
            self._validator.setDecimals(decimals)
        # Refresh display
        self.set_value(self._value)

    def get_decimals(self) -> int:
        """Get the number of decimal places"""
        return self._decimals

    def set_header_text(self, text: str):
        """Set the header text"""
        self._header_text = text
        if self._header_label:
            self._header_label.setText(text)
            self._header_label.setVisible(bool(text))

    def set_description_text(self, text: str):
        """Set the description text"""
        self._description_text = text
        if self._description_label:
            self._description_label.setText(text)
            self._description_label.setVisible(bool(text))

    def set_placeholder_text(self, text: str):
        """Set the placeholder text"""
        self._placeholder_text = text
        self._input_field.setPlaceholderText(text)

    def set_wrap_enabled(self, enabled: bool):
        """Enable or disable value wrapping"""
        self._is_wrap_enabled = enabled
        self._update_button_states()


# Export classes
__all__ = [
    'FluentNumberBox',
    'FluentNumberValidator'
]
