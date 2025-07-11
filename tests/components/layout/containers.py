import sys
import pytest
from unittest.mock import Mock

from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtTest import QTest

# Mock the theme_manager and base classes as they are not provided
# This allows testing the components in isolation.
sys.modules['core.theme'] = Mock()
class MockFluentContainerBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._padding = Mock(left=lambda: 12, top=lambda: 12, right=lambda: 12, bottom=lambda: 12)
        self._spacing = 12
        self._clickable = False
        self._layout_animations_enabled = False
        self._corner_radius = 8
    def _apply_container_styling(self): pass
    def _apply_custom_theme_tokens(self, tokens): pass
    def animate_layout_change(self, key, prop, start, end, callback=None):
        self.setProperty(prop, end)
        if callback:
            callback()

class MockFluentLayoutBase(QWidget):
     def __init__(self, parent=None):
        super().__init__(parent)
        self._corner_radius = 8
     def _apply_custom_theme_tokens(self, tokens): pass

# Replace the base classes in the module's namespace before importing
import fluent_layout_components_refactored as components
components.FluentContainerBase = MockFluentContainerBase
components.FluentLayoutBase = MockFluentLayoutBase
components.theme_manager = Mock()
components.theme_manager.get_color.return_value.name.return_value = "#000000"


# Fixture to manage the QApplication instance for the test session
@pytest.fixture(scope="session")
def qapp():
    """Creates a QApplication instance for the entire test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


class TestFluentCard:
    """Tests for the FluentCard component."""

    def test_initialization(self, qapp):
        """Test the initial state of the card."""
        card = components.FluentCard()
        assert card is not None
        assert card.header_label.text() == ""
        assert not card.header_label.isVisible()
        assert card.content_layout is not None

    def test_set_header_text(self, qapp):
        """Test setting the header text."""
        card = components.FluentCard()
        card.setHeaderText("My Card Header")
        assert card.header_label.text() == "My Card Header"
        assert card.header_label.isVisible()
        card.setHeaderText("")
        assert not card.header_label.isVisible()

    def test_add_widget_to_content(self, qapp):
        """Test adding a widget to the card's content area."""
        card = components.FluentCard()
        test_widget = QLabel("Content Widget")
        card.addWidget(test_widget)
        assert card.content_layout.itemAt(0).widget() is test_widget


class TestFluentExpander:
    """Tests for the FluentExpander component."""

    def test_initialization(self, qapp):
        """Test the initial state of the expander."""
        expander = components.FluentExpander(title="Details")
        assert expander.title_label.text() == "Details"
        assert not expander.isExpanded()
        assert expander.content_container.maximumHeight() == 0
        assert expander.expand_icon.text() == "▶"

    def test_expansion_and_collapse(self, qapp):
        """Test expanding and collapsing the content."""
        expander = components.FluentExpander()
        # Mock the signal
        mock_slot = Mock()
        expander.expanded.connect(mock_slot)

        # Expand
        expander.setExpanded(True)
        assert expander.isExpanded()
        assert expander.expand_icon.text() == "▼"
        mock_slot.assert_called_with(True)

        # Collapse
        expander.setExpanded(False)
        assert not expander.isExpanded()
        assert expander.expand_icon.text() == "▶"
        mock_slot.assert_called_with(False)

    def test_toggle_on_click(self, qapp):
        """Test that clicking the header toggles the expanded state."""
        expander = components.FluentExpander()
        assert not expander.isExpanded()
        QTest.mouseClick(expander.header, Qt.LeftButton)
        assert expander.isExpanded()
        QTest.mouseClick(expander.header, Qt.LeftButton)
        assert not expander.isExpanded()

    def test_add_widget_to_content(self, qapp):
        """Test adding a widget to the expander's content area."""
        expander = components.FluentExpander()
        test_widget = QLabel("Expander Content")
        expander.addWidget(test_widget)
        assert expander.content_layout.itemAt(0).widget() is test_widget


class TestFluentInfoBar:
    """Tests for the FluentInfoBar component."""

    @pytest.mark.parametrize("severity, icon", [
        (components.FluentInfoBar.Severity.INFO, "ℹ"),
        (components.FluentInfoBar.Severity.SUCCESS, "✓"),
        (components.FluentInfoBar.Severity.WARNING, "⚠"),
        (components.FluentInfoBar.Severity.ERROR, "✕"),
    ])
    def test_initialization_and_severity(self, qapp, severity, icon):
        """Test initialization with different severities."""
        info_bar = components.FluentInfoBar(
            title="Test Title",
            message="Test Message",
            severity=severity
        )
        assert info_bar.title_label.text() == "Test Title"
        assert info_bar.message_label.text() == "Test Message"
        assert info_bar.icon_label.text() == icon
        assert info_bar.close_btn.isVisible()

    def test_closable_property(self, qapp):
        """Test the closable property."""
        info_bar = components.FluentInfoBar("Title", closable=False)
        assert not hasattr(info_bar, 'close_btn')

    def test_signals(self, qapp):
        """Test the `closed` and `action_clicked` signals."""
        info_bar = components.FluentInfoBar("Title")
        closed_slot = Mock()
        action_slot = Mock()

        info_bar.closed.connect(closed_slot)
        info_bar.action_clicked.connect(action_slot)

        info_bar.addActionButton("retry", "Retry Now")
        action_button = info_bar.findChild(QPushButton)

        # Test action click
        QTest.mouseClick(action_button, Qt.LeftButton)
        action_slot.assert_called_with("retry")

        # Test close click
        QTest.mouseClick(info_bar.close_btn, Qt.LeftButton)
        closed_slot.assert_called_once()


class TestFluentPivot:
    """Tests for the FluentPivot component."""

    @pytest.fixture
    def pivot_setup(self, qapp):
        """Fixture for setting up a FluentPivot instance."""
        pivot = components.FluentPivot()
        pivot.addItem("Home", QLabel("Home Page"))
        pivot.addItem("Settings", QLabel("Settings Page"))
        pivot.addItem("About", QLabel("About Page"))
        return pivot

    def test_initialization_and_item_adding(self, pivot_setup):
        """Test adding items to the pivot."""
        pivot = pivot_setup
        assert len(pivot._items) == 3
        assert pivot.content_stack.count() == 3
        assert pivot.getCurrentIndex() == 0
        assert pivot.content_stack.currentIndex() == 0
        assert pivot._items[0]['button'].isChecked()
        assert not pivot._items[1]['button'].isChecked()

    def test_selection_change_on_click(self, pivot_setup):
        """Test changing selection by clicking pivot headers."""
        pivot = pivot_setup
        selection_slot = Mock()
        pivot.selection_changed.connect(selection_slot)

        # Click the 'Settings' button
        settings_button = pivot._items[1]['button']
        QTest.mouseClick(settings_button, Qt.LeftButton)

        assert pivot.getCurrentIndex() == 1
        assert pivot.content_stack.currentIndex() == 1
        assert not pivot._items[0]['button'].isChecked()
        assert pivot._items[1]['button'].isChecked()
        selection_slot.assert_called_with(1)

    def test_set_current_index(self, pivot_setup):
        """Test changing selection programmatically."""
        pivot = pivot_setup
        selection_slot = Mock()
        pivot.selection_changed.connect(selection_slot)

        pivot.setCurrentIndex(2)

        assert pivot.getCurrentIndex() == 2
        assert pivot.content_stack.currentIndex() == 2
        assert pivot._items[2]['button'].isChecked()
        selection_slot.assert_called_with(2)