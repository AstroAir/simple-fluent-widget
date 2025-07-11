#!/usr/bin/env python3
"""
Optimized Charts Demo

Demonstrates the modern, optimized Fluent Design chart components with:
- Enhanced performance and caching
- Modern Python 3.11+ features
- Advanced animations and interactions
- Theme integration and accessibility
- Type safety and error handling
"""

import sys
import os
import random
import math
from datetime import datetime, timedelta
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QScrollArea, QGridLayout, QGroupBox, QCheckBox, QPushButton,
    QComboBox, QSpinBox, QSlider, QLabel, QTabWidget
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from components.data.charts_optimized import (
        FluentBarChart, FluentLineChart, FluentPieChart, FluentGaugeChart,
        ChartConfig, ChartTheme, AnimationStyle, ChartDataPoint
    )
    from components.basic.card import FluentCard
    from components.basic.button import FluentButton
    from components.basic.label import FluentLabel
    from core.theme import theme_manager
    OPTIMIZED_CHARTS_AVAILABLE = True
except ImportError:
    # Fallback to regular charts if optimized not available
    from components.data.charts import (
        FluentSimpleBarChart as FluentBarChart,
        FluentSimpleLineChart as FluentLineChart,
        FluentSimplePieChart as FluentPieChart,
        FluentGaugeChart
    )
    from components.basic.card import FluentCard
    from components.basic.button import FluentButton
    from components.basic.label import FluentLabel
    from core.theme import theme_manager
    OPTIMIZED_CHARTS_AVAILABLE = False
    print("Using fallback charts - optimized charts not available")


class OptimizedChartsDemo(QMainWindow):
    """Comprehensive demo for optimized Fluent charts"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimized Fluent Charts Demo - Modern Python Features")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Apply modern theme styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme_manager.get_color('background').name()};
                color: {theme_manager.get_color('text_primary').name()};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme_manager.get_color('border').name()};
                background-color: {theme_manager.get_color('surface').name()};
            }}
            QTabBar::tab {{
                background-color: {theme_manager.get_color('surface').name()};
                color: {theme_manager.get_color('text_primary').name()};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {theme_manager.get_color('accent').name()};
                color: white;
            }}
        """)
        
        self.setup_ui()
        self.load_sample_data()
        
        # Setup live data updates
        self.setup_live_updates()
        
    def setup_ui(self):
        """Setup the user interface with modern layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add header
        self.create_header(main_layout)
        
        # Create tab widget for different chart categories
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Add chart tabs
        self.create_basic_charts_tab()
        self.create_advanced_charts_tab()
        self.create_performance_tab()
        self.create_customization_tab()
        
    def create_header(self, parent_layout):
        """Create header with title and controls"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # Title
        title_label = FluentLabel("Optimized Fluent Charts Demo")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Theme toggle
        theme_button = FluentButton("Toggle Theme")
        theme_button.clicked.connect(self.toggle_theme)
        header_layout.addWidget(theme_button)
        
        # Performance info
        if OPTIMIZED_CHARTS_AVAILABLE:
            perf_label = FluentLabel("✓ Optimized Charts Loaded")
            perf_label.setStyleSheet(f"color: {theme_manager.get_color('success').name()}")
        else:
            perf_label = FluentLabel("⚠ Using Fallback Charts")
            perf_label.setStyleSheet(f"color: {theme_manager.get_color('warning').name()}")
        header_layout.addWidget(perf_label)
        
        parent_layout.addWidget(header_widget)
    
    def create_basic_charts_tab(self):
        """Create basic charts demonstration tab"""
        tab_widget = QWidget()
        layout = QGridLayout(tab_widget)
        layout.setSpacing(15)
        
        # Bar Chart
        bar_card = self.create_chart_card("Modern Bar Chart", self.create_bar_chart())
        layout.addWidget(bar_card, 0, 0)
        
        # Line Chart
        line_card = self.create_chart_card("Smooth Line Chart", self.create_line_chart())
        layout.addWidget(line_card, 0, 1)
        
        # Pie Chart
        pie_card = self.create_chart_card("Animated Pie Chart", self.create_pie_chart())
        layout.addWidget(pie_card, 1, 0)
        
        # Gauge Chart
        gauge_card = self.create_chart_card("Dynamic Gauge", self.create_gauge_chart())
        layout.addWidget(gauge_card, 1, 1)
        
        self.tab_widget.addTab(tab_widget, "Basic Charts")
    
    def create_advanced_charts_tab(self):
        """Create advanced charts demonstration tab"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Multi-series line chart
        multi_line_chart = self.create_multi_series_chart()
        multi_card = self.create_chart_card("Multi-Series Analysis", multi_line_chart)
        layout.addWidget(multi_card)
        
        # Stacked data visualization
        comparison_layout = QHBoxLayout()
        
        # Comparison charts
        comparison1 = self.create_comparison_bar_chart()
        comparison2 = self.create_trend_chart()
        
        comparison_layout.addWidget(self.create_chart_card("Sales Comparison", comparison1))
        comparison_layout.addWidget(self.create_chart_card("Trend Analysis", comparison2))
        
        layout.addLayout(comparison_layout)
        
        self.tab_widget.addTab(tab_widget, "Advanced Charts")
    
    def create_performance_tab(self):
        """Create performance monitoring tab"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Performance controls
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        
        # Animation speed control
        controls_layout.addWidget(QLabel("Animation Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(100, 2000)
        self.speed_slider.setValue(300)
        self.speed_slider.valueChanged.connect(self.update_animation_speed)
        controls_layout.addWidget(self.speed_slider)
        
        # Data points control
        controls_layout.addWidget(QLabel("Data Points:"))
        self.data_points_spin = QSpinBox()
        self.data_points_spin.setRange(5, 100)
        self.data_points_spin.setValue(10)
        self.data_points_spin.valueChanged.connect(self.update_data_points)
        controls_layout.addWidget(self.data_points_spin)
        
        controls_layout.addStretch()
        layout.addWidget(controls_widget)
        
        # Performance charts
        perf_layout = QHBoxLayout()
        
        # Real-time performance chart
        self.perf_chart = self.create_performance_chart()
        perf_layout.addWidget(self.create_chart_card("Real-time Performance", self.perf_chart))
        
        # Memory usage chart
        self.memory_chart = self.create_memory_chart()
        perf_layout.addWidget(self.create_chart_card("Memory Usage", self.memory_chart))
        
        layout.addLayout(perf_layout)
        
        self.tab_widget.addTab(tab_widget, "Performance")
    
    def create_customization_tab(self):
        """Create customization demonstration tab"""
        tab_widget = QWidget()
        layout = QHBoxLayout(tab_widget)
        
        # Customization controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_widget.setMaximumWidth(300)
        
        # Theme selection
        theme_group = QGroupBox("Theme Options")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_combo = QComboBox()
        if OPTIMIZED_CHARTS_AVAILABLE:
            self.theme_combo.addItems(["Default", "Minimal", "Gradient", "Glass"])
        else:
            self.theme_combo.addItems(["Default"])
        self.theme_combo.currentTextChanged.connect(self.update_chart_theme)
        theme_layout.addWidget(self.theme_combo)
        
        # Animation selection
        animation_group = QGroupBox("Animation Style")
        animation_layout = QVBoxLayout(animation_group)
        
        self.animation_combo = QComboBox()
        if OPTIMIZED_CHARTS_AVAILABLE:
            self.animation_combo.addItems(["None", "Fade In", "Scale Up", "Slide Up", "Elastic"])
        else:
            self.animation_combo.addItems(["Default"])
        self.animation_combo.currentTextChanged.connect(self.update_animation_style)
        animation_layout.addWidget(self.animation_combo)
        
        # Feature toggles
        features_group = QGroupBox("Features")
        features_layout = QVBoxLayout(features_group)
        
        self.show_grid_cb = QCheckBox("Show Grid")
        self.show_grid_cb.setChecked(True)
        self.show_grid_cb.toggled.connect(self.toggle_grid)
        features_layout.addWidget(self.show_grid_cb)
        
        self.show_values_cb = QCheckBox("Show Values")
        self.show_values_cb.setChecked(True)
        self.show_values_cb.toggled.connect(self.toggle_values)
        features_layout.addWidget(self.show_values_cb)
        
        self.show_hover_cb = QCheckBox("Enable Hover")
        self.show_hover_cb.setChecked(True)
        self.show_hover_cb.toggled.connect(self.toggle_hover)
        features_layout.addWidget(self.show_hover_cb)
        
        controls_layout.addWidget(theme_group)
        controls_layout.addWidget(animation_group)
        controls_layout.addWidget(features_group)
        controls_layout.addStretch()
        
        layout.addWidget(controls_widget)
        
        # Customizable chart
        self.custom_chart = self.create_customizable_chart()
        custom_card = self.create_chart_card("Customizable Chart", self.custom_chart)
        layout.addWidget(custom_card)
        
        self.tab_widget.addTab(tab_widget, "Customization")
    
    def create_chart_card(self, title: str, chart_widget: QWidget) -> FluentCard:
        """Create a card containing a chart"""
        card = FluentCard()
        card.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = FluentLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Chart
        layout.addWidget(chart_widget)
        
        return card
    
    def create_bar_chart(self) -> FluentBarChart:
        """Create a modern bar chart"""
        chart = FluentBarChart()
        
        # Sample data with modern structure
        if OPTIMIZED_CHARTS_AVAILABLE:
            data = [
                ChartDataPoint("Q1", 85.5, QColor("#0078d4")),
                ChartDataPoint("Q2", 92.3, QColor("#107c10")),
                ChartDataPoint("Q3", 78.1, QColor("#d83b01")),
                ChartDataPoint("Q4", 95.7, QColor("#5c2d91"))
            ]
            chart.set_data(data)
        else:
            # Fallback for regular charts
            data = [("Q1", 85.5, QColor("#0078d4")), ("Q2", 92.3, QColor("#107c10")),
                   ("Q3", 78.1, QColor("#d83b01")), ("Q4", 95.7, QColor("#5c2d91"))]
            chart.setData(data)
            
        return chart
    
    def create_line_chart(self) -> FluentLineChart:
        """Create a smooth line chart"""
        chart = FluentLineChart()
        
        # Generate sample time series data
        data_points = []
        for i in range(20):
            x = i
            y = 50 + 30 * math.sin(i * 0.3) + random.uniform(-5, 5)
            data_points.append((x, y))
        
        chart.add_data_series("Revenue", data_points, QColor("#0078d4"))
        
        # Add second series
        data_points2 = []
        for i in range(20):
            x = i
            y = 45 + 25 * math.cos(i * 0.4) + random.uniform(-3, 3)
            data_points2.append((x, y))
        
        chart.add_data_series("Profit", data_points2, QColor("#107c10"))
        
        return chart
    
    def create_pie_chart(self) -> FluentPieChart:
        """Create an animated pie chart"""
        chart = FluentPieChart()
        
        if OPTIMIZED_CHARTS_AVAILABLE:
            data = [
                ChartDataPoint("Desktop", 45.2, QColor("#0078d4")),
                ChartDataPoint("Mobile", 35.8, QColor("#107c10")),
                ChartDataPoint("Tablet", 12.5, QColor("#d83b01")),
                ChartDataPoint("Other", 6.5, QColor("#5c2d91"))
            ]
            chart.set_data([(p.label, p.value, p.color) for p in data])
        else:
            data = [("Desktop", 45.2, QColor("#0078d4")), ("Mobile", 35.8, QColor("#107c10")),
                   ("Tablet", 12.5, QColor("#d83b01")), ("Other", 6.5, QColor("#5c2d91"))]
            chart.setData(data)
            
        return chart
    
    def create_gauge_chart(self) -> FluentGaugeChart:
        """Create a dynamic gauge chart"""
        chart = FluentGaugeChart()
        chart.set_title("Performance")
        chart.set_unit("%")
        chart.set_range(0, 100)
        chart.set_value(75.5)
        
        return chart
    
    def create_multi_series_chart(self) -> FluentLineChart:
        """Create a multi-series line chart"""
        chart = FluentLineChart()
        
        # Generate multiple data series
        series_data = {
            "Product A": [(i, 100 + 20 * math.sin(i * 0.2) + random.uniform(-5, 5)) for i in range(30)],
            "Product B": [(i, 80 + 15 * math.cos(i * 0.3) + random.uniform(-3, 3)) for i in range(30)],
            "Product C": [(i, 90 + 10 * math.sin(i * 0.4) + random.uniform(-2, 2)) for i in range(30)]
        }
        
        colors = [QColor("#0078d4"), QColor("#107c10"), QColor("#d83b01")]
        
        for i, (name, data) in enumerate(series_data.items()):
            chart.add_data_series(name, data, colors[i])
            
        return chart
    
    def create_comparison_bar_chart(self) -> FluentBarChart:
        """Create a comparison bar chart"""
        chart = FluentBarChart()
        
        if OPTIMIZED_CHARTS_AVAILABLE:
            data = [
                ChartDataPoint("Jan", 120, QColor("#0078d4")),
                ChartDataPoint("Feb", 135, QColor("#0078d4")),
                ChartDataPoint("Mar", 95, QColor("#d83b01")),
                ChartDataPoint("Apr", 168, QColor("#107c10")),
                ChartDataPoint("May", 142, QColor("#0078d4")),
                ChartDataPoint("Jun", 178, QColor("#107c10"))
            ]
            chart.set_data(data)
        else:
            data = [("Jan", 120, QColor("#0078d4")), ("Feb", 135, QColor("#0078d4")),
                   ("Mar", 95, QColor("#d83b01")), ("Apr", 168, QColor("#107c10")),
                   ("May", 142, QColor("#0078d4")), ("Jun", 178, QColor("#107c10"))]
            chart.setData(data)
            
        return chart
    
    def create_trend_chart(self) -> FluentLineChart:
        """Create a trend analysis chart"""
        chart = FluentLineChart()
        
        # Generate trend data
        trend_data = []
        base_value = 100
        for i in range(50):
            # Add trend + noise
            trend = i * 0.5
            noise = random.uniform(-5, 5)
            seasonal = 10 * math.sin(i * 0.2)
            value = base_value + trend + noise + seasonal
            trend_data.append((i, value))
        
        chart.add_data_series("Trend", trend_data, QColor("#0078d4"))
        
        return chart
    
    def create_performance_chart(self) -> FluentLineChart:
        """Create a real-time performance monitoring chart"""
        chart = FluentLineChart()
        
        # Initialize with empty data
        self.perf_data = []
        chart.add_data_series("FPS", self.perf_data, QColor("#107c10"))
        
        return chart
    
    def create_memory_chart(self) -> FluentLineChart:
        """Create a memory usage chart"""
        chart = FluentLineChart()
        
        # Initialize with empty data
        self.memory_data = []
        chart.add_data_series("Memory (MB)", self.memory_data, QColor("#d83b01"))
        
        return chart
    
    def create_customizable_chart(self) -> FluentBarChart:
        """Create a chart that can be customized"""
        chart = FluentBarChart()
        
        if OPTIMIZED_CHARTS_AVAILABLE:
            data = [
                ChartDataPoint("A", 25, QColor("#0078d4")),
                ChartDataPoint("B", 45, QColor("#107c10")),
                ChartDataPoint("C", 35, QColor("#d83b01")),
                ChartDataPoint("D", 55, QColor("#5c2d91"))
            ]
            chart.set_data(data)
        else:
            data = [("A", 25, QColor("#0078d4")), ("B", 45, QColor("#107c10")),
                   ("C", 35, QColor("#d83b01")), ("D", 55, QColor("#5c2d91"))]
            chart.setData(data)
        
        self.customizable_chart_ref = chart
        return chart
    
    def load_sample_data(self):
        """Load sample data for all charts"""
        # This method can be extended to load data from various sources
        pass
    
    def setup_live_updates(self):
        """Setup timers for live data updates"""
        # Performance data update
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.update_performance_data)
        self.perf_timer.start(100)  # Update every 100ms
        
        # Gauge update
        self.gauge_timer = QTimer()
        self.gauge_timer.timeout.connect(self.update_gauge_data)
        self.gauge_timer.start(2000)  # Update every 2 seconds
    
    def update_performance_data(self):
        """Update performance monitoring data"""
        if hasattr(self, 'perf_chart'):
            # Simulate FPS data
            current_time = len(self.perf_data)
            fps = 60 + random.uniform(-5, 5)
            self.perf_data.append((current_time, fps))
            
            # Keep only last 100 points
            if len(self.perf_data) > 100:
                self.perf_data.pop(0)
            
            # Update chart
            self.perf_chart.clear_data()
            self.perf_chart.add_data_series("FPS", self.perf_data, QColor("#107c10"))
            
            # Update memory data
            memory_usage = 50 + 20 * math.sin(current_time * 0.1) + random.uniform(-2, 2)
            self.memory_data.append((current_time, memory_usage))
            
            if len(self.memory_data) > 100:
                self.memory_data.pop(0)
            
            if hasattr(self, 'memory_chart'):
                self.memory_chart.clear_data()
                self.memory_chart.add_data_series("Memory (MB)", self.memory_data, QColor("#d83b01"))
    
    def update_gauge_data(self):
        """Update gauge chart with random data"""
        if hasattr(self, 'tab_widget'):
            # Find gauge charts and update them
            for i in range(self.tab_widget.count()):
                tab = self.tab_widget.widget(i)
                gauges = tab.findChildren(FluentGaugeChart)
                for gauge in gauges:
                    new_value = random.uniform(0, 100)
                    gauge.set_value(new_value)
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        # This would integrate with the theme manager
        if hasattr(theme_manager, 'toggle_theme'):
            theme_manager.toggle_theme()
        
    def update_animation_speed(self, value):
        """Update animation speed for charts"""
        if OPTIMIZED_CHARTS_AVAILABLE and hasattr(self, 'customizable_chart_ref'):
            # Update animation duration
            pass
    
    def update_data_points(self, value):
        """Update number of data points in performance charts"""
        # Regenerate data with new point count
        pass
    
    def update_chart_theme(self, theme_name):
        """Update chart theme"""
        if OPTIMIZED_CHARTS_AVAILABLE and hasattr(self, 'customizable_chart_ref'):
            # Apply new theme
            pass
    
    def update_animation_style(self, style_name):
        """Update animation style"""
        if OPTIMIZED_CHARTS_AVAILABLE and hasattr(self, 'customizable_chart_ref'):
            # Apply new animation style
            pass
    
    def toggle_grid(self, checked):
        """Toggle grid display"""
        if hasattr(self, 'customizable_chart_ref'):
            if hasattr(self.customizable_chart_ref, 'setShowGrid'):
                self.customizable_chart_ref.setShowGrid(checked)
    
    def toggle_values(self, checked):
        """Toggle value display"""
        if hasattr(self, 'customizable_chart_ref'):
            if hasattr(self.customizable_chart_ref, 'setShowValues'):
                self.customizable_chart_ref.setShowValues(checked)
    
    def toggle_hover(self, checked):
        """Toggle hover effects"""
        if hasattr(self, 'customizable_chart_ref'):
            if hasattr(self.customizable_chart_ref, '_chart_state'):
                self.customizable_chart_ref._chart_state.config.enable_hover = checked


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Optimized Fluent Charts Demo")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Fluent UI Python")
    
    # Apply dark theme for better chart visibility
    app.setStyle("Fusion")
    
    # Create and show main window
    window = OptimizedChartsDemo()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
