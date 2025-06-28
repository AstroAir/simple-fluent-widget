#!/usr/bin/env python3
"""
Fluent Segmented Control Component Demo

This example demonstrates the usage of FluentSegmentedControl components with various configurations,
including different sizes, styles, and interactive behaviors.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox, QTextEdit
from PySide6.QtCore import Qt

from components.basic.navigation.segmented import FluentSegmentedControl
from core.theme import theme_manager


class SegmentedDemo(QMainWindow):
    """Main demo window showcasing Fluent segmented control components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Segmented Control Demo")
        self.setGeometry(200, 200, 900, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add title
        title = QLabel("Fluent Segmented Control Components Demo")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Create demo sections
        self.create_basic_segments(main_layout)
        self.create_styled_segments(main_layout)
        self.create_size_variations(main_layout)
        self.create_interactive_segments(main_layout)
        
        main_layout.addStretch()
        
    def create_basic_segments(self, parent_layout):
        """Create basic segmented control examples."""
        group = QGroupBox("Basic Segmented Controls")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Simple two-segment control
        binary_segments = FluentSegmentedControl(
            segments=["On", "Off"],
            selected_index=0
        )
        
        binary_status = QLabel("Current selection: On")
        binary_segments.selection_changed.connect(
            lambda index: binary_status.setText(f"Current selection: {['On', 'Off'][index]}")
        )
        
        layout.addWidget(QLabel("Binary Choice:"))
        layout.addWidget(binary_segments)
        layout.addWidget(binary_status)
        layout.addSpacing(15)
        
        # Multiple segments
        view_segments = FluentSegmentedControl(
            segments=["List", "Grid", "Timeline", "Calendar"],
            selected_index=1
        )
        
        view_status = QLabel("Current view: Grid")
        view_segments.selection_changed.connect(
            lambda index: view_status.setText(f"Current view: {['List', 'Grid', 'Timeline', 'Calendar'][index]}")
        )
        
        layout.addWidget(QLabel("View Selection:"))
        layout.addWidget(view_segments)
        layout.addWidget(view_status)
        layout.addSpacing(15)
        
        # File type filter
        filter_segments = FluentSegmentedControl(
            segments=["All", "Documents", "Images", "Videos", "Audio"],
            selected_index=0
        )
        
        filter_status = QLabel("Showing: All files")
        filter_segments.selection_changed.connect(
            lambda index: filter_status.setText(f"Showing: {['All', 'Documents', 'Images', 'Videos', 'Audio'][index]} files")
        )
        
        layout.addWidget(QLabel("File Filter:"))
        layout.addWidget(filter_segments)
        layout.addWidget(filter_status)
        
        parent_layout.addWidget(group)
        
    def create_styled_segments(self, parent_layout):
        """Create segmented controls with different styles."""
        group = QGroupBox("Style Variations")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Filled style (default)
        filled_segments = FluentSegmentedControl(
            segments=["Home", "Search", "Profile"],
            style=FluentSegmentedControl.Style.FILLED,
            selected_index=0
        )
        
        layout.addWidget(QLabel("Filled Style:"))
        layout.addWidget(filled_segments)
        layout.addSpacing(15)
        
        # Outlined style
        outlined_segments = FluentSegmentedControl(
            segments=["Edit", "Preview", "Code"],
            style=FluentSegmentedControl.Style.OUTLINED,
            selected_index=1
        )
        
        layout.addWidget(QLabel("Outlined Style:"))
        layout.addWidget(outlined_segments)
        layout.addSpacing(15)
        
        # Pill style
        pill_segments = FluentSegmentedControl(
            segments=["Light", "Dark", "Auto"],
            style=FluentSegmentedControl.Style.PILL,
            selected_index=2
        )
        
        layout.addWidget(QLabel("Pill Style:"))
        layout.addWidget(pill_segments)
        
        parent_layout.addWidget(group)
        
    def create_size_variations(self, parent_layout):
        """Create segmented controls with different sizes."""
        group = QGroupBox("Size Variations")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Small size
        small_segments = FluentSegmentedControl(
            segments=["S", "M", "L", "XL"],
            size=FluentSegmentedControl.Size.SMALL,
            selected_index=1
        )
        
        layout.addWidget(QLabel("Small Size:"))
        layout.addWidget(small_segments)
        layout.addSpacing(15)
        
        # Medium size (default)
        medium_segments = FluentSegmentedControl(
            segments=["Jan", "Feb", "Mar", "Apr"],
            size=FluentSegmentedControl.Size.MEDIUM,
            selected_index=0
        )
        
        layout.addWidget(QLabel("Medium Size:"))
        layout.addWidget(medium_segments)
        layout.addSpacing(15)
        
        # Large size
        large_segments = FluentSegmentedControl(
            segments=["Design", "Develop", "Deploy"],
            size=FluentSegmentedControl.Size.LARGE,
            selected_index=1
        )
        
        layout.addWidget(QLabel("Large Size:"))
        layout.addWidget(large_segments)
        
        parent_layout.addWidget(group)
        
    def create_interactive_segments(self, parent_layout):
        """Create interactive segmented control examples."""
        group = QGroupBox("Interactive Examples")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Tab-like behavior
        tab_segments = FluentSegmentedControl(
            segments=["Overview", "Details", "Settings"],
            selected_index=0
        )
        
        # Content area that changes based on selection
        content_area = QTextEdit()
        content_area.setMaximumHeight(120)
        content_area.setReadOnly(True)
        
        content_texts = [
            "Overview Content:\n\nThis section provides a general overview of the application features and capabilities. Here you can find quick summaries and key information.",
            "Details Content:\n\nDetailed information about specific features, configuration options, and advanced settings. This section contains comprehensive documentation.",
            "Settings Content:\n\nApplication preferences and configuration options. Customize the behavior and appearance of the application to suit your needs."
        ]
        
        def update_content(index):
            content_area.setPlainText(content_texts[index])
        
        # Initialize with first content
        update_content(0)
        tab_segments.selection_changed.connect(update_content)
        
        layout.addWidget(QLabel("Tab-like Navigation:"))
        layout.addWidget(tab_segments)
        layout.addWidget(content_area)
        layout.addSpacing(15)
        
        # Toolbar-like segments
        toolbar_segments = FluentSegmentedControl(
            segments=["✏️ Edit", "👁️ View", "📤 Share", "⚙️ Tools"],
            style=FluentSegmentedControl.Style.OUTLINED,
            selected_index=0
        )
        
        toolbar_status = QLabel("Mode: Edit - Ready to make changes")
        
        def update_toolbar_status(index):
            modes = [
                "Mode: Edit - Ready to make changes",
                "Mode: View - Read-only preview",
                "Mode: Share - Sharing options available",
                "Mode: Tools - Additional tools and utilities"
            ]
            toolbar_status.setText(modes[index])
        
        toolbar_segments.selection_changed.connect(update_toolbar_status)
        
        layout.addWidget(QLabel("Toolbar Mode Selection:"))
        layout.addWidget(toolbar_segments)
        layout.addWidget(toolbar_status)
        layout.addSpacing(15)
        
        # Filter with dynamic feedback
        data_segments = FluentSegmentedControl(
            segments=["Today", "Week", "Month", "Year"],
            style=FluentSegmentedControl.Style.PILL,
            selected_index=0
        )
        
        data_display = QLabel("📊 Showing data for: Today (24 records)")
        data_display.setStyleSheet("padding: 10px; background: #f5f5f5; border: 1px solid #ddd; border-radius: 4px;")
        
        def update_data_display(index):
            data_info = [
                "📊 Showing data for: Today (24 records)",
                "📊 Showing data for: This Week (168 records)",
                "📊 Showing data for: This Month (720 records)",
                "📊 Showing data for: This Year (8,760 records)"
            ]
            data_display.setText(data_info[index])
        
        data_segments.selection_changed.connect(update_data_display)
        
        layout.addWidget(QLabel("Time Range Filter:"))
        layout.addWidget(data_segments)
        layout.addWidget(data_display)
        
        parent_layout.addWidget(group)


def main():
    """Run the segmented control demo application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent Segmented Control Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = SegmentedDemo()
    demo.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
