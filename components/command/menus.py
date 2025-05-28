"""
Fluent Design Menu and Command Components
Advanced menu systems, command palettes, and context menus
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QMenu, QAction, QScrollArea,
    QButtonGroup, QSplitter, QTreeWidget, QTreeWidgetItem, QComboBox,
    QCheckBox, QToolButton, QWidgetAction, QGraphicsDropShadowEffect
)
from PySide6.QtCore import (
    Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QRect,
    QPoint, QSize, QParallelAnimationGroup, QSequentialAnimationGroup
)
from PySide6.QtGui import (
    QFont, QIcon, QPainter, QColor, QPixmap, QKeySequence, QAction as QGuiAction,
    QPalette, QFontMetrics, QLinearGradient, QBrush, QPen
)
from core.theme import theme_manager
from typing import Optional, List, Dict, Any, Callable, Union
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

    def __init__(self, text: str = "", icon: QIcon = None, item_type: MenuItemType = MenuItemType.ACTION,
                 action: Callable = None, shortcut: str = "", checked: bool = False,
                 enabled: bool = True, data: Any = None):
        self.text = text
        self.icon = icon
        self.item_type = item_type
        self.action = action
        self.shortcut = shortcut
        self.checked = checked
        self.enabled = enabled
        self.data = data
        self.children = []  # For submenus


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
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
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
        else:
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
        self.target_widget = None
        self.context_data = None

    def show_at_cursor(self, target_widget: QWidget = None, data: Any = None):
        """Show context menu at cursor position"""
        self.target_widget = target_widget
        self.context_data = data

        cursor_pos = self.parent().mapFromGlobal(self.parent().cursor().pos()
                                                 ) if self.parent() else self.cursor().pos()
        self.exec(self.parent().mapToGlobal(cursor_pos)
                  if self.parent() else cursor_pos)

    def add_context_action(self, text: str, action: Callable, icon: QIcon = None,
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

        self.commands = {}  # command_id -> command_info
        self.filtered_commands = []
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
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.scale_animation = QPropertyAnimation(self.container, b"geometry")
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutBack)

    def add_command(self, command_id: str, title: str, description: str = "",
                    category: str = "General", icon: QIcon = None,
                    action: Callable = None, shortcut: str = ""):
        """Add a command to the palette"""
        command_info = {
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
        self.refresh_command_list()

    def remove_command(self, command_id: str):
        """Remove a command from the palette"""
        if command_id in self.commands:
            del self.commands[command_id]
            self.refresh_command_list()

    def filter_commands(self, search_text: str):
        """Filter commands based on search text"""
        search_text = search_text.lower().strip()

        if not search_text:
            self.filtered_commands = list(self.commands.values())
        else:
            self.filtered_commands = []
            for command in self.commands.values():
                # Check if search text matches any keywords
                if any(search_text in keyword for keyword in command['keywords']):
                    self.filtered_commands.append(command)

        self.refresh_command_list()
        self.update_status()

    def refresh_command_list(self):
        """Refresh the command list display"""
        self.command_list.clear()
        self.selected_index = 0

        # Group commands by category
        categories = {}
        for command in self.filtered_commands:
            category = command['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(command)

        # Add commands to list grouped by category
        for category, commands in categories.items():
            if len(categories) > 1:  # Only show category headers if multiple categories
                # Add category header
                header_item = QListWidgetItem(category)
                header_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                header_item.setFlags(Qt.ItemFlag.NoItemFlags)  # Not selectable
                self.command_list.addItem(header_item)

            for command in commands:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, command)

                # Create custom widget for command item
                widget = self.create_command_widget(command)
                item.setSizeHint(widget.sizeHint())

                self.command_list.addItem(item)
                self.command_list.setItemWidget(item, widget)

        # Select first selectable item
        if self.command_list.count() > 0:
            self.select_item(0)

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
            desc_label.setStyleSheet("color: #888;")
            text_layout.addWidget(desc_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        # Shortcut
        if command['shortcut']:
            shortcut_label = QLabel(command['shortcut'])
            shortcut_label.setFont(QFont("Segoe UI", 9))
            shortcut_label.setStyleSheet(
                "color: #666; font-family: monospace;")
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
        new_row = max(
            0, min(self.command_list.count() - 1, current_row + delta))

        # Skip non-selectable items (headers)
        while new_row < self.command_list.count() and new_row >= 0:
            item = self.command_list.item(new_row)
            if item.flags() & Qt.ItemFlag.ItemIsSelectable:
                break
            new_row += delta if delta > 0 else -1

        if 0 <= new_row < self.command_list.count():
            self.select_item(new_row)

    def select_item(self, row: int):
        """Select item at given row"""
        self.command_list.setCurrentRow(row)
        self.selected_index = row

    def execute_selected_command(self):
        """Execute the currently selected command"""
        current_item = self.command_list.currentItem()
        if current_item:
            command = current_item.data(Qt.ItemDataRole.UserRole)
            if command and command.get('action'):
                command['action']()
                self.commandExecuted.emit(command['id'], command)
                self.close_palette()

    def on_item_clicked(self, item: QListWidgetItem):
        """Handle item click"""
        command = item.data(Qt.ItemDataRole.UserRole)
        if command and command.get('action'):
            command['action']()
            self.commandExecuted.emit(command['id'], command)
            self.close_palette()

    def update_status(self):
        """Update status label"""
        count = len(self.filtered_commands)
        if count == 0:
            self.status_label.setText("No commands found")
        elif count == 1:
            self.status_label.setText("1 command found")
        else:
            self.status_label.setText(f"{count} commands found")

    def show_palette(self, center_on: QWidget = None):
        """Show the command palette"""
        # Position the palette
        if center_on:
            center_point = center_on.rect().center()
            global_center = center_on.mapToGlobal(center_point)
            palette_rect = QRect(0, 0, 600, 400)
            palette_rect.moveCenter(global_center)
            self.move(palette_rect.topLeft())

        # Reset state
        self.search_input.clear()
        self.search_input.setFocus()
        self.filter_commands("")

        # Show with animation
        self.show()

        # Start animations
        self.setWindowOpacity(0.0)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

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

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 12px;
            }}
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
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                margin: 1px;
            }}
            QListWidget::item:selected {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QListWidget::item:hover {{
                background-color: {theme.get_color('accent_light').lighter(120).name()};
            }}
            QLabel {{
                color: {theme.get_color('text_secondary').name()};
            }}
        """)


class FluentRibbonTab(QWidget):
    """Ribbon tab container"""

    def __init__(self, parent: Optional[QWidget] = None, title: str = ""):
        super().__init__(parent)
        self.title = title
        self.groups = []

        self.setup_ui()
        self.setup_style()
        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup ribbon tab UI"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(12)
        self.layout.addStretch()

    def add_group(self, title: str) -> QWidget:
        """Add a group to the ribbon tab"""
        group = QFrame()
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 8, 8, 8)
        group_layout.setSpacing(4)

        # Group content area
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(4)
        group_layout.addWidget(content_area)

        # Group title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 9))
        group_layout.addWidget(title_label)

        # Insert before stretch
        self.layout.insertWidget(self.layout.count() - 1, group)

        # Store reference
        group.content_layout = content_layout
        self.groups.append(group)

        return content_area

    def setup_style(self):
        """Setup styling"""
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme"""
        theme = theme_manager

        self.setStyleSheet(f"""
            FluentRibbonTab {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
            QFrame {{
                background-color: transparent;
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                margin: 2px;
            }}
            QLabel {{
                color: {theme.get_color('text_secondary').name()};
                font-size: 9px;
                border: none;
                background-color: transparent;
            }}
        """)


class FluentRibbon(QWidget):
    """Ribbon interface for command organization"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.tabs = {}
        self.current_tab = None

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
        self.tab_header.setFixedHeight(30)
        self.tab_header_layout = QHBoxLayout(self.tab_header)
        self.tab_header_layout.setContentsMargins(8, 0, 8, 0)
        self.tab_header_layout.setSpacing(0)
        self.tab_header_layout.addStretch()

        layout.addWidget(self.tab_header)

        # Tab content area
        self.tab_content = QFrame()
        self.tab_content.setFixedHeight(100)
        self.content_layout = QVBoxLayout(self.tab_content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.tab_content)

        # Tab button group
        self.tab_button_group = QButtonGroup()
        self.tab_button_group.buttonClicked.connect(self.on_tab_changed)

    def add_tab(self, tab_id: str, title: str) -> FluentRibbonTab:
        """Add a tab to the ribbon"""
        # Create tab button
        tab_button = QPushButton(title)
        tab_button.setCheckable(True)
        tab_button.setFixedHeight(30)
        self.tab_button_group.addButton(tab_button)

        # Insert before stretch
        self.tab_header_layout.insertWidget(
            self.tab_header_layout.count() - 1, tab_button)

        # Create tab content
        tab_widget = FluentRibbonTab(title=title)
        tab_widget.setVisible(False)
        self.content_layout.addWidget(tab_widget)

        # Store tab
        self.tabs[tab_id] = {
            'button': tab_button,
            'widget': tab_widget,
            'id': tab_id
        }

        # Select first tab
        if len(self.tabs) == 1:
            self.select_tab(tab_id)

        return tab_widget

    def select_tab(self, tab_id: str):
        """Select a tab"""
        if tab_id not in self.tabs:
            return

        # Hide all tabs
        for tab_info in self.tabs.values():
            tab_info['widget'].setVisible(False)
            tab_info['button'].setChecked(False)

        # Show selected tab
        selected_tab = self.tabs[tab_id]
        selected_tab['widget'].setVisible(True)
        selected_tab['button'].setChecked(True)
        self.current_tab = tab_id

    def on_tab_changed(self, button: QPushButton):
        """Handle tab change"""
        for tab_id, tab_info in self.tabs.items():
            if tab_info['button'] == button:
                self.select_tab(tab_id)
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
                border-bottom: 2px solid {theme.get_color('primary').name()};
            }}
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border: none;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                padding: 6px 16px;
                color: {theme.get_color('text_primary').name()};
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QPushButton:checked {{
                background-color: {theme.get_color('primary').name()};
                color: white;
            }}
        """)


# Export all menu components
__all__ = [
    'MenuItemType',
    'FluentMenuItem',
    'FluentMenu',
    'FluentContextMenu',
    'FluentCommandPalette',
    'FluentRibbonTab',
    'FluentRibbon'
]
