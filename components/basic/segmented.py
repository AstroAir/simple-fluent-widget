"""
Fluent Design Style Segmented Control Components
Enhanced with smooth animations, theme consistency, and responsive interactions
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton,
                               QLabel, QButtonGroup, QSizePolicy)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from core.theme import theme_manager
from core.enhanced_animations import (FluentMicroInteraction, FluentTransition,
                                      FluentStateTransition, FluentRevealEffect)
from typing import Optional, List


class FluentSegmentedControl(QWidget):
    """Fluent Design Style Segmented Control"""

    class Size:
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    class Style:
        FILLED = "filled"
        OUTLINED = "outlined"
        PILL = "pill"

    selection_changed = Signal(int)  # Emitted when selection changes
    segment_clicked = Signal(int, str)  # Emitted when a segment is clicked

    def __init__(self, parent: Optional[QWidget] = None,
                 segments: Optional[List[str]] = None,
                 size: str = Size.MEDIUM,
                 style: str = Style.FILLED,
                 selected_index: int = 0):
        super().__init__(parent)

        self._segments = segments or []
        self._size = size
        self._style = style
        self._selected_index = selected_index
        self._buttons: List[QPushButton] = []
        self._button_group = QButtonGroup(self)

        self._setup_ui()
        self._setup_animations()
        self._apply_style()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Add reveal animation when created
        FluentRevealEffect.fade_in(self, 300)

    def _setup_ui(self):
        """Setup segmented control UI"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(2, 2, 2, 2)
        self._layout.setSpacing(0)

        # Create buttons for each segment
        for i, segment_text in enumerate(self._segments):
            button = QPushButton(segment_text)
            button.setCheckable(True)
            button.setFont(self._get_font())
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setMinimumHeight(self._get_height())

            # Connect button click
            button.clicked.connect(
                lambda _checked, index=i: self._on_segment_clicked(index))

            self._buttons.append(button)
            self._button_group.addButton(button, i)
            self._layout.addWidget(button)

        # Set initial selection
        if 0 <= self._selected_index < len(self._buttons):
            self._buttons[self._selected_index].setChecked(True)

    def _setup_animations(self):
        """Setup animations for the segmented control"""
        # Create state transition for the entire control
        self._state_transition = FluentStateTransition(self)

        height = self._get_height() + 4  # Container height

        self._state_transition.addState("normal", {
            "minimumHeight": height,
            "maximumHeight": height,
        })

    def _get_font(self) -> QFont:
        """Get font based on size"""
        if self._size == self.Size.SMALL:
            return QFont("Segoe UI", 9)
        elif self._size == self.Size.LARGE:
            return QFont("Segoe UI", 12, QFont.Weight.Medium)
        else:  # MEDIUM
            return QFont("Segoe UI", 10)

    def _get_height(self) -> int:
        """Get button height based on size"""
        if self._size == self.Size.SMALL:
            return 28
        elif self._size == self.Size.LARGE:
            return 40
        else:  # MEDIUM
            return 32

    def _get_border_radius(self) -> int:
        """Get border radius based on style"""
        if self._style == self.Style.PILL:
            return self._get_height() // 2
        else:
            return 6

    def _apply_style(self):
        """Apply segmented control styling"""
        current_theme = theme_manager
        border_radius = self._get_border_radius()

        # Container styling
        container_style = f"""
            FluentSegmentedControl {{
                background-color: {current_theme.get_color('surface_light').name()};
                border: 1px solid {current_theme.get_color('border').name()};
                border-radius: {border_radius}px;
            }}
        """

        # Button styling based on style type
        if self._style == self.Style.FILLED:
            button_style = self._get_filled_button_style(
                current_theme, border_radius)
        elif self._style == self.Style.OUTLINED:
            button_style = self._get_outlined_button_style(
                current_theme, border_radius)
        else:  # PILL
            button_style = self._get_pill_button_style(
                current_theme, border_radius)

        self.setStyleSheet(container_style)

        # Apply styling to each button
        for i, button in enumerate(self._buttons):
            # Add position-specific styling for proper border handling
            position_style = self._get_position_style(
                i, len(self._buttons), border_radius)
            button.setStyleSheet(button_style + position_style)

    def _get_filled_button_style(self, theme, _radius: int) -> str:
        """Get filled style button styling"""
        return f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {theme.get_color('text_primary').name()};
                padding: 6px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('surface').name()};
            }}
            QPushButton:checked {{
                background-color: {theme.get_color('primary').name()};
                color: {theme.get_color('text_on_accent').name()};
            }}
            QPushButton:checked:hover {{
                background-color: {theme.get_color('primary').lighter(110).name()};
            }}
        """

    def _get_outlined_button_style(self, theme, _radius: int) -> str:
        """Get outlined style button styling"""
        return f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                color: {theme.get_color('text_primary').name()};
                padding: 6px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('surface').name()};
                border-color: {theme.get_color('border').name()};
            }}
            QPushButton:checked {{
                background-color: transparent;
                border-color: {theme.get_color('primary').name()};
                color: {theme.get_color('primary').name()};
            }}
            QPushButton:checked:hover {{
                background-color: {theme.get_color('primary').name()}10;
            }}
        """

    def _get_pill_button_style(self, theme, radius: int) -> str:
        """Get pill style button styling"""
        return f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {theme.get_color('text_primary').name()};
                padding: 6px 20px;
                font-weight: 500;
                border-radius: {radius - 2}px;
                margin: 2px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('surface').name()};
            }}
            QPushButton:checked {{
                background-color: {theme.get_color('primary').name()};
                color: {theme.get_color('text_on_accent').name()};
            }}
            QPushButton:checked:hover {{
                background-color: {theme.get_color('primary').lighter(110).name()};
            }}
        """

    def _get_position_style(self, index: int, total: int, radius: int) -> str:
        """Get position-specific styling for proper border handling"""
        if self._style == self.Style.PILL:
            return ""  # Pills don't need position-specific styling

        style = ""

        if index == 0:  # First button
            style += f"border-top-left-radius: {radius - 1}px; border-bottom-left-radius: {radius - 1}px;"
        elif index == total - 1:  # Last button
            style += f"border-top-right-radius: {radius - 1}px; border-bottom-right-radius: {radius - 1}px;"

        return f"QPushButton {{ {style} }}"

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._apply_style()

    def _on_segment_clicked(self, index: int):
        """Handle segment button click"""
        if index != self._selected_index:
            self._selected_index = index

            # Add selection animation
            FluentMicroInteraction.scale_animation(self._buttons[index], 1.05)

            # Emit signals
            self.selection_changed.emit(index)
            self.segment_clicked.emit(index, self._segments[index])

    def add_segment(self, text: str, index: int = -1):
        """Add a new segment"""
        if index == -1:
            index = len(self._segments)

        self._segments.insert(index, text)

        # Create new button
        button = QPushButton(text)
        button.setCheckable(True)
        button.setFont(self._get_font())
        button.setSizePolicy(QSizePolicy.Policy.Expanding,
                             QSizePolicy.Policy.Fixed)
        button.setMinimumHeight(self._get_height())
        button.clicked.connect(
            lambda _checked, i=index: self._on_segment_clicked(i))

        # Insert button
        self._buttons.insert(index, button)
        self._button_group.addButton(button, index)
        self._layout.insertWidget(index, button)

        # Update button group IDs for buttons after inserted one
        for i in range(index + 1, len(self._buttons)):
            self._button_group.setId(self._buttons[i], i)
            # Reconnect signal with new index
            self._buttons[i].clicked.disconnect()
            self._buttons[i].clicked.connect(
                lambda _checked, idx=i: self._on_segment_clicked(idx))

        # Reapply styling
        self._apply_style()

        # Add reveal animation to new button
        FluentRevealEffect.slide_in(button, 200, "right")

    def remove_segment(self, index: int):
        """Remove a segment"""
        if 0 <= index < len(self._segments):
            # Remove from data
            self._segments.pop(index)

            # Remove button
            button = self._buttons.pop(index)
            self._button_group.removeButton(button)
            self._layout.removeWidget(button)

            # Add fade out animation before deletion
            fade_out = FluentTransition.create_transition(
                button, FluentTransition.FADE, 200, FluentTransition.EASE_SMOOTH)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.finished.connect(button.deleteLater)
            fade_out.start()

            # Update selection if necessary
            if self._selected_index >= len(self._segments):
                self._selected_index = max(0, len(self._segments) - 1)
                if self._buttons:
                    self._buttons[self._selected_index].setChecked(True)
            elif index <= self._selected_index:
                self._selected_index = max(0, self._selected_index - 1)

            # Update button group IDs
            for i in range(len(self._buttons)):
                self._button_group.setId(self._buttons[i], i)
                # Reconnect signal with correct index
                self._buttons[i].clicked.disconnect()
                self._buttons[i].clicked.connect(
                    lambda _checked, idx=i: self._on_segment_clicked(idx))

            # Reapply styling
            self._apply_style()

    def set_selected_index(self, index: int):
        """Set the selected segment index"""
        if 0 <= index < len(self._buttons):
            self._buttons[self._selected_index].setChecked(False)
            self._selected_index = index
            self._buttons[index].setChecked(True)

            # Add selection animation
            FluentMicroInteraction.pulse_animation(self._buttons[index], 1.1)

    def get_selected_index(self) -> int:
        """Get the currently selected index"""
        return self._selected_index

    def get_selected_text(self) -> str:
        """Get the currently selected segment text"""
        if 0 <= self._selected_index < len(self._segments):
            return self._segments[self._selected_index]
        return ""

    def set_segment_text(self, index: int, text: str):
        """Set text for a specific segment"""
        if 0 <= index < len(self._segments):
            self._segments[index] = text
            self._buttons[index].setText(text)

    def get_segment_count(self) -> int:
        """Get the number of segments"""
        return len(self._segments)

    def set_enabled_segment(self, index: int, enabled: bool):
        """Enable or disable a specific segment"""
        if 0 <= index < len(self._buttons):
            self._buttons[index].setEnabled(enabled)


class FluentTabBar(FluentSegmentedControl):
    """Fluent Design Style Tab Bar (specialized segmented control)"""

    tab_changed = Signal(int)
    tab_close_requested = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None,
                 tabs: Optional[List[str]] = None,
                 closable_tabs: bool = False):
        self._closable_tabs = closable_tabs
        super().__init__(parent, tabs or [], self.Size.MEDIUM, self.Style.FILLED)

        # Override signals for tab-specific naming
        self.selection_changed.connect(self.tab_changed.emit)

    def _setup_ui(self):
        """Setup tab bar UI with close buttons if needed"""
        super()._setup_ui()

        if self._closable_tabs:
            self._add_close_buttons()

    def _add_close_buttons(self):
        """Add close buttons to tabs"""
        for i, button in enumerate(self._buttons):
            # Create a container for button + close button
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 4, 0)
            layout.setSpacing(4)

            # Move button text to a label
            text_label = QLabel(button.text())
            text_label.setFont(button.font())

            # Create close button
            close_btn = QPushButton("×")
            close_btn.setFixedSize(16, 16)
            close_btn.clicked.connect(
                lambda _checked, index=i: self._on_tab_close(index))

            layout.addWidget(text_label)
            layout.addWidget(close_btn)

            # Replace button content (this is a simplified approach)
            button.setText("")
            # In a real implementation, you'd need to handle this more carefully

    def _on_tab_close(self, index: int):
        """Handle tab close request"""
        # Add close animation
        if 0 <= index < len(self._buttons):
            button = self._buttons[index]
            FluentMicroInteraction.scale_animation(button, 0.8)

            # Emit close request signal
            self.tab_close_requested.emit(index)

    def add_tab(self, text: str, index: int = -1):
        """Add a new tab"""
        self.add_segment(text, index)

    def remove_tab(self, index: int):
        """Remove a tab"""
        self.remove_segment(index)

    def set_current_tab(self, index: int):
        """Set the current tab"""
        self.set_selected_index(index)

    def get_current_tab(self) -> int:
        """Get the current tab index"""
        return self.get_selected_index()


class FluentToggleGroup(QWidget):
    """Fluent Design Style Toggle Button Group"""

    selection_changed = Signal(list)  # For multi-select mode
    toggle_changed = Signal(int, bool)  # For individual toggle changes

    def __init__(self, parent: Optional[QWidget] = None,
                 options: Optional[List[str]] = None,
                 multi_select: bool = True,
                 size: str = FluentSegmentedControl.Size.MEDIUM):
        super().__init__(parent)

        self._options = options or []
        self._multi_select = multi_select
        self._size = size
        self._buttons: List[QPushButton] = []
        self._selected_indices: List[int] = []

        self._setup_ui()
        self._apply_style()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Add reveal animation when created
        FluentRevealEffect.fade_in(self, 300)

    def _setup_ui(self):
        """Setup toggle group UI"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(8)

        for i, option in enumerate(self._options):
            button = QPushButton(option)
            button.setCheckable(True)
            button.setFont(self._get_font())
            button.setMinimumHeight(self._get_height())
            button.clicked.connect(
                lambda checked, index=i: self._on_toggle_clicked(index, checked))

            self._buttons.append(button)
            self._layout.addWidget(button)

    def _get_font(self) -> QFont:
        """Get font based on size"""
        if self._size == FluentSegmentedControl.Size.SMALL:
            return QFont("Segoe UI", 9)
        elif self._size == FluentSegmentedControl.Size.LARGE:
            return QFont("Segoe UI", 12, QFont.Weight.Medium)
        else:  # MEDIUM
            return QFont("Segoe UI", 10)

    def _get_height(self) -> int:
        """Get button height based on size"""
        if self._size == FluentSegmentedControl.Size.SMALL:
            return 28
        elif self._size == FluentSegmentedControl.Size.LARGE:
            return 40
        else:  # MEDIUM
            return 32

    def _apply_style(self):
        """Apply toggle group styling"""
        current_theme = theme_manager

        button_style = f"""
            QPushButton {{
                background-color: {current_theme.get_color('surface').name()};
                border: 1px solid {current_theme.get_color('border').name()};
                border-radius: 6px;
                color: {current_theme.get_color('text_primary').name()};
                padding: 6px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {current_theme.get_color('surface_light').name()};
                border-color: {current_theme.get_color('primary').lighter(120).name()};
            }}
            QPushButton:checked {{
                background-color: {current_theme.get_color('primary').name()};
                border-color: {current_theme.get_color('primary').name()};
                color: {current_theme.get_color('text_on_accent').name()};
            }}
            QPushButton:checked:hover {{
                background-color: {current_theme.get_color('primary').lighter(110).name()};
            }}
        """

        for button in self._buttons:
            button.setStyleSheet(button_style)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._apply_style()

    def _on_toggle_clicked(self, index: int, checked: bool):
        """Handle toggle button click"""
        if checked:
            if not self._multi_select:
                # Single select mode - uncheck all others
                for i, button in enumerate(self._buttons):
                    if i != index and button.isChecked():
                        button.setChecked(False)
                        if i in self._selected_indices:
                            self._selected_indices.remove(i)

            if index not in self._selected_indices:
                self._selected_indices.append(index)
                # Add selection animation
                FluentMicroInteraction.pulse_animation(
                    self._buttons[index], 1.1)
        else:
            if index in self._selected_indices:
                self._selected_indices.remove(index)

        self.toggle_changed.emit(index, checked)
        self.selection_changed.emit(self._selected_indices.copy())

    def set_selected_indices(self, indices: List[int]):
        """Set selected indices"""
        # Clear current selection
        for button in self._buttons:
            button.setChecked(False)
        self._selected_indices.clear()

        # Set new selection
        for index in indices:
            if 0 <= index < len(self._buttons):
                if not self._multi_select and len(self._selected_indices) > 0:
                    break  # Only allow one selection in single-select mode

                self._buttons[index].setChecked(True)
                self._selected_indices.append(index)

    def get_selected_indices(self) -> List[int]:
        """Get selected indices"""
        return self._selected_indices.copy()

    def get_selected_texts(self) -> List[str]:
        """Get selected option texts"""
        return [self._options[i] for i in self._selected_indices if 0 <= i < len(self._options)]
