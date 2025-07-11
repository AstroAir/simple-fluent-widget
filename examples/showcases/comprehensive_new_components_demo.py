"""
Comprehensive demo showcasing new Fluent Design components

This demo demonstrates the new components added to the simple-fluent-widget library:
- FluentNumberBox: Numeric input with validation and step controls
- FluentAutoSuggestBox: Autocomplete input with fuzzy matching
- FluentTeachingTip: Contextual help tooltips
- FluentContentDialog: Modal dialogs with Fluent styling
- FluentMessageDialog: Simple message dialogs
- FluentGrid: Responsive grid layout
- FluentScrollViewer: Custom scroll container
- FluentStackPanel: Vertical/horizontal stacking layout
- FluentWrapPanel: Wrapping layout container
"""

import sys
import random
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTabWidget,
                             QTextEdit, QGroupBox, QFormLayout, QSpinBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import new components (with fallback for missing components)
try:
    from components.inputs.fluent_number_box import FluentNumberBox
    from components.inputs.fluent_auto_suggest_box import FluentAutoSuggestBox
    from components.dialogs.teaching_tip import FluentTeachingTip
    from components.dialogs.content_dialog import FluentContentDialog, show_content_dialog
    from components.dialogs.message_dialog import (FluentMessageDialog, show_information_dialog,
                                                          show_warning_dialog, show_error_dialog,
                                                          show_question_dialog, show_success_dialog)
    from components.layout.fluent_grid import FluentGrid
    from components.layout.scroll_viewer import FluentScrollViewer
    from components.layout.stack_panel import FluentStackPanel, FluentWrapPanel, StackOrientation
except ImportError as e:
    print(f"Warning: Could not import some components: {e}")
    # Create dummy classes for missing components
    class FluentNumberBox(QWidget): pass
    class FluentAutoSuggestBox(QWidget): pass
    class FluentTeachingTip(QWidget): pass
    class FluentContentDialog(QWidget): pass
    class FluentMessageDialog(QWidget): pass
    class FluentGrid(QWidget): pass
    class FluentScrollViewer(QWidget): pass
    class FluentStackPanel(QWidget): pass
    class FluentWrapPanel(QWidget): pass


class NewComponentsDemo(QMainWindow):
    """Main demo window showcasing new Fluent Design components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Fluent Design Components Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tab widget for different component categories
        self.tab_widget = QTabWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tab_widget)
        
        # Add tabs for different component categories
        self._create_input_components_tab()
        self._create_dialog_components_tab()
        self._create_layout_components_tab()
        self._create_advanced_demos_tab()
        
        # Apply styling
        self._setup_styling()
        
    def _setup_styling(self):
        """Setup window styling."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f2f1;
            }
            QTabWidget::pane {
                border: 1px solid #e1e1e1;
                background-color: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #f3f2f1;
                border: 1px solid #e1e1e1;
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover {
                background-color: #f9f9f9;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e1e1e1;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                background-color: white;
            }
        """)
        
    def _create_input_components_tab(self):
        """Create tab for input components."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Number Box Group
        number_group = QGroupBox("FluentNumberBox")
        number_layout = QFormLayout(number_group)
        
        # Basic number box
        self.number_box = FluentNumberBox()
        self.number_box.set_minimum(0)
        self.number_box.set_maximum(100)
        self.number_box.set_step(5)
        self.number_box.set_value(50)
        number_layout.addRow("Basic Number Box:", self.number_box)
        
        # Number box with custom format
        self.currency_box = FluentNumberBox()
        self.currency_box.set_minimum(0)
        self.currency_box.set_maximum(9999.99)
        self.currency_box.set_step(0.01)
        self.currency_box.set_precision(2)
        self.currency_box.set_prefix("$")
        self.currency_box.set_value(123.45)
        number_layout.addRow("Currency Box:", self.currency_box)
        
        layout.addWidget(number_group)
        
        # Auto Suggest Box Group
        suggest_group = QGroupBox("FluentAutoSuggestBox")
        suggest_layout = QFormLayout(suggest_group)
        
        # Basic auto suggest
        self.suggest_box = FluentAutoSuggestBox()
        suggestions = ["Apple", "Banana", "Cherry", "Date", "Elderberry", 
                      "Fig", "Grape", "Honeydew", "Kiwi", "Lemon"]
        self.suggest_box.set_suggestions(suggestions)
        self.suggest_box.set_placeholder_text("Type a fruit name...")
        suggest_layout.addRow("Fruit Suggestions:", self.suggest_box)
        
        # Programming languages suggest
        self.lang_suggest = FluentAutoSuggestBox()
        languages = ["Python", "JavaScript", "TypeScript", "C++", "C#", "Java",
                    "Go", "Rust", "Swift", "Kotlin", "PHP", "Ruby"]
        self.lang_suggest.set_suggestions(languages)
        self.lang_suggest.set_placeholder_text("Type a programming language...")
        self.lang_suggest.set_fuzzy_matching(True)
        suggest_layout.addRow("Language Suggestions:", self.lang_suggest)
        
        layout.addWidget(suggest_group)
        
        # Results display
        results_group = QGroupBox("Input Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(150)
        self.results_text.setPlainText("Input values will be displayed here...")
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        
        # Connect signals to update results
        try:
            self.number_box.value_changed.connect(self._update_results)
            self.currency_box.value_changed.connect(self._update_results)
            self.suggest_box.text_changed.connect(self._update_results)
            self.lang_suggest.text_changed.connect(self._update_results)
        except AttributeError:
            pass  # Fallback for dummy classes
            
        layout.addStretch()
        self.tab_widget.addTab(tab, "Input Components")
        
    def _create_dialog_components_tab(self):
        """Create tab for dialog components."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Content Dialog Group
        content_dialog_group = QGroupBox("FluentContentDialog")
        content_layout = QVBoxLayout(content_dialog_group)
        
        # Buttons to show different dialogs
        show_basic_dialog_btn = QPushButton("Show Basic Content Dialog")
        show_basic_dialog_btn.clicked.connect(self._show_basic_content_dialog)
        content_layout.addWidget(show_basic_dialog_btn)
        
        show_custom_dialog_btn = QPushButton("Show Custom Content Dialog")
        show_custom_dialog_btn.clicked.connect(self._show_custom_content_dialog)
        content_layout.addWidget(show_custom_dialog_btn)
        
        layout.addWidget(content_dialog_group)
        
        # Message Dialog Group
        message_dialog_group = QGroupBox("FluentMessageDialog")
        message_layout = QHBoxLayout(message_dialog_group)
        
        info_btn = QPushButton("Information")
        info_btn.clicked.connect(self._show_info_dialog)
        message_layout.addWidget(info_btn)
        
        warning_btn = QPushButton("Warning")
        warning_btn.clicked.connect(self._show_warning_dialog)
        message_layout.addWidget(warning_btn)
        
        error_btn = QPushButton("Error")
        error_btn.clicked.connect(self._show_error_dialog)
        message_layout.addWidget(error_btn)
        
        question_btn = QPushButton("Question")
        question_btn.clicked.connect(self._show_question_dialog)
        message_layout.addWidget(question_btn)
        
        success_btn = QPushButton("Success")
        success_btn.clicked.connect(self._show_success_dialog)
        message_layout.addWidget(success_btn)
        
        layout.addWidget(message_dialog_group)
        
        # Teaching Tip Group
        teaching_tip_group = QGroupBox("FluentTeachingTip")
        tip_layout = QVBoxLayout(teaching_tip_group)
        
        self.tip_target_btn = QPushButton("Hover for Teaching Tip")
        self.tip_target_btn.setToolTip("This button demonstrates the teaching tip")
        tip_layout.addWidget(self.tip_target_btn)
        
        # Create teaching tip
        try:
            self.teaching_tip = FluentTeachingTip(self.tip_target_btn)
            self.teaching_tip.set_title("Teaching Tip Demo")
            self.teaching_tip.set_content("This is a contextual help tooltip that provides "
                                        "additional information about UI elements.")
        except:
            pass  # Fallback for dummy classes
            
        layout.addWidget(teaching_tip_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Dialog Components")
        
    def _create_layout_components_tab(self):
        """Create tab for layout components."""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        
        # Grid Layout Group
        grid_group = QGroupBox("FluentGrid (Standard & Responsive)")
        grid_layout = QVBoxLayout(grid_group)
        
        # Create responsive grid
        try:
            self.responsive_grid = FluentGrid(use_breakpoints=True)
            
            # Add sample widgets to grid
            for i in range(12):
                btn = QPushButton(f"Item {i+1}")
                btn.setMinimumHeight(40)
                self.responsive_grid.add_widget(btn)
                
            grid_layout.addWidget(self.responsive_grid)
        except:
            grid_layout.addWidget(QLabel("FluentGrid (responsive) not available"))
            
        main_layout.addWidget(grid_group)
        
        # Stack Panel Group
        stack_group = QGroupBox("FluentStackPanel")
        stack_main_layout = QHBoxLayout(stack_group)
        
        # Vertical stack
        try:
            v_stack_container = QGroupBox("Vertical Stack")
            v_stack_layout = QVBoxLayout(v_stack_container)
            
            self.v_stack = FluentStackPanel(StackOrientation.VERTICAL)
            for i in range(4):
                btn = QPushButton(f"V-Item {i+1}")
                self.v_stack.add_widget(btn)
            v_stack_layout.addWidget(self.v_stack)
            
            stack_main_layout.addWidget(v_stack_container)
            
            # Horizontal stack
            h_stack_container = QGroupBox("Horizontal Stack")
            h_stack_layout = QVBoxLayout(h_stack_container)
            
            self.h_stack = FluentStackPanel(StackOrientation.HORIZONTAL)
            for i in range(4):
                btn = QPushButton(f"H-Item {i+1}")
                self.h_stack.add_widget(btn)
            h_stack_layout.addWidget(self.h_stack)
            
            stack_main_layout.addWidget(h_stack_container)
        except:
            stack_main_layout.addWidget(QLabel("FluentStackPanel not available"))
            
        main_layout.addWidget(stack_group)
        
        # Wrap Panel Group
        wrap_group = QGroupBox("FluentWrapPanel")
        wrap_layout = QVBoxLayout(wrap_group)
        
        try:
            self.wrap_panel = FluentWrapPanel()
            for i in range(8):
                btn = QPushButton(f"Wrap {i+1}")
                btn.setFixedSize(80, 30)
                self.wrap_panel.add_widget(btn)
            wrap_layout.addWidget(self.wrap_panel)
        except:
            wrap_layout.addWidget(QLabel("FluentWrapPanel not available"))
            
        main_layout.addWidget(wrap_group)
        
        self.tab_widget.addTab(tab, "Layout Components")
        
    def _create_advanced_demos_tab(self):
        """Create tab for advanced component combinations."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Scroll Viewer Demo
        scroll_group = QGroupBox("FluentScrollViewer with Dynamic Content")
        scroll_layout = QVBoxLayout(scroll_group)
        
        # Controls
        controls_layout = QHBoxLayout()
        add_content_btn = QPushButton("Add Content")
        add_content_btn.clicked.connect(self._add_scroll_content)
        clear_content_btn = QPushButton("Clear Content")
        clear_content_btn.clicked.connect(self._clear_scroll_content)
        
        controls_layout.addWidget(add_content_btn)
        controls_layout.addWidget(clear_content_btn)
        controls_layout.addStretch()
        scroll_layout.addLayout(controls_layout)
        
        # Scroll viewer
        try:
            self.scroll_viewer = FluentScrollViewer()
            self.scroll_content = QWidget()
            self.scroll_content_layout = QVBoxLayout(self.scroll_content)
            
            # Add initial content
            for i in range(10):
                label = QLabel(f"Scrollable content item {i+1}")
                label.setMinimumHeight(40)
                label.setStyleSheet("background-color: #f9f9f9; border: 1px solid #e1e1e1; padding: 8px; margin: 2px;")
                self.scroll_content_layout.addWidget(label)
                
            self.scroll_viewer.setWidget(self.scroll_content)
            self.scroll_viewer.setMinimumHeight(200)
            scroll_layout.addWidget(self.scroll_viewer)
        except:
            scroll_layout.addWidget(QLabel("FluentScrollViewer not available"))
            
        layout.addWidget(scroll_group)
        
        # Component Interaction Demo
        interaction_group = QGroupBox("Component Interactions")
        interaction_layout = QVBoxLayout(interaction_group)
        
        interaction_text = QLabel(
            "This demo shows how components work together:\n"
            "• NumberBox values affect grid generation\n" 
            "• AutoSuggestBox controls content filtering\n"
            "• Dialogs provide feedback and confirmations"
        )
        interaction_layout.addWidget(interaction_text)
        
        # Interactive controls
        interactive_layout = QFormLayout()
        
        self.grid_size_spinner = QSpinBox()
        self.grid_size_spinner.setRange(1, 20)
        self.grid_size_spinner.setValue(6)
        self.grid_size_spinner.valueChanged.connect(self._update_interactive_grid)
        interactive_layout.addRow("Grid Items:", self.grid_size_spinner)
        
        interaction_layout.addLayout(interactive_layout)
        
        # Interactive grid
        try:
            self.interactive_grid = FluentGrid()
            self._update_interactive_grid()
            interaction_layout.addWidget(self.interactive_grid)
        except:
            interaction_layout.addWidget(QLabel("Interactive grid not available"))
            
        layout.addWidget(interaction_group)
        
        self.tab_widget.addTab(tab, "Advanced Demos")
        
    def _update_results(self):
        """Update results display with current input values."""
        results = []
        
        try:
            if hasattr(self, 'number_box'):
                results.append(f"Number Box: {self.number_box.get_value()}")
            if hasattr(self, 'currency_box'):
                results.append(f"Currency Box: ${self.currency_box.get_value():.2f}")
            if hasattr(self, 'suggest_box'):
                results.append(f"Fruit Suggestion: {self.suggest_box.get_text()}")
            if hasattr(self, 'lang_suggest'):
                results.append(f"Language Suggestion: {self.lang_suggest.get_text()}")
        except:
            results.append("Results not available")
            
        self.results_text.setPlainText("\n".join(results))
        
    def _show_basic_content_dialog(self):
        """Show basic content dialog."""
        try:
            dialog = show_content_dialog(
                self,
                "Basic Dialog",
                "This is a basic content dialog with Fluent Design styling.",
                "OK",
                "Cancel"
            )
        except:
            print("Content dialog not available")
            
    def _show_custom_content_dialog(self):
        """Show custom content dialog."""
        try:
            dialog = FluentContentDialog(self, "Custom Dialog", 
                                       "This dialog has custom button text and callbacks.")
            dialog.set_primary_button_text("Accept")
            dialog.set_secondary_button_text("Decline")
            
            def on_accept():
                print("User accepted the dialog")
            def on_decline():
                print("User declined the dialog")
                
            dialog.set_primary_button_callback(on_accept)
            dialog.set_secondary_button_callback(on_decline)
            dialog.show()
        except:
            print("Custom content dialog not available")
            
    def _show_info_dialog(self):
        """Show information dialog."""
        try:
            show_information_dialog(self, "Information", "This is an information message.")
        except:
            print("Information dialog not available")
            
    def _show_warning_dialog(self):
        """Show warning dialog."""
        try:
            show_warning_dialog(self, "Warning", "This is a warning message.")
        except:
            print("Warning dialog not available")
            
    def _show_error_dialog(self):
        """Show error dialog."""
        try:
            show_error_dialog(self, "Error", "This is an error message.")
        except:
            print("Error dialog not available")
            
    def _show_question_dialog(self):
        """Show question dialog."""
        try:
            show_question_dialog(self, "Question", "Do you want to continue?")
        except:
            print("Question dialog not available")
            
    def _show_success_dialog(self):
        """Show success dialog."""
        try:
            show_success_dialog(self, "Success", "Operation completed successfully!")
        except:
            print("Success dialog not available")
            
    def _add_scroll_content(self):
        """Add content to scroll viewer."""
        try:
            count = self.scroll_content_layout.count()
            label = QLabel(f"Dynamic content item {count + 1}")
            label.setMinimumHeight(40)
            label.setStyleSheet("background-color: #e3f2fd; border: 1px solid #2196f3; padding: 8px; margin: 2px;")
            self.scroll_content_layout.addWidget(label)
        except:
            print("Scroll content not available")
            
    def _clear_scroll_content(self):
        """Clear scroll viewer content."""
        try:
            while self.scroll_content_layout.count():
                child = self.scroll_content_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        except:
            print("Scroll content not available")
            
    def _update_interactive_grid(self):
        """Update interactive grid based on spinner value."""
        try:
            self.interactive_grid.clear()
            count = self.grid_size_spinner.value()
            
            for i in range(count):
                btn = QPushButton(f"Grid {i+1}")
                btn.setMinimumHeight(50)
                btn.clicked.connect(lambda checked, idx=i: self._on_grid_item_clicked(idx))
                self.interactive_grid.add_widget(btn)
        except:
            print("Interactive grid not available")
            
    def _on_grid_item_clicked(self, index):
        """Handle grid item click."""
        try:
            show_information_dialog(self, "Grid Item", f"You clicked grid item {index + 1}")
        except:
            print(f"Grid item {index + 1} clicked")


def main():
    """Main function to run the demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent Design Components Demo")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    demo = NewComponentsDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
