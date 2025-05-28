"""
Comprehensive Demo - All Advanced Components

This demo showcases all the advanced components together in a unified application:
- Advanced forms with validation
- Menu systems and command palette
- Advanced charts and visualizations
- Integration with existing components
"""

import sys
import os
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QStackedWidget, QSplitter, QTextEdit)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.data.forms import FluentFormField, FluentForm, FluentMultiStepForm
from components.command.menus import FluentMenu, FluentContextMenu, FluentCommandPalette, FluentRibbon, FluentRibbonTab
from components.data.advanced_charts import FluentAreaChart, FluentScatterChart, FluentHeatMap
from components.basic.card import FluentCard
from components.basic.button import FluentPushButton
from components.basic.label import FluentLabel
from components.navigation.tab import FluentTabWidget
from components.layout.container import FluentContainer
from theme.theme_manager import theme_manager


class ComprehensiveDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comprehensive Fluent UI Demo - Enterprise Components")
        self.setGeometry(50, 50, 1800, 1000)
        
        # Apply theme
        theme_manager.apply_theme(self)
        
        self.setup_ui()
        self.setup_command_palette()
        self.load_sample_data()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Setup ribbon
        self.setup_ribbon(main_layout)
        
        # Create main content area
        self.setup_main_content(main_layout)
        
    def setup_ribbon(self, parent_layout):
        """Setup the ribbon interface"""
        self.ribbon = FluentRibbon()
        
        # File tab
        file_tab = FluentRibbonTab("File")
        file_tab.add_group("Document")
        file_tab.add_command("Document", "New", "Create new document", self.new_document)
        file_tab.add_command("Document", "Open", "Open document", self.open_document)
        file_tab.add_command("Document", "Save", "Save document", self.save_document)
        file_tab.add_command("Document", "Export", "Export data", self.export_data)
        
        file_tab.add_group("Data")
        file_tab.add_command("Data", "Import", "Import data", self.import_data)
        file_tab.add_command("Data", "Refresh", "Refresh all data", self.refresh_all_data)
        file_tab.add_command("Data", "Clear", "Clear all data", self.clear_data)
        
        self.ribbon.add_tab(file_tab)
        
        # Analytics tab
        analytics_tab = FluentRibbonTab("Analytics")
        analytics_tab.add_group("Charts")
        analytics_tab.add_command("Charts", "Area Chart", "Show area chart", lambda: self.switch_to_tab(1))
        analytics_tab.add_command("Charts", "Scatter Plot", "Show scatter plot", lambda: self.switch_to_tab(2))
        analytics_tab.add_command("Charts", "Heat Map", "Show heat map", lambda: self.switch_to_tab(3))
        
        analytics_tab.add_group("Analysis")
        analytics_tab.add_command("Analysis", "Statistics", "Show statistics", self.show_statistics)
        analytics_tab.add_command("Analysis", "Trends", "Analyze trends", self.analyze_trends)
        analytics_tab.add_command("Analysis", "Correlations", "Find correlations", self.find_correlations)
        
        self.ribbon.add_tab(analytics_tab)
        
        # Forms tab
        forms_tab = FluentRibbonTab("Forms")
        forms_tab.add_group("Create")
        forms_tab.add_command("Create", "New Form", "Create new form", lambda: self.switch_to_tab(4))
        forms_tab.add_command("Create", "Wizard", "Create wizard", lambda: self.switch_to_tab(5))
        forms_tab.add_command("Create", "Survey", "Create survey", self.create_survey)
        
        forms_tab.add_group("Validation")
        forms_tab.add_command("Validation", "Validate All", "Validate all forms", self.validate_all_forms)
        forms_tab.add_command("Validation", "Reset", "Reset forms", self.reset_forms)
        
        self.ribbon.add_tab(forms_tab)
        
        # View tab
        view_tab = FluentRibbonTab("View")
        view_tab.add_group("Layout")
        view_tab.add_command("Layout", "Dashboard", "Dashboard view", lambda: self.switch_to_tab(0))
        view_tab.add_command("Layout", "Full Screen", "Toggle full screen", self.toggle_fullscreen)
        view_tab.add_command("Layout", "Split View", "Toggle split view", self.toggle_split_view)
        
        view_tab.add_group("Theme")
        view_tab.add_command("Theme", "Light Mode", "Switch to light theme", self.set_light_theme)
        view_tab.add_command("Theme", "Dark Mode", "Switch to dark theme", self.set_dark_theme)
        view_tab.add_command("Theme", "Auto", "Auto theme selection", self.set_auto_theme)
        
        self.ribbon.add_tab(view_tab)
        
        parent_layout.addWidget(self.ribbon)
        
    def setup_main_content(self, parent_layout):
        """Setup the main content area"""
        # Create tab widget for different views
        self.tab_widget = FluentTabWidget()
        self.tab_widget.setTabPosition(FluentTabWidget.TabPosition.West)
        
        # Dashboard tab
        self.dashboard_widget = self.create_dashboard()
        self.tab_widget.addTab(self.dashboard_widget, "Dashboard")
        
        # Charts tabs
        self.area_chart_widget = self.create_area_chart_tab()
        self.tab_widget.addTab(self.area_chart_widget, "Area Chart")
        
        self.scatter_chart_widget = self.create_scatter_chart_tab()
        self.tab_widget.addTab(self.scatter_chart_widget, "Scatter Plot")
        
        self.heat_map_widget = self.create_heat_map_tab()
        self.tab_widget.addTab(self.heat_map_widget, "Heat Map")
        
        # Forms tabs
        self.forms_widget = self.create_forms_tab()
        self.tab_widget.addTab(self.forms_widget, "Forms")
        
        self.wizard_widget = self.create_wizard_tab()
        self.tab_widget.addTab(self.wizard_widget, "Wizard")
        
        parent_layout.addWidget(self.tab_widget)
        
    def create_dashboard(self):
        """Create the main dashboard"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Welcome section
        welcome_card = FluentCard()
        welcome_layout = QVBoxLayout(welcome_card)
        
        title = FluentLabel("Enterprise Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        welcome_layout.addWidget(title)
        
        subtitle = FluentLabel("Comprehensive Fluent UI component demonstration")
        subtitle.setStyleSheet("font-size: 14px; color: #666; margin-bottom: 20px;")
        welcome_layout.addWidget(subtitle)
        
        # Quick stats
        stats_layout = QHBoxLayout()
        
        # Create mini charts for overview
        self.mini_area_chart = FluentAreaChart()
        self.mini_area_chart.setMaximumHeight(150)
        stats_layout.addWidget(self.create_stat_card("Sales Trend", self.mini_area_chart))
        
        self.mini_scatter_chart = FluentScatterChart()
        self.mini_scatter_chart.setMaximumHeight(150)
        stats_layout.addWidget(self.create_stat_card("Customer Analysis", self.mini_scatter_chart))
        
        self.mini_heat_map = FluentHeatMap()
        self.mini_heat_map.setMaximumHeight(150)
        stats_layout.addWidget(self.create_stat_card("Performance Matrix", self.mini_heat_map))
        
        welcome_layout.addLayout(stats_layout)
        layout.addWidget(welcome_card)
        
        # Quick actions
        actions_card = FluentCard()
        actions_layout = QVBoxLayout(actions_card)
        
        actions_title = FluentLabel("Quick Actions")
        actions_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        actions_layout.addWidget(actions_title)
        
        buttons_layout = QHBoxLayout()
        
        create_form_btn = FluentPushButton("Create New Form")
        create_form_btn.clicked.connect(lambda: self.switch_to_tab(4))
        buttons_layout.addWidget(create_form_btn)
        
        analyze_data_btn = FluentPushButton("Analyze Data")
        analyze_data_btn.clicked.connect(lambda: self.switch_to_tab(1))
        buttons_layout.addWidget(analyze_data_btn)
        
        open_palette_btn = FluentPushButton("Command Palette")
        open_palette_btn.clicked.connect(self.show_command_palette)
        buttons_layout.addWidget(open_palette_btn)
        
        refresh_btn = FluentPushButton("Refresh All")
        refresh_btn.clicked.connect(self.refresh_all_data)
        buttons_layout.addWidget(refresh_btn)
        
        actions_layout.addLayout(buttons_layout)
        layout.addWidget(actions_card)
        
        return widget
        
    def create_stat_card(self, title, chart_widget):
        """Create a statistics card with embedded chart"""
        card = FluentCard()
        card_layout = QVBoxLayout(card)
        
        title_label = FluentLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        card_layout.addWidget(title_label)
        
        card_layout.addWidget(chart_widget)
        
        return card
        
    def create_area_chart_tab(self):
        """Create area chart tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        title = FluentLabel("Sales Performance - Area Chart")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        controls_layout.addWidget(title)
        
        controls_layout.addStretch()
        
        refresh_btn = FluentPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh_area_chart)
        controls_layout.addWidget(refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Chart
        self.main_area_chart = FluentAreaChart()
        self.main_area_chart.setMinimumHeight(400)
        layout.addWidget(self.main_area_chart)
        
        return widget
        
    def create_scatter_chart_tab(self):
        """Create scatter chart tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        title = FluentLabel("Customer Analysis - Scatter Plot")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        controls_layout.addWidget(title)
        
        controls_layout.addStretch()
        
        refresh_btn = FluentPushButton("Generate New Data")
        refresh_btn.clicked.connect(self.refresh_scatter_chart)
        controls_layout.addWidget(refresh_btn)
        
        trend_btn = FluentPushButton("Toggle Trend Line")
        trend_btn.clicked.connect(self.toggle_trend_line)
        controls_layout.addWidget(trend_btn)
        
        layout.addLayout(controls_layout)
        
        # Chart
        self.main_scatter_chart = FluentScatterChart()
        self.main_scatter_chart.setMinimumHeight(400)
        layout.addWidget(self.main_scatter_chart)
        
        return widget
        
    def create_heat_map_tab(self):
        """Create heat map tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        title = FluentLabel("Performance Matrix - Heat Map")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        controls_layout.addWidget(title)
        
        controls_layout.addStretch()
        
        refresh_btn = FluentPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh_heat_map)
        controls_layout.addWidget(refresh_btn)
        
        values_btn = FluentPushButton("Toggle Values")
        values_btn.clicked.connect(self.toggle_heat_map_values)
        controls_layout.addWidget(values_btn)
        
        layout.addLayout(controls_layout)
        
        # Chart
        self.main_heat_map = FluentHeatMap()
        self.main_heat_map.setMinimumHeight(400)
        layout.addWidget(self.main_heat_map)
        
        return widget
        
    def create_forms_tab(self):
        """Create forms tab"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left side - Form creation
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        title = FluentLabel("Form Builder")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        left_layout.addWidget(title)
        
        # Create a complete form
        self.demo_form = FluentForm("User Registration")
        self.demo_form.add_field("text", "first_name", "First Name", required=True)
        self.demo_form.add_field("text", "last_name", "Last Name", required=True)
        self.demo_form.add_field("email", "email", "Email Address", required=True)
        self.demo_form.add_field("password", "password", "Password", required=True)
        self.demo_form.add_field("date", "birth_date", "Birth Date", required=True)
        self.demo_form.add_field("text", "phone", "Phone Number")
        
        self.demo_form.form_submitted.connect(self.handle_form_submission)
        left_layout.addWidget(self.demo_form)
        
        layout.addWidget(left_panel)
        
        # Right side - Form validation demo
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        validation_title = FluentLabel("Individual Field Validation")
        validation_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        right_layout.addWidget(validation_title)
        
        # Email field
        self.email_field = FluentFormField(
            field_type="email",
            label="Email Address",
            placeholder="Enter your email",
            required=True
        )
        right_layout.addWidget(self.email_field)
        
        # Password field with custom validation
        self.password_field = FluentFormField(
            field_type="password",
            label="Strong Password",
            placeholder="Enter a strong password",
            required=True
        )
        self.password_field.add_validation_rule(
            lambda x: len(x) >= 8,
            "Password must be at least 8 characters"
        )
        right_layout.addWidget(self.password_field)
        
        # Number field
        self.age_field = FluentFormField(
            field_type="number",
            label="Age",
            placeholder="Enter your age",
            required=True
        )
        self.age_field.add_validation_rule(
            lambda x: 18 <= int(x) <= 120 if x.isdigit() else False,
            "Age must be between 18 and 120"
        )
        right_layout.addWidget(self.age_field)
        
        # Validate button
        validate_btn = FluentPushButton("Validate Fields")
        validate_btn.clicked.connect(self.validate_individual_fields)
        right_layout.addWidget(validate_btn)
        
        layout.addWidget(right_panel)
        
        return widget
        
    def create_wizard_tab(self):
        """Create wizard tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = FluentLabel("Multi-Step Form Wizard")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Create multi-step form
        self.wizard_form = FluentMultiStepForm("Account Setup Wizard")
        
        # Step 1: Personal Information
        self.wizard_form.add_step("Personal Information")
        self.wizard_form.add_field_to_step(0, "text", "first_name", "First Name", required=True)
        self.wizard_form.add_field_to_step(0, "text", "last_name", "Last Name", required=True)
        self.wizard_form.add_field_to_step(0, "date", "birth_date", "Birth Date", required=True)
        
        # Step 2: Contact Information
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
        
        layout.addWidget(self.wizard_form)
        
        return widget
        
    def setup_command_palette(self):
        """Setup command palette"""
        self.command_palette = FluentCommandPalette(self)
        
        # Add all available commands
        commands = [
            ("Dashboard: Show Overview", "Show main dashboard", lambda: self.switch_to_tab(0), "view"),
            ("Charts: Area Chart", "Show area chart", lambda: self.switch_to_tab(1), "charts"),
            ("Charts: Scatter Plot", "Show scatter plot", lambda: self.switch_to_tab(2), "charts"),
            ("Charts: Heat Map", "Show heat map", lambda: self.switch_to_tab(3), "charts"),
            ("Forms: Form Builder", "Show form builder", lambda: self.switch_to_tab(4), "forms"),
            ("Forms: Wizard", "Show form wizard", lambda: self.switch_to_tab(5), "forms"),
            ("Data: Refresh All", "Refresh all data", self.refresh_all_data, "data"),
            ("Data: Clear All", "Clear all data", self.clear_data, "data"),
            ("File: New Document", "Create new document", self.new_document, "file"),
            ("File: Save Document", "Save current document", self.save_document, "file"),
            ("View: Full Screen", "Toggle full screen", self.toggle_fullscreen, "view"),
            ("Theme: Light Mode", "Switch to light theme", self.set_light_theme, "theme"),
            ("Theme: Dark Mode", "Switch to dark theme", self.set_dark_theme, "theme"),
        ]
        
        for name, description, callback, category in commands:
            self.command_palette.add_command(name, description, callback, category)
            
    def load_sample_data(self):
        """Load sample data for all charts"""
        # Load data for main charts
        self.load_area_chart_data()
        self.load_scatter_chart_data()
        self.load_heat_map_data()
        
        # Load data for mini charts
        self.load_mini_chart_data()
        
    def load_area_chart_data(self):
        """Load area chart data"""
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        data = []
        base_value = 10000
        for i, month in enumerate(months):
            value = base_value + i * 500 + random.randint(-1000, 1000)
            data.append((month, max(0, value)))
            
        self.main_area_chart.set_data(data)
        self.main_area_chart.set_labels("Month", "Sales ($)")
        
    def load_scatter_chart_data(self):
        """Load scatter chart data"""
        data_points = []
        for _ in range(100):
            age = random.randint(18, 80)
            spending = 1000 - abs(age - 45) * 10 + random.randint(-300, 300)
            data_points.append((age, max(0, spending)))
            
        self.main_scatter_chart.set_data(data_points)
        self.main_scatter_chart.set_labels("Customer Age", "Monthly Spending ($)")
        self.main_scatter_chart.show_trend_line(True)
        
    def load_heat_map_data(self):
        """Load heat map data"""
        departments = ["Sales", "Marketing", "Engineering", "Support", "HR", "Finance"]
        metrics = ["Efficiency", "Quality", "Innovation", "Customer Sat.", "Cost Control"]
        
        data = []
        for i in range(len(departments)):
            row = []
            for j in range(len(metrics)):
                score = 50 + (i + j) * 3 + random.randint(-20, 20)
                row.append(min(100, max(0, score)))
            data.append(row)
            
        self.main_heat_map.set_data(data, departments, metrics)
        self.main_heat_map.set_color_range(0, 100)
        self.main_heat_map.show_values(True)
        
    def load_mini_chart_data(self):
        """Load data for mini charts in dashboard"""
        # Mini area chart
        data = [(f"Q{i+1}", random.randint(8000, 12000)) for i in range(4)]
        self.mini_area_chart.set_data(data)
        
        # Mini scatter chart
        data = [(random.randint(20, 60), random.randint(500, 1500)) for _ in range(20)]
        self.mini_scatter_chart.set_data(data)
        
        # Mini heat map
        data = [[random.randint(40, 90) for _ in range(3)] for _ in range(3)]
        self.mini_heat_map.set_data(data, ["A", "B", "C"], ["X", "Y", "Z"])
        
    # Navigation methods
    def switch_to_tab(self, index):
        """Switch to specified tab"""
        self.tab_widget.setCurrentIndex(index)
        
    def show_command_palette(self):
        """Show command palette"""
        self.command_palette.show_palette()
        
    # Ribbon command handlers
    def new_document(self):
        print("Creating new document...")
        
    def open_document(self):
        print("Opening document...")
        
    def save_document(self):
        print("Saving document...")
        
    def export_data(self):
        print("Exporting data...")
        
    def import_data(self):
        print("Importing data...")
        
    def refresh_all_data(self):
        """Refresh all chart data"""
        print("Refreshing all data...")
        self.load_sample_data()
        
    def clear_data(self):
        print("Clearing all data...")
        
    def refresh_area_chart(self):
        self.load_area_chart_data()
        
    def refresh_scatter_chart(self):
        self.load_scatter_chart_data()
        
    def refresh_heat_map(self):
        self.load_heat_map_data()
        
    def toggle_trend_line(self):
        current = self.main_scatter_chart.trend_line_visible
        self.main_scatter_chart.show_trend_line(not current)
        
    def toggle_heat_map_values(self):
        current = self.main_heat_map.values_visible
        self.main_heat_map.show_values(not current)
        
    def show_statistics(self):
        print("Showing statistics...")
        
    def analyze_trends(self):
        print("Analyzing trends...")
        
    def find_correlations(self):
        print("Finding correlations...")
        
    def create_survey(self):
        print("Creating survey...")
        
    def validate_all_forms(self):
        """Validate all forms"""
        print("Validating all forms...")
        self.validate_individual_fields()
        
    def reset_forms(self):
        print("Resetting forms...")
        
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def toggle_split_view(self):
        print("Toggling split view...")
        
    def set_light_theme(self):
        print("Switching to light theme...")
        
    def set_dark_theme(self):
        print("Switching to dark theme...")
        
    def set_auto_theme(self):
        print("Setting auto theme...")
        
    # Form handlers
    def validate_individual_fields(self):
        """Validate individual fields"""
        fields = [self.email_field, self.password_field, self.age_field]
        all_valid = all(field.validate() for field in fields)
        
        if all_valid:
            print("✓ All fields are valid!")
        else:
            print("✗ Some fields contain errors")
            
    def handle_form_submission(self, form_data):
        print("Form submitted:", form_data)
        
    def handle_wizard_completion(self, wizard_data):
        print("Wizard completed:", wizard_data)
        
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_P and event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            self.show_command_palette()
        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Comprehensive Fluent UI Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Fluent UI")
    
    # Create and show demo window
    demo = ComprehensiveDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
