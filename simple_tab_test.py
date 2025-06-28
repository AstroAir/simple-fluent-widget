#!/usr/bin/env python3
"""
Simple Test - Fluent Tab Component Demo
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel

def main():
    app = QApplication(sys.argv)
    
    # Import after QApplication is created
    from components.basic.navigation.tabs import FluentTabWidget
    
    class SimpleTabDemo(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Simple Tab Demo")
            self.setGeometry(200, 200, 600, 400)
            
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create main layout
            main_layout = QVBoxLayout(central_widget)
            
            # Add title
            title = QLabel("Simple Tab Demo")
            main_layout.addWidget(title)
            
            # Basic tab widget
            tabs = FluentTabWidget()
            
            # Add simple tabs
            tab1 = QWidget()
            tab1_layout = QVBoxLayout(tab1)
            tab1_layout.addWidget(QLabel("Tab 1 Content"))
            
            tab2 = QWidget()
            tab2_layout = QVBoxLayout(tab2)
            tab2_layout.addWidget(QLabel("Tab 2 Content"))
            
            tabs.addTab(tab1, "Tab 1")
            tabs.addTab(tab2, "Tab 2")
            
            main_layout.addWidget(tabs)
    
    demo = SimpleTabDemo()
    demo.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
