"""
Comprehensive Data Charts Components Demo

This demo showcases all chart components available in the simple-fluent-widget library,
including bar charts, line charts, pie charts, and advanced visualization components.

Features demonstrated:
- Simple and advanced chart types
- Interactive data visualization
- Real-time data updates
- Custom styling and theming
- Data export and analysis tools
"""

import sys
import random
import math
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QGroupBox,
    QScrollArea, QFrame, QSpacerItem, QSizePolicy, QMessageBox, QTabWidget,
    QSlider, QSpinBox, QCheckBox, QComboBox, QDoubleSpinBox, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPalette, QFont, QIcon, QPainter, QBrush, QPen

# Import fluent chart components with fallbacks
try:
    from components.data.charts.charts import (
        FluentSimpleBarChart, FluentSimpleLineChart, FluentSimplePieChart, FluentGaugeChart
    )
    FLUENT_SIMPLE_CHARTS_AVAILABLE = True
except ImportError:
    print("Warning: Fluent simple chart components not available")
    FLUENT_SIMPLE_CHARTS_AVAILABLE = False

try:
    from components.data.charts.advanced_charts import (
        FluentAreaChart, FluentScatterChart, FluentHeatMap, FluentCandlestickChart
    )
    FLUENT_ADVANCED_CHARTS_AVAILABLE = True
except ImportError:
    print("Warning: Fluent advanced chart components not available")
    FLUENT_ADVANCED_CHARTS_AVAILABLE = False

try:
    from components.data.charts.visualization import (
        FluentDataVisualization, FluentMetricsCard, FluentSparkline
    )
    FLUENT_VIZ_AVAILABLE = True
except ImportError:
    print("Warning: Fluent visualization components not available")
    FLUENT_VIZ_AVAILABLE = False

try:
    from components.layout.containers import FluentCard
    FLUENT_CARD_AVAILABLE = True
except ImportError:
    FLUENT_CARD_AVAILABLE = False


class FallbackChartWidget(QWidget):
    """Fallback chart widget when fluent components are not available."""
    
    def __init__(self, chart_type="bar"):
        super().__init__()
        self.chart_type = chart_type
        self.data = []
        self.setMinimumSize(300, 200)
        
    def setData(self, data):
        """Set chart data."""
        self.data = data
        self.update()
        
    def paintEvent(self, event):
        """Paint a simple fallback chart."""
        if not self.data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        margin = 20
        chart_rect = rect.adjusted(margin, margin, -margin, -margin)
        
        if self.chart_type == "bar":
            self.draw_bar_chart(painter, chart_rect)
        elif self.chart_type == "line":
            self.draw_line_chart(painter, chart_rect)
        elif self.chart_type == "pie":
            self.draw_pie_chart(painter, chart_rect)
        else:
            # Default to bar chart
            self.draw_bar_chart(painter, chart_rect)
            
    def draw_bar_chart(self, painter, rect):
        """Draw a simple bar chart."""
        if not self.data:
            return
            
        max_value = max(item[1] if isinstance(item, tuple) else item for item in self.data)
        if max_value == 0:
            max_value = 1
            
        bar_width = rect.width() // len(self.data) * 0.8
        spacing = rect.width() // len(self.data) * 0.2
        
        colors = [QColor(100, 150, 200), QColor(200, 100, 150), QColor(150, 200, 100),
                 QColor(200, 150, 100), QColor(150, 100, 200), QColor(100, 200, 150)]
        
        for i, item in enumerate(self.data):
            if isinstance(item, tuple):
                value = item[1]
                label = item[0]
            else:
                value = item
                label = f"Item {i+1}"
                
            bar_height = (value / max_value) * rect.height()
            x = rect.x() + i * (bar_width + spacing)
            y = rect.bottom() - bar_height
            
            color = colors[i % len(colors)]
            painter.fillRect(int(x), int(y), int(bar_width), int(bar_height), QBrush(color))
            
    def draw_line_chart(self, painter, rect):
        """Draw a simple line chart."""
        if len(self.data) < 2:
            return
            
        max_value = max(item[1] if isinstance(item, tuple) else item for item in self.data)
        if max_value == 0:
            max_value = 1
            
        # Draw line
        painter.setPen(QPen(QColor(100, 150, 200), 2))
        
        point_spacing = rect.width() / (len(self.data) - 1)
        
        for i in range(len(self.data) - 1):
            value1 = self.data[i][1] if isinstance(self.data[i], tuple) else self.data[i]
            value2 = self.data[i+1][1] if isinstance(self.data[i+1], tuple) else self.data[i+1]
            
            y1 = rect.bottom() - (value1 / max_value) * rect.height()
            y2 = rect.bottom() - (value2 / max_value) * rect.height()
            x1 = rect.x() + i * point_spacing
            x2 = rect.x() + (i + 1) * point_spacing
            
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            
        # Draw points
        painter.setBrush(QBrush(QColor(100, 150, 200)))
        for i, item in enumerate(self.data):
            value = item[1] if isinstance(item, tuple) else item
            y = rect.bottom() - (value / max_value) * rect.height()
            x = rect.x() + i * point_spacing
            painter.drawEllipse(int(x-3), int(y-3), 6, 6)
            
    def draw_pie_chart(self, painter, rect):
        """Draw a simple pie chart."""
        if not self.data:
            return
            
        total = sum(item[1] if isinstance(item, tuple) else item for item in self.data)
        if total == 0:
            return
            
        colors = [QColor(100, 150, 200), QColor(200, 100, 150), QColor(150, 200, 100),
                 QColor(200, 150, 100), QColor(150, 100, 200), QColor(100, 200, 150)]
        
        # Use a square area centered in the rect
        size = min(rect.width(), rect.height())
        pie_rect = rect.adjusted((rect.width()-size)//2, (rect.height()-size)//2, 
                                -(rect.width()-size)//2, -(rect.height()-size)//2)
        
        start_angle = 0
        for i, item in enumerate(self.data):
            value = item[1] if isinstance(item, tuple) else item
            span_angle = int((value / total) * 360 * 16)  # Qt uses 16ths of degrees
            
            color = colors[i % len(colors)]
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            painter.drawPie(pie_rect, start_angle, span_angle)
            
            start_angle += span_angle


class DataChartsDemo(QMainWindow):
    """Main demo window showcasing data chart components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Charts Components Demo")
        self.setGeometry(100, 100, 1400, 900)
        
        # Sample data for demonstrations
        self.sample_data = self.create_sample_data()
        self.time_series_data = self.create_time_series_data()
        self.real_time_data = []
        
        # Animation and update timers
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_real_time_data)
        
        self.setup_ui()
        self.populate_charts()
        
    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Data Charts Components Demo")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Tab widget for different chart categories
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs for different chart types
        self.create_simple_charts_tab()
        self.create_advanced_charts_tab()
        self.create_real_time_tab()
        self.create_interactive_tab()
        self.create_customization_tab()
        
        # Status bar
        self.statusBar().showMessage("Ready - Explore different chart types and interact with data")
        
    def create_simple_charts_tab(self):
        """Create simple charts demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Controls section
        controls_group = QGroupBox("Chart Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        # Data controls
        controls_layout.addWidget(QLabel("Data Points:"))
        self.data_count_spin = QSpinBox()
        self.data_count_spin.setRange(3, 20)
        self.data_count_spin.setValue(6)
        self.data_count_spin.valueChanged.connect(self.regenerate_data)
        controls_layout.addWidget(self.data_count_spin)
        
        regenerate_btn = QPushButton("Regenerate Data")
        regenerate_btn.clicked.connect(self.regenerate_data)
        controls_layout.addWidget(regenerate_btn)
        
        # Style controls
        self.show_values_check = QCheckBox("Show Values")
        self.show_values_check.setChecked(True)
        self.show_values_check.toggled.connect(self.update_chart_style)
        controls_layout.addWidget(self.show_values_check)
        
        self.show_grid_check = QCheckBox("Show Grid")
        self.show_grid_check.setChecked(True)
        self.show_grid_check.toggled.connect(self.update_chart_style)
        controls_layout.addWidget(self.show_grid_check)
        
        layout.addWidget(controls_group)
        
        # Charts grid
        charts_widget = QWidget()
        charts_layout = QGridLayout(charts_widget)
        
        # Bar Chart
        bar_group = QGroupBox("Bar Chart")
        bar_layout = QVBoxLayout(bar_group)
        
        if FLUENT_SIMPLE_CHARTS_AVAILABLE:
            try:
                self.bar_chart = FluentSimpleBarChart()
            except Exception as e:
                print(f"Error creating FluentSimpleBarChart: {e}")
                self.bar_chart = FallbackChartWidget("bar")
        else:
            self.bar_chart = FallbackChartWidget("bar")
            
        bar_layout.addWidget(self.bar_chart)
        charts_layout.addWidget(bar_group, 0, 0)
        
        # Line Chart
        line_group = QGroupBox("Line Chart")
        line_layout = QVBoxLayout(line_group)
        
        if FLUENT_SIMPLE_CHARTS_AVAILABLE:
            try:
                self.line_chart = FluentSimpleLineChart()
            except Exception as e:
                print(f"Error creating FluentSimpleLineChart: {e}")
                self.line_chart = FallbackChartWidget("line")
        else:
            self.line_chart = FallbackChartWidget("line")
            
        line_layout.addWidget(self.line_chart)
        charts_layout.addWidget(line_group, 0, 1)
        
        # Pie Chart
        pie_group = QGroupBox("Pie Chart")
        pie_layout = QVBoxLayout(pie_group)
        
        if FLUENT_SIMPLE_CHARTS_AVAILABLE:
            try:
                self.pie_chart = FluentSimplePieChart()
            except Exception as e:
                print(f"Error creating FluentSimplePieChart: {e}")
                self.pie_chart = FallbackChartWidget("pie")
        else:
            self.pie_chart = FallbackChartWidget("pie")
            
        pie_layout.addWidget(self.pie_chart)
        charts_layout.addWidget(pie_group, 1, 0)
        
        # Gauge Chart
        gauge_group = QGroupBox("Gauge Chart")
        gauge_layout = QVBoxLayout(gauge_group)
        
        if FLUENT_SIMPLE_CHARTS_AVAILABLE:
            try:
                self.gauge_chart = FluentGaugeChart()
            except Exception as e:
                print(f"Error creating FluentGaugeChart: {e}")
                self.gauge_chart = FallbackChartWidget("gauge")
        else:
            self.gauge_chart = FallbackChartWidget("gauge")
            
        gauge_layout.addWidget(self.gauge_chart)
        charts_layout.addWidget(gauge_group, 1, 1)
        
        layout.addWidget(charts_widget)
        self.tab_widget.addTab(tab_widget, "Simple Charts")
        
    def create_advanced_charts_tab(self):
        """Create advanced charts demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Controls section
        controls_group = QGroupBox("Advanced Chart Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        # Animation controls
        self.animation_enabled_check = QCheckBox("Enable Animations")
        self.animation_enabled_check.setChecked(True)
        controls_layout.addWidget(self.animation_enabled_check)
        
        controls_layout.addWidget(QLabel("Animation Speed:"))
        self.animation_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.animation_speed_slider.setRange(100, 2000)
        self.animation_speed_slider.setValue(500)
        controls_layout.addWidget(self.animation_speed_slider)
        
        # Data manipulation
        add_data_btn = QPushButton("Add Data Point")
        add_data_btn.clicked.connect(self.add_data_point)
        controls_layout.addWidget(add_data_btn)
        
        remove_data_btn = QPushButton("Remove Data Point")
        remove_data_btn.clicked.connect(self.remove_data_point)
        controls_layout.addWidget(remove_data_btn)
        
        layout.addWidget(controls_group)
        
        # Advanced charts grid
        charts_widget = QWidget()
        charts_layout = QGridLayout(charts_widget)
        
        # Area Chart
        area_group = QGroupBox("Area Chart")
        area_layout = QVBoxLayout(area_group)
        
        if FLUENT_ADVANCED_CHARTS_AVAILABLE:
            try:
                self.area_chart = FluentAreaChart()
            except Exception as e:
                print(f"Error creating FluentAreaChart: {e}")
                self.area_chart = FallbackChartWidget("area")
        else:
            self.area_chart = FallbackChartWidget("area")
            
        area_layout.addWidget(self.area_chart)
        charts_layout.addWidget(area_group, 0, 0)
        
        # Scatter Chart
        scatter_group = QGroupBox("Scatter Chart")
        scatter_layout = QVBoxLayout(scatter_group)
        
        if FLUENT_ADVANCED_CHARTS_AVAILABLE:
            try:
                self.scatter_chart = FluentScatterChart()
            except Exception as e:
                print(f"Error creating FluentScatterChart: {e}")
                self.scatter_chart = FallbackChartWidget("scatter")
        else:
            self.scatter_chart = FallbackChartWidget("scatter")
            
        scatter_layout.addWidget(self.scatter_chart)
        charts_layout.addWidget(scatter_group, 0, 1)
        
        # Heat Map
        heatmap_group = QGroupBox("Heat Map")
        heatmap_layout = QVBoxLayout(heatmap_group)
        
        if FLUENT_ADVANCED_CHARTS_AVAILABLE:
            try:
                self.heatmap = FluentHeatMap()
            except Exception as e:
                print(f"Error creating FluentHeatMap: {e}")
                self.heatmap = FallbackChartWidget("heatmap")
        else:
            self.heatmap = FallbackChartWidget("heatmap")
            
        heatmap_layout.addWidget(self.heatmap)
        charts_layout.addWidget(heatmap_group, 1, 0, 1, 2)
        
        layout.addWidget(charts_widget)
        self.tab_widget.addTab(tab_widget, "Advanced Charts")
        
    def create_real_time_tab(self):
        """Create real-time data demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Real-time controls
        controls_group = QGroupBox("Real-Time Data Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        start_btn = QPushButton("Start Real-Time Updates")
        start_btn.clicked.connect(self.start_real_time_updates)
        controls_layout.addWidget(start_btn)
        
        stop_btn = QPushButton("Stop Updates")
        stop_btn.clicked.connect(self.stop_real_time_updates)
        controls_layout.addWidget(stop_btn)
        
        controls_layout.addWidget(QLabel("Update Rate:"))
        self.update_rate_spin = QSpinBox()
        self.update_rate_spin.setRange(50, 5000)
        self.update_rate_spin.setValue(500)
        self.update_rate_spin.setSuffix(" ms")
        controls_layout.addWidget(self.update_rate_spin)
        
        controls_layout.addWidget(QLabel("Data Points:"))
        self.max_points_spin = QSpinBox()
        self.max_points_spin.setRange(10, 200)
        self.max_points_spin.setValue(50)
        controls_layout.addWidget(self.max_points_spin)
        
        layout.addWidget(controls_group)
        
        # Real-time charts
        charts_widget = QWidget()
        charts_layout = QGridLayout(charts_widget)
        
        # Real-time line chart
        realtime_group = QGroupBox("Real-Time Line Chart")
        realtime_layout = QVBoxLayout(realtime_group)
        
        self.realtime_chart = FallbackChartWidget("line")
        realtime_layout.addWidget(self.realtime_chart)
        charts_layout.addWidget(realtime_group, 0, 0, 1, 2)
        
        # Metrics cards
        metrics_group = QGroupBox("Live Metrics")
        metrics_layout = QGridLayout(metrics_group)
        
        self.current_value_label = QLabel("Current: --")
        self.current_value_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        metrics_layout.addWidget(self.current_value_label, 0, 0)
        
        self.average_value_label = QLabel("Average: --")
        self.average_value_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        metrics_layout.addWidget(self.average_value_label, 0, 1)
        
        self.min_value_label = QLabel("Min: --")
        self.min_value_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        metrics_layout.addWidget(self.min_value_label, 1, 0)
        
        self.max_value_label = QLabel("Max: --")
        self.max_value_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        metrics_layout.addWidget(self.max_value_label, 1, 1)
        
        charts_layout.addWidget(metrics_group, 1, 0, 1, 2)
        
        layout.addWidget(charts_widget)
        self.tab_widget.addTab(tab_widget, "Real-Time Data")
        
    def create_interactive_tab(self):
        """Create interactive charts demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Interactive controls
        controls_group = QGroupBox("Interactive Controls")
        controls_layout = QGridLayout(controls_group)
        
        # Data editing
        controls_layout.addWidget(QLabel("Edit Data Point:"), 0, 0)
        self.edit_index_spin = QSpinBox()
        self.edit_index_spin.setRange(0, 5)
        controls_layout.addWidget(self.edit_index_spin, 0, 1)
        
        controls_layout.addWidget(QLabel("New Value:"), 0, 2)
        self.edit_value_spin = QDoubleSpinBox()
        self.edit_value_spin.setRange(0, 1000)
        self.edit_value_spin.setValue(50)
        controls_layout.addWidget(self.edit_value_spin, 0, 3)
        
        update_point_btn = QPushButton("Update Point")
        update_point_btn.clicked.connect(self.update_data_point)
        controls_layout.addWidget(update_point_btn, 0, 4)
        
        # Chart style
        controls_layout.addWidget(QLabel("Chart Style:"), 1, 0)
        self.chart_style_combo = QComboBox()
        self.chart_style_combo.addItems(["Default", "Modern", "Classic", "Minimal"])
        self.chart_style_combo.currentTextChanged.connect(self.change_chart_style)
        controls_layout.addWidget(self.chart_style_combo, 1, 1)
        
        # Color scheme
        controls_layout.addWidget(QLabel("Color Scheme:"), 1, 2)
        self.color_scheme_combo = QComboBox()
        self.color_scheme_combo.addItems(["Blue", "Green", "Red", "Purple", "Orange", "Multi"])
        self.color_scheme_combo.currentTextChanged.connect(self.change_color_scheme)
        controls_layout.addWidget(self.color_scheme_combo, 1, 3)
        
        layout.addWidget(controls_group)
        
        # Interactive chart
        interactive_group = QGroupBox("Interactive Chart (Click to select data points)")
        interactive_layout = QVBoxLayout(interactive_group)
        
        self.interactive_chart = FallbackChartWidget("bar")
        interactive_layout.addWidget(self.interactive_chart)
        
        # Selection info
        self.selection_info = QLabel("Click on a chart element to see details")
        self.selection_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        interactive_layout.addWidget(self.selection_info)
        
        layout.addWidget(interactive_group)
        
        self.tab_widget.addTab(tab_widget, "Interactive")
        
    def create_customization_tab(self):
        """Create chart customization demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Customization controls
        controls_group = QGroupBox("Chart Customization")
        controls_layout = QGridLayout(controls_group)
        
        # Title and labels
        controls_layout.addWidget(QLabel("Chart Title:"), 0, 0)
        self.title_edit = QLineEdit("Sample Chart")
        controls_layout.addWidget(self.title_edit, 0, 1)
        
        controls_layout.addWidget(QLabel("X-Axis Label:"), 0, 2)
        self.xlabel_edit = QLineEdit("Categories")
        controls_layout.addWidget(self.xlabel_edit, 0, 3)
        
        controls_layout.addWidget(QLabel("Y-Axis Label:"), 1, 0)
        self.ylabel_edit = QLineEdit("Values")
        controls_layout.addWidget(self.ylabel_edit, 1, 1)
        
        # Appearance
        controls_layout.addWidget(QLabel("Grid Style:"), 1, 2)
        self.grid_style_combo = QComboBox()
        self.grid_style_combo.addItems(["None", "Solid", "Dashed", "Dotted"])
        controls_layout.addWidget(self.grid_style_combo, 1, 3)
        
        controls_layout.addWidget(QLabel("Background:"), 2, 0)
        self.background_combo = QComboBox()
        self.background_combo.addItems(["Transparent", "White", "Light Gray", "Dark"])
        controls_layout.addWidget(self.background_combo, 2, 1)
        
        # Fonts
        controls_layout.addWidget(QLabel("Font Size:"), 2, 2)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        controls_layout.addWidget(self.font_size_spin, 2, 3)
        
        # Apply changes
        apply_btn = QPushButton("Apply Customization")
        apply_btn.clicked.connect(self.apply_customization)
        controls_layout.addWidget(apply_btn, 3, 0, 1, 4)
        
        layout.addWidget(controls_group)
        
        # Customizable chart
        custom_group = QGroupBox("Customizable Chart")
        custom_layout = QVBoxLayout(custom_group)
        
        self.custom_chart = FallbackChartWidget("bar")
        custom_layout.addWidget(self.custom_chart)
        
        layout.addWidget(custom_group)
        
        # Export options
        export_group = QGroupBox("Export Options")
        export_layout = QHBoxLayout(export_group)
        
        export_png_btn = QPushButton("Export as PNG")
        export_png_btn.clicked.connect(self.export_as_png)
        export_layout.addWidget(export_png_btn)
        
        export_svg_btn = QPushButton("Export as SVG")
        export_svg_btn.clicked.connect(self.export_as_svg)
        export_layout.addWidget(export_svg_btn)
        
        export_data_btn = QPushButton("Export Data")
        export_data_btn.clicked.connect(self.export_data)
        export_layout.addWidget(export_data_btn)
        
        layout.addWidget(export_group)
        
        self.tab_widget.addTab(tab_widget, "Customization")
        
    def create_sample_data(self):
        """Create sample data for charts."""
        return [
            ("Product A", 45, QColor(100, 150, 200)),
            ("Product B", 67, QColor(200, 100, 150)),
            ("Product C", 23, QColor(150, 200, 100)),
            ("Product D", 89, QColor(200, 150, 100)),
            ("Product E", 56, QColor(150, 100, 200)),
            ("Product F", 34, QColor(100, 200, 150))
        ]
        
    def create_time_series_data(self):
        """Create time series data for line charts."""
        data = []
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            date = start_date + timedelta(days=i)
            value = 50 + 30 * math.sin(i * 0.2) + random.uniform(-10, 10)
            data.append((date.strftime("%m/%d"), value))
            
        return data
        
    def populate_charts(self):
        """Populate all charts with initial data."""
        # Simple charts
        if hasattr(self, 'bar_chart'):
            self.bar_chart.setData(self.sample_data)
        if hasattr(self, 'line_chart'):
            self.line_chart.setData(self.time_series_data)
        if hasattr(self, 'pie_chart'):
            self.pie_chart.setData(self.sample_data)
        if hasattr(self, 'gauge_chart'):
            if hasattr(self.gauge_chart, 'setValue'):
                self.gauge_chart.setValue(75)
                
        # Advanced charts
        if hasattr(self, 'area_chart'):
            self.area_chart.setData(self.time_series_data)
        if hasattr(self, 'scatter_chart'):
            scatter_data = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(20)]
            self.scatter_chart.setData(scatter_data)
        if hasattr(self, 'heatmap'):
            heatmap_data = [[random.uniform(0, 100) for _ in range(10)] for _ in range(10)]
            self.heatmap.setData(heatmap_data)
            
        # Interactive chart
        if hasattr(self, 'interactive_chart'):
            self.interactive_chart.setData(self.sample_data)
            
        # Custom chart
        if hasattr(self, 'custom_chart'):
            self.custom_chart.setData(self.sample_data)
        
    # Event handlers
    def regenerate_data(self):
        """Regenerate sample data."""
        count = self.data_count_spin.value()
        new_data = []
        colors = [QColor(100, 150, 200), QColor(200, 100, 150), QColor(150, 200, 100),
                 QColor(200, 150, 100), QColor(150, 100, 200), QColor(100, 200, 150)]
        
        for i in range(count):
            label = f"Item {chr(65 + i)}"  # A, B, C, etc.
            value = random.uniform(10, 100)
            color = colors[i % len(colors)]
            new_data.append((label, value, color))
            
        self.sample_data = new_data
        
        # Update charts
        if hasattr(self, 'bar_chart'):
            self.bar_chart.setData(self.sample_data)
        if hasattr(self, 'interactive_chart'):
            self.interactive_chart.setData(self.sample_data)
        if hasattr(self, 'custom_chart'):
            self.custom_chart.setData(self.sample_data)
            
        self.statusBar().showMessage(f"Generated {count} new data points")
        
    def update_chart_style(self):
        """Update chart display style."""
        show_values = self.show_values_check.isChecked()
        show_grid = self.show_grid_check.isChecked()
        
        # Update chart properties if available
        for chart in [getattr(self, attr, None) for attr in ['bar_chart', 'line_chart']]:
            if chart and hasattr(chart, 'setShowValues'):
                chart.setShowValues(show_values)
            if chart and hasattr(chart, 'setShowGrid'):
                chart.setShowGrid(show_grid)
                
        self.statusBar().showMessage("Chart style updated")
        
    def add_data_point(self):
        """Add a new data point to charts."""
        new_label = f"New {len(self.sample_data) + 1}"
        new_value = random.uniform(10, 100)
        new_color = QColor(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        
        self.sample_data.append((new_label, new_value, new_color))
        
        # Update relevant charts
        for chart in [getattr(self, attr, None) for attr in ['bar_chart', 'interactive_chart', 'custom_chart']]:
            if chart and hasattr(chart, 'setData'):
                chart.setData(self.sample_data)
                
        self.statusBar().showMessage("Data point added")
        
    def remove_data_point(self):
        """Remove the last data point from charts."""
        if self.sample_data:
            removed = self.sample_data.pop()
            
            # Update relevant charts
            for chart in [getattr(self, attr, None) for attr in ['bar_chart', 'interactive_chart', 'custom_chart']]:
                if chart and hasattr(chart, 'setData'):
                    chart.setData(self.sample_data)
                    
            self.statusBar().showMessage(f"Removed data point: {removed[0]}")
        else:
            self.statusBar().showMessage("No data points to remove")
            
    def start_real_time_updates(self):
        """Start real-time data updates."""
        interval = self.update_rate_spin.value()
        self.update_timer.start(interval)
        self.real_time_data = []
        self.statusBar().showMessage("Real-time updates started")
        
    def stop_real_time_updates(self):
        """Stop real-time data updates."""
        self.update_timer.stop()
        self.statusBar().showMessage("Real-time updates stopped")
        
    def update_real_time_data(self):
        """Update real-time data and chart."""
        max_points = self.max_points_spin.value()
        
        # Generate new data point
        timestamp = datetime.now().strftime("%H:%M:%S")
        value = 50 + 30 * math.sin(len(self.real_time_data) * 0.1) + random.uniform(-10, 10)
        
        self.real_time_data.append((timestamp, value))
        
        # Keep only the latest points
        if len(self.real_time_data) > max_points:
            self.real_time_data = self.real_time_data[-max_points:]
            
        # Update chart
        if hasattr(self, 'realtime_chart'):
            self.realtime_chart.setData(self.real_time_data)
            
        # Update metrics
        if self.real_time_data:
            values = [point[1] for point in self.real_time_data]
            current = values[-1]
            average = sum(values) / len(values)
            minimum = min(values)
            maximum = max(values)
            
            self.current_value_label.setText(f"Current: {current:.1f}")
            self.average_value_label.setText(f"Average: {average:.1f}")
            self.min_value_label.setText(f"Min: {minimum:.1f}")
            self.max_value_label.setText(f"Max: {maximum:.1f}")
            
    def update_data_point(self):
        """Update a specific data point."""
        index = self.edit_index_spin.value()
        new_value = self.edit_value_spin.value()
        
        if 0 <= index < len(self.sample_data):
            label, old_value, color = self.sample_data[index]
            self.sample_data[index] = (label, new_value, color)
            
            # Update charts
            for chart in [getattr(self, attr, None) for attr in ['bar_chart', 'interactive_chart', 'custom_chart']]:
                if chart and hasattr(chart, 'setData'):
                    chart.setData(self.sample_data)
                    
            self.statusBar().showMessage(f"Updated {label}: {old_value:.1f} → {new_value:.1f}")
        else:
            self.statusBar().showMessage("Invalid data point index")
            
    def change_chart_style(self, style):
        """Change chart visual style."""
        self.statusBar().showMessage(f"Chart style changed to: {style}")
        
    def change_color_scheme(self, scheme):
        """Change chart color scheme."""
        # Generate new colors based on scheme
        if scheme == "Blue":
            base_color = QColor(100, 150, 255)
        elif scheme == "Green":
            base_color = QColor(100, 255, 150)
        elif scheme == "Red":
            base_color = QColor(255, 100, 150)
        elif scheme == "Purple":
            base_color = QColor(200, 100, 255)
        elif scheme == "Orange":
            base_color = QColor(255, 200, 100)
        else:  # Multi-color
            base_color = None
            
        if base_color:
            # Update data colors
            for i, (label, value, _) in enumerate(self.sample_data):
                # Create variations of the base color
                hue_shift = i * 30
                new_color = QColor(base_color)
                h, s, v, a = new_color.getHsv()
                new_color.setHsv((h + hue_shift) % 360, s, v, a)
                self.sample_data[i] = (label, value, new_color)
                
            # Update charts
            for chart in [getattr(self, attr, None) for attr in ['bar_chart', 'interactive_chart', 'custom_chart']]:
                if chart and hasattr(chart, 'setData'):
                    chart.setData(self.sample_data)
                    
        self.statusBar().showMessage(f"Color scheme changed to: {scheme}")
        
    def apply_customization(self):
        """Apply chart customization settings."""
        title = self.title_edit.text()
        xlabel = self.xlabel_edit.text()
        ylabel = self.ylabel_edit.text()
        
        # Update chart if it supports these properties
        if hasattr(self.custom_chart, 'setTitle'):
            self.custom_chart.setTitle(title)
        if hasattr(self.custom_chart, 'setXLabel'):
            self.custom_chart.setXLabel(xlabel)
        if hasattr(self.custom_chart, 'setYLabel'):
            self.custom_chart.setYLabel(ylabel)
            
        self.statusBar().showMessage("Chart customization applied")
        
    def export_as_png(self):
        """Export chart as PNG image."""
        self.statusBar().showMessage("Chart exported as PNG (demo)")
        
    def export_as_svg(self):
        """Export chart as SVG image."""
        self.statusBar().showMessage("Chart exported as SVG (demo)")
        
    def export_data(self):
        """Export chart data."""
        data_text = "Chart Data:\\n"
        for i, (label, value, color) in enumerate(self.sample_data):
            data_text += f"{i+1}. {label}: {value:.2f}\\n"
            
        QMessageBox.information(self, "Chart Data", data_text)


def main():
    """Main function to run the demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Data Charts Components Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Simple Fluent Widget")
    
    # Create and show the demo
    demo = DataChartsDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
