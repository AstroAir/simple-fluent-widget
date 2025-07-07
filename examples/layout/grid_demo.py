#!/usr/bin/env python3
"""
Fluent Grid Component Demo
Demonstrates responsive grid layout with dynamic item management
"""

import sys
from pathlib import Path
from random import randint

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QSpinBox, QLabel, QFrame, QSlider
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from components.layout.grid import (
    FluentGrid, GridSpacing, GridItemAlignment, FluentGridBuilder
)

class GridDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Grid Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create controls
        self.create_controls(main_layout)
        
        # Create grid using builder pattern
        self.grid = (FluentGridBuilder()
                    .with_min_column_width(200)
                    .with_max_columns(6)
                    .with_spacing(GridSpacing.MEDIUM)
                    .build())
        
        main_layout.addWidget(self.grid)
        
        # Initial items
        for _ in range(6):
            self.add_grid_item()

    def create_controls(self, parent_layout):
        """Create control panel for grid properties"""
        control_card = QFrame()
        control_layout = QHBoxLayout(control_card)
        
        # Spacing selector
        self.spacing_combo = QComboBox()
        self.spacing_combo.addItems([s.name for s in GridSpacing])
        self.spacing_combo.currentIndexChanged.connect(self.update_grid_properties)
        
        # Column controls
        self.min_width_spin = QSpinBox()
        self.min_width_spin.setRange(100, 500)
        self.min_width_spin.setValue(200)
        self.min_width_spin.valueChanged.connect(self.update_grid_properties)
        
        self.max_col_spin = QSpinBox()
        self.max_col_spin.setRange(-1, 12)
        self.max_col_spin.setValue(6)
        self.max_col_spin.valueChanged.connect(self.update_grid_properties)
        
        # Item controls
        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(lambda: self.add_grid_item())
        remove_btn = QPushButton("Remove Item")
        remove_btn.clicked.connect(self.remove_grid_item)
        
        control_layout.addWidget(QLabel("Spacing:"))
        control_layout.addWidget(self.spacing_combo)
        control_layout.addWidget(QLabel("Min Width:"))
        control_layout.addWidget(self.min_width_spin)
        control_layout.addWidget(QLabel("Max Columns:"))
        control_layout.addWidget(self.max_col_spin)
        control_layout.addWidget(add_btn)
        control_layout.addWidget(remove_btn)
        
        parent_layout.addWidget(control_card)

    def add_grid_item(self):
        """Add a new grid item with random properties"""
        item = QFrame()
        item.setMinimumSize(150, 100)
        
        # Random properties
        color = QColor(randint(100,255), randint(100,255), randint(100,255))
        column_span = randint(1, 2)
        alignment = list(GridItemAlignment)[randint(0, 3)]
        
        # Item content
        layout = QVBoxLayout(item)
        title = QLabel(f"Span: {column_span}\nAlign: {alignment.value}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        
        # Styling
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {color.name()};
                border: 2px solid #ffffff;
                border-radius: 8px;
                padding: 10px;
            }}
            QLabel {{
                color: #ffffff;
                font-weight: bold;
            }}
        """)
        
        # Add to grid with random span
        self.grid.add_item(item, 
                          column_span=column_span,
                          alignment=alignment)

    def remove_grid_item(self):
        """Remove the first QFrame item from the grid, if any"""
        frame = self.grid.findChild(QFrame)
        if frame is not None:
            self.grid.remove_item(frame)

    def update_grid_properties(self):
        """Update grid properties from controls"""
        self.grid.set_spacing(GridSpacing[self.spacing_combo.currentText()])
        self.grid.set_min_column_width(self.min_width_spin.value())
        self.grid.set_max_columns(self.max_col_spin.value())

def main():
    app = QApplication(sys.argv)
    demo = GridDemo()
    demo.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()