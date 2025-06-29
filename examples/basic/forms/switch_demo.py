"""
Fluent Switch Components Demo
Comprehensive example showcasing all switch components and features
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QGroupBox,
    QScrollArea, QLineEdit, QSpinBox, QCheckBox, QTextEdit,
    QTabWidget, QFormLayout, QButtonGroup, QRadioButton
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter

# Import the switch components
from components.basic.forms.switch import FluentSwitch, FluentSwitchGroup
from core.theme import theme_manager, ThemeMode


class SwitchDemo(QMainWindow):
    """Main demo window showcasing all switch components"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Switch Components Demo")
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
        title = QLabel("Fluent Switch Components Demo")
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

        # Create demo sections using tabs
        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_basic_switches_demo(), "Basic Switches")
        tab_widget.addTab(self._create_sizes_demo(), "Switch Sizes")
        tab_widget.addTab(self._create_states_demo(), "Switch States")
        tab_widget.addTab(self._create_custom_text_demo(), "Custom Text")
        tab_widget.addTab(self._create_switch_groups_demo(), "Switch Groups")
        tab_widget.addTab(self._create_interactive_demo(), "Interactive Demo")
        tab_widget.addTab(self._create_real_world_demo(),
                          "Real-World Examples")

        main_layout.addWidget(tab_widget)
        main_layout.addStretch()

        # Setup event logging
        self._setup_event_log(main_layout)

    def _create_basic_switches_demo(self) -> QWidget:
        """Create basic switches demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Simple switches
        simple_group = QGroupBox("Simple Switches")
        simple_layout = QVBoxLayout(simple_group)

        # Basic switch without text
        basic_switch_layout = QHBoxLayout()
        basic_switch_layout.addWidget(QLabel("Basic Switch:"))
        self.basic_switch = FluentSwitch()
        self.basic_switch.toggled.connect(
            lambda checked: self._log_event(
                "Basic Switch", f"Toggled to {'ON' if checked else 'OFF'}")
        )
        basic_switch_layout.addWidget(self.basic_switch)
        basic_switch_layout.addStretch()
        simple_layout.addLayout(basic_switch_layout)

        # Switch with label text
        labeled_switch_layout = QHBoxLayout()
        labeled_switch_layout.addWidget(QLabel("Labeled Switch:"))
        self.labeled_switch = FluentSwitch(text="Enable notifications")
        self.labeled_switch.toggled.connect(
            lambda checked: self._log_event(
                "Labeled Switch", f"Notifications {'enabled' if checked else 'disabled'}")
        )
        labeled_switch_layout.addWidget(self.labeled_switch)
        labeled_switch_layout.addStretch()
        simple_layout.addLayout(labeled_switch_layout)

        # Pre-checked switch
        checked_switch_layout = QHBoxLayout()
        checked_switch_layout.addWidget(QLabel("Pre-checked Switch:"))
        self.checked_switch = FluentSwitch(text="Auto-save", checked=True)
        self.checked_switch.toggled.connect(
            lambda checked: self._log_event(
                "Pre-checked Switch", f"Auto-save {'enabled' if checked else 'disabled'}")
        )
        checked_switch_layout.addWidget(self.checked_switch)
        checked_switch_layout.addStretch()
        simple_layout.addLayout(checked_switch_layout)

        layout.addWidget(simple_group)

        # Switch with on/off text
        onoff_group = QGroupBox("Switches with On/Off Text")
        onoff_layout = QVBoxLayout(onoff_group)

        # Switch with simple on/off text
        simple_onoff_layout = QHBoxLayout()
        simple_onoff_layout.addWidget(QLabel("Simple On/Off:"))
        self.simple_onoff_switch = FluentSwitch(
            text="Power", on_text="ON", off_text="OFF"
        )
        self.simple_onoff_switch.toggled.connect(
            lambda checked: self._log_event(
                "Simple On/Off", f"Power {'ON' if checked else 'OFF'}")
        )
        simple_onoff_layout.addWidget(self.simple_onoff_switch)
        simple_onoff_layout.addStretch()
        onoff_layout.addLayout(simple_onoff_layout)

        # Switch with emoji on/off text
        emoji_onoff_layout = QHBoxLayout()
        emoji_onoff_layout.addWidget(QLabel("Emoji On/Off:"))
        self.emoji_onoff_switch = FluentSwitch(
            text="Wi-Fi", on_text="📶", off_text="📵"
        )
        self.emoji_onoff_switch.toggled.connect(
            lambda checked: self._log_event(
                "Emoji On/Off", f"Wi-Fi {'connected' if checked else 'disconnected'}")
        )
        emoji_onoff_layout.addWidget(self.emoji_onoff_switch)
        emoji_onoff_layout.addStretch()
        onoff_layout.addLayout(emoji_onoff_layout)

        # Switch with custom symbols
        symbol_onoff_layout = QHBoxLayout()
        symbol_onoff_layout.addWidget(QLabel("Symbol On/Off:"))
        self.symbol_onoff_switch = FluentSwitch(
            text="Sound", on_text="♪", off_text="♫"
        )
        self.symbol_onoff_switch.toggled.connect(
            lambda checked: self._log_event(
                "Symbol On/Off", f"Sound {'enabled' if checked else 'muted'}")
        )
        symbol_onoff_layout.addWidget(self.symbol_onoff_switch)
        symbol_onoff_layout.addStretch()
        onoff_layout.addLayout(symbol_onoff_layout)

        layout.addWidget(onoff_group)

        # Control buttons
        controls_group = QGroupBox("Switch Controls")
        controls_layout = QVBoxLayout(controls_group)

        button_layout = QHBoxLayout()

        toggle_all_btn = QPushButton("Toggle All")
        toggle_all_btn.clicked.connect(self._toggle_all_basic_switches)

        check_all_btn = QPushButton("Check All")
        check_all_btn.clicked.connect(self._check_all_basic_switches)

        uncheck_all_btn = QPushButton("Uncheck All")
        uncheck_all_btn.clicked.connect(self._uncheck_all_basic_switches)

        button_layout.addWidget(toggle_all_btn)
        button_layout.addWidget(check_all_btn)
        button_layout.addWidget(uncheck_all_btn)
        button_layout.addStretch()

        controls_layout.addLayout(button_layout)
        layout.addWidget(controls_group)

        return widget

    def _create_sizes_demo(self) -> QWidget:
        """Create switch sizes demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Different sizes
        sizes_group = QGroupBox("Switch Sizes")
        sizes_layout = QGridLayout(sizes_group)

        # Small switches
        sizes_layout.addWidget(QLabel("Small Switches:"), 0, 0)

        small_switches_layout = QVBoxLayout()
        self.small_switches = []

        small_configs = [
            ("Small Basic", ""),
            ("Small with Text", "Compact mode"),
            ("Small with On/Off", "ON", "OFF")
        ]

        for i, config in enumerate(small_configs):
            if len(config) == 2:
                switch = FluentSwitch(
                    text=config[1], size=FluentSwitch.SIZE_SMALL)
            else:
                switch = FluentSwitch(
                    text=config[1], on_text=config[2], off_text=config[3], size=FluentSwitch.SIZE_SMALL)

            switch.toggled.connect(
                lambda checked, name=config[0]: self._log_event(
                    "Size Demo", f"{name}: {'ON' if checked else 'OFF'}")
            )

            switch_layout = QHBoxLayout()
            switch_layout.addWidget(QLabel(f"{config[0]}:"))
            switch_layout.addWidget(switch)
            switch_layout.addStretch()

            small_switches_layout.addLayout(switch_layout)
            self.small_switches.append(switch)

        sizes_layout.addLayout(small_switches_layout, 0, 1)

        # Medium switches
        sizes_layout.addWidget(QLabel("Medium Switches:"), 1, 0)

        medium_switches_layout = QVBoxLayout()
        self.medium_switches = []

        medium_configs = [
            ("Medium Basic", ""),
            ("Medium with Text", "Standard mode"),
            ("Medium with On/Off", "YES", "NO")
        ]

        for i, config in enumerate(medium_configs):
            if len(config) == 2:
                switch = FluentSwitch(
                    text=config[1], size=FluentSwitch.SIZE_MEDIUM)
            else:
                switch = FluentSwitch(
                    text=config[1], on_text=config[2], off_text=config[3], size=FluentSwitch.SIZE_MEDIUM)

            switch.toggled.connect(
                lambda checked, name=config[0]: self._log_event(
                    "Size Demo", f"{name}: {'ON' if checked else 'OFF'}")
            )

            switch_layout = QHBoxLayout()
            switch_layout.addWidget(QLabel(f"{config[0]}:"))
            switch_layout.addWidget(switch)
            switch_layout.addStretch()

            medium_switches_layout.addLayout(switch_layout)
            self.medium_switches.append(switch)

        sizes_layout.addLayout(medium_switches_layout, 1, 1)

        # Large switches
        sizes_layout.addWidget(QLabel("Large Switches:"), 2, 0)

        large_switches_layout = QVBoxLayout()
        self.large_switches = []

        large_configs = [
            ("Large Basic", ""),
            ("Large with Text", "Premium mode"),
            ("Large with On/Off", "✓", "✗")
        ]

        for i, config in enumerate(large_configs):
            if len(config) == 2:
                switch = FluentSwitch(
                    text=config[1], size=FluentSwitch.SIZE_LARGE)
            else:
                switch = FluentSwitch(
                    text=config[1], on_text=config[2], off_text=config[3], size=FluentSwitch.SIZE_LARGE)

            switch.toggled.connect(
                lambda checked, name=config[0]: self._log_event(
                    "Size Demo", f"{name}: {'ON' if checked else 'OFF'}")
            )

            switch_layout = QHBoxLayout()
            switch_layout.addWidget(QLabel(f"{config[0]}:"))
            switch_layout.addWidget(switch)
            switch_layout.addStretch()

            large_switches_layout.addLayout(switch_layout)
            self.large_switches.append(switch)

        sizes_layout.addLayout(large_switches_layout, 2, 1)

        layout.addWidget(sizes_group)

        # Size comparison
        comparison_group = QGroupBox("Size Comparison")
        comparison_layout = QHBoxLayout(comparison_group)

        comparison_layout.addWidget(QLabel("Small:"))
        self.comparison_small = FluentSwitch(
            size=FluentSwitch.SIZE_SMALL, checked=True)
        comparison_layout.addWidget(self.comparison_small)

        comparison_layout.addWidget(QLabel("Medium:"))
        self.comparison_medium = FluentSwitch(
            size=FluentSwitch.SIZE_MEDIUM, checked=True)
        comparison_layout.addWidget(self.comparison_medium)

        comparison_layout.addWidget(QLabel("Large:"))
        self.comparison_large = FluentSwitch(
            size=FluentSwitch.SIZE_LARGE, checked=True)
        comparison_layout.addWidget(self.comparison_large)

        comparison_layout.addStretch()
        layout.addWidget(comparison_group)

        # Size controls
        size_controls_group = QGroupBox("Size Controls")
        size_controls_layout = QVBoxLayout(size_controls_group)

        toggle_size_layout = QHBoxLayout()

        toggle_small_btn = QPushButton("Toggle Small")
        toggle_small_btn.clicked.connect(
            lambda: self._toggle_switches_by_size(self.small_switches))

        toggle_medium_btn = QPushButton("Toggle Medium")
        toggle_medium_btn.clicked.connect(
            lambda: self._toggle_switches_by_size(self.medium_switches))

        toggle_large_btn = QPushButton("Toggle Large")
        toggle_large_btn.clicked.connect(
            lambda: self._toggle_switches_by_size(self.large_switches))

        toggle_size_layout.addWidget(toggle_small_btn)
        toggle_size_layout.addWidget(toggle_medium_btn)
        toggle_size_layout.addWidget(toggle_large_btn)
        toggle_size_layout.addStretch()

        size_controls_layout.addLayout(toggle_size_layout)
        layout.addWidget(size_controls_group)

        return widget

    def _create_states_demo(self) -> QWidget:
        """Create switch states demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Enabled/Disabled states
        states_group = QGroupBox("Switch States")
        states_layout = QGridLayout(states_group)

        # Enabled switches
        states_layout.addWidget(QLabel("Enabled States:"), 0, 0)
        enabled_layout = QVBoxLayout()

        self.enabled_unchecked = FluentSwitch(text="Enabled - Unchecked")
        self.enabled_unchecked.toggled.connect(
            lambda checked: self._log_event(
                "States", f"Enabled switch: {'ON' if checked else 'OFF'}")
        )
        enabled_layout.addWidget(self.enabled_unchecked)

        self.enabled_checked = FluentSwitch(
            text="Enabled - Checked", checked=True)
        self.enabled_checked.toggled.connect(
            lambda checked: self._log_event(
                "States", f"Enabled switch: {'ON' if checked else 'OFF'}")
        )
        enabled_layout.addWidget(self.enabled_checked)

        states_layout.addLayout(enabled_layout, 0, 1)

        # Disabled switches
        states_layout.addWidget(QLabel("Disabled States:"), 1, 0)
        disabled_layout = QVBoxLayout()

        self.disabled_unchecked = FluentSwitch(text="Disabled - Unchecked")
        self.disabled_unchecked.setEnabled(False)
        disabled_layout.addWidget(self.disabled_unchecked)

        self.disabled_checked = FluentSwitch(
            text="Disabled - Checked", checked=True)
        self.disabled_checked.setEnabled(False)
        disabled_layout.addWidget(self.disabled_checked)

        states_layout.addLayout(disabled_layout, 1, 1)

        layout.addWidget(states_group)

        # State controls
        state_controls_group = QGroupBox("State Controls")
        state_controls_layout = QVBoxLayout(state_controls_group)

        # Enable/Disable controls
        enable_disable_layout = QHBoxLayout()

        self.enable_all_cb = QCheckBox("Enable All Switches")
        self.enable_all_cb.setChecked(True)
        self.enable_all_cb.toggled.connect(self._toggle_all_switch_states)

        enable_disable_layout.addWidget(self.enable_all_cb)
        enable_disable_layout.addStretch()

        state_controls_layout.addLayout(enable_disable_layout)

        # Individual controls
        individual_controls_layout = QHBoxLayout()

        toggle_enabled_btn = QPushButton("Toggle Enabled Switches")
        toggle_enabled_btn.clicked.connect(self._toggle_enabled_switches)

        toggle_disabled_btn = QPushButton("Toggle Disabled Switches")
        toggle_disabled_btn.clicked.connect(self._toggle_disabled_switches)

        individual_controls_layout.addWidget(toggle_enabled_btn)
        individual_controls_layout.addWidget(toggle_disabled_btn)
        individual_controls_layout.addStretch()

        state_controls_layout.addLayout(individual_controls_layout)
        layout.addWidget(state_controls_group)

        # Interactive state demo
        interactive_state_group = QGroupBox("Interactive State Demo")
        interactive_state_layout = QVBoxLayout(interactive_state_group)

        self.interactive_switch = FluentSwitch(
            text="Interactive Switch", on_text="ACTIVE", off_text="IDLE")
        self.interactive_switch.toggled.connect(
            lambda checked: self._log_event(
                "Interactive", f"State changed to {'ACTIVE' if checked else 'IDLE'}")
        )
        interactive_state_layout.addWidget(self.interactive_switch)

        interactive_controls_layout = QHBoxLayout()

        programmatic_toggle_btn = QPushButton("Programmatic Toggle")
        programmatic_toggle_btn.clicked.connect(self.interactive_switch.toggle)

        set_checked_btn = QPushButton("Set Checked")
        set_checked_btn.clicked.connect(
            lambda: self.interactive_switch.setChecked(True))

        set_unchecked_btn = QPushButton("Set Unchecked")
        set_unchecked_btn.clicked.connect(
            lambda: self.interactive_switch.setChecked(False))

        interactive_controls_layout.addWidget(programmatic_toggle_btn)
        interactive_controls_layout.addWidget(set_checked_btn)
        interactive_controls_layout.addWidget(set_unchecked_btn)
        interactive_controls_layout.addStretch()

        interactive_state_layout.addLayout(interactive_controls_layout)
        layout.addWidget(interactive_state_group)

        return widget

    def _create_custom_text_demo(self) -> QWidget:
        """Create custom text demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Dynamic text changes
        dynamic_group = QGroupBox("Dynamic Text Changes")
        dynamic_layout = QVBoxLayout(dynamic_group)

        # Switch with changeable text
        self.dynamic_text_switch = FluentSwitch(text="Initial Text")
        self.dynamic_text_switch.toggled.connect(
            lambda checked: self._log_event(
                "Dynamic Text", f"Switch with dynamic text: {'ON' if checked else 'OFF'}")
        )
        dynamic_layout.addWidget(self.dynamic_text_switch)

        # Text input controls
        text_controls_layout = QGridLayout()

        text_controls_layout.addWidget(QLabel("Switch Text:"), 0, 0)
        self.switch_text_input = QLineEdit("Initial Text")
        self.switch_text_input.textChanged.connect(
            self.dynamic_text_switch.setText)
        text_controls_layout.addWidget(self.switch_text_input, 0, 1)

        text_controls_layout.addWidget(QLabel("On Text:"), 1, 0)
        self.on_text_input = QLineEdit()
        self.on_text_input.textChanged.connect(
            self.dynamic_text_switch.setOnText)
        text_controls_layout.addWidget(self.on_text_input, 1, 1)

        text_controls_layout.addWidget(QLabel("Off Text:"), 2, 0)
        self.off_text_input = QLineEdit()
        self.off_text_input.textChanged.connect(
            self.dynamic_text_switch.setOffText)
        text_controls_layout.addWidget(self.off_text_input, 2, 1)

        dynamic_layout.addLayout(text_controls_layout)
        layout.addWidget(dynamic_group)

        # Preset text examples
        presets_group = QGroupBox("Text Presets")
        presets_layout = QVBoxLayout(presets_group)

        # Create switches with different text styles
        text_presets = [
            ("System Settings", "Enable dark mode", "🌙", "☀️"),
            ("Network", "Auto-connect to Wi-Fi", "CONN", "DISC"),
            ("Security", "Two-factor authentication", "SECURE", "BASIC"),
            ("Privacy", "Share analytics data", "SHARE", "PRIVATE"),
            ("Performance", "High performance mode", "BOOST", "NORMAL"),
            ("Accessibility", "Screen reader support", "♿", "👁️"),
        ]

        self.preset_switches = []
        for category, text, on_text, off_text in text_presets:
            preset_layout = QHBoxLayout()
            preset_layout.addWidget(QLabel(f"{category}:"))

            switch = FluentSwitch(
                text=text, on_text=on_text, off_text=off_text)
            switch.toggled.connect(
                lambda checked, cat=category: self._log_event(
                    "Presets", f"{cat}: {'ON' if checked else 'OFF'}")
            )

            preset_layout.addWidget(switch)
            preset_layout.addStretch()

            presets_layout.addLayout(preset_layout)
            self.preset_switches.append(switch)

        layout.addWidget(presets_group)

        # Text preset controls
        preset_controls_group = QGroupBox("Preset Controls")
        preset_controls_layout = QVBoxLayout(preset_controls_group)

        preset_buttons_layout = QHBoxLayout()

        apply_simple_btn = QPushButton("Apply Simple Text")
        apply_simple_btn.clicked.connect(
            lambda: self._apply_text_preset("simple"))

        apply_emoji_btn = QPushButton("Apply Emoji Text")
        apply_emoji_btn.clicked.connect(
            lambda: self._apply_text_preset("emoji"))

        apply_symbols_btn = QPushButton("Apply Symbol Text")
        apply_symbols_btn.clicked.connect(
            lambda: self._apply_text_preset("symbols"))

        clear_text_btn = QPushButton("Clear On/Off Text")
        clear_text_btn.clicked.connect(
            lambda: self._apply_text_preset("clear"))

        preset_buttons_layout.addWidget(apply_simple_btn)
        preset_buttons_layout.addWidget(apply_emoji_btn)
        preset_buttons_layout.addWidget(apply_symbols_btn)
        preset_buttons_layout.addWidget(clear_text_btn)
        preset_buttons_layout.addStretch()

        preset_controls_layout.addLayout(preset_buttons_layout)
        layout.addWidget(preset_controls_group)

        return widget

    def _create_switch_groups_demo(self) -> QWidget:
        """Create switch groups demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Basic switch group
        basic_group_widget = QGroupBox("Basic Switch Group")
        basic_group_layout = QVBoxLayout(basic_group_widget)

        self.basic_switch_group = FluentSwitchGroup()

        # Add switches to group
        group_switches = [
            FluentSwitch(text="Feature A"),
            FluentSwitch(text="Feature B", checked=True),
            FluentSwitch(text="Feature C"),
            FluentSwitch(text="Feature D", checked=True)
        ]

        for switch in group_switches:
            switch.toggled.connect(
                lambda checked, sw=switch: self._log_event(
                    "Basic Group", f"{sw.text()}: {'ON' if checked else 'OFF'}")
            )
            self.basic_switch_group.addSwitch(switch)

        basic_group_layout.addWidget(self.basic_switch_group)
        layout.addWidget(basic_group_widget)

        # Themed switch groups
        themed_groups_widget = QGroupBox("Themed Switch Groups")
        themed_groups_layout = QVBoxLayout(themed_groups_widget)

        # Privacy settings group
        privacy_group_label = QLabel("Privacy Settings:")
        privacy_group_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        themed_groups_layout.addWidget(privacy_group_label)

        self.privacy_group = FluentSwitchGroup()
        privacy_switches = [
            FluentSwitch(text="Share usage data",
                         on_text="SHARE", off_text="KEEP"),
            FluentSwitch(text="Location tracking", on_text="📍", off_text="🚫"),
            FluentSwitch(text="Personalized ads",
                         on_text="ADS", off_text="NONE")
        ]

        for switch in privacy_switches:
            switch.toggled.connect(
                lambda checked, sw=switch: self._log_event(
                    "Privacy Group", f"{sw.text()}: {'ON' if checked else 'OFF'}")
            )
            self.privacy_group.addSwitch(switch)

        themed_groups_layout.addWidget(self.privacy_group)
        themed_groups_layout.addSpacing(10)

        # Performance settings group
        performance_group_label = QLabel("Performance Settings:")
        performance_group_label.setFont(
            QFont("Segoe UI", 12, QFont.Weight.Bold))
        themed_groups_layout.addWidget(performance_group_label)

        self.performance_group = FluentSwitchGroup()
        performance_switches = [
            FluentSwitch(text="GPU acceleration", checked=True,
                         on_text="🚀", off_text="🐌"),
            FluentSwitch(text="Background sync", checked=True,
                         on_text="SYNC", off_text="PAUSE"),
            FluentSwitch(text="Auto-optimization",
                         on_text="AUTO", off_text="MANUAL")
        ]

        for switch in performance_switches:
            switch.toggled.connect(
                lambda checked, sw=switch: self._log_event(
                    "Performance Group", f"{sw.text()}: {'ON' if checked else 'OFF'}")
            )
            self.performance_group.addSwitch(switch)

        themed_groups_layout.addWidget(self.performance_group)
        layout.addWidget(themed_groups_widget)

        # Group controls
        group_controls_widget = QGroupBox("Group Controls")
        group_controls_layout = QVBoxLayout(group_controls_widget)

        # Basic group controls
        basic_controls_layout = QHBoxLayout()
        basic_controls_layout.addWidget(QLabel("Basic Group:"))

        enable_basic_group_btn = QPushButton("Enable Group")
        enable_basic_group_btn.clicked.connect(
            lambda: self.basic_switch_group.setEnabled(True))

        disable_basic_group_btn = QPushButton("Disable Group")
        disable_basic_group_btn.clicked.connect(
            lambda: self.basic_switch_group.setEnabled(False))

        toggle_basic_group_btn = QPushButton("Toggle All")
        toggle_basic_group_btn.clicked.connect(
            lambda: self._toggle_group_switches(self.basic_switch_group))

        basic_controls_layout.addWidget(enable_basic_group_btn)
        basic_controls_layout.addWidget(disable_basic_group_btn)
        basic_controls_layout.addWidget(toggle_basic_group_btn)
        basic_controls_layout.addStretch()

        group_controls_layout.addLayout(basic_controls_layout)

        # Themed groups controls
        themed_controls_layout = QHBoxLayout()

        privacy_controls_layout = QVBoxLayout()
        privacy_controls_layout.addWidget(QLabel("Privacy Group:"))

        privacy_buttons_layout = QHBoxLayout()
        enable_privacy_btn = QPushButton("Enable")
        enable_privacy_btn.clicked.connect(
            lambda: self.privacy_group.setEnabled(True))

        disable_privacy_btn = QPushButton("Disable")
        disable_privacy_btn.clicked.connect(
            lambda: self.privacy_group.setEnabled(False))

        privacy_secure_btn = QPushButton("Secure Mode")
        privacy_secure_btn.clicked.connect(
            lambda: self._set_privacy_secure_mode())

        privacy_buttons_layout.addWidget(enable_privacy_btn)
        privacy_buttons_layout.addWidget(disable_privacy_btn)
        privacy_buttons_layout.addWidget(privacy_secure_btn)

        privacy_controls_layout.addLayout(privacy_buttons_layout)
        themed_controls_layout.addLayout(privacy_controls_layout)

        performance_controls_layout = QVBoxLayout()
        performance_controls_layout.addWidget(QLabel("Performance Group:"))

        performance_buttons_layout = QHBoxLayout()
        enable_performance_btn = QPushButton("Enable")
        enable_performance_btn.clicked.connect(
            lambda: self.performance_group.setEnabled(True))

        disable_performance_btn = QPushButton("Disable")
        disable_performance_btn.clicked.connect(
            lambda: self.performance_group.setEnabled(False))

        performance_boost_btn = QPushButton("Boost Mode")
        performance_boost_btn.clicked.connect(
            lambda: self._set_performance_boost_mode())

        performance_buttons_layout.addWidget(enable_performance_btn)
        performance_buttons_layout.addWidget(disable_performance_btn)
        performance_buttons_layout.addWidget(performance_boost_btn)

        performance_controls_layout.addLayout(performance_buttons_layout)
        themed_controls_layout.addLayout(performance_controls_layout)

        group_controls_layout.addLayout(themed_controls_layout)
        layout.addWidget(group_controls_widget)

        return widget

    def _create_interactive_demo(self) -> QWidget:
        """Create interactive demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Dynamic switch creator
        creator_group = QGroupBox("Dynamic Switch Creator")
        creator_layout = QVBoxLayout(creator_group)

        # Configuration form
        config_form = QFormLayout()

        self.new_switch_text = QLineEdit("New Switch")
        config_form.addRow("Switch Text:", self.new_switch_text)

        self.new_switch_on_text = QLineEdit()
        config_form.addRow("On Text:", self.new_switch_on_text)

        self.new_switch_off_text = QLineEdit()
        config_form.addRow("Off Text:", self.new_switch_off_text)

        self.new_switch_size = QComboBox()
        self.new_switch_size.addItems(["Small", "Medium", "Large"])
        self.new_switch_size.setCurrentText("Medium")
        config_form.addRow("Size:", self.new_switch_size)

        self.new_switch_checked = QCheckBox()
        config_form.addRow("Initially Checked:", self.new_switch_checked)

        creator_layout.addLayout(config_form)

        # Creator buttons
        creator_buttons_layout = QHBoxLayout()

        create_switch_btn = QPushButton("Create Switch")
        create_switch_btn.clicked.connect(self._create_dynamic_switch)

        clear_switches_btn = QPushButton("Clear All")
        clear_switches_btn.clicked.connect(self._clear_dynamic_switches)

        creator_buttons_layout.addWidget(create_switch_btn)
        creator_buttons_layout.addWidget(clear_switches_btn)
        creator_buttons_layout.addStretch()

        creator_layout.addLayout(creator_buttons_layout)

        # Dynamic switches container
        self.dynamic_switches_scroll = QScrollArea()
        self.dynamic_switches_widget = QWidget()
        self.dynamic_switches_layout = QVBoxLayout(
            self.dynamic_switches_widget)
        self.dynamic_switches_scroll.setWidget(self.dynamic_switches_widget)
        self.dynamic_switches_scroll.setWidgetResizable(True)
        self.dynamic_switches_scroll.setMaximumHeight(200)

        creator_layout.addWidget(self.dynamic_switches_scroll)
        layout.addWidget(creator_group)

        # Animation playground
        animation_group = QGroupBox("Animation Playground")
        animation_layout = QVBoxLayout(animation_group)

        # Test switches for animation
        self.animation_switches = []
        animation_configs = [
            ("Smooth Animation", FluentSwitch.SIZE_SMALL),
            ("Standard Animation", FluentSwitch.SIZE_MEDIUM),
            ("Large Animation", FluentSwitch.SIZE_LARGE)
        ]

        for text, size in animation_configs:
            switch_layout = QHBoxLayout()
            switch_layout.addWidget(QLabel(f"{text}:"))

            switch = FluentSwitch(text=text, size=size,
                                  on_text="✓", off_text="✗")
            switch.toggled.connect(
                lambda checked, name=text: self._log_event(
                    "Animation", f"{name}: {'ON' if checked else 'OFF'}")
            )

            switch_layout.addWidget(switch)
            switch_layout.addStretch()

            animation_layout.addLayout(switch_layout)
            self.animation_switches.append(switch)

        # Animation controls
        animation_controls_layout = QHBoxLayout()

        rapid_toggle_btn = QPushButton("Rapid Toggle")
        rapid_toggle_btn.clicked.connect(self._start_rapid_toggle)

        stop_toggle_btn = QPushButton("Stop Toggle")
        stop_toggle_btn.clicked.connect(self._stop_rapid_toggle)

        sequential_toggle_btn = QPushButton("Sequential Toggle")
        sequential_toggle_btn.clicked.connect(self._start_sequential_toggle)

        animation_controls_layout.addWidget(rapid_toggle_btn)
        animation_controls_layout.addWidget(stop_toggle_btn)
        animation_controls_layout.addWidget(sequential_toggle_btn)
        animation_controls_layout.addStretch()

        animation_layout.addLayout(animation_controls_layout)
        layout.addWidget(animation_group)

        # Performance test
        performance_group = QGroupBox("Performance Test")
        performance_layout = QVBoxLayout(performance_group)

        performance_info = QLabel("Test performance with many switches")
        performance_layout.addWidget(performance_info)

        performance_controls_layout = QHBoxLayout()

        self.perf_switch_count = QSpinBox()
        self.perf_switch_count.setRange(1, 100)
        self.perf_switch_count.setValue(20)

        create_many_btn = QPushButton("Create Many Switches")
        create_many_btn.clicked.connect(self._create_many_switches)

        toggle_many_btn = QPushButton("Toggle All")
        toggle_many_btn.clicked.connect(self._toggle_many_switches)

        clear_many_btn = QPushButton("Clear")
        clear_many_btn.clicked.connect(self._clear_many_switches)

        performance_controls_layout.addWidget(QLabel("Count:"))
        performance_controls_layout.addWidget(self.perf_switch_count)
        performance_controls_layout.addWidget(create_many_btn)
        performance_controls_layout.addWidget(toggle_many_btn)
        performance_controls_layout.addWidget(clear_many_btn)
        performance_controls_layout.addStretch()

        performance_layout.addLayout(performance_controls_layout)

        # Performance switches container
        self.perf_switches_scroll = QScrollArea()
        self.perf_switches_widget = QWidget()
        self.perf_switches_layout = QGridLayout(self.perf_switches_widget)
        self.perf_switches_scroll.setWidget(self.perf_switches_widget)
        self.perf_switches_scroll.setWidgetResizable(True)
        self.perf_switches_scroll.setMaximumHeight(200)

        performance_layout.addWidget(self.perf_switches_scroll)
        layout.addWidget(performance_group)

        return widget

    def _create_real_world_demo(self) -> QWidget:
        """Create real-world examples section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # System settings simulation
        system_group = QGroupBox("System Settings")
        system_layout = QVBoxLayout(system_group)

        # General settings
        general_label = QLabel("General:")
        general_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        system_layout.addWidget(general_label)

        general_settings = [
            ("Start with Windows", True, "AUTO", "MANUAL"),
            ("Check for updates automatically", True, "AUTO", "MANUAL"),
            ("Send crash reports", False, "SEND", "KEEP"),
            ("Enable animations", True, "ON", "OFF"),
        ]

        self.system_switches = []
        for text, checked, on_text, off_text in general_settings:
            switch_layout = QHBoxLayout()
            switch_layout.addWidget(QLabel(text))

            switch = FluentSwitch(
                checked=checked, on_text=on_text, off_text=off_text)
            switch.toggled.connect(
                lambda state, setting=text: self._log_event(
                    "System Settings", f"{setting}: {'Enabled' if state else 'Disabled'}")
            )

            switch_layout.addWidget(switch)
            switch_layout.addStretch()

            system_layout.addLayout(switch_layout)
            self.system_switches.append(switch)

        layout.addWidget(system_group)

        # App preferences simulation
        app_group = QGroupBox("Application Preferences")
        app_layout = QVBoxLayout(app_group)

        # UI preferences
        ui_label = QLabel("User Interface:")
        ui_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        app_layout.addWidget(ui_label)

        ui_settings = [
            ("Dark mode", False, "🌙", "☀️", FluentSwitch.SIZE_SMALL),
            ("Compact view", False, "COMPACT", "NORMAL", FluentSwitch.SIZE_SMALL),
            ("Show tooltips", True, "SHOW", "HIDE", FluentSwitch.SIZE_SMALL),
            ("Smooth scrolling", True, "SMOOTH", "STEP", FluentSwitch.SIZE_SMALL),
        ]

        self.app_switches = []
        for text, checked, on_text, off_text, size in ui_settings:
            switch_layout = QHBoxLayout()
            switch_layout.addWidget(QLabel(text))

            switch = FluentSwitch(
                checked=checked, on_text=on_text, off_text=off_text, size=size)
            switch.toggled.connect(
                lambda state, setting=text: self._log_event(
                    "App Preferences", f"{setting}: {'Enabled' if state else 'Disabled'}")
            )

            switch_layout.addWidget(switch)
            switch_layout.addStretch()

            app_layout.addLayout(switch_layout)
            self.app_switches.append(switch)

        layout.addWidget(app_group)

        # Gaming settings simulation
        gaming_group = QGroupBox("Gaming Settings")
        gaming_layout = QVBoxLayout(gaming_group)

        gaming_settings = [
            ("Game mode", False, "GAME", "NORMAL", FluentSwitch.SIZE_MEDIUM),
            ("V-Sync", True, "SYNC", "FREE", FluentSwitch.SIZE_MEDIUM),
            ("Hardware acceleration", True, "HW", "SW", FluentSwitch.SIZE_MEDIUM),
            ("Full screen optimizations", False, "OPT",
             "COMPAT", FluentSwitch.SIZE_MEDIUM),
        ]

        self.gaming_switches = []
        for text, checked, on_text, off_text, size in gaming_settings:
            switch_layout = QHBoxLayout()
            switch_layout.addWidget(QLabel(text))

            switch = FluentSwitch(
                checked=checked, on_text=on_text, off_text=off_text, size=size)
            switch.toggled.connect(
                lambda state, setting=text: self._log_event(
                    "Gaming Settings", f"{setting}: {'Enabled' if state else 'Disabled'}")
            )

            switch_layout.addWidget(switch)
            switch_layout.addStretch()

            gaming_layout.addLayout(switch_layout)
            self.gaming_switches.append(switch)

        layout.addWidget(gaming_group)

        # Profile presets
        presets_group = QGroupBox("Setting Presets")
        presets_layout = QVBoxLayout(presets_group)

        presets_buttons_layout = QHBoxLayout()

        default_preset_btn = QPushButton("Default Settings")
        default_preset_btn.clicked.connect(
            lambda: self._apply_settings_preset("default"))

        performance_preset_btn = QPushButton("Performance Mode")
        performance_preset_btn.clicked.connect(
            lambda: self._apply_settings_preset("performance"))

        power_save_preset_btn = QPushButton("Power Save Mode")
        power_save_preset_btn.clicked.connect(
            lambda: self._apply_settings_preset("power_save"))

        gaming_preset_btn = QPushButton("Gaming Mode")
        gaming_preset_btn.clicked.connect(
            lambda: self._apply_settings_preset("gaming"))

        presets_buttons_layout.addWidget(default_preset_btn)
        presets_buttons_layout.addWidget(performance_preset_btn)
        presets_buttons_layout.addWidget(power_save_preset_btn)
        presets_buttons_layout.addWidget(gaming_preset_btn)
        presets_buttons_layout.addStretch()

        presets_layout.addLayout(presets_buttons_layout)
        layout.addWidget(presets_group)

        return widget

    def _setup_event_log(self, parent_layout):
        """Setup event logging"""
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout(log_group)

        self.event_log = QTextEdit()
        self.event_log.setMaximumHeight(100)
        self.event_log.setPlaceholderText(
            "Switch events will be logged here...")
        self.event_log.setReadOnly(True)
        log_layout.addWidget(self.event_log)

        log_controls = QHBoxLayout()
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.event_log.clear)
        log_controls.addWidget(clear_log_btn)
        log_controls.addStretch()
        log_layout.addLayout(log_controls)
        parent_layout.addWidget(log_group)

    def _log_event(self, event_type: str, details: str):
        """Log switch events"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_log.append(f"[{timestamp}] {event_type}: {details}")

    # Event handlers for basic switches demo
    def _toggle_all_basic_switches(self):
        switches = [self.basic_switch, self.labeled_switch, self.checked_switch,
                    self.simple_onoff_switch, self.emoji_onoff_switch, self.symbol_onoff_switch]
        for switch in switches:
            switch.toggle()
        self._log_event("Control", "Toggled all basic switches")

    def _check_all_basic_switches(self):
        switches = [self.basic_switch, self.labeled_switch, self.checked_switch,
                    self.simple_onoff_switch, self.emoji_onoff_switch, self.symbol_onoff_switch]
        for switch in switches:
            switch.setChecked(True)
        self._log_event("Control", "Checked all basic switches")

    def _uncheck_all_basic_switches(self):
        switches = [self.basic_switch, self.labeled_switch, self.checked_switch,
                    self.simple_onoff_switch, self.emoji_onoff_switch, self.symbol_onoff_switch]
        for switch in switches:
            switch.setChecked(False)
        self._log_event("Control", "Unchecked all basic switches")

    # Event handlers for size demo
    def _toggle_switches_by_size(self, switches):
        for switch in switches:
            switch.toggle()
        size_name = "Unknown"
        if switches == self.small_switches:
            size_name = "Small"
        elif switches == self.medium_switches:
            size_name = "Medium"
        elif switches == self.large_switches:
            size_name = "Large"
        self._log_event("Size Control", f"Toggled all {size_name} switches")

    # Event handlers for states demo
    def _toggle_all_switch_states(self, enable):
        switches = [self.enabled_unchecked, self.enabled_checked,
                    self.disabled_unchecked, self.disabled_checked]
        for switch in switches:
            switch.setEnabled(enable)
        self._log_event("State Control",
                        f"{'Enabled' if enable else 'Disabled'} all switches")

    def _toggle_enabled_switches(self):
        switches = [self.enabled_unchecked, self.enabled_checked]
        for switch in switches:
            switch.toggle()
        self._log_event("State Control", "Toggled enabled switches")

    def _toggle_disabled_switches(self):
        # Temporarily enable, toggle, then disable again
        switches = [self.disabled_unchecked, self.disabled_checked]
        for switch in switches:
            was_enabled = switch.isEnabled()
            switch.setEnabled(True)
            switch.toggle()
            switch.setEnabled(was_enabled)
        self._log_event("State Control", "Toggled disabled switches")

    # Event handlers for custom text demo
    def _apply_text_preset(self, preset_type):
        if preset_type == "simple":
            presets = [("ON", "OFF"), ("YES", "NO"), ("ENABLED", "DISABLED")]
        elif preset_type == "emoji":
            presets = [("✅", "❌"), ("👍", "👎"), ("🟢", "🔴")]
        elif preset_type == "symbols":
            presets = [("●", "○"), ("■", "□"), ("▲", "▽")]
        elif preset_type == "clear":
            presets = [("", "")]
        else:
            return

        import random
        for switch in self.preset_switches:
            if preset_type == "clear":
                on_text, off_text = "", ""
            else:
                on_text, off_text = random.choice(presets)
            switch.setOnText(on_text)
            switch.setOffText(off_text)

        self._log_event("Text Presets", f"Applied {preset_type} text preset")

    # Event handlers for switch groups demo
    def _toggle_group_switches(self, group):
        for switch in group.getSwitches():
            switch.toggle()
        self._log_event("Group Control", "Toggled group switches")

    def _set_privacy_secure_mode(self):
        switches = self.privacy_group.getSwitches()
        # Secure mode: disable sharing, location, ads
        security_states = [False, False, False]
        for switch, state in zip(switches, security_states):
            switch.setChecked(state)
        self._log_event("Privacy Group", "Applied secure mode preset")

    def _set_performance_boost_mode(self):
        switches = self.performance_group.getSwitches()
        # Boost mode: enable all performance features
        for switch in switches:
            switch.setChecked(True)
        self._log_event("Performance Group", "Applied boost mode preset")

    # Event handlers for interactive demo
    def _create_dynamic_switch(self):
        text = self.new_switch_text.text()
        on_text = self.new_switch_on_text.text()
        off_text = self.new_switch_off_text.text()
        size_map = {
            "Small": FluentSwitch.SIZE_SMALL,
            "Medium": FluentSwitch.SIZE_MEDIUM,
            "Large": FluentSwitch.SIZE_LARGE
        }
        size = size_map[self.new_switch_size.currentText()]
        checked = self.new_switch_checked.isChecked()

        switch = FluentSwitch(text=text, checked=checked, size=size,
                              on_text=on_text, off_text=off_text)
        switch.toggled.connect(
            lambda state: self._log_event(
                "Dynamic Switch", f"{text}: {'ON' if state else 'OFF'}")
        )

        # Create a layout with switch and remove button
        switch_container = QWidget()
        switch_layout = QHBoxLayout(switch_container)
        switch_layout.addWidget(switch)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(
            lambda: self._remove_dynamic_switch(switch_container))
        switch_layout.addWidget(remove_btn)
        switch_layout.addStretch()

        self.dynamic_switches_layout.addWidget(switch_container)
        self._log_event("Dynamic Creation", f"Created switch: {text}")

    def _remove_dynamic_switch(self, container):
        container.setParent(None)
        container.deleteLater()
        self._log_event("Dynamic Creation", "Removed dynamic switch")

    def _clear_dynamic_switches(self):
        while self.dynamic_switches_layout.count():
            item = self.dynamic_switches_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._log_event("Dynamic Creation", "Cleared all dynamic switches")

    def _start_rapid_toggle(self):
        if not hasattr(self, 'rapid_timer'):
            self.rapid_timer = QTimer()
            self.rapid_timer.timeout.connect(self._rapid_toggle_switches)

        if not self.rapid_timer.isActive():
            self.rapid_timer.start(500)  # Toggle every 500ms
            self._log_event("Animation", "Started rapid toggle")

    def _stop_rapid_toggle(self):
        if hasattr(self, 'rapid_timer') and self.rapid_timer.isActive():
            self.rapid_timer.stop()
            self._log_event("Animation", "Stopped rapid toggle")

    def _rapid_toggle_switches(self):
        for switch in self.animation_switches:
            switch.toggle()

    def _start_sequential_toggle(self):
        if not hasattr(self, 'sequential_timer'):
            self.sequential_timer = QTimer()
            self.sequential_index = 0
            self.sequential_timer.timeout.connect(
                self._sequential_toggle_switch)

        if not self.sequential_timer.isActive():
            self.sequential_index = 0
            self.sequential_timer.start(300)  # Toggle every 300ms
            self._log_event("Animation", "Started sequential toggle")

    def _sequential_toggle_switch(self):
        if self.animation_switches:
            switch = self.animation_switches[self.sequential_index]
            switch.toggle()
            self.sequential_index = (
                self.sequential_index + 1) % len(self.animation_switches)

    def _create_many_switches(self):
        self._clear_many_switches()
        count = self.perf_switch_count.value()

        self.many_switches = []
        for i in range(count):
            row, col = divmod(i, 5)  # 5 switches per row
            switch = FluentSwitch(
                text=f"Switch {i+1}", size=FluentSwitch.SIZE_SMALL)
            switch.toggled.connect(
                lambda checked, idx=i: self._log_event(
                    "Performance", f"Switch {idx+1}: {'ON' if checked else 'OFF'}")
            )

            self.perf_switches_layout.addWidget(switch, row, col)
            self.many_switches.append(switch)

        self._log_event("Performance", f"Created {count} switches")

    def _toggle_many_switches(self):
        if hasattr(self, 'many_switches'):
            for switch in self.many_switches:
                switch.toggle()
            self._log_event(
                "Performance", f"Toggled {len(self.many_switches)} switches")

    def _clear_many_switches(self):
        if hasattr(self, 'many_switches'):
            for switch in self.many_switches:
                switch.deleteLater()
            self.many_switches.clear()

        while self.perf_switches_layout.count():
            item = self.perf_switches_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._log_event("Performance", "Cleared performance switches")

    # Event handlers for real-world demo
    def _apply_settings_preset(self, preset_name):
        if preset_name == "default":
            # Default settings
            system_states = [True, True, False, True]
            app_states = [False, False, True, True]
            gaming_states = [False, True, True, False]
        elif preset_name == "performance":
            # Performance mode
            system_states = [True, False, False, False]
            app_states = [False, True, False, False]
            gaming_states = [True, False, True, True]
        elif preset_name == "power_save":
            # Power save mode
            system_states = [False, False, False, True]
            app_states = [True, True, True, True]
            gaming_states = [False, True, False, False]
        elif preset_name == "gaming":
            # Gaming mode
            system_states = [True, False, False, False]
            app_states = [True, True, False, False]
            gaming_states = [True, False, True, True]
        else:
            return

        for switch, state in zip(self.system_switches, system_states):
            switch.setChecked(state)

        for switch, state in zip(self.app_switches, app_states):
            switch.setChecked(state)

        for switch, state in zip(self.gaming_switches, gaming_states):
            switch.setChecked(state)

        self._log_event("Settings Preset", f"Applied {preset_name} preset")

    def _toggle_theme(self, theme_name: str):
        if theme_name == "Dark":
            theme_manager.set_theme_mode(ThemeMode.DARK)
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)
        self._log_event("Theme", f"Switched to {theme_name} mode")

    def closeEvent(self, event):
        """Cleanup on close"""
        if hasattr(self, 'rapid_timer'):
            self.rapid_timer.stop()
        if hasattr(self, 'sequential_timer'):
            self.sequential_timer.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SwitchDemo()
    window.show()
    sys.exit(app.exec())
