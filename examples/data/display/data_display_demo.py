"""
Comprehensive Data Display Components Demo

This demo showcases all data display components available in the simple-fluent-widget library,
including tables, tree views, property grids, and file explorers.

Features demonstrated:
- Advanced table widgets with sorting and filtering
- Tree views with hierarchical data
- Property grids for object editing
- File explorer components
- Data visualization and management
- Performance optimizations for large datasets
"""

import sys
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QGroupBox,
    QScrollArea, QFrame, QSpacerItem, QSizePolicy, QMessageBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QHeaderView,
    QComboBox, QSpinBox, QCheckBox, QSlider, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor, QPalette, QFont, QIcon, QStandardItemModel, QStandardItem

# Import fluent components with fallbacks
try:
    from components.data.display.table import FluentTable, FluentListWidget, TableStyle
    FLUENT_TABLE_AVAILABLE = True
except ImportError:
    print("Warning: Fluent table components not available")
    FLUENT_TABLE_AVAILABLE = False

try:
    from components.data.display.tree import FluentTreeView, FluentTreeWidget
    FLUENT_TREE_AVAILABLE = True
except ImportError:
    print("Warning: Fluent tree components not available")
    FLUENT_TREE_AVAILABLE = False

try:
    from components.data.display.property_grid import FluentPropertyGrid, FluentPropertyItem, PropertyType
    FLUENT_PROPERTY_AVAILABLE = True
except ImportError:
    print("Warning: Fluent property grid components not available")
    FLUENT_PROPERTY_AVAILABLE = False

try:
    from components.data.display.fileexplorer import FluentFileExplorer, FluentDirectoryTree
    FLUENT_FILE_AVAILABLE = True
except ImportError:
    print("Warning: Fluent file explorer components not available")
    FLUENT_FILE_AVAILABLE = False

try:
    from components.layout.containers import FluentCard
    FLUENT_CARD_AVAILABLE = True
except ImportError:
    FLUENT_CARD_AVAILABLE = False


class SampleDataModel(QAbstractTableModel):
    """Sample table model for demonstration."""
    
    def __init__(self):
        super().__init__()
        self.headers = ["ID", "Name", "Type", "Size", "Modified", "Status"]
        self._data = [
            [1, "Document.pdf", "PDF", "2.5 MB", "2024-01-15", "Active"],
            [2, "Image.png", "Image", "1.2 MB", "2024-01-14", "Active"],
            [3, "Spreadsheet.xlsx", "Excel", "850 KB", "2024-01-13", "Draft"],
            [4, "Presentation.pptx", "PowerPoint", "4.1 MB", "2024-01-12", "Review"],
            [5, "Archive.zip", "Archive", "15.3 MB", "2024-01-11", "Complete"],
            [6, "Database.db", "Database", "8.7 MB", "2024-01-10", "Active"],
            [7, "Video.mp4", "Video", "125 MB", "2024-01-09", "Processing"],
            [8, "Audio.mp3", "Audio", "3.4 MB", "2024-01-08", "Active"],
            [9, "Code.py", "Python", "45 KB", "2024-01-07", "Active"],
            [10, "Config.json", "JSON", "2 KB", "2024-01-06", "Active"],
        ]
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._data)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Color code based on status
            status = self._data[index.row()][5]
            if status == "Active":
                return QColor(200, 255, 200)
            elif status == "Draft":
                return QColor(255, 255, 200)
            elif status == "Review":
                return QColor(255, 200, 200)
            elif status == "Processing":
                return QColor(200, 200, 255)
        
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None


class DataDisplayDemo(QMainWindow):
    """Main demo window showcasing data display components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Display Components Demo")
        self.setGeometry(100, 100, 1400, 900)
        
        # Sample data for demonstrations
        self.sample_model = SampleDataModel()
        self.tree_data = self.create_sample_tree_data()
        self.property_data = self.create_sample_property_data()
        
        self.setup_ui()
        self.populate_data()
        
    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Data Display Components Demo")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Tab widget for different component categories
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs for different component types
        self.create_table_tab()
        self.create_tree_tab()
        self.create_property_tab()
        self.create_file_explorer_tab()
        self.create_performance_tab()
        
        # Status bar
        self.statusBar().showMessage("Ready - Explore different data display components")
        
    def create_table_tab(self):
        """Create table components demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Controls section
        controls_group = QGroupBox("Table Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        # Filter
        controls_layout.addWidget(QLabel("Filter:"))
        self.table_filter = QLineEdit()
        self.table_filter.setPlaceholderText("Type to filter data...")
        self.table_filter.textChanged.connect(self.filter_table_data)
        controls_layout.addWidget(self.table_filter)
        
        # Sort
        controls_layout.addWidget(QLabel("Sort by:"))
        self.table_sort = QComboBox()
        self.table_sort.addItems(["ID", "Name", "Type", "Size", "Modified", "Status"])
        self.table_sort.currentTextChanged.connect(self.sort_table_data)
        controls_layout.addWidget(self.table_sort)
        
        # Actions
        add_row_btn = QPushButton("Add Row")
        add_row_btn.clicked.connect(self.add_table_row)
        controls_layout.addWidget(add_row_btn)
        
        remove_row_btn = QPushButton("Remove Selected")
        remove_row_btn.clicked.connect(self.remove_table_row)
        controls_layout.addWidget(remove_row_btn)
        
        layout.addWidget(controls_group)
        
        # Table widget
        if FLUENT_TABLE_AVAILABLE:
            try:
                self.table_widget = FluentTable()
                if hasattr(self.table_widget, 'setTableStyle'):
                    self.table_widget.setTableStyle(TableStyle.COMFORTABLE)
            except Exception as e:
                print(f"Error creating FluentTable: {e}")
                self.table_widget = QTableWidget()
        else:
            self.table_widget = QTableWidget()
        
        # Configure table
        self.table_widget.setRowCount(self.sample_model.rowCount())
        self.table_widget.setColumnCount(self.sample_model.columnCount())
        self.table_widget.setHorizontalHeaderLabels([
            self.sample_model.headerData(i, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            for i in range(self.sample_model.columnCount())
        ])
        
        # Make table sortable and selectable
        self.table_widget.setSortingEnabled(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setAlternatingRowColors(True)
        
        # Auto-resize columns
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table_widget)
        
        # Table info
        self.table_info = QLabel()
        layout.addWidget(self.table_info)
        
        self.tab_widget.addTab(tab_widget, "Tables")
        
    def create_tree_tab(self):
        """Create tree view demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Controls section
        controls_group = QGroupBox("Tree Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        expand_all_btn = QPushButton("Expand All")
        expand_all_btn.clicked.connect(self.expand_all_tree)
        controls_layout.addWidget(expand_all_btn)
        
        collapse_all_btn = QPushButton("Collapse All")
        collapse_all_btn.clicked.connect(self.collapse_all_tree)
        controls_layout.addWidget(collapse_all_btn)
        
        add_item_btn = QPushButton("Add Item")
        add_item_btn.clicked.connect(self.add_tree_item)
        controls_layout.addWidget(add_item_btn)
        
        remove_item_btn = QPushButton("Remove Selected")
        remove_item_btn.clicked.connect(self.remove_tree_item)
        controls_layout.addWidget(remove_item_btn)
        
        layout.addWidget(controls_group)
        
        # Tree widget
        if FLUENT_TREE_AVAILABLE:
            try:
                self.tree_widget = FluentTreeWidget()
            except Exception as e:
                print(f"Error creating FluentTreeWidget: {e}")
                self.tree_widget = QTreeWidget()
        else:
            self.tree_widget = QTreeWidget()
        
        # Configure tree
        self.tree_widget.setHeaderLabels(["Name", "Type", "Size", "Modified"])
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setSortingEnabled(True)
        
        # Connect signals
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        self.tree_widget.itemDoubleClicked.connect(self.on_tree_item_double_clicked)
        
        layout.addWidget(self.tree_widget)
        
        # Tree info
        self.tree_info = QLabel()
        layout.addWidget(self.tree_info)
        
        self.tab_widget.addTab(tab_widget, "Tree Views")
        
    def create_property_tab(self):
        """Create property grid demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Controls section
        controls_group = QGroupBox("Property Grid Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        load_preset_btn = QPushButton("Load Preset")
        load_preset_btn.clicked.connect(self.load_property_preset)
        controls_layout.addWidget(load_preset_btn)
        
        save_preset_btn = QPushButton("Save Preset")
        save_preset_btn.clicked.connect(self.save_property_preset)
        controls_layout.addWidget(save_preset_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_properties)
        controls_layout.addWidget(reset_btn)
        
        layout.addWidget(controls_group)
        
        # Property grid
        if FLUENT_PROPERTY_AVAILABLE:
            try:
                self.property_grid = FluentPropertyGrid()
            except Exception as e:
                print(f"Error creating FluentPropertyGrid: {e}")
                self.property_grid = self.create_fallback_property_widget()
        else:
            self.property_grid = self.create_fallback_property_widget()
        
        layout.addWidget(self.property_grid)
        
        # Property info
        self.property_info = QLabel()
        layout.addWidget(self.property_info)
        
        self.tab_widget.addTab(tab_widget, "Property Grids")
        
    def create_file_explorer_tab(self):
        """Create file explorer demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Controls section
        controls_group = QGroupBox("File Explorer Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        home_btn = QPushButton("Home")
        home_btn.clicked.connect(self.navigate_home)
        controls_layout.addWidget(home_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_file_explorer)
        controls_layout.addWidget(refresh_btn)
        
        # Path display
        controls_layout.addWidget(QLabel("Path:"))
        self.path_display = QLineEdit()
        self.path_display.setReadOnly(True)
        controls_layout.addWidget(self.path_display)
        
        layout.addWidget(controls_group)
        
        # File explorer
        if FLUENT_FILE_AVAILABLE:
            try:
                self.file_explorer = FluentFileExplorer()
                current_path = os.getcwd()
                if hasattr(self.file_explorer, 'currentPath'):
                    try:
                        current_path = self.file_explorer.currentPath()
                    except:
                        pass
                self.path_display.setText(current_path)
            except Exception as e:
                print(f"Error creating FluentFileExplorer: {e}")
                self.file_explorer = self.create_fallback_file_widget()
        else:
            self.file_explorer = self.create_fallback_file_widget()
        
        layout.addWidget(self.file_explorer)
        
        # File info
        self.file_info = QLabel()
        layout.addWidget(self.file_info)
        
        self.tab_widget.addTab(tab_widget, "File Explorer")
        
    def create_performance_tab(self):
        """Create performance demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Performance controls
        controls_group = QGroupBox("Performance Testing")
        controls_layout = QGridLayout(controls_group)
        
        controls_layout.addWidget(QLabel("Data Size:"), 0, 0)
        self.data_size_spin = QSpinBox()
        self.data_size_spin.setRange(100, 100000)
        self.data_size_spin.setValue(1000)
        self.data_size_spin.setSuffix(" rows")
        controls_layout.addWidget(self.data_size_spin, 0, 1)
        
        load_data_btn = QPushButton("Load Large Dataset")
        load_data_btn.clicked.connect(self.load_large_dataset)
        controls_layout.addWidget(load_data_btn, 0, 2)
        
        controls_layout.addWidget(QLabel("Update Rate:"), 1, 0)
        self.update_rate_spin = QSpinBox()
        self.update_rate_spin.setRange(10, 5000)
        self.update_rate_spin.setValue(100)
        self.update_rate_spin.setSuffix(" ms")
        controls_layout.addWidget(self.update_rate_spin, 1, 1)
        
        start_updates_btn = QPushButton("Start Live Updates")
        start_updates_btn.clicked.connect(self.start_live_updates)
        controls_layout.addWidget(start_updates_btn, 1, 2)
        
        stop_updates_btn = QPushButton("Stop Updates")
        stop_updates_btn.clicked.connect(self.stop_live_updates)
        controls_layout.addWidget(stop_updates_btn, 1, 3)
        
        layout.addWidget(controls_group)
        
        # Performance metrics
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QGridLayout(metrics_group)
        
        metrics_layout.addWidget(QLabel("Render Time:"), 0, 0)
        self.render_time_label = QLabel("N/A")
        metrics_layout.addWidget(self.render_time_label, 0, 1)
        
        metrics_layout.addWidget(QLabel("Memory Usage:"), 1, 0)
        self.memory_usage_label = QLabel("N/A")
        metrics_layout.addWidget(self.memory_usage_label, 1, 1)
        
        metrics_layout.addWidget(QLabel("Update Rate:"), 2, 0)
        self.actual_rate_label = QLabel("N/A")
        metrics_layout.addWidget(self.actual_rate_label, 2, 1)
        
        layout.addWidget(metrics_group)
        
        # Progress indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Performance log
        self.performance_log = QTextEdit()
        self.performance_log.setMaximumHeight(200)
        self.performance_log.setReadOnly(True)
        layout.addWidget(self.performance_log)
        
        self.tab_widget.addTab(tab_widget, "Performance")
        
        # Timer for live updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_performance_data)
        
    def create_fallback_property_widget(self):
        """Create a fallback property editor widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create basic property editors
        for category, properties in self.property_data.items():
            group = QGroupBox(category)
            group_layout = QGridLayout(group)
            
            row = 0
            for prop_name, prop_value in properties.items():
                group_layout.addWidget(QLabel(f"{prop_name}:"), row, 0)
                
                if isinstance(prop_value, bool):
                    editor = QCheckBox()
                    editor.setChecked(prop_value)
                elif isinstance(prop_value, int):
                    editor = QSpinBox()
                    editor.setRange(-999999, 999999)
                    editor.setValue(prop_value)
                elif isinstance(prop_value, float):
                    editor = QSpinBox()  # Simplified for demo
                    editor.setValue(int(prop_value))
                else:
                    editor = QLineEdit()
                    editor.setText(str(prop_value))
                
                group_layout.addWidget(editor, row, 1)
                row += 1
            
            layout.addWidget(group)
        
        return widget
        
    def create_fallback_file_widget(self):
        """Create a fallback file explorer widget."""
        widget = QTreeWidget()
        widget.setHeaderLabels(["Name", "Size", "Modified"])
        
        # Add some sample file entries
        root_item = QTreeWidgetItem(widget, ["Project Root", "", ""])
        
        folders = ["components", "examples", "tests", "docs"]
        for folder in folders:
            folder_item = QTreeWidgetItem(root_item, [folder, "<DIR>", "2024-01-15"])
            
            # Add some sample files
            files = [f"file1.py", f"file2.py", f"README.md"]
            for file in files:
                QTreeWidgetItem(folder_item, [file, "2.5 KB", "2024-01-15"])
        
        widget.expandAll()
        return widget
        
    def populate_data(self):
        """Populate all components with sample data."""
        self.populate_table_data()
        self.populate_tree_data()
        self.update_all_info_labels()
        
    def populate_table_data(self):
        """Populate table with sample data."""
        for row in range(self.sample_model.rowCount()):
            for col in range(self.sample_model.columnCount()):
                item = QTableWidgetItem(str(self.sample_model.data(
                    self.sample_model.index(row, col), Qt.ItemDataRole.DisplayRole
                )))
                
                # Apply background color
                bg_color = self.sample_model.data(
                    self.sample_model.index(row, col), Qt.ItemDataRole.BackgroundRole
                )
                if bg_color:
                    item.setBackground(bg_color)
                
                self.table_widget.setItem(row, col, item)
        
        self.update_table_info()
        
    def populate_tree_data(self):
        """Populate tree with sample hierarchical data."""
        for category, items in self.tree_data.items():
            category_item = QTreeWidgetItem(self.tree_widget, [category, "Folder", "", "2024-01-15"])
            
            for item_data in items:
                item = QTreeWidgetItem(category_item, item_data)
        
        self.tree_widget.expandAll()
        self.update_tree_info()
        
    def create_sample_tree_data(self):
        """Create sample hierarchical data."""
        return {
            "Documents": [
                ["Report.pdf", "PDF", "2.5 MB", "2024-01-15"],
                ["Presentation.pptx", "PowerPoint", "4.1 MB", "2024-01-14"],
                ["Spreadsheet.xlsx", "Excel", "850 KB", "2024-01-13"],
            ],
            "Images": [
                ["photo1.jpg", "JPEG", "1.2 MB", "2024-01-12"],
                ["diagram.png", "PNG", "456 KB", "2024-01-11"],
                ["logo.svg", "SVG", "23 KB", "2024-01-10"],
            ],
            "Code": [
                ["main.py", "Python", "45 KB", "2024-01-09"],
                ["utils.py", "Python", "12 KB", "2024-01-08"],
                ["config.json", "JSON", "2 KB", "2024-01-07"],
            ],
            "Media": [
                ["video.mp4", "Video", "125 MB", "2024-01-06"],
                ["audio.mp3", "Audio", "3.4 MB", "2024-01-05"],
                ["animation.gif", "GIF", "2.1 MB", "2024-01-04"],
            ]
        }
        
    def create_sample_property_data(self):
        """Create sample property data."""
        return {
            "Appearance": {
                "Background Color": "#FFFFFF",
                "Text Color": "#000000",
                "Font Size": 12,
                "Font Family": "Segoe UI",
                "Border Width": 1,
                "Border Radius": 4,
                "Opacity": 1.0,
                "Visible": True
            },
            "Behavior": {
                "Enabled": True,
                "Read Only": False,
                "Auto Save": True,
                "Tooltip Enabled": True,
                "Animation Speed": 250,
                "Max Length": 100,
                "Tab Order": 1
            },
            "Layout": {
                "Width": 200,
                "Height": 30,
                "Margin": 5,
                "Padding": 10,
                "Alignment": "Left",
                "Stretch": False,
                "Min Width": 50,
                "Max Width": 500
            }
        }
        
    # Event handlers
    def filter_table_data(self, text):
        """Filter table data based on search text."""
        for row in range(self.table_widget.rowCount()):
            match_found = False
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if item and text.lower() in item.text().lower():
                    match_found = True
                    break
            self.table_widget.setRowHidden(row, not match_found)
        
        self.update_table_info()
        
    def sort_table_data(self, column_name):
        """Sort table data by specified column."""
        column_index = self.sample_model.headers.index(column_name)
        self.table_widget.sortItems(column_index, Qt.SortOrder.AscendingOrder)
        self.statusBar().showMessage(f"Sorted by {column_name}")
        
    def add_table_row(self):
        """Add a new row to the table."""
        row_count = self.table_widget.rowCount()
        self.table_widget.insertRow(row_count)
        
        # Add sample data
        new_data = [
            str(row_count + 1),
            f"New Item {row_count + 1}",
            "Document",
            "1.0 KB",
            datetime.now().strftime("%Y-%m-%d"),
            "Draft"
        ]
        
        for col, value in enumerate(new_data):
            item = QTableWidgetItem(value)
            if col == 5 and value == "Draft":  # Status column
                item.setBackground(QColor(255, 255, 200))
            self.table_widget.setItem(row_count, col, item)
        
        self.update_table_info()
        self.statusBar().showMessage("New row added")
        
    def remove_table_row(self):
        """Remove selected row from table."""
        current_row = self.table_widget.currentRow()
        if current_row >= 0:
            self.table_widget.removeRow(current_row)
            self.update_table_info()
            self.statusBar().showMessage("Row removed")
        else:
            self.statusBar().showMessage("No row selected")
            
    def expand_all_tree(self):
        """Expand all tree items."""
        self.tree_widget.expandAll()
        self.statusBar().showMessage("All tree items expanded")
        
    def collapse_all_tree(self):
        """Collapse all tree items."""
        self.tree_widget.collapseAll()
        self.statusBar().showMessage("All tree items collapsed")
        
    def add_tree_item(self):
        """Add new item to tree."""
        current_item = self.tree_widget.currentItem()
        if current_item:
            # Add as child of selected item
            new_item = QTreeWidgetItem(current_item, [
                f"New Item {datetime.now().strftime('%H%M%S')}",
                "File",
                "1 KB",
                datetime.now().strftime("%Y-%m-%d")
            ])
            current_item.setExpanded(True)
        else:
            # Add as top-level item
            new_item = QTreeWidgetItem(self.tree_widget, [
                f"New Category {datetime.now().strftime('%H%M%S')}",
                "Folder",
                "",
                datetime.now().strftime("%Y-%m-%d")
            ])
        
        self.update_tree_info()
        self.statusBar().showMessage("New tree item added")
        
    def remove_tree_item(self):
        """Remove selected tree item."""
        current_item = self.tree_widget.currentItem()
        if current_item:
            parent = current_item.parent()
            if parent:
                parent.removeChild(current_item)
            else:
                index = self.tree_widget.indexOfTopLevelItem(current_item)
                self.tree_widget.takeTopLevelItem(index)
            
            self.update_tree_info()
            self.statusBar().showMessage("Tree item removed")
        else:
            self.statusBar().showMessage("No item selected")
            
    def on_tree_item_clicked(self, item, column):
        """Handle tree item click."""
        self.statusBar().showMessage(f"Selected: {item.text(0)}")
        
    def on_tree_item_double_clicked(self, item, column):
        """Handle tree item double click."""
        self.statusBar().showMessage(f"Opened: {item.text(0)}")
        
    def load_property_preset(self):
        """Load property preset."""
        self.statusBar().showMessage("Property preset loaded")
        
    def save_property_preset(self):
        """Save property preset."""
        self.statusBar().showMessage("Property preset saved")
        
    def reset_properties(self):
        """Reset properties to defaults."""
        self.statusBar().showMessage("Properties reset to defaults")
        
    def navigate_home(self):
        """Navigate to home directory."""
        self.path_display.setText(os.path.expanduser("~"))
        self.statusBar().showMessage("Navigated to home directory")
        
    def refresh_file_explorer(self):
        """Refresh file explorer."""
        self.statusBar().showMessage("File explorer refreshed")
        
    def load_large_dataset(self):
        """Load large dataset for performance testing."""
        size = self.data_size_spin.value()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, size)
        
        import time
        start_time = time.time()
        
        # Simulate loading large dataset
        for i in range(min(size, 1000)):  # Limit for demo
            self.progress_bar.setValue(i)
            QApplication.processEvents()
            
        end_time = time.time()
        
        self.progress_bar.setVisible(False)
        self.render_time_label.setText(f"{(end_time - start_time):.2f}s")
        self.performance_log.append(f"Loaded {size} rows in {(end_time - start_time):.2f}s")
        self.statusBar().showMessage(f"Loaded {size} rows")
        
    def start_live_updates(self):
        """Start live data updates."""
        interval = self.update_rate_spin.value()
        self.update_timer.start(interval)
        self.statusBar().showMessage("Live updates started")
        
    def stop_live_updates(self):
        """Stop live data updates."""
        self.update_timer.stop()
        self.statusBar().showMessage("Live updates stopped")
        
    def update_performance_data(self):
        """Update performance data in real-time."""
        import random
        import time
        
        # Simulate updating a random cell
        if self.table_widget.rowCount() > 0 and self.table_widget.columnCount() > 0:
            row = random.randint(0, self.table_widget.rowCount() - 1)
            col = random.randint(0, self.table_widget.columnCount() - 1)
            
            start_time = time.time()
            item = self.table_widget.item(row, col)
            if item:
                # Update with random data
                if col == 2:  # Size column
                    item.setText(f"{random.randint(1, 999)} KB")
                elif col == 5:  # Status column
                    statuses = ["Active", "Draft", "Review", "Complete"]
                    new_status = random.choice(statuses)
                    item.setText(new_status)
                    # Update background color
                    if new_status == "Active":
                        item.setBackground(QColor(200, 255, 200))
                    elif new_status == "Draft":
                        item.setBackground(QColor(255, 255, 200))
                    elif new_status == "Review":
                        item.setBackground(QColor(255, 200, 200))
            
            end_time = time.time()
            update_time = (end_time - start_time) * 1000  # Convert to ms
            
            self.actual_rate_label.setText(f"{update_time:.2f}ms")
            
            # Update memory usage (simplified)
            import psutil
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.memory_usage_label.setText(f"{memory_mb:.1f} MB")
            
    def update_table_info(self):
        """Update table information display."""
        visible_rows = sum(1 for row in range(self.table_widget.rowCount()) 
                          if not self.table_widget.isRowHidden(row))
        total_rows = self.table_widget.rowCount()
        
        self.table_info.setText(
            f"Showing {visible_rows} of {total_rows} rows | "
            f"{self.table_widget.columnCount()} columns | "
            f"Selected: {len(self.table_widget.selectedItems())} items"
        )
        
    def update_tree_info(self):
        """Update tree information display."""
        def count_items(parent):
            count = 0
            for i in range(parent.childCount()):
                count += 1 + count_items(parent.child(i))
            return count
        
        total_items = self.tree_widget.topLevelItemCount()
        for i in range(self.tree_widget.topLevelItemCount()):
            total_items += count_items(self.tree_widget.topLevelItem(i))
        
        self.tree_info.setText(
            f"Total items: {total_items} | "
            f"Top-level items: {self.tree_widget.topLevelItemCount()} | "
            f"Selected: {len(self.tree_widget.selectedItems())} items"
        )
        
    def update_all_info_labels(self):
        """Update all information labels."""
        self.update_table_info()
        self.update_tree_info()
        self.property_info.setText("Properties loaded and ready for editing")
        self.file_info.setText("File explorer ready - Navigate through directories")


def main():
    """Main function to run the demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Data Display Components Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Simple Fluent Widget")
    
    # Create and show the demo
    demo = DataDisplayDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
