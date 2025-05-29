"""
Fluent Design Basic Charts Components
Simple and lightweight chart components with clean Fluent Design
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, Signal, QRect, QPointF, QTimer
from PySide6.QtGui import (QPainter, QColor, QBrush, QPen, QFont, QLinearGradient, 
                          QRadialGradient, QPainterPath, QConicalGradient)
from core.theme import theme_manager
from typing import Optional, List, Dict, Any, Tuple
import math


class FluentSimpleBarChart(QWidget):
    """Simple Fluent Design bar chart without animations"""
    
    bar_clicked = Signal(int, str, float)  # index, label, value
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._data = []  # List of (label, value, color) tuples
        self._show_values = True
        self._show_grid = True
        self._max_value = None  # Auto-scale if None
        
        self.setMinimumSize(250, 150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def setData(self, data: List[Tuple[str, float, Optional[QColor]]]):
        """Set chart data"""
        self._data = data
        self.update()
    
    def setShowValues(self, show: bool):
        """Set value display visibility"""
        self._show_values = show
        self.update()
    
    def setShowGrid(self, show: bool):
        """Set grid visibility"""
        self._show_grid = show
        self.update()
    
    def setMaxValue(self, max_value: Optional[float]):
        """Set maximum value for Y-axis (None for auto-scale)"""
        self._max_value = max_value
        self.update()
    
    def paintEvent(self, event):
        """Paint bar chart"""
        if not self._data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = theme_manager
        rect = self.rect()
        
        # Calculate chart area
        margin = 30
        chart_rect = QRect(margin, margin, 
                          rect.width() - 2 * margin, 
                          rect.height() - 2 * margin)
        
        # Find max value for scaling
        max_value = self._max_value if self._max_value else max(item[1] for item in self._data)
        if max_value == 0:
            max_value = 1
            
        # Draw grid if enabled
        if self._show_grid:
            self._draw_grid(painter, chart_rect, max_value)
        
        # Draw bars
        bar_width = chart_rect.width() / len(self._data) * 0.7
        bar_spacing = chart_rect.width() / len(self._data) * 0.3
        
        for i, (label, value, color) in enumerate(self._data):
            # Calculate bar dimensions
            bar_height = (value / max_value) * chart_rect.height()
            bar_x = chart_rect.x() + i * (bar_width + bar_spacing) + bar_spacing / 2
            bar_y = chart_rect.bottom() - bar_height
            
            # Use provided color or default theme color
            if color:
                bar_color = color
            else:
                colors = [theme.get_color('primary'), theme.get_color('accent'), 
                         theme.get_color('secondary')]
                bar_color = colors[i % len(colors)]
            
            # Draw bar
            painter.fillRect(int(bar_x), int(bar_y), int(bar_width), int(bar_height), 
                           QBrush(bar_color))
            
            # Draw value text if enabled
            if self._show_values and value > 0:
                painter.setPen(QPen(theme.get_color('text_primary')))
                painter.setFont(QFont("", 9))
                value_text = f"{value:.1f}"
                painter.drawText(int(bar_x), int(bar_y - 5), int(bar_width), 15,
                               Qt.AlignmentFlag.AlignCenter, value_text)
            
            # Draw label
            painter.setPen(QPen(theme.get_color('text_secondary')))
            painter.setFont(QFont("", 8))
            painter.drawText(int(bar_x), chart_rect.bottom() + 5, int(bar_width), 15,
                           Qt.AlignmentFlag.AlignCenter, label)
    
    def _draw_grid(self, painter: QPainter, chart_rect: QRect, max_value: float):
        """Draw grid lines"""
        theme = theme_manager
        painter.setPen(QPen(theme.get_color('border'), 1, Qt.PenStyle.DashLine))
        
        # Draw horizontal grid lines
        grid_lines = 4
        for i in range(grid_lines + 1):
            y = chart_rect.bottom() - (i / grid_lines) * chart_rect.height()
            painter.drawLine(chart_rect.left(), int(y), chart_rect.right(), int(y))
    
    def mousePressEvent(self, event):
        """Handle bar click"""
        if not self._data:
            return
            
        # Calculate which bar was clicked
        margin = 30
        chart_rect = QRect(margin, margin, 
                          self.rect().width() - 2 * margin, 
                          self.rect().height() - 2 * margin)
        
        bar_width = chart_rect.width() / len(self._data) * 0.7
        bar_spacing = chart_rect.width() / len(self._data) * 0.3
        
        for i, (label, value, color) in enumerate(self._data):
            bar_x = chart_rect.x() + i * (bar_width + bar_spacing) + bar_spacing / 2
            
            if bar_x <= event.x() <= bar_x + bar_width:
                self.bar_clicked.emit(i, label, value)
                break
        
        super().mousePressEvent(event)
    
    def _setup_style(self):
        """Setup style"""
        self.setStyleSheet(f"""
            FluentSimpleBarChart {{
                background-color: transparent;
                border: none;
            }}
        """)
    
    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self.update()


class FluentSimpleLineChart(QWidget):
    """Simple Fluent Design line chart without animations"""
    
    point_clicked = Signal(int, float, float)  # index, x_value, y_value
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._data_series = []  # List of data series
        self._show_points = True
        self._show_grid = True
        self._smooth_curves = False
        
        self.setMinimumSize(300, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def addDataSeries(self, name: str, data: List[Tuple[float, float]], 
                     color: Optional[QColor] = None):
        """Add a data series"""
        if color is None:
            colors = [theme_manager.get_color('primary'), 
                     theme_manager.get_color('accent'),
                     theme_manager.get_color('secondary'),
                     theme_manager.get_color('success')]
            color = colors[len(self._data_series) % len(colors)]
        
        self._data_series.append({
            'name': name,
            'data': data,
            'color': color
        })
        
        self.update()
    
    def setShowPoints(self, show: bool):
        """Set point visibility"""
        self._show_points = show
        self.update()
    
    def setShowGrid(self, show: bool):
        """Set grid visibility"""
        self._show_grid = show
        self.update()
    
    def setSmoothCurves(self, smooth: bool):
        """Set smooth curve rendering"""
        self._smooth_curves = smooth
        self.update()
    
    def clearData(self):
        """Clear all data series"""
        self._data_series.clear()
        self.update()
    
    def paintEvent(self, event):
        """Paint line chart"""
        if not self._data_series:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = theme_manager
        rect = self.rect()
        
        # Calculate chart area
        margin = 40
        chart_rect = QRect(margin, margin, 
                          rect.width() - 2 * margin, 
                          rect.height() - 2 * margin)
        
        # Find data bounds
        all_points = []
        for series in self._data_series:
            all_points.extend(series['data'])
        
        if not all_points:
            return
            
        min_x = min(point[0] for point in all_points)
        max_x = max(point[0] for point in all_points)
        min_y = min(point[1] for point in all_points)
        max_y = max(point[1] for point in all_points)
        
        # Add padding to ranges
        x_range = max_x - min_x if max_x != min_x else 1
        y_range = max_y - min_y if max_y != min_y else 1
        
        # Draw grid if enabled
        if self._show_grid:
            self._draw_chart_grid(painter, chart_rect, min_x, max_x, min_y, max_y)
        
        # Draw data series
        for series in self._data_series:
            self._draw_series(painter, chart_rect, series, 
                            min_x, max_x, min_y, max_y)
    
    def _draw_chart_grid(self, painter: QPainter, chart_rect: QRect,
                        min_x: float, max_x: float, min_y: float, max_y: float):
        """Draw chart grid"""
        theme = theme_manager
        painter.setPen(QPen(theme.get_color('border'), 1, Qt.PenStyle.DashLine))
        
        # Draw vertical grid lines
        grid_lines = 5
        for i in range(grid_lines + 1):
            x = chart_rect.left() + (i / grid_lines) * chart_rect.width()
            painter.drawLine(int(x), chart_rect.top(), int(x), chart_rect.bottom())
        
        # Draw horizontal grid lines
        for i in range(grid_lines + 1):
            y = chart_rect.bottom() - (i / grid_lines) * chart_rect.height()
            painter.drawLine(chart_rect.left(), int(y), chart_rect.right(), int(y))
    
    def _draw_series(self, painter: QPainter, chart_rect: QRect, series: Dict,
                    min_x: float, max_x: float, min_y: float, max_y: float):
        """Draw a data series"""
        data = series['data']
        color = series['color']
        
        if len(data) < 2:
            return
        
        # Convert data points to screen coordinates
        points = []
        x_range = max_x - min_x if max_x != min_x else 1
        y_range = max_y - min_y if max_y != min_y else 1
        
        for x_val, y_val in data:
            x = chart_rect.left() + ((x_val - min_x) / x_range) * chart_rect.width()
            y = chart_rect.bottom() - ((y_val - min_y) / y_range) * chart_rect.height()
            points.append(QPointF(x, y))
        
        # Draw line
        painter.setPen(QPen(color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        
        if self._smooth_curves and len(points) > 2:
            # Draw smooth curve
            path = QPainterPath()
            path.moveTo(points[0])
            
            for i in range(1, len(points)):
                if i == 1:
                    path.lineTo(points[i])
                else:
                    # Create smooth curve using quadratic bezier
                    control_point = QPointF(
                        (points[i-1].x() + points[i].x()) / 2,
                        (points[i-1].y() + points[i].y()) / 2
                    )
                    path.quadTo(control_point, points[i])
            
            painter.drawPath(path)
        else:
            # Draw straight lines
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])
        
        # Draw points if enabled
        if self._show_points:
            painter.setPen(QPen(color.darker(120), 2))
            painter.setBrush(QBrush(color.lighter(120)))
            
            for point in points:
                painter.drawEllipse(point, 3, 3)
    
    def _setup_style(self):
        """Setup style"""
        self.setStyleSheet(f"""
            FluentSimpleLineChart {{
                background-color: transparent;
                border: none;
            }}
        """)
    
    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self.update()


class FluentSimplePieChart(QWidget):
    """Simple Fluent Design pie chart without animations"""
    
    slice_clicked = Signal(int, str, float)  # index, label, value
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._data = []  # List of (label, value, color) tuples
        self._show_labels = True
        self._show_percentages = True
        
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def setData(self, data: List[Tuple[str, float, Optional[QColor]]]):
        """Set pie chart data"""
        self._data = data
        self.update()
    
    def setShowLabels(self, show: bool):
        """Set label visibility"""
        self._show_labels = show
        self.update()
    
    def setShowPercentages(self, show: bool):
        """Set percentage visibility"""
        self._show_percentages = show
        self.update()
    
    def paintEvent(self, event):
        """Paint pie chart"""
        if not self._data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = theme_manager
        rect = self.rect()
        
        # Calculate chart area
        margin = 15
        chart_size = min(rect.width(), rect.height()) - 2 * margin
        chart_rect = QRect((rect.width() - chart_size) // 2,
                          (rect.height() - chart_size) // 2,
                          chart_size, chart_size)
        
        # Draw slices
        start_angle = 0
        total_value = sum(item[1] for item in self._data) if self._data else 1
        
        for i, (label, value, color) in enumerate(self._data):
            angle = (value / total_value) * 360
            
            # Use provided color or default theme color
            if color:
                slice_color = color
            else:
                colors = [theme.get_color('primary'), theme.get_color('accent'), 
                         theme.get_color('secondary'), theme.get_color('success'),
                         theme.get_color('warning'), theme.get_color('error')]
                slice_color = colors[i % len(colors)]
            
            # Draw slice
            painter.setBrush(QBrush(slice_color))
            painter.setPen(QPen(theme.get_color('surface'), 2))
            painter.drawPie(chart_rect, int(start_angle * 16), int(angle * 16))
            
            # Draw label if enabled
            if self._show_labels and angle > 15:  # Only show label if slice is large enough
                label_angle = start_angle + angle / 2
                label_radius = chart_size // 2 * 0.7
                
                label_x = chart_rect.center().x() + label_radius * math.cos(math.radians(label_angle))
                label_y = chart_rect.center().y() + label_radius * math.sin(math.radians(label_angle))
                
                painter.setPen(QPen(Qt.GlobalColor.white))
                painter.setFont(QFont("", 9, QFont.Weight.Bold))
                
                display_text = label
                if self._show_percentages:
                    percentage = (value / total_value) * 100
                    display_text += f"\n{percentage:.1f}%"
                
                # Draw text centered
                text_rect = QRect(int(label_x - 30), int(label_y - 10), 60, 20)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, display_text)
            
            start_angle += angle
    
    def mousePressEvent(self, event):
        """Handle slice click"""
        if not self._data:
            return
        
        # Calculate which slice was clicked
        center = self.rect().center()
        click_pos = event.pos()
        
        # Calculate angle from center to click position
        dx = click_pos.x() - center.x()
        dy = click_pos.y() - center.y()
        click_angle = math.degrees(math.atan2(dy, dx))
        if click_angle < 0:
            click_angle += 360
        
        # Find which slice contains this angle
        start_angle = 0
        total_value = sum(item[1] for item in self._data) if self._data else 1
        
        for i, (label, value, color) in enumerate(self._data):
            angle = (value / total_value) * 360
            
            if start_angle <= click_angle <= start_angle + angle:
                self.slice_clicked.emit(i, label, value)
                break
            
            start_angle += angle
        
        super().mousePressEvent(event)
    
    def _setup_style(self):
        """Setup style"""
        self.setStyleSheet(f"""
            FluentSimplePieChart {{
                background-color: transparent;
                border: none;
            }}
        """)
    
    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self.update()


class FluentGaugeChart(QWidget):
    """Fluent Design gauge chart component"""
    
    value_changed = Signal(float)  # current_value
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._min_value = 0
        self._max_value = 100
        self._current_value = 0
        self._target_value = 0
        self._title = "Gauge"
        self._unit = "%"
        self._show_value = True
        self._show_title = True
        
        # Color zones: [(start, end, color), ...]
        self._color_zones = [
            (0, 30, theme_manager.get_color('error')),
            (30, 70, theme_manager.get_color('warning')),
            (70, 100, theme_manager.get_color('success'))
        ]
        
        self.setMinimumSize(150, 150)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        # Animation timer
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._animate_value)
        
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def setValue(self, value: float, animate: bool = True):
        """Set gauge value with optional animation"""
        self._target_value = max(self._min_value, min(self._max_value, value))
        
        if animate:
            self._animation_timer.start(16)  # ~60 FPS
        else:
            self._current_value = self._target_value
            self.update()
            self.value_changed.emit(self._current_value)
    
    def setRange(self, min_value: float, max_value: float):
        """Set gauge range"""
        self._min_value = min_value
        self._max_value = max_value
        self.update()
    
    def setTitle(self, title: str):
        """Set gauge title"""
        self._title = title
        self.update()
    
    def setUnit(self, unit: str):
        """Set value unit"""
        self._unit = unit
        self.update()
    
    def setColorZones(self, zones: List[Tuple[float, float, QColor]]):
        """Set color zones: [(start, end, color), ...]"""
        self._color_zones = zones
        self.update()
    
    def paintEvent(self, event):
        """Paint gauge chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = theme_manager
        rect = self.rect()
        
        # Calculate gauge area
        margin = 20
        gauge_size = min(rect.width(), rect.height()) - 2 * margin
        gauge_rect = QRect((rect.width() - gauge_size) // 2,
                          (rect.height() - gauge_size) // 2,
                          gauge_size, gauge_size)
        
        center = gauge_rect.center()
        radius = gauge_size // 2 - 10
        
        # Draw background arc
        painter.setPen(QPen(theme.get_color('border'), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        start_angle = 225 * 16  # Start at bottom-left
        span_angle = 270 * 16   # 3/4 circle
        painter.drawArc(gauge_rect.adjusted(10, 10, -10, -10), start_angle, span_angle)
        
        # Draw color zones
        zone_angle_range = 270
        for zone_start, zone_end, zone_color in self._color_zones:
            zone_start_norm = (zone_start - self._min_value) / (self._max_value - self._min_value)
            zone_end_norm = (zone_end - self._min_value) / (self._max_value - self._min_value)
            
            zone_start_angle = start_angle + int(zone_start_norm * zone_angle_range * 16)
            zone_span_angle = int((zone_end_norm - zone_start_norm) * zone_angle_range * 16)
            
            painter.setPen(QPen(zone_color, 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(gauge_rect.adjusted(10, 10, -10, -10), zone_start_angle, zone_span_angle)
        
        # Draw value arc
        value_norm = (self._current_value - self._min_value) / (self._max_value - self._min_value)
        value_span_angle = int(value_norm * zone_angle_range * 16)
        
        # Get color for current value
        current_color = theme.get_color('primary')
        for zone_start, zone_end, zone_color in self._color_zones:
            if zone_start <= self._current_value <= zone_end:
                current_color = zone_color
                break
        
        painter.setPen(QPen(current_color, 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(gauge_rect.adjusted(10, 10, -10, -10), start_angle, value_span_angle)
        
        # Draw center circle
        painter.setBrush(QBrush(theme.get_color('surface')))
        painter.setPen(QPen(theme.get_color('border'), 2))
        center_size = 20
        painter.drawEllipse(center.x() - center_size // 2, center.y() - center_size // 2, 
                          center_size, center_size)
        
        # Draw value text
        if self._show_value:
            painter.setPen(QPen(theme.get_color('text_primary')))
            painter.setFont(QFont("", 14, QFont.Weight.Bold))
            value_text = f"{self._current_value:.1f}{self._unit}"
            painter.drawText(gauge_rect.adjusted(0, 30, 0, 0), Qt.AlignmentFlag.AlignCenter, value_text)
        
        # Draw title
        if self._show_title:
            painter.setPen(QPen(theme.get_color('text_secondary')))
            painter.setFont(QFont("", 10))
            painter.drawText(gauge_rect.adjusted(0, -30, 0, 0), Qt.AlignmentFlag.AlignCenter, self._title)
    
    def _animate_value(self):
        """Animate value change"""
        diff = self._target_value - self._current_value
        if abs(diff) < 0.1:
            self._current_value = self._target_value
            self._animation_timer.stop()
        else:
            self._current_value += diff * 0.1
        
        self.update()
        self.value_changed.emit(self._current_value)
    
    def _setup_style(self):
        """Setup style"""
        self.setStyleSheet(f"""
            FluentGaugeChart {{
                background-color: transparent;
                border: none;
            }}
        """)
    
    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self.update()


# Export all basic chart components
__all__ = [
    'FluentSimpleBarChart',
    'FluentSimpleLineChart', 
    'FluentSimplePieChart',
    'FluentGaugeChart'
]