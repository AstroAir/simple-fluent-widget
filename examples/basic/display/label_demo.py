"""
Fluent Label Components Demo
Comprehensive example showcasing all features and functionality
"""

import sys
import webbrowser
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QGroupBox,
    QScrollArea, QFrame, QLineEdit, QSpinBox, QSlider,
    QCheckBox, QTextEdit, QSizePolicy, QFileDialog
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QColor, QPixmap, QIcon, QDesktopServices

# Import the label components
from components.basic.label import (
    FluentLabel, FluentIconLabel, FluentStatusLabel,
    FluentLinkLabel, FluentLabelGroup
)
from core.theme import theme_manager, ThemeMode


class LabelDemo(QMainWindow):
    """Main demo window showcasing all label features"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Label Components Demo")
        self.setGeometry(100, 100, 1200, 900)

        # Central widget with scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        # Main layout
        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Fluent Label Components Demo")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Theme toggle
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        if theme_manager.get_theme_mode() == ThemeMode.DARK:
            self.theme_combo.setCurrentText("Dark")
        else:
            self.theme_combo.setCurrentText("Light")
        self.theme_combo.currentTextChanged.connect(self._toggle_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        main_layout.addLayout(theme_layout)

        # Create demo sections
        main_layout.addWidget(self._create_fluent_label_demo())
        main_layout.addWidget(self._create_icon_label_demo())
        main_layout.addWidget(self._create_status_label_demo())
        main_layout.addWidget(self._create_link_label_demo())
        main_layout.addWidget(self._create_label_group_demo())
        main_layout.addWidget(self._create_interactive_demo())

        main_layout.addStretch()

    def _create_fluent_label_demo(self) -> QGroupBox:
        """Create FluentLabel demonstration section"""
        group = QGroupBox("FluentLabel - Text Styles & Types")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Text styles demonstration
        layout.addWidget(QLabel("Text Styles:"))
        styles_layout = QVBoxLayout()

        style_examples = [
            ("Display Style", FluentLabel.LabelStyle.DISPLAY),
            ("Title Large Style", FluentLabel.LabelStyle.TITLE_LARGE),
            ("Title Style", FluentLabel.LabelStyle.TITLE),
            ("Subtitle Style", FluentLabel.LabelStyle.SUBTITLE),
            ("Body Style (Default)", FluentLabel.LabelStyle.BODY),
            ("Caption Style", FluentLabel.LabelStyle.CAPTION)
        ]

        for text, style in style_examples:
            style_label = FluentLabel(text, style=style)
            styles_layout.addWidget(style_label)

        layout.addLayout(styles_layout)

        # Text types demonstration
        layout.addWidget(QLabel("Text Types:"))
        types_grid = QGridLayout()

        type_examples = [
            ("Primary Text", FluentLabel.LabelType.PRIMARY),
            ("Secondary Text", FluentLabel.LabelType.SECONDARY),
            ("Disabled Text", FluentLabel.LabelType.DISABLED),
            ("Accent Text", FluentLabel.LabelType.ACCENT),
            ("Success Text", FluentLabel.LabelType.SUCCESS),
            ("Warning Text", FluentLabel.LabelType.WARNING),
            ("Error Text", FluentLabel.LabelType.ERROR)
        ]

        for i, (text, label_type) in enumerate(type_examples):
            type_label = FluentLabel(text, label_type=label_type)
            types_grid.addWidget(type_label, i // 2, i % 2)

        layout.addLayout(types_grid)

        # Clickable labels
        layout.addWidget(QLabel("Clickable Labels:"))
        clickable_layout = QHBoxLayout()

        self.clickable_label = FluentLabel(
            "Click me!", label_type=FluentLabel.LabelType.ACCENT)
        self.clickable_label.set_clickable(True)
        self.click_counter_label = FluentLabel("Clicks: 0")
        self.click_count = 0

        self.clickable_label.clicked.connect(self._on_label_clicked)

        clickable_layout.addWidget(self.clickable_label)
        clickable_layout.addWidget(self.click_counter_label)
        clickable_layout.addStretch()

        layout.addLayout(clickable_layout)

        # Word wrap demonstration
        layout.addWidget(QLabel("Word Wrap:"))
        long_text = "This is a very long text that demonstrates the word wrapping capability of FluentLabel. It should automatically wrap to multiple lines when the text exceeds the available width of the container."
        wrap_label = FluentLabel(long_text, style=FluentLabel.LabelStyle.BODY)
        wrap_label.setWordWrap(True)
        wrap_label.setStyleSheet(
            "border: 1px dashed gray; padding: 10px; border-radius: 4px;")
        layout.addWidget(wrap_label)

        return group

    def _create_icon_label_demo(self) -> QGroupBox:
        """Create FluentIconLabel demonstration section"""
        group = QGroupBox("FluentIconLabel - Labels with Icons")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Basic icon labels (using text as icons for demo)
        layout.addWidget(QLabel("Basic Icon Labels:"))
        basic_layout = QVBoxLayout()

        # Simulate icons with colored squares
        icon_examples = [
            ("📄 Document", "Horizontal layout with icon", "horizontal"),
            ("📁 Folder", "Another horizontal example", "horizontal"),
            ("🔍 Search", "Search functionality", "horizontal")
        ]

        for icon_text, label_text, direction in icon_examples:
            # Create a simple colored pixmap as icon
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(0, 120, 215))  # Blue color

            icon_label = FluentIconLabel(f"{icon_text} {label_text}", pixmap,
                                         layout_direction=direction, icon_size=16)
            basic_layout.addWidget(icon_label)

        layout.addLayout(basic_layout)

        # Vertical layout examples
        layout.addWidget(QLabel("Vertical Layout Examples:"))
        vertical_layout = QHBoxLayout()

        for i in range(3):
            pixmap = QPixmap(24, 24)
            colors = [QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255)]
            pixmap.fill(colors[i])

            v_icon_label = FluentIconLabel(f"Vertical\nLabel {i+1}", pixmap,
                                           layout_direction="vertical", icon_size=24)
            v_icon_label.setStyleSheet(
                "border: 1px solid lightgray; padding: 10px; border-radius: 4px;")
            vertical_layout.addWidget(v_icon_label)

        vertical_layout.addStretch()
        layout.addLayout(vertical_layout)

        # Different text styles with icons
        layout.addWidget(QLabel("Different Text Styles with Icons:"))
        styles_layout = QVBoxLayout()

        style_combinations = [
            ("Title with Icon", FluentLabel.LabelStyle.TITLE),
            ("Subtitle with Icon", FluentLabel.LabelStyle.SUBTITLE),
            ("Body with Icon", FluentLabel.LabelStyle.BODY),
            ("Caption with Icon", FluentLabel.LabelStyle.CAPTION)
        ]

        for text, style in style_combinations:
            pixmap = QPixmap(20, 20)
            pixmap.fill(QColor(100, 100, 100))

            styled_icon_label = FluentIconLabel(text, pixmap, icon_size=20)
            styled_icon_label.set_text_style(style)
            styles_layout.addWidget(styled_icon_label)

        layout.addLayout(styles_layout)

        # Clickable icon labels
        layout.addWidget(QLabel("Clickable Icon Labels:"))
        clickable_icon_layout = QHBoxLayout()

        for i, color in enumerate([QColor(255, 100, 100), QColor(100, 255, 100), QColor(100, 100, 255)]):
            pixmap = QPixmap(18, 18)
            pixmap.fill(color)

            clickable_icon = FluentIconLabel(
                f"Clickable {i+1}", pixmap, icon_size=18)
            clickable_icon.set_clickable(True)
            clickable_icon.clicked.connect(
                lambda checked, idx=i: self._on_icon_label_clicked(idx))
            clickable_icon_layout.addWidget(clickable_icon)

        self.icon_click_label = FluentLabel("No icon clicked yet")
        clickable_icon_layout.addWidget(self.icon_click_label)
        clickable_icon_layout.addStretch()

        layout.addLayout(clickable_icon_layout)

        return group

    def _create_status_label_demo(self) -> QGroupBox:
        """Create FluentStatusLabel demonstration section"""
        group = QGroupBox("FluentStatusLabel - Status Indicators")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Basic status types
        layout.addWidget(QLabel("Basic Status Types:"))
        status_layout = QVBoxLayout()

        status_examples = [
            ("Operation completed successfully",
             FluentStatusLabel.StatusType.SUCCESS),
            ("Warning: Check your settings", FluentStatusLabel.StatusType.WARNING),
            ("Error: Failed to save file", FluentStatusLabel.StatusType.ERROR),
            ("Information: New update available",
             FluentStatusLabel.StatusType.INFO),
            ("Processing your request...", FluentStatusLabel.StatusType.PROCESSING)
        ]

        for text, status in status_examples:
            status_label = FluentStatusLabel(text, status=status)
            status_layout.addWidget(status_label)

        layout.addLayout(status_layout)

        # Without indicators
        layout.addWidget(QLabel("Status Labels without Indicators:"))
        no_indicator_layout = QVBoxLayout()

        for text, status in status_examples[:3]:  # Show first 3 examples
            no_indicator_label = FluentStatusLabel(
                text, status=status, show_indicator=False)
            no_indicator_layout.addWidget(no_indicator_label)

        layout.addLayout(no_indicator_layout)

        # Dynamic status changes
        layout.addWidget(QLabel("Dynamic Status Changes:"))
        dynamic_layout = QHBoxLayout()

        self.dynamic_status_label = FluentStatusLabel("Click buttons to change status",
                                                      status=FluentStatusLabel.StatusType.INFO)
        dynamic_layout.addWidget(self.dynamic_status_label)

        # Status change buttons
        status_buttons_layout = QVBoxLayout()
        status_button_data = [
            ("Success", FluentStatusLabel.StatusType.SUCCESS),
            ("Warning", FluentStatusLabel.StatusType.WARNING),
            ("Error", FluentStatusLabel.StatusType.ERROR),
            ("Processing", FluentStatusLabel.StatusType.PROCESSING)
        ]

        for btn_text, status_type in status_button_data:
            btn = QPushButton(btn_text)
            btn.clicked.connect(
                lambda checked, s=status_type: self._change_dynamic_status(s))
            status_buttons_layout.addWidget(btn)

        dynamic_layout.addLayout(status_buttons_layout)
        layout.addLayout(dynamic_layout)

        return group

    def _create_link_label_demo(self) -> QGroupBox:
        """Create FluentLinkLabel demonstration section"""
        group = QGroupBox("FluentLinkLabel - Clickable Links")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Basic links
        layout.addWidget(QLabel("Basic Links:"))
        links_layout = QVBoxLayout()

        link_examples = [
            ("Visit GitHub", "https://github.com"),
            ("Python Documentation", "https://docs.python.org"),
            ("PySide6 Documentation", "https://doc.qt.io/qtforpython/"),
            ("Stack Overflow", "https://stackoverflow.com")
        ]

        for text, url in link_examples:
            link_label = FluentLinkLabel(text, url)
            links_layout.addWidget(link_label)

        layout.addLayout(links_layout)

        # Custom click handling
        layout.addWidget(QLabel("Custom Click Handling:"))
        custom_layout = QHBoxLayout()

        self.custom_link = FluentLinkLabel("Custom Action Link")
        self.custom_link.clicked.connect(self._on_custom_link_clicked)
        self.custom_link_status = FluentLabel("Link not clicked yet")

        custom_layout.addWidget(self.custom_link)
        custom_layout.addWidget(self.custom_link_status)
        custom_layout.addStretch()

        layout.addLayout(custom_layout)

        # Links in text
        layout.addWidget(QLabel("Links in Context:"))
        context_layout = QVBoxLayout()

        context_text = FluentLabel(
            "For more information, visit our ", style=FluentLabel.LabelStyle.BODY)
        context_link = FluentLinkLabel(
            "documentation", "https://example.com/docs")
        context_text2 = FluentLabel(
            " or check our ", style=FluentLabel.LabelStyle.BODY)
        context_link2 = FluentLinkLabel(
            "FAQ section", "https://example.com/faq")

        context_container_layout = QHBoxLayout()
        context_container_layout.addWidget(context_text)
        context_container_layout.addWidget(context_link)
        context_container_layout.addWidget(context_text2)
        context_container_layout.addWidget(context_link2)
        context_container_layout.addStretch()

        layout.addLayout(context_container_layout)

        return group

    def _create_label_group_demo(self) -> QGroupBox:
        """Create FluentLabelGroup demonstration section"""
        group = QGroupBox("FluentLabelGroup - Organized Label Collections")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Horizontal label group
        layout.addWidget(QLabel("Horizontal Label Group:"))
        self.horizontal_group = FluentLabelGroup(
            layout_direction="horizontal", spacing=16)

        # Add various types of labels
        self.horizontal_group.add_label("Label 1")
        self.horizontal_group.add_label(FluentLabel(
            "Accent Label", label_type=FluentLabel.LabelType.ACCENT))

        # Create icon label for group
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(0, 150, 0))
        icon_label_for_group = FluentIconLabel(
            "With Icon", pixmap, icon_size=16)
        self.horizontal_group.add_label(icon_label_for_group)

        self.horizontal_group.add_label(FluentStatusLabel(
            "Status", status=FluentStatusLabel.StatusType.SUCCESS))

        layout.addWidget(self.horizontal_group)

        # Vertical label group
        layout.addWidget(QLabel("Vertical Label Group:"))
        vertical_container = QFrame()
        vertical_container.setStyleSheet(
            "border: 1px dashed gray; padding: 10px; border-radius: 4px;")
        vertical_container_layout = QVBoxLayout(vertical_container)

        self.vertical_group = FluentLabelGroup(
            layout_direction="vertical", spacing=8)

        # Add labels with different styles
        self.vertical_group.add_label(FluentLabel(
            "Title", style=FluentLabel.LabelStyle.SUBTITLE))
        self.vertical_group.add_label(FluentLabel(
            "Description text goes here", style=FluentLabel.LabelStyle.BODY))
        self.vertical_group.add_label(FluentLabel("Additional info", style=FluentLabel.LabelStyle.CAPTION,
                                                  label_type=FluentLabel.LabelType.SECONDARY))

        vertical_container_layout.addWidget(self.vertical_group)
        layout.addWidget(vertical_container)

        # Dynamic label group management
        layout.addWidget(QLabel("Dynamic Label Group Management:"))
        management_layout = QVBoxLayout()

        self.dynamic_group = FluentLabelGroup(
            layout_direction="horizontal", spacing=12)
        self.dynamic_group.add_label("Initial Label")

        # Controls for dynamic group
        controls_layout = QHBoxLayout()

        self.new_label_input = QLineEdit()
        self.new_label_input.setPlaceholderText("Enter label text...")

        add_normal_btn = QPushButton("Add Normal")
        add_normal_btn.clicked.connect(self._add_normal_label)

        add_accent_btn = QPushButton("Add Accent")
        add_accent_btn.clicked.connect(self._add_accent_label)

        add_status_btn = QPushButton("Add Status")
        add_status_btn.clicked.connect(self._add_status_label)

        remove_last_btn = QPushButton("Remove Last")
        remove_last_btn.clicked.connect(self._remove_last_label)

        clear_all_btn = QPushButton("Clear All")
        clear_all_btn.clicked.connect(self._clear_all_labels)

        controls_layout.addWidget(self.new_label_input)
        controls_layout.addWidget(add_normal_btn)
        controls_layout.addWidget(add_accent_btn)
        controls_layout.addWidget(add_status_btn)
        controls_layout.addWidget(remove_last_btn)
        controls_layout.addWidget(clear_all_btn)

        management_layout.addWidget(self.dynamic_group)
        management_layout.addLayout(controls_layout)
        layout.addLayout(management_layout)

        return group

    def _create_interactive_demo(self) -> QGroupBox:
        """Create interactive demonstration section"""
        group = QGroupBox("Interactive Demo & Customization")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Customizable label
        layout.addWidget(QLabel("Customizable Label:"))

        # Demo label
        self.demo_label = FluentLabel("Customizable Demo Label",
                                      style=FluentLabel.LabelStyle.BODY,
                                      label_type=FluentLabel.LabelType.PRIMARY)

        demo_container = QFrame()
        demo_container.setStyleSheet(
            "border: 1px solid gray; padding: 20px; border-radius: 4px;")
        demo_container_layout = QVBoxLayout(demo_container)
        demo_container_layout.addWidget(self.demo_label)
        layout.addWidget(demo_container)

        # Controls
        controls_grid = QGridLayout()

        # Text control
        controls_grid.addWidget(QLabel("Text:"), 0, 0)
        self.text_input = QLineEdit()
        self.text_input.setText("Customizable Demo Label")
        self.text_input.textChanged.connect(self._update_demo_label_text)
        controls_grid.addWidget(self.text_input, 0, 1)

        # Style control
        controls_grid.addWidget(QLabel("Style:"), 1, 0)
        self.style_combo = QComboBox()
        self.style_combo.addItems(
            ["Body", "Caption", "Subtitle", "Title", "Title Large", "Display"])
        self.style_combo.currentTextChanged.connect(
            self._update_demo_label_style)
        controls_grid.addWidget(self.style_combo, 1, 1)

        # Type control
        controls_grid.addWidget(QLabel("Type:"), 2, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(
            ["Primary", "Secondary", "Disabled", "Accent", "Success", "Warning", "Error"])
        self.type_combo.currentTextChanged.connect(
            self._update_demo_label_type)
        controls_grid.addWidget(self.type_combo, 2, 1)

        # Clickable control
        controls_grid.addWidget(QLabel("Clickable:"), 3, 0)
        self.clickable_cb = QCheckBox("Make clickable")
        self.clickable_cb.toggled.connect(self._update_demo_label_clickable)
        controls_grid.addWidget(self.clickable_cb, 3, 1)

        layout.addLayout(controls_grid)

        # Performance test
        layout.addWidget(QLabel("Performance Test:"))
        perf_layout = QHBoxLayout()

        create_many_btn = QPushButton("Create 100 Labels")
        create_many_btn.clicked.connect(self._create_many_labels)

        clear_perf_btn = QPushButton("Clear Performance Test")
        clear_perf_btn.clicked.connect(self._clear_performance_labels)

        perf_layout.addWidget(create_many_btn)
        perf_layout.addWidget(clear_perf_btn)
        perf_layout.addStretch()

        layout.addLayout(perf_layout)

        # Container for performance test labels
        self.perf_container = QWidget()
        self.perf_layout = QVBoxLayout(self.perf_container)
        layout.addWidget(self.perf_container)

        # Event log
        layout.addWidget(QLabel("Event Log:"))
        self.event_log = QTextEdit()
        self.event_log.setMaximumHeight(100)
        self.event_log.setPlaceholderText(
            "Label events will be logged here...")
        layout.addWidget(self.event_log)

        return group

    def _on_label_clicked(self):
        """Handle clickable label click"""
        self.click_count += 1
        self.click_counter_label.setText(f"Clicks: {self.click_count}")
        self._log_event(f"Clickable label clicked (total: {self.click_count})")

    def _on_icon_label_clicked(self, index: int):
        """Handle icon label click"""
        self.icon_click_label.setText(f"Icon label {index + 1} clicked")
        self._log_event(f"Icon label {index + 1} clicked")

    def _change_dynamic_status(self, status: str):
        """Change dynamic status label"""
        status_messages = {
            FluentStatusLabel.StatusType.SUCCESS: "Operation successful!",
            FluentStatusLabel.StatusType.WARNING: "Warning state active",
            FluentStatusLabel.StatusType.ERROR: "Error occurred",
            FluentStatusLabel.StatusType.PROCESSING: "Processing..."
        }

        message = status_messages.get(status, "Status updated")
        self.dynamic_status_label.set_status(status)
        self.dynamic_status_label.set_text(message)
        self._log_event(f"Status changed to: {status}")

    def _on_custom_link_clicked(self):
        """Handle custom link click"""
        self.custom_link_status.setText("Custom link clicked!")
        self._log_event("Custom link clicked")

    def _add_normal_label(self):
        """Add normal label to dynamic group"""
        text = self.new_label_input.text().strip()
        if text:
            self.dynamic_group.add_label(text)
            self.new_label_input.clear()
            self._log_event(f"Added normal label: {text}")

    def _add_accent_label(self):
        """Add accent label to dynamic group"""
        text = self.new_label_input.text().strip()
        if text:
            accent_label = FluentLabel(
                text, label_type=FluentLabel.LabelType.ACCENT)
            self.dynamic_group.add_label(accent_label)
            self.new_label_input.clear()
            self._log_event(f"Added accent label: {text}")

    def _add_status_label(self):
        """Add status label to dynamic group"""
        text = self.new_label_input.text().strip()
        if text:
            status_label = FluentStatusLabel(
                text, status=FluentStatusLabel.StatusType.SUCCESS)
            self.dynamic_group.add_label(status_label)
            self.new_label_input.clear()
            self._log_event(f"Added status label: {text}")

    def _remove_last_label(self):
        """Remove last label from dynamic group"""
        labels = self.dynamic_group.get_labels()
        if labels:
            self.dynamic_group.remove_label(len(labels) - 1)
            self._log_event("Removed last label")

    def _clear_all_labels(self):
        """Clear all labels from dynamic group"""
        self.dynamic_group.clear_labels()
        self._log_event("Cleared all labels")

    def _update_demo_label_text(self, text: str):
        """Update demo label text"""
        self.demo_label.setText(text)

    def _update_demo_label_style(self, style_text: str):
        """Update demo label style"""
        style_map = {
            "Body": FluentLabel.LabelStyle.BODY,
            "Caption": FluentLabel.LabelStyle.CAPTION,
            "Subtitle": FluentLabel.LabelStyle.SUBTITLE,
            "Title": FluentLabel.LabelStyle.TITLE,
            "Title Large": FluentLabel.LabelStyle.TITLE_LARGE,
            "Display": FluentLabel.LabelStyle.DISPLAY
        }
        if style_text in style_map:
            self.demo_label.set_style(style_map[style_text])

    def _update_demo_label_type(self, type_text: str):
        """Update demo label type"""
        type_map = {
            "Primary": FluentLabel.LabelType.PRIMARY,
            "Secondary": FluentLabel.LabelType.SECONDARY,
            "Disabled": FluentLabel.LabelType.DISABLED,
            "Accent": FluentLabel.LabelType.ACCENT,
            "Success": FluentLabel.LabelType.SUCCESS,
            "Warning": FluentLabel.LabelType.WARNING,
            "Error": FluentLabel.LabelType.ERROR
        }
        if type_text in type_map:
            self.demo_label.set_type(type_map[type_text])

    def _update_demo_label_clickable(self, clickable: bool):
        """Update demo label clickable state"""
        self.demo_label.set_clickable(clickable)
        if clickable:
            self.demo_label.clicked.connect(
                self.demo_label.clicked.disconnect()
                self.demo_label.clicked.connect(
                    lambda: self._log_event("Demo label clicked"))

    def _create_many_labels(self):
        """Create many labels for performance testing"""
        self._clear_performance_labels()

        for i in range(100):
            if i % 20 == 0:
                # Create label group every 20 labels
                label_group = FluentLabelGroup(
                    layout_direction="horizontal", spacing=8)
                for j in range(5):
                    label_group.add_label(f"Group {i//20 + 1} Label {j + 1}")
                self.perf_layout.addWidget(label_group)
            else:
                # Create different types of labels
                if i % 5 == 0:
                    label = FluentLabel(
                        f"Title Label {i}", style=FluentLabel.LabelStyle.TITLE)
                elif i % 5 == 1:
                    label = FluentLabel(
                        f"Accent Label {i}", label_type=FluentLabel.LabelType.ACCENT)
                elif i % 5 == 2:
                    label = FluentStatusLabel(
                        f"Status {i}", status=FluentStatusLabel.StatusType.SUCCESS)
                elif i % 5 == 3:
                    label = FluentLinkLabel(
                        f"Link {i}", f"https://example.com/{i}")
                else:
                    # Create icon label
                    pixmap = QPixmap(12, 12)
                    pixmap.fill(QColor(i * 10 % 255, (i * 20) %
                                255, (i * 30) % 255))
                    label = FluentIconLabel(
                        f"Icon Label {i}", pixmap, icon_size=12)

                self.perf_layout.addWidget(label)

        self._log_event("Created 100 labels for performance test")

    def _clear_performance_labels(self):
        """Clear all performance test labels"""
        while self.perf_layout.count():
            child = self.perf_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self._log_event("Cleared performance test labels")

    def _log_event(self, message: str):
        """Log event to the event log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_log.append(f"[{timestamp}] {message}")

    def _toggle_theme(self, theme_name: str):
        """Toggle between light and dark themes"""
        if theme_name == "Dark":
            theme_manager.set_theme_mode(ThemeMode.DARK)
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)

        self._log_event(f"Theme changed to: {theme_name}")


def main():
    """Run the label demo application"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show demo window
    demo = LabelDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
