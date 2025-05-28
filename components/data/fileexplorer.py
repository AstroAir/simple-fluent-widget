#!/usr/bin/env python3
"""
File Explorer Components for Fluent UI

This module provides modern file explorer components following Fluent Design principles.
Includes FluentFileExplorer, FluentFileTree, FluentFileList, and FluentPathBar components.
"""

import os
# import stat # Unused
# from datetime import datetime # Unused
from typing import Optional, List, Dict, cast # Removed Callable (unused), added cast
from enum import Enum
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QListView, QLabel, QPushButton,
    QLineEdit, QComboBox, QSplitter, QAbstractItemView, QHeaderView, QToolButton,
    QFileSystemModel
    # QStyledItemDelegate, QStyleOptionViewItem, QMenu, QMessageBox # Unused
)
from PySide6.QtCore import (
    Qt, Signal, QModelIndex, QDir, QSortFilterProxyModel, QPersistentModelIndex
    # QFileSystemModel, # Moved to QtWidgets
    # QFileInfo, QSize, QRect, # Unused
    # QThread, pyqtSignal as Signal, QTimer # Unused or incorrect
)
# from PySide6.QtGui import ( # All seem unused in this file's Python code
#     QPainter, QPen, QBrush, QColor, QFont, QIcon, QPixmap, QFontMetrics,
#     QMouseEvent, QKeyEvent, QPalette
# )
from core.theme import theme_manager


class FluentViewMode(Enum):
    """File view mode enumeration"""
    LIST = "list"
    TREE = "tree"
    GRID = "grid"
    DETAILS = "details"


class FluentSortBy(Enum):
    """Sort criteria enumeration"""
    NAME = "name"
    SIZE = "size"
    TYPE = "type"
    DATE_MODIFIED = "date_modified"


class FluentFileExplorer(QWidget):
    """
    Complete file explorer widget with modern UI
    
    Features:
    - Multiple view modes (list, tree, grid, details)
    - Navigation breadcrumbs
    - Search functionality
    - File operations (copy, move, delete)
    - Context menus
    - Keyboard shortcuts
    """
    
    # Signals
    fileSelected = Signal(str)  # File path
    folderChanged = Signal(str)  # Folder path
    fileActivated = Signal(str)  # File path (double-clicked)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._current_path = str(Path.home())
        self._view_mode = FluentViewMode.DETAILS
        self._sort_by = FluentSortBy.NAME
        self._ascending = True
        self._show_hidden = False
        
        self.file_model: Optional[QFileSystemModel] = None
        self.proxy_model: Optional[FileFilterProxyModel] = None
        self.sidebar: Optional[FluentFolderTree] = None
        self.path_bar: Optional[FluentPathBar] = None
        self.details_view: Optional[FluentFileDetailsView] = None
        self.list_view: Optional[FluentFileListView] = None
        self.tree_view: Optional[FluentFileTreeView] = None
        self.grid_view: Optional[FluentFileGridView] = None
        self.current_view: Optional[FluentFileView] = None


        self.setup_ui()
        self.setup_file_model()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)
        
        # Navigate to initial path
        self.navigate_to(self._current_path)
    
    def setup_ui(self):
        """Setup the file explorer UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Toolbar
        self.setup_toolbar(layout)
        
        # Path bar
        self.setup_path_bar(layout)
        
        # Search bar
        self.setup_search_bar(layout)
        
        # Main content area
        self.setup_content_area(layout)
        
        # Status bar
        self.setup_status_bar(layout)
    
    def setup_toolbar(self, layout: QVBoxLayout):
        """Setup toolbar with navigation and view controls"""
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(4)
        
        # Navigation buttons
        self.back_btn = QToolButton()
        self.back_btn.setText("←")
        self.back_btn.setToolTip("后退")
        self.back_btn.clicked.connect(self.go_back)
        toolbar_layout.addWidget(self.back_btn)
        
        self.forward_btn = QToolButton()
        self.forward_btn.setText("→")
        self.forward_btn.setToolTip("前进")
        self.forward_btn.clicked.connect(self.go_forward)
        toolbar_layout.addWidget(self.forward_btn)
        
        self.up_btn = QToolButton()
        self.up_btn.setText("↑")
        self.up_btn.setToolTip("上级目录")
        self.up_btn.clicked.connect(self.go_up)
        toolbar_layout.addWidget(self.up_btn)
        
        self.refresh_btn = QToolButton()
        self.refresh_btn.setText("⟳")
        self.refresh_btn.setToolTip("刷新")
        self.refresh_btn.clicked.connect(self.refresh)
        toolbar_layout.addWidget(self.refresh_btn)
        
        toolbar_layout.addStretch()
        
        # View mode buttons
        self.list_btn = QToolButton()
        self.list_btn.setText("☰")
        self.list_btn.setToolTip("列表视图")
        self.list_btn.setCheckable(True)
        self.list_btn.clicked.connect(lambda: self.set_view_mode(FluentViewMode.LIST))
        toolbar_layout.addWidget(self.list_btn)
        
        self.tree_btn = QToolButton()
        self.tree_btn.setText("🌳")
        self.tree_btn.setToolTip("树状视图")
        self.tree_btn.setCheckable(True)
        self.tree_btn.clicked.connect(lambda: self.set_view_mode(FluentViewMode.TREE))
        toolbar_layout.addWidget(self.tree_btn)
        
        self.grid_btn = QToolButton()
        self.grid_btn.setText("⊞")
        self.grid_btn.setToolTip("网格视图")
        self.grid_btn.setCheckable(True)
        self.grid_btn.clicked.connect(lambda: self.set_view_mode(FluentViewMode.GRID))
        toolbar_layout.addWidget(self.grid_btn)
        
        self.details_btn = QToolButton()
        self.details_btn.setText("☳")
        self.details_btn.setToolTip("详细视图")
        self.details_btn.setCheckable(True)
        self.details_btn.setChecked(True)
        self.details_btn.clicked.connect(lambda: self.set_view_mode(FluentViewMode.DETAILS))
        toolbar_layout.addWidget(self.details_btn)
        
        layout.addLayout(toolbar_layout)
    
    def setup_path_bar(self, layout: QVBoxLayout):
        """Setup path breadcrumb bar"""
        self.path_bar = FluentPathBar()
        self.path_bar.pathChanged.connect(self.navigate_to)
        layout.addWidget(self.path_bar)
    
    def setup_search_bar(self, layout: QVBoxLayout):
        """Setup search bar"""
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文件和文件夹...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)
        
        # Sort options
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("排序:"))
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["名称", "大小", "类型", "修改日期"])
        self.sort_combo.currentTextChanged.connect(self.on_sort_changed)
        sort_layout.addWidget(self.sort_combo)
        
        self.ascending_btn = QPushButton("↑")
        self.ascending_btn.setMaximumWidth(30)
        self.ascending_btn.setCheckable(True)
        self.ascending_btn.setChecked(True)
        self.ascending_btn.clicked.connect(self.toggle_sort_order)
        sort_layout.addWidget(self.ascending_btn)
        
        search_layout.addLayout(sort_layout)
        
        # Hidden files toggle
        self.hidden_btn = QPushButton("显示隐藏文件")
        self.hidden_btn.setCheckable(True)
        self.hidden_btn.clicked.connect(self.toggle_hidden_files)
        search_layout.addWidget(self.hidden_btn)
        
        layout.addLayout(search_layout)
    
    def setup_content_area(self, layout: QVBoxLayout):
        """Setup main content area with splitter"""
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sidebar (folders tree)
        self.sidebar = FluentFolderTree()
        self.sidebar.setMaximumWidth(250)
        self.sidebar.folderSelected.connect(self.navigate_to)
        self.splitter.addWidget(self.sidebar)
        
        # Main file view
        self.file_view_container = QWidget()
        self.file_view_layout = QVBoxLayout(self.file_view_container)
        self.file_view_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create different view widgets
        self.setup_view_widgets()
        
        self.splitter.addWidget(self.file_view_container)
        self.splitter.setSizes([200, 600])
        
        layout.addWidget(self.splitter)
    
    def setup_view_widgets(self):
        """Setup different view mode widgets"""
        # Details view (table)
        self.details_view = FluentFileDetailsView()
        self.details_view.fileSelected.connect(self.fileSelected.emit)
        self.details_view.fileActivated.connect(self.on_file_activated)
        self.file_view_layout.addWidget(self.details_view)
        
        # List view
        self.list_view = FluentFileListView()
        self.list_view.fileSelected.connect(self.fileSelected.emit)
        self.list_view.fileActivated.connect(self.on_file_activated)
        self.list_view.hide()
        self.file_view_layout.addWidget(self.list_view)
        
        # Tree view
        self.tree_view = FluentFileTreeView()
        self.tree_view.fileSelected.connect(self.fileSelected.emit)
        self.tree_view.fileActivated.connect(self.on_file_activated)
        self.tree_view.hide()
        self.file_view_layout.addWidget(self.tree_view)
        
        # Grid view
        self.grid_view = FluentFileGridView()
        self.grid_view.fileSelected.connect(self.fileSelected.emit)
        self.grid_view.fileActivated.connect(self.on_file_activated)
        self.grid_view.hide()
        self.file_view_layout.addWidget(self.grid_view)
        
        # Store current view
        self.current_view = self.details_view
    
    def setup_status_bar(self, layout: QVBoxLayout):
        """Setup status bar"""
        self.status_bar = QLabel()
        self.status_bar.setMaximumHeight(24)
        layout.addWidget(self.status_bar)
    
    def setup_file_model(self):
        """Setup file system model"""
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("") # Set a default root path
        
        # Create filter proxy
        self.proxy_model = FileFilterProxyModel()
        self.proxy_model.setSourceModel(self.file_model)
        
        # Set model for all views
        if self.details_view: self.details_view.setModel(self.proxy_model)
        if self.list_view: self.list_view.setModel(self.proxy_model)
        if self.tree_view: self.tree_view.setModel(self.proxy_model)
        if self.grid_view: self.grid_view.setModel(self.proxy_model)
        if self.sidebar: self.sidebar.setModel(self.file_model)
    
    def navigate_to(self, path: str):
        """Navigate to specified path"""
        if not os.path.exists(path) or not self.file_model or not self.proxy_model or not self.current_view or not self.sidebar or not self.path_bar:
            return
        
        self._current_path = os.path.abspath(path)
        
        # Update path bar
        self.path_bar.setPath(self._current_path)
        
        # Update file model root
        source_root_index = self.file_model.setRootPath(self._current_path)
        # The setRootPath for QFileSystemModel also sets the view's root if the model is shared.
        # For QSortFilterProxyModel, we generally set the root on the view itself using a mapped index.
        
        # Update all views by setting their root index to the root of the proxy model
        # which corresponds to the new path in the source model.
        # QFileSystemModel.index(path) gives the index for a path.
        source_index_for_path = self.file_model.index(self._current_path)
        proxy_index_for_path = self.proxy_model.mapFromSource(source_index_for_path)

        self.details_view.setRootIndex(proxy_index_for_path)
        self.list_view.setRootIndex(proxy_index_for_path)
        self.tree_view.setRootIndex(proxy_index_for_path)
        self.grid_view.setRootIndex(proxy_index_for_path)

        # Ensure the current view also has its root index set correctly
        self.current_view.setRootIndex(proxy_index_for_path)

        # Update sidebar
        self.sidebar.setCurrentPath(self._current_path)
        
        # Update status
        self.update_status()
        
        # Emit signal
        self.folderChanged.emit(self._current_path)
    
    def on_file_activated(self, file_path: str):
        """Handle file activation (double-click)"""
        if os.path.isdir(file_path):
            self.navigate_to(file_path)
        else:
            self.fileActivated.emit(file_path)
    
    def set_view_mode(self, mode: FluentViewMode):
        """Set file view mode"""
        if mode == self._view_mode or not self.current_view or not self.file_model or not self.proxy_model:
            return
        
        # Hide current view
        self.current_view.hide()
        
        # Update button states
        self.list_btn.setChecked(mode == FluentViewMode.LIST)
        self.tree_btn.setChecked(mode == FluentViewMode.TREE)
        self.grid_btn.setChecked(mode == FluentViewMode.GRID)
        self.details_btn.setChecked(mode == FluentViewMode.DETAILS)
        
        # Show new view
        if mode == FluentViewMode.LIST:
            self.current_view = self.list_view
        elif mode == FluentViewMode.TREE:
            self.current_view = self.tree_view
        elif mode == FluentViewMode.GRID:
            self.current_view = self.grid_view
        else:  # DETAILS
            self.current_view = self.details_view
        
        if self.current_view:
            self.current_view.show()
            self._view_mode = mode
            
            # Set root index for new view
            source_index_for_path = self.file_model.index(self._current_path)
            proxy_index_for_path = self.proxy_model.mapFromSource(source_index_for_path)
            self.current_view.setRootIndex(proxy_index_for_path)
    
    def on_search_changed(self, text: str):
        """Handle search text change"""
        if self.proxy_model:
            self.proxy_model.setFilterFixedString(text)
    
    def on_sort_changed(self, text: str):
        """Handle sort criteria change"""
        sort_map: Dict[str, FluentSortBy] = {
            "名称": FluentSortBy.NAME,
            "大小": FluentSortBy.SIZE,
            "类型": FluentSortBy.TYPE,
            "修改日期": FluentSortBy.DATE_MODIFIED
        }
        self._sort_by = sort_map.get(text, FluentSortBy.NAME)
        self.update_sorting()
    
    def toggle_sort_order(self):
        """Toggle sort order"""
        self._ascending = self.ascending_btn.isChecked()
        self.ascending_btn.setText("↑" if self._ascending else "↓")
        self.update_sorting()
    
    def update_sorting(self):
        """Update model sorting"""
        if not self.proxy_model:
            return
        column_map: Dict[FluentSortBy, int] = {
            FluentSortBy.NAME: 0,
            FluentSortBy.SIZE: 1,
            FluentSortBy.TYPE: 2, # QFileSystemModel type is column 2
            FluentSortBy.DATE_MODIFIED: 3 # QFileSystemModel date is column 3
        }
        column = column_map.get(self._sort_by, 0)
        order = Qt.SortOrder.AscendingOrder if self._ascending else Qt.SortOrder.DescendingOrder
        self.proxy_model.sort(column, order)
    
    def toggle_hidden_files(self):
        """Toggle hidden files visibility"""
        if not self.file_model:
            return
        self._show_hidden = self.hidden_btn.isChecked()
        filters = QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot
        if self._show_hidden:
            filters |= QDir.Filter.Hidden
        self.file_model.setFilter(filters)
    
    def go_back(self):
        """Go back in navigation history"""
        # TODO: Implement navigation history
        pass
    
    def go_forward(self):
        """Go forward in navigation history"""
        # TODO: Implement navigation history
        pass
    
    def go_up(self):
        """Go to parent directory"""
        parent_path = str(Path(self._current_path).parent)
        if parent_path != self._current_path:
            self.navigate_to(parent_path)
    
    def refresh(self):
        """Refresh current directory"""
        if self.file_model:
            self.file_model.refresh(self.file_model.index(self._current_path))
        self.update_status()
    
    def update_status(self):
        """Update status bar"""
        if not self.status_bar:
            return
        try:
            items = os.listdir(self._current_path)
            file_count = len([f for f in items if os.path.isfile(os.path.join(self._current_path, f))])
            folder_count = len([f for f in items if os.path.isdir(os.path.join(self._current_path, f))])
            self.status_bar.setText(f"{folder_count} 个文件夹, {file_count} 个文件")
        except OSError: # Changed from generic except
            self.status_bar.setText("无法访问此位置")
    
    def current_path(self) -> str:
        """Get current path"""
        return self._current_path
    
    def apply_theme(self):
        """Apply current theme"""
        bg_color_name = theme_manager.get_color('background').name()
        surface_color_name = theme_manager.get_color('surface').name()
        text_color_name = theme_manager.get_color('on_surface').name()
        primary_color_name = theme_manager.get_color('primary').name()
        outline_color_name = theme_manager.get_color('outline').name()
        surface_variant_color_name = theme_manager.get_color('surface_variant').name()
        on_primary_color_name = theme_manager.get_color('on_primary').name()
        
        self.setStyleSheet(f"""
            FluentFileExplorer {{
                background-color: {bg_color_name};
                color: {text_color_name};
            }}
            QToolButton {{
                background-color: {surface_color_name};
                color: {text_color_name};
                border: 1px solid {outline_color_name};
                border-radius: 4px;
                padding: 6px;
                margin: 1px;
            }}
            QToolButton:hover {{
                background-color: {surface_variant_color_name};
            }}
            QToolButton:checked {{
                background-color: {primary_color_name};
                color: {on_primary_color_name};
            }}
            QLineEdit {{
                background-color: {surface_color_name};
                color: {text_color_name};
                border: 2px solid {outline_color_name};
                border-radius: 6px;
                padding: 6px;
            }}
            QLineEdit:focus {{
                border-color: {primary_color_name};
            }}
            QComboBox {{
                background-color: {surface_color_name};
                color: {text_color_name};
                border: 2px solid {outline_color_name};
                border-radius: 6px;
                padding: 4px 8px;
                min-width: 80px;
            }}
            QPushButton {{
                background-color: {surface_color_name};
                color: {text_color_name};
                border: 2px solid {outline_color_name};
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {surface_variant_color_name};
            }}
            QPushButton:checked {{
                background-color: {primary_color_name};
                color: {on_primary_color_name};
            }}
            QLabel {{
                color: {text_color_name};
            }}
            QSplitter::handle {{
                background-color: {outline_color_name};
            }}
        """)


class FluentPathBar(QWidget):
    """Breadcrumb path bar widget"""
    
    # Signals
    pathChanged = Signal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._path = ""
        self._parts: List[str] = []
        self._path_bar_layout: Optional[QHBoxLayout] = None # Renamed from self.layout
        self.breadcrumb_widget: Optional[QWidget] = None
        self.breadcrumb_layout: Optional<QHBoxLayout] = None
        self.address_input: Optional[QLineEdit] = None
        self.edit_btn: Optional[QPushButton] = None

        self.setup_ui()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def setup_ui(self):
        """Setup path bar UI"""
        self._path_bar_layout = QHBoxLayout(self)
        self._path_bar_layout.setContentsMargins(8, 4, 8, 4)
        self._path_bar_layout.setSpacing(0)
        
        # Address bar toggle
        self.edit_btn = QPushButton("📝")
        self.edit_btn.setMaximumWidth(30)
        self.edit_btn.setToolTip("编辑地址")
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        self._path_bar_layout.addWidget(self.edit_btn)
        
        # Breadcrumb area
        self.breadcrumb_widget = QWidget()
        self.breadcrumb_layout = QHBoxLayout(self.breadcrumb_widget)
        self.breadcrumb_layout.setContentsMargins(0, 0, 0, 0)
        self.breadcrumb_layout.setSpacing(2)
        self._path_bar_layout.addWidget(self.breadcrumb_widget)
        
        # Address input (hidden by default)
        self.address_input = QLineEdit()
        self.address_input.returnPressed.connect(self.on_address_entered)
        self.address_input.hide()
        self._path_bar_layout.addWidget(self.address_input)
        
        self._path_bar_layout.addStretch()
    
    def setPath(self, path: str):
        """Set current path"""
        self._path = path
        self.update_breadcrumbs()
    
    def update_breadcrumbs(self):
        """Update breadcrumb buttons"""
        if not self.breadcrumb_layout:
            return
        # Clear existing breadcrumbs
        while self.breadcrumb_layout.count():
            child = self.breadcrumb_layout.takeAt(0)
            if child and child.widget():
                child.widget().deleteLater()
        
        # Create path parts
        path_obj = Path(self._path)
        parts: List[str] = []
        
        # Add drive/root
        if os.name == 'nt':  # Windows
            anchor = str(path_obj.anchor)
            parts.append(anchor)
            if anchor != str(path_obj) : # Avoid error if path is just the anchor e.g. "C:\"
                 try:
                    remaining_parts = path_obj.relative_to(anchor).parts
                    parts.extend(remaining_parts)
                 except ValueError: # Path is likely the anchor itself
                    pass
        else:  # Unix-like
            parts.append("/")
            if str(path_obj) != "/":
                try:
                    remaining_parts = path_obj.relative_to("/").parts
                    parts.extend(remaining_parts)
                except ValueError:
                    pass

        
        # Create breadcrumb buttons
        for i, part_name in enumerate(parts):
            if i > 0:
                # Add separator
                sep = QLabel("›")
                sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
                sep.setStyleSheet("color: gray; font-weight: bold;")
                self.breadcrumb_layout.addWidget(sep)
            
            # Add part button
            display_name = part_name if part_name else "根目录" # Handle empty part for root in some cases
            if os.name != 'nt' and i == 0 and part_name == "/":
                display_name = "根目录"
            elif not part_name and i==0 and os.name == 'nt': # Handle case like "C:\" where part_name might be "C:\"
                display_name = part_name if part_name else str(path_obj.anchor)


            btn = QPushButton(display_name)
            btn.setFlat(True)
            btn.clicked.connect(self.create_breadcrumb_handler(i, parts))
            self.breadcrumb_layout.addWidget(btn)
        
        self._parts = parts
    
    def create_breadcrumb_handler(self, index: int, current_parts: List[str]):
        """Create breadcrumb click handler"""
        def handler():
            path_to_navigate = ""
            if os.name == 'nt':
                if index == 0: # Drive letter
                    path_to_navigate = current_parts[0]
                else:
                    path_to_navigate = os.path.join(current_parts[0], *current_parts[1:index+1])
            else: # Unix-like
                if index == 0: # Root
                    path_to_navigate = "/"
                else: # Subdirectory
                    path_to_navigate = "/" + "/".join(current_parts[1:index+1])
            self.pathChanged.emit(path_to_navigate)
        return handler
    
    def toggle_edit_mode(self):
        """Toggle between breadcrumb and edit mode"""
        if not self.address_input or not self.breadcrumb_widget or not self.edit_btn:
            return
        if self.address_input.isVisible():
            # Switch to breadcrumb mode
            self.address_input.hide()
            self.breadcrumb_widget.show()
            self.edit_btn.setText("📝")
        else:
            # Switch to edit mode
            self.breadcrumb_widget.hide()
            self.address_input.setText(self._path)
            self.address_input.show()
            self.address_input.setFocus()
            self.address_input.selectAll()
            self.edit_btn.setText("✓") # Indicate apply
    
    def on_address_entered(self):
        """Handle address input"""
        if not self.address_input:
            return
        path = self.address_input.text()
        if os.path.exists(path):
            self.pathChanged.emit(path)
        self.toggle_edit_mode() # Switch back to breadcrumb view
    
    def apply_theme(self):
        """Apply current theme"""
        bg_color_name = theme_manager.get_color('surface').name()
        text_color_name = theme_manager.get_color('on_surface').name()
        outline_color_name = theme_manager.get_color('outline').name()
        surface_variant_color_name = theme_manager.get_color('surface_variant').name()
        
        self.setStyleSheet(f"""
            FluentPathBar {{
                background-color: {bg_color_name};
                border: 1px solid {outline_color_name};
                border-radius: 6px;
            }}
            QPushButton {{
                color: {text_color_name};
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {surface_variant_color_name};
            }}
            QLineEdit {{
                background-color: {bg_color_name};
                color: {text_color_name};
                border: none;
                padding: 4px 8px;
            }}
        """)


class FileFilterProxyModel(QSortFilterProxyModel):
    """Proxy model for filtering files"""
    
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:
        """Filter files based on search criteria"""
        if not self.filterRegularExpression().pattern():
            return True
        
        source_model = self.sourceModel()
        if not source_model:
            return False
        index = source_model.index(source_row, 0, source_parent)
        filename = source_model.data(index, Qt.ItemDataRole.DisplayRole)
        
        if filename is None: # Should not happen for valid items
            return False
        return self.filterRegularExpression().match(str(filename)).hasMatch()


# Base class for file views
class FluentFileView(QWidget):
    """Base class for file view widgets"""
    
    # Signals
    fileSelected = Signal(str)
    fileActivated = Signal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._model: Optional[QSortFilterProxyModel] = None
    
    def setModel(self, model: QSortFilterProxyModel):
        """Set the file model"""
        self._model = model
    
    def setRootIndex(self, index: QModelIndex):  # pylint: disable=unused-argument
        """Set root index for the view (intended for override by subclasses)."""
        pass


class FluentFileDetailsView(FluentFileView):
    """Details view showing files in a table"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.tree_view: Optional[QTreeView] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup details view UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tree_view = QTreeView()
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tree_view.clicked.connect(self.on_item_clicked)
        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)
        
        layout.addWidget(self.tree_view)
    
    def setModel(self, model: QSortFilterProxyModel):
        """Set model for tree view"""
        super().setModel(model)
        if self.tree_view:
            self.tree_view.setModel(model)
            
            # Configure columns
            header = self.tree_view.header()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Name
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive) # Size
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive) # Type
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive) # Date Modified
    
    def setRootIndex(self, index: QModelIndex):
        """Set root index"""
        if self.tree_view:
            self.tree_view.setRootIndex(index)
    
    def on_item_clicked(self, index: QModelIndex):
        """Handle item click"""
        if self._model:
            file_path = self._model.filePath(index)
            self.fileSelected.emit(file_path)
    
    def on_item_double_clicked(self, index: QModelIndex):
        """Handle item double click"""
        if self._model:
            file_path = self._model.filePath(index)
            self.fileActivated.emit(file_path)


class FluentFileListView(FluentFileView):
    """List view showing files in a simple list"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.list_view: Optional[QListView] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup list view UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.list_view = QListView()
        self.list_view.clicked.connect(self.on_item_clicked)
        self.list_view.doubleClicked.connect(self.on_item_double_clicked)
        
        layout.addWidget(self.list_view)
    
    def setModel(self, model: QSortFilterProxyModel):
        """Set model for list view"""
        super().setModel(model)
        if self.list_view:
            self.list_view.setModel(model)
    
    def setRootIndex(self, index: QModelIndex):
        """Set root index"""
        if self.list_view:
            self.list_view.setRootIndex(index)
    
    def on_item_clicked(self, index: QModelIndex):
        """Handle item click"""
        if self._model:
            file_path = self._model.filePath(index)
            self.fileSelected.emit(file_path)
    
    def on_item_double_clicked(self, index: QModelIndex):
        """Handle item double click"""
        if self._model:
            file_path = self._model.filePath(index)
            self.fileActivated.emit(file_path)


# Placeholder classes for tree and grid views
class FluentFileTreeView(FluentFileView): # Note: This is distinct from FluentFolderTree
    """Tree view for hierarchical file display within the main content area."""
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.tree_view: Optional[QTreeView] = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.tree_view = QTreeView()
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.clicked.connect(self.on_item_clicked)
        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.tree_view)

    def setModel(self, model: QSortFilterProxyModel):
        super().setModel(model)
        if self.tree_view:
            self.tree_view.setModel(model)
            # Configure columns similar to DetailsView if needed
            header = self.tree_view.header()
            if header: # Check if header exists
                header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)


    def setRootIndex(self, index: QModelIndex):
        if self.tree_view:
            self.tree_view.setRootIndex(index)

    def on_item_clicked(self, index: QModelIndex):
        if self._model:
            file_path = self._model.filePath(index)
            self.fileSelected.emit(file_path)

    def on_item_double_clicked(self, index: QModelIndex):
        if self._model:
            file_path = self._model.filePath(index)
            self.fileActivated.emit(file_path)


class FluentFileGridView(FluentFileView):
    """Grid view for icon-based file display"""
    # TODO: Implement Grid View (likely using QListView with setViewMode(QListView.IconMode))
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.grid_view_widget: Optional[QListView] = None # Example, could be custom
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.grid_view_widget = QListView() # Using QListView for grid
        self.grid_view_widget.setViewMode(QListView.ViewMode.IconMode)
        self.grid_view_widget.setResizeMode(QListView.ResizeMode.Adjust)
        self.grid_view_widget.setGridSize(Qt.QSize(100,100)) # Example size
        self.grid_view_widget.setUniformItemSizes(True)
        self.grid_view_widget.clicked.connect(self.on_item_clicked)
        self.grid_view_widget.doubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.grid_view_widget)

    def setModel(self, model: QSortFilterProxyModel):
        super().setModel(model)
        if self.grid_view_widget:
            self.grid_view_widget.setModel(model)

    def setRootIndex(self, index: QModelIndex):
        if self.grid_view_widget:
            self.grid_view_widget.setRootIndex(index)

    def on_item_clicked(self, index: QModelIndex):
        if self._model:
            file_path = self._model.filePath(index)
            self.fileSelected.emit(file_path)

    def on_item_double_clicked(self, index: QModelIndex):
        if self._model:
            file_path = self._model.filePath(index)
            self.fileActivated.emit(file_path)


class FluentFolderTree(QTreeView):
    """Sidebar folder tree widget"""
    
    # Signals
    folderSelected = Signal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup folder tree UI"""
        self.setHeaderHidden(True)
        self.clicked.connect(self.on_folder_clicked)
    
    def setModel(self, model: QFileSystemModel): # Type hint specifically QFileSystemModel
        """Set file system model"""
        super().setModel(model)
        
        # Hide all columns except name
        for i in range(1, model.columnCount()):
            self.hideColumn(i)
    
    def setCurrentPath(self, path: str):
        """Set current selected path"""
        current_model = self.model()
        if isinstance(current_model, QFileSystemModel):
            fs_model = cast(QFileSystemModel, current_model) # Cast for type safety
            index = fs_model.index(path, 0) # Explicit column 0
            if index.isValid():
                self.setCurrentIndex(index)
                self.expand(index)
                self.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)
    
    def on_folder_clicked(self, index: QModelIndex):
        """Handle folder click"""
        current_model = self.model()
        if isinstance(current_model, QFileSystemModel):
            fs_model = cast(QFileSystemModel, current_model) # Cast for type safety
            if fs_model.isDir(index):
                folder_path = fs_model.filePath(index)
                self.folderSelected.emit(folder_path)


# Export all classes
__all__ = [
    'FluentViewMode',
    'FluentSortBy',
    'FluentFileExplorer',
    'FluentPathBar',
    'FluentFileView',
    'FluentFileDetailsView',
    'FluentFileListView',
    'FluentFileTreeView',
    'FluentFileGridView',
    'FluentFolderTree',
    'FileFilterProxyModel'
]
