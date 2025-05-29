#!/usr/bin/env python3
# filepath: d:\Project\simple-fluent-widget\demos\simple_charts_demo.py
"""
Simple Charts Demo

Demonstrates the simple chart components including:
- FluentSimpleBarChart - Basic bar charts
- FluentSimpleLineChart - Line charts with optional smooth curves
- FluentSimplePieChart - Interactive pie charts
- FluentGaugeChart - Animated gauge charts
"""

import sys
import os
import random
import math
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                              QWidget, QScrollArea, QGridLayout, QGroupBox, QCheckBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.data.charts import (FluentSimpleBarChart, FluentSimpleLineChart, 
                                   FluentSimplePieChart, FluentGaugeChart)
from components.basic.card import FluentCard
from components.basic.button import FluentButton
from components.basic.label import FluentLabel
from core.theme import theme_manager


class SimpleChartsDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Charts Demo - Fluent UI")
        self.setGeometry(100, 100, 1400, 900)
          # Apply theme styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme_manager.get_color('background').name()};
                color: {theme_manager.get_color('text_primary').name()};
            }}
        """)
        
        self.setup_ui()
        self.load_sample_data()
        
        # Setup timer for live data updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live_data)
        self.timer.start(3000)  # Update every 3 seconds
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Main content widget
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = FluentLabel("Simple Charts Components Demo")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Create charts grid
        charts_layout = QGridLayout()
        charts_layout.setSpacing(20)
        
        # Bar Chart
        self.create_bar_chart_section(charts_layout, 0, 0)
        
        # Line Chart
        self.create_line_chart_section(charts_layout, 0, 1)
        
        # Pie Chart
        self.create_pie_chart_section(charts_layout, 1, 0)
        
        # Gauge Chart
        self.create_gauge_chart_section(charts_layout, 1, 1)
        
        main_layout.addLayout(charts_layout)
        
        # Control buttons
        self.create_control_section(main_layout)
        
        scroll.setWidget(content_widget)
        
        # Set central widget
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        
    def create_bar_chart_section(self, parent_layout, row, col):
        """Create bar chart demo section"""
        card = FluentCard()
        card.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(card)
        
        # Title
        title = FluentLabel("Bar Chart")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Chart
        self.bar_chart = FluentSimpleBarChart()
        self.bar_chart.bar_clicked.connect(self.on_bar_clicked)
        layout.addWidget(self.bar_chart)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.bar_values_checkbox = QCheckBox("Show Values")
        self.bar_values_checkbox.setChecked(True)
        self.bar_values_checkbox.toggled.connect(self.bar_chart.setShowValues)
        controls_layout.addWidget(self.bar_values_checkbox)
        
        self.bar_grid_checkbox = QCheckBox("Show Grid")
        self.bar_grid_checkbox.setChecked(True)
        self.bar_grid_checkbox.toggled.connect(self.bar_chart.setShowGrid)
        controls_layout.addWidget(self.bar_grid_checkbox)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        parent_layout.addWidget(card, row, col)
        
    def create_line_chart_section(self, parent_layout, row, col):
        """Create line chart demo section"""
        card = FluentCard()
        card.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(card)
        
        # Title
        title = FluentLabel("Line Chart")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Chart
        self.line_chart = FluentSimpleLineChart()
        self.line_chart.point_clicked.connect(self.on_point_clicked)
        layout.addWidget(self.line_chart)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.line_smooth_checkbox = QCheckBox("Smooth Curve")
        self.line_smooth_checkbox.setChecked(False)
        self.line_smooth_checkbox.toggled.connect(self.line_chart.setSmoothCurves)
        controls_layout.addWidget(self.line_smooth_checkbox)
        
        self.line_grid_checkbox = QCheckBox("Show Grid")
        self.line_grid_checkbox.setChecked(True)
        self.line_grid_checkbox.toggled.connect(self.line_chart.setShowGrid)
        controls_layout.addWidget(self.line_grid_checkbox)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        parent_layout.addWidget(card, row, col)
        
    def create_pie_chart_section(self, parent_layout, row, col):
        """Create pie chart demo section"""
        card = FluentCard()
        card.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(card)
        
        # Title
        title = FluentLabel("Pie Chart")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Chart
        self.pie_chart = FluentSimplePieChart()
        self.pie_chart.slice_clicked.connect(self.on_slice_clicked)
        layout.addWidget(self.pie_chart)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.pie_labels_checkbox = QCheckBox("Show Labels")
        self.pie_labels_checkbox.setChecked(True)
        self.pie_labels_checkbox.toggled.connect(self.pie_chart.setShowLabels)
        controls_layout.addWidget(self.pie_labels_checkbox)
        
        self.pie_values_checkbox = QCheckBox("Show Values")
        self.pie_values_checkbox.setChecked(True)
        self.pie_values_checkbox.toggled.connect(self.pie_chart.setShowPercentages)
        controls_layout.addWidget(self.pie_values_checkbox)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        parent_layout.addWidget(card, row, col)
        
    def create_gauge_chart_section(self, parent_layout, row, col):
        """Create gauge chart demo section"""
        card = FluentCard()
        card.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(card)
        
        # Title
        title = FluentLabel("Gauge Chart")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        # Chart
        self.gauge_chart = FluentGaugeChart()
        layout.addWidget(self.gauge_chart)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        random_btn = FluentButton("Random Value")
        random_btn.clicked.connect(self.set_random_gauge_value)
        controls_layout.addWidget(random_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        parent_layout.addWidget(card, row, col)
        
    def create_control_section(self, parent_layout):
        """Create control buttons section"""
        controls_card = FluentCard()
        controls_layout = QHBoxLayout(controls_card)
        
        # Refresh data button
        refresh_btn = FluentButton("Refresh All Data")
        refresh_btn.clicked.connect(self.load_sample_data)
        controls_layout.addWidget(refresh_btn)
        
        # Toggle theme button
        theme_btn = FluentButton("Toggle Theme")
        theme_btn.clicked.connect(self.toggle_theme)
        controls_layout.addWidget(theme_btn)
        
        # Toggle animation button
        animation_btn = FluentButton("Toggle Live Updates")
        animation_btn.clicked.connect(self.toggle_animations)
        controls_layout.addWidget(animation_btn)
        
        controls_layout.addStretch()
        
        parent_layout.addWidget(controls_card)
        
    def load_sample_data(self):
        """Load sample data for all charts"""        # Bar chart data
        bar_data = [
            ("Q1", 75.0, QColor(0, 120, 215)),
            ("Q2", 85.0, QColor(16, 137, 62)),
            ("Q3", 92.0, QColor(255, 140, 0)),
            ("Q4", 68.0, QColor(232, 17, 35)),
            ("Q5", 95.0, QColor(104, 33, 122))
        ]
        self.bar_chart.setData(bar_data)
          # Line chart data
        line_data = []
        for i in range(10):
            x = i
            y = 50 + 30 * math.sin(i * 0.5) + random.randint(-10, 10)
            line_data.append((x, y))
        self.line_chart.addDataSeries("Performance", line_data, QColor(0, 120, 215))
        
        # Pie chart data
        pie_data = [
            ("Desktop", 45.2, QColor(0, 120, 215)),
            ("Mobile", 32.8, QColor(16, 137, 62)),
            ("Tablet", 15.6, QColor(255, 140, 0)),
            ("Other", 6.4, QColor(232, 17, 35))
        ]
        self.pie_chart.setData(pie_data)
          # Gauge chart setup
        self.gauge_chart.setRange(0, 100)
        self.gauge_chart.setValue(75)
        self.gauge_chart.setColorZones([
            (0, 30, QColor(232, 17, 35)),    # Red zone
            (30, 70, QColor(255, 140, 0)),   # Orange zone
            (70, 100, QColor(16, 137, 62))   # Green zone
        ])
    
    def update_live_data(self):
        """Update charts with live data"""
        # Update line chart with new point
        current_data = getattr(self, '_line_data', [])
        if len(current_data) >= 10:
            current_data = current_data[1:]  # Remove first point
        
        new_x = len(current_data)
        new_y = 50 + 30 * math.sin((len(current_data)) * 0.5) + random.randint(-10, 10)
        current_data.append((new_x, new_y))
        self._line_data = current_data
        
        # Clear and re-add data series for line chart
        self.line_chart.clearData()
        self.line_chart.addDataSeries("Performance", current_data, QColor(0, 120, 215))
        
        # Update gauge with random value
        if hasattr(self, 'gauge_chart'):
            current_value = self.gauge_chart._current_value
            new_value = max(0, min(100, current_value + random.randint(-10, 10)))
            self.gauge_chart.setValue(new_value)
    
    def set_random_gauge_value(self):
        """Set random gauge value"""
        value = random.randint(0, 100)
        self.gauge_chart.setValue(value)
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        from core.theme import ThemeMode
        current_mode = theme_manager._current_mode
        new_mode = ThemeMode.DARK if current_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
        theme_manager.set_theme_mode(new_mode)
        
    def toggle_animations(self):
        """Toggle live data updates"""
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(3000)
    
    # Event handlers
    def on_bar_clicked(self, index, label, value):
        """Handle bar chart click"""
        print(f"Bar clicked: {label} = {value} (index: {index})")
        
    def on_point_clicked(self, index, x, y):
        """Handle line chart point click"""
        print(f"Point clicked: ({x}, {y}) at index {index}")
        
    def on_slice_clicked(self, index, label, value, percentage):
        """Handle pie chart slice click"""
        print(f"Slice clicked: {label} = {value} ({percentage:.1f}%)")


def main():
    app = QApplication(sys.argv)
    
    # Apply custom styles
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f3f3f3;
        }
        
        FluentLabel#titleLabel {
            font-size: 24px;
            font-weight: bold;
            color: #323130;
            margin: 20px 0;
        }
        
        FluentLabel#sectionTitle {
            font-size: 16px;
            font-weight: bold;
            color: #323130;
            margin-bottom: 10px;
        }
        
        QCheckBox {
            font-size: 12px;
            color: #323130;
            spacing: 5px;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        
        QCheckBox::indicator:unchecked {
            background-color: white;
            border: 2px solid #8a8886;
            border-radius: 3px;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 2px solid #0078d4;
            border-radius: 3px;
        }
        
        QCheckBox::indicator:checked:hover {
            background-color: #106ebe;
        }
    """)
    
    window = SimpleChartsDemo()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
