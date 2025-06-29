import pytest
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation
from PySide6.QtWidgets import QApplication

from components.basic.display.progress import FluentProgressBar, FluentSlider, FluentRangeSlider

# Make sure a QApplication instance exists for the test session
@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestFluentProgressBar:
    def test_initialization(self, qtbot):
        widget = FluentProgressBar()
        qtbot.addWidget(widget)
        assert widget.value() == 0
        assert not widget.is_indeterminate()
        assert widget._state == 'normal'
        assert widget.minimumHeight() == 4
        assert widget.maximumHeight() == 4

    def test_set_value_animated(self, qtbot):
        widget = FluentProgressBar()
        qtbot.addWidget(widget)

        widget.set_value_animated(50)

        # Wait for animation to finish
        qtbot.waitUntil(lambda: widget.value() == 50, timeout=1000)

        assert widget.value() == 50

        # Test completion animation trigger
        widget.set_value_animated(100)
        qtbot.waitUntil(lambda: widget.value() == 100, timeout=1000)
        assert widget.value() == 100

    def test_set_indeterminate(self, qtbot):
        widget = FluentProgressBar()
        qtbot.addWidget(widget)

        widget.set_indeterminate(True)
        assert widget.is_indeterminate()
        assert widget._state == 'indeterminate'
        if widget._indeterminate_animation is not None:
            assert widget._indeterminate_animation.state() == QPropertyAnimation.State.Running

        widget.set_indeterminate(False)
        assert not widget.is_indeterminate()
        assert widget._state == 'normal'
        if widget._indeterminate_animation is not None:
            assert widget._indeterminate_animation.state() == QPropertyAnimation.State.Stopped

    def test_set_state(self, qtbot):
        widget = FluentProgressBar()
        qtbot.addWidget(widget)

        widget.set_state('error')
        assert widget._state == 'error'

        widget.set_state('success')
        assert widget._state == 'success'

        widget.set_state('paused')
        assert widget._state == 'paused'

    def test_show_percentage(self, qtbot):
        widget = FluentProgressBar()
        qtbot.addWidget(widget)

        widget.set_show_percentage(True)
        assert widget.isTextVisible()
        assert widget.minimumHeight() == 20
        assert widget.maximumHeight() == 20

        widget.set_show_percentage(False)
        assert not widget.isTextVisible()
        assert widget.minimumHeight() == 4
        assert widget.maximumHeight() == 4


class TestFluentSlider:
    def test_initialization(self, qtbot):
        widget = FluentSlider()
        qtbot.addWidget(widget)
        assert widget.orientation() == Qt.Orientation.Horizontal
        assert not widget._is_dragging
        assert not widget._is_hovering

    def test_set_value_animated(self, qtbot):
        widget = FluentSlider()
        qtbot.addWidget(widget)

        widget.set_value_animated(50)
        qtbot.waitUntil(lambda: widget.value() == 50, timeout=1000)
        assert widget.value() == 50

    def test_mouse_interaction(self, qtbot):
        widget = FluentSlider(Qt.Orientation.Horizontal)
        widget.setRange(0, 100)
        qtbot.addWidget(widget)
        widget.show()

        # Press
        press_pos = widget.rect().center()
        qtbot.mousePress(widget, Qt.MouseButton.LeftButton, pos=press_pos)
        assert widget._is_dragging

        # Drag
        move_pos = QPoint(widget.rect().center().x() + 20, widget.rect().center().y())
        qtbot.mouseMove(widget, move_pos)
        qtbot.wait(50)  # give it time to process
        assert widget.value() > 50  # Assuming it was at 50 initially

        # Release
        qtbot.mouseRelease(widget, Qt.MouseButton.LeftButton, pos=move_pos)
        assert not widget._is_dragging


class TestFluentRangeSlider:
    def test_initialization(self, qtbot):
        widget = FluentRangeSlider()
        qtbot.addWidget(widget)
        assert widget.minimum() == 0
        assert widget.maximum() == 100
        assert widget.range_minimum() == 20
        assert widget.range_maximum() == 80
        assert not widget._dragging_min
        assert not widget._dragging_max

    def test_set_range(self, qtbot):
        widget = FluentRangeSlider()
        qtbot.addWidget(widget)

        widget.set_range(0, 200)
        assert widget.minimum() == 0
        assert widget.maximum() == 200

        # Test clamping
        widget.set_values(10, 90)
        widget.set_range(30, 150)
        assert widget.range_minimum() == 30
        assert widget.range_maximum() == 90

    def test_set_values(self, qtbot):
        widget = FluentRangeSlider()
        qtbot.addWidget(widget)

        widget.set_values(30, 70)
        assert widget.range_minimum() == 30
        assert widget.range_maximum() == 70

        # Test invalid range (min > max)
        widget.set_values(80, 40)
        assert widget.range_minimum() == 40
        assert widget.range_maximum() == 80

    def test_keyboard_navigation(self, qtbot):
        widget = FluentRangeSlider()
        widget.set_range(0, 100)
        widget.set_values(20, 80)
        qtbot.addWidget(widget)
        widget.show()
        widget.setFocus()

        # Focus min thumb
        assert widget._focused_thumb == 'min'

        # Move min thumb right
        qtbot.keyClick(widget, Qt.Key.Key_Right)
        assert widget.range_minimum() == 21

        # Switch focus to max thumb
        qtbot.keyClick(widget, Qt.Key.Key_Tab)
        assert widget._focused_thumb == 'max'

        # Move max thumb left
        qtbot.keyClick(widget, Qt.Key.Key_Left)
        assert widget.range_maximum() == 79

        # Switch back to min thumb
        qtbot.keyClick(widget, Qt.Key.Key_Tab)
        assert widget._focused_thumb == 'min'