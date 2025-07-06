#!/usr/bin/env python3
"""
Fluent Display Components Demo

This example demonstrates the comprehensive usage of Fluent display components including
cards, badges, progress indicators, loading spinners, alerts, and tooltips.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QGroupBox, QPushButton, QFrame, QTabWidget, QScrollArea,
    QProgressBar, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPalette


def main():
    """Run the display components demo application."""
    app = QApplication(sys.argv)
    
    # Import after QApplication is created
    try:
        from components.basic.display.card import FluentCard
        from components.basic.display.badge import FluentBadge, BadgeType
        from components.basic.display.progress import FluentProgressBar, FluentProgressRing
        from components.basic.display.loading import FluentLoadingSpinner, FluentLoadingDots
        from components.basic.display.alert import FluentAlert, AlertType
        from components.basic.display.tooltip import FluentToolTip
        from components.basic.display.chip import FluentChip
        from components.basic.display.label import FluentLabel, LabelType
        COMPONENTS_AVAILABLE = True
    except ImportError as e:
        print(f"Import error: {e}")
        print("Some display components may not be available yet")
        COMPONENTS_AVAILABLE = False
    
    class DisplayDemo(QMainWindow):
        """Main demo window showcasing Fluent display components."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Fluent Display Components Demo")
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
            title = QLabel("Fluent Display Components Demo")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
            main_layout.addWidget(title)
            
            # Create component sections
            self.create_cards_section(main_layout)
            self.create_badges_section(main_layout)
            self.create_progress_section(main_layout)
            self.create_loading_section(main_layout)
            self.create_alerts_section(main_layout)
            self.create_labels_section(main_layout)
            self.create_interactive_demo(main_layout)
            
        def create_cards_section(self, parent_layout):
            """Create card components section."""
            group = QGroupBox("Card Components")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Cards layout
            cards_layout = QHBoxLayout()
            
            # Basic card
            basic_card = self.create_sample_card("Basic Card", 
                "This is a basic card component with clean design and subtle shadow.",
                "#f3f2f1")
            
            # Accent card
            accent_card = self.create_sample_card("Accent Card", 
                "This card uses accent colors to highlight important content.",
                "#e1f5fe", "#0078d4")
            
            # Action card
            action_card = self.create_sample_card("Action Card", 
                "This card includes action buttons and interactive elements.",
                "#f9f9f9")
            
            # Add action button to action card
            action_btn = QPushButton("Take Action")
            action_btn.setStyleSheet("""
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
            action_card.layout().addWidget(action_btn)
            
            cards_layout.addWidget(basic_card)
            cards_layout.addWidget(accent_card)
            cards_layout.addWidget(action_card)
            
            layout.addLayout(cards_layout)
            
            # Card examples
            examples_label = QLabel("""
<b>Card Types & Usage:</b><br>
• <b>Basic Card:</b> General content containers with subtle elevation<br>
• <b>Accent Card:</b> Highlighted cards for important information<br>
• <b>Action Card:</b> Interactive cards with buttons and controls<br><br>

<b>Features:</b><br>
• Consistent elevation and shadows<br>
• Responsive hover effects<br>
• Flexible content layout<br>
• Theme-aware styling
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_badges_section(self, parent_layout):
            """Create badge components section."""
            group = QGroupBox("Badge Components")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Badges layout
            badges_layout = QHBoxLayout()
            
            # Create sample badges
            badges_info = [
                ("New", "#0078d4", "white"),
                ("Hot", "#d13438", "white"),
                ("Sale", "#107c10", "white"),
                ("Beta", "#ff8c00", "white"),
                ("Pro", "#5c2d91", "white"),
                ("99+", "#323130", "white")
            ]
            
            for text, bg_color, text_color in badges_info:
                badge = self.create_sample_badge(text, bg_color, text_color)
                badges_layout.addWidget(badge)
            
            badges_layout.addStretch()
            layout.addLayout(badges_layout)
            
            # Badge with content example
            badge_demo_layout = QHBoxLayout()
            
            # Notification example
            notification_frame = QFrame()
            notification_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #edebe9;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            notification_layout = QVBoxLayout(notification_frame)
            
            notif_header = QHBoxLayout()
            notif_title = QLabel("Messages")
            notif_title.setStyleSheet("font-weight: bold; font-size: 14px;")
            notif_badge = self.create_sample_badge("3", "#d13438", "white")
            notif_badge.setFixedSize(20, 20)
            
            notif_header.addWidget(notif_title)
            notif_header.addWidget(notif_badge)
            notif_header.addStretch()
            
            notification_layout.addLayout(notif_header)
            notification_layout.addWidget(QLabel("You have 3 unread messages"))
            
            badge_demo_layout.addWidget(notification_frame)
            badge_demo_layout.addStretch()
            
            layout.addLayout(badge_demo_layout)
            
            # Badge examples
            examples_label = QLabel("""
<b>Badge Types:</b><br>
• <b>Status Badges:</b> Show status (New, Hot, Sale, etc.)<br>
• <b>Count Badges:</b> Display numbers (notifications, items)<br>
• <b>Category Badges:</b> Label categories and tags<br><br>

<b>Usage Guidelines:</b><br>
• Keep text short and meaningful<br>
• Use consistent colors for similar statuses<br>
• Position near related content<br>
• Consider accessibility and contrast
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_progress_section(self, parent_layout):
            """Create progress components section."""
            group = QGroupBox("Progress Components")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Progress bars
            progress_layout = QGridLayout()
            
            # Linear progress bars
            linear_group = QGroupBox("Progress Bars")
            linear_layout = QVBoxLayout(linear_group)
            
            # Determinate progress
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(65)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #c8c6c4;
                    border-radius: 8px;
                    background-color: #f3f2f1;
                    text-align: center;
                    height: 16px;
                }
                QProgressBar::chunk {
                    background-color: #0078d4;
                    border-radius: 7px;
                }
            """)
            
            # Indeterminate progress
            self.indeterminate_bar = QProgressBar()
            self.indeterminate_bar.setRange(0, 0)  # Indeterminate
            self.indeterminate_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #c8c6c4;
                    border-radius: 8px;
                    background-color: #f3f2f1;
                    text-align: center;
                    height: 16px;
                }
                QProgressBar::chunk {
                    background-color: #107c10;
                    border-radius: 7px;
                }
            """)
            
            # Success progress
            success_bar = QProgressBar()
            success_bar.setRange(0, 100)
            success_bar.setValue(100)
            success_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #c8c6c4;
                    border-radius: 8px;
                    background-color: #f3f2f1;
                    text-align: center;
                    height: 16px;
                }
                QProgressBar::chunk {
                    background-color: #107c10;
                    border-radius: 7px;
                }
            """)
            
            linear_layout.addWidget(QLabel("Determinate Progress (65%):"))
            linear_layout.addWidget(self.progress_bar)
            linear_layout.addWidget(QLabel("Indeterminate Progress:"))
            linear_layout.addWidget(self.indeterminate_bar)
            linear_layout.addWidget(QLabel("Completed (100%):"))
            linear_layout.addWidget(success_bar)
            
            # Progress controls
            controls_layout = QHBoxLayout()
            
            progress_btn = QPushButton("Animate Progress")
            progress_btn.clicked.connect(self.animate_progress)
            progress_btn.setStyleSheet("""
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
            
            reset_btn = QPushButton("Reset")
            reset_btn.clicked.connect(self.reset_progress)
            reset_btn.setStyleSheet("""
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
            
            controls_layout.addWidget(progress_btn)
            controls_layout.addWidget(reset_btn)
            controls_layout.addStretch()
            
            linear_layout.addLayout(controls_layout)
            
            # Circular progress
            circular_group = QGroupBox("Circular Progress")
            circular_layout = QVBoxLayout(circular_group)
            
            circular_info = QLabel("""
<b>Circular Progress Features:</b><br>
• Compact space usage<br>
• Elegant loading states<br>
• Percentage display<br>
• Smooth animations<br><br>

<i>Note: Circular progress rings would be implemented<br>
as custom components with QPainter for drawing.</i>
""")
            circular_info.setWordWrap(True)
            circular_layout.addWidget(circular_info)
            
            # Add to grid
            progress_layout.addWidget(linear_group, 0, 0)
            progress_layout.addWidget(circular_group, 0, 1)
            
            layout.addLayout(progress_layout)
            
            # Progress examples
            examples_label = QLabel("""
<b>Progress Types:</b><br>
• <b>Determinate:</b> Known progress with percentage<br>
• <b>Indeterminate:</b> Unknown duration activities<br>
• <b>Circular:</b> Compact progress indicators<br><br>

<b>Usage Guidelines:</b><br>
• Use determinate for measurable tasks<br>
• Use indeterminate for unknown duration<br>
• Provide clear labels and context<br>
• Consider accessibility and screen readers
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_loading_section(self, parent_layout):
            """Create loading components section."""
            group = QGroupBox("Loading Components")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Loading indicators layout
            loading_layout = QHBoxLayout()
            
            # Spinner loading
            spinner_group = QGroupBox("Loading Spinners")
            spinner_layout = QVBoxLayout(spinner_group)
            
            # Create animated loading spinner
            spinner_frame = QFrame()
            spinner_frame.setFixedSize(60, 60)
            spinner_frame.setStyleSheet("""
                QFrame {
                    border: 4px solid #f3f2f1;
                    border-top: 4px solid #0078d4;
                    border-radius: 30px;
                }
            """)
            
            # Dots loading
            dots_frame = QFrame()
            dots_layout = QHBoxLayout(dots_frame)
            dots_layout.setSpacing(8)
            
            # Create animated dots
            self.loading_dots = []
            for i in range(3):
                dot = QFrame()
                dot.setFixedSize(12, 12)
                dot.setStyleSheet("""
                    QFrame {
                        background-color: #0078d4;
                        border-radius: 6px;
                    }
                """)
                self.loading_dots.append(dot)
                dots_layout.addWidget(dot)
            
            spinner_layout.addWidget(QLabel("Spinner:"))
            spinner_layout.addWidget(spinner_frame, alignment=Qt.AlignmentFlag.AlignCenter)
            spinner_layout.addWidget(QLabel("Dots:"))
            spinner_layout.addWidget(dots_frame, alignment=Qt.AlignmentFlag.AlignCenter)
            
            # Loading states
            states_group = QGroupBox("Loading States")
            states_layout = QVBoxLayout(states_group)
            
            # Different loading messages
            loading_states = [
                "🔄 Loading...",
                "📊 Processing data...",
                "🌐 Connecting...",
                "💾 Saving changes...",
                "🔍 Searching...",
                "⬇️ Downloading..."
            ]
            
            for state in loading_states:
                state_frame = QFrame()
                state_frame.setStyleSheet("""
                    QFrame {
                        background-color: #f9f9f9;
                        border: 1px solid #edebe9;
                        border-radius: 4px;
                        padding: 8px;
                        margin: 2px;
                    }
                """)
                state_layout = QHBoxLayout(state_frame)
                state_layout.addWidget(QLabel(state))
                state_layout.addStretch()
                
                states_layout.addWidget(state_frame)
            
            # Loading controls
            loading_controls = QHBoxLayout()
            
            start_loading_btn = QPushButton("Start Loading Animation")
            start_loading_btn.clicked.connect(self.start_loading_animation)
            start_loading_btn.setStyleSheet("""
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
            
            stop_loading_btn = QPushButton("Stop Animation")
            stop_loading_btn.clicked.connect(self.stop_loading_animation)
            stop_loading_btn.setStyleSheet("""
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
            
            loading_controls.addWidget(start_loading_btn)
            loading_controls.addWidget(stop_loading_btn)
            loading_controls.addStretch()
            
            states_layout.addLayout(loading_controls)
            
            # Add to layout
            loading_layout.addWidget(spinner_group)
            loading_layout.addWidget(states_group)
            
            layout.addLayout(loading_layout)
            
            # Loading examples
            examples_label = QLabel("""
<b>Loading Indicators:</b><br>
• <b>Spinners:</b> Circular rotating indicators<br>
• <b>Dots:</b> Pulsating dot animations<br>
• <b>Progress Bars:</b> Linear progress for known duration<br>
• <b>Skeleton Screens:</b> Content placeholders<br><br>

<b>Best Practices:</b><br>
• Choose appropriate indicator for context<br>
• Provide meaningful loading messages<br>
• Consider animation performance<br>
• Ensure accessibility compliance
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_alerts_section(self, parent_layout):
            """Create alert components section."""
            group = QGroupBox("Alert Components")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Alert types
            alerts_layout = QVBoxLayout()
            
            # Create different alert types
            alert_types = [
                ("Info", "This is an informational alert with helpful tips.", "#0078d4", "#e1f5fe"),
                ("Success", "Operation completed successfully!", "#107c10", "#e8f5e8"),
                ("Warning", "Please review your input before proceeding.", "#ff8c00", "#fff4e6"),
                ("Error", "An error occurred. Please try again.", "#d13438", "#fde7e7")
            ]
            
            for alert_type, message, border_color, bg_color in alert_types:
                alert_frame = QFrame()
                alert_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {bg_color};
                        border-left: 4px solid {border_color};
                        border-radius: 4px;
                        padding: 12px;
                        margin: 4px 0;
                    }}
                """)
                
                alert_layout = QHBoxLayout(alert_frame)
                
                # Alert icon
                icons = {"Info": "ℹ️", "Success": "✅", "Warning": "⚠️", "Error": "❌"}
                icon_label = QLabel(icons[alert_type])
                icon_label.setStyleSheet("font-size: 16px;")
                
                # Alert content
                content_layout = QVBoxLayout()
                title_label = QLabel(f"{alert_type} Alert")
                title_label.setStyleSheet("font-weight: bold; color: #323130;")
                message_label = QLabel(message)
                message_label.setWordWrap(True)
                
                content_layout.addWidget(title_label)
                content_layout.addWidget(message_label)
                
                # Close button
                close_btn = QPushButton("✕")
                close_btn.setFixedSize(24, 24)
                close_btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: rgba(0, 0, 0, 0.1);
                    }
                """)
                close_btn.clicked.connect(lambda checked, frame=alert_frame: frame.hide())
                
                alert_layout.addWidget(icon_label)
                alert_layout.addLayout(content_layout)
                alert_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignTop)
                
                alerts_layout.addWidget(alert_frame)
            
            layout.addLayout(alerts_layout)
            
            # Alert controls
            alert_controls = QHBoxLayout()
            
            show_alerts_btn = QPushButton("Show All Alerts")
            show_alerts_btn.clicked.connect(self.show_all_alerts)
            show_alerts_btn.setStyleSheet("""
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
            
            demo_alert_btn = QPushButton("Show Demo Alert")
            demo_alert_btn.clicked.connect(self.show_demo_alert)
            demo_alert_btn.setStyleSheet("""
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
            
            alert_controls.addWidget(show_alerts_btn)
            alert_controls.addWidget(demo_alert_btn)
            alert_controls.addStretch()
            
            layout.addLayout(alert_controls)
            
            # Alert examples
            examples_label = QLabel("""
<b>Alert Types:</b><br>
• <b>Info:</b> General information and tips<br>
• <b>Success:</b> Successful operations and confirmations<br>
• <b>Warning:</b> Cautions and important notices<br>
• <b>Error:</b> Error messages and failures<br><br>

<b>Alert Features:</b><br>
• Dismissible with close button<br>
• Color-coded for quick recognition<br>
• Icon support for visual clarity<br>
• Responsive and accessible design
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_labels_section(self, parent_layout):
            """Create label components section."""
            group = QGroupBox("Label & Text Components")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Typography examples
            typography_layout = QVBoxLayout()
            
            # Different text styles
            text_styles = [
                ("Hero Title", "font-size: 32px; font-weight: bold; color: #323130;"),
                ("Section Header", "font-size: 24px; font-weight: 600; color: #323130;"),
                ("Subtitle", "font-size: 18px; font-weight: 500; color: #605e5c;"),
                ("Body Text", "font-size: 14px; color: #323130;"),
                ("Caption", "font-size: 12px; color: #605e5c;"),
                ("Link Text", "font-size: 14px; color: #0078d4; text-decoration: underline;")
            ]
            
            for text, style in text_styles:
                label = QLabel(f"{text} - Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
                label.setStyleSheet(style)
                label.setWordWrap(True)
                typography_layout.addWidget(label)
            
            layout.addLayout(typography_layout)
            
            # Chip/Tag examples
            chips_group = QGroupBox("Chips & Tags")
            chips_layout = QHBoxLayout(chips_group)
            
            # Create sample chips
            chip_data = [
                ("React", "#61dafb"),
                ("Python", "#3776ab"),
                ("JavaScript", "#f7df1e"),
                ("Design", "#ff6b6b"),
                ("UX", "#4ecdc4")
            ]
            
            for text, color in chip_data:
                chip = self.create_sample_chip(text, color)
                chips_layout.addWidget(chip)
            
            chips_layout.addStretch()
            layout.addWidget(chips_group)
            
            # Label examples
            examples_label = QLabel("""
<b>Text & Label Guidelines:</b><br>
• <b>Hierarchy:</b> Use consistent text sizes and weights<br>
• <b>Contrast:</b> Ensure sufficient color contrast<br>
• <b>Readability:</b> Choose appropriate line spacing<br>
• <b>Accessibility:</b> Support screen readers and high contrast<br><br>

<b>Chip Components:</b><br>
• <b>Tags:</b> Categorize and label content<br>
• <b>Filters:</b> Interactive filtering options<br>
• <b>Status:</b> Show status and states<br>
• <b>Actions:</b> Compact action buttons
""")
            examples_label.setWordWrap(True)
            layout.addWidget(examples_label)
            
            parent_layout.addWidget(group)
            
        def create_interactive_demo(self, parent_layout):
            """Create interactive demo section."""
            group = QGroupBox("Interactive Display Demo")
            group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
            layout = QVBoxLayout(group)
            
            # Demo controls
            demo_controls = QHBoxLayout()
            
            # Create demo buttons
            demo_buttons = [
                ("Show Success", self.show_success_demo),
                ("Show Loading", self.show_loading_demo),
                ("Show Error", self.show_error_demo),
                ("Update Progress", self.update_progress_demo),
                ("Toggle Theme", self.toggle_theme_demo)
            ]
            
            for text, callback in demo_buttons:
                btn = QPushButton(text)
                btn.clicked.connect(callback)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        margin: 2px;
                    }
                    QPushButton:hover {
                        background-color: #106ebe;
                    }
                """)
                demo_controls.addWidget(btn)
            
            demo_controls.addStretch()
            layout.addLayout(demo_controls)
            
            # Demo status area
            self.demo_status = QLabel("Ready - Click buttons above to see interactive demos")
            self.demo_status.setStyleSheet("""
                QLabel {
                    background-color: #f3f2f1;
                    border: 1px solid #edebe9;
                    border-radius: 4px;
                    padding: 15px;
                    margin: 10px 0;
                    color: #323130;
                }
            """)
            layout.addWidget(self.demo_status)
            
            parent_layout.addWidget(group)
            
        # Helper methods for creating components
        def create_sample_card(self, title, content, bg_color="#ffffff", accent_color=None):
            """Create a sample card component."""
            card = QFrame()
            card.setFixedWidth(250)
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border: 1px solid #edebe9;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                }}
                QFrame:hover {{
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }}
            """)
            
            layout = QVBoxLayout(card)
            
            title_label = QLabel(title)
            title_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {accent_color if accent_color else '#323130'};")
            
            content_label = QLabel(content)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("color: #605e5c; margin-top: 8px;")
            
            layout.addWidget(title_label)
            layout.addWidget(content_label)
            layout.addStretch()
            
            return card
            
        def create_sample_badge(self, text, bg_color, text_color):
            """Create a sample badge component."""
            badge = QLabel(text)
            badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg_color};
                    color: {text_color};
                    border-radius: 10px;
                    padding: 4px 8px;
                    font-size: 12px;
                    font-weight: bold;
                    margin: 2px;
                }}
            """)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            return badge
            
        def create_sample_chip(self, text, color):
            """Create a sample chip component."""
            chip = QFrame()
            chip.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}20;
                    border: 1px solid {color};
                    border-radius: 12px;
                    padding: 6px 12px;
                    margin: 2px;
                }}
            """)
            
            layout = QHBoxLayout(chip)
            layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(text)
            label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 500;")
            
            layout.addWidget(label)
            return chip
            
        # Animation and interaction methods
        def animate_progress(self):
            """Animate progress bar."""
            self.progress_timer = QTimer()
            self.progress_value = 0
            
            def update_progress():
                self.progress_value += 2
                self.progress_bar.setValue(self.progress_value)
                if self.progress_value >= 100:
                    self.progress_timer.stop()
                    
            self.progress_timer.timeout.connect(update_progress)
            self.progress_timer.start(50)  # Update every 50ms
            
        def reset_progress(self):
            """Reset progress bar."""
            if hasattr(self, 'progress_timer'):
                self.progress_timer.stop()
            self.progress_bar.setValue(0)
            self.progress_value = 0
            
        def start_loading_animation(self):
            """Start loading animation."""
            self.demo_status.setText("🔄 Loading animation started...")
            
        def stop_loading_animation(self):
            """Stop loading animation."""
            self.demo_status.setText("⏹️ Loading animation stopped")
            
        def show_all_alerts(self):
            """Show all hidden alerts."""
            # Find all alert frames and show them
            for widget in self.findChildren(QFrame):
                if widget.isHidden() and "border-left" in widget.styleSheet():
                    widget.show()
            self.demo_status.setText("All alerts are now visible")
            
        def show_demo_alert(self):
            """Show a demo alert."""
            self.demo_status.setText("🎉 Demo alert triggered! Check the alerts section above.")
            
        def show_success_demo(self):
            """Show success demo."""
            self.demo_status.setText("✅ Success! Operation completed successfully.")
            self.demo_status.setStyleSheet("""
                QLabel {
                    background-color: #e8f5e8;
                    border: 1px solid #107c10;
                    border-radius: 4px;
                    padding: 15px;
                    margin: 10px 0;
                    color: #107c10;
                }
            """)
            
        def show_loading_demo(self):
            """Show loading demo."""
            self.demo_status.setText("🔄 Loading... Please wait while we process your request.")
            self.demo_status.setStyleSheet("""
                QLabel {
                    background-color: #e1f5fe;
                    border: 1px solid #0078d4;
                    border-radius: 4px;
                    padding: 15px;
                    margin: 10px 0;
                    color: #0078d4;
                }
            """)
            
        def show_error_demo(self):
            """Show error demo."""
            self.demo_status.setText("❌ Error: Something went wrong. Please try again.")
            self.demo_status.setStyleSheet("""
                QLabel {
                    background-color: #fde7e7;
                    border: 1px solid #d13438;
                    border-radius: 4px;
                    padding: 15px;
                    margin: 10px 0;
                    color: #d13438;
                }
            """)
            
        def update_progress_demo(self):
            """Update progress demo."""
            self.animate_progress()
            self.demo_status.setText("📊 Progress updated! Watch the progress bar above.")
            
        def toggle_theme_demo(self):
            """Toggle theme demo."""
            # This would toggle between light and dark themes
            self.demo_status.setText("🎨 Theme toggle would be implemented here")
    
    # Create and show demo
    demo = DisplayDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
