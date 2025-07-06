"""
Additional Fluent Layout Components
Includes UniformGrid, MasonryLayout, AdaptiveLayout, and Canvas
"""

from typing import Optional, List, Dict, Any, Tuple, Callable
from enum import Enum
import math

from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import QRect, QTimer, QPropertyAnimation, QEasingCurve, QByteArray

from .layout_base import FluentLayoutBase, FluentAdaptiveLayoutBase


class FluentUniformGrid(FluentLayoutBase):
    """
    Uniform grid layout with equal-sized cells
    Similar to WPF UniformGrid
    """
    
    def __init__(self, rows: int = 0, columns: int = 0, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._rows = rows
        self._columns = columns
        self._items: List[QWidget] = []
        self._first_column = 0  # First column index (for spanning scenarios)
        
        self._setup_uniform_grid()
        
    def _setup_uniform_grid(self):
        """Setup uniform grid"""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout_changed.connect(self._perform_layout_update)
        
    def add_widget(self, widget: QWidget):
        """Add widget to the next available cell"""
        widget.setParent(self)
        self._items.append(widget)
        self.request_layout_update()
        
    def insert_widget(self, index: int, widget: QWidget):
        """Insert widget at specific index"""
        widget.setParent(self)
        self._items.insert(max(0, min(index, len(self._items))), widget)
        self.request_layout_update()
        
    def remove_widget(self, widget: QWidget):
        """Remove widget from grid"""
        if widget in self._items:
            self._items.remove(widget)
            widget.setParent(None)
            self.request_layout_update()
            
    def _perform_layout_update(self):
        """Perform uniform grid layout"""
        super()._perform_layout_update()
        
        if not self._items:
            return
            
        container_rect = self.contentsRect()
        container_rect.adjust(
            self._padding.left(), self._padding.top(),
            -self._padding.right(), -self._padding.bottom()
        )
        
        # Calculate grid dimensions
        rows, columns = self._calculate_grid_dimensions()
        
        if rows == 0 or columns == 0:
            return
            
        # Calculate cell size
        available_width = container_rect.width() - (columns - 1) * self._spacing
        available_height = container_rect.height() - (rows - 1) * self._spacing
        
        cell_width = available_width // columns
        cell_height = available_height // rows
        
        # Position widgets
        for i, widget in enumerate(self._items):
            if i >= rows * columns:
                break  # More widgets than cells
                
            row = i // columns
            col = (i + self._first_column) % columns
            
            x = container_rect.x() + col * (cell_width + self._spacing)
            y = container_rect.y() + row * (cell_height + self._spacing)
            
            widget.setGeometry(x, y, cell_width, cell_height)
            
    def _calculate_grid_dimensions(self) -> Tuple[int, int]:
        """Calculate the grid dimensions"""
        item_count = len(self._items)
        
        if item_count == 0:
            return (0, 0)
            
        # If both rows and columns are set, use them
        if self._rows > 0 and self._columns > 0:
            return (self._rows, self._columns)
            
        # If only rows is set, calculate columns
        if self._rows > 0:
            columns = math.ceil(item_count / self._rows)
            return (self._rows, columns)
            
        # If only columns is set, calculate rows
        if self._columns > 0:
            rows = math.ceil(item_count / self._columns)
            return (rows, self._columns)
            
        # Auto-calculate both based on aspect ratio
        sqrt_count = math.sqrt(item_count)
        columns = math.ceil(sqrt_count)
        rows = math.ceil(item_count / columns)
        
        return (rows, columns)
        
    # Public API
    
    def set_rows(self, rows: int):
        """Set number of rows"""
        if self._rows != rows:
            self._rows = max(0, rows)
            self.request_layout_update()
            
    def get_rows(self) -> int:
        """Get number of rows"""
        return self._rows
        
    def set_columns(self, columns: int):
        """Set number of columns"""
        if self._columns != columns:
            self._columns = max(0, columns)
            self.request_layout_update()
            
    def get_columns(self) -> int:
        """Get number of columns"""
        return self._columns
        
    def set_first_column(self, first_column: int):
        """Set first column index"""
        if self._first_column != first_column:
            self._first_column = max(0, first_column)
            self.request_layout_update()
            
    def get_first_column(self) -> int:
        """Get first column index"""
        return self._first_column


class MasonryItem:
    """Item in masonry layout"""
    
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.column = 0
        self.height = 0
        self.y_position = 0


class FluentMasonryLayout(FluentLayoutBase):
    """
    Masonry layout (Pinterest-style staggered grid)
    Items flow into columns with minimal gaps
    """
    
    def __init__(self, column_width: int = 200, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._column_width = column_width
        self._items: List[MasonryItem] = []
        self._column_heights: List[int] = []
        self._calculated_columns = 0
        
        # Performance optimization
        self._layout_timer = QTimer()
        self._layout_timer.setSingleShot(True)
        self._layout_timer.setInterval(50)  # Throttle layout updates
        self._layout_timer.timeout.connect(self._perform_masonry_layout)
        
        self._setup_masonry_layout()
        
    def _setup_masonry_layout(self):
        """Setup masonry layout"""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def add_widget(self, widget: QWidget):
        """Add widget to masonry layout"""
        widget.setParent(self)
        
        masonry_item = MasonryItem(widget)
        self._items.append(masonry_item)
        
        self._request_layout_update()
        
    def remove_widget(self, widget: QWidget):
        """Remove widget from masonry layout"""
        self._items = [item for item in self._items if item.widget != widget]
        widget.setParent(None)
        self._request_layout_update()
        
    def _request_layout_update(self):
        """Request throttled layout update"""
        self._layout_timer.start()
        
    def _perform_layout_update(self):
        """Trigger masonry layout"""
        self._layout_timer.start()
        
    def _perform_masonry_layout(self):
        """Perform masonry layout calculation"""
        if not self._items:
            return
            
        container_rect = self.contentsRect()
        container_rect.adjust(
            self._padding.left(), self._padding.top(),
            -self._padding.right(), -self._padding.bottom()
        )
        
        # Calculate number of columns
        available_width = container_rect.width()
        columns = max(1, available_width // (self._column_width + self._spacing))
        
        if columns != self._calculated_columns:
            self._calculated_columns = columns
            self._column_heights = [0] * columns
            
        # Reset column heights
        self._column_heights = [0] * columns
        
        # Place items in columns
        for item in self._items:
            # Find shortest column
            shortest_column = min(range(columns), key=lambda i: self._column_heights[i])
            
            # Calculate item size
            widget = item.widget
            widget.adjustSize()
            preferred_size = widget.sizeHint()
            
            # Set item properties
            item.column = shortest_column
            item.y_position = self._column_heights[shortest_column]
            item.height = preferred_size.height()
            
            # Calculate position
            x = container_rect.x() + shortest_column * (self._column_width + self._spacing)
            y = container_rect.y() + item.y_position
            
            # Position widget
            widget.setGeometry(x, y, self._column_width, item.height)
            
            # Update column height
            self._column_heights[shortest_column] += item.height + self._spacing
            
        # Update minimum height
        if self._column_heights:
            max_height = max(self._column_heights)
            self.setMinimumHeight(max_height + self._padding.top() + self._padding.bottom())
            
    # Public API
    
    def set_column_width(self, width: int):
        """Set column width"""
        if self._column_width != width:
            self._column_width = max(50, width)
            self._request_layout_update()
            
    def get_column_width(self) -> int:
        """Get column width"""
        return self._column_width
        
    def get_column_count(self) -> int:
        """Get current number of columns"""
        return self._calculated_columns


class LayoutStrategy:
    """Layout strategy for adaptive layouts"""
    
    def __init__(self, name: str, layout_type: str, properties: Dict[str, Any]):
        self.name = name
        self.layout_type = layout_type  # 'stack', 'grid', 'flex', etc.
        self.properties = properties


class FluentAdaptiveLayout(FluentAdaptiveLayoutBase):
    """
    Adaptive layout that switches strategies based on breakpoints
    Combines multiple layout types with smooth transitions
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._items: List[QWidget] = []
        self._current_strategy: Optional[LayoutStrategy] = None
        
        # Default strategies
        self._default_strategies = {
            'xs': LayoutStrategy('mobile_stack', 'stack', {
                'direction': 'vertical',
                'spacing': 8,
                'alignment': 'stretch'
            }),
            'sm': LayoutStrategy('tablet_stack', 'stack', {
                'direction': 'vertical',
                'spacing': 12,
                'alignment': 'stretch'
            }),
            'md': LayoutStrategy('tablet_grid', 'grid', {
                'columns': 2,
                'spacing': 16,
                'item_alignment': 'stretch'
            }),
            'lg': LayoutStrategy('desktop_grid', 'grid', {
                'columns': 3,
                'spacing': 16,
                'item_alignment': 'stretch'
            }),
            'xl': LayoutStrategy('wide_grid', 'grid', {
                'columns': 4,
                'spacing': 20,
                'item_alignment': 'stretch'
            })
        }
        
        # Set default strategies
        for breakpoint, strategy in self._default_strategies.items():
            self.add_layout_strategy(breakpoint, strategy.properties)
            
        self._setup_adaptive_layout()
        
    def _setup_adaptive_layout(self):
        """Setup adaptive layout"""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Apply initial strategy
        current_breakpoint = self.get_current_breakpoint()
        if current_breakpoint in self._layout_strategies:
            self._apply_layout_strategy(self._layout_strategies[current_breakpoint])
            
    def add_widget(self, widget: QWidget):
        """Add widget to adaptive layout"""
        widget.setParent(self)
        self._items.append(widget)
        self.request_layout_update()
        
    def remove_widget(self, widget: QWidget):
        """Remove widget from adaptive layout"""
        if widget in self._items:
            self._items.remove(widget)
            widget.setParent(None)
            self.request_layout_update()
            
    def _apply_layout_strategy(self, strategy: Dict[str, Any]):
        """Apply a layout strategy"""
        layout_type = strategy.get('layout_type', 'stack')
        
        if layout_type == 'stack':
            self._apply_stack_strategy(strategy)
        elif layout_type == 'grid':
            self._apply_grid_strategy(strategy)
        elif layout_type == 'flex':
            self._apply_flex_strategy(strategy)
        else:
            self._apply_stack_strategy(strategy)  # Fallback
            
    def _apply_stack_strategy(self, strategy: Dict[str, Any]):
        """Apply stack layout strategy"""
        direction = strategy.get('direction', 'vertical')
        spacing = strategy.get('spacing', self._spacing)
        
        container_rect = self.contentsRect()
        container_rect.adjust(
            self._padding.left(), self._padding.top(),
            -self._padding.right(), -self._padding.bottom()
        )
        
        if direction == 'vertical':
            self._layout_vertical_stack(container_rect, spacing)
        else:
            self._layout_horizontal_stack(container_rect, spacing)
            
    def _apply_grid_strategy(self, strategy: Dict[str, Any]):
        """Apply grid layout strategy"""
        columns = strategy.get('columns', 2)
        spacing = strategy.get('spacing', self._spacing)
        
        container_rect = self.contentsRect()
        container_rect.adjust(
            self._padding.left(), self._padding.top(),
            -self._padding.right(), -self._padding.bottom()
        )
        
        self._layout_grid(container_rect, columns, spacing)
        
    def _apply_flex_strategy(self, strategy: Dict[str, Any]):
        """Apply flex layout strategy"""
        # Simplified flex implementation
        self._apply_stack_strategy(strategy)
        
    def _layout_vertical_stack(self, container_rect: QRect, spacing: int):
        """Layout items in vertical stack"""
        if not self._items:
            return
            
        item_height = (container_rect.height() - (len(self._items) - 1) * spacing) // len(self._items)
        y = container_rect.y()
        
        for widget in self._items:
            widget.setGeometry(container_rect.x(), y, container_rect.width(), item_height)
            y += item_height + spacing
            
    def _layout_horizontal_stack(self, container_rect: QRect, spacing: int):
        """Layout items in horizontal stack"""
        if not self._items:
            return
            
        item_width = (container_rect.width() - (len(self._items) - 1) * spacing) // len(self._items)
        x = container_rect.x()
        
        for widget in self._items:
            widget.setGeometry(x, container_rect.y(), item_width, container_rect.height())
            x += item_width + spacing
            
    def _layout_grid(self, container_rect: QRect, columns: int, spacing: int):
        """Layout items in grid"""
        if not self._items:
            return
            
        rows = math.ceil(len(self._items) / columns)
        
        item_width = (container_rect.width() - (columns - 1) * spacing) // columns
        item_height = (container_rect.height() - (rows - 1) * spacing) // rows
        
        for i, widget in enumerate(self._items):
            row = i // columns
            col = i % columns
            
            x = container_rect.x() + col * (item_width + spacing)
            y = container_rect.y() + row * (item_height + spacing)
            
            widget.setGeometry(x, y, item_width, item_height)


class FluentCanvas(FluentLayoutBase):
    """
    Canvas layout for absolute positioning
    Similar to HTML Canvas or WPF Canvas
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._positioned_widgets: Dict[QWidget, QRect] = {}
        self._z_order: List[QWidget] = []
        
    def add_widget(self, widget: QWidget, x: int = 0, y: int = 0, 
                   width: int = -1, height: int = -1, z_index: int = 0):
        """Add widget at specific position"""
        widget.setParent(self)
        
        # Use widget's preferred size if not specified
        if width == -1 or height == -1:
            preferred_size = widget.sizeHint()
            if width == -1:
                width = preferred_size.width()
            if height == -1:
                height = preferred_size.height()
                
        # Store position
        self._positioned_widgets[widget] = QRect(x, y, width, height)
        
        # Handle z-order
        self._insert_by_z_index(widget, z_index)
        
        # Position widget
        widget.setGeometry(x, y, width, height)
        widget.show()
        
    def remove_widget(self, widget: QWidget):
        """Remove widget from canvas"""
        if widget in self._positioned_widgets:
            del self._positioned_widgets[widget]
            
        if widget in self._z_order:
            self._z_order.remove(widget)
            
        widget.setParent(None)
        
    def set_widget_position(self, widget: QWidget, x: int, y: int):
        """Set widget position"""
        if widget in self._positioned_widgets:
            rect = self._positioned_widgets[widget]
            rect.setX(x)
            rect.setY(y)
            widget.move(x, y)
            
    def set_widget_size(self, widget: QWidget, width: int, height: int):
        """Set widget size"""
        if widget in self._positioned_widgets:
            rect = self._positioned_widgets[widget]
            rect.setWidth(width)
            rect.setHeight(height)
            widget.resize(width, height)
            
    def set_widget_geometry(self, widget: QWidget, x: int, y: int, width: int, height: int):
        """Set widget geometry"""
        if widget in self._positioned_widgets:
            rect = QRect(x, y, width, height)
            self._positioned_widgets[widget] = rect
            widget.setGeometry(rect)
            
    def get_widget_position(self, widget: QWidget) -> Optional[Tuple[int, int]]:
        """Get widget position"""
        if widget in self._positioned_widgets:
            rect = self._positioned_widgets[widget]
            return (rect.x(), rect.y())
        return None
        
    def get_widget_size(self, widget: QWidget) -> Optional[Tuple[int, int]]:
        """Get widget size"""
        if widget in self._positioned_widgets:
            rect = self._positioned_widgets[widget]
            return (rect.width(), rect.height())
        return None
        
    def set_z_index(self, widget: QWidget, z_index: int):
        """Set widget z-index (stacking order)"""
        if widget in self._z_order:
            self._z_order.remove(widget)
            
        self._insert_by_z_index(widget, z_index)
        self._update_z_order()
        
    def _insert_by_z_index(self, widget: QWidget, z_index: int):
        """Insert widget in z-order list based on z-index"""
        # For simplicity, just append and sort later
        self._z_order.append(widget)
        setattr(widget, 'z_index', z_index)  # Store z-index as widget attribute
        
    def _update_z_order(self):
        """Update widget stacking order"""
        # Sort by z-index
        self._z_order.sort(key=lambda w: getattr(w, 'z_index', 0))
        
        # Raise widgets in order
        for widget in self._z_order:
            widget.raise_()
            
    def move_widget_animated(self, widget: QWidget, x: int, y: int, duration: int = 200):
        """Move widget with animation"""
        if widget not in self._positioned_widgets:
            return
            
        animation = QPropertyAnimation(widget, QByteArray(b"geometry"))
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        current_rect = widget.geometry()
        target_rect = QRect(x, y, current_rect.width(), current_rect.height())
        
        animation.setStartValue(current_rect)
        animation.setEndValue(target_rect)
        
        # Update stored position when animation finishes
        def update_stored_position():
            self._positioned_widgets[widget] = target_rect
            
        animation.finished.connect(update_stored_position)
        animation.start()
        
        # Store animation to prevent garbage collection
        setattr(widget, '_move_animation', animation)
