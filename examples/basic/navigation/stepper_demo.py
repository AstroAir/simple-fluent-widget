#!/usr/bin/env python3
"""
Fluent Stepper Component Demo

This example demonstrates the usage of FluentStepper components with various configurations,
including horizontal and vertical layouts, different step states, and interactive behaviors.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox, QPushButton, QTextEdit
from PySide6.QtCore import Qt, QTimer

from components.basic.navigation.stepper import FluentStepper
from core.theme import theme_manager


class StepperDemo(QMainWindow):
    """Main demo window showcasing Fluent stepper components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Stepper Demo")
        self.setGeometry(200, 200, 1000, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add title
        title = QLabel("Fluent Stepper Components Demo")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Create demo sections
        self.create_horizontal_steppers(main_layout)
        self.create_vertical_steppers(main_layout)
        self.create_interactive_steppers(main_layout)
        self.create_form_wizard(main_layout)
        
        main_layout.addStretch()
        
    def create_horizontal_steppers(self, parent_layout):
        """Create horizontal stepper examples."""
        group = QGroupBox("Horizontal Steppers")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Basic horizontal stepper
        basic_stepper = FluentStepper(style=FluentStepper.StepperStyle.HORIZONTAL)
        
        # Add steps
        steps = [
            {"title": "Account", "description": "Create your account"},
            {"title": "Profile", "description": "Set up your profile"},
            {"title": "Preferences", "description": "Configure settings"},
            {"title": "Complete", "description": "Finish setup"}
        ]
        
        for step in steps:
            basic_stepper.add_step(step["title"], step["description"])
        
        # Set current step
        basic_stepper.set_current_step(1)  # Profile step active
        
        layout.addWidget(QLabel("Basic Horizontal Stepper:"))
        layout.addWidget(basic_stepper)
        layout.addSpacing(15)
        
        # Order process stepper
        order_stepper = FluentStepper(style=FluentStepper.StepperStyle.HORIZONTAL)
        
        order_steps = [
            {"title": "Cart", "description": "Review items"},
            {"title": "Shipping", "description": "Enter address"},
            {"title": "Payment", "description": "Payment method"},
            {"title": "Confirm", "description": "Place order"}
        ]
        
        for step in order_steps:
            order_stepper.add_step(step["title"], step["description"])
        
        # Set some steps as completed
        order_stepper.set_step_state(0, FluentStepper.StepState.COMPLETED)
        order_stepper.set_step_state(1, FluentStepper.StepState.COMPLETED)
        order_stepper.set_current_step(2)  # Payment step active
        
        layout.addWidget(QLabel("Order Process Stepper:"))
        layout.addWidget(order_stepper)
        layout.addSpacing(15)
        
        # Progress with error
        error_stepper = FluentStepper(style=FluentStepper.StepperStyle.HORIZONTAL)
        
        error_steps = [
            {"title": "Upload", "description": "Upload files"},
            {"title": "Process", "description": "Process data"},
            {"title": "Validate", "description": "Validation failed"},
            {"title": "Complete", "description": "Finish"}
        ]
        
        for step in error_steps:
            error_stepper.add_step(step["title"], step["description"])
        
        # Set states
        error_stepper.set_step_state(0, FluentStepper.StepState.COMPLETED)
        error_stepper.set_step_state(1, FluentStepper.StepState.COMPLETED)
        error_stepper.set_step_state(2, FluentStepper.StepState.ERROR)
        error_stepper.set_current_step(2)
        
        layout.addWidget(QLabel("Stepper with Error State:"))
        layout.addWidget(error_stepper)
        
        parent_layout.addWidget(group)
        
    def create_vertical_steppers(self, parent_layout):
        """Create vertical stepper examples."""
        group = QGroupBox("Vertical Steppers")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        
        # Use horizontal layout to show vertical steppers side by side
        main_layout = QHBoxLayout(group)
        
        # Left side - Simple vertical stepper
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Installation Steps:"))
        
        install_stepper = FluentStepper(style=FluentStepper.StepperStyle.VERTICAL)
        
        install_steps = [
            {"title": "Download", "description": "Download installer"},
            {"title": "Install", "description": "Run installation"},
            {"title": "Configure", "description": "Set preferences"},
            {"title": "Launch", "description": "Start application"}
        ]
        
        for step in install_steps:
            install_stepper.add_step(step["title"], step["description"])
        
        install_stepper.set_step_state(0, FluentStepper.StepState.COMPLETED)
        install_stepper.set_step_state(1, FluentStepper.StepState.COMPLETED)
        install_stepper.set_current_step(2)
        
        left_layout.addWidget(install_stepper)
        left_layout.addStretch()
        
        # Right side - Project workflow stepper
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Project Workflow:"))
        
        workflow_stepper = FluentStepper(style=FluentStepper.StepperStyle.VERTICAL)
        
        workflow_steps = [
            {"title": "Planning", "description": "Requirements analysis"},
            {"title": "Design", "description": "UI/UX design phase"},
            {"title": "Development", "description": "Code implementation"},
            {"title": "Testing", "description": "Quality assurance"},
            {"title": "Deployment", "description": "Production release"}
        ]
        
        for step in workflow_steps:
            workflow_stepper.add_step(step["title"], step["description"])
        
        workflow_stepper.set_step_state(0, FluentStepper.StepState.COMPLETED)
        workflow_stepper.set_step_state(1, FluentStepper.StepState.COMPLETED)
        workflow_stepper.set_step_state(2, FluentStepper.StepState.COMPLETED)
        workflow_stepper.set_current_step(3)
        
        right_layout.addWidget(workflow_stepper)
        right_layout.addStretch()
        
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        
        parent_layout.addWidget(group)
        
    def create_interactive_steppers(self, parent_layout):
        """Create interactive stepper examples."""
        group = QGroupBox("Interactive Steppers")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Interactive stepper with controls
        self.interactive_stepper = FluentStepper(style=FluentStepper.StepperStyle.HORIZONTAL)
        
        interactive_steps = [
            {"title": "Start", "description": "Begin the process"},
            {"title": "Step 2", "description": "Second step"},
            {"title": "Step 3", "description": "Third step"},
            {"title": "Finish", "description": "Complete the process"}
        ]
        
        for step in interactive_steps:
            self.interactive_stepper.add_step(step["title"], step["description"])
        
        self.interactive_stepper.set_current_step(0)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.go_previous)
        self.prev_btn.setEnabled(False)  # Disabled at start
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.go_next)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_stepper)
        
        control_layout.addWidget(self.prev_btn)
        control_layout.addWidget(self.next_btn)
        control_layout.addWidget(self.reset_btn)
        control_layout.addStretch()
        
        # Status display
        self.status_label = QLabel("Current: Start (Step 1 of 4)")
        
        layout.addWidget(QLabel("Interactive Stepper with Controls:"))
        layout.addWidget(self.interactive_stepper)
        layout.addLayout(control_layout)
        layout.addWidget(self.status_label)
        layout.addSpacing(15)
        
        # Auto-advancing stepper
        self.auto_stepper = FluentStepper(style=FluentStepper.StepperStyle.HORIZONTAL)
        
        auto_steps = [
            {"title": "Initialize", "description": "Starting process"},
            {"title": "Process", "description": "Processing data"},
            {"title": "Validate", "description": "Validating results"},
            {"title": "Complete", "description": "Process finished"}
        ]
        
        for step in auto_steps:
            self.auto_stepper.add_step(step["title"], step["description"])
        
        self.auto_stepper.set_current_step(0)
        
        # Auto advance controls
        auto_control_layout = QHBoxLayout()
        
        self.start_auto_btn = QPushButton("Start Auto Process")
        self.start_auto_btn.clicked.connect(self.start_auto_process)
        
        self.stop_auto_btn = QPushButton("Stop")
        self.stop_auto_btn.clicked.connect(self.stop_auto_process)
        self.stop_auto_btn.setEnabled(False)
        
        auto_control_layout.addWidget(self.start_auto_btn)
        auto_control_layout.addWidget(self.stop_auto_btn)
        auto_control_layout.addStretch()
        
        self.auto_status_label = QLabel("Click 'Start Auto Process' to begin")
        
        # Timer for auto advance
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.advance_auto_step)
        self.auto_current_step = 0
        
        layout.addWidget(QLabel("Auto-Advancing Stepper:"))
        layout.addWidget(self.auto_stepper)
        layout.addLayout(auto_control_layout)
        layout.addWidget(self.auto_status_label)
        
        parent_layout.addWidget(group)
        
    def create_form_wizard(self, parent_layout):
        """Create a form wizard example."""
        group = QGroupBox("Form Wizard Example")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Wizard stepper
        self.wizard_stepper = FluentStepper(style=FluentStepper.StepperStyle.HORIZONTAL)
        
        wizard_steps = [
            {"title": "Personal", "description": "Personal information"},
            {"title": "Contact", "description": "Contact details"},
            {"title": "Preferences", "description": "User preferences"},
            {"title": "Review", "description": "Review and submit"}
        ]
        
        for step in wizard_steps:
            self.wizard_stepper.add_step(step["title"], step["description"])
        
        self.wizard_stepper.set_current_step(0)
        
        # Form content area
        self.form_content = QTextEdit()
        self.form_content.setMaximumHeight(100)
        self.form_content.setReadOnly(True)
        
        # Form content for each step
        self.form_contents = [
            "Personal Information Form:\n\n• Full Name\n• Date of Birth\n• Address\n• Phone Number",
            "Contact Details Form:\n\n• Email Address\n• Preferred Contact Method\n• Emergency Contact\n• Communication Preferences",
            "User Preferences Form:\n\n• Language Settings\n• Notification Preferences\n• Theme Selection\n• Privacy Settings",
            "Review and Submit:\n\n• Please review all information\n• Check for accuracy\n• Submit form when ready\n• Confirmation will be sent"
        ]
        
        # Initialize with first content
        self.form_content.setPlainText(self.form_contents[0])
        
        # Wizard controls
        wizard_control_layout = QHBoxLayout()
        
        self.wizard_prev_btn = QPushButton("Back")
        self.wizard_prev_btn.clicked.connect(self.wizard_previous)
        self.wizard_prev_btn.setEnabled(False)
        
        self.wizard_next_btn = QPushButton("Next")
        self.wizard_next_btn.clicked.connect(self.wizard_next)
        
        wizard_control_layout.addStretch()
        wizard_control_layout.addWidget(self.wizard_prev_btn)
        wizard_control_layout.addWidget(self.wizard_next_btn)
        
        self.wizard_current_step = 0
        
        layout.addWidget(QLabel("Multi-step Form Wizard:"))
        layout.addWidget(self.wizard_stepper)
        layout.addWidget(self.form_content)
        layout.addLayout(wizard_control_layout)
        
        parent_layout.addWidget(group)
    
    def go_previous(self):
        """Go to previous step in interactive stepper."""
        current = self.interactive_stepper.get_current_step()
        if current > 0:
            new_step = current - 1
            self.interactive_stepper.set_current_step(new_step)
            self.status_label.setText(f"Current: {['Start', 'Step 2', 'Step 3', 'Finish'][new_step]} (Step {new_step + 1} of 4)")
            
            # Update button states
            self.prev_btn.setEnabled(new_step > 0)
            self.next_btn.setEnabled(new_step < 3)
            self.next_btn.setText("Next" if new_step < 3 else "Finish")
    
    def go_next(self):
        """Go to next step in interactive stepper."""
        current = self.interactive_stepper.get_current_step()
        if current < 3:
            # Mark current step as completed
            self.interactive_stepper.set_step_state(current, FluentStepper.StepState.COMPLETED)
            
            new_step = current + 1
            self.interactive_stepper.set_current_step(new_step)
            self.status_label.setText(f"Current: {['Start', 'Step 2', 'Step 3', 'Finish'][new_step]} (Step {new_step + 1} of 4)")
            
            # Update button states
            self.prev_btn.setEnabled(new_step > 0)
            self.next_btn.setEnabled(new_step < 3)
            self.next_btn.setText("Next" if new_step < 3 else "Finish")
    
    def reset_stepper(self):
        """Reset the interactive stepper."""
        for i in range(4):
            self.interactive_stepper.set_step_state(i, FluentStepper.StepState.PENDING)
        
        self.interactive_stepper.set_current_step(0)
        self.status_label.setText("Current: Start (Step 1 of 4)")
        
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(True)
        self.next_btn.setText("Next")
    
    def start_auto_process(self):
        """Start the auto-advancing process."""
        self.auto_current_step = 0
        
        # Reset stepper
        for i in range(4):
            self.auto_stepper.set_step_state(i, FluentStepper.StepState.PENDING)
        
        self.auto_stepper.set_current_step(0)
        self.auto_status_label.setText("Auto process started...")
        
        # Start timer (advance every 2 seconds)
        self.auto_timer.start(2000)
        
        self.start_auto_btn.setEnabled(False)
        self.stop_auto_btn.setEnabled(True)
    
    def advance_auto_step(self):
        """Advance to next step in auto process."""
        if self.auto_current_step < 3:
            # Mark current step as completed
            self.auto_stepper.set_step_state(self.auto_current_step, FluentStepper.StepState.COMPLETED)
            
            self.auto_current_step += 1
            self.auto_stepper.set_current_step(self.auto_current_step)
            
            step_names = ["Initialize", "Process", "Validate", "Complete"]
            self.auto_status_label.setText(f"Processing: {step_names[self.auto_current_step]}...")
            
            if self.auto_current_step >= 3:
                # Process complete
                self.auto_timer.stop()
                self.auto_status_label.setText("Auto process completed!")
                self.start_auto_btn.setEnabled(True)
                self.stop_auto_btn.setEnabled(False)
    
    def stop_auto_process(self):
        """Stop the auto-advancing process."""
        self.auto_timer.stop()
        self.auto_status_label.setText("Auto process stopped")
        self.start_auto_btn.setEnabled(True)
        self.stop_auto_btn.setEnabled(False)
    
    def wizard_previous(self):
        """Go to previous step in wizard."""
        if self.wizard_current_step > 0:
            self.wizard_current_step -= 1
            self.wizard_stepper.set_current_step(self.wizard_current_step)
            self.form_content.setPlainText(self.form_contents[self.wizard_current_step])
            
            # Update button states
            self.wizard_prev_btn.setEnabled(self.wizard_current_step > 0)
            self.wizard_next_btn.setEnabled(True)
            self.wizard_next_btn.setText("Next" if self.wizard_current_step < 3 else "Submit")
    
    def wizard_next(self):
        """Go to next step in wizard."""
        if self.wizard_current_step < 3:
            # Mark current step as completed
            self.wizard_stepper.set_step_state(self.wizard_current_step, FluentStepper.StepState.COMPLETED)
            
            self.wizard_current_step += 1
            self.wizard_stepper.set_current_step(self.wizard_current_step)
            self.form_content.setPlainText(self.form_contents[self.wizard_current_step])
            
            # Update button states
            self.wizard_prev_btn.setEnabled(True)
            self.wizard_next_btn.setText("Submit" if self.wizard_current_step >= 3 else "Next")


def main():
    """Run the stepper demo application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent Stepper Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = StepperDemo()
    demo.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
