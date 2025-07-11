#!/usr/bin/env python3
"""
Optimized File Explorer Components for Fluent UI - Bug Fixed Version

Modern file explorer utilizing Python 3.11+ features and enhanced Fluent Design.
This version fixes all compilation and runtime bugs while maintaining optimization features.
"""

import os
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Optional, List, Union
from collections.abc import Callable

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QListView, QLabel,
    QLineEdit, QComboBox, QSplitter, QAbstractItemView, QHeaderView,
    QFileSystemModel,
    QPushButton
)
from PySide6.QtCore import (
    Qt, Signal, QModelIndex, QDir, QSortFilterProxyModel, QPersistentModelIndex,
    QTimer, QAbstractItemModel, QSize, Slot
)
from PySide6.QtGui import (
    QKeySequence, QShortcut,
)

# Enhanced error handling for dependencies with fallbacks
THEME_AVAILABLE = False
FLUENT_COMPONENTS_AVAILABLE = False

try:
    from core.theme import theme_manager
    THEME_AVAILABLE = True
except ImportError:
    theme_manager = None

try:
    # Attempt to import FluentButton from a custom components library.
    # If the import fails or the component is not usable, fall back to QPushButton.
    from components.basic.button import FluentButton
    if hasattr(FluentButton, '__init__'):
        FLUENT_COMPONENTS_AVAILABLE = True
    else:
        FluentButton = QPushButton
except (ImportError, AttributeError):
    FluentButton = QPushButton


# Type aliases for modern Python syntax
FilePathType = Union[str, Path]

@dataclass(slots=True)
class FileViewState:
    """
    State container for file view optimization.

    Attributes:
        current_path (str): The currently displayed directory path.
        view_mode (str): The current view mode (e.g., "details", "list").
        sort_column (int): The column index used for sorting.
        sort_order (int): The sort order (Qt.SortOrder.AscendingOrder or DescendingOrder).
        show_hidden (bool): Flag indicating whether hidden files are shown.
        filter_text (str): The current text used for filtering files.
        selected_files (List[str]): A list of currently selected file paths.
    """
    current_path: str = ""
    view_mode: str = "details"
    sort_column: int = 0
    sort_order: int = 0
    show_hidden: bool = False
    filter_text: str = ""
    selected_files: List[str] = field(default_factory=list)


class FluentViewMode(Enum):
    """File view mode enumeration with auto values."""
    LIST = auto()
    TREE = auto()
    GRID = auto()
    DETAILS = auto()


class FluentSortBy(Enum):
    """Sort criteria enumeration with auto values."""
    NAME = auto()
    SIZE = auto()
    TYPE = auto()
    DATE_MODIFIED = auto()


class FluentFileExplorer(QWidget):
    """
    Optimized Fluent Design File Explorer - Bug Fixed Version.

    Modern file explorer with Python 3.11+ features and enhanced Fluent components.
    All bugs have been fixed for reliable production use.

    Signals:
        fileSelected (str): Emitted when a file is selected.
        folderChanged (str): Emitted when the current folder changes.
        fileActivated (str): Emitted when a file or folder is double-clicked/activated.
        operationStarted (str): Emitted when a file operation starts (placeholder).
        operationCompleted (str, bool): Emitted when a file operation completes (placeholder).
    """

    # Modern signal definitions
    fileSelected = Signal(str)
    folderChanged = Signal(str)
    fileActivated = Signal(str)
    operationStarted = Signal(str)
    operationCompleted = Signal(str, bool)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initializes the FluentFileExplorer widget.

        Args:
            parent (Optional[QWidget]): The parent widget.
        """
        super().__init__(parent)

        # State management with dataclass
        self._state = FileViewState(
            current_path=str(Path.home()),
            view_mode="details",
            sort_column=0,
            sort_order=Qt.SortOrder.AscendingOrder.value,
            show_hidden=False
        )

        # Component references with proper typing
        self.file_model: Optional[QFileSystemModel] = None
        self.proxy_model: Optional[FileFilterProxyModel] = None
        self.sidebar: Optional[FluentFolderTree] = None
        self.path_bar: Optional[FluentPathBar] = None
        self.details_view: Optional[FluentFileDetailsView] = None
        self.list_view: Optional[FluentFileListView] = None
        self.tree_view: Optional[FluentFileTreeView] = None
        self.grid_view: Optional[FluentFileGridView] = None
        self.current_view: Optional[FluentFileView] = None
        self.status_bar: Optional[QLabel] = None

        # Initialize components
        self.setup_ui()
        self.setup_file_model()
        self.setup_keyboard_shortcuts()

        # Theme integration with error handling
        if THEME_AVAILABLE and theme_manager:
            try:
                self.apply_theme()
                theme_manager.theme_changed.connect(self.apply_theme)
            except Exception:
                pass

        # Navigate to initial path
        self.navigate_to(self._state.current_path)

    def setup_ui(self) -> None:
        """Sets up the main file explorer UI layout and components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Setup components
        self._setup_toolbar(layout)
        self._setup_path_bar(layout)
        self._setup_search_bar(layout)
        self._setup_content_area(layout)
        self._setup_status_bar(layout)

    def _setup_toolbar(self, layout: QVBoxLayout) -> None:
        """
        Sets up the toolbar with navigation and view controls.

        Args:
            layout (QVBoxLayout): The main layout to add the toolbar to.
        """
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(6)

        # Navigation buttons
        self.back_btn = FluentButton("←")
        self.back_btn.setToolTip("后退 (Alt+Left)")
        self.back_btn.setMaximumWidth(40)
        self.back_btn.clicked.connect(self.go_back)
        toolbar_layout.addWidget(self.back_btn)

        self.forward_btn = FluentButton("→")
        self.forward_btn.setToolTip("前进 (Alt+Right)")
        self.forward_btn.setMaximumWidth(40)
        self.forward_btn.clicked.connect(self.go_forward)
        toolbar_layout.addWidget(self.forward_btn)

        self.up_btn = FluentButton("↑")
        self.up_btn.setToolTip("上级目录 (Alt+Up)")
        self.up_btn.setMaximumWidth(40)
        self.up_btn.clicked.connect(self.go_up)
        toolbar_layout.addWidget(self.up_btn)

        self.refresh_btn = FluentButton("⟳")
        self.refresh_btn.setToolTip("刷新 (F5)")
        self.refresh_btn.setMaximumWidth(40)
        self.refresh_btn.clicked.connect(self.refresh)
        toolbar_layout.addWidget(self.refresh_btn)

        toolbar_layout.addStretch()

        # View mode buttons
        self.list_btn = FluentButton("☰")
        self.list_btn.setToolTip("列表视图")
        self.list_btn.setMaximumWidth(40)
        self.list_btn.setCheckable(True)
        self.list_btn.clicked.connect(lambda: self.set_view_mode(FluentViewMode.LIST))
        toolbar_layout.addWidget(self.list_btn)

        self.tree_btn = FluentButton("🌳")
        self.tree_btn.setToolTip("树状视图")
        self.tree_btn.setMaximumWidth(40)
        self.tree_btn.setCheckable(True)
        self.tree_btn.clicked.connect(lambda: self.set_view_mode(FluentViewMode.TREE))
        toolbar_layout.addWidget(self.tree_btn)

        self.grid_btn = FluentButton("⊞")
        self.grid_btn.setToolTip("网格视图")
        self.grid_btn.setMaximumWidth(40)
        self.grid_btn.setCheckable(True)
        self.grid_btn.clicked.connect(lambda: self.set_view_mode(FluentViewMode.GRID))
        toolbar_layout.addWidget(self.grid_btn)

        self.details_btn = FluentButton("☳")
        self.details_btn.setToolTip("详细视图")
        self.details_btn.setMaximumWidth(40)
        self.details_btn.setCheckable(True)
        self.details_btn.setChecked(True)
        self.details_btn.clicked.connect(lambda: self.set_view_mode(FluentViewMode.DETAILS))
        toolbar_layout.addWidget(self.details_btn)

        layout.addLayout(toolbar_layout)

    def _setup_path_bar(self, layout: QVBoxLayout) -> None:
        """
        Sets up the path breadcrumb bar.

        Args:
            layout (QVBoxLayout): The main layout to add the path bar to.
        """
        self.path_bar = FluentPathBar()
        self.path_bar.pathChanged.connect(self.navigate_to)
        layout.addWidget(self.path_bar)

    def _setup_search_bar(self, layout: QVBoxLayout) -> None:
        """
        Sets up the search bar with search input, sort options, and hidden files toggle.

        Args:
            layout (QVBoxLayout): The main layout to add the search bar to.
        """
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)

        # Search input
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

    def _setup_content_area(self, layout: QVBoxLayout) -> None:
        """
        Sets up the main content area with a splitter for sidebar and file views.

        Args:
            layout (QVBoxLayout): The main layout to add the content area to.
        """
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sidebar
        self.sidebar = FluentFolderTree()
        self.sidebar.setMaximumWidth(280)
        self.sidebar.setMinimumWidth(200)
        self.sidebar.folderSelected.connect(self.navigate_to)
        self.splitter.addWidget(self.sidebar)

        # Main file view container
        self.file_view_container = QWidget()
        self.file_view_layout = QVBoxLayout(self.file_view_container)
        self.file_view_layout.setContentsMargins(0, 0, 0, 0)

        # Create view widgets
        self._setup_view_widgets()

        self.splitter.addWidget(self.file_view_container)
        self.splitter.setSizes([220, 600])

        layout.addWidget(self.splitter)

    def _setup_view_widgets(self) -> None:
        """Sets up the different view mode widgets (Details, List, Tree, Grid)."""
        # Details view
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

        # Set current view
        self.current_view = self.details_view

    def _setup_status_bar(self, layout: QVBoxLayout) -> None:
        """
        Sets up the status bar at the bottom of the window.

        Args:
            layout (QVBoxLayout): The main layout to add the status bar to.
        """
        self.status_bar = QLabel()
        self.status_bar.setMaximumHeight(28)
        self.status_bar.setStyleSheet("padding: 4px 8px; border-top: 1px solid palette(mid);")
        layout.addWidget(self.status_bar)

    def setup_keyboard_shortcuts(self) -> None:
        """Sets up keyboard shortcuts for navigation actions."""
        shortcuts = [
            (QKeySequence.StandardKey.Back, self.go_back),
            (QKeySequence.StandardKey.Forward, self.go_forward),
            (QKeySequence.StandardKey.Refresh, self.refresh),
            (QKeySequence("Alt+Up"), self.go_up),
        ]

        for key_sequence, slot in shortcuts:
            shortcut = QShortcut(key_sequence, self)
            shortcut.activated.connect(slot)

    def setup_file_model(self) -> None:
        """Sets up the QFileSystemModel and QSortFilterProxyModel."""
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")

        # Set filtering based on initial state
        filters = QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot
        if self._state.show_hidden:
            filters |= QDir.Filter.Hidden
        self.file_model.setFilter(filters)

        # Create proxy model for filtering and sorting
        self.proxy_model = FileFilterProxyModel()
        self.proxy_model.setSourceModel(self.file_model)

        # Set model for all view widgets
        views = [self.details_view, self.list_view, self.tree_view, self.grid_view]
        for view in views:
            if view:
                view.setModel(self.proxy_model)

        # Set model for the sidebar tree view
        if self.sidebar:
            self.sidebar.setModel(self.file_model)

    def navigate_to(self, path: str) -> None:
        """
        Navigates the file explorer to the specified path.

        Args:
            path (str): The target directory path.
        """
        if not path or not os.path.exists(path):
            # Handle invalid or non-existent paths
            if self.status_bar:
                 self.status_bar.setText(f"路径不存在: {path}")
            return

        if not self.file_model or not self.proxy_model or not self.current_view:
            # Handle uninitialized models/views
            if self.status_bar:
                 self.status_bar.setText("文件模型或视图未初始化")
            return

        try:
            # Normalize and store the current path
            self._state.current_path = os.path.abspath(path)

            # Update path bar
            if self.path_bar:
                self.path_bar.setPath(self._state.current_path)

            # Update file model by setting the root path.
            # This triggers the model to load the contents of the new directory.
            self.file_model.setRootPath(self._state.current_path)

            # Update views: Find the index for the current path in the source model
            source_index = self.file_model.index(self._state.current_path)
            # Map the source index to the proxy model index
            proxy_index = self.proxy_model.mapFromSource(source_index)
            # Set the root index for all views to display the contents of the new path
            self._update_all_views(proxy_index)

            # Update sidebar to reflect the current path selection
            if self.sidebar and hasattr(self.sidebar, 'setCurrentPath'):
                # Use a singleShot timer to allow the model to update before setting the current path
                QTimer.singleShot(50, lambda: self.sidebar.setCurrentPath(self._state.current_path))

            # Update status bar information
            self.update_status()

            # Emit folder changed signal
            self.folderChanged.emit(self._state.current_path)

        except Exception as e:
            # Handle navigation errors
            if self.status_bar:
                self.status_bar.setText(f"导航失败: {str(e)}")

    def _update_all_views(self, proxy_index: QModelIndex) -> None:
        """
        Sets the root index for all available file view widgets.

        Args:
            proxy_index (QModelIndex): The index in the proxy model representing the current directory.
        """
        views = [self.details_view, self.list_view, self.tree_view, self.grid_view]

        for view in views:
            # Check if the view exists and has the setRootIndex method
            if view and hasattr(view, 'setRootIndex'):
                try:
                    view.setRootIndex(proxy_index)
                except Exception:
                    # Continue even if one view fails to update
                    pass

        # Ensure the current view's root index is also set (redundant but safe)
        if self.current_view and hasattr(self.current_view, 'setRootIndex'):
            try:
                self.current_view.setRootIndex(proxy_index)
            except Exception:
                pass

    def on_file_activated(self, file_path: str) -> None:
        """
        Handles the activation (double-click) of a file or folder.

        If the path is a directory, navigates into it. If it's a file, emits the fileActivated signal.

        Args:
            file_path (str): The path of the activated item.
        """
        if not file_path or not os.path.exists(file_path):
            # Handle activation of non-existent paths
            if self.status_bar:
                 self.status_bar.setText(f"无法打开不存在的路径: {file_path}")
            return

        try:
            if os.path.isdir(file_path):
                # Navigate to the directory if it's a folder
                self.navigate_to(file_path)
            else:
                # Emit signal for file activation
                self.fileActivated.emit(file_path)
        except Exception as e:
            # Handle errors during activation
            if self.status_bar:
                self.status_bar.setText(f"无法打开: {str(e)}")

    def set_view_mode(self, mode: FluentViewMode) -> None:
        """
        Sets the current file view mode (Details, List, Tree, or Grid).

        Args:
            mode (FluentViewMode): The desired view mode.
        """
        if not self.current_view:
            # Handle uninitialized current view
            return

        # Hide the currently active view
        self.current_view.hide()

        # Update the checked state of the view mode buttons
        self._update_view_buttons(mode)

        # Determine the new current view based on the selected mode
        match mode:
            case FluentViewMode.LIST:
                self.current_view = self.list_view
            case FluentViewMode.TREE:
                self.current_view = self.tree_view
            case FluentViewMode.GRID:
                self.current_view = self.grid_view
            case _: # Default to DETAILS view
                self.current_view = self.details_view

        # Show the new current view and update the state
        if self.current_view:
            self.current_view.show()
            self._state.view_mode = str(mode.name).lower()

            # Set the root index for the newly shown view
            if self.file_model and self.proxy_model:
                try:
                    source_index = self.file_model.index(self._state.current_path)
                    proxy_index = self.proxy_model.mapFromSource(source_index)
                    if hasattr(self.current_view, 'setRootIndex'):
                        self.current_view.setRootIndex(proxy_index)
                except Exception:
                    pass

    def _update_view_buttons(self, mode: FluentViewMode) -> None:
        """
        Updates the checked state of the view mode buttons based on the current mode.

        Args:
            mode (FluentViewMode): The currently active view mode.
        """
        buttons = {
            FluentViewMode.LIST: self.list_btn,
            FluentViewMode.TREE: self.tree_btn,
            FluentViewMode.GRID: self.grid_btn,
            FluentViewMode.DETAILS: self.details_btn
        }

        # Iterate through buttons and set checked state
        for btn_mode, button in buttons.items():
            if button:
                button.setChecked(btn_mode == mode)

    def on_search_changed(self, text: str) -> None:
        """
        Handles changes in the search input text.

        Updates the filter text in the state and applies the filter to the proxy model.

        Args:
            text (str): The current text in the search input.
        """
        self._state.filter_text = text
        if self.proxy_model:
            # Set the filter string on the proxy model.
            # QSortFilterProxyModel uses QRegularExpression internally for setFilterFixedString.
            self.proxy_model.setFilterFixedString(text)
            self.update_status()

    def on_sort_changed(self, text: str) -> None:
        """
        Handles changes in the sort criteria combo box.

        Updates the sort column based on the selected text and applies the sorting.

        Args:
            text (str): The selected text from the sort combo box.
        """
        sort_map = {
            "名称": FluentSortBy.NAME,
            "大小": FluentSortBy.SIZE,
            "类型": FluentSortBy.TYPE,
            "修改日期": FluentSortBy.DATE_MODIFIED
        }

        sort_by = sort_map.get(text, FluentSortBy.NAME)
        self._update_sorting(sort_by)

    def toggle_sort_order(self) -> None:
        """
        Toggles the sort order between ascending and descending.

        Updates the sort order in the state and applies the sorting.
        """
        # Determine the new sort order based on the button's checked state
        ascending = self.ascending_btn.isChecked() if self.ascending_btn else True
        self._state.sort_order = Qt.SortOrder.AscendingOrder.value if ascending else Qt.SortOrder.DescendingOrder.value

        # Update the button text to reflect the current order
        if self.ascending_btn:
            self.ascending_btn.setText("↑" if ascending else "↓")

        # Apply the updated sorting
        self._update_sorting()

    def _update_sorting(self, sort_by: Optional[FluentSortBy] = None) -> None:
        """
        Updates the sorting criteria and order on the proxy model.

        Args:
            sort_by (Optional[FluentSortBy]): The new sort criteria. If None, uses the current criteria from state.
        """
        if not self.proxy_model:
            return

        # Update the sort column if a new criteria is provided
        if sort_by:
            match sort_by:
                case FluentSortBy.NAME:
                    column = 0
                case FluentSortBy.SIZE:
                    column = 1
                case FluentSortBy.TYPE:
                    column = 2
                case FluentSortBy.DATE_MODIFIED:
                    column = 3
                case _:
                    column = 0
            self._state.sort_column = column

        # Determine the sort order from the state
        order = Qt.SortOrder.AscendingOrder if self._state.sort_order == Qt.SortOrder.AscendingOrder.value else Qt.SortOrder.DescendingOrder
        # Apply sorting to the proxy model
        self.proxy_model.sort(self._state.sort_column, order)

    def toggle_hidden_files(self) -> None:
        """
        Toggles the visibility of hidden files.

        Updates the filter on the QFileSystemModel.
        """
        if not self.file_model:
            return

        # Update the show_hidden state based on the button's checked state
        self._state.show_hidden = self.hidden_btn.isChecked() if self.hidden_btn else False

        # Set the appropriate filters on the file model
        filters = QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot
        if self._state.show_hidden:
            filters |= QDir.Filter.Hidden

        self.file_model.setFilter(filters)
        self.update_status()

    def go_back(self) -> None:
        """
        Navigates back in the history.

        Currently implemented as a simple fallback to the parent directory.
        TODO: Implement a proper history stack for back/forward navigation.
        """
        self.go_up()

    def go_forward(self) -> None:
        """
        Navigates forward in the history.

        Currently a placeholder.
        TODO: Implement a proper history stack for back/forward navigation.
        """
        pass

    def go_up(self) -> None:
        """
        Navigates to the parent directory of the current path.
        """
        # Get the parent path using pathlib
        parent_path = str(Path(self._state.current_path).parent)
        # Navigate only if the parent path is different from the current path
        if parent_path != self._state.current_path:
            self.navigate_to(parent_path)

    def refresh(self) -> None:
        """
        Refreshes the contents of the current directory.

        Forces the QFileSystemModel to re-read the directory.
        """
        if not self.file_model:
            return

        try:
            # Refresh by re-setting the root path.
            # Setting to "" and then back to the current path forces a model reset and re-read.
            self.file_model.setRootPath("")
            self.file_model.setRootPath(self._state.current_path)
            self.update_status()

            # Provide temporary status feedback
            if self.status_bar:
                original_text = self.status_bar.text()
                self.status_bar.setText("已刷新")
                # Restore original text after a delay
                QTimer.singleShot(2000, lambda: self.status_bar.setText(original_text) if self.status_bar else None)

        except Exception as e:
            # Handle refresh errors
            if self.status_bar:
                self.status_bar.setText(f"刷新失败: {str(e)}")

    def update_status(self) -> None:
        """
        Updates the status bar with information about the current directory contents.
        """
        if not self.status_bar:
            return

        try:
            # Use pathlib to list directory contents safely
            current_path_obj = Path(self._state.current_path)
            items = list(current_path_obj.iterdir())
            files = [item for item in items if item.is_file()]
            folders = [item for item in items if item.is_dir()]

            # Construct status text
            status_parts = [f"{len(folders)} 个文件夹", f"{len(files)} 个文件"]

            if self._state.filter_text:
                status_parts.append("已过滤")

            self.status_bar.setText(" | ".join(status_parts))

        except OSError:
            # Handle cases where the directory is inaccessible
            self.status_bar.setText("无法访问此位置")
        except Exception as e:
            # Handle other potential errors during status update
            self.status_bar.setText(f"状态更新失败: {str(e)}")

    def current_path(self) -> str:
        """
        Gets the current directory path.

        Returns:
            str: The current directory path.
        """
        return self._state.current_path

    def apply_theme(self) -> None:
        """
        Applies the current theme's stylesheet to the file explorer widget.
        """
        if not THEME_AVAILABLE or not theme_manager:
            return

        try:
            # Apply stylesheet using palette colors for theme integration
            self.setStyleSheet("""
                QWidget {
                    background-color: palette(base);
                    color: palette(text);
                }
                QPushButton {
                    padding: 6px 12px;
                    border: 1px solid palette(mid);
                    border-radius: 4px;
                }
                QLineEdit {
                    padding: 6px;
                    border: 1px solid palette(mid);
                    border-radius: 4px;
                }
                QSplitter::handle {
                    background-color: palette(mid);
                }
                QTreeView, QListView {
                    background-color: palette(base);
                    color: palette(text);
                    border: 1px solid palette(mid);
                    selection-background-color: palette(highlight);
                    selection-color: palette(highlightedText);
                }
                QTreeView::branch:has-children:!has-siblings:closed,
                QTreeView::branch:closed:has-children:has-siblings {
                        border-image: none;
                        image: url(:/qt-project.org/styles/commonstyle/images/branch-closed.png); /* Example icon */
                }
                QTreeView::branch:open:has-children:!has-siblings,
                QTreeView::branch:open:has-children:has-siblings {
                        border-image: none;
                        image: url(:/qt-project.org/styles/commonstyle/images/branch-open.png); /* Example icon */
                }
            """)
        except Exception:
            pass


class FluentPathBar(QWidget):
    """
    Enhanced breadcrumb path bar widget.

    Allows navigation by clicking on path segments or by typing directly into an address input.

    Signals:
        pathChanged (str): Emitted when the path is changed via the path bar.
    """

    pathChanged = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initializes the FluentPathBar widget.

        Args:
            parent (Optional[QWidget]): The parent widget.
        """
        super().__init__(parent)
        self._path = ""
        self._parts: List[str] = []
        self._edit_mode = False

        self.setup_ui()

        if THEME_AVAILABLE and theme_manager:
            try:
                self.apply_theme()
                theme_manager.theme_changed.connect(self.apply_theme)
            except Exception:
                pass

    def setup_ui(self) -> None:
        """Sets up the path bar UI with edit button, breadcrumb area, and address input."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)

        # Edit button to toggle between breadcrumb and address input
        self.edit_btn = QPushButton("📝")
        self.edit_btn.setMaximumWidth(32)
        self.edit_btn.setToolTip("编辑地址")
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        layout.addWidget(self.edit_btn)

        # Widget to hold the breadcrumb buttons
        self.breadcrumb_widget = QWidget()
        self.breadcrumb_layout = QHBoxLayout(self.breadcrumb_widget)
        self.breadcrumb_layout.setContentsMargins(4, 0, 4, 0)
        self.breadcrumb_layout.setSpacing(2)
        layout.addWidget(self.breadcrumb_widget)

        # Address input field (initially hidden)
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("输入路径...")
        self.address_input.returnPressed.connect(self.on_address_entered)
        self.address_input.hide()
        layout.addWidget(self.address_input)

        layout.addStretch()

    def setPath(self, path: str) -> None:
        """
        Sets the current path displayed in the path bar.

        Args:
            path (str): The path to display.
        """
        # Normalize path and check if it's different from the current path
        normalized_path = os.path.normpath(path)
        if not path or normalized_path == os.path.normpath(self._path):
            return

        self._path = normalized_path
        self.update_breadcrumbs()

    def update_breadcrumbs(self) -> None:
        """Updates the breadcrumb buttons based on the current path."""
        if not self.breadcrumb_layout:
            return

        # Clear existing breadcrumb buttons and separators
        while self.breadcrumb_layout.count():
            child = self.breadcrumb_layout.takeAt(0)
            if child and child.widget():
                child.widget().deleteLater()

        # Split the path into parts
        path_obj = Path(self._path)
        parts: List[str] = []

        if os.name == 'nt':  # Windows path handling
            if path_obj.anchor:
                # Add the drive letter/root
                parts.append(path_obj.anchor.rstrip('\\'))
                # Add remaining parts relative to the anchor
                if str(path_obj).lower() != path_obj.anchor.lower():
                    try:
                        remaining_parts = path_obj.relative_to(path_obj.anchor).parts
                        parts.extend(remaining_parts)
                    except ValueError:
                        # Should not happen with valid paths
                        pass
        else:  # Unix-like path handling
            # Add the root "/"
            parts.append("/")
            # Add remaining parts relative to "/"
            if str(path_obj) != "/":
                try:
                    remaining_parts = path_obj.relative_to("/").parts
                    parts.extend(remaining_parts)
                except ValueError:
                    # Should not happen with valid paths
                    pass

        # Create breadcrumb buttons for each part
        for i, part_name in enumerate(parts):
            # Add separator between parts (except for the first part)
            if i > 0:
                sep = QLabel("›")
                sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.breadcrumb_layout.addWidget(sep)

            # Determine the display name for the button
            display_name = part_name if part_name else "根目录"
            if os.name == 'nt' and i == 0 and part_name:
                 # Ensure Windows drive letter is displayed correctly (e.g., "C:")
                display_name = part_name if part_name.endswith(':') else f"{part_name}:"
            elif os.name != 'nt' and i == 0 and part_name == "/":
                display_name = "根目录"

            # Create and configure the button
            btn = QPushButton(display_name)
            btn.setFlat(True)
            # Connect button click to a handler that navigates to the corresponding path segment
            btn.clicked.connect(self._create_breadcrumb_handler(i, parts))
            self.breadcrumb_layout.addWidget(btn)

        self._parts = parts

    def _create_breadcrumb_handler(self, index: int, current_parts: List[str]) -> Callable[[], None]:
        """
        Creates a click handler function for a breadcrumb button.

        The handler constructs the path up to the clicked segment and emits pathChanged.

        Args:
            index (int): The index of the clicked part in the path segments list.
            current_parts (List[str]): The list of path segments.

        Returns:
            Callable[[], None]: The click handler function.
        """
        def handler() -> None:
            try:
                if os.name == 'nt':
                    # Reconstruct path for Windows
                    if index == 0:
                        path_to_navigate = current_parts[0]
                        # Ensure drive path ends with a backslash for root
                        if not path_to_navigate.endswith('\\'):
                            path_to_navigate += '\\'
                    else:
                        base = current_parts[0]
                        if not base.endswith('\\'):
                            base += '\\'
                        path_to_navigate = os.path.join(base, *current_parts[1:index+1])
                else: # Unix-like path reconstruction
                    if index == 0:
                        path_to_navigate = "/"
                    else:
                        path_to_navigate = "/" + "/".join(current_parts[1:index+1])

                # Emit the signal with the constructed path
                self.pathChanged.emit(path_to_navigate)

            except Exception:
                # Fallback to navigating to the parent directory on error
                try:
                    fallback_path = str(Path(self._path).parent)
                    self.pathChanged.emit(fallback_path)
                except Exception:
                    pass

        return handler

    @Slot()
    def toggle_edit_mode(self) -> None:
        """Toggles between the breadcrumb view and the address input field."""
        self._edit_mode = not self._edit_mode

        if self._edit_mode:
            # Switch to edit mode: hide breadcrumbs, show input, set text, focus
            self.breadcrumb_widget.hide()
            self.address_input.setText(self._path)
            self.address_input.show()
            self.address_input.setFocus()
            self.address_input.selectAll()
            self.edit_btn.setText("✓") # Change button text to indicate confirmation
        else:
            # Switch back to breadcrumb mode: hide input, show breadcrumbs
            self.address_input.hide()
            self.breadcrumb_widget.show()
            self.edit_btn.setText("📝") # Change button text back to edit icon

    @Slot()
    def on_address_entered(self) -> None:
        """
        Handles the user pressing Enter in the address input field.

        Normalizes the path, checks if it exists, navigates if valid, and toggles back to breadcrumb mode.
        """
        path = self.address_input.text().strip()

        try:
            # Expand user home directory if path starts with '~'
            if path.startswith('~'):
                path = os.path.expanduser(path)

            # Normalize the path
            path = os.path.normpath(path)

            # Check if the path exists and navigate
            if os.path.exists(path):
                self.pathChanged.emit(path)
                self.toggle_edit_mode() # Switch back to breadcrumb mode on success
            else:
                # Indicate invalid path visually
                self.address_input.setStyleSheet("border: 2px solid red;")
                # Reset style after a delay
                QTimer.singleShot(2000, lambda: self.address_input.setStyleSheet(""))

        except Exception:
            # Indicate error visually for any exception during processing
            self.address_input.setStyleSheet("border: 2px solid red;")
            # Reset style after a delay
            QTimer.singleShot(2000, lambda: self.address_input.setStyleSheet(""))

    def apply_theme(self) -> None:
        """Applies the current theme's stylesheet to the path bar widget."""
        if not THEME_AVAILABLE or not theme_manager:
            return
        try:
            # Apply stylesheet using palette colors
            self.setStyleSheet("""
                FluentPathBar {
                    background-color: palette(base);
                    border: 1px solid palette(mid);
                    border-radius: 6px;
                }
                QPushButton {
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    background-color: transparent; /* Ensure buttons are transparent by default */
                }
                QPushButton:hover {
                    background-color: palette(light);
                }
                QLabel { /* Style for the separator */
                    color: palette(text);
                }
            """)
        except Exception:
            pass


class FileFilterProxyModel(QSortFilterProxyModel):
    """
    Proxy model for filtering files based on a search string.

    Inherits from QSortFilterProxyModel to provide filtering capabilities
    over a source model (typically QFileSystemModel).
    """

    def filterAcceptsRow(self, source_row: int, source_parent: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        """
        Determines whether a row from the source model should be accepted by the proxy.

        Filters files based on the search criteria set via setFilterFixedString.

        Args:
            source_row (int): The row number in the source model.
            source_parent (Union[QModelIndex, QPersistentModelIndex]): The parent index in the source model.

        Returns:
            bool: True if the row is accepted, False otherwise.
        """
        # Check if there is a filter pattern set. If not, accept all rows.
        if not self.filterRegularExpression().pattern():
            return True

        source_model = self.sourceModel()
        # Ensure source model exists
        if not source_model:
            return False

        # Get the index for the current row in the source model
        index = source_model.index(source_row, 0, source_parent)
        # Get the display role data (filename) for the item
        filename = source_model.data(index, Qt.ItemDataRole.DisplayRole)

        # Ensure filename is a string and not None
        if not isinstance(filename, str):
            return False

        # Check if the filename matches the filter regular expression set by setFilterFixedString
        return self.filterRegularExpression().match(filename).hasMatch()


class FluentFileView(QWidget):
    """
    Base class for file view widgets (Details, List, Tree, Grid).

    Provides common functionality for setting the model and handling item activation signals.

    Signals:
        fileSelected (str): Emitted when a file is selected in the view.
        fileActivated (str): Emitted when a file or folder is double-clicked/activated in the view.
    """

    fileSelected = Signal(str)
    fileActivated = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initializes the FluentFileView base widget.

        Args:
            parent (Optional[QWidget]): The parent widget.
        """
        super().__init__(parent)
        # Use QAbstractItemModel as the type hint for the model
        self._model: Optional[QAbstractItemModel] = None

    def setModel(self, model: QAbstractItemModel) -> None:
        """
        Sets the file model for the view.

        Args:
            model (QAbstractItemModel): The model to set (typically a QSortFilterProxyModel).
        """
        self._model = model

    def setRootIndex(self, index: QModelIndex) -> None:
        """
        Sets the root index for the view.

        This method is a placeholder in the base class and should be overridden
        by subclasses that use a root index (e.g., QTreeView, QListView).

        Args:
            index (QModelIndex): The index to set as the root.
        """
        # This method is intended to be overridden by subclasses.
        # The parameter 'index' is named to match the expected signature for views.
        pass

    def _get_file_path(self, index: QModelIndex) -> Optional[str]:
        """
        Retrieves the file path corresponding to a given model index.

        Handles mapping from a proxy model back to the source QFileSystemModel.

        Args:
            index (QModelIndex): The model index.

        Returns:
            Optional[str]: The file path if the index is valid and path can be retrieved, otherwise None.
        """
        # Check if the index is valid
        if not index.isValid():
            return None

        # Check if the model exists
        if self._model is None:
            return None

        try:
            # If the model is a QSortFilterProxyModel, map the index to the source model
            if isinstance(self._model, QSortFilterProxyModel):
                source_model = self._model.sourceModel()
                source_index = self._model.mapToSource(index)
                # Check if the source model is a QFileSystemModel and has filePath method
                if isinstance(source_model, QFileSystemModel) and hasattr(source_model, 'filePath'):
                    return source_model.filePath(source_index)
            # If the model is directly a QFileSystemModel and has filePath method
            elif isinstance(self._model, QFileSystemModel) and hasattr(self._model, 'filePath'):
                 # Call filePath directly on the model
                return self._model.filePath(index)

        except Exception:
            # Ignore errors during path retrieval and return None
            pass

        return None


class FluentFileDetailsView(FluentFileView):
    """
    Details view showing files in a table-like structure using QTreeView.

    Displays file name, size, type, and modification date.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initializes the FluentFileDetailsView widget.

        Args:
            parent (Optional[QWidget]): The parent widget.
        """
        super().__init__(parent)
        self.tree_view: Optional[QTreeView] = None
        self.setup_ui()

    def setup_ui(self) -> None:
        """Sets up the details view UI using a QTreeView."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree_view = QTreeView()
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tree_view.clicked.connect(self.on_item_clicked)
        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)
        # Configure QTreeView to behave more like a list/table for details view
        self.tree_view.setIndentation(0)
        self.tree_view.setRootIsDecorated(False)

        layout.addWidget(self.tree_view)

    def setModel(self, model: QAbstractItemModel) -> None:
        """
        Sets the model for the internal QTreeView and configures column resizing.

        Args:
            model (QAbstractItemModel): The model to set.
        """
        super().setModel(model)
        if self.tree_view and model:
            self.tree_view.setModel(model)

            # Configure columns resize mode
            header = self.tree_view.header()
            if header:
                # Ensure columns exist before setting resize mode
                if model.columnCount() > 0:
                    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Name column stretches
                if model.columnCount() > 1:
                    header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive) # Size column
                if model.columnCount() > 2:
                    header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive) # Type column
                if model.columnCount() > 3:
                    header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive) # Date Modified column

    def setRootIndex(self, index: QModelIndex) -> None:
        """
        Sets the root index for the internal QTreeView.

        Args:
            index (QModelIndex): The index to set as the root.
        """
        if self.tree_view:
            self.tree_view.setRootIndex(index)

    def on_item_clicked(self, index: QModelIndex) -> None:
        """
        Handles a single click on an item in the view.

        Emits the fileSelected signal with the path of the clicked item.

        Args:
            index (QModelIndex): The index of the clicked item.
        """
        file_path = self._get_file_path(index)
        if file_path:
            self.fileSelected.emit(file_path)

    def on_item_double_clicked(self, index: QModelIndex) -> None:
        """
        Handles a double click on an item in the view.

        Emits the fileActivated signal with the path of the double-clicked item.

        Args:
            index (QModelIndex): The index of the double-clicked item.
        """
        file_path = self._get_file_path(index)
        if file_path:
            self.fileActivated.emit(file_path)


class FluentFileListView(FluentFileView):
    """
    List view showing files in a simple vertical list using QListView.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initializes the FluentFileListView widget.

        Args:
            parent (Optional[QWidget]): The parent widget.
        """
        super().__init__(parent)
        self.list_view: Optional[QListView] = None
        self.setup_ui()

    def setup_ui(self) -> None:
        """Sets up the list view UI using a QListView."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list_view = QListView()
        self.list_view.clicked.connect(self.on_item_clicked)
        self.list_view.doubleClicked.connect(self.on_item_double_clicked)

        layout.addWidget(self.list_view)

    def setModel(self, model: QAbstractItemModel) -> None:
        """
        Sets the model for the internal QListView.

        Args:
            model (QAbstractItemModel): The model to set.
        """
        super().setModel(model)
        if self.list_view and model:
            self.list_view.setModel(model)

    def setRootIndex(self, index: QModelIndex) -> None:
        """
        Sets the root index for the internal QListView.

        Args:
            index (QModelIndex): The index to set as the root.
        """
        if self.list_view:
            self.list_view.setRootIndex(index)

    def on_item_clicked(self, index: QModelIndex) -> None:
        """
        Handles a single click on an item in the view.

        Emits the fileSelected signal with the path of the clicked item.

        Args:
            index (QModelIndex): The index of the clicked item.
        """
        file_path = self._get_file_path(index)
        if file_path:
            self.fileSelected.emit(file_path)

    def on_item_double_clicked(self, index: QModelIndex) -> None:
        """
        Handles a double click on an item in the view.

        Emits the fileActivated signal with the path of the double-clicked item.

        Args:
            index (QModelIndex): The index of the double-clicked item.
        """
        file_path = self._get_file_path(index)
        if file_path:
            self.fileActivated.emit(file_path)


class FluentFileTreeView(FluentFileView):
    """
    Tree view for hierarchical file display using QTreeView.

    Shows the directory structure in a tree format.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initializes the FluentFileTreeView widget.

        Args:
            parent (Optional[QWidget]): The parent widget.
        """
        super().__init__(parent)
        self.tree_view: Optional[QTreeView] = None
        self.setup_ui()

    def setup_ui(self) -> None:
        """Sets up the tree view UI using a QTreeView."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree_view = QTreeView()
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.clicked.connect(self.on_item_clicked)
        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)

        layout.addWidget(self.tree_view)

    def setModel(self, model: QAbstractItemModel) -> None:
        """
        Sets the model for the internal QTreeView and configures column resizing.

        Args:
            model (QAbstractItemModel): The model to set.
        """
        super().setModel(model)
        if self.tree_view and model:
            self.tree_view.setModel(model)
            header = self.tree_view.header()
            if header:
                 # Ensure column 0 exists before setting resize mode
                if model.columnCount() > 0:
                    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Name column stretches

    def setRootIndex(self, index: QModelIndex) -> None:
        """
        Sets the root index for the internal QTreeView.

        Args:
            index (QModelIndex): The index to set as the root.
        """
        if self.tree_view:
            self.tree_view.setRootIndex(index)

    def on_item_clicked(self, index: QModelIndex) -> None:
        """
        Handles a single click on an item in the view.

        Emits the fileSelected signal with the path of the clicked item.

        Args:
            index (QModelIndex): The index of the clicked item.
        """
        file_path = self._get_file_path(index)
        if file_path:
            self.fileSelected.emit(file_path)

    def on_item_double_clicked(self, index: QModelIndex) -> None:
        """
        Handles a double click on an item in the view.

        Emits the fileActivated signal with the path of the double-clicked item.

        Args:
            index (QModelIndex): The index of the double-clicked item.
        """
        file_path = self._get_file_path(index)
        if file_path:
            self.fileActivated.emit(file_path)


class FluentFileGridView(FluentFileView):
    """
    Grid view for icon-based file display using QListView in IconMode.

    Displays files and folders as icons in a grid layout.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initializes the FluentFileGridView widget.

        Args:
            parent (Optional[QWidget]): The parent widget.
        """
        super().__init__(parent)
        self.grid_view_widget: Optional[QListView] = None
        self.setup_ui()

    def setup_ui(self) -> None:
        """Sets up the grid view UI using a QListView configured for IconMode."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.grid_view_widget = QListView()
        self.grid_view_widget.setViewMode(QListView.ViewMode.IconMode)
        self.grid_view_widget.setResizeMode(QListView.ResizeMode.Adjust)
        self.grid_view_widget.setGridSize(QSize(100, 100)) # Example grid item size
        self.grid_view_widget.setUniformItemSizes(True)
        self.grid_view_widget.clicked.connect(self.on_item_clicked)
        self.grid_view_widget.doubleClicked.connect(self.on_item_double_clicked)

        layout.addWidget(self.grid_view_widget)

    def setModel(self, model: QAbstractItemModel) -> None:
        """
        Sets the model for the internal QListView.

        Args:
            model (QAbstractItemModel): The model to set.
        """
        super().setModel(model)
        if self.grid_view_widget and model:
            self.grid_view_widget.setModel(model)

    def setRootIndex(self, index: QModelIndex) -> None:
        """
        Sets the root index for the internal QListView.

        Args:
            index (QModelIndex): The index to set as the root.
        """
        if self.grid_view_widget:
            self.grid_view_widget.setRootIndex(index)

    def on_item_clicked(self, index: QModelIndex) -> None:
        """
        Handles a single click on an item in the view.

        Emits the fileSelected signal with the path of the clicked item.

        Args:
            index (QModelIndex): The index of the clicked item.
        """
        file_path = self._get_file_path(index)
        if file_path:
            self.fileSelected.emit(file_path)

    def on_item_double_clicked(self, index: QModelIndex) -> None:
        """
        Handles a double click on an item in the view.

        Emits the fileActivated signal with the path of the double-clicked item.

        Args:
            index (QModelIndex): The index of the double-clicked item.
        """
        file_path = self._get_file_path(index)
        if file_path:
            self.fileActivated.emit(file_path)


class FluentFolderTree(QTreeView):
    """
    Sidebar folder tree widget using QTreeView.

    Displays the directory structure hierarchically and allows selecting folders.

    Signals:
        folderSelected (str): Emitted when a folder is selected in the tree.
    """

    folderSelected = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initializes the FluentFolderTree widget.

        Args:
            parent (Optional[QWidget]): The parent widget.
        """
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Sets up the folder tree UI using a QTreeView."""
        self.setHeaderHidden(True) # Hide the header as only folder names are shown
        self.clicked.connect(self.on_folder_clicked)

    def setModel(self, model: QAbstractItemModel) -> None:
        """
        Sets the file system model for the tree view and hides unnecessary columns.

        Args:
            model (QAbstractItemModel): The model to set (typically QFileSystemModel).
        """
        super().setModel(model)

        # Hide all columns except the name column (column 0)
        if model:
            # Ensure model has columns before hiding
            for i in range(1, model.columnCount()):
                self.hideColumn(i)

    def setCurrentPath(self, path: str) -> None:
        """
        Sets the currently selected path in the folder tree.

        Expands the tree to show the path and scrolls to make it visible.

        Args:
            path (str): The path to set as current.
        """
        current_model = self.model()
        # Check if the model is a QFileSystemModel to use its filePath method
        if isinstance(current_model, QFileSystemModel):
            fs_model = current_model
            # Get the index for the given path
            index = fs_model.index(path, 0)
            if index.isValid():
                # Set the current index, expand the path, and scroll to it
                self.setCurrentIndex(index)
                self.expand(index)
                self.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)

    def on_folder_clicked(self, index: QModelIndex) -> None:
        """
        Handles a click on an item in the tree view.

        If the clicked item is a directory, emits the folderSelected signal.

        Args:
            index (QModelIndex): The index of the clicked item.
        """
        current_model = self.model()
        # Check if the model is a QFileSystemModel
        if isinstance(current_model, QFileSystemModel):
            fs_model = current_model
            # Check if the clicked item is a directory
            if fs_model.isDir(index):
                # Get the file path for the clicked index
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
    'FileFilterProxyModel',
    'FileViewState'
]
