"""
Fluent Badge, Tag and Status Indicator Demo
Comprehensive example showcasing all features and functionality
"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QGridLayout, QLabel, QPushButton,
                               QSpinBox, QComboBox, QCheckBox, QGroupBox,
                               QScrollArea, QFrame, QLineEdit, QSlider)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

# Import the badge components
from components.basic.badge import FluentBadge, FluentTag, FluentStatusIndicator
from core.theme import theme_manager


class BadgeTagDemo(QMainWindow):
    """Main demo window showcasing all badge and tag features"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Badge, Tag & Status Indicator Demo")
        self.setGeometry(100, 100, 1200, 800)

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
        title = QLabel("Fluent Badge, Tag & Status Indicator Demo")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Theme toggle
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self._toggle_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        main_layout.addLayout(theme_layout)

        # Create demo sections
        main_layout.addWidget(self._create_badge_demo())
        main_layout.addWidget(self._create_tag_demo())
        main_layout.addWidget(self._create_status_demo())
        main_layout.addWidget(self._create_interactive_demo())

        main_layout.addStretch()

    def _create_badge_demo(self) -> QGroupBox:
        """Create badge demonstration section"""
        group = QGroupBox("Badge Components")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        # Basic badges
        basic_layout = QVBoxLayout()
        basic_layout.addWidget(QLabel("Basic Badge Types:"))

        badge_types_layout = QHBoxLayout()
        badge_types = [
            ("Default", FluentBadge.BadgeType.DEFAULT),
            ("Info", FluentBadge.BadgeType.INFO),
            ("Success", FluentBadge.BadgeType.SUCCESS),
            ("Warning", FluentBadge.BadgeType.WARNING),
            ("Error", FluentBadge.BadgeType.ERROR)
        ]

        for name, badge_type in badge_types:
            container = QVBoxLayout()
            badge = FluentBadge(badge_type=badge_type, text=name)
            label = QLabel(name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container.addWidget(badge)
            container.addWidget(label)

            widget = QWidget()
            widget.setLayout(container)
            badge_types_layout.addWidget(widget)

        badge_types_layout.addStretch()
        basic_layout.addLayout(badge_types_layout)
        layout.addLayout(basic_layout)

        # Number badges
        number_layout = QVBoxLayout()
        number_layout.addWidget(QLabel("Number Badges:"))

        number_badges_layout = QHBoxLayout()
        numbers = ["1", "9", "99", "999+"]
        for num in numbers:
            container = QVBoxLayout()
            badge = FluentBadge(
                badge_type=FluentBadge.BadgeType.ERROR, text=num)
            label = QLabel(f"Count: {num}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container.addWidget(badge)
            container.addWidget(label)

            widget = QWidget()
            widget.setLayout(container)
            number_badges_layout.addWidget(widget)

        number_badges_layout.addStretch()
        number_layout.addLayout(number_badges_layout)
        layout.addLayout(number_layout)

        # Dot badges
        dot_layout = QVBoxLayout()
        dot_layout.addWidget(QLabel("Dot Mode Badges:"))

        dot_badges_layout = QHBoxLayout()
        for name, badge_type in badge_types:
            container = QVBoxLayout()
            badge = FluentBadge(badge_type=badge_type, dot=True)
            label = QLabel(name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container.addWidget(badge)
            container.addWidget(label)

            widget = QWidget()
            widget.setLayout(container)
            dot_badges_layout.addWidget(widget)

        dot_badges_layout.addStretch()
        dot_layout.addLayout(dot_badges_layout)
        layout.addLayout(dot_layout)

        return group

    def _create_tag_demo(self) -> QGroupBox:
        """Create tag demonstration section"""
        group = QGroupBox("Tag Components")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        # Tag variants
        variants_layout = QVBoxLayout()
        variants_layout.addWidget(QLabel("Tag Variants:"))

        tag_variants_layout = QHBoxLayout()
        variants = [
            ("Default", FluentTag.TagVariant.DEFAULT),
            ("Outline", FluentTag.TagVariant.OUTLINE),
            ("Filled", FluentTag.TagVariant.FILLED)
        ]

        for name, variant in variants:
            container = QVBoxLayout()
            tag = FluentTag(text=name, variant=variant)
            tag.clicked.connect(lambda v=name: self._on_tag_clicked(v))
            label = QLabel(f"{name} Tag")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container.addWidget(tag)
            container.addWidget(label)

            widget = QWidget()
            widget.setLayout(container)
            tag_variants_layout.addWidget(widget)

        tag_variants_layout.addStretch()
        variants_layout.addLayout(tag_variants_layout)
        layout.addLayout(variants_layout)

        # Closable tags
        closable_layout = QVBoxLayout()
        closable_layout.addWidget(QLabel("Closable Tags:"))

        self.closable_tags_layout = QHBoxLayout()
        tag_texts = ["Python", "JavaScript", "C++", "React", "PySide6"]

        for text in tag_texts:
            tag = FluentTag(
                text=text, variant=FluentTag.TagVariant.OUTLINE, closable=True)
            tag.closed.connect(lambda t=tag: self._on_tag_closed(t))
            tag.clicked.connect(lambda txt=text: self._on_tag_clicked(txt))
            self.closable_tags_layout.addWidget(tag)

        self.closable_tags_layout.addStretch()
        closable_layout.addLayout(self.closable_tags_layout)
        layout.addLayout(closable_layout)

        # Custom colored tags
        colored_layout = QVBoxLayout()
        colored_layout.addWidget(QLabel("Custom Colored Tags:"))

        colored_tags_layout = QHBoxLayout()
        colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#feca57"]
        color_names = ["Red", "Teal", "Blue", "Green", "Yellow"]

        for color, name in zip(colors, color_names):
            tag = FluentTag(text=name, variant=FluentTag.TagVariant.FILLED)
            tag.setColor(color)
            tag.clicked.connect(lambda n=name: self._on_tag_clicked(n))
            colored_tags_layout.addWidget(tag)

        colored_tags_layout.addStretch()
        colored_layout.addLayout(colored_tags_layout)
        layout.addLayout(colored_layout)

        return group

    def _create_status_demo(self) -> QGroupBox:
        """Create status indicator demonstration section"""
        group = QGroupBox("Status Indicators")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        # Status types
        status_layout = QVBoxLayout()
        status_layout.addWidget(QLabel("Status Types:"))

        status_indicators_layout = QHBoxLayout()
        statuses = [
            ("Online", FluentStatusIndicator.Status.ONLINE),
            ("Offline", FluentStatusIndicator.Status.OFFLINE),
            ("Busy", FluentStatusIndicator.Status.BUSY),
            ("Away", FluentStatusIndicator.Status.AWAY),
            ("Unknown", FluentStatusIndicator.Status.UNKNOWN)
        ]

        for name, status in statuses:
            container = QVBoxLayout()
            indicator = FluentStatusIndicator(status=status, size=16)
            label = QLabel(name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container.addWidget(indicator)
            container.addWidget(label)

            widget = QWidget()
            widget.setLayout(container)
            status_indicators_layout.addWidget(widget)

        status_indicators_layout.addStretch()
        status_layout.addLayout(status_indicators_layout)
        layout.addLayout(status_layout)

        # Different sizes
        sizes_layout = QVBoxLayout()
        sizes_layout.addWidget(QLabel("Different Sizes (Online Status):"))

        size_indicators_layout = QHBoxLayout()
        sizes = [8, 12, 16, 20, 24]

        for size in sizes:
            container = QVBoxLayout()
            indicator = FluentStatusIndicator(
                status=FluentStatusIndicator.Status.ONLINE, size=size)
            label = QLabel(f"{size}px")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container.addWidget(indicator)
            container.addWidget(label)

            widget = QWidget()
            widget.setLayout(container)
            size_indicators_layout.addWidget(widget)

        size_indicators_layout.addStretch()
        sizes_layout.addLayout(size_indicators_layout)
        layout.addLayout(sizes_layout)

        return group

    def _create_interactive_demo(self) -> QGroupBox:
        """Create interactive demonstration section"""
        group = QGroupBox("Interactive Demo")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        # Badge customization
        badge_section = QHBoxLayout()

        # Controls
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(QLabel("Badge Controls:"))

        # Badge type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.badge_type_combo = QComboBox()
        self.badge_type_combo.addItems(
            ["Default", "Info", "Success", "Warning", "Error"])
        self.badge_type_combo.currentTextChanged.connect(
            self._update_demo_badge)
        type_layout.addWidget(self.badge_type_combo)
        controls_layout.addLayout(type_layout)

        # Badge text input
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text:"))
        self.badge_text_input = QLineEdit("Demo")
        self.badge_text_input.textChanged.connect(self._update_demo_badge)
        text_layout.addWidget(self.badge_text_input)
        controls_layout.addLayout(text_layout)

        # Dot mode checkbox
        self.dot_mode_checkbox = QCheckBox("Dot Mode")
        self.dot_mode_checkbox.toggled.connect(self._update_demo_badge)
        controls_layout.addWidget(self.dot_mode_checkbox)

        badge_section.addLayout(controls_layout)

        # Demo badge
        demo_layout = QVBoxLayout()
        demo_layout.addWidget(QLabel("Demo Badge:"))
        self.demo_badge = FluentBadge(text="Demo")
        demo_layout.addWidget(self.demo_badge)
        demo_layout.addStretch()

        badge_section.addLayout(demo_layout)
        badge_section.addStretch()

        layout.addLayout(badge_section)

        # Tag customization
        tag_section = QHBoxLayout()

        # Tag controls
        tag_controls_layout = QVBoxLayout()
        tag_controls_layout.addWidget(QLabel("Tag Controls:"))

        # Tag variant selector
        variant_layout = QHBoxLayout()
        variant_layout.addWidget(QLabel("Variant:"))
        self.tag_variant_combo = QComboBox()
        self.tag_variant_combo.addItems(["Default", "Outline", "Filled"])
        self.tag_variant_combo.currentTextChanged.connect(
            self._update_demo_tag)
        variant_layout.addWidget(self.tag_variant_combo)
        tag_controls_layout.addLayout(variant_layout)

        # Tag text input
        tag_text_layout = QHBoxLayout()
        tag_text_layout.addWidget(QLabel("Text:"))
        self.tag_text_input = QLineEdit("Demo Tag")
        self.tag_text_input.textChanged.connect(self._update_demo_tag)
        tag_text_layout.addWidget(self.tag_text_input)
        tag_controls_layout.addLayout(tag_text_layout)

        # Closable checkbox
        self.closable_checkbox = QCheckBox("Closable")
        self.closable_checkbox.toggled.connect(self._recreate_demo_tag)
        tag_controls_layout.addWidget(self.closable_checkbox)

        tag_section.addLayout(tag_controls_layout)

        # Demo tag container
        self.demo_tag_layout = QVBoxLayout()
        self.demo_tag_layout.addWidget(QLabel("Demo Tag:"))
        self.demo_tag = FluentTag(text="Demo Tag")
        self.demo_tag.clicked.connect(lambda: print("Demo tag clicked!"))
        self.demo_tag_layout.addWidget(self.demo_tag)
        self.demo_tag_layout.addStretch()

        tag_section.addLayout(self.demo_tag_layout)
        tag_section.addStretch()

        layout.addLayout(tag_section)

        # Status customization
        status_section = QHBoxLayout()

        # Status controls
        status_controls_layout = QVBoxLayout()
        status_controls_layout.addWidget(QLabel("Status Controls:"))

        # Status selector
        status_select_layout = QHBoxLayout()
        status_select_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(
            ["Online", "Offline", "Busy", "Away", "Unknown"])
        self.status_combo.currentTextChanged.connect(self._update_demo_status)
        status_select_layout.addWidget(self.status_combo)
        status_controls_layout.addLayout(status_select_layout)

        # Size slider
        size_layout = QVBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(8, 32)
        self.size_slider.setValue(16)
        self.size_slider.valueChanged.connect(self._update_demo_status)
        self.size_label = QLabel("16px")
        size_layout.addWidget(self.size_slider)
        size_layout.addWidget(self.size_label)
        status_controls_layout.addLayout(size_layout)

        status_section.addLayout(status_controls_layout)

        # Demo status
        demo_status_layout = QVBoxLayout()
        demo_status_layout.addWidget(QLabel("Demo Status:"))
        self.demo_status = FluentStatusIndicator(
            status=FluentStatusIndicator.Status.ONLINE, size=16)
        demo_status_layout.addWidget(self.demo_status)
        demo_status_layout.addStretch()

        status_section.addLayout(demo_status_layout)
        status_section.addStretch()

        layout.addLayout(status_section)

        return group

    def _toggle_theme(self, theme_name: str):
        """Toggle between light and dark themes"""
        from core.theme import ThemeMode
        if theme_name == "Dark":
            theme_manager.set_theme_mode(ThemeMode.DARK)
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)

    def _on_tag_clicked(self, tag_name: str):
        """Handle tag click events"""
        print(f"Tag '{tag_name}' was clicked!")

    def _on_tag_closed(self, tag: FluentTag):
        """Handle tag close events"""
        print(f"Tag '{tag._text}' was closed!")
        tag.deleteLater()

    def _update_demo_badge(self):
        """Update the demo badge based on controls"""
        badge_type = self.badge_type_combo.currentText().lower()
        text = self.badge_text_input.text()
        dot_mode = self.dot_mode_checkbox.isChecked()

        type_map = {
            "default": FluentBadge.BadgeType.DEFAULT,
            "info": FluentBadge.BadgeType.INFO,
            "success": FluentBadge.BadgeType.SUCCESS,
            "warning": FluentBadge.BadgeType.WARNING,
            "error": FluentBadge.BadgeType.ERROR
        }

        self.demo_badge.setBadgeType(type_map[badge_type])
        self.demo_badge.setText(text)
        self.demo_badge.setDotMode(dot_mode)

    def _update_demo_tag(self):
        """Update the demo tag based on controls"""
        if hasattr(self, 'demo_tag') and self.demo_tag:
            variant = self.tag_variant_combo.currentText().lower()
            text = self.tag_text_input.text()

            variant_map = {
                "default": FluentTag.TagVariant.DEFAULT,
                "outline": FluentTag.TagVariant.OUTLINE,
                "filled": FluentTag.TagVariant.FILLED
            }

            self.demo_tag.setVariant(variant_map[variant])
            self.demo_tag.setText(text)

    def _recreate_demo_tag(self):
        """Recreate demo tag when closable option changes"""
        if hasattr(self, 'demo_tag') and self.demo_tag:
            self.demo_tag.deleteLater()

        variant = self.tag_variant_combo.currentText().lower()
        text = self.tag_text_input.text()
        closable = self.closable_checkbox.isChecked()

        variant_map = {
            "default": FluentTag.TagVariant.DEFAULT,
            "outline": FluentTag.TagVariant.OUTLINE,
            "filled": FluentTag.TagVariant.FILLED
        }

        self.demo_tag = FluentTag(
            text=text, variant=variant_map[variant], closable=closable)
        self.demo_tag.clicked.connect(lambda: print("Demo tag clicked!"))
        if closable:
            self.demo_tag.closed.connect(lambda: print("Demo tag closed!"))

        self.demo_tag_layout.insertWidget(1, self.demo_tag)

    def _update_demo_status(self):
        """Update the demo status indicator based on controls"""
        status_name = self.status_combo.currentText().lower()
        size = self.size_slider.value()

        status_map = {
            "online": FluentStatusIndicator.Status.ONLINE,
            "offline": FluentStatusIndicator.Status.OFFLINE,
            "busy": FluentStatusIndicator.Status.BUSY,
            "away": FluentStatusIndicator.Status.AWAY,
            "unknown": FluentStatusIndicator.Status.UNKNOWN
        }

        self.demo_status.setStatus(status_map[status_name])
        self.demo_status.setSize(size)
        self.size_label.setText(f"{size}px")


def main():
    """Run the badge demo application"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show demo window
    demo = BadgeTagDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
