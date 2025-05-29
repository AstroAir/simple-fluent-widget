"""
Fluent Design Style Button Component
Enhanced with improved animations and consistent styling patterns
"""

from PySide6.QtWidgets import QPushButton, QWidget
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
from core.theme import theme_manager
from core.enhanced_base import FluentStandardButton
from core.enhanced_animations import (FluentMicroInteraction, FluentTransition,
                                      FluentStateTransition, FluentRevealEffect)
from typing import Optional


class FluentButton(FluentStandardButton):
    """Enhanced Fluent Design Style Button

    Uses enhanced animations for modern micro-interactions and state transitions.
    """

    class ButtonStyle:
        PRIMARY = "primary"
        SECONDARY = "secondary"
        ACCENT = "accent"
        SUBTLE = "subtle"
        OUTLINE = "outline"

    def __init__(self, text: str = "", parent: Optional[QWidget] = None,
                 style: Optional[str] = None, icon: Optional[QIcon] = None):
        # Use default style if none provided
        if style is None:
            style = self.ButtonStyle.PRIMARY

        # Use FluentStandardButton constructor with proper parameters
        super().__init__(text, icon, (None, None), parent)

        self._button_style = style
        self._state_transition = FluentStateTransition(self)
        self._is_hovered = False
        self._is_pressed = False

        # Setup enhanced animations and interactions
        self._setup_enhanced_animations()
        self._apply_style()

        # Connect to theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation effects"""
        # Setup state transitions for different button states
        self._state_transition.addState("normal", {
            "minimumHeight": 32,
        })

        self._state_transition.addState("hovered", {
            "minimumHeight": 34,
        }, duration=150, easing=FluentTransition.EASE_SMOOTH)

        self._state_transition.addState("pressed", {
            "minimumHeight": 30,
        }, duration=100, easing=FluentTransition.EASE_CRISP)

    def set_style(self, style: str):
        """Set button style with enhanced animations"""
        if self._button_style != style:
            old_style = self._button_style
            self._button_style = style

            # Create smooth transition between styles
            transition = FluentTransition.create_transition(
                self, FluentTransition.FADE, 200, FluentTransition.EASE_SMOOTH)
            transition.setStartValue(1.0)
            transition.setEndValue(0.8)

            def apply_new_style():
                self._apply_style()
                # Fade back in
                fade_in = FluentTransition.create_transition(
                    self, FluentTransition.FADE, 200, FluentTransition.EASE_SMOOTH)
                fade_in.setStartValue(0.8)
                fade_in.setEndValue(1.0)
                fade_in.start()

            transition.finished.connect(apply_new_style)
            transition.start()

    def _apply_style(self):
        """Apply button style with enhanced visual effects"""
        theme = theme_manager

        if self._button_style == self.ButtonStyle.PRIMARY:
            self.setStyleSheet(f"""
                FluentButton {{
                    background-color: {theme.get_color('primary').name()};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 500;
                    min-height: 32px;
                }}
                FluentButton:hover {{
                    background-color: {theme.get_color('primary').lighter(110).name()};
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                }}
                FluentButton:pressed {{
                    background-color: {theme.get_color('primary').darker(110).name()};
                }}
                FluentButton:disabled {{
                    background-color: {theme.get_color('surface').name()};
                    color: {theme.get_color('text_disabled').name()};
                }}
            """)
        elif self._button_style == self.ButtonStyle.SECONDARY:
            self.setStyleSheet(f"""
                FluentButton {{
                    background-color: {theme.get_color('surface').name()};
                    color: {theme.get_color('text_primary').name()};
                    border: 1px solid {theme.get_color('border').name()};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 400;
                    min-height: 32px;
                }}
                FluentButton:hover {{
                    background-color: {theme.get_color('accent_light').name()};
                    border-color: {theme.get_color('primary').name()};
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }}
                FluentButton:pressed {{
                    background-color: {theme.get_color('accent_medium').name()};
                }}
                FluentButton:disabled {{
                    background-color: {theme.get_color('surface').name()};
                    color: {theme.get_color('text_disabled').name()};
                    border-color: {theme.get_color('border').name()};
                }}
            """)
        elif self._button_style == self.ButtonStyle.ACCENT:
            self.setStyleSheet(f"""
                FluentButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {theme.get_color('primary').lighter(110).name()},
                        stop:1 {theme.get_color('primary').name()});
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 500;
                    min-height: 32px;
                }}
                FluentButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {theme.get_color('primary').lighter(120).name()},
                        stop:1 {theme.get_color('primary').lighter(110).name()});
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }}
                FluentButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {theme.get_color('primary').name()},
                        stop:1 {theme.get_color('primary').darker(110).name()});
                }}
                FluentButton:disabled {{
                    background-color: {theme.get_color('surface').name()};
                    color: {theme.get_color('text_disabled').name()};
                }}
            """)
        elif self._button_style == self.ButtonStyle.SUBTLE:
            self.setStyleSheet(f"""
                FluentButton {{
                    background-color: transparent;
                    color: {theme.get_color('text_primary').name()};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 400;
                    min-height: 32px;
                }}
                FluentButton:hover {{
                    background-color: {theme.get_color('accent_light').name()};
                }}
                FluentButton:pressed {{
                    background-color: {theme.get_color('accent_medium').name()};
                }}
                FluentButton:disabled {{
                    color: {theme.get_color('text_disabled').name()};
                }}
            """)
        elif self._button_style == self.ButtonStyle.OUTLINE:
            self.setStyleSheet(f"""
                FluentButton {{
                    background-color: transparent;
                    color: {theme.get_color('primary').name()};
                    border: 1px solid {theme.get_color('primary').name()};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 400;
                    min-height: 32px;
                }}
                FluentButton:hover {{
                    background-color: {theme.get_color('primary').name()};
                    color: white;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                FluentButton:pressed {{
                    background-color: {theme.get_color('primary').darker(110).name()};
                }}
                FluentButton:disabled {{
                    color: {theme.get_color('text_disabled').name()};
                    border-color: {theme.get_color('border').name()};
                }}
            """)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._apply_style()

    def enterEvent(self, event):
        """Hover enter event with enhanced animations"""
        self._is_hovered = True

        # Apply hover glow effect
        FluentMicroInteraction.hover_glow(self, 0.1)

        # Transition to hover state
        self._state_transition.transitionTo("hovered")

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave event"""
        self._is_hovered = False

        # Transition back to normal state
        self._state_transition.transitionTo("normal")

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Mouse press event with micro-interaction"""
        self._is_pressed = True

        # Apply button press micro-interaction
        FluentMicroInteraction.button_press(self, 0.95)

        # Transition to pressed state
        self._state_transition.transitionTo("pressed")

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Mouse release event"""
        self._is_pressed = False

        # Create ripple effect
        FluentMicroInteraction.ripple_effect(self)

        # Return to hover or normal state
        if self._is_hovered:
            self._state_transition.transitionTo("hovered")
        else:
            self._state_transition.transitionTo("normal")

        super().mouseReleaseEvent(event)


class FluentIconButton(FluentButton):
    """Fluent Button with Icon and enhanced animations"""

    def __init__(self, icon: QIcon, text: str = "",
                 parent: Optional[QWidget] = None,
                 style: Optional[str] = None):
        if style is None:
            style = FluentButton.ButtonStyle.PRIMARY
        super().__init__(text, parent, style, icon)

        # Setup icon size based on text height
        height = self.fontMetrics().height()
        self.setIconSize(QSize(height, height))

        # Add reveal animation when created
        FluentRevealEffect.reveal_scale(self, 100)


class FluentToggleButton(FluentButton):
    """Toggle Button with enhanced state transitions"""

    toggled = Signal(bool)

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent, FluentButton.ButtonStyle.SECONDARY)
        self.setCheckable(True)
        self._is_toggled = False

        # Connect click signal
        self.clicked.connect(self._on_clicked)

        # Setup toggle-specific state transitions
        self._setup_toggle_animations()

    def _setup_toggle_animations(self):
        """Setup toggle-specific animations"""
        # Override state transitions for toggle behavior
        self._state_transition.addState("toggled", {
            "minimumHeight": 32,
        }, duration=200, easing=FluentTransition.EASE_SPRING)

    def _on_clicked(self):
        """Handle click with smooth toggle animation"""
        self._is_toggled = self.isChecked()

        # Create smooth transition between toggle states
        if self._is_toggled:
            # Transition to primary style
            self.set_style(FluentButton.ButtonStyle.PRIMARY)
            self._state_transition.transitionTo("toggled")
        else:
            # Transition to secondary style
            self.set_style(FluentButton.ButtonStyle.SECONDARY)
            self._state_transition.transitionTo("normal")

        self.toggled.emit(self._is_toggled)

    def set_toggled(self, toggled: bool):
        """Set toggle state with animation"""
        if self._is_toggled != toggled:
            self._is_toggled = toggled
            self.setChecked(toggled)

            # Animate the toggle change
            self._on_clicked()
