import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from components.basic.display.chip import FluentChip, FluentChipGroup, FluentFilterChip

# Fixture for QApplication instance
@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

class TestFluentChip:
    def test_initialization(self, qtbot):
        chip = FluentChip(text="Test Chip")
        qtbot.addWidget(chip)
        assert chip.get_text() == "Test Chip"
        assert chip._chip_style == FluentChip.ChipStyle.FILLED
        assert chip._chip_type == FluentChip.ChipType.DEFAULT
        assert chip._size == FluentChip.ChipSize.MEDIUM
        assert not chip._closable
        assert chip._clickable

    def test_closable_chip(self, qtbot):
        chip = FluentChip(text="Closable", closable=True)
        qtbot.addWidget(chip)
        assert chip._closable
        assert hasattr(chip, '_close_button')

        with qtbot.waitSignal(chip.close_clicked, timeout=1000, raising=True):
            qtbot.mouseClick(chip._close_button, Qt.MouseButton.LeftButton)

    def test_clickable_chip(self, qtbot):
        chip = FluentChip(text="Clickable", clickable=True)
        qtbot.addWidget(chip)
        assert chip._clickable

        with qtbot.waitSignal(chip.clicked, timeout=500, raising=True):
            qtbot.mouseClick(chip, Qt.MouseButton.LeftButton)

    def test_non_clickable_chip(self, qtbot):
        chip = FluentChip(text="Not Clickable", clickable=False)
        qtbot.addWidget(chip)
        assert not chip._clickable

        # This should not emit the clicked signal
        with qtbot.assertNotEmitted(chip.clicked):
            qtbot.mouseClick(chip, Qt.MouseButton.LeftButton)

    def test_set_text(self, qtbot):
        chip = FluentChip(text="Initial")
        qtbot.addWidget(chip)
        chip.set_text("Updated")
        assert chip.get_text() == "Updated"
        assert chip._text_label.text() == "Updated"

    def test_set_type_and_style(self, qtbot):
        chip = FluentChip(text="Styled")
        qtbot.addWidget(chip)

        chip.set_type(FluentChip.ChipType.PRIMARY)
        assert chip._chip_type == FluentChip.ChipType.PRIMARY

        chip.set_style(FluentChip.ChipStyle.OUTLINED)
        assert chip._chip_style == FluentChip.ChipStyle.OUTLINED


class TestFluentChipGroup:
    def test_initialization(self, qtbot):
        group = FluentChipGroup()
        qtbot.addWidget(group)
        assert not group._selectable
        assert not group._multi_select
        assert group._max_chips == -1
        assert len(group._chips) == 0

    def test_add_and_remove_chip(self, qtbot):
        group = FluentChipGroup()
        qtbot.addWidget(group)

        # Add chip
        with qtbot.waitSignal(group.chip_added, timeout=500, check_params_cb=lambda text: text == "Chip 1"):
            chip1 = group.add_chip("Chip 1")

        assert len(group._chips) == 1
        assert group._chips[0] is chip1

        # Remove chip
        with qtbot.waitSignal(group.chip_removed, timeout=1000, check_params_cb=lambda text: text == "Chip 1"):
            group.remove_chip("Chip 1")

        qtbot.waitUntil(lambda: len(group._chips) == 0, timeout=1000)
        assert len(group._chips) == 0

    def test_clear_chips(self, qtbot):
        group = FluentChipGroup()
        qtbot.addWidget(group)
        group.add_chip("Chip 1")
        group.add_chip("Chip 2")
        assert len(group._chips) == 2

        group.clear_chips()
        qtbot.waitUntil(lambda: len(group._chips) == 0, timeout=1000)
        assert len(group._chips) == 0

    def test_single_selection(self, qtbot):
        group = FluentChipGroup(selectable=True, multi_select=False)
        qtbot.addWidget(group)
        chip1 = group.add_chip("Chip 1")
        chip2 = group.add_chip("Chip 2")

        with qtbot.waitSignal(group.selection_changed, timeout=500, check_params_cb=lambda texts: texts == ["Chip 1"]):
            if chip1 is not None:
                qtbot.mouseClick(chip1, Qt.MouseButton.LeftButton)

        assert chip1 in group._selected_chips
        assert chip2 not in group._selected_chips
        assert chip1._chip_style == FluentChip.ChipStyle.FILLED
        assert chip1._chip_type == FluentChip.ChipType.PRIMARY
        if chip2 is not None:
            assert chip2._chip_style == FluentChip.ChipStyle.OUTLINED

    def test_multi_selection(self, qtbot):
        group = FluentChipGroup(selectable=True, multi_select=True)
        qtbot.addWidget(group)
        chip1 = group.add_chip("Chip 1")
        chip2 = group.add_chip("Chip 2")

        with qtbot.waitSignal(group.selection_changed, timeout=500):
            if chip1 is not None:
                qtbot.mouseClick(chip1, Qt.MouseButton.LeftButton)
        assert group.get_selected_texts() == ["Chip 1"]

        with qtbot.waitSignal(group.selection_changed, timeout=500):
            if chip2 is not None:
                qtbot.mouseClick(chip2, Qt.MouseButton.LeftButton)
        assert sorted(group.get_selected_texts()) == ["Chip 1", "Chip 2"]


class TestFluentFilterChip:
    def test_initialization(self, qtbot):
        chip = FluentFilterChip(text="Filter")
        qtbot.addWidget(chip)
        assert not chip.is_active()
        assert chip._chip_style == FluentChip.ChipStyle.OUTLINED

    def test_toggle_filter(self, qtbot):
        chip = FluentFilterChip(text="Filter")
        qtbot.addWidget(chip)

        with qtbot.waitSignal(chip.filter_toggled, timeout=500, check_params_cb=lambda active: active is True):
            qtbot.mouseClick(chip, Qt.MouseButton.LeftButton)
        assert chip.is_active()
        assert chip._chip_style == FluentChip.ChipStyle.FILLED

        with qtbot.waitSignal(chip.filter_toggled, timeout=500, check_params_cb=lambda active: active is False):
            qtbot.mouseClick(chip, Qt.MouseButton.LeftButton)
        assert not chip.is_active()
        assert chip._chip_style