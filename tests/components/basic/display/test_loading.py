import pytest
from PySide6.QtCore import QPropertyAnimation, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QWidget, QGraphicsOpacityEffect

from components.basic.display.loading import (
    FluentSpinner,
    FluentDotLoader,
    FluentProgressRing,
    FluentLoadingOverlay,
    FluentPulseLoader
)

# Fixture for QApplication instance
@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

class TestFluentSpinner:
    def test_initialization(self, qtbot):
        spinner = FluentSpinner()
        qtbot.addWidget(spinner)
        assert spinner._size == 32
        assert spinner._line_width == 3
        assert spinner._color is None
        assert not spinner.isRunning()
        assert spinner.size() == QSize(32, 32)

    def test_start_stop(self, qtbot):
        spinner = FluentSpinner()
        qtbot.addWidget(spinner)

        spinner.start()
        assert spinner.isRunning()
        assert spinner._rotation_animation.state() == QPropertyAnimation.State.Running

        spinner.stop()
        assert not spinner.isRunning()
        assert spinner._rotation_animation.state() == QPropertyAnimation.State.Stopped

    def test_property_setters(self, qtbot):
        spinner = FluentSpinner()
        qtbot.addWidget(spinner)

        spinner.setSize(48)
        assert spinner._size == 48
        assert spinner.size() == QSize(48, 48)

        spinner.setLineWidth(5)
        assert spinner._line_width == 5

        spinner.setColor(QColor("red"))
        assert spinner._color == QColor("red")


class TestFluentDotLoader:
    def test_initialization(self, qtbot):
        loader = FluentDotLoader()
        qtbot.addWidget(loader)
        assert loader._dot_count == 3
        assert loader._dot_size == 8
        assert loader._spacing == 4
        assert not loader.isRunning()

    def test_start_stop(self, qtbot):
        loader = FluentDotLoader()
        qtbot.addWidget(loader)

        loader.start()
        assert loader.isRunning()
        assert loader._phase_animation.state() == QPropertyAnimation.State.Running

        loader.stop()
        assert not loader.isRunning()
        assert loader._phase_animation.state() == QPropertyAnimation.State.Stopped


class TestFluentProgressRing:
    def test_initialization(self, qtbot):
        ring = FluentProgressRing()
        qtbot.addWidget(ring)
        assert ring._size == 48
        assert ring._line_width == 4
        assert not ring.isIndeterminate()
        assert ring.value() == 0.0

    def test_set_value_animated(self, qtbot):
        ring = FluentProgressRing()
        qtbot.addWidget(ring)

        ring.setValue(0.75, animate=True)
        qtbot.waitUntil(lambda: abs(ring.value() - 0.75) < 0.01, timeout=1000)
        assert abs(ring.value() - 0.75) < 0.01

    def test_set_value_not_animated(self, qtbot):
        ring = FluentProgressRing()
        qtbot.addWidget(ring)

        ring.setValue(0.5, animate=False)
        assert ring.value() == 0.5

    def test_set_indeterminate(self, qtbot):
        ring = FluentProgressRing(indeterminate=False)
        qtbot.addWidget(ring)

        ring.setIndeterminate(True)
        assert ring.isIndeterminate()
        assert ring._rotation_animation.state() == QPropertyAnimation.State.Running

        ring.setIndeterminate(False)
        assert not ring.isIndeterminate()
        assert ring._rotation_animation.state() == QPropertyAnimation.State.Stopped


class TestFluentLoadingOverlay:
    def test_initialization(self, qtbot):
        parent = QWidget()
        overlay = FluentLoadingOverlay(parent=parent)
        qtbot.addWidget(parent) # qtbot manages parent's lifecycle

        assert overlay.parent() is parent
        assert overlay._text == "Loading..."
        assert overlay._spinner_size == 48
        effect = overlay.graphicsEffect()
        if effect and isinstance(effect, QGraphicsOpacityEffect):
            assert effect.opacity() == 0.0

    def test_show_hide(self, qtbot):
        parent = QWidget()
        parent.setFixedSize(200, 200)
        overlay = FluentLoadingOverlay(parent=parent)
        qtbot.addWidget(parent)

        overlay.show()
        qtbot.waitUntil(lambda: overlay.isVisible(), timeout=500)
        
        def check_opacity_high():
            effect = overlay.graphicsEffect()
            return effect and isinstance(effect, QGraphicsOpacityEffect) and effect.opacity() > 0.9
        
        qtbot.waitUntil(check_opacity_high, timeout=500)
        assert overlay._spinner.isRunning()

        overlay.hide()
        qtbot.waitUntil(lambda: not overlay.isVisible(), timeout=1000)
        
        effect = overlay.graphicsEffect()
        if effect and isinstance(effect, QGraphicsOpacityEffect):
            assert effect.opacity() < 0.1
        assert not overlay._spinner.isRunning()

    def test_event_filter(self, qtbot):
        parent = QWidget()
        parent.setFixedSize(200, 200)
        overlay = FluentLoadingOverlay(parent=parent)
        qtbot.addWidget(parent)
        overlay.show()
        qtbot.wait(100) # allow show to complete

        parent.resize(300, 300)
        # The event filter should handle the resize
        qtbot.waitUntil(lambda: overlay.size() == QSize(300, 300), timeout=500)
        assert overlay.size() == QSize(300, 300)


class TestFluentPulseLoader:
    def test_initialization(self, qtbot):
        loader = FluentPulseLoader()
        qtbot.addWidget(loader)
        assert loader._size == 40
        assert not loader._running

    def test_start_stop(self, qtbot):
        loader = FluentPulseLoader()
        qtbot.addWidget(loader)

        loader.start()
        assert loader._running
        assert loader._animation_group.state() == QPropertyAnimation.State.Running

        loader.stop()
        assert not loader._running
        assert loader._animation_group.state() == QPropertyAnimation.State.Stopped

    def test_property_setters(self, qtbot):
        loader = FluentPulseLoader()
        qtbot.addWidget(loader)

        loader.setScaleValue(1.1)
        assert loader._scale == 1.1

        loader.setOpacityValue(0.5)
        assert loader._opacity == 0.5