import pytest
from unittest.mock import patch, MagicMock

from PySide6.QtCore import Qt, QPoint, QSize, QTimer
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtTest import QTest

from components.basic.display.tooltip import FluentTooltip, FluentTooltipManager, TooltipMixin, tooltip_manager

# Fixture for QApplication instance
@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

# Helper classes for testing the mixin
class WidgetWithTooltip(QWidget, TooltipMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        TooltipMixin.__init__(self)

class MockEnterLeaveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.enter_called = False
        self.leave_called = False

    def enterEvent(self, event):
        self.enter_called = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.leave_called = True
        super().leaveEvent(event)

class WidgetWithTooltipAndEvents(MockEnterLeaveWidget, TooltipMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        TooltipMixin.__init__(self)


class TestFluentTooltip:
    def test_initialization(self, qtbot):
        tooltip = FluentTooltip("Hello")
        qtbot.addWidget(tooltip)
        assert tooltip.getText() == "Hello"
        assert tooltip._opacity == 0.0
        assert not tooltip.isVisible()

    def test_set_text(self, qtbot):
        tooltip = FluentTooltip()
        qtbot.addWidget(tooltip)

        tooltip.setText("New Text")
        assert tooltip.getText() == "New Text"
        assert not tooltip._rich_text_mode

        tooltip.setText("<b>Bold</b>", rich_text=True)
        assert tooltip.getText() == "<b>Bold</b>"
        assert tooltip._rich_text_mode
        assert tooltip._label.textFormat() == Qt.TextFormat.RichText

    def test_show_hide_animated(self, qtbot):
        tooltip = FluentTooltip("Test")
        tooltip.setShowDelay(0)  # No delay for testing
        tooltip.setHideDelay(0)
        qtbot.addWidget(tooltip)

        # Show
        tooltip.showTooltip(QPoint(100, 100))
        qtbot.waitUntil(lambda: tooltip.isVisible(), timeout=500)
        qtbot.waitUntil(lambda: tooltip.opacity > 0.9, timeout=1000)
        assert not tooltip._is_showing  # Animation finished

        # Hide
        tooltip.hideTooltip()
        qtbot.waitUntil(lambda: tooltip.opacity < 0.1, timeout=1000)
        qtbot.waitUntil(lambda: not tooltip.isVisible(), timeout=1000)
        assert not tooltip._is_hiding  # Animation finished

    def test_auto_hide(self, qtbot):
        tooltip = FluentTooltip("Auto Hide")
        tooltip.setShowDelay(0)
        tooltip.setAutoHideDelay(100)  # 100ms auto-hide
        qtbot.addWidget(tooltip)

        tooltip.showTooltip(QPoint(100, 100))
        qtbot.waitUntil(lambda: tooltip.isVisible(), timeout=500)

        # It should auto-hide
        qtbot.waitUntil(lambda: not tooltip.isVisible(), timeout=1000)

    def test_set_custom_widget(self, qtbot):
        tooltip = FluentTooltip()
        qtbot.addWidget(tooltip)

        custom_label = QLabel("Custom Widget")
        tooltip.setWidget(custom_label)

        # Check if the custom widget is in the layout
        assert tooltip._content_layout.itemAt(1).widget() is custom_label

        # Check if clearing works
        tooltip.clearWidgets()
        assert tooltip._content_layout.count() == 1
        assert tooltip._content_layout.itemAt(0).widget() is tooltip._label


class TestFluentTooltipManager:
    @pytest.fixture(autouse=True)
    def reset_manager(self, monkeypatch):
        # Patch the global tooltip to control its behavior
        self.mock_global_tooltip = MagicMock(spec=FluentTooltip)
        monkeypatch.setattr(tooltip_manager, '_global_tooltip', self.mock_global_tooltip)
        tooltip_manager._active_tooltips.clear()
        yield

    def test_show_tooltip_uses_global(self, qtbot):
        widget = QWidget()
        qtbot.addWidget(widget)

        tooltip_manager.showTooltip("Hello", QPoint(100, 100), widget, rich_text=False)

        self.mock_global_tooltip.setText.assert_called_once_with("Hello", rich_text=False)
        self.mock_global_tooltip.showTooltip.assert_called_once_with(QPoint(100, 100), widget)
        assert widget in tooltip_manager._active_tooltips
        assert tooltip_manager._active_tooltips[widget] is self.mock_global_tooltip

    def test_hide_tooltip_for_widget(self, qtbot):
        widget = QWidget()
        qtbot.addWidget(widget)

        # Pretend a tooltip is active for this widget
        tooltip_manager._active_tooltips[widget] = self.mock_global_tooltip

        tooltip_manager.hideTooltip(widget)

        self.mock_global_tooltip.hideTooltip.assert_called_once()
        assert widget not in tooltip_manager._active_tooltips

    def test_create_tooltip(self):
        tooltip = tooltip_manager.createTooltip("New")
        assert isinstance(tooltip, FluentTooltip)
        assert tooltip.getText() == "New"


class TestTooltipMixin:
    @patch('components.basic.display.tooltip.tooltip_manager.showTooltip')
    def test_enter_event_shows_tooltip(self, mock_show, qtbot):
        widget = WidgetWithTooltip()
        qtbot.addWidget(widget)
        widget.setTooltipText("Mixin Test")

        # Simulate enter event
        widget.enterEvent(None)

        mock_show.assert_called_once_with(
            "Mixin Test", widget.cursor().pos(), widget, False
        )

    @patch('components.basic.display.tooltip.tooltip_manager.hideTooltip')
    def test_leave_event_hides_tooltip(self, mock_hide, qtbot):
        widget = WidgetWithTooltip()
        qtbot.addWidget(widget)
        widget.setTooltipText("Mixin Test")

        # Simulate leave event
        widget.leaveEvent(None)

        mock_hide.assert_called_once_with(widget)

    @patch('components.basic.display.tooltip.tooltip_manager.showTooltip')
    def test_mixin_calls_parent_enter_event(self, mock_show, qtbot):
        widget = WidgetWithTooltipAndEvents()
        qtbot.addWidget(widget)
        widget.setTooltipText("Test")

        assert not widget.enter_called
        widget.enterEvent(None)
        assert widget.enter_called
        mock_show.assert_called_once()