"""
Comprehensive Composite Components Demo

This demo showcases all composite components available in the simple-fluent-widget library,
including complex forms, navigation interfaces, container panels, and integrated workflows.

Features demonstrated:
- Advanced form systems with validation
- Navigation and interface components
- Settings and properties panels
- Dialog and container management
- Workflow integration and state management
"""

import sys
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QGroupBox,
    QScrollArea, QFrame, QSpacerItem, QSizePolicy, QMessageBox, QTabWidget,
    QSplitter, QTreeWidget, QTreeWidgetItem, QComboBox, QSpinBox, 
    QCheckBox, QSlider, QProgressBar, QListWidget, QListWidgetItem,
    QStackedWidget, QToolBar, QMenuBar, QStatusBar, QToolButton, QMenu
)
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QColor, QPalette, QFont, QIcon, QAction, QPixmap

# Import fluent composite components with fallbacks
try:
    from components.composite.forms.forms import (
        FluentFieldGroup, FluentValidationForm, FluentQuickForm,
        FieldType, ValidationResult, FieldDefinition
    )
    FLUENT_FORMS_AVAILABLE = True
except ImportError:
    print("Warning: Fluent form components not available")
    FLUENT_FORMS_AVAILABLE = False

try:
    from components.composite.interface.navigation import (
        FluentSidebar, FluentHeaderNavigation, FluentBreadcrumbBar,
        NavigationItem, NavigationSection, HeaderAction
    )
    FLUENT_NAVIGATION_AVAILABLE = True
except ImportError:
    print("Warning: Fluent navigation components not available")
    FLUENT_NAVIGATION_AVAILABLE = False

try:
    from components.composite.interface.toolbars import (
        FluentToolbar, FluentRibbon, FluentCommandBar
    )
    FLUENT_TOOLBAR_AVAILABLE = True
except ImportError:
    print("Warning: Fluent toolbar components not available")
    FLUENT_TOOLBAR_AVAILABLE = False

try:
    from components.composite.containers.panels import (
        FluentSettingsPanel, FluentPropertiesEditor, 
        FluentFormDialog, FluentConfirmationDialog
    )
    FLUENT_PANELS_AVAILABLE = True
except ImportError:
    print("Warning: Fluent panel components not available")
    FLUENT_PANELS_AVAILABLE = False

try:
    from components.layout.containers import FluentCard
    FLUENT_CARD_AVAILABLE = True
except ImportError:
    FLUENT_CARD_AVAILABLE = False


class FallbackNavigationWidget(QWidget):
    """Fallback navigation widget when fluent components are not available."""
    
    def __init__(self, navigation_type="sidebar"):
        super().__init__()
        self.navigation_type = navigation_type
        self.items = []
        self.current_item = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup fallback navigation UI."""
        layout = QVBoxLayout(self)
        
        if self.navigation_type == "sidebar":
            self.setFixedWidth(200)
            
            # Title
            title = QLabel("Navigation")
            title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # Navigation list
            self.nav_list = QListWidget()
            self.nav_list.itemClicked.connect(self.on_item_clicked)
            layout.addWidget(self.nav_list)
            
        elif self.navigation_type == "header":
            self.setFixedHeight(50)
            layout.setDirection(QHBoxLayout.Direction.LeftToRight)
            
            # Header items
            self.header_layout = QHBoxLayout()
            layout.addLayout(self.header_layout)
            
        elif self.navigation_type == "breadcrumb":
            self.setFixedHeight(30)
            layout.setDirection(QHBoxLayout.Direction.LeftToRight)
            
            # Breadcrumb items
            self.breadcrumb_layout = QHBoxLayout()
            layout.addLayout(self.breadcrumb_layout)
            
    def addItem(self, text, data=None):
        """Add navigation item."""
        self.items.append({"text": text, "data": data})
        
        if self.navigation_type == "sidebar":
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, data)
            self.nav_list.addItem(item)
        elif self.navigation_type == "header":
            btn = QPushButton(text)
            btn.clicked.connect(lambda: self.on_header_clicked(text, data))
            self.header_layout.addWidget(btn)
        elif self.navigation_type == "breadcrumb":
            if self.breadcrumb_layout.count() > 0:
                separator = QLabel(" > ")
                self.breadcrumb_layout.addWidget(separator)
            
            btn = QPushButton(text)
            btn.setFlat(True)
            btn.clicked.connect(lambda: self.on_breadcrumb_clicked(text, data))
            self.breadcrumb_layout.addWidget(btn)
            
    def on_item_clicked(self, item):
        """Handle navigation item click."""
        self.current_item = item.text()
        
    def on_header_clicked(self, text, data):
        """Handle header navigation click."""
        self.current_item = text
        
    def on_breadcrumb_clicked(self, text, data):
        """Handle breadcrumb navigation click."""
        self.current_item = text


class FallbackFormWidget(QWidget):
    """Fallback form widget when fluent components are not available."""
    
    def __init__(self):
        super().__init__()
        self.fields = {}
        self.validation_rules = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup fallback form UI."""
        self.layout = QVBoxLayout(self)
        
        # Form title
        self.title = QLabel("Form")
        self.title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.layout.addWidget(self.title)
        
        # Fields container
        self.fields_layout = QGridLayout()
        self.layout.addLayout(self.fields_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.submit_form)
        buttons_layout.addWidget(self.submit_btn)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_form)
        buttons_layout.addWidget(self.reset_btn)
        
        self.layout.addLayout(buttons_layout)
        
        # Validation feedback
        self.feedback_label = QLabel("")
        self.feedback_label.setWordWrap(True)
        self.layout.addWidget(self.feedback_label)
        
    def addField(self, name, label, field_type="text", required=False, validation=None):
        """Add a field to the form."""
        row = len(self.fields)
        
        # Label
        label_widget = QLabel(f"{label}:")
        if required:
            label_widget.setText(f"{label}*:")
            label_widget.setStyleSheet("color: red;")
        self.fields_layout.addWidget(label_widget, row, 0)
        
        # Field widget
        if field_type == "text":
            field_widget = QLineEdit()
        elif field_type == "number":
            field_widget = QSpinBox()
            field_widget.setRange(-999999, 999999)
        elif field_type == "checkbox":
            field_widget = QCheckBox()
        elif field_type == "combo":
            field_widget = QComboBox()
        else:
            field_widget = QLineEdit()
            
        self.fields_layout.addWidget(field_widget, row, 1)
        
        # Store field info
        self.fields[name] = {
            "widget": field_widget,
            "type": field_type,
            "required": required,
            "validation": validation
        }
        
    def submit_form(self):
        """Submit and validate form."""
        errors = []
        values = {}
        
        for name, field_info in self.fields.items():
            widget = field_info["widget"]
            required = field_info["required"]
            field_type = field_info["type"]
            
            # Get value
            if field_type == "text":
                value = widget.text()
            elif field_type == "number":
                value = widget.value()
            elif field_type == "checkbox":
                value = widget.isChecked()
            elif field_type == "combo":
                value = widget.currentText()
            else:
                value = widget.text() if hasattr(widget, 'text') else str(widget)
                
            values[name] = value
            
            # Validate required fields
            if required and not value:
                errors.append(f"{name} is required")
                
        # Show validation results
        if errors:
            self.feedback_label.setText("Errors: " + "; ".join(errors))
            self.feedback_label.setStyleSheet("color: red;")
        else:
            self.feedback_label.setText("Form submitted successfully!")
            self.feedback_label.setStyleSheet("color: green;")
            
        return values if not errors else None
        
    def reset_form(self):
        """Reset form to default values."""
        for name, field_info in self.fields.items():
            widget = field_info["widget"]
            field_type = field_info["type"]
            
            if field_type == "text":
                widget.clear()
            elif field_type == "number":
                widget.setValue(0)
            elif field_type == "checkbox":
                widget.setChecked(False)
            elif field_type == "combo":
                widget.setCurrentIndex(0)
                
        self.feedback_label.setText("")


class FallbackSettingsPanel(QWidget):
    """Fallback settings panel when fluent components are not available."""
    
    def __init__(self):
        super().__init__()
        self.settings = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup fallback settings panel UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Settings Panel")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Settings tree
        self.settings_tree = QTreeWidget()
        self.settings_tree.setHeaderLabels(["Setting", "Value"])
        self.settings_tree.itemDoubleClicked.connect(self.edit_setting)
        layout.addWidget(self.settings_tree)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(reset_btn)
        
        layout.addLayout(buttons_layout)
        
    def addSetting(self, category, name, value, description=""):
        """Add a setting to the panel."""
        # Find or create category
        category_item = None
        for i in range(self.settings_tree.topLevelItemCount()):
            item = self.settings_tree.topLevelItem(i)
            if item.text(0) == category:
                category_item = item
                break
                
        if not category_item:
            category_item = QTreeWidgetItem(self.settings_tree, [category, ""])
            category_item.setExpanded(True)
            
        # Add setting
        setting_item = QTreeWidgetItem(category_item, [name, str(value)])
        setting_item.setData(0, Qt.ItemDataRole.UserRole, {"category": category, "name": name, "value": value, "description": description})
        
        # Store in settings dict
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][name] = value
        
    def edit_setting(self, item, column):
        """Edit a setting value."""
        if item.parent() is not None:  # Only allow editing actual settings, not categories
            current_value = item.text(1)
            # Simple text edit for demo - in real implementation would use appropriate editor
            from PySide6.QtWidgets import QInputDialog
            new_value, ok = QInputDialog.getText(self, "Edit Setting", f"Enter new value for {item.text(0)}:", text=current_value)
            if ok:
                item.setText(1, new_value)
                data = item.data(0, Qt.ItemDataRole.UserRole)
                if data:
                    self.settings[data["category"]][data["name"]] = new_value
                    
    def save_settings(self):
        """Save current settings."""
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        
    def reset_settings(self):
        """Reset settings to defaults."""
        QMessageBox.information(self, "Settings", "Settings reset to defaults!")


class CompositeComponentsDemo(QMainWindow):
    """Main demo window showcasing composite components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Composite Components Demo")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Application state
        self.current_page = "Dashboard"
        self.user_data = {}
        self.settings_data = {}
        
        self.setup_ui()
        self.setup_navigation()
        self.setup_sample_data()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Create menu bar
        self.create_menu_bar()
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout with splitter
        main_layout = QHBoxLayout(main_widget)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left sidebar for navigation
        self.setup_sidebar(splitter)
        
        # Center content area
        self.setup_content_area(splitter)
        
        # Right panel for properties/tools
        self.setup_right_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([200, 1000, 300])
        
        # Status bar
        self.setup_status_bar()
        
    def create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        sidebar_action = QAction("Toggle Sidebar", self)
        sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(sidebar_action)
        
        properties_action = QAction("Toggle Properties Panel", self)
        properties_action.triggered.connect(self.toggle_properties_panel)
        view_menu.addAction(properties_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_sidebar(self, parent):
        """Setup left sidebar navigation."""
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        
        # Sidebar title
        title = QLabel("Navigation")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title)
        
        # Navigation component
        if FLUENT_NAVIGATION_AVAILABLE:
            try:
                self.sidebar = FluentSidebar()
            except Exception as e:
                print(f"Error creating FluentSidebar: {e}")
                self.sidebar = FallbackNavigationWidget("sidebar")
        else:
            self.sidebar = FallbackNavigationWidget("sidebar")
            
        sidebar_layout.addWidget(self.sidebar)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        new_form_btn = QPushButton("New Form")
        new_form_btn.clicked.connect(self.create_new_form)
        actions_layout.addWidget(new_form_btn)
        
        import_data_btn = QPushButton("Import Data")
        import_data_btn.clicked.connect(self.import_data)
        actions_layout.addWidget(import_data_btn)
        
        export_data_btn = QPushButton("Export Data")
        export_data_btn.clicked.connect(self.export_data)
        actions_layout.addWidget(export_data_btn)
        
        sidebar_layout.addWidget(actions_group)
        
        parent.addWidget(sidebar_widget)
        self.sidebar_widget = sidebar_widget
        
    def setup_content_area(self, parent):
        """Setup center content area."""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Header navigation
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        
        # Title and breadcrumb
        title_layout = QHBoxLayout()
        
        self.page_title = QLabel("Dashboard")
        self.page_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_layout.addWidget(self.page_title)
        
        title_layout.addStretch()
        
        # Quick settings
        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.show_settings)
        title_layout.addWidget(settings_btn)
        
        header_layout.addLayout(title_layout)
        
        # Breadcrumb navigation
        if FLUENT_NAVIGATION_AVAILABLE:
            try:
                self.breadcrumb = FluentBreadcrumbBar()
            except Exception as e:
                print(f"Error creating FluentBreadcrumbBar: {e}")
                self.breadcrumb = FallbackNavigationWidget("breadcrumb")
        else:
            self.breadcrumb = FallbackNavigationWidget("breadcrumb")
            
        header_layout.addWidget(self.breadcrumb)
        
        content_layout.addWidget(header_widget)
        
        # Main content stack
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        # Create different content pages
        self.create_dashboard_page()
        self.create_forms_page()
        self.create_data_page()
        self.create_settings_page()
        
        parent.addWidget(content_widget)
        
    def setup_right_panel(self, parent):
        """Setup right properties/tools panel."""
        panel_widget = QWidget()
        panel_layout = QVBoxLayout(panel_widget)
        
        # Panel title
        title = QLabel("Properties & Tools")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(title)
        
        # Properties editor
        if FLUENT_PANELS_AVAILABLE:
            try:
                self.properties_panel = FluentPropertiesEditor()
            except Exception as e:
                print(f"Error creating FluentPropertiesEditor: {e}")
                self.properties_panel = FallbackSettingsPanel()
        else:
            self.properties_panel = FallbackSettingsPanel()
            
        panel_layout.addWidget(self.properties_panel)
        
        # Tools section
        tools_group = QGroupBox("Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        validate_btn = QPushButton("Validate Data")
        validate_btn.clicked.connect(self.validate_data)
        tools_layout.addWidget(validate_btn)
        
        analyze_btn = QPushButton("Analyze")
        analyze_btn.clicked.connect(self.analyze_data)
        tools_layout.addWidget(analyze_btn)
        
        report_btn = QPushButton("Generate Report")
        report_btn.clicked.connect(self.generate_report)
        tools_layout.addWidget(report_btn)
        
        panel_layout.addWidget(tools_group)
        
        parent.addWidget(panel_widget)
        self.properties_widget = panel_widget
        
    def setup_status_bar(self):
        """Setup status bar."""
        status_bar = self.statusBar()
        
        # Main status message
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)
        
        # Progress indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        status_bar.addPermanentWidget(self.progress_bar)
        
        # Connection status
        self.connection_label = QLabel("Connected")
        self.connection_label.setStyleSheet("color: green;")
        status_bar.addPermanentWidget(self.connection_label)
        
        # Time
        self.time_label = QLabel()
        self.update_time()
        status_bar.addPermanentWidget(self.time_label)
        
        # Timer for time updates
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        
    def setup_navigation(self):
        """Setup navigation items."""
        # Add navigation items
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Forms", "forms"),
            ("Data Management", "data"),
            ("Reports", "reports"),
            ("Settings", "settings"),
            ("Help", "help")
        ]
        
        for text, data in nav_items:
            self.sidebar.addItem(text, data)
            
        # Add breadcrumb items
        self.breadcrumb.addItem("Home", "home")
        self.breadcrumb.addItem("Dashboard", "dashboard")
        
    def setup_sample_data(self):
        """Setup sample data for demonstration."""
        # Sample user data
        self.user_data = {
            "profile": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "role": "Administrator",
                "department": "IT"
            },
            "preferences": {
                "theme": "Light",
                "language": "English",
                "notifications": True,
                "auto_save": True
            }
        }
        
        # Sample settings
        self.settings_data = {
            "General": {
                "Application Name": "Composite Demo",
                "Version": "1.0.0",
                "Auto Update": True,
                "Check for Updates": True
            },
            "Interface": {
                "Theme": "Fluent Light",
                "Font Size": 12,
                "Show Tooltips": True,
                "Animation Speed": "Normal"
            },
            "Performance": {
                "Cache Size": 100,
                "Max Threads": 4,
                "Hardware Acceleration": True,
                "Memory Limit": 1024
            }
        }
        
        # Populate properties panel
        if hasattr(self.properties_panel, 'addSetting'):
            for category, settings in self.settings_data.items():
                for name, value in settings.items():
                    self.properties_panel.addSetting(category, name, value)
                    
    def create_dashboard_page(self):
        """Create dashboard content page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Welcome section
        welcome_group = QGroupBox("Welcome to Composite Components Demo")
        welcome_layout = QVBoxLayout(welcome_group)
        
        welcome_text = QLabel(
            "This demo showcases advanced composite components including:\\n\\n"
            "• Complex form systems with validation\\n"
            "• Navigation and interface components\\n"
            "• Settings and properties panels\\n"
            "• Dialog and container management\\n"
            "• Workflow integration\\n\\n"
            "Navigate using the sidebar to explore different features."
        )
        welcome_text.setWordWrap(True)
        welcome_layout.addWidget(welcome_text)
        
        layout.addWidget(welcome_group)
        
        # Quick stats
        stats_group = QGroupBox("Quick Statistics")
        stats_layout = QGridLayout(stats_group)
        
        # Create stat cards
        stats = [
            ("Active Forms", "5", QColor(100, 150, 255)),
            ("Total Records", "1,234", QColor(150, 255, 100)),
            ("Validation Errors", "2", QColor(255, 100, 100)),
            ("System Health", "98%", QColor(100, 255, 150))
        ]
        
        for i, (label, value, color) in enumerate(stats):
            card = self.create_stat_card(label, value, color)
            stats_layout.addWidget(card, i // 2, i % 2)
            
        layout.addWidget(stats_group)
        
        # Recent activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        activity_list = QListWidget()
        activities = [
            "Form 'User Registration' was created",
            "Data validation completed successfully",
            "Settings were updated by admin",
            "New user 'Jane Smith' was added",
            "Report 'Monthly Summary' was generated"
        ]
        
        for activity in activities:
            item = QListWidgetItem(activity)
            activity_list.addItem(item)
            
        activity_layout.addWidget(activity_list)
        layout.addWidget(activity_group)
        
        layout.addStretch()
        self.content_stack.addWidget(page)
        
    def create_forms_page(self):
        """Create forms demonstration page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Form creation section
        creation_group = QGroupBox("Form Creation and Management")
        creation_layout = QHBoxLayout(creation_group)
        
        # Form builder
        builder_widget = QWidget()
        builder_layout = QVBoxLayout(builder_widget)
        
        builder_title = QLabel("Form Builder")
        builder_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        builder_layout.addWidget(builder_title)
        
        # Sample form
        if FLUENT_FORMS_AVAILABLE:
            try:
                self.sample_form = FluentValidationForm()
            except Exception as e:
                print(f"Error creating FluentValidationForm: {e}")
                self.sample_form = FallbackFormWidget()
        else:
            self.sample_form = FallbackFormWidget()
            
        # Add form fields
        if hasattr(self.sample_form, 'addField'):
            self.sample_form.addField("name", "Full Name", "text", required=True)
            self.sample_form.addField("email", "Email Address", "text", required=True)
            self.sample_form.addField("age", "Age", "number")
            self.sample_form.addField("subscribe", "Subscribe to Newsletter", "checkbox")
            self.sample_form.addField("department", "Department", "combo")
            
        builder_layout.addWidget(self.sample_form)
        creation_layout.addWidget(builder_widget)
        
        # Form templates
        templates_widget = QWidget()
        templates_layout = QVBoxLayout(templates_widget)
        
        templates_title = QLabel("Form Templates")
        templates_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        templates_layout.addWidget(templates_title)
        
        template_list = QListWidget()
        templates = [
            "User Registration",
            "Contact Form",
            "Survey Form",
            "Feedback Form",
            "Order Form",
            "Application Form"
        ]
        
        for template in templates:
            item = QListWidgetItem(template)
            template_list.addItem(item)
            
        template_list.itemDoubleClicked.connect(self.load_form_template)
        templates_layout.addWidget(template_list)
        
        load_template_btn = QPushButton("Load Selected Template")
        load_template_btn.clicked.connect(self.load_selected_template)
        templates_layout.addWidget(load_template_btn)
        
        creation_layout.addWidget(templates_widget)
        layout.addWidget(creation_group)
        
        # Form validation section
        validation_group = QGroupBox("Form Validation and Testing")
        validation_layout = QVBoxLayout(validation_group)
        
        validation_controls = QHBoxLayout()
        
        validate_btn = QPushButton("Validate Form")
        validate_btn.clicked.connect(self.validate_form)
        validation_controls.addWidget(validate_btn)
        
        test_btn = QPushButton("Test Form Submission")
        test_btn.clicked.connect(self.test_form_submission)
        validation_controls.addWidget(test_btn)
        
        clear_btn = QPushButton("Clear Form")
        clear_btn.clicked.connect(self.clear_form)
        validation_controls.addWidget(clear_btn)
        
        validation_layout.addLayout(validation_controls)
        
        # Validation results
        self.validation_results = QTextEdit()
        self.validation_results.setMaximumHeight(100)
        self.validation_results.setReadOnly(True)
        validation_layout.addWidget(self.validation_results)
        
        layout.addWidget(validation_group)
        
        self.content_stack.addWidget(page)
        
    def create_data_page(self):
        """Create data management page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Data overview
        overview_group = QGroupBox("Data Overview")
        overview_layout = QVBoxLayout(overview_group)
        
        overview_text = QLabel(
            "This section demonstrates data management capabilities including:\\n"
            "• Data validation and integrity checking\\n"
            "• Import/export functionality\\n"
            "• Real-time data updates\\n"
            "• Data visualization and analysis"
        )
        overview_layout.addWidget(overview_text)
        
        layout.addWidget(overview_group)
        
        # Data operations
        operations_group = QGroupBox("Data Operations")
        operations_layout = QGridLayout(operations_group)
        
        # Import section
        operations_layout.addWidget(QLabel("Import Data:"), 0, 0)
        import_btn = QPushButton("Import from CSV")
        import_btn.clicked.connect(self.import_csv_data)
        operations_layout.addWidget(import_btn, 0, 1)
        
        import_json_btn = QPushButton("Import from JSON")
        import_json_btn.clicked.connect(self.import_json_data)
        operations_layout.addWidget(import_json_btn, 0, 2)
        
        # Export section
        operations_layout.addWidget(QLabel("Export Data:"), 1, 0)
        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_csv_data)
        operations_layout.addWidget(export_btn, 1, 1)
        
        export_json_btn = QPushButton("Export to JSON")
        export_json_btn.clicked.connect(self.export_json_data)
        operations_layout.addWidget(export_json_btn, 1, 2)
        
        # Analysis section
        operations_layout.addWidget(QLabel("Analysis:"), 2, 0)
        analyze_btn = QPushButton("Analyze Data")
        analyze_btn.clicked.connect(self.analyze_data)
        operations_layout.addWidget(analyze_btn, 2, 1)
        
        report_btn = QPushButton("Generate Report")
        report_btn.clicked.connect(self.generate_report)
        operations_layout.addWidget(report_btn, 2, 2)
        
        layout.addWidget(operations_group)
        
        # Data display
        display_group = QGroupBox("Data Display")
        display_layout = QVBoxLayout(display_group)
        
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)
        self.data_display.setText("Sample data will be displayed here after import or generation...")
        display_layout.addWidget(self.data_display)
        
        layout.addWidget(display_group)
        
        self.content_stack.addWidget(page)
        
    def create_settings_page(self):
        """Create settings page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Settings overview
        overview_group = QGroupBox("Application Settings")
        overview_layout = QVBoxLayout(overview_group)
        
        overview_text = QLabel(
            "Configure application settings and preferences. Changes are applied immediately "
            "and saved automatically."
        )
        overview_layout.addWidget(overview_text)
        
        layout.addWidget(overview_group)
        
        # Settings panel
        if FLUENT_PANELS_AVAILABLE:
            try:
                self.settings_panel = FluentSettingsPanel()
            except Exception as e:
                print(f"Error creating FluentSettingsPanel: {e}")
                self.settings_panel = FallbackSettingsPanel()
        else:
            self.settings_panel = FallbackSettingsPanel()
            
        # Populate settings
        if hasattr(self.settings_panel, 'addSetting'):
            for category, settings in self.settings_data.items():
                for name, value in settings.items():
                    self.settings_panel.addSetting(category, name, value, f"Configuration for {name}")
                    
        layout.addWidget(self.settings_panel)
        
        # Settings actions
        actions_layout = QHBoxLayout()
        
        export_settings_btn = QPushButton("Export Settings")
        export_settings_btn.clicked.connect(self.export_settings)
        actions_layout.addWidget(export_settings_btn)
        
        import_settings_btn = QPushButton("Import Settings")
        import_settings_btn.clicked.connect(self.import_settings)
        actions_layout.addWidget(import_settings_btn)
        
        reset_settings_btn = QPushButton("Reset to Defaults")
        reset_settings_btn.clicked.connect(self.reset_all_settings)
        actions_layout.addWidget(reset_settings_btn)
        
        layout.addLayout(actions_layout)
        
        self.content_stack.addWidget(page)
        
    def create_stat_card(self, label, value, color):
        """Create a statistics card widget."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setStyleSheet(f"QFrame {{ background-color: {color.name()}; border-radius: 5px; padding: 10px; }}")
        
        layout = QVBoxLayout(card)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("color: white;")
        layout.addWidget(value_label)
        
        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_widget.setStyleSheet("color: white;")
        layout.addWidget(label_widget)
        
        return card
        
    def update_time(self):
        """Update time display in status bar."""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)
        
    # Event handlers and actions
    def new_file(self):
        """Create new file."""
        self.status_label.setText("New file created")
        
    def open_file(self):
        """Open file."""
        self.status_label.setText("File opened")
        
    def save_file(self):
        """Save file."""
        self.status_label.setText("File saved")
        
    def toggle_sidebar(self):
        """Toggle sidebar visibility."""
        self.sidebar_widget.setVisible(not self.sidebar_widget.isVisible())
        
    def toggle_properties_panel(self):
        """Toggle properties panel visibility."""
        self.properties_widget.setVisible(not self.properties_widget.isVisible())
        
    def show_settings(self):
        """Show settings page."""
        self.content_stack.setCurrentIndex(3)  # Settings page index
        self.page_title.setText("Settings")
        
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About", 
                         "Composite Components Demo\\n\\n"
                         "Demonstrates advanced composite UI components\\n"
                         "Built with PySide6 and Fluent Design principles")
        
    def create_new_form(self):
        """Create new form."""
        self.content_stack.setCurrentIndex(1)  # Forms page index
        self.page_title.setText("Forms")
        self.status_label.setText("Form creation mode activated")
        
    def import_data(self):
        """Import data."""
        self.content_stack.setCurrentIndex(2)  # Data page index
        self.page_title.setText("Data Management")
        self.status_label.setText("Data import mode activated")
        
    def export_data(self):
        """Export data."""
        self.status_label.setText("Data exported successfully")
        
    def validate_data(self):
        """Validate current data."""
        self.status_label.setText("Data validation completed")
        
    def analyze_data(self):
        """Analyze current data."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        
        # Simulate analysis progress
        self.analysis_progress = 0
        self.analysis_timer = QTimer()
        self.analysis_timer.timeout.connect(self.update_analysis_progress)
        self.analysis_timer.start(50)
        
        self.status_label.setText("Analyzing data...")
        
    def update_analysis_progress(self):
        """Update analysis progress."""
        self.analysis_progress += 2
        self.progress_bar.setValue(self.analysis_progress)
        
        if self.analysis_progress >= 100:
            self.analysis_timer.stop()
            self.progress_bar.setVisible(False)
            self.status_label.setText("Data analysis completed")
            QMessageBox.information(self, "Analysis Complete", "Data analysis has been completed successfully!")
            
    def generate_report(self):
        """Generate report."""
        self.status_label.setText("Report generated successfully")
        
    def load_form_template(self, item):
        """Load selected form template."""
        template_name = item.text()
        self.status_label.setText(f"Loaded template: {template_name}")
        
    def load_selected_template(self):
        """Load selected form template."""
        self.status_label.setText("Form template loaded")
        
    def validate_form(self):
        """Validate form."""
        if hasattr(self.sample_form, 'submit_form'):
            result = self.sample_form.submit_form()
            if result:
                self.validation_results.setText(f"Form validation successful. Data: {result}")
            else:
                self.validation_results.setText("Form validation failed. Please check required fields.")
        else:
            self.validation_results.setText("Form validation completed (demo mode)")
            
    def test_form_submission(self):
        """Test form submission."""
        self.validation_results.setText("Form submission test completed successfully")
        
    def clear_form(self):
        """Clear form."""
        if hasattr(self.sample_form, 'reset_form'):
            self.sample_form.reset_form()
        self.validation_results.clear()
        self.status_label.setText("Form cleared")
        
    def import_csv_data(self):
        """Import CSV data."""
        sample_data = "Name,Age,Department\\nJohn Doe,30,IT\\nJane Smith,25,Marketing\\nBob Johnson,35,Sales"
        self.data_display.setText(f"Imported CSV data:\\n{sample_data}")
        self.status_label.setText("CSV data imported")
        
    def import_json_data(self):
        """Import JSON data."""
        sample_data = {
            "users": [
                {"name": "John Doe", "age": 30, "department": "IT"},
                {"name": "Jane Smith", "age": 25, "department": "Marketing"}
            ]
        }
        self.data_display.setText(f"Imported JSON data:\\n{json.dumps(sample_data, indent=2)}")
        self.status_label.setText("JSON data imported")
        
    def export_csv_data(self):
        """Export CSV data."""
        self.status_label.setText("Data exported to CSV format")
        
    def export_json_data(self):
        """Export JSON data."""
        self.status_label.setText("Data exported to JSON format")
        
    def export_settings(self):
        """Export settings."""
        settings_json = json.dumps(self.settings_data, indent=2)
        QMessageBox.information(self, "Settings Export", f"Settings exported:\\n{settings_json[:200]}...")
        
    def import_settings(self):
        """Import settings."""
        QMessageBox.information(self, "Settings Import", "Settings import completed successfully")
        
    def reset_all_settings(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(self, "Reset Settings", 
                                   "Are you sure you want to reset all settings to defaults?")
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Settings Reset", "All settings have been reset to defaults")


def main():
    """Main function to run the demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Composite Components Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Simple Fluent Widget")
    
    # Create and show the demo
    demo = CompositeComponentsDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
