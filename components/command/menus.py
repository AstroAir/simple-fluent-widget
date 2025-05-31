"""
Fluent Design Menu and Command Components
Advanced menu systems, command palettes, and context menus
"""

from PySide6.QtCore import QByteArray, Qt, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QMenu, 
    QGraphicsDropShadowEffect, QButtonGroup
)
from PySide6.QtGui import (
    QFont, QIcon, QColor, QKeySequence, QCursor, QAction
)
from core.theme import theme_manager
from typing import Optional, List, Dict, Any, Callable
from enum import Enum


class MenuItemType(Enum):
    """Types of menu items"""
    ACTION = "action"
    SEPARATOR = "separator"
    SUBMENU = "submenu"
    HEADER = "header"
    CUSTOM = "custom"


class FluentMenuItem:
    """Menu item data structure"""

    def __init__(self, text: str = "", icon: Optional[QIcon] = None, item_type: MenuItemType = MenuItemType.ACTION,
                 action: Optional[Callable[..., Any]] = None, shortcut: str = "", checked: bool = False,
                 enabled: bool = True, data: Any = None):
        self.text = text
        self.icon = icon
        self.item_type = item_type
        self.action = action
        self.shortcut = shortcut
        self.checked = checked
        self.enabled = enabled
        self.data = data
        self.children: List['FluentMenuItem'] = []  # For submenus


class FluentMenu(QMenu):
    """Enhanced Fluent Design menu with animations and modern styling"""

    def __init__(self, parent: Optional[QWidget] = None, title: str = ""):
        super().__init__(title, parent)

        self.setup_style()
        self.setup_animations()
        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_style(self):
        """Setup menu styling"""
        self.apply_theme()

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    def setup_animations(self):
        """Setup menu animations"""
        self.fade_animation = QPropertyAnimation(self, QByteArray(b"windowOpacity"))
        self.fade_animation.setDuration(150)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def showEvent(self, event):
        """Override show event for animation"""
        super().showEvent(event)

        # Fade in animation
        self.setWindowOpacity(0.0)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

    def add_menu_item(self, item: FluentMenuItem) -> QAction:
        """Add a menu item"""
        if item.item_type == MenuItemType.SEPARATOR:
            return self.addSeparator()
        elif item.item_type == MenuItemType.HEADER:
            action = QAction(item.text, self)
            action.setEnabled(False)
            action.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            return self.addAction(action)
        elif item.item_type == MenuItemType.SUBMENU:
            submenu = FluentMenu(self, item.text)
            if item.icon:
                submenu.setIcon(item.icon)

            # Add children to submenu
            for child in item.children:
                submenu.add_menu_item(child)

            return self.addMenu(submenu)
        else: # ACTION or CUSTOM (handled similarly here)
            action = QAction(item.text, self)
            if item.icon:
                action.setIcon(item.icon)
            if item.shortcut:
                action.setShortcut(QKeySequence(item.shortcut))
            action.setCheckable(item.checked)
            action.setEnabled(item.enabled)

            if item.action:
                action.triggered.connect(item.action)

            return self.addAction(action)

    def apply_theme(self):
        """Apply current theme"""
        theme = theme_manager

        self.setStyleSheet(f"""
            FluentMenu {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                padding: 8px 0;
                font-size: 14px;
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
        """)


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
            text, icon, MenuItemType.ACTION, context_action, shortcut, enabled=enabled)
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
        self.fade_animation = QPropertyAnimation(self, QByteArray(b"windowOpacity"))
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.scale_animation = QPropertyAnimation(self.container, QByteArray(b"geometry"))
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
        self.filter_commands("") # Reset view by filtering with an empty string

    def remove_command(self, command_id: str):
        """Remove a command from the palette"""
        if command_id in self.commands:
            del self.commands[command_id]
            self.filter_commands(self.search_input.text()) # Re-filter with current text

    def filter_commands(self, search_text: str):
        """Filter commands based on search text"""
        search_text = search_text.lower().strip()

        if not search_text:
            self.filtered_commands = list(self.commands.values())
        else:
            self.filtered_commands = []
            for command_id in self.commands: # Iterate over keys to get original order somewhat
                command = self.commands[command_id]
                # Check if search text matches any keywords
                if any(search_text in keyword for keyword in command['keywords']):
                    self.filtered_commands.append(command)
        
        # Optionally sort filtered_commands here, e.g., by title or category
        # self.filtered_commands.sort(key=lambda cmd: (cmd['category'], cmd['title']))


        self.refresh_command_list_display()
        self.update_status()

    def refresh_command_list_display(self): # Renamed from refresh_command_list to avoid confusion
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
            if len(categories) > 1: # Only show category headers if multiple categories
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
                item_count +=1
        
        if item_count > 0:
            self.select_first_selectable_item()
        else:
            self.selected_index = -1 # No selectable items

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
            desc_label.setStyleSheet(f"color: {theme_manager.get_color('text_secondary').name()};")

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
        if current_row == -1 and delta < 0 : # No selection, up pressed, select last
            new_row = self.command_list.count() -1
        elif current_row == -1 and delta > 0 : # No selection, down pressed, select first
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
        if delta > 0 and original_new_row > 0: # Was moving down, try from top
            new_row = 0
            while 0 <= new_row < original_new_row : # Search up to where we started
                 item = self.command_list.item(new_row)
                 if item and item.flags() & Qt.ItemFlag.ItemIsSelectable:
                    self.select_item(new_row)
                    return
        elif delta < 0 and original_new_row < self.command_list.count() -1 : # Was moving up, try from bottom
            new_row = self.command_list.count() -1
            while new_row > original_new_row: # Search down to where we started
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
                 self.command_list.scrollToItem(item, QListWidget.ScrollHint.EnsureVisible)


    def execute_selected_command(self):
        """Execute the currently selected command"""
        current_item = self.command_list.currentItem()
        if current_item and (current_item.flags() & Qt.ItemFlag.ItemIsSelectable) :
            command = current_item.data(Qt.ItemDataRole.UserRole)
            if command and command.get('action'):
                try:
                    command['action']()
                    self.commandExecuted.emit(command['id'], command)
                except Exception as e:
                    print(f"Error executing command {command['id']}: {e}") # Basic error logging
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
            else: # Fallback to screen center if no clear parent window
                screen_geo = self.screen().geometry() if self.screen() else QRect(0,0,800,600) # type: ignore
                global_center = screen_geo.center()

            palette_rect = QRect(0, 0, self.container.width(), self.container.height())
            palette_rect.moveCenter(global_center)
            
            # Ensure it's within screen bounds
            if self.screen():
                screen_available_geo = self.screen().availableGeometry() # type: ignore
                palette_rect.moveTo(
                    max(screen_available_geo.left(), min(palette_rect.left(), screen_available_geo.right() - palette_rect.width())),
                    max(screen_available_geo.top(), min(palette_rect.top(), screen_available_geo.bottom() - palette_rect.height()))
                )
            self.move(palette_rect.topLeft())
        elif self.parentWidget():
             # Center on parent if no specific widget given
            parent_rect = self.parentWidget().rect()
            global_center = self.parentWidget().mapToGlobal(parent_rect.center())
            palette_rect = QRect(0, 0, self.container.width(), self.container.height())
            palette_rect.moveCenter(global_center)
            self.move(palette_rect.topLeft())


        # Reset state
        self.search_input.clear()
        self.search_input.setFocus()
        self.filter_commands("") # This calls refresh_command_list_display and select_first_selectable_item

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
        if not self.container.objectName(): # Set object name if not already set for specific styling
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
        self.groups: List[RibbonGroupFrame] = [] # Use RibbonGroupFrame

        self.main_layout: Optional[QHBoxLayout] = None # Renamed from self.layout
        self.setup_ui()
        self.setup_style()
        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup ribbon tab UI"""
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(12)
        self.main_layout.addStretch()

    def add_group(self, title: str) -> QWidget: # Returns the content_area widget
        """Add a group to the ribbon tab"""
        group = RibbonGroupFrame() # Use custom frame
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 8, 8, 8) # Margins for the group frame itself
        group_layout.setSpacing(4)

        # Group content area (this is what's returned for adding buttons etc.)
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0) # No margins within the button holder
        content_layout.setSpacing(4) # Spacing between buttons in the group
        group.content_layout = content_layout # Assign to custom frame attribute
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
        self.tab_header.setFixedHeight(30) # Height of the tab bar
        self.tab_header_layout = QHBoxLayout(self.tab_header)
        self.tab_header_layout.setContentsMargins(8, 0, 8, 0) # Left/right padding for tab bar
        self.tab_header_layout.setSpacing(0) # No space between tab buttons themselves
        self.tab_header_layout.addStretch()

        layout.addWidget(self.tab_header)

        # Tab content area
        self.tab_content = QFrame()
        self.tab_content.setObjectName("ribbonTabContent")
        # self.tab_content.setFixedHeight(100) # Height of the content area, can be dynamic
        self.content_layout = QVBoxLayout(self.tab_content) # Stack tabs here
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.tab_content)

        # Tab button group
        self.tab_button_group = QButtonGroup(self) # Ensure parent is set
        self.tab_button_group.setExclusive(True) # Only one tab button can be checked
        self.tab_button_group.buttonClicked.connect(self.on_tab_button_clicked)


    def add_tab(self, tab_id: str, title: str) -> FluentRibbonTab:
        """Add a tab to the ribbon"""
        # Create tab button
        tab_button = QPushButton(title)
        tab_button.setCheckable(True)
        tab_button.setFixedHeight(30) # Match tab_header height
        tab_button.setObjectName(f"ribbonTabButton_{tab_id}")
        self.tab_button_group.addButton(tab_button)


        # Insert before stretch in tab_header_layout
        if self.tab_header_layout.count() > 0: # Check if stretch exists
             self.tab_header_layout.insertWidget(self.tab_header_layout.count() - 1, tab_button)
        else: # Should not happen if addStretch was called
             self.tab_header_layout.addWidget(tab_button)


        # Create tab content widget
        tab_widget = FluentRibbonTab(title=title, parent=self.tab_content) # Parent to content area
        tab_widget.setVisible(False) # Initially hidden
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

        if self.current_tab == tab_id: # Already selected
            # Ensure button is checked if somehow it got unchecked
            if not self.tabs[tab_id]['button'].isChecked():
                self.tabs[tab_id]['button'].setChecked(True)
            return

        # Hide all tab widgets and uncheck buttons
        for t_id, tab_info in self.tabs.items():
            tab_info['widget'].setVisible(False)
            if t_id != tab_id : # Don't uncheck the one we are about to select
                 tab_info['button'].setChecked(False)


        # Show selected tab widget and check its button
        selected_tab_info = self.tabs[tab_id]
        selected_tab_info['widget'].setVisible(True)
        selected_tab_info['button'].setChecked(True) # Crucial for QButtonGroup
        self.current_tab = tab_id

    def on_tab_button_clicked(self, button: QPushButton):
        """Handle tab button click from QButtonGroup"""
        for tab_id, tab_info in self.tabs.items():
            if tab_info['button'] == button:
                if self.current_tab != tab_id: # Only select if it's a different tab
                    self.select_tab(tab_id)
                elif not button.isChecked(): # If clicked on active tab to uncheck (QButtonGroup might prevent this if exclusive)
                    button.setChecked(True) # Keep it checked
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
    'RibbonGroupFrame', # Export new class
    'FluentRibbonTab',
    'FluentRibbon'
]
