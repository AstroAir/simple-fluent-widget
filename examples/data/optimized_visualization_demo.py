"""
Optimized Visualization Components Demo

This demo showcases the enhanced visualization components with modern Python features:
- Tree Map with multiple layout algorithms
- Network Graph with physics simulation
- Modern configuration using dataclasses
- Performance optimizations with caching
- Enhanced user interactions
"""

import sys
import random
import math
from typing import List, Dict

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QComboBox,
                               QSlider, QTabWidget, QGroupBox, QSpinBox)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor

# Import the optimized visualization components
from components.data.visualization import (
    FluentTreeMap, FluentTreeMapItem, TreeMapConfig, TreeMapLayout,
    FluentNetworkGraph, FluentNetworkNode, FluentNetworkEdge, 
    NetworkConfig, NetworkLayout
)


class OptimizedVisualizationDemo(QMainWindow):
    """Main demo window showcasing optimized visualization components"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimized Fluent Visualization Components Demo")
        self.setGeometry(100, 100, 1400, 900)

        # Setup UI
        self._setup_ui()
        
        # Load demo data
        self._setup_treemap_demo()
        self._setup_network_demo()

        # Auto-update timer for real-time demos
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_real_time_data)
        self._update_timer.start(2000)  # Update every 2 seconds

    def _setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Setup TreeMap tab
        self._setup_treemap_tab()
        
        # Setup Network Graph tab
        self._setup_network_tab()

    def _setup_treemap_tab(self):
        """Setup the TreeMap demonstration tab"""
        treemap_widget = QWidget()
        self.tab_widget.addTab(treemap_widget, "Optimized TreeMap")
        
        layout = QVBoxLayout(treemap_widget)
        
        # Controls panel
        controls_group = QGroupBox("TreeMap Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        # Layout algorithm selector
        controls_layout.addWidget(QLabel("Layout Algorithm:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["Squarified", "Slice and Dice", "Binary"])
        self.layout_combo.currentTextChanged.connect(self._on_layout_changed)
        controls_layout.addWidget(self.layout_combo)
        
        # Enable/disable features
        self.gradient_checkbox = QPushButton("Toggle Gradients")
        self.gradient_checkbox.setCheckable(True)
        self.gradient_checkbox.setChecked(True)
        self.gradient_checkbox.clicked.connect(self._toggle_gradients)
        controls_layout.addWidget(self.gradient_checkbox)
        
        self.labels_checkbox = QPushButton("Toggle Labels")
        self.labels_checkbox.setCheckable(True)
        self.labels_checkbox.setChecked(True)
        self.labels_checkbox.clicked.connect(self._toggle_labels)
        controls_layout.addWidget(self.labels_checkbox)
        
        # Data generation
        refresh_btn = QPushButton("Generate New Data")
        refresh_btn.clicked.connect(self._generate_treemap_data)
        controls_layout.addWidget(refresh_btn)
        
        drill_up_btn = QPushButton("Drill Up")
        drill_up_btn.clicked.connect(self._drill_up_treemap)
        controls_layout.addWidget(drill_up_btn)
        
        layout.addWidget(controls_group)
        
        # TreeMap widget with optimized configuration
        treemap_config = TreeMapConfig(
            padding=3,
            label_height=24,
            min_size_for_label=50,
            animation_duration=400,
            layout_algorithm=TreeMapLayout.SQUARIFIED,
            enable_drill_down=True,
            show_labels=True,
            gradient_fill=True
        )
        
        self.treemap = FluentTreeMap(config=treemap_config)
        self.treemap.itemClicked.connect(self._on_treemap_item_clicked)
        layout.addWidget(self.treemap)

    def _setup_network_tab(self):
        """Setup the Network Graph demonstration tab"""
        network_widget = QWidget()
        self.tab_widget.addTab(network_widget, "Optimized Network Graph")
        
        layout = QVBoxLayout(network_widget)
        
        # Controls panel
        controls_group = QGroupBox("Network Graph Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        # Physics controls
        controls_layout.addWidget(QLabel("Repulsion:"))
        self.repulsion_slider = QSlider(Qt.Orientation.Horizontal)
        self.repulsion_slider.setRange(100, 2000)
        self.repulsion_slider.setValue(500)
        self.repulsion_slider.valueChanged.connect(self._update_physics)
        controls_layout.addWidget(self.repulsion_slider)
        
        controls_layout.addWidget(QLabel("Attraction:"))
        self.attraction_slider = QSlider(Qt.Orientation.Horizontal)
        self.attraction_slider.setRange(1, 20)
        self.attraction_slider.setValue(6)
        self.attraction_slider.valueChanged.connect(self._update_physics)
        controls_layout.addWidget(self.attraction_slider)
        
        # Layout algorithm selector
        controls_layout.addWidget(QLabel("Layout:"))
        self.network_layout_combo = QComboBox()
        self.network_layout_combo.addItems(["Force Directed", "Circular", "Grid", "Hierarchical"])
        self.network_layout_combo.currentTextChanged.connect(self._on_network_layout_changed)
        controls_layout.addWidget(self.network_layout_combo)
        
        # Control buttons
        self.physics_btn = QPushButton("Start Physics")
        self.physics_btn.clicked.connect(self._toggle_physics)
        controls_layout.addWidget(self.physics_btn)
        
        reset_view_btn = QPushButton("Reset View")
        reset_view_btn.clicked.connect(self._reset_network_view)
        controls_layout.addWidget(reset_view_btn)
        
        add_nodes_btn = QPushButton("Add Random Nodes")
        add_nodes_btn.clicked.connect(self._add_random_nodes)
        controls_layout.addWidget(add_nodes_btn)
        
        clear_btn = QPushButton("Clear Graph")
        clear_btn.clicked.connect(self._clear_network)
        controls_layout.addWidget(clear_btn)
        
        layout.addWidget(controls_group)
        
        # Network graph with optimized configuration
        network_config = NetworkConfig(
            repulsion=500.0,
            attraction=0.06,
            damping=0.9,
            min_velocity=0.1,
            max_velocity=10.0,
            animation_fps=60,
            enable_physics=True,
            show_labels=True,
            enable_zoom=True,
            enable_pan=True,
            gradient_nodes=True
        )
        
        self.network = FluentNetworkGraph(config=network_config)
        self.network.nodeSelected.connect(self._on_node_selected)
        self.network.nodeDoubleClicked.connect(self._on_node_double_clicked)
        layout.addWidget(self.network)

    def _setup_treemap_demo(self):
        """Setup TreeMap demo data"""
        self._generate_treemap_data()

    def _generate_treemap_data(self):
        """Generate hierarchical data for TreeMap demonstration"""
        # Create root item
        root = FluentTreeMapItem("Technology Companies", 0)
        
        # Create major categories
        categories = [
            ("Software", ["Microsoft", "Adobe", "Salesforce", "Oracle"], 
             [QColor("#0078d4"), QColor("#ff4500"), QColor("#00a1f1"), QColor("#f80000")]),
            ("Hardware", ["Apple", "Samsung", "Intel", "NVIDIA"],
             [QColor("#007acc"), QColor("#1428a0"), QColor("#0071c5"), QColor("#76b900")]),
            ("Internet", ["Google", "Meta", "Amazon", "Netflix"],
             [QColor("#4285f4"), QColor("#1877f2"), QColor("#ff9900"), QColor("#e50914")]),
            ("Mobile", ["Uber", "Spotify", "Twitter", "TikTok"],
             [QColor("#000000"), QColor("#1ed760"), QColor("#1da1f2"), QColor("#fe2c55")])
        ]
        
        for category_name, companies, colors in categories:
            category_item = FluentTreeMapItem(category_name, 0)
            
            for i, company in enumerate(companies):
                # Generate realistic market cap values (in billions)
                value = random.uniform(50, 2000)
                color = colors[i] if i < len(colors) else QColor.fromHsv(random.randint(0, 360), 200, 200)
                
                company_item = FluentTreeMapItem(f"{company}\n${value:.1f}B", value, color)
                
                # Add some sub-divisions for demonstration
                if random.random() > 0.5:
                    divisions = ["R&D", "Sales", "Marketing", "Operations"]
                    for div in divisions:
                        div_value = value * random.uniform(0.1, 0.3)
                        div_item = FluentTreeMapItem(f"{div}\n${div_value:.1f}B", div_value)
                        company_item.add_child(div_item)
                
                category_item.add_child(company_item)
            
            root.add_child(category_item)
        
        self.treemap.set_data(root)

    def _setup_network_demo(self):
        """Setup Network Graph demo data"""
        self._generate_network_data()

    def _generate_network_data(self):
        """Generate network data for demonstration"""
        # Clear existing data
        self.network.clear()
        
        # Create nodes representing a social network
        node_categories = [
            ("Influencer", QColor("#ff6b6b"), 45),
            ("Content Creator", QColor("#4ecdc4"), 35),
            ("Regular User", QColor("#45b7d1"), 25),
            ("Brand", QColor("#96ceb4"), 50),
            ("Community", QColor("#ffeaa7"), 40)
        ]
        
        nodes = []
        for i in range(20):
            category, color, size = random.choice(node_categories)
            node_id = f"node_{i}"
            label = f"{category}_{i}"
            
            node = FluentNetworkNode(node_id, label, size, color)
            nodes.append(node)
            self.network.add_node(node)
        
        # Create edges with different types
        edge_types = [
            ("follows", 1.0, False),
            ("mentions", 0.5, False),
            ("collaborates", 2.0, True),
            ("shares", 0.7, False)
        ]
        
        # Generate realistic connections
        for i in range(35):
            source_idx = random.randint(0, len(nodes) - 1)
            target_idx = random.randint(0, len(nodes) - 1)
            
            if source_idx != target_idx:
                edge_type, weight, bidirectional = random.choice(edge_types)
                
                color = QColor.fromHsv(random.randint(0, 360), 100, 150)
                edge = FluentNetworkEdge(
                    nodes[source_idx].id, 
                    nodes[target_idx].id, 
                    weight, 
                    color, 
                    bidirectional
                )
                self.network.add_edge(edge)

    def _on_layout_changed(self, layout_name: str):
        """Handle TreeMap layout algorithm change"""
        layout_map = {
            "Squarified": TreeMapLayout.SQUARIFIED,
            "Slice and Dice": TreeMapLayout.SLICE_AND_DICE,
            "Binary": TreeMapLayout.BINARY
        }
        
        # Create new config with updated layout
        current_config = self.treemap._config
        new_config = TreeMapConfig(
            padding=current_config.padding,
            label_height=current_config.label_height,
            min_size_for_label=current_config.min_size_for_label,
            animation_duration=current_config.animation_duration,
            layout_algorithm=layout_map.get(layout_name, TreeMapLayout.SQUARIFIED),
            enable_drill_down=current_config.enable_drill_down,
            show_labels=current_config.show_labels,
            gradient_fill=current_config.gradient_fill
        )
        
        # Apply new configuration
        root_item = self.treemap._root_item
        self.treemap = FluentTreeMap(config=new_config)
        self.treemap.itemClicked.connect(self._on_treemap_item_clicked)
        if root_item:
            self.treemap.set_data(root_item)

    def _toggle_gradients(self):
        """Toggle gradient fills in TreeMap"""
        current_config = self.treemap._config
        new_config = TreeMapConfig(
            padding=current_config.padding,
            label_height=current_config.label_height,
            min_size_for_label=current_config.min_size_for_label,
            animation_duration=current_config.animation_duration,
            layout_algorithm=current_config.layout_algorithm,
            enable_drill_down=current_config.enable_drill_down,
            show_labels=current_config.show_labels,
            gradient_fill=not current_config.gradient_fill
        )
        
        root_item = self.treemap._root_item
        self.treemap._config = new_config
        if root_item:
            self.treemap.update()

    def _toggle_labels(self):
        """Toggle labels in TreeMap"""
        current_config = self.treemap._config
        new_config = TreeMapConfig(
            padding=current_config.padding,
            label_height=current_config.label_height,
            min_size_for_label=current_config.min_size_for_label,
            animation_duration=current_config.animation_duration,
            layout_algorithm=current_config.layout_algorithm,
            enable_drill_down=current_config.enable_drill_down,
            show_labels=not current_config.show_labels,
            gradient_fill=current_config.gradient_fill
        )
        
        root_item = self.treemap._root_item
        self.treemap._config = new_config
        if root_item:
            self.treemap.update()

    def _drill_up_treemap(self):
        """Drill up in TreeMap"""
        self.treemap.drill_up()

    def _on_treemap_item_clicked(self, item):
        """Handle TreeMap item click"""
        print(f"TreeMap item clicked: {item.label} (value: {item.value})")

    def _update_physics(self):
        """Update network physics parameters"""
        repulsion = self.repulsion_slider.value()
        attraction = self.attraction_slider.value() / 100.0  # Convert to float
        
        # Update network configuration
        new_config = NetworkConfig(
            repulsion=float(repulsion),
            attraction=attraction,
            damping=self.network._config.damping,
            min_velocity=self.network._config.min_velocity,
            max_velocity=self.network._config.max_velocity,
            animation_fps=self.network._config.animation_fps,
            enable_physics=self.network._config.enable_physics,
            show_labels=self.network._config.show_labels,
            enable_zoom=self.network._config.enable_zoom,
            enable_pan=self.network._config.enable_pan,
            gradient_nodes=self.network._config.gradient_nodes
        )
        
        self.network._config = new_config

    def _on_network_layout_changed(self, layout_name: str):
        """Handle network layout algorithm change"""
        layout_map = {
            "Force Directed": NetworkLayout.FORCE_DIRECTED,
            "Circular": NetworkLayout.CIRCULAR,
            "Grid": NetworkLayout.GRID,
            "Hierarchical": NetworkLayout.HIERARCHICAL
        }
        
        layout = layout_map.get(layout_name, NetworkLayout.FORCE_DIRECTED)
        self.network.set_layout_algorithm(layout)

    def _toggle_physics(self):
        """Toggle physics simulation"""
        if self.network._timer.isActive():
            self.network.stop_simulation()
            self.physics_btn.setText("Start Physics")
        else:
            self.network.start_simulation()
            self.physics_btn.setText("Stop Physics")

    def _reset_network_view(self):
        """Reset network view"""
        self.network.reset_view()

    def _add_random_nodes(self):
        """Add random nodes to the network"""
        for i in range(5):
            node_id = f"random_{random.randint(1000, 9999)}"
            label = f"Node_{node_id}"
            size = random.uniform(20, 60)
            color = QColor.fromHsv(random.randint(0, 360), 200, 200)
            
            node = FluentNetworkNode(node_id, label, size, color)
            self.network.add_node(node)
            
            # Connect to existing nodes
            existing_nodes = list(self.network._nodes.keys())
            if len(existing_nodes) > 1:
                target = random.choice(existing_nodes[:-1])  # Exclude the just-added node
                edge = FluentNetworkEdge(node_id, target, random.uniform(0.5, 2.0))
                self.network.add_edge(edge)

    def _clear_network(self):
        """Clear all network data"""
        self.network.clear()

    def _on_node_selected(self, node_id: str):
        """Handle network node selection"""
        print(f"Network node selected: {node_id}")

    def _on_node_double_clicked(self, node_id: str):
        """Handle network node double click"""
        print(f"Network node double-clicked: {node_id}")
        # Example: Remove the node
        self.network.remove_node(node_id)

    def _update_real_time_data(self):
        """Update visualizations with real-time data simulation"""
        # Simulate real-time updates by slightly modifying data
        if hasattr(self, 'treemap') and self.treemap._root_item:
            # Update TreeMap values
            self._update_treemap_values(self.treemap._root_item)
            self.treemap.update()

    def _update_treemap_values(self, item):
        """Recursively update TreeMap item values"""
        # Simulate market fluctuations
        if not item.children:  # Leaf node
            variation = random.uniform(0.95, 1.05)  # ±5% variation
            item.value *= variation
        
        for child in item.children:
            self._update_treemap_values(child)


def main():
    """Main function to run the optimized visualization demo"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show the demo window
    demo = OptimizedVisualizationDemo()
    demo.show()
    
    print("=== Optimized Visualization Components Demo ===")
    print("Features demonstrated:")
    print("• Modern Python 3.11+ features (dataclasses, type hints, protocols)")
    print("• Performance optimizations (caching, weak references, context managers)")
    print("• Enhanced TreeMap with multiple layout algorithms")
    print("• Network Graph with physics simulation and multiple layouts")
    print("• Interactive controls and real-time updates")
    print("• Modern Qt drawing with QPointF and QRectF")
    print("• Theme integration and responsive design")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
