# filepath: d:\Project\simple-fluent-widget\components\basic\checkbox.py
"""
Optimized Fluent Design Style Checkbox and Radio Button Components
Enhanced with better performance, smoother animations and consistent theme integration
"""

from PySide6.QtWidgets import QCheckBox, QRadioButton, QWidget, QButtonGroup, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer, QByteArray
from PySide6.QtGui import QColor
from core.theme import theme_manager
from typing import Optional, List


class FluentCheckBox(QCheckBox):
    """Optimized Fluent Design Style Checkbox with better performance and smoother animations"""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        # Performance optimization: minimize object creation
        self._is_hovered = False
        self._is_checked = False
        self._style_cache = ""

        # Single animation controller for better performance
        self._hover_animation = None
        self._check_animation = None

        # Debounce timer for style updates
        self._style_update_timer = QTimer()
        self._style_update_timer.setSingleShot(True)
        self._style_update_timer.timeout.connect(self._update_style_impl)

        self._setup_optimized_animations()
        self._setup_consistent_style()

        # Connect signals with optimizations
        self.stateChanged.connect(self._on_state_changed_optimized)
        theme_manager.theme_changed.connect(self._on_theme_changed_optimized)

    def _setup_optimized_animations(self):
        """Setup lightweight, performance-optimized animations"""
        # Create reusable animations with optimal settings
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"minimumHeight"))
        # Reduced duration for snappier feel
        self._hover_animation.setDuration(120)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._check_animation = QPropertyAnimation(
            self, QByteArray(b"minimumHeight"))
        self._check_animation.setDuration(150)
        self._check_animation.setEasingCurve(QEasingCurve.Type.OutBack)

        # Set initial values to prevent None state
        self._hover_animation.setStartValue(24)
        self._hover_animation.setEndValue(24)
        self._check_animation.setStartValue(24)
        self._check_animation.setEndValue(24)

    def _setup_consistent_style(self):
        """Setup consistent style following Fluent Design principles"""
        # Use cached style to avoid repeated calculations
        if not self._style_cache:
            self._generate_style_cache()

        self.setStyleSheet(self._style_cache)

    def _generate_style_cache(self):
        """Generate and cache the complete stylesheet"""
        current_theme = theme_manager

        # Get theme colors with fallbacks
        primary = current_theme.get_color('primary')
        surface = current_theme.get_color('surface')
        background = current_theme.get_color('background')
        border = current_theme.get_color('border')
        text_primary = current_theme.get_color('text_primary')
        text_disabled = current_theme.get_color('text_disabled')
        accent_light = current_theme.get_color('accent_light')

        # Optimized stylesheet with Qt-compatible CSS properties
        self._style_cache = f"""
            FluentCheckBox {{
                font-family: 'Segoe UI', 'Microsoft YaHei UI', system-ui, sans-serif;
                font-size: 14px;
                font-weight: 400;
                color: {text_primary.name()};
                spacing: 10px;
                padding: 4px 0px;
                min-height: 24px;
                border: none;
                background: transparent;
            }}
            
            FluentCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {border.name()};
                background-color: {surface.name()};
                margin: 0px;
            }}
            
            FluentCheckBox::indicator:hover {{
                border-color: {primary.name()};
                background-color: {accent_light.name()};
            }}
            
            FluentCheckBox::indicator:focus {{
                border-color: {primary.name()};
                border: 3px solid {primary.name()};
            }}
            
            FluentCheckBox::indicator:checked {{
                background-color: {primary.name()};
                border-color: {primary.name()};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC41IDFMNCA3LjVMMSA0LjUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPg==);
            }}
            
            FluentCheckBox::indicator:checked:hover {{
                background-color: {primary.lighter(110).name()};
                border-color: {primary.lighter(110).name()};
            }}
            
            FluentCheckBox::indicator:indeterminate {{
                background-color: {primary.name()};
                border-color: {primary.name()};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iMiIgdmlld0JveD0iMCAwIDEwIDIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFIOSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KPC9zdmc+);
            }}
            
            FluentCheckBox::indicator:disabled {{
                background-color: {surface.darker(105).name()};
                border-color: {border.darker(120).name()};
                opacity: 0.6;
            }}
            
            FluentCheckBox:disabled {{
                color: {text_disabled.name()};
                opacity: 0.6;
            }}
            
            FluentCheckBox:focus {{
                outline: none;
            }}
        """

    def _on_state_changed_optimized(self, state):
        """Optimized state change handler with minimal overhead"""
        was_checked = self._is_checked
        self._is_checked = (state == Qt.CheckState.Checked)

        # Only animate if state actually changed
        if was_checked != self._is_checked:
            self._animate_check_transition()

    def _animate_check_transition(self):
        """Lightweight check animation"""
        if self._is_checked and self._check_animation:
            # Subtle scale effect using existing animation
            if self._check_animation.state() != QPropertyAnimation.State.Running:
                current_height = self.minimumHeight()
                self._check_animation.setStartValue(current_height)
                self._check_animation.setEndValue(current_height + 2)
                self._check_animation.finished.connect(
                    self._restore_check_size)
                self._check_animation.start()

    def _restore_check_size(self):
        """Restore size after check animation"""
        if self._check_animation:
            self._check_animation.finished.disconnect()
            current_height = self.minimumHeight()
            self._check_animation.setStartValue(current_height)
            self._check_animation.setEndValue(24)  # Default height
            self._check_animation.start()

    def _on_theme_changed_optimized(self, theme_name: str):
        """Optimized theme change with debouncing"""
        # Clear cache and schedule update
        self._style_cache = ""

        # Debounce style updates for better performance
        if not self._style_update_timer.isActive():
            self._style_update_timer.start(50)  # 50ms debounce

    def _update_style_impl(self):
        """Actual style update implementation"""
        self._setup_consistent_style()

    def enterEvent(self, event):
        """Optimized hover enter event"""
        if not self._is_hovered:
            self._is_hovered = True
            self._animate_hover_enter()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Optimized hover leave event"""
        if self._is_hovered:
            self._is_hovered = False
            self._animate_hover_leave()
        super().leaveEvent(event)

    def _animate_hover_enter(self):
        """Lightweight hover enter animation"""
        if self._hover_animation and self._hover_animation.state() != QPropertyAnimation.State.Running:
            current_height = self.minimumHeight()
            self._hover_animation.setStartValue(current_height)
            self._hover_animation.setEndValue(26)  # Slight increase
            self._hover_animation.start()

    def _animate_hover_leave(self):
        """Lightweight hover leave animation"""
        if self._hover_animation and self._hover_animation.state() != QPropertyAnimation.State.Running:
            current_height = self.minimumHeight()
            self._hover_animation.setStartValue(current_height)
            self._hover_animation.setEndValue(24)  # Back to normal
            self._hover_animation.start()

    def mousePressEvent(self, event):
        """Optimized mouse press with subtle visual feedback"""
        # Add subtle press feedback via CSS transition
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Optimized mouse release"""
        super().mouseReleaseEvent(event)


class FluentRadioButton(QRadioButton):
    """Optimized Fluent Design Style Radio Button with consistent theming and animations"""

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        # Performance optimization
        self._is_hovered = False
        self._is_selected = False
        self._style_cache = ""

        # Animation controller for better performance
        self._hover_animation = None
        self._check_animation = None

        # Debounce timer for style updates
        self._style_update_timer = QTimer()
        self._style_update_timer.setSingleShot(True)
        self._style_update_timer.timeout.connect(self._update_style_impl)

        self._setup_optimized_animations()
        self._setup_consistent_style()

        # Connect signals
        self.toggled.connect(self._on_toggled_optimized)
        theme_manager.theme_changed.connect(self._on_theme_changed_optimized)

    def _setup_optimized_animations(self):
        """Setup lightweight, performance-optimized animations"""
        # Create reusable animations with optimal settings
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"minimumHeight"))
        self._hover_animation.setDuration(120)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._check_animation = QPropertyAnimation(
            self, QByteArray(b"minimumHeight"))
        self._check_animation.setDuration(150)
        self._check_animation.setEasingCurve(QEasingCurve.Type.OutBack)

        # Set initial values to prevent None state
        self._hover_animation.setStartValue(24)
        self._hover_animation.setEndValue(24)
        self._check_animation.setStartValue(24)
        self._check_animation.setEndValue(24)

    def _setup_consistent_style(self):
        """Setup consistent style following Fluent Design principles"""
        if not self._style_cache:
            self._generate_style_cache()

        self.setStyleSheet(self._style_cache)

    def _generate_style_cache(self):
        """Generate and cache the complete stylesheet"""
        current_theme = theme_manager

        # Get theme colors with fallbacks
        primary = current_theme.get_color('primary')
        surface = current_theme.get_color('surface')
        border = current_theme.get_color('border')
        text_primary = current_theme.get_color('text_primary')
        text_disabled = current_theme.get_color('text_disabled')
        accent_light = current_theme.get_color('accent_light')

        # Optimized stylesheet with Qt-compatible CSS properties (removed transition, box-shadow, transform)
        self._style_cache = f"""
            FluentRadioButton {{
                font-family: 'Segoe UI', 'Microsoft YaHei UI', system-ui, sans-serif;
                font-size: 14px;
                font-weight: 400;
                color: {text_primary.name()};
                spacing: 10px;
                padding: 4px 0px;
                min-height: 24px;
                border: none;
                background: transparent;
            }}
            
            FluentRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid {border.name()};
                background-color: {surface.name()};
                margin: 0px;
            }}
            
            FluentRadioButton::indicator:hover {{
                border-color: {primary.name()};
                background-color: {accent_light.name()};
            }}
            
            FluentRadioButton::indicator:focus {{
                border-color: {primary.name()};
                border: 3px solid {primary.name()};
            }}
            
            FluentRadioButton::indicator:checked {{
                background-color: {primary.name()};
                border-color: {primary.name()};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOCIgaGVpZ2h0PSI4IiB2aWV3Qm94PSIwIDAgOCA4IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8Y2lyY2xlIGN4PSI0IiBjeT0iNCIgcj0iNCIgZmlsbD0id2hpdGUiLz4KPC9zdmc+);
            }}
            
            FluentRadioButton::indicator:checked:hover {{
                background-color: {primary.lighter(110).name()};
                border-color: {primary.lighter(110).name()};
            }}
            
            FluentRadioButton::indicator:disabled {{
                background-color: {surface.darker(105).name()};
                border-color: {border.darker(120).name()};
                opacity: 0.6;
            }}
            
            FluentRadioButton:disabled {{
                color: {text_disabled.name()};
                opacity: 0.6;
            }}
            
            FluentRadioButton:focus {{
                outline: none;
            }}
        """

    def _on_toggled_optimized(self, checked: bool):
        """Optimized toggle handler with animation"""
        was_selected = self._is_selected
        self._is_selected = checked

        # Only animate if state actually changed
        if was_selected != self._is_selected and self._is_selected:
            self._animate_check_transition()

    def _animate_check_transition(self):
        """Lightweight check animation"""
        if self._check_animation:
            # Subtle scale effect using existing animation
            if self._check_animation.state() != QPropertyAnimation.State.Running:
                current_height = self.minimumHeight()
                self._check_animation.setStartValue(current_height)
                self._check_animation.setEndValue(current_height + 2)
                self._check_animation.finished.connect(
                    self._restore_check_size)
                self._check_animation.start()

    def _restore_check_size(self):
        """Restore size after check animation"""
        if self._check_animation:
            self._check_animation.finished.disconnect()
            current_height = self.minimumHeight()
            self._check_animation.setStartValue(current_height)
            self._check_animation.setEndValue(24)  # Default height
            self._check_animation.start()

    def _on_theme_changed_optimized(self, theme_name: str):
        """Optimized theme change with debouncing"""
        self._style_cache = ""

        if not self._style_update_timer.isActive():
            self._style_update_timer.start(50)

    def _update_style_impl(self):
        """Actual style update implementation"""
        self._setup_consistent_style()

    def enterEvent(self, event):
        """Optimized hover enter event"""
        if not self._is_hovered:
            self._is_hovered = True
            self._animate_hover_enter()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Optimized hover leave event"""
        if self._is_hovered:
            self._is_hovered = False
            self._animate_hover_leave()
        super().leaveEvent(event)

    def _animate_hover_enter(self):
        """Lightweight hover enter animation"""
        if self._hover_animation and self._hover_animation.state() != QPropertyAnimation.State.Running:
            current_height = self.minimumHeight()
            self._hover_animation.setStartValue(current_height)
            self._hover_animation.setEndValue(26)  # Slight increase
            self._hover_animation.start()

    def _animate_hover_leave(self):
        """Lightweight hover leave animation"""
        if self._hover_animation and self._hover_animation.state() != QPropertyAnimation.State.Running:
            current_height = self.minimumHeight()
            self._hover_animation.setStartValue(current_height)
            self._hover_animation.setEndValue(24)  # Back to normal
            self._hover_animation.start()


class FluentRadioGroup(QWidget):
    """Optimized Radio Button Group with consistent theming"""

    selection_changed = Signal(int, str)  # index, text

    def __init__(self, options: List[str], parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._button_group = QButtonGroup(self)
        self._radio_buttons: List[FluentRadioButton] = []
        self._selected_index = -1

        self._setup_radio_buttons(options)
        self._button_group.buttonToggled.connect(self._on_button_toggled)

    def _setup_radio_buttons(self, options: List[str]):
        """Setup radio buttons with consistent styling"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        for i, option in enumerate(options):
            radio_button = FluentRadioButton(option, self)
            self._radio_buttons.append(radio_button)
            self._button_group.addButton(radio_button, i)
            layout.addWidget(radio_button)

    def _on_button_toggled(self, button, checked: bool):
        """Handle button toggle with optimized logic"""
        if checked:
            self._selected_index = self._button_group.id(button)
            text = button.text()
            self.selection_changed.emit(self._selected_index, text)

    def set_selected(self, index: int):
        """Set selected radio button"""
        if 0 <= index < len(self._radio_buttons):
            self._radio_buttons[index].setChecked(True)

    def get_selected_index(self) -> int:
        """Get selected radio button index"""
        return self._selected_index

    def get_selected_text(self) -> str:
        """Get selected radio button text"""
        if 0 <= self._selected_index < len(self._radio_buttons):
            return self._radio_buttons[self._selected_index].text()
        return ""
