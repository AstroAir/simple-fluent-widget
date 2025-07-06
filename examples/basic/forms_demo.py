#!/usr/bin/env python3
"""
Fluent Basic Forms Components Demo

This example demonstrates the comprehensive usage of Fluent basic form components including
buttons, text inputs, checkboxes, sliders, and other form controls with various configurations.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QGroupBox, QPushButton, QFrame, QTabWidget, QGridLayout,
    QCheckBox, QSlider, QSpinBox, QLineEdit, QTextEdit, QComboBox,
    QRadioButton, QButtonGroup, QProgressBar, QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon


def main():
    """Run the basic forms demo application."""
    app = QApplication(sys.argv)
    
    # Import form components after QApplication is created
    try:
        from components.basic.forms.button import FluentButton, FluentIconButton, FluentToggleButton
        from components.basic.forms.textbox import FluentLineEdit, FluentTextEdit, FluentPasswordEdit
        from components.basic.forms.checkbox import FluentCheckBox
        from components.basic.forms.radio import FluentRadioButton
        from components.basic.forms.slider import FluentSlider
        from components.basic.forms.switch import FluentSwitch
        from components.basic.forms.combobox import FluentComboBox
        from components.basic.forms.spinbox import FluentSpinBox, FluentDoubleSpinBox
        from components.basic.forms.toggle import FluentToggleSwitch
        FORMS_AVAILABLE = True
    except ImportError as e:
        print(f"Import error: {e}")
        print("Using fallback Qt components for demo")
        FORMS_AVAILABLE = False
    
    class BasicFormsDemo(QMainWindow):
        """Main demo window showcasing Fluent basic form components."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Fluent Basic Forms Components Demo")
            self.setGeometry(100, 100, 1400, 900)
            
            # Create central widget with tabs
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(10)
            main_layout.setContentsMargins(10, 10, 10, 10)
            
            # Add title
            title = QLabel("Fluent Basic Forms Components Demo")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
            main_layout.addWidget(title)
            
            # Create tab widget for different component examples
            self.tab_widget = QTabWidget()
            main_layout.addWidget(self.tab_widget)
            
            # Create tabs
            self.create_buttons_tab()
            self.create_text_inputs_tab()
            self.create_selection_controls_tab()
            self.create_numeric_inputs_tab()
            self.create_advanced_controls_tab()
            self.create_form_examples_tab()
            
        def create_buttons_tab(self):
            """Create buttons examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Button styles group
            styles_group = QGroupBox("Button Styles & States")
            styles_layout = QGridLayout(styles_group)
            
            # Standard buttons
            std_label = QLabel("Standard Buttons:")
            std_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            styles_layout.addWidget(std_label, 0, 0, 1, 4)
            
            if FORMS_AVAILABLE:
                # Primary button
                primary_btn = FluentButton("Primary Action")
                primary_btn.set_style("primary")
                
                # Secondary button
                secondary_btn = FluentButton("Secondary")
                secondary_btn.set_style("secondary")
                
                # Accent button
                accent_btn = FluentButton("Accent")
                accent_btn.set_style("accent")
                
                # Disabled button
                disabled_btn = FluentButton("Disabled")
                disabled_btn.setEnabled(False)
                
                styles_layout.addWidget(primary_btn, 1, 0)
                styles_layout.addWidget(secondary_btn, 1, 1)
                styles_layout.addWidget(accent_btn, 1, 2)
                styles_layout.addWidget(disabled_btn, 1, 3)
            else:
                # Fallback Qt buttons
                primary_btn = QPushButton("Primary Action")
                secondary_btn = QPushButton("Secondary")
                accent_btn = QPushButton("Accent")
                disabled_btn = QPushButton("Disabled")
                disabled_btn.setEnabled(False)
                
                # Apply some styling
                primary_btn.setStyleSheet("QPushButton { background-color: #0078d4; color: white; border: none; padding: 8px 16px; border-radius: 4px; }")
                secondary_btn.setStyleSheet("QPushButton { background-color: #f3f2f1; color: #323130; border: 1px solid #c8c6c4; padding: 8px 16px; border-radius: 4px; }")
                accent_btn.setStyleSheet("QPushButton { background-color: #8764b8; color: white; border: none; padding: 8px 16px; border-radius: 4px; }")
                
                styles_layout.addWidget(primary_btn, 1, 0)
                styles_layout.addWidget(secondary_btn, 1, 1)
                styles_layout.addWidget(accent_btn, 1, 2)
                styles_layout.addWidget(disabled_btn, 1, 3)
            
            # Icon buttons
            icon_label = QLabel("Icon Buttons:")
            icon_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            styles_layout.addWidget(icon_label, 2, 0, 1, 4)
            
            if FORMS_AVAILABLE:
                # Icon button
                icon_btn = FluentIconButton("⚙️")
                icon_btn.setToolTip("Settings")
                
                # Icon with text
                icon_text_btn = FluentButton("📁 Open File")
                
                # Toggle button
                toggle_btn = FluentToggleButton("🔒 Toggle Lock")
                
                styles_layout.addWidget(icon_btn, 3, 0)
                styles_layout.addWidget(icon_text_btn, 3, 1)
                styles_layout.addWidget(toggle_btn, 3, 2)
            else:
                # Fallback icon buttons
                icon_btn = QPushButton("⚙️")
                icon_btn.setFixedSize(40, 40)
                icon_btn.setToolTip("Settings")
                
                icon_text_btn = QPushButton("📁 Open File")
                toggle_btn = QPushButton("🔒 Toggle Lock")
                toggle_btn.setCheckable(True)
                
                styles_layout.addWidget(icon_btn, 3, 0)
                styles_layout.addWidget(icon_text_btn, 3, 1)
                styles_layout.addWidget(toggle_btn, 3, 2)
            
            layout.addWidget(styles_group)
            
            # Button interactions
            interactions_group = QGroupBox("Button Interactions")
            interactions_layout = QVBoxLayout(interactions_group)
            
            # Click counter
            self.click_count = 0
            self.click_label = QLabel(f"Button clicked {self.click_count} times")
            
            click_btn = QPushButton("Click Me!")
            click_btn.clicked.connect(self.on_button_clicked)
            
            # Hover detection
            self.hover_label = QLabel("Hover state: Not hovering")
            hover_btn = QPushButton("Hover Over Me")
            hover_btn.enterEvent = lambda e: self.hover_label.setText("Hover state: Hovering")
            hover_btn.leaveEvent = lambda e: self.hover_label.setText("Hover state: Not hovering")
            
            interactions_layout.addWidget(self.click_label)
            interactions_layout.addWidget(click_btn)
            interactions_layout.addWidget(self.hover_label)
            interactions_layout.addWidget(hover_btn)
            
            layout.addWidget(interactions_group)
            
            # Usage examples
            usage_group = QGroupBox("Button Usage Examples")
            usage_layout = QVBoxLayout(usage_group)
            
            usage_text = QLabel("""
<b>Button Types & When to Use:</b><br><br>

<b>Primary Button:</b> Main action on a page/dialog (Save, Submit, OK)<br>
<b>Secondary Button:</b> Secondary actions (Cancel, Back, More Options)<br>
<b>Accent Button:</b> Special actions that need attention (Delete, Purchase)<br>
<b>Icon Button:</b> Compact actions in toolbars (Edit, Delete, Refresh)<br>
<b>Toggle Button:</b> On/off states (Bold, Italic, Favorite)<br><br>

<b>Code Examples:</b><br>
<code>
# Primary action button<br>
save_btn = FluentButton("Save")<br>
save_btn.set_style("primary")<br>
save_btn.clicked.connect(self.save_data)<br><br>

# Icon button with tooltip<br>
settings_btn = FluentIconButton("⚙️")<br>
settings_btn.setToolTip("Open Settings")<br><br>

# Toggle button for state<br>
bold_btn = FluentToggleButton("B")<br>
bold_btn.toggled.connect(self.toggle_bold)<br>
</code>
""")
            usage_text.setWordWrap(True)
            usage_layout.addWidget(usage_text)
            
            layout.addWidget(usage_group)
            layout.addStretch()
            
            self.tab_widget.addTab(tab, "Buttons")
            
        def create_text_inputs_tab(self):
            """Create text input examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Text input types
            types_group = QGroupBox("Text Input Types")
            types_layout = QGridLayout(types_group)
            
            # Single line inputs
            types_layout.addWidget(QLabel("Single Line Input:"), 0, 0)
            if FORMS_AVAILABLE:
                self.line_edit = FluentLineEdit()
                self.line_edit.setPlaceholderText("Enter your name...")
            else:
                self.line_edit = QLineEdit()
                self.line_edit.setPlaceholderText("Enter your name...")
                self.line_edit.setStyleSheet("""
                    QLineEdit {
                        border: 2px solid #c8c6c4;
                        border-radius: 4px;
                        padding: 8px 12px;
                        font-size: 14px;
                    }
                    QLineEdit:focus {
                        border-color: #0078d4;
                    }
                """)
            types_layout.addWidget(self.line_edit, 0, 1)
            
            # Password input
            types_layout.addWidget(QLabel("Password Input:"), 1, 0)
            if FORMS_AVAILABLE:
                self.password_edit = FluentPasswordEdit()
                self.password_edit.setPlaceholderText("Enter password...")
            else:
                self.password_edit = QLineEdit()
                self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
                self.password_edit.setPlaceholderText("Enter password...")
                self.password_edit.setStyleSheet(self.line_edit.styleSheet())
            types_layout.addWidget(self.password_edit, 1, 1)
            
            # Multi-line text
            types_layout.addWidget(QLabel("Multi-line Text:"), 2, 0)
            if FORMS_AVAILABLE:
                self.text_edit = FluentTextEdit()
                self.text_edit.setPlaceholderText("Enter detailed description...")
            else:
                self.text_edit = QTextEdit()
                self.text_edit.setPlaceholderText("Enter detailed description...")
                self.text_edit.setMaximumHeight(120)
                self.text_edit.setStyleSheet("""
                    QTextEdit {
                        border: 2px solid #c8c6c4;
                        border-radius: 4px;
                        padding: 8px 12px;
                        font-size: 14px;
                    }
                    QTextEdit:focus {
                        border-color: #0078d4;
                    }
                """)
            types_layout.addWidget(self.text_edit, 2, 1)
            
            layout.addWidget(types_group)
            
            # Text input features
            features_group = QGroupBox("Input Features & Validation")
            features_layout = QVBoxLayout(features_group)
            
            # Character counter
            counter_layout = QHBoxLayout()
            self.counter_input = QLineEdit()
            self.counter_input.setPlaceholderText("Type something (max 50 chars)...")
            self.counter_input.setMaxLength(50)
            self.char_counter = QLabel("0/50")
            self.counter_input.textChanged.connect(self.update_char_counter)
            
            counter_layout.addWidget(QLabel("Character Counter:"))
            counter_layout.addWidget(self.counter_input)
            counter_layout.addWidget(self.char_counter)
            
            # Validation example
            validation_layout = QHBoxLayout()
            self.email_input = QLineEdit()
            self.email_input.setPlaceholderText("Enter email address...")
            self.validation_label = QLabel("✓ Valid email")
            self.validation_label.setStyleSheet("color: green;")
            self.validation_label.hide()
            self.email_input.textChanged.connect(self.validate_email)
            
            validation_layout.addWidget(QLabel("Email Validation:"))
            validation_layout.addWidget(self.email_input)
            validation_layout.addWidget(self.validation_label)
            
            features_layout.addLayout(counter_layout)
            features_layout.addLayout(validation_layout)
            
            layout.addWidget(features_group)
            
            # Usage examples
            usage_group = QGroupBox("Text Input Usage Examples")
            usage_layout = QVBoxLayout(usage_group)
            
            usage_text = QLabel("""
<b>Text Input Best Practices:</b><br><br>

<b>Placeholder Text:</b> Provide helpful hints about expected input format<br>
<b>Validation:</b> Real-time feedback for invalid input<br>
<b>Character Limits:</b> Show remaining characters for limited fields<br>
<b>Error States:</b> Clear visual indication of validation errors<br>
<b>Password Fields:</b> Show/hide toggle for better UX<br><br>

<b>Common Input Types:</b><br>
• <b>FluentLineEdit:</b> Single-line text, names, titles<br>
• <b>FluentPasswordEdit:</b> Secure password input with show/hide<br>
• <b>FluentTextEdit:</b> Multi-line descriptions, comments<br>
• <b>FluentSearchBox:</b> Search inputs with suggestions<br>
• <b>FluentAutoSuggestBox:</b> Autocomplete functionality<br><br>

<b>Code Example:</b><br>
<code>
email_input = FluentLineEdit()<br>
email_input.setPlaceholderText("your@email.com")<br>
email_input.set_validation_pattern(r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$')<br>
email_input.textChanged.connect(self.validate_input)<br>
</code>
""")
            usage_text.setWordWrap(True)
            usage_layout.addWidget(usage_text)
            
            layout.addWidget(usage_group)
            layout.addStretch()
            
            self.tab_widget.addTab(tab, "Text Inputs")
            
        def create_selection_controls_tab(self):
            """Create selection controls examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Checkbox examples
            checkbox_group = QGroupBox("Checkboxes & Radio Buttons")
            checkbox_layout = QGridLayout(checkbox_group)
            
            # Checkboxes
            checkbox_layout.addWidget(QLabel("Checkboxes:"), 0, 0)
            
            if FORMS_AVAILABLE:
                self.check1 = FluentCheckBox("Enable notifications")
                self.check2 = FluentCheckBox("Auto-save documents")
                self.check3 = FluentCheckBox("Dark mode")
                self.check3.setChecked(True)
            else:
                self.check1 = QCheckBox("Enable notifications")
                self.check2 = QCheckBox("Auto-save documents")
                self.check3 = QCheckBox("Dark mode")
                self.check3.setChecked(True)
                
                # Style checkboxes
                checkbox_style = """
                    QCheckBox {
                        font-size: 14px;
                        spacing: 8px;
                    }
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                        border: 2px solid #c8c6c4;
                        border-radius: 3px;
                        background-color: white;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #0078d4;
                        border-color: #0078d4;
                    }
                """
                for checkbox in [self.check1, self.check2, self.check3]:
                    checkbox.setStyleSheet(checkbox_style)
            
            checkbox_col = QVBoxLayout()
            checkbox_col.addWidget(self.check1)
            checkbox_col.addWidget(self.check2)
            checkbox_col.addWidget(self.check3)
            checkbox_layout.addLayout(checkbox_col, 0, 1)
            
            # Radio buttons
            checkbox_layout.addWidget(QLabel("Radio Buttons:"), 1, 0)
            
            self.radio_group = QButtonGroup()
            if FORMS_AVAILABLE:
                self.radio1 = FluentRadioButton("Small")
                self.radio2 = FluentRadioButton("Medium")
                self.radio3 = FluentRadioButton("Large")
            else:
                self.radio1 = QRadioButton("Small")
                self.radio2 = QRadioButton("Medium")
                self.radio3 = QRadioButton("Large")
                
                # Style radio buttons
                radio_style = """
                    QRadioButton {
                        font-size: 14px;
                        spacing: 8px;
                    }
                    QRadioButton::indicator {
                        width: 18px;
                        height: 18px;
                        border: 2px solid #c8c6c4;
                        border-radius: 9px;
                        background-color: white;
                    }
                    QRadioButton::indicator:checked {
                        background-color: #0078d4;
                        border-color: #0078d4;
                    }
                """
                for radio in [self.radio1, self.radio2, self.radio3]:
                    radio.setStyleSheet(radio_style)
            
            self.radio2.setChecked(True)  # Default selection
            self.radio_group.addButton(self.radio1)
            self.radio_group.addButton(self.radio2)
            self.radio_group.addButton(self.radio3)
            
            radio_col = QVBoxLayout()
            radio_col.addWidget(self.radio1)
            radio_col.addWidget(self.radio2)
            radio_col.addWidget(self.radio3)
            checkbox_layout.addLayout(radio_col, 1, 1)
            
            layout.addWidget(checkbox_group)
            
            # Switch controls
            switch_group = QGroupBox("Switches & Toggles")
            switch_layout = QGridLayout(switch_group)
            
            if FORMS_AVAILABLE:
                # Toggle switches
                switch_layout.addWidget(QLabel("Toggle Switches:"), 0, 0)
                
                self.switch1 = FluentSwitch()
                self.switch1.setText("WiFi")
                
                self.switch2 = FluentSwitch()
                self.switch2.setText("Bluetooth")
                self.switch2.setChecked(True)
                
                switch_col = QVBoxLayout()
                switch_col.addWidget(self.switch1)
                switch_col.addWidget(self.switch2)
                switch_layout.addLayout(switch_col, 0, 1)
                
                # Toggle buttons
                switch_layout.addWidget(QLabel("Toggle Buttons:"), 1, 0)
                
                self.toggle1 = FluentToggleSwitch("Bold")
                self.toggle2 = FluentToggleSwitch("Italic")
                self.toggle3 = FluentToggleSwitch("Underline")
                
                toggle_row = QHBoxLayout()
                toggle_row.addWidget(self.toggle1)
                toggle_row.addWidget(self.toggle2)
                toggle_row.addWidget(self.toggle3)
                switch_layout.addLayout(toggle_row, 1, 1)
            else:
                # Fallback with checkboxes styled as switches
                switch_layout.addWidget(QLabel("Switches (styled):"), 0, 0)
                
                self.switch1 = QCheckBox("WiFi")
                self.switch2 = QCheckBox("Bluetooth")
                self.switch2.setChecked(True)
                
                switch_style = """
                    QCheckBox {
                        font-size: 14px;
                        spacing: 8px;
                    }
                    QCheckBox::indicator {
                        width: 40px;
                        height: 20px;
                        border: 2px solid #c8c6c4;
                        border-radius: 10px;
                        background-color: #e5e5e5;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #0078d4;
                        border-color: #0078d4;
                    }
                """
                self.switch1.setStyleSheet(switch_style)
                self.switch2.setStyleSheet(switch_style)
                
                switch_col = QVBoxLayout()
                switch_col.addWidget(self.switch1)
                switch_col.addWidget(self.switch2)
                switch_layout.addLayout(switch_col, 0, 1)
            
            layout.addWidget(switch_group)
            
            # Selection state tracking
            state_group = QGroupBox("Selection State Tracking")
            state_layout = QVBoxLayout(state_group)
            
            self.selection_status = QLabel("Make some selections to see the state")
            state_layout.addWidget(self.selection_status)
            
            # Connect signals to update status
            self.check1.toggled.connect(self.update_selection_status)
            self.check2.toggled.connect(self.update_selection_status)
            self.check3.toggled.connect(self.update_selection_status)
            self.radio_group.buttonToggled.connect(self.update_selection_status)
            
            layout.addWidget(state_group)
            
            # Usage examples
            usage_group = QGroupBox("Selection Controls Usage")
            usage_layout = QVBoxLayout(usage_group)
            
            usage_text = QLabel("""
<b>When to Use Each Control:</b><br><br>

<b>Checkboxes:</b> Multiple independent options (permissions, features)<br>
<b>Radio Buttons:</b> Single choice from multiple options (size, color)<br>
<b>Toggle Switches:</b> On/off states with immediate effect (WiFi, notifications)<br>
<b>Toggle Buttons:</b> State changes in toolbars (bold, italic, alignment)<br><br>

<b>Best Practices:</b><br>
• Use clear, descriptive labels<br>
• Group related options together<br>
• Provide sensible defaults<br>
• Use indeterminate state for partial selections<br>
• Consider using switches for settings that take effect immediately<br><br>

<b>Code Example:</b><br>
<code>
# Checkbox with state tracking<br>
notifications = FluentCheckBox("Enable notifications")<br>
notifications.toggled.connect(self.toggle_notifications)<br><br>

# Radio button group<br>
size_group = QButtonGroup()<br>
small_radio = FluentRadioButton("Small")<br>
size_group.addButton(small_radio)<br>
</code>
""")
            usage_text.setWordWrap(True)
            usage_layout.addWidget(usage_text)
            
            layout.addWidget(usage_group)
            layout.addStretch()
            
            self.tab_widget.addTab(tab, "Selection Controls")
            
        def create_numeric_inputs_tab(self):
            """Create numeric input examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Slider controls
            sliders_group = QGroupBox("Sliders & Range Controls")
            sliders_layout = QGridLayout(sliders_group)
            
            # Horizontal slider
            sliders_layout.addWidget(QLabel("Volume:"), 0, 0)
            
            if FORMS_AVAILABLE:
                self.volume_slider = FluentSlider(Qt.Orientation.Horizontal)
                self.volume_slider.setRange(0, 100)
                self.volume_slider.setValue(75)
            else:
                self.volume_slider = QSlider(Qt.Orientation.Horizontal)
                self.volume_slider.setRange(0, 100)
                self.volume_slider.setValue(75)
                self.volume_slider.setStyleSheet("""
                    QSlider::groove:horizontal {
                        border: 1px solid #c8c6c4;
                        height: 6px;
                        background: #f3f2f1;
                        border-radius: 3px;
                    }
                    QSlider::handle:horizontal {
                        background: #0078d4;
                        border: 2px solid #005a9e;
                        width: 18px;
                        margin: -6px 0;
                        border-radius: 9px;
                    }
                    QSlider::sub-page:horizontal {
                        background: #0078d4;
                        border-radius: 3px;
                    }
                """)
            
            self.volume_label = QLabel("75%")
            self.volume_slider.valueChanged.connect(lambda v: self.volume_label.setText(f"{v}%"))
            
            slider_layout = QHBoxLayout()
            slider_layout.addWidget(self.volume_slider)
            slider_layout.addWidget(self.volume_label)
            sliders_layout.addLayout(slider_layout, 0, 1)
            
            # Vertical slider
            sliders_layout.addWidget(QLabel("Brightness:"), 1, 0)
            
            if FORMS_AVAILABLE:
                self.brightness_slider = FluentSlider(Qt.Orientation.Vertical)
                self.brightness_slider.setRange(0, 100)
                self.brightness_slider.setValue(50)
            else:
                self.brightness_slider = QSlider(Qt.Orientation.Vertical)
                self.brightness_slider.setRange(0, 100)
                self.brightness_slider.setValue(50)
            
            self.brightness_slider.setFixedHeight(100)
            self.brightness_label = QLabel("50%")
            self.brightness_slider.valueChanged.connect(lambda v: self.brightness_label.setText(f"{v}%"))
            
            brightness_layout = QHBoxLayout()
            brightness_layout.addWidget(self.brightness_slider)
            brightness_layout.addWidget(self.brightness_label)
            sliders_layout.addLayout(brightness_layout, 1, 1)
            
            layout.addWidget(sliders_group)
            
            # Spin boxes
            spinbox_group = QGroupBox("Spin Boxes & Number Inputs")
            spinbox_layout = QGridLayout(spinbox_group)
            
            # Integer spin box
            spinbox_layout.addWidget(QLabel("Quantity:"), 0, 0)
            
            if FORMS_AVAILABLE:
                self.quantity_spin = FluentSpinBox()
                self.quantity_spin.setRange(1, 999)
                self.quantity_spin.setValue(1)
            else:
                self.quantity_spin = QSpinBox()
                self.quantity_spin.setRange(1, 999)
                self.quantity_spin.setValue(1)
                self.quantity_spin.setStyleSheet("""
                    QSpinBox {
                        border: 2px solid #c8c6c4;
                        border-radius: 4px;
                        padding: 6px 8px;
                        font-size: 14px;
                        min-width: 80px;
                    }
                    QSpinBox:focus {
                        border-color: #0078d4;
                    }
                """)
            
            spinbox_layout.addWidget(self.quantity_spin, 0, 1)
            
            # Double spin box
            spinbox_layout.addWidget(QLabel("Price ($):"), 1, 0)
            
            if FORMS_AVAILABLE:
                self.price_spin = FluentDoubleSpinBox()
                self.price_spin.setRange(0.00, 9999.99)
                self.price_spin.setDecimals(2)
                self.price_spin.setValue(19.99)
            else:
                from PySide6.QtWidgets import QDoubleSpinBox
                self.price_spin = QDoubleSpinBox()
                self.price_spin.setRange(0.00, 9999.99)
                self.price_spin.setDecimals(2)
                self.price_spin.setValue(19.99)
                self.price_spin.setStyleSheet(self.quantity_spin.styleSheet())
            
            spinbox_layout.addWidget(self.price_spin, 1, 1)
            
            layout.addWidget(spinbox_group)
            
            # Combo boxes
            combo_group = QGroupBox("Dropdown Selections")
            combo_layout = QGridLayout(combo_group)
            
            # Simple combo box
            combo_layout.addWidget(QLabel("Country:"), 0, 0)
            
            if FORMS_AVAILABLE:
                self.country_combo = FluentComboBox()
            else:
                self.country_combo = QComboBox()
                self.country_combo.setStyleSheet("""
                    QComboBox {
                        border: 2px solid #c8c6c4;
                        border-radius: 4px;
                        padding: 6px 8px;
                        font-size: 14px;
                        min-width: 150px;
                    }
                    QComboBox:focus {
                        border-color: #0078d4;
                    }
                    QComboBox::drop-down {
                        border: none;
                        width: 20px;
                    }
                    QComboBox::down-arrow {
                        image: none;
                        border: none;
                    }
                """)
            
            countries = ["United States", "Canada", "United Kingdom", "Germany", "France", "Japan", "Australia"]
            self.country_combo.addItems(countries)
            self.country_combo.setCurrentText("United States")
            
            combo_layout.addWidget(self.country_combo, 0, 1)
            
            # Editable combo box
            combo_layout.addWidget(QLabel("Theme:"), 1, 0)
            
            self.theme_combo = QComboBox()
            self.theme_combo.setEditable(True)
            self.theme_combo.setStyleSheet(self.country_combo.styleSheet())
            themes = ["Light", "Dark", "Auto", "High Contrast"]
            self.theme_combo.addItems(themes)
            self.theme_combo.setCurrentText("Light")
            
            combo_layout.addWidget(self.theme_combo, 1, 1)
            
            layout.addWidget(combo_group)
            
            # Value display
            values_group = QGroupBox("Current Values")
            values_layout = QVBoxLayout(values_group)
            
            self.values_display = QLabel()
            self.update_values_display()
            values_layout.addWidget(self.values_display)
            
            # Connect all controls to update display
            self.volume_slider.valueChanged.connect(self.update_values_display)
            self.brightness_slider.valueChanged.connect(self.update_values_display)
            self.quantity_spin.valueChanged.connect(self.update_values_display)
            self.price_spin.valueChanged.connect(self.update_values_display)
            self.country_combo.currentTextChanged.connect(self.update_values_display)
            self.theme_combo.currentTextChanged.connect(self.update_values_display)
            
            layout.addWidget(values_group)
            
            # Usage examples
            usage_group = QGroupBox("Numeric Input Usage")
            usage_layout = QVBoxLayout(usage_group)
            
            usage_text = QLabel("""
<b>Numeric Input Guidelines:</b><br><br>

<b>Sliders:</b> When users need visual feedback or relative values (volume, brightness)<br>
<b>Spin Boxes:</b> Precise numeric input with increment/decrement (quantity, age)<br>
<b>Combo Boxes:</b> Predefined choices with optional custom input (themes, sizes)<br><br>

<b>Best Practices:</b><br>
• Set appropriate min/max ranges<br>
• Use step increments that make sense<br>
• Show current values clearly<br>
• Provide keyboard shortcuts (arrow keys, page up/down)<br>
• Consider using prefixes/suffixes for units<br><br>

<b>Code Example:</b><br>
<code>
# Slider with custom range and step<br>
volume = FluentSlider(Qt.Orientation.Horizontal)<br>
volume.setRange(0, 100)<br>
volume.setSingleStep(5)<br>
volume.valueChanged.connect(self.update_volume)<br><br>

# Spin box with custom formatting<br>
price = FluentDoubleSpinBox()<br>
price.setPrefix("$")<br>
price.setDecimals(2)<br>
</code>
""")
            usage_text.setWordWrap(True)
            usage_layout.addWidget(usage_text)
            
            layout.addWidget(usage_group)
            layout.addStretch()
            
            self.tab_widget.addTab(tab, "Numeric Inputs")
            
        def create_advanced_controls_tab(self):
            """Create advanced controls examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Progress indicators
            progress_group = QGroupBox("Progress Indicators")
            progress_layout = QVBoxLayout(progress_group)
            
            # Determinate progress
            det_layout = QHBoxLayout()
            det_layout.addWidget(QLabel("File Download:"))
            
            self.download_progress = QProgressBar()
            self.download_progress.setRange(0, 100)
            self.download_progress.setValue(0)
            self.download_progress.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #c8c6c4;
                    border-radius: 5px;
                    text-align: center;
                    font-size: 12px;
                }
                QProgressBar::chunk {
                    background-color: #0078d4;
                    border-radius: 3px;
                }
            """)
            
            self.progress_btn = QPushButton("Start Download")
            self.progress_btn.clicked.connect(self.start_progress_demo)
            
            det_layout.addWidget(self.download_progress)
            det_layout.addWidget(self.progress_btn)
            progress_layout.addLayout(det_layout)
            
            # Indeterminate progress
            indet_layout = QHBoxLayout()
            indet_layout.addWidget(QLabel("Processing:"))
            
            self.processing_progress = QProgressBar()
            self.processing_progress.setRange(0, 0)  # Indeterminate
            self.processing_progress.setVisible(False)
            self.processing_progress.setStyleSheet(self.download_progress.styleSheet())
            
            self.process_btn = QPushButton("Start Processing")
            self.process_btn.clicked.connect(self.toggle_processing)
            
            indet_layout.addWidget(self.processing_progress)
            indet_layout.addWidget(self.process_btn)
            progress_layout.addLayout(indet_layout)
            
            layout.addWidget(progress_group)
            
            # Status indicators
            status_group = QGroupBox("Status Indicators & Badges")
            status_layout = QGridLayout(status_group)
            
            # Status labels with colored indicators
            status_layout.addWidget(QLabel("Connection Status:"), 0, 0)
            self.connection_status = QLabel("🟢 Connected")
            self.connection_status.setStyleSheet("font-weight: bold; color: #107c10;")
            status_layout.addWidget(self.connection_status, 0, 1)
            
            status_layout.addWidget(QLabel("Sync Status:"), 1, 0)
            self.sync_status = QLabel("🟡 Syncing...")
            self.sync_status.setStyleSheet("font-weight: bold; color: #ff8c00;")
            status_layout.addWidget(self.sync_status, 1, 1)
            
            status_layout.addWidget(QLabel("System Health:"), 2, 0)
            self.health_status = QLabel("🔴 Issues Detected")
            self.health_status.setStyleSheet("font-weight: bold; color: #d13438;")
            status_layout.addWidget(self.health_status, 2, 1)
            
            # Toggle status button
            self.status_btn = QPushButton("Cycle Status")
            self.status_btn.clicked.connect(self.cycle_status)
            self.status_index = 0
            status_layout.addWidget(self.status_btn, 3, 0, 1, 2)
            
            layout.addWidget(status_group)
            
            # Interactive controls
            interactive_group = QGroupBox("Interactive Controls")
            interactive_layout = QVBoxLayout(interactive_group)
            
            # Multi-state button
            multi_layout = QHBoxLayout()
            multi_layout.addWidget(QLabel("Multi-state Control:"))
            
            self.multi_btn = QPushButton("▶️ Play")
            self.multi_btn.clicked.connect(self.toggle_play_state)
            self.is_playing = False
            
            multi_layout.addWidget(self.multi_btn)
            multi_layout.addStretch()
            interactive_layout.addLayout(multi_layout)
            
            # Rating control (star rating simulation)
            rating_layout = QHBoxLayout()
            rating_layout.addWidget(QLabel("Rating:"))
            
            self.rating_buttons = []
            for i in range(5):
                star_btn = QPushButton("☆")
                star_btn.setFixedSize(30, 30)
                star_btn.clicked.connect(lambda checked, idx=i: self.set_rating(idx))
                self.rating_buttons.append(star_btn)
                rating_layout.addWidget(star_btn)
            
            self.rating_value = 0
            rating_layout.addStretch()
            interactive_layout.addLayout(rating_layout)
            
            layout.addWidget(interactive_group)
            
            # Usage examples
            usage_group = QGroupBox("Advanced Controls Usage")
            usage_layout = QVBoxLayout(usage_group)
            
            usage_text = QLabel("""
<b>Advanced Control Patterns:</b><br><br>

<b>Progress Bars:</b><br>
• Determinate: Show exact progress (file uploads, installations)<br>
• Indeterminate: Show activity without specific progress (searching, processing)<br><br>

<b>Status Indicators:</b><br>
• Use colors consistently (green=good, yellow=warning, red=error)<br>
• Include both visual and text indicators<br>
• Update status in real-time when possible<br><br>

<b>Multi-state Controls:</b><br>
• Clearly show current state (play/pause, expand/collapse)<br>
• Use familiar icons and conventions<br>
• Provide keyboard shortcuts<br><br>

<b>Interactive Feedback:</b><br>
• Immediate visual response to user actions<br>
• Smooth transitions between states<br>
• Clear affordances (what's clickable)<br>
""")
            usage_text.setWordWrap(True)
            usage_layout.addWidget(usage_text)
            
            layout.addWidget(usage_group)
            layout.addStretch()
            
            # Setup timers for demos
            self.progress_timer = QTimer()
            self.progress_timer.timeout.connect(self.update_progress)
            
            self.tab_widget.addTab(tab, "Advanced Controls")
            
        def create_form_examples_tab(self):
            """Create complete form examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Scroll area for the form
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
            form_widget = QWidget()
            form_layout = QVBoxLayout(form_widget)
            
            # User registration form
            reg_group = QGroupBox("User Registration Form")
            reg_layout = QGridLayout(reg_group)
            
            # Personal info
            reg_layout.addWidget(QLabel("First Name:*"), 0, 0)
            self.first_name = QLineEdit()
            self.first_name.setPlaceholderText("Enter your first name")
            reg_layout.addWidget(self.first_name, 0, 1)
            
            reg_layout.addWidget(QLabel("Last Name:*"), 1, 0)
            self.last_name = QLineEdit()
            self.last_name.setPlaceholderText("Enter your last name")
            reg_layout.addWidget(self.last_name, 1, 1)
            
            reg_layout.addWidget(QLabel("Email:*"), 2, 0)
            self.reg_email = QLineEdit()
            self.reg_email.setPlaceholderText("your@email.com")
            reg_layout.addWidget(self.reg_email, 2, 1)
            
            reg_layout.addWidget(QLabel("Password:*"), 3, 0)
            self.reg_password = QLineEdit()
            self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.reg_password.setPlaceholderText("Minimum 8 characters")
            reg_layout.addWidget(self.reg_password, 3, 1)
            
            # Preferences
            reg_layout.addWidget(QLabel("Age Group:"), 4, 0)
            self.age_combo = QComboBox()
            self.age_combo.addItems(["18-24", "25-34", "35-44", "45-54", "55-64", "65+"])
            reg_layout.addWidget(self.age_combo, 4, 1)
            
            reg_layout.addWidget(QLabel("Interests:"), 5, 0)
            interests_widget = QWidget()
            interests_layout = QVBoxLayout(interests_widget)
            interests_layout.setContentsMargins(0, 0, 0, 0)
            
            self.tech_interest = QCheckBox("Technology")
            self.sports_interest = QCheckBox("Sports")
            self.music_interest = QCheckBox("Music")
            self.travel_interest = QCheckBox("Travel")
            
            interests_layout.addWidget(self.tech_interest)
            interests_layout.addWidget(self.sports_interest)
            interests_layout.addWidget(self.music_interest)
            interests_layout.addWidget(self.travel_interest)
            
            reg_layout.addWidget(interests_widget, 5, 1)
            
            # Newsletter subscription
            self.newsletter_check = QCheckBox("Subscribe to newsletter")
            reg_layout.addWidget(self.newsletter_check, 6, 0, 1, 2)
            
            # Terms agreement
            self.terms_check = QCheckBox("I agree to the Terms of Service")
            reg_layout.addWidget(self.terms_check, 7, 0, 1, 2)
            
            # Form buttons
            button_layout = QHBoxLayout()
            self.register_btn = QPushButton("Register")
            self.register_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:disabled {
                    background-color: #c8c6c4;
                }
            """)
            self.register_btn.clicked.connect(self.validate_form)
            
            self.clear_btn = QPushButton("Clear Form")
            self.clear_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f3f2f1;
                    color: #323130;
                    border: 1px solid #c8c6c4;
                    padding: 10px 20px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #e1dfdd;
                }
            """)
            self.clear_btn.clicked.connect(self.clear_form)
            
            button_layout.addWidget(self.register_btn)
            button_layout.addWidget(self.clear_btn)
            button_layout.addStretch()
            
            reg_layout.addLayout(button_layout, 8, 0, 1, 2)
            
            form_layout.addWidget(reg_group)
            
            # Form validation feedback
            self.form_feedback = QLabel()
            self.form_feedback.setStyleSheet("color: #d13438; font-weight: bold; padding: 10px;")
            self.form_feedback.hide()
            form_layout.addWidget(self.form_feedback)
            
            # Settings form example
            settings_group = QGroupBox("Application Settings")
            settings_layout = QGridLayout(settings_group)
            
            # Appearance settings
            settings_layout.addWidget(QLabel("Theme:"), 0, 0)
            self.settings_theme = QComboBox()
            self.settings_theme.addItems(["Light", "Dark", "Auto"])
            settings_layout.addWidget(self.settings_theme, 0, 1)
            
            settings_layout.addWidget(QLabel("Font Size:"), 1, 0)
            self.font_size_slider = QSlider(Qt.Orientation.Horizontal)
            self.font_size_slider.setRange(8, 24)
            self.font_size_slider.setValue(12)
            self.font_size_label = QLabel("12px")
            self.font_size_slider.valueChanged.connect(lambda v: self.font_size_label.setText(f"{v}px"))
            
            font_layout = QHBoxLayout()
            font_layout.addWidget(self.font_size_slider)
            font_layout.addWidget(self.font_size_label)
            settings_layout.addLayout(font_layout, 1, 1)
            
            # Notification settings
            settings_layout.addWidget(QLabel("Notifications:"), 2, 0)
            notifications_widget = QWidget()
            notifications_layout = QVBoxLayout(notifications_widget)
            notifications_layout.setContentsMargins(0, 0, 0, 0)
            
            self.email_notifications = QCheckBox("Email notifications")
            self.push_notifications = QCheckBox("Push notifications")
            self.sound_notifications = QCheckBox("Sound notifications")
            
            notifications_layout.addWidget(self.email_notifications)
            notifications_layout.addWidget(self.push_notifications)
            notifications_layout.addWidget(self.sound_notifications)
            
            settings_layout.addWidget(notifications_widget, 2, 1)
            
            # Auto-save interval
            settings_layout.addWidget(QLabel("Auto-save (minutes):"), 3, 0)
            self.autosave_spin = QSpinBox()
            self.autosave_spin.setRange(1, 60)
            self.autosave_spin.setValue(5)
            settings_layout.addWidget(self.autosave_spin, 3, 1)
            
            # Settings buttons
            settings_button_layout = QHBoxLayout()
            self.save_settings_btn = QPushButton("Save Settings")
            self.save_settings_btn.clicked.connect(self.save_settings)
            
            self.reset_settings_btn = QPushButton("Reset to Defaults")
            self.reset_settings_btn.clicked.connect(self.reset_settings)
            
            settings_button_layout.addWidget(self.save_settings_btn)
            settings_button_layout.addWidget(self.reset_settings_btn)
            settings_button_layout.addStretch()
            
            settings_layout.addLayout(settings_button_layout, 4, 0, 1, 2)
            
            form_layout.addWidget(settings_group)
            
            scroll.setWidget(form_widget)
            layout.addWidget(scroll)
            
            self.tab_widget.addTab(tab, "Complete Forms")
        
        # Event handlers and utility methods
        def on_button_clicked(self):
            """Handle button click for counter demo."""
            self.click_count += 1
            self.click_label.setText(f"Button clicked {self.click_count} times")
            
        def update_char_counter(self, text):
            """Update character counter."""
            count = len(text)
            self.char_counter.setText(f"{count}/50")
            
            if count > 40:
                self.char_counter.setStyleSheet("color: #d13438; font-weight: bold;")
            elif count > 30:
                self.char_counter.setStyleSheet("color: #ff8c00; font-weight: bold;")
            else:
                self.char_counter.setStyleSheet("color: #323130;")
                
        def validate_email(self, text):
            """Validate email format."""
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            if text and re.match(email_pattern, text):
                self.validation_label.setText("✓ Valid email")
                self.validation_label.setStyleSheet("color: #107c10; font-weight: bold;")
                self.validation_label.show()
            elif text:
                self.validation_label.setText("✗ Invalid email")
                self.validation_label.setStyleSheet("color: #d13438; font-weight: bold;")
                self.validation_label.show()
            else:
                self.validation_label.hide()
                
        def update_selection_status(self):
            """Update selection status display."""
            checked_items = []
            if self.check1.isChecked():
                checked_items.append("Notifications")
            if self.check2.isChecked():
                checked_items.append("Auto-save")
            if self.check3.isChecked():
                checked_items.append("Dark mode")
                
            checked_radio = "None"
            if self.radio1.isChecked():
                checked_radio = "Small"
            elif self.radio2.isChecked():
                checked_radio = "Medium"
            elif self.radio3.isChecked():
                checked_radio = "Large"
                
            status = f"Checkboxes: {', '.join(checked_items) if checked_items else 'None'}\n"
            status += f"Radio selection: {checked_radio}"
            
            self.selection_status.setText(status)
            
        def update_values_display(self):
            """Update numeric values display."""
            values = f"""Current Values:
Volume: {self.volume_slider.value()}%
Brightness: {self.brightness_slider.value()}%
Quantity: {self.quantity_spin.value()}
Price: ${self.price_spin.value():.2f}
Country: {self.country_combo.currentText()}
Theme: {self.theme_combo.currentText()}"""
            
            self.values_display.setText(values)
            
        def start_progress_demo(self):
            """Start progress bar demo."""
            self.download_progress.setValue(0)
            self.progress_btn.setText("Downloading...")
            self.progress_btn.setEnabled(False)
            self.progress_timer.start(100)  # Update every 100ms
            
        def update_progress(self):
            """Update progress bar value."""
            current = self.download_progress.value()
            if current < 100:
                self.download_progress.setValue(current + 2)
            else:
                self.progress_timer.stop()
                self.progress_btn.setText("Start Download")
                self.progress_btn.setEnabled(True)
                
        def toggle_processing(self):
            """Toggle processing indicator."""
            if self.processing_progress.isVisible():
                self.processing_progress.hide()
                self.process_btn.setText("Start Processing")
            else:
                self.processing_progress.show()
                self.process_btn.setText("Stop Processing")
                
        def cycle_status(self):
            """Cycle through different status states."""
            statuses = [
                ("🟢 Connected", "#107c10"),
                ("🟡 Connecting...", "#ff8c00"),
                ("🔴 Disconnected", "#d13438")
            ]
            
            self.status_index = (self.status_index + 1) % len(statuses)
            status_text, color = statuses[self.status_index]
            
            self.connection_status.setText(status_text)
            self.connection_status.setStyleSheet(f"font-weight: bold; color: {color};")
            
        def toggle_play_state(self):
            """Toggle play/pause state."""
            if self.is_playing:
                self.multi_btn.setText("▶️ Play")
                self.is_playing = False
            else:
                self.multi_btn.setText("⏸️ Pause")
                self.is_playing = True
                
        def set_rating(self, rating):
            """Set star rating."""
            self.rating_value = rating + 1
            
            for i, btn in enumerate(self.rating_buttons):
                if i <= rating:
                    btn.setText("★")
                    btn.setStyleSheet("color: #ff8c00; font-size: 16px;")
                else:
                    btn.setText("☆")
                    btn.setStyleSheet("color: #c8c6c4; font-size: 16px;")
                    
        def validate_form(self):
            """Validate registration form."""
            errors = []
            
            if not self.first_name.text().strip():
                errors.append("First name is required")
            if not self.last_name.text().strip():
                errors.append("Last name is required")
            if not self.reg_email.text().strip():
                errors.append("Email is required")
            if not self.reg_password.text() or len(self.reg_password.text()) < 8:
                errors.append("Password must be at least 8 characters")
            if not self.terms_check.isChecked():
                errors.append("You must agree to the Terms of Service")
                
            if errors:
                self.form_feedback.setText("Please fix the following errors:\n• " + "\n• ".join(errors))
                self.form_feedback.show()
            else:
                self.form_feedback.setText("✓ Registration successful!")
                self.form_feedback.setStyleSheet("color: #107c10; font-weight: bold; padding: 10px;")
                self.form_feedback.show()
                
        def clear_form(self):
            """Clear registration form."""
            self.first_name.clear()
            self.last_name.clear()
            self.reg_email.clear()
            self.reg_password.clear()
            self.age_combo.setCurrentIndex(0)
            
            for checkbox in [self.tech_interest, self.sports_interest, 
                           self.music_interest, self.travel_interest,
                           self.newsletter_check, self.terms_check]:
                checkbox.setChecked(False)
                
            self.form_feedback.hide()
            
        def save_settings(self):
            """Save application settings."""
            # In a real app, this would save to a config file or database
            print("Settings saved:")
            print(f"  Theme: {self.settings_theme.currentText()}")
            print(f"  Font Size: {self.font_size_slider.value()}px")
            print(f"  Email Notifications: {self.email_notifications.isChecked()}")
            print(f"  Push Notifications: {self.push_notifications.isChecked()}")
            print(f"  Sound Notifications: {self.sound_notifications.isChecked()}")
            print(f"  Auto-save Interval: {self.autosave_spin.value()} minutes")
            
        def reset_settings(self):
            """Reset settings to defaults."""
            self.settings_theme.setCurrentText("Light")
            self.font_size_slider.setValue(12)
            self.email_notifications.setChecked(False)
            self.push_notifications.setChecked(False)
            self.sound_notifications.setChecked(False)
            self.autosave_spin.setValue(5)
    
    # Create and show demo
    demo = BasicFormsDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
