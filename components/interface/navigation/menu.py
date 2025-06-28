"""
Fluent Design style menu and navigation components
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QFrame, QScrollArea, QMenuBar, QMenu, QStackedWidget)
from PySide6.QtGui import QAction, QActionGroup, QIcon
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QByteArray, QSize
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional, List, Dict, Any, Union


class FluentMenuBar(QMenuBar):
    """Fluent Design style menu bar"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QMenuBar {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
                padding: 4px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 4px;
                margin: 2px;
            }}
            QMenuBar::item:selected {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QMenuBar::item:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def add_fluent_menu(self, title: str, icon: Optional[QIcon] = None) -> 'FluentMenu':
        """Add Fluent menu"""
        menu = FluentMenu(title, self)
        if icon:
            action = self.addMenu(menu)
            action.setIcon(icon)
        else:
            self.addMenu(menu)
        return menu

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentMenu(QMenu):
    """Fluent Design style menu"""

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(title, parent)

        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QMenu {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
            }}
            QMenu::item {{
                background-color: transparent;
                padding: 8px 24px 8px 32px;
                border-radius: 4px;
                margin: 2px;
            }}
            QMenu::item:selected {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QMenu::item:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {theme.get_color('border').name()};
                margin: 4px 8px;
            }}
            QMenu::indicator {{
                width: 16px;
                height: 16px;
            }}
            QMenu::indicator:checked {{
                image: url(:/icons/check.svg);
            }}
            QMenu::right-arrow {{
                width: 12px;
                height: 12px;
                image: url(:/icons/chevron_right.svg);
            }}
        """

        self.setStyleSheet(style_sheet)

    def add_fluent_action(self, text: str, icon: Optional[QIcon] = None,
                          shortcut: Optional[str] = None, checkable: bool = False) -> QAction:
        """Add Fluent menu item"""
        action = QAction(text, self)

        if icon:
            action.setIcon(icon)
        if shortcut:
            action.setShortcut(shortcut)
        if checkable:
            action.setCheckable(True)

        self.addAction(action)
        return action

    def add_fluent_submenu(self, title: str, icon: Optional[QIcon] = None) -> 'FluentMenu':
        """Add Fluent submenu"""
        submenu = FluentMenu(title, self)
        if icon:
            submenu.setIcon(icon)
        self.addMenu(submenu)
        return submenu

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentNavigationView(QWidget):
    """Fluent Design style navigation view"""

    selection_changed = Signal(str, object)  # item_id, item_data

    class NavigationItem:
        def __init__(self, item_id: str, title: str, icon: Optional[QIcon] = None,
                     data: Any = None, children: Optional[List] = None):
            self.item_id = item_id
            self.title = title
            self.icon = icon
            self.data = data
            self.children = children or []
            self.widget: Optional[QPushButton] = None
            self.expanded = False

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items = []
        self._selected_item = None
        self._is_expanded = True
        self._compact_width = 48
        self._expanded_width = 280

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top control bar
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 8, 8, 8)

        # Expand/collapse button
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.clicked.connect(self._toggle_expansion)

        # Title
        self.title_label = QLabel("Navigation")
        self.title_label.setFont(QFont("", 14, QFont.Weight.Bold))

        header_layout.addWidget(self.toggle_btn)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # Navigation items area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.nav_widget = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_widget)
        self.nav_layout.setContentsMargins(4, 4, 4, 4)
        self.nav_layout.setSpacing(2)

        self.scroll_area.setWidget(self.nav_widget)

        layout.addLayout(header_layout)
        layout.addWidget(self.scroll_area)

        # Set initial size
        self.setFixedWidth(self._expanded_width)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentNavigationView {{
                background-color: {theme.get_color('surface').name()};
                border-right: 1px solid {theme.get_color('border').name()};
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                color: {theme.get_color('text_primary').name()};
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def add_item(self, item_id: str, title: str, icon: Optional[QIcon] = None,
                 data: Any = None, parent_id: Optional[str] = None) -> 'NavigationItem':
        """Add navigation item"""
        item = self.NavigationItem(item_id, title, icon, data)

        if parent_id:
            parent_item = self._find_item(parent_id)
            if parent_item:
                parent_item.children.append(item)
                return item

        self._items.append(item)
        self._create_item_widget(item)
        return item

    def add_header(self, title: str) -> QLabel:
        """Add navigation group header"""
        header_label = QLabel(title)
        header_label.setFont(QFont("", 11, QFont.Weight.Bold))
        header_label.setContentsMargins(16, 16, 16, 4)

        theme = theme_manager
        header_label.setStyleSheet(f"""
            QLabel {{
                color: {theme.get_color('text_secondary').name()};
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
        """)

        self.nav_layout.addWidget(header_label)
        return header_label

    def add_separator(self) -> QFrame:
        """Add separator"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        separator.setContentsMargins(12, 8, 12, 8)

        theme = theme_manager
        separator.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.get_color('border').name()};
                border: none;
            }}
        """)

        self.nav_layout.addWidget(separator)
        return separator

    def set_selected_item(self, item_id: str):
        """Set selected item"""
        item = self._find_item(item_id)
        if item and item != self._selected_item:
            # Unselect previous item
            if self._selected_item and self._selected_item.widget:
                self._selected_item.widget.setProperty("selected", False)
                self._selected_item.widget.style().unpolish(self._selected_item.widget)
                self._selected_item.widget.style().polish(self._selected_item.widget)

            # Set new selected item
            self._selected_item = item
            if item.widget:
                item.widget.setProperty("selected", True)
                item.widget.style().unpolish(item.widget)
                item.widget.style().polish(item.widget)

            self.selection_changed.emit(item_id, item.data)

    def _create_item_widget(self, item: 'NavigationItem'):
        """Create navigation item widget"""
        item_widget = QPushButton()
        item_widget.setMinimumHeight(40)
        item_widget.clicked.connect(
            lambda: self.set_selected_item(item.item_id))

        # Set text and icon
        if item.icon and not item.icon.isNull():
            item_widget.setIcon(item.icon)
            icon_size = self.fontMetrics().height()
            item_widget.setIconSize(QSize(icon_size, icon_size))

        item_widget.setText(item.title if self._is_expanded else "")

        # Apply style
        self._apply_item_style(item_widget)

        item.widget = item_widget
        self.nav_layout.addWidget(item_widget)

        # Add child items
        for child in item.children:
            self._create_item_widget(child)

    def _apply_item_style(self, widget: QPushButton):
        """Apply navigation item style"""
        theme = theme_manager

        style = f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                text-align: left;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                margin: 1px 4px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QPushButton[selected="true"] {{
                background-color: {theme.get_color('primary').name()};
                color: white;
                font-weight: 600;
            }}
            QPushButton[selected="true"]:hover {{
                background-color: {theme.get_color('primary').darker(110).name()};
            }}
        """

        widget.setStyleSheet(style)

    def _toggle_expansion(self):
        """Toggle expand/collapse state"""
        self._is_expanded = not self._is_expanded

        # Create expand/collapse animation
        animation = QPropertyAnimation(self, QByteArray(b"maximumWidth"))
        animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        animation.setEasingCurve(FluentAnimation.EASE_OUT)

        if self._is_expanded:
            animation.setStartValue(self._compact_width)
            animation.setEndValue(self._expanded_width)
            self.title_label.setVisible(True)
        else:
            animation.setStartValue(self._expanded_width)
            animation.setEndValue(self._compact_width)
            self.title_label.setVisible(False)

        animation.start()

        # Update navigation items display text
        self._update_items_display()

    def _update_items_display(self):
        """Update navigation items display"""
        for item in self._items:
            if item.widget:
                text = item.title if self._is_expanded else ""
                item.widget.setText(text)

    def _find_item(self, item_id: str) -> Optional['NavigationItem']:
        """Find navigation item"""
        for item in self._items:
            if item.item_id == item_id:
                return item

            # Search in children
            result = self._find_in_children(item.children, item_id)
            if result:
                return result

        return None

    def _find_in_children(self, children: List['NavigationItem'], item_id: str) -> Optional['NavigationItem']:
        """Find in children"""
        for child in children:
            if child.item_id == item_id:
                return child

            result = self._find_in_children(child.children, item_id)
            if result:
                return result

        return None

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()

        # Update all navigation item styles
        for item in self._items:
            if item.widget:
                self._apply_item_style(item.widget)


class FluentBreadcrumb(QWidget):
    """Breadcrumb navigation"""

    item_clicked = Signal(str)  # item_id

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items = []
        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(4)

        # Add stretch space
        self._layout.addStretch()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentBreadcrumb {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
                min-height: 32px;
            }}
        """

        self.setStyleSheet(style_sheet)

    def set_path(self, path_items: List[Dict[str, str]]):
        """Set path

        Args:
            path_items: [{"id": "home", "title": "Home"}, {"id": "docs", "title": "Docs"}]
        """
        # Clear existing items
        while self._layout.count() > 1:  # Keep the last stretch space
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self._items = path_items

        for i, item in enumerate(path_items):
            # Add separator (except for first item)
            if i > 0:
                separator = QLabel("›")
                separator.setStyleSheet(f"""
                    QLabel {{
                        color: {theme_manager.get_color('text_secondary').name()};
                        font-size: 14px;
                        margin: 0 4px;
                    }}
                """)
                self._layout.insertWidget(self._layout.count() - 1, separator)

            # Add item button
            if i == len(path_items) - 1:
                # Last item displayed as label
                item_label = QLabel(item["title"])
                item_label.setStyleSheet(f"""
                    QLabel {{
                        color: {theme_manager.get_color('text_primary').name()};
                        font-size: 14px;
                        font-weight: 600;
                        padding: 4px 8px;
                    }}
                """)
                self._layout.insertWidget(self._layout.count() - 1, item_label)
            else:
                # Other items displayed as clickable buttons
                item_btn = QPushButton(item["title"])
                item_btn.clicked.connect(lambda _, item_id=item["id"]:
                                         self.item_clicked.emit(item_id))

                item_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: none;
                        color: {theme_manager.get_color('text_secondary').name()};
                        font-size: 14px;
                        padding: 4px 8px;
                        border-radius: 4px;
                    }}
                    QPushButton:hover {{
                        background-color: {theme_manager.get_color('accent_light').name()};
                        color: {theme_manager.get_color('text_primary').name()};
                    }}
                """)

                self._layout.insertWidget(self._layout.count() - 1, item_btn)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentTabView(QWidget):
    """Fluent Design tab view"""

    current_changed = Signal(int)
    tab_close_requested = Signal(int)

    class TabButton(QPushButton):
        def __init__(self, text: str, closable: bool = False):
            super().__init__(text)
            self.closable = closable
            self._close_btn = None

            if closable:
                self._setup_close_button()

        def _setup_close_button(self):
            """Setup close button"""
            self._close_btn = QPushButton("×")
            self._close_btn.setParent(self)
            self._close_btn.setFixedSize(16, 16)
            self._close_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 0, 0, 0.2);
                }
            """)

        def resizeEvent(self, event):
            super().resizeEvent(event)
            if self._close_btn:
                self._close_btn.move(self.width() - 20, 4)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._tabs = []
        self._current_index = -1

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab bar
        self.tab_bar = QWidget()
        self.tab_bar.setFixedHeight(40)

        self.tab_layout = QHBoxLayout(self.tab_bar)
        self.tab_layout.setContentsMargins(8, 4, 8, 0)
        self.tab_layout.setSpacing(2)

        # Add tab button
        self.add_tab_btn = QPushButton("+")
        self.add_tab_btn.setFixedSize(32, 32)
        self.add_tab_btn.clicked.connect(self._on_add_tab_clicked)

        self.tab_layout.addWidget(self.add_tab_btn)
        self.tab_layout.addStretch()

        # Content area
        self.content_stack = QStackedWidget()

        layout.addWidget(self.tab_bar)
        layout.addWidget(self.content_stack)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentTabView > QWidget {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 14px;
                color: {theme.get_color('text_secondary').name()};
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                color: {theme.get_color('text_primary').name()};
            }}
            QPushButton[selected="true"] {{
                background-color: {theme.get_color('primary').name()};
                color: white;
                border-color: {theme.get_color('primary').name()};
            }}
            QStackedWidget {{
                background-color: {theme.get_color('background').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-top: none;
            }}
        """

        self.setStyleSheet(style_sheet)

    def add_tab(self, title: str, widget: QWidget, closable: bool = True) -> int:
        """Add tab"""
        tab_button = self.TabButton(title, closable)
        tab_button.clicked.connect(
            lambda: self.set_current_index(len(self._tabs)))

        if closable and tab_button._close_btn:
            tab_button._close_btn.clicked.connect(
                lambda: self.close_tab(len(self._tabs))
            )

        # Apply style
        self._apply_tab_style(tab_button)

        self._tabs.append({
            'title': title,
            'widget': widget,
            'button': tab_button,
            'closable': closable
        })

        # Insert before add button
        self.tab_layout.insertWidget(self.tab_layout.count() - 2, tab_button)
        self.content_stack.addWidget(widget)

        # Auto select first tab
        if len(self._tabs) == 1:
            self.set_current_index(0)

        return len(self._tabs) - 1

    def close_tab(self, index: int):
        """Close tab"""
        if 0 <= index < len(self._tabs):
            tab_info = self._tabs[index]

            # Emit close request signal
            self.tab_close_requested.emit(index)

            # Remove tab
            self.tab_layout.removeWidget(tab_info['button'])
            tab_info['button'].deleteLater()

            self.content_stack.removeWidget(tab_info['widget'])

            del self._tabs[index]

            # Update current selection
            if index == self._current_index:
                if index < len(self._tabs):
                    self.set_current_index(index)
                elif len(self._tabs) > 0:
                    self.set_current_index(len(self._tabs) - 1)
                else:
                    self._current_index = -1
            elif index < self._current_index:
                self._current_index -= 1

    def set_current_index(self, index: int):
        """Set current tab"""
        if 0 <= index < len(self._tabs) and index != self._current_index:
            # Update previous tab button state
            if self._current_index >= 0:
                prev_button = self._tabs[self._current_index]['button']
                prev_button.setProperty("selected", False)
                prev_button.style().unpolish(prev_button)
                prev_button.style().polish(prev_button)

            # Update current tab button state
            current_button = self._tabs[index]['button']
            current_button.setProperty("selected", True)
            current_button.style().unpolish(current_button)
            current_button.style().polish(current_button)

            # Switch content
            self.content_stack.setCurrentWidget(self._tabs[index]['widget'])
            self._current_index = index

            self.current_changed.emit(index)

    def _apply_tab_style(self, _):
        """Apply tab button style"""
        # Style is defined in _setup_style
        pass

    def _on_add_tab_clicked(self):
        """Add tab button clicked"""
        # Can emit signal for external handling of new tab addition
        pass

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
