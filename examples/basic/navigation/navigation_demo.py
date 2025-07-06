#!/usr/bin/env python3
"""
Fluent Navigation Components Demo

This example demonstrates the comprehensive usage of Fluent navigation components including
tabs, accordion, pagination, breadcrumbs, and timeline components.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QGroupBox, QPushButton, QFrame, QTabWidget, QScrollArea,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QStackedWidget, QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon


def main():
    """Run the navigation components demo application."""
    app = QApplication(sys.argv)
    
    # Import after QApplication is created
    try:
        from components.basic.navigation.tabs import FluentTabWidget, FluentTabBar
        from components.basic.navigation.accordion import FluentAccordion, FluentAccordionItem
        from components.basic.navigation.pagination import FluentPagination
        from components.basic.navigation.divider import FluentDivider
        from components.basic.navigation.stepper import FluentStepper, StepState
        from components.basic.navigation.timeline import FluentTimeline, TimelineItem
        from components.basic.navigation.segmented import FluentSegmentedControl
        COMPONENTS_AVAILABLE = True
    except ImportError as e:
        print(f"Import error: {e}")
        print("Some navigation components may not be available yet")
        COMPONENTS_AVAILABLE = False
    
    class NavigationDemo(QMainWindow):
        """Main demo window showcasing Fluent navigation components."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Fluent Navigation Components Demo")
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
            title = QLabel("Fluent Navigation Components Demo")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
            main_layout.addWidget(title)
            
            # Create component sections
            self.create_tabs_section(main_layout)
            self.create_accordion_section(main_layout)
            self.create_stepper_section(main_layout)
            self.create_pagination_section(main_layout)
            self.create_breadcrumb_section(main_layout)
            self.create_timeline_section(main_layout)
            self.create_segmented_section(main_layout)
            
        def create_tabs_section(self, parent_layout):
            """Create tabs components section."""
            group = QGroupBox("Tab Navigation")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Tab widget example
            if COMPONENTS_AVAILABLE:
                tab_widget = FluentTabWidget()
            else:
                tab_widget = QTabWidget()
                tab_widget.setStyleSheet("""
                    QTabWidget::pane {
                        border: 1px solid #c8c6c4;
                        border-radius: 4px;
                        background-color: white;
                    }
                    QTabBar::tab {
                        background-color: #f3f2f1;
                        border: 1px solid #c8c6c4;
                        padding: 8px 16px;
                        margin-right: 2px;
                        border-top-left-radius: 4px;
                        border-top-right-radius: 4px;
                    }
                    QTabBar::tab:selected {
                        background-color: white;
                        border-bottom-color: white;
                    }
                    QTabBar::tab:hover {
                        background-color: #edebe9;
                    }
                """)
            
            # Add tabs with content
            tab_contents = [
                ("Home", "🏠 Welcome to the home tab. This is the main dashboard with overview information."),
                ("Profile", "👤 User profile settings and personal information can be managed here."),
                ("Settings", "⚙️ Application settings and preferences configuration panel."),
                ("Help", "❓ Help documentation and support resources for users."),
                ("About", "ℹ️ Information about the application, version, and development team.")
            ]
            
            for title, content in tab_contents:
                tab_content = QWidget()
                tab_layout = QVBoxLayout(tab_content)
                
                content_label = QLabel(content)
                content_label.setWordWrap(True)
                content_label.setStyleSheet("padding: 20px; font-size: 14px; color: #323130;")
                
                # Add some interactive elements
                if title == "Settings":
                    settings_frame = QFrame()
                    settings_layout = QVBoxLayout(settings_frame)
                    
                    from PySide6.QtWidgets import QCheckBox, QComboBox
                    
                    settings_layout.addWidget(QCheckBox("Enable notifications"))
                    settings_layout.addWidget(QCheckBox("Auto-save changes"))
                    settings_layout.addWidget(QCheckBox("Dark mode"))
                    
                    theme_combo = QComboBox()
                    theme_combo.addItems(["System Default", "Light", "Dark", "High Contrast"])
                    settings_layout.addWidget(QLabel("Theme:"))
                    settings_layout.addWidget(theme_combo)
                    
                    tab_layout.addWidget(content_label)
                    tab_layout.addWidget(settings_frame)
                else:
                    tab_layout.addWidget(content_label)
                
                tab_layout.addStretch()
                tab_widget.addTab(tab_content, title)
            
            layout.addWidget(tab_widget)
            
            # Tab examples
            examples_label = QLabel("""
<b>Tab Navigation Features:</b><br>
• <b>Multiple Views:</b> Organize content into logical sections<br>
• <b>State Management:</b> Maintain state across tab switches<br>
• <b>Keyboard Navigation:</b> Arrow keys and tab navigation<br>
• <b>Closable Tabs:</b> Dynamic tab addition and removal<br><br>

<b>Best Practices:</b><br>
• Keep tab labels short and descriptive<br>
• Use consistent content layout across tabs<br>
• Indicate active tab clearly<br>
• Consider responsive behavior for mobile
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_accordion_section(self, parent_layout):
            """Create accordion components section."""
            group = QGroupBox("Accordion Navigation")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Create accordion-like structure using groupboxes
            accordion_items = [
                ("🎨 Design Guidelines", [
                    "• Use consistent spacing and typography",
                    "• Follow Fluent Design principles",
                    "• Maintain visual hierarchy",
                    "• Ensure accessibility compliance"
                ]),
                ("🛠️ Development Setup", [
                    "• Install Python 3.11 or higher",
                    "• Set up virtual environment",
                    "• Install PySide6 dependencies",
                    "• Configure development tools"
                ]),
                ("📚 Component Library", [
                    "• Basic components (buttons, inputs)",
                    "• Layout components (containers, grids)",
                    "• Navigation components (tabs, menus)",
                    "• Data components (tables, charts)"
                ]),
                ("🧪 Testing & Quality", [
                    "• Unit testing with pytest",
                    "• Integration testing",
                    "• Code quality with linting",
                    "• Performance benchmarking"
                ])
            ]
            
            self.accordion_sections = []
            
            for title, items in accordion_items:
                section_frame = QFrame()
                section_frame.setStyleSheet("""
                    QFrame {
                        border: 1px solid #edebe9;
                        border-radius: 4px;
                        background-color: white;
                        margin: 2px 0;
                    }
                """)
                section_layout = QVBoxLayout(section_frame)
                section_layout.setContentsMargins(0, 0, 0, 0)
                
                # Header button
                header_btn = QPushButton(title)
                header_btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 12px 16px;
                        border: none;
                        background-color: #f8f8f8;
                        font-weight: 600;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #edebe9;
                    }
                """)
                
                # Content area
                content_widget = QWidget()
                content_layout = QVBoxLayout(content_widget)
                content_layout.setContentsMargins(16, 8, 16, 16)
                
                for item in items:
                    item_label = QLabel(item)
                    item_label.setStyleSheet("color: #605e5c; padding: 2px 0;")
                    content_layout.addWidget(item_label)
                
                # Initially hide content
                content_widget.hide()
                
                # Connect toggle functionality
                header_btn.clicked.connect(
                    lambda checked, content=content_widget: content.setVisible(not content.isVisible())
                )
                
                section_layout.addWidget(header_btn)
                section_layout.addWidget(content_widget)
                
                layout.addWidget(section_frame)
                self.accordion_sections.append(content_widget)
            
            # Accordion controls
            controls_layout = QHBoxLayout()
            
            expand_all_btn = QPushButton("Expand All")
            expand_all_btn.clicked.connect(self.expand_all_accordion)
            expand_all_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
            """)
            
            collapse_all_btn = QPushButton("Collapse All")
            collapse_all_btn.clicked.connect(self.collapse_all_accordion)
            collapse_all_btn.setStyleSheet("""
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
            
            controls_layout.addWidget(expand_all_btn)
            controls_layout.addWidget(collapse_all_btn)
            controls_layout.addStretch()
            
            layout.addLayout(controls_layout)
            
            # Accordion examples
            examples_label = QLabel("""
<b>Accordion Features:</b><br>
• <b>Space Efficient:</b> Show/hide content sections on demand<br>
• <b>Hierarchical:</b> Organize related content in collapsible sections<br>
• <b>Progressive Disclosure:</b> Reveal information incrementally<br>
• <b>Keyboard Accessible:</b> Full keyboard navigation support<br><br>

<b>Use Cases:</b><br>
• FAQ sections and help documentation<br>
• Settings panels with grouped options<br>
• Navigation menus with sub-items<br>
• Form sections with optional fields
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_stepper_section(self, parent_layout):
            """Create stepper components section."""
            group = QGroupBox("Step Navigation")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Stepper example
            stepper_frame = QFrame()
            stepper_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #edebe9;
                    border-radius: 8px;
                    padding: 20px;
                }
            """)
            stepper_layout = QVBoxLayout(stepper_frame)
            
            # Create visual stepper
            steps = [
                ("Account", "Create your account", "completed"),
                ("Profile", "Set up your profile", "completed"),
                ("Preferences", "Configure preferences", "current"),
                ("Verification", "Verify your email", "pending"),
                ("Complete", "Setup complete", "pending")
            ]
            
            # Stepper visualization
            stepper_visual = QHBoxLayout()
            
            for i, (title, description, state) in enumerate(steps):
                # Step item
                step_item = QVBoxLayout()
                
                # Step circle
                circle = QLabel(str(i + 1))
                circle.setFixedSize(32, 32)
                circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # State-based styling
                if state == "completed":
                    circle.setStyleSheet("""
                        QLabel {
                            background-color: #107c10;
                            color: white;
                            border-radius: 16px;
                            font-weight: bold;
                        }
                    """)
                    circle.setText("✓")
                elif state == "current":
                    circle.setStyleSheet("""
                        QLabel {
                            background-color: #0078d4;
                            color: white;
                            border-radius: 16px;
                            font-weight: bold;
                        }
                    """)
                else:  # pending
                    circle.setStyleSheet("""
                        QLabel {
                            background-color: #f3f2f1;
                            color: #605e5c;
                            border: 2px solid #c8c6c4;
                            border-radius: 16px;
                            font-weight: bold;
                        }
                    """)
                
                # Step labels
                title_label = QLabel(title)
                title_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #323130;")
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                desc_label = QLabel(description)
                desc_label.setStyleSheet("font-size: 11px; color: #605e5c;")
                desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                desc_label.setWordWrap(True)
                
                step_item.addWidget(circle, alignment=Qt.AlignmentFlag.AlignCenter)
                step_item.addWidget(title_label)
                step_item.addWidget(desc_label)
                
                stepper_visual.addLayout(step_item)
                
                # Add connector line (except for last item)
                if i < len(steps) - 1:
                    connector = QFrame()
                    connector.setFixedSize(40, 2)
                    if state == "completed":
                        connector.setStyleSheet("background-color: #107c10;")
                    else:
                        connector.setStyleSheet("background-color: #c8c6c4;")
                    
                    connector_layout = QVBoxLayout()
                    connector_layout.addStretch()
                    connector_layout.addWidget(connector)
                    connector_layout.addStretch()
                    stepper_visual.addLayout(connector_layout)
            
            stepper_layout.addLayout(stepper_visual)
            
            # Stepper controls
            stepper_controls = QHBoxLayout()
            
            prev_btn = QPushButton("← Previous")
            prev_btn.setStyleSheet("""
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
            
            next_btn = QPushButton("Next →")
            next_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
            """)
            
            stepper_controls.addWidget(prev_btn)
            stepper_controls.addStretch()
            stepper_controls.addWidget(next_btn)
            
            stepper_layout.addLayout(stepper_controls)
            
            layout.addWidget(stepper_frame)
            
            # Stepper examples
            examples_label = QLabel("""
<b>Stepper Navigation:</b><br>
• <b>Sequential Process:</b> Guide users through multi-step workflows<br>
• <b>Progress Indication:</b> Show current position and completion status<br>
• <b>State Management:</b> Track completed, current, and pending steps<br>
• <b>Navigation Control:</b> Allow forward/backward movement<br><br>

<b>Common Applications:</b><br>
• Setup wizards and onboarding flows<br>
• Multi-step forms and checkout processes<br>
• Tutorial and guided tours<br>
• Data collection workflows
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_pagination_section(self, parent_layout):
            """Create pagination components section."""
            group = QGroupBox("Pagination Navigation")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Sample data to paginate
            self.sample_data = [f"Item {i+1}" for i in range(87)]  # 87 items
            self.items_per_page = 10
            self.current_page = 1
            
            # Data display area
            data_frame = QFrame()
            data_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #edebe9;
                    border-radius: 4px;
                    padding: 15px;
                }
            """)
            data_layout = QVBoxLayout(data_frame)
            
            # List widget to show current page data
            self.data_list = QListWidget()
            self.data_list.setStyleSheet("""
                QListWidget {
                    border: none;
                    background-color: transparent;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #f3f2f1;
                }
                QListWidget::item:hover {
                    background-color: #f8f8f8;
                }
            """)
            
            data_layout.addWidget(self.data_list)
            layout.addWidget(data_frame)
            
            # Pagination controls
            pagination_frame = QFrame()
            pagination_layout = QHBoxLayout(pagination_frame)
            
            # Previous button
            self.prev_btn = QPushButton("← Previous")
            self.prev_btn.clicked.connect(self.go_to_previous_page)
            self.prev_btn.setStyleSheet("""
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
                QPushButton:disabled {
                    background-color: #f8f8f8;
                    color: #c8c6c4;
                    border-color: #e5e5e5;
                }
            """)
            
            # Page numbers
            self.page_buttons = []
            self.page_layout = QHBoxLayout()
            
            # Next button
            self.next_btn = QPushButton("Next →")
            self.next_btn.clicked.connect(self.go_to_next_page)
            self.next_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:disabled {
                    background-color: #c8c6c4;
                }
            """)
            
            # Info label
            self.page_info = QLabel()
            self.page_info.setStyleSheet("color: #605e5c; font-size: 12px;")
            
            pagination_layout.addWidget(self.prev_btn)
            pagination_layout.addLayout(self.page_layout)
            pagination_layout.addWidget(self.next_btn)
            pagination_layout.addStretch()
            pagination_layout.addWidget(self.page_info)
            
            layout.addWidget(pagination_frame)
            
            # Initialize pagination
            self.update_pagination()
            
            # Pagination examples
            examples_label = QLabel("""
<b>Pagination Features:</b><br>
• <b>Large Dataset Navigation:</b> Break large datasets into manageable pages<br>
• <b>Performance Optimization:</b> Load only visible items<br>
• <b>User Control:</b> Allow users to navigate at their own pace<br>
• <b>State Persistence:</b> Remember current page and position<br><br>

<b>Best Practices:</b><br>
• Show total items and current page info<br>
• Provide multiple navigation options<br>
• Consider infinite scroll for mobile<br>
• Maintain consistent page sizes
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_breadcrumb_section(self, parent_layout):
            """Create breadcrumb navigation section."""
            group = QGroupBox("Breadcrumb Navigation")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Breadcrumb examples
            breadcrumb_examples = [
                ["Home"],
                ["Home", "Products"],
                ["Home", "Products", "Electronics"],
                ["Home", "Products", "Electronics", "Computers"],
                ["Home", "Products", "Electronics", "Computers", "Laptops"]
            ]
            
            for i, breadcrumb in enumerate(breadcrumb_examples):
                breadcrumb_frame = QFrame()
                breadcrumb_frame.setStyleSheet("""
                    QFrame {
                        background-color: #f8f8f8;
                        border: 1px solid #edebe9;
                        border-radius: 4px;
                        padding: 8px 12px;
                        margin: 2px 0;
                    }
                """)
                breadcrumb_layout = QHBoxLayout(breadcrumb_frame)
                breadcrumb_layout.setContentsMargins(0, 0, 0, 0)
                
                for j, item in enumerate(breadcrumb):
                    # Breadcrumb item
                    if j == len(breadcrumb) - 1:  # Last item (current page)
                        item_label = QLabel(item)
                        item_label.setStyleSheet("""
                            QLabel {
                                color: #323130;
                                font-weight: 600;
                                padding: 4px 8px;
                            }
                        """)
                    else:  # Clickable items
                        item_label = QPushButton(item)
                        item_label.setStyleSheet("""
                            QPushButton {
                                color: #0078d4;
                                background-color: transparent;
                                border: none;
                                text-align: left;
                                padding: 4px 8px;
                                text-decoration: underline;
                            }
                            QPushButton:hover {
                                color: #106ebe;
                                background-color: rgba(0, 120, 212, 0.1);
                                border-radius: 2px;
                            }
                        """)
                        item_label.clicked.connect(
                            lambda checked, level=j: self.navigate_to_breadcrumb(level)
                        )
                    
                    breadcrumb_layout.addWidget(item_label)
                    
                    # Add separator (except for last item)
                    if j < len(breadcrumb) - 1:
                        separator = QLabel("›")
                        separator.setStyleSheet("color: #8a8886; padding: 0 4px;")
                        breadcrumb_layout.addWidget(separator)
                
                breadcrumb_layout.addStretch()
                layout.addWidget(breadcrumb_frame)
            
            # Breadcrumb examples
            examples_label = QLabel("""
<b>Breadcrumb Navigation:</b><br>
• <b>Location Awareness:</b> Show user's current position in hierarchy<br>
• <b>Quick Navigation:</b> Allow jumping to any parent level<br>
• <b>Space Efficient:</b> Compact representation of navigation path<br>
• <b>SEO Friendly:</b> Helps with search engine optimization<br><br>

<b>Implementation Tips:</b><br>
• Make parent levels clickable<br>
• Use appropriate separators (›, /, →)<br>
• Keep hierarchy logical and consistent<br>
• Consider mobile responsiveness
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_timeline_section(self, parent_layout):
            """Create timeline components section."""
            group = QGroupBox("Timeline Navigation")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Timeline example
            timeline_frame = QFrame()
            timeline_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #edebe9;
                    border-radius: 8px;
                    padding: 20px;
                }
            """)
            timeline_layout = QVBoxLayout(timeline_frame)
            
            # Timeline items
            timeline_items = [
                ("2024-01-15", "Project Kickoff", "Project officially started with team meeting", "success"),
                ("2024-02-01", "Design Phase", "UI/UX design and component architecture", "success"),
                ("2024-02-15", "Development Start", "Core component development began", "success"),
                ("2024-03-01", "Alpha Release", "First alpha version released for testing", "warning"),
                ("2024-03-15", "Beta Testing", "Comprehensive testing and bug fixes", "info"),
                ("2024-04-01", "Final Release", "Production-ready version deployment", "pending")
            ]
            
            for i, (date, title, description, status) in enumerate(timeline_items):
                item_layout = QHBoxLayout()
                
                # Timeline line and dot
                timeline_visual = QVBoxLayout()
                timeline_visual.setSpacing(0)
                
                # Top line (except for first item)
                if i > 0:
                    top_line = QFrame()
                    top_line.setFixedSize(2, 20)
                    top_line.setStyleSheet("background-color: #c8c6c4;")
                    timeline_visual.addWidget(top_line, alignment=Qt.AlignmentFlag.AlignHCenter)
                
                # Dot
                dot = QFrame()
                dot.setFixedSize(12, 12)
                
                # Status-based styling
                if status == "success":
                    dot.setStyleSheet("background-color: #107c10; border-radius: 6px;")
                elif status == "warning":
                    dot.setStyleSheet("background-color: #ff8c00; border-radius: 6px;")
                elif status == "info":
                    dot.setStyleSheet("background-color: #0078d4; border-radius: 6px;")
                else:  # pending
                    dot.setStyleSheet("background-color: #c8c6c4; border-radius: 6px;")
                
                timeline_visual.addWidget(dot, alignment=Qt.AlignmentFlag.AlignHCenter)
                
                # Bottom line (except for last item)
                if i < len(timeline_items) - 1:
                    bottom_line = QFrame()
                    bottom_line.setFixedSize(2, 20)
                    bottom_line.setStyleSheet("background-color: #c8c6c4;")
                    timeline_visual.addWidget(bottom_line, alignment=Qt.AlignmentFlag.AlignHCenter)
                
                # Content
                content_layout = QVBoxLayout()
                
                # Date and title
                header_layout = QHBoxLayout()
                date_label = QLabel(date)
                date_label.setStyleSheet("color: #605e5c; font-size: 12px;")
                title_label = QLabel(title)
                title_label.setStyleSheet("font-weight: bold; color: #323130;")
                
                header_layout.addWidget(date_label)
                header_layout.addWidget(title_label)
                header_layout.addStretch()
                
                # Description
                desc_label = QLabel(description)
                desc_label.setStyleSheet("color: #605e5c; font-size: 13px; margin-bottom: 15px;")
                desc_label.setWordWrap(True)
                
                content_layout.addLayout(header_layout)
                content_layout.addWidget(desc_label)
                
                item_layout.addLayout(timeline_visual)
                item_layout.addLayout(content_layout)
                
                timeline_layout.addLayout(item_layout)
            
            layout.addWidget(timeline_frame)
            
            # Timeline examples
            examples_label = QLabel("""
<b>Timeline Features:</b><br>
• <b>Chronological Display:</b> Show events in time order<br>
• <b>Status Indication:</b> Visual cues for different states<br>
• <b>Progressive Disclosure:</b> Expandable details for each item<br>
• <b>Interactive Elements:</b> Clickable items for more information<br><br>

<b>Use Cases:</b><br>
• Project milestones and progress tracking<br>
• Activity feeds and history logs<br>
• Process flows and workflows<br>
• News feeds and social media posts
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_segmented_section(self, parent_layout):
            """Create segmented control section."""
            group = QGroupBox("Segmented Controls")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Segmented control examples
            segments_layout = QVBoxLayout()
            
            # View mode selector
            view_frame = QFrame()
            view_layout = QVBoxLayout(view_frame)
            
            view_label = QLabel("View Mode:")
            view_label.setStyleSheet("font-weight: bold; margin-bottom: 8px;")
            
            view_buttons_layout = QHBoxLayout()
            view_buttons = []
            
            view_options = ["List", "Grid", "Card"]
            for i, option in enumerate(view_options):
                btn = QPushButton(option)
                btn.setCheckable(True)
                if i == 0:  # Select first by default
                    btn.setChecked(True)
                    
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f3f2f1;
                        color: #323130;
                        border: 1px solid #8a8886;
                        padding: 8px 16px;
                        margin: 0;
                    }
                    QPushButton:checked {
                        background-color: #0078d4;
                        color: white;
                        border-color: #0078d4;
                    }
                    QPushButton:hover {
                        background-color: #edebe9;
                    }
                    QPushButton:checked:hover {
                        background-color: #106ebe;
                    }
                """)
                
                # Make mutually exclusive
                btn.clicked.connect(lambda checked, b=btn, buttons=view_buttons: self.select_single_button(b, buttons))
                view_buttons.append(btn)
                view_buttons_layout.addWidget(btn)
            
            # Style the group to look connected
            view_buttons[0].setStyleSheet(view_buttons[0].styleSheet() + "border-top-right-radius: 0; border-bottom-right-radius: 0;")
            view_buttons[1].setStyleSheet(view_buttons[1].styleSheet() + "border-radius: 0; border-left: none;")
            view_buttons[2].setStyleSheet(view_buttons[2].styleSheet() + "border-top-left-radius: 0; border-bottom-left-radius: 0; border-left: none;")
            
            view_buttons_layout.addStretch()
            
            view_layout.addWidget(view_label)
            view_layout.addLayout(view_buttons_layout)
            
            # Filter selector
            filter_frame = QFrame()
            filter_layout = QVBoxLayout(filter_frame)
            
            filter_label = QLabel("Filter:")
            filter_label.setStyleSheet("font-weight: bold; margin-bottom: 8px;")
            
            filter_buttons_layout = QHBoxLayout()
            filter_buttons = []
            
            filter_options = ["All", "Active", "Completed", "Draft"]
            for i, option in enumerate(filter_options):
                btn = QPushButton(option)
                btn.setCheckable(True)
                if i == 0:  # Select first by default
                    btn.setChecked(True)
                    
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f3f2f1;
                        color: #323130;
                        border: 1px solid #8a8886;
                        padding: 6px 12px;
                        margin: 0;
                        font-size: 12px;
                    }
                    QPushButton:checked {
                        background-color: #0078d4;
                        color: white;
                        border-color: #0078d4;
                    }
                    QPushButton:hover {
                        background-color: #edebe9;
                    }
                    QPushButton:checked:hover {
                        background-color: #106ebe;
                    }
                """)
                
                # Style connected buttons
                if i == 0:
                    btn.setStyleSheet(btn.styleSheet() + "border-top-right-radius: 0; border-bottom-right-radius: 0;")
                elif i == len(filter_options) - 1:
                    btn.setStyleSheet(btn.styleSheet() + "border-top-left-radius: 0; border-bottom-left-radius: 0; border-left: none;")
                else:
                    btn.setStyleSheet(btn.styleSheet() + "border-radius: 0; border-left: none;")
                
                # Make mutually exclusive
                btn.clicked.connect(lambda checked, b=btn, buttons=filter_buttons: self.select_single_button(b, buttons))
                filter_buttons.append(btn)
                filter_buttons_layout.addWidget(btn)
            
            filter_buttons_layout.addStretch()
            
            filter_layout.addWidget(filter_label)
            filter_layout.addLayout(filter_buttons_layout)
            
            segments_layout.addWidget(view_frame)
            segments_layout.addWidget(filter_frame)
            
            layout.addLayout(segments_layout)
            
            # Segmented control examples
            examples_label = QLabel("""
<b>Segmented Control Features:</b><br>
• <b>Mutually Exclusive:</b> Only one option can be selected at a time<br>
• <b>Visual Grouping:</b> Connected appearance shows relationship<br>
• <b>Space Efficient:</b> Compact alternative to radio buttons<br>
• <b>Clear Selection:</b> Obvious active state indication<br><br>

<b>Best Practices:</b><br>
• Use for 2-5 related options<br>
• Keep labels short and descriptive<br>
• Ensure one option is always selected<br>
• Consider responsive behavior for mobile
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        # Helper methods
        def expand_all_accordion(self):
            """Expand all accordion sections."""
            for section in self.accordion_sections:
                section.show()
                
        def collapse_all_accordion(self):
            """Collapse all accordion sections."""
            for section in self.accordion_sections:
                section.hide()
                
        def update_pagination(self):
            """Update pagination display."""
            # Calculate pagination
            total_pages = (len(self.sample_data) + self.items_per_page - 1) // self.items_per_page
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = min(start_idx + self.items_per_page, len(self.sample_data))
            
            # Update data list
            self.data_list.clear()
            for i in range(start_idx, end_idx):
                self.data_list.addItem(f"{self.sample_data[i]} (Index: {i+1})")
            
            # Update buttons
            self.prev_btn.setEnabled(self.current_page > 1)
            self.next_btn.setEnabled(self.current_page < total_pages)
            
            # Update page info
            self.page_info.setText(f"Page {self.current_page} of {total_pages} ({len(self.sample_data)} total items)")
            
            # Update page number buttons
            for btn in self.page_buttons:
                btn.deleteLater()
            self.page_buttons.clear()
            
            # Show page numbers (with ellipsis for large page counts)
            start_page = max(1, self.current_page - 2)
            end_page = min(total_pages, self.current_page + 2)
            
            if start_page > 1:
                btn = QPushButton("1")
                btn.clicked.connect(lambda: self.go_to_page(1))
                self.style_page_button(btn, 1 == self.current_page)
                self.page_layout.addWidget(btn)
                self.page_buttons.append(btn)
                
                if start_page > 2:
                    ellipsis = QLabel("...")
                    ellipsis.setStyleSheet("color: #605e5c; padding: 8px 4px;")
                    self.page_layout.addWidget(ellipsis)
            
            for page in range(start_page, end_page + 1):
                btn = QPushButton(str(page))
                btn.clicked.connect(lambda checked, p=page: self.go_to_page(p))
                self.style_page_button(btn, page == self.current_page)
                self.page_layout.addWidget(btn)
                self.page_buttons.append(btn)
            
            if end_page < total_pages:
                if end_page < total_pages - 1:
                    ellipsis = QLabel("...")
                    ellipsis.setStyleSheet("color: #605e5c; padding: 8px 4px;")
                    self.page_layout.addWidget(ellipsis)
                
                btn = QPushButton(str(total_pages))
                btn.clicked.connect(lambda: self.go_to_page(total_pages))
                self.style_page_button(btn, total_pages == self.current_page)
                self.page_layout.addWidget(btn)
                self.page_buttons.append(btn)
                
        def style_page_button(self, btn, is_current):
            """Style a page number button."""
            if is_current:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 10px;
                        font-weight: bold;
                        min-width: 20px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #323130;
                        border: 1px solid #c8c6c4;
                        border-radius: 4px;
                        padding: 6px 10px;
                        min-width: 20px;
                    }
                    QPushButton:hover {
                        background-color: #f8f8f8;
                        border-color: #8a8886;
                    }
                """)
                
        def go_to_page(self, page):
            """Navigate to a specific page."""
            total_pages = (len(self.sample_data) + self.items_per_page - 1) // self.items_per_page
            if 1 <= page <= total_pages:
                self.current_page = page
                self.update_pagination()
                
        def go_to_previous_page(self):
            """Navigate to previous page."""
            if self.current_page > 1:
                self.current_page -= 1
                self.update_pagination()
                
        def go_to_next_page(self):
            """Navigate to next page."""
            total_pages = (len(self.sample_data) + self.items_per_page - 1) // self.items_per_page
            if self.current_page < total_pages:
                self.current_page += 1
                self.update_pagination()
                
        def navigate_to_breadcrumb(self, level):
            """Navigate to a breadcrumb level."""
            print(f"Navigating to breadcrumb level: {level}")
            
        def select_single_button(self, selected_btn, button_group):
            """Make button selection mutually exclusive."""
            for btn in button_group:
                if btn != selected_btn:
                    btn.setChecked(False)
            selected_btn.setChecked(True)
    
    # Create and show demo
    demo = NavigationDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
