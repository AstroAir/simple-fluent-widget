"""
Advanced Forms Demo

Demonstrates the advanced form components including:
- FluentFormField with validation
- FluentForm with submission handling
- FluentMultiStepForm wizard
"""

import sys
import os
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea
from PySide6.QtCore import Qt

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.data.forms import FluentFormField, FluentForm, FluentMultiStepForm
from components.basic.card import FluentCard
from components.basic.button import FluentPushButton
from components.basic.label import FluentLabel
from theme.theme_manager import theme_manager


class AdvancedFormsDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Forms Demo - Fluent UI")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply theme
        theme_manager.apply_theme(self)
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = FluentLabel("Advanced Forms Demo")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Create demo sections
        self.create_form_field_demo(layout)
        self.create_complete_form_demo(layout)
        self.create_multi_step_form_demo(layout)
        
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(scroll)
        
    def create_form_field_demo(self, parent_layout):
        """Create individual form field demo"""
        card = FluentCard()
        card_layout = QVBoxLayout(card)
        
        # Card title
        card_title = FluentLabel("Individual Form Fields")
        card_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        card_layout.addWidget(card_title)
        
        # Create various form fields
        fields_layout = QVBoxLayout()
        
        # Email field
        self.email_field = FluentFormField(
            field_type="email",
            label="Email Address",
            placeholder="Enter your email address",
            required=True
        )
        fields_layout.addWidget(self.email_field)
        
        # Password field
        self.password_field = FluentFormField(
            field_type="password",
            label="Password",
            placeholder="Enter a strong password",
            required=True
        )
        # Add custom validation rule
        self.password_field.add_validation_rule(
            lambda x: len(x) >= 8,
            "Password must be at least 8 characters long"
        )
        fields_layout.addWidget(self.password_field)
        
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
        fields_layout.addWidget(self.age_field)
        
        # Date field
        self.birth_date_field = FluentFormField(
            field_type="date",
            label="Birth Date",
            required=True
        )
        fields_layout.addWidget(self.birth_date_field)
        
        card_layout.addLayout(fields_layout)
        
        # Validate button
        validate_btn = FluentPushButton("Validate All Fields")
        validate_btn.clicked.connect(self.validate_individual_fields)
        card_layout.addWidget(validate_btn)
        
        parent_layout.addWidget(card)
        
    def create_complete_form_demo(self, parent_layout):
        """Create complete form demo"""
        card = FluentCard()
        card_layout = QVBoxLayout(card)
        
        # Card title
        card_title = FluentLabel("Complete Form Example")
        card_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        card_layout.addWidget(card_title)
        
        # Create form
        self.complete_form = FluentForm("User Registration")
        
        # Add form fields
        self.complete_form.add_field("text", "first_name", "First Name", required=True)
        self.complete_form.add_field("text", "last_name", "Last Name", required=True)
        self.complete_form.add_field("email", "email", "Email Address", required=True)
        self.complete_form.add_field("password", "password", "Password", required=True)
        self.complete_form.add_field("password", "confirm_password", "Confirm Password", required=True)
        self.complete_form.add_field("date", "birth_date", "Birth Date", required=True)
        self.complete_form.add_field("text", "phone", "Phone Number")
        
        # Add custom validation for password confirmation
        def validate_password_match(form_data):
            if form_data.get("password") != form_data.get("confirm_password"):
                return False, "Passwords do not match"
            return True, ""
        
        self.complete_form.add_form_validation(validate_password_match)
        
        # Connect form submission
        self.complete_form.form_submitted.connect(self.handle_form_submission)
        
        card_layout.addWidget(self.complete_form)
        parent_layout.addWidget(card)
        
    def create_multi_step_form_demo(self, parent_layout):
        """Create multi-step form demo"""
        card = FluentCard()
        card_layout = QVBoxLayout(card)
        
        # Card title
        card_title = FluentLabel("Multi-Step Form Wizard")
        card_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        card_layout.addWidget(card_title)
        
        # Create multi-step form
        self.multi_step_form = FluentMultiStepForm("Account Setup Wizard")
        
        # Step 1: Personal Information
        self.multi_step_form.add_step("Personal Information")
        self.multi_step_form.add_field_to_step(0, "text", "first_name", "First Name", required=True)
        self.multi_step_form.add_field_to_step(0, "text", "last_name", "Last Name", required=True)
        self.multi_step_form.add_field_to_step(0, "date", "birth_date", "Birth Date", required=True)
        
        # Step 2: Contact Information
        self.multi_step_form.add_step("Contact Information")
        self.multi_step_form.add_field_to_step(1, "email", "email", "Email Address", required=True)
        self.multi_step_form.add_field_to_step(1, "text", "phone", "Phone Number", required=True)
        self.multi_step_form.add_field_to_step(1, "text", "address", "Address")
        
        # Step 3: Security
        self.multi_step_form.add_step("Security")
        self.multi_step_form.add_field_to_step(2, "password", "password", "Password", required=True)
        self.multi_step_form.add_field_to_step(2, "password", "confirm_password", "Confirm Password", required=True)
        
        # Step 4: Preferences
        self.multi_step_form.add_step("Preferences")
        self.multi_step_form.add_field_to_step(3, "text", "company", "Company")
        self.multi_step_form.add_field_to_step(3, "text", "job_title", "Job Title")
        
        # Connect wizard completion
        self.multi_step_form.wizard_completed.connect(self.handle_wizard_completion)
        
        card_layout.addWidget(self.multi_step_form)
        parent_layout.addWidget(card)
        
    def validate_individual_fields(self):
        """Validate individual form fields"""
        fields = [self.email_field, self.password_field, self.age_field, self.birth_date_field]
        
        all_valid = True
        for field in fields:
            if not field.validate():
                all_valid = False
                
        if all_valid:
            print("✓ All individual fields are valid!")
        else:
            print("✗ Some fields contain errors")
            
    def handle_form_submission(self, form_data):
        """Handle complete form submission"""
        print("Form submitted successfully!")
        print("Form data:", form_data)
        
    def handle_wizard_completion(self, wizard_data):
        """Handle wizard completion"""
        print("Wizard completed successfully!")
        print("Wizard data:", wizard_data)


def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Advanced Forms Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Fluent UI")
    
    # Create and show demo window
    demo = AdvancedFormsDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
