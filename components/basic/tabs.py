"""
Fluent Design Style Tab Component
Optimized for high performance with streamlined animations
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton,
                               QScrollArea, QFrame, QSizePolicy)
from PySide6.QtCore import (Qt, Signal, QPropertyAnimation, QRect, Property, QEasingCurve, QByteArray,
                            QTimer)
from PySide6.QtGui import QPainter, QColor
from functools import partial
from typing import Optional, List, Dict, Any

# Import core modules
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import FluentTransition, FluentMicroInteraction, FluentRevealEffect


class FluentTabButton(QPushButton):
    """Optimized tab button with efficient animations"""

    # Class-level style caching for performance
    _style_cache = {}
    _theme_connected = False

    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        # Essential state variables
        self._is_active = False
        self._hover_progress = 0.0
        self._active_progress = 0.0

        # Setup appearance
        self.setCheckable(True)
        self.setMinimumHeight(40)
        self.setMinimumWidth(80)

        # Apply styles
        self._setup_style()

        # Connect theme changes once per class
        if theme_manager and not FluentTabButton._theme_connected:
            theme_manager.theme_changed.connect(self._on_theme_class_changed)
            FluentTabButton._theme_connected = True

    @classmethod
    def _on_theme_class_changed(cls, _=None):
        """Update class-level styles when theme changes"""
        cls._style_cache = {}  # Clear cache
        # Individual instances will update their styles when needed

    def _setup_style(self):
        """Setup tab button style with caching"""
        if not theme_manager:
            return

        # Use cached style if available based on theme ID
        theme_id = id(theme_manager)
        if theme_id in FluentTabButton._style_cache:
            self.setStyleSheet(FluentTabButton._style_cache[theme_id])
            return

        # Generate style
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
                border-radius: 6px;
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

        # Cache and apply
        FluentTabButton._style_cache[theme_id] = style_sheet
        self.setStyleSheet(style_sheet)

    def _get_hover_progress(self) -> float:
        return self._hover_progress

    def _set_hover_progress(self, value: float):
        if abs(self._hover_progress - value) > 0.01:  # Only update if significant change
            self._hover_progress = value
            self.update()

    def _get_active_progress(self) -> float:
        return self._active_progress

    def _set_active_progress(self, value: float):
        if abs(self._active_progress - value) > 0.01:  # Only update if significant change
            self._active_progress = value
            self.update()

    # Define properties for animations
    hover_progress = Property(
        float, _get_hover_progress, _set_hover_progress, None, "")
    active_progress = Property(
        float, _get_active_progress, _set_active_progress, None, "")

    def setActive(self, active: bool):
        """Set tab as active with optimized animation"""
        if self._is_active == active:
            return

        self._is_active = active
        self.setChecked(active)

        # Create and start animation
        active_anim = QPropertyAnimation(self, QByteArray(b"active_progress"))
        active_anim.setDuration(FluentAnimation.DURATION_FAST)
        active_anim.setEasingCurve(FluentTransition.EASE_SPRING)
        active_anim.setStartValue(self._active_progress)
        active_anim.setEndValue(1.0 if active else 0.0)
        active_anim.start()

        # Add subtle visual feedback when becoming active
        if active:
            FluentMicroInteraction.pulse_animation(self, scale=1.02)

    def isActive(self) -> bool:
        """Check if tab is active"""
        return self._is_active

    def enterEvent(self, event):
        """Handle mouse enter with optimized hover effect"""
        super().enterEvent(event)

        # Create and start hover animation
        hover_anim = QPropertyAnimation(self, QByteArray(b"hover_progress"))
        hover_anim.setDuration(FluentAnimation.DURATION_FAST)
        hover_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        hover_anim.setStartValue(self._hover_progress)
        hover_anim.setEndValue(1.0)
        hover_anim.start()

    def leaveEvent(self, event):
        """Handle mouse leave with optimized animation"""
        super().leaveEvent(event)

        # Create and start hover animation
        hover_anim = QPropertyAnimation(self, QByteArray(b"hover_progress"))
        hover_anim.setDuration(FluentAnimation.DURATION_FAST)
        hover_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        hover_anim.setStartValue(self._hover_progress)
        hover_anim.setEndValue(0.0)
        hover_anim.start()

    def mousePressEvent(self, event):
        """Handle mouse press with visual feedback"""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            FluentMicroInteraction.button_press(self, scale=0.98)

    def paintEvent(self, event):
        """Paint the tab button with optimized rendering"""
        super().paintEvent(event)

        # Only draw when active or animating to/from active state
        if self._active_progress > 0.01 and theme_manager:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            theme = theme_manager

            # Draw active indicator line
            line_height = 3
            line_width = self.width() - 16
            line_x = 8
            line_y = self.height() - line_height

            current_width = int(line_width * self._active_progress)
            animated_rect = QRect(line_x, line_y, current_width, line_height)

            # Draw the line
            painter.fillRect(animated_rect, theme.get_color('primary'))


class FluentTabWidget(QWidget):
    """Optimized Fluent Design style tab widget"""

    # Signals
    currentChanged = Signal(int)
    tabCloseRequested = Signal(int)

    # Class-level style caching
    _style_cache = {}
    _theme_connected = False

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Single data structure for tab management
        # Stores {widget, button, text, icon, enabled, visible}
        self._tabs = []
        self._current_index = -1

        # Configuration
        self._closable_tabs = False
        self._movable_tabs = False
        self._scrollable_tabs = True

        # Setup UI and apply styles
        self._setup_ui()
        self._setup_style()

        # Connect theme changes once per class
        if theme_manager and not FluentTabWidget._theme_connected:
            theme_manager.theme_changed.connect(self._on_theme_class_changed)
            FluentTabWidget._theme_connected = True

    def _setup_ui(self):
        """Setup UI with optimized layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab bar section - optimized for performance
        if self._scrollable_tabs:
            self._tab_scroll = QScrollArea()
            self._tab_scroll.setWidgetResizable(True)
            self._tab_scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self._tab_scroll.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self._tab_scroll.setFixedHeight(50)

            self._tab_bar = QWidget()
            self._tab_layout = QHBoxLayout(self._tab_bar)
            self._tab_layout.setContentsMargins(8, 0, 8, 0)
            self._tab_layout.setSpacing(4)
            self._tab_layout.addStretch()

            self._tab_scroll.setWidget(self._tab_bar)
            layout.addWidget(self._tab_scroll)
        else:
            self._tab_bar_container = QWidget()
            self._tab_bar_container.setFixedHeight(50)
            self._tab_layout = QHBoxLayout(self._tab_bar_container)
            self._tab_layout.setContentsMargins(8, 0, 8, 0)
            self._tab_layout.setSpacing(4)
            self._tab_layout.addStretch()
            layout.addWidget(self._tab_bar_container)

        # Separator line
        self._separator = QFrame()
        self._separator.setFixedHeight(1)
        self._separator.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(self._separator)

        # Content area
        self._stack = QStackedWidget()
        layout.addWidget(self._stack, 1)

    @classmethod
    def _on_theme_class_changed(cls, _=None):
        """Update class-level styles when theme changes"""
        cls._style_cache = {}  # Clear cache

    def _setup_style(self):
        """Setup widget style with efficient caching"""
        if not theme_manager:
            return

        # Use cached style if available based on theme ID
        theme_id = id(theme_manager)
        if theme_id in FluentTabWidget._style_cache:
            self.setStyleSheet(
                FluentTabWidget._style_cache[theme_id]['widget'])
            self._separator.setStyleSheet(
                FluentTabWidget._style_cache[theme_id]['separator'])
            return

        # Generate style
        theme = theme_manager

        widget_style = f"""
            FluentTabWidget {{
                background-color: {theme.get_color('background').name()};
            }}
            QScrollArea {{
                background-color: {theme.get_color('surface').name()};
                border: none;
                border-radius: 8px;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
            QScrollBar:horizontal {{
                background-color: {theme.get_color('surface_variant').name()};
                height: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {theme.get_color('outline').name()};
                border-radius: 3px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {theme.get_color('primary').name()};
            }}
        """

        separator_style = f"background-color: {theme.get_color('border').name()}; border-radius: 0px;"

        # Cache and apply
        FluentTabWidget._style_cache[theme_id] = {
            'widget': widget_style,
            'separator': separator_style
        }

        self.setStyleSheet(widget_style)
        self._separator.setStyleSheet(separator_style)

    def addTab(self, widget: QWidget, text: str, icon=None) -> int:
        """Add a new tab with optimized reveal animation"""
        # Create tab button
        tab_button = FluentTabButton(text)

        # Store all tab information in a single dictionary
        tab_info = {
            'widget': widget,
            'button': tab_button,
            'text': text,
            'icon': icon,
            'enabled': True,
            'visible': True
        }

        # Add to collection
        index = len(self._tabs)
        self._tabs.append(tab_info)

        # Connect button using partial for efficiency
        tab_button.clicked.connect(partial(self._on_tab_clicked, index))

        # Add to layout
        self._tab_layout.insertWidget(len(self._tabs) - 1, tab_button)
        self._stack.addWidget(widget)

        # Animate new tab appearance
        FluentRevealEffect.scale_in(tab_button, duration=200)

        # Set as current if first tab
        if len(self._tabs) == 1:
            self.setCurrentIndex(0)

        return index

    def insertTab(self, index: int, widget: QWidget, text: str, icon=None) -> int:
        """Insert a tab at the specified index with animation"""
        if not (0 <= index <= len(self._tabs)):
            index = len(self._tabs)

        # Create tab button
        tab_button = FluentTabButton(text)

        # Store tab information
        tab_info = {
            'widget': widget,
            'button': tab_button,
            'text': text,
            'icon': icon,
            'enabled': True,
            'visible': True
        }

        # Insert into collection
        self._tabs.insert(index, tab_info)

        # Update layout
        self._tab_layout.insertWidget(index, tab_button)
        self._stack.insertWidget(index, widget)

        # Update connections efficiently for affected tabs
        self._update_tab_connections(index)

        # Animate insertion
        FluentRevealEffect.slide_in(tab_button, direction="left")

        # Adjust current index if necessary
        if self._current_index >= index:
            self._current_index += 1
        elif self._current_index == -1 and len(self._tabs) == 1:
            self.setCurrentIndex(0)

        return index

    def _update_tab_connections(self, start_index=0):
        """Update tab connections efficiently"""
        for i in range(start_index, len(self._tabs)):
            btn = self._tabs[i]['button']
            try:
                btn.clicked.disconnect()
            except RuntimeError:
                pass
            btn.clicked.connect(partial(self._on_tab_clicked, i))

    def removeTab(self, index: int):
        """Remove a tab with fade-out animation"""
        if not (0 <= index < len(self._tabs)):
            return

        tab_info = self._tabs[index]
        tab_button = tab_info['button']

        # Animate removal
        fade_out = FluentTransition.create_transition(
            tab_button, FluentTransition.FADE, duration=150)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)

        # Complete removal after animation
        fade_out.finished.connect(
            lambda idx=index: self._complete_tab_removal(idx))
        fade_out.start()

    def _complete_tab_removal(self, index: int):
        """Complete tab removal after animation"""
        if not (0 <= index < len(self._tabs)):
            return

        tab_info = self._tabs[index]

        # Remove from UI
        self._tab_layout.removeWidget(tab_info['button'])
        self._stack.removeWidget(tab_info['widget'])

        # Clean up
        tab_info['button'].deleteLater()

        # Remove from collection
        self._tabs.pop(index)

        # Update connections for affected tabs
        self._update_tab_connections(index)

        # Update current index efficiently
        if len(self._tabs) == 0:
            self._current_index = -1
        elif self._current_index == index:
            new_index = max(0, index - 1) if index > 0 else 0
            self.setCurrentIndex(new_index)
        elif self._current_index > index:
            self._current_index -= 1

    def setCurrentIndex(self, index: int):
        """Set the current tab with smooth transition"""
        if index == self._current_index:
            return

        if not (0 <= index < len(self._tabs)) and index != -1:
            if len(self._tabs) == 0 and self._current_index != -1:
                if self._current_index >= 0 and self._current_index < len(self._tabs):
                    self._tabs[self._current_index]['button'].setActive(False)
                self._current_index = -1
                self._stack.setCurrentIndex(-1)
                self.currentChanged.emit(-1)
            return

        # Handle special case for clearing selection
        if index == -1:
            if 0 <= self._current_index < len(self._tabs):
                self._tabs[self._current_index]['button'].setActive(False)
            self._current_index = -1
            self._stack.setCurrentIndex(-1)
            self.currentChanged.emit(-1)
            return

        # Deactivate previous tab
        if 0 <= self._current_index < len(self._tabs):
            self._tabs[self._current_index]['button'].setActive(False)

        # Activate new tab
        self._current_index = index
        self._tabs[index]['button'].setActive(True)

        # Change content with animation
        new_widget = self._tabs[index]['widget']
        self._stack.setCurrentWidget(new_widget)

        # Add subtle reveal effect
        FluentRevealEffect.fade_in(new_widget, duration=150)

        # Emit signal
        self.currentChanged.emit(index)

    def setCurrentWidget(self, widget: QWidget):
        """Set the current tab by widget"""
        for i, tab_info in enumerate(self._tabs):
            if tab_info['widget'] == widget:
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
            self._tabs[index]['button'].setText(text)

    def tabEnabled(self, index: int) -> bool:
        """Check if tab is enabled"""
        if 0 <= index < len(self._tabs):
            return self._tabs[index]['enabled']
        return False

    def setTabEnabled(self, index: int, enabled: bool):
        """Set tab enabled state with visual feedback"""
        if 0 <= index < len(self._tabs):
            if self._tabs[index]['enabled'] == enabled:
                return

            self._tabs[index]['enabled'] = enabled
            self._tabs[index]['button'].setEnabled(enabled)

            # Add visual feedback for disabled state
            if not enabled:
                anim = QPropertyAnimation(
                    self._tabs[index]['button'], QByteArray(b"windowOpacity"))
                anim.setDuration(150)
                anim.setEndValue(0.5)
                anim.start()
            else:
                anim = QPropertyAnimation(
                    self._tabs[index]['button'], QByteArray(b"windowOpacity"))
                anim.setDuration(150)
                anim.setEndValue(1.0)
                anim.start()

    def tabVisible(self, index: int) -> bool:
        """Check if tab is visible"""
        if 0 <= index < len(self._tabs):
            return self._tabs[index]['visible']
        return False

    def setTabVisible(self, index: int, visible: bool):
        """Set tab visibility with animation"""
        if not (0 <= index < len(self._tabs)):
            return

        if self._tabs[index]['visible'] == visible:
            return

        self._tabs[index]['visible'] = visible
        tab_button = self._tabs[index]['button']

        if visible:
            tab_button.setVisible(True)
            FluentRevealEffect.scale_in(tab_button)
        else:
            fade_out = FluentTransition.create_transition(
                tab_button, FluentTransition.FADE, duration=150)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.finished.connect(lambda: tab_button.setVisible(False))
            fade_out.start()

    def setTabsClosable(self, closable: bool):
        """Set whether tabs can be closable"""
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
        """Remove all tabs with optimized approach"""
        if not self._tabs:
            return

        # Get buttons for animation
        buttons = [tab['button'] for tab in reversed(self._tabs)]

        # Start staggered animations
        FluentRevealEffect.staggered_reveal(buttons, stagger_delay=50)

        # Clean up after animations complete
        cleanup_delay = len(buttons) * 50 + 150  # Total animation time
        QTimer.singleShot(cleanup_delay, self._complete_clear)

    def _complete_clear(self):
        """Complete the clear operation"""
        while self.count() > 0:
            self.removeTab(0)

    def _on_tab_clicked(self, index: int, checked=False):
        """Handle tab button click with optimized feedback"""
        # Reference checked parameter to avoid warning
        _ = checked

        if 0 <= index < len(self._tabs) and self._tabs[index]['enabled']:
            # Add visual feedback
            FluentMicroInteraction.ripple_effect(self._tabs[index]['button'])
            self.setCurrentIndex(index)

    def _on_theme_changed(self, _=None):
        """Handle theme change efficiently"""
        self._setup_style()

        # Update tab buttons
        for tab_info in self._tabs:
            tab_info['button']._setup_style()
