"""
Fluent Design Grid Component
Responsive grid layout system with automatic sizing
"""

from PySide6.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QFrame, 
                               QSizePolicy, QScrollArea)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QResizeEvent
from core.theme import theme_manager
from core.enhanced_base import FluentBaseWidget
from typing import Optional, List, Dict
from enum import Enum


class GridSpacing(Enum):
    """Grid spacing options"""
    NONE = 0
    SMALL = 4
    MEDIUM = 8
    LARGE = 16
    EXTRA_LARGE = 24


class GridItemAlignment(Enum):
    """Grid item alignment options"""
    STRETCH = "stretch"
    START = "start"
    CENTER = "center"
    END = "end"


class FluentGridItem:
    """Represents an item in the grid"""
    
    def __init__(self, widget: QWidget, column_span: int = 1, row_span: int = 1):
        self.widget = widget
        self.column_span = column_span
        self.row_span = row_span
        self.min_width = 0
        self.preferred_width = 200
        self.max_width = -1  # -1 means unlimited
        self.alignment = GridItemAlignment.STRETCH


class FluentGrid(FluentBaseWidget):
    """
    Fluent Design Grid Component
    
    Responsive grid layout that automatically adjusts columns based on:
    - Available space
    - Item minimum/preferred sizes
    - Responsive breakpoints
    - Consistent spacing and alignment
    """
    
    # Signals
    layout_changed = Signal()  # Emitted when grid layout changes
    item_clicked = Signal(QWidget)  # Emitted when an item is clicked
    
    def __init__(self, parent: Optional[QWidget] = None,
                 min_column_width: int = 200,
                 max_columns: int = -1):
        super().__init__(parent)
        
        # Properties
        self._min_column_width = min_column_width
        self._max_columns = max_columns  # -1 means unlimited
        self._spacing = GridSpacing.MEDIUM
        self._item_alignment = GridItemAlignment.STRETCH
        
        # Responsive breakpoints (width -> columns)
        self._breakpoints = {
            0: 1,      # Mobile
            480: 2,    # Small tablet
            768: 3,    # Tablet
            1024: 4,   # Small desktop
            1200: 5,   # Medium desktop
            1440: 6    # Large desktop
        }
        
        # State
        self._current_columns = 1
        self._items: List[FluentGridItem] = []
        self._item_widgets: List[QWidget] = []
        
        # UI Elements - initialized in _setup_ui
        self._scroll_area: QScrollArea
        self._grid_container: QWidget
        self._grid_layout: QGridLayout
        
        # Resize timer for responsive behavior
        self._resize_timer = QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(100)
        self._resize_timer.timeout.connect(self._update_layout)
        
        # Setup
        self._setup_ui()
        self._setup_style()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup the UI layout"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area for when content exceeds viewport
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Grid container widget
        self._grid_container = QWidget()
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(self._spacing.value)
        
        self._scroll_area.setWidget(self._grid_container)
        main_layout.addWidget(self._scroll_area)
        
    def _setup_style(self):
        """Apply Fluent Design styling"""
        theme = theme_manager
        
        # Scroll area style
        scroll_style = f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme.get_color('border').name()};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme.get_color('text_secondary').name()};
            }}
        """
        
        # Grid container style
        container_style = """
            QWidget {
                background: transparent;
            }
        """
        
        self._scroll_area.setStyleSheet(scroll_style)
        self._grid_container.setStyleSheet(container_style)
        
    def _connect_signals(self):
        """Connect signals and slots"""
        # Theme changes
        theme_manager.theme_changed.connect(self._setup_style)
        
    def resizeEvent(self, event: QResizeEvent):
        """Handle resize events to trigger responsive layout"""
        super().resizeEvent(event)
        self._resize_timer.start()
        
    def _calculate_optimal_columns(self) -> int:
        """Calculate optimal number of columns based on available width"""
        available_width = self._scroll_area.viewport().width()
        
        # Check responsive breakpoints
        columns_from_breakpoints = 1
        for width, columns in sorted(self._breakpoints.items()):
            if available_width >= width:
                columns_from_breakpoints = columns
                
        # Calculate columns based on minimum width
        columns_from_width = max(1, available_width // self._min_column_width)
        
        # Use the minimum of the two calculations
        optimal_columns = min(columns_from_breakpoints, columns_from_width)
        
        # Respect maximum columns limit
        if self._max_columns > 0:
            optimal_columns = min(optimal_columns, self._max_columns)
            
        return optimal_columns
        
    def _update_layout(self):
        """Update the grid layout based on current size"""
        new_columns = self._calculate_optimal_columns()
        
        if new_columns != self._current_columns:
            self._current_columns = new_columns
            self._rebuild_layout()
            self.layout_changed.emit()
            
    def _rebuild_layout(self):
        """Rebuild the entire grid layout"""
        # Clear existing layout
        while self._grid_layout.count():
            child = self._grid_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
                
        # Place items in grid
        row = 0
        col = 0
        
        for item in self._items:
            # Check if item fits in current row
            if col + item.column_span > self._current_columns:
                # Move to next row
                row += 1
                col = 0
                
            # Add item to grid
            self._grid_layout.addWidget(
                item.widget, 
                row, col, 
                item.row_span, item.column_span
            )
            
            # Apply alignment
            self._apply_item_alignment(item)
            
            # Update column position
            col += item.column_span
            
            # If we've filled the row, move to next row
            if col >= self._current_columns:
                row += 1
                col = 0
                
        # Set equal column stretches
        for i in range(self._current_columns):
            self._grid_layout.setColumnStretch(i, 1)
            
    def _apply_item_alignment(self, item: FluentGridItem):
        """Apply alignment settings to grid item"""
        if item.alignment == GridItemAlignment.STRETCH:
            item.widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        elif item.alignment == GridItemAlignment.START:
            item.widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        elif item.alignment == GridItemAlignment.CENTER:
            item.widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        elif item.alignment == GridItemAlignment.END:
            item.widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            
    def _setup_widget_click_handler(self, widget: QWidget):
        """Setup click handler for a widget"""
        # Check if widget has a clicked signal (like QPushButton)
        clicked_signal = getattr(widget, 'clicked', None)
        # 只有当 clicked_signal 存在且有 connect 方法时才连接
        if clicked_signal is not None and hasattr(clicked_signal, 'connect'):
            try:
                clicked_signal.connect(lambda: self.item_clicked.emit(widget))
                return
            except (AttributeError, TypeError):
                pass
        
        # For widgets without clicked signal, override mousePressEvent
        if hasattr(widget, 'mousePressEvent'):
            original_mouse_press = widget.mousePressEvent
            def mouse_press_wrapper(event):
                self.item_clicked.emit(widget)
                original_mouse_press(event)
            widget.mousePressEvent = mouse_press_wrapper
            
    # Public API
    
    def add_item(self, widget: QWidget, column_span: int = 1, row_span: int = 1,
                alignment: GridItemAlignment = GridItemAlignment.STRETCH) -> FluentGridItem:
        """Add a widget to the grid"""
        item = FluentGridItem(widget, column_span, row_span)
        item.alignment = alignment
        
        self._items.append(item)
        self._item_widgets.append(widget)
        
        # Setup click handler for the widget
        self._setup_widget_click_handler(widget)
            
        self._rebuild_layout()
        return item
        
    def remove_item(self, widget: QWidget):
        """Remove a widget from the grid"""
        self._items = [item for item in self._items if item.widget != widget]
        if widget in self._item_widgets:
            self._item_widgets.remove(widget)
            
        widget.setParent(None)
        self._rebuild_layout()
        
    def clear_items(self):
        """Remove all items from the grid"""
        for widget in self._item_widgets:
            widget.setParent(None)
            
        self._items.clear()
        self._item_widgets.clear()
        self._rebuild_layout()
        
    def get_item_count(self) -> int:
        """Get the number of items in the grid"""
        return len(self._items)
        
    def get_current_columns(self) -> int:
        """Get the current number of columns"""
        return self._current_columns
        
    def set_spacing(self, spacing: GridSpacing):
        """Set the spacing between grid items"""
        self._spacing = spacing
        self._grid_layout.setSpacing(spacing.value)
            
    def set_min_column_width(self, width: int):
        """Set the minimum column width"""
        self._min_column_width = width
        self._update_layout()
        
    def set_max_columns(self, max_columns: int):
        """Set the maximum number of columns (-1 for unlimited)"""
        self._max_columns = max_columns
        self._update_layout()
        
    def set_item_alignment(self, alignment: GridItemAlignment):
        """Set the default alignment for new items"""
        self._item_alignment = alignment
        
    def set_breakpoints(self, breakpoints: Dict[int, int]):
        """Set custom responsive breakpoints"""
        self._breakpoints = breakpoints
        self._update_layout()
        
    def get_item_at(self, index: int) -> Optional[FluentGridItem]:
        """Get item at specific index"""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
        
    def find_item(self, widget: QWidget) -> Optional[FluentGridItem]:
        """Find grid item containing the specified widget"""
        for item in self._items:
            if item.widget == widget:
                return item
        return None
        
    def set_item_span(self, widget: QWidget, column_span: int, row_span: int = 1):
        """Change the span of an existing item"""
        item = self.find_item(widget)
        if item:
            item.column_span = column_span
            item.row_span = row_span
            self._rebuild_layout()
            
    def force_layout_update(self):
        """Force an immediate layout update"""
        self._update_layout()


class FluentGridBuilder:
    """Builder for creating FluentGrid with fluent API"""
    
    def __init__(self):
        self._min_column_width = 200
        self._max_columns = -1
        self._spacing = GridSpacing.MEDIUM
        self._breakpoints = {}
        self._items = []
        
    def with_min_column_width(self, width: int):
        """Set minimum column width"""
        self._min_column_width = width
        return self
        
    def with_max_columns(self, max_columns: int):
        """Set maximum columns"""
        self._max_columns = max_columns
        return self
        
    def with_spacing(self, spacing: GridSpacing):
        """Set grid spacing"""
        self._spacing = spacing
        return self
        
    def with_breakpoints(self, breakpoints: Dict[int, int]):
        """Set responsive breakpoints"""
        self._breakpoints = breakpoints
        return self
        
    def add_item(self, widget: QWidget, column_span: int = 1, row_span: int = 1,
                alignment: GridItemAlignment = GridItemAlignment.STRETCH):
        """Add an item to the grid"""
        self._items.append({
            'widget': widget,
            'column_span': column_span,
            'row_span': row_span,
            'alignment': alignment
        })
        return self
        
    def build(self, parent: Optional[QWidget] = None) -> FluentGrid:
        """Build the grid"""
        grid = FluentGrid(parent, self._min_column_width, self._max_columns)
        grid.set_spacing(self._spacing)
        
        if self._breakpoints:
            grid.set_breakpoints(self._breakpoints)
            
        # Add items
        for item_def in self._items:
            grid.add_item(**item_def)
            
        return grid


# Export classes
__all__ = [
    'FluentGrid',
    'FluentGridItem',
    'FluentGridBuilder',
    'GridSpacing',
    'GridItemAlignment'
]
