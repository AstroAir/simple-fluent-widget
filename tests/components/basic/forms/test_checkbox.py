import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout

from components.basic.forms.checkbox import FluentCheckBox, FluentRadioButton, FluentRadioGroup

# Fixture for QApplication instance


@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestFluentCheckBox:
    def test_initialization(self, qtbot, app_instance):
        checkbox = FluentCheckBox("Test Checkbox")
        qtbot.addWidget(checkbox)
        assert checkbox.text() == "Test Checkbox"
        assert not checkbox.isChecked()
        assert not checkbox._is_checked

    def test_toggling_by_click(self, qtbot, app_instance):
        checkbox = FluentCheckBox("Click Me")
        qtbot.addWidget(checkbox)

        with qtbot.waitSignal(checkbox.stateChanged, timeout=500) as blocker:
            qtbot.mouseClick(checkbox, Qt.MouseButton.LeftButton)

        assert blocker.args == [Qt.CheckState.Checked.value]
        assert checkbox.isChecked()
        assert checkbox._is_checked

        with qtbot.waitSignal(checkbox.stateChanged, timeout=500) as blocker:
            qtbot.mouseClick(checkbox, Qt.MouseButton.LeftButton)

        assert blocker.args == [Qt.CheckState.Unchecked.value]
        assert not checkbox.isChecked()
        assert not checkbox._is_checked

    def test_set_checked_programmatically(self, qtbot, app_instance):
        checkbox = FluentCheckBox("Programmatic")
        qtbot.addWidget(checkbox)

        with qtbot.waitSignal(checkbox.stateChanged, timeout=500) as blocker:
            checkbox.setChecked(True)

        assert blocker.args == [Qt.CheckState.Checked.value]
        assert checkbox.isChecked()

        # Setting to the same state should not emit the signal
        with qtbot.assertNotEmitted(checkbox.stateChanged):
            checkbox.setChecked(True)

        with qtbot.waitSignal(checkbox.stateChanged, timeout=500) as blocker:
            checkbox.setChecked(False)

        assert blocker.args == [Qt.CheckState.Unchecked.value]
        assert not checkbox.isChecked()

    def test_disabled_state(self, qtbot, app_instance):
        checkbox = FluentCheckBox("Disabled")
        qtbot.addWidget(checkbox)

        checkbox.setEnabled(False)
        assert not checkbox.isEnabled()

        # Clicks should not change the state
        with qtbot.assertNotEmitted(checkbox.stateChanged):
            qtbot.mouseClick(checkbox, Qt.MouseButton.LeftButton)

        assert not checkbox.isChecked()


class TestFluentRadioButton:
    def test_initialization(self, qtbot, app_instance):
        radio = FluentRadioButton("Test Radio")
        qtbot.addWidget(radio)
        assert radio.text() == "Test Radio"
        assert not radio.isChecked()

    def test_auto_exclusivity_in_layout(self, qtbot, app_instance):
        parent = QWidget()
        layout = QVBoxLayout(parent)
        radio1 = FluentRadioButton("Option 1")
        radio2 = FluentRadioButton("Option 2")
        layout.addWidget(radio1)
        layout.addWidget(radio2)
        qtbot.addWidget(parent)

        radio1.setChecked(True)
        assert radio1.isChecked()
        assert not radio2.isChecked()

        radio2.setChecked(True)
        assert not radio1.isChecked()
        assert radio2.isChecked()


class TestFluentRadioGroup:
    @pytest.fixture
    def radio_group(self, qtbot, app_instance):
        options = ["Apple", "Banana", "Cherry"]
        group = FluentRadioGroup(options)
        qtbot.addWidget(group)
        return group

    def test_initialization(self, radio_group):
        assert len(radio_group._radio_buttons) == 3
        assert radio_group._radio_buttons[0].text() == "Apple"
        assert radio_group.get_selected_index() == -1
        assert radio_group.get_selected_text() == ""

    def test_selection_change(self, qtbot, radio_group):
        with qtbot.waitSignal(radio_group.selection_changed, timeout=500) as blocker:
            qtbot.mouseClick(
                radio_group._radio_buttons[1], Qt.MouseButton.LeftButton)

        assert blocker.args == [1, "Banana"]
        assert radio_group.get_selected_index() == 1
        assert radio_group.get_selected_text() == "Banana"
        assert not radio_group._radio_buttons[0].isChecked()
        assert radio_group._radio_buttons[1].isChecked()

    def test_set_selected_programmatically(self, qtbot, radio_group):
        with qtbot.waitSignal(radio_group.selection_changed, timeout=500) as blocker:
            radio_group.set_selected(2)

        assert blocker.args == [2, "Cherry"]
        assert radio_group.get_selected_index() == 2
        assert radio_group.get_selected_text() == "Cherry"
        assert radio_group._radio_buttons[2].isChecked()
