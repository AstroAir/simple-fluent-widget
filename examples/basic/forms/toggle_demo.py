#!/usr/bin/env python3
"""
Fluent Toggle Component Demo

This example demonstrates the usage of FluentToggleSwitch components with various configurations,
including basic toggles, expandable toggles, styled toggles, and grouped toggles.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox, QFormLayout
from PySide6.QtCore import Qt

from components.basic.forms.toggle import FluentToggleSwitch, FluentExpandableToggle
from core.theme import theme_manager


class ToggleDemo(QMainWindow):
    """Main demo window showcasing Fluent toggle components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Toggle Demo")
        self.setGeometry(200, 200, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add title
        title = QLabel("Fluent Toggle Components Demo")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Create demo sections
        self.create_basic_toggles(main_layout)
        self.create_labeled_toggles(main_layout)
        self.create_grouped_toggles(main_layout)
        self.create_expandable_toggles(main_layout)
        
        main_layout.addStretch()
        
    def create_basic_toggles(self, parent_layout):
        """Create basic toggle examples."""
        group = QGroupBox("Basic Toggle Switches")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Basic toggle
        basic_toggle = FluentToggleSwitch()
        basic_toggle.setText("Basic Toggle")
        
        status_label = QLabel("Status: OFF")
        basic_toggle.toggled.connect(
            lambda checked: status_label.setText(f"Status: {'ON' if checked else 'OFF'}")
        )
        
        basic_layout = QHBoxLayout()
        basic_layout.addWidget(basic_toggle)
        basic_layout.addWidget(status_label)
        basic_layout.addStretch()
        
        layout.addLayout(basic_layout)
        layout.addSpacing(10)
        
        # Pre-checked toggle
        checked_toggle = FluentToggleSwitch("Pre-checked Toggle")
        checked_toggle.setChecked(True)
        layout.addWidget(checked_toggle)
        layout.addSpacing(10)
        
        # Disabled toggle
        disabled_toggle = FluentToggleSwitch("Disabled Toggle")
        disabled_toggle.setEnabled(False)
        layout.addWidget(disabled_toggle)
        layout.addSpacing(10)
        
        # Disabled but checked toggle
        disabled_checked_toggle = FluentToggleSwitch("Disabled (Checked)")
        disabled_checked_toggle.setChecked(True)
        disabled_checked_toggle.setEnabled(False)
        layout.addWidget(disabled_checked_toggle)
        
        parent_layout.addWidget(group)
        
    def create_labeled_toggles(self, parent_layout):
        """Create toggles with descriptive labels."""
        group = QGroupBox("Settings Toggle Examples")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QFormLayout(group)
        
        # Notification settings
        notifications_toggle = FluentToggleSwitch()
        layout.addRow("Enable Notifications:", notifications_toggle)
        
        # Dark mode toggle
        dark_mode_toggle = FluentToggleSwitch()
        dark_mode_description = QLabel("Switch between light and dark themes")
        dark_mode_description.setStyleSheet("color: #666666; font-size: 12px;")
        
        dark_mode_layout = QVBoxLayout()
        dark_mode_layout.addWidget(dark_mode_toggle)
        dark_mode_layout.addWidget(dark_mode_description)
        dark_mode_layout.setSpacing(2)
        dark_mode_widget = QWidget()
        dark_mode_widget.setLayout(dark_mode_layout)
        
        layout.addRow("Dark Mode:", dark_mode_widget)
        
        # Auto-save toggle
        autosave_toggle = FluentToggleSwitch()
        autosave_toggle.setChecked(True)
        layout.addRow("Auto-save Documents:", autosave_toggle)
        
        # Sound effects toggle
        sound_toggle = FluentToggleSwitch()
        sound_status = QLabel("🔇 Muted")
        
        def update_sound_status(checked):
            sound_status.setText("🔊 Sound On" if checked else "🔇 Muted")
        
        sound_toggle.toggled.connect(update_sound_status)
        
        sound_layout = QHBoxLayout()
        sound_layout.addWidget(sound_toggle)
        sound_layout.addWidget(sound_status)
        sound_layout.addStretch()
        sound_widget = QWidget()
        sound_widget.setLayout(sound_layout)
        
        layout.addRow("Sound Effects:", sound_widget)
        
        parent_layout.addWidget(group)
        
    def create_grouped_toggles(self, parent_layout):
        """Create grouped toggle examples."""
        group = QGroupBox("Privacy Settings")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Privacy toggles
        privacy_options = [
            ("Share usage data", False),
            ("Allow cookies", True),
            ("Location services", False),
            ("Camera access", False),
            ("Microphone access", False),
        ]
        
        self.privacy_toggles = []
        
        for option_text, default_state in privacy_options:
            toggle = FluentToggleSwitch(option_text)
            toggle.setChecked(default_state)
            self.privacy_toggles.append(toggle)
            layout.addWidget(toggle)
        
        # Master control
        layout.addSpacing(15)
        master_toggle = FluentToggleSwitch("Enable All Privacy Options")
        
        def toggle_all_privacy(checked):
            for toggle in self.privacy_toggles:
                toggle.setChecked(checked)
        
        def update_master_state():
            all_checked = all(toggle.isChecked() for toggle in self.privacy_toggles)
            any_checked = any(toggle.isChecked() for toggle in self.privacy_toggles)
            
            if all_checked:
                master_toggle.setChecked(True)
                master_toggle.setText("Disable All Privacy Options")
            elif not any_checked:
                master_toggle.setChecked(False)
                master_toggle.setText("Enable All Privacy Options")
            else:
                master_toggle.setText("Mixed Privacy Settings")
        
        master_toggle.toggled.connect(toggle_all_privacy)
        
        for toggle in self.privacy_toggles:
            toggle.toggled.connect(update_master_state)
        
        update_master_state()  # Initial state
        layout.addWidget(master_toggle)
        
        parent_layout.addWidget(group)
        
    def create_expandable_toggles(self, parent_layout):
        """Create expandable toggle examples."""
        group = QGroupBox("Expandable Toggles")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Advanced settings expandable toggle
        advanced_toggle = FluentExpandableToggle("Show Advanced Settings")
        
        # Content that will be shown/hidden
        advanced_content = QWidget()
        advanced_content.setVisible(False)
        advanced_layout = QFormLayout(advanced_content)
        advanced_layout.setContentsMargins(20, 10, 10, 10)
        
        # Add some advanced options
        debug_toggle = FluentToggleSwitch()
        advanced_layout.addRow("Debug Mode:", debug_toggle)
        
        verbose_toggle = FluentToggleSwitch()
        advanced_layout.addRow("Verbose Logging:", verbose_toggle)
        
        experimental_toggle = FluentToggleSwitch()
        experimental_toggle.setChecked(True)
        advanced_layout.addRow("Experimental Features:", experimental_toggle)
        
        # Connect the expandable toggle to show/hide content
        advanced_toggle.toggled.connect(advanced_content.setVisible)
        advanced_toggle.toggled.connect(
            lambda checked: advanced_toggle.setText(
                "Hide Advanced Settings" if checked else "Show Advanced Settings"
            )
        )
        
        layout.addWidget(advanced_toggle)
        layout.addWidget(advanced_content)
        layout.addSpacing(15)
        
        # Developer options expandable toggle
        dev_toggle = FluentExpandableToggle("Developer Options")
        
        dev_content = QWidget()
        dev_content.setVisible(False)
        dev_layout = QVBoxLayout(dev_content)
        dev_layout.setContentsMargins(20, 10, 10, 10)
        
        # Developer options
        dev_options = [
            "USB Debugging",
            "Stay Awake",
            "Show CPU Usage",
            "Strict Mode",
        ]
        
        for option in dev_options:
            dev_option_toggle = FluentToggleSwitch(option)
            dev_layout.addWidget(dev_option_toggle)
        
        dev_toggle.toggled.connect(dev_content.setVisible)
        dev_toggle.toggled.connect(
            lambda checked: dev_toggle.setText(
                "Hide Developer Options" if checked else "Developer Options"
            )
        )
        
        layout.addWidget(dev_toggle)
        layout.addWidget(dev_content)
        
        parent_layout.addWidget(group)


def main():
    """Run the toggle demo application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent Toggle Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = ToggleDemo()
    demo.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
