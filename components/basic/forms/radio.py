"""
Fluent Design Radio Button and Radio Group Components
Implements single-selection radio buttons with consistent styling and behavior
"""

from typing import Optional, List, Any
from PySide6.QtWidgets import (QWidget, QAbstractButton, QButtonGroup, QVBoxLayout,
                               QHBoxLayout, QLabel)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor

from components.base.fluent_control_base import FluentControlBase
from components.base.fluent_component_interface import (
    FluentComponentState, FluentComponentSize, FluentComponentVariant
)


class FluentRadioButton(QAbstractButton, FluentControlBase):
    """
    Fluent Design Radio Button Component

    Features:
    - Smooth animations and hover effects
    - Theme-consistent styling
    - Accessible implementation
    - Custom selection indicators
    """

    # Additional signals
    hover_changed = Signal(bool)
    focus_changed = Signal(bool)

    def __init__(self, text: str = "", parent: Optional[QWidget] = None,
                 size: FluentComponentSize = FluentComponentSize.MEDIUM,
                 variant: FluentComponentVariant = FluentComponentVariant.STANDARD):
        QAbstractButton.__init__(self, parent)
        FluentControlBase.__init__(self, parent)

        # Properties
        self._text = text
        self._radio_size = 16
        self._indicator_size = 8
        self._text_spacing = 8
        self._size = size  # Ensure _size property exists
        self._variant = variant  # Ensure _variant property exists
        self._state = FluentComponentState.NORMAL  # Ensure _state property exists

        # Setup component
        self._component_type = "FluentRadioButton"
        self.set_size(size)
        self.set_variant(variant)
        self.set_accessible_name(text)

        # Set text
        self.setText(text)
        self.setCheckable(True)

        # Setup UI
        self._setup_ui()
        self._apply_themed_styles()

    def set_size(self, size: FluentComponentSize):
        self._size = size
        self._on_size_changed()

    def get_size(self) -> FluentComponentSize:
        return self._size

    def set_variant(self, variant: FluentComponentVariant):
        self._variant = variant
        self._on_variant_changed()

    def get_variant(self) -> FluentComponentVariant:
        return self._variant

    def set_state(self, state: FluentComponentState):
        self._state = state
        self._apply_state_styles()

    def get_state(self) -> FluentComponentState:
        return self._state

    def set_accessible_role(self, role: str):
        # PySide6 does not support setAccessibleRole, so this is a no-op
        pass

    def _setup_ui(self):
        """Setup the radio button UI"""
        self.setMinimumHeight(self._radio_size + 8)
        self.setMinimumWidth(self._radio_size + self._text_spacing + 100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _apply_themed_styles(self):
        """Apply themed styles based on current theme"""
        # Styles are applied via paintEvent
        self.update()

    def _apply_state_styles(self):
        """Apply styles for current state"""
        # State styles are handled in paintEvent
        self.update()

    def get_value(self) -> bool:
        """Get radio button checked state"""
        return self.isChecked()

    def set_value(self, value: Any) -> None:
        """Set radio button checked state"""
        if isinstance(value, bool):
            self.setChecked(value)

    def set_text(self, text: str) -> None:
        """Set radio button text"""
        self._text = text
        self.setText(text)
        self.set_accessible_name(text)
        self.update()

    def set_checked(self, checked: bool) -> None:
        """Set radio button checked state"""
        self.setChecked(checked)

    def _on_size_changed(self) -> None:
        """Handle size changes"""
        size_map = {
            FluentComponentSize.TINY: 12,
            FluentComponentSize.SMALL: 14,
            FluentComponentSize.MEDIUM: 16,
            FluentComponentSize.LARGE: 18,
            FluentComponentSize.XLARGE: 20
        }
        self._radio_size = size_map.get(self._size, 16)
        self._indicator_size = max(4, self._radio_size - 8)
        self.setMinimumHeight(self._radio_size + 8)
        self.update()

    def _on_variant_changed(self) -> None:
        """Handle variant changes"""
        self.update()

    def paintEvent(self, event):
        """Custom paint event for radio button"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get theme colors
        bg_color = self._theme_tokens.get("surface", QColor("#FFFFFF"))
        border_color = self._theme_tokens.get("border", QColor("#CCCCCC"))
        primary_color = self._theme_tokens.get("primary", QColor("#0078D4"))
        text_color = self._theme_tokens.get("text_primary", QColor("#000000"))

        # Adjust colors based on state
        if self._state == FluentComponentState.DISABLED:
            bg_color = bg_color.darker(110)
            border_color = border_color.lighter(150)
            text_color = text_color.lighter(150)
        elif self._state == FluentComponentState.HOVERED:
            border_color = primary_color.lighter(120)
        elif self._state == FluentComponentState.PRESSED:
            bg_color = bg_color.darker(105)

        # Draw radio circle
        radio_rect = self.rect()
        radio_center_y = radio_rect.height() // 2
        radio_x = 8
        radio_y = radio_center_y - self._radio_size // 2

        # Outer circle
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(QBrush(bg_color))
        painter.drawEllipse(
            radio_x, radio_y, self._radio_size, self._radio_size)

        # Inner circle (when checked)
        if self.isChecked():
            indicator_x = radio_x + \
                (self._radio_size - self._indicator_size) // 2
            indicator_y = radio_y + \
                (self._radio_size - self._indicator_size) // 2
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(primary_color))
            painter.drawEllipse(indicator_x, indicator_y,
                                self._indicator_size, self._indicator_size)

        # Draw text
        if self._text:
            text_x = radio_x + self._radio_size + self._text_spacing
            text_rect = painter.fontMetrics().boundingRect(self._text)
            text_y = radio_center_y + text_rect.height() // 4

            painter.setPen(QPen(text_color))
            painter.drawText(text_x, text_y, self._text)

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_state(FluentComponentState.PRESSED)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.rect().contains(event.position().toPoint()):
                self.setChecked(True)
                self.clicked.emit()
            self.set_state(FluentComponentState.HOVERED if self.underMouse(
            ) else FluentComponentState.NORMAL)
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter events"""
        if self._state != FluentComponentState.PRESSED:
            self.set_state(FluentComponentState.HOVERED)
        self.hover_changed.emit(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave events"""
        if self._state != FluentComponentState.PRESSED:
            self.set_state(FluentComponentState.NORMAL)
        self.hover_changed.emit(False)
        super().leaveEvent(event)

    def focusInEvent(self, event):
        """Handle focus in events"""
        self.set_state(FluentComponentState.FOCUSED)
        self.focus_changed.emit(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Handle focus out events"""
        self.set_state(FluentComponentState.NORMAL)
        self.focus_changed.emit(False)
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return):
            self.setChecked(True)
            self.clicked.emit()
        super().keyPressEvent(event)


class FluentRadioGroup(FluentControlBase):
    """
    Fluent Design Radio Group Component

    Features:
    - Manages multiple radio buttons
    - Ensures single selection
    - Flexible layout options
    - Accessible group behavior
    """

    # Signals
    selection_changed = Signal(int)  # index of selected radio
    value_changed = Signal(str)      # value of selected radio

    def __init__(self, parent: Optional[QWidget] = None,
                 orientation: Qt.Orientation = Qt.Orientation.Vertical,
                 spacing: int = 8,
                 size: FluentComponentSize = FluentComponentSize.MEDIUM,
                 variant: FluentComponentVariant = FluentComponentVariant.STANDARD):
        super().__init__(parent)

        # Properties
        self._orientation = orientation
        self._spacing = spacing
        self._radio_buttons: List[FluentRadioButton] = []
        self._button_group = QButtonGroup()
        self._selected_index = -1
        self._size = size  # Ensure _size property exists
        self._variant = variant  # Ensure _variant property exists

        # Setup component
        self._component_type = "FluentRadioGroup"
        self.set_accessible_role("radiogroup")

        # Setup UI
        self._setup_ui()
        self._setup_button_group()

    def set_size(self, size: FluentComponentSize):
        self._size = size
        self._on_size_changed()

    def get_size(self) -> FluentComponentSize:
        return self._size

    def set_variant(self, variant: FluentComponentVariant):
        self._variant = variant
        self._on_variant_changed()

    def get_variant(self) -> FluentComponentVariant:
        return self._variant

    def set_accessible_role(self, role: str):
        # PySide6 does not support setAccessibleRole, so this is a no-op
        pass

    def _setup_ui(self):
        """Setup the radio group UI"""
        if self._orientation == Qt.Orientation.Vertical:
            self._layout = QVBoxLayout()
        else:
            self._layout = QHBoxLayout()

        self._layout.setSpacing(self._spacing)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

    def _setup_button_group(self):
        """Setup the button group for mutual exclusion"""
        self._button_group.setExclusive(True)
        self._button_group.buttonToggled.connect(self._on_button_toggled)

    def _apply_themed_styles(self):
        """Apply themed styles"""
        # Theme is applied to individual radio buttons
        for button in self._radio_buttons:
            button._apply_themed_styles()

    def _apply_state_styles(self):
        """Apply state styles"""
        # State is managed by individual radio buttons
        pass

    def get_value(self) -> Optional[str]:
        """Get value of selected radio button"""
        if 0 <= self._selected_index < len(self._radio_buttons):
            return self._radio_buttons[self._selected_index].text()
        return None

    def set_value(self, value: str) -> None:
        """Set selected radio button by value"""
        for i, button in enumerate(self._radio_buttons):
            if button.text() == value:
                self.set_selected_index(i)
                break

    def add_radio(self, text: str, value: Optional[str] = None) -> FluentRadioButton:
        """Add a radio button to the group"""
        radio = FluentRadioButton(text, self, self._size, self._variant)
        # Add to layout and group
        self._layout.addWidget(radio)
        self._button_group.addButton(radio, len(self._radio_buttons))
        self._radio_buttons.append(radio)
        return radio

    def remove_radio(self, index: int) -> None:
        """Remove a radio button from the group"""
        if 0 <= index < len(self._radio_buttons):
            radio = self._radio_buttons.pop(index)
            self._button_group.removeButton(radio)
            self._layout.removeWidget(radio)
            radio.deleteLater()

            # Update selected index
            if self._selected_index == index:
                self._selected_index = -1
            elif self._selected_index > index:
                self._selected_index -= 1

    def clear_radios(self) -> None:
        """Remove all radio buttons"""
        while self._radio_buttons:
            self.remove_radio(0)

    def get_selected_index(self) -> int:
        """Get index of selected radio button"""
        return self._selected_index

    def set_selected_index(self, index: int) -> None:
        """Set selected radio button by index"""
        if 0 <= index < len(self._radio_buttons):
            self._radio_buttons[index].setChecked(True)

    def get_radio_count(self) -> int:
        """Get number of radio buttons"""
        return len(self._radio_buttons)

    def get_radio(self, index: int) -> Optional[FluentRadioButton]:
        """Get radio button at index"""
        if 0 <= index < len(self._radio_buttons):
            return self._radio_buttons[index]
        return None

    def set_orientation(self, orientation: Qt.Orientation) -> None:
        """Set layout orientation"""
        if self._orientation != orientation:
            self._orientation = orientation

            # Recreate layout
            old_layout = self._layout
            if orientation == Qt.Orientation.Vertical:
                self._layout = QVBoxLayout()
            else:
                self._layout = QHBoxLayout()

            self._layout.setSpacing(self._spacing)
            self._layout.setContentsMargins(0, 0, 0, 0)

            # Move widgets to new layout
            for button in self._radio_buttons:
                old_layout.removeWidget(button)
                self._layout.addWidget(button)

            # Replace layout
            self.setLayout(self._layout)

    def set_spacing(self, spacing: int) -> None:
        """Set spacing between radio buttons"""
        self._spacing = spacing
        self._layout.setSpacing(spacing)

    def _on_button_toggled(self, button, checked: bool) -> None:
        """Handle radio button toggle"""
        if checked and isinstance(button, FluentRadioButton):
            # Find the button index
            for i, radio in enumerate(self._radio_buttons):
                if radio == button:
                    self._selected_index = i
                    self.selection_changed.emit(i)
                    self.value_changed.emit(button.text())
                    break

    def _on_size_changed(self) -> None:
        """Handle size changes"""
        for button in self._radio_buttons:
            button.set_size(self._size)

    def _on_variant_changed(self) -> None:
        """Handle variant changes"""
        for button in self._radio_buttons:
            button.set_variant(self._variant)
