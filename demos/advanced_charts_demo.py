"""
Advanced Charts Demo

Demonstrates the advanced chart components including:
- FluentAreaChart with gradient fills
- FluentScatterChart with trend lines
- FluentHeatMap with color coding
"""

import sys
import os
import random
import math
from datetime import datetime, timedelta
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea
from PySide6.QtCore import Qt, QTimer

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.data.advanced_charts import FluentAreaChart, FluentScatterChart, FluentHeatMap
from components.basic.card import FluentCard
from components.basic.button import FluentPushButton
from components.basic.label import FluentLabel
from theme.theme_manager import theme_manager


class AdvancedChartsDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Charts Demo - Fluent UI")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Apply theme
        theme_manager.apply_theme(self)
        
        self.setup_ui()
        self.load_sample_data()
        
        # Setup timer for live data updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live_data)
        self.timer.start(2000)  # Update every 2 seconds
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = FluentLabel("Advanced Charts Demo")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Create demo sections
        self.create_area_chart_demo(layout)
        self.create_scatter_chart_demo(layout)
        self.create_heat_map_demo(layout)
        
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(scroll)
        
    def create_area_chart_demo(self, parent_layout):
        """Create area chart demo section"""
        card = FluentCard()
        card_layout = QVBoxLayout(card)
        
        # Card title and controls
        header_layout = QHBoxLayout()
        
        card_title = FluentLabel("Area Chart - Sales Performance")
        card_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(card_title)
        
        header_layout.addStretch()
        
        # Control buttons
        self.refresh_area_btn = FluentPushButton("Refresh Data")
        self.refresh_area_btn.clicked.connect(self.refresh_area_chart)
        header_layout.addWidget(self.refresh_area_btn)
        
        self.toggle_area_animation_btn = FluentPushButton("Toggle Animation")
        self.toggle_area_animation_btn.clicked.connect(self.toggle_area_animation)
        header_layout.addWidget(self.toggle_area_animation_btn)
        
        card_layout.addLayout(header_layout)
        
        # Create area chart
        self.area_chart = FluentAreaChart()
        self.area_chart.setMinimumHeight(300)
        
        # Connect signals
        self.area_chart.point_clicked.connect(self.on_area_point_clicked)
        self.area_chart.point_hovered.connect(self.on_area_point_hovered)
        
        card_layout.addWidget(self.area_chart)
        
        # Status label
        self.area_status = FluentLabel("Hover over points for details, click to select")
        self.area_status.setStyleSheet("color: #666; font-size: 12px;")
        card_layout.addWidget(self.area_status)
        
        parent_layout.addWidget(card)
        
    def create_scatter_chart_demo(self, parent_layout):
        """Create scatter chart demo section"""
        card = FluentCard()
        card_layout = QVBoxLayout(card)
        
        # Card title and controls
        header_layout = QHBoxLayout()
        
        card_title = FluentLabel("Scatter Chart - Customer Analysis")
        card_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(card_title)
        
        header_layout.addStretch()
        
        # Control buttons
        self.refresh_scatter_btn = FluentPushButton("Generate New Data")
        self.refresh_scatter_btn.clicked.connect(self.refresh_scatter_chart)
        header_layout.addWidget(self.refresh_scatter_btn)
        
        self.toggle_trend_btn = FluentPushButton("Toggle Trend Line")
        self.toggle_trend_btn.clicked.connect(self.toggle_trend_line)
        header_layout.addWidget(self.toggle_trend_btn)
        
        card_layout.addLayout(header_layout)
        
        # Create scatter chart
        self.scatter_chart = FluentScatterChart()
        self.scatter_chart.setMinimumHeight(350)
        
        # Connect signals
        self.scatter_chart.point_clicked.connect(self.on_scatter_point_clicked)
        self.scatter_chart.selection_changed.connect(self.on_scatter_selection_changed)
        
        card_layout.addWidget(self.scatter_chart)
        
        # Status label
        self.scatter_status = FluentLabel("Click and drag to select multiple points")
        self.scatter_status.setStyleSheet("color: #666; font-size: 12px;")
        card_layout.addWidget(self.scatter_status)
        
        parent_layout.addWidget(card)
        
    def create_heat_map_demo(self, parent_layout):
        """Create heat map demo section"""
        card = FluentCard()
        card_layout = QVBoxLayout(card)
        
        # Card title and controls
        header_layout = QHBoxLayout()
        
        card_title = FluentLabel("Heat Map - Performance Matrix")
        card_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(card_title)
        
        header_layout.addStretch()
        
        # Control buttons
        self.refresh_heatmap_btn = FluentPushButton("Refresh Data")
        self.refresh_heatmap_btn.clicked.connect(self.refresh_heat_map)
        header_layout.addWidget(self.refresh_heatmap_btn)
        
        self.toggle_values_btn = FluentPushButton("Toggle Values")
        self.toggle_values_btn.clicked.connect(self.toggle_heat_map_values)
        header_layout.addWidget(self.toggle_values_btn)
        
        card_layout.addLayout(header_layout)
        
        # Create heat map
        self.heat_map = FluentHeatMap()
        self.heat_map.setMinimumHeight(400)
        
        # Connect signals
        self.heat_map.cell_clicked.connect(self.on_heat_map_cell_clicked)
        self.heat_map.cell_hovered.connect(self.on_heat_map_cell_hovered)
        
        card_layout.addWidget(self.heat_map)
        
        # Status label
        self.heatmap_status = FluentLabel("Hover over cells to see values, click to select")
        self.heatmap_status.setStyleSheet("color: #666; font-size: 12px;")
        card_layout.addWidget(self.heatmap_status)
        
        parent_layout.addWidget(card)
        
    def load_sample_data(self):
        """Load sample data for all charts"""
        self.load_area_chart_data()
        self.load_scatter_chart_data()
        self.load_heat_map_data()
        
    def load_area_chart_data(self):
        """Load sample data for area chart"""
        # Generate sample sales data over 12 months
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        # Sales data with some trend and seasonality
        base_sales = 10000
        sales_data = []
        
        for i, month in enumerate(months):
            # Add trend (growth over time)
            trend = i * 500
            # Add seasonality (higher sales in Nov-Dec)
            seasonal = 2000 if i >= 10 else 0
            # Add some randomness
            random_factor = random.randint(-1000, 1000)
            
            value = base_sales + trend + seasonal + random_factor
            sales_data.append((month, max(0, value)))
            
        self.area_chart.set_data(sales_data)
        self.area_chart.set_labels("Month", "Sales ($)")
        
    def load_scatter_chart_data(self):
        """Load sample data for scatter chart"""
        # Generate customer data: age vs spending with some correlation
        data_points = []
        
        for _ in range(100):
            age = random.randint(18, 80)
            # Create some correlation: younger and older customers spend less
            base_spending = 1000 - abs(age - 45) * 10
            spending = max(0, base_spending + random.randint(-300, 300))
            
            data_points.append((age, spending))
            
        self.scatter_chart.set_data(data_points)
        self.scatter_chart.set_labels("Customer Age", "Monthly Spending ($)")
        self.scatter_chart.show_trend_line(True)
        
    def load_heat_map_data(self):
        """Load sample data for heat map"""
        # Generate performance matrix: departments vs metrics
        departments = ["Sales", "Marketing", "Engineering", "Support", "HR", "Finance"]
        metrics = ["Efficiency", "Quality", "Innovation", "Customer Sat.", "Cost Control"]
        
        data = []
        for i, dept in enumerate(departments):
            row = []
            for j, metric in enumerate(metrics):
                # Generate performance scores (0-100) with some patterns
                base_score = 50 + (i + j) * 3
                score = min(100, max(0, base_score + random.randint(-20, 20)))
                row.append(score)
            data.append(row)
            
        self.heat_map.set_data(data, departments, metrics)
        self.heat_map.set_color_range(0, 100)
        self.heat_map.show_values(True)
        
    def refresh_area_chart(self):
        """Refresh area chart with new data"""
        self.load_area_chart_data()
        self.area_status.setText("Area chart data refreshed")
        
    def refresh_scatter_chart(self):
        """Refresh scatter chart with new data"""
        self.load_scatter_chart_data()
        self.scatter_status.setText("Scatter chart data regenerated")
        
    def refresh_heat_map(self):
        """Refresh heat map with new data"""
        self.load_heat_map_data()
        self.heatmap_status.setText("Heat map data refreshed")
        
    def toggle_area_animation(self):
        """Toggle area chart animation"""
        current = self.area_chart.animation_enabled
        self.area_chart.set_animation_enabled(not current)
        status = "enabled" if not current else "disabled"
        self.area_status.setText(f"Animation {status}")
        
    def toggle_trend_line(self):
        """Toggle scatter chart trend line"""
        current = self.scatter_chart.trend_line_visible
        self.scatter_chart.show_trend_line(not current)
        status = "shown" if not current else "hidden"
        self.scatter_status.setText(f"Trend line {status}")
        
    def toggle_heat_map_values(self):
        """Toggle heat map value display"""
        current = self.heat_map.values_visible
        self.heat_map.show_values(not current)
        status = "shown" if not current else "hidden"
        self.heatmap_status.setText(f"Values {status}")
        
    def update_live_data(self):
        """Update charts with live data simulation"""
        # Simulate real-time updates for the area chart
        # Add small random changes to the last few data points
        if hasattr(self, 'area_chart') and self.area_chart.data_points:
            # Only update if we're not in the middle of user interaction
            pass  # For demo purposes, we'll keep static data
            
    # Event handlers
    def on_area_point_clicked(self, index, value):
        """Handle area chart point click"""
        x, y = value
        self.area_status.setText(f"Selected: {x} = ${y:,.0f}")
        
    def on_area_point_hovered(self, index, value):
        """Handle area chart point hover"""
        if value:
            x, y = value
            self.area_status.setText(f"Hover: {x} = ${y:,.0f}")
        else:
            self.area_status.setText("Hover over points for details, click to select")
            
    def on_scatter_point_clicked(self, index, value):
        """Handle scatter chart point click"""
        x, y = value
        self.scatter_status.setText(f"Customer: Age {x}, Spending ${y:,.0f}")
        
    def on_scatter_selection_changed(self, selected_indices):
        """Handle scatter chart selection change"""
        count = len(selected_indices)
        if count == 0:
            self.scatter_status.setText("Click and drag to select multiple points")
        elif count == 1:
            self.scatter_status.setText(f"1 customer selected")
        else:
            self.scatter_status.setText(f"{count} customers selected")
            
    def on_heat_map_cell_clicked(self, row, col, value):
        """Handle heat map cell click"""
        if hasattr(self.heat_map, 'row_labels') and hasattr(self.heat_map, 'col_labels'):
            dept = self.heat_map.row_labels[row] if row < len(self.heat_map.row_labels) else f"Row {row}"
            metric = self.heat_map.col_labels[col] if col < len(self.heat_map.col_labels) else f"Col {col}"
            self.heatmap_status.setText(f"Selected: {dept} - {metric} = {value:.1f}")
        
    def on_heat_map_cell_hovered(self, row, col, value):
        """Handle heat map cell hover"""
        if value is not None:
            if hasattr(self.heat_map, 'row_labels') and hasattr(self.heat_map, 'col_labels'):
                dept = self.heat_map.row_labels[row] if row < len(self.heat_map.row_labels) else f"Row {row}"
                metric = self.heat_map.col_labels[col] if col < len(self.heat_map.col_labels) else f"Col {col}"
                self.heatmap_status.setText(f"Hover: {dept} - {metric} = {value:.1f}")
        else:
            self.heatmap_status.setText("Hover over cells to see values, click to select")


def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Advanced Charts Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Fluent UI")
    
    # Create and show demo window
    demo = AdvancedChartsDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
