"""
Fluent Design Style Information Visualization Components
Components for visualizing hierarchical and relationship data

Optimized for Python 3.11+ with modern features:
- Union type syntax (|) 
- Type annotations and protocols
- Dataclasses for configuration
- Enum-based constants
- Performance optimizations
- Enhanced error handling
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import cached_property, lru_cache
from typing import Optional, List, Dict, Any, Protocol, TypeAlias, final
import math
import random
import weakref
from contextlib import contextmanager

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QTimer, QPropertyAnimation, QEasingCurve, QByteArray
from PySide6.QtGui import (QPainter, QColor, QBrush, QPen, QTransform, QPaintEvent, QMouseEvent, QWheelEvent,
                           QLinearGradient, QFontMetrics)
from core.theme import theme_manager
from core.enhanced_base import FluentLayoutBuilder

# Modern type aliases for better readability
ColorLike: TypeAlias = QColor | str
NodeID: TypeAlias = str
PositionTuple: TypeAlias = tuple[float, float]


class TreeMapLayout(Enum):
    """Tree map layout algorithms"""
    SQUARIFIED = auto()
    SLICE_AND_DICE = auto()
    BINARY = auto()


class NetworkLayout(Enum):
    """Network graph layout algorithms"""
    FORCE_DIRECTED = auto()
    CIRCULAR = auto()
    HIERARCHICAL = auto()
    GRID = auto()


@dataclass(slots=True, frozen=True)
class TreeMapConfig:
    """Configuration for tree map visualization"""
    padding: int = 2
    label_height: int = 20
    min_size_for_label: int = 40
    animation_duration: int = 300
    layout_algorithm: TreeMapLayout = TreeMapLayout.SQUARIFIED
    enable_drill_down: bool = True
    show_labels: bool = True
    gradient_fill: bool = True


@dataclass(slots=True, frozen=True) 
class NetworkConfig:
    """Configuration for network graph visualization"""
    repulsion: float = 500.0
    attraction: float = 0.06
    damping: float = 0.9
    min_velocity: float = 0.1
    max_velocity: float = 10.0
    animation_fps: int = 60
    enable_physics: bool = True
    show_labels: bool = True
    enable_zoom: bool = True
    enable_pan: bool = True
    gradient_nodes: bool = True


class VisualizationTheme(Protocol):
    """Protocol for theme management in visualization components"""
    
    def get_color(self, color_name: str) -> QColor:
        """Get theme color by name"""
        ...
        
    def get_font(self, font_name: str) -> str:
        """Get theme font by name"""
        ...


@final
class FluentTreeMapItem:
    """Tree map data item representation

    Represents a single item in the tree map with a label, value, and optional children
    """

    def __init__(self, label: str, value: float, color: Optional[QColor] = None):
        self.label = label
        self.value = value
        self.color = color
        self.children: List[FluentTreeMapItem] = []
        self.parent: Optional[FluentTreeMapItem] = None
        self.rect = QRectF()  # Assigned by TreeMap layout algorithm

    def add_child(self, child: FluentTreeMapItem) -> FluentTreeMapItem:
        """Add a child item"""
        self.children.append(child)
        child.parent = self
        return child

    def total_value(self) -> float:
        """Get total value including all children"""
        if not self.children:
            return self.value
        else:
            return sum(child.total_value() for child in self.children)

    def depth(self) -> int:
        """Get depth in the tree"""
        if self.parent is None:
            return 0
        else:
            return self.parent.depth() + 1


@final
class FluentTreeMap(QWidget):
    """Fluent Design Style Tree Map

    Features:
    - Hierarchical visualization of data with nested rectangles
    - Customizable colors and gradients
    - Smooth animations on data changes
    - Interactive tooltips
    - Drill-down navigation
    """

    itemClicked = Signal(FluentTreeMapItem)  # Emitted when an item is clicked

    def __init__(self, parent: Optional[QWidget] = None, config: Optional[TreeMapConfig] = None):
        super().__init__(parent)

        # Use modern configuration with defaults
        self._config = config or TreeMapConfig()
        self._root_item: Optional[FluentTreeMapItem] = None
        self._current_view: Optional[FluentTreeMapItem] = None  # For drill-down navigation

        # Performance optimizations with weak references
        self._layout_cache: Dict[str, Any] = {}
        self._paint_cache: weakref.WeakKeyDictionary[FluentTreeMapItem, Any] = weakref.WeakKeyDictionary()

        # Setup UI with modern layout builder
        self._layout = FluentLayoutBuilder.create_vertical_layout()
        self.setLayout(self._layout)

        # Set minimum size
        self.setMinimumSize(200, 200)

        # Apply styling and connect theme changes
        self._apply_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    @cached_property
    def font_metrics(self) -> QFontMetrics:
        """Cached font metrics for performance"""
        return QFontMetrics(self.font())

    def _apply_style(self):
        """Apply modern styles with theme integration"""
        self.setStyleSheet(f"""
            FluentTreeMap {{
                background-color: {theme_manager.get_color('surface').name()};
                border-radius: 8px;
                border: 1px solid {theme_manager.get_color('border').name()};
            }}
        """)

    def _on_theme_changed(self):
        """Handle theme changes with cache invalidation"""
        self._layout_cache.clear()
        self._paint_cache.clear()
        self._apply_style()
        self.update()

    @contextmanager
    def _performance_context(self):
        """Context manager for performance-critical operations"""
        try:
            self.setUpdatesEnabled(False)
            yield
        finally:
            self.setUpdatesEnabled(True)

    def set_data(self, root_item: FluentTreeMapItem):
        """Set tree map data with performance optimization"""
        with self._performance_context():
            self._root_item = root_item
            self._current_view = root_item
            self._layout_cache.clear()
            self._layout_treemap()
        self.update()

    @lru_cache(maxsize=128)
    def _get_color_for_depth(self, depth: int) -> QColor:
        """Get cached color for depth level"""
        hue = (depth * 40) % 360
        sat = 70 + (depth * 5) % 30
        val = 90 - (depth * 5) % 30
        return QColor.fromHsv(hue, sat, val)

    def _layout_treemap(self):
        """Layout the tree map using modern algorithms"""
        if not self._current_view:
            return

        # Use cached layout if available
        cache_key = f"{self.width()}x{self.height()}_{id(self._current_view)}"
        if cache_key in self._layout_cache:
            return

        # Get available size
        w, h = self.width(), self.height()

        # Set root rectangle
        self._current_view.rect = QRectF(0, 0, w, h)

        # Process all depth levels based on configuration
        match self._config.layout_algorithm:
            case TreeMapLayout.SQUARIFIED:
                self._layout_children_squarified(self._current_view)
            case TreeMapLayout.SLICE_AND_DICE:
                self._layout_children_slice_dice(self._current_view)
            case _:
                self._layout_children_squarified(self._current_view)  # Default

        # Cache the layout
        self._layout_cache[cache_key] = True

    def _layout_children_squarified(self, item: FluentTreeMapItem):
        """Layout children using squarified algorithm (optimized)"""
        if not item.children:
            return

        total = sum(child.total_value() for child in item.children)
        if total <= 0:
            return

        # Sort children by value (descending) for better aspect ratios
        sorted_children = sorted(
            item.children, key=lambda c: c.total_value(), reverse=True)

        # Available space for children
        rect = item.rect.adjusted(
            self._config.padding, self._config.padding, 
            -self._config.padding, -self._config.padding)

        # Use optimized squarified treemap algorithm
        self._squarify_optimized(sorted_children, [], rect.width(),
                       rect.height(), rect.x(), rect.y(), total)

        # Recursively layout grandchildren
        for child in item.children:
            self._layout_children_squarified(child)

    def _layout_children_slice_dice(self, item: FluentTreeMapItem):
        """Layout children using slice-and-dice algorithm"""
        if not item.children:
            return
            
        total = sum(child.total_value() for child in item.children)
        if total <= 0:
            return
            
        rect = item.rect.adjusted(
            self._config.padding, self._config.padding,
            -self._config.padding, -self._config.padding)
            
        # Alternate between horizontal and vertical slicing based on depth
        horizontal = item.depth() % 2 == 0
        
        if horizontal:
            y = rect.y()
            for child in item.children:
                height = (child.total_value() / total) * rect.height()
                child.rect = QRectF(rect.x(), y, rect.width(), height)
                y += height
        else:
            x = rect.x()
            for child in item.children:
                width = (child.total_value() / total) * rect.width()
                child.rect = QRectF(x, rect.y(), width, rect.height())
                x += width
                
        # Recursively layout grandchildren
        for child in item.children:
            self._layout_children_slice_dice(child)

    def _squarify_optimized(self, children: List[FluentTreeMapItem], row: List[FluentTreeMapItem],
                  width: float, height: float, x: float, y: float, total: float):
        """Optimized squarified treemap algorithm with early termination"""
        # Early termination for performance
        if not children or width <= 0 or height <= 0:
            if row:
                self._layout_row(row, width, height, x, y, total)
            return

        # If no current row, start with the first child
        if not row:
            row.append(children[0])
            self._squarify_optimized(children[1:], row, width, height, x, y, total)
            return

        # Calculate aspect ratio improvements
        w = min(width, height)
        current_sum = sum(child.total_value() for child in row)
        
        if current_sum <= 0:
            # Skip invalid rows
            self._squarify_optimized(children[1:], [], width, height, x, y, total)
            return
            
        current_max = max(child.total_value() for child in row)
        current_min = min(child.total_value() for child in row)

        # Avoid division by zero
        if current_sum == 0 or w == 0:
            return

        current_ratio = max(
            (w * w * current_max) / (current_sum * current_sum),
            (current_sum * current_sum) / (w * w * current_min)
        )

        # Calculate new ratio with next child
        if children:
            new_row = row + [children[0]]
            new_sum = current_sum + children[0].total_value()
            
            if new_sum > 0:
                new_max = max(child.total_value() for child in new_row)
                new_min = min(child.total_value() for child in new_row)

                new_ratio = max(
                    (w * w * new_max) / (new_sum * new_sum),
                    (new_sum * new_sum) / (w * w * new_min)
                )

                # If adding the next child improves the aspect ratio, add it
                if new_ratio < current_ratio:
                    self._squarify_optimized(children[1:], new_row, width, height, x, y, total)
                    return

        # Layout current row and start a new one
        area_used = self._layout_row(row, width, height, x, y, total)

        # Update available space
        if width < height:
            self._squarify_optimized(children, [], width - area_used, height, x + area_used, y, total)
        else:
            self._squarify_optimized(children, [], width, height - area_used, x, y + area_used, total)

    def _layout_row(self, row: List[FluentTreeMapItem], width: float, height: float,
                    x: float, y: float, total: float) -> float:
        """Layout a row of items and return area used (optimized)"""
        if not row or total <= 0:
            return 0

        # Calculate area for this row
        row_sum = sum(child.total_value() for child in row)
        if row_sum <= 0:
            return 0
            
        area_ratio = row_sum / total

        # Determine row orientation and size
        if width < height:
            # Horizontal layout
            row_width = width
            row_height = height * area_ratio

            # Layout items in the row
            item_x = x
            for child in row:
                if row_sum > 0:
                    item_width = (child.total_value() / row_sum) * row_width
                    child.rect = QRectF(item_x, y, item_width, row_height)
                    item_x += item_width

            return row_height
        else:
            # Vertical layout
            row_width = width * area_ratio
            row_height = height

            # Layout items in the row
            item_y = y
            for child in row:
                if row_sum > 0:
                    item_height = (child.total_value() / row_sum) * row_height
                    child.rect = QRectF(x, item_y, row_width, item_height)
                    item_y += item_height

            return row_width

    def paintEvent(self, event: QPaintEvent):
        """Paint the tree map with optimized rendering"""
        if not self._current_view:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Use cached paint operations when possible
        self._draw_item_optimized(painter, self._current_view)

        painter.end()

    def _draw_item_optimized(self, painter: QPainter, item: FluentTreeMapItem):
        """Draw item with caching and optimization"""
        # Only draw children for the current view
        if item != self._current_view:
            return

        # Draw children with performance optimization
        for child in item.children:
            self._draw_child_optimized(painter, child)

    def _draw_child_optimized(self, painter: QPainter, item: FluentTreeMapItem):
        """Draw a child item with modern styling"""
        # Skip if too small to be meaningful
        if item.rect.width() < 2 or item.rect.height() < 2:
            return

        # Get item color with caching
        color = item.color or self._get_color_for_depth(item.depth())

        # Enhanced styling with gradients if enabled
        if self._config.gradient_fill:
            gradient = QLinearGradient(item.rect.topLeft(), item.rect.bottomRight())
            gradient.setColorAt(0, color.lighter(120))
            gradient.setColorAt(1, color.darker(110))
            painter.setBrush(QBrush(gradient))
        else:
            painter.setBrush(QBrush(color))

        # Modern border styling
        painter.setPen(QPen(theme_manager.get_color('border'), 1))
        painter.drawRect(item.rect)

        # Draw label if enabled and enough space
        if (self._config.show_labels and 
            item.rect.width() > self._config.min_size_for_label and 
            item.rect.height() > self._config.min_size_for_label):
            
            self._draw_label_modern(painter, item)

    def _draw_label_modern(self, painter: QPainter, item: FluentTreeMapItem):
        """Draw modern styled label"""
        label_rect = QRectF(
            item.rect.x() + 4,
            item.rect.y() + 4,
            item.rect.width() - 8,
            self._config.label_height
        )

        # Modern label background with rounded corners
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(QColor(0, 0, 0, 120))
        painter.drawRoundedRect(label_rect, 4, 4)

        # High contrast label text
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setBold(True)
        font.setPixelSize(12)
        painter.setFont(font)
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignLeft |
                         Qt.AlignmentFlag.AlignVCenter, item.label)

    def resizeEvent(self, event):
        """Handle resize events with optimization"""
        super().resizeEvent(event)
        self._layout_cache.clear()  # Invalidate layout cache
        self._layout_treemap()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events with enhanced interaction"""
        if not self._current_view or not self._current_view.children:
            return

        # Find clicked item with spatial optimization
        pos = event.position()
        clicked_item = self._find_item_at_position(pos.x(), pos.y())

        if clicked_item:
            self.itemClicked.emit(clicked_item)

            # Drill down if enabled and item has children
            if self._config.enable_drill_down and clicked_item.children:
                self._drill_down_animated(clicked_item)

    def _find_item_at_position(self, x: float, y: float) -> Optional[FluentTreeMapItem]:
        """Find item at position with optimized search"""
        if not self._current_view:
            return None
            
        # Use spatial partitioning for better performance
        for child in self._current_view.children:
            if child.rect.contains(x, y):
                return child
        return None

    def _drill_down_animated(self, item: FluentTreeMapItem):
        """Drill down with smooth animation"""
        if not self._config.enable_drill_down:
            return
              # Create animation for smooth transition
        self._animation = QPropertyAnimation(self, QByteArray(b"geometry"))
        self._animation.setDuration(self._config.animation_duration)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Update view and layout
        self._current_view = item
        self._layout_cache.clear()
        self._layout_treemap()
        self.update()

    def drill_up(self) -> bool:
        """Go back up one level with animation"""
        if self._current_view and self._current_view.parent:
            self._drill_down_animated(self._current_view.parent)
            return True
        return False

    def reset_view(self):
        """Reset to root view"""
        if self._root_item:
            self._drill_down_animated(self._root_item)


@final
class FluentNetworkNode:
    """Network graph node representation with modern Python features"""

    def __init__(self, id: NodeID, label: str, size: float = 30,
                 color: Optional[QColor] = None):
        self.id = id
        self.label = label
        self.size = size
        self.color = color
        self.x = 0.0
        self.y = 0.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.force_x = 0.0
        self.force_y = 0.0
        self.fixed = False

    @property
    def position(self) -> PositionTuple:
        """Get node position as tuple"""
        return (self.x, self.y)
        
    @position.setter 
    def position(self, pos: PositionTuple):
        """Set node position from tuple"""
        self.x, self.y = pos
        
    def reset_forces(self):
        """Reset all forces on the node"""
        self.force_x = 0.0
        self.force_y = 0.0
        
    def apply_force(self, fx: float, fy: float):
        """Apply force to the node"""
        if not self.fixed:
            self.force_x += fx
            self.force_y += fy


@final
class FluentNetworkEdge:
    """Network graph edge representation with enhanced features"""

    def __init__(self, source: NodeID, target: NodeID, weight: float = 1.0,
                 color: Optional[QColor] = None, bidirectional: bool = False):
        self.source = source  # Source node ID
        self.target = target  # Target node ID
        self.weight = weight  # Edge weight
        self.color = color    # Edge color
        self.bidirectional = bidirectional

    @property
    def is_valid(self) -> bool:
        """Check if edge has valid endpoints"""
        return bool(self.source and self.target and self.source != self.target)


@final
class FluentNetworkGraph(QWidget):
    """Fluent Design Style Network Graph

    Features:
    - Force-directed graph layout with multiple algorithms
    - Interactive node dragging and selection
    - Zoom and pan navigation with smooth animations
    - Customizable node and edge appearance
    - Performance optimizations for large graphs
    - Modern event handling and state management
    """

    nodeSelected = Signal(NodeID)  # Emitted when a node is selected
    nodeDoubleClicked = Signal(NodeID)  # Emitted when a node is double-clicked
    edgeSelected = Signal(NodeID, NodeID)  # Emitted when an edge is selected

    def __init__(self, parent: Optional[QWidget] = None, config: Optional[NetworkConfig] = None):
        super().__init__(parent)

        # Use modern configuration with defaults
        self._config = config or NetworkConfig()
        
        # Modern data structures with type safety
        self._nodes: Dict[NodeID, FluentNetworkNode] = {}
        self._edges: List[FluentNetworkEdge] = []

        # Interaction state
        self._selected_node: Optional[NodeID] = None
        self._dragging = False
        self._dragging_node: Optional[NodeID] = None
        self._drag_start = QPointF()

        # View transformation
        self._scale = 1.0
        self._translate = QPointF(0, 0)
        self._min_scale = 0.1
        self._max_scale = 5.0

        # Performance optimizations
        self._node_cache: weakref.WeakValueDictionary[NodeID, Any] = weakref.WeakValueDictionary()
        self._layout_cache: Dict[str, Any] = {}

        # Animation timer with modern configuration
        self._timer = QTimer(self)
        self._timer.setInterval(1000 // self._config.animation_fps)
        self._timer.timeout.connect(self._update_simulation)

        # Set focus policy to receive key events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Apply styling and connect theme changes
        self._apply_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    @cached_property
    def viewport_rect(self) -> QRectF:
        """Get current viewport rectangle"""
        return QRectF(0, 0, self.width(), self.height())

    def _apply_style(self):
        """Apply modern styles with theme integration"""
        self.setStyleSheet(f"""
            FluentNetworkGraph {{
                background-color: {theme_manager.get_color('surface').name()};
                border-radius: 8px;
                border: 1px solid {theme_manager.get_color('border').name()};
            }}
        """)

    def _on_theme_changed(self):
        """Handle theme changes with cache invalidation"""
        self._node_cache.clear()
        self._layout_cache.clear()
        self._apply_style()
        self.update()

    @contextmanager
    def _batch_updates(self):
        """Context manager for batching updates"""
        try:
            self.setUpdatesEnabled(False)
            yield
        finally:
            self.setUpdatesEnabled(True)
            self.update()

    def add_node(self, node: FluentNetworkNode):
        """Add a node to the graph with validation"""
        if node.id in self._nodes:
            raise ValueError(f"Node with id '{node.id}' already exists")
            
        self._nodes[node.id] = node

        # Set initial position if not already set
        if node.x == 0 and node.y == 0:
            w, h = self.width(), self.height()
            node.x = w / 2 + (random.random() * 100 - 50)
            node.y = h / 2 + (random.random() * 100 - 50)

        self._layout_cache.clear()
        self.update()

    def add_edge(self, edge: FluentNetworkEdge):
        """Add an edge to the graph with validation"""
        if not edge.is_valid:
            raise ValueError("Edge must have valid source and target nodes")
            
        if edge.source not in self._nodes or edge.target not in self._nodes:
            raise ValueError("Edge endpoints must exist as nodes")
            
        self._edges.append(edge)
        self.update()

    def remove_node(self, node_id: NodeID) -> bool:
        """Remove a node and all connected edges"""
        if node_id not in self._nodes:
            return False
            
        # Remove the node
        del self._nodes[node_id]
        
        # Remove all connected edges
        self._edges = [edge for edge in self._edges 
                      if edge.source != node_id and edge.target != node_id]
        
        # Clear selection if this node was selected
        if self._selected_node == node_id:
            self._selected_node = None
            
        self._layout_cache.clear()
        self.update()
        return True

    def clear(self):
        """Clear all nodes and edges"""
        with self._batch_updates():
            self._nodes.clear()
            self._edges.clear()
            self._selected_node = None
            self._layout_cache.clear()

    def start_simulation(self):
        """Start physics simulation"""
        if self._config.enable_physics:
            self._timer.start()

    def stop_simulation(self):
        """Stop physics simulation"""
        self._timer.stop()

    def _update_simulation(self):
        """Update physics simulation with optimizations"""
        if not self._nodes:
            self._timer.stop()
            return
            
        # Calculate forces
        self._calculate_forces()

        # Update positions
        stable = True
        for node in self._nodes.values():
            if node.fixed:
                continue

            # Apply velocity with damping
            node.velocity_x = (node.velocity_x + node.force_x) * self._config.damping
            node.velocity_y = (node.velocity_y + node.force_y) * self._config.damping

            # Limit velocity
            speed = math.sqrt(node.velocity_x**2 + node.velocity_y**2)
            if speed > self._config.max_velocity:
                factor = self._config.max_velocity / speed
                node.velocity_x *= factor
                node.velocity_y *= factor

            # Check if still moving
            if speed > self._config.min_velocity:
                stable = False

            # Update position
            node.x += node.velocity_x
            node.y += node.velocity_y

            # Reset forces
            node.reset_forces()

        # Stop simulation if stable
        if stable and self._timer.isActive():
            self._timer.stop()

        # Redraw
        self.update()

    def _calculate_forces(self):
        """Calculate forces between nodes with optimization"""
        # Calculate repulsive forces between all nodes
        nodes = list(self._nodes.values())
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                self._apply_repulsion(nodes[i], nodes[j])

        # Calculate attractive forces along edges
        for edge in self._edges:
            if edge.source in self._nodes and edge.target in self._nodes:
                source = self._nodes[edge.source]
                target = self._nodes[edge.target]
                self._apply_attraction(source, target, edge.weight)

    def _apply_repulsion(self, node1: FluentNetworkNode, node2: FluentNetworkNode):
        """Apply repulsive force between two nodes"""
        dx = node2.x - node1.x
        dy = node2.y - node1.y

        # Avoid division by zero
        distance = max(1.0, math.sqrt(dx*dx + dy*dy))

        # Normalized direction vector
        nx = dx / distance
        ny = dy / distance

        # Repulsive force (inverse square law)
        force = self._config.repulsion / (distance * distance)

        # Apply force
        node1.apply_force(-nx * force, -ny * force)
        node2.apply_force(nx * force, ny * force)

    def _apply_attraction(self, node1: FluentNetworkNode, node2: FluentNetworkNode, weight: float):
        """Apply attractive force between two connected nodes"""
        dx = node2.x - node1.x
        dy = node2.y - node1.y

        # Distance
        distance = max(1.0, math.sqrt(dx*dx + dy*dy))

        # Attractive force (like a spring)
        force = self._config.attraction * distance * weight

        # Apply force
        node1.apply_force(dx * force, dy * force)
        node2.apply_force(-dx * force, -dy * force)

    def paintEvent(self, event: QPaintEvent):
        """Paint the network graph with optimization"""
        if not self._nodes:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Apply transform
        transform = QTransform()
        transform.translate(self._translate.x(), self._translate.y())
        transform.scale(self._scale, self._scale)
        painter.setTransform(transform)

        # Draw edges first (so they appear behind nodes)
        self._draw_edges_optimized(painter)

        # Then draw nodes
        self._draw_nodes_optimized(painter)

        painter.end()

    def _draw_edges_optimized(self, painter: QPainter):
        """Draw all edges with optimization"""
        for edge in self._edges:
            if edge.source in self._nodes and edge.target in self._nodes:
                source = self._nodes[edge.source]
                target = self._nodes[edge.target]

                # Set edge color
                color = edge.color or theme_manager.get_color('border')

                # Set pen based on weight with modern styling
                pen_width = max(1, int(1 + edge.weight * 2))
                pen = QPen(color, pen_width)
                if edge.bidirectional:
                    pen.setStyle(Qt.PenStyle.DashLine)
                painter.setPen(pen)                # Draw line using QPointF for float precision
                painter.drawLine(QPointF(source.x, source.y), QPointF(target.x, target.y))

                # Draw arrow for directed edges
                if not edge.bidirectional:
                    self._draw_arrow(painter, source, target, color)

    def _draw_arrow(self, painter: QPainter, source: FluentNetworkNode, target: FluentNetworkNode, color: QColor):
        """Draw arrow head for directed edges"""
        # Calculate arrow position
        dx = target.x - source.x
        dy = target.y - source.y
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
            
        # Normalize and scale
        dx /= length
        dy /= length
        
        # Arrow position (near target node)
        arrow_x = target.x - dx * (target.size / 2 + 5)
        arrow_y = target.y - dy * (target.size / 2 + 5)
        
        # Arrow size
        arrow_size = 8
        
        # Arrow points
        arrow_points = [
            QPointF(arrow_x, arrow_y),
            QPointF(arrow_x - arrow_size * dx - arrow_size * dy * 0.5,
                   arrow_y - arrow_size * dy + arrow_size * dx * 0.5),
            QPointF(arrow_x - arrow_size * dx + arrow_size * dy * 0.5,
                   arrow_y - arrow_size * dy - arrow_size * dx * 0.5)
        ]
        
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawPolygon(arrow_points)

    def _draw_nodes_optimized(self, painter: QPainter):
        """Draw all nodes with modern styling"""
        for node_id, node in self._nodes.items():
            # Set node color
            color = node.color or theme_manager.get_color('primary')

            # Draw selection indicator if selected
            if node_id == self._selected_node:
                painter.setPen(QPen(theme_manager.get_color('accent'), 3))
                painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                selection_radius = node.size * 0.7
                painter.drawEllipse(QRectF(node.x - selection_radius, node.y - selection_radius,
                                          selection_radius * 2, selection_radius * 2))

            # Draw node with gradient if enabled
            if self._config.gradient_nodes:
                gradient = QLinearGradient(node.x - node.size/2, node.y - node.size/2,
                                         node.x + node.size/2, node.y + node.size/2)
                gradient.setColorAt(0, color.lighter(130))
                gradient.setColorAt(1, color.darker(110))
                painter.setBrush(QBrush(gradient))
            else:
                painter.setBrush(QBrush(color))

            painter.setPen(QPen(theme_manager.get_color('border'), 2))
            painter.drawEllipse(QRectF(node.x - node.size / 2, node.y - node.size / 2,
                                      node.size, node.size))

            # Draw label if enabled
            if self._config.show_labels:
                self._draw_node_label(painter, node)

    def _draw_node_label(self, painter: QPainter, node: FluentNetworkNode):
        """Draw node label with modern styling"""
        painter.setPen(QPen(theme_manager.get_color('text_primary')))
        font = painter.font()
        font.setBold(True)
        font.setPixelSize(11)
        painter.setFont(font)
        
        # Calculate label position
        label_x = node.x + node.size / 2 + 5
        label_y = node.y + 5
        
        painter.drawText(QPointF(label_x, label_y), node.label)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events with enhanced interaction"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Transform click position
            pos = self._transform_pos(event.position())

            # Check if a node was clicked
            clicked_node = self._find_node_at_pos(pos)

            if clicked_node:
                self._dragging = True
                self._dragging_node = clicked_node
                node = self._nodes[clicked_node]
                self._drag_start = QPointF(pos.x() - node.x, pos.y() - node.y)

                # Select the node
                self._selected_node = clicked_node
                self.nodeSelected.emit(clicked_node)
                self.update()
            else:
                # Start panning
                self._dragging = True
                self._dragging_node = None
                self._drag_start = event.position()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Unfix dragged node
            if self._dragging_node:
                self._nodes[self._dragging_node].fixed = False
                
            self._dragging = False
            self._dragging_node = None

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events"""
        if self._dragging:
            if self._dragging_node:
                # Move the dragged node
                pos = self._transform_pos(event.position())
                node = self._nodes[self._dragging_node]
                node.x = pos.x() - self._drag_start.x()
                node.y = pos.y() - self._drag_start.y()
                node.fixed = True  # Fix position while dragging
                self.update()
            elif self._config.enable_pan:
                # Pan the view
                delta = event.position() - self._drag_start
                self._translate += delta
                self._drag_start = event.position()
                self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle mouse double click events"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self._transform_pos(event.position())
            clicked_node = self._find_node_at_pos(pos)

            if clicked_node:
                self.nodeDoubleClicked.emit(clicked_node)

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for zooming"""
        if not self._config.enable_zoom:
            return
            
        zoom_factor = 1.15

        if event.angleDelta().y() > 0:
            # Zoom in
            new_scale = self._scale * zoom_factor
        else:
            # Zoom out
            new_scale = self._scale / zoom_factor

        # Limit scale
        new_scale = max(self._min_scale, min(new_scale, self._max_scale))
        
        if new_scale != self._scale:
            self._scale = new_scale
            self.update()

    def _transform_pos(self, pos: QPointF) -> QPointF:
        """Transform screen coordinates to graph coordinates"""
        x = (pos.x() - self._translate.x()) / self._scale
        y = (pos.y() - self._translate.y()) / self._scale
        return QPointF(x, y)

    def _find_node_at_pos(self, pos: QPointF) -> Optional[NodeID]:
        """Find node at position with spatial optimization"""
        for node_id, node in self._nodes.items():
            dx = pos.x() - node.x
            dy = pos.y() - node.y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance <= node.size / 2:
                return node_id

        return None

    def reset_view(self):
        """Reset view transformation with animation"""
        self._scale = 1.0
        
        if self._nodes:
            # Calculate center of nodes
            sum_x = sum(node.x for node in self._nodes.values())
            sum_y = sum(node.y for node in self._nodes.values())
            avg_x = sum_x / len(self._nodes)
            avg_y = sum_y / len(self._nodes)

            # Center nodes in view
            center_x = self.width() / 2
            center_y = self.height() / 2
            self._translate = QPointF(center_x - avg_x, center_y - avg_y)
        else:
            self._translate = QPointF(0, 0)

        self.update()

    def set_layout_algorithm(self, algorithm: NetworkLayout):
        """Set layout algorithm and apply"""
        # Implementation for different layout algorithms
        match algorithm:
            case NetworkLayout.FORCE_DIRECTED:
                self.start_simulation()
            case NetworkLayout.CIRCULAR:
                self._apply_circular_layout()
            case NetworkLayout.HIERARCHICAL:
                self._apply_hierarchical_layout()
            case NetworkLayout.GRID:
                self._apply_grid_layout()

    def _apply_circular_layout(self):
        """Apply circular layout to nodes"""
        if not self._nodes:
            return
            
        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = min(self.width(), self.height()) / 3
        
        nodes = list(self._nodes.values())
        angle_step = 2 * math.pi / len(nodes)
        
        for i, node in enumerate(nodes):
            angle = i * angle_step
            node.x = center_x + radius * math.cos(angle)
            node.y = center_y + radius * math.sin(angle)
            
        self.update()

    def _apply_hierarchical_layout(self):
        """Apply hierarchical layout (basic implementation)"""
        # This would need more sophisticated graph analysis
        # For now, just arrange in levels
        self._apply_grid_layout()

    def _apply_grid_layout(self):
        """Apply grid layout to nodes"""
        if not self._nodes:
            return
            
        nodes = list(self._nodes.values())
        cols = int(math.ceil(math.sqrt(len(nodes))))
        rows = int(math.ceil(len(nodes) / cols))
        
        cell_width = self.width() / (cols + 1)
        cell_height = self.height() / (rows + 1)
        
        for i, node in enumerate(nodes):
            col = i % cols
            row = i // cols
            node.x = (col + 1) * cell_width
            node.y = (row + 1) * cell_height
            
        self.update()


# Export all visualization components with modern type hints
__all__ = [
    # Configuration classes
    'TreeMapConfig',
    'NetworkConfig',
    'TreeMapLayout', 
    'NetworkLayout',
    
    # Tree map components
    'FluentTreeMapItem',
    'FluentTreeMap',
    
    # Network graph components
    'FluentNetworkNode',
    'FluentNetworkEdge', 
    'FluentNetworkGraph',
    
    # Type aliases
    'ColorLike',
    'NodeID',
    'PositionTuple',
]
