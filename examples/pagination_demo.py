"""
Fluent Pagination Components Demo
Comprehensive example showcasing all pagination features and functionality
"""

import sys
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QGroupBox,
    QScrollArea, QFrame, QLineEdit, QSpinBox, QSlider,
    QCheckBox, QTextEdit, QSizePolicy, QTableWidget, QTableWidgetItem,
    QTabWidget, QListWidget, QListWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

# Import the pagination components
from components.basic.pagination import FluentPagination, FluentSimplePagination
from core.theme import theme_manager, ThemeMode


class PaginationDemo(QMainWindow):
    """Main demo window showcasing all pagination features"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Pagination Components Demo")
        self.setGeometry(100, 100, 1400, 1000)

        # Sample data for demonstrations
        self.sample_data = self._generate_sample_data(1000)

        # Central widget with scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        # Main layout
        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Fluent Pagination Components Demo")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Theme toggle
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        if theme_manager.get_theme_mode() == ThemeMode.DARK:
            self.theme_combo.setCurrentText("Dark")
        else:
            self.theme_combo.setCurrentText("Light")
        self.theme_combo.currentTextChanged.connect(self._toggle_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        main_layout.addLayout(theme_layout)

        # Create demo sections using tabs
        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_basic_pagination_demo(), "Basic Pagination")
        tab_widget.addTab(self._create_modes_demo(), "Display Modes")
        tab_widget.addTab(self._create_simple_pagination_demo(), "Simple Pagination")
        tab_widget.addTab(self._create_data_demo(), "Data Integration")
        tab_widget.addTab(self._create_interactive_demo(), "Interactive Demo")
        tab_widget.addTab(self._create_advanced_demo(), "Advanced Features")
        
        main_layout.addWidget(tab_widget)
        main_layout.addStretch()

    def _generate_sample_data(self, count: int) -> list:
        """Generate sample data for demonstration"""
        names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Ivy", "Jack"]
        departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]
        
        data = []
        for i in range(count):
            data.append({
                "id": i + 1,
                "name": f"{random.choice(names)} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}",
                "department": random.choice(departments),
                "salary": random.randint(30000, 120000),
                "experience": random.randint(0, 15)
            })
        return data

    def _create_basic_pagination_demo(self) -> QWidget:
        """Create basic pagination demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Basic full pagination
        basic_group = QGroupBox("Basic Full Pagination")
        basic_layout = QVBoxLayout(basic_group)
        
        # Different page sizes
        layout_grid = QGridLayout()
        
        # Small dataset
        layout_grid.addWidget(QLabel("Small Dataset (50 items, 10 per page):"), 0, 0)
        self.small_pagination = FluentPagination(
            total=50, 
            page_size=10, 
            current_page=1,
            mode=FluentPagination.MODE_FULL
        )
        self.small_pagination.page_changed.connect(
            lambda page: self._log_page_change("Small", page)
        )
        layout_grid.addWidget(self.small_pagination, 1, 0)
        
        # Medium dataset
        layout_grid.addWidget(QLabel("Medium Dataset (500 items, 20 per page):"), 0, 1)
        self.medium_pagination = FluentPagination(
            total=500, 
            page_size=20, 
            current_page=5,
            mode=FluentPagination.MODE_FULL
        )
        self.medium_pagination.page_changed.connect(
            lambda page: self._log_page_change("Medium", page)
        )
        layout_grid.addWidget(self.medium_pagination, 1, 1)
        
        # Large dataset
        layout_grid.addWidget(QLabel("Large Dataset (10000 items, 50 per page):"), 2, 0)
        self.large_pagination = FluentPagination(
            total=10000, 
            page_size=50, 
            current_page=100,
            mode=FluentPagination.MODE_FULL
        )
        self.large_pagination.page_changed.connect(
            lambda page: self._log_page_change("Large", page)
        )
        layout_grid.addWidget(self.large_pagination, 3, 0)
        
        # Empty dataset
        layout_grid.addWidget(QLabel("Empty Dataset (0 items):"), 2, 1)
        self.empty_pagination = FluentPagination(
            total=0, 
            page_size=10, 
            current_page=1,
            mode=FluentPagination.MODE_FULL
        )
        self.empty_pagination.page_changed.connect(
            lambda page: self._log_page_change("Empty", page)
        )
        layout_grid.addWidget(self.empty_pagination, 3, 1)
        
        basic_layout.addLayout(layout_grid)
        layout.addWidget(basic_group)

        # Page size options demonstration
        page_size_group = QGroupBox("Custom Page Size Options")
        page_size_layout = QVBoxLayout(page_size_group)
        
        custom_options_info = QLabel("Custom page size options: [5, 15, 30, 60, 100]")
        page_size_layout.addWidget(custom_options_info)
        
        self.custom_page_size_pagination = FluentPagination(
            total=300,
            page_size=15,
            current_page=1,
            page_size_options=[5, 15, 30, 60, 100]
        )
        self.custom_page_size_pagination.page_changed.connect(
            lambda page: self._log_page_change("Custom Options", page)
        )
        self.custom_page_size_pagination.page_size_changed.connect(
            lambda size: self._log_page_size_change("Custom Options", size)
        )
        page_size_layout.addWidget(self.custom_page_size_pagination)
        
        layout.addWidget(page_size_group)

        # Controls demonstration
        controls_group = QGroupBox("Feature Controls")
        controls_layout = QGridLayout(controls_group)
        
        controls_layout.addWidget(QLabel("Toggle Features:"), 0, 0, 1, 2)
        
        # Controllable pagination for feature demonstration
        self.feature_pagination = FluentPagination(
            total=200,
            page_size=20,
            current_page=3,
            show_page_size=True,
            show_jumper=True,
            show_total=True
        )
        self.feature_pagination.page_changed.connect(
            lambda page: self._log_page_change("Feature Demo", page)
        )
        controls_layout.addWidget(self.feature_pagination, 1, 0, 1, 2)
        
        # Feature toggle controls
        self.show_total_cb = QCheckBox("Show Total")
        self.show_total_cb.setChecked(True)
        self.show_total_cb.toggled.connect(self._toggle_show_total)
        controls_layout.addWidget(self.show_total_cb, 2, 0)
        
        self.show_page_size_cb = QCheckBox("Show Page Size")
        self.show_page_size_cb.setChecked(True)
        self.show_page_size_cb.toggled.connect(self._toggle_show_page_size)
        controls_layout.addWidget(self.show_page_size_cb, 2, 1)
        
        self.show_jumper_cb = QCheckBox("Show Jumper")
        self.show_jumper_cb.setChecked(True)
        self.show_jumper_cb.toggled.connect(self._toggle_show_jumper)
        controls_layout.addWidget(self.show_jumper_cb, 3, 0)
        
        layout.addWidget(controls_group)

        # Event log
        self._setup_event_log(layout)

        return widget

    def _create_modes_demo(self) -> QWidget:
        """Create display modes demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Full mode
        full_mode_group = QGroupBox("Full Mode (MODE_FULL)")
        full_mode_layout = QVBoxLayout(full_mode_group)
        
        full_mode_info = QLabel("Shows all controls: page buttons, page size selector, jumper, total count")
        full_mode_layout.addWidget(full_mode_info)
        
        self.full_mode_pagination = FluentPagination(
            total=1000,
            page_size=25,
            current_page=10,
            mode=FluentPagination.MODE_FULL
        )
        self.full_mode_pagination.page_changed.connect(
            lambda page: self._log_page_change("Full Mode", page)
        )
        full_mode_layout.addWidget(self.full_mode_pagination)
        
        layout.addWidget(full_mode_group)

        # Compact mode
        compact_mode_group = QGroupBox("Compact Mode (MODE_COMPACT)")
        compact_mode_layout = QVBoxLayout(compact_mode_group)
        
        compact_mode_info = QLabel("Shows essential controls, hides some elements when only one page")
        compact_mode_layout.addWidget(compact_mode_info)
        
        # Multiple pagination examples for compact mode
        compact_examples_layout = QVBoxLayout()
        
        # Multi-page compact
        compact_examples_layout.addWidget(QLabel("Multi-page compact:"))
        self.compact_mode_pagination = FluentPagination(
            total=150,
            page_size=15,
            current_page=3,
            mode=FluentPagination.MODE_COMPACT
        )
        self.compact_mode_pagination.page_changed.connect(
            lambda page: self._log_page_change("Compact Mode", page)
        )
        compact_examples_layout.addWidget(self.compact_mode_pagination)
        
        # Single page compact
        compact_examples_layout.addWidget(QLabel("Single page compact:"))
        self.single_page_compact = FluentPagination(
            total=10,
            page_size=15,
            current_page=1,
            mode=FluentPagination.MODE_COMPACT
        )
        compact_examples_layout.addWidget(self.single_page_compact)
        
        compact_mode_layout.addLayout(compact_examples_layout)
        layout.addWidget(compact_mode_group)

        # Simple mode
        simple_mode_group = QGroupBox("Simple Mode (MODE_SIMPLE)")
        simple_mode_layout = QVBoxLayout(simple_mode_group)
        
        simple_mode_info = QLabel("Shows only previous/next buttons and total count")
        simple_mode_layout.addWidget(simple_mode_info)
        
        self.simple_mode_pagination = FluentPagination(
            total=500,
            page_size=30,
            current_page=8,
            mode=FluentPagination.MODE_SIMPLE
        )
        self.simple_mode_pagination.page_changed.connect(
            lambda page: self._log_page_change("Simple Mode", page)
        )
        simple_mode_layout.addWidget(self.simple_mode_pagination)
        
        layout.addWidget(simple_mode_group)

        # Mode switching demonstration
        mode_switch_group = QGroupBox("Dynamic Mode Switching")
        mode_switch_layout = QVBoxLayout(mode_switch_group)
        
        self.dynamic_mode_pagination = FluentPagination(
            total=300,
            page_size=20,
            current_page=5
        )
        self.dynamic_mode_pagination.page_changed.connect(
            lambda page: self._log_page_change("Dynamic Mode", page)
        )
        mode_switch_layout.addWidget(self.dynamic_mode_pagination)
        
        # Mode switch buttons
        mode_buttons_layout = QHBoxLayout()
        
        full_mode_btn = QPushButton("Full Mode")
        full_mode_btn.clicked.connect(lambda: self._set_dynamic_mode(FluentPagination.MODE_FULL))
        
        compact_mode_btn = QPushButton("Compact Mode")
        compact_mode_btn.clicked.connect(lambda: self._set_dynamic_mode(FluentPagination.MODE_COMPACT))
        
        simple_mode_btn = QPushButton("Simple Mode")
        simple_mode_btn.clicked.connect(lambda: self._set_dynamic_mode(FluentPagination.MODE_SIMPLE))
        
        mode_buttons_layout.addWidget(full_mode_btn)
        mode_buttons_layout.addWidget(compact_mode_btn)
        mode_buttons_layout.addWidget(simple_mode_btn)
        mode_buttons_layout.addStretch()
        
        mode_switch_layout.addLayout(mode_buttons_layout)
        layout.addWidget(mode_switch_group)

        return widget

    def _create_simple_pagination_demo(self) -> QWidget:
        """Create FluentSimplePagination demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Basic simple pagination
        basic_simple_group = QGroupBox("Basic Simple Pagination")
        basic_simple_layout = QVBoxLayout(basic_simple_group)
        
        simple_info = QLabel("Simple pagination with just Previous/Next buttons and page display")
        basic_simple_layout.addWidget(simple_info)
        
        # Different states
        states_layout = QGridLayout()
        
        # First page
        states_layout.addWidget(QLabel("First Page:"), 0, 0)
        self.first_page_simple = FluentSimplePagination(
            current_page=1,
            has_prev=False,
            has_next=True
        )
        self.first_page_simple.page_changed.connect(
            lambda page: self._handle_simple_page_change("First Page", page)
        )
        states_layout.addWidget(self.first_page_simple, 1, 0)
        
        # Middle page
        states_layout.addWidget(QLabel("Middle Page:"), 0, 1)
        self.middle_page_simple = FluentSimplePagination(
            current_page=5,
            has_prev=True,
            has_next=True
        )
        self.middle_page_simple.page_changed.connect(
            lambda page: self._handle_simple_page_change("Middle Page", page)
        )
        states_layout.addWidget(self.middle_page_simple, 1, 1)
        
        # Last page
        states_layout.addWidget(QLabel("Last Page:"), 2, 0)
        self.last_page_simple = FluentSimplePagination(
            current_page=10,
            has_prev=True,
            has_next=False
        )
        self.last_page_simple.page_changed.connect(
            lambda page: self._handle_simple_page_change("Last Page", page)
        )
        states_layout.addWidget(self.last_page_simple, 3, 0)
        
        # Single page
        states_layout.addWidget(QLabel("Single Page:"), 2, 1)
        self.single_page_simple = FluentSimplePagination(
            current_page=1,
            has_prev=False,
            has_next=False
        )
        states_layout.addWidget(self.single_page_simple, 3, 1)
        
        basic_simple_layout.addLayout(states_layout)
        layout.addWidget(basic_simple_group)

        # Interactive simple pagination
        interactive_simple_group = QGroupBox("Interactive Simple Pagination")
        interactive_simple_layout = QVBoxLayout(interactive_simple_group)
        
        self.interactive_simple = FluentSimplePagination(
            current_page=1,
            has_prev=False,
            has_next=True
        )
        self.interactive_simple.page_changed.connect(self._handle_interactive_simple_change)
        interactive_simple_layout.addWidget(self.interactive_simple)
        
        # Controls for interactive simple pagination
        simple_controls_layout = QGridLayout()
        
        simple_controls_layout.addWidget(QLabel("Current Page:"), 0, 0)
        self.simple_current_spinbox = QSpinBox()
        self.simple_current_spinbox.setRange(1, 100)
        self.simple_current_spinbox.setValue(1)
        self.simple_current_spinbox.valueChanged.connect(self._update_interactive_simple)
        simple_controls_layout.addWidget(self.simple_current_spinbox, 0, 1)
        
        simple_controls_layout.addWidget(QLabel("Total Pages:"), 0, 2)
        self.simple_total_spinbox = QSpinBox()
        self.simple_total_spinbox.setRange(1, 100)
        self.simple_total_spinbox.setValue(10)
        self.simple_total_spinbox.valueChanged.connect(self._update_interactive_simple)
        simple_controls_layout.addWidget(self.simple_total_spinbox, 0, 3)
        
        interactive_simple_layout.addLayout(simple_controls_layout)
        layout.addWidget(interactive_simple_group)

        return widget

    def _create_data_demo(self) -> QWidget:
        """Create data integration demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Table with pagination
        table_group = QGroupBox("Table with Pagination")
        table_layout = QVBoxLayout(table_group)
        
        # Data table
        self.data_table = QTableWidget(0, 5)
        self.data_table.setHorizontalHeaderLabels(["ID", "Name", "Department", "Salary", "Experience"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.data_table.setMaximumHeight(300)
        table_layout.addWidget(self.data_table)
        
        # Table pagination
        self.table_pagination = FluentPagination(
            total=len(self.sample_data),
            page_size=10,
            current_page=1,
            mode=FluentPagination.MODE_FULL
        )
        self.table_pagination.page_changed.connect(self._update_table_data)
        self.table_pagination.page_size_changed.connect(self._update_table_data)
        table_layout.addWidget(self.table_pagination)
        
        layout.addWidget(table_group)

        # List with pagination
        list_group = QGroupBox("List with Pagination")
        list_layout = QVBoxLayout(list_group)
        
        # Data list
        self.data_list = QListWidget()
        self.data_list.setMaximumHeight(200)
        list_layout.addWidget(self.data_list)
        
        # List pagination
        self.list_pagination = FluentPagination(
            total=len(self.sample_data),
            page_size=15,
            current_page=1,
            mode=FluentPagination.MODE_COMPACT
        )
        self.list_pagination.page_changed.connect(self._update_list_data)
        self.list_pagination.page_size_changed.connect(self._update_list_data)
        list_layout.addWidget(self.list_pagination)
        
        layout.addWidget(list_group)

        # Search with pagination
        search_group = QGroupBox("Search Results with Pagination")
        search_layout = QVBoxLayout(search_group)
        
        # Search controls
        search_controls_layout = QHBoxLayout()
        
        search_controls_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter name or department...")
        self.search_input.textChanged.connect(self._perform_search)
        search_controls_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self._perform_search)
        search_controls_layout.addWidget(search_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_search)
        search_controls_layout.addWidget(clear_btn)
        
        search_layout.addLayout(search_controls_layout)
        
        # Search results
        self.search_results = QListWidget()
        self.search_results.setMaximumHeight(150)
        search_layout.addWidget(self.search_results)
        
        # Search pagination
        self.search_pagination = FluentPagination(
            total=0,
            page_size=10,
            current_page=1,
            mode=FluentPagination.MODE_FULL
        )
        self.search_pagination.page_changed.connect(self._update_search_results)
        self.search_pagination.page_size_changed.connect(self._update_search_results)
        search_layout.addWidget(self.search_pagination)
        
        layout.addWidget(search_group)

        # Initialize data displays
        self._update_table_data()
        self._update_list_data()

        return widget

    def _create_interactive_demo(self) -> QWidget:
        """Create interactive demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Customizable pagination
        custom_group = QGroupBox("Customizable Pagination")
        custom_layout = QVBoxLayout(custom_group)
        
        # The pagination to customize
        self.custom_pagination = FluentPagination(
            total=500,
            page_size=20,
            current_page=5,
            mode=FluentPagination.MODE_FULL
        )
        self.custom_pagination.page_changed.connect(
            lambda page: self._log_page_change("Custom", page)
        )
        self.custom_pagination.page_size_changed.connect(
            lambda size: self._log_page_size_change("Custom", size)
        )
        custom_layout.addWidget(self.custom_pagination)
        
        # Customization controls
        controls_grid = QGridLayout()
        
        # Total items control
        controls_grid.addWidget(QLabel("Total Items:"), 0, 0)
        self.total_spinbox = QSpinBox()
        self.total_spinbox.setRange(0, 10000)
        self.total_spinbox.setValue(500)
        self.total_spinbox.valueChanged.connect(self._update_custom_total)
        controls_grid.addWidget(self.total_spinbox, 0, 1)
        
        # Page size control
        controls_grid.addWidget(QLabel("Page Size:"), 0, 2)
        self.page_size_spinbox = QSpinBox()
        self.page_size_spinbox.setRange(1, 100)
        self.page_size_spinbox.setValue(20)
        self.page_size_spinbox.valueChanged.connect(self._update_custom_page_size)
        controls_grid.addWidget(self.page_size_spinbox, 0, 3)
        
        # Current page control
        controls_grid.addWidget(QLabel("Current Page:"), 1, 0)
        self.current_page_spinbox = QSpinBox()
        self.current_page_spinbox.setRange(1, 100)
        self.current_page_spinbox.setValue(5)
        self.current_page_spinbox.valueChanged.connect(self._update_custom_current_page)
        controls_grid.addWidget(self.current_page_spinbox, 1, 1)
        
        # Mode control
        controls_grid.addWidget(QLabel("Mode:"), 1, 2)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Full", "Compact", "Simple"])
        self.mode_combo.currentTextChanged.connect(self._update_custom_mode)
        controls_grid.addWidget(self.mode_combo, 1, 3)
        
        custom_layout.addLayout(controls_grid)
        layout.addWidget(custom_group)

        # Stress test
        stress_group = QGroupBox("Stress Test & Performance")
        stress_layout = QVBoxLayout(stress_group)
        
        stress_info = QLabel("Test pagination performance with large datasets")
        stress_layout.addWidget(stress_info)
        
        # Stress test controls
        stress_controls_layout = QHBoxLayout()
        
        small_stress_btn = QPushButton("10K Items")
        small_stress_btn.clicked.connect(lambda: self._run_stress_test(10000))
        stress_controls_layout.addWidget(small_stress_btn)
        
        medium_stress_btn = QPushButton("100K Items")
        medium_stress_btn.clicked.connect(lambda: self._run_stress_test(100000))
        stress_controls_layout.addWidget(medium_stress_btn)
        
        large_stress_btn = QPushButton("1M Items")
        large_stress_btn.clicked.connect(lambda: self._run_stress_test(1000000))
        stress_controls_layout.addWidget(large_stress_btn)
        
        reset_stress_btn = QPushButton("Reset")
        reset_stress_btn.clicked.connect(self._reset_stress_test)
        stress_controls_layout.addWidget(reset_stress_btn)
        
        stress_controls_layout.addStretch()
        stress_layout.addLayout(stress_controls_layout)
        
        # Stress test pagination
        self.stress_pagination = FluentPagination(
            total=1000,
            page_size=50,
            current_page=1,
            mode=FluentPagination.MODE_FULL
        )
        self.stress_pagination.page_changed.connect(
            lambda page: self._log_page_change("Stress Test", page)
        )
        stress_layout.addWidget(self.stress_pagination)
        
        layout.addWidget(stress_group)

        # Multiple pagination coordination
        coordination_group = QGroupBox("Multiple Pagination Coordination")
        coordination_layout = QVBoxLayout(coordination_group)
        
        coordination_info = QLabel("Multiple paginations that can be synchronized")
        coordination_layout.addWidget(coordination_info)
        
        # Master pagination
        coordination_layout.addWidget(QLabel("Master Pagination:"))
        self.master_pagination = FluentPagination(
            total=200,
            page_size=10,
            current_page=1,
            mode=FluentPagination.MODE_FULL
        )
        self.master_pagination.page_changed.connect(self._sync_paginations)
        coordination_layout.addWidget(self.master_pagination)
        
        # Slave paginations
        coordination_layout.addWidget(QLabel("Synchronized Paginations:"))
        
        sync_layout = QVBoxLayout()
        
        self.slave_pagination_1 = FluentPagination(
            total=200,
            page_size=10,
            current_page=1,
            mode=FluentPagination.MODE_COMPACT
        )
        sync_layout.addWidget(self.slave_pagination_1)
        
        self.slave_pagination_2 = FluentPagination(
            total=200,
            page_size=10,
            current_page=1,
            mode=FluentPagination.MODE_SIMPLE
        )
        sync_layout.addWidget(self.slave_pagination_2)
        
        coordination_layout.addLayout(sync_layout)
        
        # Sync controls
        sync_controls = QHBoxLayout()
        
        enable_sync_cb = QCheckBox("Enable Synchronization")
        enable_sync_cb.setChecked(True)
        enable_sync_cb.toggled.connect(self._toggle_sync)
        sync_controls.addWidget(enable_sync_cb)
        
        self.sync_enabled = True
        sync_controls.addStretch()
        
        coordination_layout.addLayout(sync_controls)
        layout.addWidget(coordination_group)

        return widget

    def _create_advanced_demo(self) -> QWidget:
        """Create advanced features demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Page range algorithms
        algorithm_group = QGroupBox("Page Range Display Algorithm")
        algorithm_layout = QVBoxLayout(algorithm_group)
        
        algorithm_info = QLabel("Demonstrates page button display logic with different total pages")
        algorithm_layout.addWidget(algorithm_info)
        
        # Different total page scenarios
        scenarios_layout = QGridLayout()
        
        scenarios = [
            ("Few Pages (5)", 5, 3),
            ("Medium Pages (15)", 15, 8),
            ("Many Pages (50)", 50, 25),
            ("Lots of Pages (200)", 200, 100)
        ]
        
        self.algorithm_paginations = {}
        
        for i, (title, total_pages, current) in enumerate(scenarios):
            row = i // 2
            col = i % 2
            
            scenarios_layout.addWidget(QLabel(title), row * 2, col)
            
            pagination = FluentPagination(
                total=total_pages * 10,  # 10 items per page
                page_size=10,
                current_page=current,
                mode=FluentPagination.MODE_FULL
            )
            pagination.page_changed.connect(
                lambda page, t=title: self._log_page_change(t, page)
            )
            scenarios_layout.addWidget(pagination, row * 2 + 1, col)
            
            self.algorithm_paginations[title] = pagination
        
        algorithm_layout.addLayout(scenarios_layout)
        layout.addWidget(algorithm_group)

        # Edge cases
        edge_cases_group = QGroupBox("Edge Cases & Special Scenarios")
        edge_cases_layout = QVBoxLayout(edge_cases_group)
        
        edge_cases_layout.addWidget(QLabel("Various edge cases and special scenarios:"))
        
        edge_scenarios_layout = QGridLayout()
        
        # Single page
        edge_scenarios_layout.addWidget(QLabel("Single Page:"), 0, 0)
        single_page_edge = FluentPagination(
            total=5,
            page_size=10,
            current_page=1,
            mode=FluentPagination.MODE_FULL
        )
        edge_scenarios_layout.addWidget(single_page_edge, 1, 0)
        
        # Exact page division
        edge_scenarios_layout.addWidget(QLabel("Exact Division:"), 0, 1)
        exact_division_edge = FluentPagination(
            total=100,
            page_size=10,
            current_page=5,
            mode=FluentPagination.MODE_FULL
        )
        edge_scenarios_layout.addWidget(exact_division_edge, 1, 1)
        
        # Large page size
        edge_scenarios_layout.addWidget(QLabel("Large Page Size:"), 2, 0)
        large_page_size_edge = FluentPagination(
            total=50,
            page_size=100,
            current_page=1,
            mode=FluentPagination.MODE_FULL
        )
        edge_scenarios_layout.addWidget(large_page_size_edge, 3, 0)
        
        # Dynamic data changes
        edge_scenarios_layout.addWidget(QLabel("Dynamic Data:"), 2, 1)
        self.dynamic_edge = FluentPagination(
            total=100,
            page_size=10,
            current_page=5,
            mode=FluentPagination.MODE_FULL
        )
        edge_scenarios_layout.addWidget(self.dynamic_edge, 3, 1)
        
        edge_cases_layout.addLayout(edge_scenarios_layout)
        
        # Dynamic data controls
        dynamic_controls = QHBoxLayout()
        
        add_data_btn = QPushButton("Add 50 Items")
        add_data_btn.clicked.connect(lambda: self._modify_dynamic_data(50))
        dynamic_controls.addWidget(add_data_btn)
        
        remove_data_btn = QPushButton("Remove 30 Items")
        remove_data_btn.clicked.connect(lambda: self._modify_dynamic_data(-30))
        dynamic_controls.addWidget(remove_data_btn)
        
        clear_data_btn = QPushButton("Clear All")
        clear_data_btn.clicked.connect(lambda: self._set_dynamic_data(0))
        dynamic_controls.addWidget(clear_data_btn)
        
        reset_data_btn = QPushButton("Reset to 100")
        reset_data_btn.clicked.connect(lambda: self._set_dynamic_data(100))
        dynamic_controls.addWidget(reset_data_btn)
        
        dynamic_controls.addStretch()
        
        edge_cases_layout.addLayout(dynamic_controls)
        layout.addWidget(edge_cases_group)

        # Performance metrics
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QVBoxLayout(metrics_group)
        
        self.metrics_display = QTextEdit()
        self.metrics_display.setMaximumHeight(100)
        self.metrics_display.setPlainText("Click buttons above to see performance metrics...")
        metrics_layout.addWidget(self.metrics_display)
        
        layout.addWidget(metrics_group)

        return widget

    def _setup_event_log(self, parent_layout):
        """Setup event logging"""
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout(log_group)
        
        self.event_log = QTextEdit()
        self.event_log.setMaximumHeight(120)
        self.event_log.setPlaceholderText("Pagination events will be logged here...")
        log_layout.addWidget(self.event_log)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.event_log.clear)
        log_controls.addWidget(clear_log_btn)
        
        log_controls.addStretch()
        log_layout.addLayout(log_controls)
        
        parent_layout.addWidget(log_group)

    def _log_page_change(self, source: str, page: int):
        """Log page change events"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_log.append(f"[{timestamp}] {source}: Page changed to {page}")

    def _log_page_size_change(self, source: str, size: int):
        """Log page size change events"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_log.append(f"[{timestamp}] {source}: Page size changed to {size}")

    def _toggle_show_total(self, checked: bool):
        """Toggle show total feature"""
        # Note: This would require extending the FluentPagination API
        # For demo purposes, we'll just log the change
        self._log_page_change("Feature Toggle", f"Show Total: {checked}")

    def _toggle_show_page_size(self, checked: bool):
        """Toggle show page size feature"""
        self._log_page_change("Feature Toggle", f"Show Page Size: {checked}")

    def _toggle_show_jumper(self, checked: bool):
        """Toggle show jumper feature"""
        self._log_page_change("Feature Toggle", f"Show Jumper: {checked}")

    def _set_dynamic_mode(self, mode: str):
        """Set dynamic pagination mode"""
        self.dynamic_mode_pagination.set_mode(mode)
        self._log_page_change("Dynamic Mode", f"Mode changed to {mode}")

    def _handle_simple_page_change(self, source: str, page: int):
        """Handle simple pagination page changes"""
        self._log_page_change(f"Simple ({source})", page)
        
        # Update the pagination state based on new page
        if source == "First Page" and page > 1:
            self.first_page_simple.set_page_info(page, True, True)
        elif source == "Middle Page":
            has_prev = page > 1
            has_next = page < 10  # Assuming 10 total pages
            self.middle_page_simple.set_page_info(page, has_prev, has_next)
        elif source == "Last Page" and page < 10:
            self.last_page_simple.set_page_info(page, True, True)

    def _handle_interactive_simple_change(self, page: int):
        """Handle interactive simple pagination changes"""
        self._log_page_change("Interactive Simple", page)
        
        # Update spinbox
        self.simple_current_spinbox.setValue(page)
        
        # Update pagination state
        total_pages = self.simple_total_spinbox.value()
        has_prev = page > 1
        has_next = page < total_pages
        self.interactive_simple.set_page_info(page, has_prev, has_next)

    def _update_interactive_simple(self):
        """Update interactive simple pagination"""
        current = self.simple_current_spinbox.value()
        total = self.simple_total_spinbox.value()
        
        has_prev = current > 1
        has_next = current < total
        
        self.interactive_simple.set_page_info(current, has_prev, has_next)

    def _update_table_data(self):
        """Update table data based on pagination"""
        page = self.table_pagination.get_current_page()
        page_size = self.table_pagination.get_page_size()
        
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(self.sample_data))
        
        page_data = self.sample_data[start_idx:end_idx]
        
        self.data_table.setRowCount(len(page_data))
        for row, item in enumerate(page_data):
            self.data_table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.data_table.setItem(row, 1, QTableWidgetItem(item["name"]))
            self.data_table.setItem(row, 2, QTableWidgetItem(item["department"]))
            self.data_table.setItem(row, 3, QTableWidgetItem(f"${item['salary']:,}"))
            self.data_table.setItem(row, 4, QTableWidgetItem(f"{item['experience']} years"))

    def _update_list_data(self):
        """Update list data based on pagination"""
        page = self.list_pagination.get_current_page()
        page_size = self.list_pagination.get_page_size()
        
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(self.sample_data))
        
        page_data = self.sample_data[start_idx:end_idx]
        
        self.data_list.clear()
        for item in page_data:
            list_item = QListWidgetItem(f"{item['name']} - {item['department']} (${item['salary']:,})")
            self.data_list.addItem(list_item)

    def _perform_search(self):
        """Perform search and update pagination"""
        query = self.search_input.text().lower().strip()
        
        if not query:
            self.filtered_data = self.sample_data[:]
        else:
            self.filtered_data = [
                item for item in self.sample_data
                if query in item["name"].lower() or query in item["department"].lower()
            ]
        
        # Update search pagination
        self.search_pagination.set_total(len(self.filtered_data))
        self.search_pagination.set_current_page(1)
        
        self._update_search_results()

    def _clear_search(self):
        """Clear search"""
        self.search_input.clear()
        self.filtered_data = self.sample_data[:]
        self.search_pagination.set_total(len(self.filtered_data))
        self.search_pagination.set_current_page(1)
        self._update_search_results()

    def _update_search_results(self):
        """Update search results based on pagination"""
        if not hasattr(self, 'filtered_data'):
            self.filtered_data = self.sample_data[:]
        
        page = self.search_pagination.get_current_page()
        page_size = self.search_pagination.get_page_size()
        
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(self.filtered_data))
        
        page_data = self.filtered_data[start_idx:end_idx]
        
        self.search_results.clear()
        for item in page_data:
            result_item = QListWidgetItem(f"{item['name']} ({item['department']})")
            self.search_results.addItem(result_item)

    def _update_custom_total(self, total: int):
        """Update custom pagination total"""
        self.custom_pagination.set_total(total)
        max_pages = self.custom_pagination.get_total_pages()
        self.current_page_spinbox.setMaximum(max(1, max_pages))

    def _update_custom_page_size(self, size: int):
        """Update custom pagination page size"""
        self.custom_pagination.set_page_size(size)
        max_pages = self.custom_pagination.get_total_pages()
        self.current_page_spinbox.setMaximum(max(1, max_pages))

    def _update_custom_current_page(self, page: int):
        """Update custom pagination current page"""
        self.custom_pagination.set_current_page(page)

    def _update_custom_mode(self, mode_text: str):
        """Update custom pagination mode"""
        mode_map = {
            "Full": FluentPagination.MODE_FULL,
            "Compact": FluentPagination.MODE_COMPACT,
            "Simple": FluentPagination.MODE_SIMPLE
        }
        if mode_text in mode_map:
            self.custom_pagination.set_mode(mode_map[mode_text])

    def _run_stress_test(self, total_items: int):
        """Run stress test with large dataset"""
        import time
        start_time = time.time()
        
        self.stress_pagination.set_total(total_items)
        self.stress_pagination.set_current_page(1)
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        
        metrics = f"Stress Test Results:\n"
        metrics += f"Items: {total_items:,}\n"
        metrics += f"Update Time: {duration:.2f}ms\n"
        metrics += f"Total Pages: {self.stress_pagination.get_total_pages():,}\n"
        
        self.metrics_display.setPlainText(metrics)
        self._log_page_change("Stress Test", f"Loaded {total_items:,} items in {duration:.2f}ms")

    def _reset_stress_test(self):
        """Reset stress test"""
        self.stress_pagination.set_total(1000)
        self.stress_pagination.set_current_page(1)
        self.metrics_display.setPlainText("Stress test reset to 1,000 items")

    def _sync_paginations(self, page: int):
        """Sync multiple paginations"""
        if hasattr(self, 'sync_enabled') and self.sync_enabled:
            self.slave_pagination_1.set_current_page(page)
            self.slave_pagination_2.set_current_page(page)
            self._log_page_change("Sync Master", f"Synced to page {page}")

    def _toggle_sync(self, enabled: bool):
        """Toggle pagination synchronization"""
        self.sync_enabled = enabled
        self._log_page_change("Sync Control", f"Synchronization {'enabled' if enabled else 'disabled'}")

    def _modify_dynamic_data(self, change: int):
        """Modify dynamic edge case data"""
        current_total = self.dynamic_edge.get_total()
        new_total = max(0, current_total + change)
        self.dynamic_edge.set_total(new_total)
        self._log_page_change("Dynamic Data", f"Total changed from {current_total} to {new_total}")

    def _set_dynamic_data(self, total: int):
        """Set dynamic edge case data"""
        self.dynamic_edge.set_total(total)
        self.dynamic_edge.set_current_page(1)
        self._log_page_change("Dynamic Data", f"Set total to {total}")

    def _toggle_theme(self, theme_name: str):
        """Toggle between light and dark themes"""
        if theme_name == "Dark":
            theme_manager.set_theme_mode(ThemeMode.DARK)
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)
        
        self._log_page_change("Theme", f"Changed to {theme_name}")


def main():
    """Run the pagination demo application"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show demo window
    demo = PaginationDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()