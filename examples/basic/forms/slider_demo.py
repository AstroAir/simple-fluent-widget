#!/usr/bin/env python3
"""
Fluent Slider Component Demo

This example demonstrates the usage of FluentSlider components with various configurations,
including basic sliders, range sliders, vertical sliders, and customized styling.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox
from PySide6.QtCore import Qt

from components.basic.forms.slider import FluentSlider, FluentRangeSlider
from core.theme import theme_manager


class SliderDemo(QMainWindow):
    """Main demo window showcasing Fluent slider components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Slider Demo")
        self.setGeometry(200, 200, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add title
        title = QLabel("Fluent Slider Components Demo")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Create demo sections
        self.create_basic_sliders(main_layout)
        self.create_range_sliders(main_layout)
        self.create_vertical_sliders(main_layout)
        self.create_styled_sliders(main_layout)
        
        main_layout.addStretch()
        
    def create_basic_sliders(self, parent_layout):
        """Create basic slider examples."""
        group = QGroupBox("Basic Sliders")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Basic horizontal slider
        basic_slider = FluentSlider(orientation=Qt.Orientation.Horizontal, minimum=0, maximum=100, value=50)
        
        basic_label = QLabel("Value: 50")
        basic_slider.valueChanged.connect(lambda v: basic_label.setText(f"Value: {v}"))
        
        layout.addWidget(QLabel("Basic Horizontal Slider (0-100):"))
        layout.addWidget(basic_slider)
        layout.addWidget(basic_label)
        layout.addSpacing(10)
        
        # Slider with step interval
        step_slider = FluentSlider(orientation=Qt.Orientation.Horizontal, minimum=0, maximum=50, value=25)
        step_slider.setSingleStep(5)
        
        step_label = QLabel("Value: 25")
        step_slider.valueChanged.connect(lambda v: step_label.setText(f"Value: {v}"))
        
        layout.addWidget(QLabel("Stepped Slider (Step: 5):"))
        layout.addWidget(step_slider)
        layout.addWidget(step_label)
        layout.addSpacing(10)
        
        # Disabled slider
        disabled_slider = FluentSlider(orientation=Qt.Orientation.Horizontal, minimum=0, maximum=100, value=30)
        disabled_slider.setEnabled(False)
        
        layout.addWidget(QLabel("Disabled Slider:"))
        layout.addWidget(disabled_slider)
        
        parent_layout.addWidget(group)
        
    def create_range_sliders(self, parent_layout):
        """Create range slider examples."""
        group = QGroupBox("Range Sliders")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Basic range slider
        range_slider = FluentRangeSlider(minimum=0, maximum=100, low_value=20, high_value=80)
        
        range_label = QLabel("Range: 20 - 80")
        range_slider.range_changed.connect(
            lambda min_val, max_val: range_label.setText(f"Range: {min_val} - {max_val}")
        )
        
        layout.addWidget(QLabel("Range Slider (0-100):"))
        layout.addWidget(range_slider)
        layout.addWidget(range_label)
        layout.addSpacing(10)
        
        # Price range example
        price_slider = FluentRangeSlider(minimum=0, maximum=1000, low_value=100, high_value=500)
        
        price_label = QLabel("Price Range: $100 - $500")
        price_slider.range_changed.connect(
            lambda min_val, max_val: price_label.setText(f"Price Range: ${min_val} - ${max_val}")
        )
        
        layout.addWidget(QLabel("Price Range Slider ($0-$1000):"))
        layout.addWidget(price_slider)
        layout.addWidget(price_label)
        
        parent_layout.addWidget(group)
        
    def create_vertical_sliders(self, parent_layout):
        """Create vertical slider examples."""
        group = QGroupBox("Vertical Sliders")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        h_layout = QHBoxLayout(group)
        
        # Volume control
        volume_layout = QVBoxLayout()
        volume_slider = FluentSlider(orientation=Qt.Orientation.Vertical, minimum=0, maximum=100, value=75)
        volume_slider.setFixedHeight(200)
        
        volume_label = QLabel("Volume: 75%")
        volume_slider.valueChanged.connect(lambda v: volume_label.setText(f"Volume: {v}%"))
        
        volume_layout.addWidget(QLabel("Volume Control:"))
        volume_layout.addWidget(volume_slider, alignment=Qt.AlignmentFlag.AlignCenter)
        volume_layout.addWidget(volume_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Temperature control
        temp_layout = QVBoxLayout()
        temp_slider = FluentSlider(orientation=Qt.Orientation.Vertical, minimum=-10, maximum=40, value=22)
        temp_slider.setFixedHeight(200)
        
        temp_label = QLabel("Temp: 22°C")
        temp_slider.valueChanged.connect(lambda v: temp_label.setText(f"Temp: {v}°C"))
        
        temp_layout.addWidget(QLabel("Temperature:"))
        temp_layout.addWidget(temp_slider, alignment=Qt.AlignmentFlag.AlignCenter)
        temp_layout.addWidget(temp_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        h_layout.addLayout(volume_layout)
        h_layout.addSpacing(50)
        h_layout.addLayout(temp_layout)
        h_layout.addStretch()
        
        parent_layout.addWidget(group)
        
    def create_styled_sliders(self, parent_layout):
        """Create styled slider examples."""
        group = QGroupBox("Styled Sliders")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Custom styled slider
        styled_slider = FluentSlider(
            orientation=Qt.Orientation.Horizontal, 
            minimum=0, maximum=100, value=65,
            slider_style=FluentSlider.SliderStyle.ACCENT
        )
        
        styled_label = QLabel("Progress: 65%")
        styled_slider.valueChanged.connect(lambda v: styled_label.setText(f"Progress: {v}%"))
        
        layout.addWidget(QLabel("Accent Style Slider:"))
        layout.addWidget(styled_slider)
        layout.addWidget(styled_label)
        layout.addSpacing(10)
        
        # Large size slider
        large_slider = FluentSlider(
            orientation=Qt.Orientation.Horizontal, 
            minimum=0, maximum=10, value=7,
            size=FluentSlider.Size.LARGE
        )
        
        large_label = QLabel("Rating: 7/10")
        large_slider.valueChanged.connect(lambda v: large_label.setText(f"Rating: {v}/10"))
        
        layout.addWidget(QLabel("Large Size Slider (Rating):"))
        layout.addWidget(large_slider)
        layout.addWidget(large_label)
        
        parent_layout.addWidget(group)


def main():
    """Run the slider demo application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent Slider Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = SliderDemo()
    demo.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
