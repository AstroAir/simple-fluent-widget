"""
Fluent ComboBox Components Demo
Comprehensive example showcasing all features and functionality
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QGroupBox,
    QScrollArea, QFrame, QLineEdit, QSpinBox, QTextEdit
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon

# Import the combobox components
from components.basic.combobox import (
    FluentComboBox, FluentMultiSelectComboBox, 
    FluentSearchableComboBox, FluentDropDownButton
)
from core.theme import theme_manager, ThemeMode


class ComboBoxDemo(QMainWindow):
    """Main demo window showcasing all combobox features"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent ComboBox Components Demo")
        self.setGeometry(100, 100, 1200, 800)

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
        title = QLabel("Fluent ComboBox Components Demo")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Theme toggle
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        if theme_manager._current_mode == ThemeMode.DARK:
            self.theme_combo.setCurrentText("Dark")
        else:
            self.theme_combo.setCurrentText("Light")
        self.theme_combo.currentTextChanged.connect(self._toggle_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        main_layout.addLayout(theme_layout)

        # Create demo sections
        main_layout.addWidget(self._create_fluent_combobox_demo())
        main_layout.addWidget(self._create_multiselect_demo())
        main_layout.addWidget(self._create_searchable_demo())
        main_layout.addWidget(self._create_dropdown_button_demo())
        main_layout.addWidget(self._create_interactive_demo())

        main_layout.addStretch()

    def _create_fluent_combobox_demo(self) -> QGroupBox:
        """Create FluentComboBox demonstration section"""
        group = QGroupBox("FluentComboBox")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Basic ComboBox
        layout.addWidget(QLabel("Basic FluentComboBox:"))
        basic_layout = QHBoxLayout()
        
        self.basic_combo = FluentComboBox()
        basic_items = ["Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape"]
        self.basic_combo.addItems(basic_items)
        self.basic_combo.setCurrentText("Cherry")
        
        self.basic_combo_label = QLabel(f"Selected: {self.basic_combo.currentText()}")
        self.basic_combo.currentTextChanged.connect(
            lambda text: self.basic_combo_label.setText(f"Selected: {text}")
        )
        
        basic_layout.addWidget(self.basic_combo)
        basic_layout.addWidget(self.basic_combo_label)
        basic_layout.addStretch()
        layout.addLayout(basic_layout)

        # States demonstration
        layout.addWidget(QLabel("Different States:"))
        states_layout = QGridLayout()
        
        # Normal state
        normal_combo = FluentComboBox()
        normal_combo.addItems(["Option 1", "Option 2", "Option 3"])
        normal_combo.setCurrentIndex(0)
        
        # Disabled state
        disabled_combo = FluentComboBox()
        disabled_combo.addItems(["Disabled Option 1", "Disabled Option 2"])
        disabled_combo.setCurrentIndex(1)
        disabled_combo.setEnabled(False)
        
        # Many items
        many_items_combo = FluentComboBox()
        many_items = [f"Item {i+1}" for i in range(20)]
        many_items_combo.addItems(many_items)
        many_items_combo.setCurrentIndex(5)
        
        states_layout.addWidget(QLabel("Normal:"), 0, 0)
        states_layout.addWidget(normal_combo, 0, 1)
        states_layout.addWidget(QLabel("Disabled:"), 1, 0)
        states_layout.addWidget(disabled_combo, 1, 1)
        states_layout.addWidget(QLabel("Many Items:"), 2, 0)
        states_layout.addWidget(many_items_combo, 2, 1)
        
        layout.addLayout(states_layout)

        # Dynamic manipulation
        layout.addWidget(QLabel("Dynamic Manipulation:"))
        dynamic_layout = QVBoxLayout()
        
        self.dynamic_combo = FluentComboBox()
        self.dynamic_combo.addItems(["Initial Item 1", "Initial Item 2"])
        
        controls_layout = QHBoxLayout()
        self.new_item_input = QLineEdit()
        self.new_item_input.setPlaceholderText("Enter new item...")
        
        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self._add_dynamic_item)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_dynamic_item)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_dynamic_items)
        
        controls_layout.addWidget(self.new_item_input)
        controls_layout.addWidget(add_btn)
        controls_layout.addWidget(remove_btn)
        controls_layout.addWidget(clear_btn)
        
        dynamic_layout.addWidget(self.dynamic_combo)
        dynamic_layout.addLayout(controls_layout)
        layout.addLayout(dynamic_layout)

        return group

    def _create_multiselect_demo(self) -> QGroupBox:
        """Create FluentMultiSelectComboBox demonstration section"""
        group = QGroupBox("FluentMultiSelectComboBox")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Basic multi-select
        layout.addWidget(QLabel("Basic Multi-Select:"))
        self.multiselect_basic = FluentMultiSelectComboBox()
        programming_languages = [
            "Python", "JavaScript", "Java", "C++", "C#", 
            "Go", "Rust", "TypeScript", "Swift", "Kotlin"
        ]
        self.multiselect_basic.add_items(programming_languages)
        
        self.multiselect_basic_label = QLabel("Selected: None")
        self.multiselect_basic.selection_changed.connect(
            lambda items: self.multiselect_basic_label.setText(f"Selected: {', '.join(items) if items else 'None'}")
        )
        
        layout.addWidget(self.multiselect_basic)
        layout.addWidget(self.multiselect_basic_label)

        # Pre-selected items
        layout.addWidget(QLabel("With Pre-selected Items:"))
        self.multiselect_preselected = FluentMultiSelectComboBox()
        colors = ["Red", "Green", "Blue", "Yellow", "Purple", "Orange", "Pink", "Black", "White"]
        self.multiselect_preselected.add_items(colors)
        self.multiselect_preselected.set_selected_items(["Red", "Blue", "Green"])
        
        self.multiselect_preselected_label = QLabel("Selected: Red, Blue, Green")
        self.multiselect_preselected.selection_changed.connect(
            lambda items: self.multiselect_preselected_label.setText(f"Selected: {', '.join(items) if items else 'None'}")
        )
        
        layout.addWidget(self.multiselect_preselected)
        layout.addWidget(self.multiselect_preselected_label)

        # Programmatic control
        layout.addWidget(QLabel("Programmatic Control:"))
        self.multiselect_control = FluentMultiSelectComboBox()
        frameworks = ["React", "Vue", "Angular", "Svelte", "Django", "Flask", "FastAPI", "Spring"]
        self.multiselect_control.add_items(frameworks)
        
        control_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(lambda: self.multiselect_control.set_selected_items(frameworks))
        
        select_web_btn = QPushButton("Select Web Frameworks")
        select_web_btn.clicked.connect(
            lambda: self.multiselect_control.set_selected_items(["React", "Vue", "Angular", "Svelte"])
        )
        
        select_python_btn = QPushButton("Select Python Frameworks")
        select_python_btn.clicked.connect(
            lambda: self.multiselect_control.set_selected_items(["Django", "Flask", "FastAPI"])
        )
        
        clear_selection_btn = QPushButton("Clear Selection")
        clear_selection_btn.clicked.connect(self.multiselect_control.clear_selection)
        
        control_layout.addWidget(select_all_btn)
        control_layout.addWidget(select_web_btn)
        control_layout.addWidget(select_python_btn)
        control_layout.addWidget(clear_selection_btn)
        
        self.multiselect_control_label = QLabel("Selected: None")
        self.multiselect_control.selection_changed.connect(
            lambda items: self.multiselect_control_label.setText(f"Selected: {', '.join(items) if items else 'None'}")
        )
        
        layout.addWidget(self.multiselect_control)
        layout.addLayout(control_layout)
        layout.addWidget(self.multiselect_control_label)

        return group

    def _create_searchable_demo(self) -> QGroupBox:
        """Create FluentSearchableComboBox demonstration section"""
        group = QGroupBox("FluentSearchableComboBox")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Basic searchable
        layout.addWidget(QLabel("Basic Searchable ComboBox:"))
        self.searchable_basic = FluentSearchableComboBox()
        countries = [
            "United States", "Canada", "United Kingdom", "Germany", "France",
            "Italy", "Spain", "Netherlands", "Belgium", "Switzerland",
            "Austria", "Sweden", "Norway", "Denmark", "Finland",
            "Japan", "South Korea", "China", "India", "Australia"
        ]
        self.searchable_basic.add_items(countries)
        
        self.searchable_basic_label = QLabel("Selected: None")
        self.searchable_basic.item_selected.connect(
            lambda text, data: self.searchable_basic_label.setText(f"Selected: {text}")
        )
        
        layout.addWidget(self.searchable_basic)
        layout.addWidget(self.searchable_basic_label)

        # With custom data
        layout.addWidget(QLabel("With Custom Data (Cities with Population):"))
        self.searchable_data = FluentSearchableComboBox()
        cities_data = [
            ("Tokyo", {"population": 37400000, "country": "Japan"}),
            ("Delhi", {"population": 28500000, "country": "India"}),
            ("Shanghai", {"population": 25600000, "country": "China"}),
            ("São Paulo", {"population": 21700000, "country": "Brazil"}),
            ("Mexico City", {"population": 21600000, "country": "Mexico"}),
            ("Cairo", {"population": 20100000, "country": "Egypt"}),
            ("Mumbai", {"population": 19980000, "country": "India"}),
            ("Beijing", {"population": 19600000, "country": "China"}),
            ("Dhaka", {"population": 19600000, "country": "Bangladesh"}),
            ("Osaka", {"population": 19300000, "country": "Japan"})
        ]
        
        for city, data in cities_data:
            self.searchable_data.add_item(city, data)
        
        self.searchable_data_label = QLabel("Selected: None")
        self.searchable_data.item_selected.connect(self._on_city_selected)
        
        layout.addWidget(self.searchable_data)
        layout.addWidget(self.searchable_data_label)

        # Programmatic control
        layout.addWidget(QLabel("Programmatic Control:"))
        self.searchable_control = FluentSearchableComboBox()
        programming_terms = [
            "Algorithm", "API", "Array", "Boolean", "Class", "Compiler",
            "Database", "Debug", "Exception", "Function", "Git", "Hash",
            "IDE", "JSON", "Kernel", "Library", "Method", "Null",
            "Object", "Parser", "Query", "Recursion", "Stack", "Thread"
        ]
        self.searchable_control.add_items(programming_terms)
        
        search_control_layout = QHBoxLayout()
        set_text_input = QLineEdit()
        set_text_input.setPlaceholderText("Enter text to set...")
        
        set_text_btn = QPushButton("Set Text")
        set_text_btn.clicked.connect(
            lambda: self.searchable_control.set_selected_text(set_text_input.text())
        )
        
        clear_items_btn = QPushButton("Clear Items")
        clear_items_btn.clicked.connect(self.searchable_control.clear_items)
        
        reload_items_btn = QPushButton("Reload Items")
        reload_items_btn.clicked.connect(
            lambda: self.searchable_control.add_items(programming_terms)
        )
        
        search_control_layout.addWidget(set_text_input)
        search_control_layout.addWidget(set_text_btn)
        search_control_layout.addWidget(clear_items_btn)
        search_control_layout.addWidget(reload_items_btn)
        
        layout.addLayout(search_control_layout)

        return group

    def _create_dropdown_button_demo(self) -> QGroupBox:
        """Create FluentDropDownButton demonstration section"""
        group = QGroupBox("FluentDropDownButton")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Basic dropdown button
        layout.addWidget(QLabel("Basic Dropdown Button:"))
        basic_layout = QHBoxLayout()
        
        self.dropdown_basic = FluentDropDownButton("File Operations")
        file_operations = [
            ("New File", "new"),
            ("Open File", "open"),
            ("Save File", "save"),
            ("Save As...", "save_as"),
            ("Close File", "close")
        ]
        
        for text, data in file_operations:
            self.dropdown_basic.add_menu_item(text, data)
        
        self.dropdown_basic_label = QLabel("Last Action: None")
        self.dropdown_basic.item_clicked.connect(
            lambda text, data: self.dropdown_basic_label.setText(f"Last Action: {text} ({data})")
        )
        
        basic_layout.addWidget(self.dropdown_basic)
        basic_layout.addWidget(self.dropdown_basic_label)
        basic_layout.addStretch()
        layout.addLayout(basic_layout)

        # With different categories
        layout.addWidget(QLabel("Edit Operations:"))
        edit_layout = QHBoxLayout()
        
        self.dropdown_edit = FluentDropDownButton("Edit")
        edit_operations = [
            ("Undo", "undo"),
            ("Redo", "redo"),
            ("Cut", "cut"),
            ("Copy", "copy"),
            ("Paste", "paste"),
            ("Select All", "select_all")
        ]
        
        for text, data in edit_operations:
            self.dropdown_edit.add_menu_item(text, data)
        
        self.dropdown_edit_label = QLabel("Last Edit: None")
        self.dropdown_edit.item_clicked.connect(
            lambda text, data: self.dropdown_edit_label.setText(f"Last Edit: {text}")
        )
        
        edit_layout.addWidget(self.dropdown_edit)
        edit_layout.addWidget(self.dropdown_edit_label)
        edit_layout.addStretch()
        layout.addLayout(edit_layout)

        # Dynamic menu
        layout.addWidget(QLabel("Dynamic Menu:"))
        self.dropdown_dynamic = FluentDropDownButton("Dynamic Menu")
        
        dynamic_control_layout = QHBoxLayout()
        self.menu_item_input = QLineEdit()
        self.menu_item_input.setPlaceholderText("Enter menu item...")
        
        add_menu_item_btn = QPushButton("Add Menu Item")
        add_menu_item_btn.clicked.connect(self._add_menu_item)
        
        clear_menu_btn = QPushButton("Clear Menu")
        clear_menu_btn.clicked.connect(self._clear_menu_items)
        
        dynamic_control_layout.addWidget(self.menu_item_input)
        dynamic_control_layout.addWidget(add_menu_item_btn)
        dynamic_control_layout.addWidget(clear_menu_btn)
        
        self.dropdown_dynamic_label = QLabel("Last Selection: None")
        self.dropdown_dynamic.item_clicked.connect(
            lambda text, data: self.dropdown_dynamic_label.setText(f"Last Selection: {text}")
        )
        
        layout.addWidget(self.dropdown_dynamic)
        layout.addLayout(dynamic_control_layout)
        layout.addWidget(self.dropdown_dynamic_label)

        return group

    def _create_interactive_demo(self) -> QGroupBox:
        """Create interactive demonstration section"""
        group = QGroupBox("Interactive Demo & Testing")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Stress test with many items
        layout.addWidget(QLabel("Performance Test (1000 items):"))
        perf_layout = QHBoxLayout()
        
        self.perf_combo = FluentComboBox()
        perf_items = [f"Performance Item {i+1}" for i in range(1000)]
        
        load_perf_btn = QPushButton("Load 1000 Items")
        load_perf_btn.clicked.connect(lambda: self._load_performance_items(perf_items))
        
        self.perf_label = QLabel("Items loaded: 0")
        
        perf_layout.addWidget(self.perf_combo)
        perf_layout.addWidget(load_perf_btn)
        perf_layout.addWidget(self.perf_label)
        perf_layout.addStretch()
        layout.addLayout(perf_layout)

        # Combined functionality test
        layout.addWidget(QLabel("Combined Functionality Test:"))
        
        # Create all component types in a grid
        grid_layout = QGridLayout()
        
        # Regular combo
        grid_layout.addWidget(QLabel("Regular:"), 0, 0)
        self.test_regular = FluentComboBox()
        self.test_regular.addItems(["Test 1", "Test 2", "Test 3"])
        grid_layout.addWidget(self.test_regular, 0, 1)
        
        # Multi-select
        grid_layout.addWidget(QLabel("Multi-Select:"), 1, 0)
        self.test_multi = FluentMultiSelectComboBox()
        self.test_multi.add_items(["Multi 1", "Multi 2", "Multi 3", "Multi 4"])
        grid_layout.addWidget(self.test_multi, 1, 1)
        
        # Searchable
        grid_layout.addWidget(QLabel("Searchable:"), 2, 0)
        self.test_searchable = FluentSearchableComboBox()
        self.test_searchable.add_items(["Search A", "Search B", "Search C", "Different Item"])
        grid_layout.addWidget(self.test_searchable, 2, 1)
        
        # Dropdown button
        grid_layout.addWidget(QLabel("Dropdown Button:"), 3, 0)
        self.test_dropdown = FluentDropDownButton("Actions")
        self.test_dropdown.add_menu_item("Action 1", "action1")
        self.test_dropdown.add_menu_item("Action 2", "action2")
        grid_layout.addWidget(self.test_dropdown, 3, 1)
        
        layout.addLayout(grid_layout)

        # Test controls
        test_controls_layout = QHBoxLayout()
        
        enable_all_btn = QPushButton("Enable All")
        enable_all_btn.clicked.connect(self._enable_all_test_components)
        
        disable_all_btn = QPushButton("Disable All")
        disable_all_btn.clicked.connect(self._disable_all_test_components)
        
        reset_all_btn = QPushButton("Reset All")
        reset_all_btn.clicked.connect(self._reset_all_test_components)
        
        test_controls_layout.addWidget(enable_all_btn)
        test_controls_layout.addWidget(disable_all_btn)
        test_controls_layout.addWidget(reset_all_btn)
        test_controls_layout.addStretch()
        
        layout.addLayout(test_controls_layout)

        # Status display
        self.status_display = QTextEdit()
        self.status_display.setMaximumHeight(100)
        self.status_display.setPlaceholderText("Component interactions will be logged here...")
        layout.addWidget(self.status_display)

        # Connect all test components to status logger
        self._connect_test_components_to_logger()

        return group

    def _add_dynamic_item(self):
        """Add item to dynamic combo"""
        text = self.new_item_input.text().strip()
        if text:
            self.dynamic_combo.addItem(text)
            self.new_item_input.clear()

    def _remove_dynamic_item(self):
        """Remove selected item from dynamic combo"""
        current_index = self.dynamic_combo.currentIndex()
        if current_index >= 0:
            self.dynamic_combo.removeItem(current_index)

    def _clear_dynamic_items(self):
        """Clear all items from dynamic combo"""
        self.dynamic_combo.clear()

    def _on_city_selected(self, text: str, data: dict):
        """Handle city selection with population data"""
        if data:
            population = data.get('population', 0)
            country = data.get('country', 'Unknown')
            self.searchable_data_label.setText(
                f"Selected: {text} (Population: {population:,}, Country: {country})"
            )
        else:
            self.searchable_data_label.setText(f"Selected: {text}")

    def _add_menu_item(self):
        """Add menu item to dynamic dropdown"""
        text = self.menu_item_input.text().strip()
        if text:
            self.dropdown_dynamic.add_menu_item(text, f"data_{len(self.dropdown_dynamic._menu_items)}")
            self.menu_item_input.clear()

    def _clear_menu_items(self):
        """Clear all menu items from dynamic dropdown"""
        self.dropdown_dynamic.clear_menu_items()

    def _load_performance_items(self, items: list):
        """Load performance test items"""
        self.perf_combo.clear()
        self.perf_combo.addItems(items)
        self.perf_label.setText(f"Items loaded: {len(items)}")

    def _enable_all_test_components(self):
        """Enable all test components"""
        components = [self.test_regular, self.test_multi, self.test_searchable, self.test_dropdown]
        for component in components:
            component.setEnabled(True)
        self._log_status("All test components enabled")

    def _disable_all_test_components(self):
        """Disable all test components"""
        components = [self.test_regular, self.test_multi, self.test_searchable, self.test_dropdown]
        for component in components:
            component.setEnabled(False)
        self._log_status("All test components disabled")

    def _reset_all_test_components(self):
        """Reset all test components"""
        self.test_regular.setCurrentIndex(0)
        self.test_multi.clear_selection()
        self.test_searchable.set_selected_text("")
        self._log_status("All test components reset")

    def _connect_test_components_to_logger(self):
        """Connect test components to status logger"""
        self.test_regular.currentTextChanged.connect(
            lambda text: self._log_status(f"Regular combo selected: {text}")
        )
        
        self.test_multi.selection_changed.connect(
            lambda items: self._log_status(f"Multi-select changed: {items}")
        )
        
        self.test_searchable.item_selected.connect(
            lambda text, data: self._log_status(f"Searchable selected: {text}")
        )
        
        self.test_dropdown.item_clicked.connect(
            lambda text, data: self._log_status(f"Dropdown action: {text}")
        )

    def _log_status(self, message: str):
        """Log status message"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_display.append(f"[{timestamp}] {message}")

    def _toggle_theme(self, theme_name: str):
        """Toggle between light and dark themes"""
        if theme_name == "Dark":
            theme_manager.set_theme_mode(ThemeMode.DARK)
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)


def main():
    """Run the combobox demo application"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show demo window
    demo = ComboBoxDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
