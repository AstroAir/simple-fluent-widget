"""
Fluent Design Style Checkbox and Radio Button Components
"""

from PySide6.QtWidgets import QCheckBox, QRadioButton, QWidget, QButtonGroup
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QRect, QByteArray
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPaintEvent
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional, List


class FluentCheckBox(QCheckBox):
    """Fluent Design Style Checkbox"""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self._check_animation = None
        self._is_hovered = False

        self._setup_style()
        self._setup_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup checkbox style"""
        theme = theme_manager

        style_sheet = f"""
            FluentCheckBox {{
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                spacing: 8px;
            }}
            FluentCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 2px;
                border: 1px solid {theme.get_color('border').name()};
                background-color: {theme.get_color('surface').name()};
            }}
            FluentCheckBox::indicator:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
            }}
            FluentCheckBox::indicator:checked {{
                background-color: {theme.get_color('primary').name()};
                border-color: {theme.get_color('primary').name()};
                image: url(:/icons/check.svg);
            }}
            FluentCheckBox::indicator:checked:hover {{
                background-color: {theme.get_color('primary').darker(110).name()};
            }}
            FluentCheckBox::indicator:indeterminate {{
                background-color: {theme.get_color('primary').name()};
                border-color: {theme.get_color('primary').name()};
                image: url(:/icons/indeterminate.svg);
            }}
            FluentCheckBox:disabled {{
                color: {theme.get_color('text_disabled').name()};
            }}
            FluentCheckBox::indicator:disabled {{
                border-color: {theme.get_color('text_disabled').name()};
                background-color: {theme.get_color('background').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup animations"""
        self.stateChanged.connect(self._on_state_changed)

    def _on_state_changed(self, state: int):
        """Handle state change animation"""
        if not self._check_animation:
            self._check_animation = QPropertyAnimation(
                self, QByteArray(b"geometry"))
            self._check_animation.setDuration(FluentAnimation.DURATION_FAST)
            self._check_animation.setEasingCurve(FluentAnimation.EASE_OUT)

        # Add subtle scale animation effect
        current_rect = self.geometry()
        if state == Qt.CheckState.Checked.value:
            # Animation when checked
            self._check_animation.setStartValue(current_rect)
            self._check_animation.setEndValue(current_rect)

    def enterEvent(self, event):
        """Hover enter"""
        self._is_hovered = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave"""
        self._is_hovered = False
        super().leaveEvent(event)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._setup_style()


class FluentRadioButton(QRadioButton):
    """Fluent Design Style Radio Button"""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self._is_hovered = False
        self._select_animation = None

        self._setup_style()
        self._setup_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup radio button style"""
        theme = theme_manager

        style_sheet = f"""
            FluentRadioButton {{
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                spacing: 8px;
            }}
            FluentRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 1px solid {theme.get_color('border').name()};
                background-color: {theme.get_color('surface').name()};
            }}
            FluentRadioButton::indicator:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
            }}
            FluentRadioButton::indicator:checked {{
                background-color: {theme.get_color('primary').name()};
                border-color: {theme.get_color('primary').name()};
            }}
            FluentRadioButton::indicator:checked:hover {{
                background-color: {theme.get_color('primary').darker(110).name()};
            }}
            FluentRadioButton:disabled {{
                color: {theme.get_color('text_disabled').name()};
            }}
            FluentRadioButton::indicator:disabled {{
                border-color: {theme.get_color('text_disabled').name()};
                background-color: {theme.get_color('background').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup animations"""
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        """Handle selection state change animation"""
        if not self._select_animation:
            self._select_animation = QPropertyAnimation(
                self, QByteArray(b"geometry"))
            self._select_animation.setDuration(FluentAnimation.DURATION_FAST)
            self._select_animation.setEasingCurve(FluentAnimation.EASE_OUT)

        if checked:
            # Add selection animation effect
            current_rect = self.geometry()
            self._select_animation.setStartValue(current_rect)
            self._select_animation.setEndValue(current_rect)

    def enterEvent(self, event):
        """Hover enter"""
        self._is_hovered = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave"""
        self._is_hovered = False
        super().leaveEvent(event)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._setup_style()


class FluentRadioGroup(QWidget):
    """Radio Button Group"""

    selection_changed = Signal(int, str)  # index, text

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.button_group = QButtonGroup(self)
        self.radio_buttons: List[FluentRadioButton] = []

        self.button_group.buttonToggled.connect(self._on_selection_changed)

    def add_radio_button(self, text: str) -> FluentRadioButton:
        """Add radio button"""
        radio_button = FluentRadioButton(text, self)
        self.radio_buttons.append(radio_button)
        self.button_group.addButton(radio_button, len(self.radio_buttons) - 1)

        return radio_button

    def set_selected_index(self, index: int):
        """Set selected item"""
        if 0 <= index < len(self.radio_buttons):
            self.radio_buttons[index].setChecked(True)

    def get_selected_index(self) -> int:
        """Get selected item index"""
        return self.button_group.checkedId()

    def get_selected_text(self) -> str:
        """Get selected item text"""
        checked_button = self.button_group.checkedButton()
        return checked_button.text() if checked_button else ""

    def _on_selection_changed(self, button, checked: bool):
        """Handle selection change"""
        if checked:
            index = self.button_group.id(button)
            text = button.text()
            self.selection_changed.emit(index, text)


class FluentSwitch(QWidget):
    """Switch Component"""

    toggled = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._is_checked = False
        self._is_hovered = False
        self._is_pressed = False
        self._thumb_animation = None

        self.setFixedSize(40, 20)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._setup_animations()

        theme_manager.theme_changed.connect(self.update)

    def _setup_animations(self):
        """Setup animations"""
        self._thumb_animation = QPropertyAnimation(
            self, QByteArray(b"thumb_position"))
        self._thumb_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._thumb_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def paintEvent(self, _event: QPaintEvent):
        """Paint switch"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = theme_manager
        rect = self.rect()

        # Draw background track
        track_rect = QRect(2, 4, rect.width() - 4, 12)
        if self._is_checked:
            track_color = theme.get_color('primary')
        else:
            track_color = theme.get_color('border')

        painter.setBrush(QBrush(track_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(track_rect, 6, 6)

        # Draw thumb
        thumb_size = 16
        if self._is_checked:
            thumb_x = rect.width() - thumb_size - 2
        else:
            thumb_x = 2

        thumb_rect = QRect(thumb_x, 2, thumb_size, thumb_size)

        thumb_color = QColor(255, 255, 255)
        if self._is_hovered:
            thumb_color = thumb_color.darker(105)

        painter.setBrush(QBrush(thumb_color))
        painter.setPen(QPen(theme.get_color('border'), 1))
        painter.drawEllipse(thumb_rect)

    def mousePressEvent(self, event):
        """Mouse press"""
        self._is_pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Mouse release"""
        if self._is_pressed:
            self.toggle()

        self._is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """Hover enter"""
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave"""
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)

    def toggle(self):
        """Toggle switch state"""
        self.set_checked(not self._is_checked)

    def set_checked(self, checked: bool):
        """Set switch state"""
        if self._is_checked != checked:
            self._is_checked = checked
            self.update()
            self.toggled.emit(checked)

    def is_checked(self) -> bool:
        """Get switch state"""
        return self._is_checked
