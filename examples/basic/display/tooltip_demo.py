#!/usr/bin/env python3
"""
Fluent Tooltip Component Demo

This example demonstrates the usage of FluentTooltip components and TooltipMixin
with various configurations, including different tooltip styles, positions, and content types.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox, QPushButton, QTextEdit, QSlider
from PySide6.QtCore import Qt

from components.basic.display.tooltip import FluentTooltip, TooltipMixin
from components.basic.forms.button import FluentButton
from core.theme import theme_manager


class TooltipButton(QPushButton, TooltipMixin):
    """Button with tooltip mixin functionality."""
    def __init__(self, text, tooltip_text="", parent=None):
        super().__init__(text, parent)
        if tooltip_text:
            self.set_tooltip(tooltip_text)


class TooltipDemo(QMainWindow):
    """Main demo window showcasing Fluent tooltip components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Tooltip Demo")
        self.setGeometry(200, 200, 1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add title
        title = QLabel("Fluent Tooltip Components Demo")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Create demo sections
        self.create_basic_tooltips(main_layout)
        self.create_position_tooltips(main_layout)
        self.create_interactive_tooltips(main_layout)
        self.create_rich_content_tooltips(main_layout)
        
        main_layout.addStretch()
        
    def create_basic_tooltips(self, parent_layout):
        """Create basic tooltip examples."""
        group = QGroupBox("Basic Tooltips")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Simple tooltip buttons
        button_layout = QHBoxLayout()
        
        # Basic tooltip
        basic_btn = TooltipButton("Hover for Basic Tooltip", "This is a simple tooltip!")
        button_layout.addWidget(basic_btn)
        
        # Longer tooltip
        long_btn = TooltipButton(
            "Long Tooltip", 
            "This is a much longer tooltip that demonstrates how the tooltip component handles longer text content with proper wrapping."
        )
        button_layout.addWidget(long_btn)
        
        # Multi-line tooltip
        multiline_btn = TooltipButton(
            "Multi-line Tooltip",
            "This tooltip has multiple lines.\nLine 2: More information here.\nLine 3: Even more details!"
        )
        button_layout.addWidget(multiline_btn)
        
        button_layout.addStretch()
        
        layout.addWidget(QLabel("Hover over the buttons to see tooltips:"))
        layout.addLayout(button_layout)
        layout.addSpacing(15)
        
        # Tooltip on different widgets
        widget_layout = QHBoxLayout()
        
        # Label with tooltip
        info_label = QLabel("ℹ️ Info Label")
        info_label.setStyleSheet("border: 1px solid #ccc; padding: 8px; background: #f5f5f5;")
        # Apply tooltip using mixin (if the label supported it, we'd use a custom class)
        info_label.setToolTip("This label provides important information about the current context.")
        widget_layout.addWidget(info_label)
        
        # Slider with tooltip
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(50)
        volume_slider.setToolTip("Adjust the volume level (0-100)")
        widget_layout.addWidget(volume_slider)
        
        widget_layout.addStretch()
        
        layout.addWidget(QLabel("Tooltips on different widget types:"))
        layout.addLayout(widget_layout)
        
        parent_layout.addWidget(group)
        
    def create_position_tooltips(self, parent_layout):
        """Create tooltips with different positions."""
        group = QGroupBox("Tooltip Positioning")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Positioning explanation
        layout.addWidget(QLabel("Tooltips automatically position themselves to stay within the screen bounds:"))
        layout.addSpacing(10)
        
        # Grid of buttons for position testing
        grid_layout = QVBoxLayout()
        
        # Top row
        top_layout = QHBoxLayout()
        top_left = TooltipButton("Top Left", "Tooltip positioned from top-left corner")
        top_center = TooltipButton("Top Center", "Tooltip positioned from top-center")
        top_right = TooltipButton("Top Right", "Tooltip positioned from top-right corner")
        
        top_layout.addWidget(top_left)
        top_layout.addWidget(top_center)
        top_layout.addWidget(top_right)
        top_layout.addStretch()
        
        # Middle row
        middle_layout = QHBoxLayout()
        middle_left = TooltipButton("Left", "Tooltip positioned from left side")
        center_btn = TooltipButton("Center", "Tooltip positioned from center - should adapt based on available space")
        middle_right = TooltipButton("Right", "Tooltip positioned from right side")
        
        middle_layout.addWidget(middle_left)
        middle_layout.addWidget(center_btn)
        middle_layout.addWidget(middle_right)
        middle_layout.addStretch()
        
        # Bottom row
        bottom_layout = QHBoxLayout()
        bottom_left = TooltipButton("Bottom Left", "Tooltip positioned from bottom-left")
        bottom_center = TooltipButton("Bottom Center", "Tooltip positioned from bottom-center")
        bottom_right = TooltipButton("Bottom Right", "Tooltip positioned from bottom-right")
        
        bottom_layout.addWidget(bottom_left)
        bottom_layout.addWidget(bottom_center)
        bottom_layout.addWidget(bottom_right)
        bottom_layout.addStretch()
        
        grid_layout.addLayout(top_layout)
        grid_layout.addLayout(middle_layout)
        grid_layout.addLayout(bottom_layout)
        
        layout.addLayout(grid_layout)
        
        parent_layout.addWidget(group)
        
    def create_interactive_tooltips(self, parent_layout):
        """Create interactive tooltip examples."""
        group = QGroupBox("Interactive Tooltips")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Dynamic tooltip content
        counter = {"count": 0}
        
        def create_dynamic_tooltip():
            counter["count"] += 1
            return f"You've hovered {counter['count']} time(s)!"
        
        dynamic_btn = QPushButton("Dynamic Tooltip Content")
        
        def update_tooltip():
            dynamic_btn.setToolTip(create_dynamic_tooltip())
        
        # Update tooltip on hover (would need custom implementation for real dynamic updates)
        dynamic_btn.setToolTip("Dynamic content will update - hover to see count!")
        
        layout.addWidget(QLabel("Dynamic and contextual tooltips:"))
        layout.addWidget(dynamic_btn)
        layout.addSpacing(15)
        
        # Conditional tooltips
        conditional_layout = QHBoxLayout()
        
        enabled_btn = TooltipButton("Enabled Button", "This button is enabled and ready to use!")
        conditional_layout.addWidget(enabled_btn)
        
        disabled_btn = TooltipButton("Disabled Button", "This button is disabled. Enable it in settings to use this feature.")
        disabled_btn.setEnabled(False)
        conditional_layout.addWidget(disabled_btn)
        
        conditional_layout.addStretch()
        
        layout.addWidget(QLabel("Conditional tooltips based on state:"))
        layout.addLayout(conditional_layout)
        layout.addSpacing(15)
        
        # Help tooltips
        help_layout = QHBoxLayout()
        
        help_icon = QLabel("❓")
        help_icon.setStyleSheet("font-size: 18px; color: #0078d4; cursor: pointer;")
        help_icon.setToolTip("Click for more detailed help information")
        help_layout.addWidget(help_icon)
        
        settings_icon = QLabel("⚙️")
        settings_icon.setStyleSheet("font-size: 18px; cursor: pointer;")
        settings_icon.setToolTip("Open application settings")
        help_layout.addWidget(settings_icon)
        
        info_icon = QLabel("ℹ️")
        info_icon.setStyleSheet("font-size: 18px; cursor: pointer;")
        info_icon.setToolTip("About this application")
        help_layout.addWidget(info_icon)
        
        help_layout.addStretch()
        
        layout.addWidget(QLabel("Icon tooltips for help and navigation:"))
        layout.addLayout(help_layout)
        
        parent_layout.addWidget(group)
        
    def create_rich_content_tooltips(self, parent_layout):
        """Create tooltips with rich content."""
        group = QGroupBox("Rich Content Tooltips")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Keyboard shortcuts
        shortcut_layout = QHBoxLayout()
        
        save_btn = TooltipButton("Save", "Save Document\nKeyboard: Ctrl+S")
        shortcut_layout.addWidget(save_btn)
        
        copy_btn = TooltipButton("Copy", "Copy Selection\nKeyboard: Ctrl+C")
        shortcut_layout.addWidget(copy_btn)
        
        paste_btn = TooltipButton("Paste", "Paste from Clipboard\nKeyboard: Ctrl+V")
        shortcut_layout.addWidget(paste_btn)
        
        undo_btn = TooltipButton("Undo", "Undo Last Action\nKeyboard: Ctrl+Z")
        shortcut_layout.addWidget(undo_btn)
        
        shortcut_layout.addStretch()
        
        layout.addWidget(QLabel("Tooltips with keyboard shortcuts:"))
        layout.addLayout(shortcut_layout)
        layout.addSpacing(15)
        
        # Status information
        status_layout = QHBoxLayout()
        
        connection_btn = TooltipButton("🌐 Connection", "Status: Connected\nServer: api.example.com\nLatency: 45ms")
        status_layout.addWidget(connection_btn)
        
        battery_btn = TooltipButton("🔋 Battery", "Battery Level: 85%\nEstimated Time: 4h 23m\nPower Mode: Balanced")
        status_layout.addWidget(battery_btn)
        
        storage_btn = TooltipButton("💾 Storage", "Available: 245 GB\nUsed: 755 GB\nTotal: 1 TB")
        status_layout.addWidget(storage_btn)
        
        status_layout.addStretch()
        
        layout.addWidget(QLabel("Status and system information tooltips:"))
        layout.addLayout(status_layout)
        layout.addSpacing(15)
        
        # Feature descriptions
        feature_layout = QHBoxLayout()
        
        ai_btn = TooltipButton("🤖 AI Assistant", "AI-powered code completion\n\n• Smart suggestions\n• Context awareness\n• Multiple languages\n• Real-time analysis")
        feature_layout.addWidget(ai_btn)
        
        cloud_btn = TooltipButton("☁️ Cloud Sync", "Synchronize your work across devices\n\n• Real-time collaboration\n• Version history\n• Offline support\n• 99.9% uptime")
        feature_layout.addWidget(cloud_btn)
        
        feature_layout.addStretch()
        
        layout.addWidget(QLabel("Feature description tooltips:"))
        layout.addLayout(feature_layout)
        
        parent_layout.addWidget(group)


def main():
    """Run the tooltip demo application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent Tooltip Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = TooltipDemo()
    demo.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
