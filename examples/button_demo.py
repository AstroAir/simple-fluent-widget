"""
Fluent Button Components Demo
Comprehensive example showcasing all button features and functionality
"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QGridLayout, QLabel, QGroupBox,
                               QScrollArea, QFrame, QLineEdit, QComboBox,
                               QCheckBox, QSpinBox, QSlider, QTextEdit, QSplitter)
from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor

# Import the button components
from components.basic.button import FluentButton, FluentIconButton, FluentToggleButton
from core.theme import theme_manager, ThemeMode


class ButtonDemo(QMainWindow):
    """Main demo window showcasing all button features"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Button Components Demo")
        self.setGeometry(100, 100, 1400, 900)

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
        title = QLabel("Fluent Button Components Demo")
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

        # Create splitter for better layout
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Button demos
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(self._create_basic_buttons_demo())
        left_layout.addWidget(self._create_icon_buttons_demo())
        left_layout.addWidget(self._create_toggle_buttons_demo())
        left_layout.addWidget(self._create_special_buttons_demo())
        left_layout.addStretch()

        # Right side - Interactive demo and event log
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(self._create_interactive_demo())
        right_layout.addWidget(self._create_event_log())

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([800, 600])

        main_layout.addWidget(splitter)

        # Event counter
        self.click_count = 0

    def _create_basic_buttons_demo(self) -> QGroupBox:
        """Create basic button styles demonstration"""
        group = QGroupBox("Basic Button Styles")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        # Button styles grid
        styles_layout = QGridLayout()

        # Style definitions
        button_styles = [
            ("Primary", FluentButton.ButtonStyle.PRIMARY, "Main action button"),
            ("Secondary", FluentButton.ButtonStyle.SECONDARY, "Secondary action"),
            ("Accent", FluentButton.ButtonStyle.ACCENT, "Highlighted action"),
            ("Subtle", FluentButton.ButtonStyle.SUBTLE, "Minimal action"),
            ("Outline", FluentButton.ButtonStyle.OUTLINE, "Outlined style")
        ]

        for i, (name, style, description) in enumerate(button_styles):
            # Container for each button demo
            container = QVBoxLayout()

            # Button
            button = FluentButton(name, style=style)
            button.clicked.connect(
                lambda checked, n=name: self._log_event(f"{n} button clicked"))

            # Description
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: gray; font-size: 11px;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            container.addWidget(button)
            container.addWidget(desc_label)

            # Create widget to hold the layout
            widget = QWidget()
            widget.setLayout(container)

            styles_layout.addWidget(widget, i // 3, i % 3)

        layout.addLayout(styles_layout)

        # Button states demo
        states_layout = QVBoxLayout()
        states_layout.addWidget(QLabel("Button States:"))

        states_buttons_layout = QHBoxLayout()

        # Normal button
        normal_btn = FluentButton(
            "Normal", style=FluentButton.ButtonStyle.PRIMARY)
        normal_btn.clicked.connect(
            lambda: self._log_event("Normal button clicked"))
        states_buttons_layout.addWidget(normal_btn)

        # Disabled button
        disabled_btn = FluentButton(
            "Disabled", style=FluentButton.ButtonStyle.PRIMARY)
        disabled_btn.setEnabled(False)
        states_buttons_layout.addWidget(disabled_btn)

        # Long text button
        long_btn = FluentButton(
            "Button with Very Long Text", style=FluentButton.ButtonStyle.SECONDARY)
        long_btn.clicked.connect(
            lambda: self._log_event("Long text button clicked"))
        states_buttons_layout.addWidget(long_btn)

        states_buttons_layout.addStretch()
        states_layout.addLayout(states_buttons_layout)
        layout.addLayout(states_layout)

        return group

    def _create_icon_buttons_demo(self) -> QGroupBox:
        """Create icon button demonstration"""
        group = QGroupBox("Icon Buttons")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        # Create some sample icons
        icons = self._create_sample_icons()

        # Icon buttons with different styles
        icon_styles_layout = QVBoxLayout()
        icon_styles_layout.addWidget(
            QLabel("Icon Buttons with Different Styles:"))

        icon_buttons_layout = QHBoxLayout()

        for i, (name, style) in enumerate([
            ("Save", FluentButton.ButtonStyle.PRIMARY),
            ("Edit", FluentButton.ButtonStyle.SECONDARY),
            ("Delete", FluentButton.ButtonStyle.ACCENT),
            ("Settings", FluentButton.ButtonStyle.OUTLINE)
        ]):
            icon_btn = FluentIconButton(
                icons[i % len(icons)], name, style=style)
            icon_btn.clicked.connect(
                lambda checked, n=name: self._log_event(f"Icon button '{n}' clicked"))
            icon_buttons_layout.addWidget(icon_btn)

        icon_buttons_layout.addStretch()
        icon_styles_layout.addLayout(icon_buttons_layout)
        layout.addLayout(icon_styles_layout)

        # Icon-only buttons
        icon_only_layout = QVBoxLayout()
        icon_only_layout.addWidget(QLabel("Icon-Only Buttons:"))

        icon_only_buttons_layout = QHBoxLayout()

        for i, tooltip in enumerate(["Home", "Search", "Refresh", "Info", "Help"]):
            icon_btn = FluentIconButton(
                icons[i % len(icons)], style=FluentButton.ButtonStyle.SUBTLE)
            icon_btn.setToolTip(tooltip)
            icon_btn.clicked.connect(lambda checked, t=tooltip: self._log_event(
                f"Icon-only button '{t}' clicked"))
            icon_only_buttons_layout.addWidget(icon_btn)

        icon_only_buttons_layout.addStretch()
        icon_only_layout.addLayout(icon_only_buttons_layout)
        layout.addLayout(icon_only_layout)

        # Different icon sizes
        sizes_layout = QVBoxLayout()
        sizes_layout.addWidget(QLabel("Different Icon Sizes:"))

        sizes_buttons_layout = QHBoxLayout()

        for size, label in [(16, "Small"), (24, "Medium"), (32, "Large")]:
            icon_btn = FluentIconButton(
                icons[0], f"{label} ({size}px)", style=FluentButton.ButtonStyle.SECONDARY)
            icon_btn.setIconSize(QSize(size, size))
            icon_btn.clicked.connect(
                lambda checked, s=size: self._log_event(f"Icon button {s}px clicked"))
            sizes_buttons_layout.addWidget(icon_btn)

        sizes_buttons_layout.addStretch()
        sizes_layout.addLayout(sizes_buttons_layout)
        layout.addLayout(sizes_layout)

        return group

    def _create_toggle_buttons_demo(self) -> QGroupBox:
        """Create toggle button demonstration"""
        group = QGroupBox("Toggle Buttons")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        # Basic toggle buttons
        basic_toggle_layout = QVBoxLayout()
        basic_toggle_layout.addWidget(QLabel("Basic Toggle Buttons:"))

        toggle_buttons_layout = QHBoxLayout()

        for name in ["Toggle A", "Toggle B", "Toggle C"]:
            toggle_btn = FluentToggleButton(name)
            toggle_btn.toggled.connect(lambda checked, n=name: self._log_event(
                f"Toggle '{n}' {'ON' if checked else 'OFF'}"))
            toggle_buttons_layout.addWidget(toggle_btn)

        toggle_buttons_layout.addStretch()
        basic_toggle_layout.addLayout(toggle_buttons_layout)
        layout.addLayout(basic_toggle_layout)

        # Toggle button group simulation
        group_layout = QVBoxLayout()
        group_layout.addWidget(
            QLabel("Toggle Button Group (Radio-like behavior):"))

        self.toggle_group = []
        group_buttons_layout = QHBoxLayout()

        for option in ["Option 1", "Option 2", "Option 3", "Option 4"]:
            toggle_btn = FluentToggleButton(option)
            toggle_btn.toggled.connect(
                lambda checked, btn=toggle_btn, opt=option: self._handle_group_toggle(btn, opt, checked))
            self.toggle_group.append(toggle_btn)
            group_buttons_layout.addWidget(toggle_btn)

        group_buttons_layout.addStretch()
        group_layout.addLayout(group_buttons_layout)
        layout.addLayout(group_layout)

        # Pre-selected toggle
        pre_selected_layout = QVBoxLayout()
        pre_selected_layout.addWidget(QLabel("Pre-selected Toggle:"))

        pre_selected_btn = FluentToggleButton("Pre-selected")
        pre_selected_btn.set_toggled(True)
        pre_selected_btn.toggled.connect(lambda checked: self._log_event(
            f"Pre-selected toggle {'ON' if checked else 'OFF'}"))
        pre_selected_layout.addWidget(pre_selected_btn)

        layout.addLayout(pre_selected_layout)

        return group

    def _create_special_buttons_demo(self) -> QGroupBox:
        """Create special button demonstrations"""
        group = QGroupBox("Special Buttons")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        # Loading button simulation
        loading_layout = QVBoxLayout()
        loading_layout.addWidget(QLabel("Loading Button Simulation:"))

        self.loading_btn = FluentButton(
            "Click to Load", style=FluentButton.ButtonStyle.PRIMARY)
        self.loading_btn.clicked.connect(self._simulate_loading)
        loading_layout.addWidget(self.loading_btn)
        layout.addLayout(loading_layout)

        # Confirmation button
        confirm_layout = QVBoxLayout()
        confirm_layout.addWidget(QLabel("Confirmation Button:"))

        self.confirm_btn = FluentButton(
            "Delete Item", style=FluentButton.ButtonStyle.ACCENT)
        self.confirm_btn.clicked.connect(self._handle_confirmation)
        self.confirm_state = "normal"  # normal, confirm, confirmed
        confirm_layout.addWidget(self.confirm_btn)
        layout.addLayout(confirm_layout)

        # Counter button
        counter_layout = QVBoxLayout()
        counter_layout.addWidget(QLabel("Counter Button:"))

        self.counter_btn = FluentButton(
            "Click Count: 0", style=FluentButton.ButtonStyle.SECONDARY)
        self.counter_btn.clicked.connect(self._increment_counter)
        counter_layout.addWidget(self.counter_btn)
        layout.addLayout(counter_layout)

        # Dynamic style button
        dynamic_layout = QVBoxLayout()
        dynamic_layout.addWidget(QLabel("Dynamic Style Button:"))

        self.dynamic_btn = FluentButton(
            "Cycle Styles", style=FluentButton.ButtonStyle.PRIMARY)
        self.dynamic_btn.clicked.connect(self._cycle_button_style)
        self.current_style_index = 0
        self.available_styles = [
            FluentButton.ButtonStyle.PRIMARY,
            FluentButton.ButtonStyle.SECONDARY,
            FluentButton.ButtonStyle.ACCENT,
            FluentButton.ButtonStyle.SUBTLE,
            FluentButton.ButtonStyle.OUTLINE
        ]
        dynamic_layout.addWidget(self.dynamic_btn)
        layout.addLayout(dynamic_layout)

        return group

    def _create_interactive_demo(self) -> QGroupBox:
        """Create interactive button customization demo"""
        group = QGroupBox("Interactive Button Demo")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        # Controls section
        controls_layout = QGridLayout()

        # Text input
        controls_layout.addWidget(QLabel("Button Text:"), 0, 0)
        self.text_input = QLineEdit("Custom Button")
        self.text_input.textChanged.connect(self._update_demo_button)
        controls_layout.addWidget(self.text_input, 0, 1)

        # Style selector
        controls_layout.addWidget(QLabel("Button Style:"), 1, 0)
        self.style_combo = QComboBox()
        self.style_combo.addItems(
            ["Primary", "Secondary", "Accent", "Subtle", "Outline"])
        self.style_combo.currentTextChanged.connect(self._update_demo_button)
        controls_layout.addWidget(self.style_combo, 1, 1)

        # Enabled checkbox
        self.enabled_checkbox = QCheckBox("Enabled")
        self.enabled_checkbox.setChecked(True)
        self.enabled_checkbox.toggled.connect(self._update_demo_button)
        controls_layout.addWidget(self.enabled_checkbox, 2, 0)

        # Icon checkbox
        self.icon_checkbox = QCheckBox("Show Icon")
        self.icon_checkbox.toggled.connect(self._update_demo_button)
        controls_layout.addWidget(self.icon_checkbox, 2, 1)

        layout.addLayout(controls_layout)

        # Demo button
        self.interactive_demo_actual_layout = QVBoxLayout()
        self.interactive_demo_actual_layout.addWidget(QLabel("Demo Button:"))

        self.demo_button = FluentButton(
            "Custom Button", style=FluentButton.ButtonStyle.PRIMARY)
        self.demo_button.clicked.connect(
            lambda: self._log_event("Demo button clicked"))
        self.interactive_demo_actual_layout.addWidget(self.demo_button)

        layout.addLayout(self.interactive_demo_actual_layout)

        # Button properties display
        props_layout = QVBoxLayout()
        props_layout.addWidget(QLabel("Button Properties:"))

        self.props_label = QLabel()
        self.props_label.setStyleSheet(
            "background-color: #f0f0f0; padding: 8px; border-radius: 4px; font-family: monospace;")
        self.props_label.setWordWrap(True)
        props_layout.addWidget(self.props_label)

        layout.addLayout(props_layout)

        # Update initial display
        self._update_demo_button()

        return group

    def _create_event_log(self) -> QGroupBox:
        """Create event log display"""
        group = QGroupBox("Event Log")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        # Clear button
        clear_btn = FluentButton(
            "Clear Log", style=FluentButton.ButtonStyle.SUBTLE)
        clear_btn.clicked.connect(self._clear_log)
        layout.addWidget(clear_btn)

        # Event log
        self.event_log = QTextEdit()
        self.event_log.setMaximumHeight(200)
        self.event_log.setReadOnly(True)
        layout.addWidget(self.event_log)

        return group

    def _create_sample_icons(self) -> list:
        """Create sample icons for demonstration"""
        icons = []
        colors = [
            QColor(52, 152, 219),   # Blue
            QColor(46, 204, 113),   # Green
            QColor(241, 196, 15),   # Yellow
            QColor(231, 76, 60),    # Red
            QColor(155, 89, 182),   # Purple
        ]

        for i, color in enumerate(colors):
            # Create a simple colored circle icon
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(2, 2, 20, 20)
            painter.end()

            icons.append(QIcon(pixmap))

        return icons

    def _toggle_theme(self, theme_name: str):
        """Toggle between light and dark themes"""
        if theme_name == "Dark":
            theme_manager.set_theme_mode(ThemeMode.DARK)
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)

    def _log_event(self, message: str):
        """Log an event to the event log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.event_log.append(f"[{timestamp}] {message}")

        # Auto-scroll to bottom
        cursor = self.event_log.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.event_log.setTextCursor(cursor)

    def _handle_group_toggle(self, clicked_btn: FluentToggleButton, option: str, checked: bool):
        """Handle toggle group behavior (radio-like)"""
        if checked:
            # Turn off other toggles in the group
            for btn in self.toggle_group:
                if btn != clicked_btn and btn.isChecked():
                    btn.set_toggled(False)
            self._log_event(f"Selected option: {option}")
        else:
            self._log_event(f"Deselected option: {option}")

    def _simulate_loading(self):
        """Simulate a loading operation"""
        self.loading_btn.setText("Loading...")
        self.loading_btn.setEnabled(False)
        self._log_event("Loading started")

        # Simulate async operation with timer
        QTimer.singleShot(2000, self._finish_loading)

    def _finish_loading(self):
        """Finish the loading simulation"""
        self.loading_btn.setText("Load Complete!")
        self.loading_btn.set_style(FluentButton.ButtonStyle.ACCENT)
        self._log_event("Loading completed")

        # Reset after a delay
        QTimer.singleShot(1500, self._reset_loading_button)

    def _reset_loading_button(self):
        """Reset the loading button"""
        self.loading_btn.setText("Click to Load")
        self.loading_btn.setEnabled(True)
        self.loading_btn.set_style(FluentButton.ButtonStyle.PRIMARY)

    def _handle_confirmation(self):
        """Handle confirmation button logic"""
        if self.confirm_state == "normal":
            self.confirm_btn.setText("Are you sure?")
            self.confirm_btn.set_style(FluentButton.ButtonStyle.OUTLINE)
            self.confirm_state = "confirm"
            self._log_event("Confirmation requested")

            # Reset after timeout
            QTimer.singleShot(3000, self._reset_confirm_button)

        elif self.confirm_state == "confirm":
            self.confirm_btn.setText("Deleted!")
            self.confirm_btn.set_style(FluentButton.ButtonStyle.ACCENT)
            self.confirm_btn.setEnabled(False)
            self.confirm_state = "confirmed"
            self._log_event("Item deleted")

            # Reset after delay
            QTimer.singleShot(2000, self._reset_confirm_button)

    def _reset_confirm_button(self):
        """Reset the confirmation button"""
        self.confirm_btn.setText("Delete Item")
        self.confirm_btn.set_style(FluentButton.ButtonStyle.ACCENT)
        self.confirm_btn.setEnabled(True)
        self.confirm_state = "normal"

    def _increment_counter(self):
        """Increment the counter button"""
        self.click_count += 1
        self.counter_btn.setText(f"Click Count: {self.click_count}")

        # Change style based on count
        if self.click_count % 5 == 0:
            self.counter_btn.set_style(FluentButton.ButtonStyle.ACCENT)
        else:
            self.counter_btn.set_style(FluentButton.ButtonStyle.SECONDARY)

        self._log_event(f"Counter incremented to {self.click_count}")

    def _cycle_button_style(self):
        """Cycle through different button styles"""
        self.current_style_index = (
            self.current_style_index + 1) % len(self.available_styles)
        new_style = self.available_styles[self.current_style_index]
        self.dynamic_btn.set_style(new_style)

        style_names = ["Primary", "Secondary", "Accent", "Subtle", "Outline"]
        self._log_event(
            f"Style changed to: {style_names[self.current_style_index]}")

    def _update_demo_button(self):
        """Update the demo button based on controls"""
        text = self.text_input.text()
        style_map = {
            "Primary": FluentButton.ButtonStyle.PRIMARY,
            "Secondary": FluentButton.ButtonStyle.SECONDARY,
            "Accent": FluentButton.ButtonStyle.ACCENT,
            "Subtle": FluentButton.ButtonStyle.SUBTLE,
            "Outline": FluentButton.ButtonStyle.OUTLINE
        }
        style = style_map[self.style_combo.currentText()]
        is_enabled = self.enabled_checkbox.isChecked()
        needs_icon_button = self.icon_checkbox.isChecked()

        current_button_is_icon_button = isinstance(
            self.demo_button, FluentIconButton)
        button_type_changed = (needs_icon_button and not current_button_is_icon_button) or \
                              (not needs_icon_button and current_button_is_icon_button)

        if button_type_changed:
            self.demo_button.deleteLater()  # Remove old button from layout

            if needs_icon_button:
                icons = self._create_sample_icons()
                self.demo_button = FluentIconButton(
                    icons[0], text, style=style)
            else:
                self.demo_button = FluentButton(text, style=style)

            self.demo_button.clicked.connect(
                lambda: self._log_event("Demo button clicked"))
            # Add new button to the stored layout (at index 1, after the label)
            self.interactive_demo_actual_layout.insertWidget(
                1, self.demo_button)
        else:
            # Button type is correct, just update its properties
            self.demo_button.setText(text)
            self.demo_button.set_style(style)

        # Update enabled state for the (potentially new) button
        self.demo_button.setEnabled(is_enabled)

        # Update properties display
        props_text = f"""
Text: "{text}"
Style: {self.style_combo.currentText()}
Enabled: {is_enabled}
Has Icon: {needs_icon_button}
Type: {type(self.demo_button).__name__}
        """.strip()
        self.props_label.setText(props_text)

    def _clear_log(self):
        """Clear the event log"""
        self.event_log.clear()
        self._log_event("Event log cleared")


def main():
    """Run the button demo application"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show demo window
    demo = ButtonDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
