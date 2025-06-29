import pytest
from PySide6.QtCore import Qt, QEasingCurve
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

from components.basic.forms.toggle import FluentToggleSwitch, FluentExpandableToggle

# Fixture for QApplication instance


@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestFluentToggleSwitch:
    @pytest.fixture
    def switch(self, qtbot, app_instance):
        widget = FluentToggleSwitch("Test Toggle")
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, switch):
        assert switch.text() == "Test Toggle"
        assert not switch.isChecked()
        assert not switch._is_hovered
        assert not switch._is_pressed
        assert switch._thumb_position == 0.0

    def test_toggling_by_click(self, switch, qtbot):
        assert not switch.isChecked()

        with qtbot.waitSignal(switch.stateChanged, check_params_cb=lambda checked: checked is True, timeout=1000):
            qtbot.mouseClick(switch, Qt.MouseButton.LeftButton)

        assert switch.isChecked()
        qtbot.waitUntil(lambda: switch._thumb_animation.state()
                        == QPropertyAnimation.State.Stopped, timeout=500)
        assert switch._thumb_position == 1.0

        with qtbot.waitSignal(switch.stateChanged, check_params_cb=lambda checked: checked is False, timeout=1000):
            qtbot.mouseClick(switch, Qt.MouseButton.LeftButton)

        assert not switch.isChecked()
        qtbot.waitUntil(lambda: switch._thumb_animation.state()
                        == QPropertyAnimation.State.Stopped, timeout=500)
        assert switch._thumb_position == 0.0

    def test_set_checked_programmatically(self, switch, qtbot):
        with qtbot.waitSignal(switch.stateChanged, check_params_cb=lambda checked: checked is True, timeout=1000):
            switch.setChecked(True)

        assert switch.isChecked()
        qtbot.waitUntil(lambda: switch._thumb_animation.state()
                        == QPropertyAnimation.State.Stopped, timeout=500)
        assert switch._thumb_position == 1.0

    def test_set_checked_without_animation(self, switch, qtbot):
        switch.set_checked_without_animation(True)
        assert switch.isChecked()
        assert switch._thumb_position == 1.0

        # Should not emit stateChanged signal
        with qtbot.assertNotEmitted(switch.stateChanged):
            switch.set_checked_without_animation(True)

    def test_disabled_state(self, switch, qtbot):
        switch.setEnabled(False)
        assert not switch.isEnabled()

        # Clicks should not change the state
        with qtbot.assertNotEmitted(switch.stateChanged):
            qtbot.mouseClick(switch, Qt.MouseButton.LeftButton, timeout=500)

        assert not switch.isChecked()

    def test_hover_events(self, switch, qtbot):
        switch.show()
        assert not switch._is_hovered

        qtbot.mouseMove(switch)
        assert switch._is_hovered

        qtbot.mouseMove(QWidget())  # Move mouse away
        assert not switch._is_hovered

    def test_custom_properties(self, switch):
        switch.setTrackWidth(50)
        assert switch._track_width == 50

        switch.setThumbSize(25)
        assert switch._thumb_size == 25

        switch.setAnimationDuration(500)
        assert switch._animation_duration == 500
        assert switch._thumb_animation.duration() == 500

        switch.setAnimationCurve(QEasingCurve.Type.InQuad)
        assert switch._animation_curve == QEasingCurve.Type.InQuad
        assert switch._thumb_animation.easingCurve().type() == QEasingCurve.Type.InQuad


class TestFluentExpandableToggle:
    @pytest.fixture
    def expandable_toggle(self, qtbot, app_instance):
        parent_widget = QWidget()
        layout = QVBoxLayout(parent_widget)

        toggle = FluentExpandableToggle("Expand Me")
        content = QLabel("This is the content")
        toggle.set_content_widget(content)

        layout.addWidget(toggle)
        layout.addWidget(content)

        qtbot.addWidget(parent_widget)
        parent_widget.show()

        return toggle, content

    def test_initialization(self, expandable_toggle):
        toggle, content = expandable_toggle
        assert toggle.text() == "Expand Me"
        assert not toggle.isChecked()
        assert not toggle._expanded
        assert content.maximumHeight() == 0

    def test_toggling_by_click_expands_content(self, expandable_toggle, qtbot):
        toggle, content = expandable_toggle
        content_height = content.sizeHint().height()

        with qtbot.waitSignal(toggle.expandChanged, check_params_cb=lambda expanded: expanded is True, timeout=1000):
            qtbot.mouseClick(toggle, Qt.MouseButton.LeftButton)

        assert toggle.isChecked()
        assert toggle._expanded
        qtbot.waitUntil(lambda: content.maximumHeight() == content_height, timeout=500)

        with qtbot.waitSignal(toggle.expandChanged, check_params_cb=lambda expanded: expanded is False, timeout=1000):
            qtbot.mouseClick(toggle, Qt.MouseButton.LeftButton)

        assert not toggle.isChecked()
        assert not toggle._expanded
        qtbot.waitUntil(lambda: content.maximumHeight() == 0, timeout=500)

    def test_set_content_widget(self, qtbot, app_instance):
        toggle = FluentExpandableToggle("Test")
        qtbot.addWidget(toggle)

        assert toggle._content_widget is None

        content = QWidget()
        toggle.set_content_widget(content)

        assert toggle._content_widget is content
        assert content.maximumHeight() == 0
        assert content.isVisible()