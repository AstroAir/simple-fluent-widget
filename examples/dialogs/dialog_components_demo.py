"""
Comprehensive Dialog Components Demo

This demo showcases all dialog components available in the simple-fluent-widget library,
including content dialogs, message boxes, input dialogs, form dialogs, and teaching tips.

Features demonstrated:
- Content dialogs with custom content
- Message dialogs for notifications
- Input dialogs for user data collection
- Form dialogs for complex input
- Progress dialogs for long operations
- Teaching tips for user guidance
- Modal and non-modal dialog patterns
"""

import sys
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QGroupBox,
    QScrollArea, QFrame, QSpacerItem, QSizePolicy, QMessageBox, QTabWidget,
    QSlider, QSpinBox, QCheckBox, QComboBox, QProgressBar, QDialog,
    QDialogButtonBox, QFormLayout, QDateEdit, QTimeEdit, QColorDialog,
    QFileDialog, QInputDialog, QProgressDialog, QErrorMessage
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QThread, pyqtSignal
from PySide6.QtGui import QColor, QPalette, QFont, QIcon, QPixmap

# Import fluent dialog components with fallbacks
try:
    from components.dialogs.content_dialog import FluentContentDialog
    FLUENT_CONTENT_DIALOG_AVAILABLE = True
except ImportError:
    print("Warning: FluentContentDialog not available")
    FLUENT_CONTENT_DIALOG_AVAILABLE = False

try:
    from components.dialogs.message_dialog import FluentMessageDialog
    FLUENT_MESSAGE_DIALOG_AVAILABLE = True
except ImportError:
    print("Warning: FluentMessageDialog not available")
    FLUENT_MESSAGE_DIALOG_AVAILABLE = False

try:
    from components.dialogs.input_dialog import FluentInputDialog
    FLUENT_INPUT_DIALOG_AVAILABLE = True
except ImportError:
    print("Warning: FluentInputDialog not available")
    FLUENT_INPUT_DIALOG_AVAILABLE = False

try:
    from components.dialogs.form_dialog import FluentFormDialog
    FLUENT_FORM_DIALOG_AVAILABLE = True
except ImportError:
    print("Warning: FluentFormDialog not available")
    FLUENT_FORM_DIALOG_AVAILABLE = False

try:
    from components.dialogs.progress_dialog import FluentProgressDialog
    FLUENT_PROGRESS_DIALOG_AVAILABLE = True
except ImportError:
    print("Warning: FluentProgressDialog not available")
    FLUENT_PROGRESS_DIALOG_AVAILABLE = False

try:
    from components.dialogs.teaching_tip import FluentTeachingTip
    FLUENT_TEACHING_TIP_AVAILABLE = True
except ImportError:
    print("Warning: FluentTeachingTip not available")
    FLUENT_TEACHING_TIP_AVAILABLE = False


class WorkerThread(QThread):
    """Worker thread for demonstrating progress dialogs."""
    
    progress_updated = pyqtSignal(int)
    task_completed = pyqtSignal()
    
    def run(self):
        """Simulate a long-running task."""
        for i in range(101):
            time.sleep(0.05)  # Simulate work
            self.progress_updated.emit(i)
        self.task_completed.emit()


class CustomDialog(QDialog):
    """Custom dialog for demonstration purposes."""
    
    def __init__(self, parent=None, title="Custom Dialog"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 300)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Content area
        content_label = QLabel("This is a custom dialog with Fluent Design styling.")
        content_label.setWordWrap(True)
        layout.addWidget(content_label)
        
        # Input fields
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)
        
        self.email_input = QLineEdit()
        form_layout.addRow("Email:", self.email_input)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Apply Fluent styling
        self.setStyleSheet("""
            QDialog {
                background-color: #faf9f8;
                border: 1px solid #c8c6c4;
                border-radius: 8px;
            }
            QLabel {
                color: #323130;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #c8c6c4;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #0078d4;
            }
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #c8c6c4;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #f3f2f1;
            }
            QPushButton:pressed {
                background-color: #e1dfdd;
            }
        """)
        
    def get_data(self):
        """Get the data entered in the dialog."""
        return {
            'name': self.name_input.text(),
            'email': self.email_input.text(),
            'notes': self.notes_input.toPlainText()
        }


class DialogComponentsDemo(QMainWindow):
    """Main demo window showcasing dialog components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dialog Components Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Dialog result storage
        self.dialog_results = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Dialog Components Demo")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Tab widget for different dialog categories
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create demo tabs
        self.create_content_dialogs_tab()
        self.create_message_dialogs_tab()
        self.create_input_dialogs_tab()
        self.create_form_dialogs_tab()
        self.create_progress_dialogs_tab()
        self.create_teaching_tips_tab()
        self.create_system_dialogs_tab()
        
        # Results display
        self.create_results_display(main_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready - Click buttons to test different dialog types")
        
    def create_content_dialogs_tab(self):
        """Create content dialogs demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Content dialog examples
        content_group = QGroupBox("Content Dialog Examples")
        content_layout = QGridLayout(content_group)
        
        # Simple content dialog
        simple_btn = QPushButton("Simple Content Dialog")
        simple_btn.clicked.connect(self.show_simple_content_dialog)
        content_layout.addWidget(simple_btn, 0, 0)
        
        # Rich content dialog
        rich_btn = QPushButton("Rich Content Dialog")
        rich_btn.clicked.connect(self.show_rich_content_dialog)
        content_layout.addWidget(rich_btn, 0, 1)
        
        # Scrollable content dialog
        scrollable_btn = QPushButton("Scrollable Content Dialog")
        scrollable_btn.clicked.connect(self.show_scrollable_content_dialog)
        content_layout.addWidget(scrollable_btn, 1, 0)
        
        # Custom button dialog
        custom_btn = QPushButton("Custom Button Dialog")
        custom_btn.clicked.connect(self.show_custom_button_dialog)
        content_layout.addWidget(custom_btn, 1, 1)
        
        layout.addWidget(content_group)
        
        # Content dialog configuration
        config_group = QGroupBox("Content Dialog Configuration")
        config_layout = QFormLayout(config_group)
        
        # Dialog size
        self.dialog_width_spin = QSpinBox()
        self.dialog_width_spin.setRange(300, 800)
        self.dialog_width_spin.setValue(400)
        config_layout.addRow("Width:", self.dialog_width_spin)
        
        self.dialog_height_spin = QSpinBox()
        self.dialog_height_spin.setRange(200, 600)
        self.dialog_height_spin.setValue(300)
        config_layout.addRow("Height:", self.dialog_height_spin)
        
        # Modal setting
        self.modal_check = QCheckBox("Modal Dialog")
        self.modal_check.setChecked(True)
        config_layout.addRow("Behavior:", self.modal_check)
        
        # Resizable setting
        self.resizable_check = QCheckBox("Resizable")
        self.resizable_check.setChecked(False)
        config_layout.addRow("", self.resizable_check)
        
        layout.addWidget(config_group)
        
        # Documentation
        docs_group = QGroupBox("Content Dialog Features")
        docs_layout = QVBoxLayout(docs_group)
        
        docs_text = QLabel("""
<b>Content Dialog Capabilities:</b><br>
• <b>Flexible Content:</b> Support for any widget content<br>
• <b>Custom Buttons:</b> Configurable button sets and actions<br>
• <b>Modal/Modeless:</b> Can be modal or non-modal<br>
• <b>Resizable:</b> Optional resize functionality<br>
• <b>Fluent Styling:</b> Consistent with Fluent Design principles<br><br>

<b>Use Cases:</b><br>
• Information display with rich content<br>
• Settings panels and preferences<br>
• Help and documentation viewers<br>
• Custom input forms and wizards<br>
""")
        docs_text.setWordWrap(True)
        docs_layout.addWidget(docs_text)
        
        layout.addWidget(docs_group)
        
        self.tab_widget.addTab(tab_widget, "Content Dialogs")
        
    def create_message_dialogs_tab(self):
        """Create message dialogs demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Message dialog examples
        message_group = QGroupBox("Message Dialog Examples")
        message_layout = QGridLayout(message_group)
        
        # Information dialog
        info_btn = QPushButton("ℹ️ Information")
        info_btn.clicked.connect(self.show_info_dialog)
        message_layout.addWidget(info_btn, 0, 0)
        
        # Warning dialog
        warning_btn = QPushButton("⚠️ Warning")
        warning_btn.clicked.connect(self.show_warning_dialog)
        message_layout.addWidget(warning_btn, 0, 1)
        
        # Error dialog
        error_btn = QPushButton("❌ Error")
        error_btn.clicked.connect(self.show_error_dialog)
        message_layout.addWidget(error_btn, 1, 0)
        
        # Question dialog
        question_btn = QPushButton("❓ Question")
        question_btn.clicked.connect(self.show_question_dialog)
        message_layout.addWidget(question_btn, 1, 1)
        
        # Success dialog
        success_btn = QPushButton("✅ Success")
        success_btn.clicked.connect(self.show_success_dialog)
        message_layout.addWidget(success_btn, 2, 0)
        
        # Custom icon dialog
        custom_icon_btn = QPushButton("🎨 Custom Icon")
        custom_icon_btn.clicked.connect(self.show_custom_icon_dialog)
        message_layout.addWidget(custom_icon_btn, 2, 1)
        
        layout.addWidget(message_group)
        
        # Message content configuration
        content_config_group = QGroupBox("Message Content Configuration")
        content_config_layout = QFormLayout(content_config_group)
        
        # Title
        self.message_title_input = QLineEdit("Dialog Title")
        content_config_layout.addRow("Title:", self.message_title_input)
        
        # Message text
        self.message_text_input = QTextEdit()
        self.message_text_input.setPlainText("This is the message content.")
        self.message_text_input.setMaximumHeight(80)
        content_config_layout.addRow("Message:", self.message_text_input)
        
        # Detailed text
        self.detailed_text_input = QTextEdit()
        self.detailed_text_input.setPlainText("Additional detailed information...")
        self.detailed_text_input.setMaximumHeight(60)
        content_config_layout.addRow("Details:", self.detailed_text_input)
        
        layout.addWidget(content_config_group)
        
        # Documentation
        message_docs_group = QGroupBox("Message Dialog Types")
        message_docs_layout = QVBoxLayout(message_docs_group)
        
        message_docs_text = QLabel("""
<b>Message Dialog Types:</b><br><br>

<b>Information (ℹ️):</b> General information, confirmations<br>
<b>Warning (⚠️):</b> Potential issues, confirmations needed<br>
<b>Error (❌):</b> Error messages, failure notifications<br>
<b>Question (❓):</b> Yes/No questions, user decisions<br>
<b>Success (✅):</b> Success confirmations, completion messages<br><br>

<b>Best Practices:</b><br>
• Use clear, concise messaging<br>
• Choose appropriate icons for context<br>
• Provide actionable button text<br>
• Include details when helpful<br>
• Consider the user's workflow impact<br>
""")
        message_docs_text.setWordWrap(True)
        message_docs_layout.addWidget(message_docs_text)
        
        layout.addWidget(message_docs_group)
        
        self.tab_widget.addTab(tab_widget, "Message Dialogs")
        
    def create_input_dialogs_tab(self):
        """Create input dialogs demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Input dialog examples
        input_group = QGroupBox("Input Dialog Examples")
        input_layout = QGridLayout(input_group)
        
        # Text input
        text_input_btn = QPushButton("📝 Text Input")
        text_input_btn.clicked.connect(self.show_text_input_dialog)
        input_layout.addWidget(text_input_btn, 0, 0)
        
        # Number input
        number_input_btn = QPushButton("🔢 Number Input")
        number_input_btn.clicked.connect(self.show_number_input_dialog)
        input_layout.addWidget(number_input_btn, 0, 1)
        
        # Password input
        password_input_btn = QPushButton("🔒 Password Input")
        password_input_btn.clicked.connect(self.show_password_input_dialog)
        input_layout.addWidget(password_input_btn, 1, 0)
        
        # Multi-line input
        multiline_input_btn = QPushButton("📄 Multi-line Input")
        multiline_input_btn.clicked.connect(self.show_multiline_input_dialog)
        input_layout.addWidget(multiline_input_btn, 1, 1)
        
        # Choice input
        choice_input_btn = QPushButton("📋 Choice Input")
        choice_input_btn.clicked.connect(self.show_choice_input_dialog)
        input_layout.addWidget(choice_input_btn, 2, 0)
        
        # Date input
        date_input_btn = QPushButton("📅 Date Input")
        date_input_btn.clicked.connect(self.show_date_input_dialog)
        input_layout.addWidget(date_input_btn, 2, 1)
        
        layout.addWidget(input_group)
        
        # Input validation
        validation_group = QGroupBox("Input Validation Examples")
        validation_layout = QGridLayout(validation_group)
        
        # Email validation
        email_btn = QPushButton("📧 Email Validation")
        email_btn.clicked.connect(self.show_email_input_dialog)
        validation_layout.addWidget(email_btn, 0, 0)
        
        # URL validation
        url_btn = QPushButton("🌐 URL Validation")
        url_btn.clicked.connect(self.show_url_input_dialog)
        validation_layout.addWidget(url_btn, 0, 1)
        
        # Range validation
        range_btn = QPushButton("📊 Range Validation")
        range_btn.clicked.connect(self.show_range_input_dialog)
        validation_layout.addWidget(range_btn, 1, 0)
        
        # Custom validation
        custom_validation_btn = QPushButton("🔧 Custom Validation")
        custom_validation_btn.clicked.connect(self.show_custom_validation_dialog)
        validation_layout.addWidget(custom_validation_btn, 1, 1)
        
        layout.addWidget(validation_group)
        
        # Documentation
        input_docs_group = QGroupBox("Input Dialog Features")
        input_docs_layout = QVBoxLayout(input_docs_group)
        
        input_docs_text = QLabel("""
<b>Input Dialog Capabilities:</b><br>
• <b>Various Input Types:</b> Text, numbers, passwords, dates<br>
• <b>Validation Support:</b> Real-time and submission validation<br>
• <b>Placeholder Text:</b> Helpful hints for users<br>
• <b>Input Masks:</b> Format enforcement for specific data types<br>
• <b>Multiple Inputs:</b> Support for multiple related inputs<br><br>

<b>Validation Features:</b><br>
• Email format validation<br>
• URL format validation<br>
• Numeric range validation<br>
• Custom regex validation<br>
• Required field validation<br>
""")
        input_docs_text.setWordWrap(True)
        input_docs_layout.addWidget(input_docs_text)
        
        layout.addWidget(input_docs_group)
        
        self.tab_widget.addTab(tab_widget, "Input Dialogs")
        
    def create_form_dialogs_tab(self):
        """Create form dialogs demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Form dialog examples
        form_group = QGroupBox("Form Dialog Examples")
        form_layout = QGridLayout(form_group)
        
        # User registration form
        user_form_btn = QPushButton("👤 User Registration")
        user_form_btn.clicked.connect(self.show_user_registration_dialog)
        form_layout.addWidget(user_form_btn, 0, 0)
        
        # Settings form
        settings_form_btn = QPushButton("⚙️ Settings Form")
        settings_form_btn.clicked.connect(self.show_settings_form_dialog)
        form_layout.addWidget(settings_form_btn, 0, 1)
        
        # Contact form
        contact_form_btn = QPushButton("📞 Contact Form")
        contact_form_btn.clicked.connect(self.show_contact_form_dialog)
        form_layout.addWidget(contact_form_btn, 1, 0)
        
        # Survey form
        survey_form_btn = QPushButton("📊 Survey Form")
        survey_form_btn.clicked.connect(self.show_survey_form_dialog)
        form_layout.addWidget(survey_form_btn, 1, 1)
        
        # Wizard form
        wizard_form_btn = QPushButton("🧙 Wizard Form")
        wizard_form_btn.clicked.connect(self.show_wizard_form_dialog)
        form_layout.addWidget(wizard_form_btn, 2, 0)
        
        # Multi-page form
        multipage_form_btn = QPushButton("📑 Multi-page Form")
        multipage_form_btn.clicked.connect(self.show_multipage_form_dialog)
        form_layout.addWidget(multipage_form_btn, 2, 1)
        
        layout.addWidget(form_group)
        
        # Form features
        features_group = QGroupBox("Form Features")
        features_layout = QVBoxLayout(features_group)
        
        features_text = QLabel("""
<b>Advanced Form Features:</b><br>
• <b>Field Validation:</b> Real-time validation with error messages<br>
• <b>Conditional Fields:</b> Show/hide fields based on other inputs<br>
• <b>Auto-save:</b> Automatic saving of draft data<br>
• <b>Field Dependencies:</b> Fields that depend on other field values<br>
• <b>Form Sections:</b> Organized grouping of related fields<br>
• <b>Progress Indication:</b> Show completion progress<br><br>

<b>Input Types Supported:</b><br>
• Text inputs with validation • Date and time pickers<br>
• Number inputs with ranges • File upload components<br>
• Dropdown selections • Color pickers<br>
• Checkboxes and radio buttons • Rich text editors<br>
""")
        features_text.setWordWrap(True)
        features_layout.addWidget(features_text)
        
        layout.addWidget(features_group)
        
        self.tab_widget.addTab(tab_widget, "Form Dialogs")
        
    def create_progress_dialogs_tab(self):
        """Create progress dialogs demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Progress dialog examples
        progress_group = QGroupBox("Progress Dialog Examples")
        progress_layout = QGridLayout(progress_group)
        
        # Determinate progress
        determinate_btn = QPushButton("📊 Determinate Progress")
        determinate_btn.clicked.connect(self.show_determinate_progress)
        progress_layout.addWidget(determinate_btn, 0, 0)
        
        # Indeterminate progress
        indeterminate_btn = QPushButton("🔄 Indeterminate Progress")
        indeterminate_btn.clicked.connect(self.show_indeterminate_progress)
        progress_layout.addWidget(indeterminate_btn, 0, 1)
        
        # Cancellable progress
        cancellable_btn = QPushButton("❌ Cancellable Progress")
        cancellable_btn.clicked.connect(self.show_cancellable_progress)
        progress_layout.addWidget(cancellable_btn, 1, 0)
        
        # Multi-step progress
        multistep_btn = QPushButton("📈 Multi-step Progress")
        multistep_btn.clicked.connect(self.show_multistep_progress)
        progress_layout.addWidget(multistep_btn, 1, 1)
        
        layout.addWidget(progress_group)
        
        # Progress configuration
        config_group = QGroupBox("Progress Configuration")
        config_layout = QFormLayout(config_group)
        
        # Duration
        self.progress_duration_spin = QSpinBox()
        self.progress_duration_spin.setRange(1, 60)
        self.progress_duration_spin.setValue(5)
        self.progress_duration_spin.setSuffix(" seconds")
        config_layout.addRow("Duration:", self.progress_duration_spin)
        
        # Show percentage
        self.show_percentage_check = QCheckBox("Show Percentage")
        self.show_percentage_check.setChecked(True)
        config_layout.addRow("Display:", self.show_percentage_check)
        
        # Show time remaining
        self.show_time_check = QCheckBox("Show Time Remaining")
        self.show_time_check.setChecked(False)
        config_layout.addRow("", self.show_time_check)
        
        layout.addWidget(config_group)
        
        # Documentation
        progress_docs_group = QGroupBox("Progress Dialog Types")
        progress_docs_layout = QVBoxLayout(progress_docs_group)
        
        progress_docs_text = QLabel("""
<b>Progress Dialog Types:</b><br><br>

<b>Determinate:</b> Shows specific progress percentage<br>
• Use when progress can be measured<br>
• Provides clear completion timeline<br>
• Users can estimate remaining time<br><br>

<b>Indeterminate:</b> Shows activity without specific progress<br>
• Use when progress cannot be measured<br>
• Indicates system is working<br>
• Prevents user anxiety about hang-ups<br><br>

<b>Cancellable:</b> Allows user to cancel operation<br>
• Important for long-running operations<br>
• Gives users control over their workflow<br>
• Should handle cancellation gracefully<br><br>

<b>Multi-step:</b> Shows progress through multiple phases<br>
• Breaks complex operations into steps<br>
• Provides context about current activity<br>
• Helps users understand the process<br>
""")
        progress_docs_text.setWordWrap(True)
        progress_docs_layout.addWidget(progress_docs_text)
        
        layout.addWidget(progress_docs_group)
        
        self.tab_widget.addTab(tab_widget, "Progress Dialogs")
        
    def create_teaching_tips_tab(self):
        """Create teaching tips demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Teaching tip examples
        tips_group = QGroupBox("Teaching Tip Examples")
        tips_layout = QGridLayout(tips_group)
        
        # Basic tip
        basic_tip_btn = QPushButton("💡 Basic Tip")
        basic_tip_btn.clicked.connect(lambda: self.show_teaching_tip(basic_tip_btn, "Basic Tip", "This is a basic teaching tip to help users understand features."))
        tips_layout.addWidget(basic_tip_btn, 0, 0)
        
        # Rich content tip
        rich_tip_btn = QPushButton("🎨 Rich Content Tip")
        rich_tip_btn.clicked.connect(lambda: self.show_rich_teaching_tip(rich_tip_btn))
        tips_layout.addWidget(rich_tip_btn, 0, 1)
        
        # Action tip
        action_tip_btn = QPushButton("⚡ Action Tip")
        action_tip_btn.clicked.connect(lambda: self.show_action_teaching_tip(action_tip_btn))
        tips_layout.addWidget(action_tip_btn, 1, 0)
        
        # Dismissible tip
        dismissible_tip_btn = QPushButton("❌ Dismissible Tip")
        dismissible_tip_btn.clicked.connect(lambda: self.show_dismissible_teaching_tip(dismissible_tip_btn))
        tips_layout.addWidget(dismissible_tip_btn, 1, 1)
        
        layout.addWidget(tips_group)
        
        # Tip configuration
        tip_config_group = QGroupBox("Teaching Tip Configuration")
        tip_config_layout = QFormLayout(tip_config_group)
        
        # Position
        self.tip_position_combo = QComboBox()
        self.tip_position_combo.addItems(["Top", "Bottom", "Left", "Right", "Auto"])
        self.tip_position_combo.setCurrentText("Auto")
        tip_config_layout.addRow("Position:", self.tip_position_combo)
        
        # Auto-dismiss
        self.auto_dismiss_check = QCheckBox("Auto-dismiss")
        self.auto_dismiss_check.setChecked(False)
        tip_config_layout.addRow("Behavior:", self.auto_dismiss_check)
        
        # Dismiss timeout
        self.dismiss_timeout_spin = QSpinBox()
        self.dismiss_timeout_spin.setRange(1, 30)
        self.dismiss_timeout_spin.setValue(5)
        self.dismiss_timeout_spin.setSuffix(" seconds")
        tip_config_layout.addRow("Auto-dismiss timeout:", self.dismiss_timeout_spin)
        
        layout.addWidget(tip_config_group)
        
        # Documentation
        tips_docs_group = QGroupBox("Teaching Tips Best Practices")
        tips_docs_layout = QVBoxLayout(tips_docs_group)
        
        tips_docs_text = QLabel("""
<b>Teaching Tips Guidelines:</b><br><br>

<b>When to Use:</b><br>
• Introduce new features or functionality<br>
• Provide contextual help for complex UI elements<br>
• Guide users through multi-step processes<br>
• Highlight important changes or updates<br><br>

<b>Content Best Practices:</b><br>
• Keep messages concise and actionable<br>
• Use clear, friendly language<br>
• Include relevant visuals when helpful<br>
• Provide a clear way to dismiss<br>
• Don't overuse - can become annoying<br><br>

<b>Positioning:</b><br>
• Position close to the relevant UI element<br>
• Ensure tips don't cover important content<br>
• Consider screen size and responsive design<br>
• Auto-adjust position to stay visible<br>
""")
        tips_docs_text.setWordWrap(True)
        tips_docs_layout.addWidget(tips_docs_text)
        
        layout.addWidget(tips_docs_group)
        
        self.tab_widget.addTab(tab_widget, "Teaching Tips")
        
    def create_system_dialogs_tab(self):
        """Create system dialogs demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # System dialog examples
        system_group = QGroupBox("System Dialog Examples")
        system_layout = QGridLayout(system_group)
        
        # File dialogs
        open_file_btn = QPushButton("📁 Open File")
        open_file_btn.clicked.connect(self.show_open_file_dialog)
        system_layout.addWidget(open_file_btn, 0, 0)
        
        save_file_btn = QPushButton("💾 Save File")
        save_file_btn.clicked.connect(self.show_save_file_dialog)
        system_layout.addWidget(save_file_btn, 0, 1)
        
        # Directory dialog
        select_dir_btn = QPushButton("📂 Select Directory")
        select_dir_btn.clicked.connect(self.show_directory_dialog)
        system_layout.addWidget(select_dir_btn, 1, 0)
        
        # Color dialog
        color_dialog_btn = QPushButton("🎨 Color Picker")
        color_dialog_btn.clicked.connect(self.show_color_dialog)
        system_layout.addWidget(color_dialog_btn, 1, 1)
        
        layout.addWidget(system_group)
        
        # Custom system dialogs
        custom_system_group = QGroupBox("Custom System Dialogs")
        custom_system_layout = QGridLayout(custom_system_group)
        
        # Font dialog
        font_dialog_btn = QPushButton("🔤 Font Selector")
        font_dialog_btn.clicked.connect(self.show_font_dialog)
        custom_system_layout.addWidget(font_dialog_btn, 0, 0)
        
        # Print dialog
        print_dialog_btn = QPushButton("🖨️ Print Dialog")
        print_dialog_btn.clicked.connect(self.show_print_dialog)
        custom_system_layout.addWidget(print_dialog_btn, 0, 1)
        
        layout.addWidget(custom_system_group)
        
        # Documentation
        system_docs_group = QGroupBox("System Dialog Features")
        system_docs_layout = QVBoxLayout(system_docs_group)
        
        system_docs_text = QLabel("""
<b>System Dialogs:</b><br>
• <b>File Operations:</b> Open, save, directory selection<br>
• <b>Color Selection:</b> System color picker integration<br>
• <b>Font Selection:</b> System font chooser<br>
• <b>Print Options:</b> Print configuration and preview<br><br>

<b>Benefits:</b><br>
• Consistent with system UI conventions<br>
• Native look and feel on each platform<br>
• Automatic handling of system preferences<br>
• Built-in accessibility support<br>
• User familiarity and confidence<br><br>

<b>Customization:</b><br>
• File filters and extensions<br>
• Default directories and filenames<br>
• Dialog titles and labels<br>
• Custom validation and handling<br>
""")
        system_docs_text.setWordWrap(True)
        system_docs_layout.addWidget(system_docs_text)
        
        layout.addWidget(system_docs_group)
        
        self.tab_widget.addTab(tab_widget, "System Dialogs")
        
    def create_results_display(self, parent_layout):
        """Create results display area."""
        results_group = QGroupBox("Dialog Results")
        results_layout = QVBoxLayout(results_group)
        
        # Clear button
        clear_btn = QPushButton("Clear Results")
        clear_btn.clicked.connect(self.clear_results)
        results_layout.addWidget(clear_btn)
        
        # Results display
        self.results_display = QTextEdit()
        self.results_display.setMaximumHeight(150)
        self.results_display.setReadOnly(True)
        results_layout.addWidget(self.results_display)
        
        parent_layout.addWidget(results_group)
        
    # Dialog implementation methods
    def show_simple_content_dialog(self):
        """Show simple content dialog."""
        if FLUENT_CONTENT_DIALOG_AVAILABLE:
            try:
                dialog = FluentContentDialog()
                dialog.setTitle("Simple Content Dialog")
                dialog.setContent("This is a simple content dialog with basic text content.")
                result = dialog.exec()
                self.log_result("Simple Content Dialog", f"Result: {result}")
            except Exception as e:
                self.show_fallback_dialog("Simple Content Dialog", str(e))
        else:
            self.show_fallback_dialog("Simple Content Dialog", "FluentContentDialog not available")
            
    def show_rich_content_dialog(self):
        """Show rich content dialog."""
        dialog = CustomDialog(self, "Rich Content Dialog")
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.log_result("Rich Content Dialog", f"Accepted: {data}")
        else:
            self.log_result("Rich Content Dialog", "Rejected")
            
    def show_scrollable_content_dialog(self):
        """Show scrollable content dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Scrollable Content Dialog")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        scroll_area = QScrollArea()
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Add lots of content
        for i in range(20):
            content_layout.addWidget(QLabel(f"This is line {i+1} of scrollable content."))
            
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        result = dialog.exec()
        self.log_result("Scrollable Content Dialog", f"Result: {result}")
        
    def show_custom_button_dialog(self):
        """Show custom button dialog."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Custom Button Dialog")
        msg_box.setText("Choose your preferred action:")
        
        # Add custom buttons
        save_btn = msg_box.addButton("Save", QMessageBox.ButtonRole.AcceptRole)
        save_as_btn = msg_box.addButton("Save As...", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        result = msg_box.exec()
        clicked_button = msg_box.clickedButton()
        
        if clicked_button == save_btn:
            self.log_result("Custom Button Dialog", "Save clicked")
        elif clicked_button == save_as_btn:
            self.log_result("Custom Button Dialog", "Save As clicked")
        else:
            self.log_result("Custom Button Dialog", "Cancel clicked")
            
    def show_info_dialog(self):
        """Show information dialog."""
        title = self.message_title_input.text()
        message = self.message_text_input.toPlainText()
        
        QMessageBox.information(self, title, message)
        self.log_result("Information Dialog", f"Shown: {title}")
        
    def show_warning_dialog(self):
        """Show warning dialog."""
        title = self.message_title_input.text()
        message = self.message_text_input.toPlainText()
        
        result = QMessageBox.warning(
            self, title, message,
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        
        self.log_result("Warning Dialog", f"Result: {result}")
        
    def show_error_dialog(self):
        """Show error dialog."""
        title = self.message_title_input.text()
        message = self.message_text_input.toPlainText()
        
        QMessageBox.critical(self, title, message)
        self.log_result("Error Dialog", f"Shown: {title}")
        
    def show_question_dialog(self):
        """Show question dialog."""
        title = self.message_title_input.text()
        message = self.message_text_input.toPlainText()
        
        result = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        self.log_result("Question Dialog", f"Result: {result}")
        
    def show_success_dialog(self):
        """Show success dialog."""
        title = self.message_title_input.text()
        message = self.message_text_input.toPlainText()
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        result = msg_box.exec()
        self.log_result("Success Dialog", f"Result: {result}")
        
    def show_custom_icon_dialog(self):
        """Show custom icon dialog."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Custom Icon Dialog")
        msg_box.setText("This dialog has a custom icon.")
        msg_box.setIcon(QMessageBox.Icon.NoIcon)
        # In a real implementation, you would set a custom pixmap
        # msg_box.setIconPixmap(QPixmap("custom_icon.png"))
        
        result = msg_box.exec()
        self.log_result("Custom Icon Dialog", f"Result: {result}")
        
    def show_text_input_dialog(self):
        """Show text input dialog."""
        text, ok = QInputDialog.getText(self, "Text Input", "Enter your name:")
        
        if ok and text:
            self.log_result("Text Input Dialog", f"Entered: {text}")
        else:
            self.log_result("Text Input Dialog", "Cancelled")
            
    def show_number_input_dialog(self):
        """Show number input dialog."""
        number, ok = QInputDialog.getInt(self, "Number Input", "Enter a number:", 0, -100, 100, 1)
        
        if ok:
            self.log_result("Number Input Dialog", f"Entered: {number}")
        else:
            self.log_result("Number Input Dialog", "Cancelled")
            
    def show_password_input_dialog(self):
        """Show password input dialog."""
        from PySide6.QtWidgets import QLineEdit
        password, ok = QInputDialog.getText(
            self, "Password Input", "Enter password:", 
            QLineEdit.EchoMode.Password
        )
        
        if ok:
            self.log_result("Password Input Dialog", f"Password entered (length: {len(password)})")
        else:
            self.log_result("Password Input Dialog", "Cancelled")
            
    def show_multiline_input_dialog(self):
        """Show multi-line input dialog."""
        text, ok = QInputDialog.getMultiLineText(
            self, "Multi-line Input", "Enter multiple lines:"
        )
        
        if ok:
            lines = text.count('\\n') + 1
            self.log_result("Multi-line Input Dialog", f"Entered {lines} lines")
        else:
            self.log_result("Multi-line Input Dialog", "Cancelled")
            
    def show_choice_input_dialog(self):
        """Show choice input dialog."""
        items = ["Option 1", "Option 2", "Option 3", "Option 4"]
        item, ok = QInputDialog.getItem(self, "Choice Input", "Select an option:", items, 0, False)
        
        if ok and item:
            self.log_result("Choice Input Dialog", f"Selected: {item}")
        else:
            self.log_result("Choice Input Dialog", "Cancelled")
            
    def show_date_input_dialog(self):
        """Show date input dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Date Input")
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        date_edit = QDateEdit()
        date_edit.setDate(datetime.now().date())
        layout.addRow("Select Date:", date_edit)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            date = date_edit.date().toString()
            self.log_result("Date Input Dialog", f"Selected: {date}")
        else:
            self.log_result("Date Input Dialog", "Cancelled")
            
    def show_email_input_dialog(self):
        """Show email input dialog with validation."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Email Input")
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        email_input = QLineEdit()
        email_input.setPlaceholderText("user@example.com")
        layout.addRow("Email:", email_input)
        
        error_label = QLabel()
        error_label.setStyleSheet("color: red;")
        layout.addWidget(error_label)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        
        def validate_email():
            import re
            email = email_input.text()
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
            
            if re.match(pattern, email):
                error_label.setText("")
                button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
                return True
            else:
                error_label.setText("Invalid email format")
                button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
                return False
                
        email_input.textChanged.connect(validate_email)
        validate_email()  # Initial validation
        
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.log_result("Email Input Dialog", f"Valid email: {email_input.text()}")
        else:
            self.log_result("Email Input Dialog", "Cancelled")
            
    def show_url_input_dialog(self):
        """Show URL input dialog with validation."""
        # Similar to email but with URL validation
        text, ok = QInputDialog.getText(self, "URL Input", "Enter URL:", text="https://")
        
        if ok and text:
            self.log_result("URL Input Dialog", f"Entered: {text}")
        else:
            self.log_result("URL Input Dialog", "Cancelled")
            
    def show_range_input_dialog(self):
        """Show range input dialog with validation."""
        number, ok = QInputDialog.getDouble(self, "Range Input", "Enter value (0-100):", 50.0, 0.0, 100.0, 2)
        
        if ok:
            self.log_result("Range Input Dialog", f"Entered: {number}")
        else:
            self.log_result("Range Input Dialog", "Cancelled")
            
    def show_custom_validation_dialog(self):
        """Show custom validation dialog."""
        self.log_result("Custom Validation Dialog", "Custom validation logic would be implemented here")
        
    def show_user_registration_dialog(self):
        """Show user registration form dialog."""
        dialog = CustomDialog(self, "User Registration")
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.log_result("User Registration Dialog", f"Registration data: {data}")
        else:
            self.log_result("User Registration Dialog", "Registration cancelled")
            
    def show_settings_form_dialog(self):
        """Show settings form dialog."""
        self.log_result("Settings Form Dialog", "Settings form would be implemented here")
        
    def show_contact_form_dialog(self):
        """Show contact form dialog."""
        self.log_result("Contact Form Dialog", "Contact form would be implemented here")
        
    def show_survey_form_dialog(self):
        """Show survey form dialog."""
        self.log_result("Survey Form Dialog", "Survey form would be implemented here")
        
    def show_wizard_form_dialog(self):
        """Show wizard form dialog."""
        self.log_result("Wizard Form Dialog", "Wizard form would be implemented here")
        
    def show_multipage_form_dialog(self):
        """Show multi-page form dialog."""
        self.log_result("Multi-page Form Dialog", "Multi-page form would be implemented here")
        
    def show_determinate_progress(self):
        """Show determinate progress dialog."""
        duration = self.progress_duration_spin.value()
        
        progress = QProgressDialog("Processing...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Determinate Progress")
        progress.setModal(True)
        progress.show()
        
        # Simulate work with timer
        self.progress_timer = QTimer()
        self.progress_value = 0
        
        def update_progress():
            self.progress_value += 2
            progress.setValue(self.progress_value)
            
            if self.progress_value >= 100:
                self.progress_timer.stop()
                progress.close()
                self.log_result("Determinate Progress", "Completed")
            elif progress.wasCanceled():
                self.progress_timer.stop()
                self.log_result("Determinate Progress", "Cancelled")
                
        self.progress_timer.timeout.connect(update_progress)
        self.progress_timer.start(duration * 10)  # Update every duration*10 ms
        
    def show_indeterminate_progress(self):
        """Show indeterminate progress dialog."""
        progress = QProgressDialog("Processing...", None, 0, 0, self)
        progress.setWindowTitle("Indeterminate Progress")
        progress.setModal(True)
        progress.show()
        
        # Close after a few seconds
        QTimer.singleShot(3000, lambda: [progress.close(), self.log_result("Indeterminate Progress", "Completed")])
        
    def show_cancellable_progress(self):
        """Show cancellable progress dialog."""
        self.worker_thread = WorkerThread()
        
        progress = QProgressDialog("Processing...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Cancellable Progress")
        progress.setModal(True)
        
        def on_progress_updated(value):
            progress.setValue(value)
            if progress.wasCanceled():
                self.worker_thread.terminate()
                self.log_result("Cancellable Progress", "Cancelled")
                
        def on_task_completed():
            progress.close()
            self.log_result("Cancellable Progress", "Completed")
            
        self.worker_thread.progress_updated.connect(on_progress_updated)
        self.worker_thread.task_completed.connect(on_task_completed)
        
        progress.show()
        self.worker_thread.start()
        
    def show_multistep_progress(self):
        """Show multi-step progress dialog."""
        steps = ["Initializing", "Processing", "Finalizing", "Complete"]
        current_step = 0
        
        progress = QProgressDialog(steps[0], "Cancel", 0, len(steps), self)
        progress.setWindowTitle("Multi-step Progress")
        progress.setModal(True)
        progress.show()
        
        def next_step():
            nonlocal current_step
            current_step += 1
            
            if current_step < len(steps):
                progress.setLabelText(steps[current_step])
                progress.setValue(current_step)
                QTimer.singleShot(1500, next_step)
            else:
                progress.close()
                self.log_result("Multi-step Progress", "All steps completed")
                
        QTimer.singleShot(1500, next_step)
        
    def show_teaching_tip(self, target_widget, title, content):
        """Show basic teaching tip."""
        if FLUENT_TEACHING_TIP_AVAILABLE:
            try:
                tip = FluentTeachingTip()
                tip.setTarget(target_widget)
                tip.setTitle(title)
                tip.setContent(content)
                tip.show()
                self.log_result("Teaching Tip", f"Shown: {title}")
            except Exception as e:
                self.show_fallback_tip(target_widget, title, content)
        else:
            self.show_fallback_tip(target_widget, title, content)
            
    def show_rich_teaching_tip(self, target_widget):
        """Show rich content teaching tip."""
        self.show_teaching_tip(
            target_widget, 
            "Rich Content Tip",
            "This tip contains rich content with formatting and multiple paragraphs.\\n\\nYou can include images, links, and other rich elements."
        )
        
    def show_action_teaching_tip(self, target_widget):
        """Show action teaching tip."""
        self.show_teaching_tip(
            target_widget,
            "Action Required",
            "This tip suggests an action for the user to take. Click the button to continue."
        )
        
    def show_dismissible_teaching_tip(self, target_widget):
        """Show dismissible teaching tip."""
        self.show_teaching_tip(
            target_widget,
            "Dismissible Tip", 
            "This tip can be dismissed by the user and won't show again."
        )
        
    def show_fallback_tip(self, target_widget, title, content):
        """Show fallback tooltip as teaching tip."""
        target_widget.setToolTip(f"<b>{title}</b><br>{content}")
        self.log_result("Teaching Tip (Fallback)", f"Tooltip set: {title}")
        
    def show_open_file_dialog(self):
        """Show open file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*);;Text Files (*.txt);;Python Files (*.py)"
        )
        
        if file_path:
            self.log_result("Open File Dialog", f"Selected: {file_path}")
        else:
            self.log_result("Open File Dialog", "Cancelled")
            
    def show_save_file_dialog(self):
        """Show save file dialog."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.log_result("Save File Dialog", f"Save to: {file_path}")
        else:
            self.log_result("Save File Dialog", "Cancelled")
            
    def show_directory_dialog(self):
        """Show directory selection dialog."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        
        if directory:
            self.log_result("Directory Dialog", f"Selected: {directory}")
        else:
            self.log_result("Directory Dialog", "Cancelled")
            
    def show_color_dialog(self):
        """Show color picker dialog."""
        color = QColorDialog.getColor(Qt.GlobalColor.white, self, "Select Color")
        
        if color.isValid():
            self.log_result("Color Dialog", f"Selected: {color.name()}")
        else:
            self.log_result("Color Dialog", "Cancelled")
            
    def show_font_dialog(self):
        """Show font selector dialog."""
        from PySide6.QtWidgets import QFontDialog
        font, ok = QFontDialog.getFont(self.font(), self, "Select Font")
        
        if ok:
            self.log_result("Font Dialog", f"Selected: {font.family()}, {font.pointSize()}pt")
        else:
            self.log_result("Font Dialog", "Cancelled")
            
    def show_print_dialog(self):
        """Show print dialog."""
        self.log_result("Print Dialog", "Print dialog would be implemented here")
        
    def show_fallback_dialog(self, title, message):
        """Show fallback dialog when fluent components are not available."""
        QMessageBox.information(self, f"{title} (Fallback)", message)
        self.log_result(f"{title} (Fallback)", "Shown with QMessageBox")
        
    def log_result(self, dialog_type, result):
        """Log dialog result to results display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {dialog_type}: {result}"
        
        self.dialog_results.append(log_entry)
        self.results_display.append(log_entry)
        self.statusBar().showMessage(f"Latest: {dialog_type} - {result}")
        
    def clear_results(self):
        """Clear the results display."""
        self.dialog_results.clear()
        self.results_display.clear()
        self.statusBar().showMessage("Results cleared")


def main():
    """Main function to run the demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Dialog Components Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Simple Fluent Widget")
    
    # Create and show the demo
    demo = DialogComponentsDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
