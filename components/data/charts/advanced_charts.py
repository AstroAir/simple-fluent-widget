"""
Advanced Fluent Design Data Visualization Components
Specialized charts, graphs, and data visualization widgets
"""

from PySide6.QtWidgets import (
    QWidget
)
from PySide6.QtCore import (
    Qt, Signal, QRectF, QPointF
)
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QLinearGradient,
    QPainterPath, QFontMetrics,
    QPaintEvent, QMouseEvent
)
from core.theme import theme_manager
from typing import Optional, List, Dict, Any, Tuple, Union
import math
from enum import Enum


class ChartType(Enum):
    """Chart type enumeration"""
    AREA = "area"
    SCATTER = "scatter"
    CANDLESTICK = "candlestick"
    HEATMAP = "heatmap"
    BUBBLE = "bubble"
    RADAR = "radar"
    GANTT = "gantt"


class FluentAreaChart(QWidget):
    """Fluent Design area chart with gradient fills"""

    # Signals
    pointHovered = Signal(int, object)  # series_index, data_point
    pointClicked = Signal(int, object)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.series_data = []  # List of series
        self.x_labels = []
        self.y_range = (0, 100)
        self.show_grid = True
        self.show_legend = True
        self.show_points = True
        self.fill_opacity = 0.3
        self.hover_point = None

        self.setMinimumSize(300, 200)
        self.setup_style()
        theme_manager.theme_changed.connect(self.apply_theme)

    def add_series(self, name: str, data: List[Tuple[Union[str, float], float]],
                   color: Optional[QColor] = None, fill_color: Optional[QColor] = None):
        """Add a data series"""
        if color is None:
            colors = [QColor("#0078d4"), QColor("#00bcf2"), QColor("#40e0d0"),
                      QColor("#8764b8"), QColor("#ca5010"), QColor("#10893e")]
            color = colors[len(self.series_data) % len(colors)]

        if fill_color is None:
            fill_color = QColor(color)
            fill_color.setAlphaF(self.fill_opacity)

        series = {
            'name': name,
            'data': data,
            'color': color,
            'fill_color': fill_color,
            'visible': True
        }

        self.series_data.append(series)
        self.update()

    def clear_series(self):
        """Clear all series data"""
        self.series_data.clear()
        self.update()

    def set_y_range(self, min_val: float, max_val: float):
        """Set Y-axis range"""
        self.y_range = (min_val, max_val)
        self.update()

    def paintEvent(self, _event: QPaintEvent):
        """Paint the area chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate chart area
        margin = 60
        chart_rect = QRectF(margin, margin, self.width() -
                            2 * margin, self.height() - 2 * margin)

        if not self.series_data:
            painter.drawText(
                chart_rect, Qt.AlignmentFlag.AlignCenter, "No data to display")
            return

        # Draw grid
        if self.show_grid:
            self.draw_grid(painter, chart_rect)

        # Draw axes
        self.draw_axes(painter, chart_rect)

        # Draw series
        for series in self.series_data:
            if series['visible']:
                self.draw_series(painter, chart_rect, series)

        # Draw legend
        if self.show_legend:
            self.draw_legend(painter)

        # Draw hover tooltip
        if self.hover_point:
            self.draw_hover_tooltip(painter)

    def draw_grid(self, painter: QPainter, chart_rect: QRectF):
        """Draw chart grid"""
        theme = theme_manager
        pen = QPen(theme.get_color('border'))
        pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)

        # Vertical grid lines
        for i in range(6):
            x = chart_rect.left() + (chart_rect.width() / 5) * i
            painter.drawLine(QPointF(x, chart_rect.top()),
                             QPointF(x, chart_rect.bottom()))

        # Horizontal grid lines
        for i in range(6):
            y = chart_rect.top() + (chart_rect.height() / 5) * i
            painter.drawLine(QPointF(chart_rect.left(), y),
                             QPointF(chart_rect.right(), y))

    def draw_axes(self, painter: QPainter, chart_rect: QRectF):
        """Draw chart axes"""
        theme = theme_manager
        pen = QPen(theme.get_color('text_primary'), 2)
        painter.setPen(pen)

        # X-axis
        painter.drawLine(chart_rect.bottomLeft(), chart_rect.bottomRight())

        # Y-axis
        painter.drawLine(chart_rect.bottomLeft(), chart_rect.topLeft())

        # Y-axis labels
        font = QFont("Segoe UI", 9)
        painter.setFont(font)
        painter.setPen(QPen(theme.get_color('text_secondary')))

        for i in range(6):
            y = chart_rect.bottom() - (chart_rect.height() / 5) * i
            value = self.y_range[0] + \
                (self.y_range[1] - self.y_range[0]) * (i / 5)
            painter.drawText(QRectF(0, y - 10, chart_rect.left() - 10, 20),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             f"{value:.1f}")

    def draw_series(self, painter: QPainter, chart_rect: QRectF, series: Dict[str, Any]):
        """Draw a data series"""
        if not series['data']:
            return

        # Create path for area
        path = QPainterPath()
        points = []

        # Calculate points
        data_count = len(series['data'])
        for i, (_x_val, y_val) in enumerate(series['data']):
            x = chart_rect.left() + (chart_rect.width() / (data_count - 1)) * i
            y_ratio = (y_val - self.y_range[0]) / \
                (self.y_range[1] - self.y_range[0])
            y = chart_rect.bottom() - chart_rect.height() * y_ratio
            points.append(QPointF(x, y))

        # Create area path
        if points:
            path.moveTo(chart_rect.left(), chart_rect.bottom())
            for point in points:
                path.lineTo(point)
            path.lineTo(chart_rect.left() + chart_rect.width(),
                        chart_rect.bottom())
            path.closeSubpath()

            # Fill area
            painter.fillPath(path, QBrush(series['fill_color']))

            # Draw line
            pen = QPen(series['color'], 3)
            painter.setPen(pen)

            line_path = QPainterPath()
            line_path.moveTo(points[0])
            for point in points[1:]:
                line_path.lineTo(point)
            painter.drawPath(line_path)

            # Draw points
            if self.show_points:
                painter.setBrush(QBrush(series['color']))
                for point in points:
                    painter.drawEllipse(point, 4, 4)

    def draw_legend(self, painter: QPainter):
        """Draw chart legend"""
        if not self.series_data:
            return

        theme = theme_manager
        legend_rect = QRectF(self.width() - 150, 20, 130,
                             len(self.series_data) * 25 + 10)

        # Legend background
        painter.fillRect(legend_rect, QBrush(theme.get_color('surface')))
        painter.setPen(QPen(theme.get_color('border')))
        painter.drawRect(legend_rect)

        # Legend items
        font = QFont("Segoe UI", 9)
        painter.setFont(font)

        for i, series in enumerate(self.series_data):
            y = legend_rect.top() + 15 + i * 25

            # Color indicator
            color_rect = QRectF(legend_rect.left() + 10, y - 6, 12, 12)
            painter.fillRect(color_rect, QBrush(series['color']))

            # Series name
            painter.setPen(QPen(theme.get_color('text_primary')))
            text_rect = QRectF(legend_rect.left() + 30, y - 8, 90, 16)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             series['name'])

    def draw_hover_tooltip(self, painter: QPainter):
        """Draw hover tooltip"""
        if not self.hover_point:
            return

        theme = theme_manager
        series_idx, _point_idx, data_point = self.hover_point

        # Tooltip text
        text = f"{self.series_data[series_idx]['name']}: {data_point[1]:.2f}"

        # Calculate tooltip position
        font = QFont("Segoe UI", 9)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        text_rect = metrics.boundingRect(text)

        tooltip_rect = QRectF(text_rect)
        tooltip_rect.adjust(-8, -4, 8, 4)

        # Position near mouse
        mouse_pos = self.mapFromGlobal(self.cursor().pos())
        tooltip_rect.moveTopLeft(
            QPointF(mouse_pos.x() + 10, mouse_pos.y() - 30))

        # Draw tooltip
        painter.fillRect(tooltip_rect, QBrush(theme.get_color('surface')))
        painter.setPen(QPen(theme.get_color('border')))
        painter.drawRect(tooltip_rect)

        painter.setPen(QPen(theme.get_color('text_primary')))
        painter.drawText(tooltip_rect, Qt.AlignmentFlag.AlignCenter, text)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for hover effects"""
        margin = 60
        chart_rect = QRectF(margin, margin, self.width() -
                            2 * margin, self.height() - 2 * margin)

        if chart_rect.contains(event.position()):
            # Find closest point
            closest_point = None
            min_distance = float('inf')

            for series_idx, series in enumerate(self.series_data):
                if not series['visible'] or not series['data']:
                    continue

                data_count = len(series['data'])
                for point_idx, (x_val, y_val) in enumerate(series['data']):
                    x = chart_rect.left() + (chart_rect.width() / (data_count - 1)) * point_idx
                    y_ratio = (
                        y_val - self.y_range[0]) / (self.y_range[1] - self.y_range[0])
                    y = chart_rect.bottom() - chart_rect.height() * y_ratio

                    distance = math.sqrt(
                        (event.position().x() - x) ** 2 + (event.position().y() - y) ** 2)
                    if distance < min_distance and distance < 20:
                        min_distance = distance
                        closest_point = (series_idx, point_idx, (x_val, y_val))

            if closest_point != self.hover_point:
                self.hover_point = closest_point
                if closest_point:
                    self.pointHovered.emit(closest_point[0], closest_point[2])
                self.update()
        else:
            if self.hover_point:
                self.hover_point = None
                self.update()

    def mousePressEvent(self, _event: QMouseEvent):
        """Handle mouse click"""
        if self.hover_point:
            self.pointClicked.emit(self.hover_point[0], self.hover_point[2])

    def setup_style(self):
        """Setup styling"""
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme"""
        theme = theme_manager
        self.setStyleSheet(f"""
            FluentAreaChart {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
        """)


class FluentScatterChart(QWidget):
    """Fluent Design scatter plot with clustering and trend lines"""

    # Signals
    pointClicked = Signal(object)  # data_point
    selectionChanged = Signal(list)  # selected_points

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.data_points = []  # List of (x, y, size, color, label, data)
        self.x_range = (0, 100)
        self.y_range = (0, 100)
        self.show_trend_line = False
        self.show_grid = True
        self.point_size_range = (5, 20)
        self.selected_points = set()
        self.hover_point = None

        self.setMinimumSize(300, 200)
        self.setup_style()
        theme_manager.theme_changed.connect(self.apply_theme)

    def add_point(self, x: float, y: float, size: float = 10, color: Optional[QColor] = None,
                  label: str = "", data: Any = None):
        """Add a data point"""
        if color is None:
            color = theme_manager.get_color('primary')

        point = {
            'x': x, 'y': y, 'size': size, 'color': color,
            'label': label, 'data': data
        }
        self.data_points.append(point)
        self.update()

    def set_data(self, points: List[Dict[str, Any]]):
        """Set all data points at once"""
        self.data_points = points

        # Auto-calculate ranges
        if points:
            x_values = [p['x'] for p in points]
            y_values = [p['y'] for p in points]
            self.x_range = (min(x_values), max(x_values))
            self.y_range = (min(y_values), max(y_values))

        self.update()

    def clear_data(self):
        """Clear all data points"""
        self.data_points.clear()
        self.selected_points.clear()
        self.update()

    def paintEvent(self, _event: QPaintEvent):
        """Paint the scatter chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate chart area
        margin = 60
        chart_rect = QRectF(margin, margin, self.width() -
                            2 * margin, self.height() - 2 * margin)

        if not self.data_points:
            painter.drawText(
                chart_rect, Qt.AlignmentFlag.AlignCenter, "No data to display")
            return

        # Draw grid
        if self.show_grid:
            self.draw_grid(painter, chart_rect)

        # Draw axes
        self.draw_axes(painter, chart_rect)

        # Draw trend line
        if self.show_trend_line:
            self.draw_trend_line(painter, chart_rect)

        # Draw points
        self.draw_points(painter, chart_rect)

        # Draw hover tooltip
        if self.hover_point:
            self.draw_hover_tooltip(painter)

    def draw_grid(self, painter: QPainter, chart_rect: QRectF):
        """Draw chart grid"""
        theme = theme_manager
        pen = QPen(theme.get_color('border'))
        pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)

        # Vertical grid lines
        for i in range(6):
            x = chart_rect.left() + (chart_rect.width() / 5) * i
            painter.drawLine(QPointF(x, chart_rect.top()),
                             QPointF(x, chart_rect.bottom()))

        # Horizontal grid lines
        for i in range(6):
            y = chart_rect.top() + (chart_rect.height() / 5) * i
            painter.drawLine(QPointF(chart_rect.left(), y),
                             QPointF(chart_rect.right(), y))

    def draw_axes(self, painter: QPainter, chart_rect: QRectF):
        """Draw chart axes with labels"""
        theme = theme_manager
        pen = QPen(theme.get_color('text_primary'), 2)
        painter.setPen(pen)

        # X-axis
        painter.drawLine(chart_rect.bottomLeft(), chart_rect.bottomRight())

        # Y-axis
        painter.drawLine(chart_rect.bottomLeft(), chart_rect.topLeft())

        # Axis labels
        font = QFont("Segoe UI", 9)
        painter.setFont(font)
        painter.setPen(QPen(theme.get_color('text_secondary')))

        # X-axis labels
        for i in range(6):
            x = chart_rect.left() + (chart_rect.width() / 5) * i
            value = self.x_range[0] + \
                (self.x_range[1] - self.x_range[0]) * (i / 5)
            painter.drawText(QRectF(x - 20, chart_rect.bottom() + 5, 40, 20),
                             Qt.AlignmentFlag.AlignCenter, f"{value:.1f}")

        # Y-axis labels
        for i in range(6):
            y = chart_rect.bottom() - (chart_rect.height() / 5) * i
            value = self.y_range[0] + \
                (self.y_range[1] - self.y_range[0]) * (i / 5)
            painter.drawText(QRectF(0, y - 10, chart_rect.left() - 10, 20),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             f"{value:.1f}")

    def draw_trend_line(self, painter: QPainter, chart_rect: QRectF):
        """Draw trend line using linear regression"""
        if len(self.data_points) < 2:
            return

        # Calculate linear regression
        x_values = [p['x'] for p in self.data_points]
        y_values = [p['y'] for p in self.data_points]

        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)

        # Calculate slope and intercept
        # Avoid division by zero if all x_values are the same
        denominator = (n * sum_x2 - sum_x * sum_x)
        if denominator == 0:
            return  # Cannot draw a trend line

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

        # Draw trend line
        theme = theme_manager
        pen = QPen(theme.get_color('accent_medium'), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)

        # Calculate line points
        x1_val = self.x_range[0]
        y1_val = slope * x1_val + intercept
        x2_val = self.x_range[1]
        y2_val = slope * x2_val + intercept

        # Convert to screen coordinates
        screen_x1 = chart_rect.left()
        screen_y1 = chart_rect.bottom() - ((y1_val -
                                            self.y_range[0]) / (self.y_range[1] - self.y_range[0])) * chart_rect.height()
        screen_x2 = chart_rect.right()
        screen_y2 = chart_rect.bottom() - ((y2_val -
                                            self.y_range[0]) / (self.y_range[1] - self.y_range[0])) * chart_rect.height()

        painter.drawLine(QPointF(screen_x1, screen_y1),
                         QPointF(screen_x2, screen_y2))

    def draw_points(self, painter: QPainter, chart_rect: QRectF):
        """Draw all data points"""
        if not self.data_points:  # Ensure there are points to draw
            return

        # Ensure x_range and y_range are valid to prevent division by zero
        if self.x_range[1] == self.x_range[0] or self.y_range[1] == self.y_range[0]:
            return  # Cannot map points if range is zero

        for i, point in enumerate(self.data_points):
            # Calculate screen position
            x_ratio = (point['x'] - self.x_range[0]) / \
                (self.x_range[1] - self.x_range[0])
            y_ratio = (point['y'] - self.y_range[0]) / \
                (self.y_range[1] - self.y_range[0])

            screen_x = chart_rect.left() + x_ratio * chart_rect.width()
            screen_y = chart_rect.bottom() - y_ratio * chart_rect.height()

            # Point size
            size = point.get('size', 10)

            # Point color
            color = point.get('color', theme_manager.get_color('primary'))

            # Highlight selected points
            if i in self.selected_points:
                painter.setPen(
                    QPen(theme_manager.get_color('accent_medium'), 3))
            else:
                painter.setPen(QPen(color.darker(120), 1))

            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(screen_x, screen_y), size/2, size/2)

    def draw_hover_tooltip(self, painter: QPainter):
        """Draw hover tooltip"""
        if self.hover_point is None:
            return

        point = self.data_points[self.hover_point]
        theme = theme_manager

        # Tooltip text
        text = f"({point['x']:.2f}, {point['y']:.2f})"
        if point.get('label'):
            text = f"{point['label']}: {text}"

        # Calculate tooltip position
        font = QFont("Segoe UI", 9)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        text_rect = metrics.boundingRect(text)

        tooltip_rect = QRectF(text_rect)
        tooltip_rect.adjust(-8, -4, 8, 4)

        # Position near mouse
        mouse_pos = self.mapFromGlobal(self.cursor().pos())
        tooltip_rect.moveTopLeft(
            QPointF(mouse_pos.x() + 10, mouse_pos.y() - 30))

        # Draw tooltip
        painter.fillRect(tooltip_rect, QBrush(theme.get_color('surface')))
        painter.setPen(QPen(theme.get_color('border')))
        painter.drawRect(tooltip_rect)

        painter.setPen(QPen(theme.get_color('text_primary')))
        painter.drawText(tooltip_rect, Qt.AlignmentFlag.AlignCenter, text)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for hover effects"""
        margin = 60
        chart_rect = QRectF(margin, margin, self.width() -
                            2 * margin, self.height() - 2 * margin)

        if chart_rect.contains(event.position()):
            # Find closest point
            closest_point_idx = None
            min_distance = float('inf')

            # Ensure x_range and y_range are valid to prevent division by zero
            if not self.data_points or self.x_range[1] == self.x_range[0] or self.y_range[1] == self.y_range[0]:
                if self.hover_point is not None:
                    self.hover_point = None
                    self.update()
                return

            for i, point in enumerate(self.data_points):
                x_ratio = (point['x'] - self.x_range[0]) / \
                    (self.x_range[1] - self.x_range[0])
                y_ratio = (point['y'] - self.y_range[0]) / \
                    (self.y_range[1] - self.y_range[0])

                screen_x = chart_rect.left() + x_ratio * chart_rect.width()
                screen_y = chart_rect.bottom() - y_ratio * chart_rect.height()

                distance = math.sqrt(
                    (event.position().x() - screen_x) ** 2 + (event.position().y() - screen_y) ** 2)
                # Check against point size for hover activation
                if distance < min_distance and distance < point.get('size', 10):
                    min_distance = distance
                    closest_point_idx = i

            if closest_point_idx != self.hover_point:
                self.hover_point = closest_point_idx
                self.update()
        else:
            if self.hover_point is not None:
                self.hover_point = None
                self.update()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse click for point selection"""
        if self.hover_point is not None:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                # Multi-select with Ctrl
                if self.hover_point in self.selected_points:
                    self.selected_points.remove(self.hover_point)
                else:
                    self.selected_points.add(self.hover_point)
            else:
                # Single select
                self.selected_points = {self.hover_point}

            self.pointClicked.emit(self.data_points[self.hover_point])
            self.selectionChanged.emit(
                [self.data_points[i] for i in self.selected_points])
            self.update()

    def setup_style(self):
        """Setup styling"""
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme"""
        theme = theme_manager
        self.setStyleSheet(f"""
            FluentScatterChart {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
        """)


class FluentHeatMap(QWidget):
    """Fluent Design heat map visualization"""

    # Signals
    cellClicked = Signal(int, int, object)  # row, col, value
    cellHovered = Signal(int, int, object)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.data_matrix = []  # 2D array of values
        self.row_labels = []
        self.col_labels = []
        self.value_range = (0, 100)
        self.color_scheme = "blue_red"  # "blue_red", "green_red", "grayscale"
        self.show_values = True
        self.cell_size = 40
        self.hover_cell = None

        self.setMinimumSize(200, 200)
        self.setup_style()
        theme_manager.theme_changed.connect(self.apply_theme)

    def set_data(self, data: List[List[float]], row_labels: Optional[List[str]] = None,
                 col_labels: Optional[List[str]] = None):
        """Set heat map data"""
        self.data_matrix = data
        self.row_labels = row_labels if row_labels is not None else [
            f"Row {i+1}" for i in range(len(data))]
        self.col_labels = col_labels if col_labels is not None else (
            [f"Col {i+1}" for i in range(len(data[0]))] if data and data[0] else [])

        # Calculate value range
        if data and any(data):  # 确保数据非空且行非空
            all_values = [val for row in data for val in row if row]  # 确保行非空
            if all_values:  # 确保有值可处理
                self.value_range = (min(all_values), max(all_values))
            else:
                self.value_range = (0, 0)  # 默认值
        else:
            self.value_range = (0, 0)  # 默认值

        self.update()

    def get_color_for_value(self, value: float) -> QColor:
        """Get color for a value based on the color scheme"""
        if self.value_range[1] == self.value_range[0]:
            ratio = 0.5  # Avoid division by zero, default to mid-color
        else:
            ratio = (value - self.value_range[0]) / \
                (self.value_range[1] - self.value_range[0])

        ratio = max(0.0, min(1.0, ratio))  # Clamp ratio to [0, 1]

        if self.color_scheme == "blue_red":
            if ratio < 0.5:
                # Blue to white
                intensity = int(255 * (1 - ratio * 2))
                return QColor(intensity, intensity, 255)
            else:
                # White to red
                intensity = int(255 * (1 - (ratio - 0.5) * 2))
                return QColor(255, intensity, intensity)
        elif self.color_scheme == "green_red":
            if ratio < 0.5:
                # Green to yellow
                red = int(255 * ratio * 2)
                return QColor(red, 255, 0)
            else:
                # Yellow to red
                green = int(255 * (1 - (ratio - 0.5) * 2))
                return QColor(255, green, 0)
        else:  # grayscale
            intensity = int(255 * ratio)
            return QColor(intensity, intensity, intensity)

    def paintEvent(self, _event: QPaintEvent):
        """Paint the heat map"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.data_matrix or not self.data_matrix[0]:
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter, "No data to display")
            return

        rows = len(self.data_matrix)
        cols = len(self.data_matrix[0])

        # Calculate dimensions
        label_width = 80
        label_height = 30

        # Draw column labels
        font = QFont("Segoe UI", 9)
        painter.setFont(font)
        painter.setPen(QPen(theme_manager.get_color('text_primary')))

        for col in range(cols):
            if col < len(self.col_labels):  # Check if label exists
                x = label_width + col * self.cell_size
                rect = QRectF(x, 0, self.cell_size, label_height)
                painter.drawText(
                    rect, Qt.AlignmentFlag.AlignCenter, self.col_labels[col])

        # Draw row labels and cells
        for row in range(rows):
            if row < len(self.row_labels):  # Check if label exists
                y = label_height + row * self.cell_size

                # Row label
                rect = QRectF(0, y, label_width, self.cell_size)
                painter.drawText(
                    rect, Qt.AlignmentFlag.AlignCenter, self.row_labels[row])

                # Data cells
                for col in range(cols):
                    x = label_width + col * self.cell_size
                    cell_rect = QRectF(x, y, self.cell_size, self.cell_size)

                    value = self.data_matrix[row][col]
                    color = self.get_color_for_value(value)

                    # Highlight hovered cell
                    if self.hover_cell and self.hover_cell == (row, col):
                        color = color.lighter(120)

                    # Draw cell
                    painter.fillRect(cell_rect, QBrush(color))
                    painter.setPen(QPen(theme_manager.get_color('border')))
                    painter.drawRect(cell_rect)

                    # Draw value text
                    if self.show_values:
                        text_color = QColor(
                            "white") if color.lightness() < 128 else QColor("black")
                        painter.setPen(QPen(text_color))
                        painter.drawText(
                            cell_rect, Qt.AlignmentFlag.AlignCenter, f"{value:.1f}")

        # Draw color scale legend
        self.draw_color_legend(painter)

    def draw_color_legend(self, painter: QPainter):
        """Draw color scale legend"""
        legend_width = 20
        legend_height = 150
        legend_x = self.width() - legend_width - 20
        legend_y = 50

        # Draw gradient
        # Corrected gradient points
        gradient = QLinearGradient(
            legend_x, legend_y + legend_height, legend_x, legend_y)

        if self.color_scheme == "blue_red":
            gradient.setColorAt(0, QColor(0, 0, 255))  # Min value color
            gradient.setColorAt(0.5, QColor(255, 255, 255))
            gradient.setColorAt(1, QColor(255, 0, 0))  # Max value color
        elif self.color_scheme == "green_red":
            gradient.setColorAt(0, QColor(0, 255, 0))  # Min value color
            gradient.setColorAt(0.5, QColor(255, 255, 0))
            gradient.setColorAt(1, QColor(255, 0, 0))  # Max value color
        else:  # grayscale
            gradient.setColorAt(0, QColor(0, 0, 0))  # Min value color
            gradient.setColorAt(1, QColor(255, 255, 255))  # Max value color

        painter.fillRect(QRectF(legend_x, legend_y, legend_width,
                         legend_height), QBrush(gradient))
        painter.setPen(QPen(theme_manager.get_color('border')))
        painter.drawRect(
            QRectF(legend_x, legend_y, legend_width, legend_height))

        # Draw value labels
        font = QFont("Segoe UI", 8)
        painter.setFont(font)
        painter.setPen(QPen(theme_manager.get_color('text_secondary')))

        # Max value (top of legend)
        painter.drawText(QRectF(legend_x + legend_width + 5, legend_y - 10, 45, 20),
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         f"{self.value_range[1]:.1f}")

        # Min value (bottom of legend)
        painter.drawText(QRectF(legend_x + legend_width + 5, legend_y + legend_height - 10, 45, 20),
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         f"{self.value_range[0]:.1f}")

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for hover effects"""
        if not self.data_matrix or not self.data_matrix[0]:
            if self.hover_cell:
                self.hover_cell = None
                self.update()
            return

        label_width = 80
        label_height = 30

        # Calculate cell position
        x_pos = event.position().x() - label_width
        y_pos = event.position().y() - label_height

        if x_pos >= 0 and y_pos >= 0:
            col = int(x_pos // self.cell_size)
            row = int(y_pos // self.cell_size)

            if (0 <= row < len(self.data_matrix) and
                    0 <= col < len(self.data_matrix[0])):

                if self.hover_cell != (row, col):
                    self.hover_cell = (row, col)
                    value = self.data_matrix[row][col]
                    self.cellHovered.emit(row, col, value)
                    self.update()
            else:  # Mouse is outside the cell grid but within the labeled area
                if self.hover_cell:
                    self.hover_cell = None
                    self.update()
        else:  # Mouse is outside the labeled area
            if self.hover_cell:
                self.hover_cell = None
                self.update()

    def mousePressEvent(self, _event: QMouseEvent):
        """Handle mouse click"""
        if self.hover_cell:
            row, col = self.hover_cell
            if 0 <= row < len(self.data_matrix) and 0 <= col < len(self.data_matrix[0]):
                value = self.data_matrix[row][col]
                self.cellClicked.emit(row, col, value)

    def setup_style(self):
        """Setup styling"""
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme"""
        theme = theme_manager
        self.setStyleSheet(f"""
            FluentHeatMap {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
        """)


# Export all advanced chart components
__all__ = [
    'ChartType',
    'FluentAreaChart',
    'FluentScatterChart',
    'FluentHeatMap'
]
