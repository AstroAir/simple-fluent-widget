"""
Comprehensive Demo of New Fluent Design Components

This demo showcases the newly added components that improve Fluent Design alignment:
- FluentAppBar: Top application bar
- FluentNavigationView: Side navigation panel  
- FluentFlyout: Popup containers
- Enhanced Fluent styling across all components
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QTextEdit, QSplitter)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import new components
    from components.interface.navigation.appbar import (FluentAppBar, FluentAppBarAction, 
                                                        FluentAppBarBuilder)
    from components.interface.navigation.navigationview import (FluentNavigationView, 
                                                                NavigationItem,
                                                                NavigationViewDisplayMode)
    from components.overlays_and_flyouts.flyout import (FluentFlyout, FlyoutPlacement,
                                                        show_flyout_at_widget, 
                                                        show_tooltip_flyout)
    
    # Import existing components for comparison
    from components.basic.forms.button import FluentButton
    from components.basic.forms.textbox import FluentLineEdit
    from components.basic.display.card import FluentCard
    
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Some components not available: {e}")
    COMPONENTS_AVAILABLE = False


class NewComponentsDemo(QMainWindow):
    """Demo window showcasing new Fluent Design components"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Design Components - New Components Demo")
        self.setMinimumSize(1200, 800)
        
        # Components references
        self.app_bar = None
        self.navigation_view = None
        self.content_area = None
        self.current_flyout = None
        
        self._setup_ui()
        self._populate_navigation()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup the main UI structure"""
        # Central widget with vertical layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # App Bar at the top
        self._setup_app_bar()
        main_layout.addWidget(self.app_bar)
        
        # Main content area with navigation and content
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Navigation View on the left
        self._setup_navigation_view()
        content_splitter.addWidget(self.navigation_view)
        
        # Content area on the right
        self._setup_content_area()
        content_splitter.addWidget(self.content_area)
        
        # Set splitter proportions
        content_splitter.setSizes([280, 920])
        content_splitter.setCollapsible(0, False)
        content_splitter.setCollapsible(1, False)
        
        main_layout.addWidget(content_splitter)
        
    def _setup_app_bar(self):
        """Setup the FluentAppBar"""
        if not COMPONENTS_AVAILABLE:
            self.app_bar = QLabel("FluentAppBar not available")
            return
            
        # Create app bar using builder pattern
        self.app_bar = (FluentAppBarBuilder()
                       .with_title("Fluent Components Demo")
                       .with_height_mode("standard")
                       .add_action("🏠", None, self._show_home, "navigation")
                       .add_action("📂", None, self._show_projects, "navigation")
                       .add_action("⚙️", None, self._show_settings, "primary")
                       .add_action("❓", None, self._show_help, "primary")
                       .build())
                       
    def _setup_navigation_view(self):
        """Setup the FluentNavigationView"""
        if not COMPONENTS_AVAILABLE:
            self.navigation_view = QLabel("FluentNavigationView not available")
            return
            
        self.navigation_view = FluentNavigationView()
        
    def _setup_content_area(self):
        """Setup the main content area"""
        self.content_area = QWidget()
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)
        
        # Title
        title_label = QLabel("New Fluent Design Components")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        content_layout.addWidget(title_label)
        
        # Description
        description = """
        This demo showcases the newly implemented Fluent Design components that enhance
        the library's alignment with Microsoft Fluent Design System:
        
        • FluentAppBar: Top-level application navigation and actions
        • FluentNavigationView: Hierarchical side navigation with responsive modes
        • FluentFlyout: Lightweight popups with smart positioning
        • Enhanced styling and animations across all components
        """
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; line-height: 1.4;")
        content_layout.addWidget(desc_label)
        
        # Demo sections
        self._add_demo_sections(content_layout)
        
        content_layout.addStretch()
        
    def _add_demo_sections(self, layout):
        """Add demo sections for each component"""
        
        # Flyout Demo Section
        flyout_card = self._create_demo_card(
            "FluentFlyout Demo",
            "Click buttons to see flyouts with different placements and content"
        )
        
        flyout_content = QHBoxLayout()
        
        # Flyout demo buttons
        flyout_buttons = [
            ("Show Tooltip", self._show_tooltip_flyout),
            ("Show Bottom Flyout", self._show_bottom_flyout),
            ("Show Right Flyout", self._show_right_flyout),
            ("Show Custom Content", self._show_custom_flyout)
        ]
        
        for text, callback in flyout_buttons:
            if COMPONENTS_AVAILABLE:
                btn = FluentButton(text)
                btn.clicked.connect(callback)
            else:
                btn = QPushButton(text + " (N/A)")
                btn.setEnabled(False)
            flyout_content.addWidget(btn)
            
        flyout_content.addStretch()
        flyout_card.addLayout(flyout_content)
        layout.addWidget(flyout_card)
        
        # Navigation Demo Section
        nav_card = self._create_demo_card(
            "Navigation Components Demo",
            "The app bar and navigation view demonstrate responsive design patterns"
        )
        
        nav_content = QHBoxLayout()
        
        nav_info = QLabel("""
        • App Bar: Provides consistent top-level navigation with actions
        • Navigation View: Supports minimal, compact, and expanded modes
        • Smart responsive behavior adapts to window size
        • Smooth animations enhance user experience
        """)
        nav_info.setWordWrap(True)
        nav_content.addWidget(nav_info)
        
        if COMPONENTS_AVAILABLE:
            toggle_btn = FluentButton("Toggle Navigation Mode")
            toggle_btn.clicked.connect(self._toggle_navigation_mode)
            nav_content.addWidget(toggle_btn)
            
        nav_card.addLayout(nav_content)
        layout.addWidget(nav_card)
        
    def _create_demo_card(self, title: str, description: str) -> QWidget:
        """Create a demo card container"""
        if COMPONENTS_AVAILABLE:
            card = FluentCard()
        else:
            card = QWidget()
            card.setStyleSheet("""
                QWidget {
                    background-color: #f9f9f9;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 16px;
                }
            """)
            
        layout = QVBoxLayout(card)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.DemiBold))
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 8px;")
        layout.addWidget(desc_label)
        
        return card
        
    def _populate_navigation(self):
        """Populate the navigation view with items"""
        if not COMPONENTS_AVAILABLE or not self.navigation_view:
            return
            
        # Create navigation items
        nav_items = [
            NavigationItem("Home", None, "home", "Go to home page"),
            NavigationItem("Components", None, "components", "Browse components", children=[
                NavigationItem("Basic", None, "basic", "Basic UI elements"),
                NavigationItem("Data", None, "data", "Data components"),
                NavigationItem("Interface", None, "interface", "Interface controls"),
                NavigationItem("Layout", None, "layout", "Layout containers"),
            ]),
            NavigationItem("Examples", None, "examples", "Code examples"),
            NavigationItem("Documentation", None, "docs", "API documentation"),
            NavigationItem("Settings", None, "settings", "Application settings"),
        ]
        
        # Add items to navigation view
        for item in nav_items:
            self.navigation_view.add_navigation_item(item)
            
    def _connect_signals(self):
        """Connect component signals"""
        if not COMPONENTS_AVAILABLE:
            return
            
        # App bar signals
        if self.app_bar:
            self.app_bar.navigation_requested.connect(self._handle_navigation)
            self.app_bar.action_triggered.connect(self._handle_action)
            
        # Navigation view signals
        if self.navigation_view:
            self.navigation_view.selection_changed.connect(self._handle_nav_selection)
            
    # Event handlers
    
    def _handle_navigation(self, action: str):
        """Handle navigation requests from app bar"""
        print(f"Navigation requested: {action}")
        
    def _handle_action(self, action: str):
        """Handle action triggers from app bar"""
        print(f"Action triggered: {action}")
        
    def _handle_nav_selection(self, item_key: str):
        """Handle navigation selection changes"""
        print(f"Navigation item selected: {item_key}")
        
    def _show_home(self):
        """Show home view"""
        print("Showing home")
        
    def _show_projects(self):
        """Show projects view"""
        print("Showing projects")
        
    def _show_settings(self):
        """Show settings view"""
        print("Showing settings")
        
    def _show_help(self):
        """Show help view"""
        print("Showing help")
        
    def _show_tooltip_flyout(self):
        """Show a simple tooltip flyout"""
        if not COMPONENTS_AVAILABLE:
            return
            
        sender = self.sender()
        show_tooltip_flyout(
            "This is a tooltip flyout with rich content!",
            sender,
            FlyoutPlacement.TOP
        )
        
    def _show_bottom_flyout(self):
        """Show a flyout positioned at the bottom"""
        if not COMPONENTS_AVAILABLE:
            return
            
        sender = self.sender()
        content = QLabel("Bottom positioned flyout\nwith multiple lines\nof content!")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        flyout = show_flyout_at_widget(content, sender, FlyoutPlacement.BOTTOM)
        self.current_flyout = flyout
        
    def _show_right_flyout(self):
        """Show a flyout positioned to the right"""
        if not COMPONENTS_AVAILABLE:
            return
            
        sender = self.sender()
        
        # Create more complex content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        content_layout.addWidget(QLabel("Right-positioned Flyout"))
        
        text_edit = QTextEdit()
        text_edit.setPlainText("This flyout contains\nmore complex content\nwith an editable text area.")
        text_edit.setMaximumHeight(100)
        content_layout.addWidget(text_edit)
        
        close_btn = QPushButton("Close")
        content_layout.addWidget(close_btn)
        
        flyout = show_flyout_at_widget(content_widget, sender, FlyoutPlacement.RIGHT)
        self.current_flyout = flyout
        
        # Connect close button
        close_btn.clicked.connect(flyout.hide_flyout)
        
    def _show_custom_flyout(self):
        """Show a flyout with custom content and styling"""
        if not COMPONENTS_AVAILABLE:
            return
            
        sender = self.sender()
        
        # Create custom content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        title = QLabel("Custom Flyout Content")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #0078d4; margin-bottom: 8px;")
        content_layout.addWidget(title)
        
        description = QLabel("This demonstrates a flyout with custom styling and interactive content.")
        description.setWordWrap(True)
        content_layout.addWidget(description)
        
        # Interactive elements
        input_field = QLineEdit()
        input_field.setPlaceholderText("Enter some text...")
        content_layout.addWidget(input_field)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        content_layout.addLayout(button_layout)
        
        flyout = show_flyout_at_widget(content_widget, sender, FlyoutPlacement.BOTTOM)
        self.current_flyout = flyout
        
        # Connect buttons
        ok_btn.clicked.connect(lambda: self._handle_custom_flyout_ok(input_field.text(), flyout))
        cancel_btn.clicked.connect(flyout.hide_flyout)
        
    def _handle_custom_flyout_ok(self, text: str, flyout):
        """Handle OK button in custom flyout"""
        print(f"Custom flyout OK clicked with text: {text}")
        flyout.hide_flyout()
        
    def _toggle_navigation_mode(self):
        """Toggle navigation view display mode"""
        if not COMPONENTS_AVAILABLE or not self.navigation_view:
            return
            
        current_mode = self.navigation_view._display_mode
        
        if current_mode == NavigationViewDisplayMode.EXPANDED:
            new_mode = NavigationViewDisplayMode.COMPACT
        elif current_mode == NavigationViewDisplayMode.COMPACT:
            new_mode = NavigationViewDisplayMode.MINIMAL
        else:
            new_mode = NavigationViewDisplayMode.EXPANDED
            
        self.navigation_view.set_display_mode(new_mode)


def main():
    """Run the demo application"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent Components Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Fluent Design")
    
    # Create and show main window
    window = NewComponentsDemo()
    window.show()
    
    # Center window on screen
    screen = app.primaryScreen().geometry()
    window_geometry = window.frameGeometry()
    center_point = screen.center()
    window_geometry.moveCenter(center_point)
    window.move(window_geometry.topLeft())
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
