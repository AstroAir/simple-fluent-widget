#!/usr/bin/env python3
"""
Fluent Tab Component Demo

This example demonstrates the usage of FluentTabWidget and FluentTabButton components 
with various configurations, including different tab styles, closable tabs, and content management.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox, QTextEdit, QPushButton, QScrollArea
from PySide6.QtCore import Qt


def main():
    """Run the tab demo application."""
    app = QApplication(sys.argv)
    
    # Import after QApplication is created to avoid widget creation before app
    from components.basic.navigation.tabs import FluentTabWidget, FluentTabButton
    from core.theme import theme_manager
    
    class TabDemo(QMainWindow):
        """Main demo window showcasing Fluent tab components."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Fluent Tab Demo")
            self.setGeometry(200, 200, 1000, 800)
            
            # Create central widget with scroll area
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
            central_widget = QWidget()
            scroll.setWidget(central_widget)
            self.setCentralWidget(scroll)
            
            # Create main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(20)
            main_layout.setContentsMargins(20, 20, 20, 20)
            
            # Add title
            title = QLabel("Fluent Tab Components Demo")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
            main_layout.addWidget(title)
            
            # Create demo sections
            self.create_basic_tabs(main_layout)
            self.create_closable_tabs(main_layout)
            self.create_dynamic_tabs(main_layout)
            self.create_content_tabs(main_layout)
            
            main_layout.addStretch()
        
    def create_basic_tabs(self, parent_layout):
        """Create basic tab examples."""
        group = QGroupBox("Basic Tab Widget")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Basic tab widget
        basic_tabs = FluentTabWidget()
        
        # Add tabs with content
        home_content = QWidget()
        home_layout = QVBoxLayout(home_content)
        home_layout.addWidget(QLabel("🏠 Home Content"))
        home_layout.addWidget(QLabel("Welcome to the home page! This is the main dashboard where you can access all features."))
        home_layout.addStretch()
        
        profile_content = QWidget()
        profile_layout = QVBoxLayout(profile_content)
        profile_layout.addWidget(QLabel("👤 Profile Content"))
        profile_layout.addWidget(QLabel("Manage your profile information, settings, and preferences here."))
        profile_layout.addStretch()
        
        settings_content = QWidget()
        settings_layout = QVBoxLayout(settings_content)
        settings_layout.addWidget(QLabel("⚙️ Settings Content"))
        settings_layout.addWidget(QLabel("Configure application settings and customize your experience."))
        settings_layout.addStretch()
        
        help_content = QWidget()
        help_layout = QVBoxLayout(help_content)
        help_layout.addWidget(QLabel("❓ Help Content"))
        help_layout.addWidget(QLabel("Find answers to common questions and access documentation."))
        help_layout.addStretch()
        
        # Add tabs
        basic_tabs.addTab(home_content, "Home")
        basic_tabs.addTab(profile_content, "Profile")
        basic_tabs.addTab(settings_content, "Settings")
        basic_tabs.addTab(help_content, "Help")
        
        # Set active tab
        basic_tabs.setCurrentIndex(0)
        
        layout.addWidget(QLabel("Standard Tab Widget:"))
        layout.addWidget(basic_tabs)
        
        parent_layout.addWidget(group)
        
    def create_closable_tabs(self, parent_layout):
        """Create closable tab examples."""
        group = QGroupBox("Closable Tabs")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Closable tab widget
        self.closable_tabs = FluentTabWidget()
        
        # Add some initial tabs
        self.tab_counter = 1
        
        for i in range(3):
            self.add_document_tab()
        
        # Add tab controls
        control_layout = QHBoxLayout()
        
        add_tab_btn = QPushButton("Add New Tab")
        add_tab_btn.clicked.connect(self.add_document_tab)
        
        close_all_btn = QPushButton("Close All Tabs")
        close_all_btn.clicked.connect(self.close_all_tabs)
        
        control_layout.addWidget(add_tab_btn)
        control_layout.addWidget(close_all_btn)
        control_layout.addStretch()
        
        layout.addWidget(QLabel("Closable Tabs (Document Editor Style):"))
        layout.addWidget(self.closable_tabs)
        layout.addLayout(control_layout)
        
        parent_layout.addWidget(group)
        
    def create_dynamic_tabs(self, parent_layout):
        """Create dynamic tab examples."""
        group = QGroupBox("Dynamic Tab Management")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Dynamic tab widget
        self.dynamic_tabs = FluentTabWidget()
        
        # Initial tabs
        browser_tabs = [
            ("Google", "🌐 Google Search"),
            ("GitHub", "💻 GitHub Repository"),
            ("Documentation", "📚 API Documentation")
        ]
        
        for tab_name, tab_description in browser_tabs:
            content = QWidget()
            content_layout = QVBoxLayout(content)
            content_layout.addWidget(QLabel(tab_description))
            content_layout.addWidget(QLabel(f"This is the {tab_name} tab content. You can switch between tabs to see different content."))
            content_layout.addStretch()
            
            self.dynamic_tabs.addTab(content, tab_name)
        
        # Dynamic controls
        dynamic_control_layout = QHBoxLayout()
        
        add_google_btn = QPushButton("Add Google Tab")
        add_google_btn.clicked.connect(lambda: self.add_browser_tab("Google", "🔍 Google Search Engine"))
        
        add_github_btn = QPushButton("Add GitHub Tab")
        add_github_btn.clicked.connect(lambda: self.add_browser_tab("GitHub", "🐙 GitHub Platform"))
        
        add_docs_btn = QPushButton("Add Docs Tab")
        add_docs_btn.clicked.connect(lambda: self.add_browser_tab("Docs", "📖 Documentation Site"))
        
        dynamic_control_layout.addWidget(add_google_btn)
        dynamic_control_layout.addWidget(add_github_btn)
        dynamic_control_layout.addWidget(add_docs_btn)
        dynamic_control_layout.addStretch()
        
        # Tab status
        self.tab_status = QLabel(f"Active tabs: {self.dynamic_tabs.count()}")
        
        # Connect signals
        self.dynamic_tabs.currentChanged.connect(self.update_tab_status)
        # Note: tabCloseRequested would need to be connected if closable tabs were supported
        
        layout.addWidget(QLabel("Dynamic Tab Management (Browser Style):"))
        layout.addWidget(self.dynamic_tabs)
        layout.addLayout(dynamic_control_layout)
        layout.addWidget(self.tab_status)
        
        parent_layout.addWidget(group)
        
    def create_content_tabs(self, parent_layout):
        """Create tabs with rich content."""
        group = QGroupBox("Rich Content Tabs")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Rich content tab widget
        content_tabs = FluentTabWidget()
        
        # Dashboard tab
        dashboard_content = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_content)
        dashboard_layout.addWidget(QLabel("📊 Dashboard"))
        
        dashboard_text = QTextEdit()
        dashboard_text.setMaximumHeight(80)
        dashboard_text.setPlainText("Key Metrics:\n• Active Users: 1,234\n• Revenue: $45,678\n• Growth: +12%")
        dashboard_text.setReadOnly(True)
        
        dashboard_layout.addWidget(dashboard_text)
        dashboard_layout.addStretch()
        
        # Analytics tab
        analytics_content = QWidget()
        analytics_layout = QVBoxLayout(analytics_content)
        analytics_layout.addWidget(QLabel("📈 Analytics"))
        
        analytics_text = QTextEdit()
        analytics_text.setMaximumHeight(80)
        analytics_text.setPlainText("Performance Data:\n• Page Views: 15,432\n• Bounce Rate: 32%\n• Session Duration: 4:23")
        analytics_text.setReadOnly(True)
        
        analytics_layout.addWidget(analytics_text)
        analytics_layout.addStretch()
        
        # Reports tab
        reports_content = QWidget()
        reports_layout = QVBoxLayout(reports_content)
        reports_layout.addWidget(QLabel("📋 Reports"))
        
        reports_text = QTextEdit()
        reports_text.setMaximumHeight(80)
        reports_text.setPlainText("Latest Reports:\n• Monthly Sales Report\n• User Engagement Analysis\n• System Performance Report")
        reports_text.setReadOnly(True)
        
        reports_layout.addWidget(reports_text)
        reports_layout.addStretch()
        
        # Settings tab
        settings_content = QWidget()
        settings_layout = QVBoxLayout(settings_content)
        settings_layout.addWidget(QLabel("🔧 Settings"))
        
        settings_controls = QVBoxLayout()
        settings_controls.addWidget(QPushButton("General Settings"))
        settings_controls.addWidget(QPushButton("Privacy Settings"))
        settings_controls.addWidget(QPushButton("Advanced Settings"))
        settings_controls.addStretch()
        
        settings_layout.addLayout(settings_controls)
        settings_layout.addStretch()
        
        # Add all tabs
        content_tabs.addTab(dashboard_content, "Dashboard")
        content_tabs.addTab(analytics_content, "Analytics")
        content_tabs.addTab(reports_content, "Reports")
        content_tabs.addTab(settings_content, "Settings")
        
        # Tab change handler
        def on_tab_changed(index):
            tab_names = ["Dashboard", "Analytics", "Reports", "Settings"]
            content_status.setText(f"Viewing: {tab_names[index]} (Tab {index + 1} of {len(tab_names)})")
        
        content_tabs.currentChanged.connect(on_tab_changed)
        
        content_status = QLabel("Viewing: Dashboard (Tab 1 of 4)")
        
        layout.addWidget(QLabel("Application Tabs with Rich Content:"))
        layout.addWidget(content_tabs)
        layout.addWidget(content_status)
        
        parent_layout.addWidget(group)
    
    def add_document_tab(self):
        """Add a new document tab."""
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        content_layout.addWidget(QLabel(f"📄 Document {self.tab_counter}"))
        
        text_edit = QTextEdit()
        text_edit.setPlaceholderText(f"Start typing in Document {self.tab_counter}...")
        text_edit.setMaximumHeight(100)
        
        content_layout.addWidget(text_edit)
        content_layout.addStretch()
        
        tab_name = f"Document {self.tab_counter}"
        self.closable_tabs.addTab(content, tab_name)
        
        # Make the new tab active
        self.closable_tabs.setCurrentIndex(self.closable_tabs.count() - 1)
        
        self.tab_counter += 1
    
    def close_all_tabs(self):
        """Close all tabs in the closable tab widget."""
        # Close from the end to avoid index issues
        while self.closable_tabs.count() > 0:
            self.closable_tabs.removeTab(self.closable_tabs.count() - 1)
    
    def add_browser_tab(self, tab_type, description):
        """Add a new browser tab."""
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.addWidget(QLabel(description))
        content_layout.addWidget(QLabel(f"This is a new {tab_type} tab. Content loads here..."))
        content_layout.addStretch()
        
        self.dynamic_tabs.addTab(content, tab_type)
        
        # Make the new tab active
        self.dynamic_tabs.setCurrentIndex(self.dynamic_tabs.count() - 1)
    
    def update_tab_status(self):
        """Update the tab status label."""
        count = self.dynamic_tabs.count()
        self.tab_status.setText(f"Active tabs: {count}")


def main():
    """Run the tab demo application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent Tab Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = TabDemo()
    demo.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
