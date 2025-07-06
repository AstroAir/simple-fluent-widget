#!/usr/bin/env python3
"""
Fluent Forms Components Demo

This example demonstrates the comprehensive usage of Fluent form components including
buttons, text inputs, checkboxes, sliders, combo boxes, and other form controls.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QGroupBox, QPushButton, QFrame, QTabWidget, QScrollArea,
    QSlider, QCheckBox, QRadioButton, QComboBox, QSpinBox, QLineEdit,
    QTextEdit, QButtonGroup, QFormLayout, QGridLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon


def main():
    """Run the forms demo application."""
    app = QApplication(sys.argv)
    
    # Import after QApplication is created
    try:
        from components.basic.forms.button import FluentButton, FluentIconButton, FluentToggleButton
        from components.basic.forms.textbox import FluentLineEdit, FluentTextEdit
        from components.basic.forms.checkbox import FluentCheckBox
        from components.basic.forms.radio import FluentRadioButton
        from components.basic.forms.slider import FluentSlider
        from components.basic.forms.combobox import FluentComboBox
        from components.basic.forms.spinbox import FluentSpinBox
        from components.basic.forms.switch import FluentSwitch
        from components.basic.forms.toggle import FluentToggle
        from components.basic.forms.passwordbox import FluentPasswordBox
        from components.basic.forms.searchbox import FluentSearchBox
        from components.basic.forms.numberbox import FluentNumberBox
        from components.basic.forms.autosuggestbox import FluentAutoSuggestBox
        COMPONENTS_AVAILABLE = True
    except ImportError as e:
        print(f"Import error: {e}")
        print("Some form components may not be available yet")
        COMPONENTS_AVAILABLE = False
    
    class FormsDemo(QMainWindow):
        """Main demo window showcasing Fluent form components."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Fluent Forms Components Demo")
            self.setGeometry(100, 100, 1200, 800)
            
            # Create central widget with scroll area
            scroll_area = QScrollArea()
            self.setCentralWidget(scroll_area)
            
            # Create main widget
            main_widget = QWidget()
            scroll_area.setWidget(main_widget)
            scroll_area.setWidgetResizable(True)
            
            # Create main layout
            main_layout = QVBoxLayout(main_widget)
            main_layout.setSpacing(20)
            main_layout.setContentsMargins(20, 20, 20, 20)
            
            # Add title
            title = QLabel("Fluent Forms Components Demo")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
            main_layout.addWidget(title)
            
            # Create component sections
            self.create_button_section(main_layout)
            self.create_text_input_section(main_layout)
            self.create_selection_section(main_layout)
            self.create_numeric_section(main_layout)
            self.create_advanced_section(main_layout)
            self.create_complete_form_example(main_layout)
            
        def create_button_section(self, parent_layout):
            """Create button components section."""
            group = QGroupBox("Button Components")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Button types
            buttons_layout = QHBoxLayout()
            
            if COMPONENTS_AVAILABLE:
                # Primary button
                primary_btn = FluentButton("Primary Button", button_type="primary")
                primary_btn.clicked.connect(lambda: self.show_message("Primary button clicked"))
                
                # Secondary button
                secondary_btn = FluentButton("Secondary Button", button_type="secondary")
                secondary_btn.clicked.connect(lambda: self.show_message("Secondary button clicked"))
                
                # Icon button
                icon_btn = FluentIconButton("⚙️", tooltip="Settings")
                icon_btn.clicked.connect(lambda: self.show_message("Icon button clicked"))
                
                # Toggle button
                toggle_btn = FluentToggleButton("Toggle Me")
                toggle_btn.toggled.connect(lambda checked: self.show_message(f"Toggle: {'On' if checked else 'Off'}"))
                
                buttons_layout.addWidget(primary_btn)
                buttons_layout.addWidget(secondary_btn)
                buttons_layout.addWidget(icon_btn)
                buttons_layout.addWidget(toggle_btn)
            else:
                # Fallback to standard buttons
                primary_btn = QPushButton("Primary Button")
                secondary_btn = QPushButton("Secondary Button")
                icon_btn = QPushButton("⚙️")
                toggle_btn = QPushButton("Toggle Me")
                
                # Style buttons
                primary_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #106ebe;
                    }
                """)
                
                secondary_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f3f2f1;
                        color: #323130;
                        border: 1px solid #8a8886;
                        border-radius: 4px;
                        padding: 8px 16px;
                    }
                    QPushButton:hover {
                        background-color: #edebe9;
                    }
                """)
                
                buttons_layout.addWidget(primary_btn)
                buttons_layout.addWidget(secondary_btn)
                buttons_layout.addWidget(icon_btn)
                buttons_layout.addWidget(toggle_btn)
            
            buttons_layout.addStretch()
            layout.addLayout(buttons_layout)
            
            # Button examples explanation
            examples_label = QLabel("""
<b>Button Types:</b><br>
• <b>Primary:</b> Main action button with accent color<br>
• <b>Secondary:</b> Secondary actions with subtle styling<br>
• <b>Icon:</b> Compact buttons with icon-only content<br>
• <b>Toggle:</b> On/off state buttons for toggles<br><br>

<b>Usage Tips:</b><br>
• Use primary buttons sparingly (1-2 per view)<br>
• Group related buttons together<br>
• Provide clear, action-oriented labels<br>
• Consider button hierarchy and importance
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_text_input_section(self, parent_layout):
            """Create text input components section."""
            group = QGroupBox("Text Input Components")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Form layout for inputs
            form_layout = QFormLayout()
            
            if COMPONENTS_AVAILABLE:
                # Standard text input
                self.text_input = FluentLineEdit()
                self.text_input.setPlaceholderText("Enter text here...")
                self.text_input.textChanged.connect(lambda text: self.show_message(f"Text changed: {text}"))
                
                # Password input
                self.password_input = FluentPasswordBox()
                self.password_input.setPlaceholderText("Enter password...")
                
                # Search box
                self.search_input = FluentSearchBox()
                self.search_input.setPlaceholderText("Search...")
                self.search_input.searchRequested.connect(lambda query: self.show_message(f"Searching: {query}"))
                
                # Multi-line text
                self.text_area = FluentTextEdit()
                self.text_area.setPlaceholderText("Enter multi-line text here...")
                self.text_area.setMaximumHeight(100)
                
                # Auto-suggest box
                self.autosuggest_input = FluentAutoSuggestBox()
                self.autosuggest_input.setPlaceholderText("Type to see suggestions...")
                suggestions = ["Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape"]
                self.autosuggest_input.setSuggestions(suggestions)
                
                form_layout.addRow("Text Input:", self.text_input)
                form_layout.addRow("Password:", self.password_input)
                form_layout.addRow("Search:", self.search_input)
                form_layout.addRow("Multi-line:", self.text_area)
                form_layout.addRow("Auto-suggest:", self.autosuggest_input)
            else:
                # Fallback to standard inputs
                self.text_input = QLineEdit()
                self.text_input.setPlaceholderText("Enter text here...")
                
                self.password_input = QLineEdit()
                self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
                self.password_input.setPlaceholderText("Enter password...")
                
                self.search_input = QLineEdit()
                self.search_input.setPlaceholderText("Search...")
                
                self.text_area = QTextEdit()
                self.text_area.setPlaceholderText("Enter multi-line text here...")
                self.text_area.setMaximumHeight(100)
                
                # Style inputs
                input_style = """
                    QLineEdit, QTextEdit {
                        border: 1px solid #8a8886;
                        border-radius: 4px;
                        padding: 8px;
                        background-color: white;
                    }
                    QLineEdit:focus, QTextEdit:focus {
                        border-color: #0078d4;
                        outline: none;
                    }
                """
                self.text_input.setStyleSheet(input_style)
                self.password_input.setStyleSheet(input_style)
                self.search_input.setStyleSheet(input_style)
                self.text_area.setStyleSheet(input_style)
                
                form_layout.addRow("Text Input:", self.text_input)
                form_layout.addRow("Password:", self.password_input)
                form_layout.addRow("Search:", self.search_input)
                form_layout.addRow("Multi-line:", self.text_area)
            
            layout.addLayout(form_layout)
            
            # Text input examples
            examples_label = QLabel("""
<b>Text Input Types:</b><br>
• <b>LineEdit:</b> Single-line text input with validation<br>
• <b>PasswordBox:</b> Secure password input with reveal option<br>
• <b>SearchBox:</b> Search input with search icon and clear button<br>
• <b>TextEdit:</b> Multi-line text input with rich text support<br>
• <b>AutoSuggestBox:</b> Input with intelligent suggestions<br><br>

<b>Features:</b><br>
• Placeholder text and validation<br>
• Custom styling and themes<br>
• Keyboard shortcuts and accessibility<br>
• Real-time input feedback
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_selection_section(self, parent_layout):
            """Create selection components section."""
            group = QGroupBox("Selection Components")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Selection controls layout
            selection_layout = QGridLayout()
            
            # Checkboxes
            checkbox_group = QGroupBox("Checkboxes")
            checkbox_layout = QVBoxLayout(checkbox_group)
            
            if COMPONENTS_AVAILABLE:
                self.checkbox1 = FluentCheckBox("Enable notifications")
                self.checkbox2 = FluentCheckBox("Auto-save")
                self.checkbox3 = FluentCheckBox("Remember me")
                
                self.checkbox1.toggled.connect(lambda checked: self.show_message(f"Notifications: {'On' if checked else 'Off'}"))
            else:
                self.checkbox1 = QCheckBox("Enable notifications")
                self.checkbox2 = QCheckBox("Auto-save")
                self.checkbox3 = QCheckBox("Remember me")
                
                # Style checkboxes
                checkbox_style = """
                    QCheckBox {
                        spacing: 8px;
                    }
                    QCheckBox::indicator {
                        width: 16px;
                        height: 16px;
                        border: 1px solid #8a8886;
                        border-radius: 2px;
                        background-color: white;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #0078d4;
                        border-color: #0078d4;
                    }
                """
                for cb in [self.checkbox1, self.checkbox2, self.checkbox3]:
                    cb.setStyleSheet(checkbox_style)
            
            checkbox_layout.addWidget(self.checkbox1)
            checkbox_layout.addWidget(self.checkbox2)
            checkbox_layout.addWidget(self.checkbox3)
            
            # Radio buttons
            radio_group = QGroupBox("Radio Buttons")
            radio_layout = QVBoxLayout(radio_group)
            
            self.radio_group = QButtonGroup()
            
            if COMPONENTS_AVAILABLE:
                self.radio1 = FluentRadioButton("Option 1")
                self.radio2 = FluentRadioButton("Option 2")
                self.radio3 = FluentRadioButton("Option 3")
            else:
                self.radio1 = QRadioButton("Option 1")
                self.radio2 = QRadioButton("Option 2")
                self.radio3 = QRadioButton("Option 3")
                
                # Style radio buttons
                radio_style = """
                    QRadioButton {
                        spacing: 8px;
                    }
                    QRadioButton::indicator {
                        width: 16px;
                        height: 16px;
                        border: 1px solid #8a8886;
                        border-radius: 8px;
                        background-color: white;
                    }
                    QRadioButton::indicator:checked {
                        background-color: #0078d4;
                        border-color: #0078d4;
                    }
                """
                for rb in [self.radio1, self.radio2, self.radio3]:
                    rb.setStyleSheet(radio_style)
            
            self.radio_group.addButton(self.radio1)
            self.radio_group.addButton(self.radio2)
            self.radio_group.addButton(self.radio3)
            self.radio1.setChecked(True)
            
            radio_layout.addWidget(self.radio1)
            radio_layout.addWidget(self.radio2)
            radio_layout.addWidget(self.radio3)
            
            # ComboBox
            combo_group = QGroupBox("Dropdown Selection")
            combo_layout = QVBoxLayout(combo_group)
            
            if COMPONENTS_AVAILABLE:
                self.combo_box = FluentComboBox()
            else:
                self.combo_box = QComboBox()
                self.combo_box.setStyleSheet("""
                    QComboBox {
                        border: 1px solid #8a8886;
                        border-radius: 4px;
                        padding: 8px;
                        background-color: white;
                        min-width: 150px;
                    }
                    QComboBox:focus {
                        border-color: #0078d4;
                    }
                """)
            
            self.combo_box.addItems(["Select option...", "Option A", "Option B", "Option C", "Option D"])
            self.combo_box.currentTextChanged.connect(lambda text: self.show_message(f"Selected: {text}"))
            combo_layout.addWidget(self.combo_box)
            
            # Switch/Toggle
            switch_group = QGroupBox("Switches")
            switch_layout = QVBoxLayout(switch_group)
            
            if COMPONENTS_AVAILABLE:
                self.switch1 = FluentSwitch("WiFi")
                self.switch2 = FluentSwitch("Bluetooth")
                self.toggle1 = FluentToggle("Dark Mode")
            else:
                # Use checkboxes as fallback
                self.switch1 = QCheckBox("WiFi")
                self.switch2 = QCheckBox("Bluetooth")
                self.toggle1 = QCheckBox("Dark Mode")
                
                # Style as switches
                switch_style = """
                    QCheckBox {
                        spacing: 8px;
                    }
                    QCheckBox::indicator {
                        width: 40px;
                        height: 20px;
                        border: 1px solid #8a8886;
                        border-radius: 10px;
                        background-color: #e5e5e5;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #0078d4;
                    }
                """
                for sw in [self.switch1, self.switch2, self.toggle1]:
                    sw.setStyleSheet(switch_style)
            
            switch_layout.addWidget(self.switch1)
            switch_layout.addWidget(self.switch2)
            switch_layout.addWidget(self.toggle1)
            
            # Add groups to grid
            selection_layout.addWidget(checkbox_group, 0, 0)
            selection_layout.addWidget(radio_group, 0, 1)
            selection_layout.addWidget(combo_group, 1, 0)
            selection_layout.addWidget(switch_group, 1, 1)
            
            layout.addLayout(selection_layout)
            
            # Selection examples
            examples_label = QLabel("""
<b>Selection Components:</b><br>
• <b>CheckBox:</b> Multiple selection, independent options<br>
• <b>RadioButton:</b> Single selection from group<br>
• <b>ComboBox:</b> Dropdown selection with search<br>
• <b>Switch/Toggle:</b> Binary on/off controls<br><br>

<b>Best Practices:</b><br>
• Use checkboxes for multiple selections<br>
• Use radio buttons for exclusive choices<br>
• Use dropdowns for large option lists<br>
• Use switches for instant on/off actions
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_numeric_section(self, parent_layout):
            """Create numeric input components section."""
            group = QGroupBox("Numeric Input Components")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Numeric controls layout
            numeric_layout = QGridLayout()
            
            # Slider
            slider_group = QGroupBox("Sliders")
            slider_layout = QVBoxLayout(slider_group)
            
            if COMPONENTS_AVAILABLE:
                self.slider = FluentSlider(Qt.Orientation.Horizontal)
                self.slider.setRange(0, 100)
                self.slider.setValue(50)
                self.slider.valueChanged.connect(lambda value: self.show_message(f"Slider: {value}"))
                
                self.vertical_slider = FluentSlider(Qt.Orientation.Vertical)
                self.vertical_slider.setRange(0, 100)
                self.vertical_slider.setValue(25)
                self.vertical_slider.setMaximumHeight(100)
            else:
                self.slider = QSlider(Qt.Orientation.Horizontal)
                self.slider.setRange(0, 100)
                self.slider.setValue(50)
                
                self.vertical_slider = QSlider(Qt.Orientation.Vertical)
                self.vertical_slider.setRange(0, 100)
                self.vertical_slider.setValue(25)
                self.vertical_slider.setMaximumHeight(100)
                
                # Style sliders
                slider_style = """
                    QSlider::groove:horizontal {
                        border: 1px solid #c8c6c4;
                        height: 4px;
                        background: #e5e5e5;
                        border-radius: 2px;
                    }
                    QSlider::handle:horizontal {
                        background: #0078d4;
                        border: 1px solid #005a9e;
                        width: 16px;
                        border-radius: 8px;
                        margin: -6px 0;
                    }
                """
                self.slider.setStyleSheet(slider_style)
                self.vertical_slider.setStyleSheet(slider_style)
            
            # Add value label
            self.slider_value_label = QLabel("Value: 50")
            self.slider.valueChanged.connect(lambda v: self.slider_value_label.setText(f"Value: {v}"))
            
            slider_layout.addWidget(QLabel("Horizontal Slider:"))
            slider_layout.addWidget(self.slider)
            slider_layout.addWidget(self.slider_value_label)
            
            vertical_layout = QHBoxLayout()
            vertical_layout.addWidget(QLabel("Vertical:"))
            vertical_layout.addWidget(self.vertical_slider)
            vertical_layout.addStretch()
            slider_layout.addLayout(vertical_layout)
            
            # SpinBox
            spin_group = QGroupBox("Spin Boxes")
            spin_layout = QFormLayout(spin_group)
            
            if COMPONENTS_AVAILABLE:
                self.spin_box = FluentSpinBox()
                self.spin_box.setRange(0, 1000)
                self.spin_box.setValue(100)
                
                self.number_box = FluentNumberBox()
                self.number_box.setDecimals(2)
                self.number_box.setValue(3.14)
            else:
                self.spin_box = QSpinBox()
                self.spin_box.setRange(0, 1000)
                self.spin_box.setValue(100)
                
                self.number_box = QSpinBox()  # Fallback to int spinbox
                self.number_box.setRange(0, 1000)
                self.number_box.setValue(314)
                
                # Style spinboxes
                spinbox_style = """
                    QSpinBox {
                        border: 1px solid #8a8886;
                        border-radius: 4px;
                        padding: 8px;
                        background-color: white;
                        min-width: 100px;
                    }
                    QSpinBox:focus {
                        border-color: #0078d4;
                    }
                """
                self.spin_box.setStyleSheet(spinbox_style)
                self.number_box.setStyleSheet(spinbox_style)
            
            spin_layout.addRow("Integer:", self.spin_box)
            spin_layout.addRow("Decimal:", self.number_box)
            
            # Add to grid
            numeric_layout.addWidget(slider_group, 0, 0)
            numeric_layout.addWidget(spin_group, 0, 1)
            
            layout.addLayout(numeric_layout)
            
            # Numeric input examples
            examples_label = QLabel("""
<b>Numeric Input Types:</b><br>
• <b>Slider:</b> Visual range selection with immediate feedback<br>
• <b>SpinBox:</b> Precise integer input with increment/decrement<br>
• <b>NumberBox:</b> Decimal number input with validation<br><br>

<b>Usage Guidelines:</b><br>
• Use sliders for approximate values and visual feedback<br>
• Use spinboxes for precise numeric entry<br>
• Set appropriate min/max ranges<br>
• Provide clear units and formatting
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_advanced_section(self, parent_layout):
            """Create advanced form components section."""
            group = QGroupBox("Advanced Form Components")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Status display
            self.status_label = QLabel("Ready - Interact with components to see status updates")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #f3f2f1;
                    border: 1px solid #edebe9;
                    border-radius: 4px;
                    padding: 8px;
                    color: #323130;
                }
            """)
            layout.addWidget(self.status_label)
            
            # Advanced features
            features_label = QLabel("""
<b>Advanced Form Features:</b><br><br>

<b>Validation:</b><br>
• Real-time input validation<br>
• Custom validation rules<br>
• Error state styling<br>
• Accessibility announcements<br><br>

<b>Theming:</b><br>
• Consistent Fluent Design styling<br>
• Light and dark theme support<br>
• Custom color schemes<br>
• High contrast mode<br><br>

<b>Accessibility:</b><br>
• Screen reader support<br>
• Keyboard navigation<br>
• Focus management<br>
• ARIA labels and descriptions<br><br>

<b>Animations:</b><br>
• Smooth transitions<br>
• Focus indicators<br>
• State change animations<br>
• Micro-interactions
""")
            features_label.setWordWrap(True)
            layout.addWidget(features_label)
            
            parent_layout.addWidget(group)
            
        def create_complete_form_example(self, parent_layout):
            """Create a complete form example using all components."""
            group = QGroupBox("Complete Form Example")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Form frame
            form_frame = QFrame()
            form_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #edebe9;
                    border-radius: 8px;
                    padding: 20px;
                }
            """)
            form_layout = QFormLayout(form_frame)
            
            # Form title
            form_title = QLabel("User Registration Form")
            form_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #323130; margin-bottom: 10px;")
            layout.addWidget(form_title)
            
            # Form fields
            self.form_name = QLineEdit()
            self.form_name.setPlaceholderText("Enter your full name")
            
            self.form_email = QLineEdit()
            self.form_email.setPlaceholderText("Enter your email address")
            
            self.form_password = QLineEdit()
            self.form_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.form_password.setPlaceholderText("Create a password")
            
            self.form_age = QSpinBox()
            self.form_age.setRange(13, 120)
            self.form_age.setValue(25)
            
            self.form_country = QComboBox()
            self.form_country.addItems(["Select country...", "United States", "Canada", "United Kingdom", "Germany", "France", "Japan", "Australia"])
            
            self.form_newsletter = QCheckBox("Subscribe to newsletter")
            self.form_terms = QCheckBox("I agree to the terms and conditions")
            
            self.form_experience = QSlider(Qt.Orientation.Horizontal)
            self.form_experience.setRange(0, 10)
            self.form_experience.setValue(5)
            
            # Style form inputs
            input_style = """
                QLineEdit, QSpinBox, QComboBox {
                    border: 1px solid #8a8886;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: white;
                    min-height: 20px;
                }
                QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                    border-color: #0078d4;
                    outline: none;
                }
            """
            for widget in [self.form_name, self.form_email, self.form_password, self.form_age, self.form_country]:
                widget.setStyleSheet(input_style)
            
            # Add fields to form
            form_layout.addRow("Full Name*:", self.form_name)
            form_layout.addRow("Email*:", self.form_email)
            form_layout.addRow("Password*:", self.form_password)
            form_layout.addRow("Age:", self.form_age)
            form_layout.addRow("Country:", self.form_country)
            
            # Experience slider with label
            exp_layout = QHBoxLayout()
            exp_layout.addWidget(self.form_experience)
            self.exp_label = QLabel("5 years")
            self.form_experience.valueChanged.connect(lambda v: self.exp_label.setText(f"{v} years"))
            exp_layout.addWidget(self.exp_label)
            form_layout.addRow("Experience:", exp_layout)
            
            form_layout.addRow("", self.form_newsletter)
            form_layout.addRow("", self.form_terms)
            
            # Form buttons
            button_layout = QHBoxLayout()
            
            submit_btn = QPushButton("Submit Registration")
            submit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 10px 20px;
                    font-weight: 600;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:disabled {
                    background-color: #c8c6c4;
                }
            """)
            submit_btn.clicked.connect(self.submit_form)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f3f2f1;
                    color: #323130;
                    border: 1px solid #8a8886;
                    border-radius: 4px;
                    padding: 10px 20px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #edebe9;
                }
            """)
            cancel_btn.clicked.connect(self.clear_form)
            
            button_layout.addWidget(submit_btn)
            button_layout.addWidget(cancel_btn)
            button_layout.addStretch()
            
            form_layout.addRow("", button_layout)
            
            layout.addWidget(form_frame)
            
            parent_layout.addWidget(group)
            
        def show_message(self, message):
            """Show a status message."""
            if hasattr(self, 'status_label'):
                self.status_label.setText(message)
                # Auto-clear message after 3 seconds
                QTimer.singleShot(3000, lambda: self.status_label.setText("Ready - Interact with components to see status updates"))
            
        def submit_form(self):
            """Handle form submission."""
            # Validate required fields
            if not self.form_name.text().strip():
                self.show_message("Error: Name is required")
                self.form_name.setFocus()
                return
                
            if not self.form_email.text().strip():
                self.show_message("Error: Email is required")
                self.form_email.setFocus()
                return
                
            if not self.form_password.text():
                self.show_message("Error: Password is required")
                self.form_password.setFocus()
                return
                
            if not self.form_terms.isChecked():
                self.show_message("Error: You must agree to the terms and conditions")
                return
            
            # Simulate form submission
            self.show_message("✅ Registration submitted successfully!")
            
        def clear_form(self):
            """Clear all form fields."""
            self.form_name.clear()
            self.form_email.clear()
            self.form_password.clear()
            self.form_age.setValue(25)
            self.form_country.setCurrentIndex(0)
            self.form_newsletter.setChecked(False)
            self.form_terms.setChecked(False)
            self.form_experience.setValue(5)
            self.show_message("Form cleared")
    
    # Create and show demo
    demo = FormsDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
