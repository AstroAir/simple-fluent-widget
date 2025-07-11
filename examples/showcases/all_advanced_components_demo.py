"""
All Advanced Components Demo

This demo showcases ALL advanced components in a single comprehensive application:
- Advanced forms with validation
- Menu systems and command palette  
- Advanced charts and visualizations
- Property grids and settings panels
- JSON viewer and editor
- Integration with existing components
"""

import sys
import os
import json
import random
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QStackedWidget, QSplitter, QTextEdit, QScrollArea)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all advanced components
from components.data.forms import FluentFormField, FluentForm, FluentMultiStepForm
from components.command.menus import FluentMenu, FluentContextMenu, FluentCommandPalette, FluentRibbon, FluentRibbonTab
from components.data.advanced_charts import FluentAreaChart, FluentScatterChart, FluentHeatMap
from components.data.property_grid import FluentPropertyGrid, FluentSettingsPanel, FluentPropertyItem, PropertyType
from components.data.json_viewer import FluentJsonViewer, FluentJsonTreeWidget

# Import existing components
from components.basic.card import FluentCard
from components.basic.button import FluentPushButton
from components.basic.label import FluentLabel
from components.navigation.tab import FluentTabWidget
from theme.theme_manager import theme_manager


class AllAdvancedComponentsDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("All Advanced Components Demo - Complete Fluent UI Showcase")
        self.setGeometry(50, 50, 1900, 1100)
        
        # Apply theme
        theme_manager.apply_theme(self)
        
        # Sample data for demonstrations
        self.sample_settings = {}
        self.sample_json_data = {}
        
        self.setup_ui()
        self.setup_command_palette()
        self.load_all_sample_data()
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh_data)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Setup ribbon
        self.setup_ribbon(main_layout)
        
        # Create main content with splitter
        self.setup_main_content(main_layout)
        
    def setup_ribbon(self, parent_layout):
        """Setup comprehensive ribbon interface"""
        self.ribbon = FluentRibbon()
        
        # Data Management tab
        data_tab = FluentRibbonTab("Data")
        data_tab.add_group("Import/Export")
        data_tab.add_command("Import/Export", "Import JSON", "Import JSON data", self.import_json_data)
        data_tab.add_command("Import/Export", "Export JSON", "Export current data", self.export_json_data)
        data_tab.add_command("Import/Export", "Load Settings", "Load configuration", self.load_settings)
        data_tab.add_command("Import/Export", "Save Settings", "Save configuration", self.save_settings)
        
        data_tab.add_group("Data Operations")
        data_tab.add_command("Data Operations", "Refresh All", "Refresh all data", self.refresh_all_data)
        data_tab.add_command("Data Operations", "Generate Sample", "Generate sample data", self.generate_sample_data)
        data_tab.add_command("Data Operations", "Clear All", "Clear all data", self.clear_all_data)
        data_tab.add_command("Data Operations", "Validate", "Validate all data", self.validate_all_data)
        
        self.ribbon.add_tab(data_tab)
        
        # Analytics tab
        analytics_tab = FluentRibbonTab("Analytics")
        analytics_tab.add_group("Visualizations")
        analytics_tab.add_command("Visualizations", "Area Chart", "Show area chart", lambda: self.switch_to_section("charts", 0))
        analytics_tab.add_command("Visualizations", "Scatter Plot", "Show scatter plot", lambda: self.switch_to_section("charts", 1))
        analytics_tab.add_command("Visualizations", "Heat Map", "Show heat map", lambda: self.switch_to_section("charts", 2))
        analytics_tab.add_command("Visualizations", "Dashboard", "Show dashboard", lambda: self.switch_to_section("overview", 0))
        
        analytics_tab.add_group("Analysis Tools")
        analytics_tab.add_command("Analysis Tools", "Statistics", "Show statistics", self.show_statistics)
        analytics_tab.add_command("Analysis Tools", "Correlations", "Find correlations", self.analyze_correlations)
        analytics_tab.add_command("Analysis Tools", "Trends", "Analyze trends", self.analyze_trends)
        analytics_tab.add_command("Analysis Tools", "Export Report", "Export analysis report", self.export_report)
        
        self.ribbon.add_tab(analytics_tab)
        
        # Forms & Input tab
        forms_tab = FluentRibbonTab("Forms")
        forms_tab.add_group("Form Types")
        forms_tab.add_command("Form Types", "Simple Form", "Create simple form", lambda: self.switch_to_section("forms", 0))
        forms_tab.add_command("Form Types", "Wizard Form", "Create wizard", lambda: self.switch_to_section("forms", 1))
        forms_tab.add_command("Form Types", "Validation Demo", "Show validation", lambda: self.switch_to_section("forms", 2))
        
        forms_tab.add_group("Form Operations")
        forms_tab.add_command("Form Operations", "Validate All", "Validate all forms", self.validate_all_forms)
        forms_tab.add_command("Form Operations", "Reset Forms", "Reset all forms", self.reset_all_forms)
        forms_tab.add_command("Form Operations", "Submit All", "Submit all forms", self.submit_all_forms)
        
        self.ribbon.add_tab(forms_tab)
        
        # Configuration tab
        config_tab = FluentRibbonTab("Configuration")
        config_tab.add_group("Settings")
        config_tab.add_command("Settings", "Properties", "Show property grid", lambda: self.switch_to_section("config", 0))
        config_tab.add_command("Settings", "Settings Panel", "Show settings", lambda: self.switch_to_section("config", 1))
        config_tab.add_command("Settings", "JSON Editor", "Edit JSON", lambda: self.switch_to_section("config", 2))
        
        config_tab.add_group("Configuration Management")
        config_tab.add_command("Configuration Management", "Import Config", "Import configuration", self.import_configuration)
        config_tab.add_command("Configuration Management", "Export Config", "Export configuration", self.export_configuration)
        config_tab.add_command("Configuration Management", "Reset Config", "Reset to defaults", self.reset_configuration)
        
        self.ribbon.add_tab(config_tab)
        
        # View tab
        view_tab = FluentRibbonTab("View")
        view_tab.add_group("Layout")
        view_tab.add_command("Layout", "Split Horizontal", "Split view horizontally", self.split_horizontal)
        view_tab.add_command("Layout", "Split Vertical", "Split view vertically", self.split_vertical)
        view_tab.add_command("Layout", "Single Pane", "Show single pane", self.single_pane)
        view_tab.add_command("Layout", "Full Screen", "Toggle full screen", self.toggle_fullscreen)
        
        view_tab.add_group("Theme")
        view_tab.add_command("Theme", "Light Mode", "Switch to light theme", self.set_light_theme)
        view_tab.add_command("Theme", "Dark Mode", "Switch to dark theme", self.set_dark_theme)
        view_tab.add_command("Theme", "Auto Theme", "Auto theme selection", self.set_auto_theme)
        
        self.ribbon.add_tab(view_tab)
        
        parent_layout.addWidget(self.ribbon)
        
    def setup_main_content(self, parent_layout):
        """Setup main content with splitter"""
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Navigation and overview
        self.left_panel = self.create_left_panel()
        self.main_splitter.addWidget(self.left_panel)
        
        # Right panel - Detailed views
        self.right_panel = self.create_right_panel()
        self.main_splitter.addWidget(self.right_panel)
        
        # Set splitter sizes (30% left, 70% right)
        self.main_splitter.setSizes([400, 1200])
        
        parent_layout.addWidget(self.main_splitter)
        
    def create_left_panel(self):
        """Create left navigation panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Title
        title = FluentLabel("Component Showcase")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Quick stats card
        stats_card = self.create_stats_card()
        layout.addWidget(stats_card)
        
        # Navigation buttons
        nav_card = FluentCard()
        nav_layout = QVBoxLayout(nav_card)
        
        nav_title = FluentLabel("Navigation")
        nav_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        nav_layout.addWidget(nav_title)
        
        # Create navigation buttons
        nav_buttons = [
            ("📊 Charts & Analytics", lambda: self.switch_to_section("charts", 0)),
            ("📝 Forms & Input", lambda: self.switch_to_section("forms", 0)),
            ("⚙️ Configuration", lambda: self.switch_to_section("config", 0)),
            ("🎛️ Property Editor", lambda: self.switch_to_section("config", 0)),
            ("📋 JSON Viewer", lambda: self.switch_to_section("config", 2)),
            ("🎨 Settings Panel", lambda: self.switch_to_section("config", 1)),
        ]
        
        for text, callback in nav_buttons:
            btn = FluentPushButton(text)
            btn.clicked.connect(callback)
            nav_layout.addWidget(btn)
            
        layout.addWidget(nav_card)
        
        # Command palette button
        palette_card = FluentCard()
        palette_layout = QVBoxLayout(palette_card)
        
        palette_title = FluentLabel("Quick Actions")
        palette_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        palette_layout.addWidget(palette_title)
        
        palette_btn = FluentPushButton("🔍 Open Command Palette")
        palette_btn.clicked.connect(self.show_command_palette)
        palette_layout.addWidget(palette_btn)
        
        refresh_btn = FluentPushButton("🔄 Refresh All Data")
        refresh_btn.clicked.connect(self.refresh_all_data)
        palette_layout.addWidget(refresh_btn)
        
        layout.addWidget(palette_card)
        
        layout.addStretch()
        
        return panel
        
    def create_stats_card(self):
        """Create quick statistics card"""
        card = FluentCard()
        layout = QVBoxLayout(card)
        
        title = FluentLabel("Quick Stats")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Create mini visualizations
        self.stats_area_chart = FluentAreaChart()
        self.stats_area_chart.setMaximumHeight(80)
        layout.addWidget(self.stats_area_chart)
        
        # Stats labels
        stats_layout = QHBoxLayout()
        
        self.total_items_label = FluentLabel("Items: 0")
        stats_layout.addWidget(self.total_items_label)
        
        self.avg_value_label = FluentLabel("Avg: 0")
        stats_layout.addWidget(self.avg_value_label)
        
        layout.addLayout(stats_layout)
        
        return card
        
    def create_right_panel(self):
        """Create right panel with detailed views"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        
        # Create tab widget for different sections
        self.main_tabs = FluentTabWidget()
        
        # Overview tab
        overview_tab = self.create_overview_tab()
        self.main_tabs.addTab(overview_tab, "📈 Overview")
        
        # Charts tab
        charts_tab = self.create_charts_tab()
        self.main_tabs.addTab(charts_tab, "📊 Charts")
        
        # Forms tab
        forms_tab = self.create_forms_tab()
        self.main_tabs.addTab(forms_tab, "📝 Forms")
        
        # Configuration tab
        config_tab = self.create_configuration_tab()
        self.main_tabs.addTab(config_tab, "⚙️ Configuration")
        
        layout.addWidget(self.main_tabs)
        
        return panel
        
    def create_overview_tab(self):
        """Create overview dashboard tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Welcome section
        welcome_card = FluentCard()
        welcome_layout = QVBoxLayout(welcome_card)
        
        title = FluentLabel("Advanced Components Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        welcome_layout.addWidget(title)
        
        subtitle = FluentLabel("Complete showcase of all advanced Fluent UI components")
        subtitle.setStyleSheet("font-size: 14px; color: #666; margin-bottom: 20px;")
        welcome_layout.addWidget(subtitle)
        
        # Feature overview
        features_layout = QHBoxLayout()
        
        features = [
            ("Advanced Forms", "✓ Validation\n✓ Multi-step wizards\n✓ Custom field types"),
            ("Data Visualization", "✓ Area charts\n✓ Scatter plots\n✓ Heat maps"),
            ("Configuration", "✓ Property grids\n✓ Settings panels\n✓ JSON editing"),
            ("Command Interface", "✓ Ribbon UI\n✓ Context menus\n✓ Command palette")
        ]
        
        for feature_name, feature_desc in features:
            feature_card = FluentCard()
            feature_layout = QVBoxLayout(feature_card)
            
            feature_title = FluentLabel(feature_name)
            feature_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 8px;")
            feature_layout.addWidget(feature_title)
            
            feature_text = FluentLabel(feature_desc)
            feature_text.setStyleSheet("font-size: 12px; color: #666;")
            feature_layout.addWidget(feature_text)
            
            features_layout.addWidget(feature_card)
            
        welcome_layout.addLayout(features_layout)
        layout.addWidget(welcome_card)
        
        # Live dashboard
        dashboard_card = FluentCard()
        dashboard_layout = QVBoxLayout(dashboard_card)
        
        dashboard_title = FluentLabel("Live Data Dashboard")
        dashboard_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        dashboard_layout.addWidget(dashboard_title)
        
        # Create dashboard charts
        charts_layout = QHBoxLayout()
        
        self.dashboard_area_chart = FluentAreaChart()
        self.dashboard_area_chart.setMinimumHeight(200)
        charts_layout.addWidget(self.dashboard_area_chart)
        
        self.dashboard_scatter_chart = FluentScatterChart()
        self.dashboard_scatter_chart.setMinimumHeight(200)
        charts_layout.addWidget(self.dashboard_scatter_chart)
        
        dashboard_layout.addLayout(charts_layout)
        
        self.dashboard_heat_map = FluentHeatMap()
        self.dashboard_heat_map.setMinimumHeight(150)
        dashboard_layout.addWidget(self.dashboard_heat_map)
        
        layout.addWidget(dashboard_card)
        
        return widget
        
    def create_charts_tab(self):
        """Create charts demonstration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create sub-tabs for different chart types
        charts_tabs = FluentTabWidget()
        
        # Area chart tab
        area_tab = QWidget()
        area_layout = QVBoxLayout(area_tab)
        area_layout.setContentsMargins(20, 20, 20, 20)
        
        area_controls = QHBoxLayout()
        area_title = FluentLabel("Area Chart - Sales Performance")
        area_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        area_controls.addWidget(area_title)
        area_controls.addStretch()
        
        area_refresh_btn = FluentPushButton("Refresh Data")
        area_refresh_btn.clicked.connect(self.refresh_area_chart)
        area_controls.addWidget(area_refresh_btn)
        
        area_layout.addLayout(area_controls)
        
        self.main_area_chart = FluentAreaChart()
        self.main_area_chart.setMinimumHeight(400)
        area_layout.addWidget(self.main_area_chart)
        
        charts_tabs.addTab(area_tab, "Area Chart")
        
        # Scatter chart tab  
        scatter_tab = QWidget()
        scatter_layout = QVBoxLayout(scatter_tab)
        scatter_layout.setContentsMargins(20, 20, 20, 20)
        
        scatter_controls = QHBoxLayout()
        scatter_title = FluentLabel("Scatter Chart - Customer Analysis")
        scatter_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        scatter_controls.addWidget(scatter_title)
        scatter_controls.addStretch()
        
        scatter_refresh_btn = FluentPushButton("Generate Data")
        scatter_refresh_btn.clicked.connect(self.refresh_scatter_chart)
        scatter_controls.addWidget(scatter_refresh_btn)
        
        scatter_trend_btn = FluentPushButton("Toggle Trend")
        scatter_trend_btn.clicked.connect(self.toggle_scatter_trend)
        scatter_controls.addWidget(scatter_trend_btn)
        
        scatter_layout.addLayout(scatter_controls)
        
        self.main_scatter_chart = FluentScatterChart()
        self.main_scatter_chart.setMinimumHeight(400)
        scatter_layout.addWidget(self.main_scatter_chart)
        
        charts_tabs.addTab(scatter_tab, "Scatter Chart")
        
        # Heat map tab
        heatmap_tab = QWidget()
        heatmap_layout = QVBoxLayout(heatmap_tab)
        heatmap_layout.setContentsMargins(20, 20, 20, 20)
        
        heatmap_controls = QHBoxLayout()
        heatmap_title = FluentLabel("Heat Map - Performance Matrix")
        heatmap_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        heatmap_controls.addWidget(heatmap_title)
        heatmap_controls.addStretch()
        
        heatmap_refresh_btn = FluentPushButton("Refresh Data")
        heatmap_refresh_btn.clicked.connect(self.refresh_heat_map)
        heatmap_controls.addWidget(heatmap_refresh_btn)
        
        heatmap_values_btn = FluentPushButton("Toggle Values")
        heatmap_values_btn.clicked.connect(self.toggle_heatmap_values)
        heatmap_controls.addWidget(heatmap_values_btn)
        
        heatmap_layout.addLayout(heatmap_controls)
        
        self.main_heat_map = FluentHeatMap()
        self.main_heat_map.setMinimumHeight(400)
        heatmap_layout.addWidget(self.main_heat_map)
        
        charts_tabs.addTab(heatmap_tab, "Heat Map")
        
        layout.addWidget(charts_tabs)
        return widget
        
    def create_forms_tab(self):
        """Create forms demonstration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create sub-tabs for different form types
        forms_tabs = FluentTabWidget()
        
        # Simple form tab
        simple_form_tab = QWidget()
        simple_layout = QVBoxLayout(simple_form_tab)
        simple_layout.setContentsMargins(20, 20, 20, 20)
        
        simple_title = FluentLabel("Simple Form with Validation")
        simple_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        simple_layout.addWidget(simple_title)
        
        # Create simple form
        self.simple_form = FluentForm("User Registration")
        self.simple_form.add_field("text", "first_name", "First Name", required=True)
        self.simple_form.add_field("text", "last_name", "Last Name", required=True)
        self.simple_form.add_field("email", "email", "Email Address", required=True)
        self.simple_form.add_field("password", "password", "Password", required=True)
        self.simple_form.add_field("date", "birth_date", "Birth Date")
        self.simple_form.add_field("text", "phone", "Phone Number")
        
        self.simple_form.form_submitted.connect(self.handle_simple_form_submission)
        simple_layout.addWidget(self.simple_form)
        
        forms_tabs.addTab(simple_form_tab, "Simple Form")
        
        # Wizard form tab
        wizard_form_tab = QWidget()
        wizard_layout = QVBoxLayout(wizard_form_tab)
        wizard_layout.setContentsMargins(20, 20, 20, 20)
        
        wizard_title = FluentLabel("Multi-Step Wizard Form")
        wizard_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        wizard_layout.addWidget(wizard_title)
        
        # Create wizard form
        self.wizard_form = FluentMultiStepForm("Account Setup Wizard")
        
        # Step 1: Personal Info
        self.wizard_form.add_step("Personal Information")
        self.wizard_form.add_field_to_step(0, "text", "first_name", "First Name", required=True)
        self.wizard_form.add_field_to_step(0, "text", "last_name", "Last Name", required=True)
        self.wizard_form.add_field_to_step(0, "date", "birth_date", "Birth Date", required=True)
        
        # Step 2: Contact Info
        self.wizard_form.add_step("Contact Information")
        self.wizard_form.add_field_to_step(1, "email", "email", "Email Address", required=True)
        self.wizard_form.add_field_to_step(1, "text", "phone", "Phone Number", required=True)
        self.wizard_form.add_field_to_step(1, "text", "address", "Address")
        
        # Step 3: Security
        self.wizard_form.add_step("Security")
        self.wizard_form.add_field_to_step(2, "password", "password", "Password", required=True)
        self.wizard_form.add_field_to_step(2, "password", "confirm_password", "Confirm Password", required=True)
        
        # Step 4: Preferences
        self.wizard_form.add_step("Preferences")
        self.wizard_form.add_field_to_step(3, "text", "company", "Company")
        self.wizard_form.add_field_to_step(3, "text", "job_title", "Job Title")
        
        self.wizard_form.wizard_completed.connect(self.handle_wizard_completion)
        wizard_layout.addWidget(self.wizard_form)
        
        forms_tabs.addTab(wizard_form_tab, "Wizard Form")
        
        # Field validation tab
        validation_tab = QWidget()
        validation_layout = QVBoxLayout(validation_tab)
        validation_layout.setContentsMargins(20, 20, 20, 20)
        
        validation_title = FluentLabel("Field Validation Examples")
        validation_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        validation_layout.addWidget(validation_title)
        
        # Email field
        self.email_field = FluentFormField(
            field_type="email",
            label="Email Address",
            placeholder="Enter valid email",
            required=True
        )
        validation_layout.addWidget(self.email_field)
        
        # Password with custom validation
        self.password_field = FluentFormField(
            field_type="password", 
            label="Strong Password",
            placeholder="At least 8 characters",
            required=True
        )
        self.password_field.add_validation_rule(
            lambda x: len(x) >= 8,
            "Password must be at least 8 characters"
        )
        validation_layout.addWidget(self.password_field)
        
        # Age field
        self.age_field = FluentFormField(
            field_type="number",
            label="Age",
            placeholder="18-120",
            required=True
        )
        self.age_field.add_validation_rule(
            lambda x: 18 <= int(x) <= 120 if x.isdigit() else False,
            "Age must be between 18 and 120"
        )
        validation_layout.addWidget(self.age_field)
        
        # Validation button
        validate_btn = FluentPushButton("Validate All Fields")
        validate_btn.clicked.connect(self.validate_form_fields)
        validation_layout.addWidget(validate_btn)
        
        validation_layout.addStretch()
        
        forms_tabs.addTab(validation_tab, "Validation")
        
        layout.addWidget(forms_tabs)
        return widget
        
    def create_configuration_tab(self):
        """Create configuration tab with property grid, settings, and JSON editor"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create sub-tabs for configuration tools
        config_tabs = FluentTabWidget()
        
        # Property grid tab
        property_tab = QWidget()
        property_layout = QVBoxLayout(property_tab)
        property_layout.setContentsMargins(20, 20, 20, 20)
        
        property_title = FluentLabel("Property Grid Editor")
        property_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        property_layout.addWidget(property_title)
        
        self.property_grid = FluentPropertyGrid()
        self.property_grid.property_changed.connect(self.on_property_changed)
        property_layout.addWidget(self.property_grid)
        
        config_tabs.addTab(property_tab, "Properties")
        
        # Settings panel tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setContentsMargins(20, 20, 20, 20)
        
        settings_title = FluentLabel("Application Settings")
        settings_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        settings_layout.addWidget(settings_title)
        
        self.settings_panel = FluentSettingsPanel()
        self.settings_panel.setting_changed.connect(self.on_setting_changed)
        settings_layout.addWidget(self.settings_panel)
        
        config_tabs.addTab(settings_tab, "Settings")
        
        # JSON editor tab
        json_tab = QWidget()
        json_layout = QVBoxLayout(json_tab)
        json_layout.setContentsMargins(20, 20, 20, 20)
        
        json_title = FluentLabel("JSON Data Editor")
        json_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        json_layout.addWidget(json_title)
        
        self.json_viewer = FluentJsonViewer()
        self.json_viewer.json_changed.connect(self.on_json_changed)
        self.json_viewer.validation_changed.connect(self.on_json_validation_changed)
        json_layout.addWidget(self.json_viewer)
        
        config_tabs.addTab(json_tab, "JSON Editor")
        
        layout.addWidget(config_tabs)
        return widget
        
    def setup_command_palette(self):
        """Setup comprehensive command palette"""
        self.command_palette = FluentCommandPalette(self)
        
        # Add all available commands
        commands = [
            # Navigation commands
            ("View: Dashboard", "Show main dashboard", lambda: self.switch_to_section("overview", 0), "view"),
            ("View: Charts", "Show chart visualizations", lambda: self.switch_to_section("charts", 0), "view"),
            ("View: Forms", "Show form examples", lambda: self.switch_to_section("forms", 0), "view"),
            ("View: Configuration", "Show configuration tools", lambda: self.switch_to_section("config", 0), "view"),
            
            # Chart commands
            ("Charts: Area Chart", "Show area chart", lambda: self.switch_to_section("charts", 0), "charts"),
            ("Charts: Scatter Plot", "Show scatter plot", lambda: self.switch_to_section("charts", 1), "charts"),
            ("Charts: Heat Map", "Show heat map", lambda: self.switch_to_section("charts", 2), "charts"),
            ("Charts: Refresh All", "Refresh all chart data", self.refresh_all_charts, "charts"),
            
            # Data commands
            ("Data: Refresh All", "Refresh all data", self.refresh_all_data, "data"),
            ("Data: Generate Sample", "Generate sample data", self.generate_sample_data, "data"),
            ("Data: Clear All", "Clear all data", self.clear_all_data, "data"),
            ("Data: Export JSON", "Export data as JSON", self.export_json_data, "data"),
            ("Data: Import JSON", "Import JSON data", self.import_json_data, "data"),
            
            # Form commands
            ("Forms: Validate All", "Validate all forms", self.validate_all_forms, "forms"),
            ("Forms: Reset All", "Reset all forms", self.reset_all_forms, "forms"),
            ("Forms: Submit All", "Submit all forms", self.submit_all_forms, "forms"),
            
            # Configuration commands
            ("Config: Properties", "Show property grid", lambda: self.switch_to_section("config", 0), "config"),
            ("Config: Settings", "Show settings panel", lambda: self.switch_to_section("config", 1), "config"),
            ("Config: JSON Editor", "Show JSON editor", lambda: self.switch_to_section("config", 2), "config"),
            ("Config: Export", "Export configuration", self.export_configuration, "config"),
            ("Config: Import", "Import configuration", self.import_configuration, "config"),
            
            # Analysis commands
            ("Analysis: Statistics", "Show statistics", self.show_statistics, "analysis"),
            ("Analysis: Correlations", "Analyze correlations", self.analyze_correlations, "analysis"),
            ("Analysis: Trends", "Analyze trends", self.analyze_trends, "analysis"),
            ("Analysis: Export Report", "Export analysis report", self.export_report, "analysis"),
            
            # View commands
            ("View: Full Screen", "Toggle full screen", self.toggle_fullscreen, "view"),
            ("View: Split Horizontal", "Split view horizontally", self.split_horizontal, "view"),
            ("View: Split Vertical", "Split view vertically", self.split_vertical, "view"),
            ("View: Single Pane", "Show single pane", self.single_pane, "view"),
            
            # Theme commands
            ("Theme: Light Mode", "Switch to light theme", self.set_light_theme, "theme"),
            ("Theme: Dark Mode", "Switch to dark theme", self.set_dark_theme, "theme"),
            ("Theme: Auto", "Auto theme selection", self.set_auto_theme, "theme"),
        ]
        
        for name, description, callback, category in commands:
            self.command_palette.add_command(name, description, callback, category)
            
    def load_all_sample_data(self):
        """Load sample data for all components"""
        self.load_chart_data()
        self.load_property_data()
        self.load_settings_data()
        self.load_json_data()
        self.update_stats()
        
    def load_chart_data(self):
        """Load sample data for charts"""
        # Area chart data
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        area_data = []
        for i, month in enumerate(months):
            value = 10000 + i * 800 + random.randint(-2000, 3000)
            area_data.append((month, max(0, value)))
            
        self.main_area_chart.set_data(area_data)
        self.main_area_chart.set_labels("Month", "Sales ($)")
        
        # Dashboard area chart (smaller data)
        dashboard_area_data = [(f"Q{i+1}", random.randint(5000, 15000)) for i in range(4)]
        self.dashboard_area_chart.set_data(dashboard_area_data)
        self.dashboard_area_chart.set_labels("Quarter", "Revenue")
        
        # Stats area chart (mini)
        stats_data = [(f"W{i+1}", random.randint(100, 200)) for i in range(8)]
        self.stats_area_chart.set_data(stats_data)
        
        # Scatter chart data
        scatter_data = []
        for _ in range(150):
            age = random.randint(18, 80)
            spending = 1000 - abs(age - 45) * 8 + random.randint(-400, 400)
            scatter_data.append((age, max(0, spending)))
            
        self.main_scatter_chart.set_data(scatter_data)
        self.main_scatter_chart.set_labels("Customer Age", "Monthly Spending ($)")
        self.main_scatter_chart.show_trend_line(True)
        
        # Dashboard scatter chart
        dashboard_scatter_data = [(random.randint(20, 70), random.randint(300, 1200)) for _ in range(50)]
        self.dashboard_scatter_chart.set_data(dashboard_scatter_data)
        
        # Heat map data
        departments = ["Sales", "Marketing", "Engineering", "Support", "HR", "Finance", "Operations"]
        metrics = ["Efficiency", "Quality", "Innovation", "Customer Sat.", "Cost Control"]
        
        heat_data = []
        for i in range(len(departments)):
            row = []
            for j in range(len(metrics)):
                score = 45 + (i + j) * 4 + random.randint(-25, 25)
                row.append(min(100, max(0, score)))
            heat_data.append(row)
            
        self.main_heat_map.set_data(heat_data, departments, metrics)
        self.main_heat_map.set_color_range(0, 100)
        self.main_heat_map.show_values(True)
        
        # Dashboard heat map (smaller)
        dashboard_heat_data = [[random.randint(30, 95) for _ in range(4)] for _ in range(4)]
        self.dashboard_heat_map.set_data(dashboard_heat_data, 
                                         ["Team A", "Team B", "Team C", "Team D"],
                                         ["Q1", "Q2", "Q3", "Q4"])
                                         
    def load_property_data(self):
        """Load sample data for property grid"""
        # Application properties
        self.property_grid.add_property(FluentPropertyItem("App Name", "Advanced Components Demo", PropertyType.STRING, "Application name"))
        self.property_grid.add_property(FluentPropertyItem("Version", "1.0.0", PropertyType.STRING, "Application version", readonly=True))
        self.property_grid.add_property(FluentPropertyItem("Debug Mode", False, PropertyType.BOOLEAN, "Enable debug mode"))
        self.property_grid.add_property(FluentPropertyItem("Max Users", 1000, PropertyType.INTEGER, "Maximum concurrent users"))
        self.property_grid.add_property(FluentPropertyItem("Timeout", 30.0, PropertyType.FLOAT, "Request timeout in seconds"))
        
        # UI properties
        self.property_grid.add_property(FluentPropertyItem("Theme", "Auto", PropertyType.CHOICE, "UI theme", 
                                                           choices=["Light", "Dark", "Auto"], category="UI"))
        self.property_grid.add_property(FluentPropertyItem("Font Size", 12, PropertyType.INTEGER, "UI font size", category="UI"))
        self.property_grid.add_property(FluentPropertyItem("Accent Color", "#0078d4", PropertyType.COLOR, "Accent color", category="UI"))
        self.property_grid.add_property(FluentPropertyItem("Animation Speed", 75, PropertyType.RANGE, "Animation speed percentage", 
                                                           range_min=0, range_max=100, category="UI"))
        
        # Performance properties
        self.property_grid.add_property(FluentPropertyItem("Cache Size", 256, PropertyType.INTEGER, "Cache size in MB", category="Performance"))
        self.property_grid.add_property(FluentPropertyItem("Update Interval", 5.0, PropertyType.FLOAT, "Auto-update interval in seconds", category="Performance"))
        self.property_grid.add_property(FluentPropertyItem("Enable Caching", True, PropertyType.BOOLEAN, "Enable data caching", category="Performance"))
        
    def load_settings_data(self):
        """Load sample data for settings panel"""
        # Appearance settings
        self.settings_panel.add_setting("Appearance", 
                                        FluentPropertyItem("Theme", "Dark", PropertyType.CHOICE, 
                                                          "Application theme", choices=["Light", "Dark", "Auto"]))
        self.settings_panel.add_setting("Appearance", 
                                        FluentPropertyItem("Font Size", 12, PropertyType.INTEGER, "UI font size"))
        self.settings_panel.add_setting("Appearance", 
                                        FluentPropertyItem("Accent Color", "#0078d4", PropertyType.COLOR, "Theme accent color"))
        self.settings_panel.add_setting("Appearance", 
                                        FluentPropertyItem("Show Animations", True, PropertyType.BOOLEAN, "Enable UI animations"))
        
        # Behavior settings
        self.settings_panel.add_setting("Behavior", 
                                        FluentPropertyItem("Auto Save", True, PropertyType.BOOLEAN, "Auto save documents"))
        self.settings_panel.add_setting("Behavior", 
                                        FluentPropertyItem("Save Interval", 300, PropertyType.INTEGER, "Auto save interval (seconds)"))
        self.settings_panel.add_setting("Behavior", 
                                        FluentPropertyItem("Confirm Exit", True, PropertyType.BOOLEAN, "Show confirmation on exit"))
        
        # Data settings
        self.settings_panel.add_setting("Data", 
                                        FluentPropertyItem("Data Source", "Local", PropertyType.CHOICE, 
                                                          "Data source type", choices=["Local", "Remote", "Cloud"]))
        self.settings_panel.add_setting("Data", 
                                        FluentPropertyItem("Cache Duration", 3600, PropertyType.INTEGER, "Cache duration in seconds"))
        self.settings_panel.add_setting("Data", 
                                        FluentPropertyItem("Max Records", 10000, PropertyType.INTEGER, "Maximum records to load"))
        
        # Advanced settings
        self.settings_panel.add_setting("Advanced", 
                                        FluentPropertyItem("Debug Mode", False, PropertyType.BOOLEAN, "Enable debug logging"))
        self.settings_panel.add_setting("Advanced", 
                                        FluentPropertyItem("Log Level", "Info", PropertyType.CHOICE, 
                                                          "Logging level", choices=["Debug", "Info", "Warning", "Error"]))
        self.settings_panel.add_setting("Advanced", 
                                        FluentPropertyItem("Performance Monitor", True, PropertyType.BOOLEAN, "Enable performance monitoring"))
        
    def load_json_data(self):
        """Load sample JSON data"""
        self.sample_json_data = {
            "application": {
                "name": "Advanced Components Demo",
                "version": "1.0.0",
                "author": "Fluent UI Team",
                "description": "Comprehensive demonstration of advanced Fluent UI components"
            },
            "features": [
                {
                    "name": "Advanced Forms",
                    "enabled": True,
                    "components": ["FluentForm", "FluentMultiStepForm", "FluentFormField"],
                    "capabilities": {
                        "validation": True,
                        "multi_step": True,
                        "custom_fields": True
                    }
                },
                {
                    "name": "Data Visualization", 
                    "enabled": True,
                    "components": ["FluentAreaChart", "FluentScatterChart", "FluentHeatMap"],
                    "capabilities": {
                        "animations": True,
                        "interactions": True,
                        "themes": True
                    }
                },
                {
                    "name": "Configuration Tools",
                    "enabled": True,
                    "components": ["FluentPropertyGrid", "FluentSettingsPanel", "FluentJsonViewer"],
                    "capabilities": {
                        "property_editing": True,
                        "settings_management": True,
                        "json_editing": True
                    }
                }
            ],
            "settings": {
                "theme": "auto",
                "animation_speed": 0.75,
                "auto_save": True,
                "debug_mode": False
            },
            "statistics": {
                "total_components": 15,
                "total_demos": 6,
                "lines_of_code": 5000,
                "last_updated": "2025-05-27"
            }
        }
        
        self.json_viewer.set_json(self.sample_json_data)
        
    def update_stats(self):
        """Update statistics display"""
        # Calculate totals
        total_items = len(self.sample_json_data.get("features", []))
        avg_value = random.randint(75, 95)
        
        self.total_items_label.setText(f"Items: {total_items}")
        self.avg_value_label.setText(f"Avg: {avg_value}%")
        
    # Navigation methods
    def switch_to_section(self, section: str, tab_index: int = 0):
        """Switch to specific section and tab"""
        section_map = {
            "overview": 0,
            "charts": 1,
            "forms": 2,
            "config": 3
        }
        
        if section in section_map:
            self.main_tabs.setCurrentIndex(section_map[section])
            
            # Switch to specific sub-tab if needed
            current_widget = self.main_tabs.currentWidget()
            if hasattr(current_widget, 'findChild'):
                sub_tabs = current_widget.findChild(FluentTabWidget)
                if sub_tabs and tab_index < sub_tabs.count():
                    sub_tabs.setCurrentIndex(tab_index)
                    
    def show_command_palette(self):
        """Show command palette"""
        self.command_palette.show_palette()
        
    # Data refresh methods
    def refresh_all_data(self):
        """Refresh all data"""
        print("🔄 Refreshing all data...")
        self.load_all_sample_data()
        
    def auto_refresh_data(self):
        """Auto refresh data periodically"""
        # Update some random values
        if hasattr(self, 'stats_area_chart'):
            stats_data = [(f"W{i+1}", random.randint(100, 200)) for i in range(8)]
            self.stats_area_chart.set_data(stats_data)
            
        self.update_stats()
        
    def refresh_all_charts(self):
        """Refresh all chart data"""
        print("📊 Refreshing chart data...")
        self.load_chart_data()
        
    def refresh_area_chart(self):
        """Refresh area chart data"""
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        data = [(month, random.randint(5000, 20000)) for month in months]
        self.main_area_chart.set_data(data)
        
    def refresh_scatter_chart(self):
        """Refresh scatter chart data"""
        data = [(random.randint(18, 80), random.randint(200, 1500)) for _ in range(150)]
        self.main_scatter_chart.set_data(data)
        
    def refresh_heat_map(self):
        """Refresh heat map data"""
        data = [[random.randint(20, 100) for _ in range(5)] for _ in range(7)]
        departments = ["Sales", "Marketing", "Engineering", "Support", "HR", "Finance", "Operations"]
        metrics = ["Efficiency", "Quality", "Innovation", "Customer Sat.", "Cost Control"]
        self.main_heat_map.set_data(data, departments, metrics)
        
    def toggle_scatter_trend(self):
        """Toggle scatter chart trend line"""
        current = self.main_scatter_chart.trend_line_visible
        self.main_scatter_chart.show_trend_line(not current)
        
    def toggle_heatmap_values(self):
        """Toggle heat map value display"""
        current = self.main_heat_map.values_visible
        self.main_heat_map.show_values(not current)
        
    # Form event handlers
    def handle_simple_form_submission(self, form_data):
        """Handle simple form submission"""
        print("📝 Simple form submitted:", form_data)
        
    def handle_wizard_completion(self, wizard_data):
        """Handle wizard completion"""
        print("🧙 Wizard completed:", wizard_data)
        
    def validate_form_fields(self):
        """Validate individual form fields"""
        fields = [self.email_field, self.password_field, self.age_field]
        all_valid = all(field.validate() for field in fields)
        
        if all_valid:
            print("✅ All fields are valid!")
        else:
            print("❌ Some fields contain errors")
            
    def validate_all_forms(self):
        """Validate all forms"""
        print("📋 Validating all forms...")
        self.validate_form_fields()
        
    def reset_all_forms(self):
        """Reset all forms"""
        print("🔄 Resetting all forms...")
        
    def submit_all_forms(self):
        """Submit all forms"""
        print("📤 Submitting all forms...")
        
    # Configuration event handlers
    def on_property_changed(self, property_name: str, value):
        """Handle property change"""
        print(f"🔧 Property changed: {property_name} = {value}")
        
    def on_setting_changed(self, category: str, setting_name: str, value):
        """Handle setting change"""
        print(f"⚙️ Setting changed: {category}.{setting_name} = {value}")
        
    def on_json_changed(self, json_data):
        """Handle JSON data change"""
        print("📄 JSON data changed")
        self.sample_json_data = json_data
        
    def on_json_validation_changed(self, is_valid: bool, error_message: str):
        """Handle JSON validation change"""
        if is_valid:
            print("✅ JSON is valid")
        else:
            print(f"❌ JSON validation error: {error_message}")
            
    # Data management methods
    def generate_sample_data(self):
        """Generate new sample data"""
        print("🎲 Generating sample data...")
        self.load_all_sample_data()
        
    def clear_all_data(self):
        """Clear all data"""
        print("🗑️ Clearing all data...")
        
    def validate_all_data(self):
        """Validate all data"""
        print("✅ Validating all data...")
        
    def import_json_data(self):
        """Import JSON data"""
        print("📥 Importing JSON data...")
        
    def export_json_data(self):
        """Export JSON data"""
        print("📤 Exporting JSON data...")
        
    def load_settings(self):
        """Load settings"""
        print("📁 Loading settings...")
        
    def save_settings(self):
        """Save settings"""
        print("💾 Saving settings...")
        
    def import_configuration(self):
        """Import configuration"""
        print("📥 Importing configuration...")
        
    def export_configuration(self):
        """Export configuration"""
        print("📤 Exporting configuration...")
        
    def reset_configuration(self):
        """Reset configuration"""
        print("🔄 Resetting configuration...")
        
    # Analysis methods
    def show_statistics(self):
        """Show statistics"""
        print("📈 Showing statistics...")
        
    def analyze_correlations(self):
        """Analyze correlations"""
        print("🔗 Analyzing correlations...")
        
    def analyze_trends(self):
        """Analyze trends"""
        print("📊 Analyzing trends...")
        
    def export_report(self):
        """Export analysis report"""
        print("📋 Exporting analysis report...")
        
    # View management methods
    def split_horizontal(self):
        """Split view horizontally"""
        print("↔️ Splitting view horizontally")
        self.main_splitter.setOrientation(Qt.Orientation.Horizontal)
        
    def split_vertical(self):
        """Split view vertically"""
        print("↕️ Splitting view vertically")
        self.main_splitter.setOrientation(Qt.Orientation.Vertical)
        
    def single_pane(self):
        """Show single pane"""
        print("📱 Showing single pane")
        
    def toggle_fullscreen(self):
        """Toggle full screen"""
        if self.isFullScreen():
            self.showNormal()
            print("🪟 Exited full screen")
        else:
            self.showFullScreen()
            print("🖥️ Entered full screen")
            
    def set_light_theme(self):
        """Set light theme"""
        print("☀️ Switching to light theme")
        
    def set_dark_theme(self):
        """Set dark theme"""
        print("🌙 Switching to dark theme")
        
    def set_auto_theme(self):
        """Set auto theme"""
        print("🔄 Setting auto theme")
        
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_P and event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            self.show_command_palette()
        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("All Advanced Components Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Fluent UI")
    
    # Create and show demo window
    demo = AllAdvancedComponentsDemo()
    demo.show()
    
    print("🚀 All Advanced Components Demo launched!")
    print("💡 Press Ctrl+Shift+P to open the command palette")
    print("🎯 Explore all the advanced components in the tabs")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
