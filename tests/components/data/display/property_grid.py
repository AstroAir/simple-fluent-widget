import pytest
from pytestqt.qt_compat import qt_api
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QLabel
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtTest import QTest
from unittest.mock import MagicMock
# Change relative import to absolute import
from components.data.display.property_grid import FluentPropertyGrid, FluentPropertyItem, PropertyType, PropertyConstraints, PropertyValue, PropertyValidationProtocol
# Import Any for type hinting
from typing import Any

# Fixture for QApplication (provided by pytest-qt)
# @pytest.fixture(scope="session")
# def qapp():
#     yield qt_api.QtWidgets.QApplication([])

# Fixture for FluentPropertyGrid


@pytest.fixture
def prop_grid(qapp, mocker):
    """Provides a FluentPropertyGrid instance for each test."""
    # Mock theme_manager and animations to prevent errors if optional dependencies are missing
    mocker.patch(
        'components.data.display.property_grid.theme_manager', MagicMock())
    mocker.patch(
        'components.data.display.property_grid.FluentRevealEffect', MagicMock())
    mocker.patch(
        'components.data.display.property_grid.FluentMicroInteraction', MagicMock())

    grid = FluentPropertyGrid()
    # Disable animations for predictable tests
    grid.animations_enabled = False
    yield grid
    # Clean up the grid
    grid.close()


class TestFluentPropertyGrid:
    """Unit tests for the FluentPropertyGrid class."""

    def test_init(self, prop_grid):
        """Test initial state of the property grid."""
        assert prop_grid.tree is not None
        assert isinstance(prop_grid.tree, qt_api.QtWidgets.QTreeWidget)
        assert not prop_grid.properties
        assert not prop_grid.editors
        assert not prop_grid.categories
        assert not prop_grid._property_history
        assert prop_grid._history_index == -1
        assert prop_grid.animations_enabled is False  # Disabled by fixture

    def test_setup_ui_called(self, mocker):
        """Test that setup_ui is called during initialization."""
        mock_setup_ui = mocker.patch.object(FluentPropertyGrid, 'setup_ui')
        grid = FluentPropertyGrid()
        mock_setup_ui.assert_called_once()
        grid.close()

    def test_setup_shortcuts_called(self, mocker):
        """Test that setup_shortcuts is called during initialization."""
        mock_setup_shortcuts = mocker.patch.object(
            FluentPropertyGrid, 'setup_shortcuts')
        grid = FluentPropertyGrid()
        mock_setup_shortcuts.assert_called_once()
        grid.close()

    def test_apply_theme_called(self, mocker):
        """Test that apply_theme is called during initialization."""
        mock_apply_theme = mocker.patch.object(
            FluentPropertyGrid, 'apply_theme')
        grid = FluentPropertyGrid()
        mock_apply_theme.assert_called_once()
        grid.close()

    def test_setup_theme_connections_called(self, mocker):
        """Test that setup_theme_connections is called during initialization."""
        mock_setup_theme_connections = mocker.patch.object(
            FluentPropertyGrid, 'setup_theme_connections')
        grid = FluentPropertyGrid()
        mock_setup_theme_connections.assert_called_once()
        grid.close()

    def test_add_property_string(self, prop_grid):
        """Test adding a string property."""
        prop = FluentPropertyItem("Name", "Test", PropertyType.STRING)
        prop_grid.add_property(prop)

        assert "Name" in prop_grid.properties
        assert prop_grid.properties["Name"] == prop
        assert prop_grid.tree.topLevelItemCount() == 1  # Should create a category
        category_item = prop_grid.tree.topLevelItem(0)
        assert category_item.text(0) == "General"
        assert category_item.childCount() == 1  # Should add the property item
        prop_item = category_item.child(0)
        assert prop_item.text(0) == "Name"
        editor = prop_grid.tree.itemWidget(prop_item, 1)
        assert isinstance(editor, QLineEdit)
        assert editor.text() == "Test"
        assert "Name" in prop_grid.editors
        assert prop_grid.editors["Name"] == editor

    def test_add_property_integer(self, prop_grid):
        """Test adding an integer property."""
        prop = FluentPropertyItem("Age", 30, PropertyType.INTEGER)
        prop_grid.add_property(prop)
        prop_item = prop_grid.tree.topLevelItem(0).child(0)
        editor = prop_grid.tree.itemWidget(prop_item, 1)
        assert isinstance(editor, QSpinBox)
        assert editor.value() == 30

    def test_add_property_float(self, prop_grid):
        """Test adding a float property."""
        prop = FluentPropertyItem("Height", 1.75, PropertyType.FLOAT)
        prop_grid.add_property(prop)
        prop_item = prop_grid.tree.topLevelItem(0).child(0)
        editor = prop_grid.tree.itemWidget(prop_item, 1)
        assert isinstance(editor, QDoubleSpinBox)
        assert editor.value() == 1.75

    def test_add_property_boolean(self, prop_grid):
        """Test adding a boolean property."""
        prop = FluentPropertyItem("Active", True, PropertyType.BOOLEAN)
        prop_grid.add_property(prop)
        prop_item = prop_grid.tree.topLevelItem(0).child(0)
        editor = prop_grid.tree.itemWidget(prop_item, 1)
        assert isinstance(editor, QCheckBox)
        assert editor.isChecked() is True

    def test_add_property_choice(self, prop_grid):
        """Test adding a choice property."""
        prop = FluentPropertyItem("Color", "Red", PropertyType.CHOICE, choices=[
                                  "Red", "Green", "Blue"])
        prop_grid.add_property(prop)
        prop_item = prop_grid.tree.topLevelItem(0).child(0)
        editor = prop_grid.tree.itemWidget(prop_item, 1)
        assert isinstance(editor, QComboBox)
        assert editor.currentText() == "Red"
        assert editor.count() == 3

    def test_add_property_readonly(self, prop_grid):
        """Test adding a readonly property."""
        prop = FluentPropertyItem(
            "ID", "XYZ", PropertyType.STRING, readonly=True)
        prop_grid.add_property(prop)
        prop_item = prop_grid.tree.topLevelItem(0).child(0)
        editor = prop_grid.tree.itemWidget(prop_item, 1)
        assert isinstance(editor, QLabel)
        assert editor.text() == "XYZ"

    def test_add_property_with_category(self, prop_grid):
        """Test adding properties to different categories."""
        prop1 = FluentPropertyItem(
            "Name", "Test", PropertyType.STRING, category="Personal")
        prop2 = FluentPropertyItem(
            "Age", 30, PropertyType.INTEGER, category="Personal")
        prop3 = FluentPropertyItem(
            "City", "London", PropertyType.STRING, category="Location")

        prop_grid.add_property(prop1)
        prop_grid.add_property(prop3)
        prop_grid.add_property(prop2)  # Add out of category order

        assert prop_grid.tree.topLevelItemCount() == 2
        categories = [prop_grid.tree.topLevelItem(i).text(
            0) for i in range(prop_grid.tree.topLevelItemCount())]
        assert "Personal" in categories
        assert "Location" in categories

        personal_item = prop_grid.categories["Personal"]
        location_item = prop_grid.categories["Location"]

        assert personal_item.childCount() == 2
        assert location_item.childCount() == 1

        personal_children_names = [personal_item.child(i).text(
            0) for i in range(personal_item.childCount())]
        assert "Name" in personal_children_names
        assert "Age" in personal_children_names

        location_children_names = [location_item.child(i).text(
            0) for i in range(location_item.childCount())]
        assert "City" in location_children_names

    def test_add_property_required_marker(self, prop_grid):
        """Test that required properties get a '*' marker."""
        prop_required = FluentPropertyItem(
            "Name", "Test", PropertyType.STRING, constraints=PropertyConstraints(required=True))
        prop_not_required = FluentPropertyItem("Age", 30, PropertyType.INTEGER)

        prop_grid.add_property(prop_required)
        prop_grid.add_property(prop_not_required)

        name_item = prop_grid.tree.topLevelItem(0).child(0)
        age_item = prop_grid.tree.topLevelItem(0).child(1)

        assert name_item.text(0) == "Name *"
        assert age_item.text(0) == "Age"

    def test_get_property_value(self, prop_grid):
        """Test retrieving property values."""
        prop_grid.add_property(FluentPropertyItem(
            "Name", "Test", PropertyType.STRING))
        prop_grid.add_property(FluentPropertyItem(
            "Age", 30, PropertyType.INTEGER))
        assert prop_grid.get_property_value("Name") == "Test"
        assert prop_grid.get_property_value("Age") == 30
        assert prop_grid.get_property_value("NonExistent") is None

    def test_set_property_value_valid(self, prop_grid):
        """Test setting valid property values."""
        prop_grid.add_property(FluentPropertyItem(
            "Name", "Test", PropertyType.STRING))
        prop_grid.add_property(FluentPropertyItem(
            "Age", 30, PropertyType.INTEGER, constraints=PropertyConstraints(min_value=0)))
        assert prop_grid.set_property_value("Name", "New Name") is True
        assert prop_grid.get_property_value("Name") == "New Name"
        assert prop_grid.set_property_value("Age", 40) is True
        assert prop_grid.get_property_value("Age") == 40

    def test_set_property_value_invalid(self, prop_grid, qtbot):
        """Test setting invalid property values."""
        prop_grid.add_property(FluentPropertyItem(
            "Age", 30, PropertyType.INTEGER, constraints=PropertyConstraints(min_value=10, max_value=50)))
        prop_grid.add_property(FluentPropertyItem(
            "Name", "Test", PropertyType.STRING, constraints=PropertyConstraints(required=True)))

        # Test invalid age
        with qtbot.wait_for_signal(prop_grid.property_validation_failed) as blocker:
            assert prop_grid.set_property_value("Age", 5) is False
        assert blocker.args == ("Age", 5, "Invalid value")
        assert prop_grid.get_property_value(
            "Age") == 30  # Value should not change

        # Test invalid required string
        with qtbot.wait_for_signal(prop_grid.property_validation_failed) as blocker:
            assert prop_grid.set_property_value("Name", "") is False
        assert blocker.args == ("Name", "", "Invalid value")
        assert prop_grid.get_property_value(
            "Name") == "Test"  # Value should not change

    def test_editor_change_updates_property_and_emits_signal(self, prop_grid, qtbot):
        """Test that changing an editor updates the property and emits property_changed."""
        prop_grid.add_property(FluentPropertyItem(
            "Name", "Test", PropertyType.STRING))
        prop_grid.add_property(FluentPropertyItem(
            "Age", 30, PropertyType.INTEGER))
        prop_grid.add_property(FluentPropertyItem(
            "Height", 1.75, PropertyType.FLOAT))
        prop_grid.add_property(FluentPropertyItem(
            "Active", True, PropertyType.BOOLEAN))
        prop_grid.add_property(FluentPropertyItem(
            "Color", "Red", PropertyType.CHOICE, choices=["Red", "Green", "Blue"]))

        # Find editors (assuming order based on addition)
        name_editor = prop_grid.editors["Name"]
        age_editor = prop_grid.editors["Age"]
        height_editor = prop_grid.editors["Height"]
        active_editor = prop_grid.editors["Active"]
        color_editor = prop_grid.editors["Color"]

        # Test String editor
        assert isinstance(name_editor, QLineEdit)
        with qtbot.wait_for_signal(prop_grid.property_changed) as blocker:
            name_editor.setText("New Name")
        assert blocker.args == ("Name", "New Name")
        assert prop_grid.get_property_value("Name") == "New Name"

        # Test Integer editor
        assert isinstance(age_editor, QSpinBox)
        with qtbot.wait_for_signal(prop_grid.property_changed) as blocker:
            age_editor.setValue(45)
        assert blocker.args == ("Age", 45)
        assert prop_grid.get_property_value("Age") == 45

        # Test Float editor
        assert isinstance(height_editor, QDoubleSpinBox)
        with qtbot.wait_for_signal(prop_grid.property_changed) as blocker:
            height_editor.setValue(1.80)
        assert blocker.args == ("Height", 1.80)
        assert prop_grid.get_property_value("Height") == 1.80

        # Test Boolean editor
        assert isinstance(active_editor, QCheckBox)
        with qtbot.wait_for_signal(prop_grid.property_changed) as blocker:
            active_editor.setChecked(False)
        assert blocker.args == ("Active", False)
        assert prop_grid.get_property_value("Active") is False

        # Test Choice editor
        assert isinstance(color_editor, QComboBox)
        with qtbot.wait_for_signal(prop_grid.property_changed) as blocker:
            color_editor.setCurrentText("Green")
        assert blocker.args == ("Color", "Green")
        assert prop_grid.get_property_value("Color") == "Green"

    def test_editor_change_invalid_emits_validation_failed(self, prop_grid, qtbot):
        """Test that changing an editor to an invalid value emits property_validation_failed."""
        prop_grid.add_property(FluentPropertyItem(
            "Age", 30, PropertyType.INTEGER, constraints=PropertyConstraints(min_value=10, max_value=50)))

        age_editor = prop_grid.editors["Age"]
        assert isinstance(age_editor, QSpinBox)

        with qtbot.wait_for_signal(prop_grid.property_validation_failed) as blocker:
            age_editor.setValue(5)  # Invalid value
        assert blocker.args == ("Age", 5, "Invalid value")
        # Value should not have changed internally
        assert prop_grid.get_property_value("Age") == 30

    def test_is_valid_required_string(self):
        """Test is_valid for required string constraint."""
        prop_required = FluentPropertyItem(
            "Name", "", PropertyType.STRING, constraints=PropertyConstraints(required=True))
        prop_not_required = FluentPropertyItem("Desc", "", PropertyType.STRING)
        assert prop_required.is_valid("abc") is True
        assert prop_required.is_valid("") is False
        assert prop_required.is_valid("   ") is False  # Stripped whitespace
        assert prop_not_required.is_valid("") is True

    def test_is_valid_integer_range(self):
        """Test is_valid for integer range constraint."""
        prop = FluentPropertyItem("Age", 30, PropertyType.INTEGER,
                                  constraints=PropertyConstraints(min_value=10, max_value=50))
        assert prop.is_valid(20) is True
        assert prop.is_valid(10) is True
        assert prop.is_valid(50) is True
        assert prop.is_valid(5) is False
        assert prop.is_valid(60) is False
        assert prop.is_valid("abc") is False  # Non-numeric

    def test_is_valid_float_range(self):
        """Test is_valid for float range constraint."""
        prop = FluentPropertyItem("Temp", 25.5, PropertyType.FLOAT,
                                  constraints=PropertyConstraints(min_value=0.0, max_value=100.0))
        assert prop.is_valid(50.0) is True
        assert prop.is_valid(0.0) is True
        assert prop.is_valid(100.0) is True
        assert prop.is_valid(-1.0) is False
        assert prop.is_valid(101.0) is False
        assert prop.is_valid("abc") is False  # Non-numeric

    def test_is_valid_choice(self):
        """Test is_valid for choice constraint."""
        prop = FluentPropertyItem("Color", "Red", PropertyType.CHOICE,
                                  constraints=PropertyConstraints(choices=("Red", "Green", "Blue")))
        assert prop.is_valid("Red") is True
        assert prop.is_valid("Green") is True
        assert prop.is_valid("Yellow") is False  # Not in choices

    def test_is_valid_custom_validator(self):
        """Test is_valid with a custom validator function."""
        def is_even(value: Any) -> bool:
            try:
                return int(value) % 2 == 0
            except (ValueError, TypeError):
                return False

        prop = FluentPropertyItem("Number", 2, PropertyType.INTEGER)
        prop.set_validator(is_even)
        assert prop.is_valid(4) is True
        assert prop.is_valid(3) is False
        assert prop.is_valid("abc") is False

    def test_undo_redo_single_change(self, prop_grid, qtbot):
        """Test undoing and redoing a single property change."""
        prop_grid.add_property(FluentPropertyItem(
            "Name", "Initial", PropertyType.STRING))

        # Initial state saved
        assert len(prop_grid._property_history) == 1
        assert prop_grid._history_index == 0

        # Change Name
        name_editor = prop_grid.editors["Name"]
        with qtbot.wait_for_signal(prop_grid.property_changed):
            name_editor.setText("Change 1")
        assert prop_grid.get_property_value("Name") == "Change 1"
        assert len(prop_grid._property_history) == 2
        assert prop_grid._history_index == 1

        # Undo
        prop_grid.undo_last_change()
        qtbot.wait(10)  # Allow editor update to process
        assert prop_grid.get_property_value("Name") == "Initial"
        assert prop_grid._history_index == 0
        assert name_editor.text() == "Initial"

        # Redo
        prop_grid.redo_last_change()
        qtbot.wait(10)  # Allow editor update to process
        assert prop_grid.get_property_value("Name") == "Change 1"
        assert prop_grid._history_index == 1
        assert name_editor.text() == "Change 1"

    def test_undo_redo_multiple_changes(self, prop_grid, qtbot):
        """Test undoing and redoing multiple property changes."""
        prop_grid.add_property(FluentPropertyItem(
            "Name", "Initial", PropertyType.STRING))

        name_editor = prop_grid.editors["Name"]

        # Change 1
        with qtbot.wait_for_signal(prop_grid.property_changed):
            name_editor.setText("Change 1")
        # Change 2
        with qtbot.wait_for_signal(prop_grid.property_changed):
            name_editor.setText("Change 2")
        # Change 3
        with qtbot.wait_for_signal(prop_grid.property_changed):
            name_editor.setText("Change 3")

        assert prop_grid.get_property_value("Name") == "Change 3"
        assert len(prop_grid._property_history) == 4  # Initial + 3 changes
        assert prop_grid._history_index == 3

        # Undo 1
        prop_grid.undo_last_change()
        qtbot.wait(10)
        assert prop_grid.get_property_value("Name") == "Change 2"
        assert prop_grid._history_index == 2

        # Undo 2
        prop_grid.undo_last_change()
        qtbot.wait(10)
        assert prop_grid.get_property_value("Name") == "Change 1"
        assert prop_grid._history_index == 1

        # Undo 3 (back to initial)
        prop_grid.undo_last_change()
        qtbot.wait(10)
        assert prop_grid.get_property_value("Name") == "Initial"
        assert prop_grid._history_index == 0

        # Undo past beginning (should do nothing)
        prop_grid.undo_last_change()
        qtbot.wait(10)
        assert prop_grid.get_property_value("Name") == "Initial"
        assert prop_grid._history_index == 0

        # Redo 1
        prop_grid.redo_last_change()
        qtbot.wait(10)
        assert prop_grid.get_property_value("Name") == "Change 1"
        assert prop_grid._history_index == 1

        # Redo 2
        prop_grid.redo_last_change()
        qtbot.wait(10)
        assert prop_grid.get_property_value("Name") == "Change 2"
        assert prop_grid._history_index == 2

        # Redo 3
        prop_grid.redo_last_change()
        qtbot.wait(10)
        assert prop_grid.get_property_value("Name") == "Change 3"
        assert prop_grid._history_index == 3

        # Redo past end (should do nothing)
        prop_grid.redo_last_change()
        qtbot.wait(10)
        assert prop_grid.get_property_value("Name") == "Change 3"
        assert prop_grid._history_index == 3

    def test_undo_redo_new_change_after_undo(self, prop_grid, qtbot):
        """Test making a new change after undoing history."""
        prop_grid.add_property(FluentPropertyItem(
            "Name", "Initial", PropertyType.STRING))

        name_editor = prop_grid.editors["Name"]

        # Change 1
        with qtbot.wait_for_signal(prop_grid.property_changed):
            name_editor.setText("Change 1")
        # Change 2
        with qtbot.wait_for_signal(prop_grid.property_changed):
            name_editor.setText("Change 2")

        assert len(prop_grid._property_history) == 3  # Initial, C1, C2
        assert prop_grid._history_index == 2

        # Undo 1 (back to Change 1)
        prop_grid.undo_last_change()
        qtbot.wait(10)
        assert prop_grid.get_property_value("Name") == "Change 1"
        assert prop_grid._history_index == 1

        # Make a new change (Change 3)
        with qtbot.wait_for_signal(prop_grid.property_changed):
            name_editor.setText("Change 3")

        assert prop_grid.get_property_value("Name") == "Change 3"
        # Initial, C1, C3 (C2 is gone)
        assert len(prop_grid._property_history) == 3
        assert prop_grid._history_index == 2  # Points to C3

        # Redo should do nothing now
        prop_grid.redo_last_change()
        qtbot.wait(10)
        assert prop_grid.get_property_value("Name") == "Change 3"
        assert prop_grid._history_index == 2

        # Undo should go back to Change 1
        prop_grid.undo_last_change()
        qtbot.wait(10)
        assert prop_grid.get_property_value("Name") == "Change 1"
        assert prop_grid._history_index == 1
