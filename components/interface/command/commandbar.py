"""
Fluent Design Command Bar Component
Contextual action bar with primary and secondary commands
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, 
                               QFrame, QMenu, QSizePolicy, QToolButton, 
                               QButtonGroup)
from PySide6.QtCore import Signal, Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor, QAction
from core.theme import theme_manager
from core.enhanced_base import FluentBaseWidget
from core.enhanced_animations import FluentMicroInteraction
from typing import Optional, List, Dict, Any, Callable
from enum import Enum


class CommandBarPlacement(Enum):
    """Command bar placement options"""
    TOP = "top"
    BOTTOM = "bottom"
    FLOATING = "floating"


class FluentCommandBarAction:
    """Represents a command bar action"""
    
    def __init__(self, text: str, icon: Optional[QIcon] = None, action_id: str = "",
                 callback: Optional[Callable] = None, tooltip: str = ""):
        self.text = text
        self.icon = icon
        self.action_id = action_id or text.lower().replace(" ", "_")
        self.callback = callback
        self.tooltip = tooltip or text
        self.is_enabled = True
        self.is_visible = True
        self.is_primary = True  # Primary actions are always visible


class FluentCommandBar(FluentBaseWidget):
    """
    Fluent Design Command Bar Component
    
    Contextual action toolbar with:
    - Primary commands (always visible)
    - Secondary commands (in overflow menu)
    - Adaptive layout based on available space
    - Consistent Fluent styling
    - Keyboard shortcuts support
    """
    
    # Signals
    action_triggered = Signal(str)  # Emitted when action is triggered (action_id)
    overflow_toggled = Signal(bool)  # Emitted when overflow menu is toggled
    
    def __init__(self, parent: Optional[QWidget] = None,
                 placement: CommandBarPlacement = CommandBarPlacement.TOP):
        super().__init__(parent)
        
        # Properties
        self._placement = placement
        self._max_primary_commands = 6  # Max commands before overflow
        self._is_compact = False
        self._show_labels = True
        
        # Actions
        self._actions: List[FluentCommandBarAction] = []
        self._primary_actions: List[FluentCommandBarAction] = []
        self._secondary_actions: List[FluentCommandBarAction] = []
        
        # State
        self._is_overflow_open = False
        
        # UI Elements
        self._main_layout: Optional[QHBoxLayout] = None  # type: ignore
        self._primary_container: Optional[QFrame] = None  # type: ignore
        self._primary_layout: Optional[QHBoxLayout] = None  # type: ignore
        self._overflow_button: Optional[QToolButton] = None  # type: ignore
        self._overflow_menu: Optional[QMenu] = None  # type: ignore
        
        # Button tracking
        self._action_buttons: Dict[str, QPushButton] = {}
        
        # Setup
        self._setup_ui()
        self._setup_style()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup the UI layout"""
        # Main horizontal layout
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(8, 4, 8, 4)
        self._main_layout.setSpacing(4)
        
        # Primary commands container
        self._primary_container = QFrame()
        self._primary_container.setFrameStyle(QFrame.Shape.NoFrame)
        
        self._primary_layout = QHBoxLayout(self._primary_container)
        self._primary_layout.setContentsMargins(0, 0, 0, 0)
        self._primary_layout.setSpacing(4)
        
        self._main_layout.addWidget(self._primary_container)
        
        # Spacer to push overflow button to right
        self._main_layout.addStretch()
        
        # Overflow button (initially hidden)
        self._overflow_button = QToolButton()
        self._overflow_button.setText("⋯")
        self._overflow_button.setToolTip("More commands")
        self._overflow_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._overflow_button.hide()
        
        # Setup overflow menu
        self._overflow_menu = QMenu()
        self._overflow_button.setMenu(self._overflow_menu)
        
        self._main_layout.addWidget(self._overflow_button)
        
    def _setup_style(self):
        """Apply Fluent Design styling"""
        if not self._primary_container or not self._overflow_button:
            return
            
        theme = theme_manager
        
        # Main command bar style
        bar_style = f"""
            QWidget {{
                background-color: {theme.get_color('surface').name()};
                border: none;
            }}
        """
        
        # Primary container style
        container_style = f"""
            QFrame {{
                background: transparent;
                border: none;
            }}
        """
        
        # Overflow button style
        overflow_style = f"""
            QToolButton {{
                background: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 16px;
                color: {theme.get_color('text_primary').name()};
                min-width: 32px;
                min-height: 32px;
            }}
            QToolButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('border').name()};
            }}
            QToolButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
        """
        
        # Overflow menu style
        menu_style = f"""
            QMenu {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 16px;
                border-radius: 4px;
                color: {theme.get_color('text_primary').name()};
            }}
            QMenu::item:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QMenu::item:selected {{
                background-color: {theme.get_color('primary').name()};
                color: {theme.get_color('text_on_primary').name()};
            }}
        """
        
        self.setStyleSheet(bar_style)
        self._primary_container.setStyleSheet(container_style)
        self._overflow_button.setStyleSheet(overflow_style)
        if self._overflow_menu:
            self._overflow_menu.setStyleSheet(menu_style)
        
    def _connect_signals(self):
        """Connect signals and slots"""
        if self._overflow_menu:
            self._overflow_menu.aboutToShow.connect(lambda: self.overflow_toggled.emit(True))
            self._overflow_menu.aboutToHide.connect(lambda: self.overflow_toggled.emit(False))
            
        # Theme changes
        theme_manager.theme_changed.connect(self._setup_style)
        
    def _create_command_button(self, action: FluentCommandBarAction) -> QPushButton:
        """Create a styled command button"""
        button = QPushButton()
        
        # Set icon and text
        if action.icon:
            button.setIcon(action.icon)
            button.setIconSize(QSize(16, 16))
            
        if self._show_labels and not self._is_compact:
            button.setText(action.text)
        else:
            button.setToolTip(action.tooltip)
            
        # Set button properties
        button.setEnabled(action.is_enabled)
        button.setVisible(action.is_visible)
        button.setProperty("action_id", action.action_id)
        
        # Apply styling
        self._style_command_button(button)
        
        # Connect callback
        if action.callback:
            button.clicked.connect(action.callback)
        button.clicked.connect(lambda: self.action_triggered.emit(action.action_id))
        
        return button
        
    def _style_command_button(self, button: QPushButton):
        """Apply Fluent styling to command button"""
        theme = theme_manager
        
        if self._is_compact:
            # Compact mode - icon only
            style = f"""
                QPushButton {{
                    background: transparent;
                    border: 1px solid transparent;
                    border-radius: 4px;
                    padding: 6px;
                    color: {theme.get_color('text_primary').name()};
                    min-width: 32px;
                    min-height: 32px;
                }}
                QPushButton:hover {{
                    background-color: {theme.get_color('accent_light').name()};
                    border-color: {theme.get_color('border').name()};
                }}
                QPushButton:pressed {{
                    background-color: {theme.get_color('accent_medium').name()};
                }}
                QPushButton:disabled {{
                    color: {theme.get_color('text_disabled').name()};
                    background: transparent;
                }}
            """
        else:
            # Standard mode - icon and text
            style = f"""
                QPushButton {{
                    background: transparent;
                    border: 1px solid transparent;
                    border-radius: 4px;
                    padding: 6px 12px;
                    color: {theme.get_color('text_primary').name()};
                    font-size: 12px;
                    font-weight: 500;
                    text-align: left;
                    min-height: 32px;
                }}
                QPushButton:hover {{
                    background-color: {theme.get_color('accent_light').name()};
                    border-color: {theme.get_color('border').name()};
                }}
                QPushButton:pressed {{
                    background-color: {theme.get_color('accent_medium').name()};
                }}
                QPushButton:disabled {{
                    color: {theme.get_color('text_disabled').name()};
                    background: transparent;
                }}
            """
            
        button.setStyleSheet(style)
        
    def _rebuild_layout(self):
        """Rebuild the command bar layout"""
        if not self._primary_layout or not self._overflow_menu:
            return
            
        # Clear existing buttons
        for button in self._action_buttons.values():
            button.deleteLater()
        self._action_buttons.clear()
        
        # Clear layouts
        while self._primary_layout.count():
            child = self._primary_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Clear overflow menu
        self._overflow_menu.clear()
        
        # Determine which actions go where
        self._organize_actions()
        
        # Add primary action buttons
        for action in self._primary_actions:
            if action.is_visible:
                button = self._create_command_button(action)
                self._action_buttons[action.action_id] = button
                self._primary_layout.addWidget(button)
                
        # Add secondary actions to overflow menu
        for action in self._secondary_actions:
            if action.is_visible:
                menu_action = QAction(action.text, self._overflow_menu)
                if action.icon:
                    menu_action.setIcon(action.icon)
                menu_action.setEnabled(action.is_enabled)
                menu_action.setProperty("action_id", action.action_id)
                
                # Connect action
                if action.callback:
                    menu_action.triggered.connect(action.callback)
                menu_action.triggered.connect(
                    lambda checked, aid=action.action_id: self.action_triggered.emit(aid)
                )
                
                self._overflow_menu.addAction(menu_action)
                
        # Show/hide overflow button
        if self._overflow_button:
            self._overflow_button.setVisible(len(self._secondary_actions) > 0)
        
    def _organize_actions(self):
        """Organize actions into primary and secondary based on priority and space"""
        self._primary_actions.clear()
        self._secondary_actions.clear()
        
        # Separate actions by priority
        primary_candidates = [a for a in self._actions if a.is_primary and a.is_visible]
        secondary_candidates = [a for a in self._actions if not a.is_primary and a.is_visible]
        
        # Add primary actions up to the limit
        available_slots = self._max_primary_commands
        
        for action in primary_candidates[:available_slots]:
            self._primary_actions.append(action)
            
        # Remaining primary actions go to secondary
        for action in primary_candidates[available_slots:]:
            self._secondary_actions.append(action)
            
        # Add secondary actions
        self._secondary_actions.extend(secondary_candidates)
        
    # Public API
    
    def add_action(self, text: str, icon: Optional[QIcon] = None, action_id: str = "",
                  callback: Optional[Callable] = None, tooltip: str = "", is_primary: bool = True) -> FluentCommandBarAction:
        """Add a new action to the command bar"""
        action = FluentCommandBarAction(text, icon, action_id, callback, tooltip)
        action.is_primary = is_primary
        
        self._actions.append(action)
        self._rebuild_layout()
        
        return action
        
    def remove_action(self, action_id: str):
        """Remove an action by ID"""
        self._actions = [a for a in self._actions if a.action_id != action_id]
        self._rebuild_layout()
        
    def get_action(self, action_id: str) -> Optional[FluentCommandBarAction]:
        """Get an action by ID"""
        for action in self._actions:
            if action.action_id == action_id:
                return action
        return None
        
    def set_action_enabled(self, action_id: str, enabled: bool):
        """Enable or disable an action"""
        action = self.get_action(action_id)
        if action:
            action.is_enabled = enabled
            
            # Update button if it exists
            if action_id in self._action_buttons:
                self._action_buttons[action_id].setEnabled(enabled)
                
            # Update menu action if in overflow
            if self._overflow_menu:
                for menu_action in self._overflow_menu.actions():
                    if menu_action.property("action_id") == action_id:
                        menu_action.setEnabled(enabled)
                        break
                    
    def set_action_visible(self, action_id: str, visible: bool):
        """Show or hide an action"""
        action = self.get_action(action_id)
        if action:
            action.is_visible = visible
            self._rebuild_layout()
            
    def set_compact_mode(self, compact: bool):
        """Enable or disable compact mode (icons only)"""
        if self._is_compact != compact:
            self._is_compact = compact
            self._rebuild_layout()
            
    def set_show_labels(self, show: bool):
        """Show or hide text labels"""
        if self._show_labels != show:
            self._show_labels = show
            self._rebuild_layout()
            
    def set_max_primary_commands(self, max_count: int):
        """Set maximum number of primary commands before overflow"""
        self._max_primary_commands = max(1, max_count)
        self._rebuild_layout()
        
    def clear_actions(self):
        """Remove all actions"""
        self._actions.clear()
        self._rebuild_layout()
        
    def add_separator(self):
        """Add a separator to the primary commands"""
        if self._primary_layout:
            separator = QFrame()
            separator.setFrameStyle(QFrame.Shape.VLine)
            separator.setStyleSheet(f"""
                QFrame {{ 
                    color: {theme_manager.get_color('border').name()};
                    margin: 4px 2px;
                }}
            """)
            self._primary_layout.addWidget(separator)


class FluentCommandBarBuilder:
    """Builder for creating FluentCommandBar with fluent API"""
    
    def __init__(self):
        self._placement = CommandBarPlacement.TOP
        self._actions = []
        self._max_primary = 6
        self._compact = False
        self._show_labels = True
        
    def with_placement(self, placement: CommandBarPlacement):
        """Set the command bar placement"""
        self._placement = placement
        return self
        
    def add_action(self, text: str, icon: Optional[QIcon] = None, action_id: str = "",
                  callback: Optional[Callable] = None, tooltip: str = "", is_primary: bool = True):
        """Add an action to the command bar"""
        self._actions.append({
            'text': text,
            'icon': icon,
            'action_id': action_id,
            'callback': callback,
            'tooltip': tooltip,
            'is_primary': is_primary
        })
        return self
        
    def with_compact_mode(self, compact: bool = True):
        """Enable compact mode"""
        self._compact = compact
        return self
        
    def with_labels(self, show_labels: bool = True):
        """Show or hide labels"""
        self._show_labels = show_labels
        return self
        
    def with_max_primary_commands(self, max_count: int):
        """Set maximum primary commands"""
        self._max_primary = max_count
        return self
        
    def build(self, parent: Optional[QWidget] = None) -> FluentCommandBar:
        """Build the command bar"""
        command_bar = FluentCommandBar(parent, self._placement)
        command_bar.set_compact_mode(self._compact)
        command_bar.set_show_labels(self._show_labels)
        command_bar.set_max_primary_commands(self._max_primary)
        
        # Add actions
        for action_def in self._actions:
            command_bar.add_action(**action_def)
            
        return command_bar


# Export classes
__all__ = [
    'FluentCommandBar',
    'FluentCommandBarAction',
    'FluentCommandBarBuilder',
    'CommandBarPlacement'
]
