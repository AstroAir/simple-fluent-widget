import pytest
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication

from components.basic.forms.slider import FluentSlider, FluentRangeSlider, FluentVolumeSlider

# Fixture for QApplication instance


@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestFluentSlider:
    @pytest.fixture
    def slider(self, qtbot, app_instance):
        widget = FluentSlider()
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, slider):
        assert slider.orientation() == Qt.Orientation.Horizontal
        assert slider._slider_style == FluentSlider.SliderStyle.STANDARD
        assert slider._size == FluentSlider.Size.MEDIUM
        assert slider.minimum() == 0
        assert slider.maximum() == 100
        assert slider.value() == 0

    def test_set_value(self, slider):
        slider.setValue(75)
        assert slider.value() == 75

    def test_set_style_and_size(self, slider):
        initial_height = slider.minimumHeight()
        slider.set_style(FluentSlider.SliderStyle.ACCENT)
        assert slider._slider_style == FluentSlider.SliderStyle.ACCENT

        slider.set_size(FluentSlider.Size.LARGE)
        assert slider._size == FluentSlider.Size.LARGE
        assert slider.minimumHeight() > initial_height

    def test_signals_on_drag(self, slider, qtbot):
        slider.show()
        slider.setRange(0, 100)
        slider.setValue(0)

        # Simulate pressing the slider handle
        qtbot.mousePress(slider, Qt.MouseButton.LeftButton,
                         pos=QPoint(10, slider.height() // 2))
        assert slider._is_dragging

        # Simulate dragging
        with qtbot.waitSignal(slider.value_changing, timeout=500) as changing_blocker:
            qtbot.mouseMove(slider, pos=QPoint(
                slider.width() // 2, slider.height() // 2))

        assert changing_blocker.args[0] > 0

        # Simulate releasing the slider
        with qtbot.waitSignal(slider.value_changed_final, timeout=500) as final_blocker:
            qtbot.mouseRelease(slider, Qt.MouseButton.LeftButton, pos=QPoint(
                slider.width() // 2, slider.height() // 2))

        assert not slider._is_dragging
        assert final_blocker.args[0] == slider.value()


class TestFluentRangeSlider:
    @pytest.fixture
    def range_slider(self, qtbot, app_instance):
        widget = FluentRangeSlider()
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, range_slider):
        assert range_slider._minimum == 0
        assert range_slider._maximum == 100
        assert range_slider.get_values() == (25, 75)

    def test_set_values(self, range_slider):
        range_slider.set_values(10, 90)
        assert range_slider.get_values() == (10, 90)

        # Test clamping
        range_slider.set_values(-10, 110)
        assert range_slider.get_values() == (0, 100)

        # Test that low is always <= high
        range_slider.set_values(80, 20)
        assert range_slider.get_values() == (20, 80)

    def test_drag_low_handle(self, range_slider, qtbot):
        range_slider.set_values(25, 75)
        range_slider.show()
        qtbot.waitUntil(lambda: range_slider._track_rect is not None)

        # Calculate position of the low handle
        low_handle_x = range_slider._track_rect.left() + range_slider._low_handle_pos
        center_y = range_slider.height() // 2

        qtbot.mousePress(range_slider, Qt.MouseButton.LeftButton,
                         pos=QPoint(low_handle_x, center_y))
        assert range_slider._dragging_handle == 'low'

        with qtbot.waitSignal(range_slider.range_changing, timeout=500):
            # Move to a new position (e.g., 10%)
            new_x = range_slider._track_rect.left() + int(range_slider._track_rect.width() * 0.1)
            qtbot.mouseMove(range_slider, pos=QPoint(new_x, center_y))

        assert range_slider.get_values()[0] < 25

        with qtbot.waitSignal(range_slider.range_changed, timeout=500):
            qtbot.mouseRelease(range_slider, Qt.MouseButton.LeftButton)

        assert range_slider._dragging_handle is None

    def test_drag_high_handle(self, range_slider, qtbot):
        range_slider.set_values(25, 75)
        range_slider.show()
        qtbot.waitUntil(lambda: range_slider._track_rect is not None)

        # Calculate position of the high handle
        high_handle_x = range_slider._track_rect.left() + range_slider._high_handle_pos
        center_y = range_slider.height() // 2

        qtbot.mousePress(range_slider, Qt.MouseButton.LeftButton,
                         pos=QPoint(high_handle_x, center_y))
        assert range_slider._dragging_handle == 'high'

        with qtbot.waitSignal(range_slider.range_changing, timeout=500):
            # Move to a new position (e.g., 90%)
            new_x = range_slider._track_rect.left() + int(range_slider._track_rect.width() * 0.9)
            qtbot.mouseMove(range_slider, pos=QPoint(new_x, center_y))

        assert range_slider.get_values()[1] > 75

        with qtbot.waitSignal(range_slider.range_changed, timeout=500):
            qtbot.mouseRelease(range_slider, Qt.MouseButton.LeftButton)

        assert range_slider._dragging_handle is None


class TestFluentVolumeSlider:
    @pytest.fixture
    def volume_slider(self, qtbot, app_instance):
        widget = FluentVolumeSlider(value=50)
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, volume_slider):
        assert volume_slider.value() == 50
        assert not volume_slider.is_muted()
        assert volume_slider._volume_icon.text() == "🔊"

    def test_mute_toggle(self, volume_slider, qtbot):
        with qtbot.waitSignal(volume_slider.mute_toggled, check_params_cb=lambda muted: muted is True, timeout=500):
            qtbot.mouseClick(volume_slider._volume_icon,
                             Qt.MouseButton.LeftButton)

        assert volume_slider.is_muted()
        assert volume_slider.value() == 0
        assert volume_slider._volume_icon.text() == "🔇"
        assert volume_slider._volume_before_mute == 50

        with qtbot.waitSignal(volume_slider.mute_toggled, check_params_cb=lambda muted: muted is False, timeout=500):
            qtbot.mouseClick(volume_slider._volume_icon,
                             Qt.MouseButton.LeftButton)

        assert not volume_slider.is_muted()
        assert volume_slider.value() == 50
        assert volume_slider._volume_icon.text() == "🔊"
