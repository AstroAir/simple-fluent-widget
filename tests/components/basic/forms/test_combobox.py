import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QCheckBox, QPushButton

from components.basic.forms.combobox import (
    FluentComboBox,
    FluentMultiSelectComboBox,
    FluentSearchableComboBox,
    FluentDropDownButton,
    FluentSearchBox
)

# Fixture for QApplication instance
@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestFluentComboBox:
    def test_initialization(self, qtbot, app_instance):
        combo = FluentComboBox()
        qtbot.addWidget(combo)
        assert combo.count() == 0
        assert not combo._is_expanded

    def test_add_items(self, qtbot, app_instance):
        combo = FluentComboBox()
        qtbot.addWidget(combo)
        items = ["Item 1", "Item 2", "Item 3"]
        combo.addItems(items)
        assert combo.count() == 3
        assert combo.itemText(1) == "Item 2"

    def test_popup_visibility(self, qtbot, app_instance):
        combo = FluentComboBox()
        qtbot.addWidget(combo)
        combo.addItems(["One", "Two"])
        combo.show()

        with qtbot.wait_exposed(combo.view()):
            combo.showPopup()

        assert combo.view().isVisible()
        assert combo._is_expanded

        combo.hidePopup()
        qtbot.waitUntil(lambda: not combo.view().isVisible(), timeout=1000)
        assert not combo._is_expanded

    def test_selection_change_signal(self, qtbot, app_instance):
        combo = FluentComboBox()
        qtbot.addWidget(combo)
        combo.addItems(["A", "B", "C"])

        with qtbot.waitSignal(combo.currentIndexChanged, timeout=500) as blocker:
            combo.setCurrentIndex(2)

        assert blocker.args == [2]
        assert combo.currentText() == "C"


class TestFluentMultiSelectComboBox:
    @pytest.fixture
    def multi_combo(self, qtbot, app_instance):
        widget = FluentMultiSelectComboBox()
        widget.add_items(["Apple", "Banana", "Cherry", "Date"])
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, multi_combo):
        assert len(multi_combo.get_selected_items()) == 0
        assert multi_combo.main_button.text() == "Select items..."

    def test_programmatic_selection(self, multi_combo, qtbot):
        with qtbot.waitSignal(multi_combo.selection_changed, timeout=500) as blocker:
            multi_combo.set_selected_items(["Apple", "Cherry"])

        assert blocker.args == [["Apple", "Cherry"]]
        assert multi_combo.get_selected_items() == ["Apple", "Cherry"]
        assert multi_combo.main_button.text() == "2 items selected"

    def test_clear_selection(self, multi_combo, qtbot):
        multi_combo.set_selected_items(["Apple", "Cherry"])
        assert len(multi_combo.get_selected_items()) == 2

        with qtbot.waitSignal(multi_combo.selection_changed, timeout=500) as blocker:
            multi_combo.clear_selection()

        assert blocker.args == [[]]
        assert len(multi_combo.get_selected_items()) == 0
        assert multi_combo.main_button.text() == "Select items..."

    def test_dropdown_interaction(self, multi_combo, qtbot):
        multi_combo.show()
        qtbot.mouseClick(multi_combo.main_button, Qt.MouseButton.LeftButton)

        qtbot.waitUntil(lambda: multi_combo._dropdown_widget is not None and multi_combo._dropdown_widget.isVisible())

        dropdown = multi_combo._dropdown_widget
        checkboxes = dropdown.findChildren(QCheckBox)
        assert len(checkboxes) == 4

        with qtbot.waitSignal(multi_combo.selection_changed, timeout=500) as blocker:
            qtbot.mouseClick(checkboxes[1], Qt.MouseButton.LeftButton)

        assert blocker.args == [["Banana"]]
        assert multi_combo.get_selected_items() == ["Banana"]
        assert multi_combo.main_button.text() == "Banana"

        buttons = dropdown.findChildren(QPushButton)
        done_button = next(b for b in buttons if b.text() == "Done")

        qtbot.mouseClick(done_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: not dropdown.isVisible())
        assert not multi_combo._is_expanded


class TestFluentSearchableComboBox:
    @pytest.fixture
    def searchable_combo(self, qtbot, app_instance):
        widget = FluentSearchableComboBox()
        widget.add_items(["Apple", "Apricot", "Avocado", "Banana", "Blueberry"])
        qtbot.addWidget(widget)
        return widget

    def test_initialization(self, searchable_combo):
        assert searchable_combo.get_selected_item() is None
        assert not searchable_combo.list_widget.isVisible()

    def test_search_filtering(self, searchable_combo, qtbot):
        search_box = searchable_combo.search_box
        list_widget = searchable_combo.list_widget

        qtbot.keyClicks(search_box, "Ap")

        qtbot.waitUntil(lambda: list_widget.isVisible())
        qtbot.waitUntil(lambda: list_widget.count() == 2)

        assert list_widget.item(0).text() == "Apple"
        assert list_widget.item(1).text() == "Apricot"

        search_box.clear()
        qtbot.waitUntil(lambda: not list_widget.isVisible())

    def test_item_selection_by_click(self, searchable_combo, qtbot):
        search_box = searchable_combo.search_box
        list_widget = searchable_combo.list_widget

        qtbot.keyClicks(search_box, "B")
        qtbot.waitUntil(lambda: list_widget.isVisible() and list_widget.count() == 2)

        with qtbot.waitSignal(searchable_combo.item_selected, timeout=500) as blocker:
            item_to_click = list_widget.item(1)
            qtbot.mouseClick(list_widget.viewport(), Qt.MouseButton.LeftButton, pos=list_widget.visualItemRect(item_to_click).center())

        assert blocker.args == ["Blueberry", None]
        assert searchable_combo.get_selected_item()['text'] == "Blueberry"
        assert search_box.text() == "Blueberry"
        qtbot.waitUntil(lambda: not list_widget.isVisible())


class TestFluentDropDownButton:
    @pytest.fixture
    def dropdown_button(self, qtbot, app_instance):
        button = FluentDropDownButton("Actions")
        button.add_menu_item("Copy", data="copy_action")
        button.add_menu_item("Paste", data="paste_action")
        qtbot.addWidget(button)
        return button

    def test_initialization(self, dropdown_button):
        assert dropdown_button.text() == "Actions ▼"
        assert not dropdown_button._is_expanded

    def test_dropdown_visibility(self, dropdown_button, qtbot):
        dropdown_button.show()
        qtbot.mouseClick(dropdown_button, Qt.MouseButton.LeftButton)

        qtbot.waitUntil(lambda: dropdown_button._dropdown_widget is not None and dropdown_button._dropdown_widget.isVisible())
        assert dropdown_button._is_expanded

        qtbot.mouseClick(dropdown_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: not dropdown_button._dropdown_widget.isVisible())
        assert not dropdown_button._is_expanded

    def test_item_click_signal(self, dropdown_button, qtbot):
        dropdown_button.show()
        qtbot.mouseClick(dropdown_button, Qt.MouseButton.LeftButton)

        qtbot.waitUntil(lambda: dropdown_button._dropdown_widget is not None)
        dropdown = dropdown_button._dropdown_widget

        menu_buttons = dropdown.findChildren(QPushButton)
        assert len(menu_buttons) == 2

        with qtbot.waitSignal(dropdown_button.item_clicked, timeout=500) as blocker:
            qtbot.mouseClick(menu_buttons[1], Qt.MouseButton.LeftButton)

        assert blocker.args == ["Paste", "paste_action"]
        qtbot.waitUntil(lambda: not dropdown.isVisible())
        assert not dropdown_button._is_expanded