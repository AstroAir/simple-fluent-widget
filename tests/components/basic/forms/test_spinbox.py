import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget

from components.basic.forms.spinbox import (
    FluentSpinBox,
    FluentDoubleSpinBox,
    FluentNumberInput
)

# Fixture for QApplication instance


@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestFluentSpinBox:
    @pytest.fixture
    def spinbox(self, qtbot, app_instance):
        widget = FluentSpinBox()
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, spinbox):
        assert spinbox.minimumHeight() == 36
        assert spinbox.buttonSymbols() == FluentSpinBox.ButtonSymbols.UpDownArrows
        assert not spinbox._is_hovered
        assert not spinbox._is_focused

    def test_hover_events(self, spinbox, qtbot):
        spinbox.show()
        qtbot.mouseMove(spinbox)
        assert spinbox._is_hovered
        qtbot.waitUntil(lambda: spinbox._hover_group.state() ==
                        spinbox._hover_group.State.Running, timeout=500)

        qtbot.mouseMove(QWidget())  # Move mouse away
        qtbot.waitUntil(lambda: not spinbox._is_hovered, timeout=1000)
        qtbot.waitUntil(lambda: spinbox._hover_group.state() ==
                        spinbox._hover_group.State.Running, timeout=500)

    def test_focus_events(self, spinbox, qtbot):
        spinbox.show()
        spinbox.setFocus()
        assert spinbox.hasFocus()
        assert spinbox._is_focused
        qtbot.waitUntil(lambda: spinbox._focus_group.state() ==
                        spinbox._focus_group.State.Running, timeout=500)

        spinbox.clearFocus()
        assert not spinbox.hasFocus()
        assert not spinbox._is_focused
        qtbot.waitUntil(lambda: spinbox._focus_group.state() ==
                        spinbox._focus_group.State.Running, timeout=500)

    def test_set_value_animated(self, spinbox, qtbot):
        spinbox.show()
        with qtbot.waitSignal(spinbox.value_changed_animated, check_params_cb=lambda v: v == 50, timeout=1000):
            spinbox.set_value_animated(50)

        qtbot.waitUntil(lambda: spinbox.value() == 50, timeout=1000)
        assert spinbox.value() == 50
        assert not spinbox._is_animating

    def test_step_by(self, spinbox, qtbot):
        spinbox.show()
        spinbox.setValue(10)
        spinbox.stepBy(5)
        qtbot.waitUntil(lambda: spinbox.value() == 15, timeout=500)
        assert spinbox.value() == 15


class TestFluentDoubleSpinBox:
    @pytest.fixture
    def double_spinbox(self, qtbot, app_instance):
        widget = FluentDoubleSpinBox()
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, double_spinbox):
        assert double_spinbox.minimumHeight() == 36
        assert double_spinbox.buttonSymbols() == FluentDoubleSpinBox.ButtonSymbols.UpDownArrows

    def test_set_value_animated(self, double_spinbox, qtbot):
        double_spinbox.show()
        with qtbot.waitSignal(double_spinbox.value_changed_animated, check_params_cb=lambda v: v == 25.5, timeout=1000):
            double_spinbox.set_value_animated(25.5)

        qtbot.waitUntil(lambda: abs(
            double_spinbox.value() - 25.5) < 1e-9, timeout=1000)
        assert abs(double_spinbox.value() - 25.5) < 1e-9
        assert not double_spinbox._is_animating


class TestFluentNumberInput:
    @pytest.fixture
    def number_input(self, qtbot, app_instance):
        widget = FluentNumberInput(
            minimum=0, maximum=100, decimals=2, step=0.5)
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, number_input):
        assert isinstance(number_input.spin_box, FluentDoubleSpinBox)
        assert number_input.spin_box.minimum() == 0
        assert number_input.spin_box.maximum() == 100
        assert number_input.spin_box.decimals() == 2
        assert number_input.spin_box.singleStep() == 0.5
        assert number_input.value() == 0.0

    def test_integer_initialization(self, qtbot, app_instance):
        widget = FluentNumberInput(decimals=0)
        qtbot.addWidget(widget)
        assert isinstance(widget.spin_box, FluentSpinBox)

    def test_increase_button(self, number_input, qtbot):
        number_input.show()
        number_input.set_value(10.0)

        with qtbot.waitSignal(number_input.value_changed, check_params_cb=lambda v: abs(v - 10.5) < 1e-9, timeout=1000):
            qtbot.mouseClick(number_input.increase_btn,
                             Qt.MouseButton.LeftButton)

        qtbot.waitUntil(lambda: abs(number_input.value() - 10.5)
                        < 1e-9, timeout=1000)
        assert abs(number_input.value() - 10.5) < 1e-9

    def test_decrease_button(self, number_input, qtbot):
        number_input.show()
        number_input.set_value(10.0)

        with qtbot.waitSignal(number_input.value_changed, check_params_cb=lambda v: abs(v - 9.5) < 1e-9, timeout=1000):
            qtbot.mouseClick(number_input.decrease_btn,
                             Qt.MouseButton.LeftButton)

        qtbot.waitUntil(lambda: abs(number_input.value() - 9.5)
                        < 1e-9, timeout=1000)
        assert abs(number_input.value() - 9.5) < 1e-9

    def test_set_value(self, number_input, qtbot):
        number_input.show()
        with qtbot.waitSignal(number_input.value_changed, check_params_cb=lambda v: abs(v - 75.75) < 1e-9, timeout=1000):
            number_input.set_value(75.75)

        qtbot.waitUntil(lambda: abs(
            number_input.value() - 75.75) < 1e-9, timeout=1000)
        assert abs(number_input.value() - 75.75) < 1e-9

    def test_set_value_clamps_to_max(self, number_input, qtbot):
        number_input.show()
        with qtbot.waitSignal(number_input.value_changed, check_params_cb=lambda v: abs(v - 100.0) < 1e-9, timeout=1000):
            number_input.set_value(150.0)

        qtbot.waitUntil(lambda: abs(
            number_input.value() - 100.0) < 1e-9, timeout=1000)
        assert abs(number_input.value() - 100.0) < 1e-9
