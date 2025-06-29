import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from components.basic.forms.switch import FluentSwitch, FluentSwitchGroup

# Fixture for QApplication instance


@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestFluentSwitch:
    @pytest.fixture
    def switch(self, qtbot, app_instance):
        widget = FluentSwitch()
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, switch):
        assert not switch.isChecked()
        assert switch.text() == ""
        assert switch._size == FluentSwitch.SIZE_MEDIUM
        assert switch._on_text == ""
        assert switch._off_text == ""
        assert switch.isEnabled()

    def test_custom_initialization(self, qtbot, app_instance):
        widget = FluentSwitch(
            text="Test Switch",
            checked=True,
            size=FluentSwitch.SIZE_LARGE,
            on_text="ON",
            off_text="OFF"
        )
        qtbot.addWidget(widget)
        assert widget.isChecked()
        assert widget.text() == "Test Switch"
        assert widget._size == FluentSwitch.SIZE_LARGE
        assert widget._on_text == "ON"
        assert widget._off_text == "OFF"

    def test_toggling_by_click(self, switch, qtbot):
        switch.show()
        with qtbot.waitSignal(switch.toggled, check_params_cb=lambda checked: checked is True, timeout=500):
            qtbot.mouseClick(switch, Qt.MouseButton.LeftButton)

        assert switch.isChecked()

        with qtbot.waitSignal(switch.toggled, check_params_cb=lambda checked: checked is False, timeout=500):
            qtbot.mouseClick(switch, Qt.MouseButton.LeftButton)

        assert not switch.isChecked()

    def test_set_checked_programmatically(self, switch, qtbot):
        with qtbot.waitSignal(switch.toggled, check_params_cb=lambda checked: checked is True, timeout=500):
            switch.setChecked(True)
        assert switch.isChecked()

        # Setting to the same state should not emit the signal again
        with qtbot.assertNotEmitted(switch.toggled):
            switch.setChecked(True)

        with qtbot.waitSignal(switch.toggled, check_params_cb=lambda checked: checked is False, timeout=500):
            switch.setChecked(False)
        assert not switch.isChecked()

    def test_toggle_method(self, switch, qtbot):
        assert not switch.isChecked()

        with qtbot.waitSignal(switch.toggled, timeout=500):
            switch.toggle()
        assert switch.isChecked()

        with qtbot.waitSignal(switch.toggled, timeout=500):
            switch.toggle()
        assert not switch.isChecked()

    def test_disabled_state(self, switch, qtbot):
        switch.setEnabled(False)
        assert not switch.isEnabled()

        # Clicks should not change the state
        with qtbot.assertNotEmitted(switch.toggled):
            qtbot.mouseClick(switch, Qt.MouseButton.LeftButton)

        assert not switch.isChecked()

    def test_size_change(self, switch):
        initial_size = switch.size()
        switch.setSize(FluentSwitch.SIZE_LARGE)
        assert switch.size() != initial_size
        assert switch._size == FluentSwitch.SIZE_LARGE

        large_size = switch.size()
        switch.setSize(FluentSwitch.SIZE_SMALL)
        assert switch.size() != large_size
        assert switch._size == FluentSwitch.SIZE_SMALL

    def test_text_properties(self, switch):
        switch.setText("New Label")
        assert switch.text() == "New Label"

        switch.setOnText("Yes")
        assert switch._on_text == "Yes"

        switch.setOffText("No")
        assert switch._off_text == "No"


class TestFluentSwitchGroup:
    @pytest.fixture
    def switch_group(self, qtbot, app_instance):
        widget = FluentSwitchGroup()
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, switch_group):
        assert len(switch_group.getSwitches()) == 0

    def test_add_and_get_switches(self, switch_group):
        s1 = FluentSwitch("Switch 1")
        s2 = FluentSwitch("Switch 2")

        switch_group.addSwitch(s1)
        switch_group.addSwitch(s2)

        switches = switch_group.getSwitches()
        assert len(switches) == 2
        assert s1 in switches
        assert s2 in switches

    def test_remove_switch(self, switch_group):
        s1 = FluentSwitch("Switch 1")
        s2 = FluentSwitch("Switch 2")
        switch_group.addSwitch(s1)
        switch_group.addSwitch(s2)

        assert len(switch_group.getSwitches()) == 2

        switch_group.removeSwitch(s1)

        switches = switch_group.getSwitches()
        assert len(switches) == 1
        assert s1 not in switches
        assert s2 in switches
        assert s1.parent() is None

    def test_set_enabled(self, switch_group):
        s1 = FluentSwitch("Switch 1")
        s2 = FluentSwitch("Switch 2")
        switch_group.addSwitch(s1)
        switch_group.addSwitch(s2)

        assert s1.isEnabled()
        assert s2.isEnabled()

        switch_group.setEnabled(False)

        assert not s1.isEnabled()
        assert not s2.isEnabled()

        switch_group.setEnabled(True)

        assert s1.isEnabled()
        assert s2.isEnabled()
