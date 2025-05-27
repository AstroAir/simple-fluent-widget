"""
Fluent Design Style Numeric Adjuster
"""

from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox, QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal, QPropertyAnimation, QByteArray
from PySide6.QtGui import QWheelEvent
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional


class FluentSpinBox(QSpinBox):
    """**Fluent Design Style Integer Adjuster**"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._is_hovered = False
        self._value_animation = None

        self.setMinimumHeight(32)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)

        self._setup_style()
        self._setup_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QSpinBox {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()}40;
            }}
            QSpinBox:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
            }}
            QSpinBox:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
                padding: 5px 7px;
            }}
            QSpinBox::up-button {{
                background-color: transparent;
                border: none;
                width: 20px;
                border-radius: 2px;
                margin-right: 2px;
            }}
            QSpinBox::up-button:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QSpinBox::up-button:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QSpinBox::down-button {{
                background-color: transparent;
                border: none;
                width: 20px;
                border-radius: 2px;
                margin-right: 2px;
            }}
            QSpinBox::down-button:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QSpinBox::down-button:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QSpinBox::up-arrow {{
                image: url(:/icons/chevron_up.svg);
                width: 10px;
                height: 10px;
            }}
            QSpinBox::down-arrow {{
                image: url(:/icons/chevron_down.svg);
                width: 10px;
                height: 10px;
            }}
            QSpinBox:disabled {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_disabled').name()};
                border-color: {theme.get_color('text_disabled').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup animations"""
        self._value_animation = QPropertyAnimation(self, QByteArray(b"value"))
        self._value_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._value_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def set_value_animated(self, value: int):
        """**Set value with animation**"""
        if self._value_animation:
            self._value_animation.setStartValue(self.value())
            self._value_animation.setEndValue(value)
            self._value_animation.start()
        else:
            self.setValue(value)

    def enterEvent(self, event):
        """Hover enter"""
        self._is_hovered = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave"""
        self._is_hovered = False
        super().leaveEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Mouse wheel event"""
        if self.hasFocus():
            # Only respond to wheel events when focused
            super().wheelEvent(event)

    def _on_theme_changed(self, theme_name: str):
        """Theme change handler"""
        # Suppress unused parameter warning
        _ = theme_name
        self._setup_style()


class FluentDoubleSpinBox(QDoubleSpinBox):
    """**Fluent Design Style Floating Point Adjuster**"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._is_hovered = False
        self._value_animation = None

        self.setMinimumHeight(32)
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.UpDownArrows)
        self.setDecimals(2)

        self._setup_style()
        self._setup_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QDoubleSpinBox {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()}40;
            }}
            QDoubleSpinBox:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
            }}
            QDoubleSpinBox:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
                padding: 5px 7px;
            }}
            QDoubleSpinBox::up-button {{
                background-color: transparent;
                border: none;
                width: 20px;
                border-radius: 2px;
                margin-right: 2px;
            }}
            QDoubleSpinBox::up-button:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QDoubleSpinBox::down-button {{
                background-color: transparent;
                border: none;
                width: 20px;
                border-radius: 2px;
                margin-right: 2px;
            }}
            QDoubleSpinBox::down-button:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QDoubleSpinBox::up-arrow {{
                image: url(:/icons/chevron_up.svg);
                width: 10px;
                height: 10px;
            }}
            QDoubleSpinBox::down-arrow {{
                image: url(:/icons/chevron_down.svg);
                width: 10px;
                height: 10px;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup animations"""
        self._value_animation = QPropertyAnimation(self, QByteArray(b"value"))
        self._value_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._value_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def set_value_animated(self, value: float):
        """**Set value with animation**"""
        if self._value_animation:
            self._value_animation.setStartValue(self.value())
            self._value_animation.setEndValue(value)
            self._value_animation.start()
        else:
            self.setValue(value)

    def enterEvent(self, event):
        """Hover enter"""
        self._is_hovered = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave"""
        self._is_hovered = False
        super().leaveEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Mouse wheel event"""
        if self.hasFocus():
            super().wheelEvent(event)

    def _on_theme_changed(self, theme_name: str):
        """Theme change handler"""
        # Suppress unused parameter warning
        _ = theme_name
        self._setup_style()


class FluentNumberInput(QWidget):
    """**Enhanced Numeric Input**"""

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

    def _setup_ui(self):
        """Setup UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Decrease button
        self.decrease_btn = QPushButton("−")
        self.decrease_btn.setFixedSize(32, 32)
        self.decrease_btn.clicked.connect(self._decrease_value)

        # Input box
        if self._decimals > 0:
            self.spin_box = FluentDoubleSpinBox()
            self.spin_box.setDecimals(self._decimals)
        else:
            self.spin_box = FluentSpinBox()

        # Convert float to int for QSpinBox
        if isinstance(self.spin_box, FluentSpinBox):
            self.spin_box.setRange(int(self._minimum), int(self._maximum))
            self.spin_box.setSingleStep(int(self._step))
            self.spin_box.setValue(int(self._value))
        else:
            self.spin_box.setRange(self._minimum, self._maximum)
            self.spin_box.setSingleStep(self._step)
            self.spin_box.setValue(self._value)

        self.spin_box.valueChanged.connect(self._on_value_changed)

        # Increase button
        self.increase_btn = QPushButton("+")
        self.increase_btn.setFixedSize(32, 32)
        self.increase_btn.clicked.connect(self._increase_value)

        layout.addWidget(self.decrease_btn)
        layout.addWidget(self.spin_box)
        layout.addWidget(self.increase_btn)

        self._setup_button_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_button_style(self):
        """Setup button style"""
        theme = theme_manager

        button_style = f"""
            QPushButton {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                color: {theme.get_color('text_primary').name()};
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('primary').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
        """

        self.decrease_btn.setStyleSheet(button_style)
        self.increase_btn.setStyleSheet(button_style)

    def _decrease_value(self):
        """Decrease value"""
        current_value = self.spin_box.value()
        new_value = max(self._minimum, current_value - self._step)
        if isinstance(self.spin_box, FluentSpinBox):
            self.spin_box.set_value_animated(int(new_value))
        else:
            self.spin_box.set_value_animated(new_value)

    def _increase_value(self):
        """Increase value"""
        current_value = self.spin_box.value()
        new_value = min(self._maximum, current_value + self._step)
        if isinstance(self.spin_box, FluentSpinBox):
            self.spin_box.set_value_animated(int(new_value))
        else:
            self.spin_box.set_value_animated(new_value)

    def _on_value_changed(self, value):
        """Value change handler"""
        self._value = value
        self.value_changed.emit(value)

    def get_value(self) -> float:
        """**Get current value**"""
        return self._value

    def set_value(self, value: float):
        """**Set value**"""
        if isinstance(self.spin_box, FluentSpinBox):
            self.spin_box.setValue(int(value))
        else:
            self.spin_box.setValue(value)

    def set_range(self, minimum: float, maximum: float):
        """**Set range**"""
        self._minimum = minimum
        self._maximum = maximum
        if isinstance(self.spin_box, FluentSpinBox):
            self.spin_box.setRange(int(minimum), int(maximum))
        else:
            self.spin_box.setRange(minimum, maximum)

    def set_step(self, step: float):
        """**Set step**"""
        self._step = step
        if isinstance(self.spin_box, FluentSpinBox):
            self.spin_box.setSingleStep(int(step))
        else:
            self.spin_box.setSingleStep(step)

    def _on_theme_changed(self, theme_name: str):
        """Theme change handler"""
        # Suppress unused parameter warning
        _ = theme_name
        self._setup_button_style()
