#!/usr/bin/env python3
"""
Fluent Layout Components Demo

This example demonstrates the comprehensive usage of Fluent layout components including
StackPanel, ScrollViewer, Containers, and basic Qt layouts styled with Fluent design.
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
        from components.layout.scroll_viewer import FluentScrollViewer
        from components.layout.containers import FluentCard
        FLUENT_COMPONENTS_AVAILABLE = True
    except ImportError as e:
        print(f"Import note: {e}")
        print("Using standard Qt components for demo")
        FLUENT_COMPONENTS_AVAILABLE = False
    
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
            if FLUENT_COMPONENTS_AVAILABLE:
                self.create_fluent_stack_panel_tab()
                self.create_fluent_scroll_viewer_tab()
                self.create_fluent_containers_tab()
            
            self.create_standard_layouts_tab()
            self.create_layout_overview_tab()
            
        def create_fluent_stack_panel_tab(self):
            """Create FluentStackPanel examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Import here to avoid errors if not available
            from components.layout.stack_panel import FluentStackPanel, StackOrientation
            
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
            stack_group = QGroupBox("Interactive FluentStackPanel")
            stack_layout = QVBoxLayout(stack_group)
            
            # Create stack panel (use concrete implementation if available)
            try:
                self.stack_panel = FluentStackPanel(StackOrientation.VERTICAL)
                self.stack_panel.setMinimumHeight(300)
                
                # Add initial items
                for i in range(4):
                    self.add_stack_item_internal(f"Stack Item {i+1}")
                
                stack_layout.addWidget(self.stack_panel)
            except Exception as e:
                error_label = QLabel(f"FluentStackPanel not available: {e}")
                error_label.setStyleSheet("color: red; font-style: italic;")
                stack_layout.addWidget(error_label)
            
            layout.addWidget(stack_group)
            
            # Add examples section
            examples_group = QGroupBox("FluentStackPanel Usage Examples")
            examples_layout = QVBoxLayout(examples_group)
            
            examples_text = QLabel("""
<b>FluentStackPanel Features:</b><br>
• <b>Animated Transitions:</b> Smooth adding/removing of items<br>
• <b>Flexible Orientation:</b> Vertical or horizontal stacking<br>
• <b>Auto-wrap Support:</b> Responsive behavior on screen size changes<br>
• <b>Theme Integration:</b> Consistent with Fluent Design system<br><br>

<b>API Usage:</b><br>
<code>
stack = FluentStackPanel(StackOrientation.VERTICAL)<br>
stack.add_widget(widget)  # Add with animation<br>
stack.remove_widget(widget)  # Remove with animation<br>
stack.set_spacing(15)  # Adjust spacing<br>
stack.set_orientation(StackOrientation.HORIZONTAL)<br>
</code><br><br>

<b>Signals:</b><br>
• item_added(widget) - Emitted when item is added<br>
• item_removed(widget) - Emitted when item is removed<br>
• orientation_changed(orientation) - Emitted when orientation changes<br>
""")
            examples_text.setWordWrap(True)
            examples_layout.addWidget(examples_text)
            
            layout.addWidget(examples_group)
            
            self.tab_widget.addTab(tab, "FluentStackPanel")
            
        def create_fluent_scroll_viewer_tab(self):
            """Create FluentScrollViewer examples tab."""
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
            scroll_group = QGroupBox("Interactive FluentScrollViewer")
            scroll_layout = QVBoxLayout(scroll_group)
            
            # Use FluentScrollViewer if available, otherwise QScrollArea
            try:
                from components.layout.scroll_viewer import FluentScrollViewer
                # Note: This might fail due to abstract methods - in that case we'd need the concrete implementation
                self.scroll_viewer = QScrollArea()  # Fallback for now
                scroll_layout.addWidget(QLabel("FluentScrollViewer implementation pending"))
            except Exception as e:
                self.scroll_viewer = QScrollArea()
                self.scroll_viewer.setFixedHeight(400)
                
                # Create content that requires scrolling
                content_widget = self.create_large_content()
                self.scroll_viewer.setWidget(content_widget)
                
                scroll_layout.addWidget(self.scroll_viewer)
            
            layout.addWidget(scroll_group)
            
            # ScrollViewer examples
            examples_group = QGroupBox("FluentScrollViewer Features")
            examples_layout = QVBoxLayout(examples_group)
            
            examples_text = QLabel("""
<b>FluentScrollViewer Capabilities:</b><br>
• <b>Smooth Scrolling:</b> Momentum-based scrolling with easing<br>
• <b>Custom Scrollbars:</b> Fluent Design styled scrollbars<br>
• <b>Touch Support:</b> Native touch gestures and kinetic scrolling<br>
• <b>Zoom Integration:</b> Built-in zoom and pan capabilities<br>
• <b>Responsive Design:</b> Adapts to different screen sizes<br><br>

<b>API Usage:</b><br>
<code>
scroll_viewer = FluentScrollViewer()<br>
scroll_viewer.set_content(content_widget)<br>
scroll_viewer.set_horizontal_scroll_visibility(ScrollBarVisibility.AUTO)<br>
scroll_viewer.set_vertical_scroll_visibility(ScrollBarVisibility.VISIBLE)<br>
scroll_viewer.enable_zoom(True)<br>
</code><br><br>

<b>Common Use Cases:</b><br>
• <b>Document Viewers:</b> Long articles, manuals, documentation<br>
• <b>Data Lists:</b> Tables, file explorers, contact lists<br>
• <b>Image Galleries:</b> Zoomable photo viewers<br>
• <b>Form Containers:</b> Long forms with many fields<br>
""")
            examples_text.setWordWrap(True)
            examples_layout.addWidget(examples_text)
            
            layout.addWidget(examples_group)
            
            self.tab_widget.addTab(tab, "FluentScrollViewer")
            
        def create_fluent_containers_tab(self):
            """Create FluentCard and container examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Container examples
            containers_group = QGroupBox("Fluent Container Components")
            containers_layout = QVBoxLayout(containers_group)
            
            # FluentCard examples in horizontal layout
            cards_layout = QHBoxLayout()
            
            try:
                from components.layout.containers import FluentCard
                
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
                
            except Exception as e:
                error_label = QLabel(f"FluentCard components not available: {e}")
                error_label.setStyleSheet("color: red; font-style: italic;")
                cards_layout.addWidget(error_label)
            
            containers_layout.addLayout(cards_layout)
            layout.addWidget(containers_group)
            
            # Container documentation
            examples_group = QGroupBox("Container Types & Usage")
            examples_layout = QVBoxLayout(examples_group)
            
            examples_text = QLabel("""
<b>Fluent Container Components:</b><br><br>

<b>FluentCard:</b><br>
• Material Design-inspired card with elevation shadows<br>
• Support for header text and custom content layouts<br>
• Hover animations and focus states<br>
• Theme-aware background and border colors<br><br>

<b>FluentSection:</b> (planned)<br>
• Organized content sections with collapsible headers<br>
• Perfect for settings panels and form organization<br>
• Expandable/collapsible functionality<br><br>

<b>FluentContainer:</b> (planned)<br>
• Generic container with consistent theming<br>
• Flexible content layout support<br>
• Responsive design capabilities<br><br>

<b>API Usage:</b><br>
<code>
card = FluentCard()<br>
card.setHeaderText("My Card Title")<br>
card.addWidget(QLabel("Content text"))<br>
card.addWidget(QPushButton("Action Button"))<br>
# or<br>
layout = QVBoxLayout()<br>
card.addLayout(layout)<br>
</code><br><br>

<b>Design Features:</b><br>
• Consistent elevation and shadow effects<br>
• Smooth hover and focus transitions<br>
• Theme integration with automatic color updates<br>
• Responsive padding and spacing<br>
""")
            examples_text.setWordWrap(True)
            examples_layout.addWidget(examples_text)
            
            layout.addWidget(examples_group)
            
            self.tab_widget.addTab(tab, "FluentContainers")
            
        def create_standard_layouts_tab(self):
            """Create examples using standard Qt layouts with Fluent styling."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Grid layout example
            grid_group = QGroupBox("Responsive Grid Layout (QGridLayout)")
            grid_layout_outer = QVBoxLayout(grid_group)
            
            # Grid controls
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
            
            # VBox/HBox examples
            box_group = QGroupBox("Box Layouts with Fluent Styling")
            box_layout = QVBoxLayout(box_group)
            
            # Horizontal box example
            hbox_example = QFrame()
            hbox_example.setStyleSheet("""
                QFrame {
                    background-color: #f3f2f1;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                }
            """)
            hbox_layout = QHBoxLayout(hbox_example)
            
            hbox_layout.addWidget(QPushButton("Left"))
            hbox_layout.addStretch()
            hbox_layout.addWidget(QPushButton("Center"))
            hbox_layout.addStretch()
            hbox_layout.addWidget(QPushButton("Right"))
            
            # Vertical box example
            vbox_example = QFrame()
            vbox_example.setStyleSheet("""
                QFrame {
                    background-color: #faf9f8;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                }
            """)
            vbox_layout = QVBoxLayout(vbox_example)
            
            vbox_layout.addWidget(QLabel("Top Section"))
            vbox_layout.addWidget(QLabel("Middle Content"))
            vbox_layout.addStretch()
            vbox_layout.addWidget(QPushButton("Bottom Action"))
            
            box_examples_layout = QHBoxLayout()
            box_examples_layout.addWidget(hbox_example)
            box_examples_layout.addWidget(vbox_example)
            
            box_layout.addLayout(box_examples_layout)
            layout.addWidget(box_group)
            
            self.tab_widget.addTab(tab, "Standard Layouts")
            
        def create_layout_overview_tab(self):
            """Create layout system overview and architecture tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Architecture overview
            overview_group = QGroupBox("Fluent Layout System Architecture")
            overview_layout = QVBoxLayout(overview_group)
            
            overview_text = QLabel("""
<b>Fluent Layout System Design:</b><br><br>

<b>Base Classes:</b><br>
• <b>FluentLayoutBase:</b> Base for all layout containers with theme integration<br>
• <b>FluentContainerBase:</b> Base for content containers with consistent styling<br>
• <b>FluentControlBase:</b> Base for interactive controls with state management<br><br>

<b>Layout Components Available:</b><br>
• <b>FluentStackPanel:</b> Animated vertical/horizontal stacking<br>
• <b>FluentDockPanel:</b> Dockable panels with resizable splitters<br>
• <b>FluentGrid:</b> Responsive grid with flexible sizing rules<br>
• <b>FluentScrollViewer:</b> Smooth scrolling with custom scrollbars<br>
• <b>FluentCard:</b> Elevated content container with shadows<br><br>

<b>Design Principles:</b><br>
• <b>Consistent Theming:</b> All components respect the global theme<br>
• <b>Smooth Animations:</b> Enter/exit transitions for dynamic content<br>
• <b>Responsive Behavior:</b> Adapts to different screen sizes automatically<br>
• <b>Accessibility First:</b> Keyboard navigation and screen reader support<br>
• <b>Modern Visual Language:</b> Following Microsoft Fluent Design guidelines<br><br>

<b>Theme Integration:</b><br>
• Components automatically update when theme changes<br>
• Support for light, dark, and high contrast themes<br>
• Custom accent color integration<br>
• Consistent spacing, typography, and elevation<br>
""")
            overview_text.setWordWrap(True)
            overview_layout.addWidget(overview_text)
            
            layout.addWidget(overview_group)
            
            # Best practices
            practices_group = QGroupBox("Layout Best Practices")
            practices_layout = QVBoxLayout(practices_group)
            
            practices_text = QLabel("""
<b>Choosing the Right Layout:</b><br><br>

<b>Use FluentStackPanel when:</b><br>
• You need simple vertical or horizontal stacking<br>
• Items should be added/removed with animations<br>
• You want responsive behavior (orientation changes)<br><br>

<b>Use FluentDockPanel when:</b><br>
• Building complex application layouts<br>
• Users need resizable panels (like IDE interfaces)<br>
• You have primary content with supporting panels<br><br>

<b>Use FluentGrid when:</b><br>
• Content needs precise positioning<br>
• Building responsive card layouts<br>
• Creating form layouts with aligned controls<br><br>

<b>Use FluentScrollViewer when:</b><br>
• Content exceeds available space<br>
• You need smooth, custom scrolling behavior<br>
• Building document or list viewers<br><br>

<b>Performance Tips:</b><br>
• Use appropriate layout for your content size<br>
• Avoid deep nesting of layouts<br>
• Consider virtualization for large lists<br>
• Test on different screen sizes and DPI settings<br>
""")
            practices_text.setWordWrap(True)
            practices_layout.addWidget(practices_text)
            
            layout.addWidget(practices_group)
            
            self.tab_widget.addTab(tab, "Layout Guide")
            
        # Helper methods for interactive controls
        def update_stack_orientation(self, text):
            if hasattr(self, 'stack_panel'):
                from components.layout.stack_panel import StackOrientation
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
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #d2d0ce;
                    }
                    QPushButton:pressed {
                        background-color: #c8c6c4;
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
            grid_layout.setSpacing(10)
            
            colors = ["#ffcdd2", "#f8bbd9", "#e1bee7", "#d1c4e9", "#c5cae9", 
                     "#bbdefb", "#b3e5fc", "#b2dfdb", "#c8e6c9", "#dcedc8"]
            
            for i in range(9):
                item = QFrame()
                item.setFixedSize(120, 90)
                item.setStyleSheet(f"""
                    QFrame {{
                        background-color: {colors[i % len(colors)]};
                        border: 1px solid #c8c6c4;
                        border-radius: 8px;
                    }}
                """)
                
                item_layout = QVBoxLayout(item)
                item_layout.setContentsMargins(10, 10, 10, 10)
                
                title = QLabel(f"Item {i+1}")
                title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                title.setStyleSheet("font-weight: bold; color: #323130;")
                
                subtitle = QLabel(f"Grid cell")
                subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
                subtitle.setStyleSheet("color: #605e5c; font-size: 11px;")
                
                item_layout.addWidget(title)
                item_layout.addWidget(subtitle)
                
                grid_layout.addWidget(item, i // 3, i % 3)
                
        def update_grid_columns(self, cols):
            """Update grid column count."""
            if hasattr(self, 'grid_widget'):
                # For simplicity, just update spacing - in a real implementation
                # you'd rebuild the grid with the new column count
                if self.grid_widget.layout():
                    self.grid_widget.layout().setSpacing(10 + cols)
            
        def update_grid_gap(self, gap):
            """Update grid gap."""
            if hasattr(self, 'grid_widget') and self.grid_widget.layout():
                self.grid_widget.layout().setSpacing(gap)
            
        def create_large_content(self):
            """Create content larger than the scroll viewer."""
            widget = QWidget()
            layout = QVBoxLayout(widget)
            
            for i in range(20):
                section = QGroupBox(f"Section {i+1}")
                section.setStyleSheet("""
                    QGroupBox {
                        font-weight: bold;
                        border: 1px solid #c8c6c4;
                        border-radius: 6px;
                        margin-top: 10px;
                        padding-top: 10px;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 10px;
                        padding: 0 5px 0 5px;
                    }
                """)
                section_layout = QVBoxLayout(section)
                
                for j in range(3):
                    label = QLabel(f"Content item {j+1} in section {i+1}")
                    label.setStyleSheet("padding: 5px; color: #323130;")
                    section_layout.addWidget(label)
                    
                action_btn = QPushButton(f"Action for Section {i+1}")
                action_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #106ebe;
                    }
                """)
                section_layout.addWidget(action_btn)
                layout.addWidget(section)
                
            return widget
    
    # Create and show demo
    demo = LayoutDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
