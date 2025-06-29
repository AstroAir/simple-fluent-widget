"""
Comprehensive Demo of Fluent Design Dialog System

This demo showcases all dialog types and their features:
- Content dialogs with custom content
- Message dialogs for different scenarios
- Input dialogs for data collection
- Progress dialogs for operations
- Form dialogs for complex data entry
- Teaching tips for contextual help
"""

import sys
import time
from typing import Optional

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QWidget, QPushButton, QLabel, QTextEdit, QGroupBox,
                               QScrollArea, QFrame)
from PySide6.QtCore import QTimer, QThread, Signal
from PySide6.QtGui import QFont

# Import all dialog components
from components.dialogs import (
    # Base infrastructure
    FluentBaseDialog, FluentDialogBuilder, DialogSize, DialogType, ButtonRole,
    
    # Specific dialogs
    FluentContentDialog, show_content_dialog,
    FluentMessageDialog, MessageType, show_information_dialog, show_warning_dialog,
    show_error_dialog, show_question_dialog, show_success_dialog,
    FluentInputDialog, InputType, get_text_input, get_password_input,
    get_number_input, get_choice_input, get_file_path, get_folder_path,
    FluentProgressDialog, ProgressMode, ProgressContext, show_progress_dialog,
    FluentFormDialog, FieldType, FieldConfig, create_contact_form, create_settings_form
)


class WorkerThread(QThread):
    """Worker thread for demonstrating progress dialogs."""
    
    progress_updated = Signal(int, str)
    subtask_updated = Signal(int, int, str)
    finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.should_cancel = False
    
    def run(self):
        """Simulate long-running work with progress updates."""
        total_steps = 100
        
        for i in range(total_steps):
            if self.should_cancel:
                break
            
            # Simulate work
            self.msleep(50)
            
            # Update main progress
            progress = int((i + 1) / total_steps * 100)
            detail = f"Processing item {i + 1} of {total_steps}"
            self.progress_updated.emit(progress, detail)
            
            # Simulate subtask progress every 10 steps
            if i % 10 == 0:
                for j in range(10):
                    if self.should_cancel:
                        break
                    self.msleep(20)
                    self.subtask_updated.emit(j + 1, 10, f"Subtask {j + 1}/10")
        
        self.finished.emit()
    
    def cancel(self):
        """Cancel the work."""
        self.should_cancel = True


class FluentDialogDemo(QMainWindow):
    """Main demo window showcasing all dialog types."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Design Dialog System Demo")
        self.setMinimumSize(900, 700)
        
        # Setup UI
        self._setup_ui()
        
        # Demo state
        self.worker_thread: Optional[WorkerThread] = None
        self.current_progress_dialog: Optional[FluentProgressDialog] = None
    
    def _setup_ui(self):
        """Setup the demo UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Fluent Design Dialog System Demo")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #323130; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Explore comprehensive dialog components with consistent Fluent Design styling and behavior.")
        desc.setFont(QFont("Segoe UI", 12))
        desc.setStyleSheet("color: #605e5c; margin-bottom: 20px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Create scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Add demo sections
        content_layout.addWidget(self._create_content_dialog_section())
        content_layout.addWidget(self._create_message_dialog_section())
        content_layout.addWidget(self._create_input_dialog_section())
        content_layout.addWidget(self._create_progress_dialog_section())
        content_layout.addWidget(self._create_form_dialog_section())
        content_layout.addWidget(self._create_advanced_section())
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area, 1)
    
    def _create_section(self, title: str, description: str) -> QGroupBox:
        """Create a demo section with title and description."""
        section = QGroupBox(title)
        section.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e1e1e1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #323130;
            }
        """)
        
        layout = QVBoxLayout(section)
        layout.setSpacing(12)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setStyleSheet("color: #605e5c; margin-bottom: 8px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        return section
    
    def _create_content_dialog_section(self) -> QGroupBox:
        """Create content dialog demo section."""
        section = self._create_section(
            "Content Dialogs",
            "Modal dialogs for displaying custom content with primary and secondary actions."
        )
        
        button_layout = QHBoxLayout()
        
        # Basic content dialog
        basic_btn = QPushButton("Basic Content Dialog")
        basic_btn.clicked.connect(self._show_basic_content_dialog)
        button_layout.addWidget(basic_btn)
        
        # Custom content dialog
        custom_btn = QPushButton("Custom Content Dialog")
        custom_btn.clicked.connect(self._show_custom_content_dialog)
        button_layout.addWidget(custom_btn)
        
        # Builder pattern dialog
        builder_btn = QPushButton("Builder Pattern Dialog")
        builder_btn.clicked.connect(self._show_builder_dialog)
        button_layout.addWidget(builder_btn)
        
        button_layout.addStretch()
        section.layout().addLayout(button_layout)
        
        return section
    
    def _create_message_dialog_section(self) -> QGroupBox:
        """Create message dialog demo section."""
        section = self._create_section(
            "Message Dialogs",
            "Simple dialogs for displaying messages with appropriate icons and button configurations."
        )
        
        button_layout = QHBoxLayout()
        
        # Information
        info_btn = QPushButton("Information")
        info_btn.clicked.connect(lambda: show_information_dialog(
            self, "Information", "This is an informational message."))
        button_layout.addWidget(info_btn)
        
        # Warning
        warning_btn = QPushButton("Warning")
        warning_btn.clicked.connect(lambda: show_warning_dialog(
            self, "Warning", "This is a warning message that requires attention."))
        button_layout.addWidget(warning_btn)
        
        # Error
        error_btn = QPushButton("Error")
        error_btn.clicked.connect(lambda: show_error_dialog(
            self, "Error", "An error has occurred and needs to be addressed."))
        button_layout.addWidget(error_btn)
        
        # Question
        question_btn = QPushButton("Question")
        question_btn.clicked.connect(lambda: show_question_dialog(
            self, "Confirm Action", "Are you sure you want to proceed with this action?"))
        button_layout.addWidget(question_btn)
        
        # Success
        success_btn = QPushButton("Success")
        success_btn.clicked.connect(lambda: show_success_dialog(
            self, "Success", "The operation completed successfully!"))
        button_layout.addWidget(success_btn)
        
        button_layout.addStretch()
        section.layout().addLayout(button_layout)
        
        return section
    
    def _create_input_dialog_section(self) -> QGroupBox:
        """Create input dialog demo section."""
        section = self._create_section(
            "Input Dialogs",
            "Dialogs for collecting various types of user input with validation."
        )
        
        button_layout1 = QHBoxLayout()
        button_layout2 = QHBoxLayout()
        
        # Text input
        text_btn = QPushButton("Text Input")
        text_btn.clicked.connect(self._show_text_input)
        button_layout1.addWidget(text_btn)
        
        # Password input
        password_btn = QPushButton("Password Input")
        password_btn.clicked.connect(self._show_password_input)
        button_layout1.addWidget(password_btn)
        
        # Number input
        number_btn = QPushButton("Number Input")
        number_btn.clicked.connect(self._show_number_input)
        button_layout1.addWidget(number_btn)
        
        # Choice input
        choice_btn = QPushButton("Choice Input")
        choice_btn.clicked.connect(self._show_choice_input)
        button_layout1.addWidget(choice_btn)
        
        button_layout1.addStretch()
        
        # File path
        file_btn = QPushButton("File Path")
        file_btn.clicked.connect(self._show_file_input)
        button_layout2.addWidget(file_btn)
        
        # Folder path
        folder_btn = QPushButton("Folder Path")
        folder_btn.clicked.connect(self._show_folder_input)
        button_layout2.addWidget(folder_btn)
        
        # Custom validation
        validation_btn = QPushButton("Custom Validation")
        validation_btn.clicked.connect(self._show_validation_input)
        button_layout2.addWidget(validation_btn)
        
        button_layout2.addStretch()
        
        section.layout().addLayout(button_layout1)
        section.layout().addLayout(button_layout2)
        
        return section
    
    def _create_progress_dialog_section(self) -> QGroupBox:
        """Create progress dialog demo section."""
        section = self._create_section(
            "Progress Dialogs",
            "Dialogs for showing progress of long-running operations with cancellation support."
        )
        
        button_layout = QHBoxLayout()
        
        # Determinate progress
        determinate_btn = QPushButton("Determinate Progress")
        determinate_btn.clicked.connect(self._show_determinate_progress)
        button_layout.addWidget(determinate_btn)
        
        # Indeterminate progress
        indeterminate_btn = QPushButton("Indeterminate Progress")
        indeterminate_btn.clicked.connect(self._show_indeterminate_progress)
        button_layout.addWidget(indeterminate_btn)
        
        # Subtask progress
        subtask_btn = QPushButton("Subtask Progress")
        subtask_btn.clicked.connect(self._show_subtask_progress)
        button_layout.addWidget(subtask_btn)
        
        # Context manager
        context_btn = QPushButton("Context Manager")
        context_btn.clicked.connect(self._show_context_progress)
        button_layout.addWidget(context_btn)
        
        button_layout.addStretch()
        section.layout().addLayout(button_layout)
        
        return section
    
    def _create_form_dialog_section(self) -> QGroupBox:
        """Create form dialog demo section."""
        section = self._create_section(
            "Form Dialogs",
            "Complex forms with multiple fields, validation, and dependencies."
        )
        
        button_layout = QHBoxLayout()
        
        # Contact form
        contact_btn = QPushButton("Contact Form")
        contact_btn.clicked.connect(self._show_contact_form)
        button_layout.addWidget(contact_btn)
        
        # Settings form
        settings_btn = QPushButton("Settings Form")
        settings_btn.clicked.connect(self._show_settings_form)
        button_layout.addWidget(settings_btn)
        
        # Custom form
        custom_form_btn = QPushButton("Custom Form")
        custom_form_btn.clicked.connect(self._show_custom_form)
        button_layout.addWidget(custom_form_btn)
        
        button_layout.addStretch()
        section.layout().addLayout(button_layout)
        
        return section
    
    def _create_advanced_section(self) -> QGroupBox:
        """Create advanced features demo section.""" 
        section = self._create_section(
            "Advanced Features",
            "Advanced dialog features including theming, animations, and custom dialogs."
        )
        
        button_layout = QHBoxLayout()
        
        # Theme demo
        theme_btn = QPushButton("Theme Integration")
        theme_btn.clicked.connect(self._show_theme_demo)
        button_layout.addWidget(theme_btn)
        
        # Animation demo
        animation_btn = QPushButton("Animation Demo")
        animation_btn.clicked.connect(self._show_animation_demo)
        button_layout.addWidget(animation_btn)
        
        # Custom dialog
        custom_btn = QPushButton("Custom Dialog")
        custom_btn.clicked.connect(self._show_custom_dialog)
        button_layout.addWidget(custom_btn)
        
        button_layout.addStretch()
        section.layout().addLayout(button_layout)
        
        return section
    
    # Content Dialog Demos
    def _show_basic_content_dialog(self):
        """Show basic content dialog."""
        show_content_dialog(
            self,
            title="Basic Content Dialog",
            content="This is a basic content dialog with default styling and buttons.",
            primary_text="Accept",
            secondary_text="Cancel"
        )
    
    def _show_custom_content_dialog(self):
        """Show custom content dialog."""
        dialog = FluentContentDialog(self, "Custom Content", "")
        
        # Add custom content
        custom_widget = QTextEdit()
        custom_widget.setPlainText("This dialog contains custom content widgets.\n\nYou can add any Qt widgets to create rich dialog experiences.")
        custom_widget.setMaximumHeight(100)
        dialog.add_content_widget(custom_widget)
        
        dialog.set_primary_button_text("Save")
        dialog.set_secondary_button_text("Discard")
        dialog.show_animated()
    
    def _show_builder_dialog(self):
        """Show dialog created with builder pattern."""
        content_label = QLabel("This dialog was created using the FluentDialogBuilder pattern for more flexible construction.")
        content_label.setWordWrap(True)
        
        dialog = (FluentDialogBuilder()
                 .title("Builder Pattern Dialog")
                 .modal()
                 .size(DialogSize.MEDIUM)
                 .add_content(content_label)
                 .add_button("Custom Action", ButtonRole.PRIMARY)
                 .add_button("Cancel", ButtonRole.CANCEL)
                 .build(self))
        
        dialog.show_animated()
    
    # Input Dialog Demos
    def _show_text_input(self):
        """Show text input dialog."""
        text, ok = get_text_input(
            self, "Enter Text", "Please enter your name:",
            default="John Doe", placeholder="Enter full name"
        )
        if ok:
            show_information_dialog(self, "Input Received", f"You entered: {text}")
    
    def _show_password_input(self):
        """Show password input dialog."""
        password, ok = get_password_input(
            self, "Enter Password", "Please enter your password:",
            validator=lambda p: len(p) >= 6 or "Password must be at least 6 characters"
        )
        if ok:
            show_success_dialog(self, "Password Set", "Password has been set successfully!")
    
    def _show_number_input(self):
        """Show number input dialog."""
        number, ok = get_number_input(
            self, "Enter Number", "Enter a number between 1 and 100:",
            default=50, min_value=1, max_value=100
        )
        if ok:
            show_information_dialog(self, "Number Received", f"You entered: {number}")
    
    def _show_choice_input(self):
        """Show choice input dialog."""
        choice, ok = get_choice_input(
            self, "Select Option", "Choose your favorite color:",
            items=["Red", "Green", "Blue", "Yellow", "Purple"],
            default="Blue"
        )
        if ok:
            show_information_dialog(self, "Choice Made", f"You selected: {choice}")
    
    def _show_file_input(self):
        """Show file input dialog."""
        file_path, ok = get_file_path(
            self, "Select File", "Choose a file:",
            file_filter="Text Files (*.txt);;All Files (*)"
        )
        if ok:
            show_information_dialog(self, "File Selected", f"Selected file: {file_path}")
    
    def _show_folder_input(self):
        """Show folder input dialog."""
        folder_path, ok = get_folder_path(
            self, "Select Folder", "Choose a folder:"
        )
        if ok:
            show_information_dialog(self, "Folder Selected", f"Selected folder: {folder_path}")
    
    def _show_validation_input(self):
        """Show input with custom validation."""
        def email_validator(email: str) -> str:
            import re
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return "Please enter a valid email address"
            return True
        
        email, ok = get_text_input(
            self, "Email Validation", "Enter your email address:",
            placeholder="user@example.com", validator=email_validator
        )
        if ok:
            show_success_dialog(self, "Valid Email", f"Email {email} is valid!")
    
    # Progress Dialog Demos
    def _show_determinate_progress(self):
        """Show determinate progress dialog."""
        progress_dialog = show_progress_dialog(
            self, "Processing", "Processing files...", cancelable=True
        )
        progress_dialog.start_timing()
        
        # Simulate progress
        self._simulate_progress(progress_dialog)
    
    def _show_indeterminate_progress(self):
        """Show indeterminate progress dialog."""
        progress_dialog = show_progress_dialog(
            self, "Loading", "Loading data...", cancelable=True, indeterminate=True
        )
        
        # Auto-close after 3 seconds
        QTimer.singleShot(3000, progress_dialog.accept)
    
    def _show_subtask_progress(self):
        """Show progress with subtasks."""
        self.current_progress_dialog = FluentProgressDialog(
            self, "Complex Operation", "Processing multiple tasks...", True
        )
        self.current_progress_dialog.set_progress_mode(ProgressMode.SUBTASK)
        self.current_progress_dialog.start_timing()
        
        # Start worker thread
        self.worker_thread = WorkerThread()
        self.worker_thread.progress_updated.connect(
            lambda progress, detail: self.current_progress_dialog.set_progress(progress, detail)
        )
        self.worker_thread.subtask_updated.connect(
            lambda value, max_val, text: self.current_progress_dialog.set_subtask_progress(value, max_val, text)
        )
        self.worker_thread.finished.connect(
            lambda: self.current_progress_dialog.accept()
        )
        self.current_progress_dialog.cancelled.connect(
            lambda: self.worker_thread.cancel()
        )
        
        self.current_progress_dialog.show_animated()
        self.worker_thread.start()
    
    def _show_context_progress(self):
        """Show progress using context manager."""
        def simulate_work():
            with ProgressContext(self, "Context Manager", "Using context manager for progress...") as progress:
                for i in range(50):
                    if progress.is_cancelled():
                        break
                    time.sleep(0.05)
                    progress.set_progress(int(i / 49 * 100), f"Step {i + 1} of 50")
        
        # Run in timer to avoid blocking UI
        QTimer.singleShot(100, simulate_work)
    
    def _simulate_progress(self, dialog: FluentProgressDialog):
        """Simulate progress updates."""
        progress = 0
        
        def update_progress():
            nonlocal progress
            progress += 5
            dialog.set_progress(progress, f"Processing item {progress // 5} of 20")
            
            if progress < 100 and not dialog.is_cancelled():
                QTimer.singleShot(200, update_progress)
            elif progress >= 100:
                dialog.accept()
        
        update_progress()
    
    # Form Dialog Demos
    def _show_contact_form(self):
        """Show contact form dialog."""
        form = create_contact_form(self)
        form.form_submitted.connect(
            lambda data: show_information_dialog(
                self, "Form Submitted", f"Contact information saved:\n{self._format_form_data(data)}"
            )
        )
        form.show_animated()
    
    def _show_settings_form(self):
        """Show settings form dialog."""
        form = create_settings_form(self)
        form.form_submitted.connect(
            lambda data: show_success_dialog(
                self, "Settings Saved", f"Settings have been updated:\n{self._format_form_data(data)}"
            )
        )
        form.show_animated()
    
    def _show_custom_form(self):
        """Show custom form with dependencies."""
        form = FluentFormDialog(self, "Registration Form")
        
        # User section
        form.add_field(FieldConfig("user", "User Information", FieldType.SECTION))
        form.add_field(FieldConfig("username", "Username", FieldType.TEXT, required=True))
        form.add_field(FieldConfig("email", "Email", FieldType.EMAIL, required=True))
        form.add_field(FieldConfig("subscribe", "Subscribe to newsletter", FieldType.CHECKBOX, default_value=True))
        
        # Conditional preferences (only shown if subscribed)
        form.add_field(FieldConfig("prefs", "Preferences", FieldType.SECTION, depends_on="subscribe", depends_value=True))
        form.add_field(FieldConfig("frequency", "Email Frequency", FieldType.COMBOBOX, 
                                 items=["Daily", "Weekly", "Monthly"], default_value="Weekly",
                                 depends_on="subscribe", depends_value=True))
        
        form.form_submitted.connect(
            lambda data: show_success_dialog(
                self, "Registration Complete", f"User registered:\n{self._format_form_data(data)}"
            )
        )
        form.show_animated()
    
    def _format_form_data(self, data: dict) -> str:
        """Format form data for display."""
        formatted = []
        for key, value in data.items():
            formatted.append(f"• {key}: {value}")
        return "\n".join(formatted)
    
    # Advanced Demos
    def _show_theme_demo(self):
        """Show theme integration demo."""
        show_information_dialog(
            self, "Theme Integration",
            "All dialogs automatically inherit the current application theme. "
            "Colors, fonts, and styling adapt to light/dark themes and custom themes."
        )
    
    def _show_animation_demo(self):
        """Show animation demo."""
        dialog = FluentContentDialog(self, "Animation Demo", 
                                   "Notice the smooth fade-in animation when this dialog appears, "
                                   "and the fade-out animation when it closes.")
        dialog.show_animated()
    
    def _show_custom_dialog(self):
        """Show custom dialog extending base."""
        # This would show how to create custom dialogs by extending FluentBaseDialog
        show_information_dialog(
            self, "Custom Dialogs",
            "You can create custom dialogs by extending FluentBaseDialog. "
            "This provides consistent styling, animations, and behavior while "
            "allowing complete customization of content and functionality."
        )


def main():
    """Run the dialog demo application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent Dialog Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Fluent Design")
    
    # Create and show demo window
    demo = FluentDialogDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
