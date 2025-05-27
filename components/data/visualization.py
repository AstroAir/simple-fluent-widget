"""
Fluent Design Style Information Visualization Components
Components for visualizing hierarchical and relationship data
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QTransform
from core.theme import theme_manager
from typing import Optional, List
import math
import random


class FluentTreeMapItem:
    """Tree map data item representation

    Represents a single item in the tree map with a label, value, and optional children
    """

    def __init__(self, label: str, value: float, color: Optional[QColor] = None):
        self.label = label
        self.value = value
        self.color = color
        self.children = []
        self.parent = None
        self.rect = QRectF()  # Assigned by TreeMap layout algorithm

    def add_child(self, child: 'FluentTreeMapItem'):
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

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._root_item = None
        self._current_view = None  # For drill-down navigation
        self._animation_duration = 300
        self._padding = 2
        self._label_height = 20
        self._min_size_for_label = 40

        # Setup UI
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # Set minimum size
        self.setMinimumSize(200, 200)

        # Apply styling
        self._apply_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _apply_style(self):
        """Apply styles"""
        self.setStyleSheet(f"""
            FluentTreeMap {{
                background-color: {theme_manager.get_color('surface').name()};
            }}
        """)

    def _on_theme_changed(self):
        """Handle theme changes"""
        self._apply_style()
        self.update()

    def set_data(self, root_item: FluentTreeMapItem):
        """Set tree map data"""
        self._root_item = root_item
        self._current_view = root_item
        self._layout_treemap()
        self.update()

    def _layout_treemap(self):
        """Layout the tree map using squarified algorithm"""
        if not self._current_view:
            return

        # Get available size
        w = self.width()
        h = self.height()

        # Set root rectangle
        self._current_view.rect = QRectF(0, 0, w, h)

        # Process all depth levels
        self._layout_children(self._current_view)

    def _layout_children(self, item: FluentTreeMapItem):
        """Layout children of an item recursively"""
        if not item.children:
            return

        # Calculate total value of children
        total = sum(child.total_value() for child in item.children)

        # Sort children by value (descending)
        sorted_children = sorted(
            item.children, key=lambda c: c.total_value(), reverse=True)

        # Available space for children
        rect = item.rect.adjusted(
            self._padding, self._padding, -self._padding, -self._padding)

        # Use squarified treemap algorithm
        self._squarify(sorted_children, [], rect.width(),
                       rect.height(), rect.x(), rect.y(), total)

        # Recursively layout grandchildren
        for child in item.children:
            self._layout_children(child)

    def _squarify(self, children: List[FluentTreeMapItem], row: List[FluentTreeMapItem],
                  width: float, height: float, x: float, y: float, total: float):
        """Squarified treemap algorithm"""
        # Base case: no more children to process
        if not children:
            self._layout_row(row, width, height, x, y, total)
            return

        # If no current row, start with the first child
        if not row:
            row.append(children[0])
            self._squarify(children[1:], row, width, height, x, y, total)
            return

        # Calculate aspect ratio with and without adding the next child
        w = min(width, height)
        current_sum = sum(child.total_value() for child in row)
        current_max = max(child.total_value() for child in row)
        current_min = min(child.total_value() for child in row)

        current_ratio = max(
            (w * w * current_max) / (current_sum * current_sum),
            (current_sum * current_sum) / (w * w * current_min)
        )

        # Calculate new ratio with next child
        new_row = row + [children[0]]
        new_sum = current_sum + children[0].total_value()
        new_max = max(child.total_value() for child in new_row)
        new_min = min(child.total_value() for child in new_row)

        new_ratio = max(
            (w * w * new_max) / (new_sum * new_sum),
            (new_sum * new_sum) / (w * w * new_min)
        )

        # If adding the next child improves the aspect ratio, add it
        if new_ratio < current_ratio:
            self._squarify(children[1:], new_row, width, height, x, y, total)
        else:
            # Layout current row and start a new one
            area_used = self._layout_row(row, width, height, x, y, total)

            # Update available space
            if width < height:
                x += area_used
                width -= area_used
            else:
                y += area_used
                height -= area_used

            # Start a new row with the next child
            self._squarify(children, [], width, height, x, y, total)

    def _layout_row(self, row: List[FluentTreeMapItem], width: float, height: float,
                    x: float, y: float, total: float) -> float:
        """Layout a row of items and return area used"""
        if not row:
            return 0

        # Calculate area for this row
        row_sum = sum(child.total_value() for child in row)
        area_ratio = row_sum / total

        # Determine row orientation and size
        if width < height:
            # Horizontal layout
            row_width = width
            row_height = height * area_ratio

            # Layout items in the row
            item_x = x
            for child in row:
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
                item_height = (child.total_value() / row_sum) * row_height
                child.rect = QRectF(x, item_y, row_width, item_height)
                item_y += item_height

            return row_width

    def paintEvent(self, event):
        """Paint the tree map"""
        if not self._current_view:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw tree map
        self._draw_item(painter, self._current_view)

        painter.end()

    def _draw_item(self, painter: QPainter, item: FluentTreeMapItem):
        """Draw a single item and its children"""
        # Only draw children for the current view
        if item != self._current_view:
            return

        # Draw children
        for child in item.children:
            self._draw_child(painter, child)

    def _draw_child(self, painter: QPainter, item: FluentTreeMapItem):
        """Draw a child item"""
        # Skip if too small
        if item.rect.width() < 2 or item.rect.height() < 2:
            return

        # Get item color
        if item.color:
            color = item.color
        else:
            # Generate color based on depth
            hue = (item.depth() * 40) % 360
            sat = 70 + (item.depth() * 5) % 30
            val = 90 - (item.depth() * 5) % 30
            color = QColor.fromHsv(hue, sat, val)

        # Draw rectangle
        painter.setPen(QPen(theme_manager.get_color('border'), 1))
        painter.setBrush(QBrush(color))
        painter.drawRect(item.rect)

        # Draw label if enough space
        if item.rect.width() > self._min_size_for_label and item.rect.height() > self._min_size_for_label:
            label_rect = QRectF(
                item.rect.x() + 4,
                item.rect.y() + 4,
                item.rect.width() - 8,
                self._label_height
            )

            # Draw label background
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.setBrush(QColor(0, 0, 0, 100))
            painter.drawRect(label_rect)

            # Draw label text
            painter.setPen(QColor(255, 255, 255))
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignLeft |
                             Qt.AlignmentFlag.AlignVCenter, item.label)

    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        self._layout_treemap()

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if not self._current_view or not self._current_view.children:
            return

        # Find clicked item
        for child in self._current_view.children:
            if child.rect.contains(event.position().x(), event.position().y()):
                self.itemClicked.emit(child)

                # If the item has children, drill down
                if child.children:
                    self._drill_down(child)

                break

    def _drill_down(self, item: FluentTreeMapItem):
        """Drill down to show a specific item's children"""
        self._current_view = item
        self._layout_treemap()
        self.update()

    def drill_up(self):
        """Go back up one level"""
        if self._current_view and self._current_view.parent:
            self._current_view = self._current_view.parent
            self._layout_treemap()
            self.update()
            return True
        return False


class FluentNetworkNode:
    """Network graph node representation"""

    def __init__(self, id: str, label: str, size: float = 30,
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


class FluentNetworkEdge:
    """Network graph edge representation"""

    def __init__(self, source: str, target: str, weight: float = 1.0,
                 color: Optional[QColor] = None):
        self.source = source  # Source node ID
        self.target = target  # Target node ID
        self.weight = weight  # Edge weight
        self.color = color    # Edge color


class FluentNetworkGraph(QWidget):
    """Fluent Design Style Network Graph

    Features:
    - Force-directed graph layout
    - Interactive node dragging and selection
    - Zoom and pan navigation
    - Customizable node and edge appearance
    - Animated transitions
    """

    nodeSelected = Signal(str)  # Emitted when a node is selected
    nodeDoubleClicked = Signal(str)  # Emitted when a node is double-clicked

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._nodes = {}  # Dict of node ID to FluentNetworkNode
        self._edges = []  # List of FluentNetworkEdge

        self._selected_node = None
        self._dragging = False
        self._dragging_node = None
        self._drag_start = QPointF()

        self._scale = 1.0
        self._translate = QPointF(0, 0)

        # Physics parameters
        self._repulsion = 500
        self._attraction = 0.06
        self._damping = 0.9
        self._min_velocity = 0.1
        self._max_velocity = 10.0

        # Animation timer
        self._timer = QTimer(self)
        self._timer.setInterval(16)  # 60 FPS
        self._timer.timeout.connect(self._update_simulation)

        # Set focus policy to receive key events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Apply styling
        self._apply_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _apply_style(self):
        """Apply styles"""
        self.setStyleSheet(f"""
            FluentNetworkGraph {{
                background-color: {theme_manager.get_color('surface').name()};
            }}
        """)

    def _on_theme_changed(self):
        """Handle theme changes"""
        self._apply_style()
        self.update()

    def add_node(self, node: FluentNetworkNode):
        """Add a node to the graph"""
        self._nodes[node.id] = node

        # Set initial position if not already set
        if node.x == 0 and node.y == 0:
            w, h = self.width(), self.height()
            node.x = w / 2 + (random.random() * 100 - 50)
            node.y = h / 2 + (random.random() * 100 - 50)

        self.update()

    def add_edge(self, edge: FluentNetworkEdge):
        """Add an edge to the graph"""
        self._edges.append(edge)
        self.update()

    def clear(self):
        """Clear all nodes and edges"""
        self._nodes.clear()
        self._edges.clear()
        self._selected_node = None
        self.update()

    def start_simulation(self):
        """Start physics simulation"""
        self._timer.start()

    def stop_simulation(self):
        """Stop physics simulation"""
        self._timer.stop()

    def _update_simulation(self):
        """Update physics simulation"""
        # Calculate forces
        self._calculate_forces()

        # Update positions
        stable = True
        for node in self._nodes.values():
            if node.fixed:
                continue

            # Apply velocity
            node.velocity_x = (node.velocity_x + node.force_x) * self._damping
            node.velocity_y = (node.velocity_y + node.force_y) * self._damping

            # Limit velocity
            speed = math.sqrt(node.velocity_x**2 + node.velocity_y**2)
            if speed > self._max_velocity:
                node.velocity_x = (node.velocity_x / speed) * \
                    self._max_velocity
                node.velocity_y = (node.velocity_y / speed) * \
                    self._max_velocity

            # Check if still moving
            if speed > self._min_velocity:
                stable = False

            # Update position
            node.x += node.velocity_x
            node.y += node.velocity_y

            # Reset forces
            node.force_x = 0
            node.force_y = 0

        # Stop simulation if stable
        if stable and self._timer.isActive():
            self._timer.stop()

        # Redraw
        self.update()

    def _calculate_forces(self):
        """Calculate forces between nodes"""
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
        force = self._repulsion / (distance * distance)

        # Apply force
        if not node1.fixed:
            node1.force_x -= nx * force
            node1.force_y -= ny * force

        if not node2.fixed:
            node2.force_x += nx * force
            node2.force_y += ny * force

    def _apply_attraction(self, node1: FluentNetworkNode, node2: FluentNetworkNode, weight: float):
        """Apply attractive force between two connected nodes"""
        dx = node2.x - node1.x
        dy = node2.y - node1.y

        # Distance
        distance = max(1.0, math.sqrt(dx*dx + dy*dy))

        # Attractive force (like a spring)
        force = self._attraction * distance * weight

        # Apply force
        if not node1.fixed:
            node1.force_x += dx * force
            node1.force_y += dy * force

        if not node2.fixed:
            node2.force_x -= dx * force
            node2.force_y -= dy * force

    def paintEvent(self, event):
        """Paint the network graph"""
        if not self._nodes:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Apply transform
        transform = QTransform()
        transform.translate(self._translate.x(), self._translate.y())
        transform.scale(self._scale, self._scale)
        painter.setTransform(transform)

        # Draw edges first
        self._draw_edges(painter)

        # Then draw nodes
        self._draw_nodes(painter)

        painter.end()

    def _draw_edges(self, painter: QPainter):
        """Draw all edges"""
        for edge in self._edges:
            if edge.source in self._nodes and edge.target in self._nodes:
                source = self._nodes[edge.source]
                target = self._nodes[edge.target]

                # Set edge color
                if edge.color:
                    color = edge.color
                else:
                    color = theme_manager.get_color('border')

                # Set pen based on weight
                pen = QPen(color, 1 + edge.weight)
                painter.setPen(pen)

                # Draw line
                painter.drawLine(source.x, source.y, target.x, target.y)

    def _draw_nodes(self, painter: QPainter):
        """Draw all nodes"""
        for node_id, node in self._nodes.items():
            # Set node color
            if node.color:
                color = node.color
            else:
                color = theme_manager.get_color('primary')

            # Draw selection indicator if selected
            if node_id == self._selected_node:
                painter.setPen(QPen(theme_manager.get_color('primary'), 2))
                painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                painter.drawEllipse(node.x - node.size * 0.6, node.y - node.size * 0.6,
                                    node.size * 1.2, node.size * 1.2)

            # Draw node
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(node.x - node.size / 2, node.y - node.size / 2,
                                node.size, node.size)

            # Draw label
            painter.setPen(QPen(theme_manager.get_color('text_primary')))
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(node.x + node.size / 2 +
                             5, node.y + 5, node.label)

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Transform click position
            pos = self._transform_pos(event.position())

            # Check if a node was clicked
            clicked_node = self._find_node_at_pos(pos)

            if clicked_node:
                self._dragging = True
                self._dragging_node = clicked_node
                self._drag_start = QPointF(pos.x() - self._nodes[clicked_node].x,
                                           pos.y() - self._nodes[clicked_node].y)

                # Select the node
                self._selected_node = clicked_node
                self.nodeSelected.emit(clicked_node)
                self.update()
            else:
                # Start panning
                self._dragging = True
                self._dragging_node = None
                self._drag_start = event.position()

    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._dragging_node = None

    def mouseMoveEvent(self, event):
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
            else:
                # Pan the view
                delta = event.position() - self._drag_start
                self._translate += delta
                self._drag_start = event.position()
                self.update()

    def mouseDoubleClickEvent(self, event):
        """Handle mouse double click events"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self._transform_pos(event.position())
            clicked_node = self._find_node_at_pos(pos)

            if clicked_node:
                self.nodeDoubleClicked.emit(clicked_node)

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming"""
        zoom_factor = 1.2

        if event.angleDelta().y() > 0:
            # Zoom in
            self._scale *= zoom_factor
        else:
            # Zoom out
            self._scale /= zoom_factor

        # Limit scale
        self._scale = max(0.1, min(self._scale, 5.0))
        self.update()

    def _transform_pos(self, pos: QPointF) -> QPointF:
        """Transform screen coordinates to graph coordinates"""
        x = (pos.x() - self._translate.x()) / self._scale
        y = (pos.y() - self._translate.y()) / self._scale
        return QPointF(x, y)

    def _find_node_at_pos(self, pos: QPointF) -> Optional[str]:
        """Find node at position"""
        for node_id, node in self._nodes.items():
            dx = pos.x() - node.x
            dy = pos.y() - node.y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance <= node.size / 2:
                return node_id

        return None

    def reset_view(self):
        """Reset view transformation"""
        self._scale = 1.0
        center_x = self.width() / 2
        center_y = self.height() / 2

        # Calculate center of nodes
        if self._nodes:
            sum_x = sum(node.x for node in self._nodes.values())
            sum_y = sum(node.y for node in self._nodes.values())
            avg_x = sum_x / len(self._nodes)
            avg_y = sum_y / len(self._nodes)

            # Center nodes in view
            self._translate = QPointF(center_x - avg_x, center_y - avg_y)
        else:
            self._translate = QPointF(0, 0)

        self.update()
