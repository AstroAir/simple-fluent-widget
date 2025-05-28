"""
Fluent Design Breadcrumb Component
Navigation breadcrumb with separators and interactive items
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton,
                               QSizePolicy, QMenu)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, Property, QByteArray
from PySide6.QtGui import QFont, QAction
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional, List, Dict, Any
from enum import Enum


class FluentBreadcrumbItem(QPushButton):
    """Individual breadcrumb item"""
    hoverProgressChanged = Signal(float)

    def __init__(self, text: str = "", data: Any = None, parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self._data = data
        self._is_current = False
        self._hover_progress = 0.0

        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set font
        font = QFont()
        font.setPointSize(13)
        self.setFont(font)

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Minimum,
                           QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(32)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        if self._is_current:
            text_color = theme.get_color('text_primary')
            bg_color = "transparent"
            # cursor = "default" # Unused variable
        else:
            text_color = theme.get_color('text_secondary')
            bg_color = "transparent"
            # cursor = "pointer" # Unused variable

        style_sheet = f"""
            QPushButton {{
                background-color: {bg_color};
                border: none;
                color: {text_color.name()};
                padding: 6px 8px;
                border-radius: 4px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
        """

        if self._is_current:
            style_sheet += """
                QPushButton:hover {
                    background-color: transparent;
                }
                QPushButton:pressed {
                    background-color: transparent;
                }
            """
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup animations"""
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_progress"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def _get_hover_progress(self):
        return self._hover_progress

    def _set_hover_progress(self, value):
        if self._hover_progress != value:
            self._hover_progress = value
            self.hoverProgressChanged.emit(self._hover_progress)
            self.update()

    hover_progress = Property(float, _get_hover_progress,
                              _set_hover_progress, None, "", notify=hoverProgressChanged)

    def setData(self, data: Any):
        """Set item data"""
        self._data = data

    def data(self) -> Any:
        """Get item data"""
        return self._data

    def setCurrent(self, current: bool):
        """Set whether this is the current item"""
        self._is_current = current
        self._setup_style()

    def isCurrent(self) -> bool:
        """Check if this is the current item"""
        return self._is_current

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentBreadcrumbSeparator(QLabel):
    """Breadcrumb separator"""

    def __init__(self, separator: str = ">", parent: Optional[QWidget] = None):
        super().__init__(separator, parent)

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedWidth(20)

        font = QFont()
        font.setPointSize(12)
        self.setFont(font)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QLabel {{
                color: {theme.get_color('text_tertiary').name()};
                background-color: transparent;
                border: none;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentBreadcrumb(QWidget):
    """Fluent Design breadcrumb navigation"""

    class OverflowMode(Enum):
        ELLIPSIS = "ellipsis"
        DROPDOWN = "dropdown"
        SCROLL = "scroll"

    # Signals
    item_clicked = Signal(int, object)  # index, data

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items: List[Dict[str, Any]] = []
        self._max_items = 5
        self._overflow_mode = self.OverflowMode.ELLIPSIS
        self._separator = ">"
        self._show_home = True
        self._home_text = "主页"
        self._home_data = None

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 4, 8, 4)
        self._layout.setSpacing(0)

        # Add stretch at the end
        self._layout.addStretch()

        self._update_breadcrumb()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentBreadcrumb {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
            }}
        """

        self.setStyleSheet(style_sheet)

    def addItem(self, text: str, data: Any = None):
        """Add breadcrumb item"""
        self._items.append({"text": text, "data": data})
        self._update_breadcrumb()

    def insertItem(self, index: int, text: str, data: Any = None):
        """Insert item at index"""
        if 0 <= index <= len(self._items):
            self._items.insert(index, {"text": text, "data": data})
            self._update_breadcrumb()

    def removeItem(self, index: int):
        """Remove item at index"""
        if 0 <= index < len(self._items):
            self._items.pop(index)
            self._update_breadcrumb()

    def setItems(self, items: List[Dict[str, Any]]):
        """Set all items

        Args:
            items: List of dicts with 'text' and optionally 'data' keys
        """
        self._items = items.copy()
        self._update_breadcrumb()

    def items(self) -> List[Dict[str, Any]]:
        """Get all items"""
        return self._items.copy()

    def clear(self):
        """Clear all items"""
        self._items.clear()
        self._update_breadcrumb()

    def setMaxItems(self, max_items: int):
        """Set maximum visible items"""
        self._max_items = max(1, max_items)
        self._update_breadcrumb()

    def maxItems(self) -> int:
        """Get maximum visible items"""
        return self._max_items

    def setOverflowMode(self, mode: OverflowMode):
        """Set overflow handling mode"""
        self._overflow_mode = mode
        self._update_breadcrumb()

    def overflowMode(self) -> OverflowMode:
        """Get overflow handling mode"""
        return self._overflow_mode

    def setSeparator(self, separator: str):
        """Set separator text"""
        self._separator = separator
        self._update_breadcrumb()

    def separator(self) -> str:
        """Get separator text"""
        return self._separator

    def setShowHome(self, show: bool):
        """Set whether to show home item"""
        self._show_home = show
        self._update_breadcrumb()

    def showHome(self) -> bool:
        """Check if home item is shown"""
        return self._show_home

    def setHomeText(self, text: str):
        """Set home item text"""
        self._home_text = text
        self._update_breadcrumb()

    def homeText(self) -> str:
        """Get home item text"""
        return self._home_text

    def setHomeData(self, data: Any):
        """Set home item data"""
        self._home_data = data

    def homeData(self) -> Any:
        """Get home item data"""
        return self._home_data

    def _update_breadcrumb(self):
        """Update breadcrumb display"""
        # Clear existing widgets
        for i in reversed(range(self._layout.count())):
            item = self._layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget and not widget.objectName() == "stretch":
                    widget.setParent(None)

        # Remove stretch
        if self._layout.count() > 0:
            self._layout.removeItem(
                self._layout.itemAt(self._layout.count() - 1))

        all_items = []

        # Add home item if enabled
        if self._show_home:
            all_items.append(
                {"text": self._home_text, "data": self._home_data, "is_home": True})

        # Add regular items
        all_items.extend([{**item, "is_home": False} for item in self._items])

        if not all_items:
            self._layout.addStretch()
            return

        # Handle overflow
        visible_items = self._get_visible_items(all_items)

        # Create widgets
        for i, item_data in enumerate(visible_items):
            # Add separator (except for first item)
            if i > 0:
                separator = FluentBreadcrumbSeparator(self._separator, self)
                self._layout.addWidget(separator)

            # Create item
            if item_data.get("is_ellipsis", False):
                # Ellipsis item with dropdown
                ellipsis_item = self._create_ellipsis_item(
                    item_data["hidden_items"])
                self._layout.addWidget(ellipsis_item)
            else:
                # Regular item
                item = FluentBreadcrumbItem(
                    item_data["text"], item_data["data"], self)

                # Set current state (last item is current)
                is_current = (i == len(visible_items) - 1)
                item.setCurrent(is_current)

                # Connect click signal
                if not is_current:
                    original_index = item_data.get("original_index", -1)
                    # Capture item_data correctly for the lambda
                    item.clicked.connect(
                        lambda _checked=False, idx=original_index, current_item_data=item_data["data"]:
                        self._on_item_clicked(idx, current_item_data)
                    )

                self._layout.addWidget(item)

        # Add stretch at the end
        self._layout.addStretch()

    def _get_visible_items(self, all_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get visible items based on overflow mode"""
        # Ensure all items have an original_index before slicing or processing
        for idx, item_content in enumerate(all_items):
            # Assign if not already (e.g. home item)
            if "original_index" not in item_content:
                # This logic assumes items in self._items are indexed after home
                if item_content.get("is_home"):
                    # Special index for home or adjust as needed
                    item_content["original_index"] = -1
                else:
                    # Find its original position in self._items if possible, or use all_items index
                    # This part needs careful handling if self._items indices are important
                    # For simplicity, using all_items index if it's not home
                    item_content["original_index"] = self._items.index(next(
                        i for i in self._items if i["text"] == item_content["text"] and i["data"] == item_content["data"])) if not item_content.get("is_home") else -1

        if len(all_items) <= self._max_items:
            return all_items

        if self._overflow_mode == self.OverflowMode.ELLIPSIS:
            visible = []

            first_item = all_items[0].copy()
            visible.append(first_item)

            hidden_start = 1
            hidden_end = len(all_items) - (self._max_items - 2)

            # Ensure hidden_end is not less than hidden_start
            if hidden_start < hidden_end:
                hidden_items_list = all_items[hidden_start:hidden_end]
                if hidden_items_list:
                    ellipsis_data = {
                        "text": "...", "data": None, "is_ellipsis": True,
                        "hidden_items": hidden_items_list
                    }
                    visible.append(ellipsis_data)
            else:  # Not enough items for ellipsis, adjust hidden_end
                hidden_end = hidden_start

            for i in range(hidden_end, len(all_items)):
                item = all_items[i].copy()
                visible.append(item)

            return visible

        elif self._overflow_mode == self.OverflowMode.DROPDOWN:
            if len(all_items) > 2:  # Need at least home, dropdown, current
                visible = []

                first_item = all_items[0].copy()
                visible.append(first_item)

                hidden_items_list = all_items[1:-1]  # Middle items
                if hidden_items_list:
                    dropdown_data = {
                        "text": "...", "data": None, "is_ellipsis": True,
                        "hidden_items": hidden_items_list
                    }
                    visible.append(dropdown_data)

                last_item = all_items[-1].copy()
                visible.append(last_item)

                return visible
            # Fallback if not enough items for dropdown structure
            return all_items[-self._max_items:].copy()

        # SCROLL mode or fallback
        return all_items[-self._max_items:].copy()

    def _create_ellipsis_item(self, hidden_items: List[Dict[str, Any]]) -> FluentBreadcrumbItem:
        """Create ellipsis item with dropdown menu"""
        ellipsis_item = FluentBreadcrumbItem("...", None, self)
        ellipsis_item.setCurrent(False)

        menu = QMenu(self)

        for item_data_loop_var in hidden_items:
            # Ensure original_index is present in item_data_loop_var
            # It should have been added by _get_visible_items
            action_text = item_data_loop_var.get("text", "N/A")
            action = QAction(action_text, menu)

            # Correctly capture item_data_loop_var for the lambda
            action.triggered.connect(
                lambda _checked=False, current_item_data=item_data_loop_var:
                self._on_item_clicked(current_item_data.get(
                    "original_index", -1), current_item_data.get("data"))
            )
            menu.addAction(action)

        ellipsis_item.clicked.connect(
            lambda _checked=False: self._show_dropdown_menu(ellipsis_item, menu))

        return ellipsis_item

    def _show_dropdown_menu(self, button: FluentBreadcrumbItem, menu: QMenu):
        """Show dropdown menu"""
        global_pos = button.mapToGlobal(button.rect().bottomLeft())
        menu.exec(global_pos)

    def _on_item_clicked(self, index: int, data: Any):
        """Handle item clicked"""
        self.item_clicked.emit(index, data)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self._update_breadcrumb()
