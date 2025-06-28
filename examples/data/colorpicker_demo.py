#!/usr/bin/env python3
"""
Fluent Color Picker Component Demo

This example demonstrates the usage of FluentColorPicker and related color components 
with various configurations, including color selection, validation, and theming.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


def main():
    """Run the color picker demo application."""
    app = QApplication(sys.argv)
    
    # Import after QApplication is created
    from components.data.input.colorpicker import FluentColorPicker, FluentColorButton
    
    class ColorPickerDemo(QMainWindow):
        """Main demo window showcasing Fluent color picker components."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Fluent Color Picker Demo")
            self.setGeometry(200, 200, 900, 700)
            
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(20)
            main_layout.setContentsMargins(20, 20, 20, 20)
            
            # Add title
            title = QLabel("Fluent Color Picker Components Demo")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
            main_layout.addWidget(title)
            
            # Create color picker sections
            self.create_basic_color_picker(main_layout)
            self.create_color_buttons(main_layout)
            self.create_preset_colors(main_layout)
            
            main_layout.addStretch()
        
        def create_basic_color_picker(self, parent_layout):
            """Create basic color picker examples."""
            group = QGroupBox("Basic Color Picker Widget")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Basic color picker widget
            self.basic_picker = FluentColorPicker()
            
            # Set default color
            default_color = QColor(64, 158, 255)  # Fluent blue
            self.basic_picker.set_color(default_color)
            
            layout.addWidget(QLabel("Standard Color Picker Widget:"))
            layout.addWidget(self.basic_picker)
            
            # Status label
            self.basic_status = QLabel(f"Selected Color: {default_color.name()}")
            layout.addWidget(self.basic_status)
            
            # Connect color change signal
            self.basic_picker.colorChanged.connect(self.on_basic_color_changed)
            
            parent_layout.addWidget(group)
        
        def create_color_buttons(self, parent_layout):
            """Create color button examples."""
            group = QGroupBox("Color Buttons")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Color buttons layout
            buttons_layout = QHBoxLayout()
            
            # Create color buttons with different preset colors
            colors = [
                (QColor(255, 99, 99), "Red"),
                (QColor(99, 255, 99), "Green"), 
                (QColor(99, 99, 255), "Blue"),
                (QColor(255, 255, 99), "Yellow"),
                (QColor(255, 99, 255), "Magenta"),
                (QColor(99, 255, 255), "Cyan")
            ]
            
            self.color_buttons = []
            for color, name in colors:
                btn = FluentColorButton(color)
                btn.setToolTip(f"{name} Color")
                btn.colorSelected.connect(lambda c, n=name: self.on_color_button_clicked(c, n))
                self.color_buttons.append(btn)
                buttons_layout.addWidget(btn)
            
            buttons_layout.addStretch()
            
            # Status for color buttons
            self.button_status = QLabel("Click a color button to select")
            
            layout.addWidget(QLabel("Color Selection Buttons:"))
            layout.addLayout(buttons_layout)
            layout.addWidget(self.button_status)
            
            parent_layout.addWidget(group)
        
        def create_preset_colors(self, parent_layout):
            """Create preset color palette example."""
            group = QGroupBox("Interactive Color Controls")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Interactive color picker
            self.interactive_picker = FluentColorPicker()
            
            # Control buttons
            control_layout = QHBoxLayout()
            
            random_btn = QPushButton("Random Color")
            random_btn.clicked.connect(self.set_random_color)
            
            reset_btn = QPushButton("Reset to Blue")
            reset_btn.clicked.connect(self.reset_to_blue)
            
            copy_btn = QPushButton("Copy Color")
            copy_btn.clicked.connect(self.copy_color)
            
            control_layout.addWidget(random_btn)
            control_layout.addWidget(reset_btn)
            control_layout.addWidget(copy_btn)
            control_layout.addStretch()
            
            layout.addWidget(QLabel("Interactive Color Picker with Controls:"))
            layout.addWidget(self.interactive_picker)
            layout.addLayout(control_layout)
            
            # Status label
            self.interactive_status = QLabel("Select a color or use controls")
            layout.addWidget(self.interactive_status)
            
            # Connect signals
            self.interactive_picker.colorChanged.connect(self.on_interactive_color_changed)
            
            parent_layout.addWidget(group)
        
        def on_basic_color_changed(self, color):
            """Handle basic color picker color change."""
            self.basic_status.setText(f"Selected Color: {color.name()} (RGB: {color.red()}, {color.green()}, {color.blue()})")
        
        def on_color_button_clicked(self, color, name):
            """Handle color button click."""
            self.button_status.setText(f"{name} selected: {color.name()}")
        
        def on_interactive_color_changed(self, color):
            """Handle interactive color picker color change."""
            hsv = color.getHsv()
            self.interactive_status.setText(f"Color: {color.name()} | HSV: ({hsv[0]}, {hsv[1]}, {hsv[2]})")
        
        def set_random_color(self):
            """Set a random color."""
            import random
            color = QColor(
                random.randint(0, 255),
                random.randint(0, 255), 
                random.randint(0, 255)
            )
            self.interactive_picker.set_color(color)
        
        def reset_to_blue(self):
            """Reset to Fluent blue color."""
            blue = QColor(64, 158, 255)
            self.interactive_picker.set_color(blue)
        
        def copy_color(self):
            """Copy current color to clipboard."""
            color = self.interactive_picker.get_color()
            color_text = color.name()
            
            clipboard = QApplication.clipboard()
            clipboard.setText(color_text)
            
            self.interactive_status.setText(f"Copied to clipboard: {color_text}")
    
    # Set application properties
    app.setApplicationName("Fluent Color Picker Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = ColorPickerDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
