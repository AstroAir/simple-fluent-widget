"""
Fluent CheckBox, RadioButton, and RadioGroup Demo
Comprehensive example showcasing all features and functionality
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QGroupBox,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Import the checkbox and radio button components
from components.basic.checkbox import FluentCheckBox, FluentRadioButton, FluentRadioGroup
from core.theme import theme_manager, ThemeMode


class CheckboxRadioDemo(QMainWindow):
    """Main demo window showcasing checkbox and radio button features"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent CheckBox, RadioButton & RadioGroup Demo")
        self.setGeometry(100, 100, 900, 700)

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
        title = QLabel("Fluent CheckBox, RadioButton & RadioGroup Demo")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Theme toggle
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        # Set initial theme based on current theme_manager state
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
        main_layout.addWidget(self._create_checkbox_demo())
        main_layout.addWidget(self._create_radiobutton_demo())
        main_layout.addWidget(self._create_radiogroup_demo())
        main_layout.addWidget(self._create_interactive_demo())

        main_layout.addStretch()

    def _create_checkbox_demo(self) -> QGroupBox:
        """Create FluentCheckBox demonstration section"""
        group = QGroupBox("FluentCheckBox")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Basic CheckBoxes
        basic_layout = QGridLayout()
        basic_layout.setSpacing(10)

        self.cb_unchecked = FluentCheckBox("Unchecked")
        self.cb_checked = FluentCheckBox("Checked Initially")
        self.cb_checked.setChecked(True)
        self.cb_tristate = FluentCheckBox("Tri-state")
        self.cb_tristate.setTristate(True)
        self.cb_tristate.setCheckState(Qt.CheckState.PartiallyChecked)

        self.cb_disabled_unchecked = FluentCheckBox("Disabled Unchecked")
        self.cb_disabled_unchecked.setEnabled(False)
        self.cb_disabled_checked = FluentCheckBox("Disabled Checked")
        self.cb_disabled_checked.setChecked(True)
        self.cb_disabled_checked.setEnabled(False)
        self.cb_disabled_tristate = FluentCheckBox("Disabled Tri-state")
        self.cb_disabled_tristate.setTristate(True)
        self.cb_disabled_tristate.setCheckState(Qt.CheckState.PartiallyChecked)
        self.cb_disabled_tristate.setEnabled(False)

        basic_layout.addWidget(self.cb_unchecked, 0, 0)
        basic_layout.addWidget(self.cb_checked, 0, 1)
        basic_layout.addWidget(self.cb_tristate, 1, 0)
        basic_layout.addWidget(self.cb_disabled_unchecked, 2, 0)
        basic_layout.addWidget(self.cb_disabled_checked, 2, 1)
        basic_layout.addWidget(self.cb_disabled_tristate, 3, 0)

        layout.addWidget(QLabel("Basic States and Disabled:"))
        layout.addLayout(basic_layout)

        # Tri-state cycle button
        tristate_cycle_button = QPushButton("Cycle Tri-state CheckBox")
        tristate_cycle_button.clicked.connect(self._cycle_tristate_checkbox)
        layout.addWidget(tristate_cycle_button)

        # Signal Handling
        signal_layout = QHBoxLayout()
        self.cb_signal = FluentCheckBox("Listen to my state")
        self.cb_signal_label = QLabel(
            f"State: {self._get_check_state_str(self.cb_signal.checkState())}")
        self.cb_signal.stateChanged.connect(
            self._on_checkbox_signal_state_changed)
        signal_layout.addWidget(self.cb_signal)
        signal_layout.addWidget(self.cb_signal_label)
        signal_layout.addStretch()

        layout.addWidget(QLabel("Signal Handling (stateChanged):"))
        layout.addLayout(signal_layout)

        return group

    def _get_check_state_str(self, state: Qt.CheckState) -> str:
        if state == Qt.CheckState.Unchecked:
            return "Unchecked"
        elif state == Qt.CheckState.PartiallyChecked:
            return "PartiallyChecked"
        elif state == Qt.CheckState.Checked:
            return "Checked"
        return "Unknown"

    def _on_checkbox_signal_state_changed(self, state_int: int):
        state = Qt.CheckState(state_int)
        self.cb_signal_label.setText(
            f"State: {self._get_check_state_str(state)}")

    def _cycle_tristate_checkbox(self):
        current_state = self.cb_tristate.checkState()
        if current_state == Qt.CheckState.Unchecked:
            self.cb_tristate.setCheckState(Qt.CheckState.PartiallyChecked)
        elif current_state == Qt.CheckState.PartiallyChecked:
            self.cb_tristate.setCheckState(Qt.CheckState.Checked)
        else:  # Checked
            self.cb_tristate.setCheckState(Qt.CheckState.Unchecked)

    def _create_radiobutton_demo(self) -> QGroupBox:
        """Create FluentRadioButton demonstration section"""
        group = QGroupBox("FluentRadioButton")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # RadioButtons in a group (implicitly by parent, or explicitly with QButtonGroup)
        # For demo purposes, we'll use QGroupBox as a visual separator
        # and rely on QRadioButton's auto-exclusive behavior within a parent widget.

        layout.addWidget(QLabel("Group 1 (Auto-exclusive):"))
        rb_group1_layout = QHBoxLayout()
        self.rb_g1_opt1 = FluentRadioButton("Option A1")
        self.rb_g1_opt2 = FluentRadioButton("Option B1 (Selected Initially)")
        self.rb_g1_opt2.setChecked(True)
        self.rb_g1_opt3 = FluentRadioButton("Option C1")
        rb_group1_layout.addWidget(self.rb_g1_opt1)
        rb_group1_layout.addWidget(self.rb_g1_opt2)
        rb_group1_layout.addWidget(self.rb_g1_opt3)
        rb_group1_layout.addStretch()
        layout.addLayout(rb_group1_layout)

        layout.addWidget(QLabel("Group 2 (With Disabled):"))
        rb_group2_layout = QHBoxLayout()
        self.rb_g2_opt1 = FluentRadioButton("Option X2")
        self.rb_g2_opt2 = FluentRadioButton("Option Y2 (Disabled)")
        self.rb_g2_opt2.setEnabled(False)
        self.rb_g2_opt3 = FluentRadioButton("Option Z2 (Disabled & Selected)")
        # Will be auto-unchecked if another in same parent is checked
        self.rb_g2_opt3.setChecked(True)
        self.rb_g2_opt3.setEnabled(False)

        # To ensure Z2 can be selected and disabled, it needs its own group or careful management
        # For simplicity, we demonstrate individual disabled states.
        # If Z2 needs to be selected while disabled, it should be the only one checked in its auto-exclusive group.
        # Let's ensure Y2 is not checked to avoid conflict if they share the same implicit group.
        self.rb_g2_opt2.setChecked(False)

        rb_group2_layout.addWidget(self.rb_g2_opt1)
        rb_group2_layout.addWidget(self.rb_g2_opt2)
        rb_group2_layout.addWidget(self.rb_g2_opt3)
        rb_group2_layout.addStretch()
        layout.addLayout(rb_group2_layout)

        # If rb_g2_opt3 should be selected and disabled, ensure no other radio in its group is selected.
        # This might require putting it in a separate QWidget parent if auto-exclusivity is an issue.
        # For this demo, we'll assume they are in the same implicit group from the QGroupBox.
        # If self.rb_g2_opt1 is checked, self.rb_g2_opt3 will be unchecked.
        # To show a disabled selected radio, it's best if it's the only one initially checked in its group.
        # Let's make rb_g2_opt1 not checked by default.
        self.rb_g2_opt1.setChecked(False)

        # Signal Handling
        signal_layout = QHBoxLayout()
        self.rb_signal = FluentRadioButton("Listen to my toggle")
        self.rb_signal_label = QLabel(
            f"Selected: {self.rb_signal.isChecked()}")
        self.rb_signal.toggled.connect(self._on_radio_signal_toggled)
        signal_layout.addWidget(self.rb_signal)
        signal_layout.addWidget(self.rb_signal_label)
        signal_layout.addStretch()

        layout.addWidget(QLabel("Signal Handling (toggled):"))
        layout.addLayout(signal_layout)

        return group

    def _on_radio_signal_toggled(self, checked: bool):
        self.rb_signal_label.setText(f"Selected: {checked}")

    def _create_radiogroup_demo(self) -> QGroupBox:
        """Create FluentRadioGroup demonstration section"""
        group = QGroupBox("FluentRadioGroup")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Basic Usage & Signal
        layout.addWidget(QLabel("Basic Group & Signal (selection_changed):"))
        options1 = ["Apple", "Banana", "Cherry", "Date"]
        self.radio_group1 = FluentRadioGroup(options1)
        self.radio_group1_label = QLabel("Selected: None")
        self.radio_group1.selection_changed.connect(
            self._on_group1_selection_changed)
        layout.addWidget(self.radio_group1)
        layout.addWidget(self.radio_group1_label)

        # Programmatic Control
        layout.addWidget(QLabel("Programmatic Control:"))
        options2 = ["Dog", "Cat", "Bird", "Fish", "Lizard"]
        self.radio_group2 = FluentRadioGroup(options2)
        layout.addWidget(self.radio_group2)

        control_layout = QHBoxLayout()
        self.rg2_select_combo = QComboBox()
        for i, option in enumerate(options2):
            self.rg2_select_combo.addItem(f"{option} (Index {i})", i)

        btn_set_selected = QPushButton("Set Selected")
        btn_set_selected.clicked.connect(self._set_group2_selected)

        btn_get_selected = QPushButton("Get Selected")
        btn_get_selected.clicked.connect(self._get_group2_selected)

        control_layout.addWidget(self.rg2_select_combo)
        control_layout.addWidget(btn_set_selected)
        control_layout.addWidget(btn_get_selected)
        layout.addLayout(control_layout)
        self.radio_group2_status_label = QLabel("Status: ")
        layout.addWidget(self.radio_group2_status_label)

        # Disabled Group
        layout.addWidget(QLabel("Disabled Group:"))
        options3 = ["Red", "Green", "Blue"]
        self.radio_group3 = FluentRadioGroup(options3)
        self.radio_group3.setEnabled(False)  # Disable the whole group
        layout.addWidget(self.radio_group3)

        # Initially select an item in group1 and group2 for demo
        self.radio_group1.set_selected(1)  # Banana
        self.radio_group2.set_selected(0)  # Dog

        return group

    def _on_group1_selection_changed(self, index: int, text: str):
        self.radio_group1_label.setText(f"Selected: '{text}' at index {index}")

    def _set_group2_selected(self):
        index_to_select = self.rg2_select_combo.currentData()
        if index_to_select is not None:
            self.radio_group2.set_selected(index_to_select)
            self.radio_group2_status_label.setText(
                f"Status: Set to index {index_to_select}")

    def _get_group2_selected(self):
        index = self.radio_group2.get_selected_index()
        text = self.radio_group2.get_selected_text()
        self.radio_group2_status_label.setText(
            f"Status: Current is '{text}' at index {index}")

    def _create_interactive_demo(self) -> QGroupBox:
        """Create interactive demonstration section"""
        group = QGroupBox("Interactive Demo")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Checkbox to enable/disable RadioGroup
        self.interactive_cb = FluentCheckBox("Enable RadioGroup below")
        self.interactive_cb.setChecked(True)  # Initially enabled

        options = ["Option Alpha", "Option Beta", "Option Gamma"]
        self.interactive_radiogroup = FluentRadioGroup(options)

        self.interactive_cb.toggled.connect(
            self.interactive_radiogroup.setEnabled)

        self.interactive_label = QLabel("RadioGroup Selection: None")
        self.interactive_radiogroup.selection_changed.connect(
            lambda index, text: self.interactive_label.setText(
                f"RadioGroup Selection: '{text}' (index {index})")
        )
        # Initial selection for interactive radio group
        self.interactive_radiogroup.set_selected(0)

        layout.addWidget(self.interactive_cb)
        layout.addWidget(self.interactive_radiogroup)
        layout.addWidget(self.interactive_label)

        return group

    def _toggle_theme(self, theme_name: str):
        """Toggle between light and dark themes"""
        if theme_name == "Dark":
            theme_manager.set_theme_mode(ThemeMode.DARK)
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)


def main():
    """Run the checkbox and radio button demo application"""
    app = QApplication(sys.argv)

    # Optional: Set application style if not handled by theme_manager or for consistency
    # app.setStyle('Fusion')

    # Create and show demo window
    demo = CheckboxRadioDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
