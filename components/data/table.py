"""
Fluent Design Style Table and List Components
Enhanced with improved animations and consistent styling patterns
"""

from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
                               QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout,
                               QHBoxLayout, QAbstractItemView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from core.theme import theme_manager
from core.enhanced_animations import (FluentMicroInteraction, FluentTransition, 
                                     FluentStateTransition, FluentRevealEffect)
from ..basic.button import FluentButton
from ..basic.textbox import FluentLineEdit
from typing import Optional, List, Any


class FluentTableWidget(QTableWidget):
    """Fluent Design Style Table with enhanced animations"""

    def __init__(self, rows: int = 0, columns: int = 0, parent: Optional[QWidget] = None):
        super().__init__(rows, columns, parent)

        self._state_transition = FluentStateTransition(self)
        self._is_hovered = False
        
        self._setup_enhanced_animations()
        self._setup_style()
        self._setup_behavior()

        theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Add reveal animation when created
        FluentRevealEffect.reveal_fade(self, 400)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation effects"""
        # Setup state transitions for table widget
        self._state_transition.addState("normal", {
            "minimumHeight": 200,
        })
        
        self._state_transition.addState("hovered", {
            "minimumHeight": 202,
        }, duration=150, easing=FluentTransition.EASE_SMOOTH)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QTableWidget {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                gridline-color: {theme.get_color('border').name()};
                selection-background-color: {theme.get_color('accent_light').name()};
                selection-color: {theme.get_color('text_primary').name()};
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
            }}
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {theme.get_color('primary').name()}40;
                color: {theme.get_color('text_primary').name()};
            }}
            QTableWidget::item:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QHeaderView::section {{
                background-color: {theme.get_color('surface').name()};
                border: none;
                border-bottom: 2px solid {theme.get_color('primary').name()};
                border-right: 1px solid {theme.get_color('border').name()};
                padding: 8px;
                font-weight: 600;
                color: {theme.get_color('text_primary').name()};
            }}
            QHeaderView::section:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {theme.get_color('background').name()};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme.get_color('border').name()};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme.get_color('text_secondary').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_behavior(self):
        """Setup behavior"""
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(True)

    def add_data_row(self, data: List[str]):
        """**Add data row**"""
        row = self.rowCount()
        self.insertRow(row)

        for col, text in enumerate(data):
            if col < self.columnCount():
                item = QTableWidgetItem(str(text))
                self.setItem(row, col, item)

    def set_headers(self, headers: List[str]):
        """**Set headers**"""
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    def clear_data(self):
        """**Clear data**"""
        self.setRowCount(0)

    def _on_theme_changed(self, theme_name: str):
        """Theme change handler"""
        # Suppress unused parameter warning
        _ = theme_name
        self._setup_style()


class FluentListWidget(QListWidget):
    """**Fluent Design Style List**"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._setup_style()
        self._setup_behavior()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QListWidget {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px;
                border: none;
                border-radius: 4px;
                margin: 2px;
            }}
            QListWidget::item:selected {{
                background-color: {theme.get_color('primary').name()};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_behavior(self):
        """Setup behavior"""
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSpacing(2)

    def add_item_with_icon(self, text: str, icon: Optional[QIcon] = None, data: Any = None):
        """**Add item with icon**"""
        item = QListWidgetItem(text)
        if icon:
            item.setIcon(icon)
        if data:
            item.setData(Qt.ItemDataRole.UserRole, data)

        self.addItem(item)
        return item

    def _on_theme_changed(self, theme_name: str):
        """Theme change handler"""
        # Suppress unused parameter warning
        _ = theme_name
        self._setup_style()


class FluentTreeWidget(QTreeWidget):
    """**Fluent Design Style Tree Widget**"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._setup_style()
        self._setup_behavior()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QTreeWidget {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                outline: none;
            }}
            QTreeWidget::item {{
                padding: 6px;
                border: none;
                border-radius: 4px;
                margin: 1px;
            }}
            QTreeWidget::item:selected {{
                background-color: {theme.get_color('primary').name()};
                color: white;
            }}
            QTreeWidget::item:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                image: url(:/icons/chevron_right.svg);
            }}
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                image: url(:/icons/chevron_down.svg);
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_behavior(self):
        """Setup behavior"""
        self.setIndentation(20)
        self.setRootIsDecorated(True)
        self.setAnimated(True)
        self.header().setVisible(False)

    def add_tree_item(self, text: str, parent: Optional[QTreeWidgetItem] = None,
                      icon: Optional[QIcon] = None, data: Any = None) -> QTreeWidgetItem:
        """**Add tree item**"""
        item = QTreeWidgetItem([text])

        if icon:
            item.setIcon(0, icon)
        if data:
            item.setData(0, Qt.ItemDataRole.UserRole, data)

        if parent:
            parent.addChild(item)
        else:
            self.addTopLevelItem(item)

        return item

    def _on_theme_changed(self, theme_name: str):
        """Theme change handler"""
        # Suppress unused parameter warning
        _ = theme_name
        self._setup_style()


class FluentDataGrid(QWidget):
    """**Advanced Data Grid**"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._data = []
        self._headers = []
        self._filtered_data = []
        self._sort_column = -1
        self._sort_order = Qt.SortOrder.AscendingOrder

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Toolbar
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 8, 8, 8)

        # Search box
        self.search_box = FluentLineEdit(placeholder="Search...")
        self.search_box.textChanged.connect(self._filter_data)
        self.search_box.setMaximumWidth(300)

        # Action buttons
        self.add_btn = FluentButton("Add")
        self.edit_btn = FluentButton(
            "Edit", style=FluentButton.ButtonStyle.SECONDARY)
        self.delete_btn = FluentButton(
            "Delete", style=FluentButton.ButtonStyle.SECONDARY)

        toolbar_layout.addWidget(self.search_box)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.add_btn)
        toolbar_layout.addWidget(self.edit_btn)
        toolbar_layout.addWidget(self.delete_btn)

        # Table
        self.table = FluentTableWidget()

        layout.addWidget(toolbar)
        layout.addWidget(self.table)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentDataGrid {{
                background-color: {theme.get_color('background').name()};
            }}
            QWidget {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                padding: 4px;
            }}
        """

        self.setStyleSheet(style_sheet)

    def set_data(self, headers: List[str], data: List[List[str]]):
        """**Set data**"""
        self._headers = headers
        self._data = data
        self._filtered_data = data.copy()

        self.table.set_headers(headers)
        self._update_table()

    def _update_table(self):
        """Update table display"""
        self.table.clear_data()

        for row_data in self._filtered_data:
            self.table.add_data_row(row_data)

    def _filter_data(self, text: str):
        """Filter data"""
        if not text:
            self._filtered_data = self._data.copy()
        else:
            self._filtered_data = []
            for row in self._data:
                if any(text.lower() in str(cell).lower() for cell in row):
                    self._filtered_data.append(row)

        self._update_table()

    def _on_theme_changed(self, theme_name: str):
        """Theme change handler"""
        # Suppress unused parameter warning
        _ = theme_name
        self._setup_style()
