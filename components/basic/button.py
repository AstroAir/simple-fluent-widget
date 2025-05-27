"""
Fluent Design Style Button Component
Supports multiple button styles and animation effects
"""

from PySide6.QtWidgets import QPushButton, QWidget
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
from core.theme import theme_manager
from core.animation import AnimationHelper
from typing import Optional


class FluentButton(QPushButton):
    """Fluent Design Style Button

    Features:
    - Supports multiple button styles (Primary, Secondary, Accent)
    - Built-in hover and click animation effects
    - Adaptive theme colors
    - Supports icons and text
    """

    class ButtonStyle:
        PRIMARY = "primary"
        SECONDARY = "secondary"
        ACCENT = "accent"
        SUBTLE = "subtle"
        OUTLINE = "outline"

    def __init__(self, text: str = "", parent: Optional[QWidget] = None,
                 style: str = ButtonStyle.PRIMARY):
        super().__init__(text, parent)

        self._button_style = style
        self._is_hovered = False
        self._is_pressed = False
        self._animation_helper = AnimationHelper(self)

        # Set basic properties
        self.setMinimumSize(120, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Apply style and theme
        self._apply_style()
        self._setup_animations()

        # Connect theme change signal
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def set_style(self, style: str):
        """Set button style"""
        self._button_style = style
        self._apply_style()

    def _apply_style(self):
        """Apply button style"""
        theme = theme_manager
        style_sheet = ""  # Initialize to prevent unbound variable

        if self._button_style == self.ButtonStyle.PRIMARY:
            style_sheet = f"""
                FluentButton {{
                    background-color: {theme.get_color('primary').name()};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                    font-weight: 400;
                    outline: none;
                }}
                FluentButton:hover {{
                    background-color: {theme.get_color('primary').darker(110).name()};
                }}
                FluentButton:pressed {{
                    background-color: {theme.get_color('primary').darker(120).name()};
                }}
                FluentButton:disabled {{
                    background-color: {theme.get_color('border').name()};
                    color: {theme.get_color('text_disabled').name()};
                }}
            """
        elif self._button_style == self.ButtonStyle.SECONDARY:
            style_sheet = f"""
                FluentButton {{
                    background-color: {theme.get_color('surface').name()};
                    color: {theme.get_color('text_primary').name()};
                    border: 1px solid {theme.get_color('border').name()};
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                    font-weight: 400;
                }}
                FluentButton:hover {{
                    background-color: {theme.get_color('accent_light').name()};
                    border-color: {theme.get_color('primary').name()};
                }}
                FluentButton:pressed {{
                    background-color: {theme.get_color('accent_medium').name()};
                }}
            """
        elif self._button_style == self.ButtonStyle.ACCENT:
            style_sheet = f"""
                FluentButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {theme.get_color('primary').lighter(110).name()},
                        stop:1 {theme.get_color('primary').name()});
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                FluentButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {theme.get_color('primary').lighter(120).name()},
                        stop:1 {theme.get_color('primary').lighter(110).name()});
                }}
            """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Set up animation effects"""
        # Add hover effect
        self._animation_helper.add_hover_effect()

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._apply_style()

    def enterEvent(self, event):
        """Hover enter event"""
        self._is_hovered = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave event"""
        self._is_hovered = False
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Mouse press event"""
        self._is_pressed = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Mouse release event"""
        self._is_pressed = False
        super().mouseReleaseEvent(event)


class FluentIconButton(FluentButton):
    """Fluent Button with Icon"""

    def __init__(self, icon: QIcon, text: str = "",
                 parent: Optional[QWidget] = None,
                 style: str = FluentButton.ButtonStyle.PRIMARY):
        super().__init__(text, parent, style)
        self.setIcon(icon)
        height = self.fontMetrics().height()
        self.setIconSize(QSize(height, height))


class FluentToggleButton(FluentButton):
    """Toggle Button"""

    toggled = Signal(bool)

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent, FluentButton.ButtonStyle.SECONDARY)
        self.setCheckable(True)
        self._is_toggled = False

        # Connect click signal
        self.clicked.connect(self._on_clicked)

    def _on_clicked(self):
        """Handle click"""
        self._is_toggled = self.isChecked()
        self._update_toggle_style()
        self.toggled.emit(self._is_toggled)

    def _update_toggle_style(self):
        """Update toggle style"""
        if self._is_toggled:
            self.set_style(FluentButton.ButtonStyle.PRIMARY)
        else:
            self.set_style(FluentButton.ButtonStyle.SECONDARY)

    def set_toggled(self, toggled: bool):
        """Set toggle state"""
        self._is_toggled = toggled
        self.setChecked(toggled)
        self._update_toggle_style()
