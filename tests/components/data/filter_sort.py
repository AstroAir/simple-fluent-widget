import pytest
import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QComboBox, QPushButton, QToolButton, QMenu, QMainWindow, QTableView
from PySide6.QtCore import Qt, Signal, QTimer, QModelIndex, QPersistentModelIndex, QAbstractItemModel
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtTest import QTest
from .filter_sort import FLUENT_COMPONENTS_AVAILABLE

# Add the project root to the path if necessary for relative imports
# Assuming the test file is components/data/test_filter_sort.py
# and the module is components/data/filter_sort.py
# The parent directory 'data' is a package (__init__.py exists)
# So we can use relative import
try:
    from .filter_sort import (
        FluentFilterBar, FluentSortingMenu, FluentFilterSortHeader,
        FluentFilterProxyModel, FilterConfig, SortConfig, FilterSortState,
        CustomFilterFunction, CategoryList, SortFieldDict
    )
    # Check if Fluent components are available or if fallbacks are used
    if not FLUENT_COMPONENTS_AVAILABLE:
         # If fallbacks are used, we might need to mock or adjust tests
         # For now, assume basic QWidget functionality is sufficient for tests
         # that don't rely on specific FluentButton/LineEdit features beyond basic signals/slots
         pass

except ImportError as e:
    pytest.fail(f"Failed to import components: {e}")


@pytest.fixture(scope="session")
def qapp():
    """Fixture to initialize QApplication."""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app
    # No need to quit the app if it was already running or managed by pytest-qt


@pytest.fixture
def widget_cleanup():
    """Fixture to clean up widgets after each test."""
    widgets = []
    yield widgets
    for widget in widgets:
        if widget and hasattr(widget, 'close'):
            widget.close()
    QApplication.processEvents() # Process events to ensure widgets are closed


@pytest.fixture
def simple_model():
    """Fixture to create a simple QStandardItemModel."""
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Name", "Category", "Value"])
    model.appendRow([QStandardItem("Apple"), QStandardItem("Fruit"), QStandardItem("1")])
    model.appendRow([QStandardItem("Banana"), QStandardItem("Fruit"), QStandardItem("2")])
    model.appendRow([QStandardItem("Carrot"), QStandardItem("Vegetable"), QStandardItem("3")])
    model.appendRow([QStandardItem("Date"), QStandardItem("Fruit"), QStandardItem("4")])
    model.appendRow([QStandardItem("Eggplant"), QStandardItem("Vegetable"), QStandardItem("5")])
    return model


class TestFluentFilterBar:

    def test_initialization(self, qapp, widget_cleanup):
        bar = FluentFilterBar()
        widget_cleanup.append(bar)
        assert isinstance(bar, QWidget)
        assert hasattr(bar, 'filterChanged')
        assert isinstance(bar._search_input, (QLineEdit, QWidget)) # Check against fallback too
        assert bar._category_selector is None
        assert isinstance(bar._clear_button, (QPushButton, QWidget)) # Check against fallback too
        assert bar._config.placeholder_text == "Filter items..."

    def test_initialization_with_categories(self, qapp, widget_cleanup):
        categories = ["Category A", "Category B"]
        bar = FluentFilterBar(categories=categories)
        widget_cleanup.append(bar)
        assert isinstance(bar._category_selector, QComboBox)
        assert bar._category_selector.count() == 3 # "All" + 2 categories
        assert bar._category_selector.itemText(0) == "All"
        assert bar._category_selector.itemText(1) == "Category A"
        assert bar._category_selector.itemText(2) == "Category B"

    def test_initialization_with_config(self, qapp, widget_cleanup):
        config = FilterConfig(placeholder_text="Search...", debounce_delay=500)
        bar = FluentFilterBar(config=config)
        widget_cleanup.append(bar)
        assert bar._config.placeholder_text == "Search..."
        assert bar._config.debounce_delay == 500
        if hasattr(bar._search_input, 'placeholderText'):
             assert bar._search_input.placeholderText() == "Search..." # type: ignore

    def test_filter_changed_signal_text(self, qapp, widget_cleanup):
        bar = FluentFilterBar()
        widget_cleanup.append(bar)
        
        emitted_text = None
        emitted_category = None

        def on_filter_changed(text, category):
            nonlocal emitted_text, emitted_category
            emitted_text = text
            emitted_category = category

        bar.filterChanged.connect(on_filter_changed)

        # Simulate text input
        if hasattr(bar._search_input, 'setText'):
            bar._search_input.setText("test") # type: ignore

        # Wait for debounce timer
        QTest.qWaitFor(bar._config.debounce_delay + 50)

        assert emitted_text == "test"
        assert emitted_category == "" # No category selected

    def test_filter_changed_signal_category(self, qapp, widget_cleanup):
        categories = ["Cat1", "Cat2"]
        bar = FluentFilterBar(categories=categories)
        widget_cleanup.append(bar)

        emitted_text = None
        emitted_category = None

        def on_filter_changed(text, category):
            nonlocal emitted_text, emitted_category
            emitted_text = text
            emitted_category = category

        bar.filterChanged.connect(on_filter_changed)

        # Simulate category change
        if bar._category_selector:
            bar._category_selector.setCurrentIndex(1) # Select Cat1

        # Category change is usually immediate, but wait a bit just in case
        QApplication.processEvents()
        QTest.qWaitFor(50)

        assert emitted_text == "" # No text entered yet
        assert emitted_category == "Cat1"

    def test_clear_filters(self, qapp, widget_cleanup):
        categories = ["Cat1", "Cat2"]
        bar = FluentFilterBar(categories=categories)
        widget_cleanup.append(bar)

        emitted_text = None
        emitted_category = None

        def on_filter_changed(text, category):
            nonlocal emitted_text, emitted_category
            emitted_text = text
            emitted_category = category

        bar.filterChanged.connect(on_filter_changed)

        # Set some filter and category
        if hasattr(bar._search_input, 'setText'):
            bar._search_input.setText("test") # type: ignore
        if bar._category_selector:
            bar._category_selector.setCurrentIndex(1) # Select Cat1

        QTest.qWaitFor(bar._config.debounce_delay + 50) # Wait for debounce

        assert bar.get_current_filter() == ("test", "Cat1")

        # Clear filters
        bar.clear_filters()

        # Wait for clear to process
        QApplication.processEvents()
        QTest.qWaitFor(50)

        assert bar.get_current_filter() == ("", "")
        if hasattr(bar._search_input, 'text'):
            assert bar._search_input.text() == "" # type: ignore
        if bar._category_selector:
            assert bar._category_selector.currentIndex() == 0 # "All"

        # Check signal emitted after clear
        assert emitted_text == ""
        assert emitted_category == ""

    def test_set_filter_text(self, qapp, widget_cleanup):
        bar = FluentFilterBar()
        widget_cleanup.append(bar)

        emitted_text = None
        emitted_category = None

        def on_filter_changed(text, category):
            nonlocal emitted_text, emitted_category
            emitted_text = text
            emitted_category = category

        bar.filterChanged.connect(on_filter_changed)

        bar.set_filter_text("programmatic")

        # Wait for debounce
        QTest.qWaitFor(bar._config.debounce_delay + 50)

        assert bar.get_current_filter() == ("programmatic", "")
        if hasattr(bar._search_input, 'text'):
            assert bar._search_input.text() == "programmatic" # type: ignore
        assert emitted_text == "programmatic"
        assert emitted_category == ""

    def test_set_category(self, qapp, widget_cleanup):
        categories = ["CatA", "CatB"]
        bar = FluentFilterBar(categories=categories)
        widget_cleanup.append(bar)

        emitted_text = None
        emitted_category = None

        def on_filter_changed(text, category):
            nonlocal emitted_text, emitted_category
            emitted_text = text
            emitted_category = category

        bar.filterChanged.connect(on_filter_changed)

        bar.set_category("CatB")

        QApplication.processEvents()
        QTest.qWaitFor(50)

        assert bar.get_current_filter() == ("", "CatB")
        if bar._category_selector:
            assert bar._category_selector.currentText() == "CatB"
        assert emitted_text == ""
        assert emitted_category == "CatB"

    def test_filter_history(self, qapp, widget_cleanup):
        bar = FluentFilterBar(config=FilterConfig(max_history_items=3))
        widget_cleanup.append(bar)

        if hasattr(bar._search_input, 'setText'):
            bar._search_input.setText("one") # type: ignore
            QTest.qWaitFor(bar._config.debounce_delay + 50)
            bar._search_input.setText("two") # type: ignore
            QTest.qWaitFor(bar._config.debounce_delay + 50)
            bar._search_input.setText("three") # type: ignore
            QTest.qWaitFor(bar._config.debounce_delay + 50)
            bar._search_input.setText("four") # type: ignore
            QTest.qWaitFor(bar._config.debounce_delay + 50)

        # Access the cached property
        history = bar.filter_history

        assert len(history) <= 3 # Max history items
        assert history == ["two", "three", "four"] # Check order and limit


class TestFluentSortingMenu:

    def test_initialization(self, qapp, widget_cleanup):
        menu = FluentSortingMenu()
        widget_cleanup.append(menu)
        assert isinstance(menu, QMenu)
        assert hasattr(menu, 'sortChanged')
        assert menu._fields == []
        assert menu._config.default_field == ""
        assert menu._config.default_ascending is True
        assert menu._state.current_sort_field == ""
        assert menu._state.sort_ascending is True
        assert len(menu.actions()) == 3 # Direction menu, separator, no field actions

    def test_initialization_with_fields(self, qapp, widget_cleanup):
        fields = [{"name": "col1", "display": "Column 1"}, {"name": "col2", "display": "Column 2"}]
        menu = FluentSortingMenu(fields=fields)
        widget_cleanup.append(menu)
        assert menu._fields == fields
        assert len(menu.actions()) == 5 # Direction menu, separator, 2 field actions
        assert menu._field_actions[0].text() == "Column 1"
        assert menu._field_actions[0].data() == "col1"
        assert menu._field_actions[1].text() == "Column 2"
        assert menu._field_actions[1].data() == "col2"
        # Default selection should be the first field if no default_field in config
        assert menu._state.current_sort_field == "col1"
        assert menu._field_actions[0].isChecked() is True
        assert menu._field_actions[1].isChecked() is False

    def test_initialization_with_config_and_fields(self, qapp, widget_cleanup):
        fields = [{"name": "col1", "display": "Column 1"}, {"name": "col2", "display": "Column 2"}]
        config = SortConfig(default_field="col2", default_ascending=False)
        menu = FluentSortingMenu(fields=fields, config=config)
        widget_cleanup.append(menu)
        assert menu._config.default_field == "col2"
        assert menu._config.default_ascending is False
        assert menu._state.current_sort_field == "col2"
        assert menu._state.sort_ascending is False
        assert menu._field_actions[0].isChecked() is False
        assert menu._field_actions[1].isChecked() is True
        assert menu.asc_action.isChecked() is False
        assert menu.desc_action.isChecked() is True

    def test_sort_changed_signal_direction(self, qapp, widget_cleanup):
        fields = [{"name": "col1", "display": "Column 1"}]
        menu = FluentSortingMenu(fields=fields)
        widget_cleanup.append(menu)

        emitted_field = None
        emitted_ascending = None

        def on_sort_changed(field, ascending):
            nonlocal emitted_field, emitted_ascending
            emitted_field = field
            emitted_ascending = ascending

        menu.sortChanged.connect(on_sort_changed)

        # Trigger descending action
        menu.desc_action.trigger()

        QApplication.processEvents()
        QTest.qWaitFor(50)

        assert menu._state.sort_ascending is False
        assert menu.asc_action.isChecked() is False
        assert menu.desc_action.isChecked() is True
        assert emitted_field == "col1" # Default field
        assert emitted_ascending is False

        # Trigger ascending action
        menu.asc_action.trigger()

        QApplication.processEvents()
        QTest.qWaitFor(50)

        assert menu._state.sort_ascending is True
        assert menu.asc_action.isChecked() is True
        assert menu.desc_action.isChecked() is False
        assert emitted_field == "col1" # Field should not change
        assert emitted_ascending is True

    def test_sort_changed_signal_field(self, qapp, widget_cleanup):
        fields = [{"name": "col1", "display": "Column 1"}, {"name": "col2", "display": "Column 2"}]
        menu = FluentSortingMenu(fields=fields)
        widget_cleanup.append(menu)

        emitted_field = None
        emitted_ascending = None

        def on_sort_changed(field, ascending):
            nonlocal emitted_field, emitted_ascending
            emitted_field = field
            emitted_ascending = ascending

        menu.sortChanged.connect(on_sort_changed)

        # Trigger action for col2
        menu._field_actions[1].trigger()

        QApplication.processEvents()
        QTest.qWaitFor(50)

        assert menu._state.current_sort_field == "col2"
        assert menu._field_actions[0].isChecked() is False
        assert menu._field_actions[1].isChecked() is True
        assert emitted_field == "col2"
        assert emitted_ascending is True # Default direction

        # Trigger action for col1
        menu._field_actions[0].trigger()

        QApplication.processEvents()
        QTest.qWaitFor(50)

        assert menu._state.current_sort_field == "col1"
        assert menu._field_actions[0].isChecked() is True
        assert menu._field_actions[1].isChecked() is False
        assert emitted_field == "col1"
        assert emitted_ascending is True # Direction should not change

    def test_set_sort_field(self, qapp, widget_cleanup):
        fields = [{"name": "col1", "display": "Column 1"}, {"name": "col2", "display": "Column 2"}]
        menu = FluentSortingMenu(fields=fields)
        widget_cleanup.append(menu)

        menu.set_sort_field("col2")

        QApplication.processEvents()
        QTest.qWaitFor(50)

        assert menu.get_current_sort() == ("col2", True) # Direction is default
        assert menu._field_actions[0].isChecked() is False
        assert menu._field_actions[1].isChecked() is True

    def test_set_sort_direction(self, qapp, widget_cleanup):
        fields = [{"name": "col1", "display": "Column 1"}]
        menu = FluentSortingMenu(fields=fields)
        widget_cleanup.append(menu)

        menu.set_sort_direction(False)

        QApplication.processEvents()
        QTest.qWaitFor(50)

        assert menu.get_current_sort() == ("col1", False) # Field is default
        assert menu.asc_action.isChecked() is False
        assert menu.desc_action.isChecked() is True


class TestFluentFilterSortHeader:

    def test_initialization(self, qapp, widget_cleanup):
        header = FluentFilterSortHeader()
        widget_cleanup.append(header)
        assert isinstance(header, QWidget)
        assert hasattr(header, 'filterChanged')
        assert hasattr(header, 'sortChanged')
        assert isinstance(header._filter_bar, FluentFilterBar)
        assert isinstance(header._sort_button, QToolButton)
        assert isinstance(header._sort_menu, FluentSortingMenu)

    def test_initialization_with_configs(self, qapp, widget_cleanup):
        filter_config = FilterConfig(placeholder_text="Find...")
        sort_config = SortConfig(default_field="id")
        header = FluentFilterSortHeader(filter_config=filter_config, sort_config=sort_config)
        widget_cleanup.append(header)
        assert header._filter_bar._config.placeholder_text == "Find..."
        assert header._sort_menu._config.default_field == "id"

    def test_filter_signal_forwarding(self, qapp, widget_cleanup):
        header = FluentFilterSortHeader()
        widget_cleanup.append(header)

        emitted_text = None
        emitted_category = None

        def on_filter_changed(text, category):
            nonlocal emitted_text, emitted_category
            emitted_text = text
            emitted_category = category

        header.filterChanged.connect(on_filter_changed)

        # Simulate text change in the internal filter bar
        if hasattr(header._filter_bar._search_input, 'setText'):
            header._filter_bar._search_input.setText("forward_test") # type: ignore

        # Wait for debounce in the filter bar
        QTest.qWaitFor(header._filter_bar._config.debounce_delay + 50)

        assert emitted_text == "forward_test"
        assert emitted_category == ""

    def test_sort_signal_forwarding(self, qapp, widget_cleanup):
        fields = [{"name": "colA", "display": "Col A"}]
        header = FluentFilterSortHeader(sort_fields=fields)
        widget_cleanup.append(header)

        emitted_field = None
        emitted_ascending = None

        def on_sort_changed(field, ascending):
            nonlocal emitted_field, emitted_ascending
            emitted_field = field
            emitted_ascending = ascending

        header.sortChanged.connect(on_sort_changed)

        # Simulate direction change in the internal sort menu
        header._sort_menu.desc_action.trigger()

        QApplication.processEvents()
        QTest.qWaitFor(50)

        assert emitted_field == "colA" # Default field
        assert emitted_ascending is False

    def test_clear_filters_method(self, qapp, widget_cleanup):
        header = FluentFilterSortHeader()
        widget_cleanup.append(header)

        # Set filter text
        if hasattr(header._filter_bar._search_input, 'setText'):
            header._filter_bar._search_input.setText("to_clear") # type: ignore
        QTest.qWaitFor(header._filter_bar._config.debounce_delay + 50)

        assert header.get_current_filter() == ("to_clear", "")

        header.clear_filters()

        QApplication.processEvents()
        QTest.qWaitFor(50)

        assert header.get_current_filter() == ("", "")

    def test_set_filter_text_method(self, qapp, widget_cleanup):
        header = FluentFilterSortHeader()
        widget_cleanup.append(header)

        header.set_filter_text("set_via_header")

        QTest.qWaitFor(header._filter_bar._config.debounce_delay + 50)

        assert header.get_current_filter() == ("set_via_header", "")
        if hasattr(header._filter_bar._search_input, 'text'):
            assert header._filter_bar._search_input.text() == "set_via_header" # type: ignore

    def test_set_sort_field_method(self, qapp, widget_cleanup):
        fields = [{"name": "colX", "display": "Col X"}, {"name": "colY", "display": "Col Y"}]
        header = FluentFilterSortHeader(sort_fields=fields)
        widget_cleanup.append(header)

        header.set_sort_field("colY")

        QApplication.processEvents()
        QTest.qWaitFor(50)

        assert header.get_current_sort() == ("colY", True) # Direction is default

    def test_set_sort_direction_method(self, qapp, widget_cleanup):
        fields = [{"name": "colZ", "display": "Col Z"}]
        header = FluentFilterSortHeader(sort_fields=fields)
        widget_cleanup.append(header)

        header.set_sort_direction(False)

        QApplication.processEvents()
        QTest.qWaitFor(50)

        assert header.get_current_sort() == ("colZ", False) # Field is default


class TestFluentFilterProxyModel:

    def test_initialization(self, qapp, widget_cleanup):
        proxy = FluentFilterProxyModel()
        widget_cleanup.append(proxy)
        assert isinstance(proxy, QSortFilterProxyModel)
        assert proxy.filterCaseSensitivity() == Qt.CaseSensitivity.CaseInsensitive
        assert proxy.filterKeyColumn() == -1 # Filter all columns

    def test_basic_filtering_case_insensitive(self, qapp, widget_cleanup, simple_model):
        proxy = FluentFilterProxyModel()
        widget_cleanup.append(proxy)
        proxy.setSourceModel(simple_model)

        proxy.setFilterRegularExpression("apple")
        QApplication.processEvents()
        assert proxy.rowCount() == 1
        assert proxy.data(proxy.index(0, 0), Qt.ItemDataRole.DisplayRole) == "Apple"

        proxy.setFilterRegularExpression("FRUIT")
        QApplication.processEvents()
        assert proxy.rowCount() == 3
        # Check if correct items are present (order might vary based on sort)
        items = [proxy.data(proxy.index(i, 0), Qt.ItemDataRole.DisplayRole) for i in range(proxy.rowCount())]
        assert "Apple" in items
        assert "Banana" in items
        assert "Date" in items
        assert "Carrot" not in items

        proxy.setFilterRegularExpression("")
        QApplication.processEvents()
        assert proxy.rowCount() == 5 # All rows visible when filter is empty

    def test_basic_filtering_case_sensitive(self, qapp, widget_cleanup, simple_model):
        proxy = FluentFilterProxyModel()
        widget_cleanup.append(proxy)
        proxy.setSourceModel(simple_model)
        proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseSensitive)

        proxy.setFilterRegularExpression("apple")
        QApplication.processEvents()
        assert proxy.rowCount() == 1
        assert proxy.data(proxy.index(0, 0), Qt.ItemDataRole.DisplayRole) == "Apple"

        proxy.setFilterRegularExpression("APPLE") # Should not match
        QApplication.processEvents()
        assert proxy.rowCount() == 0

        proxy.setFilterRegularExpression("Fruit") # Should not match
        QApplication.processEvents()
        assert proxy.rowCount() == 0

        proxy.setFilterRegularExpression("Fruit") # Should match if case sensitive is off
        proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        QApplication.processEvents()
        assert proxy.rowCount() == 3

    def test_filtering_specific_columns(self, qapp, widget_cleanup, simple_model):
        proxy = FluentFilterProxyModel()
        widget_cleanup.append(proxy)
        proxy.setSourceModel(simple_model)

        # Filter only by Category column (index 1)
        proxy.set_filter_columns([1])

        proxy.setFilterRegularExpression("Fruit")
        QApplication.processEvents()
        assert proxy.rowCount() == 3
        items = [proxy.data(proxy.index(i, 0), Qt.ItemDataRole.DisplayRole) for i in range(proxy.rowCount())]
        assert "Apple" in items
        assert "Banana" in items
        assert "Date" in items
        assert "Carrot" not in items

        proxy.setFilterRegularExpression("Vegetable")
        QApplication.processEvents()
        assert proxy.rowCount() == 2
        items = [proxy.data(proxy.index(i, 0), Qt.ItemDataRole.DisplayRole) for i in range(proxy.rowCount())]
        assert "Carrot" in items
        assert "Eggplant" in items
        assert "Apple" not in items

        # Filter only by Value column (index 2)
        proxy.set_filter_columns([2])
        proxy.setFilterRegularExpression("3")
        QApplication.processEvents()
        assert proxy.rowCount() == 1
        assert proxy.data(proxy.index(0, 0), Qt.ItemDataRole.DisplayRole) == "Carrot"

        # Reset filter columns
        proxy.set_filter_columns([])
        proxy.setFilterRegularExpression("Fruit")
        QApplication.processEvents()
        assert proxy.rowCount() == 3 # Back to filtering all columns

    def test_custom_filter_function(self, qapp, widget_cleanup, simple_model):
        proxy = FluentFilterProxyModel()
        widget_cleanup.append(proxy)
        proxy.setSourceModel(simple_model)

        # Custom function: only show items where the name starts with the pattern
        def starts_with_filter(index: QModelIndex, pattern: str) -> bool:
            if not index.isValid():
                return False
            data = index.data(Qt.ItemDataRole.DisplayRole)
            if data is None:
                return False
            return str(data).lower().startswith(pattern.lower())

        proxy.set_filter_function(starts_with_filter)

        proxy.setFilterRegularExpression("a")
        QApplication.processEvents()
        assert proxy.rowCount() == 1 # Only Apple
        assert proxy.data(proxy.index(0, 0), Qt.ItemDataRole.DisplayRole) == "Apple"

        proxy.setFilterRegularExpression("b")
        QApplication.processEvents()
        assert proxy.rowCount() == 1 # Only Banana
        assert proxy.data(proxy.index(0, 0), Qt.ItemDataRole.DisplayRole) == "Banana"

        proxy.setFilterRegularExpression("f") # Should match Fruit category, but function only checks name
        QApplication.processEvents()
        assert proxy.rowCount() == 0

        # Reset custom function
        proxy.set_filter_function(None)
        proxy.setFilterRegularExpression("f") # Now should match Fruit category again
        QApplication.processEvents()
        assert proxy.rowCount() == 3

    def test_column_visibility(self, qapp, widget_cleanup, simple_model):
        proxy = FluentFilterProxyModel()
        widget_cleanup.append(proxy)
        proxy.setSourceModel(simple_model)

        # Initially all columns are visible
        assert proxy.columnCount() == 3

        # Set visible columns to Name and Value (indices 0 and 2)
        proxy.set_visible_columns([0, 2])
        QApplication.processEvents()
        assert proxy.columnCount() == 2 # Only 2 columns should be visible

        # Check if the correct columns are mapped
        # Note: mapToSource is for rows, mapToSource for columns is not direct
        # We check by trying to access data at the new column indices
        assert proxy.headerData(0, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) == "Name"
        assert proxy.headerData(1, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) == "Value"

        # Reset visible columns
        proxy.set_visible_columns(None)
        QApplication.processEvents()
        assert proxy.columnCount() == 3 # All columns visible again

    def test_batch_filter_updates(self, qapp, widget_cleanup, simple_model):
        proxy = FluentFilterProxyModel()
        widget_cleanup.append(proxy)
        proxy.setSourceModel(simple_model)

        # Initial state
        assert proxy.rowCount() == 5

        with proxy.batch_filter_updates():
            # Set filter 1
            proxy.setFilterRegularExpression("Fruit")
            # Row count should not update immediately
            assert proxy.rowCount() == 5

            # Set filter columns
            proxy.set_filter_columns([0]) # Filter only by Name
            # Row count should still not update immediately
            assert proxy.rowCount() == 5

        # After exiting the context, invalidation should happen
        QApplication.processEvents()
        # Now filter "Fruit" should only match rows where Name contains "Fruit" (none in simple_model)
        assert proxy.rowCount() == 0

        # Test another batch update
        with proxy.batch_filter_updates():
             proxy.set_filter_columns([]) # Filter all columns again
             proxy.setFilterRegularExpression("Fruit") # Should match category now
             assert proxy.rowCount() == 0 # Still not updated

        QApplication.processEvents()
        assert proxy.rowCount() == 3 # Now updated

    def test_filter_accepts_row_persistent_index(self, qapp, widget_cleanup, simple_model):
        proxy = FluentFilterProxyModel()
        widget_cleanup.append(proxy)
        proxy.setSourceModel(simple_model)

        # Get a persistent index for a row
        source_index = simple_model.index(0, 0) # Index for "Apple"
        persistent_index = QPersistentModelIndex(source_index)

        # Set a filter that should match this row
        proxy.setFilterRegularExpression("Apple")
        QApplication.processEvents()

        # Manually call filterAcceptsRow with the persistent index's parent
        # The parent of a top-level item is an invalid QModelIndex/QPersistentModelIndex
        # We need to simulate the call signature from QSortFilterProxyModel
        # The source_parent argument in filterAcceptsRow is the parent of the source_row
        # For top-level items, this is an invalid index.
        # Let's test with a valid parent if we had a tree structure, but for a flat list,
        # the parent is always invalid. The important part is that the row index is correct.
        # The proxy model's filterAcceptsRow is called with the source row index and the source parent index.
        # For a flat model, source_parent is always QModelIndex().
        # The internal logic needs to handle QPersistentModelIndex if it were passed as source_parent,
        # but the QSortFilterProxyModel API passes QModelIndex.
        # The code in filterAcceptsRow handles the *source_parent* being potentially a QPersistentModelIndex,
        # which seems slightly off based on the standard QSortFilterProxyModel API, but let's test the logic.

        # Let's simulate the call with a valid source_row and an invalid source_parent (as is typical for top-level items)
        # The method signature is `filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex)`
        # QSortFilterProxyModel documentation says source_parent is QModelIndex.
        # The code includes QPersistentModelIndex in the type hint and handles it.
        # Let's create a persistent index for the parent (which is invalid) and pass it.
        invalid_persistent_parent = QPersistentModelIndex(QModelIndex())

        # Test row 0 ("Apple") with filter "Apple" and invalid persistent parent
        # This tests the QPersistentModelIndex handling for the parent argument, even if unusual.
        accepts_apple = proxy.filterAcceptsRow(0, invalid_persistent_parent)
        assert accepts_apple is True

        # Test row 2 ("Carrot") with filter "Apple" and invalid persistent parent
        accepts_carrot = proxy.filterAcceptsRow(2, invalid_persistent_parent)
        assert accepts_carrot is False

        # Test with a valid QModelIndex parent (simulating a child item if the model was hierarchical)
        # Although simple_model is flat, we can still pass a valid index as the parent argument
        # to test the QPersistentModelIndex conversion logic within the method.
        # Let's use the index of the first item as a dummy parent for testing the conversion logic path.
        dummy_valid_parent_index = simple_model.index(0, 0)
        dummy_persistent_parent = QPersistentModelIndex(dummy_valid_parent_index)

        # Call filterAcceptsRow with a dummy valid persistent parent index
        # The logic inside should convert dummy_persistent_parent to a QModelIndex
        # and then proceed. The actual filtering logic will still apply to source_row 0.
        accepts_apple_with_dummy_parent = proxy.filterAcceptsRow(0, dummy_persistent_parent)
        assert accepts_apple_with_dummy_parent is True # Should still accept based on row 0 data

        # Call filterAcceptsRow with a dummy valid persistent parent index for a non-matching row
        accepts_carrot_with_dummy_parent = proxy.filterAcceptsRow(2, dummy_persistent_parent)
        assert accepts_carrot_with_dummy_parent is False # Should still reject based on row 2 data
