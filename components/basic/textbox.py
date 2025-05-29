"""
Fluent Design Style Text Input Components
Enhanced with improved animations and consistent styling patterns
"""

from PySide6.QtWidgets import QLineEdit, QTextEdit, QWidget
from PySide6.QtCore import Signal
from PySide6.QtGui import QFocusEvent
from core.theme import theme_manager
from core.enhanced_animations import (FluentMicroInteraction, FluentTransition,
                                      FluentStateTransition, FluentRevealEffect)
from typing import Optional


class FluentLineEdit(QLineEdit):
    """Fluent Design Style Single Line Text Input with enhanced animations"""

    def __init__(self, parent: Optional[QWidget] = None,
                 placeholder: str = ""):
        super().__init__(parent)

        self._state_transition = FluentStateTransition(self)
        self._is_focused = False
        self._is_hovered = False

        # Set basic properties
        if placeholder:
            self.setPlaceholderText(placeholder)

        self.setMinimumHeight(32)

        self._setup_enhanced_animations()
        self._apply_style()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation effects"""
        # Setup state transitions for different input states
        self._state_transition.addState("normal", {
            "minimumHeight": 32,
        })

        self._state_transition.addState("hovered", {
            "minimumHeight": 34,
        }, duration=150, easing=FluentTransition.EASE_SMOOTH)

        self._state_transition.addState("focused", {
            "minimumHeight": 36,
        }, duration=200, easing=FluentTransition.EASE_SPRING)

    def _apply_style(self):
        """Apply style with enhanced visual effects"""
        current_theme = theme_manager

        style_sheet = f"""
            FluentLineEdit {{
                background-color: {current_theme.get_color('surface').name()};
                border: 1px solid {current_theme.get_color('border').name()};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: {current_theme.get_color('text_primary').name()};
                selection-background-color: {current_theme.get_color('primary').name()}40;
                min-height: 32px;
            }}
            FluentLineEdit:hover {{
                border-color: {current_theme.get_color('primary').lighter(150).name()};
                background-color: {current_theme.get_color('accent_light').name()};
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }}
            FluentLineEdit:focus {{
                border-color: {current_theme.get_color('primary').name()};
                border-width: 2px;
                padding: 7px 11px;
                background-color: {current_theme.get_color('surface').name()};
                box-shadow: 0 0 0 3px {current_theme.get_color('primary').name()}20;
            }}
            FluentLineEdit:disabled {{
                background-color: {current_theme.get_color('surface').name()};
                color: {current_theme.get_color('text_disabled').name()};
                border-color: {current_theme.get_color('border').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, theme_name: str):
        """Handle theme change"""
        self._apply_style()

    def focusInEvent(self, event: QFocusEvent):
        """Focus in event with enhanced animations"""
        self._is_focused = True

        # Apply focus glow effect
        FluentMicroInteraction.hover_glow(self, 0.2)

        # Transition to focused state
        self._state_transition.transitionTo("focused")

        # Add subtle scale animation
        FluentMicroInteraction.scale_animation(self, 1.02)

        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        """Focus out event"""
        self._is_focused = False

        # Transition back to normal or hover state
        if self._is_hovered:
            self._state_transition.transitionTo("hovered")
        else:
            self._state_transition.transitionTo("normal")

        super().focusOutEvent(event)

    def enterEvent(self, event):
        """Hover enter event with enhanced animations"""
        self._is_hovered = True

        # Apply hover glow effect if not focused
        if not self._is_focused:
            FluentMicroInteraction.hover_glow(self, 0.1)
            self._state_transition.transitionTo("hovered")

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave event"""
        self._is_hovered = False

        # Transition back to normal state if not focused
        if not self._is_focused:
            self._state_transition.transitionTo("normal")

        super().leaveEvent(event)


class FluentTextEdit(QTextEdit):
    """Fluent Design Style Multi-line Text Input with enhanced animations"""

    def __init__(self, parent: Optional[QWidget] = None,
                 placeholder: str = ""):
        super().__init__(parent)

        self._state_transition = FluentStateTransition(self)
        self._is_focused = False
        self._is_hovered = False

        # Set basic properties
        if placeholder:
            self.setPlaceholderText(placeholder)

        self.setMinimumHeight(80)

        self._setup_enhanced_animations()
        self._apply_style()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation effects"""
        # Setup state transitions for different text edit states
        self._state_transition.addState("normal", {
            "minimumHeight": 80,
        })

        self._state_transition.addState("hovered", {
            "minimumHeight": 82,
        }, duration=150, easing=FluentTransition.EASE_SMOOTH)

        self._state_transition.addState("focused", {
            "minimumHeight": 84,
        }, duration=200, easing=FluentTransition.EASE_SPRING)

    def _apply_style(self):
        """Apply style with enhanced visual effects"""
        current_theme = theme_manager

        style_sheet = f"""
            FluentTextEdit {{
                background-color: {current_theme.get_color('surface').name()};
                border: 1px solid {current_theme.get_color('border').name()};
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                color: {current_theme.get_color('text_primary').name()};
                selection-background-color: {current_theme.get_color('primary').name()}40;
                min-height: 80px;
            }}
            FluentTextEdit:hover {{
                border-color: {current_theme.get_color('primary').lighter(150).name()};
                background-color: {current_theme.get_color('accent_light').name()};
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }}
            FluentTextEdit:focus {{
                border-color: {current_theme.get_color('primary').name()};
                border-width: 2px;
                padding: 11px;
                background-color: {current_theme.get_color('surface').name()};
                box-shadow: 0 0 0 3px {current_theme.get_color('primary').name()}20;
            }}
            FluentTextEdit:disabled {{
                background-color: {current_theme.get_color('surface').name()};
                color: {current_theme.get_color('text_disabled').name()};
                border-color: {current_theme.get_color('border').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, theme_name: str):
        """Handle theme change"""
        self._apply_style()

    def focusInEvent(self, event: QFocusEvent):
        """Focus in event with enhanced animations"""
        self._is_focused = True

        # Apply focus glow effect
        FluentMicroInteraction.hover_glow(self, 0.2)

        # Transition to focused state
        self._state_transition.transitionTo("focused")

        # Add subtle scale animation
        FluentMicroInteraction.scale_animation(self, 1.01)

        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        """Focus out event"""
        self._is_focused = False

        # Transition back to normal or hover state
        if self._is_hovered:
            self._state_transition.transitionTo("hovered")
        else:
            self._state_transition.transitionTo("normal")

        super().focusOutEvent(event)

    def enterEvent(self, event):
        """Hover enter event with enhanced animations"""
        self._is_hovered = True

        # Apply hover glow effect if not focused
        if not self._is_focused:
            FluentMicroInteraction.hover_glow(self, 0.1)
            self._state_transition.transitionTo("hovered")

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave event"""
        self._is_hovered = False

        # Transition back to normal state if not focused
        if not self._is_focused:
            self._state_transition.transitionTo("normal")

        super().leaveEvent(event)


class FluentPasswordEdit(FluentLineEdit):
    """Fluent Design Style Password Input with enhanced animations"""

    def __init__(self, parent: Optional[QWidget] = None,
                 placeholder: str = "Enter password"):
        super().__init__(parent, placeholder)

        # Set password mode
        self.setEchoMode(QLineEdit.EchoMode.Password)

        # Add reveal animation when created
        FluentRevealEffect.fade_in(self, 300)

    def _apply_style(self):
        """Override to apply password-specific styling"""
        super()._apply_style()

        # Add password-specific visual indicators
        current_theme = theme_manager
        additional_style = f"""
            FluentPasswordEdit {{
                font-family: 'Consolas', 'Courier New', monospace;
                letter-spacing: 2px;
            }}
            FluentPasswordEdit:focus {{
                border-color: {current_theme.get_color('primary').name()};
                box-shadow: 0 0 0 3px {current_theme.get_color('primary').name()}30;
            }}
        """

        current_style = self.styleSheet()
        self.setStyleSheet(current_style + additional_style)


class FluentSearchBox(FluentLineEdit):
    """Fluent Design Style Search Box with enhanced animations"""

    search_triggered = Signal(str)  # Emitted when search is performed

    def __init__(self, parent: Optional[QWidget] = None,
                 placeholder: str = "Search..."):
        super().__init__(parent, placeholder)

        # Connect return press to search
        self.returnPressed.connect(self._on_search)

        # Add search icon styling
        self._apply_search_style()

        # Add reveal animation when created
        FluentRevealEffect.slide_in(self, 300, "right")

    def _apply_search_style(self):
        """Apply search-specific styling"""
        super()._apply_style()

        current_theme = theme_manager
        additional_style = f"""
            FluentSearchBox {{
                background-image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTExLjc0MiAxMC4zNDRMMTQuNSAxMy4xTDE0IDEzLjZMMTEuMjQ0IDEwLjg0NEMxMC41IDExLjUgOS4yNSAxMiA4IDEyQzQuNjg2IDEyIDIgOS4zMTQgMiA2UzQuNjg2IDAgOCAwUzE0IDIuNjg2IDE0IDZDMTQgNy4yNSAxMy41IDEwLjUgMTEuNzQyIDEwLjM0NFpNOCAxMUM5LjkzIDExIDExLjUgOS40MyAxMS41IDcuNUM4IDQgOCA0IDggNFMxOCA0IDguNSA2LjVTNC4wNyA5IDYgOVpNOCAxQzUuMjQgMSAzIDMuMjQgMyA2UzUuMjQgMTEgOCAxMVM4IDguNzYgOCA2UzguNzYgMSA4IDFaIiBmaWxsPSIjNjY2IiAvPgo8L3N2Zz4K);
                background-repeat: no-repeat;
                background-position: 12px center;
                padding-left: 40px;
            }}
            FluentSearchBox:focus {{
                background-image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1zbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTExLjc0MiAxMC4zNDRMMTQuNSAxMy4xTDE0IDEzLjZMMTEuMjQ0IDEwLjg0NEMxMC41IDExLjUgOS4yNSAxMiA4IDEyQzQuNjg2IDEyIDIgOS4zMTQgMiA2UzQuNjg2IDAgOCAwUzE0IDIuNjg2IDE0IDZDMTQgNy4yNSAxMy41IDEwLjUgMTEuNzQyIDEwLjM0NFpNOCAxMUM5LjkzIDExIDExLjUgOS40MyAxMS41IDcuNUM4IDQgOCA0IDggNFMxOCA0IDguNSA2LjVTNC4wNyA5IDYgOVpNOCAxQzUuMjQgMSAzIDMuMjQgMyA2UzUuMjQgMTEgOCAxMVM4IDguNzYgOCA2UzguNzYgMSA4IDFaIiBmaWxsPSIjZmZmIiAvPgo8L3N2Zz4K);
                padding-left: 39px;
            }}
        """

        current_style = self.styleSheet()
        self.setStyleSheet(current_style + additional_style)

    def _on_search(self):
        """Handle search trigger with animation"""
        text = self.text().strip()
        if text:
            # Apply search animation
            FluentMicroInteraction.pulse_animation(self, 1.05)
            self.search_triggered.emit(text)

    def set_search_text(self, text: str):
        """Set search text with animation"""
        # Fade out current text
        fade_out = FluentTransition.create_transition(
            self, FluentTransition.FADE, 150, FluentTransition.EASE_SMOOTH)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.7)

        def set_text_and_fade_in():
            self.setText(text)
            # Fade in new text
            fade_in = FluentTransition.create_transition(
                self, FluentTransition.FADE, 150, FluentTransition.EASE_SMOOTH)
            fade_in.setStartValue(0.7)
            fade_in.setEndValue(1.0)
            fade_in.start()

        fade_out.finished.connect(set_text_and_fade_in)
        fade_out.start()


class FluentNumericEdit(FluentLineEdit):
    """Fluent Design Style Numeric Input with enhanced animations"""

    value_changed = Signal(float)  # Emitted when numeric value changes

    def __init__(self, parent: Optional[QWidget] = None,
                 minimum: float = 0, maximum: float = 100,
                 decimals: int = 2, placeholder: str = "Enter number"):
        super().__init__(parent, placeholder)

        self._minimum = minimum
        self._maximum = maximum
        self._decimals = decimals
        self._current_value = minimum

        # Connect text change to validation
        self.textChanged.connect(self._on_text_changed)

        # Add reveal animation when created
        FluentRevealEffect.scale_in(self, 200)

        # Set initial value
        self.set_value(minimum)

    def _on_text_changed(self, text: str):
        """Handle text change with validation and animation"""
        try:
            if text.strip():
                value = float(text)
                # Clamp value to range
                value = max(self._minimum, min(self._maximum, value))

                if value != self._current_value:
                    self._current_value = value
                    # Apply subtle pulse for valid input
                    FluentMicroInteraction.pulse_animation(self, 1.02)
                    self.value_changed.emit(value)
            else:
                self._current_value = self._minimum

        except ValueError:
            # Apply shake animation for invalid input
            FluentMicroInteraction.shake_animation(self, 5)

    def set_value(self, value: float):
        """Set numeric value with animation"""
        value = max(self._minimum, min(self._maximum, value))
        if value != self._current_value:
            self._current_value = value

            # Format value based on decimal places
            if self._decimals == 0:
                text = str(int(value))
            else:
                text = f"{value:.{self._decimals}f}"

            # Set text with fade animation
            fade_out = FluentTransition.create_transition(
                self, FluentTransition.FADE, 100, FluentTransition.EASE_SMOOTH)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.8)

            def set_text_and_fade_in():
                self.setText(text)
                fade_in = FluentTransition.create_transition(
                    self, FluentTransition.FADE, 100, FluentTransition.EASE_SMOOTH)
                fade_in.setStartValue(0.8)
                fade_in.setEndValue(1.0)
                fade_in.start()

            fade_out.finished.connect(set_text_and_fade_in)
            fade_out.start()

    def get_value(self) -> float:
        """Get current numeric value"""
        return self._current_value

    def set_range(self, minimum: float, maximum: float):
        """Set value range"""
        self._minimum = minimum
        self._maximum = maximum
        # Re-validate current value
        self.set_value(self._current_value)
