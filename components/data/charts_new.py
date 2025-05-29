"""
Fluent Design Data Visualization Components
Enhanced with improved animations and consistent styling patterns
Charts, graphs, and data visualization widgets
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QScrollArea, QSizePolicy, QGridLayout)
from PySide6.QtCore import Qt, Signal, QTimer, QRect, QPointF, QPropertyAnimation
from PySide6.QtGui import (QPainter, QColor, QBrush, QPen, QFont, QLinearGradient, 
                          QRadialGradient, QPainterPath, QPolygonF)
from core.theme import theme_manager
from core.enhanced_animations import (FluentMicroInteraction, FluentTransition, 
                                     FluentStateTransition, FluentRevealEffect)
from typing import Optional, List, Dict, Any, Tuple
import math


class FluentProgressRing(QWidget):
    """Fluent Design style progress ring with enhanced animations"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._value = 0
        self._animated_value = 0  # For smooth animation
        self._minimum = 0
        self._maximum = 100
        self._text_visible = True
        self._thickness = 8
        
        self._state_transition = FluentStateTransition(self)
        self._value_animation = None
        
        self.setFixedSize(80, 80)
        self._setup_enhanced_animations()
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Add reveal animation when created
        FluentRevealEffect.reveal_scale(self, 300)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation effects"""
        # Setup state transitions for progress ring
        self._state_transition.addState("normal", {
            "minimumWidth": 80,
            "minimumHeight": 80,
        })
        
        self._state_transition.addState("hovered", {
            "minimumWidth": 84,
            "minimumHeight": 84,
        }, duration=200, easing=FluentTransition.EASE_SMOOTH)

    def setValue(self, value: int):
        """Set progress value with smooth animation"""
        new_value = max(self._minimum, min(self._maximum, value))
        if new_value != self._value:
            old_value = self._animated_value
            self._value = new_value
            
            # Create smooth value transition
            if self._value_animation:
                self._value_animation.stop()
            
            self._value_animation = QPropertyAnimation(self, b"_animated_value")
            self._value_animation.setDuration(400)
            self._value_animation.setStartValue(old_value)
            self._value_animation.setEndValue(new_value)
            self._value_animation.valueChanged.connect(self.update)
            self._value_animation.start()

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
        """Paint progress ring with enhanced animations"""
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
        
        # Draw progress arc using animated value
        if self._maximum > self._minimum:
            progress = (self._animated_value - self._minimum) / (self._maximum - self._minimum)
            span_angle = int(progress * 360 * 16)  # Qt uses 1/16th degree units
            
            # Create gradient for progress arc
            gradient = QLinearGradient(0, 0, rect.width(), 0)
            gradient.setColorAt(0, theme.get_color('primary'))
            gradient.setColorAt(1, theme.get_color('primary').lighter(120))
            
            pen = QPen(QBrush(gradient), self._thickness)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            
            painter.drawArc(center.x() - radius, center.y() - radius,
                          radius * 2, radius * 2, 90 * 16, -span_angle)
        
        # Draw text
        if self._text_visible:
            painter.setPen(QPen(theme.get_color('text_primary')))
            painter.setFont(QFont("", 12, QFont.Weight.Bold))
            
            if self._maximum > self._minimum:
                percentage = int((self._animated_value - self._minimum) / (self._maximum - self._minimum) * 100)
                text = f"{percentage}%"
            else:
                text = "0%"
            
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    def enterEvent(self, event):
        """Hover enter event with enhanced animations"""
        FluentMicroInteraction.hover_glow(self, 0.1)
        self._state_transition.transitionTo("hovered")
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave event"""
        self._state_transition.transitionTo("normal")
        super().leaveEvent(event)

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
    """Fluent Design style bar chart with enhanced animations"""
    
    bar_clicked = Signal(int, str, float)  # index, label, value
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._data = []  # List of (label, value, color) tuples
        self._show_values = True
        self._show_grid = True
        self._animated_values = []
        self._bar_animations = []
        
        self.setMinimumSize(300, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Add reveal animation when created
        FluentRevealEffect.reveal_fade(self, 400)

    def setData(self, data: List[Tuple[str, float, Optional[QColor]]]):
        """Set chart data with enhanced animations"""
        self._data = data
        old_values = self._animated_values if self._animated_values else [0.0] * len(data)
        self._animated_values = [0.0] * len(data)
        
        # Stop existing animations
        for animation in self._bar_animations:
            animation.stop()
        self._bar_animations.clear()
        
        # Create staggered animations for each bar
        for i, (label, value, color) in enumerate(data):
            animation = QPropertyAnimation()
            animation.setTargetObject(self)
            animation.setPropertyName(b"dummy")  # We'll manually handle the animation
            animation.setDuration(600 + i * 100)  # Staggered timing
            animation.setStartValue(old_values[i] if i < len(old_values) else 0.0)
            animation.setEndValue(value)
            
            # Create a custom update function for this bar
            def create_updater(index):
                def update_bar(val):
                    if index < len(self._animated_values):
                        self._animated_values[index] = val
                        self.update()
                return update_bar
            
            animation.valueChanged.connect(create_updater(i))
            animation.start()
            self._bar_animations.append(animation)

    def setShowValues(self, show: bool):
        """Set value display visibility"""
        self._show_values = show
        self.update()

    def setShowGrid(self, show: bool):
        """Set grid visibility"""
        self._show_grid = show
        self.update()

    def paintEvent(self, event):
        """Paint bar chart with enhanced visuals"""
        if not self._data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = theme_manager
        rect = self.rect()
        
        # Calculate chart area (leave margins for labels and values)
        margin = 40
        chart_rect = QRect(margin, margin, 
                          rect.width() - 2 * margin, 
                          rect.height() - 2 * margin)
        
        # Find max value for scaling
        max_value = max(item[1] for item in self._data) if self._data else 1
        if max_value == 0:
            max_value = 1
            
        # Draw grid if enabled
        if self._show_grid:
            self._draw_grid(painter, chart_rect, max_value)
        
        # Draw bars
        bar_width = chart_rect.width() / len(self._data) * 0.8
        bar_spacing = chart_rect.width() / len(self._data) * 0.2
        
        for i, (label, value, color) in enumerate(self._data):
            animated_value = self._animated_values[i] if i < len(self._animated_values) else 0
            
            # Calculate bar dimensions
            bar_height = (animated_value / max_value) * chart_rect.height()
            bar_x = chart_rect.x() + i * (bar_width + bar_spacing) + bar_spacing / 2
            bar_y = chart_rect.bottom() - bar_height
            
            # Use provided color or default theme color
            if color:
                bar_color = color
            else:
                colors = [theme.get_color('primary'), theme.get_color('accent'), 
                         theme.get_color('secondary')]
                bar_color = colors[i % len(colors)]
            
            # Create gradient for bar
            gradient = QLinearGradient(0, bar_y, 0, bar_y + bar_height)
            gradient.setColorAt(0, bar_color.lighter(120))
            gradient.setColorAt(1, bar_color)
            
            # Draw bar
            painter.fillRect(int(bar_x), int(bar_y), int(bar_width), int(bar_height), 
                           QBrush(gradient))
            
            # Draw value text if enabled
            if self._show_values and animated_value > 0:
                painter.setPen(QPen(theme.get_color('text_primary')))
                painter.setFont(QFont("", 10))
                value_text = f"{animated_value:.1f}"
                painter.drawText(int(bar_x), int(bar_y - 5), int(bar_width), 20,
                               Qt.AlignmentFlag.AlignCenter, value_text)
            
            # Draw label
            painter.setPen(QPen(theme.get_color('text_secondary')))
            painter.setFont(QFont("", 9))
            painter.drawText(int(bar_x), chart_rect.bottom() + 5, int(bar_width), 20,
                           Qt.AlignmentFlag.AlignCenter, label)

    def _draw_grid(self, painter: QPainter, chart_rect: QRect, max_value: float):
        """Draw grid lines"""
        theme = theme_manager
        painter.setPen(QPen(theme.get_color('border'), 1, Qt.PenStyle.DashLine))
        
        # Draw horizontal grid lines
        grid_lines = 5
        for i in range(grid_lines + 1):
            y = chart_rect.bottom() - (i / grid_lines) * chart_rect.height()
            painter.drawLine(chart_rect.left(), int(y), chart_rect.right(), int(y))
            
            # Draw grid value labels
            value = (i / grid_lines) * max_value
            painter.setPen(QPen(theme.get_color('text_secondary')))
            painter.setFont(QFont("", 8))
            painter.drawText(5, int(y - 5), 30, 10, Qt.AlignmentFlag.AlignRight, f"{value:.0f}")
            painter.setPen(QPen(theme.get_color('border'), 1, Qt.PenStyle.DashLine))

    def mousePressEvent(self, event):
        """Handle bar click with micro-interaction"""
        if not self._data:
            return
            
        # Calculate which bar was clicked
        margin = 40
        chart_rect = QRect(margin, margin, 
                          self.rect().width() - 2 * margin, 
                          self.rect().height() - 2 * margin)
        
        bar_width = chart_rect.width() / len(self._data) * 0.8
        bar_spacing = chart_rect.width() / len(self._data) * 0.2
        
        for i, (label, value, color) in enumerate(self._data):
            bar_x = chart_rect.x() + i * (bar_width + bar_spacing) + bar_spacing / 2
            
            if bar_x <= event.x() <= bar_x + bar_width:
                # Apply click micro-interaction
                FluentMicroInteraction.button_press(self, 0.98, 100)
                FluentMicroInteraction.ripple_effect(self)
                
                self.bar_clicked.emit(i, label, value)
                break
        
        super().mousePressEvent(event)

    def _setup_style(self):
        """Setup style"""
        self.setStyleSheet(f"""
            FluentBarChart {{
                background-color: transparent;
                border: none;
            }}
        """)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self.update()


class FluentLineChart(QWidget):
    """Fluent Design style line chart with enhanced animations"""
    
    point_clicked = Signal(int, float, float)  # index, x_value, y_value
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._data_series = []  # List of data series
        self._show_points = True
        self._show_grid = True
        self._smooth_curves = True
        self._animated_progress = 0.0
        
        self.setMinimumSize(400, 250)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self._animation = None
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Add reveal animation when created
        FluentRevealEffect.reveal_slide(self, 500, "up")

    def addDataSeries(self, name: str, data: List[Tuple[float, float]], 
                     color: Optional[QColor] = None):
        """Add a data series with animation"""
        if color is None:
            colors = [theme_manager.get_color('primary'), 
                     theme_manager.get_color('accent'),
                     theme_manager.get_color('secondary')]
            color = colors[len(self._data_series) % len(colors)]
        
        self._data_series.append({
            'name': name,
            'data': data,
            'color': color
        })
        
        # Animate the new series appearance
        self._start_draw_animation()

    def _start_draw_animation(self):
        """Start line drawing animation"""
        if self._animation:
            self._animation.stop()
        
        self._animation = QPropertyAnimation(self, b"_animated_progress")
        self._animation.setDuration(1000)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.valueChanged.connect(self.update)
        self._animation.start()

    def paintEvent(self, event):
        """Paint line chart with enhanced visuals"""
        if not self._data_series:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = theme_manager
        rect = self.rect()
        
        # Calculate chart area
        margin = 50
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
        grid_lines = 6
        for i in range(grid_lines + 1):
            x = chart_rect.left() + (i / grid_lines) * chart_rect.width()
            painter.drawLine(int(x), chart_rect.top(), int(x), chart_rect.bottom())
        
        # Draw horizontal grid lines
        for i in range(grid_lines + 1):
            y = chart_rect.bottom() - (i / grid_lines) * chart_rect.height()
            painter.drawLine(chart_rect.left(), int(y), chart_rect.right(), int(y))

    def _draw_series(self, painter: QPainter, chart_rect: QRect, series: Dict,
                    min_x: float, max_x: float, min_y: float, max_y: float):
        """Draw a data series with animation"""
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
        
        # Animate line drawing
        visible_points = int(len(points) * self._animated_progress)
        if visible_points < 2:
            return
        
        # Draw line
        painter.setPen(QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        
        if self._smooth_curves and visible_points > 2:
            # Draw smooth curve
            path = QPainterPath()
            path.moveTo(points[0])
            
            for i in range(1, visible_points):
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
            for i in range(visible_points - 1):
                painter.drawLine(points[i], points[i + 1])
        
        # Draw points if enabled
        if self._show_points:
            painter.setPen(QPen(color.darker(120), 2))
            painter.setBrush(QBrush(color.lighter(120)))
            
            for i in range(visible_points):
                painter.drawEllipse(points[i], 4, 4)

    def clearData(self):
        """Clear all data series"""
        self._data_series.clear()
        self.update()

    def _setup_style(self):
        """Setup style"""
        self.setStyleSheet(f"""
            FluentLineChart {{
                background-color: transparent;
                border: none;
            }}
        """)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self.update()


class FluentPieChart(QWidget):
    """Fluent Design style pie chart with enhanced animations"""
    
    slice_clicked = Signal(int, str, float)  # index, label, value
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._data = []  # List of (label, value, color) tuples
        self._show_labels = True
        self._show_percentages = True
        self._animated_angles = []
        self._slice_animations = []
        
        self.setMinimumSize(250, 250)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Add reveal animation when created
        FluentRevealEffect.reveal_scale(self, 600)

    def setData(self, data: List[Tuple[str, float, Optional[QColor]]]):
        """Set pie chart data with enhanced animations"""
        self._data = data
        total_value = sum(item[1] for item in data) if data else 1
        
        # Calculate angles
        angles = []
        current_angle = 0
        for label, value, color in data:
            angle = (value / total_value) * 360
            angles.append(angle)
        
        # Stop existing animations
        for animation in self._slice_animations:
            animation.stop()
        self._slice_animations.clear()
        
        self._animated_angles = [0.0] * len(data)
        
        # Create staggered animations for each slice
        for i, angle in enumerate(angles):
            animation = QPropertyAnimation()
            animation.setTargetObject(self)
            animation.setPropertyName(b"dummy")
            animation.setDuration(800 + i * 150)
            animation.setStartValue(0.0)
            animation.setEndValue(angle)
            
            def create_updater(index):
                def update_slice(val):
                    if index < len(self._animated_angles):
                        self._animated_angles[index] = val
                        self.update()
                return update_slice
            
            animation.valueChanged.connect(create_updater(i))
            animation.start()
            self._slice_animations.append(animation)

    def paintEvent(self, event):
        """Paint pie chart with enhanced visuals"""
        if not self._data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = theme_manager
        rect = self.rect()
        
        # Calculate chart area
        margin = 20
        chart_size = min(rect.width(), rect.height()) - 2 * margin
        chart_rect = QRect((rect.width() - chart_size) // 2,
                          (rect.height() - chart_size) // 2,
                          chart_size, chart_size)
        
        # Draw slices
        start_angle = 0
        total_value = sum(item[1] for item in self._data) if self._data else 1
        
        for i, (label, value, color) in enumerate(self._data):
            if i >= len(self._animated_angles):
                continue
                
            animated_angle = self._animated_angles[i]
            
            if animated_angle <= 0:
                continue
            
            # Use provided color or default theme color
            if color:
                slice_color = color
            else:
                colors = [theme.get_color('primary'), theme.get_color('accent'), 
                         theme.get_color('secondary'), theme.get_color('success'),
                         theme.get_color('warning'), theme.get_color('error')]
                slice_color = colors[i % len(colors)]
            
            # Create gradient for slice
            gradient = QRadialGradient(chart_rect.center(), chart_size // 2)
            gradient.setColorAt(0, slice_color.lighter(120))
            gradient.setColorAt(1, slice_color)
            
            # Draw slice
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(theme.get_color('surface'), 2))
            painter.drawPie(chart_rect, int(start_angle * 16), int(animated_angle * 16))
            
            # Draw label if enabled
            if self._show_labels and animated_angle > 10:  # Only show label if slice is large enough
                label_angle = start_angle + animated_angle / 2
                label_radius = chart_size // 2 * 0.7
                
                label_x = chart_rect.center().x() + label_radius * math.cos(math.radians(label_angle))
                label_y = chart_rect.center().y() + label_radius * math.sin(math.radians(label_angle))
                
                painter.setPen(QPen(Qt.GlobalColor.white))
                painter.setFont(QFont("", 10, QFont.Weight.Bold))
                
                display_text = label
                if self._show_percentages:
                    percentage = (value / total_value) * 100
                    display_text += f"\n{percentage:.1f}%"
                
                # Draw text with shadow for better visibility
                painter.setPen(QPen(Qt.GlobalColor.black))
                painter.drawText(int(label_x + 1), int(label_y + 1), display_text)
                painter.setPen(QPen(Qt.GlobalColor.white))
                painter.drawText(int(label_x), int(label_y), display_text)
            
            start_angle += animated_angle

    def mousePressEvent(self, event):
        """Handle slice click with micro-interaction"""
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
            if i >= len(self._animated_angles):
                continue
                
            animated_angle = self._animated_angles[i]
            
            if start_angle <= click_angle <= start_angle + animated_angle:
                # Apply click micro-interaction
                FluentMicroInteraction.button_press(self, 0.95, 150)
                FluentMicroInteraction.ripple_effect(self)
                
                self.slice_clicked.emit(i, label, value)
                break
            
            start_angle += animated_angle
        
        super().mousePressEvent(event)

    def _setup_style(self):
        """Setup style"""
        self.setStyleSheet(f"""
            FluentPieChart {{
                background-color: transparent;
                border: none;
            }}
        """)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self.update()
