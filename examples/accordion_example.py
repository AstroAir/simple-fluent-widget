"""
FluentAccordion Component Example
Comprehensive demonstration of all accordion features
"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QTextEdit, QLineEdit, 
                               QPushButton, QCheckBox, QSpinBox, QGroupBox,
                               QScrollArea, QGridLayout, QFormLayout, QSlider,
                               QProgressBar, QComboBox, QTabWidget, QListWidget,
                               QTableWidget, QTableWidgetItem, QSplitter)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon

from components.basic.accordion import FluentAccordion, FluentAccordionItem
from core.theme import theme_manager


class AccordionExampleWindow(QMainWindow):
    """Main example window showcasing all accordion features"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FluentAccordion - Complete Feature Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        central_widget = QWidget()
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - Basic accordion examples
        self._create_basic_examples_panel(main_layout)
        
        # Right panel - Advanced features and controls
        self._create_advanced_panel(main_layout)
        
        # Apply theme
        # theme_manager.apply_theme_to_widget(self)

    def _create_basic_examples_panel(self, parent_layout):
        """Create basic accordion examples panel"""
        left_panel = QWidget()
        left_panel.setMaximumWidth(600)
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title = QLabel("Basic Accordion Examples")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        left_layout.addWidget(title)
        
        # Example 1: Settings Panel
        self._create_settings_accordion(left_layout)
        
        # Example 2: Content Accordion
        self._create_content_accordion(left_layout)
        
        # Example 3: Form Accordion
        self._create_form_accordion(left_layout)
        
        parent_layout.addWidget(left_panel)

    def _create_settings_accordion(self, parent_layout):
        """Create settings accordion example"""
        group = QGroupBox("Settings Panel Accordion")
        layout = QVBoxLayout(group)
        
        # Create accordion
        self.settings_accordion = FluentAccordion()
        self.settings_accordion.setAllowMultipleExpanded(True)
        
        # General Settings
        general_widget = self._create_general_settings_widget()
        self.settings_accordion.addItem("🔧 General Settings", general_widget)
        
        # Display Settings
        display_widget = self._create_display_settings_widget()
        self.settings_accordion.addItem("🖥️ Display Settings", display_widget)
        
        # Audio Settings
        audio_widget = self._create_audio_settings_widget()
        self.settings_accordion.addItem("🔊 Audio Settings", audio_widget)
        
        # Privacy Settings
        privacy_widget = self._create_privacy_settings_widget()
        self.settings_accordion.addItem("🔒 Privacy & Security", privacy_widget)
        
        layout.addWidget(self.settings_accordion)
        parent_layout.addWidget(group)

    def _create_general_settings_widget(self):
        """Create general settings content"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Language selection
        language_combo = QComboBox()
        language_combo.addItems(["English", "中文", "Français", "Deutsch", "日本語"])
        layout.addRow("Language:", language_combo)
        
        # Auto-save
        auto_save_checkbox = QCheckBox("Enable auto-save")
        auto_save_checkbox.setChecked(True)
        layout.addRow(auto_save_checkbox)
        
        # Startup behavior
        startup_combo = QComboBox()
        startup_combo.addItems(["Remember last session", "Start with new document", "Show start page"])
        layout.addRow("Startup behavior:", startup_combo)
        
        # Recent files count
        recent_files_spin = QSpinBox()
        recent_files_spin.setRange(0, 20)
        recent_files_spin.setValue(10)
        layout.addRow("Recent files count:", recent_files_spin)
        
        return widget

    def _create_display_settings_widget(self):
        """Create display settings content"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        theme_combo = QComboBox()
        theme_combo.addItems(["Light", "Dark", "Auto"])
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)
        
        # Zoom level
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("Zoom level:")
        zoom_slider = QSlider(Qt.Orientation.Horizontal)
        zoom_slider.setRange(50, 200)
        zoom_slider.setValue(100)
        zoom_value_label = QLabel("100%")
        zoom_slider.valueChanged.connect(lambda v: zoom_value_label.setText(f"{v}%"))
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(zoom_slider)
        zoom_layout.addWidget(zoom_value_label)
        layout.addLayout(zoom_layout)
        
        # Window settings
        window_group = QGroupBox("Window Settings")
        window_layout = QVBoxLayout(window_group)
        
        maximize_checkbox = QCheckBox("Start maximized")
        remember_size_checkbox = QCheckBox("Remember window size")
        remember_size_checkbox.setChecked(True)
        show_toolbar_checkbox = QCheckBox("Show toolbar")
        show_toolbar_checkbox.setChecked(True)
        
        window_layout.addWidget(maximize_checkbox)
        window_layout.addWidget(remember_size_checkbox)
        window_layout.addWidget(show_toolbar_checkbox)
        
        layout.addWidget(window_group)
        
        return widget

    def _create_audio_settings_widget(self):
        """Create audio settings content"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Master volume
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Master Volume:")
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(80)
        volume_value = QLabel("80%")
        volume_slider.valueChanged.connect(lambda v: volume_value.setText(f"{v}%"))
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(volume_slider)
        volume_layout.addWidget(volume_value)
        layout.addLayout(volume_layout)
        
        # Audio device
        device_layout = QHBoxLayout()
        device_label = QLabel("Output Device:")
        device_combo = QComboBox()
        device_combo.addItems(["Default", "Speakers", "Headphones", "HDMI Audio"])
        device_layout.addWidget(device_label)
        device_layout.addWidget(device_combo)
        device_layout.addStretch()
        layout.addLayout(device_layout)
        
        # Audio effects
        effects_group = QGroupBox("Audio Effects")
        effects_layout = QVBoxLayout(effects_group)
        
        enable_effects = QCheckBox("Enable audio effects")
        bass_boost = QCheckBox("Bass boost")
        surround_sound = QCheckBox("Virtual surround sound")
        noise_reduction = QCheckBox("Noise reduction")
        
        effects_layout.addWidget(enable_effects)
        effects_layout.addWidget(bass_boost)
        effects_layout.addWidget(surround_sound)
        effects_layout.addWidget(noise_reduction)
        
        layout.addWidget(effects_group)
        
        return widget

    def _create_privacy_settings_widget(self):
        """Create privacy settings content"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Data collection
        data_group = QGroupBox("Data Collection")
        data_layout = QVBoxLayout(data_group)
        
        usage_data = QCheckBox("Send usage data to improve the product")
        crash_reports = QCheckBox("Send crash reports automatically")
        anonymous_analytics = QCheckBox("Allow anonymous analytics")
        
        data_layout.addWidget(usage_data)
        data_layout.addWidget(crash_reports)
        data_layout.addWidget(anonymous_analytics)
        
        layout.addWidget(data_group)
        
        # Security
        security_group = QGroupBox("Security")
        security_layout = QVBoxLayout(security_group)
        
        auto_lock = QCheckBox("Auto-lock after inactivity")
        require_password = QCheckBox("Require password for sensitive operations")
        require_password.setChecked(True)
        
        security_layout.addWidget(auto_lock)
        security_layout.addWidget(require_password)
        
        # Clear data button
        clear_btn = QPushButton("Clear All Data")
        clear_btn.setStyleSheet("QPushButton { background-color: #ff4444; color: white; }")
        security_layout.addWidget(clear_btn)
        
        layout.addWidget(security_group)
        
        return widget

    def _create_content_accordion(self, parent_layout):
        """Create content accordion example"""
        group = QGroupBox("Content Accordion (Single Expand)")
        layout = QVBoxLayout(group)
        
        # Create accordion - only one item can be expanded
        self.content_accordion = FluentAccordion()
        self.content_accordion.setAllowMultipleExpanded(False)
        
        # Documentation section
        doc_widget = self._create_documentation_widget()
        self.content_accordion.addItem("📚 Documentation", doc_widget)
        
        # Tutorials section
        tutorial_widget = self._create_tutorials_widget()
        self.content_accordion.addItem("🎓 Tutorials", tutorial_widget)
        
        # Examples section
        examples_widget = self._create_examples_widget()
        self.content_accordion.addItem("💡 Code Examples", examples_widget)
        
        # FAQ section
        faq_widget = self._create_faq_widget()
        self.content_accordion.addItem("❓ Frequently Asked Questions", faq_widget)
        
        layout.addWidget(self.content_accordion)
        parent_layout.addWidget(group)

    def _create_documentation_widget(self):
        """Create documentation content"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Quick links
        links_layout = QGridLayout()
        
        quick_start_btn = QPushButton("Quick Start Guide")
        api_reference_btn = QPushButton("API Reference")
        user_guide_btn = QPushButton("User Guide")
        changelog_btn = QPushButton("Changelog")
        
        links_layout.addWidget(quick_start_btn, 0, 0)
        links_layout.addWidget(api_reference_btn, 0, 1)
        links_layout.addWidget(user_guide_btn, 1, 0)
        links_layout.addWidget(changelog_btn, 1, 1)
        
        layout.addLayout(links_layout)
        
        # Recent updates
        updates_text = QTextEdit()
        updates_text.setMaximumHeight(100)
        updates_text.setPlainText(
            "Recent Documentation Updates:\n"
            "• Added new component examples\n"
            "• Updated API documentation\n"
            "• Fixed typos in user guide\n"
            "• Added troubleshooting section"
        )
        updates_text.setReadOnly(True)
        layout.addWidget(QLabel("Recent Updates:"))
        layout.addWidget(updates_text)
        
        return widget

    def _create_tutorials_widget(self):
        """Create tutorials content"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tutorial list
        tutorial_list = QListWidget()
        tutorials = [
            "Getting Started with Fluent Design",
            "Creating Your First Component",
            "Advanced Animation Techniques",
            "Theme Customization",
            "Building Responsive Layouts",
            "Performance Optimization Tips"
        ]
        
        for tutorial in tutorials:
            tutorial_list.addItem(f"▶️ {tutorial}")
        
        layout.addWidget(QLabel("Available Tutorials:"))
        layout.addWidget(tutorial_list)
        
        # Progress
        progress_label = QLabel("Your Progress:")
        progress_bar = QProgressBar()
        progress_bar.setValue(65)
        progress_bar.setFormat("%p% Complete")
        
        layout.addWidget(progress_label)
        layout.addWidget(progress_bar)
        
        return widget

    def _create_examples_widget(self):
        """Create code examples content"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Example tabs
        tab_widget = QTabWidget()
        
        # Basic example
        basic_code = QTextEdit()
        basic_code.setPlainText("""
# Basic Accordion Usage
accordion = FluentAccordion()

# Add items
accordion.addItem("Settings", settings_widget)
accordion.addItem("About", about_widget)

# Configure behavior
accordion.setAllowMultipleExpanded(True)
accordion.setAnimateTransitions(True)
        """)
        basic_code.setReadOnly(True)
        basic_code.setMaximumHeight(120)
        tab_widget.addTab(basic_code, "Basic")
        
        # Advanced example
        advanced_code = QTextEdit()
        advanced_code.setPlainText("""
# Advanced Features
accordion = FluentAccordion()

# Programmatic control
accordion.setItemExpanded(0, True)
accordion.expandAll()
accordion.collapseAll()

# Event handling
accordion.item_expanded.connect(on_item_expanded)
accordion.item_clicked.connect(on_item_clicked)
        """)
        advanced_code.setReadOnly(True)
        advanced_code.setMaximumHeight(120)
        tab_widget.addTab(advanced_code, "Advanced")
        
        layout.addWidget(tab_widget)
        
        return widget

    def _create_faq_widget(self):
        """Create FAQ content"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # FAQ items
        faq_data = [
            ("How do I change the animation speed?", "Use setAnimationDuration() method or modify the theme settings."),
            ("Can I nest accordions?", "Yes, you can add accordions as content widgets of other accordion items."),
            ("How do I customize the appearance?", "Use the theme manager or apply custom stylesheets."),
            ("Is keyboard navigation supported?", "Yes, use Tab to navigate and Space/Enter to toggle items.")
        ]
        
        faq_table = QTableWidget(len(faq_data), 2)
        faq_table.setHorizontalHeaderLabels(["Question", "Answer"])
        faq_table.horizontalHeader().setStretchLastSection(True)
        
        for i, (question, answer) in enumerate(faq_data):
            faq_table.setItem(i, 0, QTableWidgetItem(question))
            faq_table.setItem(i, 1, QTableWidgetItem(answer))
        
        faq_table.setMaximumHeight(200)
        layout.addWidget(faq_table)
        
        return widget

    def _create_form_accordion(self, parent_layout):
        """Create form accordion example"""
        group = QGroupBox("Dynamic Form Accordion")
        layout = QVBoxLayout(group)
        
        # Create accordion for form sections
        self.form_accordion = FluentAccordion()
        self.form_accordion.setAllowMultipleExpanded(True)
        
        # Personal Information
        personal_widget = self._create_personal_info_widget()
        self.form_accordion.addItem("👤 Personal Information", personal_widget)
        
        # Contact Details
        contact_widget = self._create_contact_widget()
        self.form_accordion.addItem("📞 Contact Details", contact_widget)
        
        # Preferences
        preferences_widget = self._create_preferences_widget()
        self.form_accordion.addItem("⚙️ Preferences", preferences_widget)
        
        layout.addWidget(self.form_accordion)
        
        # Form controls
        controls_layout = QHBoxLayout()
        
        add_section_btn = QPushButton("Add Section")
        add_section_btn.clicked.connect(self._add_dynamic_section)
        
        validate_btn = QPushButton("Validate Form")
        validate_btn.clicked.connect(self._validate_form)
        
        submit_btn = QPushButton("Submit")
        submit_btn.setStyleSheet("QPushButton { background-color: #0078d4; color: white; }")
        
        controls_layout.addWidget(add_section_btn)
        controls_layout.addWidget(validate_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(submit_btn)
        
        layout.addLayout(controls_layout)
        parent_layout.addWidget(group)

    def _create_personal_info_widget(self):
        """Create personal information form"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        first_name = QLineEdit()
        first_name.setPlaceholderText("Enter your first name")
        layout.addRow("First Name:", first_name)
        
        last_name = QLineEdit()
        last_name.setPlaceholderText("Enter your last name")
        layout.addRow("Last Name:", last_name)
        
        birth_date = QLineEdit()
        birth_date.setPlaceholderText("YYYY-MM-DD")
        layout.addRow("Birth Date:", birth_date)
        
        gender_combo = QComboBox()
        gender_combo.addItems(["Prefer not to say", "Male", "Female", "Other"])
        layout.addRow("Gender:", gender_combo)
        
        return widget

    def _create_contact_widget(self):
        """Create contact information form"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        email = QLineEdit()
        email.setPlaceholderText("example@email.com")
        layout.addRow("Email:", email)
        
        phone = QLineEdit()
        phone.setPlaceholderText("+1 (555) 123-4567")
        layout.addRow("Phone:", phone)
        
        address = QTextEdit()
        address.setMaximumHeight(80)
        address.setPlaceholderText("Enter your address")
        layout.addRow("Address:", address)
        
        country_combo = QComboBox()
        country_combo.addItems(["United States", "Canada", "United Kingdom", "Germany", "France", "Japan", "Other"])
        layout.addRow("Country:", country_combo)
        
        return widget

    def _create_preferences_widget(self):
        """Create preferences form"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Notification preferences
        notifications_group = QGroupBox("Notifications")
        notifications_layout = QVBoxLayout(notifications_group)
        
        email_notifications = QCheckBox("Email notifications")
        email_notifications.setChecked(True)
        push_notifications = QCheckBox("Push notifications")
        marketing_emails = QCheckBox("Marketing emails")
        
        notifications_layout.addWidget(email_notifications)
        notifications_layout.addWidget(push_notifications)
        notifications_layout.addWidget(marketing_emails)
        
        layout.addWidget(notifications_group)
        
        # Communication preferences
        communication_group = QGroupBox("Communication")
        communication_layout = QFormLayout(communication_group)
        
        preferred_contact = QComboBox()
        preferred_contact.addItems(["Email", "Phone", "SMS", "Mail"])
        communication_layout.addRow("Preferred Contact:", preferred_contact)
        
        frequency_combo = QComboBox()
        frequency_combo.addItems(["Daily", "Weekly", "Monthly", "Never"])
        communication_layout.addRow("Contact Frequency:", frequency_combo)
        
        layout.addWidget(communication_group)
        
        return widget

    def _create_advanced_panel(self, parent_layout):
        """Create advanced features panel"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Title
        title = QLabel("Advanced Features & Controls")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        right_layout.addWidget(title)
        
        # Control panel
        self._create_control_panel(right_layout)
        
        # Dynamic accordion
        self._create_dynamic_accordion(right_layout)
        
        # Nested accordion example
        self._create_nested_accordion(right_layout)
        
        parent_layout.addWidget(right_panel)

    def _create_control_panel(self, parent_layout):
        """Create accordion control panel"""
        group = QGroupBox("Accordion Controls")
        layout = QVBoxLayout(group)
        
        # Global controls
        global_controls = QHBoxLayout()
        
        expand_all_btn = QPushButton("Expand All")
        expand_all_btn.clicked.connect(lambda: self._expand_all_accordions())
        
        collapse_all_btn = QPushButton("Collapse All")
        collapse_all_btn.clicked.connect(lambda: self._collapse_all_accordions())
        
        toggle_animations_btn = QPushButton("Toggle Animations")
        toggle_animations_btn.clicked.connect(self._toggle_animations)
        
        global_controls.addWidget(expand_all_btn)
        global_controls.addWidget(collapse_all_btn)
        global_controls.addWidget(toggle_animations_btn)
        
        layout.addLayout(global_controls)
        
        # Settings controls
        settings_controls = QGridLayout()
        
        # Multiple expand setting
        multiple_expand_check = QCheckBox("Allow Multiple Expanded")
        multiple_expand_check.setChecked(True)
        multiple_expand_check.toggled.connect(self._toggle_multiple_expand)
        settings_controls.addWidget(multiple_expand_check, 0, 0)
        
        # Animation speed
        speed_label = QLabel("Animation Speed:")
        speed_slider = QSlider(Qt.Orientation.Horizontal)
        speed_slider.setRange(100, 1000)
        speed_slider.setValue(300)
        speed_slider.valueChanged.connect(self._change_animation_speed)
        settings_controls.addWidget(speed_label, 1, 0)
        settings_controls.addWidget(speed_slider, 1, 1)
        
        # Stagger delay
        stagger_label = QLabel("Stagger Delay:")
        stagger_spin = QSpinBox()
        stagger_spin.setRange(0, 200)
        stagger_spin.setValue(50)
        stagger_spin.valueChanged.connect(self._change_stagger_delay)
        settings_controls.addWidget(stagger_label, 2, 0)
        settings_controls.addWidget(stagger_spin, 2, 1)
        
        layout.addLayout(settings_controls)
        
        # Status display
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #0078d4; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        parent_layout.addWidget(group)

    def _create_dynamic_accordion(self, parent_layout):
        """Create dynamic accordion for testing"""
        group = QGroupBox("Dynamic Accordion Test")
        layout = QVBoxLayout(group)
        
        # Create accordion
        self.dynamic_accordion = FluentAccordion()
        
        # Initial items
        for i in range(3):
            content = QLabel(f"Dynamic content {i+1}\nThis content was added dynamically.")
            content.setMinimumHeight(60)
            content.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content.setStyleSheet("background-color: rgba(0, 120, 212, 0.1); border-radius: 4px; padding: 10px;")
            self.dynamic_accordion.addItem(f"Dynamic Item {i+1}", content)
        
        layout.addWidget(self.dynamic_accordion)
        
        # Dynamic controls
        dynamic_controls = QHBoxLayout()
        
        add_item_btn = QPushButton("Add Item")
        add_item_btn.clicked.connect(self._add_dynamic_item)
        
        remove_item_btn = QPushButton("Remove Last")
        remove_item_btn.clicked.connect(self._remove_dynamic_item)
        
        insert_item_btn = QPushButton("Insert at Start")
        insert_item_btn.clicked.connect(self._insert_dynamic_item)
        
        dynamic_controls.addWidget(add_item_btn)
        dynamic_controls.addWidget(remove_item_btn)
        dynamic_controls.addWidget(insert_item_btn)
        
        layout.addLayout(dynamic_controls)
        parent_layout.addWidget(group)

    def _create_nested_accordion(self, parent_layout):
        """Create nested accordion example"""
        group = QGroupBox("Nested Accordion Example")
        layout = QVBoxLayout(group)
        
        # Main accordion
        self.nested_accordion = FluentAccordion()
        self.nested_accordion.setAllowMultipleExpanded(True)
        
        # Create nested content
        for category in ["UI Components", "Data Structures", "Algorithms"]:
            nested_content = self._create_nested_content(category)
            self.nested_accordion.addItem(f"📁 {category}", nested_content)
        
        layout.addWidget(self.nested_accordion)
        parent_layout.addWidget(group)

    def _create_nested_content(self, category):
        """Create nested accordion content"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Description
        description = QLabel(f"This section contains items related to {category.lower()}.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Nested accordion
        nested_accordion = FluentAccordion()
        nested_accordion.setAllowMultipleExpanded(False)
        
        if category == "UI Components":
            items = ["Buttons", "Text Fields", "Sliders", "Progress Bars"]
        elif category == "Data Structures":
            items = ["Arrays", "Lists", "Trees", "Graphs"]
        else:  # Algorithms
            items = ["Sorting", "Searching", "Graph Traversal", "Dynamic Programming"]
        
        for item in items:
            content = QLabel(f"Information about {item.lower()}\n\nThis is a nested accordion item that demonstrates the flexibility of the FluentAccordion component.")
            content.setWordWrap(True)
            content.setMinimumHeight(80)
            content.setStyleSheet("padding: 10px; background-color: rgba(255, 255, 255, 0.05); border-radius: 4px;")
            nested_accordion.addItem(item, content)
        
        layout.addWidget(nested_accordion)
        return widget

    # Event handlers and utility methods
    
    def _expand_all_accordions(self):
        """Expand all accordion items"""
        accordions = [self.settings_accordion, self.content_accordion, 
                     self.form_accordion, self.dynamic_accordion, self.nested_accordion]
        
        for accordion in accordions:
            accordion.expandAll()
        
        self.status_label.setText("Status: All items expanded")
        QTimer.singleShot(3000, lambda: self.status_label.setText("Status: Ready"))

    def _collapse_all_accordions(self):
        """Collapse all accordion items"""
        accordions = [self.settings_accordion, self.content_accordion, 
                     self.form_accordion, self.dynamic_accordion, self.nested_accordion]
        
        for accordion in accordions:
            accordion.collapseAll()
        
        self.status_label.setText("Status: All items collapsed")
        QTimer.singleShot(3000, lambda: self.status_label.setText("Status: Ready"))

    def _toggle_animations(self):
        """Toggle animations for all accordions"""
        accordions = [self.settings_accordion, self.content_accordion, 
                     self.form_accordion, self.dynamic_accordion, self.nested_accordion]
        
        current_state = accordions[0].animateTransitions()
        new_state = not current_state
        
        for accordion in accordions:
            accordion.setAnimateTransitions(new_state)
        
        status = "enabled" if new_state else "disabled"
        self.status_label.setText(f"Status: Animations {status}")
        QTimer.singleShot(3000, lambda: self.status_label.setText("Status: Ready"))

    def _toggle_multiple_expand(self, checked):
        """Toggle multiple expand for settings accordion"""
        self.settings_accordion.setAllowMultipleExpanded(checked)
        status = "allowed" if checked else "restricted"
        self.status_label.setText(f"Status: Multiple expand {status}")
        QTimer.singleShot(3000, lambda: self.status_label.setText("Status: Ready"))

    def _change_animation_speed(self, value):
        """Change animation speed (placeholder - would need accordion method)"""
        self.status_label.setText(f"Status: Animation speed set to {value}ms")
        QTimer.singleShot(2000, lambda: self.status_label.setText("Status: Ready"))

    def _change_stagger_delay(self, value):
        """Change stagger delay"""
        accordions = [self.settings_accordion, self.content_accordion, 
                     self.form_accordion, self.dynamic_accordion, self.nested_accordion]
        
        for accordion in accordions:
            accordion.setStaggerDelay(value)
        
        self.status_label.setText(f"Status: Stagger delay set to {value}ms")
        QTimer.singleShot(2000, lambda: self.status_label.setText("Status: Ready"))

    def _add_dynamic_item(self):
        """Add item to dynamic accordion"""
        count = self.dynamic_accordion.itemCount()
        content = QLabel(f"Dynamic content {count+1}\nAdded at runtime with smooth animation.")
        content.setMinimumHeight(60)
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.setStyleSheet("background-color: rgba(0, 120, 212, 0.1); border-radius: 4px; padding: 10px;")
        
        self.dynamic_accordion.addItem(f"Dynamic Item {count+1}", content)
        self.status_label.setText(f"Status: Added item {count+1}")
        QTimer.singleShot(2000, lambda: self.status_label.setText("Status: Ready"))

    def _remove_dynamic_item(self):
        """Remove last item from dynamic accordion"""
        count = self.dynamic_accordion.itemCount()
        if count > 0:
            self.dynamic_accordion.removeItem(count - 1)
            self.status_label.setText(f"Status: Removed item {count}")
            QTimer.singleShot(2000, lambda: self.status_label.setText("Status: Ready"))

    def _insert_dynamic_item(self):
        """Insert item at start of dynamic accordion"""
        content = QLabel("Inserted content\nThis item was inserted at the beginning.")
        content.setMinimumHeight(60)
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.setStyleSheet("background-color: rgba(255, 165, 0, 0.1); border-radius: 4px; padding: 10px;")
        
        self.dynamic_accordion.insertItem(0, "Inserted Item", content)
        self.status_label.setText("Status: Inserted item at start")
        QTimer.singleShot(2000, lambda: self.status_label.setText("Status: Ready"))

    def _add_dynamic_section(self):
        """Add dynamic section to form accordion"""
        count = self.form_accordion.itemCount()
        
        # Create dynamic form section
        widget = QWidget()
        layout = QFormLayout(widget)
        
        field1 = QLineEdit()
        field1.setPlaceholderText(f"Dynamic field {count+1}")
        layout.addRow(f"Field {count+1}:", field1)
        
        field2 = QComboBox()
        field2.addItems(["Option 1", "Option 2", "Option 3"])
        layout.addRow(f"Selection {count+1}:", field2)
        
        self.form_accordion.addItem(f"🆕 Dynamic Section {count-2}", widget)
        self.status_label.setText(f"Status: Added form section")
        QTimer.singleShot(2000, lambda: self.status_label.setText("Status: Ready"))

    def _validate_form(self):
        """Validate form (placeholder)"""
        self.status_label.setText("Status: Form validation passed ✓")
        QTimer.singleShot(3000, lambda: self.status_label.setText("Status: Ready"))


def main():
    """Run the accordion example"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("FluentAccordion Example")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Fluent Widget Examples")
    
    # Create and show window
    window = AccordionExampleWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()