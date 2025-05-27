"""
Fluent Design style dropdown components
"""

from PySide6.QtWidgets import (QComboBox, QWidget, QVBoxLayout, QHBoxLayout,
                               QListWidget, QListWidgetItem, QPushButton,
                               QScrollArea)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QRect, QByteArray
from PySide6.QtGui import QIcon
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional, List, Any


class FluentComboBox(QComboBox):
    """Fluent Design style combo box"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._drop_animation = None
        self._is_expanded = False

        self.setMinimumHeight(32)

        self._setup_style()
        self._setup_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QComboBox {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()};
            }}
            QComboBox:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
            }}
            QComboBox:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
                padding: 5px 11px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 32px;
                background: transparent;
            }}
            QComboBox::down-arrow {{
                image: url(:/icons/chevron_down.svg);
                width: 12px;
                height: 12px;
            }}
            QComboBox::down-arrow:hover {{
                image: url(:/icons/chevron_down_hover.svg);
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
                selection-background-color: {theme.get_color('accent_light').name()};
                selection-color: {theme.get_color('text_primary').name()};
                padding: 4px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-radius: 4px;
                margin: 1px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {theme.get_color('primary').name()};
                color: white;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup animations"""
        self._drop_animation = QPropertyAnimation(
            self.view(), QByteArray(b"geometry"))
        self._drop_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._drop_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def showPopup(self):
        """Show dropdown list"""
        self._is_expanded = True
        super().showPopup()

        # Add dropdown animation
        if self._drop_animation and self.view():
            view_rect = self.view().geometry()
            start_rect = QRect(view_rect.x(), view_rect.y() -
                               20, view_rect.width(), 0)

            self._drop_animation.setStartValue(start_rect)
            self._drop_animation.setEndValue(view_rect)
            self._drop_animation.start()

    def hidePopup(self):
        """Hide dropdown list"""
        self._is_expanded = False
        super().hidePopup()

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._setup_style()


class FluentMultiSelectComboBox(QWidget):
    """Multi-select combo box"""

    selection_changed = Signal(list)  # List of selected items

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items = []
        self._selected_items = []
        self._is_expanded = False
        self._dropdown_widget = None

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main button
        self.main_button = QPushButton("Please select items")
        self.main_button.setMinimumHeight(32)
        self.main_button.clicked.connect(self._toggle_dropdown)

        layout.addWidget(self.main_button)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QPushButton {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                text-align: left;
            }}
            QPushButton:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
        """

        self.main_button.setStyleSheet(style_sheet)

    def add_item(self, text: str, data: Any = None):
        """Add item"""
        item = {
            'text': text,
            'data': data,
            'selected': False
        }
        self._items.append(item)
        self._update_display()

    def add_items(self, items: List[str]):
        """Add multiple items"""
        for item_text in items:
            self.add_item(item_text)

    def get_selected_items(self) -> List[str]:
        """Get selected items"""
        return [item['text'] for item in self._items if item['selected']]

    def get_selected_data(self) -> List[Any]:
        """Get selected item data"""
        return [item['data'] for item in self._items if item['selected']]

    def set_selected_items(self, selected_texts: List[str]):
        """Set selected items"""
        for item in self._items:
            item['selected'] = item['text'] in selected_texts

        self._selected_items = selected_texts
        self._update_display()
        self.selection_changed.emit(self._selected_items)

    def clear_selection(self):
        """Clear selection"""
        for item in self._items:
            item['selected'] = False

        self._selected_items = []
        self._update_display()
        self.selection_changed.emit(self._selected_items)

    def _toggle_dropdown(self):
        """Toggle dropdown state"""
        if self._is_expanded:
            self._hide_dropdown()
        else:
            self._show_dropdown()

    def _show_dropdown(self):
        """Show dropdown list"""
        if self._dropdown_widget:
            self._dropdown_widget.close()

        self._dropdown_widget = self._create_dropdown_widget()
        self._dropdown_widget.show()

        self._is_expanded = True

        # Add show animation
        fade_anim = FluentAnimation.fade_in(
            self._dropdown_widget, FluentAnimation.DURATION_FAST)
        fade_anim.start()

    def _hide_dropdown(self):
        """Hide dropdown list"""
        if self._dropdown_widget:
            fade_anim = FluentAnimation.fade_out(
                self._dropdown_widget, FluentAnimation.DURATION_FAST)
            fade_anim.finished.connect(self._dropdown_widget.close)
            fade_anim.start()

        self._is_expanded = False

    def _create_dropdown_widget(self) -> QWidget:
        """Create dropdown widget"""
        dropdown = QWidget(self, Qt.WindowType.Popup)
        dropdown.setFixedWidth(self.width())
        dropdown.setMaximumHeight(200)

        # Calculate position
        global_pos = self.mapToGlobal(self.rect().bottomLeft())
        dropdown.move(global_pos)

        layout = QVBoxLayout(dropdown)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # Apply style
        theme = theme_manager
        dropdown.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
            }}
        """)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(1)

        # Add checkbox options
        from .checkbox import FluentCheckBox

        for i, item in enumerate(self._items):
            checkbox = FluentCheckBox(item['text'])
            checkbox.setChecked(item['selected'])
            checkbox.stateChanged.connect(
                lambda state, idx=i: self._on_item_toggled(idx, state))

            content_layout.addWidget(checkbox)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        # Bottom action buttons
        button_layout = QHBoxLayout()

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)

        clear_all_btn = QPushButton("Clear")
        clear_all_btn.clicked.connect(self.clear_selection)

        done_btn = QPushButton("Done")
        done_btn.clicked.connect(self._hide_dropdown)

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(clear_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(done_btn)

        layout.addLayout(button_layout)

        return dropdown

    def _on_item_toggled(self, index: int, state: int):
        """Handle item toggle"""
        if 0 <= index < len(self._items):
            self._items[index]['selected'] = (
                state == Qt.CheckState.Checked.value)
            self._selected_items = self.get_selected_items()
            self._update_display()
            self.selection_changed.emit(self._selected_items)

    def _select_all(self):
        """Select all items"""
        for item in self._items:
            item['selected'] = True

        self._selected_items = self.get_selected_items()
        self._update_display()
        self.selection_changed.emit(self._selected_items)

        # Recreate dropdown list to update checkbox states
        if self._dropdown_widget:
            self._dropdown_widget.close()
            self._show_dropdown()

    def _update_display(self):
        """Update display text"""
        selected_count = len(self._selected_items)

        if selected_count == 0:
            self.main_button.setText("Please select items")
        elif selected_count == 1:
            self.main_button.setText(self._selected_items[0])
        else:
            self.main_button.setText(f"Selected {selected_count} items")

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._setup_style()


class FluentSearchableComboBox(QWidget):
    """Searchable combo box"""

    item_selected = Signal(str, object)  # text, data

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items = []
        self._filtered_items = []
        self._selected_item = None
        self._is_expanded = False

        self._setup_ui()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Search input box
        from .textbox import FluentSearchBox
        self.search_box = FluentSearchBox()
        self.search_box.text_changed.connect(self._on_search_text_changed)
        self.search_box.line_edit.returnPressed.connect(
            self._select_first_item)

        # Dropdown list
        self.list_widget = QListWidget()
        self.list_widget.setMaximumHeight(200)
        self.list_widget.setVisible(False)

        self.list_widget.itemClicked.connect(self._on_item_clicked)

        layout.addWidget(self.search_box)
        layout.addWidget(self.list_widget)

        self._setup_list_style()

    def _setup_list_style(self):
        """Setup list style"""
        theme = theme_manager

        style_sheet = f"""
            QListWidget {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
                outline: none;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 4px;
                margin: 1px;
                color: {theme.get_color('text_primary').name()};
            }}
            QListWidget::item:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QListWidget::item:selected {{
                background-color: {theme.get_color('primary').name()};
                color: white;
            }}
        """

        self.list_widget.setStyleSheet(style_sheet)

    def add_item(self, text: str, data: Any = None):
        """Add item"""
        item = {
            'text': text,
            'data': data
        }
        self._items.append(item)
        self._update_filtered_items()

    def add_items(self, items: List[str]):
        """Add multiple items"""
        for item_text in items:
            self.add_item(item_text)

    def clear_items(self):
        """Clear items"""
        self._items.clear()
        self._filtered_items.clear()
        self.list_widget.clear()

    def set_selected_text(self, text: str):
        """Set selected text"""
        self.search_box.set_text(text)
        self._selected_item = next(
            (item for item in self._items if item['text'] == text), None)

    def get_selected_item(self) -> Optional[dict]:
        """Get selected item"""
        return self._selected_item

    def _on_search_text_changed(self, text: str):
        """Handle search text change"""
        self._update_filtered_items(text)

        # Show/hide list
        if text and self._filtered_items:
            self.list_widget.setVisible(True)
            self._is_expanded = True
        else:
            self.list_widget.setVisible(False)
            self._is_expanded = False

    def _update_filtered_items(self, filter_text: str = ""):
        """Update filtered items"""
        self.list_widget.clear()
        self._filtered_items.clear()

        for item in self._items:
            if not filter_text or filter_text.lower() in item['text'].lower():
                self._filtered_items.append(item)

                list_item = QListWidgetItem(item['text'])
                list_item.setData(Qt.ItemDataRole.UserRole, item)
                self.list_widget.addItem(list_item)

    def _on_item_clicked(self, list_item: QListWidgetItem):
        """Handle item click"""
        item = list_item.data(Qt.ItemDataRole.UserRole)
        self._selected_item = item

        self.search_box.set_text(item['text'])
        self.list_widget.setVisible(False)
        self._is_expanded = False

        self.item_selected.emit(item['text'], item['data'])

    def _select_first_item(self):
        """Select first item"""
        if self._filtered_items:
            first_item = self._filtered_items[0]
            self._selected_item = first_item

            self.search_box.set_text(first_item['text'])
            self.list_widget.setVisible(False)
            self._is_expanded = False

            self.item_selected.emit(first_item['text'], first_item['data'])

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._setup_list_style()


class FluentDropDownButton(QPushButton):
    """Dropdown button"""

    item_clicked = Signal(str, object)  # text, data

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self._menu_items = []
        self._dropdown_widget = None
        self._is_expanded = False

        self.clicked.connect(self._toggle_dropdown)

        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QPushButton {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 8px 16px 8px 12px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                text-align: left;
            }}
            QPushButton:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

        # Add dropdown arrow
        self.setText(self.text() + " ▼")

    def add_menu_item(self, text: str, data: Any = None, icon: Optional[QIcon] = None):
        """Add menu item"""
        item = {
            'text': text,
            'data': data,
            'icon': icon
        }
        self._menu_items.append(item)

    def clear_menu_items(self):
        """Clear menu items"""
        self._menu_items.clear()

    def _toggle_dropdown(self):
        """Toggle dropdown menu"""
        if self._is_expanded:
            self._hide_dropdown()
        else:
            self._show_dropdown()

    def _show_dropdown(self):
        """Show dropdown menu"""
        if not self._menu_items:
            return

        if self._dropdown_widget:
            self._dropdown_widget.close()

        self._dropdown_widget = self._create_dropdown_menu()
        self._dropdown_widget.show()

        self._is_expanded = True

    def _hide_dropdown(self):
        """Hide dropdown menu"""
        if self._dropdown_widget:
            self._dropdown_widget.close()

        self._is_expanded = False

    def _create_dropdown_menu(self) -> QWidget:
        """Create dropdown menu"""
        menu = QWidget(None, Qt.WindowType.Popup)
        menu.setMinimumWidth(self.width())

        # Calculate position
        global_pos = self.mapToGlobal(self.rect().bottomLeft())
        menu.move(global_pos)

        layout = QVBoxLayout(menu)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # Apply style
        theme = theme_manager
        menu.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
            }}
        """)

        # Create menu items
        for item in self._menu_items:
            menu_item_btn = QPushButton(item['text'])
            if item['icon']:
                menu_item_btn.setIcon(item['icon'])

            menu_item_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 12px;
                    text-align: left;
                    color: {theme.get_color('text_primary').name()};
                }}
                QPushButton:hover {{
                    background-color: {theme.get_color('accent_light').name()};
                }}
                QPushButton:pressed {{
                    background-color: {theme.get_color('accent_medium').name()};
                }}
            """)

            menu_item_btn.clicked.connect(
                lambda _checked, item=item: self._on_menu_item_clicked(item)
            )

            layout.addWidget(menu_item_btn)

        return menu

    def _on_menu_item_clicked(self, item: dict):
        """Handle menu item click"""
        self._hide_dropdown()
        self.item_clicked.emit(item['text'], item['data'])

    def _on_theme_changed(self, _theme_name: str):
        """Handle theme change"""
        self._setup_style()
