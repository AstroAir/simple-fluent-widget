"""
Comprehensive Interface Components Demo

This demo showcases all interface components available in the simple-fluent-widget library,
including navigation bars, command bars, toolbars, breadcrumbs, and menu systems.

Features demonstrated:
- Navigation components with hierarchical structure
- Command bars with fluent design
- Interactive menu systems
- Breadcrumb navigation
- Toolbar components
- Responsive interface layouts
"""

import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QGroupBox,
    QScrollArea, QFrame, QSpacerItem, QSizePolicy, QMessageBox, QTabWidget,
    QSlider, QSpinBox, QCheckBox, QComboBox, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem, QSplitter, QMenuBar, QMenu, QToolBar,
    QAction, QActionGroup, QButtonGroup, QRadioButton, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QUrl
from PySide6.QtGui import QColor, QPalette, QFont, QIcon, QPixmap, QAction as QGuiAction

# Import fluent interface components with fallbacks
try:
    from components.interface.navigation.navigation import (
        FluentSidebar, FluentHeaderNavigation, FluentBreadcrumbBar,
        NavigationItem, NavigationSection, HeaderAction
    )
    FLUENT_NAVIGATION_AVAILABLE = True
except ImportError:
    print("Warning: Fluent navigation components not available")
    FLUENT_NAVIGATION_AVAILABLE = False

try:
    from components.interface.command.command_bar import (
        FluentCommandBar, FluentToolbar, CommandItem, ToolbarAction
    )
    FLUENT_COMMAND_AVAILABLE = True
except ImportError:
    print("Warning: Fluent command components not available")
    FLUENT_COMMAND_AVAILABLE = False

try:
    from components.interface.navigation.menu import (
        FluentContextMenu, FluentMenuBar, FluentMenuItem
    )
    FLUENT_MENU_AVAILABLE = True
except ImportError:
    print("Warning: Fluent menu components not available")
    FLUENT_MENU_AVAILABLE = False

try:
    from components.layout.containers import FluentCard
    FLUENT_CARD_AVAILABLE = True
except ImportError:
    FLUENT_CARD_AVAILABLE = False


class FallbackNavigation(QWidget):
    """Fallback navigation component when fluent components are not available."""
    
    def __init__(self, nav_type="sidebar"):
        super().__init__()
        self.nav_type = nav_type
        self.items = []
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the fallback navigation UI."""
        layout = QVBoxLayout(self)
        
        if self.nav_type == "sidebar":
            self.setFixedWidth(200)
            self.setStyleSheet("""
                QWidget {
                    background-color: #f3f2f1;
                    border-right: 1px solid #edebe9;
                }
            """)
            
            # Add navigation items
            nav_items = [
                ("🏠", "Home"),
                ("📊", "Dashboard"),
                ("📁", "Files"),
                ("⚙️", "Settings"),
                ("👤", "Profile"),
                ("❓", "Help")
            ]
            
            for icon, text in nav_items:
                btn = QPushButton(f"{icon} {text}")
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 10px 15px;
                        border: none;
                        background-color: transparent;
                    }
                    QPushButton:hover {
                        background-color: #e1dfdd;
                    }
                """)
                layout.addWidget(btn)
                
            layout.addStretch()
            
        elif self.nav_type == "header":
            self.setFixedHeight(50)
            self.setStyleSheet("""
                QWidget {
                    background-color: #ffffff;
                    border-bottom: 1px solid #edebe9;
                }
            """)
            
            layout = QHBoxLayout(self)
            
            # Logo/Title
            logo = QLabel("App Title")
            logo.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            layout.addWidget(logo)
            
            layout.addStretch()
            
            # Navigation items
            nav_items = ["Home", "Products", "Services", "About", "Contact"]
            for item in nav_items:
                btn = QPushButton(item)
                btn.setStyleSheet("""
                    QPushButton {
                        padding: 8px 16px;
                        border: none;
                        background-color: transparent;
                    }
                    QPushButton:hover {
                        background-color: #f3f2f1;
                    }
                """)
                layout.addWidget(btn)
                
        elif self.nav_type == "breadcrumb":
            self.setFixedHeight(40)
            layout = QHBoxLayout(self)
            
            # Breadcrumb items
            breadcrumbs = ["Home", "Documents", "Projects", "Current Folder"]
            for i, crumb in enumerate(breadcrumbs):
                if i > 0:
                    separator = QLabel("›")
                    separator.setStyleSheet("color: #a19f9d; margin: 0 5px;")
                    layout.addWidget(separator)
                
                if i == len(breadcrumbs) - 1:
                    # Current item (not clickable)
                    label = QLabel(crumb)
                    label.setStyleSheet("font-weight: bold; color: #323130;")
                    layout.addWidget(label)
                else:
                    # Clickable breadcrumb
                    btn = QPushButton(crumb)
                    btn.setStyleSheet("""
                        QPushButton {
                            border: none;
                            background-color: transparent;
                            color: #0078d4;
                            text-decoration: underline;
                        }
                        QPushButton:hover {
                            color: #106ebe;
                        }
                    """)
                    layout.addWidget(btn)
                    
            layout.addStretch()


class InterfaceComponentsDemo(QMainWindow):
    """Main demo window showcasing interface components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interface Components Demo")
        self.setGeometry(100, 100, 1400, 900)
        
        # Current navigation state
        self.current_page = "Home"
        self.navigation_history = ["Home"]
        
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_toolbar()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header navigation
        self.create_header_navigation(main_layout)
        
        # Content area with sidebar
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Sidebar navigation
        self.create_sidebar_navigation(content_layout)
        
        # Main content area
        self.create_main_content_area(content_layout)
        
        main_layout.addLayout(content_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready - Navigate through different interface components")
        
    def create_header_navigation(self, parent_layout):
        """Create header navigation component."""
        header_group = QGroupBox("Header Navigation")
        header_layout = QVBoxLayout(header_group)
        
        if FLUENT_NAVIGATION_AVAILABLE:
            try:
                self.header_nav = FluentHeaderNavigation()
                # Configure header navigation
                header_actions = [
                    HeaderAction("Home", self.navigate_to_page),
                    HeaderAction("Products", self.navigate_to_page),
                    HeaderAction("Services", self.navigate_to_page),
                    HeaderAction("About", self.navigate_to_page),
                    HeaderAction("Contact", self.navigate_to_page)
                ]
                for action in header_actions:
                    self.header_nav.addAction(action)
            except Exception as e:
                print(f"Error creating FluentHeaderNavigation: {e}")
                self.header_nav = FallbackNavigation("header")
        else:
            self.header_nav = FallbackNavigation("header")
            
        header_layout.addWidget(self.header_nav)
        parent_layout.addWidget(header_group)
        
    def create_sidebar_navigation(self, parent_layout):
        """Create sidebar navigation component."""
        sidebar_group = QGroupBox("Sidebar Navigation")
        sidebar_layout = QVBoxLayout(sidebar_group)
        
        if FLUENT_NAVIGATION_AVAILABLE:
            try:
                self.sidebar = FluentSidebar()
                
                # Add navigation sections
                home_section = NavigationSection("Main")
                home_section.addItem(NavigationItem("🏠", "Home", self.navigate_to_page))
                home_section.addItem(NavigationItem("📊", "Dashboard", self.navigate_to_page))
                home_section.addItem(NavigationItem("📈", "Analytics", self.navigate_to_page))
                
                content_section = NavigationSection("Content")
                content_section.addItem(NavigationItem("📁", "Files", self.navigate_to_page))
                content_section.addItem(NavigationItem("📷", "Media", self.navigate_to_page))
                content_section.addItem(NavigationItem("📝", "Documents", self.navigate_to_page))
                
                settings_section = NavigationSection("System")
                settings_section.addItem(NavigationItem("⚙️", "Settings", self.navigate_to_page))
                settings_section.addItem(NavigationItem("👤", "Profile", self.navigate_to_page))
                settings_section.addItem(NavigationItem("❓", "Help", self.navigate_to_page))
                
                self.sidebar.addSection(home_section)
                self.sidebar.addSection(content_section)
                self.sidebar.addSection(settings_section)
                
            except Exception as e:
                print(f"Error creating FluentSidebar: {e}")
                self.sidebar = FallbackNavigation("sidebar")
        else:
            self.sidebar = FallbackNavigation("sidebar")
            
        sidebar_layout.addWidget(self.sidebar)
        parent_layout.addWidget(sidebar_group)
        
    def create_main_content_area(self, parent_layout):
        """Create main content area with tabs."""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Breadcrumb navigation
        self.create_breadcrumb_navigation(content_layout)
        
        # Tab widget for different demo sections
        self.tab_widget = QTabWidget()
        content_layout.addWidget(self.tab_widget)
        
        # Create demo tabs
        self.create_command_bar_tab()
        self.create_menu_systems_tab()
        self.create_navigation_patterns_tab()
        self.create_interaction_demo_tab()
        
        parent_layout.addWidget(content_widget)
        
    def create_breadcrumb_navigation(self, parent_layout):
        """Create breadcrumb navigation component."""
        breadcrumb_group = QGroupBox("Breadcrumb Navigation")
        breadcrumb_layout = QVBoxLayout(breadcrumb_group)
        
        if FLUENT_NAVIGATION_AVAILABLE:
            try:
                self.breadcrumb = FluentBreadcrumbBar()
                self.update_breadcrumb()
            except Exception as e:
                print(f"Error creating FluentBreadcrumbBar: {e}")
                self.breadcrumb = FallbackNavigation("breadcrumb")
        else:
            self.breadcrumb = FallbackNavigation("breadcrumb")
            
        breadcrumb_layout.addWidget(self.breadcrumb)
        parent_layout.addWidget(breadcrumb_group)
        
    def create_command_bar_tab(self):
        """Create command bar demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Command bar controls
        controls_group = QGroupBox("Command Bar Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        # Add command buttons
        add_command_btn = QPushButton("Add Command")
        add_command_btn.clicked.connect(self.add_command)
        controls_layout.addWidget(add_command_btn)
        
        remove_command_btn = QPushButton("Remove Command")
        remove_command_btn.clicked.connect(self.remove_command)
        controls_layout.addWidget(remove_command_btn)
        
        # Command bar style
        controls_layout.addWidget(QLabel("Style:"))
        self.command_style_combo = QComboBox()
        self.command_style_combo.addItems(["Default", "Compact", "Fluent", "Modern"])
        self.command_style_combo.currentTextChanged.connect(self.change_command_style)
        controls_layout.addWidget(self.command_style_combo)
        
        # Show labels
        self.show_labels_check = QCheckBox("Show Labels")
        self.show_labels_check.setChecked(True)
        self.show_labels_check.toggled.connect(self.toggle_command_labels)
        controls_layout.addWidget(self.show_labels_check)
        
        layout.addWidget(controls_group)
        
        # Command bar example
        command_group = QGroupBox("Interactive Command Bar")
        command_layout = QVBoxLayout(command_group)
        
        if FLUENT_COMMAND_AVAILABLE:
            try:
                self.command_bar = FluentCommandBar()
                
                # Add default commands
                commands = [
                    CommandItem("📁", "New", "Create new file", self.execute_command),
                    CommandItem("💾", "Save", "Save current file", self.execute_command),
                    CommandItem("📋", "Copy", "Copy selection", self.execute_command),
                    CommandItem("📌", "Paste", "Paste from clipboard", self.execute_command),
                    CommandItem("🔍", "Search", "Search content", self.execute_command),
                    CommandItem("⚙️", "Settings", "Open settings", self.execute_command)
                ]
                
                for command in commands:
                    self.command_bar.addCommand(command)
                    
            except Exception as e:
                print(f"Error creating FluentCommandBar: {e}")
                self.command_bar = self.create_fallback_command_bar()
        else:
            self.command_bar = self.create_fallback_command_bar()
            
        command_layout.addWidget(self.command_bar)
        layout.addWidget(command_group)
        
        # Command bar documentation
        docs_group = QGroupBox("Command Bar Features")
        docs_layout = QVBoxLayout(docs_group)
        
        docs_text = QLabel("""
<b>Command Bar Capabilities:</b><br>
• <b>Primary Commands:</b> Most important actions prominently displayed<br>
• <b>Secondary Commands:</b> Less common actions in overflow menu<br>
• <b>Adaptive Layout:</b> Automatically adjusts to available space<br>
• <b>Keyboard Shortcuts:</b> Accessible via keyboard navigation<br>
• <b>Icon + Text:</b> Clear visual and textual indicators<br><br>

<b>Best Practices:</b><br>
• Limit primary commands to 5-7 items<br>
• Use clear, action-oriented labels<br>
• Group related commands together<br>
• Provide tooltips for icon-only commands<br>
• Consider context-sensitive commands<br>
""")
        docs_text.setWordWrap(True)
        docs_layout.addWidget(docs_text)
        
        layout.addWidget(docs_group)
        
        self.tab_widget.addTab(tab_widget, "Command Bars")
        
    def create_menu_systems_tab(self):
        """Create menu systems demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Menu controls
        controls_group = QGroupBox("Menu System Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        # Context menu trigger
        context_menu_btn = QPushButton("Show Context Menu")
        context_menu_btn.clicked.connect(self.show_context_menu)
        controls_layout.addWidget(context_menu_btn)
        
        # Menu bar toggle
        menubar_toggle = QCheckBox("Show Menu Bar")
        menubar_toggle.setChecked(True)
        menubar_toggle.toggled.connect(self.toggle_menu_bar)
        controls_layout.addWidget(menubar_toggle)
        
        # Menu style
        controls_layout.addWidget(QLabel("Menu Style:"))
        self.menu_style_combo = QComboBox()
        self.menu_style_combo.addItems(["Default", "Fluent", "Dark", "Compact"])
        self.menu_style_combo.currentTextChanged.connect(self.change_menu_style)
        controls_layout.addWidget(self.menu_style_combo)
        
        layout.addWidget(controls_group)
        
        # Menu examples
        menu_examples_group = QGroupBox("Menu Examples")
        menu_examples_layout = QGridLayout(menu_examples_group)
        
        # Context menu example area
        context_area = QFrame()
        context_area.setFixedHeight(150)
        context_area.setStyleSheet("""
            QFrame {
                background-color: #f3f2f1;
                border: 2px dashed #c8c6c4;
                border-radius: 8px;
            }
        """)
        
        context_layout = QVBoxLayout(context_area)
        context_label = QLabel("Right-click here for context menu")
        context_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        context_layout.addWidget(context_label)
        
        # Enable context menu
        context_area.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        context_area.customContextMenuRequested.connect(self.show_custom_context_menu)
        
        menu_examples_layout.addWidget(context_area, 0, 0, 1, 2)
        
        # Menu bar example
        menubar_frame = QFrame()
        menubar_frame.setFixedHeight(100)
        menubar_frame.setStyleSheet("background-color: white; border: 1px solid #edebe9; border-radius: 4px;")
        
        menubar_layout = QVBoxLayout(menubar_frame)
        menubar_info = QLabel("Menu Bar Example (see top of window)")
        menubar_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menubar_layout.addWidget(menubar_info)
        
        menu_examples_layout.addWidget(menubar_frame, 1, 0, 1, 2)
        
        layout.addWidget(menu_examples_group)
        
        # Menu documentation
        menu_docs_group = QGroupBox("Menu System Features")
        menu_docs_layout = QVBoxLayout(menu_docs_group)
        
        menu_docs_text = QLabel("""
<b>Menu System Components:</b><br><br>

<b>Menu Bar:</b><br>
• Traditional horizontal menu at top of window<br>
• Supports nested submenus and separators<br>
• Keyboard navigation with Alt key<br>
• Mnemonics for quick access<br><br>

<b>Context Menus:</b><br>
• Right-click activated menus<br>
• Context-sensitive actions<br>
• Can include icons and shortcuts<br>
• Support for disabled/checked states<br><br>

<b>Fluent Menu Features:</b><br>
• Modern visual styling<br>
• Smooth animations<br>
• Consistent with Fluent Design<br>
• Touch-friendly sizing<br>
""")
        menu_docs_text.setWordWrap(True)
        menu_docs_layout.addWidget(menu_docs_text)
        
        layout.addWidget(menu_docs_group)
        
        self.tab_widget.addTab(tab_widget, "Menu Systems")
        
    def create_navigation_patterns_tab(self):
        """Create navigation patterns demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Navigation patterns
        patterns_group = QGroupBox("Navigation Patterns Examples")
        patterns_layout = QGridLayout(patterns_group)
        
        # Tab navigation example
        tab_example = QTabWidget()
        tab_example.addTab(QLabel("Tab 1 Content"), "Home")
        tab_example.addTab(QLabel("Tab 2 Content"), "Settings")
        tab_example.addTab(QLabel("Tab 3 Content"), "About")
        tab_example.setFixedHeight(150)
        
        patterns_layout.addWidget(QLabel("Tab Navigation:"), 0, 0)
        patterns_layout.addWidget(tab_example, 0, 1)
        
        # Tree navigation example
        tree_nav = QTreeWidget()
        tree_nav.setHeaderLabel("Tree Navigation")
        tree_nav.setFixedHeight(150)
        
        # Add tree items
        root1 = QTreeWidgetItem(tree_nav, ["📁 Documents"])
        QTreeWidgetItem(root1, ["📄 File 1.txt"])
        QTreeWidgetItem(root1, ["📄 File 2.pdf"])
        
        root2 = QTreeWidgetItem(tree_nav, ["📁 Images"])
        QTreeWidgetItem(root2, ["🖼️ Photo 1.jpg"])
        QTreeWidgetItem(root2, ["🖼️ Photo 2.png"])
        
        root3 = QTreeWidgetItem(tree_nav, ["📁 Projects"])
        project1 = QTreeWidgetItem(root3, ["📁 Project A"])
        QTreeWidgetItem(project1, ["📄 README.md"])
        QTreeWidgetItem(project1, ["📄 main.py"])
        
        tree_nav.expandAll()
        
        patterns_layout.addWidget(QLabel("Tree Navigation:"), 1, 0)
        patterns_layout.addWidget(tree_nav, 1, 1)
        
        # List navigation example
        list_nav = QListWidget()
        list_nav.setFixedHeight(150)
        
        list_items = [
            "🏠 Home Dashboard",
            "📊 Analytics Overview", 
            "👥 User Management",
            "📧 Email Settings",
            "🔐 Security Options",
            "🎨 Theme Preferences"
        ]
        
        for item_text in list_items:
            list_nav.addItem(QListWidgetItem(item_text))
            
        patterns_layout.addWidget(QLabel("List Navigation:"), 2, 0)
        patterns_layout.addWidget(list_nav, 2, 1)
        
        layout.addWidget(patterns_group)
        
        # Navigation state management
        state_group = QGroupBox("Navigation State Management")
        state_layout = QVBoxLayout(state_group)
        
        # Current state display
        self.nav_state_label = QLabel("Current Page: Home")
        self.nav_state_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        state_layout.addWidget(self.nav_state_label)
        
        # Navigation history
        history_layout = QHBoxLayout()
        history_layout.addWidget(QLabel("Navigation History:"))
        
        self.history_display = QLabel(" → ".join(self.navigation_history))
        self.history_display.setStyleSheet("color: #0078d4;")
        history_layout.addWidget(self.history_display)
        
        history_layout.addStretch()
        
        # Back/Forward buttons
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self.navigate_back)
        history_layout.addWidget(back_btn)
        
        forward_btn = QPushButton("Forward →")
        forward_btn.clicked.connect(self.navigate_forward)
        history_layout.addWidget(forward_btn)
        
        state_layout.addLayout(history_layout)
        
        # Quick navigation
        quick_nav_layout = QHBoxLayout()
        quick_nav_layout.addWidget(QLabel("Quick Navigation:"))
        
        pages = ["Home", "Dashboard", "Settings", "Profile", "Help"]
        for page in pages:
            btn = QPushButton(page)
            btn.clicked.connect(lambda checked, p=page: self.navigate_to_page(p))
            quick_nav_layout.addWidget(btn)
            
        quick_nav_layout.addStretch()
        state_layout.addLayout(quick_nav_layout)
        
        layout.addWidget(state_group)
        
        self.tab_widget.addTab(tab_widget, "Navigation Patterns")
        
    def create_interaction_demo_tab(self):
        """Create interaction demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Interactive features
        interaction_group = QGroupBox("Interactive Interface Features")
        interaction_layout = QVBoxLayout(interaction_group)
        
        # Search bar with auto-complete
        search_frame = QFrame()
        search_frame.setStyleSheet("background-color: white; border: 1px solid #edebe9; border-radius: 4px; padding: 10px;")
        search_layout = QVBoxLayout(search_frame)
        
        search_layout.addWidget(QLabel("Search with Auto-complete:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.textChanged.connect(self.update_search_suggestions)
        search_layout.addWidget(self.search_input)
        
        self.search_suggestions = QListWidget()
        self.search_suggestions.setMaximumHeight(120)
        self.search_suggestions.setVisible(False)
        self.search_suggestions.itemClicked.connect(self.select_search_suggestion)
        search_layout.addWidget(self.search_suggestions)
        
        interaction_layout.addWidget(search_frame)
        
        # Filter and sort controls
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: white; border: 1px solid #edebe9; border-radius: 4px; padding: 10px;")
        filter_layout = QGridLayout(filter_frame)
        
        filter_layout.addWidget(QLabel("Filter by Category:"), 0, 0)
        category_filter = QComboBox()
        category_filter.addItems(["All", "Documents", "Images", "Videos", "Audio"])
        filter_layout.addWidget(category_filter, 0, 1)
        
        filter_layout.addWidget(QLabel("Sort by:"), 0, 2)
        sort_combo = QComboBox()
        sort_combo.addItems(["Name", "Date", "Size", "Type"])
        filter_layout.addWidget(sort_combo, 0, 3)
        
        filter_layout.addWidget(QLabel("Sort Order:"), 1, 0)
        order_combo = QComboBox()
        order_combo.addItems(["Ascending", "Descending"])
        filter_layout.addWidget(order_combo, 1, 1)
        
        # View options
        filter_layout.addWidget(QLabel("View:"), 1, 2)
        view_group = QButtonGroup()
        
        list_view_radio = QRadioButton("List")
        list_view_radio.setChecked(True)
        grid_view_radio = QRadioButton("Grid")
        
        view_group.addButton(list_view_radio)
        view_group.addButton(grid_view_radio)
        
        view_layout = QHBoxLayout()
        view_layout.addWidget(list_view_radio)
        view_layout.addWidget(grid_view_radio)
        
        view_widget = QWidget()
        view_widget.setLayout(view_layout)
        filter_layout.addWidget(view_widget, 1, 3)
        
        interaction_layout.addWidget(filter_frame)
        
        # Progress and status indicators
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: white; border: 1px solid #edebe9; border-radius: 4px; padding: 10px;")
        status_layout = QVBoxLayout(status_frame)
        
        status_layout.addWidget(QLabel("Status Indicators:"))
        
        # Progress bar
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Loading Progress:"))
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(75)
        progress_layout.addWidget(self.progress_bar)
        
        progress_btn = QPushButton("Simulate Progress")
        progress_btn.clicked.connect(self.simulate_progress)
        progress_layout.addWidget(progress_btn)
        
        status_layout.addLayout(progress_layout)
        
        # Status indicators
        status_indicators_layout = QHBoxLayout()
        
        # Online status
        online_indicator = QLabel("🟢 Online")
        online_indicator.setStyleSheet("color: #107c10; font-weight: bold;")
        status_indicators_layout.addWidget(online_indicator)
        
        # Sync status
        sync_indicator = QLabel("🔄 Syncing...")
        sync_indicator.setStyleSheet("color: #0078d4; font-weight: bold;")
        status_indicators_layout.addWidget(sync_indicator)
        
        # Error status
        error_indicator = QLabel("❌ Error")
        error_indicator.setStyleSheet("color: #d13438; font-weight: bold;")
        status_indicators_layout.addWidget(error_indicator)
        
        status_indicators_layout.addStretch()
        status_layout.addLayout(status_indicators_layout)
        
        interaction_layout.addWidget(status_frame)
        
        layout.addWidget(interaction_group)
        
        # Accessibility features
        accessibility_group = QGroupBox("Accessibility Features")
        accessibility_layout = QVBoxLayout(accessibility_group)
        
        accessibility_text = QLabel("""
<b>Built-in Accessibility Features:</b><br>
• <b>Keyboard Navigation:</b> Full keyboard support for all interface elements<br>
• <b>Screen Reader Support:</b> Proper ARIA labels and semantic markup<br>
• <b>High Contrast:</b> Support for high contrast themes<br>
• <b>Focus Indicators:</b> Clear visual focus indicators<br>
• <b>Touch Friendly:</b> Adequate touch target sizes<br>
• <b>Customizable:</b> User-configurable UI scaling and colors<br><br>

<b>Keyboard Shortcuts:</b><br>
• Tab/Shift+Tab: Navigate between elements<br>
• Enter/Space: Activate buttons and controls<br>
• Arrow Keys: Navigate lists and menus<br>
• Escape: Close dialogs and menus<br>
• Ctrl+F: Open search functionality<br>
""")
        accessibility_text.setWordWrap(True)
        accessibility_layout.addWidget(accessibility_text)
        
        layout.addWidget(accessibility_group)
        
        self.tab_widget.addTab(tab_widget, "Interactions")
        
    def setup_menu_bar(self):
        """Set up the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(lambda: self.execute_command("New"))
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(lambda: self.execute_command("Open"))
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(lambda: self.execute_command("Save"))
        file_menu.addAction(save_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(lambda: self.execute_command("Copy"))
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(lambda: self.execute_command("Paste"))
        edit_menu.addAction(paste_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        fullscreen_action = QAction("Full Screen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_toolbar(self):
        """Set up the application toolbar."""
        toolbar = self.addToolBar("Main")
        toolbar.setObjectName("MainToolbar")
        
        # Add toolbar actions
        toolbar.addAction("🏠", lambda: self.navigate_to_page("Home"))
        toolbar.addAction("📁", lambda: self.execute_command("New"))
        toolbar.addAction("💾", lambda: self.execute_command("Save"))
        toolbar.addSeparator()
        toolbar.addAction("📋", lambda: self.execute_command("Copy"))
        toolbar.addAction("📌", lambda: self.execute_command("Paste"))
        toolbar.addSeparator()
        toolbar.addAction("🔍", lambda: self.execute_command("Search"))
        toolbar.addAction("⚙️", lambda: self.navigate_to_page("Settings"))
        
    def create_fallback_command_bar(self):
        """Create fallback command bar."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        widget.setStyleSheet("""
            QWidget {
                background-color: #faf9f8;
                border: 1px solid #edebe9;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        
        commands = [
            ("📁", "New"),
            ("💾", "Save"),
            ("📋", "Copy"),
            ("📌", "Paste"),
            ("🔍", "Search"),
            ("⚙️", "Settings")
        ]
        
        for icon, text in commands:
            btn = QPushButton(f"{icon} {text}")
            btn.clicked.connect(lambda checked, cmd=text: self.execute_command(cmd))
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 12px;
                    border: 1px solid #c8c6c4;
                    border-radius: 4px;
                    background-color: white;
                }
                QPushButton:hover {
                    background-color: #f3f2f1;
                }
            """)
            layout.addWidget(btn)
            
        layout.addStretch()
        return widget
        
    # Event handlers
    def navigate_to_page(self, page_name):
        """Navigate to a specific page."""
        self.current_page = page_name
        self.navigation_history.append(page_name)
        
        # Update displays
        self.nav_state_label.setText(f"Current Page: {page_name}")
        self.history_display.setText(" → ".join(self.navigation_history[-5:]))  # Show last 5
        self.update_breadcrumb()
        
        self.statusBar().showMessage(f"Navigated to: {page_name}")
        
    def navigate_back(self):
        """Navigate back in history."""
        if len(self.navigation_history) > 1:
            self.navigation_history.pop()
            previous_page = self.navigation_history[-1]
            self.current_page = previous_page
            
            self.nav_state_label.setText(f"Current Page: {previous_page}")
            self.history_display.setText(" → ".join(self.navigation_history[-5:]))
            self.update_breadcrumb()
            
            self.statusBar().showMessage(f"Navigated back to: {previous_page}")
        else:
            self.statusBar().showMessage("No previous page in history")
            
    def navigate_forward(self):
        """Navigate forward (demo functionality)."""
        self.statusBar().showMessage("Forward navigation (not implemented in demo)")
        
    def update_breadcrumb(self):
        """Update breadcrumb navigation."""
        if hasattr(self.breadcrumb, 'updatePath') and callable(self.breadcrumb.updatePath):
            path_parts = ["Home"]
            if self.current_page != "Home":
                path_parts.extend(self.current_page.split(" / "))
            self.breadcrumb.updatePath(path_parts)
            
    def execute_command(self, command):
        """Execute a command from command bar or menu."""
        self.statusBar().showMessage(f"Executed command: {command}")
        
        if command == "Search":
            self.search_input.setFocus()
        elif command == "Settings":
            self.navigate_to_page("Settings")
        # Add more command implementations as needed
        
    def add_command(self):
        """Add a new command to the command bar."""
        self.statusBar().showMessage("New command added (demo)")
        
    def remove_command(self):
        """Remove a command from the command bar."""
        self.statusBar().showMessage("Command removed (demo)")
        
    def change_command_style(self, style):
        """Change command bar style."""
        self.statusBar().showMessage(f"Command bar style changed to: {style}")
        
    def toggle_command_labels(self, show_labels):
        """Toggle command labels visibility."""
        self.statusBar().showMessage(f"Command labels: {'Shown' if show_labels else 'Hidden'}")
        
    def show_context_menu(self):
        """Show context menu demonstration."""
        self.statusBar().showMessage("Context menu demonstration")
        
    def show_custom_context_menu(self, position):
        """Show custom context menu."""
        menu = QMenu(self)
        
        # Add context menu actions
        copy_action = menu.addAction("📋 Copy")
        copy_action.triggered.connect(lambda: self.execute_command("Copy"))
        
        paste_action = menu.addAction("📌 Paste")
        paste_action.triggered.connect(lambda: self.execute_command("Paste"))
        
        menu.addSeparator()
        
        properties_action = menu.addAction("🔧 Properties")
        properties_action.triggered.connect(lambda: self.execute_command("Properties"))
        
        # Show menu at cursor position
        menu.exec(self.mapToGlobal(position))
        
    def toggle_menu_bar(self, visible):
        """Toggle menu bar visibility."""
        self.menuBar().setVisible(visible)
        self.statusBar().showMessage(f"Menu bar: {'Shown' if visible else 'Hidden'}")
        
    def change_menu_style(self, style):
        """Change menu style."""
        self.statusBar().showMessage(f"Menu style changed to: {style}")
        
    def update_search_suggestions(self, text):
        """Update search suggestions based on input."""
        suggestions = [
            "Home Dashboard",
            "User Settings",
            "File Management",
            "System Preferences",
            "Help Documentation",
            "Contact Support",
            "Navigation Menu",
            "Command Bar",
            "Interface Settings"
        ]
        
        if text:
            filtered = [s for s in suggestions if text.lower() in s.lower()]
            self.search_suggestions.clear()
            
            if filtered:
                for suggestion in filtered[:5]:  # Limit to 5 suggestions
                    self.search_suggestions.addItem(suggestion)
                self.search_suggestions.setVisible(True)
            else:
                self.search_suggestions.setVisible(False)
        else:
            self.search_suggestions.setVisible(False)
            
    def select_search_suggestion(self, item):
        """Select a search suggestion."""
        self.search_input.setText(item.text())
        self.search_suggestions.setVisible(False)
        self.statusBar().showMessage(f"Selected: {item.text()}")
        
    def simulate_progress(self):
        """Simulate progress bar animation."""
        self.progress_timer = QTimer()
        self.progress_value = 0
        
        def update_progress():
            self.progress_value += 5
            self.progress_bar.setValue(self.progress_value)
            
            if self.progress_value >= 100:
                self.progress_timer.stop()
                self.statusBar().showMessage("Progress completed")
            
        self.progress_timer.timeout.connect(update_progress)
        self.progress_timer.start(100)
        
    def toggle_fullscreen(self, checked):
        """Toggle fullscreen mode."""
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()
            
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About", 
                         "Interface Components Demo\\n\\n"
                         "This demo showcases various interface components "
                         "available in the simple-fluent-widget library.")


def main():
    """Main function to run the demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Interface Components Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Simple Fluent Widget")
    
    # Create and show the demo
    demo = InterfaceComponentsDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
