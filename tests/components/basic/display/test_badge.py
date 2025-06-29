import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor

from components.basic.display.badge import FluentBadge, FluentTag, FluentStatusIndicator

# Fixture for QApplication instance


@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestFluentBadge:
    def test_initialization(self, qtbot):
        badge = FluentBadge(text="New")
        qtbot.addWidget(badge)
        assert badge._text == "New"
        assert badge._badge_type == FluentBadge.BadgeType.DEFAULT
        assert not badge._dot_mode

    def test_dot_mode_initialization(self, qtbot):
        badge = FluentBadge(dot=True)
        qtbot.addWidget(badge)
        assert badge._dot_mode
        assert badge.width() == 8
        assert badge.height() == 8
        assert not badge._label.isVisible()

    def test_set_text(self, qtbot):
        badge = FluentBadge(text="Initial")
        qtbot.addWidget(badge)
        badge.setText("Updated")
        assert badge._text == "Updated"
        assert badge._label.text() == "Updated"

    def test_set_badge_type(self, qtbot):
        badge = FluentBadge(text="Info")
        qtbot.addWidget(badge)

        badge.setBadgeType(FluentBadge.BadgeType.SUCCESS)
        assert badge._badge_type == FluentBadge.BadgeType.SUCCESS
        # We can't easily check the color from stylesheet, but we can check the internal color cache
        colors = badge._get_theme_colors()
        # This is a bit of an implementation detail test, but it's the easiest way to verify
        # Check for green-ish color
        assert "107c10" in colors['bg'] or "0d7377" in colors['bg']

        badge.setBadgeType(FluentBadge.BadgeType.ERROR)
        assert badge._badge_type == FluentBadge.BadgeType.ERROR
        colors = badge._get_theme_colors()
        # Check for red-ish color
        assert "d13438" in colors['bg'] or "dc2626" in colors['bg']

    def test_set_dot_mode(self, qtbot):
        badge = FluentBadge(text="99+")
        qtbot.addWidget(badge)

        badge.setDotMode(True)
        qtbot.waitUntil(lambda: badge.width() == 8, timeout=500)
        assert badge._dot_mode
        assert badge.width() == 8
        assert badge.height() == 8
        assert not badge._label.isVisible()

        badge.setDotMode(False)
        qtbot.waitUntil(lambda: badge.width() != 8, timeout=500)
        assert not badge._dot_mode
        assert badge.height() == 20
        assert badge._label.isVisible()


class TestFluentTag:
    def test_initialization(self, qtbot):
        tag = FluentTag(text="My Tag")
        qtbot.addWidget(tag)
        assert tag._text == "My Tag"
        assert tag._variant == FluentTag.TagVariant.DEFAULT
        assert not tag._closable
        assert not hasattr(tag, '_close_btn')

    def test_closable_tag(self, qtbot):
        tag = FluentTag(text="Closable", closable=True)
        qtbot.addWidget(tag)
        assert tag._closable
        assert hasattr(tag, '_close_btn')

        with qtbot.waitSignal(tag.closed, timeout=1000):
            QTest.mouseClick(tag._close_btn, Qt.MouseButton.LeftButton)

    def test_click_signal(self, qtbot):
        tag = FluentTag(text="Click Me")
        qtbot.addWidget(tag)
        with qtbot.waitSignal(tag.clicked, timeout=500):
            QTest.mouseClick(tag, Qt.MouseButton.LeftButton)

    def test_set_variant(self, qtbot):
        tag = FluentTag(text="Variant")
        qtbot.addWidget(tag)

        tag.setVariant(FluentTag.TagVariant.FILLED)
        assert tag._variant == FluentTag.TagVariant.FILLED

        tag.setVariant(FluentTag.TagVariant.OUTLINE)
        assert tag._variant == FluentTag.TagVariant.OUTLINE

    def test_set_color(self, qtbot):
        tag = FluentTag(text="Colored")
        qtbot.addWidget(tag)

        custom_color = "#ff00ff"
        tag.setColor(custom_color)
        assert tag._color == custom_color

        # Check if the new color is applied
        colors = tag._get_theme_colors()
        assert colors['primary'] == custom_color


class TestFluentStatusIndicator:
    def test_initialization(self, qtbot):
        indicator = FluentStatusIndicator()
        qtbot.addWidget(indicator)
        assert indicator._status == FluentStatusIndicator.Status.UNKNOWN
        assert indicator.width() == 12
        assert indicator.height() == 12

    def test_set_status(self, qtbot):
        indicator = FluentStatusIndicator()
        qtbot.addWidget(indicator)

        indicator.setStatus(FluentStatusIndicator.Status.ONLINE)
        assert indicator._status == FluentStatusIndicator.Status.ONLINE

        indicator.setStatus(FluentStatusIndicator.Status.OFFLINE)
        assert indicator._status == FluentStatusIndicator.Status.OFFLINE

    def test_set_size(self, qtbot):
        indicator = FluentStatusIndicator(size=12)
        qtbot.addWidget(indicator)

        indicator.setSize(24)
        qtbot.waitUntil(lambda: indicator.width() == 24, timeout=500)
        assert indicator._size == 24
        assert indicator.width() == 24
        assert indicator.height() == 24
