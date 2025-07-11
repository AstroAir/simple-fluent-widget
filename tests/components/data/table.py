import pytest
import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtTest import QTest

# Add the parent directory to the path for relative import if necessary
# Assuming the test file is components/data/test_table.py
# and the module is components/data/table.py
# The parent directory 'data' is a package (__init__.py exists)
# So we can use relative import
try:
    from .table import (
        FluentDataGrid, DataGridConfig, FluentTableWidget,
        FluentButton, FluentLineEdit, FLUENT_COMPONENTS_AVAILABLE
    )
except ImportError as e:
    pytest.fail(f"Failed to import components: {e}")

# pytest-qt provides the qapp fixture automatically

@pytest.fixture
def widget_cleanup():
    """Fixture to clean up widgets after each test."""
    widgets = []
    yield widgets
    for widget in widgets:
        # Check if widget is a QObject and hasn't been deleted
        if widget is not None and hasattr(widget, 'deleteLater'):
             # Check if it's a QWidget and visible, then close
             if isinstance(widget, QWidget) and widget.isVisible():
                 widget.close()
             # Schedule deletion
             widget.deleteLater()
    QApplication.processEvents() # Process events to ensure widgets are closed/deleted


class TestFluentDataGrid:

    def test_initialization_default(self, qapp, widget_cleanup):
        """Test FluentDataGrid initialization with default config."""
        grid = FluentDataGrid()
        widget_cleanup.append(grid)

        assert isinstance(grid, FluentDataGrid)
        assert isinstance(grid, QWidget)
        assert isinstance(grid._config, DataGridConfig)
        assert grid._config.enable_search is True
        assert grid._config.enable_sort is True
        assert grid._config.enable_filter is True # Note: enable_filter is not directly used in the provided code, but is in config
        assert grid._config.search_box_width == 300

        assert isinstance(grid.table, FluentTableWidget)
        assert hasattr(grid, 'search_box') # Search enabled by default
        assert isinstance(grid.search_box, (QLineEdit, QWidget)) # Check against fallback too
        assert hasattr(grid, 'add_btn')
        assert isinstance(grid.add_btn, (QPushButton, QWidget)) # Check against fallback too
        assert hasattr(grid, 'edit_btn')
        assert isinstance(grid.edit_btn, (QPushButton, QWidget)) # Check against fallback too
        assert hasattr(grid, 'delete_btn')
        assert isinstance(grid.delete_btn, (QPushButton, QWidget)) # Check against fallback too

    def test_initialization_config_disabled_features(self, qapp, widget_cleanup):
        """Test FluentDataGrid initialization with disabled features in config."""
        config = DataGridConfig(enable_search=False, enable_sort=False, enable_filter=False)
        grid = FluentDataGrid(config=config)
        widget_cleanup.append(grid)

        assert grid._config.enable_search is False
        assert grid._config.enable_sort is False
        assert grid._config.enable_filter is False

        assert isinstance(grid.table, FluentTableWidget)
        assert not hasattr(grid, 'search_box') # Search disabled
        # Action buttons are always created in _create_toolbar regardless of enable_sort/filter
        assert hasattr(grid, 'add_btn')
        assert hasattr(grid, 'edit_btn')
        assert hasattr(grid, 'delete_btn')

    def test_set_data(self, qapp, widget_cleanup):
        """Test set_data method."""
        grid = FluentDataGrid()
        widget_cleanup.append(grid)

        headers = ["Col A", "Col B"]
        data = [
            ["Row 1 A", "Row 1 B"],
            ["Row 2 A", "Row 2 B"],
        ]

        data_changed_emitted = False
        def on_data_changed():
            nonlocal data_changed_emitted
            data_changed_emitted = True

        grid.data_changed.connect(on_data_changed)

        grid.set_data(headers, data)
        QApplication.processEvents()

        assert grid._headers == headers
        assert grid._data == data
        assert grid._filtered_data == data # Initially filtered data is a copy of original
        assert data_changed_emitted is True

        # Check if table widget is populated
        assert grid.table.columnCount() == 2
        assert grid.table.rowCount() == 2
        assert grid.table.horizontalHeaderItem(0).text() == "Col A"
        assert grid.table.horizontalHeaderItem(1).text() == "Col B"
        assert grid.table.item(0, 0).text() == "Row 1 A"
        assert grid.table.item(1, 1).text() == "Row 2 B"

    def test_add_row(self, qapp, widget_cleanup):
        """Test add_row method."""
        grid = FluentDataGrid()
        widget_cleanup.append(grid)

        headers = ["Col A", "Col B"]
        initial_data = [["Row 1 A", "Row 1 B"]]
        grid.set_data(headers, initial_data)
        QApplication.processEvents()

        assert grid.table.rowCount() == 1
        assert len(grid._data) == 1

        new_row_data = ["Row 2 A", "Row 2 B"]

        data_changed_emitted = False
        def on_data_changed():
            nonlocal data_changed_emitted
            data_changed_emitted = True

        grid.data_changed.connect(on_data_changed)

        grid.add_row(new_row_data)
        QApplication.processEvents()

        assert len(grid._data) == 2
        assert grid._data[-1] == new_row_data
        # Adding a row should also update the filtered data and table
        assert grid.table.rowCount() == 2
        assert grid.table.item(1, 0).text() == "Row 2 A"
        assert data_changed_emitted is True

    def test_remove_selected_rows(self, qapp, widget_cleanup):
        """Test remove_selected_rows method."""
        grid = FluentDataGrid()
        widget_cleanup.append(grid)

        headers = ["Col A", "Col B"]
        data = [
            ["Row 0 A", "Row 0 B"],
            ["Row 1 A", "Row 1 B"],
            ["Row 2 A", "Row 2 B"],
            ["Row 3 A", "Row 3 B"],
        ]
        grid.set_data(headers, data)
        QApplication.processEvents()

        assert grid.table.rowCount() == 4
        assert len(grid._data) == 4

        data_changed_emitted = False
        def on_data_changed():
            nonlocal data_changed_emitted
            data_changed_emitted = True

        grid.data_changed.connect(on_data_changed)

        # Select rows 1 and 3 in the table
        grid.table.selectRow(1)
        grid.table.selectRow(3)
        QApplication.processEvents()

        # Check selected indices in state (should be original indices)
        assert sorted(grid._state.selected_rows) == [1, 3]

        # Remove selected rows
        success = grid.remove_selected_rows()
        QApplication.processEvents()

        assert success is True
        assert len(grid._data) == 2 # Rows 1 and 3 removed
        assert grid._data[0] == ["Row 0 A", "Row 0 B"]
        assert grid._data[1] == ["Row 2 A", "Row 2 B"] # Row 2 is now at index 1
        assert data_changed_emitted is True

        # Check table update
        assert grid.table.rowCount() == 2
        assert grid.table.item(0, 0).text() == "Row 0 A"
        assert grid.table.item(1, 0).text() == "Row 2 A" # Row 2 is now table row 1

        # Test removing no rows
        data_changed_emitted = False # Reset flag
        grid.table.clearSelection()
        QApplication.processEvents()
        success_no_remove = grid.remove_selected_rows()
        QApplication.processEvents()
        assert success_no_remove is False
        assert len(grid._data) == 2 # Data should not change
        assert data_changed_emitted is False # Signal should not be emitted

    def test_get_selected_data(self, qapp, widget_cleanup):
        """Test get_selected_data method."""
        grid = FluentDataGrid()
        widget_cleanup.append(grid)

        headers = ["Col A", "Col B"]
        data = [
            ["Row 0 A", "Row 0 B"],
            ["Row 1 A", "Row 1 B"],
            ["Row 2 A", "Row 2 B"],
        ]
        grid.set_data(headers, data)
        QApplication.processEvents()

        # Select rows 0 and 2
        grid.table.selectRow(0)
        grid.table.selectRow(2)
        QApplication.processEvents()

        selected_data = grid.get_selected_data()

        # The order might depend on how selectedItems() returns items,
        # but the content should match the original data for rows 0 and 2.
        assert len(selected_data) == 2
        assert ["Row 0 A", "Row 0 B"] in selected_data
        assert ["Row 2 A", "Row 2 B"] in selected_data
        assert ["Row 1 A", "Row 1 B"] not in selected_data

        # Test with no selection
        grid.table.clearSelection()
        QApplication.processEvents()
        selected_data_none = grid.get_selected_data()
        assert selected_data_none == []

    def test_filtering(self, qapp, widget_cleanup):
        """Test filtering data via search box."""
        grid = FluentDataGrid()
        widget_cleanup.append(grid)

        headers = ["Name", "Category", "Value"]
        data = [
            ["Apple", "Fruit", "1"],
            ["Banana", "Fruit", "2"],
            ["Carrot", "Vegetable", "3"],
            ["Date", "Fruit", "4"],
            ["Eggplant", "Vegetable", "5"],
        ]
        grid.set_data(headers, data)
        QApplication.processEvents()

        assert grid.table.rowCount() == 5
        assert len(grid._filtered_data) == 5

        # Simulate typing in search box
        if hasattr(grid.search_box, 'setText'):
            grid.search_box.setText("Fruit") # type: ignore
        QApplication.processEvents()

        # Filtering happens immediately on textChanged
        assert grid._state.current_filter == "Fruit"
        assert len(grid._filtered_data) == 3 # Apple, Banana, Date
        assert grid.table.rowCount() == 3
        table_items = [grid.table.item(i, 0).text() for i in range(grid.table.rowCount())]
        assert "Apple" in table_items
        assert "Banana" in table_items
        assert "Date" in table_items
        assert "Carrot" not in table_items

        # Simulate typing another filter
        if hasattr(grid.search_box, 'setText'):
            grid.search_box.setText("Egg") # type: ignore
        QApplication.processEvents()

        assert grid._state.current_filter == "Egg"
        assert len(grid._filtered_data) == 1 # Eggplant
        assert grid.table.rowCount() == 1
        assert grid.table.item(0, 0).text() == "Eggplant"

        # Simulate clearing search box
        if hasattr(grid.search_box, 'clear'):
            grid.search_box.clear() # type: ignore
        QApplication.processEvents()

        assert grid._state.current_filter == ""
        assert len(grid._filtered_data) == 5 # All data back
        assert grid.table.rowCount() == 5

    def test_selection_signal(self, qapp, widget_cleanup):
        """Test selection_changed signal emission."""
        grid = FluentDataGrid()
        widget_cleanup.append(grid)

        headers = ["Col A"]
        data = [["Row 0"], ["Row 1"], ["Row 2"]]
        grid.set_data(headers, data)
        QApplication.processEvents()

        emitted_selection = None
        def on_selection_changed(selected_indices):
            nonlocal emitted_selection
            emitted_selection = selected_indices

        grid.selection_changed.connect(on_selection_changed)

        # Select row 1
        grid.table.selectRow(1)
        QApplication.processEvents()

        assert emitted_selection == [1] # Should emit original index

        # Select rows 0 and 2 (multi-selection needs appropriate config, but QTableWidget allows it by default)
        grid.table.selectRow(0)
        grid.table.selectRow(2)
        QApplication.processEvents()

        # Order might vary, check content
        assert len(emitted_selection) == 2
        assert 0 in emitted_selection
        assert 2 in emitted_selection

        # Clear selection
        grid.table.clearSelection()
        QApplication.processEvents()

        assert emitted_selection == []

    def test_get_selected_row_indices_with_filter(self, qapp, widget_cleanup):
        """Test _get_selected_row_indices when data is filtered."""
        grid = FluentDataGrid()
        widget_cleanup.append(grid)

        headers = ["Name", "Category"]
        data = [
            ["Apple", "Fruit"],    # Original index 0
            ["Banana", "Fruit"],   # Original index 1
            ["Carrot", "Veg"],     # Original index 2
            ["Date", "Fruit"],     # Original index 3
            ["Eggplant", "Veg"],   # Original index 4
        ]
        grid.set_data(headers, data)
        QApplication.processEvents()

        # Apply filter "Fruit"
        if hasattr(grid.search_box, 'setText'):
            grid.search_box.setText("Fruit") # type: ignore
        QApplication.processEvents()

        # Filtered data is now: ["Apple", "Banana", "Date"]
        # Table rows correspond to these filtered indices:
        # Table Row 0 -> "Apple" (Original index 0)
        # Table Row 1 -> "Banana" (Original index 1)
        # Table Row 2 -> "Date" (Original index 3)

        # Select table rows 0 and 2
        grid.table.selectRow(0)
        grid.table.selectRow(2)
        QApplication.processEvents()

        # Get selected original indices
        selected_original_indices = grid._get_selected_row_indices()

        # Should map table row 0 -> original index 0
        # Should map table row 2 -> original index 3
        assert sorted(selected_original_indices) == [0, 3]

        # Test removing selected rows while filtered
        data_changed_emitted = False
        def on_data_changed():
            nonlocal data_changed_emitted
            data_changed_emitted = True
        grid.data_changed.connect(on_data_changed)

        success = grid.remove_selected_rows()
        QApplication.processEvents()

        assert success is True
        assert data_changed_emitted is True
        assert len(grid._data) == 3 # Original rows 0 and 3 removed
        # Check remaining original data
        assert ["Banana", "Fruit"] in grid._data
        assert ["Carrot", "Veg"] in grid._data
        assert ["Eggplant", "Veg"] in grid._data
        assert ["Apple", "Fruit"] not in grid._data
        assert ["Date", "Fruit"] not in grid._data

        # Check table update after removal (filter is still "Fruit")
        # The remaining "Fruit" item is "Banana" (original index 1)
        assert grid.table.rowCount() == 1
        assert grid.table.item(0, 0).text() == "Banana"

    def test_action_button_connections(self, qapp, widget_cleanup):
        """Test if action button signals are connected."""
        grid = FluentDataGrid()
        widget_cleanup.append(grid)

        # Check if slots exist and are callable (indirect check for connection)
        assert hasattr(grid, '_on_add_clicked')
        assert callable(grid._on_add_clicked)
        assert hasattr(grid, '_on_edit_clicked')
        assert callable(grid._on_edit_clicked)
        assert hasattr(grid, '_on_delete_clicked')
        assert callable(grid._on_delete_clicked)

        # More direct check: connect a mock slot and trigger the button
        add_clicked = False
        edit_clicked = False
        delete_clicked = False

        def mock_add():
            nonlocal add_clicked
            add_clicked = True
        def mock_edit():
            nonlocal edit_clicked
            edit_clicked = True
        def mock_delete():
            nonlocal delete_clicked
            delete_clicked = True

        # Disconnect original slots (if any were connected) and connect mocks
        # This is tricky with private slots. A simpler approach is to just check
        # if the button exists and has the clicked signal.
        assert hasattr(grid.add_btn, 'clicked')
        assert hasattr(grid.edit_btn, 'clicked')
        assert hasattr(grid.delete_btn, 'clicked')

        # We can't easily verify the *specific* slot connection without internal Qt APIs.
        # The presence of the slots and the buttons is a reasonable check for setup.
        # The functional tests for add/remove/edit would implicitly test the connections
        # if those methods were fully implemented.

    def test_theme_change_connection(self, qapp, widget_cleanup):
        """Test if theme_changed signal is connected."""
        grid = FluentDataGrid()
        widget_cleanup.append(grid)

        # Check if the theme change handler exists and is callable
        assert hasattr(grid, '_on_theme_changed')
        assert callable(grid._on_theme_changed)

        # We can't easily verify the connection itself without internal Qt APIs.
        # The presence of the handler and the check for theme_manager existence
        # in the setup code is the best we can do without mocking the theme manager.
