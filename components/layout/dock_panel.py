"""
Fluent Dock Panel - Dock widgets to edges with center fill
Similar to WPF DockPanel with modern Fluent design
"""

from typing import Optional, List, Dict, Any
from enum import Enum

from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, Signal, QSize, QRect
from PySide6.QtGui import QResizeEvent

from .layout_base import FluentLayoutBase


class DockPosition(Enum):
    """Dock position options"""
    LEFT = "left"
    TOP = "top"
    RIGHT = "right"
    BOTTOM = "bottom"
    FILL = "fill"


class DockItem:
    """Represents a docked widget"""
    
    def __init__(self, widget: QWidget, position: DockPosition, size: int = -1):
        self.widget = widget
        self.position = position
        self.size = size  # Fixed size for docked panels, -1 for auto
        self.min_size = 0
        self.max_size = 16777215  # QWIDGETSIZE_MAX
        self.splitter_enabled = True  # Whether the dock can be resized
        self.target_rect = QRect()  # Target rectangle for animation


class FluentDockPanel(FluentLayoutBase):
    """
    Dock panel layout that arranges widgets around the edges with a center fill area
    
    Features:
    - Dock widgets to left, top, right, bottom, or fill center
    - Resizable dock areas with splitters
    - Minimum and maximum size constraints
    - Auto-hiding collapsed docks
    - Responsive behavior for mobile layouts
    """
    
    # Dock-specific signals
    dock_position_changed = Signal(QWidget, DockPosition)
    dock_size_changed = Signal(QWidget, int)
    dock_collapsed = Signal(QWidget)
    dock_expanded = Signal(QWidget)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Dock properties
        self._dock_items: List[DockItem] = []
        self._fill_widget: Optional[QWidget] = None
        self._splitter_width = 6
        self._auto_hide_empty = True
        self._collapse_threshold = 50
        
        # Layout areas
        self._left_area = QRect()
        self._top_area = QRect()
        self._right_area = QRect()
        self._bottom_area = QRect()
        self._center_area = QRect()
        
        # Responsive behavior
        self._mobile_stack_threshold = 768  # Stack docks vertically below this width
        self._mobile_mode = False
        
        self._setup_dock_panel()
        
    def _setup_dock_panel(self):
        """Setup dock panel"""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout_changed.connect(self._update_dock_layout)
        
    def _update_dock_layout(self):
        """Update dock layout when changes occur"""
        self.update()
        
    def add_dock_widget(self, widget: QWidget, position: DockPosition, 
                       size: int = -1, min_size: int = 0, max_size: int = 16777215) -> DockItem:
        """Add a widget to the dock panel"""
        widget.setParent(self)
        
        if position == DockPosition.FILL:
            # Only one fill widget allowed
            if self._fill_widget:
                self._fill_widget.setParent(None)
            self._fill_widget = widget
            dock_item = DockItem(widget, position, size)
        else:
            dock_item = DockItem(widget, position, size)
            dock_item.min_size = min_size
            dock_item.max_size = max_size
            self._dock_items.append(dock_item)
        
        self.request_layout_update()
        return dock_item
        
    def remove_dock_widget(self, widget: QWidget):
        """Remove a widget from the dock panel"""
        if self._fill_widget == widget:
            self._fill_widget = None
            widget.setParent(None)
        else:
            self._dock_items = [item for item in self._dock_items if item.widget != widget]
            widget.setParent(None)
            
        self.request_layout_update()
        
    def set_dock_position(self, widget: QWidget, position: DockPosition):
        """Change the dock position of a widget"""
        if self._fill_widget == widget and position != DockPosition.FILL:
            # Moving fill widget to dock
            self._fill_widget = None
            dock_item = DockItem(widget, position)
            self._dock_items.append(dock_item)
        elif position == DockPosition.FILL:
            # Moving dock widget to fill
            self._dock_items = [item for item in self._dock_items if item.widget != widget]
            if self._fill_widget:
                self._fill_widget.setParent(None)
            self._fill_widget = widget
        else:
            # Changing dock position
            for item in self._dock_items:
                if item.widget == widget:
                    item.position = position
                    break
                    
        self.dock_position_changed.emit(widget, position)
        self.request_layout_update()
        
    def get_dock_position(self, widget: QWidget) -> Optional[DockPosition]:
        """Get the dock position of a widget"""
        if self._fill_widget == widget:
            return DockPosition.FILL
            
        for item in self._dock_items:
            if item.widget == widget:
                return item.position
                
        return None
        
    def set_dock_size(self, widget: QWidget, size: int):
        """Set the size of a docked widget"""
        for item in self._dock_items:
            if item.widget == widget:
                old_size = item.size
                item.size = max(item.min_size, min(size, item.max_size))
                if old_size != item.size:
                    self.dock_size_changed.emit(widget, item.size)
                    self.request_layout_update()
                break
                
    def get_dock_size(self, widget: QWidget) -> int:
        """Get the size of a docked widget"""
        for item in self._dock_items:
            if item.widget == widget:
                return item.size
        return -1
        
    def collapse_dock(self, widget: QWidget):
        """Collapse a docked widget"""
        for item in self._dock_items:
            if item.widget == widget:
                item.size = 0
                widget.hide()
                self.dock_collapsed.emit(widget)
                self.request_layout_update()
                break
                
    def expand_dock(self, widget: QWidget, size: int = -1):
        """Expand a collapsed docked widget"""
        for item in self._dock_items:
            if item.widget == widget:
                if size == -1:
                    # Use preferred size
                    preferred_size = widget.sizeHint()
                    if item.position in [DockPosition.LEFT, DockPosition.RIGHT]:
                        size = preferred_size.width()
                    else:
                        size = preferred_size.height()
                        
                item.size = max(item.min_size, min(size, item.max_size))
                widget.show()
                self.dock_expanded.emit(widget)
                self.request_layout_update()
                break
                
    def _perform_layout_update(self):
        """Perform dock panel layout calculation"""
        super()._perform_layout_update()
        
        container_rect = self.contentsRect()
        container_rect.adjust(
            self._padding.left(), self._padding.top(),
            -self._padding.right(), -self._padding.bottom()
        )
        
        # Check for mobile mode
        self._update_mobile_mode(container_rect.width())
        
        if self._mobile_mode:
            self._layout_mobile_mode(container_rect)
        else:
            self._layout_desktop_mode(container_rect)
            
        self._position_widgets()
        
    def _update_mobile_mode(self, width: int):
        """Update mobile mode based on width"""
        old_mobile = self._mobile_mode
        self._mobile_mode = width < self._mobile_stack_threshold
        
        if old_mobile != self._mobile_mode:
            # Mobile mode changed, need to adjust layout
            self._adjust_for_mobile_mode()
            
    def _adjust_for_mobile_mode(self):
        """Adjust dock items for mobile mode"""
        if self._mobile_mode:
            # In mobile mode, stack all docks vertically
            for item in self._dock_items:
                if item.position in [DockPosition.LEFT, DockPosition.RIGHT]:
                    # Convert horizontal docks to top/bottom
                    if item.position == DockPosition.LEFT:
                        item.position = DockPosition.TOP
                    else:
                        item.position = DockPosition.BOTTOM
                        
    def _layout_desktop_mode(self, container_rect: QRect):
        """Layout docks in desktop mode"""
        # Calculate dock areas in order: left, top, right, bottom, center
        current_rect = QRect(container_rect)
        
        # Left docks
        left_width = 0
        for item in self._dock_items:
            if item.position == DockPosition.LEFT:
                width = self._calculate_dock_size(item, current_rect.width(), True)
                left_width += width + self._spacing
                
        if left_width > 0:
            left_width -= self._spacing  # Remove last spacing
            self._left_area = QRect(current_rect.x(), current_rect.y(), 
                                   left_width, current_rect.height())
            current_rect.setX(current_rect.x() + left_width + self._splitter_width)
            current_rect.setWidth(current_rect.width() - left_width - self._splitter_width)
        else:
            self._left_area = QRect()
            
        # Right docks
        right_width = 0
        for item in self._dock_items:
            if item.position == DockPosition.RIGHT:
                width = self._calculate_dock_size(item, current_rect.width(), True)
                right_width += width + self._spacing
                
        if right_width > 0:
            right_width -= self._spacing  # Remove last spacing
            self._right_area = QRect(current_rect.right() - right_width + 1, current_rect.y(),
                                    right_width, current_rect.height())
            current_rect.setWidth(current_rect.width() - right_width - self._splitter_width)
        else:
            self._right_area = QRect()
            
        # Top docks
        top_height = 0
        for item in self._dock_items:
            if item.position == DockPosition.TOP:
                height = self._calculate_dock_size(item, current_rect.height(), False)
                top_height += height + self._spacing
                
        if top_height > 0:
            top_height -= self._spacing  # Remove last spacing
            self._top_area = QRect(current_rect.x(), current_rect.y(),
                                  current_rect.width(), top_height)
            current_rect.setY(current_rect.y() + top_height + self._splitter_width)
            current_rect.setHeight(current_rect.height() - top_height - self._splitter_width)
        else:
            self._top_area = QRect()
            
        # Bottom docks
        bottom_height = 0
        for item in self._dock_items:
            if item.position == DockPosition.BOTTOM:
                height = self._calculate_dock_size(item, current_rect.height(), False)
                bottom_height += height + self._spacing
                
        if bottom_height > 0:
            bottom_height -= self._spacing  # Remove last spacing
            self._bottom_area = QRect(current_rect.x(), current_rect.bottom() - bottom_height + 1,
                                     current_rect.width(), bottom_height)
            current_rect.setHeight(current_rect.height() - bottom_height - self._splitter_width)
        else:
            self._bottom_area = QRect()
            
        # Center area
        self._center_area = current_rect
        
    def _layout_mobile_mode(self, container_rect: QRect):
        """Layout docks in mobile mode (stacked vertically)"""
        current_y = container_rect.y()
        available_height = container_rect.height()
        
        # Calculate total height needed for docks
        total_dock_height = 0
        dock_count = 0
        
        for item in self._dock_items:
            if item.widget.isVisible():
                height = self._calculate_dock_size(item, available_height, False)
                total_dock_height += height
                dock_count += 1
                
        if dock_count > 0:
            total_dock_height += (dock_count - 1) * self._spacing
            
        # Stack docks vertically
        for item in self._dock_items:
            if item.widget.isVisible():
                height = self._calculate_dock_size(item, available_height, False)
                item.target_rect = QRect(container_rect.x(), current_y,
                                       container_rect.width(), height)
                current_y += height + self._spacing
                
        # Remaining space for fill widget
        if self._fill_widget and self._fill_widget.isVisible():
            remaining_height = container_rect.bottom() - current_y + 1
            self._center_area = QRect(container_rect.x(), current_y,
                                     container_rect.width(), max(0, remaining_height))
        else:
            self._center_area = QRect()
            
    def _calculate_dock_size(self, item: DockItem, available_space: int, is_width: bool) -> int:
        """Calculate the size of a dock item"""
        if item.size >= 0:
            # Fixed size
            return min(item.size, available_space)
        else:
            # Auto size based on widget's preferred size
            preferred_size = item.widget.sizeHint()
            if is_width:
                size = preferred_size.width()
            else:
                size = preferred_size.height()
                
            # Apply constraints
            size = max(item.min_size, min(size, item.max_size))
            return min(size, available_space)
            
    def _position_widgets(self):
        """Position all dock widgets"""
        # Position left docks
        x = self._left_area.x()
        for item in self._dock_items:
            if item.position == DockPosition.LEFT and item.widget.isVisible():
                width = self._calculate_dock_size(item, self._left_area.width(), True)
                item.widget.setGeometry(x, self._left_area.y(), width, self._left_area.height())
                x += width + self._spacing
                
        # Position right docks
        x = self._right_area.right()
        for item in reversed(self._dock_items):
            if item.position == DockPosition.RIGHT and item.widget.isVisible():
                width = self._calculate_dock_size(item, self._right_area.width(), True)
                x -= width
                item.widget.setGeometry(x, self._right_area.y(), width, self._right_area.height())
                x -= self._spacing
                
        # Position top docks
        y = self._top_area.y()
        for item in self._dock_items:
            if item.position == DockPosition.TOP and item.widget.isVisible():
                height = self._calculate_dock_size(item, self._top_area.height(), False)
                item.widget.setGeometry(self._top_area.x(), y, self._top_area.width(), height)
                y += height + self._spacing
                
        # Position bottom docks
        y = self._bottom_area.bottom()
        for item in reversed(self._dock_items):
            if item.position == DockPosition.BOTTOM and item.widget.isVisible():
                height = self._calculate_dock_size(item, self._bottom_area.height(), False)
                y -= height
                item.widget.setGeometry(self._bottom_area.x(), y, self._bottom_area.width(), height)
                y -= self._spacing
                
        # Position fill widget
        if self._fill_widget and self._fill_widget.isVisible():
            self._fill_widget.setGeometry(self._center_area)
            
    # Responsive breakpoint handling
    def _on_breakpoint_changed(self, old_breakpoint: str, new_breakpoint: str):
        """Handle responsive breakpoint changes"""
        super()._on_breakpoint_changed(old_breakpoint, new_breakpoint)
        
        # Adjust dock sizes based on breakpoint
        if new_breakpoint in ['xs', 'sm']:
            # Small screens - collapse or minimize docks
            for item in self._dock_items:
                if item.position in [DockPosition.LEFT, DockPosition.RIGHT]:
                    # Collapse side docks on small screens
                    if item.size > self._collapse_threshold:
                        self.collapse_dock(item.widget)
                        
    # Public API
    
    def set_splitter_width(self, width: int):
        """Set the width of splitters between dock areas"""
        if self._splitter_width != width:
            self._splitter_width = max(0, width)
            self.request_layout_update()
            
    def get_splitter_width(self) -> int:
        """Get splitter width"""
        return self._splitter_width
        
    def set_mobile_threshold(self, threshold: int):
        """Set the width threshold for mobile mode"""
        if self._mobile_stack_threshold != threshold:
            self._mobile_stack_threshold = threshold
            self.request_layout_update()
            
    def get_mobile_threshold(self) -> int:
        """Get mobile threshold"""
        return self._mobile_stack_threshold
        
    def is_mobile_mode(self) -> bool:
        """Check if currently in mobile mode"""
        return self._mobile_mode
        
    def get_dock_items(self) -> List[DockItem]:
        """Get all dock items"""
        return self._dock_items.copy()
        
    def get_fill_widget(self) -> Optional[QWidget]:
        """Get the fill widget"""
        return self._fill_widget
