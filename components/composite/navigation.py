"""
Composite Navigation Components

This module provides higher-level navigation components that combine multiple
basic widgets into common navigation patterns.
"""

from typing import Optional, Dict, Any, List
from PySide6.QtWidgets import (QWidget, QLabel, QSizePolicy,
                               QFrame, QScrollArea, QVBoxLayout, QHBoxLayout)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QByteArray
from PySide6.QtGui import QFont

from ...core.enhanced_base import (FluentStandardButton,
                                   FluentLayoutBuilder, FluentCompositeWidget)
from ...core.animation import FluentAnimation
from ..basic.textbox import FluentLineEdit


class FluentSidebar(FluentCompositeWidget):
    """
    Enhanced sidebar navigation component with collapsible sections,
    search functionality, and smooth animations.
    """

    item_selected = Signal(str)  # item_id
    section_toggled = Signal(str, bool)  # section_id, expanded

    def __init__(self,
                 width: int = 250,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._width = width
        self._collapsed_width = 50
        self._is_collapsed = False
        self._navigation_items: Dict[str, Dict[str, Any]] = {}
        self._sections: Dict[str, Dict[str, Any]] = {}
        self._main_layout: Optional[QVBoxLayout] = None

        self.setFixedWidth(width)
        self._setup_sidebar_ui()

    def _setup_sidebar_ui(self):
        """Setup sidebar-specific UI"""
        self._main_layout = FluentLayoutBuilder.create_vertical_layout()
        self.setLayout(self._main_layout)

        self._setup_search_section()
        self._setup_navigation_area()
        self._setup_footer_actions()
        # Add stretch to main layout to push footer down if content is less
        self._main_layout.addStretch(1)

    def _setup_search_section(self):
        """Setup search functionality"""
        search_frame = QFrame()
        search_layout = FluentLayoutBuilder.create_vertical_layout(spacing=8)
        search_frame.setLayout(search_layout)

        self.search_box = FluentLineEdit()
        self.search_box.setPlaceholderText("Search navigation...")
        self.search_box.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_box)

        if self._main_layout:
            self._main_layout.addWidget(search_frame)

    def _setup_navigation_area(self):
        """Setup scrollable navigation area"""
        self.nav_scroll = QScrollArea()
        self.nav_scroll.setWidgetResizable(True)
        self.nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.nav_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Make scroll area take available space
        self.nav_scroll.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self.nav_widget = QWidget()
        self.nav_layout = FluentLayoutBuilder.create_vertical_layout(spacing=4)
        self.nav_widget.setLayout(self.nav_layout)

        self.nav_scroll.setWidget(self.nav_widget)
        if self._main_layout:
            self._main_layout.addWidget(self.nav_scroll)

        # Add stretch to push items to top inside the scroll area
        self.nav_layout.addStretch()

    def _setup_footer_actions(self):
        """Setup footer action buttons"""
        footer_frame = QFrame()
        footer_layout = FluentLayoutBuilder.create_vertical_layout(spacing=4)
        footer_frame.setLayout(footer_layout)

        self.collapse_button = FluentStandardButton("☰", size=(40, 32))
        self.collapse_button.clicked.connect(self._toggle_collapse)
        footer_layout.addWidget(self.collapse_button)

        if self._main_layout:
            # Footer should not stretch, so add it before the main layout's stretch
            # Or ensure main_layout has nav_scroll as expanding and footer as fixed.
            # Current _setup_sidebar_ui adds stretch last, which is fine.
            self._main_layout.addWidget(footer_frame)

    def add_navigation_section(self, section_id: str, title: str,
                               collapsible: bool = True) -> QWidget:
        """Add a navigation section"""
        section_frame = QFrame()
        section_layout = FluentLayoutBuilder.create_vertical_layout(spacing=2)
        section_frame.setLayout(section_layout)

        header_button = FluentStandardButton(title, size=(None, 36))
        header_button.setCheckable(collapsible)
        if collapsible:
            header_button.clicked.connect(
                lambda: self._toggle_section(section_id))

        section_layout.addWidget(header_button)

        content_widget = QWidget()
        content_layout = FluentLayoutBuilder.create_vertical_layout(spacing=2)
        content_widget.setLayout(content_layout)
        section_layout.addWidget(content_widget)
        if not collapsible or (collapsible and self._sections.get(section_id, {}).get('expanded', True)):
            pass  # Visible by default if expanded or not collapsible
        else:
            content_widget.setVisible(False)

        self._sections[section_id] = {
            'frame': section_frame,
            'header': header_button,
            'content': content_widget,
            'content_layout': content_layout,
            'expanded': True,
            'items': []
        }

        layout = self.nav_layout
        layout.insertWidget(layout.count() - 1, section_frame)

        return content_widget

    def add_navigation_item(self, section_id: str, item_id: str,
                            title: str,
                            badge_text: str = "") -> FluentStandardButton:
        """Add navigation item to section"""
        if section_id not in self._sections:
            raise ValueError(f"Section '{section_id}' not found")

        section = self._sections[section_id]

        item_button = FluentStandardButton(title, size=(None, 32))
        item_button.setCheckable(True)
        item_button.clicked.connect(lambda: self._on_item_selected(item_id))

        if badge_text:
            item_button.setText(f"{title} ({badge_text})")

        section['content_layout'].addWidget(item_button)
        section['items'].append({
            'id': item_id,
            'button': item_button,
            'title': title,
            'section': section_id
        })

        self._navigation_items[item_id] = {
            'button': item_button,
            'title': title,
            'section_id': section_id,
            'badge_text': badge_text
        }

        return item_button

    def _toggle_section(self, section_id: str):
        """Toggle section expansion"""
        if section_id not in self._sections:
            return

        section = self._sections[section_id]
        expanded = not section['expanded']
        content_widget = section['content']

        if expanded:
            content_widget.setVisible(True)
            fade_in_anim = FluentAnimation.fade_in(content_widget)
            if fade_in_anim:
                fade_in_anim.start()
        else:
            fade_out_anim = FluentAnimation.fade_out(content_widget)
            if fade_out_anim:
                fade_out_anim.finished.connect(
                    lambda: content_widget.setVisible(False))
                fade_out_anim.start()
            else:
                content_widget.setVisible(False)

        section['expanded'] = expanded
        self.section_toggled.emit(section_id, expanded)

    def _toggle_collapse(self):
        """Toggle sidebar collapse state"""
        self._is_collapsed = not self._is_collapsed
        target_width = self._collapsed_width if self._is_collapsed else self._width

        current_actual_width = self.width()
        if hasattr(self, "_width_anim_group") and self._width_anim_group.state() == QPropertyAnimation.State.Running:
            self._width_anim_group.stop()
            # Re-read width if animation was stopped mid-way
            current_actual_width = self.width()

        if not hasattr(self, "_width_anim_group"):
            self._min_width_anim = QPropertyAnimation(
                self, QByteArray(b"minimumWidth"))
            self._min_width_anim.setDuration(300)
            self._min_width_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

            self._max_width_anim = QPropertyAnimation(
                self, QByteArray(b"maximumWidth"))
            self._max_width_anim.setDuration(300)
            self._max_width_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

            self._width_anim_group = QParallelAnimationGroup(self)
            self._width_anim_group.addAnimation(self._min_width_anim)
            self._width_anim_group.addAnimation(self._max_width_anim)

        self._min_width_anim.setStartValue(current_actual_width)
        self._min_width_anim.setEndValue(target_width)

        self._max_width_anim.setStartValue(current_actual_width)
        self._max_width_anim.setEndValue(target_width)

        self._width_anim_group.start()

        self.search_box.setVisible(not self._is_collapsed)

        for section_data in self._sections.values():
            for item in section_data['items']:
                button = item['button']
                original_text = item['title']
                # Assuming icon is part of FluentStandardButton and handles visibility
                if self._is_collapsed:
                    button.setText("")  # Show only icon
                else:
                    button.setText(original_text)

    def _on_item_selected(self, item_id: str):
        """Handle navigation item selection"""
        for other_id, item_data in self._navigation_items.items():
            if other_id != item_id:
                item_data['button'].setChecked(False)

        if item_id in self._navigation_items:
            self._navigation_items[item_id]['button'].setChecked(True)

        self.item_selected.emit(item_id)

    def _on_search_changed(self, text: str):
        """Handle search text change"""
        text_lower = text.lower()
        for _, item_data in self._navigation_items.items():  # item_id changed to _
            button = item_data['button']
            title = item_data['title'].lower()
            visible = not text or text_lower in title
            button.setVisible(visible)

    def set_selected_item(self, item_id: str):
        """Programmatically select navigation item"""
        self._on_item_selected(item_id)


class FluentHeaderNavigation(FluentCompositeWidget):
    """
    Horizontal header navigation bar with breadcrumbs, actions, and user profile.
    """
    action_triggered = Signal(str)
    profile_clicked = Signal()

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._actions: List[Dict[str, Any]] = []
        self._breadcrumbs: List[str] = []
        self._main_layout: Optional[QHBoxLayout] = None
        self.setFixedHeight(60)
        self._setup_header_ui(title)

    def _setup_header_ui(self, title: str):
        """Setup header navigation UI"""
        self._main_layout = FluentLayoutBuilder.create_horizontal_layout(
            spacing=16)
        self.setLayout(self._main_layout)
        self._setup_left_section(title)
        # Add stretch to push center/right sections
        self._main_layout.addStretch(1)
        self._setup_center_section()
        self._setup_right_section()

    def _setup_left_section(self, title: str):
        """Setup left section with title and breadcrumbs"""
        left_frame = QFrame()
        left_layout = FluentLayoutBuilder.create_horizontal_layout(spacing=8)
        left_frame.setLayout(left_layout)

        if title:
            self.title_label = QLabel(title)
            self.title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            left_layout.addWidget(self.title_label)

        self.breadcrumb_widget = QWidget()
        self.breadcrumb_layout = FluentLayoutBuilder.create_horizontal_layout(
            spacing=4)
        self.breadcrumb_widget.setLayout(self.breadcrumb_layout)
        left_layout.addWidget(self.breadcrumb_widget)

        if self._main_layout:
            self._main_layout.addWidget(left_frame)

    def _setup_center_section(self):
        """Setup center section with search"""
        self.search_box = FluentLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.setMaximumWidth(300)
        self.search_box.setVisible(False)
        if self._main_layout:
            self._main_layout.addWidget(self.search_box)

    def _setup_right_section(self):
        """Setup right section with actions and profile"""
        right_frame = QFrame()
        right_layout = FluentLayoutBuilder.create_horizontal_layout(spacing=8)
        right_frame.setLayout(right_layout)

        self.actions_widget = QWidget()
        self.actions_layout = FluentLayoutBuilder.create_horizontal_layout(
            spacing=4)
        self.actions_widget.setLayout(self.actions_layout)
        right_layout.addWidget(self.actions_widget)

        self.profile_button = FluentStandardButton("👤", size=(40, 40))
        self.profile_button.clicked.connect(self.profile_clicked.emit)
        right_layout.addWidget(self.profile_button)
        if self._main_layout:
            self._main_layout.addWidget(right_frame)

    def add_action(self, action_id: str, title: str,
                   tooltip: str = "") -> FluentStandardButton:
        """Add action button to header"""
        action_button = FluentStandardButton(title, size=(None, 36))
        action_button.clicked.connect(
            lambda: self.action_triggered.emit(action_id))
        if tooltip:
            action_button.setToolTip(tooltip)
        self.actions_layout.addWidget(action_button)
        self._actions.append(
            {'id': action_id, 'button': action_button, 'title': title})
        return action_button

    def set_breadcrumbs(self, breadcrumbs: List[str]):
        """Set breadcrumb navigation"""
        while self.breadcrumb_layout.count():
            item = self.breadcrumb_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self._breadcrumbs = breadcrumbs
        for i, crumb in enumerate(breadcrumbs):
            if i > 0:
                separator = QLabel(" > ")
                separator.setFont(QFont("Segoe UI", 10))
                self.breadcrumb_layout.addWidget(separator)
            crumb_button = FluentStandardButton(crumb, size=(None, 24))
            crumb_button.clicked.connect(
                lambda _, idx=i: self._on_breadcrumb_clicked(idx))
            self.breadcrumb_layout.addWidget(crumb_button)

    def _on_breadcrumb_clicked(self, index: int):
        """Handle breadcrumb click"""
        if index < len(self._breadcrumbs):
            pass  # Placeholder for navigation logic

    def show_search(self, visible: bool = True):
        """Show/hide search box"""
        self.search_box.setVisible(visible)


class FluentBreadcrumbBar(FluentCompositeWidget):
    """
    Standalone breadcrumb navigation bar with animations and overflow handling.
    """
    breadcrumb_clicked = Signal(int, str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._breadcrumbs: List[str] = []
        self._buttons: List[FluentStandardButton] = []
        self._main_layout: Optional[QHBoxLayout] = None
        self.setFixedHeight(40)
        self._setup_breadcrumb_ui()

    def _setup_breadcrumb_ui(self):
        """Setup breadcrumb UI"""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.breadcrumb_widget = QWidget()
        self.breadcrumb_layout = FluentLayoutBuilder.create_horizontal_layout(
            spacing=4)
        self.breadcrumb_widget.setLayout(self.breadcrumb_layout)
        self.scroll_area.setWidget(self.breadcrumb_widget)

        self._main_layout = FluentLayoutBuilder.create_horizontal_layout()
        self.setLayout(self._main_layout)
        self._main_layout.addWidget(self.scroll_area)
        self.breadcrumb_layout.addStretch()

    def set_breadcrumbs(self, breadcrumbs: List[str], animate: bool = True):
        """Set breadcrumb path with optional animation"""
        old_count = len(self._breadcrumbs)
        self._breadcrumbs = breadcrumbs.copy()

        for button in self._buttons:
            button.deleteLater()
        self._buttons.clear()

        while self.breadcrumb_layout.count() > 1:  # Keep stretch
            item = self.breadcrumb_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        for i, crumb in enumerate(breadcrumbs):
            if i > 0:
                separator = QLabel(" / ")
                separator.setFont(QFont("Segoe UI", 10))
                separator.setStyleSheet("color: #999;")
                self.breadcrumb_layout.insertWidget(
                    self.breadcrumb_layout.count() - 1, separator)

            button = FluentStandardButton(crumb, size=(None, 28))
            button.clicked.connect(
                lambda _, idx=i: self._on_breadcrumb_clicked(idx))
            if i == len(breadcrumbs) - 1:
                button.setStyleSheet("font-weight: bold;")
            else:
                button.setStyleSheet("text-decoration: underline;")
            self._buttons.append(button)
            self.breadcrumb_layout.insertWidget(
                self.breadcrumb_layout.count() - 1, button)

        if animate and len(breadcrumbs) > old_count:
            for i in range(old_count, len(breadcrumbs)):
                if i < len(self._buttons):
                    fade_in_anim = FluentAnimation.fade_in(self._buttons[i])
                    if fade_in_anim:
                        fade_in_anim.start()

    def _on_breadcrumb_clicked(self, index: int):
        """Handle breadcrumb click"""
        if index < len(self._breadcrumbs):
            self.breadcrumb_clicked.emit(index, self._breadcrumbs[index])

    def get_breadcrumbs(self) -> List[str]:
        """Get current breadcrumbs"""
        return self._breadcrumbs.copy()

    def add_breadcrumb(self, text: str, animate: bool = True):
        """Add a new breadcrumb to the end"""
        new_breadcrumbs = self._breadcrumbs + [text]
        self.set_breadcrumbs(new_breadcrumbs, animate)

    def pop_breadcrumb(self, animate: bool = True):
        """Remove the last breadcrumb"""
        if self._breadcrumbs:
            new_breadcrumbs = self._breadcrumbs[:-1]
            self.set_breadcrumbs(new_breadcrumbs, animate)

    def clear_breadcrumbs(self):
        """Clear all breadcrumbs"""
        self.set_breadcrumbs([], animate=False)
