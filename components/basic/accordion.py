"""
Fluent Design Accordion Component
Expandable and collapsible content panels with smooth animations
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel)
from PySide6.QtCore import (Qt, Signal, QPropertyAnimation, QEasingCurve,
                            Property, QByteArray)
from PySide6.QtGui import QFont
from core.theme import theme_manager
from typing import Optional, List


class FluentAccordionItem(QFrame):
    """Individual accordion item with header and content"""

    # Signals
    expanded = Signal(bool)
    clicked = Signal()

    def __init__(self, title: str = "", content_widget: Optional[QWidget] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._is_expanded = False
        self._content_height = 0
        self._header_height = 48
        self._animation_duration = 250  # 使用具体值代替 FluentAnimation.DURATION_NORMAL
        self._expand_progress = 0.0
        self._hover_progress = 0.0
        self._icon_rotation = 0.0

        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        if content_widget:
            self.setContentWidget(content_widget)

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setFrameStyle(QFrame.Shape.NoFrame)

        # Main layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Header
        self._header = QFrame()
        self._header.setFixedHeight(self._header_height)
        self._header.setCursor(Qt.CursorShape.PointingHandCursor)

        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(16, 0, 16, 0)
        header_layout.setSpacing(12)

        # Expand/collapse icon
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(16, 16)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_icon()

        # Title label
        self._title_label = QLabel(self._title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.Medium)
        self._title_label.setFont(title_font)

        header_layout.addWidget(self._icon_label)
        header_layout.addWidget(self._title_label)
        header_layout.addStretch()

        # Content container
        self._content_container = QFrame()
        self._content_container.setFixedHeight(0)
        self._content_container.setVisible(False)

        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(16, 0, 16, 16)
        self._content_layout.setSpacing(8)

        self._layout.addWidget(self._header)
        self._layout.addWidget(self._content_container)

        # Connect header click
        self._header.mousePressEvent = self._on_header_clicked
        self._header.enterEvent = self._on_header_enter
        self._header.leaveEvent = self._on_header_leave

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        # Header style
        header_style = f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-bottom: none;
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                background: transparent;
                border: none;
            }}
        """

        # Content style
        content_style = f"""
            QFrame {{
                background-color: {theme.get_color('background').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-top: none;
            }}
        """

        self._header.setStyleSheet(header_style)
        self._content_container.setStyleSheet(content_style)

    def _setup_animations(self):
        """Setup animations"""
        # Expand animation
        self._expand_animation = QPropertyAnimation(
            self, QByteArray(b"expand_progress"))
        self._expand_animation.setDuration(self._animation_duration)
        self._expand_animation.setEasingCurve(
            QEasingCurve.Type.OutCubic)  # 使用正确的曲线类型
        self._expand_animation.finished.connect(self._on_expand_finished)

        # Hover animation
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_progress"))
        self._hover_animation.setDuration(150)  # 快速动画持续时间
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Icon rotation animation
        self._icon_animation = QPropertyAnimation(
            self, QByteArray(b"icon_rotation"))
        self._icon_animation.setDuration(self._animation_duration)
        self._icon_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _update_icon(self):
        """Update expand/collapse icon"""
        theme = theme_manager
        icon_color = theme.get_color('text_secondary')

        # Create arrow icon (simple implementation)
        self._icon_label.setText("▶" if not self._is_expanded else "▼")
        self._icon_label.setStyleSheet(f"color: {icon_color.name()};")

    def _get_expand_progress(self):
        return self._expand_progress

    def _set_expand_progress(self, value):
        self._expand_progress = value

        # Update content container height
        if self._content_height > 0:
            height = int(self._content_height * value)
            self._content_container.setFixedHeight(height)

        self.update()

    def _get_hover_progress(self):
        return self._hover_progress

    def _set_hover_progress(self, value):
        self._hover_progress = value
        # Could add hover effects here
        self.update()

    def _get_icon_rotation(self):
        return self._icon_rotation

    def _set_icon_rotation(self, value):
        self._icon_rotation = value
        self.update()

    expand_progress = Property(
        float, _get_expand_progress, _set_expand_progress, None, "", user=True)
    hover_progress = Property(
        float, _get_hover_progress, _set_hover_progress, None, "", user=True)
    icon_rotation = Property(float, _get_icon_rotation,
                             _set_icon_rotation, None, "", user=True)

    def setTitle(self, title: str):
        """Set accordion item title"""
        self._title = title
        self._title_label.setText(title)

    def title(self) -> str:
        """Get accordion item title"""
        return self._title

    def setContentWidget(self, widget: QWidget):
        """Set content widget"""
        # Clear existing content
        for i in reversed(range(self._content_layout.count())):
            child = self._content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Add new content
        self._content_layout.addWidget(widget)

        # Calculate content height
        widget.adjustSize()
        self._content_height = widget.sizeHint().height() + 32  # Add margins

    def contentWidget(self) -> Optional[QWidget]:
        """Get content widget"""
        if self._content_layout.count() > 0:
            return self._content_layout.itemAt(0).widget()
        return None

    def setExpanded(self, expanded: bool, animate: bool = True):
        """Set expanded state"""
        if self._is_expanded == expanded:
            return

        self._is_expanded = expanded
        self._update_icon()

        if animate:
            start_value = self._expand_progress
            end_value = 1.0 if expanded else 0.0

            self._expand_animation.setStartValue(start_value)
            self._expand_animation.setEndValue(end_value)

            if expanded:
                self._content_container.setVisible(True)

            self._expand_animation.start()
        else:
            self._expand_progress = 1.0 if expanded else 0.0
            self._content_container.setVisible(expanded)
            if expanded and self._content_height > 0:
                self._content_container.setFixedHeight(self._content_height)
            else:
                self._content_container.setFixedHeight(0)

        self.expanded.emit(expanded)

    def isExpanded(self) -> bool:
        """Check if item is expanded"""
        return self._is_expanded

    def toggle(self, animate: bool = True):
        """Toggle expanded state"""
        self.setExpanded(not self._is_expanded, animate)

    def _on_header_clicked(self, _):
        """Handle header click"""
        self.toggle()
        self.clicked.emit()

    def _on_header_enter(self, _):
        """Handle mouse enter header"""
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()

    def _on_header_leave(self, _):
        """Handle mouse leave header"""
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()

    def _on_expand_finished(self):
        """Handle expand animation finished"""
        if not self._is_expanded:
            self._content_container.setVisible(False)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self._update_icon()


class FluentAccordion(QWidget):
    """Fluent Design accordion widget with multiple expandable items"""

    # Signals
    item_expanded = Signal(int, bool)  # index, expanded
    item_clicked = Signal(int)  # index

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items: List[FluentAccordionItem] = []
        self._allow_multiple = True
        self._animate_transitions = True

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(1)  # Small gap between items

        # Add stretch at the end
        self._layout.addStretch()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentAccordion {{
                background-color: {theme.get_color('background').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def addItem(self, title: str, content_widget: Optional[QWidget] = None) -> int:
        """Add accordion item

        Args:
            title: Item title
            content_widget: Content widget

        Returns:
            Index of added item
        """
        item = FluentAccordionItem(title, content_widget, self)

        # Connect signals
        item.expanded.connect(lambda expanded, idx=len(
            self._items): self._on_item_expanded(idx, expanded))
        item.clicked.connect(lambda idx=len(self._items)
                             : self._on_item_clicked(idx))

        # Insert before stretch
        self._layout.insertWidget(len(self._items), item)
        self._items.append(item)

        return len(self._items) - 1

    def insertItem(self, index: int, title: str, content_widget: Optional[QWidget] = None):
        """Insert accordion item at index"""
        if not 0 <= index <= len(self._items):
            return

        item = FluentAccordionItem(title, content_widget, self)

        # Connect signals
        item.expanded.connect(
            lambda expanded, idx=index: self._on_item_expanded(idx, expanded))
        item.clicked.connect(lambda idx=index: self._on_item_clicked(idx))

        self._layout.insertWidget(index, item)
        self._items.insert(index, item)

        # Update signal connections for items after the inserted one
        for i in range(index + 1, len(self._items)):
            self._items[i].expanded.disconnect()
            self._items[i].clicked.disconnect()
            self._items[i].expanded.connect(
                lambda expanded, idx=i: self._on_item_expanded(idx, expanded))
            self._items[i].clicked.connect(
                lambda idx=i: self._on_item_clicked(idx))

    def removeItem(self, index: int):
        """Remove item at index"""
        if not 0 <= index < len(self._items):
            return

        item = self._items.pop(index)
        item.setParent(None)

        # Update signal connections
        for i in range(index, len(self._items)):
            self._items[i].expanded.disconnect()
            self._items[i].clicked.disconnect()
            self._items[i].expanded.connect(
                lambda expanded, idx=i: self._on_item_expanded(idx, expanded))
            self._items[i].clicked.connect(
                lambda idx=i: self._on_item_clicked(idx))

    def item(self, index: int) -> Optional[FluentAccordionItem]:
        """Get item at index"""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def itemCount(self) -> int:
        """Get item count"""
        return len(self._items)

    def setItemExpanded(self, index: int, expanded: bool):
        """Set item expanded state"""
        if 0 <= index < len(self._items):
            self._items[index].setExpanded(expanded, self._animate_transitions)

    def isItemExpanded(self, index: int) -> bool:
        """Check if item is expanded"""
        if 0 <= index < len(self._items):
            return self._items[index].isExpanded()
        return False

    def setAllowMultipleExpanded(self, allow: bool):
        """Set whether multiple items can be expanded simultaneously"""
        self._allow_multiple = allow

    def allowMultipleExpanded(self) -> bool:
        """Check if multiple items can be expanded"""
        return self._allow_multiple

    def setAnimateTransitions(self, animate: bool):
        """Set whether to animate transitions"""
        self._animate_transitions = animate

    def animateTransitions(self) -> bool:
        """Check if transitions are animated"""
        return self._animate_transitions

    def expandAll(self):
        """Expand all items"""
        for item in self._items:
            item.setExpanded(True, self._animate_transitions)

    def collapseAll(self):
        """Collapse all items"""
        for item in self._items:
            item.setExpanded(False, self._animate_transitions)

    def _on_item_expanded(self, index: int, expanded: bool):
        """Handle item expanded"""
        if expanded and not self._allow_multiple:
            # Collapse other items
            for i, item in enumerate(self._items):
                if i != index and item.isExpanded():
                    item.setExpanded(False, self._animate_transitions)

        self.item_expanded.emit(index, expanded)

    def _on_item_clicked(self, index: int):
        """Handle item clicked"""
        self.item_clicked.emit(index)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
