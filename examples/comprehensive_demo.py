#!/usr/bin/env python3
"""
Comprehensive Fluent Components Demo

This example demonstrates multiple Fluent components working together in a cohesive application,
showcasing the modernized and organized component structure.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QLabel, QGroupBox, QPushButton, QSplitter,
                               QScrollArea, QFrame)
from PySide6.QtCore import Qt


def main():
    """Run the comprehensive demo application."""
    app = QApplication(sys.argv)
    
    # Import components after QApplication is created
    from components.basic.navigation.tabs import FluentTabWidget
    from components.basic.forms.button import FluentButton
    from components.basic.forms.slider import FluentSlider
    from components.basic.forms.textbox import FluentLineEdit
    from components.basic.display.progress import FluentProgressBar
    from components.data.input.calendar import OptimizedFluentCalendar
    from components.data.input.colorpicker import FluentColorPicker
    from PySide6.QtCore import QDate
    from PySide6.QtGui import QColor
    
    class ComprehensiveDemo(QMainWindow):
        """Main demo window showcasing multiple Fluent components working together."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Comprehensive Fluent Components Demo")
            self.setGeometry(100, 100, 1200, 800)
            
            # Create central widget with splitter
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            main_layout = QVBoxLayout(central_widget)
            
            # Add title
            title = QLabel("🎨 Comprehensive Fluent Components Demo")
            title.setStyleSheet("""
                font-size: 28px; 
                font-weight: bold; 
                color: #323130; 
                margin: 20px 0;
                text-align: center;
            """)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(title)
            
            # Create main tab widget
            self.main_tabs = FluentTabWidget()
            
            # Create different demo sections
            self.create_forms_demo()
            self.create_data_demo()
            self.create_interactive_demo()
            
            main_layout.addWidget(self.main_tabs)
            
        def create_forms_demo(self):
            """Create forms and input components demo."""
            forms_widget = QWidget()
            layout = QVBoxLayout(forms_widget)
            layout.setSpacing(20)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Progress section
            progress_group = QGroupBox("Progress Components")
            progress_layout = QVBoxLayout(progress_group)
            
            self.progress_bar = FluentProgressBar()
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(0)
            
            progress_layout.addWidget(QLabel("Progress Bar:"))
            progress_layout.addWidget(self.progress_bar)
            
            # Slider section
            slider_group = QGroupBox("Slider Controls")
            slider_layout = QVBoxLayout(slider_group)
            
            self.slider = FluentSlider(parent=None)
            self.slider.setOrientation(Qt.Orientation.Horizontal)
            self.slider.setMinimum(0)
            self.slider.setMaximum(100)
            self.slider.setValue(50)
            
            self.slider_label = QLabel("Value: 50")
            
            slider_layout.addWidget(QLabel("Slider Control:"))
            slider_layout.addWidget(self.slider)
            slider_layout.addWidget(self.slider_label)
            
            # Connect slider to progress bar
            self.slider.valueChanged.connect(self.on_slider_changed)
            
            # Text input section
            text_group = QGroupBox("Text Input")
            text_layout = QVBoxLayout(text_group)
            
            self.text_input = FluentLineEdit()
            self.text_input.setPlaceholderText("Enter text here...")
            
            text_layout.addWidget(QLabel("Text Input:"))
            text_layout.addWidget(self.text_input)
            
            # Button section
            button_group = QGroupBox("Action Buttons")
            button_layout = QHBoxLayout(button_group)
            
            self.start_btn = FluentButton("Start Progress")
            self.reset_btn = FluentButton("Reset")
            self.animate_btn = FluentButton("Animate")
            
            self.start_btn.clicked.connect(self.start_progress)
            self.reset_btn.clicked.connect(self.reset_values)
            self.animate_btn.clicked.connect(self.animate_progress)
            
            button_layout.addWidget(self.start_btn)
            button_layout.addWidget(self.reset_btn)
            button_layout.addWidget(self.animate_btn)
            button_layout.addStretch()
            
            # Add all groups to layout
            layout.addWidget(progress_group)
            layout.addWidget(slider_group)
            layout.addWidget(text_group)
            layout.addWidget(button_group)
            layout.addStretch()
            
            self.main_tabs.addTab(forms_widget, "Forms & Controls")
        
        def create_data_demo(self):
            """Create data components demo."""
            data_widget = QWidget()
            layout = QHBoxLayout(data_widget)
            layout.setSpacing(20)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Calendar section
            calendar_group = QGroupBox("Calendar Component")
            calendar_layout = QVBoxLayout(calendar_group)
            
            self.calendar = OptimizedFluentCalendar()
            self.calendar_status = QLabel("Select a date...")
            
            calendar_layout.addWidget(QLabel("Date Selection:"))
            calendar_layout.addWidget(self.calendar)
            calendar_layout.addWidget(self.calendar_status)
            
            # Connect calendar signals
            self.calendar.dateSelected.connect(self.on_date_selected)
            
            # Color picker section
            color_group = QGroupBox("Color Picker")
            color_layout = QVBoxLayout(color_group)
            
            self.color_picker = FluentColorPicker()
            self.color_status = QLabel("Color: #0078d4")
            self.color_display = QFrame()
            self.color_display.setFixedHeight(50)
            self.color_display.setStyleSheet("background-color: #0078d4; border: 1px solid #ccc; border-radius: 4px;")
            
            color_layout.addWidget(QLabel("Color Selection:"))
            color_layout.addWidget(self.color_picker)
            color_layout.addWidget(self.color_status)
            color_layout.addWidget(self.color_display)
            color_layout.addStretch()
            
            # Connect color picker signals
            self.color_picker.colorChanged.connect(self.on_color_changed)
            
            layout.addWidget(calendar_group)
            layout.addWidget(color_group)
            
            self.main_tabs.addTab(data_widget, "Data Components")
        
        def create_interactive_demo(self):
            """Create interactive demo showing component integration."""
            interactive_widget = QWidget()
            layout = QVBoxLayout(interactive_widget)
            layout.setSpacing(20)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Integration demo
            integration_group = QGroupBox("Component Integration Demo")
            integration_layout = QVBoxLayout(integration_group)
            
            info_label = QLabel("""
            🔗 This tab demonstrates how components work together:
            
            • Adjust the slider in the 'Forms & Controls' tab to see the progress bar update
            • Select a date in the 'Data Components' tab to see it reflected here
            • Pick a color to change the theme of various elements
            • Use the buttons to trigger animations and interactions
            
            All components are properly integrated and responsive!
            """)
            info_label.setWordWrap(True)
            info_label.setStyleSheet("padding: 20px; background-color: #f3f2f1; border-radius: 8px; line-height: 1.6;")
            
            # Status display
            self.integration_status = QLabel("Integration Status: All systems ready!")
            self.integration_status.setStyleSheet("font-weight: bold; color: #107c10; padding: 10px;")
            
            # Demo controls
            demo_controls = QHBoxLayout()
            
            self.sync_btn = FluentButton("Sync Components")
            self.demo_btn = FluentButton("Run Demo")
            self.info_btn = FluentButton("Show Info")
            
            self.sync_btn.clicked.connect(self.sync_components)
            self.demo_btn.clicked.connect(self.run_demo)
            self.info_btn.clicked.connect(self.show_info)
            
            demo_controls.addWidget(self.sync_btn)
            demo_controls.addWidget(self.demo_btn)
            demo_controls.addWidget(self.info_btn)
            demo_controls.addStretch()
            
            integration_layout.addWidget(info_label)
            integration_layout.addWidget(self.integration_status)
            integration_layout.addLayout(demo_controls)
            integration_layout.addStretch()
            
            layout.addWidget(integration_group)
            
            self.main_tabs.addTab(interactive_widget, "Integration Demo")
        
        def on_slider_changed(self, value):
            """Handle slider value changes."""
            self.slider_label.setText(f"Value: {value}")
            self.progress_bar.set_value_animated(value)
            
        def on_date_selected(self, date):
            """Handle calendar date selection."""
            date_str = date.toString("yyyy-MM-dd dddd")
            self.calendar_status.setText(f"Selected: {date_str}")
            self.integration_status.setText(f"Integration Status: Date selected - {date_str}")
            
        def on_color_changed(self, color):
            """Handle color picker changes."""
            color_name = color.name()
            self.color_status.setText(f"Color: {color_name}")
            self.color_display.setStyleSheet(f"background-color: {color_name}; border: 1px solid #ccc; border-radius: 4px;")
            self.integration_status.setText(f"Integration Status: Color changed to {color_name}")
            
        def start_progress(self):
            """Start progress animation."""
            self.progress_bar.set_value_animated(100, 3000)  # 3 second animation
            self.integration_status.setText("Integration Status: Progress animation started!")
            
        def reset_values(self):
            """Reset all values to defaults."""
            self.slider.setValue(50)
            self.progress_bar.setValue(0)
            self.text_input.clear()
            self.text_input.setPlaceholderText("Enter text here...")
            self.integration_status.setText("Integration Status: Values reset to defaults!")
            
        def animate_progress(self):
            """Animate progress with steps."""
            # Animate to 25%, then 50%, then 75%, then 100%
            import threading
            import time
            
            def animate():
                for value in [25, 50, 75, 100]:
                    self.progress_bar.set_value_animated(value, 800)
                    time.sleep(1)
            
            thread = threading.Thread(target=animate)
            thread.daemon = True
            thread.start()
            
            self.integration_status.setText("Integration Status: Step-by-step animation running!")
            
        def sync_components(self):
            """Sync all components to current values."""
            current_slider_value = self.slider.value()
            self.progress_bar.set_value_animated(current_slider_value)
            
            if self.calendar.selectedDate().isValid():
                date_str = self.calendar.selectedDate().toString("yyyy-MM-dd")
                self.integration_status.setText(f"Integration Status: Synced! Slider: {current_slider_value}%, Date: {date_str}")
            else:
                self.integration_status.setText(f"Integration Status: Synced! Slider: {current_slider_value}%")
                
        def run_demo(self):
            """Run a comprehensive demo sequence."""
            self.integration_status.setText("Integration Status: Running comprehensive demo...")
            
            # Switch to forms tab and animate
            self.main_tabs.setCurrentIndex(0)
            self.animate_progress()
            
        def show_info(self):
            """Show information about the demo."""
            from PySide6.QtWidgets import QMessageBox
            
            QMessageBox.information(self, "Demo Information", 
                "🎨 Comprehensive Fluent Components Demo\n\n"
                "This demo showcases the modernized and organized Fluent UI components:\n\n"
                "✅ Fixed API compatibility issues\n"
                "✅ Resolved import system problems\n"
                "✅ Updated to Python 3.11+ features\n"
                "✅ Organized into logical component hierarchy\n"
                "✅ Created comprehensive examples\n\n"
                "All components are now working together seamlessly!")
    
    # Set application properties
    app.setApplicationName("Comprehensive Fluent Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = ComprehensiveDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
