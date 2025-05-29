"""
Fluent Design Style Checkbox and Radio Button Components
Enhanced with improved animations and consistent styling patterns
"""

from PySide6.QtWidgets import QCheckBox, QRadioButton, QWidget, QButtonGroup, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from core.theme import theme_manager
from core.enhanced_animations import (FluentMicroInteraction, FluentTransition,
                                      FluentStateTransition, FluentRevealEffect)
from typing import Optional, List


class FluentCheckBox(QCheckBox):
    """Fluent Design Style Checkbox with enhanced animations"""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self._state_transition = FluentStateTransition(self)
        self._is_hovered = False
        self._is_checked = False

        self._setup_enhanced_animations()
        self._setup_style()

        # Connect signals
        self.stateChanged.connect(self._on_state_changed)
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation effects"""
        # Setup state transitions for different checkbox states
        self._state_transition.addState("normal", {
            "minimumHeight": 20,
        })

        self._state_transition.addState("hovered", {
            "minimumHeight": 22,
        }, duration=150, easing=FluentTransition.EASE_SMOOTH)

        self._state_transition.addState("checked", {
            "minimumHeight": 20,
        }, duration=200, easing=FluentTransition.EASE_SPRING)

    def _setup_style(self):
        """Setup checkbox style with enhanced visual effects"""
        current_theme = theme_manager

        style_sheet = f"""
            FluentCheckBox {{
                font-size: 14px;
                color: {current_theme.get_color('text_primary').name()};
                spacing: 8px;
                min-height: 20px;
            }}
            FluentCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid {current_theme.get_color('border').name()};
                background-color: {current_theme.get_color('surface').name()};
            }}
            FluentCheckBox::indicator:hover {{
                border-color: {current_theme.get_color('primary').name()};
                background-color: {current_theme.get_color('accent_light').name()};
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            FluentCheckBox::indicator:checked {{
                background-color: {current_theme.get_color('primary').name()};
                border-color: {current_theme.get_color('primary').name()};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEwIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+DQo8cGF0aCBkPSJNOC41IDFMMy41IDZMMSA0IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+DQo8L3N2Zz4NCg==);
            }}
            FluentCheckBox::indicator:checked:hover {{
                background-color: {current_theme.get_color('primary').lighter(110).name()};
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            }}
            FluentCheckBox::indicator:indeterminate {{
                background-color: {current_theme.get_color('primary').name()};
                border-color: {current_theme.get_color('primary').name()};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOCIgaGVpZ2h0PSIyIiB2aWV3Qm94PSIwIDAgOCAyIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cGF0aCBkPSJNMSAxSDciIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KPC9zdmc+);
            }}
            FluentCheckBox::indicator:disabled {{
                background-color: {current_theme.get_color('surface').name()};
                border-color: {current_theme.get_color('border').name()};
            }}
            FluentCheckBox:disabled {{
                color: {current_theme.get_color('text_disabled').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_state_changed(self, state):
        """Handle checkbox state change with enhanced animations"""
        self._is_checked = (state == Qt.CheckState.Checked)

        # Apply check animation with micro-interaction
        if self._is_checked:
            FluentMicroInteraction.button_press(self, 0.95)
            self._state_transition.transitionTo("checked")
            # Add a subtle pulse effect
            FluentMicroInteraction.pulse_animation(self, 1.05)
        else:
            self._state_transition.transitionTo(
                "normal" if not self._is_hovered else "hovered")

    def _on_theme_changed(self, theme_name: str):
        """Handle theme change"""
        self._setup_style()

    def enterEvent(self, event):
        """Hover enter event with enhanced animations"""
        self._is_hovered = True

        # Apply hover glow effect
        FluentMicroInteraction.hover_glow(self, 0.05)

        # Transition to hover state
        if not self._is_checked:
            self._state_transition.transitionTo("hovered")

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave event"""
        self._is_hovered = False

        # Transition back to normal state
        if not self._is_checked:
            self._state_transition.transitionTo("normal")

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Mouse press event with micro-interaction"""
        # Apply button press micro-interaction
        FluentMicroInteraction.scale_animation(self, 0.9)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Mouse release event with ripple effect"""
        # Create ripple effect at the checkbox indicator
        FluentMicroInteraction.ripple_effect(self)

        super().mouseReleaseEvent(event)


class FluentRadioButton(QRadioButton):
    """Fluent Design Style Radio Button with enhanced animations"""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self._state_transition = FluentStateTransition(self)
        self._is_hovered = False
        self._is_selected = False

        self._setup_enhanced_animations()
        self._setup_style()

        # Connect signals
        self.toggled.connect(self._on_toggled)
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation effects"""
        # Setup state transitions for different radio button states
        self._state_transition.addState("normal", {
            "minimumHeight": 20,
        })

        self._state_transition.addState("hovered", {
            "minimumHeight": 22,
        }, duration=150, easing=FluentTransition.EASE_SMOOTH)

        self._state_transition.addState("selected", {
            "minimumHeight": 20,
        }, duration=200, easing=FluentTransition.EASE_SPRING)

    def _setup_style(self):
        """Setup radio button style with enhanced visual effects"""
        current_theme = theme_manager

        style_sheet = f"""
            FluentRadioButton {{
                font-size: 14px;
                color: {current_theme.get_color('text_primary').name()};
                spacing: 8px;
                min-height: 20px;
            }}
            FluentRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid {current_theme.get_color('border').name()};
                background-color: {current_theme.get_color('surface').name()};
            }}
            FluentRadioButton::indicator:hover {{
                border-color: {current_theme.get_color('primary').name()};
                background-color: {current_theme.get_color('accent_light').name()};
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            FluentRadioButton::indicator:checked {{
                background-color: {current_theme.get_color('primary').name()};
                border-color: {current_theme.get_color('primary').name()};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNiIgaGVpZ2h0PSI2IiB2aWV3Qm94PSIwIDAgNiA2IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8Y2lyY2xlIGN4PSIzIiBjeT0iMyIgcj0iMyIgZmlsbD0id2hpdGUiLz4KPC9zdmc+);
            }}
            FluentRadioButton::indicator:checked:hover {{
                background-color: {current_theme.get_color('primary').lighter(110).name()};
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            }}
            FluentRadioButton::indicator:disabled {{
                background-color: {current_theme.get_color('surface').name()};
                border-color: {current_theme.get_color('border').name()};
            }}
            FluentRadioButton:disabled {{
                color: {current_theme.get_color('text_disabled').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_toggled(self, checked: bool):
        """Handle radio button toggle with enhanced animations"""
        self._is_selected = checked

        if checked:
            # Apply selection animation with micro-interaction
            FluentMicroInteraction.scale_animation(self, 0.95)
            self._state_transition.transitionTo("selected")
            # Add a subtle pulse effect
            FluentMicroInteraction.pulse_animation(self, 1.05)
        else:
            self._state_transition.transitionTo(
                "normal" if not self._is_hovered else "hovered")

    def _on_theme_changed(self, theme_name: str):
        """Handle theme change"""
        self._setup_style()

    def enterEvent(self, event):
        """Hover enter event with enhanced animations"""
        self._is_hovered = True

        # Apply hover glow effect
        FluentMicroInteraction.hover_glow(self, 0.05)

        # Transition to hover state
        if not self._is_selected:
            self._state_transition.transitionTo("hovered")

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave event"""
        self._is_hovered = False

        # Transition back to normal state
        if not self._is_selected:
            self._state_transition.transitionTo("normal")

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Mouse press event with micro-interaction"""
        # Apply button press micro-interaction
        FluentMicroInteraction.scale_animation(self, 0.9)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Mouse release event with ripple effect"""
        # Create ripple effect at the radio button indicator
        FluentMicroInteraction.ripple_effect(self)

        super().mouseReleaseEvent(event)


class FluentRadioGroup(QWidget):
    """Radio Button Group with enhanced animations"""

    selection_changed = Signal(int, str)  # index, text

    def __init__(self, options: List[str], parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._button_group = QButtonGroup(self)
        self._radio_buttons: List[FluentRadioButton] = []
        self._selected_index = -1

        self._setup_radio_buttons(options)
        self._button_group.buttonToggled.connect(self._on_button_toggled)

        # Add reveal animation when created
        FluentRevealEffect.fade_in(self, 300)

    def _setup_radio_buttons(self, options: List[str]):
        """Setup radio buttons with enhanced animations"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        for i, option in enumerate(options):
            radio_button = FluentRadioButton(option, self)
            self._radio_buttons.append(radio_button)
            self._button_group.addButton(radio_button, i)
            layout.addWidget(radio_button)

            # Add staggered reveal animation
            FluentRevealEffect.slide_in(radio_button, 200 + i * 50, "up")

    def _on_button_toggled(self, button, checked: bool):
        """Handle button toggle with enhanced animations"""
        if checked:
            self._selected_index = self._button_group.id(button)
            text = button.text()

            # Create smooth transition animation between selections
            if hasattr(self, '_previous_button') and self._previous_button != button:
                # Fade out previous selection
                fade_out = FluentTransition.create_transition(
                    self._previous_button, FluentTransition.FADE, 150,
                    FluentTransition.EASE_SMOOTH)
                fade_out.setStartValue(1.0)
                fade_out.setEndValue(0.8)
                fade_out.start()

                # Fade in new selection
                fade_in = FluentTransition.create_transition(
                    button, FluentTransition.FADE, 150,
                    FluentTransition.EASE_SMOOTH)
                fade_in.setStartValue(0.8)
                fade_in.setEndValue(1.0)
                fade_in.start()

            self._previous_button = button
            self.selection_changed.emit(self._selected_index, text)

    def set_selected(self, index: int):
        """Set selected radio button with animation"""
        if 0 <= index < len(self._radio_buttons):
            self._radio_buttons[index].setChecked(True)

    def get_selected_index(self) -> int:
        """Get selected radio button index"""
        return self._selected_index

    def get_selected_text(self) -> str:
        """Get selected radio button text"""
        if 0 <= self._selected_index < len(self._radio_buttons):
            return self._radio_buttons[self._selected_index].text()
        return ""
