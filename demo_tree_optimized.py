"""
Demo for Optimized Fluent Design Tree Components
Showcases modern Python features and enhanced PySide6 capabilities
"""

import sys
import time
from typing import List
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QIcon

from components.data.tree import (
    FluentTreeWidget, FluentHierarchicalView, FluentOrgChart,
    TreeItemData, NodeData, TreeConfiguration, TreeState
)
from core.theme import theme_manager


class OptimizedTreeDemo(QMainWindow):
    """Demo application for optimized tree components"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimized Fluent Tree Components Demo")
        self.setGeometry(100, 100, 1400, 900)

        # Setup central widget with tabs
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)

        self._setup_demos()
        self._apply_theme()

    def _setup_demos(self):
        """Setup all demo tabs"""
        # Tab 1: Enhanced Tree Widget
        tree_demo = self._create_tree_widget_demo()
        self.central_widget.addTab(tree_demo, "🌳 Enhanced Tree Widget")

        # Tab 2: Hierarchical View
        hierarchical_demo = self._create_hierarchical_view_demo()
        self.central_widget.addTab(hierarchical_demo, "📊 Hierarchical Data View")

        # Tab 3: Organization Chart
        org_chart_demo = self._create_org_chart_demo()
        self.central_widget.addTab(org_chart_demo, "🏢 Organization Chart")

        # Tab 4: Performance Comparison
        performance_demo = self._create_performance_demo()
        self.central_widget.addTab(performance_demo, "⚡ Performance Features")

    def _create_tree_widget_demo(self) -> QWidget:
        """Create enhanced tree widget demo"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Configuration for enhanced features
        config = TreeConfiguration(
            expand_on_click=True,
            show_icons=True,
            alternating_colors=True,
            checkable_items=True,
            drag_drop_enabled=True,
            animation_duration=300,
            search_debounce=250,
            lazy_loading=True
        )

        # Create tree with configuration
        tree = FluentTreeWidget(config=config)
        tree.setHeaderLabels(["Name", "Type", "Size", "Modified"])

        # Add sample data with type safety
        self._populate_sample_tree_data(tree)

        # Control buttons
        controls = self._create_tree_controls(tree)

        layout.addWidget(controls)
        layout.addWidget(tree)

        # Connect signals for demonstration
        tree.item_clicked_signal.connect(
            lambda item, col: print(f"Clicked: {item.text(0)} (Column {col})"))
        tree.state_changed.connect(
            lambda state: print(f"State changed to: {state.name}"))

        return widget

    def _create_hierarchical_view_demo(self) -> QWidget:
        """Create hierarchical view demo"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Create hierarchical view with enhanced configuration
        config = TreeConfiguration(
            search_debounce=200,
            max_visible_items=500,
            animation_duration=250
        )

        hierarchical_view = FluentHierarchicalView(config=config)

        # Add filters
        hierarchical_view.addFilter("Type", ["Document", "Folder", "Image", "Video"])
        hierarchical_view.addFilter("Status", ["Active", "Archived", "Draft"])

        # Populate with sample hierarchical data
        sample_data = self._create_sample_hierarchical_data()
        hierarchical_view.setData(sample_data)

        # Connect signals
        hierarchical_view.item_selected.connect(
            lambda data: print(f"Selected: {data.get('text', 'Unknown')}"))
        hierarchical_view.search_performed.connect(
            lambda term: print(f"Search performed: '{term}'"))

        layout.addWidget(hierarchical_view)
        return widget

    def _create_org_chart_demo(self) -> QWidget:
        """Create organization chart demo"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Create organization chart
        org_chart = FluentOrgChart()

        # Add sample organizational data
        self._populate_org_chart_data(org_chart)

        # Control buttons for org chart
        controls = self._create_org_chart_controls(org_chart)

        layout.addWidget(controls)
        layout.addWidget(org_chart)

        # Connect signals
        org_chart.node_clicked.connect(
            lambda data: print(f"Node clicked: {data.get('title', 'Unknown')}"))
        org_chart.layout_changed.connect(
            lambda: print("Organization chart layout updated"))

        return widget

    def _create_performance_demo(self) -> QWidget:
        """Create performance comparison demo"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Performance metrics display
        metrics_widget = QWidget()
        metrics_layout = QVBoxLayout(metrics_widget)

        # Create performance test buttons
        perf_controls = QHBoxLayout()

        load_1k_btn = QPushButton("Load 1K Items")
        load_5k_btn = QPushButton("Load 5K Items")
        load_10k_btn = QPushButton("Load 10K Items")
        clear_btn = QPushButton("Clear All")

        perf_controls.addWidget(load_1k_btn)
        perf_controls.addWidget(load_5k_btn)
        perf_controls.addWidget(load_10k_btn)
        perf_controls.addWidget(clear_btn)
        perf_controls.addStretch()

        # Tree for performance testing
        perf_config = TreeConfiguration(
            lazy_loading=True,
            animation_duration=150,  # Faster for performance
            search_debounce=100,
            max_visible_items=1000
        )

        perf_tree = FluentTreeWidget(config=perf_config)
        perf_tree.setHeaderLabels(["Item", "Type", "Index"])

        # Connect performance test buttons
        load_1k_btn.clicked.connect(lambda: self._load_performance_data(perf_tree, 1000))
        load_5k_btn.clicked.connect(lambda: self._load_performance_data(perf_tree, 5000))
        load_10k_btn.clicked.connect(lambda: self._load_performance_data(perf_tree, 10000))
        clear_btn.clicked.connect(perf_tree.clear)

        layout.addLayout(perf_controls)
        layout.addWidget(perf_tree)

        return widget

    def _populate_sample_tree_data(self, tree: FluentTreeWidget):
        """Populate tree with sample data using type-safe structures"""
        # Root folders
        documents_data: TreeItemData = {
            'text': 'Documents',
            'item_type': 'folder',
            'status': 'active',
            'metadata': {'size': '2.5 GB', 'items': 156},
            'children': [
                {
                    'text': 'Projects',
                    'item_type': 'folder',
                    'status': 'active',
                    'children': [
                        {'text': 'Project Alpha.docx', 'item_type': 'document', 'status': 'active'},
                        {'text': 'Project Beta.pdf', 'item_type': 'document', 'status': 'draft'},
                    ]
                },
                {
                    'text': 'Reports',
                    'item_type': 'folder',
                    'status': 'active',
                    'children': [
                        {'text': 'Q1 Report.xlsx', 'item_type': 'spreadsheet', 'status': 'active'},
                        {'text': 'Q2 Report.xlsx', 'item_type': 'spreadsheet', 'status': 'draft'},
                    ]
                }
            ]
        }

        media_data: TreeItemData = {
            'text': 'Media',
            'item_type': 'folder',
            'status': 'active',
            'metadata': {'size': '15.2 GB', 'items': 89},
            'children': [
                {
                    'text': 'Photos',
                    'item_type': 'folder',
                    'status': 'active',
                    'children': [
                        {'text': 'Vacation 2023', 'item_type': 'folder', 'status': 'active'},
                        {'text': 'Family Photos', 'item_type': 'folder', 'status': 'active'},
                    ]
                },
                {
                    'text': 'Videos',
                    'item_type': 'folder',
                    'status': 'active',
                    'children': [
                        {'text': 'Presentation.mp4', 'item_type': 'video', 'status': 'active'},
                        {'text': 'Tutorial.mov', 'item_type': 'video', 'status': 'active'},
                    ]
                }
            ]
        }

        tree.addTopLevelItemFromDict(documents_data)
        tree.addTopLevelItemFromDict(media_data)

    def _create_sample_hierarchical_data(self) -> List[TreeItemData]:
        """Create sample hierarchical data"""
        return [
            {
                'text': 'Company Files',
                'item_type': 'folder',
                'status': 'Active',
                'metadata': {'created': '2023-01-15', 'owner': 'Admin'},
                'children': [
                    {
                        'text': 'HR Documents',
                        'item_type': 'folder',
                        'status': 'Active',
                        'children': [
                            {'text': 'Employee Handbook.pdf', 'item_type': 'document', 'status': 'Active'},
                            {'text': 'Policy Updates.docx', 'item_type': 'document', 'status': 'Draft'},
                        ]
                    },
                    {
                        'text': 'Marketing',
                        'item_type': 'folder',
                        'status': 'Active',
                        'children': [
                            {'text': 'Brand Guidelines.pdf', 'item_type': 'document', 'status': 'Active'},
                            {'text': 'Campaign Assets', 'item_type': 'folder', 'status': 'Active'},
                        ]
                    }
                ]
            },
            {
                'text': 'Archives',
                'item_type': 'folder',
                'status': 'Archived',
                'metadata': {'created': '2022-01-01', 'owner': 'System'},
                'children': [
                    {'text': 'Old Reports', 'item_type': 'folder', 'status': 'Archived'},
                    {'text': 'Legacy Data', 'item_type': 'folder', 'status': 'Archived'},
                ]
            }
        ]

    def _populate_org_chart_data(self, org_chart: FluentOrgChart):
        """Populate organization chart with sample data"""
        # CEO
        ceo_data: NodeData = {
            'title': 'Sarah Johnson',
            'subtitle': 'Chief Executive Officer',
            'status': 'active',
            'metadata': {'department': 'Executive', 'level': 'C-Suite'}
        }
        org_chart.addNode('ceo', ceo_data)

        # VPs
        vp_tech_data: NodeData = {
            'title': 'Michael Chen',
            'subtitle': 'VP of Technology',
            'status': 'active',
            'metadata': {'department': 'Technology', 'level': 'VP'}
        }
        org_chart.addNode('vp_tech', vp_tech_data, 'ceo')

        vp_sales_data: NodeData = {
            'title': 'Lisa Rodriguez',
            'subtitle': 'VP of Sales',
            'status': 'active',
            'metadata': {'department': 'Sales', 'level': 'VP'}
        }
        org_chart.addNode('vp_sales', vp_sales_data, 'ceo')

        # Directors
        dir_eng_data: NodeData = {
            'title': 'David Kim',
            'subtitle': 'Director of Engineering',
            'status': 'active',
            'metadata': {'department': 'Engineering', 'level': 'Director'}
        }
        org_chart.addNode('dir_eng', dir_eng_data, 'vp_tech')

        dir_design_data: NodeData = {
            'title': 'Emma Wilson',
            'subtitle': 'Director of Design',
            'status': 'active',
            'metadata': {'department': 'Design', 'level': 'Director'}
        }
        org_chart.addNode('dir_design', dir_design_data, 'vp_tech')

        # Team Leads
        lead_frontend_data: NodeData = {
            'title': 'Alex Thompson',
            'subtitle': 'Frontend Team Lead',
            'status': 'active',
            'metadata': {'department': 'Engineering', 'level': 'Lead'}
        }
        org_chart.addNode('lead_frontend', lead_frontend_data, 'dir_eng')

        lead_backend_data: NodeData = {
            'title': 'Maria Garcia',
            'subtitle': 'Backend Team Lead',
            'status': 'active',
            'metadata': {'department': 'Engineering', 'level': 'Lead'}
        }
        org_chart.addNode('lead_backend', lead_backend_data, 'dir_eng')

    def _create_tree_controls(self, tree: FluentTreeWidget) -> QWidget:
        """Create control buttons for tree widget"""
        controls = QWidget()
        layout = QHBoxLayout(controls)

        expand_btn = QPushButton("Expand All")
        collapse_btn = QPushButton("Collapse All")
        search_btn = QPushButton("Search 'Project'")
        clear_search_btn = QPushButton("Clear Search")

        expand_btn.clicked.connect(tree.expandAll)
        collapse_btn.clicked.connect(tree.collapseAll)
        search_btn.clicked.connect(lambda: tree.setSearchText("Project"))
        clear_search_btn.clicked.connect(lambda: tree.setSearchText(""))

        layout.addWidget(expand_btn)
        layout.addWidget(collapse_btn)
        layout.addWidget(search_btn)
        layout.addWidget(clear_search_btn)
        layout.addStretch()

        return controls

    def _create_org_chart_controls(self, org_chart: FluentOrgChart) -> QWidget:
        """Create control buttons for organization chart"""
        controls = QWidget()
        layout = QHBoxLayout(controls)

        zoom_in_btn = QPushButton("Zoom In")
        zoom_out_btn = QPushButton("Zoom Out")
        reset_zoom_btn = QPushButton("Reset Zoom")
        add_node_btn = QPushButton("Add Node")

        zoom_in_btn.clicked.connect(lambda: setattr(org_chart, 'zoom_factor', org_chart.zoom_factor * 1.2))
        zoom_out_btn.clicked.connect(lambda: setattr(org_chart, 'zoom_factor', org_chart.zoom_factor * 0.8))
        reset_zoom_btn.clicked.connect(lambda: setattr(org_chart, 'zoom_factor', 1.0))
        add_node_btn.clicked.connect(lambda: self._add_random_node(org_chart))

        layout.addWidget(zoom_in_btn)
        layout.addWidget(zoom_out_btn)
        layout.addWidget(reset_zoom_btn)
        layout.addWidget(add_node_btn)
        layout.addStretch()

        return controls

    def _add_random_node(self, org_chart: FluentOrgChart):
        """Add a random node to demonstrate dynamic updates"""
        import random
        node_id = f"node_{random.randint(1000, 9999)}"
        node_data: NodeData = {
            'title': f'New Employee {random.randint(1, 100)}',
            'subtitle': 'Software Developer',
            'status': 'active',
            'metadata': {'department': 'Engineering', 'level': 'Developer'}
        }
        # Add to a random existing node (simplified for demo)
        try:
            org_chart.addNode(node_id, node_data, 'lead_frontend')
        except ValueError:
            print("Could not add node - parent not found")

    def _load_performance_data(self, tree: FluentTreeWidget, count: int):
        """Load test data for performance demonstration"""
        import time
        
        print(f"Loading {count} items...")
        start_time = time.time()
        
        tree.clear()
        tree.current_state = TreeState.LOADING
        
        # Use QTimer for non-blocking loading
        self._load_items_batch(tree, count, 0, start_time)

    def _load_items_batch(self, tree: FluentTreeWidget, total: int, current: int, start_time: float):
        """Load items in batches for better performance"""
        batch_size = 100
        end_batch = min(current + batch_size, total)
        
        for i in range(current, end_batch):
            item_data: TreeItemData = {
                'text': f'Performance Item {i + 1}',
                'item_type': 'test_item',
                'status': 'active',
                'metadata': {'index': i, 'batch': current // batch_size}
            }
            tree.addTopLevelItemFromDict(item_data)
        
        if end_batch < total:
            # Continue with next batch
            QTimer.singleShot(1, lambda: self._load_items_batch(tree, total, end_batch, start_time))
        else:
            # Finished loading
            elapsed = time.time() - start_time
            tree.current_state = TreeState.IDLE
            print(f"Loaded {total} items in {elapsed:.2f} seconds")

    def _apply_theme(self):
        """Apply theme to the demo application"""
        theme_manager.set_theme_mode(theme_manager.ThemeMode.LIGHT)


def main():
    """Main demo application"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Optimized Fluent Tree Components")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Fluent Widgets Demo")

    # Create and show demo window
    demo = OptimizedTreeDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
