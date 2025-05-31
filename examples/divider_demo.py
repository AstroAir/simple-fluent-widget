"""
Fluent Divider, Separator and Section Demo
Comprehensive example showcasing all features and functionality
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QGroupBox,
    QScrollArea, QFrame, QLineEdit, QSpinBox, QSlider,
    QCheckBox, QTextEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from core.theme import ThemeMode

# Import the divider components
from components.basic.divider import FluentDivider, FluentSeparator, FluentSection
from core.theme import theme_manager, ThemeMode


class DividerDemo(QMainWindow):
    """Main demo window showcasing all divider, separator and section features"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Divider, Separator & Section Demo")
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
        title = QLabel("Fluent Divider, Separator & Section Demo")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Theme toggle
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        if theme_manager._current_mode == ThemeMode.DARK:
            self.theme_combo.setCurrentText("Dark")
        else:
            self.theme_combo.setCurrentText("Light")
        self.theme_combo.currentTextChanged.connect(self._toggle_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        main_layout.addLayout(theme_layout)

        # Create demo sections
        main_layout.addWidget(self._create_basic_dividers_demo())
        main_layout.addWidget(self._create_styled_dividers_demo())
        main_layout.addWidget(self._create_text_dividers_demo())
        main_layout.addWidget(self._create_vertical_dividers_demo())
        main_layout.addWidget(self._create_sections_demo())
        main_layout.addWidget(self._create_interactive_demo())

        main_layout.addStretch()

    def _create_basic_dividers_demo(self) -> QGroupBox:
        """Create basic dividers demonstration section"""
        group = QGroupBox("Basic Dividers")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(20)

        # Simple horizontal dividers
        layout.addWidget(QLabel("Simple Horizontal Dividers:"))

        content1 = QLabel("Content above the divider")
        layout.addWidget(content1)

        basic_divider = FluentDivider()
        layout.addWidget(basic_divider)

        content2 = QLabel("Content below the divider")
        layout.addWidget(content2)

        # Another divider with different margin
        layout.addWidget(QLabel("Divider with custom margin (8px):"))

        content3 = QLabel("Content with smaller margin divider")
        layout.addWidget(content3)

        margin_divider = FluentDivider()
        margin_divider.setMargin(8)
        layout.addWidget(margin_divider)

        content4 = QLabel("Content after smaller margin divider")
        layout.addWidget(content4)

        # Separator alias demonstration
        layout.addWidget(QLabel("FluentSeparator (alias for FluentDivider):"))

        content5 = QLabel("Using FluentSeparator instead of FluentDivider")
        layout.addWidget(content5)

        separator = FluentSeparator()
        layout.addWidget(separator)

        content6 = QLabel("Functionally identical to FluentDivider")
        layout.addWidget(content6)

        return group

    def _create_styled_dividers_demo(self) -> QGroupBox:
        """Create styled dividers demonstration section"""
        group = QGroupBox("Divider Styles & Thickness")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Different styles
        styles_data = [
            ("Solid Style (Default)", FluentDivider.Style.SOLID),
            ("Dashed Style", FluentDivider.Style.DASHED),
            ("Dotted Style", FluentDivider.Style.DOTTED),
            ("Gradient Style", FluentDivider.Style.GRADIENT),
            ("Double Style", FluentDivider.Style.DOUBLE)
        ]

        for style_name, style_enum in styles_data:
            layout.addWidget(QLabel(style_name))

            styled_divider = FluentDivider()
            styled_divider.setDividerStyle(style_enum)
            layout.addWidget(styled_divider)

        # Different thickness
        layout.addWidget(QLabel("Different Thickness:"))

        thicknesses = [1, 2, 3, 5, 8]
        for thickness in thicknesses:
            layout.addWidget(QLabel(f"Thickness: {thickness}px"))

            thick_divider = FluentDivider()
            thick_divider.setThickness(thickness)
            layout.addWidget(thick_divider)

        # Custom colors
        layout.addWidget(QLabel("Custom Colors:"))

        colors = [
            ("Red", QColor(255, 0, 0)),
            ("Green", QColor(0, 255, 0)),
            ("Blue", QColor(0, 0, 255)),
            ("Purple", QColor(128, 0, 128)),
            ("Orange", QColor(255, 165, 0))
        ]

        for color_name, color in colors:
            layout.addWidget(QLabel(f"{color_name} Divider"))

            colored_divider = FluentDivider()
            colored_divider.setColor(color)
            colored_divider.setThickness(2)
            layout.addWidget(colored_divider)

        return group

    def _create_text_dividers_demo(self) -> QGroupBox:
        """Create text dividers demonstration section"""
        group = QGroupBox("Dividers with Text")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Text positions
        text_positions = [
            ("Left aligned text", 0.0),
            ("Center aligned text", 0.5),
            ("Right aligned text", 1.0),
            ("Quarter position text", 0.25),
            ("Three-quarter position text", 0.75)
        ]

        for text, position in text_positions:
            layout.addWidget(QLabel(f"Text Position: {position} ({text})"))

            text_divider = FluentDivider()
            text_divider.setText(text)
            text_divider.setTextPosition(position)
            layout.addWidget(text_divider)

        # Text with different styles
        layout.addWidget(QLabel("Text with Different Divider Styles:"))

        style_text_combinations = [
            ("Solid with Text", FluentDivider.Style.SOLID),
            ("Dashed with Text", FluentDivider.Style.DASHED),
            ("Dotted with Text", FluentDivider.Style.DOTTED),
            ("Gradient with Text", FluentDivider.Style.GRADIENT),
            ("Double with Text", FluentDivider.Style.DOUBLE)
        ]

        for text, style in style_text_combinations:
            styled_text_divider = FluentDivider()
            styled_text_divider.setText(text)
            styled_text_divider.setDividerStyle(style)
            styled_text_divider.setThickness(2)
            layout.addWidget(styled_text_divider)

        return group

    def _create_vertical_dividers_demo(self) -> QGroupBox:
        """Create vertical dividers demonstration section"""
        group = QGroupBox("Vertical Dividers")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Horizontal layout for vertical dividers
        layout.addWidget(QLabel("Vertical Dividers in Horizontal Layout:"))

        vertical_demo_layout = QHBoxLayout()

        # Content sections separated by vertical dividers
        content_sections = [
            "Section 1\nThis is the first\ncontent section",
            "Section 2\nThis is the second\ncontent section",
            "Section 3\nThis is the third\ncontent section",
            "Section 4\nThis is the fourth\ncontent section"
        ]

        for i, content in enumerate(content_sections):
            # Add content
            content_label = QLabel(content)
            content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_label.setStyleSheet(
                "padding: 10px; border: 1px solid lightgray; border-radius: 4px;")
            vertical_demo_layout.addWidget(content_label)

            # Add vertical divider (except after last section)
            if i < len(content_sections) - 1:
                vertical_divider = FluentDivider(
                    FluentDivider.Orientation.VERTICAL)
                vertical_divider.setThickness(2)
                vertical_demo_layout.addWidget(vertical_divider)

        layout.addLayout(vertical_demo_layout)

        # Different vertical divider styles
        layout.addWidget(QLabel("Different Vertical Divider Styles:"))

        vertical_styles_layout = QHBoxLayout()

        for style_name, style_enum in [
            ("Solid", FluentDivider.Style.SOLID),
            ("Dashed", FluentDivider.Style.DASHED),
            ("Dotted", FluentDivider.Style.DOTTED),
            ("Gradient", FluentDivider.Style.GRADIENT),
            ("Double", FluentDivider.Style.DOUBLE)
        ]:
            # Content
            style_label = QLabel(f"{style_name}\nVertical\nDivider")
            style_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vertical_styles_layout.addWidget(style_label)

            # Vertical divider with style
            if style_name != "Double":  # Skip divider after last item
                v_divider = FluentDivider(FluentDivider.Orientation.VERTICAL)
                v_divider.setDividerStyle(style_enum)
                v_divider.setThickness(3)
                vertical_styles_layout.addWidget(v_divider)

        layout.addLayout(vertical_styles_layout)

        return group

    def _create_sections_demo(self) -> QGroupBox:
        """Create FluentSection demonstration"""
        group = QGroupBox("FluentSection Components")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(20)

        # Basic sections
        section1 = FluentSection(
            "Getting Started", "This section explains the basic concepts")
        layout.addWidget(section1)

        # Add some content after section1
        content_after_section1 = QLabel(
            "Content that belongs to the 'Getting Started' section")
        content_after_section1.setStyleSheet(
            "padding: 10px; background-color: rgba(0, 100, 200, 0.1); border-radius: 4px;")
        layout.addWidget(content_after_section1)

        section2 = FluentSection(
            "Advanced Features", "Explore more complex functionality and customization options")
        layout.addWidget(section2)

        # Add some content after section2
        content_after_section2 = QLabel(
            "Advanced content with more detailed information and examples")
        content_after_section2.setStyleSheet(
            "padding: 10px; background-color: rgba(200, 100, 0, 0.1); border-radius: 4px;")
        layout.addWidget(content_after_section2)

        section3 = FluentSection("Configuration")
        layout.addWidget(section3)

        # Add some content after section3
        content_after_section3 = QLabel("Configuration settings and options")
        content_after_section3.setStyleSheet(
            "padding: 10px; background-color: rgba(0, 200, 100, 0.1); border-radius: 4px;")
        layout.addWidget(content_after_section3)

        # Section with only title (no description)
        section4 = FluentSection(
            "", "This section has description but no title")
        layout.addWidget(section4)

        # Add some content after section4
        content_after_section4 = QLabel(
            "Content under a section with description only")
        content_after_section4.setStyleSheet(
            "padding: 10px; background-color: rgba(200, 0, 100, 0.1); border-radius: 4px;")
        layout.addWidget(content_after_section4)

        # Empty section (just divider)
        section5 = FluentSection()
        layout.addWidget(section5)

        return group

    def _create_interactive_demo(self) -> QGroupBox:
        """Create interactive demonstration section"""
        group = QGroupBox("Interactive Demo & Customization")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Interactive divider customization
        layout.addWidget(QLabel("Customize Divider Properties:"))

        # Create the demo divider
        self.demo_divider = FluentDivider()
        self.demo_divider.setText("Demo Divider")

        # Controls grid
        controls_layout = QGridLayout()

        # Orientation control
        controls_layout.addWidget(QLabel("Orientation:"), 0, 0)
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["Horizontal", "Vertical"])
        self.orientation_combo.currentTextChanged.connect(
            self._update_demo_divider_orientation)
        controls_layout.addWidget(self.orientation_combo, 0, 1)

        # Style control
        controls_layout.addWidget(QLabel("Style:"), 1, 0)
        self.style_combo = QComboBox()
        self.style_combo.addItems(
            ["Solid", "Dashed", "Dotted", "Gradient", "Double"])
        self.style_combo.currentTextChanged.connect(
            self._update_demo_divider_style)
        controls_layout.addWidget(self.style_combo, 1, 1)

        # Thickness control
        controls_layout.addWidget(QLabel("Thickness:"), 2, 0)
        self.thickness_spinbox = QSpinBox()
        self.thickness_spinbox.setRange(1, 10)
        self.thickness_spinbox.setValue(1)
        self.thickness_spinbox.valueChanged.connect(
            self._update_demo_divider_thickness)
        controls_layout.addWidget(self.thickness_spinbox, 2, 1)

        # Margin control
        controls_layout.addWidget(QLabel("Margin:"), 3, 0)
        self.margin_spinbox = QSpinBox()
        self.margin_spinbox.setRange(0, 50)
        self.margin_spinbox.setValue(16)
        self.margin_spinbox.valueChanged.connect(
            self._update_demo_divider_margin)
        controls_layout.addWidget(self.margin_spinbox, 3, 1)

        # Text control
        controls_layout.addWidget(QLabel("Text:"), 0, 2)
        self.text_input = QLineEdit()
        self.text_input.setText("Demo Divider")
        self.text_input.textChanged.connect(self._update_demo_divider_text)
        controls_layout.addWidget(self.text_input, 0, 3)

        # Text position control
        controls_layout.addWidget(QLabel("Text Position:"), 1, 2)
        self.text_position_slider = QSlider(Qt.Orientation.Horizontal)
        self.text_position_slider.setRange(0, 100)
        self.text_position_slider.setValue(50)
        self.text_position_slider.valueChanged.connect(
            self._update_demo_divider_text_position)
        controls_layout.addWidget(self.text_position_slider, 1, 3)

        # Color controls
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))

        self.use_theme_color_cb = QCheckBox("Use Theme Color")
        self.use_theme_color_cb.setChecked(True)
        self.use_theme_color_cb.toggled.connect(
            self._update_demo_divider_color)
        color_layout.addWidget(self.use_theme_color_cb)

        color_buttons = [
            ("Red", QColor(255, 0, 0)),
            ("Green", QColor(0, 255, 0)),
            ("Blue", QColor(0, 0, 255)),
            ("Purple", QColor(128, 0, 128)),
            ("Orange", QColor(255, 165, 0))
        ]

        for color_name, color in color_buttons:
            color_btn = QPushButton(color_name)
            color_btn.clicked.connect(
                lambda checked, c=color: self._set_demo_divider_color(c))
            color_layout.addWidget(color_btn)

        color_layout.addStretch()
        controls_layout.addLayout(color_layout, 2, 2, 1, 2)

        layout.addLayout(controls_layout)

        # Demo divider container
        demo_container = QFrame()
        demo_container.setStyleSheet(
            "border: 1px dashed gray; padding: 20px; border-radius: 4px;")
        demo_layout = QVBoxLayout(demo_container)

        demo_layout.addWidget(QLabel("Content above demo divider"))
        demo_layout.addWidget(self.demo_divider)
        demo_layout.addWidget(QLabel("Content below demo divider"))

        layout.addWidget(demo_container)

        # Interactive section customization
        layout.addWidget(QLabel("Customize Section Properties:"))

        # Section controls
        section_controls_layout = QHBoxLayout()

        self.section_title_input = QLineEdit()
        self.section_title_input.setPlaceholderText("Section Title")
        self.section_title_input.textChanged.connect(self._update_demo_section)

        self.section_desc_input = QLineEdit()
        self.section_desc_input.setPlaceholderText("Section Description")
        self.section_desc_input.textChanged.connect(self._update_demo_section)

        section_controls_layout.addWidget(QLabel("Title:"))
        section_controls_layout.addWidget(self.section_title_input)
        section_controls_layout.addWidget(QLabel("Description:"))
        section_controls_layout.addWidget(self.section_desc_input)

        layout.addLayout(section_controls_layout)

        # Demo section
        self.demo_section = FluentSection(
            "Demo Section", "This is a customizable demo section")
        layout.addWidget(self.demo_section)

        # Content after demo section
        demo_section_content = QLabel(
            "Content that belongs to the demo section")
        demo_section_content.setStyleSheet(
            "padding: 15px; background-color: rgba(100, 100, 100, 0.1); border-radius: 4px;")
        layout.addWidget(demo_section_content)

        # Performance test
        layout.addWidget(QLabel("Performance Test:"))

        perf_layout = QHBoxLayout()

        self.create_many_btn = QPushButton("Create 50 Dividers")
        self.create_many_btn.clicked.connect(self._create_many_dividers)

        self.clear_many_btn = QPushButton("Clear Performance Test")
        self.clear_many_btn.clicked.connect(self._clear_many_dividers)

        perf_layout.addWidget(self.create_many_btn)
        perf_layout.addWidget(self.clear_many_btn)
        perf_layout.addStretch()

        layout.addLayout(perf_layout)

        # Container for many dividers
        self.many_dividers_container = QWidget()
        self.many_dividers_layout = QVBoxLayout(self.many_dividers_container)
        layout.addWidget(self.many_dividers_container)

        return group

    def _update_demo_divider_orientation(self, orientation_text: str):
        """Update demo divider orientation"""
        if orientation_text == "Horizontal":
            self.demo_divider.setOrientation(
                FluentDivider.Orientation.HORIZONTAL)
        else:
            self.demo_divider.setOrientation(
                FluentDivider.Orientation.VERTICAL)

    def _update_demo_divider_style(self, style_text: str):
        """Update demo divider style"""
        style_map = {
            "Solid": FluentDivider.Style.SOLID,
            "Dashed": FluentDivider.Style.DASHED,
            "Dotted": FluentDivider.Style.DOTTED,
            "Gradient": FluentDivider.Style.GRADIENT,
            "Double": FluentDivider.Style.DOUBLE
        }
        if style_text in style_map:
            self.demo_divider.setDividerStyle(style_map[style_text])

    def _update_demo_divider_thickness(self, thickness: int):
        """Update demo divider thickness"""
        self.demo_divider.setThickness(thickness)

    def _update_demo_divider_margin(self, margin: int):
        """Update demo divider margin"""
        self.demo_divider.setMargin(margin)

    def _update_demo_divider_text(self, text: str):
        """Update demo divider text"""
        self.demo_divider.setText(text)

    def _update_demo_divider_text_position(self, value: int):
        """Update demo divider text position"""
        position = value / 100.0  # Convert 0-100 to 0.0-1.0
        self.demo_divider.setTextPosition(position)

    def _update_demo_divider_color(self, use_theme: bool):
        """Update demo divider color"""
        if use_theme:
            # Reset to theme color by passing empty QColor
            self.demo_divider.setColor(QColor())

    def _set_demo_divider_color(self, color: QColor):
        """Set demo divider to specific color"""
        self.use_theme_color_cb.setChecked(False)
        self.demo_divider.setColor(color)

    def _update_demo_section(self):
        """Update demo section properties"""
        title = self.section_title_input.text()
        description = self.section_desc_input.text()

        self.demo_section.setTitle(title)
        self.demo_section.setDescription(description)

    def _create_many_dividers(self):
        """Create many dividers for performance testing"""
        self._clear_many_dividers()  # Clear existing first

        for i in range(50):
            if i % 10 == 0:
                # Create a section every 10 dividers
                section = FluentSection(
                    f"Section {i//10 + 1}", f"Performance test section {i//10 + 1}")
                self.many_dividers_layout.addWidget(section)
            else:
                # Create different types of dividers
                divider = FluentDivider()

                # Vary properties
                styles = [FluentDivider.Style.SOLID, FluentDivider.Style.DASHED,
                          FluentDivider.Style.DOTTED, FluentDivider.Style.GRADIENT]
                divider.setDividerStyle(styles[i % len(styles)])
                divider.setThickness((i % 3) + 1)

                if i % 5 == 0:
                    divider.setText(f"Divider {i}")

                self.many_dividers_layout.addWidget(divider)

    def _clear_many_dividers(self):
        """Clear all performance test dividers"""
        # Remove all widgets from the container
        while self.many_dividers_layout.count():
            child = self.many_dividers_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _toggle_theme(self, theme_name: str):
        """Toggle between light and dark themes"""
        if theme_name == "Dark":
            theme_manager.set_theme_mode(ThemeMode.DARK)
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)


def main():
    """Run the divider demo application"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show demo window
    demo = DividerDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
