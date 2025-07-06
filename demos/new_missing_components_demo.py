"""
Demo showcasing the new missing components and refactored consistency
Demonstrates RadioButton, RadioGroup, SearchBox, and TreeView components
"""

import sys
from typing import List
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTabWidget, QLabel, QGroupBox,
                               QScrollArea, QFrame, QSplitter, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor

# Import the new components
from components.basic.forms.radio import FluentRadioButton, FluentRadioGroup
from components.basic.forms.searchbox import FluentSearchBox
from components.basic.navigation.treeview import FluentTreeView, FluentTreeNode, create_tree_node
from components.base.fluent_component_interface import FluentComponentSize, FluentComponentVariant


class NewComponentsDemo(QMainWindow):
    """Demo application for new Fluent components"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent UI - New Components Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Setup UI
        self._setup_ui()
        self._populate_demo_data()
        
    def _setup_ui(self):
        """Setup the demo UI"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel("New Fluent UI Components Demonstration")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Create tabbed interface
        self._tab_widget = QTabWidget()
        main_layout.addWidget(self._tab_widget)
        
        # Add tabs for different components
        self._setup_radio_tab()
        self._setup_search_tab()
        self._setup_tree_tab()
        self._setup_combination_tab()
        
    def _setup_radio_tab(self):
        """Setup radio button demo tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Individual radio buttons
        individual_group = QGroupBox("Individual Radio Buttons")
        individual_layout = QVBoxLayout()
        individual_group.setLayout(individual_layout)
        
        self._radio1 = FluentRadioButton("Option 1", size=FluentComponentSize.SMALL)
        self._radio2 = FluentRadioButton("Option 2", size=FluentComponentSize.MEDIUM)
        self._radio3 = FluentRadioButton("Option 3", size=FluentComponentSize.LARGE)
        
        individual_layout.addWidget(self._radio1)
        individual_layout.addWidget(self._radio2)
        individual_layout.addWidget(self._radio3)
        
        scroll_layout.addWidget(individual_group)
        
        # Radio groups
        groups_frame = QFrame()
        groups_layout = QHBoxLayout()
        groups_frame.setLayout(groups_layout)
        
        # Vertical radio group
        vertical_group = QGroupBox("Vertical Radio Group")
        vertical_layout = QVBoxLayout()
        vertical_group.setLayout(vertical_layout)
        
        self._vertical_radio_group = FluentRadioGroup(
            orientation=Qt.Orientation.Vertical,
            spacing=8
        )
        self._vertical_radio_group.add_radio("Red")
        self._vertical_radio_group.add_radio("Green")
        self._vertical_radio_group.add_radio("Blue")
        self._vertical_radio_group.add_radio("Yellow")
        
        vertical_layout.addWidget(self._vertical_radio_group)
        groups_layout.addWidget(vertical_group)
        
        # Horizontal radio group
        horizontal_group = QGroupBox("Horizontal Radio Group")
        horizontal_layout = QVBoxLayout()
        horizontal_group.setLayout(horizontal_layout)
        
        self._horizontal_radio_group = FluentRadioGroup(
            orientation=Qt.Orientation.Horizontal,
            spacing=12
        )
        self._horizontal_radio_group.add_radio("Small")
        self._horizontal_radio_group.add_radio("Medium")
        self._horizontal_radio_group.add_radio("Large")
        
        horizontal_layout.addWidget(self._horizontal_radio_group)
        groups_layout.addWidget(horizontal_group)
        
        scroll_layout.addWidget(groups_frame)
        
        # Size variations
        sizes_group = QGroupBox("Size Variations")
        sizes_layout = QHBoxLayout()
        sizes_group.setLayout(sizes_layout)
        
        for size in [FluentComponentSize.TINY, FluentComponentSize.SMALL, 
                     FluentComponentSize.MEDIUM, FluentComponentSize.LARGE, 
                     FluentComponentSize.XLARGE]:
            radio = FluentRadioButton(f"{size.value.title()} Radio", size=size)
            sizes_layout.addWidget(radio)
        
        scroll_layout.addWidget(sizes_group)
        
        # Connect signals
        self._vertical_radio_group.selection_changed.connect(
            lambda idx: self._show_selection_message(f"Vertical group selected: index {idx}")
        )
        self._horizontal_radio_group.value_changed.connect(
            lambda val: self._show_selection_message(f"Horizontal group selected: {val}")
        )
        
        self._tab_widget.addTab(tab, "Radio Buttons")
    
    def _setup_search_tab(self):
        """Setup search box demo tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Basic search box
        basic_group = QGroupBox("Basic Search Box")
        basic_layout = QVBoxLayout()
        basic_group.setLayout(basic_layout)
        
        self._basic_search = FluentSearchBox(placeholder="Search anything...")
        basic_layout.addWidget(self._basic_search)
        layout.addWidget(basic_group)
        
        # Search with suggestions
        suggestions_group = QGroupBox("Search with Suggestions")
        suggestions_layout = QVBoxLayout()
        suggestions_group.setLayout(suggestions_layout)
        
        self._suggestions_search = FluentSearchBox(placeholder="Search with suggestions...")
        self._suggestions_search.set_suggestions([
            "Apple", "Banana", "Cherry", "Date", "Elderberry",
            "Fig", "Grape", "Honeydew", "Kiwi", "Lemon",
            "Mango", "Orange", "Pear", "Quince", "Raspberry"
        ])
        suggestions_layout.addWidget(self._suggestions_search)
        layout.addWidget(suggestions_group)
        
        # Size variations
        sizes_group = QGroupBox("Size Variations")
        sizes_layout = QVBoxLayout()
        sizes_group.setLayout(sizes_layout)
        
        for size in [FluentComponentSize.SMALL, FluentComponentSize.MEDIUM, 
                     FluentComponentSize.LARGE]:
            search = FluentSearchBox(
                placeholder=f"{size.value.title()} search box...",
                size=size
            )
            sizes_layout.addWidget(search)
        
        layout.addWidget(sizes_group)
        
        # Results area
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)
        
        self._results_label = QLabel("Search results will appear here...")
        self._results_label.setStyleSheet("padding: 10px; background: #f5f5f5; border-radius: 4px;")
        results_layout.addWidget(self._results_label)
        layout.addWidget(results_group)
        
        # Connect signals
        self._basic_search.search_requested.connect(
            lambda text: self._results_label.setText(f"Basic search: '{text}'")
        )
        self._suggestions_search.search_requested.connect(
            lambda text: self._results_label.setText(f"Suggestions search: '{text}'")
        )
        self._suggestions_search.suggestion_selected.connect(
            lambda text: self._results_label.setText(f"Suggestion selected: '{text}'")
        )
        
        layout.addStretch()
        self._tab_widget.addTab(tab, "Search Box")
    
    def _setup_tree_tab(self):
        """Setup tree view demo tab"""
        tab = QWidget()
        layout = QHBoxLayout()
        tab.setLayout(layout)
        
        # Tree view
        tree_group = QGroupBox("Hierarchical Data Tree")
        tree_layout = QVBoxLayout()
        tree_group.setLayout(tree_layout)
        
        self._tree_view = FluentTreeView(show_header=True)
        self._tree_view.set_header_labels(["Name", "Type"])
        tree_layout.addWidget(self._tree_view)
        
        layout.addWidget(tree_group, 2)
        
        # Details panel
        details_group = QGroupBox("Selected Item Details")
        details_layout = QVBoxLayout()
        details_group.setLayout(details_layout)
        
        self._details_label = QLabel("Select an item to see details...")
        self._details_label.setStyleSheet("padding: 10px; background: #f5f5f5; border-radius: 4px;")
        self._details_label.setWordWrap(True)
        details_layout.addWidget(self._details_label)
        
        # Tree operations
        operations_group = QGroupBox("Tree Operations")
        operations_layout = QVBoxLayout()
        operations_group.setLayout(operations_layout)
        
        from PySide6.QtWidgets import QPushButton
        expand_all_btn = QPushButton("Expand All")
        collapse_all_btn = QPushButton("Collapse All")
        
        expand_all_btn.clicked.connect(self._tree_view.expand_all)
        collapse_all_btn.clicked.connect(self._tree_view.collapse_all)
        
        operations_layout.addWidget(expand_all_btn)
        operations_layout.addWidget(collapse_all_btn)
        details_layout.addWidget(operations_group)
        
        details_layout.addStretch()
        layout.addWidget(details_group, 1)
        
        # Connect tree signals
        self._tree_view.item_selected.connect(self._on_tree_item_selected)
        self._tree_view.item_double_clicked.connect(self._on_tree_item_double_clicked)
        
        self._tab_widget.addTab(tab, "Tree View")
    
    def _setup_combination_tab(self):
        """Setup combined components demo"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Split layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Search and filters
        left_panel = QFrame()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Search section
        search_group = QGroupBox("Search & Filter")
        search_layout = QVBoxLayout()
        search_group.setLayout(search_layout)
        
        self._combo_search = FluentSearchBox(placeholder="Search items...")
        search_layout.addWidget(self._combo_search)
        
        # Filter radio group
        filter_group = FluentRadioGroup(orientation=Qt.Orientation.Vertical)
        filter_group.add_radio("All Items")
        filter_group.add_radio("Folders Only")
        filter_group.add_radio("Files Only")
        filter_group.set_selected_index(0)
        search_layout.addWidget(filter_group)
        
        left_layout.addWidget(search_group)
        left_layout.addStretch()
        splitter.addWidget(left_panel)
        
        # Right panel - Tree with filtered results
        right_panel = QFrame()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        results_label = QLabel("Filtered Results")
        results_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        right_layout.addWidget(results_label)
        
        self._combo_tree = FluentTreeView(show_header=True)
        self._combo_tree.set_header_labels(["Name", "Size", "Modified"])
        right_layout.addWidget(self._combo_tree)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 600])
        
        self._tab_widget.addTab(tab, "Combined Demo")
    
    def _populate_demo_data(self):
        """Populate demo data for tree views"""
        # Create sample tree data
        tree_data = [
            create_tree_node("Documents", "folder", expanded=True, children=[
                create_tree_node("Projects", "folder", children=[
                    create_tree_node("Web App", "folder", children=[
                        create_tree_node("src", "folder", children=[
                            create_tree_node("main.py", "file"),
                            create_tree_node("utils.py", "file"),
                        ]),
                        create_tree_node("README.md", "file"),
                    ]),
                    create_tree_node("Mobile App", "folder", children=[
                        create_tree_node("MainActivity.java", "file"),
                        create_tree_node("layout.xml", "file"),
                    ]),
                ]),
                create_tree_node("Reports", "folder", children=[
                    create_tree_node("Q1 Report.pdf", "file"),
                    create_tree_node("Q2 Report.pdf", "file"),
                ]),
            ]),
            create_tree_node("Pictures", "folder", expanded=True, children=[
                create_tree_node("Vacation", "folder", children=[
                    create_tree_node("beach.jpg", "file"),
                    create_tree_node("sunset.jpg", "file"),
                ]),
                create_tree_node("Family", "folder", children=[
                    create_tree_node("birthday.jpg", "file"),
                    create_tree_node("wedding.jpg", "file"),
                ]),
            ]),
            create_tree_node("Music", "folder", children=[
                create_tree_node("Rock", "folder", children=[
                    create_tree_node("song1.mp3", "file"),
                    create_tree_node("song2.mp3", "file"),
                ]),
                create_tree_node("Jazz", "folder", children=[
                    create_tree_node("blues.mp3", "file"),
                    create_tree_node("smooth.mp3", "file"),
                ]),
            ]),
        ]
        
        # Set data for tree views
        self._tree_view.set_data(tree_data)
        self._combo_tree.set_data(tree_data)
    
    def _on_tree_item_selected(self, node: FluentTreeNode):
        """Handle tree item selection"""
        details = f"""
        <b>Name:</b> {node.text}<br>
        <b>Type:</b> {node.value}<br>
        <b>Children:</b> {len(node.children) if node.children else 0}<br>
        <b>Expanded:</b> {node.expanded}<br>
        <b>Selectable:</b> {node.selectable}
        """
        self._details_label.setText(details)
    
    def _on_tree_item_double_clicked(self, node: FluentTreeNode):
        """Handle tree item double click"""
        QMessageBox.information(
            self,
            "Item Double Clicked",
            f"You double-clicked on: {node.text}\nType: {node.value}"
        )
    
    def _show_selection_message(self, message: str):
        """Show selection message in status bar"""
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage(message, 3000)


def main():
    """Main function to run the demo"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent UI New Components Demo")
    app.setApplicationVersion("2.0.0")
    
    # Create and show the demo
    demo = NewComponentsDemo()
    demo.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
