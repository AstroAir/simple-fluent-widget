import pytest
from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout
from unittest.mock import patch

from components.basic.display.label import (
    FluentLabel,
    FluentIconLabel,
    FluentStatusLabel,
    FluentLinkLabel,
    FluentLabelGroup
)

# Fixture for QApplication instance
@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

class TestFluentLabel:
    def test_initialization(self, qtbot):
        label = FluentLabel("Hello")
        qtbot.addWidget(label)
        assert label.text() == "Hello"
        assert label._label_style == FluentLabel.LabelStyle.BODY
        assert label._label_type == FluentLabel.LabelType.PRIMARY
        assert not label._is_clickable

    def test_set_style_and_type(self, qtbot):
        label = FluentLabel("Test")
        qtbot.addWidget(label)

        label.set_style(FluentLabel.LabelStyle.TITLE)
        assert label._label_style == FluentLabel.LabelStyle.TITLE
        # Check font size as a proxy for style change
        assert label.font().pointSize() == 20

        label.set_type(FluentLabel.LabelType.ACCENT)
        assert label._label_type == FluentLabel.LabelType.ACCENT
        # Cannot easily check stylesheet color, but we can check the internal method
        color = label._get_theme_color()
        assert color.name() in ["#0078d4", "#4cc2ff", "#005a9e"] # light/dark/contrast theme primary

    def test_clickable(self, qtbot):
        label = FluentLabel("Clickable")
        qtbot.addWidget(label)

        label.set_clickable(True)
        assert label._is_clickable
        assert label.cursor().shape() == Qt.CursorShape.PointingHandCursor

        with qtbot.waitSignal(label.clicked, timeout=500):
            qtbot.mouseClick(label, Qt.MouseButton.LeftButton)

        label.set_clickable(False)
        assert not label._is_clickable
        assert label.cursor().shape() == Qt.CursorShape.ArrowCursor

    def test_hover_events(self, qtbot):
        label = FluentLabel("Hover")
        label.set_clickable(True)
        qtbot.addWidget(label)
        label.show()

        with qtbot.waitSignal(label.hover_changed, timeout=500, check_params_cb=lambda h: h is True):
            qtbot.mouseMove(label, label.rect().center()) # enterEvent

        qtbot.wait(100) # allow animations to start

        with qtbot.waitSignal(label.hover_changed, timeout=500, check_params_cb=lambda h: h is False):
            # Move mouse out of the widget to a safe, non-None parent widget's center
            if label.parentWidget():
                parent = label.parentWidget()
                rect = parent.rect() if parent is not None else None
                if rect is not None:
                    qtbot.mouseMove(parent, rect.center())

    def test_animations(self, qtbot):
        label = FluentLabel("Animate")
        label.set_animations_enabled(True)
        qtbot.addWidget(label)
        label.show()

        # Fade In
        label.fade_in(100)
        qtbot.waitUntil(lambda: label._opacity_effect is not None and label._opacity_effect.opacity() > 0.9, timeout=200)
        assert label._opacity_effect is not None and label._opacity_effect.opacity() > 0.9

        # Fade Out
        label.fade_out(100)
        qtbot.waitUntil(lambda: label._opacity_effect is not None and label._opacity_effect.opacity() < 0.1, timeout=200)
        assert label._opacity_effect is not None and label._opacity_effect.opacity() < 0.1

class TestFluentIconLabel:
    def test_initialization(self, qtbot):
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.red)
        icon = QIcon(pixmap)
        widget = FluentIconLabel("Icon Label", icon=icon)
        qtbot.addWidget(widget)

        assert widget.text() == "Icon Label"
        assert widget.icon_label is not None
        assert isinstance(widget.layout(), QHBoxLayout)

    def test_vertical_layout(self, qtbot):
        widget = FluentIconLabel("Vertical", layout_direction="vertical")
        qtbot.addWidget(widget)
        assert isinstance(widget.layout(), QVBoxLayout)

    def test_set_text_and_style(self, qtbot):
        widget = FluentIconLabel("Initial")
        qtbot.addWidget(widget)

        widget.set_text("Updated")
        assert widget.text() == "Updated"

        widget.set_text_style(FluentLabel.LabelStyle.CAPTION)
        assert widget.text_label._label_style == FluentLabel.LabelStyle.CAPTION

        widget.set_text_type(FluentLabel.LabelType.DISABLED)
        assert widget.text_label._label_type == FluentLabel.LabelType.DISABLED

class TestFluentStatusLabel:
    def test_initialization(self, qtbot):
        widget = FluentStatusLabel("Info Status")
        qtbot.addWidget(widget)
        assert widget.text() == "Info Status"
        assert widget._status == FluentStatusLabel.StatusType.INFO
        assert widget.indicator is not None

    def test_set_status(self, qtbot):
        widget = FluentStatusLabel("Status")
        qtbot.addWidget(widget)

        widget.set_status(FluentStatusLabel.StatusType.SUCCESS)
        assert widget._status == FluentStatusLabel.StatusType.SUCCESS
        assert widget.text_label._label_type == FluentLabel.LabelType.SUCCESS

        widget.set_status(FluentStatusLabel.StatusType.ERROR)
        assert widget._status == FluentStatusLabel.StatusType.ERROR
        assert widget.text_label._label_type == FluentLabel.LabelType.ERROR

    def test_processing_animation(self, qtbot):
        widget = FluentStatusLabel("Processing", status=FluentStatusLabel.StatusType.PROCESSING)
        qtbot.addWidget(widget)
        widget.show()

        qtbot.waitUntil(lambda: widget._pulse_animation is not None and widget._pulse_animation.state() == QPropertyAnimation.State.Running, timeout=500)
        assert widget._pulse_animation is not None and widget._pulse_animation.state() == QPropertyAnimation.State.Running

        widget.set_status(FluentStatusLabel.StatusType.INFO)
        qtbot.waitUntil(lambda: widget._pulse_animation is not None and widget._pulse_animation.state() == QPropertyAnimation.State.Stopped, timeout=500)
        assert widget._pulse_animation is not None and widget._pulse_animation.state() == QPropertyAnimation.State.Stopped

class TestFluentLinkLabel:
    @patch('webbrowser.open')
    def test_link_clicked(self, mock_open, qtbot):
        url = "https://example.com"
        widget = FluentLinkLabel("Link", url=url)
        qtbot.addWidget(widget)

        with qtbot.waitSignal(widget.clicked, timeout=500):
            qtbot.mouseClick(widget, Qt.MouseButton.LeftButton)

        mock_open.assert_called_once_with(url)

    def test_initialization(self, qtbot):
        widget = FluentLinkLabel("Link", url="test.com")
        qtbot.addWidget(widget)
        assert widget.text() == "Link"
        assert widget.get_url() == "test.com"
        assert widget._label_type == FluentLabel.LabelType.ACCENT
        assert "underline" in widget.styleSheet()

class TestFluentLabelGroup:
    def test_initialization(self, qtbot):
        group = FluentLabelGroup()
        qtbot.addWidget(group)
        assert isinstance(group.layout(), QHBoxLayout)
        assert len(group.get_labels()) == 0

    def test_add_and_remove_label(self, qtbot):
        group = FluentLabelGroup()
        qtbot.addWidget(group)

        # Add by string
        label1 = group.add_label("Label 1", animate=False)
        assert len(group.get_labels()) == 1
        assert isinstance(label1, FluentLabel)
        assert label1.text() == "Label 1"

        # Add by widget
        label2 = FluentLabel("Label 2")
        group.add_label(label2, animate=False)
        assert len(group.get_labels()) == 2

        # Remove by index
        group.remove_label(0, animate=False)
        assert len(group.get_labels()) == 1
        assert group.get_labels()[0] is label2

        # Remove by reference
        group.remove_label(label2, animate=False)
        assert len(group.get_labels()) == 0

    def test_clear_labels(self, qtbot):
        group = FluentLabelGroup()
        qtbot.addWidget(group)
        group.add_label("One", animate=False)
        group.add_label("Two", animate=False)
        assert len(group.get_labels()) == 2

        group.clear_labels(animate=False)
        assert len(group.get_labels()) == 0