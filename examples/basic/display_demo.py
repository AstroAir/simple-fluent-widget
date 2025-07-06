#!/usr/bin/env python3
"""
Fluent Basic Display Components Demo

This example demonstrates the comprehensive usage of Fluent basic display components including
progress bars, labels, badges, cards, tooltips, and other visual elements.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QGroupBox, QPushButton, QFrame, QTabWidget, QGridLayout,
    QProgressBar, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QPalette


def main():
    """Run the basic display demo application."""
    app = QApplication(sys.argv)
    
    # Import display components after QApplication is created
    try:
        from components.basic.display.progress import FluentProgressBar, FluentProgressRing
        from components.basic.display.label import FluentLabel, FluentTitleLabel
        from components.basic.display.badge import FluentBadge, FluentNotificationBadge
        from components.basic.display.card import FluentCard, FluentInfoCard
        from components.basic.display.tooltip import FluentToolTip
        from components.basic.display.loading import FluentLoadingSpinner, FluentLoadingDots
        from components.basic.display.alert import FluentAlert, FluentInfoBar
        DISPLAY_AVAILABLE = True
    except ImportError as e:
        print(f"Import error: {e}")
        print("Using fallback Qt components for demo")
        DISPLAY_AVAILABLE = False
    
    class BasicDisplayDemo(QMainWindow):
        """Main demo window showcasing Fluent basic display components."""
        
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Fluent Basic Display Components Demo")
            self.setGeometry(100, 100, 1400, 900)
            
            # Create central widget with tabs
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(10)
            main_layout.setContentsMargins(10, 10, 10, 10)
            
            # Add title
            title = QLabel("Fluent Basic Display Components Demo")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
            main_layout.addWidget(title)
            
            # Create tab widget for different component examples
            self.tab_widget = QTabWidget()
            main_layout.addWidget(self.tab_widget)
            
            # Create tabs
            self.create_progress_tab()
            self.create_labels_tab()
            self.create_badges_tab()
            self.create_cards_tab()
            self.create_loading_tab()
            self.create_alerts_tab()
            
        def create_progress_tab(self):
            """Create progress indicators examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Linear progress bars
            linear_group = QGroupBox("Linear Progress Indicators")
            linear_layout = QVBoxLayout(linear_group)
            
            # Determinate progress
            det_layout = QHBoxLayout()
            det_layout.addWidget(QLabel("File Upload:"))
            
            if DISPLAY_AVAILABLE:
                self.upload_progress = FluentProgressBar()
                self.upload_progress.set_style("primary")
            else:
                self.upload_progress = QProgressBar()
                self.upload_progress.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid #e1dfdd;
                        border-radius: 6px;
                        text-align: center;
                        font-size: 12px;
                        background-color: #f3f2f1;
                        height: 24px;
                    }
                    QProgressBar::chunk {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                   stop:0 #0078d4, stop:1 #106ebe);
                        border-radius: 4px;
                        margin: 1px;
                    }
                """)
            
            self.upload_progress.setRange(0, 100)
            self.upload_progress.setValue(65)
            
            self.upload_label = QLabel("65% Complete")
            det_layout.addWidget(self.upload_progress)
            det_layout.addWidget(self.upload_label)
            linear_layout.addLayout(det_layout)
            
            # Success progress
            success_layout = QHBoxLayout()
            success_layout.addWidget(QLabel("Installation:"))
            
            if DISPLAY_AVAILABLE:
                self.install_progress = FluentProgressBar()
                self.install_progress.set_style("success")
            else:
                self.install_progress = QProgressBar()
                self.install_progress.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid #e1dfdd;
                        border-radius: 6px;
                        text-align: center;
                        font-size: 12px;
                        background-color: #f3f2f1;
                        height: 24px;
                    }
                    QProgressBar::chunk {
                        background-color: #107c10;
                        border-radius: 4px;
                        margin: 1px;
                    }
                """)
            
            self.install_progress.setRange(0, 100)
            self.install_progress.setValue(100)
            
            success_layout.addWidget(self.install_progress)
            success_layout.addWidget(QLabel("✓ Complete"))
            linear_layout.addLayout(success_layout)
            
            # Warning progress
            warning_layout = QHBoxLayout()
            warning_layout.addWidget(QLabel("Sync Status:"))
            
            if DISPLAY_AVAILABLE:
                self.sync_progress = FluentProgressBar()
                self.sync_progress.set_style("warning")
            else:
                self.sync_progress = QProgressBar()
                self.sync_progress.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid #e1dfdd;
                        border-radius: 6px;
                        text-align: center;
                        font-size: 12px;
                        background-color: #f3f2f1;
                        height: 24px;
                    }
                    QProgressBar::chunk {
                        background-color: #ff8c00;
                        border-radius: 4px;
                        margin: 1px;
                    }
                """)
            
            self.sync_progress.setRange(0, 100)
            self.sync_progress.setValue(35)
            
            warning_layout.addWidget(self.sync_progress)
            warning_layout.addWidget(QLabel("⚠️ Issues"))
            linear_layout.addLayout(warning_layout)
            
            # Indeterminate progress
            indet_layout = QHBoxLayout()
            indet_layout.addWidget(QLabel("Processing:"))
            
            self.process_progress = QProgressBar()
            self.process_progress.setRange(0, 0)  # Indeterminate
            self.process_progress.setStyleSheet(self.upload_progress.styleSheet())
            
            indet_layout.addWidget(self.process_progress)
            indet_layout.addWidget(QLabel("Please wait..."))
            linear_layout.addLayout(indet_layout)
            
            layout.addWidget(linear_group)
            
            # Circular progress
            circular_group = QGroupBox("Circular Progress Indicators")
            circular_layout = QHBoxLayout(circular_group)
            
            if DISPLAY_AVAILABLE:
                # Progress rings
                self.cpu_ring = FluentProgressRing()
                self.cpu_ring.setValue(45)
                self.cpu_ring.set_style("primary")
                
                self.memory_ring = FluentProgressRing()
                self.memory_ring.setValue(78)
                self.memory_ring.set_style("warning")
                
                self.disk_ring = FluentProgressRing()
                self.disk_ring.setValue(23)
                self.disk_ring.set_style("success")
                
                # Create containers for rings with labels
                cpu_container = QVBoxLayout()
                cpu_container.addWidget(self.cpu_ring)
                cpu_container.addWidget(QLabel("CPU: 45%"))
                cpu_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                memory_container = QVBoxLayout()
                memory_container.addWidget(self.memory_ring)
                memory_container.addWidget(QLabel("Memory: 78%"))
                memory_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                disk_container = QVBoxLayout()
                disk_container.addWidget(self.disk_ring)
                disk_container.addWidget(QLabel("Disk: 23%"))
                disk_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                circular_layout.addLayout(cpu_container)
                circular_layout.addLayout(memory_container)
                circular_layout.addLayout(disk_container)
            else:
                # Fallback with styled labels
                for name, value, color in [("CPU", "45%", "#0078d4"), ("Memory", "78%", "#ff8c00"), ("Disk", "23%", "#107c10")]:
                    container = QVBoxLayout()
                    
                    # Create circular progress simulation
                    circle = QLabel(value)
                    circle.setFixedSize(80, 80)
                    circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    circle.setStyleSheet(f"""
                        QLabel {{
                            border: 4px solid {color};
                            border-radius: 40px;
                            background-color: #f3f2f1;
                            font-weight: bold;
                            font-size: 14px;
                        }}
                    """)
                    
                    container.addWidget(circle)
                    container.addWidget(QLabel(f"{name}: {value}"))
                    container.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    circular_layout.addLayout(container)
            
            circular_layout.addStretch()
            layout.addWidget(circular_group)
            
            # Progress controls
            controls_group = QGroupBox("Progress Controls")
            controls_layout = QHBoxLayout(controls_group)
            
            self.animate_btn = QPushButton("Animate Progress")
            self.animate_btn.clicked.connect(self.animate_progress)
            
            self.reset_btn = QPushButton("Reset Progress")
            self.reset_btn.clicked.connect(self.reset_progress)
            
            controls_layout.addWidget(self.animate_btn)
            controls_layout.addWidget(self.reset_btn)
            controls_layout.addStretch()
            
            layout.addWidget(controls_group)
            
            # Usage documentation
            usage_group = QGroupBox("Progress Indicator Usage")
            usage_layout = QVBoxLayout(usage_group)
            
            usage_text = QLabel("""
<b>Progress Indicator Guidelines:</b><br><br>

<b>Linear Progress Bars:</b><br>
• Use for sequential processes (file transfers, installations)<br>
• Show percentage text when space allows<br>
• Use different colors for different states (primary, success, warning, error)<br>
• Indeterminate for unknown duration tasks<br><br>

<b>Circular Progress:</b><br>
• Perfect for dashboards and status displays<br>
• Great for showing system resource usage<br>
• Compact representation of progress<br>
• Can display percentage in center<br><br>

<b>Best Practices:</b><br>
• Always provide context about what's progressing<br>
• Use appropriate colors (green for success, orange for warnings)<br>
• Include cancel option for long operations<br>
• Show time estimates when possible<br>
""")
            usage_text.setWordWrap(True)
            usage_layout.addWidget(usage_text)
            
            layout.addWidget(usage_group)
            layout.addStretch()
            
            # Setup animation timer
            self.progress_timer = QTimer()
            self.progress_timer.timeout.connect(self.update_animated_progress)
            self.animation_direction = 1
            
            self.tab_widget.addTab(tab, "Progress")
            
        def create_labels_tab(self):
            """Create labels and text display examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Typography examples
            typography_group = QGroupBox("Typography & Text Styles")
            typography_layout = QVBoxLayout(typography_group)
            
            # Title styles
            if DISPLAY_AVAILABLE:
                title_label = FluentTitleLabel("Large Title")
                title_label.set_style("large")
                
                subtitle_label = FluentTitleLabel("Subtitle")
                subtitle_label.set_style("subtitle")
                
                body_label = FluentLabel("Body text with proper line height and spacing for readability.")
                body_label.set_style("body")
                
                caption_label = FluentLabel("Caption text for secondary information")
                caption_label.set_style("caption")
            else:
                # Fallback with styled QLabels
                title_label = QLabel("Large Title")
                title_label.setStyleSheet("font-size: 32px; font-weight: 300; color: #323130; margin: 10px 0;")
                
                subtitle_label = QLabel("Subtitle")
                subtitle_label.setStyleSheet("font-size: 20px; font-weight: 600; color: #323130; margin: 8px 0;")
                
                body_label = QLabel("Body text with proper line height and spacing for readability.")
                body_label.setStyleSheet("font-size: 14px; line-height: 1.4; color: #323130; margin: 4px 0;")
                body_label.setWordWrap(True)
                
                caption_label = QLabel("Caption text for secondary information")
                caption_label.setStyleSheet("font-size: 12px; color: #605e5c; margin: 2px 0;")
            
            typography_layout.addWidget(title_label)
            typography_layout.addWidget(subtitle_label)
            typography_layout.addWidget(body_label)
            typography_layout.addWidget(caption_label)
            
            layout.addWidget(typography_group)
            
            # Colored labels
            colors_group = QGroupBox("Colored Text & Status Labels")
            colors_layout = QGridLayout(colors_group)
            
            # Status colors
            status_labels = [
                ("Success Status", "#107c10"),
                ("Warning Status", "#ff8c00"), 
                ("Error Status", "#d13438"),
                ("Info Status", "#0078d4"),
                ("Neutral Status", "#605e5c")
            ]
            
            for i, (text, color) in enumerate(status_labels):
                label = QLabel(text)
                label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
                colors_layout.addWidget(label, i // 2, i % 2)
            
            layout.addWidget(colors_group)
            
            # Interactive labels
            interactive_group = QGroupBox("Interactive Labels")
            interactive_layout = QVBoxLayout(interactive_group)
            
            # Clickable label
            self.clickable_label = QLabel("🔗 Clickable Link (Click me!)")
            self.clickable_label.setStyleSheet("""
                QLabel {
                    color: #0078d4;
                    text-decoration: underline;
                    cursor: pointer;
                    font-size: 14px;
                    padding: 5px;
                }
                QLabel:hover {
                    color: #106ebe;
                    background-color: #f3f2f1;
                }
            """)
            self.clickable_label.mousePressEvent = self.on_link_clicked
            
            # Selectable label
            self.selectable_label = QLabel("This text is selectable. Try selecting this text with your mouse.")
            self.selectable_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self.selectable_label.setStyleSheet("padding: 8px; border: 1px solid #e1dfdd; border-radius: 4px; background-color: #faf9f8;")
            self.selectable_label.setWordWrap(True)
            
            # Rich text label
            rich_text = """
            <p>This label supports <b>bold</b>, <i>italic</i>, and <u>underlined</u> text.</p>
            <p>It can also display <span style="color: #0078d4;">colored text</span> and 
            <a href="#" style="color: #0078d4;">hyperlinks</a>.</p>
            <ul>
                <li>Bullet points</li>
                <li>Are also supported</li>
            </ul>
            """
            
            self.rich_label = QLabel(rich_text)
            self.rich_label.setTextFormat(Qt.TextFormat.RichText)
            self.rich_label.setWordWrap(True)
            self.rich_label.setStyleSheet("padding: 10px; border: 1px solid #c8c6c4; border-radius: 4px; background-color: white;")
            
            interactive_layout.addWidget(self.clickable_label)
            interactive_layout.addWidget(self.selectable_label)
            interactive_layout.addWidget(self.rich_label)
            
            layout.addWidget(interactive_group)
            
            # Usage examples
            usage_group = QGroupBox("Label Usage Guidelines")
            usage_layout = QVBoxLayout(usage_group)
            
            usage_text = QLabel("""
<b>Label Types & When to Use:</b><br><br>

<b>Title Labels:</b> Page headers, section titles, dialog headers<br>
<b>Body Labels:</b> Main content, descriptions, explanations<br>
<b>Caption Labels:</b> Secondary information, help text, timestamps<br>
<b>Status Labels:</b> Success/error messages, system status<br>
<b>Link Labels:</b> Clickable text, navigation elements<br><br>

<b>Typography Best Practices:</b><br>
• Use consistent font hierarchy throughout your app<br>
• Ensure sufficient contrast for accessibility<br>
• Keep line length readable (45-75 characters)<br>
• Use appropriate font weights for emphasis<br>
• Consider color-blind users when using color alone<br><br>

<b>Code Example:</b><br>
<code>
title = FluentTitleLabel("Section Title")<br>
title.set_style("large")<br><br>

status = FluentLabel("Operation completed successfully")<br>
status.set_color("success")<br>
status.set_icon("checkmark")<br>
</code>
""")
            usage_text.setWordWrap(True)
            usage_layout.addWidget(usage_text)
            
            layout.addWidget(usage_group)
            layout.addStretch()
            
            self.tab_widget.addTab(tab, "Labels & Text")
            
        def create_badges_tab(self):
            """Create badges and notification examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Status badges
            status_group = QGroupBox("Status Badges")
            status_layout = QGridLayout(status_group)
            
            if DISPLAY_AVAILABLE:
                # Fluent badges
                badges = [
                    ("Online", "success"),
                    ("Away", "warning"),
                    ("Busy", "error"),
                    ("Offline", "neutral"),
                    ("New", "accent")
                ]
                
                for i, (text, style) in enumerate(badges):
                    badge = FluentBadge(text)
                    badge.set_style(style)
                    status_layout.addWidget(badge, i // 3, i % 3)
            else:
                # Fallback badges with styling
                badge_styles = [
                    ("Online", "#107c10", "white"),
                    ("Away", "#ff8c00", "white"),
                    ("Busy", "#d13438", "white"),
                    ("Offline", "#605e5c", "white"),
                    ("New", "#8764b8", "white")
                ]
                
                for i, (text, bg_color, text_color) in enumerate(badge_styles):
                    badge = QLabel(text)
                    badge.setStyleSheet(f"""
                        QLabel {{
                            background-color: {bg_color};
                            color: {text_color};
                            padding: 4px 8px;
                            border-radius: 12px;
                            font-size: 12px;
                            font-weight: bold;
                            max-width: 60px;
                        }}
                    """)
                    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    status_layout.addWidget(badge, i // 3, i % 3)
            
            layout.addWidget(status_group)
            
            # Notification badges
            notification_group = QGroupBox("Notification Badges")
            notification_layout = QHBoxLayout(notification_group)
            
            # Create containers with badges
            containers = [
                ("📧 Mail", "12"),
                ("🔔 Notifications", "3"),
                ("📁 Files", "99+"),
                ("⚙️ Settings", ""),
                ("👤 Profile", "1")
            ]
            
            for icon_text, count in containers:
                container = QFrame()
                container.setFixedSize(100, 80)
                container.setStyleSheet("""
                    QFrame {
                        border: 1px solid #c8c6c4;
                        border-radius: 8px;
                        background-color: #faf9f8;
                    }
                    QFrame:hover {
                        background-color: #f3f2f1;
                        border-color: #0078d4;
                    }
                """)
                
                container_layout = QVBoxLayout(container)
                container_layout.setContentsMargins(10, 10, 10, 10)
                
                # Icon/text
                icon_label = QLabel(icon_text)
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                icon_label.setStyleSheet("font-size: 12px; font-weight: bold; border: none;")
                container_layout.addWidget(icon_label)
                
                # Badge
                if count:
                    if DISPLAY_AVAILABLE:
                        badge = FluentNotificationBadge(count)
                    else:
                        badge = QLabel(count)
                        badge.setStyleSheet("""
                            QLabel {
                                background-color: #d13438;
                                color: white;
                                padding: 2px 6px;
                                border-radius: 10px;
                                font-size: 10px;
                                font-weight: bold;
                                max-width: 30px;
                                border: none;
                            }
                        """)
                        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    container_layout.addWidget(badge)
                    container_layout.setAlignment(badge, Qt.AlignmentFlag.AlignCenter)
                
                notification_layout.addWidget(container)
            
            notification_layout.addStretch()
            layout.addWidget(notification_group)
            
            # Interactive badges
            interactive_group = QGroupBox("Interactive Badge Examples")
            interactive_layout = QVBoxLayout(interactive_group)
            
            # Badge counter demo
            counter_layout = QHBoxLayout()
            counter_layout.addWidget(QLabel("Message Count:"))
            
            self.message_count = 0
            if DISPLAY_AVAILABLE:
                self.counter_badge = FluentNotificationBadge("0")
            else:
                self.counter_badge = QLabel("0")
                self.counter_badge.setStyleSheet("""
                    QLabel {
                        background-color: #0078d4;
                        color: white;
                        padding: 4px 8px;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: bold;
                        min-width: 20px;
                    }
                """)
                self.counter_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            add_btn = QPushButton("Add Message")
            add_btn.clicked.connect(self.add_message)
            
            clear_btn = QPushButton("Clear All")
            clear_btn.clicked.connect(self.clear_messages)
            
            counter_layout.addWidget(self.counter_badge)
            counter_layout.addWidget(add_btn)
            counter_layout.addWidget(clear_btn)
            counter_layout.addStretch()
            
            interactive_layout.addLayout(counter_layout)
            
            # Status toggle demo
            status_layout = QHBoxLayout()
            status_layout.addWidget(QLabel("User Status:"))
            
            if DISPLAY_AVAILABLE:
                self.status_badge = FluentBadge("Online")
                self.status_badge.set_style("success")
            else:
                self.status_badge = QLabel("Online")
                self.status_badge.setStyleSheet("""
                    QLabel {
                        background-color: #107c10;
                        color: white;
                        padding: 4px 12px;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                """)
                self.status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            toggle_status_btn = QPushButton("Toggle Status")
            toggle_status_btn.clicked.connect(self.toggle_status)
            self.current_status = 0
            
            status_layout.addWidget(self.status_badge)
            status_layout.addWidget(toggle_status_btn)
            status_layout.addStretch()
            
            interactive_layout.addLayout(status_layout)
            
            layout.addWidget(interactive_group)
            
            # Usage guidelines
            usage_group = QGroupBox("Badge Usage Guidelines")
            usage_layout = QVBoxLayout(usage_group)
            
            usage_text = QLabel("""
<b>Badge Types & Applications:</b><br><br>

<b>Status Badges:</b> User presence, system status, connection state<br>
<b>Notification Badges:</b> Unread counts, new items, alerts<br>
<b>Category Badges:</b> Tags, labels, classifications<br>
<b>Progress Badges:</b> Step indicators, completion status<br><br>

<b>Design Guidelines:</b><br>
• Keep text short (ideally 1-3 characters for counts)<br>
• Use "99+" for counts over 99<br>
• Choose colors that match your app's semantic meaning<br>
• Ensure badges are large enough to be easily tappable<br>
• Consider accessibility when using color alone<br><br>

<b>Best Practices:</b><br>
• Update badges in real-time when possible<br>
• Use animation to draw attention to changes<br>
• Position badges consistently across your app<br>
• Provide clear actions to dismiss/clear badges<br>
""")
            usage_text.setWordWrap(True)
            usage_layout.addWidget(usage_text)
            
            layout.addWidget(usage_group)
            layout.addStretch()
            
            self.tab_widget.addTab(tab, "Badges")
            
        def create_cards_tab(self):
            """Create cards and containers examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Create scroll area for cards
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
            cards_widget = QWidget()
            cards_layout = QVBoxLayout(cards_widget)
            
            # Basic cards
            basic_group = QGroupBox("Basic Cards")
            basic_layout = QHBoxLayout(basic_group)
            
            if DISPLAY_AVAILABLE:
                # Simple info card
                info_card = FluentInfoCard()
                info_card.set_title("System Information")
                info_card.set_content("CPU: Intel i7-9700K\nRAM: 16GB DDR4\nStorage: 512GB SSD")
                info_card.set_icon("🖥️")
                
                # Action card
                action_card = FluentCard()
                action_card.set_title("Quick Actions")
                action_card.add_action("Backup", self.on_card_action)
                action_card.add_action("Sync", self.on_card_action)
                action_card.add_action("Settings", self.on_card_action)
                
                basic_layout.addWidget(info_card)
                basic_layout.addWidget(action_card)
            else:
                # Fallback cards
                for title, content in [("System Information", "CPU: Intel i7-9700K\nRAM: 16GB DDR4\nStorage: 512GB SSD"), 
                                     ("Quick Actions", "Available actions:\n• Backup\n• Sync\n• Settings")]:
                    card = self.create_fallback_card(title, content)
                    basic_layout.addWidget(card)
            
            basic_layout.addStretch()
            cards_layout.addWidget(basic_group)
            
            # Feature cards
            feature_group = QGroupBox("Feature Cards")
            feature_layout = QGridLayout(feature_group)
            
            features = [
                ("📊 Analytics", "View detailed analytics\nand performance metrics"),
                ("🔒 Security", "Manage security settings\nand permissions"),
                ("🌐 Network", "Configure network\nconnections and settings"),
                ("📱 Mobile", "Mobile app companion\nwith sync capabilities"),
                ("🎨 Themes", "Customize appearance\nwith various themes"),
                ("⚡ Performance", "Optimize system\nperformance settings")
            ]
            
            for i, (title, description) in enumerate(features):
                if DISPLAY_AVAILABLE:
                    card = FluentCard()
                    card.set_title(title)
                    card.set_description(description)
                    card.set_clickable(True)
                    card.clicked.connect(lambda: self.on_feature_card_clicked(title))
                else:
                    card = self.create_fallback_card(title, description)
                
                feature_layout.addWidget(card, i // 3, i % 3)
            
            cards_layout.addWidget(feature_group)
            
            # Interactive cards
            interactive_group = QGroupBox("Interactive Cards")
            interactive_layout = QVBoxLayout(interactive_group)
            
            # Expandable card
            self.expandable_card = self.create_expandable_card()
            interactive_layout.addWidget(self.expandable_card)
            
            # Hoverable cards with actions
            actions_layout = QHBoxLayout()
            for i in range(3):
                card = self.create_action_card(f"Item {i+1}")
                actions_layout.addWidget(card)
            actions_layout.addStretch()
            
            interactive_layout.addLayout(actions_layout)
            cards_layout.addWidget(interactive_group)
            
            scroll.setWidget(cards_widget)
            layout.addWidget(scroll)
            
            # Usage guidelines
            usage_group = QGroupBox("Card Design Guidelines")
            usage_layout = QVBoxLayout(usage_group)
            
            usage_text = QLabel("""
<b>Card Types & Usage:</b><br><br>

<b>Info Cards:</b> Display read-only information with optional icons<br>
<b>Action Cards:</b> Contain buttons or clickable elements for user actions<br>
<b>Feature Cards:</b> Highlight app features or navigation options<br>
<b>Content Cards:</b> Display articles, posts, or media content<br><br>

<b>Design Principles:</b><br>
• Use consistent elevation and shadow effects<br>
• Maintain proper padding and spacing<br>
• Group related information logically<br>
• Provide clear visual hierarchy<br>
• Use hover effects to indicate interactivity<br><br>

<b>Accessibility:</b><br>
• Ensure sufficient contrast ratios<br>
• Provide keyboard navigation support<br>
• Use semantic HTML structure<br>
• Include appropriate ARIA labels<br>
""")
            usage_text.setWordWrap(True)
            usage_layout.addWidget(usage_text)
            
            layout.addWidget(usage_group)
            
            self.tab_widget.addTab(tab, "Cards")
            
        def create_loading_tab(self):
            """Create loading indicators examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Spinner types
            spinners_group = QGroupBox("Loading Spinners")
            spinners_layout = QHBoxLayout(spinners_group)
            
            if DISPLAY_AVAILABLE:
                # Different spinner styles
                spinner1 = FluentLoadingSpinner()
                spinner1.set_style("primary")
                spinner1.start()
                
                spinner2 = FluentLoadingSpinner()
                spinner2.set_style("accent") 
                spinner2.set_size("large")
                spinner2.start()
                
                dots_loader = FluentLoadingDots()
                dots_loader.start()
                
                spinners_layout.addWidget(QLabel("Primary Spinner:"))
                spinners_layout.addWidget(spinner1)
                spinners_layout.addWidget(QLabel("Large Accent:"))
                spinners_layout.addWidget(spinner2)
                spinners_layout.addWidget(QLabel("Dots Loader:"))
                spinners_layout.addWidget(dots_loader)
            else:
                # Fallback loading indicators
                for text, color in [("Primary", "#0078d4"), ("Accent", "#8764b8"), ("Dots", "#605e5c")]:
                    label = QLabel(f"{text} Loading...")
                    label.setStyleSheet(f"""
                        QLabel {{
                            color: {color};
                            font-weight: bold;
                            padding: 10px;
                            border: 2px dashed {color};
                            border-radius: 8px;
                            background-color: rgba(0, 120, 212, 0.1);
                        }}
                    """)
                    spinners_layout.addWidget(label)
            
            spinners_layout.addStretch()
            layout.addWidget(spinners_group)
            
            # Loading states
            states_group = QGroupBox("Loading State Examples")
            states_layout = QVBoxLayout(states_group)
            
            # Button loading states
            button_layout = QHBoxLayout()
            
            self.load_btn = QPushButton("Load Data")
            self.load_btn.clicked.connect(self.simulate_loading)
            
            self.save_btn = QPushButton("Save Changes")
            self.save_btn.clicked.connect(self.simulate_saving)
            
            self.refresh_btn = QPushButton("🔄 Refresh")
            self.refresh_btn.clicked.connect(self.simulate_refresh)
            
            button_layout.addWidget(self.load_btn)
            button_layout.addWidget(self.save_btn)
            button_layout.addWidget(self.refresh_btn)
            button_layout.addStretch()
            
            states_layout.addLayout(button_layout)
            
            # Content loading placeholder
            content_frame = QFrame()
            content_frame.setFixedHeight(200)
            content_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #c8c6c4;
                    border-radius: 8px;
                    background-color: #faf9f8;
                }
            """)
            
            self.content_layout = QVBoxLayout(content_frame)
            self.show_content()
            
            states_layout.addWidget(QLabel("Content Area:"))
            states_layout.addWidget(content_frame)
            
            layout.addWidget(states_group)
            
            # Loading controls
            controls_group = QGroupBox("Loading Controls")
            controls_layout = QHBoxLayout(controls_group)
            
            start_btn = QPushButton("Start All Loaders")
            start_btn.clicked.connect(self.start_all_loaders)
            
            stop_btn = QPushButton("Stop All Loaders")
            stop_btn.clicked.connect(self.stop_all_loaders)
            
            controls_layout.addWidget(start_btn)
            controls_layout.addWidget(stop_btn)
            controls_layout.addStretch()
            
            layout.addWidget(controls_group)
            
            # Usage guidelines
            usage_group = QGroupBox("Loading Indicator Usage")
            usage_layout = QVBoxLayout(usage_group)
            
            usage_text = QLabel("""
<b>Loading Indicator Guidelines:</b><br><br>

<b>Spinner Types:</b><br>
• <b>Small Spinners:</b> Inline loading, button states<br>
• <b>Large Spinners:</b> Full page loading, major operations<br>
• <b>Dots/Pulse:</b> Subtle background processes<br>
• <b>Progress Bars:</b> When duration is known<br><br>

<b>When to Use:</b><br>
• Data fetching operations (> 1 second)<br>
• File uploads/downloads<br>
• Form submissions<br>
• Page transitions<br>
• Background sync processes<br><br>

<b>Best Practices:</b><br>
• Show loading state immediately<br>
• Provide context about what's loading<br>
• Use skeleton screens for predictable layouts<br>
• Allow cancellation for long operations<br>
• Avoid showing multiple loaders simultaneously<br>
""")
            usage_text.setWordWrap(True)
            usage_layout.addWidget(usage_text)
            
            layout.addWidget(usage_group)
            layout.addStretch()
            
            # Setup timers for loading simulations
            self.loading_timer = QTimer()
            self.loading_timer.timeout.connect(self.finish_loading)
            
            self.tab_widget.addTab(tab, "Loading")
            
        def create_alerts_tab(self):
            """Create alerts and notifications examples tab."""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Alert types
            alerts_group = QGroupBox("Alert Types")
            alerts_layout = QVBoxLayout(alerts_group)
            
            if DISPLAY_AVAILABLE:
                # Different alert styles
                success_alert = FluentAlert("Operation completed successfully!", "success")
                warning_alert = FluentAlert("Please check your input before proceeding.", "warning") 
                error_alert = FluentAlert("Failed to connect to server. Please try again.", "error")
                info_alert = FluentAlert("New update available. Click here to download.", "info")
                
                alerts_layout.addWidget(success_alert)
                alerts_layout.addWidget(warning_alert)
                alerts_layout.addWidget(error_alert)
                alerts_layout.addWidget(info_alert)
            else:
                # Fallback alerts
                alert_types = [
                    ("✓ Operation completed successfully!", "#107c10", "#dff6dd"),
                    ("⚠ Please check your input before proceeding.", "#ff8c00", "#fff4ce"),
                    ("✗ Failed to connect to server. Please try again.", "#d13438", "#fde7e9"),
                    ("ℹ New update available. Click here to download.", "#0078d4", "#deecf9")
                ]
                
                for text, color, bg_color in alert_types:
                    alert = QLabel(text)
                    alert.setStyleSheet(f"""
                        QLabel {{
                            color: {color};
                            background-color: {bg_color};
                            border: 1px solid {color};
                            border-radius: 6px;
                            padding: 12px 16px;
                            font-size: 14px;
                            margin: 4px 0;
                        }}
                    """)
                    alert.setWordWrap(True)
                    alerts_layout.addWidget(alert)
            
            layout.addWidget(alerts_group)
            
            # Dismissible alerts
            dismissible_group = QGroupBox("Dismissible Alerts")
            dismissible_layout = QVBoxLayout(dismissible_group)
            
            # Create dismissible alerts
            self.dismissible_alerts = []
            for i, (text, alert_type) in enumerate([
                ("This alert can be dismissed by clicking the X button.", "info"),
                ("Warning: This action cannot be undone.", "warning"),
                ("Error: Please fix the issues below.", "error")
            ]):
                alert_frame = QFrame()
                alert_layout = QHBoxLayout(alert_frame)
                alert_layout.setContentsMargins(0, 0, 0, 0)
                
                if DISPLAY_AVAILABLE:
                    alert = FluentAlert(text, alert_type)
                    alert.set_dismissible(True)
                    alert.dismissed.connect(lambda: self.remove_alert(alert_frame))
                else:
                    # Fallback dismissible alert
                    colors = {"info": ("#0078d4", "#deecf9"), "warning": ("#ff8c00", "#fff4ce"), "error": ("#d13438", "#fde7e9")}
                    color, bg_color = colors[alert_type]
                    
                    alert_label = QLabel(text)
                    alert_label.setStyleSheet(f"""
                        QLabel {{
                            color: {color};
                            background-color: {bg_color};
                            border: 1px solid {color};
                            border-radius: 6px;
                            padding: 12px 16px;
                            font-size: 14px;
                        }}
                    """)
                    alert_label.setWordWrap(True)
                    
                    close_btn = QPushButton("✕")
                    close_btn.setFixedSize(24, 24)
                    close_btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: transparent;
                            border: none;
                            color: {color};
                            font-weight: bold;
                            border-radius: 12px;
                        }}
                        QPushButton:hover {{
                            background-color: rgba(0, 0, 0, 0.1);
                        }}
                    """)
                    close_btn.clicked.connect(lambda checked, af=alert_frame: self.remove_alert(af))
                    
                    alert_layout.addWidget(alert_label)
                    alert_layout.addWidget(close_btn)
                    alert_layout.setAlignment(close_btn, Qt.AlignmentFlag.AlignTop)
                
                if not DISPLAY_AVAILABLE:
                    dismissible_layout.addWidget(alert_frame)
                    self.dismissible_alerts.append(alert_frame)
                else:
                    dismissible_layout.addWidget(alert)
                    self.dismissible_alerts.append(alert)
            
            layout.addWidget(dismissible_group)
            
            # Toast notifications simulation
            toast_group = QGroupBox("Toast Notifications")
            toast_layout = QVBoxLayout(toast_group)
            
            toast_buttons_layout = QHBoxLayout()
            
            success_toast_btn = QPushButton("Show Success Toast")
            success_toast_btn.clicked.connect(lambda: self.show_toast("File saved successfully!", "success"))
            
            warning_toast_btn = QPushButton("Show Warning Toast") 
            warning_toast_btn.clicked.connect(lambda: self.show_toast("Connection unstable", "warning"))
            
            error_toast_btn = QPushButton("Show Error Toast")
            error_toast_btn.clicked.connect(lambda: self.show_toast("Failed to save file", "error"))
            
            toast_buttons_layout.addWidget(success_toast_btn)
            toast_buttons_layout.addWidget(warning_toast_btn)
            toast_buttons_layout.addWidget(error_toast_btn)
            toast_buttons_layout.addStretch()
            
            toast_layout.addLayout(toast_buttons_layout)
            
            # Toast display area
            self.toast_area = QFrame()
            self.toast_area.setFixedHeight(100)
            self.toast_area.setStyleSheet("""
                QFrame {
                    border: 1px dashed #c8c6c4;
                    border-radius: 8px;
                    background-color: #f9f9f9;
                }
            """)
            
            self.toast_layout = QVBoxLayout(self.toast_area)
            self.toast_layout.addWidget(QLabel("Toast notifications will appear here"))
            
            toast_layout.addWidget(QLabel("Toast Preview Area:"))
            toast_layout.addWidget(self.toast_area)
            
            layout.addWidget(toast_group)
            
            # Usage guidelines
            usage_group = QGroupBox("Alert & Notification Guidelines")
            usage_layout = QVBoxLayout(usage_group)
            
            usage_text = QLabel("""
<b>Alert Types & Usage:</b><br><br>

<b>Success Alerts:</b> Confirm completed actions (save, send, delete)<br>
<b>Warning Alerts:</b> Caution about potential issues (unsaved changes)<br>
<b>Error Alerts:</b> Report problems that need user attention<br>
<b>Info Alerts:</b> Provide helpful information (tips, updates)<br><br>

<b>Toast Notifications:</b><br>
• Brief, auto-dismissing messages<br>
• Don't interrupt user workflow<br>
• Use for status updates and confirmations<br>
• Position consistently (usually top-right or bottom)<br><br>

<b>Best Practices:</b><br>
• Use clear, actionable language<br>
• Provide solutions when showing errors<br>
• Don't stack too many alerts<br>
• Allow manual dismissal for persistent alerts<br>
• Use appropriate icons and colors<br>
""")
            usage_text.setWordWrap(True)
            usage_layout.addWidget(usage_text)
            
            layout.addWidget(usage_group)
            layout.addStretch()
            
            self.tab_widget.addTab(tab, "Alerts")
        
        # Event handlers and utility methods
        def animate_progress(self):
            """Start progress animation."""
            if not self.progress_timer.isActive():
                self.progress_timer.start(100)
                self.animate_btn.setText("Stop Animation")
            else:
                self.progress_timer.stop()
                self.animate_btn.setText("Animate Progress")
                
        def update_animated_progress(self):
            """Update animated progress values."""
            current = self.upload_progress.value()
            if current >= 100:
                self.animation_direction = -1
            elif current <= 0:
                self.animation_direction = 1
                
            new_value = current + (self.animation_direction * 2)
            self.upload_progress.setValue(new_value)
            self.upload_label.setText(f"{new_value}% Complete")
            
            # Update circular progress if available
            if hasattr(self, 'cpu_ring'):
                cpu_val = (self.cpu_ring.value() + 1) % 100
                self.cpu_ring.setValue(cpu_val)
                
        def reset_progress(self):
            """Reset all progress indicators."""
            self.upload_progress.setValue(0)
            self.upload_label.setText("0% Complete")
            
            if hasattr(self, 'cpu_ring'):
                self.cpu_ring.setValue(0)
                self.memory_ring.setValue(0)
                self.disk_ring.setValue(0)
                
        def on_link_clicked(self, event):
            """Handle clickable label click."""
            self.clickable_label.setText("🔗 Link clicked! (Click again)")
            QTimer.singleShot(2000, lambda: self.clickable_label.setText("🔗 Clickable Link (Click me!)"))
            
        def add_message(self):
            """Add message to counter."""
            self.message_count += 1
            count_text = str(self.message_count) if self.message_count < 100 else "99+"
            self.counter_badge.setText(count_text)
            
        def clear_messages(self):
            """Clear message counter."""
            self.message_count = 0
            self.counter_badge.setText("0")
            
        def toggle_status(self):
            """Toggle status badge."""
            statuses = [
                ("Online", "#107c10"),
                ("Away", "#ff8c00"), 
                ("Busy", "#d13438"),
                ("Offline", "#605e5c")
            ]
            
            self.current_status = (self.current_status + 1) % len(statuses)
            status_text, color = statuses[self.current_status]
            
            self.status_badge.setText(status_text)
            if not DISPLAY_AVAILABLE:
                self.status_badge.setStyleSheet(f"""
                    QLabel {{
                        background-color: {color};
                        color: white;
                        padding: 4px 12px;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: bold;
                    }}
                """)
                
        def create_fallback_card(self, title, content):
            """Create fallback card with Qt widgets."""
            card = QFrame()
            card.setFixedSize(200, 150)
            card.setStyleSheet("""
                QFrame {
                    border: 1px solid #c8c6c4;
                    border-radius: 8px;
                    background-color: white;
                    padding: 12px;
                }
                QFrame:hover {
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    border-color: #0078d4;
                }
            """)
            
            # Add drop shadow effect
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(0, 0, 0, 50))
            shadow.setOffset(0, 2)
            card.setGraphicsEffect(shadow)
            
            layout = QVBoxLayout(card)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #323130; border: none;")
            
            content_label = QLabel(content)
            content_label.setStyleSheet("font-size: 12px; color: #605e5c; border: none;")
            content_label.setWordWrap(True)
            
            layout.addWidget(title_label)
            layout.addWidget(content_label)
            layout.addStretch()
            
            return card
            
        def create_expandable_card(self):
            """Create an expandable card example."""
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    border: 1px solid #c8c6c4;
                    border-radius: 8px;
                    background-color: white;
                    padding: 12px;
                }
            """)
            
            layout = QVBoxLayout(card)
            
            # Header with expand button
            header_layout = QHBoxLayout()
            header_label = QLabel("📊 Detailed Statistics")
            header_label.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
            
            self.expand_btn = QPushButton("▼ Expand")
            self.expand_btn.setFixedSize(80, 24)
            self.expand_btn.clicked.connect(self.toggle_card_expansion)
            
            header_layout.addWidget(header_label)
            header_layout.addStretch()
            header_layout.addWidget(self.expand_btn)
            
            # Expandable content
            self.expandable_content = QFrame()
            self.expandable_content.setStyleSheet("border: none; background-color: #f9f9f9; border-radius: 4px; padding: 8px;")
            content_layout = QVBoxLayout(self.expandable_content)
            
            content_layout.addWidget(QLabel("CPU Usage: 45%"))
            content_layout.addWidget(QLabel("Memory Usage: 67%"))
            content_layout.addWidget(QLabel("Disk Usage: 23%"))
            content_layout.addWidget(QLabel("Network: 15 Mbps"))
            
            self.expandable_content.hide()
            self.is_expanded = False
            
            layout.addLayout(header_layout)
            layout.addWidget(self.expandable_content)
            
            return card
            
        def create_action_card(self, title):
            """Create action card with hover effects."""
            card = QFrame()
            card.setFixedSize(150, 120)
            card.setStyleSheet("""
                QFrame {
                    border: 1px solid #c8c6c4;
                    border-radius: 8px;
                    background-color: white;
                    padding: 12px;
                }
                QFrame:hover {
                    background-color: #f3f2f1;
                    border-color: #0078d4;
                }
            """)
            
            layout = QVBoxLayout(card)
            
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
            
            action_btn = QPushButton("Action")
            action_btn.clicked.connect(lambda: self.on_card_action(title))
            
            layout.addWidget(title_label)
            layout.addStretch()
            layout.addWidget(action_btn)
            
            return card
            
        def toggle_card_expansion(self):
            """Toggle card expansion state."""
            if self.is_expanded:
                self.expandable_content.hide()
                self.expand_btn.setText("▼ Expand")
                self.is_expanded = False
            else:
                self.expandable_content.show()
                self.expand_btn.setText("▲ Collapse")
                self.is_expanded = True
                
        def on_card_action(self, action):
            """Handle card action button clicks."""
            print(f"Card action clicked: {action}")
            
        def on_feature_card_clicked(self, feature):
            """Handle feature card clicks."""
            print(f"Feature card clicked: {feature}")
            
        def simulate_loading(self):
            """Simulate loading operation."""
            self.load_btn.setText("Loading...")
            self.load_btn.setEnabled(False)
            self.show_loading_content()
            QTimer.singleShot(3000, lambda: self.finish_button_loading(self.load_btn, "Load Data"))
            
        def simulate_saving(self):
            """Simulate saving operation."""
            self.save_btn.setText("Saving...")
            self.save_btn.setEnabled(False)
            QTimer.singleShot(2000, lambda: self.finish_button_loading(self.save_btn, "Save Changes"))
            
        def simulate_refresh(self):
            """Simulate refresh operation."""
            self.refresh_btn.setText("🔄 Refreshing...")
            self.refresh_btn.setEnabled(False)
            QTimer.singleShot(1500, lambda: self.finish_button_loading(self.refresh_btn, "🔄 Refresh"))
            
        def finish_button_loading(self, button, original_text):
            """Finish button loading state."""
            button.setText(original_text)
            button.setEnabled(True)
            
        def show_content(self):
            """Show normal content."""
            # Clear layout
            while self.content_layout.count():
                child = self.content_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                    
            # Add content
            self.content_layout.addWidget(QLabel("📄 Content loaded successfully!"))
            self.content_layout.addWidget(QLabel("This is the main content area."))
            self.content_layout.addWidget(QLabel("Data refreshed at: 2:30 PM"))
            
        def show_loading_content(self):
            """Show loading content."""
            # Clear layout
            while self.content_layout.count():
                child = self.content_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                    
            # Add loading indicator
            loading_label = QLabel("⏳ Loading content...")
            loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            loading_label.setStyleSheet("color: #605e5c; font-style: italic;")
            self.content_layout.addWidget(loading_label)
            
        def finish_loading(self):
            """Finish loading and show content."""
            self.show_content()
            
        def start_all_loaders(self):
            """Start all loading indicators."""
            # This would start all spinners if they were available
            pass
            
        def stop_all_loaders(self):
            """Stop all loading indicators."""
            # This would stop all spinners if they were available
            pass
            
        def remove_alert(self, alert_frame):
            """Remove dismissible alert."""
            alert_frame.hide()
            if alert_frame in self.dismissible_alerts:
                self.dismissible_alerts.remove(alert_frame)
                
        def show_toast(self, message, toast_type):
            """Show toast notification in preview area."""
            # Clear existing toasts
            while self.toast_layout.count():
                child = self.toast_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                    
            # Create toast
            colors = {
                "success": ("#107c10", "#dff6dd"),
                "warning": ("#ff8c00", "#fff4ce"), 
                "error": ("#d13438", "#fde7e9")
            }
            color, bg_color = colors[toast_type]
            
            toast = QLabel(f"🍞 {message}")
            toast.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    background-color: {bg_color};
                    border: 1px solid {color};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 12px;
                }}
            """)
            
            self.toast_layout.addWidget(toast)
            
            # Auto-dismiss after 3 seconds
            QTimer.singleShot(3000, lambda: self.toast_layout.removeWidget(toast) if toast else None)
    
    # Create and show demo
    demo = BasicDisplayDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
