"""
Fluent Design Style Tab Component
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QScrollArea, QFrame
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QRect, Property, QByteArray
from PySide6.QtGui import QPainter, QColor
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional, List, Dict, Any


class FluentTabButton(QPushButton):
    """Individual tab button"""

    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self._is_active = False
        self._hover_progress = 0.0
        self._active_progress = 0.0
        self._close_button_visible = False

        self.setCheckable(True)
        self.setMinimumHeight(40)
        self.setMinimumWidth(80)

        self._setup_animations()
        self._setup_style()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animations(self):
        """Setup animations"""
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_progress"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentAnimation.EASE_OUT)

        self._active_animation = QPropertyAnimation(
            self, QByteArray(b"active_progress"))
        self._active_animation.setDuration(
            FluentAnimation.DURATION_FAST)  # Changed from DURATION_NORMAL
        self._active_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def _setup_style(self):
        """Setup style"""
        if not theme_manager:
            return
        theme = theme_manager

        style_sheet = f"""
            FluentTabButton {{
                background-color: transparent;
                border: none;
                color: {theme.get_color('text_secondary').name()};
                font-size: 14px;
                font-family: "Segoe UI", sans-serif;
                padding: 8px 16px;
                text-align: left;
            }}
            FluentTabButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                color: {theme.get_color('text_primary').name()};
            }}
            FluentTabButton:checked {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('primary').name()};
                font-weight: 600;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _get_hover_progress(self) -> float:
        return self._hover_progress

    def _set_hover_progress(self, value: float):
        self._hover_progress = value
        self.update()

    def _get_active_progress(self) -> float:
        return self._active_progress

    def _set_active_progress(self, value: float):
        self._active_progress = value
        self.update()

    hover_progress = Property(
        float, _get_hover_progress, _set_hover_progress, None, "")
    active_progress = Property(
        float, _get_active_progress, _set_active_progress, None, "")

    def setActive(self, active: bool):
        """Set tab as active"""
        self._is_active = active
        self.setChecked(active)

        # Animate active state
        self._active_animation.setStartValue(self._active_progress)
        self._active_animation.setEndValue(1.0 if active else 0.0)
        self._active_animation.start()

    def isActive(self) -> bool:
        """Check if tab is active"""
        return self._is_active

    def enterEvent(self, event):
        """Handle mouse enter"""
        super().enterEvent(event)
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()

    def leaveEvent(self, event):
        """Handle mouse leave"""
        super().leaveEvent(event)
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()

    def paintEvent(self, event):
        """Paint the tab button"""
        super().paintEvent(event)

        if self._is_active and theme_manager:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            theme = theme_manager

            # Draw active indicator (bottom line)
            line_height = 3
            line_width = self.width() - 16
            line_x = 8
            line_y = self.height() - line_height

            # Animate line appearance
            current_width = int(line_width * self._active_progress)
            animated_rect = QRect(line_x, line_y, current_width, line_height)

            painter.fillRect(animated_rect, theme.get_color('primary'))

    def _on_theme_changed(self, _=None):
        """Handle theme change"""
        self._setup_style()


class FluentTabWidget(QWidget):
    """Fluent Design style tab widget"""

    # Signals
    currentChanged = Signal(int)  # Emitted when current tab changes
    tabCloseRequested = Signal(int)  # Emitted when tab close is requested

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._tabs: List[Dict[str, Any]] = []
        self._current_index = -1
        self._tab_buttons: List[FluentTabButton] = []
        self._closable_tabs = False
        self._movable_tabs = False
        self._scrollable_tabs = True

        self._setup_ui()
        self._setup_style()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab bar container
        self._tab_bar_container = QWidget()
        self._tab_bar_container.setFixedHeight(50)

        # Scrollable tab bar
        if self._scrollable_tabs:
            self._tab_scroll = QScrollArea()
            self._tab_scroll.setWidgetResizable(True)
            self._tab_scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self._tab_scroll.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Changed from ScrollBarNever
            self._tab_scroll.setFixedHeight(50)

            self._tab_bar = QWidget()
            self._tab_layout = QHBoxLayout(self._tab_bar)
            self._tab_layout.setContentsMargins(0, 0, 0, 0)
            self._tab_layout.setSpacing(2)
            self._tab_layout.addStretch()

            self._tab_scroll.setWidget(self._tab_bar)
            layout.addWidget(self._tab_scroll)
        else:
            self._tab_layout = QHBoxLayout(self._tab_bar_container)
            self._tab_layout.setContentsMargins(8, 0, 8, 0)
            self._tab_layout.setSpacing(2)
            self._tab_layout.addStretch()
            layout.addWidget(self._tab_bar_container)

        # Content area
        self._stack = QStackedWidget()
        layout.addWidget(self._stack, 1)

        # Separator line
        self._separator = QFrame()
        self._separator.setFixedHeight(1)
        # Insert separator between tab bar and stack
        layout.insertWidget(1, self._separator)

    def _setup_style(self):
        """Setup style"""
        if not theme_manager:
            return
        theme = theme_manager

        style_sheet = f"""
            FluentTabWidget {{
                background-color: {theme.get_color('background').name()};
            }}
            QScrollArea {{
                background-color: {theme.get_color('surface').name()};
                border: none;
            }}
            QFrame#_separator {{ /* Assuming you might want to name it for specific styling */
                background-color: {theme.get_color('border').name()};
            }}
        """
        # Apply to self and specific children if needed
        self.setStyleSheet(style_sheet)
        if hasattr(self, '_separator'):  # Ensure separator exists
            self._separator.setStyleSheet(
                f"background-color: {theme.get_color('border').name()};")

    def addTab(self, widget: QWidget, text: str, icon=None) -> int:
        """Add a new tab"""
        # Create tab data
        tab_data = {
            'widget': widget,
            'text': text,
            'icon': icon,
            'enabled': True,
            'visible': True
        }

        # Create tab button
        tab_button = FluentTabButton(text)
        # Capture the index correctly for the lambda
        new_tab_index = len(self._tabs)
        tab_button.clicked.connect(
            lambda _checked: self._on_tab_clicked(new_tab_index))

        # Add to collections
        self._tabs.append(tab_data)
        self._tab_buttons.append(tab_button)

        # Add to layouts
        self._tab_layout.insertWidget(len(self._tab_buttons) - 1, tab_button)
        self._stack.addWidget(widget)

        # Set as current if first tab
        if len(self._tabs) == 1:
            self.setCurrentIndex(0)

        return len(self._tabs) - 1

    def insertTab(self, index: int, widget: QWidget, text: str, icon=None) -> int:
        """Insert a tab at the specified index"""
        if not (0 <= index <= len(self._tabs)):  # Allow inserting at the end
            # Correct index if out of bounds for append-like behavior
            index = len(self._tabs)

        # Create tab data
        tab_data = {
            'widget': widget,
            'text': text,
            'icon': icon,
            'enabled': True,
            'visible': True
        }

        # Create tab button
        tab_button = FluentTabButton(text)
        # The lambda will capture the 'index' as it is at definition time.
        # This is fine if 'index' correctly represents the final position.

        # Insert into collections
        self._tabs.insert(index, tab_data)
        self._tab_buttons.insert(index, tab_button)

        # Update layouts
        self._tab_layout.insertWidget(index, tab_button)
        self._stack.insertWidget(index, widget)

        # Update click handlers for all tabs because indices change
        for i, btn in enumerate(self._tab_buttons):
            # Disconnect all previous connections to avoid multiple calls
            try:
                btn.clicked.disconnect()
            except RuntimeError:  # No connections to disconnect
                pass
            btn.clicked.connect(
                lambda _checked, idx=i: self._on_tab_clicked(idx))

        # Adjust current index if necessary
        if self._current_index >= index:
            self._current_index += 1
        # If inserting the first tab
        elif self._current_index == -1 and len(self._tabs) == 1:
            self.setCurrentIndex(0)

        return index

    def removeTab(self, index: int):
        """Remove a tab"""
        if not (0 <= index < len(self._tabs)):
            return

        # Remove from collections
        tab_data = self._tabs.pop(index)
        tab_button = self._tab_buttons.pop(index)

        # Remove from layouts
        self._tab_layout.removeWidget(tab_button)
        self._stack.removeWidget(tab_data['widget'])

        # Clean up
        tab_button.deleteLater()
        # Also delete the widget associated with the tab
        tab_data['widget'].deleteLater()

        # Update click handlers
        for i, btn in enumerate(self._tab_buttons):
            try:
                btn.clicked.disconnect()
            except RuntimeError:
                pass
            btn.clicked.connect(
                lambda _checked, idx=i: self._on_tab_clicked(idx))

        # Adjust current index
        if len(self._tabs) == 0:
            self._current_index = -1
        elif self._current_index == index:
            # If the removed tab was current, set new current tab
            new_index = max(0, index - 1) if index > 0 else 0
            self.setCurrentIndex(new_index)
        elif self._current_index > index:
            self._current_index -= 1

        # If after adjustment, current_index is out of bounds (e.g. -1 but tabs exist)
        # or points to a non-existent tab, re-evaluate.
        if self._current_index >= len(self._tabs) and len(self._tabs) > 0:
            self.setCurrentIndex(len(self._tabs) - 1)

    def setCurrentIndex(self, index: int):
        """Set the current tab by index"""
        if not (0 <= index < len(self._tabs)) or index == self._current_index:
            if len(self._tabs) == 0 and self._current_index != -1:  # Handle clearing all tabs
                # Check bounds
                if self._current_index >= 0 and self._current_index < len(self._tab_buttons):
                    self._tab_buttons[self._current_index].setActive(False)
                self._current_index = -1
                self._stack.setCurrentIndex(-1)  # Clear stack
                self.currentChanged.emit(-1)
            return

        # Deactivate previous tab
        # Check bounds
        if self._current_index >= 0 and self._current_index < len(self._tab_buttons):
            self._tab_buttons[self._current_index].setActive(False)

        # Activate new tab
        self._current_index = index
        if self._current_index < len(self._tab_buttons):  # Check bounds
            self._tab_buttons[index].setActive(True)
            self._stack.setCurrentIndex(index)
            self.currentChanged.emit(index)
        else:  # Should not happen if logic is correct
            self._current_index = -1
            self._stack.setCurrentIndex(-1)
            self.currentChanged.emit(-1)

    def setCurrentWidget(self, widget: QWidget):
        """Set the current tab by widget"""
        for i, tab_data in enumerate(self._tabs):
            if tab_data['widget'] == widget:
                self.setCurrentIndex(i)
                break

    def currentIndex(self) -> int:
        """Get the current tab index"""
        return self._current_index

    def currentWidget(self) -> Optional[QWidget]:
        """Get the current tab widget"""
        if 0 <= self._current_index < len(self._tabs):
            return self._tabs[self._current_index]['widget']
        return None

    def count(self) -> int:
        """Get the number of tabs"""
        return len(self._tabs)

    def widget(self, index: int) -> Optional[QWidget]:
        """Get widget at index"""
        if 0 <= index < len(self._tabs):
            return self._tabs[index]['widget']
        return None

    def tabText(self, index: int) -> str:
        """Get tab text at index"""
        if 0 <= index < len(self._tabs):
            return self._tabs[index]['text']
        return ""

    def setTabText(self, index: int, text: str):
        """Set tab text at index"""
        if 0 <= index < len(self._tabs):
            self._tabs[index]['text'] = text
            self._tab_buttons[index].setText(text)

    def tabEnabled(self, index: int) -> bool:
        """Check if tab is enabled"""
        if 0 <= index < len(self._tabs):
            return self._tabs[index]['enabled']
        return False

    def setTabEnabled(self, index: int, enabled: bool):
        """Set tab enabled state"""
        if 0 <= index < len(self._tabs):
            self._tabs[index]['enabled'] = enabled
            self._tab_buttons[index].setEnabled(enabled)

    def tabVisible(self, index: int) -> bool:
        """Check if tab is visible"""
        if 0 <= index < len(self._tabs):
            return self._tabs[index]['visible']
        return False

    def setTabVisible(self, index: int, visible: bool):
        """Set tab visibility"""
        if 0 <= index < len(self._tabs):
            self._tabs[index]['visible'] = visible
            self._tab_buttons[index].setVisible(visible)

    def setTabsClosable(self, closable: bool):
        """Set whether tabs can be closed"""
        self._closable_tabs = closable
        # Implementation for close buttons would go here

    def tabsClosable(self) -> bool:
        """Check if tabs are closable"""
        return self._closable_tabs

    def setMovable(self, movable: bool):
        """Set whether tabs can be moved"""
        self._movable_tabs = movable
        # Implementation for tab dragging would go here

    def isMovable(self) -> bool:
        """Check if tabs are movable"""
        return self._movable_tabs

    def clear(self):
        """Remove all tabs"""
        while self.count() > 0:
            self.removeTab(0)

    def _on_tab_clicked(self, index: int):
        """Handle tab button click"""
        if 0 <= index < len(self._tabs) and self._tabs[index]['enabled']:
            self.setCurrentIndex(index)

    def _on_theme_changed(self, _=None):
        """Handle theme change"""
        self._setup_style()
        for btn in self._tab_buttons:
            btn._on_theme_changed()  # Propagate theme change
