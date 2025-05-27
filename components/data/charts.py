"""
Fluent Design Data Visualization Components
Charts, graphs, and data visualization widgets
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QScrollArea, QSizePolicy, QGridLayout)
from PySide6.QtCore import Qt, Signal, QTimer, QRect, QPointF
from PySide6.QtGui import (QPainter, QColor, QBrush, QPen, QFont, QLinearGradient, 
                          QRadialGradient, QPainterPath, QPolygonF)
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional, List, Dict, Any, Tuple
import math


class FluentProgressRing(QWidget):
    """Fluent Design style progress ring"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._value = 0
        self._minimum = 0
        self._maximum = 100
        self._text_visible = True
        self._thickness = 8
        
        self.setFixedSize(80, 80)
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def setValue(self, value: int):
        """Set progress value"""
        self._value = max(self._minimum, min(self._maximum, value))
        self.update()

    def setRange(self, minimum: int, maximum: int):
        """Set value range"""
        self._minimum = minimum
        self._maximum = maximum
        self.update()

    def setTextVisible(self, visible: bool):
        """Set text visibility"""
        self._text_visible = visible
        self.update()

    def setThickness(self, thickness: int):
        """Set ring thickness"""
        self._thickness = thickness
        self.update()

    def paintEvent(self, event):
        """Paint progress ring"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = theme_manager
        
        # Calculate dimensions
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - self._thickness
        
        # Draw background ring
        pen = QPen(theme.get_color('border'), self._thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawEllipse(center.x() - radius, center.y() - radius, 
                          radius * 2, radius * 2)
        
        # Draw progress arc
        if self._maximum > self._minimum:
            progress = (self._value - self._minimum) / (self._maximum - self._minimum)
            span_angle = int(progress * 360 * 16)  # Qt uses 1/16th degree units
            
            pen = QPen(theme.get_color('primary'), self._thickness)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            
            painter.drawArc(center.x() - radius, center.y() - radius,
                          radius * 2, radius * 2, 90 * 16, -span_angle)
        
        # Draw text
        if self._text_visible:
            painter.setPen(QPen(theme.get_color('text_primary')))
            painter.setFont(QFont("", 12, QFont.Weight.Bold))
            
            if self._maximum > self._minimum:
                percentage = int((self._value - self._minimum) / (self._maximum - self._minimum) * 100)
                text = f"{percentage}%"
            else:
                text = "0%"
            
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    def _setup_style(self):
        """Setup style"""
        self.setStyleSheet(f"""
            FluentProgressRing {{
                background-color: transparent;
            }}
        """)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self.update()


class FluentBarChart(QWidget):
    """Fluent Design style bar chart"""
    
    bar_clicked = Signal(int, str, float)  # index, label, value
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._data = []  # List of (label, value, color) tuples
        self._show_values = True
        self._show_grid = True
        self._animation_enabled = True
        self._animated_values = []
        
        self.setMinimumSize(300, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._animate_bars)
        
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def setData(self, data: List[Tuple[str, float, Optional[QColor]]]):
        """Set chart data
        
        Args:
            data: List of (label, value, color) tuples
        """
        self._data = data
        self._animated_values = [0.0] * len(data)
        
        if self._animation_enabled:
            self._start_animation()
        else:
            self._animated_values = [item[1] for item in data]
            self.update()

    def setShowValues(self, show: bool):
        """Set value display visibility"""
        self._show_values = show
        self.update()

    def setShowGrid(self, show: bool):
        """Set grid visibility"""
        self._show_grid = show
        self.update()

    def setAnimationEnabled(self, enabled: bool):
        """Set animation enabled"""
        self._animation_enabled = enabled

    def _start_animation(self):
        """Start bar animation"""
        self._animation_timer.start(16)  # ~60 FPS

    def _animate_bars(self):
        """Animate bar values"""
        all_complete = True
        
        for i, (_, target_value, _) in enumerate(self._data):
            current = self._animated_values[i]
            diff = target_value - current
            
            if abs(diff) > 0.1:
                self._animated_values[i] += diff * 0.1
                all_complete = False
            else:
                self._animated_values[i] = target_value
        
        self.update()
        
        if all_complete:
            self._animation_timer.stop()

    def paintEvent(self, event):
        """Paint bar chart"""
        if not self._data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = theme_manager
        rect = self.rect()
        margin = 40
        chart_rect = QRect(margin, margin, rect.width() - 2 * margin, 
                          rect.height() - 2 * margin)
        
        # Find max value for scaling
        max_value = max(abs(val) for _, val, _ in self._data) if self._data else 1
        if max_value == 0:
            max_value = 1
        
        # Draw grid
        if self._show_grid:
            self._draw_grid(painter, chart_rect, max_value)
        
        # Draw bars
        bar_width = chart_rect.width() / len(self._data) * 0.8
        bar_spacing = chart_rect.width() / len(self._data) * 0.2
        
        for i, ((label, value, color), animated_value) in enumerate(zip(self._data, self._animated_values)):
            x = chart_rect.left() + i * (bar_width + bar_spacing) + bar_spacing / 2
            bar_height = (animated_value / max_value) * chart_rect.height()
            y = chart_rect.bottom() - bar_height
            
            # Use provided color or default
            bar_color = color if color else theme.get_color('primary')
            
            # Create gradient
            gradient = QLinearGradient(0, y, 0, chart_rect.bottom())
            gradient.setColorAt(0, bar_color)
            gradient.setColorAt(1, bar_color.darker(120))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(bar_color.darker(130), 1))
            
            bar_rect = QRect(int(x), int(y), int(bar_width), int(bar_height))
            painter.drawRoundedRect(bar_rect, 4, 4)
            
            # Draw value text
            if self._show_values and animated_value > 0:
                painter.setPen(QPen(theme.get_color('text_primary')))
                painter.setFont(QFont("", 9))
                value_text = f"{value:.1f}"
                painter.drawText(bar_rect.adjusted(0, -20, 0, -5), 
                               Qt.AlignmentFlag.AlignCenter, value_text)
            
            # Draw label
            painter.setPen(QPen(theme.get_color('text_secondary')))
            painter.setFont(QFont("", 8))
            label_rect = QRect(int(x), chart_rect.bottom() + 5, 
                             int(bar_width), 20)
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, label)

    def _draw_grid(self, painter: QPainter, rect: QRect, max_value: float):
        """Draw chart grid"""
        theme = theme_manager
        painter.setPen(QPen(theme.get_color('border'), 1, Qt.PenStyle.DotLine))
        
        # Horizontal grid lines
        for i in range(5):
            y = rect.top() + (rect.height() / 4) * i
            painter.drawLine(rect.left(), int(y), rect.right(), int(y))
            
            # Grid value labels
            value = max_value * (1 - i / 4)
            painter.setPen(QPen(theme.get_color('text_secondary')))
            painter.setFont(QFont("", 8))
            painter.drawText(QRect(5, int(y) - 10, 30, 20), 
                           Qt.AlignmentFlag.AlignCenter, f"{value:.1f}")
            painter.setPen(QPen(theme.get_color('border'), 1, Qt.PenStyle.DotLine))

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if not self._data:
            return
            
        margin = 40
        chart_rect = QRect(margin, margin, self.width() - 2 * margin, 
                          self.height() - 2 * margin)
        
        bar_width = chart_rect.width() / len(self._data) * 0.8
        bar_spacing = chart_rect.width() / len(self._data) * 0.2
        
        for i, (label, value, _) in enumerate(self._data):
            x = chart_rect.left() + i * (bar_width + bar_spacing) + bar_spacing / 2
            bar_rect = QRect(int(x), chart_rect.top(), int(bar_width), chart_rect.height())
            
            if bar_rect.contains(event.pos()):
                self.bar_clicked.emit(i, label, value)
                break

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager
        self.setStyleSheet(f"""
            FluentBarChart {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
        """)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self.update()


class FluentLineChart(QWidget):
    """Fluent Design style line chart"""
    
    point_clicked = Signal(int, float, float)  # index, x_value, y_value
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._data_series = []  # List of (name, data_points, color) tuples
        self._show_points = True
        self._show_grid = True
        self._smooth_lines = True
        
        self.setMinimumSize(400, 250)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def addSeries(self, name: str, data_points: List[Tuple[float, float]], 
                  color: Optional[QColor] = None):
        """Add data series
        
        Args:
            name: Series name
            data_points: List of (x, y) value tuples
            color: Line color (optional)
        """
        if not color:
            # Use different colors for each series
            colors = [
                theme_manager.get_color('primary'),
                QColor("#28a745"),
                QColor("#ffc107"),
                QColor("#dc3545"),
                QColor("#17a2b8"),
                QColor("#6f42c1")
            ]
            color = colors[len(self._data_series) % len(colors)]
        
        self._data_series.append((name, data_points, color))
        self.update()

    def clearSeries(self):
        """Clear all data series"""
        self._data_series.clear()
        self.update()

    def setShowPoints(self, show: bool):
        """Set point markers visibility"""
        self._show_points = show
        self.update()

    def setShowGrid(self, show: bool):
        """Set grid visibility"""
        self._show_grid = show
        self.update()

    def setSmoothLines(self, smooth: bool):
        """Set line smoothing"""
        self._smooth_lines = smooth
        self.update()

    def paintEvent(self, event):
        """Paint line chart"""
        if not self._data_series:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = theme_manager
        rect = self.rect()
        margin = 50
        chart_rect = QRect(margin, margin, rect.width() - 2 * margin, 
                          rect.height() - 2 * margin)
        
        # Find value ranges
        all_x = []
        all_y = []
        for _, points, _ in self._data_series:
            for x, y in points:
                all_x.append(x)
                all_y.append(y)
        
        if not all_x or not all_y:
            return
            
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        
        # Add padding to ranges
        x_range = max_x - min_x if max_x != min_x else 1
        y_range = max_y - min_y if max_y != min_y else 1
        
        min_x -= x_range * 0.05
        max_x += x_range * 0.05
        min_y -= y_range * 0.05
        max_y += y_range * 0.05
        
        # Draw grid
        if self._show_grid:
            self._draw_chart_grid(painter, chart_rect, min_x, max_x, min_y, max_y)
        
        # Draw series
        for name, points, color in self._data_series:
            if len(points) < 2:
                continue
                
            # Convert points to screen coordinates
            screen_points = []
            for x, y in points:
                screen_x = chart_rect.left() + (x - min_x) / (max_x - min_x) * chart_rect.width()
                screen_y = chart_rect.bottom() - (y - min_y) / (max_y - min_y) * chart_rect.height()
                screen_points.append(QPointF(screen_x, screen_y))
            
            # Draw line
            pen = QPen(color, 2)
            painter.setPen(pen)
            
            if self._smooth_lines and len(screen_points) > 2:
                # Draw smooth curve
                path = QPainterPath()
                path.moveTo(screen_points[0])
                
                for i in range(1, len(screen_points)):
                    if i == len(screen_points) - 1:
                        path.lineTo(screen_points[i])
                    else:
                        # Simple curve approximation
                        cp1 = screen_points[i - 1]
                        cp2 = screen_points[i]
                        path.quadTo(cp1, cp2)
                
                painter.drawPath(path)
            else:
                # Draw straight lines
                for i in range(len(screen_points) - 1):
                    painter.drawLine(screen_points[i], screen_points[i + 1])
            
            # Draw points
            if self._show_points:
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(color.darker(120), 1))
                
                for point in screen_points:
                    painter.drawEllipse(point, 4, 4)

    def _draw_chart_grid(self, painter: QPainter, rect: QRect, 
                        min_x: float, max_x: float, min_y: float, max_y: float):
        """Draw chart grid and axes"""
        theme = theme_manager
        painter.setPen(QPen(theme.get_color('border'), 1, Qt.PenStyle.DotLine))
        
        # Vertical grid lines
        for i in range(6):
            x = rect.left() + (rect.width() / 5) * i
            painter.drawLine(int(x), rect.top(), int(x), rect.bottom())
            
            # X-axis labels
            value = min_x + (max_x - min_x) * (i / 5)
            painter.setPen(QPen(theme.get_color('text_secondary')))
            painter.setFont(QFont("", 8))
            painter.drawText(QRect(int(x) - 20, rect.bottom() + 5, 40, 20), 
                           Qt.AlignmentFlag.AlignCenter, f"{value:.1f}")
            painter.setPen(QPen(theme.get_color('border'), 1, Qt.PenStyle.DotLine))
        
        # Horizontal grid lines
        for i in range(6):
            y = rect.top() + (rect.height() / 5) * i
            painter.drawLine(rect.left(), int(y), rect.right(), int(y))
            
            # Y-axis labels
            value = max_y - (max_y - min_y) * (i / 5)
            painter.setPen(QPen(theme.get_color('text_secondary')))
            painter.setFont(QFont("", 8))
            painter.drawText(QRect(5, int(y) - 10, 35, 20), 
                           Qt.AlignmentFlag.AlignCenter, f"{value:.1f}")
            painter.setPen(QPen(theme.get_color('border'), 1, Qt.PenStyle.DotLine))

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager
        self.setStyleSheet(f"""
            FluentLineChart {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
        """)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self.update()


class FluentPieChart(QWidget):
    """Fluent Design style pie chart"""
    
    slice_clicked = Signal(int, str, float)  # index, label, value
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._data = []  # List of (label, value, color) tuples
        self._show_labels = True
        self._show_percentages = True
        self._exploded_slice = -1
        
        self.setMinimumSize(250, 250)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
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

    def explodeSlice(self, index: int):
        """Explode a pie slice"""
        self._exploded_slice = index
        self.update()

    def paintEvent(self, event):
        """Paint pie chart"""
        if not self._data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 50
        
        # Calculate total value
        total_value = sum(value for _, value, _ in self._data)
        if total_value == 0:
            return
        
        # Draw slices
        start_angle = 0
        
        for i, (label, value, color) in enumerate(self._data):
            span_angle = int((value / total_value) * 360 * 16)  # Qt uses 1/16th degree units
            
            # Use provided color or generate one
            if not color:
                colors = [
                    theme_manager.get_color('primary'),
                    QColor("#28a745"),
                    QColor("#ffc107"),
                    QColor("#dc3545"),
                    QColor("#17a2b8"),
                    QColor("#6f42c1"),
                    QColor("#fd7e14"),
                    QColor("#20c997")
                ]
                color = colors[i % len(colors)]
            
            # Calculate slice position
            slice_center = QPointF(center)
            if i == self._exploded_slice:
                # Move exploded slice outward
                angle_rad = math.radians((start_angle + span_angle // 2) / 16)
                offset_x = math.cos(angle_rad) * 15
                offset_y = math.sin(angle_rad) * 15
                slice_center = QPointF(center.x() + offset_x, center.y() + offset_y)
            
            # Create gradient
            gradient = QRadialGradient(slice_center, radius)
            gradient.setColorAt(0, color.lighter(120))
            gradient.setColorAt(1, color)
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(color.darker(120), 2))
            
            # Draw slice
            pie_rect = QRect(int(slice_center.x() - radius), int(slice_center.y() - radius),
                           radius * 2, radius * 2)
            painter.drawPie(pie_rect, start_angle, span_angle)
            
            # Draw label
            if self._show_labels or self._show_percentages:
                angle_rad = math.radians((start_angle + span_angle // 2) / 16)
                label_x = center.x() + math.cos(angle_rad) * (radius + 20)
                label_y = center.y() + math.sin(angle_rad) * (radius + 20)
                
                text_parts = []
                if self._show_labels:
                    text_parts.append(label)
                if self._show_percentages:
                    percentage = (value / total_value) * 100
                    text_parts.append(f"({percentage:.1f}%)")
                
                text = " ".join(text_parts)
                
                painter.setPen(QPen(theme_manager.get_color('text_primary')))
                painter.setFont(QFont("", 9))
                
                # Calculate text position
                metrics = painter.fontMetrics()
                text_width = metrics.horizontalAdvance(text)
                text_height = metrics.height()
                
                text_rect = QRect(int(label_x - text_width // 2), 
                                int(label_y - text_height // 2),
                                text_width, text_height)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
            
            start_angle += span_angle

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if not self._data:
            return
            
        center = self.rect().center()
        click_pos = event.pos()
        
        # Calculate angle from center to click position
        dx = click_pos.x() - center.x()
        dy = click_pos.y() - center.y()
        
        click_angle = math.degrees(math.atan2(dy, dx))
        if click_angle < 0:
            click_angle += 360
        
        # Find which slice was clicked
        total_value = sum(value for _, value, _ in self._data)
        current_angle = 0
        
        for i, (label, value, _) in enumerate(self._data):
            slice_angle = (value / total_value) * 360
            
            if current_angle <= click_angle <= current_angle + slice_angle:
                self.slice_clicked.emit(i, label, value)
                self.explodeSlice(i)
                break
                
            current_angle += slice_angle

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager
        self.setStyleSheet(f"""
            FluentPieChart {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
        """)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self.update()
