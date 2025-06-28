#!/usr/bin/env python3
"""
Fluent Textbox Component Demo

This example demonstrates the usage of FluentTextbox components with various configurations,
including line edits, text areas, password fields, search boxes, and validation features.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox, QFormLayout
from PySide6.QtCore import Qt

from components.basic.forms.textbox import FluentLineEdit, FluentTextEdit, FluentPasswordEdit, FluentSearchBox
from core.theme import theme_manager


class TextboxDemo(QMainWindow):
    """Main demo window showcasing Fluent textbox components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Textbox Demo")
        self.setGeometry(200, 200, 900, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add title
        title = QLabel("Fluent Textbox Components Demo")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Create demo sections
        self.create_line_edits(main_layout)
        self.create_text_areas(main_layout)
        self.create_password_fields(main_layout)
        self.create_search_boxes(main_layout)
        
        main_layout.addStretch()
        
    def create_line_edits(self, parent_layout):
        """Create line edit examples."""
        group = QGroupBox("Line Edit Components")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QFormLayout(group)
        
        # Basic line edit
        basic_edit = FluentLineEdit()
        basic_edit.setPlaceholderText("Enter your name...")
        layout.addRow("Basic Line Edit:", basic_edit)
        
        # Line edit with validation
        email_edit = FluentLineEdit()
        email_edit.setPlaceholderText("Enter your email address...")
        
        # Add email validation (simple pattern)
        def validate_email():
            text = email_edit.text()
            if "@" in text and "." in text:
                email_edit.setStyleSheet("border: 2px solid #107C10;")  # Green border
            elif text:
                email_edit.setStyleSheet("border: 2px solid #D83B01;")  # Red border
            else:
                email_edit.setStyleSheet("")  # Reset
        
        email_edit.textChanged.connect(validate_email)
        layout.addRow("Email (with validation):", email_edit)
        
        # Disabled line edit
        disabled_edit = FluentLineEdit()
        disabled_edit.setText("This field is disabled")
        disabled_edit.setEnabled(False)
        layout.addRow("Disabled Line Edit:", disabled_edit)
        
        # Read-only line edit
        readonly_edit = FluentLineEdit()
        readonly_edit.setText("This field is read-only")
        readonly_edit.setReadOnly(True)
        layout.addRow("Read-only Line Edit:", readonly_edit)
        
        # Line edit with character limit
        limited_edit = FluentLineEdit()
        limited_edit.setPlaceholderText("Max 20 characters...")
        limited_edit.setMaxLength(20)
        
        char_count_label = QLabel("0/20")
        limited_edit.textChanged.connect(
            lambda text: char_count_label.setText(f"{len(text)}/20")
        )
        
        limited_layout = QHBoxLayout()
        limited_layout.addWidget(limited_edit)
        limited_layout.addWidget(char_count_label)
        limited_widget = QWidget()
        limited_widget.setLayout(limited_layout)
        
        layout.addRow("Limited Length (20):", limited_widget)
        
        parent_layout.addWidget(group)
        
    def create_text_areas(self, parent_layout):
        """Create text area examples."""
        group = QGroupBox("Text Area Components")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Basic text area
        basic_text = FluentTextEdit()
        basic_text.setPlaceholderText("Enter your message here...")
        basic_text.setMaximumHeight(100)
        
        layout.addWidget(QLabel("Basic Text Area:"))
        layout.addWidget(basic_text)
        layout.addSpacing(10)
        
        # Text area with word count
        counted_text = FluentTextEdit()
        counted_text.setPlaceholderText("Type something and see the word count...")
        counted_text.setMaximumHeight(100)
        
        word_count_label = QLabel("Words: 0 | Characters: 0")
        
        def update_counts():
            text = counted_text.toPlainText()
            words = len(text.split()) if text.strip() else 0
            chars = len(text)
            word_count_label.setText(f"Words: {words} | Characters: {chars}")
        
        counted_text.textChanged.connect(update_counts)
        
        layout.addWidget(QLabel("Text Area with Word Count:"))
        layout.addWidget(counted_text)
        layout.addWidget(word_count_label)
        layout.addSpacing(10)
        
        # Code editor style text area
        code_text = FluentTextEdit()
        code_text.setPlaceholderText("// Enter your code here...")
        code_text.setMaximumHeight(120)
        code_text.setStyleSheet("""
            FluentTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
            }
        """)
        
        layout.addWidget(QLabel("Code Editor Style:"))
        layout.addWidget(code_text)
        
        parent_layout.addWidget(group)
        
    def create_password_fields(self, parent_layout):
        """Create password field examples."""
        group = QGroupBox("Password Components")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QFormLayout(group)
        
        # Basic password field
        password_edit = FluentPasswordEdit()
        password_edit.setPlaceholderText("Enter your password...")
        layout.addRow("Password:", password_edit)
        
        # Password with strength indicator
        strong_password_edit = FluentPasswordEdit()
        strong_password_edit.setPlaceholderText("Enter a strong password...")
        
        strength_label = QLabel("Password strength: None")
        
        def check_password_strength():
            password = strong_password_edit.text()
            if len(password) == 0:
                strength = "None"
                color = "#666666"
            elif len(password) < 6:
                strength = "Weak"
                color = "#D83B01"
            elif len(password) < 10:
                strength = "Medium"
                color = "#FF8C00"
            else:
                # Check for uppercase, lowercase, numbers, and special chars
                has_upper = any(c.isupper() for c in password)
                has_lower = any(c.islower() for c in password)
                has_digit = any(c.isdigit() for c in password)
                has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
                
                score = sum([has_upper, has_lower, has_digit, has_special])
                if score >= 3:
                    strength = "Strong"
                    color = "#107C10"
                else:
                    strength = "Medium"
                    color = "#FF8C00"
            
            strength_label.setText(f"Password strength: {strength}")
            strength_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        strong_password_edit.textChanged.connect(check_password_strength)
        
        password_layout = QVBoxLayout()
        password_layout.addWidget(strong_password_edit)
        password_layout.addWidget(strength_label)
        password_widget = QWidget()
        password_widget.setLayout(password_layout)
        
        layout.addRow("Password with Strength:", password_widget)
        
        # Confirm password field
        confirm_password_edit = FluentPasswordEdit()
        confirm_password_edit.setPlaceholderText("Confirm your password...")
        
        match_label = QLabel("")
        
        def check_password_match():
            if not strong_password_edit.text() or not confirm_password_edit.text():
                match_label.setText("")
                return
                
            if strong_password_edit.text() == confirm_password_edit.text():
                match_label.setText("✓ Passwords match")
                match_label.setStyleSheet("color: #107C10; font-weight: bold;")
            else:
                match_label.setText("✗ Passwords don't match")
                match_label.setStyleSheet("color: #D83B01; font-weight: bold;")
        
        strong_password_edit.textChanged.connect(check_password_match)
        confirm_password_edit.textChanged.connect(check_password_match)
        
        confirm_layout = QVBoxLayout()
        confirm_layout.addWidget(confirm_password_edit)
        confirm_layout.addWidget(match_label)
        confirm_widget = QWidget()
        confirm_widget.setLayout(confirm_layout)
        
        layout.addRow("Confirm Password:", confirm_widget)
        
        parent_layout.addWidget(group)
        
    def create_search_boxes(self, parent_layout):
        """Create search box examples."""
        group = QGroupBox("Search Components")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Basic search box
        search_box = FluentSearchBox()
        search_box.setPlaceholderText("Search for anything...")
        
        search_results_label = QLabel("Type to search...")
        
        def handle_search():
            query = search_box.text()
            if query:
                search_results_label.setText(f"Searching for: '{query}'")
            else:
                search_results_label.setText("Type to search...")
        
        search_box.textChanged.connect(handle_search)
        
        layout.addWidget(QLabel("Basic Search Box:"))
        layout.addWidget(search_box)
        layout.addWidget(search_results_label)
        layout.addSpacing(10)
        
        # Search with instant results simulation
        instant_search = FluentSearchBox()
        instant_search.setPlaceholderText("Search users...")
        
        # Simulate some data
        users = ["Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Prince", "Eve Wilson"]
        results_label = QLabel("Start typing to see results...")
        
        def instant_search_handler():
            query = instant_search.text().lower()
            if query:
                matches = [user for user in users if query in user.lower()]
                if matches:
                    results_label.setText("Found: " + ", ".join(matches))
                else:
                    results_label.setText("No matches found")
            else:
                results_label.setText("Start typing to see results...")
        
        instant_search.textChanged.connect(instant_search_handler)
        
        layout.addWidget(QLabel("Instant Search (Users):"))
        layout.addWidget(instant_search)
        layout.addWidget(results_label)
        
        parent_layout.addWidget(group)


def main():
    """Run the textbox demo application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent Textbox Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = TextboxDemo()
    demo.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
