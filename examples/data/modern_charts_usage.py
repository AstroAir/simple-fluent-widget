#!/usr/bin/env python3
"""
Modern Chart Usage Examples

Simple examples demonstrating the optimized Fluent Design charts:
- Basic usage patterns
- Real-time data updates
- Performance demonstrations

Note: This example requires the optimized charts from charts_optimized.py
"""

from typing import Optional, List, Tuple
import random
import math
from datetime import datetime, timedelta

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor

# Import optimized charts
try:
    from components.data.charts_optimized import (
        FluentBarChart, FluentLineChart, FluentPieChart, FluentGaugeChart,
        ChartValue
    )
    OPTIMIZED_AVAILABLE = True
except ImportError as e:
    print(f"Optimized charts not available: {e}")
    print("Please ensure charts_optimized.py is available in components/data/")
    exit(1)


class SimpleChartUsageExample:
    """Simple examples demonstrating chart usage"""
    
    def __init__(self):
        self.app = QApplication([])
        self.setup_examples()
    
    def setup_examples(self):
        """Setup various chart examples"""
        print("=== Fluent Charts Usage Examples ===")
        
        # Example 1: Basic bar chart
        self.example_bar_chart()
        
        # Example 2: Line chart with multiple series
        self.example_line_chart()
        
        # Example 3: Animated pie chart
        self.example_pie_chart()
        
        # Example 4: Dynamic gauge
        self.example_gauge_chart()
        
        # Example 5: Real-time updates
        self.example_real_time_updates()
    
    def example_bar_chart(self):
        """Example 1: Basic bar chart"""
        print("\\n=== Example 1: Basic Bar Chart ===")
        
        chart = FluentBarChart()
        
        # Sample data
        data = [
            ("Q1 2024", 125000.50, QColor("#0078d4")),
            ("Q2 2024", 142750.25, QColor("#107c10")),
            ("Q3 2024", 98500.00, QColor("#d83b01")),
            ("Q4 2024", 156800.75, QColor("#5c2d91"))
        ]
          # Set data using the optimized API
        chart.set_data(data, animate=True)
        
        # Connect signals if available
        if hasattr(chart, 'bar_clicked'):
            chart.bar_clicked.connect(self.on_bar_clicked)
        
        print(f"Created bar chart with {len(data)} data points")
        print("✓ Chart configured successfully")
    
    def example_line_chart(self):
        """Example 2: Line chart with multiple series"""
        print("\\n=== Example 2: Line Chart ===")
        
        chart = FluentLineChart()
        
        # Generate sample time series data
        revenue_data = []
        profit_data = []
        
        for i in range(30):
            x = i
            revenue = 1000 + 500 * math.sin(i * 0.2) + random.uniform(-50, 50)
            profit = 800 + 300 * math.cos(i * 0.3) + random.uniform(-30, 30)
            
            revenue_data.append((x, revenue))
            profit_data.append((x, profit))
        
        # Add data series
        chart.add_data_series("Revenue", revenue_data, QColor("#0078d4"))
        chart.add_data_series("Profit", profit_data, QColor("#107c10"))
        
        print(f"Created line chart with 2 series, {len(revenue_data)} points each")
        print("✓ Multi-series chart configured")
    
    def example_pie_chart(self):
        """Example 3: Animated pie chart"""
        print("\\n=== Example 3: Pie Chart ===")
        
        chart = FluentPieChart()
        
        # Market share data
        data = [
            ("Mobile", 45.5, QColor("#0078d4")),
            ("Desktop", 32.1, QColor("#107c10")),
            ("Tablet", 15.8, QColor("#d83b01")),
            ("Smart TV", 4.2, QColor("#5c2d91")),
            ("Other", 2.4, QColor("#00bcf2"))
        ]
        
        # Set data based on available API
        if OPTIMIZED_AVAILABLE:
            chart.set_data(data, animate=True)
        else:
            chart.setData(data)
        
        print(f"Created pie chart with {len(data)} segments")
        print("✓ Pie chart with market share data")
    
    def example_gauge_chart(self):
        """Example 4: Dynamic gauge chart"""
        print("\\n=== Example 4: Gauge Chart ===")
        
        chart = FluentGaugeChart()
        
        # Configure gauge
        if hasattr(chart, 'set_title'):
            chart.set_title("System Performance")
            chart.set_unit("%")
            chart.set_range(0, 100)
            chart.set_value(85.5, animate=True)
        else:
            chart.setTitle("System Performance")
            chart.setUnit("%")
            chart.setRange(0, 100)
            chart.setValue(85.5, True)
        
        # Set custom color zones if supported
        if hasattr(chart, 'set_color_zones'):
            chart.set_color_zones([
                (0, 30, QColor("#d83b01")),    # Red zone
                (30, 70, QColor("#ffb900")),   # Yellow zone  
                (70, 90, QColor("#107c10")),   # Green zone
                (90, 100, QColor("#0078d4"))   # Excellent zone
            ])
        
        print("Created gauge chart with performance metrics")
        print("✓ Custom color zones configured")
    
    def example_real_time_updates(self):
        """Example 5: Real-time data updates"""
        print("\\n=== Example 5: Real-time Updates ===")
        
        # Create charts for real-time demo
        self.rt_line_chart = FluentLineChart()
        self.rt_gauge = FluentGaugeChart()
        
        # Initialize gauge
        if hasattr(self.rt_gauge, 'set_title'):
            self.rt_gauge.set_title("Live CPU Usage")
            self.rt_gauge.set_unit("%")
            self.rt_gauge.set_range(0, 100)
        else:
            self.rt_gauge.setTitle("Live CPU Usage")
            self.rt_gauge.setUnit("%")
            self.rt_gauge.setRange(0, 100)
        
        # Setup data storage
        self.rt_data = []
        self.update_count = 0
        
        # Create update timer
        self.rt_timer = QTimer()
        self.rt_timer.timeout.connect(self.update_real_time_data)
        self.rt_timer.start(500)  # Update every 500ms
        
        print("Started real-time data updates")
        print("✓ Timer configured for 500ms intervals")
    
    def update_real_time_data(self):
        """Update real-time charts with new data"""
        self.update_count += 1
        
        # Generate new data point
        current_time = self.update_count
        cpu_usage = 50 + 30 * math.sin(current_time * 0.1) + random.uniform(-10, 10)
        cpu_usage = max(0, min(100, cpu_usage))  # Clamp to 0-100
        
        # Update gauge
        if hasattr(self.rt_gauge, 'set_value'):
            self.rt_gauge.set_value(cpu_usage, animate=True)
        else:
            self.rt_gauge.setValue(cpu_usage, True)
        
        # Update line chart
        self.rt_data.append((current_time, cpu_usage))
        
        # Keep only last 50 points
        if len(self.rt_data) > 50:
            self.rt_data.pop(0)
        
        # Update chart
        self.rt_line_chart.clear_data()
        self.rt_line_chart.add_data_series("CPU Usage", self.rt_data, QColor("#d83b01"))
        
        # Print status every 10 updates
        if self.update_count % 10 == 0:
            print(f"Update #{self.update_count}: CPU = {cpu_usage:.1f}%")
    
    # Event handlers
    def on_bar_clicked(self, index: int, label: str, value: float):
        """Handle bar click events"""
        print(f"Bar clicked: {label} (index: {index}, value: {value:,.2f})")
    
    def run_examples(self):
        """Run all examples"""
        print("Running chart examples...")
        
        if OPTIMIZED_AVAILABLE:
            print("✓ Using optimized charts")
        else:
            print("ℹ Using fallback charts")


def create_dashboard_example():
    """Create a simple dashboard example"""
    print("\\n=== Dashboard Example ===")
    
    # Create dashboard widget
    dashboard = QWidget()
    dashboard.setWindowTitle("Simple Charts Dashboard")
    dashboard.resize(1000, 600)
    
    layout = QVBoxLayout(dashboard)
    
    # Top row: Gauges
    top_row = QHBoxLayout()
    
    gauges = []
    for i, (title, value) in enumerate([("CPU", 75), ("Memory", 60), ("Disk", 45)]):
        gauge = FluentGaugeChart()
        
        if hasattr(gauge, 'set_title'):
            gauge.set_title(title)
            gauge.set_unit("%")
            gauge.set_range(0, 100)
            gauge.set_value(value, animate=True)
        else:
            gauge.setTitle(title)
            gauge.setUnit("%")
            gauge.setRange(0, 100)
            gauge.setValue(value, True)
        
        gauges.append(gauge)
        top_row.addWidget(gauge)
    
    # Bottom row: Charts
    bottom_row = QHBoxLayout()
    
    # Performance chart
    perf_chart = FluentLineChart()
    perf_data = [(i, 50 + 20 * math.sin(i * 0.2) + random.uniform(-5, 5)) for i in range(20)]
    perf_chart.add_data_series("Performance", perf_data, QColor("#0078d4"))
    
    # Usage pie chart
    usage_chart = FluentPieChart()
    usage_data = [
        ("Used", 65, QColor("#d83b01")),
        ("Available", 35, QColor("#107c10"))
    ]
    
    if hasattr(usage_chart, 'set_data'):
        usage_chart.set_data(usage_data)
    else:
        usage_chart.setData(usage_data)
    
    bottom_row.addWidget(perf_chart)
    bottom_row.addWidget(usage_chart)
    
    layout.addLayout(top_row)
    layout.addLayout(bottom_row)
    
    dashboard.show()
    print("Dashboard created with:")
    print("- 3 gauge charts for system metrics")
    print("- Line chart for performance history")
    print("- Pie chart for usage distribution")
    
    return dashboard


def main():
    """Main function to run all examples"""
    # Create and run usage examples
    examples = SimpleChartUsageExample()
    examples.run_examples()
    
    # Create dashboard
    dashboard = create_dashboard_example()
    
    # Run application
    if dashboard:
        print("\\n=== Running Application ===")
        print("Dashboard displayed - close window to exit")
        examples.app.exec()


if __name__ == "__main__":
    main()
