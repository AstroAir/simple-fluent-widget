#!/usr/bin/env python3
"""
Fluent Dock Panel Component Demo

This example demonstrates the comprehensive usage of FluentDockPanel component with various configurations,
including dock positioning, resizing, responsive behavior, and dynamic dock management.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QGroupBox, QPushButton, QTextEdit, QListWidget, 
    QTreeWidget, QTreeWidgetItem, QSplitter, QFrame, QSlider,
    QCheckBox, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt


def main():
    """Run the dock panel demo application."""
    app = QApplication(sys.argv)
    
    # Import after QApplication is created
    from components.layout.dock_panel import FluentDockPanel, DockPosition
    
    class DockPanelDemo(QMainWindow):
        """Main demo window showcasing Fluent dock panel components."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Fluent Dock Panel Demo")
            self.setGeometry(100, 100, 1200, 800)
            
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(10)
            main_layout.setContentsMargins(10, 10, 10, 10)
            
            # Add title
            title = QLabel("Fluent Dock Panel Components Demo")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
            main_layout.addWidget(title)
            
            # Create control panel
            self.create_control_panel(main_layout)
            
            # Create dock panel examples
            self.create_basic_dock_panel(main_layout)
            
        def create_control_panel(self, parent_layout):
            """Create control panel for dock panel manipulation."""
            control_group = QGroupBox("Dock Panel Controls")
            control_layout = QHBoxLayout(control_group)
            
            # Position controls
            position_label = QLabel("Add Widget Position:")
            self.position_combo = QComboBox()
            self.position_combo.addItems(["Left", "Top", "Right", "Bottom", "Fill"])
            
            # Size controls
            size_label = QLabel("Size:")
            self.size_spin = QSpinBox()
            self.size_spin.setRange(50, 400)
            self.size_spin.setValue(200)
            
            # Add widget button
            add_btn = QPushButton("Add Widget")
            add_btn.clicked.connect(self.add_dock_widget)
            
            # Remove widget button
            remove_btn = QPushButton("Remove Selected")
            remove_btn.clicked.connect(self.remove_selected_widget)
            
            # Toggle responsive mode
            self.responsive_check = QCheckBox("Responsive Mode")
            self.responsive_check.setChecked(True)
            self.responsive_check.toggled.connect(self.toggle_responsive_mode)
            
            control_layout.addWidget(position_label)
            control_layout.addWidget(self.position_combo)
            control_layout.addWidget(size_label)
            control_layout.addWidget(self.size_spin)
            control_layout.addWidget(add_btn)
            control_layout.addWidget(remove_btn)
            control_layout.addWidget(self.responsive_check)
            control_layout.addStretch()
            
            parent_layout.addWidget(control_group)
            
        def create_basic_dock_panel(self, parent_layout):
            """Create basic dock panel example."""
            dock_group = QGroupBox("Interactive Dock Panel")
            dock_layout = QVBoxLayout(dock_group)
            
            # Create dock panel
            self.dock_panel = FluentDockPanel()
            self.dock_panel.setMinimumHeight(500)
            
            # Create initial widgets
            self.create_initial_dock_widgets()
            
            # Status display
            self.status_label = QLabel("Ready - Use controls above to add/remove dock widgets")
            self.status_label.setStyleSheet("color: #605e5c; font-style: italic;")
            
            dock_layout.addWidget(self.dock_panel)
            dock_layout.addWidget(self.status_label)
            
            parent_layout.addWidget(dock_group)
            
        def create_initial_dock_widgets(self):
            """Create initial dock widgets for demonstration."""
            # Left panel - File explorer
            left_widget = self.create_file_explorer()
            self.dock_panel.add_dock_widget(left_widget, DockPosition.LEFT, 200)
            
            # Right panel - Properties
            right_widget = self.create_properties_panel()
            self.dock_panel.add_dock_widget(right_widget, DockPosition.RIGHT, 250)
            
            # Bottom panel - Output
            bottom_widget = self.create_output_panel()
            self.dock_panel.add_dock_widget(bottom_widget, DockPosition.BOTTOM, 150)
            
            # Center panel - Main content
            center_widget = self.create_main_content()
            self.dock_panel.add_dock_widget(center_widget, DockPosition.FILL)
            
            # Connect signals
            self.dock_panel.dock_position_changed.connect(self.on_dock_position_changed)
            self.dock_panel.dock_size_changed.connect(self.on_dock_size_changed)
            
        def create_file_explorer(self):
            """Create a file explorer widget."""
            widget = QFrame()
            layout = QVBoxLayout(widget)
            
            title = QLabel("📁 File Explorer")
            title.setStyleSheet("font-weight: bold; color: #323130; padding: 5px;")
            
            tree = QTreeWidget()
            tree.setHeaderLabel("Files")
            
            # Add sample items
            root = QTreeWidgetItem(tree, ["Project"])
            src_folder = QTreeWidgetItem(root, ["src"])
            QTreeWidgetItem(src_folder, ["main.py"])
            QTreeWidgetItem(src_folder, ["utils.py"])
            docs_folder = QTreeWidgetItem(root, ["docs"])
            QTreeWidgetItem(docs_folder, ["README.md"])
            
            tree.expandAll()
            
            layout.addWidget(title)
            layout.addWidget(tree)
            
            widget.setStyleSheet("""
                QFrame {
                    background-color: #f3f2f1;
                    border: 1px solid #edebe9;
                    border-radius: 4px;
                }
            """)
            
            return widget
            
        def create_properties_panel(self):
            """Create a properties panel widget."""
            widget = QFrame()
            layout = QVBoxLayout(widget)
            
            title = QLabel("🔧 Properties")
            title.setStyleSheet("font-weight: bold; color: #323130; padding: 5px;")
            
            # Property controls
            prop_list = QListWidget()
            prop_list.addItems([
                "Name: dock_panel",
                "Type: FluentDockPanel", 
                "Width: 1200px",
                "Height: 800px",
                "Responsive: Yes"
            ])
            
            layout.addWidget(title)
            layout.addWidget(prop_list)
            
            widget.setStyleSheet("""
                QFrame {
                    background-color: #faf9f8;
                    border: 1px solid #edebe9;
                    border-radius: 4px;
                }
            """)
            
            return widget
            
        def create_output_panel(self):
            """Create an output panel widget."""
            widget = QFrame()
            layout = QVBoxLayout(widget)
            
            title = QLabel("📄 Output")
            title.setStyleSheet("font-weight: bold; color: #323130; padding: 5px;")
            
            output = QTextEdit()
            output.setPlainText("""Dock Panel Demo Output:
- Left panel added at position LEFT with size 200px
- Right panel added at position RIGHT with size 250px  
- Bottom panel added at position BOTTOM with size 150px
- Center panel added at position FILL

Ready for interaction...
""")
            output.setMaximumHeight(120)
            
            layout.addWidget(title)
            layout.addWidget(output)
            
            widget.setStyleSheet("""
                QFrame {
                    background-color: #f8f8f8;
                    border: 1px solid #edebe9;
                    border-radius: 4px;
                }
            """)
            
            return widget
            
        def create_main_content(self):
            """Create main content widget."""
            widget = QFrame()
            layout = QVBoxLayout(widget)
            
            title = QLabel("📋 Main Content Area")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #323130; padding: 10px;")
            
            content = QLabel("""
            <h2>Welcome to Dock Panel Demo</h2>
            <p>This is the main content area (FILL position) of the dock panel.</p>
            <p>Features demonstrated:</p>
            <ul>
                <li>Dockable panels on all sides (Left, Top, Right, Bottom)</li>
                <li>Resizable dock areas with splitters</li>
                <li>Fill area that adapts to available space</li>
                <li>Dynamic widget addition and removal</li>
                <li>Responsive behavior for different screen sizes</li>
                <li>Signal handling for position and size changes</li>
            </ul>
            <p>Use the controls above to experiment with adding and removing dock widgets!</p>
            """)
            content.setWordWrap(True)
            content.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            layout.addWidget(title)
            layout.addWidget(content)
            layout.addStretch()
            
            widget.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #edebe9;
                    border-radius: 4px;
                    padding: 10px;
                }
            """)
            
            return widget
            
        def add_dock_widget(self):
            """Add a new dock widget."""
            position_map = {
                "Left": DockPosition.LEFT,
                "Top": DockPosition.TOP,
                "Right": DockPosition.RIGHT,
                "Bottom": DockPosition.BOTTOM,
                "Fill": DockPosition.FILL
            }
            
            position_text = self.position_combo.currentText()
            position = position_map[position_text]
            size = self.size_spin.value()
            
            # Create new widget
            widget = QFrame()
            layout = QVBoxLayout(widget)
            
            title = QLabel(f"🆕 New {position_text} Panel")
            title.setStyleSheet("font-weight: bold; color: #323130; padding: 5px;")
            
            content = QLabel(f"This is a dynamically added {position_text.lower()} panel.\nSize: {size}px")
            content.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            layout.addWidget(title)
            layout.addWidget(content)
            
            widget.setStyleSheet("""
                QFrame {
                    background-color: #e1dfdd;
                    border: 1px solid #c8c6c4;
                    border-radius: 4px;
                }
            """)
            
            # Add to dock panel
            if position == DockPosition.FILL:
                self.dock_panel.add_dock_widget(widget, position)
            else:
                self.dock_panel.add_dock_widget(widget, position, size)
                
            self.status_label.setText(f"Added {position_text} panel with size {size}px")
            
        def remove_selected_widget(self):
            """Remove the last added widget (simple demo)."""
            # This is a simplified example - in a real app you'd track widgets properly
            self.status_label.setText("Widget removal functionality would be implemented here")
            
        def toggle_responsive_mode(self, enabled):
            """Toggle responsive mode."""
            # This would control responsive behavior in a real implementation
            self.status_label.setText(f"Responsive mode: {'Enabled' if enabled else 'Disabled'}")
            
        def on_dock_position_changed(self, widget, position):
            """Handle dock position changes."""
            self.status_label.setText(f"Widget position changed to: {position.value}")
            
        def on_dock_size_changed(self, widget, size):
            """Handle dock size changes."""
            self.status_label.setText(f"Widget size changed to: {size}px")
    
    # Create and show demo
    demo = DockPanelDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
