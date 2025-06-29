import pytest
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from PySide6.QtTest import QTest

from components.basic.display.card import FluentCard, ExpandableFluentCard, FluentCardMetrics

# Fixture for QApplication instance


@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestFluentCard:
    def test_initialization(self, qtbot):
        card = FluentCard()
        qtbot.addWidget(card)
        assert not card.isClickable()
        assert card.getElevation() == FluentCardMetrics.ELEVATION_MEDIUM
        assert card.getCornerRadius() == FluentCardMetrics.RADIUS_MEDIUM
        assert card.graphicsEffect() is not None

    def test_set_clickable(self, qtbot):
        card = FluentCard()
        qtbot.addWidget(card)

        card.setClickable(True)
        assert card.isClickable()
        assert card.cursor().shape() == Qt.CursorShape.PointingHandCursor
        assert card.property("clickable") is True

        card.setClickable(False)
        assert not card.isClickable()
        assert card.cursor().shape() == Qt.CursorShape.ArrowCursor
        assert card.property("clickable") is False

    def test_set_elevation(self, qtbot):
        card = FluentCard()
        qtbot.addWidget(card)

        card.setElevation(FluentCardMetrics.ELEVATION_HIGH)
        qtbot.waitUntil(lambda: card.getElevation() ==
                        FluentCardMetrics.ELEVATION_HIGH, timeout=500)
        assert card.getElevation() == FluentCardMetrics.ELEVATION_HIGH
        # Test shadow update implicitly
        assert card._shadow.blurRadius() > 1

    def test_set_corner_radius(self, qtbot):
        card = FluentCard()
        qtbot.addWidget(card)

        card.setCornerRadius(FluentCardMetrics.RADIUS_LARGE)
        assert card.getCornerRadius() == FluentCardMetrics.RADIUS_LARGE
        # Check if stylesheet was updated
        assert f"border-radius: {FluentCardMetrics.RADIUS_LARGE}px;" in card.styleSheet()

    def test_hover_and_press_animations(self, qtbot):
        card = FluentCard()
        card.setClickable(True)
        qtbot.addWidget(card)
        card.show()

        # Hover Enter
        qtbot.mouseMove(card, card.rect().center())
        qtbot.waitUntil(lambda: card._hover_progress > 0.9, timeout=500)
        assert card._hover_progress > 0.9

        # Press
        qtbot.mousePress(card, Qt.MouseButton.LeftButton,
                         pos=card.rect().center())
        qtbot.waitUntil(lambda: card._press_progress > 0.9, timeout=500)
        assert card._press_progress > 0.9

        # Release
        qtbot.mouseRelease(card, Qt.MouseButton.LeftButton,
                           pos=card.rect().center())
        qtbot.waitUntil(lambda: card._press_progress < 0.1, timeout=500)
        assert card._press_progress < 0.1

    def test_add_remove_widget(self, qtbot):
        card = FluentCard()
        qtbot.addWidget(card)

        label = QLabel("Test")
        card.addWidget(label)
        assert card._layout.count() == 2  # 1 for widget, 1 for stretch
        assert card._layout.itemAt(0).widget() is label

        card.removeWidget(label)
        qtbot.waitUntil(lambda: card._layout.count() == 1,
                        timeout=500)  # Only stretch left
        assert label.parent() is None

    def test_responsive_layout(self, qtbot):
        card = FluentCard()
        card.setResponsiveMode(True)
        qtbot.addWidget(card)
        card.show()

        # Small size
        card.resize(QSize(300, 200))
        qtbot.wait(50)  # Allow resize event to process
        assert card._current_breakpoint == FluentCardMetrics.BREAKPOINT_SMALL
        margins = card._layout.contentsMargins()
        assert margins.left() == FluentCardMetrics.MARGIN_SMALL

        # Large size
        card.resize(QSize(1200, 200))
        qtbot.wait(50)
        assert card._current_breakpoint == FluentCardMetrics.BREAKPOINT_LARGE
        margins = card._layout.contentsMargins()
        assert margins.left() == FluentCardMetrics.MARGIN_LARGE

        # Medium size
        card.resize(QSize(800, 200))
        qtbot.wait(50)
        assert card._current_breakpoint == FluentCardMetrics.BREAKPOINT_MEDIUM
        margins = card._layout.contentsMargins()
        assert margins.left() == FluentCardMetrics.MARGIN_MEDIUM


class TestExpandableFluentCard:
    def test_initialization(self, qtbot):
        card = ExpandableFluentCard()
        qtbot.addWidget(card)
        assert not card.isExpanded()
        assert card._header_widget is not None
        assert card._content_container is not None
        assert card._content_container is not None and not card._content_container.isVisible()

    def test_set_header_and_content(self, qtbot):
        card = ExpandableFluentCard()
        qtbot.addWidget(card)

        header_label = QLabel("Header")
        content_label = QLabel("Content")

        card.setHeader(header_label)
        card.setContent(content_label)

        assert card._header_layout.itemAt(0).widget() is header_label
        assert card._content_layout.itemAt(0).widget() is content_label

    def test_expand_collapse(self, qtbot):
        card = ExpandableFluentCard()
        content = QWidget()
        content.setFixedSize(200, 100)
        card.setContent(content)
        qtbot.addWidget(card)
        card.show()

        # Expand
        with qtbot.waitSignal(card.expanded, timeout=1000):
            card.expand()

        assert card.isExpanded()
        qtbot.waitUntil(
            lambda: card._content_container is not None and card._content_container.isVisible(), timeout=500)
        qtbot.waitUntil(lambda: card._content_container is not None and card._content_container.height()
                        > 90, timeout=500)

        # Collapse
        with qtbot.waitSignal(card.collapsed, timeout=1000):
            card.collapse()

        assert not card.isExpanded()
        qtbot.waitUntil(
            lambda: card._content_container is not None and not card._content_container.isVisible(), timeout=500)
        assert card._content_container is not None and card._content_container.height() == 0

    def test_toggle_by_clicking_header(self, qtbot):
        card = ExpandableFluentCard()
        header = QLabel("Header")  # A non-clickable widget
        content = QWidget()
        content.setFixedSize(200, 100)

        card.setHeader(header)
        card.setContent(content)
        qtbot.addWidget(card)
        card.show()

        # Click header to expand
        with qtbot.waitSignal(card.expanded, timeout=1000):
            if card._header_widget is not None and card._header_widget.children():
                qtbot.mouseClick(card._header_widget.children()[
                                 0], Qt.MouseButton.LeftButton)

        assert card.isExpanded()
        qtbot.waitUntil(lambda: card._content_container is not None and card._content_container.height()
                        > 90, timeout=500)

        # Click header to collapse
        with qtbot.waitSignal(card.collapsed, timeout=1000):
            if card._header_widget is not None and card._header_widget.children():
                qtbot.mouseClick(card._header_widget.children()[
                                 0], Qt.MouseButton.LeftButton)

        assert not card.isExpanded()
        qtbot.waitUntil(lambda: card._content_container is not None and card._content_container.height()
                        == 0, timeout=500)
