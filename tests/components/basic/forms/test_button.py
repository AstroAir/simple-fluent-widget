import pytest
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget

from components.basic.forms.button import FluentButton, FluentIconButton, FluentToggleButton

# Fixture for QApplication instance


@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestFluentButton:
    def test_initialization(self, qtbot):
        button = FluentButton("Test Button")
        qtbot.addWidget(button)
        assert button.text() == "Test Button"
        assert button._button_style == FluentButton.ButtonStyle.PRIMARY
        assert button._button_size == FluentButton.Size.MEDIUM
        assert button._animation_level == FluentButton.AnimationLevel.STANDARD
        assert button.icon().isNull()

    def test_custom_initialization(self, qtbot):
        icon = QIcon()
        button = FluentButton(
            text="Custom",
            style=FluentButton.ButtonStyle.SECONDARY,
            icon=icon,
            size=FluentButton.Size.LARGE,
            animation_level=FluentButton.AnimationLevel.FLUID
        )
        qtbot.addWidget(button)
        assert button.text() == "Custom"
        assert button._button_style == FluentButton.ButtonStyle.SECONDARY
        assert not button.icon().isNull()
        assert button._button_size == FluentButton.Size.LARGE
        assert button._animation_level == FluentButton.AnimationLevel.FLUID

    def test_set_style(self, qtbot):
        button = FluentButton("Style Test")
        qtbot.addWidget(button)
        button.set_style(FluentButton.ButtonStyle.OUTLINE)
        assert button._button_style == FluentButton.ButtonStyle.OUTLINE

    def test_set_size(self, qtbot):
        button = FluentButton("Size Test")
        qtbot.addWidget(button)
        initial_height = button.minimumHeight()
        button.set_size(FluentButton.Size.LARGE)
        assert button._button_size == FluentButton.Size.LARGE
        assert button.minimumHeight() > initial_height

    def test_set_loading(self, qtbot):
        button = FluentButton("Loading Test")
        qtbot.addWidget(button)

        button.set_loading(True)
        assert button._is_loading
        assert not button.isEnabled()
        assert button.text() == "Loading..."

        button.set_loading(False)
        assert not button._is_loading
        assert button.isEnabled()
        # The text is not restored automatically, which is the expected behavior.
        assert button.text() == "Loading..."

    def test_expand_content(self, qtbot):
        button = FluentButton("Expandable")
        qtbot.addWidget(button)
        button.show()
        initial_width = button.width()

        with qtbot.waitSignal(button.animationFinished, check_params_cb=lambda s: s == "expand", timeout=1000):
            button.expand_content(True)

        assert button._is_expanded
        qtbot.waitUntil(lambda: button.width() > initial_width, timeout=500)

        expanded_width = button.width()

        with qtbot.waitSignal(button.animationFinished, check_params_cb=lambda s: s == "collapse", timeout=1000):
            button.expand_content(False)

        assert not button._is_expanded
        qtbot.waitUntil(lambda: button.width() < expanded_width, timeout=500)

    def test_hover_events(self, qtbot):
        button = FluentButton("Hover Test")
        qtbot.addWidget(button)
        button.show()

        with qtbot.waitSignal(button.hoverChanged, check_params_cb=lambda h: h is True, timeout=500):
            qtbot.mouseMove(button, button.rect().center())
        assert button._is_hovered

        # Create a dummy widget to move the mouse to, ensuring a leave event
        dummy = QWidget()
        qtbot.addWidget(dummy)
        dummy.move(button.mapToGlobal(
            button.rect().topRight()) + QPoint(10, 0))
        dummy.show()

        with qtbot.waitSignal(button.hoverChanged, check_params_cb=lambda h: h is False, timeout=500):
            qtbot.mouseMove(dummy)
        assert not button._is_hovered

    def test_press_and_click_events(self, qtbot):
        button = FluentButton("Click Test")
        qtbot.addWidget(button)
        button.show()

        qtbot.mousePress(button, Qt.MouseButton.LeftButton,
                         pos=button.rect().center())
        assert button._is_pressed

        with qtbot.waitSignal(button.clicked, timeout=500):
            qtbot.mouseRelease(
                button, Qt.MouseButton.LeftButton, pos=button.rect().center())

        assert not button._is_pressed


class TestFluentIconButton:
    def test_initialization(self, qtbot):
        # Use a valid path or resource
        icon = QIcon(":/qfluentwidgets/images/Close_dark.svg")
        button = FluentIconButton(icon=icon, text="Icon Button")
        qtbot.addWidget(button)
        assert button.text() == "Icon Button"
        assert not button.icon().isNull()
        assert button.iconSize() == QSize(20, 20)  # Default MEDIUM size

    def test_icon_size_changes_with_button_size(self, qtbot):
        # Use a valid path or resource
        icon = QIcon(":/qfluentwidgets/images/Close_dark.svg")
        button = FluentIconButton(icon=icon, size=FluentButton.Size.LARGE)
        qtbot.addWidget(button)
        assert button.iconSize() == QSize(22, 22)

        button.set_size(FluentButton.Size.SMALL)
        assert button.iconSize() == QSize(18, 18)


class TestFluentToggleButton:
    def test_initialization(self, qtbot):
        button = FluentToggleButton("Toggle Me")
        qtbot.addWidget(button)
        assert button.isCheckable()
        assert not button.isChecked()
        assert not button._is_toggled
        assert button._button_style == FluentButton.ButtonStyle.SECONDARY

    def test_toggling_by_click(self, qtbot):
        button = FluentToggleButton("Toggle Me")
        qtbot.addWidget(button)

        with qtbot.waitSignal(button.toggled, check_params_cb=lambda checked: checked is True, timeout=500):
            qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        assert button.isChecked()
        assert button._is_toggled
        assert button._button_style == FluentButton.ButtonStyle.PRIMARY

        with qtbot.waitSignal(button.toggled, check_params_cb=lambda checked: checked is False, timeout=500):
            qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        assert not button.isChecked()
        assert not button._is_toggled
        assert button._button_style == FluentButton.ButtonStyle.SECONDARY

    def test_set_toggled_programmatically(self, qtbot):
        button = FluentToggleButton("Toggle Me")
        qtbot.addWidget(button)

        with qtbot.waitSignal(button.toggled, check_params_cb=lambda checked: checked is True, timeout=500):
            button.set_toggled(True)

        assert button.isChecked()
        assert button._is_toggled
        assert button._button_style == FluentButton.ButtonStyle.PRIMARY

        with qtbot.waitSignal(button.toggled, check_params_cb=lambda checked: checked is False, timeout=500):
            button.set_toggled(False)

        assert not button.isChecked()
        assert not button._is_toggled
        assert button._button_style == FluentButton.ButtonStyle.SECONDARY
