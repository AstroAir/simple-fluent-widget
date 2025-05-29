"""
Fluent Design Style Numeric Adjuster
"""

from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox, QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal, QPropertyAnimation, QByteArray
from PySide6.QtGui import QWheelEvent
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import FluentRevealEffect, FluentMicroInteraction, FluentTransition
from typing import Optional


class FluentSpinBox(QSpinBox):
    """Fluent Design Style Integer Adjuster with Enhanced Animations"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._is_hovered = False
        self._is_focused = False
        self._value_animation = None
        self._hover_animation = None
        self._focus_animation = None

        self.setMinimumHeight(36)  # Slightly taller for better touch targets
        self.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)

        self._setup_style()
        self._setup_animations()

        # Connect signals for enhanced feedback
        self.valueChanged.connect(self._on_value_changed)

        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Initial reveal animation
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_MEDIUM)

    def _setup_style(self):
        """Setup enhanced visual styling"""
        theme = theme_manager

        style_sheet = f"""
            QSpinBox {{
                background-color: {theme.get_color('surface').name()};
                border: 2px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 500;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()}40;
                transition: all 0.2s ease;
            }}
            QSpinBox:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transform: translateY(-1px);
            }}
            QSpinBox:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
                background-color: {theme.get_color('surface').lighter(105).name()};
                box-shadow: 0 0 0 3px {theme.get_color('primary').name()}20;
                outline: none;
            }}
            QSpinBox::up-button {{
                background-color: transparent;
                border: none;
                width: 24px;
                height: 18px;
                border-radius: 3px;
                margin: 2px;
                transition: all 0.2s ease;
            }}
            QSpinBox::up-button:hover {{
                background-color: {theme.get_color('primary').lighter(130).name()};
                transform: scale(1.1);
            }}
            QSpinBox::up-button:pressed {{
                background-color: {theme.get_color('primary').name()};
                transform: scale(0.95);
            }}
            QSpinBox::down-button {{
                background-color: transparent;
                border: none;
                width: 24px;
                height: 18px;
                border-radius: 3px;
                margin: 2px;
                transition: all 0.2s ease;
            }}
            QSpinBox::down-button:hover {{
                background-color: {theme.get_color('primary').lighter(130).name()};
                transform: scale(1.1);
            }}
            QSpinBox::down-button:pressed {{
                background-color: {theme.get_color('primary').name()};
                transform: scale(0.95);
            }}
            QSpinBox::up-arrow {{
                image: url(:/icons/chevron_up.svg);
                width: 12px;
                height: 12px;
            }}
            QSpinBox::down-arrow {{
                image: url(:/icons/chevron_down.svg);
                width: 12px;
                height: 12px;
            }}
            QSpinBox:disabled {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_disabled').name()};
                border-color: {theme.get_color('text_disabled').name()};
                opacity: 0.6;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup enhanced animations"""
        # Value change animation with smooth easing
        self._value_animation = QPropertyAnimation(self, QByteArray(b"value"))
        self._value_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._value_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)

        # Hover animation for subtle scaling
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentTransition.EASE_SPRING)

        # Focus animation for glow effect
        self._focus_animation = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self._focus_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._focus_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)

    def set_value_animated(self, value: int):
        """Set value with enhanced animation and feedback"""
        if self._value_animation:
            old_value = self.value()

            self._value_animation.setStartValue(old_value)
            self._value_animation.setEndValue(value)
            self._value_animation.start()

            # Add pulse effect for significant changes
            if abs(value - old_value) > 5:
                FluentMicroInteraction.pulse_animation(self, scale=1.05)
            elif abs(value - old_value) > 1:
                FluentMicroInteraction.scale_animation(self, scale=1.02)
        else:
            self.setValue(value)

    def _on_value_changed(self, value: int):
        """Handle value changes with micro-feedback"""
        # Add subtle feedback for value changes
        FluentMicroInteraction.scale_animation(self, scale=1.02)

    def enterEvent(self, event):
        """Enhanced hover enter with micro-interactions"""
        self._is_hovered = True

        # Add hover glow effect
        FluentMicroInteraction.hover_glow(self, intensity=0.1)

        # Subtle scale up on hover
        original_rect = self.geometry()
        hover_rect = original_rect.adjusted(-2, -1, 2, 1)

        if self._hover_animation:
            self._hover_animation.setStartValue(original_rect)
            self._hover_animation.setEndValue(hover_rect)
            self._hover_animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Enhanced hover leave with smooth transition"""
        self._is_hovered = False

        # Return to normal size
        current_rect = self.geometry()
        normal_rect = current_rect.adjusted(2, 1, -2, -1)

        if self._hover_animation:
            self._hover_animation.setStartValue(current_rect)
            self._hover_animation.setEndValue(normal_rect)
            self._hover_animation.start()

        super().leaveEvent(event)

    def focusInEvent(self, event):
        """Enhanced focus in with glow effect"""
        self._is_focused = True

        # Add focus reveal effect
        FluentRevealEffect.scale_in(
            self, duration=FluentAnimation.DURATION_FAST)

        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Enhanced focus out with smooth transition"""
        self._is_focused = False

        # Subtle fade effect when losing focus
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_FAST)

        super().focusOutEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Enhanced mouse wheel event with feedback"""
        if self.hasFocus():
            old_value = self.value()
            super().wheelEvent(event)
            new_value = self.value()

            # Add feedback for wheel changes
            if old_value != new_value:
                FluentMicroInteraction.scale_animation(self, scale=1.03)

    def stepBy(self, steps: int):
        """Enhanced step by with animation"""
        old_value = self.value()
        super().stepBy(steps)
        new_value = self.value()

        # Add feedback for button steps
        if old_value != new_value:
            if steps > 0:
                # Positive step - subtle upward animation
                FluentMicroInteraction.scale_animation(self, scale=1.02)
            else:
                # Negative step - subtle downward animation
                FluentMicroInteraction.scale_animation(self, scale=0.98)

    def _on_theme_changed(self, theme_name: str):
        """Enhanced theme change handler"""
        _ = theme_name  # Suppress unused parameter warning

        # Smooth transition when theme changes
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_MEDIUM)
        self._setup_style()


class FluentDoubleSpinBox(QDoubleSpinBox):
    """Fluent Design Style Floating Point Adjuster with Enhanced Animations"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._is_hovered = False
        self._is_focused = False
        self._value_animation = None
        self._hover_animation = None
        self._focus_animation = None

        self.setMinimumHeight(36)
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.UpDownArrows)
        self.setDecimals(2)

        self._setup_style()
        self._setup_animations()

        # Connect signals for enhanced feedback
        self.valueChanged.connect(self._on_value_changed)

        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Initial reveal animation
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_MEDIUM)

    def _setup_style(self):
        """Setup enhanced visual styling"""
        theme = theme_manager

        style_sheet = f"""
            QDoubleSpinBox {{
                background-color: {theme.get_color('surface').name()};
                border: 2px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 500;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()}40;
                transition: all 0.2s ease;
            }}
            QDoubleSpinBox:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transform: translateY(-1px);
            }}
            QDoubleSpinBox:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
                background-color: {theme.get_color('surface').lighter(105).name()};
                box-shadow: 0 0 0 3px {theme.get_color('primary').name()}20;
                outline: none;
            }}
            QDoubleSpinBox::up-button {{
                background-color: transparent;
                border: none;
                width: 24px;
                height: 18px;
                border-radius: 3px;
                margin: 2px;
                transition: all 0.2s ease;
            }}
            QDoubleSpinBox::up-button:hover {{
                background-color: {theme.get_color('primary').lighter(130).name()};
                transform: scale(1.1);
            }}
            QDoubleSpinBox::up-button:pressed {{
                background-color: {theme.get_color('primary').name()};
                transform: scale(0.95);
            }}
            QDoubleSpinBox::down-button {{
                background-color: transparent;
                border: none;
                width: 24px;
                height: 18px;
                border-radius: 3px;
                margin: 2px;
                transition: all 0.2s ease;
            }}
            QDoubleSpinBox::down-button:hover {{
                background-color: {theme.get_color('primary').lighter(130).name()};
                transform: scale(1.1);
            }}
            QDoubleSpinBox::down-button:pressed {{
                background-color: {theme.get_color('primary').name()};
                transform: scale(0.95);
            }}
            QDoubleSpinBox::up-arrow {{
                image: url(:/icons/chevron_up.svg);
                width: 12px;
                height: 12px;
            }}
            QDoubleSpinBox::down-arrow {{
                image: url(:/icons/chevron_down.svg);
                width: 12px;
                height: 12px;
            }}
            QDoubleSpinBox:disabled {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_disabled').name()};
                border-color: {theme.get_color('text_disabled').name()};
                opacity: 0.6;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup enhanced animations"""
        # Value change animation with smooth easing
        self._value_animation = QPropertyAnimation(self, QByteArray(b"value"))
        self._value_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._value_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)

        # Hover animation for subtle effects
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentTransition.EASE_SPRING)

    def set_value_animated(self, value: float):
        """Set value with enhanced animation and feedback"""
        if self._value_animation:
            old_value = self.value()

            self._value_animation.setStartValue(old_value)
            self._value_animation.setEndValue(value)
            self._value_animation.start()

            # Add pulse effect for significant changes
            if abs(value - old_value) > 5.0:
                FluentMicroInteraction.pulse_animation(self, scale=1.05)
            elif abs(value - old_value) > 0.5:
                FluentMicroInteraction.scale_animation(self, scale=1.02)
        else:
            self.setValue(value)

    def _on_value_changed(self, value: float):
        """Handle value changes with micro-feedback"""
        # Add subtle feedback for value changes
        FluentMicroInteraction.scale_animation(self, scale=1.02)

    def enterEvent(self, event):
        """Enhanced hover enter with micro-interactions"""
        self._is_hovered = True

        # Add hover glow effect
        FluentMicroInteraction.hover_glow(self, intensity=0.1)

        # Subtle scale up on hover
        original_rect = self.geometry()
        hover_rect = original_rect.adjusted(-2, -1, 2, 1)

        if self._hover_animation:
            self._hover_animation.setStartValue(original_rect)
            self._hover_animation.setEndValue(hover_rect)
            self._hover_animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Enhanced hover leave with smooth transition"""
        self._is_hovered = False

        # Return to normal size
        current_rect = self.geometry()
        normal_rect = current_rect.adjusted(2, 1, -2, -1)

        if self._hover_animation:
            self._hover_animation.setStartValue(current_rect)
            self._hover_animation.setEndValue(normal_rect)
            self._hover_animation.start()

        super().leaveEvent(event)

    def focusInEvent(self, event):
        """Enhanced focus in with glow effect"""
        self._is_focused = True
        FluentRevealEffect.scale_in(
            self, duration=FluentAnimation.DURATION_FAST)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Enhanced focus out with smooth transition"""
        self._is_focused = False
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_FAST)
        super().focusOutEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Enhanced mouse wheel event with feedback"""
        if self.hasFocus():
            old_value = self.value()
            super().wheelEvent(event)
            new_value = self.value()

            # Add feedback for wheel changes
            if abs(old_value - new_value) > 0.01:  # Account for floating point precision
                FluentMicroInteraction.scale_animation(self, scale=1.03)

    def stepBy(self, steps: int):
        """Enhanced step by with animation"""
        old_value = self.value()
        super().stepBy(steps)
        new_value = self.value()

        # Add feedback for button steps
        if abs(old_value - new_value) > 0.01:
            if steps > 0:
                FluentMicroInteraction.scale_animation(self, scale=1.02)
            else:
                FluentMicroInteraction.scale_animation(self, scale=0.98)

    def _on_theme_changed(self, theme_name: str):
        """Enhanced theme change handler"""
        _ = theme_name
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_MEDIUM)
        self._setup_style()


class FluentNumberInput(QWidget):
    """Enhanced Numeric Input with Animated Buttons"""

    value_changed = Signal(float)

    def __init__(self, parent: Optional[QWidget] = None,
                 minimum: float = 0.0, maximum: float = 100.0,
                 decimals: int = 2, step: float = 1.0):
        super().__init__(parent)

        self._minimum = minimum
        self._maximum = maximum
        self._decimals = decimals
        self._step = step
        self._value = minimum

        self._setup_ui()

        # Initial reveal animation
        FluentRevealEffect.scale_in(
            self, duration=FluentAnimation.DURATION_MEDIUM)

    def _setup_ui(self):
        """Setup enhanced UI with better animations"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # Enhanced decrease button
        self.decrease_btn = QPushButton("−")
        self.decrease_btn.setFixedSize(36, 36)
        self.decrease_btn.clicked.connect(self._decrease_value)
        self.decrease_btn.setToolTip("Decrease value")

        # Add enhanced interactions to decrease button
        self.decrease_btn.enterEvent = lambda event: self._on_button_hover(
            self.decrease_btn, event)
        self.decrease_btn.leaveEvent = lambda event: self._on_button_leave(
            self.decrease_btn, event)
        self.decrease_btn.mousePressEvent = lambda event: self._on_button_press(
            self.decrease_btn, event)

        # Enhanced input box
        if self._decimals > 0:
            self.spin_box = FluentDoubleSpinBox()
            self.spin_box.setDecimals(self._decimals)
        else:
            self.spin_box = FluentSpinBox()

        # Configure spinbox with type-appropriate values
        if isinstance(self.spin_box, FluentSpinBox):
            self.spin_box.setRange(int(self._minimum), int(self._maximum))
            self.spin_box.setSingleStep(int(self._step))
            self.spin_box.setValue(int(self._value))
        else:
            self.spin_box.setRange(self._minimum, self._maximum)
            self.spin_box.setSingleStep(self._step)
            self.spin_box.setValue(self._value)

        self.spin_box.valueChanged.connect(self._on_value_changed)

        # Enhanced increase button
        self.increase_btn = QPushButton("+")
        self.increase_btn.setFixedSize(36, 36)
        self.increase_btn.clicked.connect(self._increase_value)
        self.increase_btn.setToolTip("Increase value")

        # Add enhanced interactions to increase button
        self.increase_btn.enterEvent = lambda event: self._on_button_hover(
            self.increase_btn, event)
        self.increase_btn.leaveEvent = lambda event: self._on_button_leave(
            self.increase_btn, event)
        self.increase_btn.mousePressEvent = lambda event: self._on_button_press(
            self.increase_btn, event)

        layout.addWidget(self.decrease_btn)
        layout.addWidget(self.spin_box, 1)  # Give spinbox more space
        layout.addWidget(self.increase_btn)

        self._setup_button_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_button_hover(self, button: QPushButton, event):
        """Enhanced button hover effect"""
        FluentMicroInteraction.hover_glow(button, intensity=0.15)
        button.mousePressEvent(event)  # Call original

    def _on_button_leave(self, button: QPushButton, event):
        """Enhanced button leave effect"""
        button.leaveEvent(event)  # Call original

    def _on_button_press(self, button: QPushButton, event):
        """Enhanced button press effect"""
        FluentMicroInteraction.button_press(button, scale=0.9)
        button.mousePressEvent(event)  # Call original

    def _setup_button_style(self):
        """Setup enhanced button styling"""
        theme = theme_manager

        button_style = f"""
            QPushButton {{
                background-color: {theme.get_color('surface').name()};
                border: 2px solid {theme.get_color('border').name()};
                border-radius: 8px;
                font-size: 18px;
                font-weight: 600;
                color: {theme.get_color('text_primary').name()};
                transition: all 0.2s ease;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('primary').lighter(140).name()};
                border-color: {theme.get_color('primary').name()};
                color: {theme.get_color('on_primary').name()};
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('primary').name()};
                border-color: {theme.get_color('primary').darker(110).name()};
                color: {theme.get_color('on_primary').name()};
                transform: translateY(0px) scale(0.95);
                box-shadow: 0 1px 4px rgba(0,0,0,0.2);
            }}
            QPushButton:disabled {{
                background-color: {theme.get_color('surface_variant').name()};
                color: {theme.get_color('on_surface_variant').darker(120).name()};
                border-color: {theme.get_color('outline').name()};
                opacity: 0.6;
            }}
        """

        self.decrease_btn.setStyleSheet(button_style)
        self.increase_btn.setStyleSheet(button_style)

    def _decrease_value(self):
        """Decrease value with enhanced feedback"""
        current_value = self.spin_box.value()
        new_value = max(self._minimum, current_value - self._step)

        # Add directional feedback
        FluentMicroInteraction.scale_animation(self.decrease_btn, scale=0.9)

        if isinstance(self.spin_box, FluentSpinBox):
            self.spin_box.set_value_animated(int(new_value))
        else:
            self.spin_box.set_value_animated(new_value)

    def _increase_value(self):
        """Increase value with enhanced feedback"""
        current_value = self.spin_box.value()
        new_value = min(self._maximum, current_value + self._step)

        # Add directional feedback
        FluentMicroInteraction.scale_animation(self.increase_btn, scale=0.9)

        if isinstance(self.spin_box, FluentSpinBox):
            self.spin_box.set_value_animated(int(new_value))
        else:
            self.spin_box.set_value_animated(new_value)

    def _on_value_changed(self, value):
        """Enhanced value change handler"""
        old_value = self._value
        self._value = value

        # Add celebration effect for significant positive changes
        if value > old_value and abs(value - old_value) >= self._step * 5:
            FluentMicroInteraction.pulse_animation(self.spin_box, scale=1.05)
        elif value != old_value:
            FluentMicroInteraction.scale_animation(self.spin_box, scale=1.02)

        self.value_changed.emit(value)

    def get_value(self) -> float:
        """Get current value"""
        return self._value

    def set_value(self, value: float):
        """Set value with animation"""
        if isinstance(self.spin_box, FluentSpinBox):
            self.spin_box.set_value_animated(int(value))
        else:
            self.spin_box.set_value_animated(value)

    def set_range(self, minimum: float, maximum: float):
        """Set range with validation and feedback"""
        self._minimum = minimum
        self._maximum = maximum

        # Add feedback for range changes
        FluentRevealEffect.scale_in(
            self, duration=FluentAnimation.DURATION_FAST)

        if isinstance(self.spin_box, FluentSpinBox):
            self.spin_box.setRange(int(minimum), int(maximum))
        else:
            self.spin_box.setRange(minimum, maximum)

    def set_step(self, step: float):
        """Set step with validation"""
        self._step = step
        if isinstance(self.spin_box, FluentSpinBox):
            self.spin_box.setSingleStep(int(step))
        else:
            self.spin_box.setSingleStep(step)

    def set_enabled(self, enabled: bool):
        """Set enabled state with smooth transition"""
        super().setEnabled(enabled)

        # Add visual feedback for state changes
        if enabled:
            FluentRevealEffect.fade_in(
                self, duration=FluentAnimation.DURATION_MEDIUM)
        else:
            # Subtle fade out effect for disabled state
            FluentRevealEffect.fade_in(
                self, duration=FluentAnimation.DURATION_FAST)

    def _on_theme_changed(self, theme_name: str):
        """Enhanced theme change handler"""
        _ = theme_name

        # Smooth theme transition
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_MEDIUM)
        self._setup_button_style()
