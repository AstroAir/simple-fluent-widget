"""
Fluent Design Command Bar and Toolbar Components
Command bars, toolbars, and action-based UI components for enterprise applications
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QFrame, QMenu, QButtonGroup)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QKeySequence
from core.theme import theme_manager
from typing import Optional


class FluentCommandBar(QFrame):
    """Fluent Design style command bar"""

    command_triggered = Signal(str)  # Command name

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._commands = {}
        self._primary_commands = []
        self._secondary_commands = []
        self._overflow_threshold = 6
        self._compact_mode = False

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setFixedHeight(48)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(12, 6, 12, 6)
        self.main_layout.setSpacing(4)

        # Primary commands area
        self.primary_area = QFrame()
        self.primary_layout = QHBoxLayout(self.primary_area)
        self.primary_layout.setContentsMargins(0, 0, 0, 0)
        self.primary_layout.setSpacing(4)

        # Overflow button for secondary commands
        self.overflow_btn = QPushButton("⋯")
        self.overflow_btn.setFixedSize(36, 36)
        self.overflow_btn.clicked.connect(self._show_overflow_menu)
        self.overflow_btn.setVisible(False)

        self.main_layout.addWidget(self.primary_area)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.overflow_btn)

    def addCommand(self, name: str, text: str, icon: Optional[QIcon] = None,
                   shortcut: Optional[str] = None, tooltip: Optional[str] = None,
                   is_primary: bool = True, enabled: bool = True) -> QPushButton:
        """Add command to command bar"""

        # Create command button
        if self._compact_mode:
            btn = QPushButton()
            btn.setFixedSize(36, 36)
            if icon:
                btn.setIcon(icon)
        else:
            btn = QPushButton(text)
            btn.setFixedHeight(36)
            if icon:
                btn.setIcon(icon)
                btn.setIconSize(QSize(16, 16))

        btn.setEnabled(enabled)
        btn.clicked.connect(lambda: self.command_triggered.emit(name))

        if tooltip:
            btn.setToolTip(tooltip)

        if shortcut:
            btn.setShortcut(QKeySequence(shortcut))

        # Store command info
        command_info = {
            'name': name,
            'text': text,
            'icon': icon,
            'button': btn,
            'shortcut': shortcut,
            'tooltip': tooltip,
            'enabled': enabled,
            'is_primary': is_primary
        }

        self._commands[name] = command_info

        if is_primary:
            self._primary_commands.append(command_info)
            self._add_to_primary_area(btn)
        else:
            self._secondary_commands.append(command_info)

        self._update_overflow_visibility()
        return btn

    def addSeparator(self, is_primary: bool = True):
        """Add separator to command bar"""
        separator = QFrame()
        separator.setFrameStyle(QFrame.Shape.VLine)
        separator.setFixedWidth(1)
        separator.setFixedHeight(24)

        if is_primary:
            self._add_to_primary_area(separator)

    def removeCommand(self, name: str):
        """Remove command from command bar"""
        if name in self._commands:
            command_info = self._commands[name]

            # Remove from layout
            command_info['button'].deleteLater()

            # Remove from lists
            if command_info in self._primary_commands:
                self._primary_commands.remove(command_info)
            if command_info in self._secondary_commands:
                self._secondary_commands.remove(command_info)

            # Remove from storage
            del self._commands[name]

            self._update_overflow_visibility()

    def setCommandEnabled(self, name: str, enabled: bool):
        """Set command enabled state"""
        if name in self._commands:
            self._commands[name]['button'].setEnabled(enabled)
            self._commands[name]['enabled'] = enabled

    def setCompactMode(self, compact: bool):
        """Set compact mode (icon-only buttons)"""
        self._compact_mode = compact

        # Update existing buttons
        for command_info in self._commands.values():
            btn = command_info['button']
            if compact:
                btn.setText("")
                btn.setFixedSize(36, 36)
            else:
                btn.setText(command_info['text'])
                btn.setFixedHeight(36)
                btn.setMinimumWidth(0)

    def _add_to_primary_area(self, widget: QWidget):
        """Add widget to primary area"""
        self.primary_layout.addWidget(widget)

    def _update_overflow_visibility(self):
        """Update overflow button visibility"""
        has_secondary = len(self._secondary_commands) > 0
        has_overflow_primary = len(
            self._primary_commands) > self._overflow_threshold

        self.overflow_btn.setVisible(has_secondary or has_overflow_primary)

    def _show_overflow_menu(self):
        """Show overflow menu with secondary commands"""
        menu = QMenu(self)

        # Add overflow primary commands if any
        visible_primary = self._overflow_threshold
        if len(self._primary_commands) > visible_primary:
            for command_info in self._primary_commands[visible_primary:]:
                action = menu.addAction(command_info['text'])
                if command_info['icon']:
                    action.setIcon(command_info['icon'])
                action.triggered.connect(
                    lambda _, name=command_info['name']: self.command_triggered.emit(
                        name)
                )
                action.setEnabled(command_info['enabled'])

        # Add separator if we have both types
        if self._secondary_commands and len(self._primary_commands) > visible_primary:
            menu.addSeparator()

        # Add secondary commands
        for command_info in self._secondary_commands:
            action = menu.addAction(command_info['text'])
            if command_info['icon']:
                action.setIcon(command_info['icon'])
            action.triggered.connect(
                lambda _, name=command_info['name']: self.command_triggered.emit(
                    name)
            )
            action.setEnabled(command_info['enabled'])

        # Show menu
        button_rect = self.overflow_btn.geometry()
        menu_pos = self.mapToGlobal(button_rect.bottomLeft())
        menu.exec(menu_pos)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentCommandBar {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
            QPushButton {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('border').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QPushButton:disabled {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_disabled').name()};
            }}
            QFrame[frameShape="5"] {{
                color: {theme.get_color('border').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentToolbar(QFrame):
    """Fluent Design style toolbar"""

    action_triggered = Signal(str)  # Action name

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._orientation = orientation
        self._actions = {}
        self._toggle_groups = {}

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        if self._orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(44)
            self.main_layout = QHBoxLayout(self)
        else:
            self.setFixedWidth(44)
            self.main_layout = QVBoxLayout(self)

        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(2)

    def addToolbarAction(self, name: str, icon: QIcon, tooltip: str = "",
                         checkable: bool = False, toggle_group: Optional[str] = None) -> QPushButton:
        """Add action to toolbar (renamed to avoid conflict with QWidget.addAction)"""

        btn = QPushButton()
        btn.setIcon(icon)
        btn.setIconSize(QSize(20, 20))
        btn.setFixedSize(32, 32)
        btn.setCheckable(checkable)

        if tooltip:
            btn.setToolTip(tooltip)

        btn.clicked.connect(lambda: self.action_triggered.emit(name))

        # Handle toggle groups
        if toggle_group and checkable:
            if toggle_group not in self._toggle_groups:
                self._toggle_groups[toggle_group] = QButtonGroup(self)
                self._toggle_groups[toggle_group].setExclusive(True)

            self._toggle_groups[toggle_group].addButton(btn)

        # Store action info
        self._actions[name] = {
            'button': btn,
            'name': name,
            'icon': icon,
            'tooltip': tooltip,
            'checkable': checkable,
            'toggle_group': toggle_group
        }

        self.main_layout.addWidget(btn)
        return btn

    def addSeparator(self):
        """Add separator to toolbar"""
        separator = QFrame()
        if self._orientation == Qt.Orientation.Horizontal:
            separator.setFrameStyle(QFrame.Shape.VLine)
            separator.setFixedWidth(1)
            separator.setFixedHeight(24)
        else:
            separator.setFrameStyle(QFrame.Shape.HLine)
            separator.setFixedHeight(1)
            separator.setFixedWidth(24)

        self.main_layout.addWidget(separator)

    def addStretch(self):
        """Add stretch to toolbar"""
        self.main_layout.addStretch()

    def setActionChecked(self, name: str, checked: bool):
        """Set action checked state"""
        if name in self._actions:
            self._actions[name]['button'].setChecked(checked)

    def setActionEnabled(self, name: str, enabled: bool):
        """Set action enabled state"""
        if name in self._actions:
            self._actions[name]['button'].setEnabled(enabled)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentToolbar {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
            }}
            QPushButton {{
                background-color: transparent;
                color: {theme.get_color('text_primary').name()};
                border: 1px solid transparent;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('border').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QPushButton:checked {{
                background-color: {theme.get_color('primary').name()};
                color: white;
            }}
            QPushButton:disabled {{
                color: {theme.get_color('text_disabled').name()};
            }}
            QFrame[frameShape="5"], QFrame[frameShape="4"] {{
                color: {theme.get_color('border').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentRibbon(QWidget):
    """Fluent Design style ribbon interface"""

    command_triggered = Signal(str, str)  # tab_name, command_name

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._tabs = {}
        self._current_tab = None
        self._collapsed = False

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Tab bar
        self.tab_bar = QFrame()
        self.tab_bar.setFixedHeight(32)
        self.tab_bar_layout = QHBoxLayout(self.tab_bar)
        self.tab_bar_layout.setContentsMargins(8, 0, 8, 0)
        self.tab_bar_layout.setSpacing(0)

        # Collapse/expand button
        self.collapse_btn = QPushButton("^")
        self.collapse_btn.setFixedSize(24, 24)
        self.collapse_btn.clicked.connect(self._toggle_collapse)

        self.tab_bar_layout.addStretch()
        self.tab_bar_layout.addWidget(self.collapse_btn)

        # Content area
        self.content_area = QFrame()
        self.content_area.setFixedHeight(120)
        self.content_layout = QHBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_layout.setSpacing(16)

        self.main_layout.addWidget(self.tab_bar)
        self.main_layout.addWidget(self.content_area)

    def addTab(self, name: str, title: str) -> 'FluentRibbonTab':
        """Add ribbon tab"""

        # Create tab button
        tab_btn = QPushButton(title)
        tab_btn.setCheckable(True)
        tab_btn.setFixedHeight(32)
        tab_btn.clicked.connect(lambda: self._select_tab(name))

        # Insert before collapse button
        insert_index = self.tab_bar_layout.count() - 2
        self.tab_bar_layout.insertWidget(insert_index, tab_btn)

        # Create tab content
        tab_content = FluentRibbonTab(name, self)
        tab_content.setVisible(False)

        # Store tab info
        self._tabs[name] = {
            'name': name,
            'title': title,
            'button': tab_btn,
            'content': tab_content
        }

        # Select first tab
        if len(self._tabs) == 1:
            self._select_tab(name)

        return tab_content

    def _select_tab(self, name: str):
        """Select ribbon tab"""
        if name not in self._tabs:
            return

        # Update button states
        for tab_name, tab_info in self._tabs.items():
            tab_info['button'].setChecked(tab_name == name)
            tab_info['content'].setVisible(tab_name == name)

        # Clear content layout
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        # Add selected tab content
        self.content_layout.addWidget(self._tabs[name]['content'])
        self._current_tab = name

    def _toggle_collapse(self):
        """Toggle ribbon collapse state"""
        self._collapsed = not self._collapsed

        if self._collapsed:
            self.content_area.setVisible(False)
            self.collapse_btn.setText("v")
            self.setFixedHeight(32)
        else:
            self.content_area.setVisible(True)
            self.collapse_btn.setText("^")
            self.setFixedHeight(152)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentRibbon {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
            QFrame {{
                background-color: {theme.get_color('surface').name()};
            }}
            QPushButton {{
                background-color: transparent;
                color: {theme.get_color('text_primary').name()};
                border: none;
                padding: 6px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QPushButton:checked {{
                background-color: {theme.get_color('accent_medium').name()};
                border-bottom: 2px solid {theme.get_color('primary').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentRibbonTab(QWidget):
    """Fluent Design style ribbon tab content"""

    def __init__(self, tab_name: str, parent_ribbon: 'FluentRibbon'):
        super().__init__()

        self._tab_name = tab_name
        self._parent_ribbon = parent_ribbon
        self._groups = []

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI"""
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(16)

    def addGroup(self, title: str) -> 'FluentRibbonGroup':
        """Add ribbon group"""
        group = FluentRibbonGroup(title, self._tab_name, self._parent_ribbon)
        self.main_layout.addWidget(group)
        self._groups.append(group)
        return group

    def addStretch(self):
        """Add stretch to tab"""
        self.main_layout.addStretch()


class FluentRibbonGroup(QFrame):
    """Fluent Design style ribbon group"""

    def __init__(self, title: str, tab_name: str, parent_ribbon: 'FluentRibbon'):
        super().__init__()

        self._title = title
        self._tab_name = tab_name
        self._parent_ribbon = parent_ribbon

        self._setup_ui()
        self._setup_style()

    def _setup_ui(self):
        """Setup UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 4)
        self.main_layout.setSpacing(4)

        # Content area
        self.content_area = QFrame()
        self.content_layout = QHBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(4)

        # Title label
        self.title_label = QLabel(self._title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(self.content_area, 1)
        self.main_layout.addWidget(self.title_label)

    def addLargeButton(self, name: str, text: str, icon: QIcon, tooltip: str = "") -> QPushButton:
        """Add large button (icon on top, text below)"""
        btn = QPushButton(text)
        btn.setIcon(icon)
        btn.setIconSize(QSize(32, 32))
        btn.setFixedSize(64, 80)

        if tooltip:
            btn.setToolTip(tooltip)

        btn.clicked.connect(
            lambda: self._parent_ribbon.command_triggered.emit(self._tab_name, name))

        self.content_layout.addWidget(btn)
        return btn

    def addSmallButton(self, name: str, text: str, icon: QIcon, tooltip: str = "") -> QPushButton:
        """Add small button (icon and text side by side)"""
        btn = QPushButton(text)
        btn.setIcon(icon)
        btn.setIconSize(QSize(16, 16))
        btn.setFixedHeight(24)

        if tooltip:
            btn.setToolTip(tooltip)

        btn.clicked.connect(
            lambda: self._parent_ribbon.command_triggered.emit(self._tab_name, name))

        self.content_layout.addWidget(btn)
        return btn

    def addSeparator(self):
        """Add vertical separator"""
        separator = QFrame()
        separator.setFrameStyle(QFrame.Shape.VLine)
        separator.setFixedWidth(1)
        separator.setFixedHeight(70)

        self.content_layout.addWidget(separator)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentRibbonGroup {{
                background-color: {theme.get_color('background').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
            }}
            QPushButton {{
                background-color: transparent;
                color: {theme.get_color('text_primary').name()};
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 2px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('border').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QLabel {{
                color: {theme.get_color('text_secondary').name()};
                background-color: transparent;
                border: none;
            }}
            QFrame[frameShape="5"] {{
                color: {theme.get_color('border').name()};
            }}
        """

        self.setStyleSheet(style_sheet)


class FluentQuickAccessToolbar(QFrame):
    """Fluent Design style quick access toolbar"""

    action_triggered = Signal(str)  # Action name

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._actions = {}

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setFixedHeight(28)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 2, 4, 2)
        self.main_layout.setSpacing(2)

        # Customize button
        self.customize_btn = QPushButton("▼")
        self.customize_btn.setFixedSize(16, 24)
        self.customize_btn.clicked.connect(self._show_customize_menu)

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.customize_btn)

    def addQuickAction(self, name: str, icon: QIcon, tooltip: str = "") -> QPushButton:
        """Add action to quick access toolbar (renamed to avoid conflict)"""
        btn = QPushButton()
        btn.setIcon(icon)
        btn.setIconSize(QSize(16, 16))
        btn.setFixedSize(24, 24)

        if tooltip:
            btn.setToolTip(tooltip)

        btn.clicked.connect(lambda: self.action_triggered.emit(name))

        # Insert before stretch and customize button
        insert_index = self.main_layout.count() - 2
        self.main_layout.insertWidget(insert_index, btn)

        self._actions[name] = {
            'button': btn,
            'icon': icon,
            'tooltip': tooltip
        }

        return btn

    def removeQuickAction(self, name: str):
        """Remove action from toolbar (renamed to avoid conflict)"""
        if name in self._actions:
            self._actions[name]['button'].deleteLater()
            del self._actions[name]

    def _show_customize_menu(self):
        """Show customization menu"""
        menu = QMenu(self)

        # Add common actions
        save_action = menu.addAction("Add Save")
        save_action.triggered.connect(
            lambda: self._add_common_action("save", "Save"))

        undo_action = menu.addAction("Add Undo")
        undo_action.triggered.connect(
            lambda: self._add_common_action("undo", "Undo"))

        redo_action = menu.addAction("Add Redo")
        redo_action.triggered.connect(
            lambda: self._add_common_action("redo", "Redo"))

        menu.addSeparator()

        # Remove actions
        if self._actions:
            for name, action_info in self._actions.items():
                remove_action = menu.addAction(
                    f"Remove {action_info['tooltip'] or name}")
                remove_action.triggered.connect(
                    lambda _, n=name: self.removeQuickAction(n))

        # Show menu
        button_rect = self.customize_btn.geometry()
        menu_pos = self.mapToGlobal(button_rect.bottomLeft())
        menu.exec(menu_pos)

    def _add_common_action(self, name: str, tooltip: str):
        """Add common action with default icon"""
        # Create a simple colored square as icon
        pixmap = QPixmap(16, 16)
        pixmap.fill(theme_manager.get_color('primary'))
        icon = QIcon(pixmap)

        self.addQuickAction(name, icon, tooltip)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentQuickAccessToolbar {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
            QPushButton {{
                background-color: transparent;
                color: {theme.get_color('text_primary').name()};
                border: 1px solid transparent;
                border-radius: 2px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('border').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
