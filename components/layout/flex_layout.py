"""
Fluent Flex Layout - CSS Flexbox-inspired layout for Qt
Provides flexible, responsive layout with proper flex grow/shrink behavior
"""

from typing import Optional, List, Dict, Any, Union
from enum import Enum

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLayoutItem
from PySide6.QtCore import Qt, Signal, QSize, QRect
from PySide6.QtGui import QResizeEvent

from .layout_base import FluentLayoutBase


class FlexDirection(Enum):
    """Flex direction options"""
    ROW = "row"
    COLUMN = "column"
    ROW_REVERSE = "row-reverse"
    COLUMN_REVERSE = "column-reverse"


class FlexWrap(Enum):
    """Flex wrap options"""
    NO_WRAP = "nowrap"
    WRAP = "wrap"
    WRAP_REVERSE = "wrap-reverse"


class JustifyContent(Enum):
    """Main axis alignment options"""
    FLEX_START = "flex-start"
    FLEX_END = "flex-end"
    CENTER = "center"
    SPACE_BETWEEN = "space-between"
    SPACE_AROUND = "space-around"
    SPACE_EVENLY = "space-evenly"


class AlignItems(Enum):
    """Cross axis alignment options"""
    STRETCH = "stretch"
    FLEX_START = "flex-start"
    FLEX_END = "flex-end"
    CENTER = "center"
    BASELINE = "baseline"


class AlignContent(Enum):
    """Multi-line alignment options"""
    STRETCH = "stretch"
    FLEX_START = "flex-start"
    FLEX_END = "flex-end"
    CENTER = "center"
    SPACE_BETWEEN = "space-between"
    SPACE_AROUND = "space-around"


class FlexItem:
    """Represents a flex item with its properties"""
    
    def __init__(self, widget: QWidget, flex_grow: float = 0, flex_shrink: float = 1, 
                 flex_basis: Union[int, str] = "auto", align_self: Optional[AlignItems] = None):
        self.widget = widget
        self.flex_grow = max(0, flex_grow)
        self.flex_shrink = max(0, flex_shrink)
        self.flex_basis = flex_basis
        self.align_self = align_self
        
        # Calculated properties
        self.calculated_size = QSize()
        self.target_rect = QRect()


class FluentFlexLayout(FluentLayoutBase):
    """
    CSS Flexbox-inspired layout for Qt widgets
    
    Features:
    - Flexible item sizing with grow/shrink
    - Multiple alignment options
    - Wrapping support
    - Responsive behavior
    - Proper baseline alignment
    """
    
    # Flex-specific signals
    flex_direction_changed = Signal(FlexDirection)
    wrap_changed = Signal(FlexWrap)
    items_wrapped = Signal(bool)  # True when items wrap to multiple lines
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Flex properties
        self._flex_direction = FlexDirection.ROW
        self._flex_wrap = FlexWrap.NO_WRAP
        self._justify_content = JustifyContent.FLEX_START
        self._align_items = AlignItems.STRETCH
        self._align_content = AlignContent.STRETCH
        
        # Items
        self._flex_items: List[FlexItem] = []
        self._item_rects: List[QRect] = []
        self._lines: List[List[FlexItem]] = []  # Wrapped lines
        
        # Gap (modern flexbox feature)
        self._row_gap = 0
        self._column_gap = 0
        
        self._setup_flex_layout()
        
    def _setup_flex_layout(self):
        """Setup flex layout"""
        # Set initial size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Connect to layout changes
        self.layout_changed.connect(self._update_flex_layout)
        
    def _update_flex_layout(self):
        """Update flex layout when changes occur"""
        self.update()  # Use Qt's update method instead
        
    def add_widget(self, widget: QWidget, flex_grow: float = 0, flex_shrink: float = 1,
                   flex_basis: Union[int, str] = "auto", align_self: Optional[AlignItems] = None):
        """Add a widget with flex properties"""
        widget.setParent(self)
        
        flex_item = FlexItem(widget, flex_grow, flex_shrink, flex_basis, align_self)
        self._flex_items.append(flex_item)
        
        self.request_layout_update()
        
    def remove_widget(self, widget: QWidget):
        """Remove a widget from flex layout"""
        self._flex_items = [item for item in self._flex_items if item.widget != widget]
        widget.setParent(None)
        self.request_layout_update()
        
    def _perform_layout_update(self):
        """Perform flex layout calculation and positioning"""
        super()._perform_layout_update()
        
        if not self._flex_items:
            return
            
        container_rect = self.contentsRect()
        container_rect.adjust(
            self._padding.left(), self._padding.top(),
            -self._padding.right(), -self._padding.bottom()
        )
        
        # Step 1: Determine available space
        available_width = container_rect.width()
        available_height = container_rect.height()
        
        # Step 2: Resolve flex basis for all items
        self._resolve_flex_basis(available_width, available_height)
        
        # Step 3: Collect items into flex lines
        self._collect_flex_lines(available_width, available_height)
        
        # Step 4: Resolve flexible lengths
        self._resolve_flexible_lengths()
        
        # Step 5: Main axis alignment
        self._align_main_axis(container_rect)
        
        # Step 6: Cross axis alignment
        self._align_cross_axis(container_rect)
        
        # Step 7: Position widgets
        self._position_widgets()
        
    def _resolve_flex_basis(self, available_width: int, available_height: int):
        """Resolve flex-basis for all items"""
        is_horizontal = self._flex_direction in [FlexDirection.ROW, FlexDirection.ROW_REVERSE]
        
        for item in self._flex_items:
            widget = item.widget
            
            if item.flex_basis == "auto":
                # Use widget's preferred size
                preferred_size = widget.sizeHint()
                if preferred_size.isValid():
                    item.calculated_size = preferred_size
                else:
                    item.calculated_size = QSize(100, 32)  # Default size
            elif isinstance(item.flex_basis, int):
                # Fixed size
                if is_horizontal:
                    height = widget.sizeHint().height()
                    item.calculated_size = QSize(item.flex_basis, height)
                else:
                    width = widget.sizeHint().width()
                    item.calculated_size = QSize(width, item.flex_basis)
            else:
                # Percentage or other units (simplified)
                item.calculated_size = widget.sizeHint()
                
    def _collect_flex_lines(self, available_width: int, available_height: int):
        """Collect items into flex lines based on wrapping"""
        self._lines.clear()
        
        if self._flex_wrap == FlexWrap.NO_WRAP:
            # Single line
            self._lines.append(self._flex_items.copy())
            return
            
        # Multi-line wrapping
        is_horizontal = self._flex_direction in [FlexDirection.ROW, FlexDirection.ROW_REVERSE]
        current_line = []
        current_line_size = 0
        
        for item in self._flex_items:
            item_size = (item.calculated_size.width() if is_horizontal 
                        else item.calculated_size.height())
            gap = (self._column_gap if is_horizontal else self._row_gap)
            
            # Check if item fits in current line
            needed_size = current_line_size + item_size + (gap if current_line else 0)
            max_size = available_width if is_horizontal else available_height
            
            if current_line and needed_size > max_size:
                # Start new line
                self._lines.append(current_line)
                current_line = [item]
                current_line_size = item_size
            else:
                # Add to current line
                current_line.append(item)
                current_line_size = needed_size
                
        if current_line:
            self._lines.append(current_line)
            
        # Emit wrapping signal
        self.items_wrapped.emit(len(self._lines) > 1)
        
    def _resolve_flexible_lengths(self):
        """Resolve flexible lengths for each line"""
        is_horizontal = self._flex_direction in [FlexDirection.ROW, FlexDirection.ROW_REVERSE]
        
        for line in self._lines:
            if not line:
                continue
                
            # Calculate available space for this line
            container_size = (self.contentsRect().width() if is_horizontal 
                            else self.contentsRect().height())
            
            # Subtract fixed sizes and gaps
            used_space = 0
            gap = self._column_gap if is_horizontal else self._row_gap
            
            for i, item in enumerate(line):
                item_size = (item.calculated_size.width() if is_horizontal 
                           else item.calculated_size.height())
                used_space += item_size
                if i > 0:
                    used_space += gap
                    
            free_space = container_size - used_space
            
            # Distribute free space based on flex-grow/shrink
            if free_space > 0:
                self._distribute_positive_free_space(line, free_space, is_horizontal)
            elif free_space < 0:
                self._distribute_negative_free_space(line, abs(free_space), is_horizontal)
                
    def _distribute_positive_free_space(self, line: List[FlexItem], free_space: int, is_horizontal: bool):
        """Distribute positive free space using flex-grow"""
        total_grow = sum(item.flex_grow for item in line)
        
        if total_grow == 0:
            return  # No flexible items
            
        space_per_grow = free_space / total_grow
        
        for item in line:
            if item.flex_grow > 0:
                additional_space = int(space_per_grow * item.flex_grow)
                if is_horizontal:
                    new_width = item.calculated_size.width() + additional_space
                    item.calculated_size.setWidth(new_width)
                else:
                    new_height = item.calculated_size.height() + additional_space
                    item.calculated_size.setHeight(new_height)
                    
    def _distribute_negative_free_space(self, line: List[FlexItem], deficit: int, is_horizontal: bool):
        """Distribute negative free space using flex-shrink"""
        total_shrink_factor = 0
        
        for item in line:
            base_size = (item.calculated_size.width() if is_horizontal 
                        else item.calculated_size.height())
            total_shrink_factor += item.flex_shrink * base_size
            
        if total_shrink_factor == 0:
            return  # No shrinkable items
            
        for item in line:
            base_size = (item.calculated_size.width() if is_horizontal 
                        else item.calculated_size.height())
            shrink_factor = item.flex_shrink * base_size
            shrink_amount = int((shrink_factor / total_shrink_factor) * deficit)
            
            if is_horizontal:
                new_width = max(0, item.calculated_size.width() - shrink_amount)
                item.calculated_size.setWidth(new_width)
            else:
                new_height = max(0, item.calculated_size.height() - shrink_amount)
                item.calculated_size.setHeight(new_height)
                
    def _align_main_axis(self, container_rect: QRect):
        """Align items along the main axis"""
        is_horizontal = self._flex_direction in [FlexDirection.ROW, FlexDirection.ROW_REVERSE]
        
        for line in self._lines:
            if not line:
                continue
                
            # Calculate total line size
            line_size = 0
            gap = self._column_gap if is_horizontal else self._row_gap
            
            for i, item in enumerate(line):
                item_size = (item.calculated_size.width() if is_horizontal 
                           else item.calculated_size.height())
                line_size += item_size
                if i > 0:
                    line_size += gap
                    
            container_size = (container_rect.width() if is_horizontal 
                            else container_rect.height())
            free_space = container_size - line_size
            
            # Calculate positions based on justify-content
            positions = self._calculate_main_axis_positions(
                len(line), line_size, free_space, container_size)
            
            # Apply positions
            for i, item in enumerate(line):
                if is_horizontal:
                    item.target_rect.setX(container_rect.x() + positions[i])
                    item.target_rect.setWidth(item.calculated_size.width())
                else:
                    item.target_rect.setY(container_rect.y() + positions[i])
                    item.target_rect.setHeight(item.calculated_size.height())
                    
    def _calculate_main_axis_positions(self, item_count: int, line_size: int, 
                                     free_space: int, container_size: int) -> List[int]:
        """Calculate item positions along main axis"""
        positions = []
        
        if self._justify_content == JustifyContent.FLEX_START:
            pos = 0
            for i in range(item_count):
                positions.append(pos)
                pos += self._get_item_main_size(i) + self._get_main_gap()
                
        elif self._justify_content == JustifyContent.FLEX_END:
            pos = free_space
            for i in range(item_count):
                positions.append(pos)
                pos += self._get_item_main_size(i) + self._get_main_gap()
                
        elif self._justify_content == JustifyContent.CENTER:
            pos = free_space // 2
            for i in range(item_count):
                positions.append(pos)
                pos += self._get_item_main_size(i) + self._get_main_gap()
                
        elif self._justify_content == JustifyContent.SPACE_BETWEEN:
            if item_count == 1:
                positions.append(0)
            else:
                gap_size = free_space // (item_count - 1)
                pos = 0
                for i in range(item_count):
                    positions.append(pos)
                    pos += self._get_item_main_size(i) + gap_size
                    
        elif self._justify_content == JustifyContent.SPACE_AROUND:
            gap_size = free_space // item_count
            pos = gap_size // 2
            for i in range(item_count):
                positions.append(pos)
                pos += self._get_item_main_size(i) + gap_size
                
        elif self._justify_content == JustifyContent.SPACE_EVENLY:
            gap_size = free_space // (item_count + 1)
            pos = gap_size
            for i in range(item_count):
                positions.append(pos)
                pos += self._get_item_main_size(i) + gap_size
                
        return positions
        
    def _align_cross_axis(self, container_rect: QRect):
        """Align items along the cross axis"""
        is_horizontal = self._flex_direction in [FlexDirection.ROW, FlexDirection.ROW_REVERSE]
        
        for line_index, line in enumerate(self._lines):
            line_height = self._calculate_line_cross_size(line, is_horizontal)
            line_y = self._calculate_line_cross_position(line_index, line_height, container_rect)
            
            for item in line:
                align = item.align_self if item.align_self else self._align_items
                
                if is_horizontal:
                    # Cross axis is vertical
                    item.target_rect.setY(line_y)
                    if align == AlignItems.STRETCH:
                        item.target_rect.setHeight(line_height)
                    elif align == AlignItems.CENTER:
                        y_offset = (line_height - item.calculated_size.height()) // 2
                        item.target_rect.setY(line_y + y_offset)
                        item.target_rect.setHeight(item.calculated_size.height())
                    elif align == AlignItems.FLEX_END:
                        y_offset = line_height - item.calculated_size.height()
                        item.target_rect.setY(line_y + y_offset)
                        item.target_rect.setHeight(item.calculated_size.height())
                    else:  # FLEX_START or BASELINE
                        item.target_rect.setY(line_y)
                        item.target_rect.setHeight(item.calculated_size.height())
                else:
                    # Cross axis is horizontal
                    item.target_rect.setX(container_rect.x())
                    if align == AlignItems.STRETCH:
                        item.target_rect.setWidth(container_rect.width())
                    elif align == AlignItems.CENTER:
                        x_offset = (container_rect.width() - item.calculated_size.width()) // 2
                        item.target_rect.setX(container_rect.x() + x_offset)
                        item.target_rect.setWidth(item.calculated_size.width())
                    elif align == AlignItems.FLEX_END:
                        x_offset = container_rect.width() - item.calculated_size.width()
                        item.target_rect.setX(container_rect.x() + x_offset)
                        item.target_rect.setWidth(item.calculated_size.width())
                    else:  # FLEX_START or BASELINE
                        item.target_rect.setX(container_rect.x())
                        item.target_rect.setWidth(item.calculated_size.width())
                        
    def _calculate_line_cross_size(self, line: List[FlexItem], is_horizontal: bool) -> int:
        """Calculate the cross size of a flex line"""
        if not line:
            return 0
            
        max_size = 0
        for item in line:
            size = (item.calculated_size.height() if is_horizontal 
                   else item.calculated_size.width())
            max_size = max(max_size, size)
            
        return max_size
        
    def _calculate_line_cross_position(self, line_index: int, line_height: int, 
                                     container_rect: QRect) -> int:
        """Calculate the cross axis position of a flex line"""
        # Simplified - just stack lines
        return container_rect.y() + line_index * (line_height + self._row_gap)
        
    def _position_widgets(self):
        """Position all widgets according to calculated rects"""
        for item in self._flex_items:
            item.widget.setGeometry(item.target_rect)
            
    def _get_item_main_size(self, index: int) -> int:
        """Get main axis size for item at index (helper method)"""
        return 100  # Simplified
        
    def _get_main_gap(self) -> int:
        """Get main axis gap (helper method)"""
        is_horizontal = self._flex_direction in [FlexDirection.ROW, FlexDirection.ROW_REVERSE]
        return self._column_gap if is_horizontal else self._row_gap
        
    # Public API
    
    def set_flex_direction(self, direction: FlexDirection):
        """Set flex direction"""
        if self._flex_direction != direction:
            self._flex_direction = direction
            self.flex_direction_changed.emit(direction)
            self.request_layout_update()
            
    def get_flex_direction(self) -> FlexDirection:
        """Get flex direction"""
        return self._flex_direction
        
    def set_flex_wrap(self, wrap: FlexWrap):
        """Set flex wrap"""
        if self._flex_wrap != wrap:
            self._flex_wrap = wrap
            self.wrap_changed.emit(wrap)
            self.request_layout_update()
            
    def get_flex_wrap(self) -> FlexWrap:
        """Get flex wrap"""
        return self._flex_wrap
        
    def set_justify_content(self, justify: JustifyContent):
        """Set justify content (main axis alignment)"""
        if self._justify_content != justify:
            self._justify_content = justify
            self.request_layout_update()
            
    def get_justify_content(self) -> JustifyContent:
        """Get justify content"""
        return self._justify_content
        
    def set_align_items(self, align: AlignItems):
        """Set align items (cross axis alignment)"""
        if self._align_items != align:
            self._align_items = align
            self.request_layout_update()
            
    def get_align_items(self) -> AlignItems:
        """Get align items"""
        return self._align_items
        
    def set_gap(self, row_gap: int, column_gap: Optional[int] = None):
        """Set gap between items"""
        if column_gap is None:
            column_gap = row_gap
            
        if self._row_gap != row_gap or self._column_gap != column_gap:
            self._row_gap = row_gap
            self._column_gap = column_gap
            self.request_layout_update()
            
    def get_gap(self) -> tuple:
        """Get gap (row_gap, column_gap)"""
        return (self._row_gap, self._column_gap)
    
    def update_item_flex(self, widget: QWidget, flex_grow: Optional[float] = None,
                        flex_shrink: Optional[float] = None, flex_basis: Optional[Union[int, str]] = None,
                        align_self: Optional[AlignItems] = None):
        """Update flex properties of an existing item"""
        for item in self._flex_items:
            if item.widget == widget:
                if flex_grow is not None:
                    item.flex_grow = max(0, flex_grow)
                if flex_shrink is not None:
                    item.flex_shrink = max(0, flex_shrink)
                if flex_basis is not None:
                    item.flex_basis = flex_basis
                if align_self is not None:
                    item.align_self = align_self
                    
                self.request_layout_update()
                break
