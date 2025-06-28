"""
Fluent Design Style Chip Components
Enhanced chips, tags and filter components with smooth animations and theme consistency
"""

from PySide6.QtWidgets import (QWidget, QLabel, QHBoxLayout, QPushButton,
                               QSizePolicy)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QFont
from core.theme import theme_manager
from core.enhanced_animations import (FluentMicroInteraction, FluentTransition,
                                      FluentStateTransition, FluentRevealEffect)
from typing import Optional, List, Dict


class FluentChip(QWidget):
    """Fluent Design Style Chip Component"""

    class ChipStyle:
        FILLED = "filled"
        OUTLINED = "outlined"
        TEXT = "text"

    class ChipSize:
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    class ChipType:
        DEFAULT = "default"
        PRIMARY = "primary"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"
        INFO = "info"

    clicked = Signal()
    close_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None,
                 text: str = "",
                 chip_style: str = ChipStyle.FILLED,
                 chip_type: str = ChipType.DEFAULT,
                 size: str = ChipSize.MEDIUM,
                 closable: bool = False,
                 clickable: bool = True,
                 icon: str = ""):
        super().__init__(parent)

        self._text = text
        self._chip_style = chip_style
        self._chip_type = chip_type
        self._size = size
        self._closable = closable
        self._clickable = clickable
        self._icon = icon

        self._is_hovered = False
        self._is_pressed = False
        self._state_transition = FluentStateTransition(self)

        self._setup_ui()
        self._setup_animations()
        self._apply_style()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Add reveal animation when created
        FluentRevealEffect.scale_in(self, 200)

    def _setup_ui(self):
        """Setup chip UI"""
        layout = QHBoxLayout(self)

        # Set padding based on size
        padding = self._get_padding()
        layout.setContentsMargins(padding, padding//2, padding, padding//2)
        layout.setSpacing(4)

        # Icon (if provided)
        if self._icon:
            self._icon_label = QLabel(self._icon)
            self._icon_label.setFixedSize(
                self._get_icon_size(), self._get_icon_size())
            self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self._icon_label)

        # Text label
        self._text_label = QLabel(self._text)
        self._text_label.setFont(self._get_font())
        layout.addWidget(self._text_label)

        # Close button (if closable)
        if self._closable:
            self._close_button = QPushButton("×")
            self._close_button.setFixedSize(
                self._get_close_size(), self._get_close_size())
            self._close_button.clicked.connect(self._on_close_clicked)
            layout.addWidget(self._close_button)

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def _get_padding(self) -> int:
        """Get padding based on size"""
        if self._size == self.ChipSize.SMALL:
            return 8
        elif self._size == self.ChipSize.LARGE:
            return 16
        else:  # MEDIUM
            return 12

    def _get_icon_size(self) -> int:
        """Get icon size based on chip size"""
        if self._size == self.ChipSize.SMALL:
            return 12
        elif self._size == self.ChipSize.LARGE:
            return 20
        else:  # MEDIUM
            return 16

    def _get_close_size(self) -> int:
        """Get close button size based on chip size"""
        if self._size == self.ChipSize.SMALL:
            return 14
        elif self._size == self.ChipSize.LARGE:
            return 22
        else:  # MEDIUM
            return 18

    def _get_font(self) -> QFont:
        """Get font based on size"""
        if self._size == self.ChipSize.SMALL:
            return QFont("Segoe UI", 8)
        elif self._size == self.ChipSize.LARGE:
            return QFont("Segoe UI", 12, QFont.Weight.Medium)
        else:  # MEDIUM
            return QFont("Segoe UI", 10)

    def _get_height(self) -> int:
        """Get chip height based on size"""
        if self._size == self.ChipSize.SMALL:
            return 24
        elif self._size == self.ChipSize.LARGE:
            return 40
        else:  # MEDIUM
            return 32

    def _setup_animations(self):
        """Setup animations for the chip"""
        height = self._get_height()

        self._state_transition.addState("normal", {
            "minimumHeight": height,
            "maximumHeight": height,
        })

        self._state_transition.addState("hovered", {
            "minimumHeight": height + 2,
            "maximumHeight": height + 2,
        }, duration=150, easing=FluentTransition.EASE_SMOOTH)

        self._state_transition.addState("pressed", {
            "minimumHeight": height - 2,
            "maximumHeight": height - 2,
        }, duration=100, easing=FluentTransition.EASE_CRISP)

    def _apply_style(self):
        """Apply chip styling"""
        # Get colors based on type and style
        colors = self._get_type_colors()
        bg_color = colors['background']
        text_color = colors['text']
        border_color = colors['border']

        # Base chip styling
        border_radius = self._get_height() // 2

        if self._chip_style == self.ChipStyle.FILLED:
            chip_style_sheet = f"""
                FluentChip {{
                    background-color: {bg_color.name()};
                    border: 1px solid {border_color.name()};
                    border-radius: {border_radius}px;
                    color: {text_color.name()};
                }}
                FluentChip:hover {{
                    background-color: {bg_color.lighter(110).name()};
                    border-color: {border_color.lighter(120).name()};
                }}
            """
        elif self._chip_style == self.ChipStyle.OUTLINED:
            chip_style_sheet = f"""
                FluentChip {{
                    background-color: transparent;
                    border: 2px solid {border_color.name()};
                    border-radius: {border_radius}px;
                    color: {text_color.name()};
                }}
                FluentChip:hover {{
                    background-color: {bg_color.name()}20;
                    border-color: {border_color.lighter(120).name()};
                }}
            """
        else:  # TEXT
            chip_style_sheet = f"""
                FluentChip {{
                    background-color: transparent;
                    border: none;
                    border-radius: {border_radius}px;
                    color: {text_color.name()};
                }}
                FluentChip:hover {{
                    background-color: {bg_color.name()}15;
                }}
            """

        # Text label styling
        text_style = f"""
            QLabel {{
                background: transparent;
                border: none;
                color: {text_color.name()};
            }}
        """

        # Close button styling (if exists)
        if self._closable:
            close_style = f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: {self._get_close_size() // 2}px;
                    color: {text_color.name()};
                    font-weight: bold;
                    font-size: {self._get_close_size() - 4}px;
                }}
                QPushButton:hover {{
                    background-color: {text_color.name()}20;
                }}
                QPushButton:pressed {{
                    background-color: {text_color.name()}30;
                }}
            """
            self._close_button.setStyleSheet(close_style)

        self.setStyleSheet(chip_style_sheet)
        self._text_label.setStyleSheet(text_style)

        if self._icon and hasattr(self, '_icon_label'):
            self._icon_label.setStyleSheet(text_style)

    def _get_type_colors(self) -> Dict[str, QColor]:
        """Get colors based on chip type"""
        current_theme = theme_manager

        if self._chip_type == self.ChipType.PRIMARY:
            return {
                'background': current_theme.get_color('primary'),
                'text': current_theme.get_color('text_on_accent'),
                'border': current_theme.get_color('primary')
            }
        elif self._chip_type == self.ChipType.SUCCESS:
            return {
                'background': current_theme.get_color('success'),
                'text': current_theme.get_color('text_on_accent'),
                'border': current_theme.get_color('success')
            }
        elif self._chip_type == self.ChipType.WARNING:
            return {
                'background': current_theme.get_color('warning'),
                'text': current_theme.get_color('text_on_accent'),
                'border': current_theme.get_color('warning')
            }
        elif self._chip_type == self.ChipType.ERROR:
            return {
                'background': current_theme.get_color('error'),
                'text': current_theme.get_color('text_on_accent'),
                'border': current_theme.get_color('error')
            }
        elif self._chip_type == self.ChipType.INFO:
            return {
                'background': current_theme.get_color('info'),
                'text': current_theme.get_color('text_on_accent'),
                'border': current_theme.get_color('info')
            }
        else:  # DEFAULT
            return {
                'background': current_theme.get_color('surface_light'),
                'text': current_theme.get_color('text_primary'),
                'border': current_theme.get_color('border')
            }

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._apply_style()

    def _on_close_clicked(self):
        """Handle close button click"""
        # Add close animation before emitting signal
        FluentMicroInteraction.scale_animation(self, 0.8)

        # Delay signal emission to allow animation
        QTimer.singleShot(100, self.close_clicked.emit)

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton and self._clickable:
            self._is_pressed = True
            self._state_transition.transitionTo("pressed")
            FluentMicroInteraction.scale_animation(self, 0.95)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton and self._clickable:
            self._is_pressed = False

            if self._is_hovered:
                self._state_transition.transitionTo("hovered")
            else:
                self._state_transition.transitionTo("normal")

            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit()

        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """Handle hover enter"""
        self._is_hovered = True
        if not self._is_pressed:
            self._state_transition.transitionTo("hovered")
            FluentMicroInteraction.hover_glow(self, 0.1)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle hover leave"""
        self._is_hovered = False
        if not self._is_pressed:
            self._state_transition.transitionTo("normal")
        super().leaveEvent(event)

    def set_text(self, text: str):
        """Set chip text"""
        self._text = text
        self._text_label.setText(text)

    def get_text(self) -> str:
        """Get chip text"""
        return self._text

    def set_type(self, chip_type: str):
        """Set chip type"""
        if chip_type in [self.ChipType.DEFAULT, self.ChipType.PRIMARY,
                         self.ChipType.SUCCESS, self.ChipType.WARNING,
                         self.ChipType.ERROR, self.ChipType.INFO]:
            self._chip_type = chip_type
            self._apply_style()

    def set_style(self, chip_style: str):
        """Set chip style"""
        if chip_style in [self.ChipStyle.FILLED, self.ChipStyle.OUTLINED, self.ChipStyle.TEXT]:
            self._chip_style = chip_style
            self._apply_style()


class FluentChipGroup(QWidget):
    """Fluent Design Style Chip Group for multiple chips"""

    chip_added = Signal(str)
    chip_removed = Signal(str)
    selection_changed = Signal(list)  # For selectable chips

    def __init__(self, parent: Optional[QWidget] = None,
                 selectable: bool = False,
                 multi_select: bool = False,
                 max_chips: int = -1):
        super().__init__(parent)

        self._selectable = selectable
        self._multi_select = multi_select
        self._max_chips = max_chips
        self._chips: List[FluentChip] = []
        self._selected_chips: List[FluentChip] = []

        self._setup_ui()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Add reveal animation when created
        FluentRevealEffect.fade_in(self, 300)

    def _setup_ui(self):
        """Setup chip group UI"""
        # Use a flow layout for automatic wrapping
        self._layout = QHBoxLayout(self)  # Simplified for now
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(8)

    def add_chip(self, text: str,
                 chip_style: str = FluentChip.ChipStyle.FILLED,
                 chip_type: str = FluentChip.ChipType.DEFAULT,
                 size: str = FluentChip.ChipSize.MEDIUM,
                 closable: bool = True,
                 icon: str = "") -> Optional[FluentChip]:
        """Add a chip to the group"""
        if self._max_chips > 0 and len(self._chips) >= self._max_chips:
            return None

        chip = FluentChip(
            parent=self,
            text=text,
            chip_style=chip_style,
            chip_type=chip_type,
            size=size,
            closable=closable,
            clickable=self._selectable,
            icon=icon
        )

        chip.close_clicked.connect(lambda: self._on_chip_close(chip))

        if self._selectable:
            chip.clicked.connect(lambda: self._on_chip_clicked(chip))

        self._chips.append(chip)
        self._layout.addWidget(chip)

        # Add chip with animation
        FluentRevealEffect.slide_in(chip, 200, "right")

        self.chip_added.emit(text)
        return chip

    def _on_chip_close(self, chip: FluentChip):
        """Handle chip close"""
        if chip in self._chips:
            text = chip.get_text()
            self._chips.remove(chip)

            if chip in self._selected_chips:
                self._selected_chips.remove(chip)
                self.selection_changed.emit(
                    [c.get_text() for c in self._selected_chips])

            # Remove with animation
            fade_out = FluentTransition.create_transition(
                chip, FluentTransition.FADE, 200, FluentTransition.EASE_SMOOTH)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)

            def remove_chip_widget():
                self._layout.removeWidget(chip)
                chip.deleteLater()

            fade_out.finished.connect(remove_chip_widget)
            fade_out.start()

            self.chip_removed.emit(text)

    def _on_chip_clicked(self, chip: FluentChip):
        """Handle chip selection"""
        if not self._selectable:
            return

        if chip in self._selected_chips:
            # Deselect
            self._selected_chips.remove(chip)
            # Reset to default outlined
            chip.set_style(FluentChip.ChipStyle.OUTLINED)
            chip.set_type(FluentChip.ChipType.DEFAULT)  # Reset to default type
        else:
            # Select
            if not self._multi_select:
                # Clear previous selection
                for selected_chip in self._selected_chips:
                    selected_chip.set_style(FluentChip.ChipStyle.OUTLINED)
                    selected_chip.set_type(FluentChip.ChipType.DEFAULT)
                self._selected_chips.clear()

            self._selected_chips.append(chip)
            chip.set_style(FluentChip.ChipStyle.FILLED)
            chip.set_type(FluentChip.ChipType.PRIMARY)

        self.selection_changed.emit([c.get_text()
                                    for c in self._selected_chips])

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        for chip in self._chips:
            chip._apply_style()

    def remove_chip(self, text: str):
        """Remove chip by text"""
        for chip in self._chips:
            if chip.get_text() == text:
                self._on_chip_close(chip)
                break

    def clear_chips(self):
        """Remove all chips"""
        for chip in self._chips.copy():  # Iterate over a copy for safe removal
            self._on_chip_close(chip)

    def get_selected_texts(self) -> List[str]:
        """Get selected chip texts"""
        return [chip.get_text() for chip in self._selected_chips]

    def get_all_texts(self) -> List[str]:
        """Get all chip texts"""
        return [chip.get_text() for chip in self._chips]

    def set_max_chips(self, max_chips: int):
        """Set maximum number of chips"""
        self._max_chips = max_chips


class FluentFilterChip(FluentChip):
    """Fluent Design Style Filter Chip with toggle state"""

    filter_toggled = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None,
                 text: str = "",
                 initially_active: bool = False):
        self._is_active = initially_active

        super().__init__(
            parent=parent,
            text=text,
            chip_style=self.ChipStyle.FILLED if initially_active else self.ChipStyle.OUTLINED,
            chip_type=self.ChipType.PRIMARY if initially_active else self.ChipType.DEFAULT,
            clickable=True
        )

        self.clicked.connect(self._toggle_filter)

    def _toggle_filter(self):
        """Toggle filter state"""
        self._is_active = not self._is_active

        if self._is_active:
            self.set_style(self.ChipStyle.FILLED)
            self.set_type(self.ChipType.PRIMARY)
        else:
            self.set_style(self.ChipStyle.OUTLINED)
            self.set_type(self.ChipType.DEFAULT)

        # Add toggle animation
        FluentMicroInteraction.pulse_animation(self, 1.1)

        self.filter_toggled.emit(self._is_active)

    def is_active(self) -> bool:
        """Check if filter is active"""
        return self._is_active

    def set_active(self, active: bool):
        """Set filter active state"""
        if active != self._is_active:
            # Call _toggle_filter to ensure UI updates and signal emission
            self._toggle_filter()
