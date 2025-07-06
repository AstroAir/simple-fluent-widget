"""
Comprehensive Component Examples Index

This is the main entry point for exploring all component examples in the simple-fluent-widget library.
It provides easy navigation to all available demonstrations and usage examples.

Examples Categories:
- Layout Components (dock panels, stack panels, grids, containers)
- Basic Components (forms, display, navigation, visual elements)
- Data Components (input, display, charts, visualization)
- Composite Components (complex forms, navigation, settings panels)
- Dialog Components (message dialogs, form dialogs, progress dialogs)
- Media Components (audio, video, image viewers)
- Interface Components (menus, toolbars, command interfaces)

Usage:
    python examples_index.py

This will launch a main window with navigation to all available examples.
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QTextEdit, QGroupBox,
    QScrollArea, QFrame, QSplitter, QTreeWidget, QTreeWidgetItem,
    QTabWidget, QListWidget, QListWidgetItem, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QProcess
from PySide6.QtGui import QColor, QPalette, QFont, QIcon, QPixmap

# Project root for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ExampleRunner(QThread):
    """Thread for running example scripts."""
    
    finished = Signal(str, bool)  # script_name, success
    output = Signal(str)  # output text
    
    def __init__(self, script_path):
        super().__init__()
        self.script_path = script_path
        
    def run(self):
        """Run the example script."""
        try:
            process = QProcess()
            process.start(sys.executable, [str(self.script_path)])
            process.waitForStarted()
            
            if process.state() == QProcess.ProcessState.Running:
                self.output.emit(f"Started: {self.script_path.name}")
                self.finished.emit(self.script_path.name, True)
            else:
                self.output.emit(f"Failed to start: {self.script_path.name}")
                self.finished.emit(self.script_path.name, False)
                
        except Exception as e:
            self.output.emit(f"Error running {self.script_path.name}: {str(e)}")
            self.finished.emit(self.script_path.name, False)


class ComponentExamplesIndex(QMainWindow):
    """Main window for browsing and running component examples."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Fluent Widget - Component Examples Index")
        self.setGeometry(100, 100, 1400, 900)
        
        # Example categories and their files
        self.examples = self.discover_examples()
        self.running_processes = {}
        
        self.setup_ui()
        self.populate_examples_tree()
        
    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with splitter
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - examples tree
        self.setup_examples_panel(splitter)
        
        # Right panel - details and controls
        self.setup_details_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([400, 1000])
        
        # Status bar
        self.setup_status_bar()
        
    def setup_examples_panel(self, parent):
        """Setup left panel with examples tree."""
        panel_widget = QWidget()
        panel_layout = QVBoxLayout(panel_widget)
        
        # Title
        title = QLabel("Component Examples")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(title)
        
        # Search/filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_input = QPushButton("Filter examples (coming soon)")
        self.search_input.setEnabled(False)
        search_layout.addWidget(self.search_input)
        
        panel_layout.addLayout(search_layout)
        
        # Examples tree
        self.examples_tree = QTreeWidget()
        self.examples_tree.setHeaderLabels(["Example", "Status"])
        self.examples_tree.itemClicked.connect(self.on_example_selected)
        self.examples_tree.itemDoubleClicked.connect(self.run_selected_example)
        panel_layout.addWidget(self.examples_tree)
        
        # Control buttons
        buttons_layout = QVBoxLayout()
        
        self.run_btn = QPushButton("Run Selected Example")
        self.run_btn.clicked.connect(self.run_selected_example)
        self.run_btn.setEnabled(False)
        buttons_layout.addWidget(self.run_btn)
        
        self.view_code_btn = QPushButton("View Source Code")
        self.view_code_btn.clicked.connect(self.view_source_code)
        self.view_code_btn.setEnabled(False)
        buttons_layout.addWidget(self.view_code_btn)
        
        self.run_all_btn = QPushButton("Run All Examples")
        self.run_all_btn.clicked.connect(self.run_all_examples)
        buttons_layout.addWidget(self.run_all_btn)
        
        panel_layout.addLayout(buttons_layout)
        
        parent.addWidget(panel_widget)
        
    def setup_details_panel(self, parent):
        """Setup right panel with example details."""
        panel_widget = QWidget()
        panel_layout = QVBoxLayout(panel_widget)
        
        # Tab widget for different views
        self.details_tabs = QTabWidget()
        panel_layout.addWidget(self.details_tabs)
        
        # Overview tab
        self.setup_overview_tab()
        
        # Example details tab
        self.setup_details_tab()
        
        # Source code tab
        self.setup_source_tab()
        
        # Output log tab
        self.setup_output_tab()
        
        parent.addWidget(panel_widget)
        
    def setup_overview_tab(self):
        """Setup overview tab."""
        tab_widget = QScrollArea()
        tab_widget.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Welcome section
        welcome_group = QGroupBox("Welcome to Simple Fluent Widget Examples")
        welcome_layout = QVBoxLayout(welcome_group)
        
        welcome_text = QLabel("""
        <h2>Component Examples Collection</h2>
        <p>This collection demonstrates all available components in the simple-fluent-widget library. 
        Each example showcases comprehensive usage, best practices, and integration patterns.</p>
        
        <h3>Available Categories:</h3>
        <ul>
            <li><b>Layout Components:</b> Dock panels, stack panels, grids, containers</li>
            <li><b>Basic Components:</b> Forms, display elements, navigation, visual components</li>
            <li><b>Data Components:</b> Input widgets, data display, charts, visualization</li>
            <li><b>Composite Components:</b> Complex forms, navigation systems, settings panels</li>
            <li><b>Dialog Components:</b> Message dialogs, form dialogs, progress dialogs</li>
            <li><b>Media Components:</b> Audio, video, image viewers and players</li>
            <li><b>Interface Components:</b> Menus, toolbars, command interfaces</li>
        </ul>
        
        <h3>How to Use:</h3>
        <ol>
            <li>Browse the examples tree on the left</li>
            <li>Select an example to view its details</li>
            <li>Click "Run Selected Example" to launch it</li>
            <li>View source code to understand implementation</li>
            <li>Check the output log for any messages</li>
        </ol>
        
        <p><i>Note: Some examples may require additional dependencies or have fallback implementations 
        when Fluent components are not available.</i></p>
        """)
        welcome_text.setWordWrap(True)
        welcome_layout.addWidget(welcome_text)
        
        content_layout.addWidget(welcome_group)
        
        # Statistics section
        stats_group = QGroupBox("Example Statistics")
        stats_layout = QGridLayout(stats_group)
        
        total_examples = sum(len(examples) for examples in self.examples.values())
        
        stats_data = [
            ("Total Examples", str(total_examples)),
            ("Categories", str(len(self.examples))),
            ("Layout Examples", str(len(self.examples.get("Layout", [])))),
            ("Basic Examples", str(len(self.examples.get("Basic", [])))),
            ("Data Examples", str(len(self.examples.get("Data", [])))),
            ("Composite Examples", str(len(self.examples.get("Composite", [])))),
        ]
        
        for i, (label, value) in enumerate(stats_data):
            stats_layout.addWidget(QLabel(f"{label}:"), i // 2, (i % 2) * 2)
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            stats_layout.addWidget(value_label, i // 2, (i % 2) * 2 + 1)
            
        content_layout.addWidget(stats_group)
        
        # Quick start section
        quickstart_group = QGroupBox("Quick Start Guide")
        quickstart_layout = QVBoxLayout(quickstart_group)
        
        quickstart_text = QLabel("""
        <h3>Getting Started</h3>
        <p>New to Simple Fluent Widget? Try these examples first:</p>
        <ul>
            <li><b>Layout → Dock Panel Demo:</b> Learn about flexible layout management</li>
            <li><b>Basic → Forms Demo:</b> Understand form creation and validation</li>
            <li><b>Data → Input Demo:</b> Explore data input components</li>
            <li><b>Data → Charts Demo:</b> See data visualization capabilities</li>
            <li><b>Composite → Composite Demo:</b> Experience integrated workflows</li>
        </ul>
        
        <h3>Advanced Features</h3>
        <p>Once familiar with basics, explore these advanced topics:</p>
        <ul>
            <li>Custom styling and theming</li>
            <li>Animation and micro-interactions</li>
            <li>Data binding and validation</li>
            <li>Performance optimization</li>
            <li>Accessibility features</li>
        </ul>
        """)
        quickstart_text.setWordWrap(True)
        quickstart_layout.addWidget(quickstart_text)
        
        content_layout.addWidget(quickstart_group)
        content_layout.addStretch()
        
        tab_widget.setWidget(content_widget)
        self.details_tabs.addTab(tab_widget, "Overview")
        
    def setup_details_tab(self):
        """Setup example details tab."""
        self.details_widget = QWidget()
        details_layout = QVBoxLayout(self.details_widget)
        
        # Example info
        self.example_title = QLabel("Select an example to view details")
        self.example_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        details_layout.addWidget(self.example_title)
        
        self.example_description = QTextEdit()
        self.example_description.setReadOnly(True)
        self.example_description.setMaximumHeight(200)
        details_layout.addWidget(self.example_description)
        
        # Example metadata
        metadata_group = QGroupBox("Example Information")
        metadata_layout = QGridLayout(metadata_group)
        
        metadata_layout.addWidget(QLabel("File Path:"), 0, 0)
        self.file_path_label = QLabel("N/A")
        self.file_path_label.setWordWrap(True)
        metadata_layout.addWidget(self.file_path_label, 0, 1)
        
        metadata_layout.addWidget(QLabel("File Size:"), 1, 0)
        self.file_size_label = QLabel("N/A")
        metadata_layout.addWidget(self.file_size_label, 1, 1)
        
        metadata_layout.addWidget(QLabel("Last Modified:"), 2, 0)
        self.modified_label = QLabel("N/A")
        metadata_layout.addWidget(self.modified_label, 2, 1)
        
        metadata_layout.addWidget(QLabel("Components Used:"), 3, 0)
        self.components_label = QLabel("N/A")
        self.components_label.setWordWrap(True)
        metadata_layout.addWidget(self.components_label, 3, 1)
        
        details_layout.addWidget(metadata_group)
        
        # Run controls
        controls_group = QGroupBox("Run Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        self.detailed_run_btn = QPushButton("Run This Example")
        self.detailed_run_btn.clicked.connect(self.run_selected_example)
        self.detailed_run_btn.setEnabled(False)
        controls_layout.addWidget(self.detailed_run_btn)
        
        self.open_folder_btn = QPushButton("Open in File Explorer")
        self.open_folder_btn.clicked.connect(self.open_example_folder)
        self.open_folder_btn.setEnabled(False)
        controls_layout.addWidget(self.open_folder_btn)
        
        details_layout.addWidget(controls_group)
        details_layout.addStretch()
        
        self.details_tabs.addTab(self.details_widget, "Example Details")
        
    def setup_source_tab(self):
        """Setup source code view tab."""
        self.source_widget = QWidget()
        source_layout = QVBoxLayout(self.source_widget)
        
        # Source controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Source Code:"))
        controls_layout.addStretch()
        
        self.copy_code_btn = QPushButton("Copy to Clipboard")
        self.copy_code_btn.clicked.connect(self.copy_source_code)
        self.copy_code_btn.setEnabled(False)
        controls_layout.addWidget(self.copy_code_btn)
        
        self.open_editor_btn = QPushButton("Open in Editor")
        self.open_editor_btn.clicked.connect(self.open_in_editor)
        self.open_editor_btn.setEnabled(False)
        controls_layout.addWidget(self.open_editor_btn)
        
        source_layout.addLayout(controls_layout)
        
        # Source code display
        self.source_code = QTextEdit()
        self.source_code.setReadOnly(True)
        self.source_code.setFont(QFont("Consolas", 10))
        self.source_code.setPlainText("Select an example to view its source code...")
        source_layout.addWidget(self.source_code)
        
        self.details_tabs.addTab(self.source_widget, "Source Code")
        
    def setup_output_tab(self):
        """Setup output log tab."""
        self.output_widget = QWidget()
        output_layout = QVBoxLayout(self.output_widget)
        
        # Output controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Output Log:"))
        controls_layout.addStretch()
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.clear_output_log)
        controls_layout.addWidget(clear_log_btn)
        
        output_layout.addLayout(controls_layout)
        
        # Output display
        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        self.output_log.setFont(QFont("Consolas", 9))
        self.output_log.setMaximumHeight(300)
        output_layout.addWidget(self.output_log)
        
        # Running processes
        processes_group = QGroupBox("Running Processes")
        processes_layout = QVBoxLayout(processes_group)
        
        self.processes_list = QListWidget()
        processes_layout.addWidget(self.processes_list)
        
        kill_process_btn = QPushButton("Stop Selected Process")
        kill_process_btn.clicked.connect(self.stop_selected_process)
        processes_layout.addWidget(kill_process_btn)
        
        output_layout.addWidget(processes_group)
        
        self.details_tabs.addTab(self.output_widget, "Output Log")
        
    def setup_status_bar(self):
        """Setup status bar."""
        status_bar = self.statusBar()
        
        self.status_label = QLabel("Ready - Select an example to get started")
        status_bar.addWidget(self.status_label)
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        status_bar.addPermanentWidget(self.progress_bar)
        
        # Time display
        self.time_label = QLabel()
        self.update_time()
        status_bar.addPermanentWidget(self.time_label)
        
        # Timer for time updates
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(60000)  # Update every minute
        
    def discover_examples(self):
        """Discover all example files in the project."""
        examples = {
            "Layout": [],
            "Basic": [],
            "Data": [],
            "Composite": [],
            "Dialogs": [],
            "Media": [],
            "Interface": [],
            "Utilities": []
        }
        
        examples_dir = project_root / "examples"
        
        if not examples_dir.exists():
            return examples
            
        # Discover layout examples
        layout_dir = examples_dir / "layout"
        if layout_dir.exists():
            for file_path in layout_dir.glob("*.py"):
                if file_path.name != "__init__.py":
                    examples["Layout"].append(file_path)
                    
        # Discover basic examples
        basic_dir = examples_dir / "basic"
        if basic_dir.exists():
            for subdir in basic_dir.iterdir():
                if subdir.is_dir():
                    for file_path in subdir.glob("*.py"):
                        if file_path.name != "__init__.py":
                            examples["Basic"].append(file_path)
                            
        # Discover data examples
        data_dir = examples_dir / "data"
        if data_dir.exists():
            for subdir in data_dir.iterdir():
                if subdir.is_dir():
                    for file_path in subdir.glob("*.py"):
                        if file_path.name != "__init__.py":
                            examples["Data"].append(file_path)
                            
        # Discover composite examples
        composite_dir = examples_dir / "composite"
        if composite_dir.exists():
            for file_path in composite_dir.glob("*.py"):
                if file_path.name != "__init__.py":
                    examples["Composite"].append(file_path)
                    
        return examples
        
    def populate_examples_tree(self):
        """Populate the examples tree widget."""
        self.examples_tree.clear()
        
        for category, example_files in self.examples.items():
            if not example_files:
                continue
                
            category_item = QTreeWidgetItem(self.examples_tree, [category, f"({len(example_files)})"])
            category_item.setExpanded(True)
            
            for file_path in example_files:
                example_name = file_path.stem.replace("_", " ").title()
                example_item = QTreeWidgetItem(category_item, [example_name, "Ready"])
                example_item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                
    def on_example_selected(self, item, column):
        """Handle example selection."""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        
        if file_path and isinstance(file_path, Path):
            self.current_example = file_path
            self.update_example_details(file_path)
            self.load_source_code(file_path)
            
            # Enable buttons
            self.run_btn.setEnabled(True)
            self.view_code_btn.setEnabled(True)
            self.detailed_run_btn.setEnabled(True)
            self.open_folder_btn.setEnabled(True)
            self.copy_code_btn.setEnabled(True)
            self.open_editor_btn.setEnabled(True)
            
            self.status_label.setText(f"Selected: {file_path.name}")
        else:
            # Category selected
            self.run_btn.setEnabled(False)
            self.view_code_btn.setEnabled(False)
            self.detailed_run_btn.setEnabled(False)
            
    def update_example_details(self, file_path):
        """Update example details panel."""
        self.example_title.setText(file_path.stem.replace("_", " ").title())
        
        # Read file for description
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract docstring
            lines = content.split('\\n')
            in_docstring = False
            description_lines = []
            
            for line in lines:
                if '"""' in line and not in_docstring:
                    in_docstring = True
                    if line.count('"""') == 2:  # Single line docstring
                        description_lines.append(line.replace('"""', '').strip())
                        break
                    else:
                        description_lines.append(line.split('"""')[1])
                elif '"""' in line and in_docstring:
                    description_lines.append(line.split('"""')[0])
                    break
                elif in_docstring:
                    description_lines.append(line)
                    
            description = '\\n'.join(description_lines).strip()
            if not description:
                description = "No description available."
                
            self.example_description.setPlainText(description)
            
        except Exception as e:
            self.example_description.setPlainText(f"Error reading file: {e}")
            
        # Update metadata
        self.file_path_label.setText(str(file_path))
        
        try:
            stat = file_path.stat()
            self.file_size_label.setText(f"{stat.st_size:,} bytes")
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            self.modified_label.setText(modified_time.strftime("%Y-%m-%d %H:%M:%S"))
        except Exception:
            self.file_size_label.setText("Unknown")
            self.modified_label.setText("Unknown")
            
        # Extract component imports (simplified)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            import_lines = [line.strip() for line in content.split('\\n') 
                          if line.strip().startswith('from components.') or 
                             line.strip().startswith('import components.')]
                             
            if import_lines:
                components = "\\n".join(import_lines[:5])  # Show first 5 imports
                if len(import_lines) > 5:
                    components += f"\\n... and {len(import_lines) - 5} more"
            else:
                components = "No specific component imports found"
                
            self.components_label.setText(components)
            
        except Exception:
            self.components_label.setText("Unknown")
            
    def load_source_code(self, file_path):
        """Load source code into the viewer."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.source_code.setPlainText(content)
        except Exception as e:
            self.source_code.setPlainText(f"Error loading source code: {e}")
            
    def run_selected_example(self):
        """Run the selected example."""
        if not hasattr(self, 'current_example'):
            QMessageBox.warning(self, "No Selection", "Please select an example to run.")
            return
            
        self.run_example(self.current_example)
        
    def run_example(self, file_path):
        """Run a specific example."""
        try:
            # Start the example in a new process
            process = QProcess()
            process.start(sys.executable, [str(file_path)])
            
            if process.waitForStarted():
                self.running_processes[file_path.name] = process
                
                # Add to processes list
                list_item = QListWidgetItem(f"{file_path.name} (PID: {process.processId()})")
                list_item.setData(Qt.ItemDataRole.UserRole, file_path.name)
                self.processes_list.addItem(list_item)
                
                # Log output
                self.log_output(f"Started: {file_path.name}")
                self.status_label.setText(f"Running: {file_path.name}")
                
                # Update tree item status
                self.update_tree_item_status(file_path.name, "Running")
                
            else:
                self.log_output(f"Failed to start: {file_path.name}")
                QMessageBox.warning(self, "Run Error", f"Failed to start: {file_path.name}")
                
        except Exception as e:
            self.log_output(f"Error running {file_path.name}: {str(e)}")
            QMessageBox.critical(self, "Run Error", f"Error running {file_path.name}:\\n{str(e)}")
            
    def run_all_examples(self):
        """Run all available examples."""
        reply = QMessageBox.question(self, "Run All Examples", 
                                   "This will start all available examples. Continue?")
        if reply == QMessageBox.StandardButton.Yes:
            total_examples = sum(len(examples) for examples in self.examples.values())
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, total_examples)
            
            count = 0
            for category, example_files in self.examples.items():
                for file_path in example_files:
                    self.run_example(file_path)
                    count += 1
                    self.progress_bar.setValue(count)
                    QApplication.processEvents()
                    
            self.progress_bar.setVisible(False)
            self.log_output(f"Started {count} examples")
            
    def view_source_code(self):
        """Switch to source code tab."""
        self.details_tabs.setCurrentIndex(2)  # Source code tab
        
    def copy_source_code(self):
        """Copy source code to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.source_code.toPlainText())
        self.status_label.setText("Source code copied to clipboard")
        
    def open_in_editor(self):
        """Open example in default editor."""
        if hasattr(self, 'current_example'):
            os.startfile(str(self.current_example))
            
    def open_example_folder(self):
        """Open example folder in file explorer."""
        if hasattr(self, 'current_example'):
            folder_path = self.current_example.parent
            os.startfile(str(folder_path))
            
    def stop_selected_process(self):
        """Stop selected running process."""
        current_item = self.processes_list.currentItem()
        if current_item:
            process_name = current_item.data(Qt.ItemDataRole.UserRole)
            if process_name in self.running_processes:
                process = self.running_processes[process_name]
                process.terminate()
                del self.running_processes[process_name]
                
                # Remove from list
                row = self.processes_list.row(current_item)
                self.processes_list.takeItem(row)
                
                self.log_output(f"Stopped: {process_name}")
                self.update_tree_item_status(process_name, "Stopped")
                
    def update_tree_item_status(self, filename, status):
        """Update tree item status."""
        # Find and update the tree item
        for i in range(self.examples_tree.topLevelItemCount()):
            category_item = self.examples_tree.topLevelItem(i)
            for j in range(category_item.childCount()):
                example_item = category_item.child(j)
                file_path = example_item.data(0, Qt.ItemDataRole.UserRole)
                if file_path and file_path.name == filename:
                    example_item.setText(1, status)
                    break
                    
    def log_output(self, message):
        """Log message to output."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_log.append(f"[{timestamp}] {message}")
        
    def clear_output_log(self):
        """Clear output log."""
        self.output_log.clear()
        
    def update_time(self):
        """Update time display."""
        current_time = datetime.now().strftime("%H:%M")
        self.time_label.setText(current_time)


def main():
    """Main function to run the examples index."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Simple Fluent Widget Examples")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Simple Fluent Widget")
    
    # Create and show the index
    index = ComponentExamplesIndex()
    index.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
