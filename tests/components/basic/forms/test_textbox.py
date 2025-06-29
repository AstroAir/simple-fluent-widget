import pytest
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit

from components.basic.forms.textbox import (
    FluentLineEdit,
    FluentTextEdit,
    FluentPasswordEdit,
    FluentSearchBox,
    FluentNumericEdit
)

# Fixture for QApplication instance


@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestFluentLineEdit:
    @pytest.fixture
    def line_edit(self, qtbot, app_instance):
        widget = FluentLineEdit()
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, line_edit):
        assert line_edit.placeholderText() == ""
        assert line_edit.minimumHeight() == 32
        assert not line_edit._fluent_base._is_focused
        assert not line_edit._fluent_base._is_hovered

    def test_placeholder(self, line_edit):
        line_edit.setPlaceholderText("Enter text...")
        assert line_edit.placeholderText() == "Enter text..."

    def test_focus_events(self, line_edit, qtbot):
        line_edit.show()
        line_edit.setFocus()
        qtbot.waitUntil(lambda: line_edit._fluent_base._is_focused)
        assert line_edit._fluent_base._is_focused

        line_edit.clearFocus()
        qtbot.waitUntil(lambda: not line_edit._fluent_base._is_focused)
        assert not line_edit._fluent_base._is_focused

    def test_hover_events(self, line_edit, qtbot):
        line_edit.show()
        qtbot.mouseMove(line_edit)
        qtbot.waitUntil(lambda: line_edit._fluent_base._is_hovered)
        assert line_edit._fluent_base._is_hovered

        # Create a dummy widget to move the mouse to, ensuring a leave event
        dummy = QWidget()
        qtbot.addWidget(dummy)
        dummy.move(line_edit.mapToGlobal(
            line_edit.rect().topRight()) + QPoint(10, 0))
        dummy.show()

        qtbot.mouseMove(dummy)
        qtbot.waitUntil(lambda: not line_edit._fluent_base._is_hovered)
        assert not line_edit._fluent_base._is_hovered

    def test_disabled_state(self, line_edit):
        line_edit.setEnabled(False)
        assert not line_edit.isEnabled()


class TestFluentTextEdit:
    @pytest.fixture
    def text_edit(self, qtbot, app_instance):
        widget = FluentTextEdit()
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, text_edit):
        assert text_edit.placeholderText() == ""
        assert text_edit.minimumHeight() == 80

    def test_placeholder(self, text_edit):
        text_edit.setPlaceholderText("Enter multi-line text...")
        assert text_edit.placeholderText() == "Enter multi-line text..."

    def test_focus_events(self, text_edit, qtbot):
        text_edit.show()
        text_edit.setFocus()
        qtbot.waitUntil(lambda: text_edit._fluent_base._is_focused)
        assert text_edit._fluent_base._is_focused

        text_edit.clearFocus()
        qtbot.waitUntil(lambda: not text_edit._fluent_base._is_focused)
        assert not text_edit._fluent_base._is_focused


class TestFluentPasswordEdit:
    @pytest.fixture
    def password_edit(self, qtbot, app_instance):
        widget = FluentPasswordEdit()
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, password_edit):
        assert password_edit.echoMode() == QLineEdit.EchoMode.Password
        assert password_edit.placeholderText() == "Enter password"


class TestFluentSearchBox:
    @pytest.fixture
    def search_box(self, qtbot, app_instance):
        widget = FluentSearchBox()
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, search_box):
        assert search_box.placeholderText() == "Search..."

    def test_search_triggered_signal(self, search_box, qtbot):
        search_box.setText("test query")
        with qtbot.waitSignal(search_box.search_triggered, check_params_cb=lambda text: text == "test query", timeout=500):
            qtbot.keyClick(search_box, Qt.Key.Key_Return)

    def test_search_not_triggered_on_empty(self, search_box, qtbot):
        search_box.setText("   ")  # Whitespace should be stripped
        with qtbot.assertNotEmitted(search_box.search_triggered):
            qtbot.keyClick(search_box, Qt.Key.Key_Return)


class TestFluentNumericEdit:
    @pytest.fixture
    def numeric_edit(self, qtbot, app_instance):
        widget = FluentNumericEdit(minimum=10, maximum=50, decimals=2)
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, numeric_edit):
        assert numeric_edit._minimum == 10
        assert numeric_edit._maximum == 50
        assert numeric_edit._decimals == 2
        assert numeric_edit.text() == "10.00"
        assert numeric_edit.get_value() == 10.0

    def test_set_value(self, numeric_edit):
        numeric_edit.set_value(25.55)
        assert numeric_edit.text() == "25.55"
        assert numeric_edit.get_value() == 25.55

    def test_value_clamping(self, numeric_edit):
        numeric_edit.set_value(100)
        assert numeric_edit.get_value() == 50.0
        numeric_edit.set_value(0)
        assert numeric_edit.get_value() == 10.0

    def test_text_change_emits_signal(self, numeric_edit, qtbot):
        with qtbot.waitSignal(numeric_edit.value_changed, check_params_cb=lambda v: abs(v - 30.12) < 1e-9, timeout=500):
            qtbot.keyClicks(numeric_edit, "30.12")
        assert abs(numeric_edit.get_value() - 30.12) < 1e-9

    def test_set_range(self, numeric_edit):
        numeric_edit.set_range(-50, 50)
        assert numeric_edit._minimum == -50
        assert numeric_edit._maximum == 50

        # Check if value is clamped to new range
        numeric_edit.set_value(100)
        assert numeric_edit.get_value() == 50.0

        numeric_edit.set_value(-100)
        assert numeric_edit.get_value() == -50.0