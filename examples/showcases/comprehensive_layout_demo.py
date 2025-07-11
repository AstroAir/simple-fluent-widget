"""
Comprehensive Layout Components Demo
Showcases all the refactored and new layout components with modern Fluent design
"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QScrollArea, QLabel, QPushButton, 
                               QTextEdit, QLineEdit, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

# Import all layout components
from components.layout import (
    # Base classes
    FluentLayoutBase, FluentContainerBase,
    
    # Modern layouts
    FluentFlexLayout, FlexDirection, JustifyContent, AlignItems,
    FluentDockPanel, DockPosition,
    FluentUniformGrid, FluentMasonryLayout, FluentAdaptiveLayout, FluentCanvas,
    
    # Container components
    FluentCard, FluentExpander, FluentSplitter, FluentTabWidget, 
    FluentInfoBar, FluentPivot,
    
    # Existing components
    FluentGrid, FluentScrollViewer, FluentStackPanel
)

from core.theme import theme_manager


class LayoutDemoWidget(QWidget):
    """Demo widget for a specific layout component"""
    
    def __init__(self, title: str, description: str):
        super().__init__()
        self.title = title
        self.description = description
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(self.description)
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #605e5c; margin-bottom: 10px;")
        layout.addWidget(desc_label)
        
        # Demo area
        self.demo_area = QFrame()
        self.demo_area.setFrameStyle(QFrame.Shape.Box)
        self.demo_area.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
                border: 1px solid #d1d1d1;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.demo_area)


class FlexLayoutDemo(LayoutDemoWidget):
    """Demo for FluentFlexLayout"""
    
    def __init__(self):
        super().__init__(
            "FluentFlexLayout", 
            "CSS Flexbox-inspired layout with flexible item sizing, wrapping, and alignment options."
        )
        self.setup_flex_demo()
        
    def setup_flex_demo(self):
        layout = QVBoxLayout(self.demo_area)
        
        # Controls
        controls = QHBoxLayout()
        
        direction_btn = QPushButton("Toggle Direction")
        direction_btn.clicked.connect(self.toggle_direction)
        controls.addWidget(direction_btn)
        
        justify_btn = QPushButton("Change Justify")
        justify_btn.clicked.connect(self.change_justify)
        controls.addWidget(justify_btn)
        
        wrap_btn = QPushButton("Toggle Wrap")
        wrap_btn.clicked.connect(self.toggle_wrap)
        controls.addWidget(wrap_btn)
        
        layout.addLayout(controls)
        
        # Flex container
        self.flex_layout = FluentFlexLayout()
        self.flex_layout.setMinimumHeight(200)
        self.flex_layout.set_gap(8)
        
        # Add flex items
        colors = ["#0078d4", "#107c10", "#ff8c00", "#d13438", "#8764b8"]
        for i in range(5):
            item = QPushButton(f"Flex Item {i+1}")
            item.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors[i]};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {QColor(colors[i]).darker(110).name()};
                }}
            """)
            item.setMinimumSize(100, 40)
            
            # Vary flex properties
            if i == 0:
                self.flex_layout.add_widget(item, flex_grow=2)
            elif i == 2:
                self.flex_layout.add_widget(item, flex_grow=1)
            else:
                self.flex_layout.add_widget(item)
                
        layout.addWidget(self.flex_layout)
        
        self.current_direction = 0
        self.current_justify = 0
        
    def toggle_direction(self):
        directions = [FlexDirection.ROW, FlexDirection.COLUMN]
        self.current_direction = (self.current_direction + 1) % len(directions)
        self.flex_layout.set_flex_direction(directions[self.current_direction])
        
    def change_justify(self):
        justifies = [JustifyContent.FLEX_START, JustifyContent.CENTER, 
                    JustifyContent.FLEX_END, JustifyContent.SPACE_BETWEEN, 
                    JustifyContent.SPACE_AROUND]
        self.current_justify = (self.current_justify + 1) % len(justifies)
        self.flex_layout.set_justify_content(justifies[self.current_justify])
        
    def toggle_wrap(self):
        from components.layout.flex_layout import FlexWrap
        current = self.flex_layout.get_flex_wrap()
        new_wrap = FlexWrap.WRAP if current == FlexWrap.NO_WRAP else FlexWrap.NO_WRAP
        self.flex_layout.set_flex_wrap(new_wrap)


class DockPanelDemo(LayoutDemoWidget):
    """Demo for FluentDockPanel"""
    
    def __init__(self):
        super().__init__(
            "FluentDockPanel",
            "Dock widgets to edges with center fill area, similar to WPF DockPanel."
        )
        self.setup_dock_demo()
        
    def setup_dock_demo(self):
        layout = QVBoxLayout(self.demo_area)
        
        # Dock panel
        self.dock_panel = FluentDockPanel()
        self.dock_panel.setMinimumHeight(300)
        
        # Add docked widgets
        left_panel = QLabel("Left Panel")
        left_panel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.setStyleSheet("""
            QLabel {
                background-color: #deecf9;
                border: 1px solid #0078d4;
                border-radius: 4px;
                padding: 8px;
                font-weight: 500;
            }
        """)
        self.dock_panel.add_dock_widget(left_panel, DockPosition.LEFT, 150)
        
        top_panel = QLabel("Top Panel")
        top_panel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_panel.setStyleSheet("""
            QLabel {
                background-color: #d4edda;
                border: 1px solid #107c10;
                border-radius: 4px;
                padding: 8px;
                font-weight: 500;
            }
        """)
        self.dock_panel.add_dock_widget(top_panel, DockPosition.TOP, 60)
        
        right_panel = QLabel("Right Panel")
        right_panel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                border: 1px solid #ff8c00;
                border-radius: 4px;
                padding: 8px;
                font-weight: 500;
            }
        """)
        self.dock_panel.add_dock_widget(right_panel, DockPosition.RIGHT, 120)
        
        # Center content
        center_content = QTextEdit("This is the center fill area.\n\nResize the window to see responsive behavior.")
        center_content.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #d1d1d1;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.dock_panel.add_dock_widget(center_content, DockPosition.FILL)
        
        layout.addWidget(self.dock_panel)


class UniformGridDemo(LayoutDemoWidget):
    """Demo for FluentUniformGrid"""
    
    def __init__(self):
        super().__init__(
            "FluentUniformGrid",
            "Grid layout with equal-sized cells, similar to WPF UniformGrid."
        )
        self.setup_uniform_grid_demo()
        
    def setup_uniform_grid_demo(self):
        layout = QVBoxLayout(self.demo_area)
        
        # Controls
        controls = QHBoxLayout()
        
        cols_btn = QPushButton("Change Columns")
        cols_btn.clicked.connect(self.change_columns)
        controls.addWidget(cols_btn)
        
        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_item)
        controls.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Item")
        remove_btn.clicked.connect(self.remove_item)
        controls.addWidget(remove_btn)
        
        layout.addLayout(controls)
        
        # Uniform grid
        self.uniform_grid = FluentUniformGrid(columns=3)
        self.uniform_grid.setMinimumHeight(200)
        self.uniform_grid.set_spacing(8)
        
        # Add initial items
        self.item_count = 0
        for i in range(6):
            self.add_grid_item()
            
        layout.addWidget(self.uniform_grid)
        
        self.current_columns = 3
        
    def add_grid_item(self):
        colors = ["#0078d4", "#107c10", "#ff8c00", "#d13438", "#8764b8", "#00bcf2"]
        color = colors[self.item_count % len(colors)]
        
        item = QPushButton(f"Item {self.item_count + 1}")
        item.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {QColor(color).darker(110).name()};
            }}
        """)
        
        self.uniform_grid.add_widget(item)
        self.item_count += 1
        
    def change_columns(self):
        columns = [2, 3, 4, 5]
        current_index = columns.index(self.current_columns)
        new_index = (current_index + 1) % len(columns)
        self.current_columns = columns[new_index]
        self.uniform_grid.set_columns(self.current_columns)
        
    def add_item(self):
        self.add_grid_item()
        
    def remove_item(self):
        if self.item_count > 0:
            # Get last widget and remove it
            widgets = [self.uniform_grid._items[i] for i in range(len(self.uniform_grid._items))]
            if widgets:
                self.uniform_grid.remove_widget(widgets[-1])
                self.item_count -= 1


class MasonryDemo(LayoutDemoWidget):
    """Demo for FluentMasonryLayout"""
    
    def __init__(self):
        super().__init__(
            "FluentMasonryLayout",
            "Pinterest-style staggered grid layout with automatic column balancing."
        )
        self.setup_masonry_demo()
        
    def setup_masonry_demo(self):
        layout = QVBoxLayout(self.demo_area)
        
        # Controls
        controls = QHBoxLayout()
        
        width_btn = QPushButton("Change Column Width")
        width_btn.clicked.connect(self.change_column_width)
        controls.addWidget(width_btn)
        
        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_masonry_item)
        controls.addWidget(add_btn)
        
        layout.addLayout(controls)
        
        # Scroll area for masonry
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(250)
        
        # Masonry layout
        self.masonry_layout = FluentMasonryLayout(column_width=180)
        self.masonry_layout.set_spacing(8)
        
        # Add initial items with varying heights
        self.masonry_item_count = 0
        for i in range(8):
            self.add_masonry_item()
            
        scroll.setWidget(self.masonry_layout)
        layout.addWidget(scroll)
        
        self.column_widths = [150, 180, 220, 250]
        self.current_width_index = 1
        
    def add_masonry_item(self):
        import random
        
        colors = ["#0078d4", "#107c10", "#ff8c00", "#d13438", "#8764b8", "#00bcf2"]
        color = colors[self.masonry_item_count % len(colors)]
        
        # Random height for masonry effect
        height = random.randint(60, 150)
        
        item = QLabel(f"Masonry Item {self.masonry_item_count + 1}")
        item.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFixedHeight(height)
        item.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: 500;
            }}
        """)
        
        self.masonry_layout.add_widget(item)
        self.masonry_item_count += 1
        
    def change_column_width(self):
        self.current_width_index = (self.current_width_index + 1) % len(self.column_widths)
        new_width = self.column_widths[self.current_width_index]
        self.masonry_layout.set_column_width(new_width)


class ContainerDemo(LayoutDemoWidget):
    """Demo for container components"""
    
    def __init__(self):
        super().__init__(
            "Container Components",
            "Cards, expanders, info bars, and other container components with modern styling."
        )
        self.setup_container_demo()
        
    def setup_container_demo(self):
        layout = QVBoxLayout(self.demo_area)
        
        # Card demo
        card = FluentCard()
        card.setHeaderText("Sample Card")
        card.set_elevated(True, 2)
        card.set_clickable(True)
        
        card_content = QVBoxLayout()
        card_content.addWidget(QLabel("This is a card with elevation and click interaction."))
        
        card_btn = QPushButton("Card Action")
        card_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        card_content.addWidget(card_btn)
        
        card.content_layout.addLayout(card_content)
        layout.addWidget(card)
        
        # Expander demo
        expander = FluentExpander("Expandable Content")
        expander_content = QVBoxLayout()
        expander_content.addWidget(QLabel("This content can be expanded and collapsed."))
        expander_content.addWidget(QLineEdit("Sample input field"))
        expander.content_layout.addLayout(expander_content)
        layout.addWidget(expander)
        
        # Info bar demo
        info_bar = FluentInfoBar(
            "Information",
            "This is an informational message with an action button.",
            FluentInfoBar.Severity.INFO
        )
        info_bar.addActionButton("action", "Take Action")
        layout.addWidget(info_bar)
        
        # Tab widget demo
        tabs = FluentTabWidget()
        
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.addWidget(QLabel("Content of Tab 1"))
        tabs.addTab(tab1, "Tab 1")
        
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.addWidget(QLabel("Content of Tab 2"))
        tabs.addTab(tab2, "Tab 2")
        
        layout.addWidget(tabs)


class ComprehensiveLayoutDemo(QMainWindow):
    """Main demo window showcasing all layout components"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Layout Components - Comprehensive Demo")
        self.setMinimumSize(1200, 800)
        
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout using dock panel
        main_dock = FluentDockPanel()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.addWidget(main_dock)
        
        # Header
        header = QLabel("Fluent Layout Components Demo")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet("""
            QLabel {
                background-color: #0078d4;
                color: white;
                padding: 16px;
                border-radius: 0px;
            }
        """)
        main_dock.add_dock_widget(header, DockPosition.TOP, 60)
        
        # Sidebar with navigation
        sidebar = self.create_sidebar()
        main_dock.add_dock_widget(sidebar, DockPosition.LEFT, 200)
        
        # Main content area with scroll
        scroll_area = FluentScrollViewer()
        scroll_area.set_smooth_scrolling(True)
        
        self.content_stack = FluentStackPanel()
        self.content_stack.set_spacing(20)
        self.content_stack.setContentsMargins(20, 20, 20, 20)
        
        # Add all demos
        self.content_stack.add_widget(FlexLayoutDemo())
        self.content_stack.add_widget(DockPanelDemo())
        self.content_stack.add_widget(UniformGridDemo())
        self.content_stack.add_widget(MasonryDemo())
        self.content_stack.add_widget(ContainerDemo())
        
        scroll_area.setWidget(self.content_stack)
        main_dock.add_dock_widget(scroll_area, DockPosition.FILL)
        
        # Status bar
        status = QLabel("Ready - Resize window to see responsive behavior")
        status.setStyleSheet("""
            QLabel {
                background-color: #f3f2f1;
                color: #323130;
                padding: 8px 16px;
                border-top: 1px solid #d1d1d1;
            }
        """)
        main_dock.add_dock_widget(status, DockPosition.BOTTOM, 30)
        
    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-right: 1px solid #d1d1d1;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        title = QLabel("Components")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        components = [
            "FlexLayout", "DockPanel", "UniformGrid", 
            "MasonryLayout", "Containers"
        ]
        
        for component in components:
            btn = QPushButton(component)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px 12px;
                    border: none;
                    border-radius: 4px;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: #e1e6ea;
                }
                QPushButton:pressed {
                    background-color: #d1d7dc;
                }
            """)
            layout.addWidget(btn)
            
        layout.addStretch()
        
        # Theme toggle
        theme_btn = QPushButton("Toggle Theme")
        theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(theme_btn)
        
        return sidebar
        
    def apply_theme(self):
        """Apply global theme"""
        if theme_manager:
            theme_manager.apply_theme()
            
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        if theme_manager:
            from core.theme import ThemeMode
            current_mode = theme_manager._current_mode
            new_mode = ThemeMode.DARK if current_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
            theme_manager.set_theme_mode(new_mode)


def main():
    # Check if QApplication already exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Initialize theme manager
    if theme_manager:
        theme_manager.load_settings()
    
    window = ComprehensiveLayoutDemo()
    window.show()
    
    # Auto-demo timer (optional)
    def auto_demo():
        # Automatically demonstrate some features
        pass
        
    timer = QTimer()
    timer.timeout.connect(auto_demo)
    timer.start(5000)  # 5 second intervals
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
