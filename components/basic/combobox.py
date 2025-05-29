"""
Fluent Design style dropdown components
"""

from PySide6.QtWidgets import (QComboBox, QWidget, QVBoxLayout, QHBoxLayout,
                               QListWidget, QListWidgetItem, QPushButton,
                               QScrollArea, QLineEdit)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QRect, QByteArray
from PySide6.QtGui import QIcon
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                      FluentRevealEffect, FluentSequence)
from typing import Optional, List, Any


class FluentSearchBox(QLineEdit):
    """Search box component for internal use"""

    text_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.textChanged.connect(self.text_changed.emit)

    def set_text(self, text: str):
        """Set text content"""
        self.setText(text)


class FluentComboBox(QComboBox):
    """Fluent Design style combo box with enhanced animations"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._drop_animation = None
        self._is_expanded = False

        self.setMinimumHeight(32)

        self._setup_style()
        self._setup_animations()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style with enhanced visual effects"""
        theme = theme_manager

        style_sheet = f"""
            QComboBox {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()};
                transition: all 0.2s ease;
            }}
            QComboBox:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
            QComboBox:focus {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
                padding: 7px 11px;
                background-color: {theme.get_color('surface').name()};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 32px;
                background: transparent;
                border-radius: 3px;
            }}
            QComboBox::drop-down:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QComboBox::down-arrow {{
                image: url(:/icons/chevron_down.svg);
                width: 14px;
                height: 14px;
            }}
            QComboBox::down-arrow:hover {{
                image: url(:/icons/chevron_down_hover.svg);
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                selection-background-color: {theme.get_color('accent_light').name()};
                selection-color: {theme.get_color('text_primary').name()};
                padding: 6px;
                outline: none;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
            }}
            QComboBox QAbstractItemView::item {{
                padding: 10px 14px;
                border-radius: 6px;
                margin: 2px;
                border: none;
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
        """Setup enhanced animations"""
        self._drop_animation = QPropertyAnimation(
            self.view(), QByteArray(b"geometry"))
        self._drop_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._drop_animation.setEasingCurve(FluentTransition.EASE_SPRING)

    def showPopup(self):
        """Show dropdown list with enhanced animation"""
        self._is_expanded = True
        super().showPopup()

        # Enhanced dropdown animation with bounce effect
        if self._drop_animation and self.view():
            view_rect = self.view().geometry()
            start_rect = QRect(view_rect.x(), view_rect.y() -
                               30, view_rect.width(), 10)

            self._drop_animation.setStartValue(start_rect)
            self._drop_animation.setEndValue(view_rect)
            self._drop_animation.start()

            # Add fade in effect
            FluentRevealEffect.fade_in(self.view(), 200)

    def hidePopup(self):
        """Hide dropdown list with animation"""
        self._is_expanded = False

        # Add fade out animation before hiding
        if self.view():
            fade_sequence = FluentSequence(self)
            fade_sequence.addCallback(
                lambda: FluentRevealEffect.fade_in(self.view(), 150))
            fade_sequence.addPause(150)
            fade_sequence.addCallback(lambda: super(
                FluentComboBox, self).hidePopup())
            fade_sequence.start()
        else:
            super().hidePopup()

    def enterEvent(self, event):
        """Handle mouse enter with micro-interaction"""
        FluentMicroInteraction.pulse_animation(self, 1.02)
        super().enterEvent(event)

    def _on_theme_changed(self):
        """Handle theme change with transition"""
        self._setup_style()
        FluentMicroInteraction.pulse_animation(self, 1.01)


class FluentMultiSelectComboBox(QWidget):
    """Multi-select combo box with enhanced animations"""

    selection_changed = Signal(list)  # List of selected items

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items = []
        self._selected_items = []
        self._is_expanded = False
        self._dropdown_widget = None

        self._setup_ui()
        self._setup_style()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI with enhanced components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Enhanced main button
        self.main_button = QPushButton("Please select items")
        self.main_button.setMinimumHeight(36)
        self.main_button.clicked.connect(self._toggle_dropdown)

        layout.addWidget(self.main_button)

        # Add entrance animation
        FluentRevealEffect.scale_in(self.main_button, 250)

    def _setup_style(self):
        """Setup enhanced style"""
        theme = theme_manager

        style_sheet = f"""
            QPushButton {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                text-align: left;
                transition: all 0.2s ease;
            }}
            QPushButton:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
                transform: scale(0.98);
            }}
        """

        self.main_button.setStyleSheet(style_sheet)

    def add_item(self, text: str, data: Any = None):
        """Add item with animation"""
        item = {
            'text': text,
            'data': data,
            'selected': False
        }
        self._items.append(item)
        self._update_display()

        # Add micro-interaction feedback
        FluentMicroInteraction.pulse_animation(self.main_button, 1.01)

    def add_items(self, items: List[str]):
        """Add multiple items with staggered animation"""
        for i, item_text in enumerate(items):
            # Add delay for staggered effect
            from PySide6.QtCore import QTimer
            QTimer.singleShot(
                i * 50, lambda text=item_text: self.add_item(text))

    def get_selected_items(self) -> List[str]:
        """Get selected items"""
        return [item['text'] for item in self._items if item['selected']]

    def get_selected_data(self) -> List[Any]:
        """Get selected item data"""
        return [item['data'] for item in self._items if item['selected']]

    def set_selected_items(self, selected_texts: List[str]):
        """Set selected items with animation"""
        for item in self._items:
            item['selected'] = item['text'] in selected_texts

        self._selected_items = selected_texts
        self._update_display()
        self.selection_changed.emit(self._selected_items)

        # Add feedback animation
        FluentMicroInteraction.pulse_animation(self.main_button, 1.02)

    def clear_selection(self):
        """Clear selection with animation"""
        for item in self._items:
            item['selected'] = False

        self._selected_items = []
        self._update_display()
        self.selection_changed.emit(self._selected_items)

        # Add shake animation for feedback
        FluentMicroInteraction.shake_animation(self.main_button, 3)

    def _toggle_dropdown(self):
        """Toggle dropdown state with enhanced animation"""
        # Add button press feedback
        FluentMicroInteraction.button_press(self.main_button, 0.96)

        if self._is_expanded:
            self._hide_dropdown()
        else:
            self._show_dropdown()

    def _show_dropdown(self):
        """Show dropdown list with enhanced animations"""
        if self._dropdown_widget:
            self._dropdown_widget.close()

        self._dropdown_widget = self._create_dropdown_widget()
        self._dropdown_widget.show()

        self._is_expanded = True

        # Enhanced show animation sequence
        show_sequence = FluentSequence(self)
        show_sequence.addCallback(
            lambda: FluentRevealEffect.scale_in(self._dropdown_widget, 200) if self._dropdown_widget else None)
        show_sequence.addPause(50)
        show_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self._dropdown_widget, 150) if self._dropdown_widget else None)
        show_sequence.start()

    def _hide_dropdown(self):
        """Hide dropdown list with enhanced animation"""
        if self._dropdown_widget:
            hide_sequence = FluentSequence(self)
            hide_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self._dropdown_widget, 0.9) if self._dropdown_widget else None)
            hide_sequence.addPause(150)
            hide_sequence.addCallback(
                lambda: self._dropdown_widget.close() if self._dropdown_widget else None)
            hide_sequence.start()

        self._is_expanded = False

    def _create_dropdown_widget(self) -> QWidget:
        """Create enhanced dropdown widget"""
        dropdown = QWidget(self, Qt.WindowType.Popup)
        dropdown.setFixedWidth(self.width())
        dropdown.setMaximumHeight(250)

        # Calculate position
        global_pos = self.mapToGlobal(self.rect().bottomLeft())
        dropdown.move(global_pos)

        layout = QVBoxLayout(dropdown)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Enhanced styling
        theme = theme_manager
        dropdown.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
            }}
        """)

        # Create enhanced scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)

        # Add enhanced checkbox options
        from .checkbox import FluentCheckBox

        for i, item in enumerate(self._items):
            checkbox = FluentCheckBox(item['text'])
            checkbox.setChecked(item['selected'])
            checkbox.stateChanged.connect(
                lambda state, idx=i: self._on_item_toggled(idx, state))

            content_layout.addWidget(checkbox)

            # Add staggered entrance animation
            from PySide6.QtCore import QTimer
            QTimer.singleShot(
                i * 30, lambda cb=checkbox: FluentRevealEffect.slide_in(cb, 150, "up"))

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        # Enhanced bottom action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)

        clear_all_btn = QPushButton("Clear")
        clear_all_btn.clicked.connect(self.clear_selection)

        done_btn = QPushButton("Done")
        done_btn.clicked.connect(self._hide_dropdown)

        # Style action buttons
        for btn in [select_all_btn, clear_all_btn, done_btn]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme.get_color('accent_light').name()};
                    border: 1px solid {theme.get_color('border').name()};
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {theme.get_color('primary').name()};
                    color: white;
                }}
            """)

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(clear_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(done_btn)

        layout.addLayout(button_layout)

        return dropdown

    def _on_item_toggled(self, index: int, state: int):
        """Handle item toggle with animation"""
        if 0 <= index < len(self._items):
            self._items[index]['selected'] = (
                state == Qt.CheckState.Checked.value)
            self._selected_items = self.get_selected_items()
            self._update_display()
            self.selection_changed.emit(self._selected_items)

            # Add micro-feedback
            FluentMicroInteraction.pulse_animation(self.main_button, 1.01)

    def _select_all(self):
        """Select all items with enhanced feedback"""
        for item in self._items:
            item['selected'] = True

        self._selected_items = self.get_selected_items()
        self._update_display()
        self.selection_changed.emit(self._selected_items)

        # Enhanced feedback animation
        FluentMicroInteraction.pulse_animation(self.main_button, 1.05)

        # Recreate dropdown list to update checkbox states
        if self._dropdown_widget:
            self._dropdown_widget.close()
            self._show_dropdown()

    def _update_display(self):
        """Update display text with transition"""
        selected_count = len(self._selected_items)

        if selected_count == 0:
            new_text = "Please select items"
        elif selected_count == 1:
            new_text = self._selected_items[0]
        else:
            new_text = f"Selected {selected_count} items"

        # Animate text change
        if self.main_button.text() != new_text:
            self.main_button.setText(new_text)
            FluentMicroInteraction.pulse_animation(self.main_button, 1.01)

    def _on_theme_changed(self):
        """Handle theme change with transition"""
        self._setup_style()
        FluentMicroInteraction.pulse_animation(self, 1.02)


class FluentSearchableComboBox(QWidget):
    """Searchable combo box with enhanced search capabilities"""

    item_selected = Signal(str, object)  # text, data

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items = []
        self._filtered_items = []
        self._selected_item = None
        self._is_expanded = False

        self._setup_ui()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup enhanced UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Enhanced search input box
        self.search_box = FluentSearchBox()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.text_changed.connect(self._on_search_text_changed)
        self.search_box.returnPressed.connect(self._select_first_item)

        # Enhanced dropdown list
        self.list_widget = QListWidget()
        self.list_widget.setMaximumHeight(220)
        self.list_widget.setVisible(False)

        self.list_widget.itemClicked.connect(self._on_item_clicked)

        layout.addWidget(self.search_box)
        layout.addWidget(self.list_widget)

        self._setup_list_style()

        # Add entrance animations
        FluentRevealEffect.scale_in(self.search_box, 200)

    def _setup_list_style(self):
        """Setup enhanced list style"""
        theme = theme_manager

        style_sheet = f"""
            QListWidget {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                outline: none;
                padding: 6px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            }}
            QListWidget::item {{
                padding: 10px 14px;
                border-radius: 6px;
                margin: 2px;
                color: {theme.get_color('text_primary').name()};
                border: none;
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
        """Add item with animation feedback"""
        item = {
            'text': text,
            'data': data
        }
        self._items.append(item)
        self._update_filtered_items()

        # Add micro-feedback
        FluentMicroInteraction.pulse_animation(self.search_box, 1.01)

    def add_items(self, items: List[str]):
        """Add multiple items with enhanced feedback"""
        for item_text in items:
            self.add_item(item_text)

        # Add completion feedback
        FluentMicroInteraction.pulse_animation(self.search_box, 1.02)

    def clear_items(self):
        """Clear items with animation"""
        self._items.clear()
        self._filtered_items.clear()
        self.list_widget.clear()

        # Add clearing animation
        FluentMicroInteraction.shake_animation(self.search_box, 3)

    def set_selected_text(self, text: str):
        """Set selected text with animation"""
        self.search_box.set_text(text)
        self._selected_item = next(
            (item for item in self._items if item['text'] == text), None)

        # Add selection feedback
        FluentMicroInteraction.pulse_animation(self.search_box, 1.02)

    def get_selected_item(self) -> Optional[dict]:
        """Get selected item"""
        return self._selected_item

    def _on_search_text_changed(self, text: str):
        """Handle search text change with enhanced animations"""
        self._update_filtered_items(text)

        # Enhanced show/hide with animations
        if text and self._filtered_items:
            if not self.list_widget.isVisible():
                self.list_widget.setVisible(True)
                FluentRevealEffect.slide_in(self.list_widget, 200, "up")
            self._is_expanded = True
        else:
            if self.list_widget.isVisible():
                hide_sequence = FluentSequence(self)
                hide_sequence.addCallback(
                    lambda: FluentMicroInteraction.scale_animation(self.list_widget, 0.95))
                hide_sequence.addPause(150)
                hide_sequence.addCallback(
                    lambda: self.list_widget.setVisible(False))
                hide_sequence.start()
            self._is_expanded = False

    def _update_filtered_items(self, filter_text: str = ""):
        """Update filtered items with enhanced visualization"""
        self.list_widget.clear()
        self._filtered_items.clear()

        for item in self._items:
            if not filter_text or filter_text.lower() in item['text'].lower():
                self._filtered_items.append(item)

                list_item = QListWidgetItem(item['text'])
                list_item.setData(Qt.ItemDataRole.UserRole, item)
                self.list_widget.addItem(list_item)

        # Add staggered item appearance
        for i in range(self.list_widget.count()):
            item_widget = self.list_widget.itemWidget(self.list_widget.item(i))
            if item_widget:
                from PySide6.QtCore import QTimer
                QTimer.singleShot(
                    i * 20, lambda w=item_widget: FluentRevealEffect.slide_in(w, 100, "left"))

    def _on_item_clicked(self, list_item: QListWidgetItem):
        """Handle item click with enhanced feedback"""
        item = list_item.data(Qt.ItemDataRole.UserRole)
        self._selected_item = item

        self.search_box.set_text(item['text'])

        # Enhanced hide animation
        hide_sequence = FluentSequence(self)
        hide_sequence.addCallback(
            lambda: FluentMicroInteraction.scale_animation(self.list_widget, 0.9))
        hide_sequence.addPause(100)
        hide_sequence.addCallback(lambda: self.list_widget.setVisible(False))
        hide_sequence.start()

        self._is_expanded = False

        # Add selection feedback
        FluentMicroInteraction.pulse_animation(self.search_box, 1.03)

        self.item_selected.emit(item['text'], item['data'])

    def _select_first_item(self):
        """Select first item with enhanced feedback"""
        if self._filtered_items:
            first_item = self._filtered_items[0]
            self._selected_item = first_item

            self.search_box.set_text(first_item['text'])

            # Enhanced hide with feedback
            hide_sequence = FluentSequence(self)
            hide_sequence.addCallback(
                lambda: FluentMicroInteraction.pulse_animation(self.search_box, 1.05))
            hide_sequence.addPause(100)
            hide_sequence.addCallback(
                lambda: self.list_widget.setVisible(False))
            hide_sequence.start()

            self._is_expanded = False

            self.item_selected.emit(first_item['text'], first_item['data'])

    def _on_theme_changed(self):
        """Handle theme change with transition"""
        self._setup_list_style()
        FluentMicroInteraction.pulse_animation(self, 1.02)


class FluentDropDownButton(QPushButton):
    """Enhanced dropdown button with modern animations"""

    item_clicked = Signal(str, object)  # text, data

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self._menu_items = []
        self._dropdown_widget = None
        self._is_expanded = False
        self._original_text = text

        self.clicked.connect(self._toggle_dropdown)

        self._setup_style()
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

        # Add entrance animation
        FluentRevealEffect.scale_in(self, 250)

    def _setup_style(self):
        """Setup enhanced style"""
        theme = theme_manager

        style_sheet = f"""
            QPushButton {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 10px 18px 10px 14px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                text-align: left;
                transition: all 0.2s ease;
            }}
            QPushButton:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
                transform: scale(0.98);
            }}
        """

        self.setStyleSheet(style_sheet)

        # Add enhanced dropdown arrow
        self.setText(f"{self._original_text} ▼")

    def add_menu_item(self, text: str, data: Any = None, icon: Optional[QIcon] = None):
        """Add menu item with feedback"""
        item = {
            'text': text,
            'data': data,
            'icon': icon
        }
        self._menu_items.append(item)

        # Add micro-feedback
        FluentMicroInteraction.pulse_animation(self, 1.01)

    def clear_menu_items(self):
        """Clear menu items with animation"""
        self._menu_items.clear()
        FluentMicroInteraction.shake_animation(self, 3)

    def _toggle_dropdown(self):
        """Toggle dropdown menu with enhanced animations"""
        # Enhanced button press feedback
        FluentMicroInteraction.button_press(self, 0.96)

        if self._is_expanded:
            self._hide_dropdown()
        else:
            self._show_dropdown()

    def _show_dropdown(self):
        """Show dropdown menu with enhanced animation"""
        if not self._menu_items:
            FluentMicroInteraction.shake_animation(self, 2)
            return

        if self._dropdown_widget:
            self._dropdown_widget.close()

        self._dropdown_widget = self._create_dropdown_menu()
        self._dropdown_widget.show()

        self._is_expanded = True

        # Enhanced show animation
        show_sequence = FluentSequence(self)
        show_sequence.addCallback(
            lambda: FluentRevealEffect.scale_in(self._dropdown_widget, 200) if self._dropdown_widget else None)
        show_sequence.addPause(50)
        show_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self._dropdown_widget, 150) if self._dropdown_widget else None)
        show_sequence.start()

    def _hide_dropdown(self):
        """Hide dropdown menu with enhanced animation"""
        if self._dropdown_widget:
            hide_sequence = FluentSequence(self)
            hide_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self._dropdown_widget, 0.9) if self._dropdown_widget else None)
            hide_sequence.addPause(150)
            hide_sequence.addCallback(
                lambda: self._dropdown_widget.close() if self._dropdown_widget else None)
            hide_sequence.start()

        self._is_expanded = False

    def _create_dropdown_menu(self) -> QWidget:
        """Create enhanced dropdown menu"""
        menu = QWidget(None, Qt.WindowType.Popup)
        menu.setMinimumWidth(self.width())

        # Calculate position
        global_pos = self.mapToGlobal(self.rect().bottomLeft())
        menu.move(global_pos)

        layout = QVBoxLayout(menu)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Enhanced styling
        theme = theme_manager
        menu.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
            }}
        """)

        # Create enhanced menu items
        for i, item in enumerate(self._menu_items):
            menu_item_btn = QPushButton(item['text'])
            if item['icon']:
                menu_item_btn.setIcon(item['icon'])

            menu_item_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 14px;
                    text-align: left;
                    color: {theme.get_color('text_primary').name()};
                    transition: all 0.15s ease;
                }}
                QPushButton:hover {{
                    background-color: {theme.get_color('accent_light').name()};
                }}
                QPushButton:pressed {{
                    background-color: {theme.get_color('accent_medium').name()};
                    transform: scale(0.98);
                }}
            """)

            menu_item_btn.clicked.connect(
                lambda item=item: self._on_menu_item_clicked(item)
            )

            layout.addWidget(menu_item_btn)

            # Add staggered entrance animation
            from PySide6.QtCore import QTimer
            QTimer.singleShot(
                i * 30, lambda btn=menu_item_btn: FluentRevealEffect.slide_in(btn, 150, "up"))

        return menu

    def _on_menu_item_clicked(self, item: dict):
        """Handle menu item click with enhanced feedback"""
        # Add click feedback
        hide_sequence = FluentSequence(self)
        hide_sequence.addCallback(
            lambda: FluentMicroInteraction.pulse_animation(self, 1.05))
        hide_sequence.addPause(100)
        hide_sequence.addCallback(lambda: self._hide_dropdown())
        hide_sequence.start()

        self.item_clicked.emit(item['text'], item['data'])

    def enterEvent(self, event):
        """Handle mouse enter with micro-interaction"""
        FluentMicroInteraction.hover_glow(self, 0.1)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave"""
        FluentMicroInteraction.hover_glow(self, -0.1)
        super().leaveEvent(event)

    def _on_theme_changed(self):
        """Handle theme change with transition"""
        self._setup_style()
        FluentMicroInteraction.pulse_animation(self, 1.02)
