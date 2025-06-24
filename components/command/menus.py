"""
Fluent Design Menu and Command Components
Optimized for Python 3.11+ with modern features and enhanced PySide6 integration
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable, Protocol, Union
from weakref import WeakValueDictionary
from enum import Enum, auto
import time

from PySide6.QtCore import (QByteArray, Qt, Signal, QPropertyAnimation, QEasingCurve,
                            QRect, QTimer, QPoint)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QMenu,
    QGraphicsDropShadowEffect, QButtonGroup, QGraphicsOpacityEffect
)
from PySide6.QtGui import (
    QFont, QIcon, QColor, QKeySequence, QCursor, QAction, QPixmap
)

from core.theme import theme_manager
from core.enhanced_base import FluentLayoutBuilder
from core.enhanced_animations import FluentMicroInteraction, FluentTransition

# Try to import enhanced components, fallback to basic ones
try:
    from components.basic.button import FluentButton
    from components.basic.textbox import FluentLineEdit
except ImportError:
    from PySide6.QtWidgets import QPushButton as FluentButton
    from PySide6.QtWidgets import QLineEdit as FluentLineEdit


class MenuItemType(Enum):
    """Enhanced menu item types with auto values"""
    ACTION = auto()
    SEPARATOR = auto()
    SUBMENU = auto()
    HEADER = auto()
    CUSTOM = auto()
    TOGGLE = auto()
    RADIO = auto()


class MenuItemState(Enum):
    """Menu item states"""
    ENABLED = auto()
    DISABLED = auto()
    HIDDEN = auto()
    LOADING = auto()


@dataclass(slots=True, frozen=True)
class FluentMenuItem:
    """Immutable menu item data structure with slots for memory efficiency"""
    text: str = ""
    icon: Optional[QIcon] = None
    item_type: MenuItemType = MenuItemType.ACTION
    action: Optional[Callable[..., Any]] = None
    shortcut: str = ""
    checked: bool = False
    state: MenuItemState = MenuItemState.ENABLED
    data: Any = None
    children: List['FluentMenuItem'] = field(
        default_factory=list)  # For submenus
    tooltip: str = ""
    role: str = ""  # For accessibility


class MenuProtocol(Protocol):
    """Protocol for menu implementations"""

    def add_menu_item(self, item: FluentMenuItem) -> QAction: ...
    def remove_menu_item(self, text: str) -> bool: ...
    def clear_menu(self) -> None: ...


@dataclass(slots=True)
class MenuState:
    """Mutable state container for menu"""
    items: Dict[str, FluentMenuItem] = field(default_factory=dict)
    animation_enabled: bool = True
    last_update_time: float = field(default_factory=time.time)


class FluentMenu(QMenu):
    """Enhanced Fluent Design menu with modern Python features and animations"""

    # Enhanced signals
    item_triggered = Signal(str, object)  # item_text, item_data
    menu_opened = Signal()
    menu_closed = Signal()

    def __init__(self, parent: Optional[QWidget] = None, title: str = "",
                 enable_animations: bool = True):
        super().__init__(title, parent)

        # Modern state management
        self._state = MenuState(animation_enabled=enable_animations)

        # Performance optimization
        self._style_cache: Dict[str, str] = {}
        self._action_cache: WeakValueDictionary[str,
                                                QAction] = WeakValueDictionary()

        # Animation system
        self._animations: Dict[str, QPropertyAnimation] = {}
        self._shadow_effect: Optional[QGraphicsDropShadowEffect] = None

        self._setup_style()
        self._setup_animations()
        self._setup_accessibility()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup enhanced menu styling with caching"""
        self._apply_theme()

        # Add enhanced shadow effect
        if self._state.animation_enabled:
            self._shadow_effect = QGraphicsDropShadowEffect()
            self._shadow_effect.setBlurRadius(20)
            self._shadow_effect.setColor(QColor(0, 0, 0, 60))
            self._shadow_effect.setOffset(0, 5)
            self.setGraphicsEffect(self._shadow_effect)

    def _setup_animations(self):
        """Setup enhanced menu animations"""
        if not self._state.animation_enabled:
            return

        # Fade in/out animation
        self._animations['fade'] = QPropertyAnimation(
            self, QByteArray(b"windowOpacity"))
        self._animations['fade'].setDuration(150)
        self._animations['fade'].setEasingCurve(QEasingCurve.Type.OutCubic)

        # Scale animation for modern feel
        self._animations['scale'] = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self._animations['scale'].setDuration(200)
        self._animations['scale'].setEasingCurve(QEasingCurve.Type.OutBack)

    def _setup_accessibility(self):
        """Setup accessibility features"""
        self.setAccessibleName("Menu")
        self.setAccessibleDescription("Context menu with actions")

        # Enable keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def showEvent(self, event):
        """Enhanced show event with modern animations"""
        super().showEvent(event)
        self.menu_opened.emit()

        if self._state.animation_enabled and 'fade' in self._animations:
            # Fade in animation
            self.setWindowOpacity(0.0)
            fade_animation = self._animations['fade']
            fade_animation.setStartValue(0.0)
            fade_animation.setEndValue(1.0)
            fade_animation.start()

    def hideEvent(self, event):
        """Enhanced hide event"""
        super().hideEvent(event)
        self.menu_closed.emit()

    def add_menu_item(self, item: FluentMenuItem) -> QAction:
        """Add menu item with enhanced type safety and error handling"""
        try:
            # Store item in state
            self._state.items[item.text] = item

            # Handle different item types using match statement
            match item.item_type:
                case MenuItemType.SEPARATOR:
                    return self.addSeparator()

                case MenuItemType.HEADER:
                    action = self._create_header_action(item)
                    self.addAction(action)
                    return action

                case MenuItemType.SUBMENU:
                    submenu = self._create_submenu(item)
                    self.addMenu(submenu)
                    return submenu.menuAction()

                case MenuItemType.TOGGLE:
                    action = self._create_toggle_action(item)
                    self.addAction(action)
                    return action

                case MenuItemType.RADIO:
                    action = self._create_radio_action(item)
                    self.addAction(action)
                    return action

                case _:  # ACTION, CUSTOM, or default
                    action = self._create_standard_action(item)
                    self.addAction(action)
                    return action

        except Exception as e:
            print(f"Error adding menu item '{item.text}': {e}")
            # Return a dummy action to prevent crashes
            return QAction("Error", self)

    def _create_header_action(self, item: FluentMenuItem) -> QAction:
        """Create header action with enhanced styling"""
        action = QAction(item.text, self)
        action.setEnabled(False)
        action.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))

        if item.tooltip:
            action.setToolTip(item.tooltip)

        return action

    def _create_submenu(self, item: FluentMenuItem) -> 'FluentMenu':
        """Create submenu with enhanced features"""
        submenu = FluentMenu(self, item.text, self._state.animation_enabled)

        if item.icon:
            submenu.setIcon(item.icon)

        if item.tooltip:
            submenu.setToolTip(item.tooltip)

        # Add children to submenu
        for child in item.children:
            submenu.add_menu_item(child)

        return submenu

    def _create_toggle_action(self, item: FluentMenuItem) -> QAction:
        """Create toggle action with enhanced features"""
        action = QAction(item.text, self)
        action.setCheckable(True)
        action.setChecked(item.checked)

        self._configure_action(action, item)
        return action

    def _create_radio_action(self, item: FluentMenuItem) -> QAction:
        """Create radio action with enhanced features"""
        action = QAction(item.text, self)
        action.setCheckable(True)
        action.setChecked(item.checked)
        # Radio actions would need to be in an action group for exclusivity

        self._configure_action(action, item)
        return action

    def _create_standard_action(self, item: FluentMenuItem) -> QAction:
        """Create standard action with enhanced features"""
        action = QAction(item.text, self)
        self._configure_action(action, item)
        return action

    def _configure_action(self, action: QAction, item: FluentMenuItem):
        """Configure action with common properties"""
        if item.icon:
            action.setIcon(item.icon)

        if item.shortcut:
            action.setShortcut(QKeySequence(item.shortcut))

        if item.tooltip:
            enhanced_tooltip = item.tooltip
            if item.shortcut:
                enhanced_tooltip += f" ({item.shortcut})"
            action.setToolTip(enhanced_tooltip)

        # Set state
        match item.state:
            case MenuItemState.ENABLED:
                action.setEnabled(True)
                action.setVisible(True)
            case MenuItemState.DISABLED:
                action.setEnabled(False)
                action.setVisible(True)
            case MenuItemState.HIDDEN:
                action.setVisible(False)
            case MenuItemState.LOADING:
                action.setEnabled(False)
                action.setText(f"{item.text} (Loading...)")

        # Connect action with error handling
        if item.action:
            action.triggered.connect(lambda: self._execute_action(item))
        else:
            action.triggered.connect(
                lambda: self.item_triggered.emit(item.text, item.data))

        # Cache action for performance
        self._action_cache[item.text] = action

    def _execute_action(self, item: FluentMenuItem):
        """Execute action with error handling"""
        try:
            if item.action:
                item.action()
            self.item_triggered.emit(item.text, item.data)
        except Exception as e:
            print(f"Error executing action '{item.text}': {e}")

    def _apply_theme(self):
        """Apply current theme with caching"""
        theme = theme_manager
        theme_name = getattr(theme, 'current_theme', 'default')

        # Use cached stylesheet if available
        if theme_name in self._style_cache:
            self.setStyleSheet(self._style_cache[theme_name])
            return

        style_sheet = f"""
            FluentMenu {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                padding: 8px 0;
                font-size: 14px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                color: {theme.get_color('text_primary').name()};
            }}
            FluentMenu::item {{
                background-color: transparent;
                padding: 8px 16px;
                margin: 0 4px;
                border-radius: 4px;
                min-width: 120px;
            }}
            FluentMenu::item:selected {{
                background-color: {theme.get_color('accent_light').name()};
                color: {theme.get_color('text_primary').name()};
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }}
            FluentMenu::item:disabled {{
                color: {theme.get_color('text_disabled').name()};
            }}
            FluentMenu::separator {{
                height: 1px;
                background-color: {theme.get_color('border').name()};
                margin: 4px 8px;
            }}
            FluentMenu::indicator {{
                width: 16px;
                height: 16px;
                left: 8px;
            }}
            FluentMenu::indicator:checked {{
                background-color: {theme.get_color('primary').name()};
                border: 2px solid {theme.get_color('primary').name()};
                border-radius: 2px;
            }}
            /* Enhanced submenu arrow */
            FluentMenu::right-arrow {{
                width: 8px;
                height: 8px;
                right: 8px;
            }}
        """

        # Cache the stylesheet
        self._style_cache[theme_name] = style_sheet
        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, theme_name: str):
        """Handle theme change with smooth transition"""
        if self._state.animation_enabled:
            # Clear cache and apply new theme
            self._style_cache.clear()
            self._apply_theme()
        else:
            self._style_cache.clear()
            self._apply_theme()

    def remove_menu_item(self, text: str) -> bool:
        """Remove menu item by text"""
        if text not in self._state.items:
            return False

        # Find and remove the action
        for action in self.actions():
            if action.text() == text:
                self.removeAction(action)
                break

        # Remove from state and cache
        del self._state.items[text]
        if text in self._action_cache:
            del self._action_cache[text]

        self._state.last_update_time = time.time()
        return True

    def clear_menu(self) -> None:
        """Clear all menu items"""
        self.clear()
        self._state.items.clear()
        self._action_cache.clear()
        self._state.last_update_time = time.time()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring"""
        return {
            'item_count': len(self._state.items),
            'cached_actions': len(self._action_cache),
            'cached_styles': len(self._style_cache),
            'last_update': self._state.last_update_time,
            'animations_enabled': self._state.animation_enabled
        }

    def cleanup(self):
        """Clean up resources when widget is destroyed"""
        # Stop all animations
        for animation in self._animations.values():
            if animation:
                animation.stop()

        # Clear caches
        self._action_cache.clear()
        self._style_cache.clear()

        # Disconnect theme manager
        try:
            theme_manager.theme_changed.disconnect(self._on_theme_changed)
        except RuntimeError:
            pass  # Already disconnected

    # Legacy method for backward compatibility
    def apply_theme(self):
        """Legacy method for backward compatibility"""
        return self._apply_theme()


class FluentContextMenu(FluentMenu):
    """Context menu with fluent design styling"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.target_widget: Optional[QWidget] = None
        self.context_data: Any = None

    def show_at_cursor(self, target_widget: Optional[QWidget] = None, data: Any = None):
        """Show context menu at cursor position"""
        self.target_widget = target_widget
        self.context_data = data
        self.exec(QCursor.pos())

    def add_context_action(self, text: str, action: Callable[[Optional[QWidget], Any], None], icon: Optional[QIcon] = None,
                           shortcut: str = "", enabled: bool = True):
        """Add a context-aware action"""
        def context_action():
            action(self.target_widget, self.context_data)

        menu_item = FluentMenuItem(
            text, icon, MenuItemType.ACTION, context_action, shortcut, state=MenuItemState.ENABLED if enabled else MenuItemState.DISABLED)
        return self.add_menu_item(menu_item)


class FluentCommandPalette(QWidget):
    """Command palette for quick action access"""

    # Signals
    commandExecuted = Signal(str, object)  # command_id, data
    closed = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.commands: Dict[str, Dict[str, Any]] = {}
        self.filtered_commands: List[Dict[str, Any]] = []
        self.selected_index = 0

        self.setup_ui()
        self.setup_style()
        self.setup_animations()

        # Make it a popup window
        self.setWindowFlags(Qt.WindowType.Popup |
                            Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup command palette UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main container
        self.container = QFrame()
        self.container.setFixedSize(600, 400)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(8, 8, 8, 8)
        container_layout.setSpacing(8)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type a command...")
        self.search_input.textChanged.connect(self.filter_commands)
        self.search_input.returnPressed.connect(self.execute_selected_command)
        container_layout.addWidget(self.search_input)

        # Command list
        self.command_list = QListWidget()
        self.command_list.setFrameShape(QFrame.Shape.NoFrame)
        self.command_list.itemClicked.connect(self.on_item_clicked)
        container_layout.addWidget(self.command_list)

        # Status bar
        self.status_label = QLabel("Type to search commands")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 9))
        container_layout.addWidget(self.status_label)

        layout.addWidget(self.container)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 10)
        self.container.setGraphicsEffect(shadow)

    def setup_animations(self):
        """Setup animations"""
        self.fade_animation = QPropertyAnimation(
            self, QByteArray(b"windowOpacity"))
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.scale_animation = QPropertyAnimation(
            self.container, QByteArray(b"geometry"))
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutBack)

    def add_command(self, command_id: str, title: str, description: str = "",
                    category: str = "General", icon: Optional[QIcon] = None,
                    action: Optional[Callable[..., Any]] = None, shortcut: str = ""):
        """Add a command to the palette"""
        command_info: Dict[str, Any] = {
            'id': command_id,
            'title': title,
            'description': description,
            'category': category,
            'icon': icon,
            'action': action,
            'shortcut': shortcut,
            'keywords': [title.lower(), description.lower(), category.lower()]
        }

        self.commands[command_id] = command_info
        # Reset view by filtering with an empty string
        self.filter_commands("")

    def remove_command(self, command_id: str):
        """Remove a command from the palette"""
        if command_id in self.commands:
            del self.commands[command_id]
            # Re-filter with current text
            self.filter_commands(self.search_input.text())

    def filter_commands(self, search_text: str):
        """Filter commands based on search text"""
        search_text = search_text.lower().strip()

        if not search_text:
            self.filtered_commands = list(self.commands.values())
        else:
            self.filtered_commands = []
            for command_id in self.commands:  # Iterate over keys to get original order somewhat
                command = self.commands[command_id]
                # Check if search text matches any keywords
                if any(search_text in keyword for keyword in command['keywords']):
                    self.filtered_commands.append(command)

        # Optionally sort filtered_commands here, e.g., by title or category
        # self.filtered_commands.sort(key=lambda cmd: (cmd['category'], cmd['title']))

        self.refresh_command_list_display()
        self.update_status()

    # Renamed from refresh_command_list to avoid confusion
    def refresh_command_list_display(self):
        """Refresh the command list display based on self.filtered_commands"""
        self.command_list.clear()
        # self.selected_index = 0 # Resetting selection should be handled carefully

        # Group commands by category
        categories: Dict[str, List[Dict[str, Any]]] = {}
        for command in self.filtered_commands:
            category = command['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(command)

        # Add commands to list grouped by category
        # Sort categories for consistent order
        sorted_category_names = sorted(categories.keys())

        item_count = 0
        for category_name in sorted_category_names:
            commands_in_category = categories[category_name]
            if len(categories) > 1:  # Only show category headers if multiple categories
                header_item = QListWidgetItem(category_name)
                header_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                header_item.setFlags(Qt.ItemFlag.NoItemFlags)  # Not selectable
                self.command_list.addItem(header_item)

            for command in commands_in_category:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, command)

                widget = self.create_command_widget(command)
                item.setSizeHint(widget.sizeHint())

                self.command_list.addItem(item)
                self.command_list.setItemWidget(item, widget)
                item_count += 1

        if item_count > 0:
            self.select_first_selectable_item()
        else:
            self.selected_index = -1  # No selectable items

    def select_first_selectable_item(self):
        for i in range(self.command_list.count()):
            item = self.command_list.item(i)
            if item and item.flags() & Qt.ItemFlag.ItemIsSelectable:
                self.select_item(i)
                return
        self.selected_index = -1

    def create_command_widget(self, command: Dict[str, Any]) -> QWidget:
        """Create a widget for displaying a command"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Icon
        if command['icon']:
            icon_label = QLabel()
            icon_label.setPixmap(command['icon'].pixmap(20, 20))
            layout.addWidget(icon_label)

        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_label = QLabel(command['title'])
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        text_layout.addWidget(title_label)

        if command['description']:
            desc_label = QLabel(command['description'])
            desc_label.setFont(QFont("Segoe UI", 9))
            # desc_label.setStyleSheet("color: #888;") # Use theme color
            desc_label.setStyleSheet(
                f"color: {theme_manager.get_color('text_secondary').name()};")

            text_layout.addWidget(desc_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        # Shortcut
        if command['shortcut']:
            shortcut_label = QLabel(command['shortcut'])
            shortcut_label.setFont(QFont("Segoe UI", 9))
            shortcut_label.setStyleSheet(
                # "color: #666; font-family: monospace;") # Use theme color
                f"color: {theme_manager.get_color('text_secondary').name()}; font-family: monospace;")
            layout.addWidget(shortcut_label)

        return widget

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close_palette()
        elif event.key() == Qt.Key.Key_Up:
            self.move_selection(-1)
        elif event.key() == Qt.Key.Key_Down:
            self.move_selection(1)
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.execute_selected_command()
        else:
            super().keyPressEvent(event)

    def move_selection(self, delta: int):
        """Move selection up or down"""
        if self.command_list.count() == 0:
            return

        current_row = self.command_list.currentRow()
        if current_row == -1 and delta < 0:  # No selection, up pressed, select last
            new_row = self.command_list.count() - 1
        elif current_row == -1 and delta > 0:  # No selection, down pressed, select first
            new_row = 0
        else:
            new_row = current_row + delta

        # Find next selectable item
        original_new_row = new_row
        while 0 <= new_row < self.command_list.count():
            item = self.command_list.item(new_row)
            if item and item.flags() & Qt.ItemFlag.ItemIsSelectable:
                self.select_item(new_row)
                return
            new_row += 1 if delta > 0 else -1

        # If we wrapped around and didn't find anything (e.g. only headers)
        # or went out of bounds, try from the start/end if we didn't start there
        if delta > 0 and original_new_row > 0:  # Was moving down, try from top
            new_row = 0
            while 0 <= new_row < original_new_row:  # Search up to where we started
                item = self.command_list.item(new_row)
                if item and item.flags() & Qt.ItemFlag.ItemIsSelectable:
                    self.select_item(new_row)
                    return
        elif delta < 0 and original_new_row < self.command_list.count() - 1:  # Was moving up, try from bottom
            new_row = self.command_list.count() - 1
            while new_row > original_new_row:  # Search down to where we started
                item = self.command_list.item(new_row)
                if item and item.flags() & Qt.ItemFlag.ItemIsSelectable:
                    self.select_item(new_row)
                    return

    def select_item(self, row: int):
        """Select item at given row"""
        if 0 <= row < self.command_list.count():
            item = self.command_list.item(row)
            if item and item.flags() & Qt.ItemFlag.ItemIsSelectable:
                self.command_list.setCurrentRow(row)
                self.selected_index = row
                self.command_list.scrollToItem(
                    item, QListWidget.ScrollHint.EnsureVisible)

    def execute_selected_command(self):
        """Execute the currently selected command"""
        current_item = self.command_list.currentItem()
        if current_item and (current_item.flags() & Qt.ItemFlag.ItemIsSelectable):
            command = current_item.data(Qt.ItemDataRole.UserRole)
            if command and command.get('action'):
                try:
                    command['action']()
                    self.commandExecuted.emit(command['id'], command)
                except Exception as e:
                    # Basic error logging
                    print(f"Error executing command {command['id']}: {e}")
                self.close_palette()

    def on_item_clicked(self, item: QListWidgetItem):
        """Handle item click"""
        if item and (item.flags() & Qt.ItemFlag.ItemIsSelectable):
            command = item.data(Qt.ItemDataRole.UserRole)
            if command and command.get('action'):
                try:
                    command['action']()
                    self.commandExecuted.emit(command['id'], command)
                except Exception as e:
                    print(f"Error executing command {command['id']}: {e}")
                self.close_palette()

    def update_status(self):
        """Update status label"""
        # Count actual command items, not headers
        count = len(self.filtered_commands)
        if count == 0:
            self.status_label.setText("No commands found")
        elif count == 1:
            self.status_label.setText("1 command found")
        else:
            self.status_label.setText(f"{count} commands found")

    def show_palette(self, center_on: Optional[QWidget] = None):
        """Show the command palette"""
        if center_on:
            parent_window = center_on.window() if center_on else self.parentWidget()
            if parent_window:
                center_point = parent_window.rect().center()
                global_center = parent_window.mapToGlobal(center_point)
            else:  # Fallback to screen center if no clear parent window
                screen_geo = self.screen().geometry() if self.screen(
                ) else QRect(0, 0, 800, 600)  # type: ignore
                global_center = screen_geo.center()

            palette_rect = QRect(
                0, 0, self.container.width(), self.container.height())
            palette_rect.moveCenter(global_center)

            # Ensure it's within screen bounds
            if self.screen():
                screen_available_geo = self.screen().availableGeometry()  # type: ignore
                palette_rect.moveTo(
                    max(screen_available_geo.left(), min(palette_rect.left(),
                        screen_available_geo.right() - palette_rect.width())),
                    max(screen_available_geo.top(), min(palette_rect.top(),
                        screen_available_geo.bottom() - palette_rect.height()))
                )
            self.move(palette_rect.topLeft())
        elif self.parentWidget():
            # Center on parent if no specific widget given
            parent_widget = self.parentWidget()
            if parent_widget is not None:
                parent_rect = parent_widget.rect()
                global_center = parent_widget.mapToGlobal(parent_rect.center())
                palette_rect = QRect(
                    0, 0, self.container.width(), self.container.height())
                palette_rect.moveCenter(global_center)
                self.move(palette_rect.topLeft())

        # Reset state
        self.search_input.clear()
        self.search_input.setFocus()
        # This calls refresh_command_list_display and select_first_selectable_item
        self.filter_commands("")

        # Show with animation
        self.show()

        # Start animations
        self.setWindowOpacity(0.0)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

        # Initial scale for animation
        # initial_rect = QRect(self.container.x() + self.container.width() // 2,
        #                      self.container.y() + self.container.height() // 4, 0, 0)
        # final_rect = self.container.geometry()
        # self.scale_animation.setStartValue(initial_rect)
        # self.scale_animation.setEndValue(final_rect)
        # self.scale_animation.start()

    def close_palette(self):
        """Close the command palette"""
        self.closed.emit()
        self.hide()

    def setup_style(self):
        """Setup styling"""
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme"""
        theme = theme_manager

        self.container.setStyleSheet(f"""
            QFrame#commandPaletteContainer {{ /* Updated to match actual objectName */
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 12px;
            }}
        """)
        if not self.container.objectName():  # Set object name if not already set for specific styling
            self.container.setObjectName("commandPaletteContainer")

        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.get_color('background').name()};
                border: 2px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 16px;
                color: {theme.get_color('text_primary').name()};
            }}
            QLineEdit:focus {{
                border-color: {theme.get_color('primary').name()};
            }}
        """)
        self.command_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none; /* For focus rectangle */
            }}
            QListWidget::item {{
                background-color: transparent;
                border: none; /* Remove border from item itself */
                border-radius: 6px; /* Add border-radius to item */
                margin: 1px 4px; /* Add some horizontal margin */
                padding: 2px; /* Add padding for the selection highlight */
            }}
            QListWidget::item:selected {{
                background-color: {theme.get_color('accent_light').name()};
                color: {theme.get_color('text_primary').name()}; /* Ensure text color contrasts */
            }}
            QListWidget::item:hover {{
                background-color: {theme.get_color('accent_light').lighter(110).name()};
            }}
        """)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {theme.get_color('text_secondary').name()};
            }}
        """)


class RibbonGroupFrame(QFrame):
    """Custom QFrame for Ribbon Groups to hold content_layout."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.content_layout: Optional[QHBoxLayout] = None


class FluentRibbonTab(QWidget):
    """Ribbon tab container"""

    def __init__(self, parent: Optional[QWidget] = None, title: str = ""):
        super().__init__(parent)
        self.title = title
        self.groups: List[RibbonGroupFrame] = []  # Use RibbonGroupFrame

        # Renamed from self.layout
        self.main_layout: Optional[QHBoxLayout] = None
        self.setup_ui()
        self.setup_style()
        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup ribbon tab UI"""
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(12)
        self.main_layout.addStretch()

    def add_group(self, title: str) -> QWidget:  # Returns the content_area widget
        """Add a group to the ribbon tab"""
        group = RibbonGroupFrame()  # Use custom frame
        group_layout = QVBoxLayout(group)
        # Margins for the group frame itself
        group_layout.setContentsMargins(8, 8, 8, 8)
        group_layout.setSpacing(4)

        # Group content area (this is what's returned for adding buttons etc.)
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        # No margins within the button holder
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(4)  # Spacing between buttons in the group
        group.content_layout = content_layout  # Assign to custom frame attribute
        group_layout.addWidget(content_area)

        # Group title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 9))
        group_layout.addWidget(title_label)

        # Insert before stretch in the main_layout of the tab
        if self.main_layout:
            self.main_layout.insertWidget(self.main_layout.count() - 1, group)

        self.groups.append(group)
        return content_area

    def setup_style(self):
        """Setup styling"""
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme"""
        theme = theme_manager

        # Style for the tab itself
        self.setStyleSheet(f"""
            FluentRibbonTab {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
        """)
        # Style for groups within the tab
        for group_frame in self.groups:
            group_frame.setStyleSheet(f"""
                 RibbonGroupFrame {{ /* Style the custom frame */
                    background-color: transparent; /* Or a subtle group background */
                    border: 1px solid {theme.get_color('border').name()};
                    border-radius: 4px;
                    margin: 2px; /* Margin around each group */
                }}
                RibbonGroupFrame > QLabel {{ /* Style title label within the group */
                    color: {theme.get_color('text_secondary').name()};
                    font-size: 9px;
                    border: none;
                    background-color: transparent;
                    padding-top: 2px; /* Space between content and title */
                }}
            """)


class FluentRibbon(QWidget):
    """Ribbon interface for command organization"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.tabs: Dict[str, Dict[str, Any]] = {}
        self.current_tab: Optional[str] = None

        self.setup_ui()
        self.setup_style()
        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup ribbon UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab headers
        self.tab_header = QFrame()
        self.tab_header.setObjectName("ribbonTabHeader")
        self.tab_header.setFixedHeight(30)  # Height of the tab bar
        self.tab_header_layout = QHBoxLayout(self.tab_header)
        self.tab_header_layout.setContentsMargins(
            8, 0, 8, 0)  # Left/right padding for tab bar
        # No space between tab buttons themselves
        self.tab_header_layout.setSpacing(0)
        self.tab_header_layout.addStretch()

        layout.addWidget(self.tab_header)

        # Tab content area
        self.tab_content = QFrame()
        self.tab_content.setObjectName("ribbonTabContent")
        # self.tab_content.setFixedHeight(100) # Height of the content area, can be dynamic
        self.content_layout = QVBoxLayout(self.tab_content)  # Stack tabs here
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.tab_content)

        # Tab button group
        self.tab_button_group = QButtonGroup(self)  # Ensure parent is set
        # Only one tab button can be checked
        self.tab_button_group.setExclusive(True)
        self.tab_button_group.buttonClicked.connect(self.on_tab_button_clicked)

    def add_tab(self, tab_id: str, title: str) -> FluentRibbonTab:
        """Add a tab to the ribbon"""
        # Create tab button
        tab_button = QPushButton(title)
        tab_button.setCheckable(True)
        tab_button.setFixedHeight(30)  # Match tab_header height
        tab_button.setObjectName(f"ribbonTabButton_{tab_id}")
        self.tab_button_group.addButton(tab_button)

        # Insert before stretch in tab_header_layout
        if self.tab_header_layout.count() > 0:  # Check if stretch exists
            self.tab_header_layout.insertWidget(
                self.tab_header_layout.count() - 1, tab_button)
        else:  # Should not happen if addStretch was called
            self.tab_header_layout.addWidget(tab_button)

        # Create tab content widget
        tab_widget = FluentRibbonTab(
            title=title, parent=self.tab_content)  # Parent to content area
        tab_widget.setVisible(False)  # Initially hidden
        self.content_layout.addWidget(tab_widget)

        # Store tab
        self.tabs[tab_id] = {
            'button': tab_button,
            'widget': tab_widget,
            'id': tab_id
        }

        # Select first tab added
        if len(self.tabs) == 1:
            self.select_tab(tab_id)
            # tab_button.setChecked(True) # Also ensure button is checked

        return tab_widget

    def select_tab(self, tab_id: str):
        """Select a tab by its ID"""
        if tab_id not in self.tabs:
            return

        if self.current_tab == tab_id:  # Already selected
            # Ensure button is checked if somehow it got unchecked
            if not self.tabs[tab_id]['button'].isChecked():
                self.tabs[tab_id]['button'].setChecked(True)
            return

        # Hide all tab widgets and uncheck buttons
        for t_id, tab_info in self.tabs.items():
            tab_info['widget'].setVisible(False)
            if t_id != tab_id:  # Don't uncheck the one we are about to select
                tab_info['button'].setChecked(False)

        # Show selected tab widget and check its button
        selected_tab_info = self.tabs[tab_id]
        selected_tab_info['widget'].setVisible(True)
        selected_tab_info['button'].setChecked(
            True)  # Crucial for QButtonGroup
        self.current_tab = tab_id

    def on_tab_button_clicked(self, button: QPushButton):
        """Handle tab button click from QButtonGroup"""
        for tab_id, tab_info in self.tabs.items():
            if tab_info['button'] == button:
                if self.current_tab != tab_id:  # Only select if it's a different tab
                    self.select_tab(tab_id)
                elif not button.isChecked():  # If clicked on active tab to uncheck (QButtonGroup might prevent this if exclusive)
                    button.setChecked(True)  # Keep it checked
                break

    def setup_style(self):
        """Setup styling"""
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme"""
        theme = theme_manager

        self.setStyleSheet(f"""
            FluentRibbon {{
                background-color: {theme.get_color('background').name()};
            }}
        """)
        self.tab_header.setStyleSheet(f"""
            QFrame#ribbonTabHeader {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
            /* Style for QPushButton within the tab_header */
            QFrame#ribbonTabHeader > QPushButton {{
                background-color: transparent;
                border: none;
                border-bottom: 2px solid transparent; /* For selected indicator */
                padding: 0px 16px; /* top/bottom padding handled by fixed height */
                margin-right: 2px; /* Small gap between tabs */
                color: {theme.get_color('text_secondary').name()};
                font-size: 12px;
                font-weight: 500; /* Medium */
                min-height: 28px; /* Ensure text is vertically centered */
            }}
            QFrame#ribbonTabHeader > QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                color: {theme.get_color('text_primary').name()};
            }}
            QFrame#ribbonTabHeader > QPushButton:checked {{
                color: {theme.get_color('primary').name()};
                border-bottom: 2px solid {theme.get_color('primary').name()};
                font-weight: 600; /* Semibold */
            }}
        """)
        self.tab_content.setStyleSheet(f"""
            QFrame#ribbonTabContent {{
                background-color: {theme.get_color('surface').name()}; /* Or background if tabs fill it */
                border: none;
            }}
        """)


# Export all menu components
__all__ = [
    'MenuItemType',
    'FluentMenuItem',
    'FluentMenu',
    'FluentContextMenu',
    'FluentCommandPalette',
    'RibbonGroupFrame',  # Export new class
    'FluentRibbonTab',
    'FluentRibbon'
]
