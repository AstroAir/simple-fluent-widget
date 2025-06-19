"""
Fluent Design Style Segmented Control Components
Enhanced with smooth animations, theme consistency, and responsive interactions
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton,
                               QLabel, QButtonGroup, QSizePolicy)
from PySide6.QtCore import Signal, Property
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
        self._cached_styles = {}  # Cache for frequently used styles

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

            # Store index in button property for more efficient signal handling
            button.setProperty("segment_index", i)
            button.clicked.connect(self._on_segment_clicked_handler)

            self._buttons.append(button)
            self._button_group.addButton(button, i)
            self._layout.addWidget(button)

        # Set initial selection
        if 0 <= self._selected_index < len(self._buttons):
            self._buttons[self._selected_index].setChecked(True)

    def _on_segment_clicked_handler(self):
        """Handle segment button click by getting index from sender"""
        sender = self.sender()
        if sender:
            index = sender.property("segment_index")
            self._on_segment_clicked(index)

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
        """Apply segmented control styling with style caching"""
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

        # Create style key for caching
        style_key = f"{self._style}_{current_theme.current_theme}"

        # Get button base style from cache or create it
        if style_key not in self._cached_styles:
            if self._style == self.Style.FILLED:
                self._cached_styles[style_key] = self._get_filled_button_style(
                    current_theme, border_radius)
            elif self._style == self.Style.OUTLINED:
                self._cached_styles[style_key] = self._get_outlined_button_style(
                    current_theme, border_radius)
            else:  # PILL
                self._cached_styles[style_key] = self._get_pill_button_style(
                    current_theme, border_radius)

        base_button_style = self._cached_styles[style_key]
        self.setStyleSheet(container_style)

        # Apply styling to each button
        total_buttons = len(self._buttons)
        for i, button in enumerate(self._buttons):
            # Add position-specific styling only when needed
            position_style = "" if self._style == self.Style.PILL else self._get_position_style(
                i, total_buttons, border_radius)
            button.setStyleSheet(base_button_style + position_style)

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
        # Clear cached styles when theme changes
        self._cached_styles.clear()
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
        """Add a new segment efficiently"""
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

        # Set index property and connect signal
        button.setProperty("segment_index", index)
        button.clicked.connect(self._on_segment_clicked_handler)

        # Insert button
        self._buttons.insert(index, button)
        self._button_group.addButton(button, index)
        self._layout.insertWidget(index, button)

        # Update button indices
        self._update_button_indices()

        # Apply style to affected buttons only
        for i in range(index, len(self._buttons)):
            self._apply_button_style(i)

        # Add reveal animation to new button
        FluentRevealEffect.slide_in(button, 200, "right")

    def _update_button_indices(self):
        """Update button indices and button group IDs efficiently"""
        for i, button in enumerate(self._buttons):
            button.setProperty("segment_index", i)
            self._button_group.setId(button, i)

    def _apply_button_style(self, index: int):
        """Apply style to a specific button by index"""
        if not (0 <= index < len(self._buttons)):
            return

        button = self._buttons[index]
        current_theme = theme_manager
        border_radius = self._get_border_radius()

        # Get style from cache
        style_key = f"{self._style}_{current_theme.current_theme}"
        if style_key not in self._cached_styles:
            if self._style == self.Style.FILLED:
                self._cached_styles[style_key] = self._get_filled_button_style(
                    current_theme, border_radius)
            elif self._style == self.Style.OUTLINED:
                self._cached_styles[style_key] = self._get_outlined_button_style(
                    current_theme, border_radius)
            else:  # PILL
                self._cached_styles[style_key] = self._get_pill_button_style(
                    current_theme, border_radius)

        base_style = self._cached_styles[style_key]

        # Add position styling only when needed
        position_style = "" if self._style == self.Style.PILL else self._get_position_style(
            index, len(self._buttons), border_radius)
        button.setStyleSheet(base_style + position_style)

    def remove_segment(self, index: int):
        """Remove a segment efficiently"""
        if not (0 <= index < len(self._segments)):
            return

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
            if self._buttons and self._selected_index >= 0:
                self._buttons[self._selected_index].setChecked(True)
        elif index <= self._selected_index:
            self._selected_index = max(0, self._selected_index - 1)
            if self._buttons and self._selected_index >= 0:
                self._buttons[self._selected_index].setChecked(True)

        # Update button indices
        self._update_button_indices()

        # Only update styles for buttons whose positions changed
        for i in range(index, len(self._buttons)):
            self._apply_button_style(i)

    def set_selected_index(self, index: int):
        """Set the selected segment index"""
        if 0 <= index < len(self._buttons):
            if 0 <= self._selected_index < len(self._buttons):
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
        self._close_buttons = []  # Track close buttons separately
        super().__init__(parent, tabs or [], self.Size.MEDIUM, self.Style.FILLED)

        # Override signals for tab-specific naming
        self.selection_changed.connect(self.tab_changed.emit)

    def _setup_ui(self):
        """Setup tab bar UI with close buttons if needed"""
        super()._setup_ui()

        if self._closable_tabs:
            self._add_close_buttons()

    def _add_close_buttons(self):
        """Add close buttons to tabs efficiently"""
        for i, button in enumerate(self._buttons):
            # Store original text and clear button text
            button_text = button.text()
            button.setText("")

            # Create container layout within button for better performance
            container_layout = QHBoxLayout(button)
            container_layout.setContentsMargins(6, 2, 6, 2)
            container_layout.setSpacing(4)

            # Text label
            text_label = QLabel(button_text)
            text_label.setFont(button.font())

            # Close button with stored index property
            close_btn = QPushButton("×")
            close_btn.setFixedSize(16, 16)
            close_btn.setProperty("tab_index", i)
            close_btn.clicked.connect(self._on_tab_close_handler)
            self._close_buttons.append(close_btn)

            container_layout.addWidget(text_label, 1)  # 1 = stretch factor
            container_layout.addWidget(close_btn, 0)   # 0 = no stretch

    def _on_tab_close_handler(self):
        """Handle tab close click using sender property"""
        sender = self.sender()
        if sender:
            index = sender.property("tab_index")
            self._on_tab_close(index)

    def _on_tab_close(self, index: int):
        """Handle tab close request"""
        # Add close animation
        if 0 <= index < len(self._buttons):
            button = self._buttons[index]
            FluentMicroInteraction.scale_animation(button, 0.8)

            # Emit close request signal
            self.tab_close_requested.emit(index)

    def _update_button_indices(self):
        """Override to update both button and close button indices"""
        super()._update_button_indices()

        # Update close button indices
        for i, close_btn in enumerate(self._close_buttons):
            close_btn.setProperty("tab_index", i)

    def add_tab(self, text: str, index: int = -1):
        """Add a new tab with close button if needed"""
        super().add_segment(text, index)

        # If tabs are closable, add close button to the new tab
        if self._closable_tabs:
            if index == -1:
                index = len(self._buttons) - 1

            button = self._buttons[index]
            button_text = button.text()
            button.setText("")

            container_layout = QHBoxLayout(button)
            container_layout.setContentsMargins(6, 2, 6, 2)
            container_layout.setSpacing(4)

            text_label = QLabel(button_text)
            text_label.setFont(button.font())

            close_btn = QPushButton("×")
            close_btn.setFixedSize(16, 16)
            close_btn.setProperty("tab_index", index)
            close_btn.clicked.connect(self._on_tab_close_handler)

            # Insert close button at correct position
            self._close_buttons.insert(index, close_btn)

            container_layout.addWidget(text_label, 1)
            container_layout.addWidget(close_btn, 0)

            # Update all indices
            self._update_button_indices()

    def remove_tab(self, index: int):
        """Remove a tab and its close button if present"""
        if self._closable_tabs and 0 <= index < len(self._close_buttons):
            self._close_buttons.pop(index)

        super().remove_segment(index)

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
        self._button_style_cache = None  # Style cache for performance

        self._setup_ui()
        self._apply_style()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

        # Add reveal animation when created
        FluentRevealEffect.fade_in(self, 300)

    def _setup_ui(self):
        """Setup toggle group UI with property-based signal handling"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(8)

        for i, option in enumerate(self._options):
            button = QPushButton(option)
            button.setCheckable(True)
            button.setFont(self._get_font())
            button.setMinimumHeight(self._get_height())

            # Store index in button property
            button.setProperty("toggle_index", i)
            button.clicked.connect(self._on_toggle_clicked_handler)

            self._buttons.append(button)
            self._layout.addWidget(button)

    def _on_toggle_clicked_handler(self, checked):
        """Handler that uses sender properties to identify source button"""
        sender = self.sender()
        if sender:
            index = sender.property("toggle_index")
            self._on_toggle_clicked(index, checked)

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
        """Apply toggle group styling with caching for better performance"""
        current_theme = theme_manager

        # Use cached style if available, otherwise generate it
        if self._button_style_cache is None:
            self._button_style_cache = f"""
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

        # Apply cached style to all buttons
        for button in self._buttons:
            button.setStyleSheet(self._button_style_cache)

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change by invalidating cache"""
        self._button_style_cache = None
        self._apply_style()

    def _on_toggle_clicked(self, index: int, checked: bool):
        """Handle toggle button click with optimized selection logic"""
        if checked:
            if not self._multi_select:
                # Single select mode - uncheck all others efficiently
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

        # Sort indices for consistent ordering
        self._selected_indices.sort()

        self.toggle_changed.emit(index, checked)
        self.selection_changed.emit(self._selected_indices.copy())

    def set_selected_indices(self, indices: List[int]):
        """Set selected indices efficiently"""
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

        # Sort indices for consistent ordering
        self._selected_indices.sort()

    def get_selected_indices(self) -> List[int]:
        """Get selected indices"""
        return self._selected_indices.copy()

    def get_selected_texts(self) -> List[str]:
        """Get selected option texts"""
        return [self._options[i] for i in self._selected_indices if 0 <= i < len(self._options)]
