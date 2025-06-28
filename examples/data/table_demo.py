#!/usr/bin/env python3
"""
Fluent Table Component Demo

This example demonstrates the usage of FluentTable component with various configurations,
including data display, sorting, filtering, and theming.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox, QPushButton, QTableWidgetItem
from PySide6.QtCore import Qt


def main():
    """Run the table demo application."""
    app = QApplication(sys.argv)
    
    # Import after QApplication is created
    from components.data.display.table import FluentTableWidget
    
    class TableDemo(QMainWindow):
        """Main demo window showcasing Fluent table components."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Fluent Table Demo")
            self.setGeometry(200, 200, 1000, 700)
            
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(20)
            main_layout.setContentsMargins(20, 20, 20, 20)
            
            # Add title
            title = QLabel("Fluent Table Components Demo")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
            main_layout.addWidget(title)
            
            # Create table sections
            self.create_basic_table(main_layout)
            self.create_interactive_table(main_layout)
            
            main_layout.addStretch()
        
        def create_basic_table(self, parent_layout):
            """Create basic table examples."""
            group = QGroupBox("Basic Table Widget")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Basic table widget
            self.basic_table = FluentTableWidget()
            
            # Set up table headers
            headers = ["Name", "Age", "Department", "Salary", "Status"]
            self.basic_table.setColumnCount(len(headers))
            self.basic_table.setHorizontalHeaderLabels(headers)
            
            # Sample data
            data = [
                ["Alice Johnson", "28", "Engineering", "$75,000", "Active"],
                ["Bob Smith", "35", "Marketing", "$65,000", "Active"],
                ["Carol Davis", "42", "Finance", "$80,000", "Active"],
                ["David Wilson", "31", "Engineering", "$72,000", "On Leave"],
                ["Eva Brown", "29", "HR", "$58,000", "Active"],
                ["Frank Miller", "38", "Engineering", "$78,000", "Active"],
                ["Grace Lee", "26", "Design", "$62,000", "Active"],
                ["Henry Chen", "45", "Management", "$95,000", "Active"]
            ]
            
            # Populate table with data
            self.basic_table.setRowCount(len(data))
            for row, row_data in enumerate(data):
                for col, cell_data in enumerate(row_data):
                    self.basic_table.setItem(row, col, QTableWidgetItem(cell_data))
            
            # Resize columns to content
            self.basic_table.resizeColumnsToContents()
            
            layout.addWidget(QLabel("Employee Data Table:"))
            layout.addWidget(self.basic_table)
            
            parent_layout.addWidget(group)
        
        def create_interactive_table(self, parent_layout):
            """Create interactive table examples."""
            group = QGroupBox("Interactive Table with Controls")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Interactive table widget
            self.interactive_table = FluentTableWidget()
            
            # Set up headers
            headers = ["Product", "Category", "Price", "Stock", "Rating"]
            self.interactive_table.setColumnCount(len(headers))
            self.interactive_table.setHorizontalHeaderLabels(headers)
            
            # Sample product data
            self.product_data = [
                ["Laptop Pro", "Electronics", "$1,299", "15", "4.5"],
                ["Office Chair", "Furniture", "$299", "32", "4.2"],
                ["Coffee Maker", "Appliances", "$89", "8", "4.7"],
                ["Smartphone", "Electronics", "$699", "24", "4.3"],
                ["Desk Lamp", "Furniture", "$45", "56", "4.1"],
                ["Tablet", "Electronics", "$499", "18", "4.4"],
                ["Bookshelf", "Furniture", "$149", "12", "4.0"],
                ["Headphones", "Electronics", "$179", "41", "4.6"]
            ]
            
            self.populate_interactive_table()
            
            # Control buttons
            control_layout = QHBoxLayout()
            
            add_btn = QPushButton("Add Product")
            add_btn.clicked.connect(self.add_product)
            
            remove_btn = QPushButton("Remove Selected")
            remove_btn.clicked.connect(self.remove_selected)
            
            sort_btn = QPushButton("Sort by Price")
            sort_btn.clicked.connect(self.sort_by_price)
            
            clear_btn = QPushButton("Clear Table")
            clear_btn.clicked.connect(self.clear_table)
            
            control_layout.addWidget(add_btn)
            control_layout.addWidget(remove_btn)
            control_layout.addWidget(sort_btn)
            control_layout.addWidget(clear_btn)
            control_layout.addStretch()
            
            layout.addWidget(QLabel("Product Inventory Table:"))
            layout.addWidget(self.interactive_table)
            layout.addLayout(control_layout)
            
            # Status label
            self.table_status = QLabel(f"Total products: {len(self.product_data)}")
            layout.addWidget(self.table_status)
            
            # Connect selection changes
            self.interactive_table.itemSelectionChanged.connect(self.on_selection_changed)
            
            parent_layout.addWidget(group)
        
        def populate_interactive_table(self):
            """Populate the interactive table with product data."""
            self.interactive_table.setRowCount(len(self.product_data))
            for row, row_data in enumerate(self.product_data):
                for col, cell_data in enumerate(row_data):
                    self.interactive_table.setItem(row, col, QTableWidgetItem(cell_data))
            
            self.interactive_table.resizeColumnsToContents()
            self.update_status()
        
        def add_product(self):
            """Add a new product to the table."""
            new_products = [
                ["Gaming Mouse", "Electronics", "$79", "25", "4.4"],
                ["Monitor Stand", "Furniture", "$35", "18", "4.0"],
                ["Wireless Keyboard", "Electronics", "$125", "14", "4.2"],
                ["Plant Pot", "Decor", "$25", "30", "4.3"]
            ]
            
            # Add a random new product
            import random
            new_product = random.choice(new_products)
            self.product_data.append(new_product)
            
            # Update table
            row = self.interactive_table.rowCount()
            self.interactive_table.setRowCount(row + 1)
            for col, cell_data in enumerate(new_product):
                self.interactive_table.setItem(row, col, QTableWidgetItem(cell_data))
            
            self.interactive_table.resizeColumnsToContents()
            self.update_status()
        
        def remove_selected(self):
            """Remove selected rows from the table."""
            selected_rows = set()
            for item in self.interactive_table.selectedItems():
                selected_rows.add(item.row())
            
            if not selected_rows:
                return
            
            # Remove from data (in reverse order to maintain indices)
            for row in sorted(selected_rows, reverse=True):
                if 0 <= row < len(self.product_data):
                    del self.product_data[row]
            
            # Refresh table
            self.populate_interactive_table()
        
        def sort_by_price(self):
            """Sort table by price column."""
            # Extract price values and sort
            def price_key(item):
                price_str = item[2].replace('$', '').replace(',', '')
                return float(price_str)
            
            self.product_data.sort(key=price_key, reverse=True)
            self.populate_interactive_table()
        
        def clear_table(self):
            """Clear all data from the table."""
            self.product_data.clear()
            self.interactive_table.setRowCount(0)
            self.update_status()
        
        def on_selection_changed(self):
            """Handle table selection changes."""
            selected_count = len(self.interactive_table.selectedItems()) // self.interactive_table.columnCount()
            if selected_count > 0:
                self.table_status.setText(f"Total products: {len(self.product_data)} | Selected: {selected_count}")
            else:
                self.table_status.setText(f"Total products: {len(self.product_data)}")
        
        def update_status(self):
            """Update the status label."""
            self.table_status.setText(f"Total products: {len(self.product_data)}")
    
    # Set application properties
    app.setApplicationName("Fluent Table Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = TableDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
