"""
Composite Navigation Components

This module provides higher-level navigation components that combine multiple
basic widgets into common navigation patterns.
"""

from typing import Optional, Dict, Any, List, Callable, Union, Tuple
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QFrame, QScrollArea, QStackedWidget, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QPainter, QColor

from ...core.enhanced_base import (FluentStandardButton,
                                   FluentLayoutBuilder, FluentCompositeWidget,
                                   FluentFormGroup)
from ...core.animation import FluentAnimation
from ..basic.button import FluentButton
from ..basic.textbox import FluentLineEdit


class FluentSidebar(FluentCompositeWidget):
    """
    Enhanced sidebar navigation component with collapsible sections,
    search functionality, and smooth animations.
    """

    item_selected = Signal(str)  # item_id
    section_toggled = Signal(str, bool)  # section_id, expanded

    def __init__(self, title: str = "Navigation",
                 collapsible: bool = True,
                 width: int = 250,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._width = width
        self._collapsed_width = 50
        self._is_collapsed = False
        self._navigation_items: Dict[str, Dict[str, Any]] = {}
        self._sections: Dict[str, Dict[str, Any]] = {}

        self.setFixedWidth(width)
        self._setup_sidebar_ui()

    def _setup_sidebar_ui(self):
        """Setup sidebar-specific UI"""
        layout = FluentLayoutBuilder.create_vertical_layout()
        self.setLayout(layout)

        # Search section (if not collapsed)
        self._setup_search_section()

        # Navigation items container
        self._setup_navigation_area()

        # Footer actions
        self._setup_footer_actions()

    def _setup_search_section(self):
        """Setup search functionality"""
        search_frame = QFrame()
        search_layout = FluentLayoutBuilder.create_vertical_layout(spacing=8)
        search_frame.setLayout(search_layout)

        self.search_box = FluentLineEdit()
        self.search_box.setPlaceholderText("Search navigation...")
        self.search_box.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_box)

        self.layout().addWidget(search_frame)

    def _setup_navigation_area(self):
        """Setup scrollable navigation area"""
        self.nav_scroll = QScrollArea()
        self.nav_scroll.setWidgetResizable(True)
        self.nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.nav_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.nav_widget = QWidget()
        self.nav_layout = FluentLayoutBuilder.create_vertical_layout(spacing=4)
        self.nav_widget.setLayout(self.nav_layout)

        self.nav_scroll.setWidget(self.nav_widget)
        self.layout().addWidget(self.nav_scroll)

        # Add stretch to push items to top
        self.nav_layout.addStretch()

    def _setup_footer_actions(self):
        """Setup footer action buttons"""
        footer_frame = QFrame()
        footer_layout = FluentLayoutBuilder.create_vertical_layout(spacing=4)
        footer_frame.setLayout(footer_layout)

        # Collapse toggle button
        self.collapse_button = FluentStandardButton("☰", size=(40, 32))
        self.collapse_button.clicked.connect(self._toggle_collapse)
        footer_layout.addWidget(self.collapse_button)

        self.layout().addWidget(footer_frame)

    def add_navigation_section(self, section_id: str, title: str,
                               icon: Optional[QIcon] = None,
                               collapsible: bool = True) -> QWidget:
        """Add a navigation section"""
        section_frame = QFrame()
        section_layout = FluentLayoutBuilder.create_vertical_layout(spacing=2)
        section_frame.setLayout(section_layout)

        # Section header
        header_button = FluentStandardButton(title, size=(None, 36))
        header_button.setCheckable(collapsible)
        if collapsible:
            header_button.clicked.connect(
                lambda: self._toggle_section(section_id))

        section_layout.addWidget(header_button)

        # Section content container
        content_widget = QWidget()
        content_layout = FluentLayoutBuilder.create_vertical_layout(spacing=2)
        content_widget.setLayout(content_layout)
        section_layout.addWidget(content_widget)

        # Store section info
        self._sections[section_id] = {
            'frame': section_frame,
            'header': header_button,
            'content': content_widget,
            'content_layout': content_layout,
            'expanded': True,
            'items': []
        }

        # Insert before stretch
        layout = self.nav_layout
        layout.insertWidget(layout.count() - 1, section_frame)

        return content_widget

    def add_navigation_item(self, section_id: str, item_id: str,
                            title: str, icon: Optional[QIcon] = None,
                            badge_text: str = "") -> FluentStandardButton:
        """Add navigation item to section"""
        if section_id not in self._sections:
            raise ValueError(f"Section '{section_id}' not found")

        section = self._sections[section_id]

        # Create navigation item button
        item_button = FluentStandardButton(title, size=(None, 32))
        item_button.setCheckable(True)
        item_button.clicked.connect(lambda: self._on_item_selected(item_id))

        # Add badge if provided
        if badge_text:
            item_button.setText(f"{title} ({badge_text})")

        # Add to section
        section['content_layout'].addWidget(item_button)
        section['items'].append({
            'id': item_id,
            'button': item_button,
            'title': title,
            'section': section_id
        })

        # Store in navigation items
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

        # Animate section content
        content_widget = section['content']

        if expanded:
            # Expand with fade in
            content_widget.setVisible(True)
            fade_in = FluentAnimation.fade_in(content_widget)
            fade_in.start()
        else:
            # Collapse with fade out
            fade_out = FluentAnimation.fade_out(content_widget)
            fade_out.finished.connect(lambda: content_widget.setVisible(False))
            fade_out.start()

        section['expanded'] = expanded
        self.section_toggled.emit(section_id, expanded)

    def _toggle_collapse(self):
        """Toggle sidebar collapse state"""
        self._is_collapsed = not self._is_collapsed

        target_width = self._collapsed_width if self._is_collapsed else self._width

        # Animate width change
        width_animation = FluentAnimation.slide_horizontal(
            self, target_width, duration=300)
        width_animation.start()

        # Hide/show text elements
        self.search_box.setVisible(not self._is_collapsed)

        # Update button text visibility
        for section in self._sections.values():
            for item in section['items']:
                button = item['button']
                if self._is_collapsed:
                    button.setText("")
                else:
                    button.setText(item['title'])

    def _on_item_selected(self, item_id: str):
        """Handle navigation item selection"""
        # Uncheck all other items
        for other_id, item_data in self._navigation_items.items():
            if other_id != item_id:
                item_data['button'].setChecked(False)

        # Check selected item
        if item_id in self._navigation_items:
            self._navigation_items[item_id]['button'].setChecked(True)

        self.item_selected.emit(item_id)

    def _on_search_changed(self, text: str):
        """Handle search text change"""
        text_lower = text.lower()

        for item_id, item_data in self._navigation_items.items():
            button = item_data['button']
            title = item_data['title'].lower()

            # Show/hide based on search
            visible = not text or text_lower in title
            button.setVisible(visible)

    def set_selected_item(self, item_id: str):
        """Programmatically select navigation item"""
        self._on_item_selected(item_id)


class FluentHeaderNavigation(FluentCompositeWidget):
    """
    Horizontal header navigation bar with breadcrumbs, actions, and user profile.
    """

    action_triggered = Signal(str)  # action_id
    profile_clicked = Signal()

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._actions: List[Dict[str, Any]] = []
        self._breadcrumbs: List[str] = []

        self.setFixedHeight(60)
        self._setup_header_ui(title)

    def _setup_header_ui(self, title: str):
        """Setup header navigation UI"""
        layout = FluentLayoutBuilder.create_horizontal_layout(spacing=16)
        self.setLayout(layout)

        # Left section: Logo/Title and breadcrumbs
        self._setup_left_section(title)

        # Center: Search (optional)
        self._setup_center_section()

        # Right section: Actions and profile
        self._setup_right_section()

    def _setup_left_section(self, title: str):
        """Setup left section with title and breadcrumbs"""
        left_frame = QFrame()
        left_layout = FluentLayoutBuilder.create_horizontal_layout(spacing=8)
        left_frame.setLayout(left_layout)

        # Title
        if title:
            self.title_label = QLabel(title)
            self.title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            left_layout.addWidget(self.title_label)

        # Breadcrumbs container
        self.breadcrumb_widget = QWidget()
        self.breadcrumb_layout = FluentLayoutBuilder.create_horizontal_layout(
            spacing=4)
        self.breadcrumb_widget.setLayout(self.breadcrumb_layout)
        left_layout.addWidget(self.breadcrumb_widget)

        self.layout().addWidget(left_frame)

    def _setup_center_section(self):
        """Setup center section with search"""
        # Optional search box
        self.search_box = FluentLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.setMaximumWidth(300)
        self.search_box.setVisible(False)  # Hidden by default

        self.layout().addWidget(self.search_box)

    def _setup_right_section(self):
        """Setup right section with actions and profile"""
        right_frame = QFrame()
        right_layout = FluentLayoutBuilder.create_horizontal_layout(spacing=8)
        right_frame.setLayout(right_layout)

        # Actions container
        self.actions_widget = QWidget()
        self.actions_layout = FluentLayoutBuilder.create_horizontal_layout(
            spacing=4)
        self.actions_widget.setLayout(self.actions_layout)
        right_layout.addWidget(self.actions_widget)

        # Profile button
        self.profile_button = FluentStandardButton("👤", size=(40, 40))
        self.profile_button.clicked.connect(self.profile_clicked.emit)
        right_layout.addWidget(self.profile_button)

        self.layout().addWidget(right_frame)

    def add_action(self, action_id: str, title: str,
                   icon: Optional[QIcon] = None,
                   tooltip: str = "") -> FluentStandardButton:
        """Add action button to header"""
        action_button = FluentStandardButton(title, size=(None, 36))
        action_button.clicked.connect(
            lambda: self.action_triggered.emit(action_id))

        if tooltip:
            action_button.setToolTip(tooltip)

        self.actions_layout.addWidget(action_button)

        self._actions.append({
            'id': action_id,
            'button': action_button,
            'title': title
        })

        return action_button

    def set_breadcrumbs(self, breadcrumbs: List[str]):
        """Set breadcrumb navigation"""
        # Clear existing breadcrumbs
        while self.breadcrumb_layout.count():
            item = self.breadcrumb_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        self._breadcrumbs = breadcrumbs

        # Add new breadcrumbs
        for i, crumb in enumerate(breadcrumbs):
            if i > 0:
                # Add separator
                separator = QLabel(" > ")
                separator.setFont(QFont("Segoe UI", 10))
                self.breadcrumb_layout.addWidget(separator)

            # Add breadcrumb button
            crumb_button = FluentStandardButton(crumb, size=(None, 24))
            crumb_button.clicked.connect(
                lambda _, idx=i: self._on_breadcrumb_clicked(idx))
            self.breadcrumb_layout.addWidget(crumb_button)

    def _on_breadcrumb_clicked(self, index: int):
        """Handle breadcrumb click"""
        # Emit navigation to breadcrumb level
        if index < len(self._breadcrumbs):
            # You could emit a signal here for breadcrumb navigation
            pass

    def show_search(self, visible: bool = True):
        """Show/hide search box"""
        self.search_box.setVisible(visible)


class FluentBreadcrumbBar(FluentCompositeWidget):
    """
    Standalone breadcrumb navigation bar with animations and overflow handling.
    """

    breadcrumb_clicked = Signal(int, str)  # index, text

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._breadcrumbs: List[str] = []
        self._buttons: List[FluentStandardButton] = []

        self.setFixedHeight(40)
        self._setup_breadcrumb_ui()

    def _setup_breadcrumb_ui(self):
        """Setup breadcrumb UI"""
        # Use scroll area for overflow handling
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

        # Main layout
        layout = FluentLayoutBuilder.create_horizontal_layout()
        self.setLayout(layout)
        layout.addWidget(self.scroll_area)

        # Add stretch to push breadcrumbs to left
        self.breadcrumb_layout.addStretch()

    def set_breadcrumbs(self, breadcrumbs: List[str], animate: bool = True):
        """Set breadcrumb path with optional animation"""
        old_count = len(self._breadcrumbs)
        self._breadcrumbs = breadcrumbs.copy()

        # Clear existing buttons
        for button in self._buttons:
            button.deleteLater()
        self._buttons.clear()

        # Clear layout
        while self.breadcrumb_layout.count() > 1:  # Keep stretch
            item = self.breadcrumb_layout.takeAt(0)

        # Add new breadcrumbs
        for i, crumb in enumerate(breadcrumbs):
            if i > 0:
                # Add separator
                separator = QLabel(" / ")
                separator.setFont(QFont("Segoe UI", 10))
                separator.setStyleSheet("color: #999;")
                self.breadcrumb_layout.insertWidget(
                    self.breadcrumb_layout.count() - 1, separator)

            # Add breadcrumb button
            button = FluentStandardButton(crumb, size=(None, 28))
            button.clicked.connect(
                lambda _, idx=i: self._on_breadcrumb_clicked(idx))

            # Style the button based on position
            if i == len(breadcrumbs) - 1:
                # Current/last breadcrumb - bold
                button.setStyleSheet("font-weight: bold;")
            else:
                # Clickable breadcrumb
                button.setStyleSheet("text-decoration: underline;")

            self._buttons.append(button)
            self.breadcrumb_layout.insertWidget(
                self.breadcrumb_layout.count() - 1, button)

        # Animate if requested and breadcrumbs increased
        if animate and len(breadcrumbs) > old_count:
            # Animate the new breadcrumb(s)
            for i in range(old_count, len(breadcrumbs)):
                if i < len(self._buttons):
                    fade_in = FluentAnimation.fade_in(self._buttons[i])
                    fade_in.start()

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
