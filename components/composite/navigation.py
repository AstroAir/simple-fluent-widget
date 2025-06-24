"""
Composite Navigation Components - Optimized for Python 3.11+

This module provides higher-level navigation components that combine multiple
basic widgets into common navigation patterns with modern Python features.

Enhanced with:
- Modern type system with protocols and type aliases
- Dataclasses with slots for memory efficiency
- Advanced animation system
- Performance optimizations and caching
- Comprehensive error handling
"""

from __future__ import annotations
from typing import Any, Callable, TypeVar, TypeAlias, Protocol, Optional, Dict, List, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import lru_cache, partial
from contextlib import contextmanager
import weakref
from collections.abc import Sequence
import time

from PySide6.QtWidgets import (QWidget, QLabel, QSizePolicy,
                               QFrame, QScrollArea, QVBoxLayout, QHBoxLayout,
                               QApplication, QGraphicsOpacityEffect)
from PySide6.QtCore import (Qt, Signal, QPropertyAnimation, QEasingCurve,
                            QParallelAnimationGroup, QByteArray, QTimer, QAbstractAnimation)
from PySide6.QtGui import QFont, QIcon, QPixmap

from core.enhanced_base import (FluentStandardButton,
                                FluentLayoutBuilder, FluentCompositeWidget)
from core.enhanced_animations import FluentTransition, FluentMicroInteraction
from core.theme import theme_manager

# Try to import enhanced components, fallback to basic ones
try:
    from components.basic.textbox import FluentLineEdit
    from components.basic.button import FluentButton
except ImportError:
    from PySide6.QtWidgets import QLineEdit as FluentLineEdit, QPushButton as FluentButton

# Type aliases for better readability
NavigationCallback: TypeAlias = Callable[[str], None]
ItemId: TypeAlias = str
SectionId: TypeAlias = str
BreadcrumbPath: TypeAlias = List[str]

T = TypeVar('T', bound=QWidget)
N = TypeVar('N', bound='FluentSidebar')


# Modern configuration dataclasses with slots for memory efficiency
@dataclass(slots=True, frozen=True)
class NavigationItem:
    """Immutable configuration for navigation items with slots"""
    id: str
    title: str
    icon: Optional[QIcon] = None
    badge_text: str = ""
    tooltip: str = ""
    enabled: bool = True
    callback: Optional[NavigationCallback] = None

    def __post_init__(self):
        if not self.id or not self.title:
            raise ValueError("Navigation item id and title are required")


@dataclass(slots=True, frozen=True)
class NavigationSection:
    """Immutable configuration for navigation sections with slots"""
    id: str
    title: str
    collapsible: bool = True
    expanded: bool = True
    icon: Optional[QIcon] = None
    items: Sequence[NavigationItem] = field(default_factory=list)

    def __post_init__(self):
        if not self.id or not self.title:
            raise ValueError("Navigation section id and title are required")


@dataclass(slots=True)
class HeaderAction:
    """Mutable configuration for header actions with slots"""
    id: str
    title: str
    icon: Optional[QIcon] = None
    tooltip: str = ""
    callback: Optional[NavigationCallback] = None
    variant: str = "secondary"
    enabled: bool = True
    visible: bool = True

    def __post_init__(self):
        if not self.id or not self.title:
            raise ValueError("Header action id and title are required")


@dataclass(slots=True)
class NavigationComponentState:
    """Mutable state container for navigation components"""
    current_item: Optional[str] = None
    collapsed_sections: set[str] = field(default_factory=set)
    search_query: str = ""
    is_collapsed: bool = False
    last_update_time: float = field(default_factory=time.time)


class NavigationMode(Enum):
    """Navigation mode enumeration"""
    NORMAL = auto()
    COLLAPSED = auto()
    HIDDEN = auto()
    LOADING = auto()


class SearchableProtocol(Protocol):
    """Protocol for searchable navigation components"""

    def filter_items(self, query: str) -> None: ...
    def clear_filter(self) -> None: ...


class CacheManager:
    """Optimized cache manager for navigation resources"""

    def __init__(self, max_size: int = 256):
        self._cache: Dict[str, Any] = {}
        self._max_size = max_size

    @lru_cache(maxsize=256)
    def get_cached_style(self, theme_name: str, component_type: str) -> str:
        """Get cached style for component"""
        key = f"{theme_name}_{component_type}"
        return self._cache.get(key, "")

    def set_cached_style(self, theme_name: str, component_type: str, style: str) -> None:
        """Set cached style with size management"""
        if len(self._cache) >= self._max_size:
            # Remove oldest entries
            oldest_keys = list(self._cache.keys())[:self._max_size // 4]
            for key in oldest_keys:
                self._cache.pop(key, None)

        key = f"{theme_name}_{component_type}"
        self._cache[key] = style

    def clear_cache(self) -> None:
        """Clear the cache"""
        self._cache.clear()
        self.get_cached_style.cache_clear()


# Global cache instance
_cache_manager = CacheManager()


class FluentSidebar(FluentCompositeWidget, SearchableProtocol):
    """
    Enhanced sidebar navigation component with collapsible sections,
    search functionality, and smooth animations.

    Optimized with modern Python features, better performance, and type safety.
    """

    item_selected = Signal(str)  # item_id
    section_toggled = Signal(str, bool)  # section_id, expanded
    search_changed = Signal(str)  # query
    state_changed = Signal(object)  # NavigationState

    def __init__(self,
                 width: int = 250,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._width = width
        self._collapsed_width = 50
        self._state = NavigationMode.NORMAL
        self._navigation_items: Dict[str, Dict[str, Any]] = {}
        self._sections: Dict[str, Dict[str, Any]] = {}
        self._section_configs: Dict[str, NavigationSection] = {}
        self._main_layout: Optional[QVBoxLayout] = None
        self._search_debounce_timer = QTimer(self)
        self._weak_refs: List[weakref.ref] = []
        self._current_filter: str = ""

        # Setup debouncing for search
        self._search_debounce_timer.setSingleShot(True)
        self._search_debounce_timer.timeout.connect(self._emit_search_changed)

        self.setFixedWidth(width)
        self._setup_sidebar_ui()
        self._apply_enhanced_styling()

    def _setup_sidebar_ui(self):
        """Setup sidebar-specific UI with enhanced layout"""
        self._main_layout = FluentLayoutBuilder.create_vertical_layout()
        self.setLayout(self._main_layout)

        self._setup_search_section()
        self._setup_navigation_area()
        self._setup_footer_actions()

    def _apply_enhanced_styling(self) -> None:
        """Apply enhanced styling with caching"""
        theme_key = getattr(
            theme_manager, 'get_current_theme_name', lambda: 'default')()
        cached_style = _cache_manager.get_cached_style(theme_key, 'sidebar')

        if not cached_style:
            cached_style = f"""
                FluentSidebar {{
                    background-color: {theme_manager.get_color("surface")};
                    border-right: 1px solid {theme_manager.get_color("border")};
                }}
                QScrollArea {{
                    background-color: transparent;
                    border: none;
                }}
            """
            _cache_manager.set_cached_style(theme_key, 'sidebar', cached_style)

        self.setStyleSheet(cached_style)

    @contextmanager
    def batch_updates(self):
        """Context manager for batching multiple navigation updates"""
        self.setUpdatesEnabled(False)
        try:
            yield
        finally:
            self.setUpdatesEnabled(True)
            self.update()

    def _setup_search_section(self):
        """Setup search functionality with enhanced features"""
        search_frame = QFrame()
        search_layout = FluentLayoutBuilder.create_vertical_layout(spacing=8)
        search_frame.setLayout(search_layout)

        self.search_box = FluentLineEdit()
        self.search_box.setPlaceholderText("Search navigation...")
        self.search_box.textChanged.connect(self._on_search_changed_debounced)

        # Apply enhanced search styling
        self._apply_search_styling()

        search_layout.addWidget(self.search_box)

        if self._main_layout:
            self._main_layout.addWidget(search_frame)

    def _apply_search_styling(self) -> None:
        """Apply enhanced search input styling"""
        self.search_box.setStyleSheet(f"""
            FluentLineEdit {{
                background-color: {theme_manager.get_color("input_background")};
                border: 1px solid {theme_manager.get_color("border")};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                margin: 8px;
            }}
            FluentLineEdit:focus {{
                border-color: {theme_manager.get_color("accent")};
                background-color: {theme_manager.get_color("surface")};
            }}
        """)

    def _setup_navigation_area(self):
        """Setup scrollable navigation area with optimization"""
        self.nav_scroll = QScrollArea()
        self.nav_scroll.setWidgetResizable(True)
        self.nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.nav_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.nav_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.nav_scroll.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self.nav_widget = QWidget()
        self.nav_layout = FluentLayoutBuilder.create_vertical_layout(spacing=4)
        self.nav_widget.setLayout(self.nav_layout)

        self.nav_scroll.setWidget(self.nav_widget)
        if self._main_layout:
            self._main_layout.addWidget(self.nav_scroll)

        # Add stretch to push items to top
        self.nav_layout.addStretch()

    def _setup_footer_actions(self):
        """Setup footer action buttons with enhanced styling"""
        footer_frame = QFrame()
        footer_layout = FluentLayoutBuilder.create_vertical_layout(spacing=4)
        footer_frame.setLayout(footer_layout)

        self.collapse_button = FluentStandardButton(
            "☰",
            size=(40, 32),
            variant=FluentStandardButton.OUTLINE
        )
        self.collapse_button.setToolTip("Toggle sidebar")
        self.collapse_button.clicked.connect(self._toggle_collapse)
        FluentMicroInteraction.button_press(self.collapse_button)

        footer_layout.addWidget(self.collapse_button)

        if self._main_layout:
            self._main_layout.addWidget(footer_frame)

    def add_section_from_config(self, config: NavigationSection) -> QWidget:
        """Add navigation section from configuration object"""
        content_widget = self.add_navigation_section(
            config.id, config.title, config.collapsible
        )

        self._section_configs[config.id] = config

        # Add items from configuration
        with self.batch_updates():
            for item_config in config.items:
                self.add_item_from_config(config.id, item_config)

        # Set initial expansion state
        if not config.expanded and config.collapsible:
            self._toggle_section(config.id)

        return content_widget

    def add_item_from_config(self, section_id: str, config: NavigationItem) -> FluentStandardButton:
        """Add navigation item from configuration object"""
        button = self.add_navigation_item(
            section_id, config.id, config.title, config.badge_text
        )
        if config.icon:
            button.setIcon(config.icon)
        if config.tooltip:
            button.setToolTip(config.tooltip)
        if config.callback:
            button.clicked.connect(
                lambda checked=False, cfg=config: cfg.callback(
                    cfg.id) if cfg.callback else None
            )

        button.setEnabled(config.enabled)

        return button

    def add_navigation_section(self, section_id: str, title: str,
                               collapsible: bool = True) -> QWidget:
        """Add a navigation section with enhanced styling"""
        section_frame = QFrame()
        section_layout = FluentLayoutBuilder.create_vertical_layout(spacing=2)
        section_frame.setLayout(section_layout)

        header_button = FluentStandardButton(title, size=(None, 36))
        header_button.setCheckable(collapsible)

        # Apply section header styling
        self._apply_section_header_styling(header_button, collapsible)

        if collapsible:
            header_button.clicked.connect(
                partial(self._toggle_section, section_id))
            FluentMicroInteraction.button_press(header_button)

        section_layout.addWidget(header_button)

        content_widget = QWidget()
        content_layout = FluentLayoutBuilder.create_vertical_layout(spacing=2)
        content_widget.setLayout(content_layout)
        section_layout.addWidget(content_widget)

        self._sections[section_id] = {
            'frame': section_frame,
            'header': header_button,
            'content': content_widget,
            'content_layout': content_layout,
            'expanded': True,
            'items': [],
            'collapsible': collapsible
        }

        layout = self.nav_layout
        layout.insertWidget(layout.count() - 1, section_frame)

        return content_widget

    def _apply_section_header_styling(self, button: FluentStandardButton, collapsible: bool) -> None:
        """Apply enhanced section header styling"""
        if collapsible:
            button.setStyleSheet(f"""
                FluentStandardButton {{
                    background-color: {theme_manager.get_color("hover")};
                    border: none;
                    border-radius: 6px;
                    text-align: left;
                    padding: 8px 12px;
                    font-weight: bold;
                    color: {theme_manager.get_color("text")};
                }}
                FluentStandardButton:hover {{
                    background-color: {theme_manager.get_color("accent")};
                    color: white;
                }}
                FluentStandardButton:checked {{
                    background-color: {theme_manager.get_color("accent")};
                    color: white;
                }}
            """)
        else:
            button.setStyleSheet(f"""
                FluentStandardButton {{
                    background-color: transparent;
                    border: none;
                    text-align: left;
                    padding: 8px 12px;
                    font-weight: bold;
                    color: {theme_manager.get_color("text")};
                }}
            """)

    def add_navigation_item(self, section_id: str, item_id: str,
                            title: str, badge_text: str = "") -> FluentStandardButton:
        """Add navigation item to section with enhanced configuration"""
        if section_id not in self._sections:
            raise ValueError(f"Section '{section_id}' not found")

        section = self._sections[section_id]

        item_button = FluentStandardButton(title, size=(None, 32))
        item_button.setCheckable(True)
        item_button.clicked.connect(partial(self._on_item_selected, item_id))

        # Apply navigation item styling
        self._apply_nav_item_styling(item_button)

        # Add micro-interaction
        FluentMicroInteraction.button_press(item_button)

        if badge_text:
            item_button.setText(f"{title} ({badge_text})")

        section['content_layout'].addWidget(item_button)

        item_data = {
            'id': item_id,
            'button': item_button,
            'title': title,
            'section': section_id,
            'badge_text': badge_text,
            'visible': True
        }

        section['items'].append(item_data)

        self._navigation_items[item_id] = {
            'button': item_button,
            'title': title,
            'section_id': section_id,
            'badge_text': badge_text,
            'data': item_data
        }

        return item_button

    def _apply_nav_item_styling(self, button: FluentStandardButton) -> None:
        """Apply enhanced navigation item styling"""
        button.setStyleSheet(f"""
            FluentStandardButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                text-align: left;
                padding: 6px 16px;
                color: {theme_manager.get_color("text")};
            }}
            FluentStandardButton:hover {{
                background-color: {theme_manager.get_color("hover")};
            }}
            FluentStandardButton:checked {{
                background-color: {theme_manager.get_color("accent")};
                color: white;
                font-weight: bold;
            }}
        """)

    def _toggle_section(self, section_id: str):
        """Toggle section expansion with enhanced animations"""
        if section_id not in self._sections:
            return

        section = self._sections[section_id]
        expanded = not section['expanded']
        content_widget = section['content']

        if expanded:
            content_widget.setVisible(True)
            # Create fade in animation
            fade_in_anim = FluentTransition.create_transition(
                content_widget, FluentTransition.FADE, duration=200
            )
            if fade_in_anim:
                fade_in_anim.start()
        else:
            # Create fade out animation
            fade_out_anim = FluentTransition.create_transition(
                content_widget, FluentTransition.FADE, duration=200
            )
            if fade_out_anim:
                fade_out_anim.finished.connect(
                    lambda: content_widget.setVisible(False))
                fade_out_anim.start()
            else:
                content_widget.setVisible(False)

        section['expanded'] = expanded
        section['header'].setChecked(expanded)
        self.section_toggled.emit(section_id, expanded)

    def _toggle_collapse(self):
        """Toggle sidebar collapse state with enhanced animation"""
        new_state = NavigationMode.COLLAPSED if self._state == NavigationMode.NORMAL else NavigationMode.NORMAL
        self.set_state(new_state)

    def set_state(self, state: NavigationMode) -> None:
        """Set sidebar state with smooth transitions"""
        if self._state == state:
            return

        old_state = self._state
        self._state = state

        if state == NavigationMode.COLLAPSED:
            target_width = self._collapsed_width
        elif state == NavigationMode.NORMAL:
            target_width = self._width
        elif state == NavigationMode.HIDDEN:
            target_width = 0
        else:
            target_width = self._width

        self._animate_width_change(target_width)
        self._update_content_visibility(state)
        self.state_changed.emit(state)

    def _animate_width_change(self, target_width: int) -> None:
        """Animate width change with enhanced easing"""
        current_width = self.width()

        if hasattr(self, "_width_anim_group") and self._width_anim_group.state() == QPropertyAnimation.State.Running:
            self._width_anim_group.stop()

        if not hasattr(self, "_width_anim_group"):
            self._min_width_anim = QPropertyAnimation(
                self, QByteArray(b"minimumWidth"))
            self._min_width_anim.setDuration(300)
            self._min_width_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            self._max_width_anim = QPropertyAnimation(
                self, QByteArray(b"maximumWidth"))
            self._max_width_anim.setDuration(300)
            self._max_width_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            self._width_anim_group = QParallelAnimationGroup(self)
            self._width_anim_group.addAnimation(self._min_width_anim)
            self._width_anim_group.addAnimation(self._max_width_anim)

        self._min_width_anim.setStartValue(current_width)
        self._min_width_anim.setEndValue(target_width)
        self._max_width_anim.setStartValue(current_width)
        self._max_width_anim.setEndValue(target_width)

        self._width_anim_group.start()

    def _update_content_visibility(self, state: NavigationMode) -> None:
        """Update content visibility based on state"""
        is_collapsed = state == NavigationMode.COLLAPSED
        is_hidden = state == NavigationMode.HIDDEN

        # Update search box visibility
        self.search_box.setVisible(not is_collapsed and not is_hidden)

        # Update navigation item text visibility
        for section_data in self._sections.values():
            for item in section_data['items']:
                button = item['button']
                if is_collapsed:
                    # Show only icon or first letter
                    original_text = item['title']
                    icon = button.icon()
                    if not icon.isNull():
                        button.setText("")  # Show only icon
                    else:
                        button.setText(
                            original_text[0] if original_text else "")
                    button.setToolTip(original_text)
                else:
                    # Show full text
                    title = item['title']
                    badge = item.get('badge_text', '')
                    if badge:
                        button.setText(f"{title} ({badge})")
                    else:
                        button.setText(title)
                    button.setToolTip("")

    def _on_item_selected(self, item_id: str):
        """Handle navigation item selection with enhanced state management"""
        # Clear previous selections
        for other_id, item_data in self._navigation_items.items():
            if other_id != item_id:
                item_data['button'].setChecked(False)

        # Set current selection
        if item_id in self._navigation_items:
            self._navigation_items[item_id]['button'].setChecked(True)

        self.item_selected.emit(item_id)

    def _on_search_changed_debounced(self, text: str):
        """Handle search text change with debouncing"""
        self._current_filter = text
        self._search_debounce_timer.start(300)  # 300ms debounce

    def _emit_search_changed(self):
        """Emit search changed signal after debounce period"""
        self.search_changed.emit(self._current_filter)
        self.filter_items(self._current_filter)

    def filter_items(self, query: str) -> None:
        """Filter navigation items based on search query"""
        query_lower = query.lower().strip()

        for item_id, item_data in self._navigation_items.items():
            button = item_data['button']
            title = item_data['title'].lower()
            section_id = item_data['section_id']

            # Check if item matches query
            is_visible = not query_lower or query_lower in title
            button.setVisible(is_visible)

            # Update item visibility state
            if section_id in self._sections:
                section_items = self._sections[section_id]['items']
                for item in section_items:
                    if item['id'] == item_id:
                        item['visible'] = is_visible
                        break

        # Update section visibility based on item visibility
        self._update_section_visibility()

    def _update_section_visibility(self) -> None:
        """Update section visibility based on item visibility"""
        for section_id, section_data in self._sections.items():
            has_visible_items = any(item['visible']
                                    for item in section_data['items'])
            section_data['frame'].setVisible(has_visible_items)

    def clear_filter(self) -> None:
        """Clear search filter and show all items"""
        self.search_box.clear()
        for item_data in self._navigation_items.values():
            item_data['button'].setVisible(True)
            item_data['data']['visible'] = True

        for section_data in self._sections.values():
            section_data['frame'].setVisible(True)

    def set_selected_item(self, item_id: str) -> bool:
        """Programmatically select navigation item"""
        if item_id in self._navigation_items:
            self._on_item_selected(item_id)
            return True
        return False

    def get_selected_item(self) -> Optional[str]:
        """Get currently selected item ID"""
        for item_id, item_data in self._navigation_items.items():
            if item_data['button'].isChecked():
                return item_id
        return None

    def update_item_badge(self, item_id: str, badge_text: str) -> bool:
        """Update item badge text"""
        if item_id not in self._navigation_items:
            return False

        item_data = self._navigation_items[item_id]
        button = item_data['button']
        title = item_data['title']

        item_data['badge_text'] = badge_text
        item_data['data']['badge_text'] = badge_text

        if self._state != NavigationMode.COLLAPSED:
            if badge_text:
                button.setText(f"{title} ({badge_text})")
            else:
                button.setText(title)

        return True

    def remove_navigation_item(self, item_id: str) -> bool:
        """Remove navigation item"""
        if item_id not in self._navigation_items:
            return False

        item_data = self._navigation_items[item_id]
        section_id = item_data['section_id']
        button = item_data['button']

        # Remove from section
        if section_id in self._sections:
            section = self._sections[section_id]
            section['items'] = [
                item for item in section['items'] if item['id'] != item_id]
            section['content_layout'].removeWidget(button)

        # Remove button
        button.deleteLater()

        # Remove from items dict
        del self._navigation_items[item_id]

        return True

    def remove_navigation_section(self, section_id: str) -> bool:
        """Remove entire navigation section"""
        if section_id not in self._sections:
            return False

        section = self._sections[section_id]

        # Remove all items in section
        for item in section['items']:
            item_id = item['id']
            if item_id in self._navigation_items:
                del self._navigation_items[item_id]

        # Remove section frame
        section['frame'].deleteLater()

        # Remove from sections dict
        del self._sections[section_id]
        if section_id in self._section_configs:
            del self._section_configs[section_id]

        return True

    def get_navigation_items(self) -> Dict[str, str]:
        """Get all navigation items as dict of id -> title"""
        return {
            item_id: item_data['title']
            for item_id, item_data in self._navigation_items.items()
        }

    def get_navigation_sections(self) -> Dict[str, str]:
        """Get all navigation sections as dict of id -> title"""
        return {
            section_id: section_data['header'].text()
            for section_id, section_data in self._sections.items()
        }

    def clear_navigation(self) -> None:
        """Clear all navigation items and sections"""
        with self.batch_updates():
            # Clear all sections (this will also clear items)
            section_ids = list(self._sections.keys())
            for section_id in section_ids:
                self.remove_navigation_section(section_id)

    def get_state(self) -> NavigationMode:
        """Get current sidebar state"""
        return self._state

    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, '_search_debounce_timer'):
                self._search_debounce_timer.stop()
            if hasattr(self, '_width_anim_group'):
                self._width_anim_group.stop()
        except:
            pass  # Ignore cleanup errors


@dataclass
class HeaderConfig:
    """Configuration for header navigation"""
    title: str = ""
    show_breadcrumbs: bool = True
    show_search: bool = False
    show_profile: bool = True
    profile_text: str = "👤"
    profile_tooltip: str = "User Profile"
    actions: List[HeaderAction] = field(default_factory=list)
    search_placeholder: str = "Search..."
    max_search_width: int = 300


class FluentHeaderNavigation(FluentCompositeWidget):
    """
    Modern horizontal header navigation bar with breadcrumbs, actions, and user profile.
    Uses dataclasses for configuration and modern Python patterns.
    """
    action_triggered = Signal(str)
    profile_clicked = Signal()
    search_changed = Signal(str)

    def __init__(self, config: Optional[HeaderConfig] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._config = config or HeaderConfig()
        self._actions: Dict[str, HeaderAction] = {}
        self._action_buttons: Dict[str, FluentStandardButton] = {}
        self._breadcrumbs: List[str] = []
        self._main_layout: Optional[QHBoxLayout] = None

        # Enhanced styling and animations
        self._cache_manager = CacheManager()

        self.setFixedHeight(60)
        self._setup_header_ui()
        self._apply_theme_aware_styling()

    def _setup_header_ui(self):
        """Setup header navigation UI with modern layout"""
        self._main_layout = FluentLayoutBuilder.create_horizontal_layout(
            spacing=16)
        self.setLayout(self._main_layout)

        self._setup_left_section()
        self._main_layout.addStretch(1)
        self._setup_center_section()
        self._setup_right_section()
        # Load actions from config
        for action_config in self._config.actions:
            self.add_action_from_config(action_config)

    def _setup_left_section(self):
        """Setup left section with title and breadcrumbs"""
        left_frame = QFrame()
        left_layout = FluentLayoutBuilder.create_horizontal_layout(spacing=8)
        left_frame.setLayout(left_layout)

        if self._config.title:
            self.title_label = QLabel(self._config.title)
            self.title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            left_layout.addWidget(self.title_label)

        if self._config.show_breadcrumbs:
            self.breadcrumb_widget = QWidget()
            self.breadcrumb_layout = FluentLayoutBuilder.create_horizontal_layout(
                spacing=4)
            self.breadcrumb_widget.setLayout(self.breadcrumb_layout)
            left_layout.addWidget(self.breadcrumb_widget)

        if self._main_layout:
            self._main_layout.addWidget(left_frame)

    def _setup_center_section(self):
        """Setup center section with search"""
        if self._config.show_search:
            self.search_box = FluentLineEdit()
            self.search_box.setPlaceholderText(self._config.search_placeholder)
            self.search_box.setMaximumWidth(self._config.max_search_width)
            self.search_box.textChanged.connect(self.search_changed.emit)
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

        if self._config.show_profile:
            self.profile_button = FluentStandardButton(
                self._config.profile_text, size=(40, 40))
            self.profile_button.setToolTip(self._config.profile_tooltip)
            self.profile_button.clicked.connect(self.profile_clicked.emit)
            right_layout.addWidget(self.profile_button)

        if self._main_layout:
            self._main_layout.addWidget(right_frame)

    def _apply_theme_aware_styling(self):
        """Apply theme-aware styling"""
        try:
            from core.theme import get_theme_manager
            theme = get_theme_manager()
            style = f"""
            FluentHeaderNavigation {{
                background-color: {theme.get_color('surface')};
                border-bottom: 1px solid {theme.get_color('outline')};
            }}
            """
            self.setStyleSheet(style)
        except Exception as e:
            print(f"Header navigation theme styling error: {e}")

    def add_action_from_config(self, config: HeaderAction) -> FluentStandardButton:
        """Add action button from configuration object"""
        action_button = FluentStandardButton(config.title, size=(None, 36))
        if config.icon:
            action_button.setIcon(config.icon)
        if config.tooltip:
            action_button.setToolTip(config.tooltip)
        if config.callback:
            action_button.clicked.connect(lambda checked=False, cfg=config: cfg.callback(
                cfg.id) if cfg.callback else None)
        else:
            action_button.clicked.connect(
                lambda: self.action_triggered.emit(config.id))

        action_button.setEnabled(config.enabled)
        action_button.setVisible(config.visible)

        self.actions_layout.addWidget(action_button)
        self._actions[config.id] = config
        self._action_buttons[config.id] = action_button

        return action_button

    # Legacy method for backward compatibility
    def add_action(self, action_id: str, title: str,
                   tooltip: str = "") -> FluentStandardButton:
        """Add action button to header (legacy method)"""
        action_config = HeaderAction(
            id=action_id, title=title, tooltip=tooltip)
        return self.add_action_from_config(action_config)

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
                lambda _, idx=i: None)  # Placeholder - implement navigation logic
            self.breadcrumb_layout.addWidget(crumb_button)

    def show_search(self, visible: bool = True):
        """Show/hide search box"""
        if hasattr(self, 'search_box'):
            self.search_box.setVisible(visible)


@dataclass
class BreadcrumbConfig:
    """Configuration for breadcrumb bar"""
    separator: str = " / "
    separator_color: str = "#999"
    animate_additions: bool = True
    max_visible_items: int = 10
    ellipsis_text: str = "..."
    show_home_icon: bool = False
    home_icon: Optional[QIcon] = None


class FluentBreadcrumbBar(FluentCompositeWidget):
    """
    Modern standalone breadcrumb navigation bar with animations, overflow handling,
    and configuration-driven behavior.
    """
    breadcrumb_clicked = Signal(int, str)
    navigation_requested = Signal(str)  # For full path navigation

    def __init__(self, config: Optional[BreadcrumbConfig] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._config = config or BreadcrumbConfig()
        self._breadcrumbs: List[str] = []
        self._buttons: List[FluentStandardButton] = []
        self._main_layout: Optional[QHBoxLayout] = None

        # Enhanced features
        self._cache_manager = CacheManager()
        self._animation_group: Optional[QParallelAnimationGroup] = None

        self.setFixedHeight(40)
        self._setup_breadcrumb_ui()
        self._apply_theme_styling()

    def _setup_breadcrumb_ui(self):
        """Setup modern breadcrumb UI with scroll support"""
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

    def _apply_theme_styling(self):
        """Apply theme-aware styling"""
        try:
            from core.theme import get_theme_manager
            theme = get_theme_manager()
            style = f"""
            FluentBreadcrumbBar {{
                background-color: {theme.get_color('surface')};
                border: 1px solid {theme.get_color('outline')};
                border-radius: 6px;
            }}
            """
            self.setStyleSheet(style)
        except Exception as e:
            print(f"Breadcrumb bar theme styling error: {e}")

    @lru_cache(maxsize=100)
    def _create_separator_widget(self) -> QLabel:
        """Create cached separator widget"""
        separator = QLabel(self._config.separator)
        separator.setFont(QFont("Segoe UI", 10))
        separator.setStyleSheet(f"color: {self._config.separator_color};")
        return separator

    def set_breadcrumbs(self, breadcrumbs: List[str], animate: Optional[bool] = None):
        """Set breadcrumb path with enhanced animation and overflow handling"""
        if animate is None:
            animate = self._config.animate_additions

        old_count = len(self._breadcrumbs)
        self._breadcrumbs = breadcrumbs.copy()

        # Clear existing content
        self._clear_breadcrumb_widgets()

        # Handle overflow with ellipsis
        display_breadcrumbs = self._handle_overflow(breadcrumbs)

        # Create new breadcrumb widgets
        animations = []
        for i, crumb in enumerate(display_breadcrumbs):
            if i > 0:
                separator = self._create_separator_widget()
                self.breadcrumb_layout.insertWidget(
                    self.breadcrumb_layout.count() - 1, separator)

            button = self._create_breadcrumb_button(
                crumb, i, len(display_breadcrumbs))
            self._buttons.append(button)
            self.breadcrumb_layout.insertWidget(
                self.breadcrumb_layout.count() - 1, button)

            # Prepare animation for new items
            if animate and i >= old_count:
                animation = self._create_fade_in_animation(button)
                if animation:
                    animations.append(animation)

        # Execute animations in parallel
        if animations:
            self._execute_parallel_animations(animations)

    def _clear_breadcrumb_widgets(self):
        """Clear existing breadcrumb widgets"""
        for button in self._buttons:
            button.deleteLater()
        self._buttons.clear()

        while self.breadcrumb_layout.count() > 1:  # Keep stretch
            item = self.breadcrumb_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def _handle_overflow(self, breadcrumbs: List[str]) -> List[str]:
        """Handle breadcrumb overflow with ellipsis"""
        if len(breadcrumbs) <= self._config.max_visible_items:
            return breadcrumbs

        # Show first few, ellipsis, and last few
        visible_count = self._config.max_visible_items - 1  # Account for ellipsis
        first_half = visible_count // 2
        second_half = visible_count - first_half

        return (breadcrumbs[:first_half] +
                [self._config.ellipsis_text] +
                breadcrumbs[-second_half:])

    def _create_breadcrumb_button(self, text: str, index: int, total: int) -> FluentStandardButton:
        """Create a styled breadcrumb button"""
        if text == self._config.ellipsis_text:
            button = FluentStandardButton(text, size=(None, 28))
            button.setEnabled(False)
            return button

        button = FluentStandardButton(text, size=(None, 28))

        # Connect click handler
        actual_index = self._calculate_actual_index(index, total)
        button.clicked.connect(
            lambda: self._on_breadcrumb_clicked(actual_index))

        # Apply styling based on position
        if index == total - 1:
            button.setStyleSheet("font-weight: bold;")
        else:
            button.setStyleSheet("text-decoration: underline;")

        return button

    def _calculate_actual_index(self, display_index: int, total_display: int) -> int:
        """Calculate actual breadcrumb index from display index"""
        # Handle ellipsis case
        if len(self._breadcrumbs) > self._config.max_visible_items:
            ellipsis_pos = self._config.max_visible_items // 2
            if display_index < ellipsis_pos:
                return display_index
            elif display_index == ellipsis_pos:
                return -1  # Ellipsis - invalid
            else:
                # After ellipsis
                offset = len(self._breadcrumbs) - \
                    total_display + ellipsis_pos + 1
                return display_index + offset
        return display_index

    def _create_fade_in_animation(self, widget: QWidget) -> Optional[QPropertyAnimation]:
        """Create fade-in animation for new breadcrumb"""
        try:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

            animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
            animation.setDuration(250)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)

            return animation
        except Exception as e:
            print(f"Breadcrumb animation error: {e}")
            return None

    def _execute_parallel_animations(self, animations: List[QPropertyAnimation]):
        """Execute multiple animations in parallel"""
        if not animations:
            return

        if self._animation_group:
            self._animation_group.stop()

        self._animation_group = QParallelAnimationGroup()
        for animation in animations:
            self._animation_group.addAnimation(animation)

        self._animation_group.start(
            QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def _on_breadcrumb_clicked(self, index: int):
        """Handle breadcrumb click with enhanced validation"""
        if index < 0 or index >= len(self._breadcrumbs):
            return

        breadcrumb_text = self._breadcrumbs[index]
        self.breadcrumb_clicked.emit(index, breadcrumb_text)

        # Emit full path navigation request
        path = self._get_path_to_index(index)
        self.navigation_requested.emit(path)

    def _get_path_to_index(self, index: int) -> str:
        """Get full navigation path up to specified index"""
        return "/".join(self._breadcrumbs[:index + 1])

    @contextmanager
    def batch_breadcrumb_updates(self):
        """Context manager for batch breadcrumb updates"""
        old_animate = self._config.animate_additions
        self._config.animate_additions = False
        try:
            yield
        finally:
            self._config.animate_additions = old_animate

    def get_breadcrumbs(self) -> List[str]:
        """Get current breadcrumbs list"""
        return self._breadcrumbs.copy()

    def add_breadcrumb(self, text: str, animate: Optional[bool] = None):
        """Add a new breadcrumb to the end"""
        new_breadcrumbs = self._breadcrumbs + [text]
        self.set_breadcrumbs(new_breadcrumbs, animate)

    def pop_breadcrumb(self, animate: Optional[bool] = None):
        """Remove the last breadcrumb"""
        if self._breadcrumbs:
            new_breadcrumbs = self._breadcrumbs[:-1]
            self.set_breadcrumbs(new_breadcrumbs, animate)

    def clear_breadcrumbs(self):
        """Clear all breadcrumbs"""
        self.set_breadcrumbs([], animate=False)

    def navigate_to_index(self, index: int):
        """Navigate to specific breadcrumb index"""
        if 0 <= index < len(self._breadcrumbs):
            truncated_breadcrumbs = self._breadcrumbs[:index + 1]
            self.set_breadcrumbs(truncated_breadcrumbs)

    def update_config(self, **kwargs):
        """Update breadcrumb configuration dynamically"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

        # Refresh display with new config
        current_breadcrumbs = self._breadcrumbs.copy()
        self.set_breadcrumbs(current_breadcrumbs, animate=False)

    def get_current_path(self) -> str:
        """Get the current full path as string"""
        return "/".join(self._breadcrumbs)

    def set_from_path(self, path: str, separator: str = "/"):
        """Set breadcrumbs from a path string"""
        if not path:
            self.clear_breadcrumbs()
            return

        breadcrumbs = [part.strip()
                       for part in path.split(separator) if part.strip()]
        self.set_breadcrumbs(breadcrumbs)
