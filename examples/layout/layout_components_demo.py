#!/usr/bin/env python3
"""
Fluent Layout Components Demo

This example demonstrates the comprehensive usage of Fluent layout components including
StackPanel, Grid, FlexLayout, ScrollViewer, and Containers with various configurations.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QGroupBox, QPushButton, QFrame, QScrollArea, QTabWidget,
    QSlider, QCheckBox, QComboBox, QSpinBox, QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor


def main():
    """Run the layout components demo application."""
    app = QApplication(sys.argv)
    
    # Import after QApplication is created
    try:
        from components.layout.stack_panel import FluentStackPanel, StackOrientation
        from components.layout.containers import FluentCard
        COMPONENTS_AVAILABLE = True
        print("Fluent layout components loaded successfully")
    except ImportError as e:
        print(f"Import error: {e}")
        print("Some layout components may not be available yet")
        COMPONENTS_AVAILABLE = False
        # Fallback imports
        StackOrientation = None
        FluentStackPanel = None
        FluentCard = None
    
    class LayoutDemo(QMainWindow):
        """Main demo window showcasing Fluent layout components."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Fluent Layout Components Demo")
            self.setGeometry(100, 100, 1400, 900)
            
            # Create central widget with tabs
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(10)
            main_layout.setContentsMargins(10, 10, 10, 10)
            
            # Add title
            title = QLabel("Fluent Layout Components Demo")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
            main_layout.addWidget(title)
            
            # Create tab widget for different layout examples
            self.tab_widget = QTabWidget()
            main_layout.addWidget(self.tab_widget)
            
            # Create tabs
            if COMPONENTS_AVAILABLE:
                self.create_stack_panel_tab()
                self.create_scroll_viewer_tab()
                self.create_containers_tab()
            
            self.create_grid_layout_tab()
            self.create_basic_layouts_tab()
            
        def create_stack_panel_tab(self):
            """Create StackPanel examples tab."""
            if not COMPONENTS_AVAILABLE:
                tab = QWidget()
                layout = QVBoxLayout(tab)
                layout.addWidget(QLabel("FluentStackPanel components not available yet."))
                self.tab_widget.addTab(tab, "StackPanel")
                return
                
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Controls
            controls_group = QGroupBox("StackPanel Controls")
            controls_layout = QHBoxLayout(controls_group)
            
            orientation_label = QLabel("Orientation:")
            self.orientation_combo = QComboBox()
            self.orientation_combo.addItems(["Vertical", "Horizontal"])
            self.orientation_combo.currentTextChanged.connect(self.update_stack_orientation)
            
            spacing_label = QLabel("Spacing:")
            self.spacing_slider = QSlider(Qt.Orientation.Horizontal)
            self.spacing_slider.setRange(0, 50)
            self.spacing_slider.setValue(10)
            self.spacing_slider.valueChanged.connect(self.update_stack_spacing)
            
            add_btn = QPushButton("Add Item")
            add_btn.clicked.connect(self.add_stack_item)
            
            remove_btn = QPushButton("Remove Last Item")
            remove_btn.clicked.connect(self.remove_stack_item)
            
            controls_layout.addWidget(orientation_label)
            controls_layout.addWidget(self.orientation_combo)
            controls_layout.addWidget(spacing_label)
            controls_layout.addWidget(self.spacing_slider)
            controls_layout.addWidget(add_btn)
            controls_layout.addWidget(remove_btn)
            controls_layout.addStretch()
            
            layout.addWidget(controls_group)
            
            # StackPanel examples
            stack_group = QGroupBox("Interactive StackPanel")
            stack_layout = QVBoxLayout(stack_group)
            
            # Create stack panel
            self.stack_panel = FluentStackPanel(StackOrientation.VERTICAL)
            self.stack_panel.setMinimumHeight(300)
            
            # Add initial items
            for i in range(4):
                self.add_stack_item_internal(f"Stack Item {i+1}")
            
            stack_layout.addWidget(self.stack_panel)
            layout.addWidget(stack_group)
            
            # Add examples section
            examples_group = QGroupBox("StackPanel Usage Examples")
            examples_layout = QVBoxLayout(examples_group)
            
            examples_text = QLabel("""
<b>Common StackPanel Use Cases:</b><br>
• <b>Vertical Layout:</b> Form fields, list items, navigation menus<br>
• <b>Horizontal Layout:</b> Toolbars, button groups, status bars<br>
• <b>Auto-sizing:</b> Items expand to fill available space<br>
• <b>Responsive:</b> Automatically adjusts to content changes<br><br>

<b>Code Example:</b><br>
<code>
stack = FluentStackPanel(StackOrientation.VERTICAL)<br>
stack.add_widget(QLabel("Item 1"))<br>
stack.add_widget(QPushButton("Button"))<br>
stack.set_spacing(15)<br>
</code>
""")
            examples_text.setWordWrap(True)
            examples_layout.addWidget(examples_text)
            
            layout.addWidget(examples_group)
            
            self.tab_widget.addTab(tab, "StackPanel")
            
        def create_grid_layout_tab(self):
            """Create Grid layout examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Grid examples
            grid_group = QGroupBox("Responsive Grid Layout")
            grid_layout_outer = QVBoxLayout(grid_group)
            
            # Add grid controls
            controls_frame = QFrame()
            controls_layout = QHBoxLayout(controls_frame)
            
            cols_label = QLabel("Columns:")
            self.cols_spin = QSpinBox()
            self.cols_spin.setRange(1, 6)
            self.cols_spin.setValue(3)
            self.cols_spin.valueChanged.connect(self.update_grid_columns)
            
            gap_label = QLabel("Gap:")
            self.gap_slider = QSlider(Qt.Orientation.Horizontal)
            self.gap_slider.setRange(0, 30)
            self.gap_slider.setValue(10)
            self.gap_slider.valueChanged.connect(self.update_grid_gap)
            
            controls_layout.addWidget(cols_label)
            controls_layout.addWidget(self.cols_spin)
            controls_layout.addWidget(gap_label)
            controls_layout.addWidget(self.gap_slider)
            controls_layout.addStretch()
            
            grid_layout_outer.addWidget(controls_frame)
            
            # Create grid widget
            self.grid_widget = QWidget()
            self.setup_grid_items(self.grid_widget)
            grid_layout_outer.addWidget(self.grid_widget)
            
            layout.addWidget(grid_group)
            
            # Grid examples documentation
            examples_group = QGroupBox("Grid Layout Features")
            examples_layout = QVBoxLayout(examples_group)
            
            examples_text = QLabel("""
<b>Grid Layout Capabilities:</b><br>
• <b>Flexible Column/Row Definitions:</b> Auto, fixed, or proportional sizing<br>
• <b>Grid Spanning:</b> Items can span multiple columns or rows<br>
• <b>Responsive Design:</b> Automatic reflow on screen size changes<br>
• <b>Alignment Control:</b> Precise positioning within grid cells<br><br>

<b>Usage Example:</b><br>
<code>
grid = QGridLayout()<br>
grid.addWidget(widget, row, column, rowSpan, columnSpan)<br>
grid.setSpacing(10)<br>
grid.setContentsMargins(15, 15, 15, 15)<br>
</code>
""")
            examples_text.setWordWrap(True)
            examples_layout.addWidget(examples_text)
            
            layout.addWidget(examples_group)
            
            self.tab_widget.addTab(tab, "Grid Layout")
            
        def create_scroll_viewer_tab(self):
            """Create ScrollViewer examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Scroll controls
            controls_group = QGroupBox("ScrollViewer Controls")
            controls_layout = QHBoxLayout(controls_group)
            
            h_scroll_label = QLabel("H Scroll:")
            self.h_scroll_combo = QComboBox()
            self.h_scroll_combo.addItems(["Auto", "Always On", "Always Off"])
            
            v_scroll_label = QLabel("V Scroll:")
            self.v_scroll_combo = QComboBox()
            self.v_scroll_combo.addItems(["Auto", "Always On", "Always Off"])
            
            smooth_scroll_label = QLabel("Smooth Scrolling:")
            self.smooth_scroll_check = QCheckBox()
            self.smooth_scroll_check.setChecked(True)
            
            controls_layout.addWidget(h_scroll_label)
            controls_layout.addWidget(self.h_scroll_combo)
            controls_layout.addWidget(v_scroll_label)
            controls_layout.addWidget(self.v_scroll_combo)
            controls_layout.addWidget(smooth_scroll_label)
            controls_layout.addWidget(self.smooth_scroll_check)
            controls_layout.addStretch()
            
            layout.addWidget(controls_group)
            
            # Scroll viewer example
            scroll_group = QGroupBox("Interactive ScrollViewer")
            scroll_layout = QVBoxLayout(scroll_group)
            
            # Use QScrollArea as fallback if FluentScrollViewer not available
            # Use QScrollArea as FluentScrollViewer needs more work
            self.scroll_viewer = QScrollArea()
            self.scroll_viewer.setFixedHeight(400)
            
            # Create content that requires scrolling
            content_widget = self.create_large_content()
            if hasattr(self.scroll_viewer, 'setWidget'):
                self.scroll_viewer.setWidget(content_widget)
            else:
                # Assume it's FluentScrollViewer with different API
                pass
            
            scroll_layout.addWidget(self.scroll_viewer)
            layout.addWidget(scroll_group)
            
            # ScrollViewer examples
            examples_group = QGroupBox("ScrollViewer Features")
            examples_layout = QVBoxLayout(examples_group)
            
            examples_text = QLabel("""
<b>ScrollViewer Capabilities:</b><br>
• <b>Automatic Scrollbars:</b> Show/hide based on content size<br>
• <b>Smooth Scrolling:</b> Animated transitions with momentum<br>
• <b>Keyboard Navigation:</b> Arrow keys, Page Up/Down, Home/End<br>
• <b>Touch Gestures:</b> Native touch scrolling and panning<br>
• <b>Custom Styling:</b> Fluent Design scrollbar appearance<br><br>

<b>Common Use Cases:</b><br>
• <b>Content Areas:</b> Long articles, documentation<br>
• <b>Lists:</b> Large data sets, file browsers<br>
• <b>Forms:</b> Multi-section forms with many fields<br>
• <b>Images:</b> Zoomable image viewers<br>
""")
            examples_text.setWordWrap(True)
            examples_layout.addWidget(examples_text)
            
            layout.addWidget(examples_group)
            
            self.tab_widget.addTab(tab, "ScrollViewer")
            
        def create_containers_tab(self):
            """Create container components examples tab."""
            if not COMPONENTS_AVAILABLE:
                tab = QWidget()
                layout = QVBoxLayout(tab)
                layout.addWidget(QLabel("FluentCard components not available yet."))
                self.tab_widget.addTab(tab, "Containers")
                return
                
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Container examples
            containers_group = QGroupBox("Container Components")
            containers_layout = QVBoxLayout(containers_group)
            
            # FluentCard examples in horizontal layout
            cards_layout = QHBoxLayout()
            
            # Card 1
            card1 = FluentCard()
            card1.setHeaderText("Sample Card 1")
            card1.addWidget(QLabel("This is a Fluent Design card with elevation shadow and rounded corners."))
            card1.addWidget(QPushButton("Card Action"))
            
            # Card 2
            card2 = FluentCard()
            card2.setHeaderText("Settings Card")
            card2.addWidget(QCheckBox("Enable notifications"))
            card2.addWidget(QCheckBox("Auto-save"))
            card2.addWidget(QCheckBox("Dark mode"))
            
            # Card 3
            card3 = FluentCard()
            card3.setHeaderText("Statistics")
            card3.addWidget(QLabel("Users: 1,234"))
            card3.addWidget(QLabel("Sessions: 5,678"))
            card3.addWidget(QSlider(Qt.Orientation.Horizontal))
            
            cards_layout.addWidget(card1)
            cards_layout.addWidget(card2)
            cards_layout.addWidget(card3)
            
            containers_layout.addLayout(cards_layout)
            layout.addWidget(containers_group)
            
            # Container documentation
            examples_group = QGroupBox("Container Types & Usage")
            examples_layout = QVBoxLayout(examples_group)
            
            examples_text = QLabel("""
<b>Container Components:</b><br><br>

<b>FluentCard:</b><br>
• Elevated surface with shadow and rounded corners<br>
• Perfect for content grouping and highlighting<br>
• Supports title, content, and action areas<br>
• Responsive elevation on hover/focus<br><br>

<b>Usage Examples:</b><br>
• <b>Dashboard Widgets:</b> Statistics, quick actions<br>
• <b>Content Blocks:</b> Articles, product cards<br>
• <b>Form Sections:</b> Grouped form fields<br>
• <b>Media Cards:</b> Image galleries, video thumbnails<br><br>

<b>Code Example:</b><br>
<code>
card = FluentCard()<br>
card.setHeaderText("My Card")<br>
card.addWidget(QLabel("Content"))<br>
card.addWidget(QPushButton("Action"))<br>
</code>
""")
            examples_text.setWordWrap(True)
            examples_layout.addWidget(examples_text)
            
            layout.addWidget(examples_group)
            
            self.tab_widget.addTab(tab, "Containers")
            
        def create_basic_layouts_tab(self):
            """Create basic layout examples using standard Qt components."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Basic layouts overview
            overview_group = QGroupBox("Layout Overview")
            overview_layout = QVBoxLayout(overview_group)
            
            overview_text = QLabel("""
<b>Fluent Layout System Architecture:</b><br><br>

<b>Layout Base Classes:</b><br>
• <b>FluentLayoutBase:</b> Base class for all Fluent layouts<br>
• <b>FluentContainerBase:</b> Base class for container components<br>
• <b>FluentControlBase:</b> Base class for interactive controls<br><br>

<b>Available Layout Components:</b><br>
• <b>FluentStackPanel:</b> Vertical/horizontal stacking with animations<br>
• <b>FluentDockPanel:</b> Dockable panels with resizable areas<br>
• <b>FluentGrid:</b> Responsive grid with flexible sizing<br>
• <b>FluentFlexLayout:</b> CSS Flexbox-inspired layout<br>
• <b>FluentScrollViewer:</b> Smooth scrolling container<br>
• <b>FluentCard:</b> Elevated content container<br><br>

<b>Design Principles:</b><br>
• Consistent theming across all components<br>
• Smooth animations and transitions<br>
• Responsive behavior for different screen sizes<br>
• Accessibility support built-in<br>
• Modern Fluent Design visual language<br>
""")
            overview_text.setWordWrap(True)
            overview_layout.addWidget(overview_text)
            
            layout.addWidget(overview_group)
            
            # Example layout combinations
            combinations_group = QGroupBox("Layout Combinations Example")
            combinations_layout = QVBoxLayout(combinations_group)
            
            # Create a complex layout example
            example_frame = QFrame()
            example_frame.setFrameStyle(QFrame.Shape.StyledPanel)
            example_frame.setStyleSheet("""
                QFrame {
                    background-color: #f3f2f1;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
            
            example_layout = QVBoxLayout(example_frame)
            
            # Header
            header = QLabel("Complex Layout Example")
            header.setStyleSheet("font-size: 16px; font-weight: bold; color: #323130; margin-bottom: 5px;")
            example_layout.addWidget(header)
            
            # Main content area with sidebar
            content_splitter = QHBoxLayout()
            
            # Sidebar
            sidebar = QFrame()
            sidebar.setFixedWidth(200)
            sidebar.setStyleSheet("background-color: white; border-radius: 4px; padding: 10px;")
            sidebar_layout = QVBoxLayout(sidebar)
            sidebar_layout.addWidget(QLabel("Navigation"))
            sidebar_layout.addWidget(QPushButton("Home"))
            sidebar_layout.addWidget(QPushButton("Settings"))
            sidebar_layout.addWidget(QPushButton("About"))
            sidebar_layout.addStretch()
            
            # Main content
            main_content = QFrame()
            main_content.setStyleSheet("background-color: white; border-radius: 4px; padding: 10px;")
            main_layout = QVBoxLayout(main_content)
            main_layout.addWidget(QLabel("Main Content Area"))
            main_layout.addWidget(QLabel("This demonstrates how multiple layout components can work together."))
            
            # Action buttons
            button_layout = QHBoxLayout()
            button_layout.addWidget(QPushButton("Save"))
            button_layout.addWidget(QPushButton("Cancel"))
            button_layout.addStretch()
            main_layout.addLayout(button_layout)
            
            content_splitter.addWidget(sidebar)
            content_splitter.addWidget(main_content)
            
            example_layout.addLayout(content_splitter)
            combinations_layout.addWidget(example_frame)
            
            layout.addWidget(combinations_group)
            
            self.tab_widget.addTab(tab, "Layout Overview")
            
        # Helper methods for interactive controls
        def update_stack_orientation(self, text):
            if hasattr(self, 'stack_panel') and COMPONENTS_AVAILABLE and StackOrientation:
                orientation = StackOrientation.VERTICAL if text == "Vertical" else StackOrientation.HORIZONTAL
                self.stack_panel.set_orientation(orientation)
            
        def update_stack_spacing(self, value):
            if hasattr(self, 'stack_panel'):
                self.stack_panel.set_spacing(value)
            
        def add_stack_item(self):
            if hasattr(self, 'stack_panel'):
                count = self.stack_panel.get_widget_count() + 1
                self.add_stack_item_internal(f"New Item {count}")
            
        def add_stack_item_internal(self, text):
            if hasattr(self, 'stack_panel'):
                item = QPushButton(text)
                item.setStyleSheet("""
                    QPushButton {
                        background-color: #e1dfdd;
                        border: 1px solid #c8c6c4;
                        border-radius: 4px;
                        padding: 8px 16px;
                        min-height: 30px;
                    }
                    QPushButton:hover {
                        background-color: #d2d0ce;
                    }
                """)
                self.stack_panel.add_widget(item)
            
        def remove_stack_item(self):
            if hasattr(self, 'stack_panel') and self.stack_panel.get_widget_count() > 0:
                # Get the last widget and remove it
                last_widget = self.stack_panel.get_widget_at(self.stack_panel.get_widget_count() - 1)
                if last_widget:
                    self.stack_panel.remove_widget(last_widget)
                
        def setup_grid_items(self, widget):
            """Set up a grid layout with demo items."""
            grid_layout = QGridLayout(widget)
            
            for i in range(9):
                item = QFrame()
                item.setFixedSize(100, 80)
                item.setStyleSheet(f"""
                    QFrame {{
                        background-color: hsl({i*40}, 60%, 85%);
                        border: 1px solid #c8c6c4;
                        border-radius: 4px;
                    }}
                """)
                
                label = QLabel(f"Item {i+1}")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                item_layout = QVBoxLayout(item)
                item_layout.addWidget(label)
                
                grid_layout.addWidget(item, i // 3, i % 3)
                
        def update_grid_columns(self, cols):
            """Update grid column count."""
            if hasattr(self, 'grid_widget'):
                # Clear existing layout
                old_layout = self.grid_widget.layout()
                if old_layout:
                    while old_layout.count():
                        child = old_layout.takeAt(0)
                        if child.widget():
                            child.widget().deleteLater()
                    old_layout.deleteLater()
                
                # Create new layout with updated columns
                self.setup_grid_items(self.grid_widget)
            
        def update_grid_gap(self, gap):
            """Update grid gap."""
            if hasattr(self, 'grid_widget'):
                layout = self.grid_widget.layout()
                if layout:
                    layout.setSpacing(gap)
            
        def create_large_content(self):
            """Create content larger than the scroll viewer."""
            widget = QWidget()
            layout = QVBoxLayout(widget)
            
            for i in range(20):
                section = QGroupBox(f"Section {i+1}")
                section_layout = QVBoxLayout(section)
                
                for j in range(3):
                    section_layout.addWidget(QLabel(f"Content item {j+1} in section {i+1}"))
                    
                section_layout.addWidget(QPushButton(f"Action for Section {i+1}"))
                layout.addWidget(section)
                
            return widget
    
    # Create and show demo
    demo = LayoutDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
