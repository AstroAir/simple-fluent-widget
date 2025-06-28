#!/usr/bin/env python3
"""
Working Fluent Tab Component Demo

This example demonstrates the usage of FluentTabWidget components.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox, QTextEdit, QPushButton


def main():
    """Run the tab demo application."""
    app = QApplication(sys.argv)
    
    # Import after QApplication is created to avoid widget creation before app
    from components.basic.navigation.tabs import FluentTabWidget
    
    class TabDemo(QMainWindow):
        """Main demo window showcasing Fluent tab components."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Fluent Tab Demo")
            self.setGeometry(200, 200, 800, 600)
            
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(20)
            main_layout.setContentsMargins(20, 20, 20, 20)
            
            # Add title
            title = QLabel("Fluent Tab Components Demo")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
            main_layout.addWidget(title)
            
            # Create basic tabs section
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
            
            # Add tabs
            basic_tabs.addTab(home_content, "Home")
            basic_tabs.addTab(profile_content, "Profile")
            basic_tabs.addTab(settings_content, "Settings")
            
            # Set active tab
            basic_tabs.setCurrentIndex(0)
            
            layout.addWidget(QLabel("Standard Tab Widget:"))
            layout.addWidget(basic_tabs)
            
            main_layout.addWidget(group)
            main_layout.addStretch()
    
    # Set application properties
    app.setApplicationName("Fluent Tab Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = TabDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
