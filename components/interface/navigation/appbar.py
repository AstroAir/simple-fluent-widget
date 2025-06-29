"""
Fluent Design App Bar Component
A top-level application bar with actions, navigation, and branding
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSizePolicy, QToolButton, QLineEdit)
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon, QFont
from core.theme import theme_manager
from core.enhanced_base import FluentBaseWidget
from typing import Optional, List


class FluentAppBarAction:
    """Represents an action in the app bar"""

    def __init__(self, text: str = "", icon: Optional[QIcon] = None,
                 tooltip: str = "", callback=None, shortcut: str = ""):
        self.text = text
        self.icon = icon
        self.tooltip = tooltip
        self.callback = callback
        self.shortcut = shortcut
        self.enabled = True
        self.visible = True


class FluentAppBar(FluentBaseWidget):
    """
    Fluent Design App Bar Component

    Provides application-level navigation, actions, and branding in a
    top-level bar following Fluent Design principles.

    Features:
    - Brand/title area
    - Navigation actions
    - Primary and secondary actions
    - Search integration
    - User profile area
    - Responsive behavior
    - Theme consistency
    """

    # Signals
    navigation_requested = Signal(str)  # Navigation action
    action_triggered = Signal(str)      # Action triggered
    search_requested = Signal(str)      # Search query

    # Constants
    HEIGHT_COMPACT = 48
    HEIGHT_STANDARD = 56
    HEIGHT_TALL = 64

    def __init__(self, parent: Optional[QWidget] = None, title: str = ""):
        super().__init__(parent)

        # Properties
        self._title = title
        self._height_mode = "standard"
        self._is_compact = False
        self._show_back_button = False
        self._show_search = False
        self._show_user_area = False

        # Collections
        self._navigation_actions: List[FluentAppBarAction] = []
        self._primary_actions: List[FluentAppBarAction] = []
        self._secondary_actions: List[FluentAppBarAction] = []

        # UI elements (initialized in _setup_ui)
        self._main_layout: QHBoxLayout
        self._title_label: QLabel
        self._back_button: QToolButton
        self._search_box: Optional[QLineEdit] = None
        self._primary_actions_layout: QHBoxLayout
        self._secondary_actions_layout: QHBoxLayout
        self._user_button: Optional[QToolButton] = None
        self._navigation_actions_layout: QHBoxLayout
        self._right_layout: QHBoxLayout  # Store reference to right layout

        # Setup
        self._setup_ui()
        self._setup_style()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the UI layout and components"""
        # Set fixed height based on mode
        self.setFixedHeight(self._get_current_height())
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)

        # Main horizontal layout
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(16, 0, 16, 0)
        self._main_layout.setSpacing(16)

        # Left section - Navigation and title
        self._setup_left_section()

        # Center section - Search (if enabled)
        self._setup_center_section()

        # Right section - Actions and user
        self._setup_right_section()

    def _setup_left_section(self):
        """Setup the left section with navigation and title"""
        left_layout = QHBoxLayout()
        left_layout.setSpacing(12)

        # Back button (hidden by default)
        self._back_button = QToolButton()
        self._back_button.setText("←")  # Use Unicode arrow instead of icon
        self._back_button.setToolTip("Go back")
        self._back_button.setFixedSize(32, 32)
        self._back_button.setVisible(self._show_back_button)
        self._back_button.clicked.connect(
            lambda: self.navigation_requested.emit("back"))
        left_layout.addWidget(self._back_button)

        # Title label
        self._title_label = QLabel(self._title)
        self._title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.DemiBold))
        left_layout.addWidget(self._title_label)

        # Navigation actions
        self._navigation_actions_layout = QHBoxLayout()
        self._navigation_actions_layout.setSpacing(4)
        left_layout.addLayout(self._navigation_actions_layout)

        left_layout.addStretch()
        self._main_layout.addLayout(left_layout)

    def _setup_center_section(self):
        """Setup the center section with search"""
        if self._show_search:
            self._setup_search_box()
        else:
            # Add a stretch to push right content to the right
            self._main_layout.addStretch(2)

    def _setup_search_box(self):
        """Setup the search box in center section"""
        # Create search container
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        # Search input field
        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText("Search...")
        self._search_box.setFixedWidth(300)
        self._search_box.setMaximumHeight(32)

        # Connect search signals
        self._search_box.returnPressed.connect(self._on_search_submitted)
        self._search_box.textChanged.connect(self._on_search_text_changed)

        search_layout.addWidget(self._search_box)

        # Add search container to main layout
        self._main_layout.addWidget(search_container)
        self._main_layout.addStretch(1)

    def _setup_right_section(self):
        """Setup the right section with actions and user area"""
        self._right_layout = QHBoxLayout()
        self._right_layout.setSpacing(8)

        # Primary actions
        self._primary_actions_layout = QHBoxLayout()
        self._primary_actions_layout.setSpacing(4)
        self._right_layout.addLayout(self._primary_actions_layout)

        # Secondary actions (overflow menu)
        self._secondary_actions_layout = QHBoxLayout()
        self._secondary_actions_layout.setSpacing(4)
        self._right_layout.addLayout(self._secondary_actions_layout)

        # User area (if enabled)
        if self._show_user_area:
            self._setup_user_area(self._right_layout)

        self._main_layout.addLayout(self._right_layout)

    def _setup_user_area(self, parent_layout: QHBoxLayout):
        """Setup the user profile area"""
        self._user_button = QToolButton()
        self._user_button.setText("👤")  # Use Unicode character instead of icon
        self._user_button.setToolTip("User profile")
        self._user_button.setFixedSize(32, 32)
        parent_layout.addWidget(self._user_button)

    def _setup_style(self):
        """Apply Fluent Design styling"""
        theme = theme_manager

        style = f"""
            FluentAppBar {{
                background-color: {theme.get_color('surface').name()};
                border: none;
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                background: transparent;
            }}
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
                color: {theme.get_color('text_primary').name()};
                font-size: 16px;
            }}
            QToolButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QToolButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QLineEdit {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 16px;
                padding: 6px 12px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()}40;
            }}
            QLineEdit:hover {{
                border-color: {theme.get_color('primary').lighter(150).name()};
            }}
            QLineEdit:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
                padding: 5px 11px;
            }}
            QLineEdit::placeholder {{
                color: {theme.get_color('text_secondary').name()};
            }}
        """

        self.setStyleSheet(style)

    def _connect_signals(self):
        """Connect theme and other signals"""
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self):
        """Handle theme changes"""
        self._setup_style()

    def _on_search_submitted(self):
        """Handle search submission (Enter pressed)"""
        if self._search_box:
            query = self._search_box.text().strip()
            if query:
                self.search_requested.emit(query)

    def _on_search_text_changed(self, text: str):
        """Handle search text changes for live search"""
        # Emit search signal for live search functionality
        # Users can connect to this signal for real-time search
        if len(text) >= 2:  # Only search if at least 2 characters
            self.search_requested.emit(text)

    def _get_current_height(self) -> int:
        """Get the current height based on mode"""
        height_map = {
            "compact": self.HEIGHT_COMPACT,
            "standard": self.HEIGHT_STANDARD,
            "tall": self.HEIGHT_TALL
        }
        return height_map.get(self._height_mode, self.HEIGHT_STANDARD)

    # Public API methods

    def set_title(self, title: str):
        """Set the app bar title"""
        self._title = title
        if self._title_label:
            self._title_label.setText(title)

    def get_title(self) -> str:
        """Get the current title"""
        return self._title

    def set_height_mode(self, mode: str):
        """Set the height mode: compact, standard, or tall"""
        if mode in ["compact", "standard", "tall"]:
            self._height_mode = mode
            self.setFixedHeight(self._get_current_height())

    def show_back_button(self, show: bool = True):
        """Show or hide the back button"""
        self._show_back_button = show
        if self._back_button:
            self._back_button.setVisible(show)

    def add_navigation_action(self, action: FluentAppBarAction):
        """Add a navigation action to the left section"""
        self._navigation_actions.append(action)
        self._create_action_button(action, self._navigation_actions_layout)

    def add_primary_action(self, action: FluentAppBarAction):
        """Add a primary action to the right section"""
        self._primary_actions.append(action)
        self._create_action_button(action, self._primary_actions_layout)

    def add_secondary_action(self, action: FluentAppBarAction):
        """Add a secondary action (may be in overflow menu)"""
        self._secondary_actions.append(action)
        self._create_action_button(action, self._secondary_actions_layout)

    def _create_action_button(self, action: FluentAppBarAction, layout: QHBoxLayout):
        """Create a button for an action and add it to the layout"""
        button = QToolButton()

        if action.icon:
            button.setIcon(action.icon)
        if action.text and not action.icon:
            button.setText(action.text)
        if action.tooltip:
            button.setToolTip(action.tooltip)

        button.setFixedSize(32, 32)

        # Connect callback
        if action.callback:
            button.clicked.connect(action.callback)

        # Simple show without animation to avoid dependency issues
        button.show()

        layout.addWidget(button)
        return button

    def set_compact_mode(self, compact: bool):
        """Toggle compact mode"""
        self._is_compact = compact
        if compact:
            self.set_height_mode("compact")
        else:
            self.set_height_mode("standard")

    def enable_search(self, enable: bool = True):
        """Enable or disable search functionality"""
        was_showing_search = self._show_search
        self._show_search = enable

        # If search state changed, rebuild the center section
        if was_showing_search != enable:
            self._rebuild_center_section()

    def _rebuild_center_section(self):
        """Rebuild the center section when search state changes"""
        # Remove existing center section widgets
        for i in reversed(range(1, self._main_layout.count() - 1)):
            item = self._main_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
            elif item and item.spacerItem():
                self._main_layout.removeItem(item)

        # Rebuild center section
        self._setup_center_section()

    def enable_user_area(self, enable: bool = True):
        """Enable or disable user profile area"""
        self._show_user_area = enable
        if enable and not self._user_button:
            # Use the stored reference to right layout
            self._setup_user_area(self._right_layout)

    def get_search_text(self) -> str:
        """Get current search text"""
        if self._search_box:
            return self._search_box.text()
        return ""

    def set_search_text(self, text: str):
        """Set search text programmatically"""
        if self._search_box:
            self._search_box.setText(text)

    def clear_search(self):
        """Clear the search box"""
        if self._search_box:
            self._search_box.clear()

    def set_search_placeholder(self, placeholder: str):
        """Set search box placeholder text"""
        if self._search_box:
            self._search_box.setPlaceholderText(placeholder)


class FluentAppBarBuilder:
    """Builder class for creating app bars with fluent API"""

    def __init__(self):
        self._app_bar = FluentAppBar()

    def with_title(self, title: str):
        self._app_bar.set_title(title)
        return self

    def with_back_button(self):
        self._app_bar.show_back_button(True)
        return self

    def with_height_mode(self, mode: str):
        self._app_bar.set_height_mode(mode)
        return self

    def with_search(self, placeholder: str = "Search..."):
        self._app_bar.enable_search(True)
        if placeholder != "Search...":
            self._app_bar.set_search_placeholder(placeholder)
        return self

    def with_user_area(self):
        self._app_bar.enable_user_area(True)
        return self

    def add_action(self, text: str = "", icon: Optional[QIcon] = None,
                   callback=None, section: str = "primary"):
        action = FluentAppBarAction(text=text, icon=icon, callback=callback)
        if section == "navigation":
            self._app_bar.add_navigation_action(action)
        elif section == "primary":
            self._app_bar.add_primary_action(action)
        else:
            self._app_bar.add_secondary_action(action)
        return self

    def build(self) -> FluentAppBar:
        return self._app_bar


# Export classes
__all__ = [
    'FluentAppBar',
    'FluentAppBarAction',
    'FluentAppBarBuilder'
]
