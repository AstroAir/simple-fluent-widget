"""
Fluent Design Style Tab Component
Enhanced with modern animations and micro-interactions
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QScrollArea, QFrame
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QRect, Property, QByteArray
from PySide6.QtGui import QPainter
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import FluentTransition, FluentMicroInteraction, FluentRevealEffect
from typing import Optional, List, Dict, Any


class FluentTabButton(QPushButton):
    """Individual tab button with enhanced animations"""

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
        """Setup enhanced animations"""
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_progress"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)

        self._active_animation = QPropertyAnimation(
            self, QByteArray(b"active_progress"))
        self._active_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._active_animation.setEasingCurve(FluentTransition.EASE_SPRING)

    def _setup_style(self):
        """Setup tab button style"""
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
        """Set tab as active with enhanced animation"""
        self._is_active = active
        self.setChecked(active)

        # Enhanced active state animation
        self._active_animation.setStartValue(self._active_progress)
        self._active_animation.setEndValue(1.0 if active else 0.0)
        self._active_animation.start()

        # Add micro-interaction when becoming active
        if active:
            FluentMicroInteraction.pulse_animation(self, scale=1.02)

    def isActive(self) -> bool:
        """Check if tab is active"""
        return self._is_active

    def enterEvent(self, event):
        """Handle mouse enter with enhanced hover effect"""
        super().enterEvent(event)
        
        # Enhanced hover animation
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        
        # Add subtle glow effect
        if self._enabled:
            FluentMicroInteraction.hover_glow(self, intensity=0.1)

    def leaveEvent(self, event):
        """Handle mouse leave"""
        super().leaveEvent(event)
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()

    def mousePressEvent(self, event):
        """Handle mouse press with micro-interaction"""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            FluentMicroInteraction.button_press(self, scale=0.98)

    def paintEvent(self, event):
        """Paint the tab button with enhanced visuals"""
        super().paintEvent(event)

        if self._is_active and theme_manager:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            theme = theme_manager

            # Draw enhanced active indicator
            line_height = 3
            line_width = self.width() - 16
            line_x = 8
            line_y = self.height() - line_height

            # Animated line appearance with gradient effect
            current_width = int(line_width * self._active_progress)
            animated_rect = QRect(line_x, line_y, current_width, line_height)

            # Add subtle shadow to the indicator
            shadow_rect = animated_rect.adjusted(0, 1, 0, 1)
            shadow_color = theme.get_color('shadow')
            if shadow_color.isValid():
                shadow_color.setAlpha(50)
                painter.fillRect(shadow_rect, shadow_color)

            painter.fillRect(animated_rect, theme.get_color('primary'))

    def _on_theme_changed(self, _=None):
        """Handle theme change"""
        self._setup_style()


class FluentTabWidget(QWidget):
    """Enhanced Fluent Design style tab widget with modern animations"""

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
        """Setup enhanced UI with animations"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Enhanced tab bar container
        self._tab_bar_container = QWidget()
        self._tab_bar_container.setFixedHeight(50)

        # Scrollable tab bar with smooth scrolling
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
            self._tab_layout = QHBoxLayout(self._tab_bar_container)
            self._tab_layout.setContentsMargins(8, 0, 8, 0)
            self._tab_layout.setSpacing(4)
            self._tab_layout.addStretch()
            layout.addWidget(self._tab_bar_container)

        # Enhanced separator line
        self._separator = QFrame()
        self._separator.setFixedHeight(1)
        self._separator.setFrameShape(QFrame.Shape.HLine)
        layout.insertWidget(1, self._separator)

        # Content area with reveal animations
        self._stack = QStackedWidget()
        layout.addWidget(self._stack, 1)

    def _setup_style(self):
        """Setup enhanced styling"""
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
        
        self.setStyleSheet(style_sheet)
        if hasattr(self, '_separator'):
            self._separator.setStyleSheet(
                f"background-color: {theme.get_color('border').name()}; border-radius: 0px;")

    def addTab(self, widget: QWidget, text: str, icon=None) -> int:
        """Add a new tab with reveal animation"""
        # Create tab data
        tab_data = {
            'widget': widget,
            'text': text,
            'icon': icon,
            'enabled': True,
            'visible': True
        }

        # Create enhanced tab button
        tab_button = FluentTabButton(text)
        new_tab_index = len(self._tabs)
        tab_button.clicked.connect(
            lambda checked: self._on_tab_clicked(new_tab_index, checked))

        # Add to collections
        self._tabs.append(tab_data)
        self._tab_buttons.append(tab_button)

        # Add to layouts with reveal animation
        self._tab_layout.insertWidget(len(self._tab_buttons) - 1, tab_button)
        self._stack.addWidget(widget)

        # Animate new tab appearance
        FluentRevealEffect.scale_in(tab_button, duration=200)

        # Set as current if first tab
        if len(self._tabs) == 1:
            self.setCurrentIndex(0)

        return len(self._tabs) - 1

    def insertTab(self, index: int, widget: QWidget, text: str, icon=None) -> int:
        """Insert a tab at the specified index with animation"""
        if not (0 <= index <= len(self._tabs)):
            index = len(self._tabs)

        # Create tab data
        tab_data = {
            'widget': widget,
            'text': text,
            'icon': icon,
            'enabled': True,
            'visible': True
        }

        # Create enhanced tab button
        tab_button = FluentTabButton(text)

        # Insert into collections
        self._tabs.insert(index, tab_data)
        self._tab_buttons.insert(index, tab_button)

        # Update layouts
        self._tab_layout.insertWidget(index, tab_button)
        self._stack.insertWidget(index, widget)

        # Update click handlers for all tabs
        for i, btn in enumerate(self._tab_buttons):
            try:
                btn.clicked.disconnect()
            except RuntimeError:
                pass
            btn.clicked.connect(
                lambda checked, idx=i: self._on_tab_clicked(idx, checked))

        # Animate insertion
        FluentRevealEffect.slide_in(tab_button, direction="left")

        # Adjust current index if necessary
        if self._current_index >= index:
            self._current_index += 1
        elif self._current_index == -1 and len(self._tabs) == 1:
            self.setCurrentIndex(0)

        return index

    def removeTab(self, index: int):
        """Remove a tab with fade-out animation"""
        if not (0 <= index < len(self._tabs)):
            return

        tab_button = self._tab_buttons[index]
        
        # Animate removal
        fade_out = FluentTransition.create_transition(
            tab_button, FluentTransition.FADE, duration=150)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        
        # Remove after animation completes
        fade_out.finished.connect(lambda: self._complete_tab_removal(index))
        fade_out.start()

    def _complete_tab_removal(self, index: int):
        """Complete tab removal after animation"""
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
        tab_data['widget'].deleteLater()

        # Update click handlers
        for i, btn in enumerate(self._tab_buttons):
            try:
                btn.clicked.disconnect()
            except RuntimeError:
                pass
            btn.clicked.connect(
                lambda checked, idx=i: self._on_tab_clicked(idx, checked))

        # Adjust current index
        if len(self._tabs) == 0:
            self._current_index = -1
        elif self._current_index == index:
            new_index = max(0, index - 1) if index > 0 else 0
            self.setCurrentIndex(new_index)
        elif self._current_index > index:
            self._current_index -= 1

        if self._current_index >= len(self._tabs) and len(self._tabs) > 0:
            self.setCurrentIndex(len(self._tabs) - 1)

    def setCurrentIndex(self, index: int):
        """Set the current tab with smooth transition"""
        if not (0 <= index < len(self._tabs)) or index == self._current_index:
            if len(self._tabs) == 0 and self._current_index != -1:
                if self._current_index >= 0 and self._current_index < len(self._tab_buttons):
                    self._tab_buttons[self._current_index].setActive(False)
                self._current_index = -1
                self._stack.setCurrentIndex(-1)
                self.currentChanged.emit(-1)
            return

        # Deactivate previous tab with animation
        if self._current_index >= 0 and self._current_index < len(self._tab_buttons):
            self._tab_buttons[self._current_index].setActive(False)

        # Activate new tab with enhanced animation
        self._current_index = index
        if self._current_index < len(self._tab_buttons):
            self._tab_buttons[index].setActive(True)
            
            # Animate content transition
            new_widget = self._tabs[index]['widget']
            self._stack.setCurrentIndex(index)
            
            # Add reveal effect to new content
            FluentRevealEffect.fade_in(new_widget, duration=200)
            
            self.currentChanged.emit(index)
        else:
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
        """Set tab enabled state with visual feedback"""
        if 0 <= index < len(self._tabs):
            self._tabs[index]['enabled'] = enabled
            self._tab_buttons[index].setEnabled(enabled)
            
            # Add visual feedback for disabled state
            if not enabled:
                FluentTransition.create_transition(
                    self._tab_buttons[index], FluentTransition.FADE, duration=150
                ).setEndValue(0.5)

    def tabVisible(self, index: int) -> bool:
        """Check if tab is visible"""
        if 0 <= index < len(self._tabs):
            return self._tabs[index]['visible']
        return False

    def setTabVisible(self, index: int, visible: bool):
        """Set tab visibility with animation"""
        if 0 <= index < len(self._tabs):
            self._tabs[index]['visible'] = visible
            
            if visible:
                self._tab_buttons[index].setVisible(True)
                FluentRevealEffect.scale_in(self._tab_buttons[index])
            else:
                fade_out = FluentTransition.create_transition(
                    self._tab_buttons[index], FluentTransition.FADE, duration=150)
                fade_out.setEndValue(0.0)
                fade_out.finished.connect(
                    lambda: self._tab_buttons[index].setVisible(False))
                fade_out.start()

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
        """Remove all tabs with staggered animation"""
        if len(self._tabs) > 0:
            # Animate removal of all tabs
            FluentRevealEffect.staggered_reveal(
                [btn for btn in reversed(self._tab_buttons)], stagger_delay=50)
            
        # Clear after animations
        while self.count() > 0:
            self.removeTab(0)

    def _on_tab_clicked(self, index: int, checked: bool):
        """Handle tab button click with micro-interaction"""
        # Reference checked parameter to avoid warning
        _ = checked
        
        if 0 <= index < len(self._tabs) and self._tabs[index]['enabled']:
            # Add click feedback
            FluentMicroInteraction.ripple_effect(self._tab_buttons[index])
            self.setCurrentIndex(index)

    def _on_theme_changed(self, _=None):
        """Handle theme change"""
        self._setup_style()
        for btn in self._tab_buttons:
            btn._on_theme_changed()
