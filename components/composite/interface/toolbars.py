"""
Composite Toolbar Components
High-level toolbar components that combine multiple widgets for common use cases.
Optimized for Python 3.10+ with modern typing, dataclasses, and enhanced performance.
"""

from __future__ import annotations
from typing import Any, Callable, TypeVar, TypeAlias, Protocol, Optional, Dict, List
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import lru_cache, partial
from contextlib import contextmanager
import weakref
from collections.abc import Sequence

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox,
                               QToolButton, QButtonGroup, QSizePolicy,
                               QSpacerItem, QFrame)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QModelIndex
from PySide6.QtGui import QIcon, QAction

from core.enhanced_base import FluentLayoutBuilder, FluentStandardButton, FluentToolbar
from core.enhanced_animations import FluentTransition, FluentMicroInteraction
from core.theme import theme_manager

# Type aliases for better readability
ActionCallback: TypeAlias = Callable[[], None]
FilterValue: TypeAlias = str | int | Any
OptionTuple: TypeAlias = tuple[str, Any]
ButtonRef: TypeAlias = weakref.ref[QPushButton]

T = TypeVar('T', bound=QWidget)


# Configuration dataclasses for better structure
@dataclass(frozen=True)
class ActionConfig:
    """Configuration for toolbar actions"""
    id: str
    text: str
    icon: QIcon | None = None
    tooltip: str = ""
    callback: ActionCallback | None = None
    enabled: bool = True

    def __post_init__(self):
        if not self.id or not self.text:
            raise ValueError("Action id and text are required")


@dataclass(frozen=True)
class FilterConfig:
    """Configuration for filter combos"""
    id: str
    label: str
    options: Sequence[OptionTuple]
    default_index: int = 0

    def __post_init__(self):
        if not self.options:
            raise ValueError("Filter options cannot be empty")
        if not 0 <= self.default_index < len(self.options):
            raise ValueError("Default index out of range")


@dataclass(frozen=True)
class ViewConfig:
    """Configuration for view controls"""
    id: str
    icon: QIcon | None = None
    tooltip: str = ""

    def __post_init__(self):
        if not self.id:
            raise ValueError("View id is required")


class ToolbarState(Enum):
    """Toolbar state enumeration"""
    NORMAL = auto()
    LOADING = auto()
    ERROR = auto()
    DISABLED = auto()


class ThemeAwareProtocol(Protocol):
    """Protocol for theme-aware widgets"""

    def _setup_enhanced_styling(self) -> None: ...
    def _on_theme_changed(self, theme_name: str = "") -> None: ...


class CacheManager:
    """Simple cache manager for toolbar resources"""

    def __init__(self, max_size: int = 128):
        self._cache: dict[str, Any] = {}
        self._max_size = max_size

    @lru_cache(maxsize=128)
    def get_cached_style(self, theme_name: str, component_type: str) -> str:
        """Get cached style for component"""
        key = f"{theme_name}_{component_type}"
        return self._cache.get(key, "")

    def clear_cache(self) -> None:
        """Clear the cache"""
        self._cache.clear()
        self.get_cached_style.cache_clear()


# Global cache instance
_cache_manager = CacheManager()


class FluentActionToolbar(FluentToolbar):
    """Enhanced action toolbar with grouped actions and animations

    Optimized implementation using dataclasses, weak references, and caching
    for better performance and memory efficiency.
    """

    action_triggered = Signal(str)  # action_id

    def __init__(self, title: str = "", parent: QWidget | None = None, height: int = 48):
        super().__init__(height, parent)
        self._action_groups: dict[str, dict[str, Any]] = {}
        self._weak_buttons: dict[str, list[ButtonRef]] = {}
        self._state = ToolbarState.NORMAL

        self.setFixedHeight(height)
        self._setup_enhanced_styling()

        # Performance optimization: batch style updates
        self._style_update_timer = QTimer(self)
        self._style_update_timer.timeout.connect(self._apply_pending_styles)
        self._style_update_timer.setSingleShot(True)

    def _setup_enhanced_styling(self) -> None:
        """Apply enhanced styling with animations and caching"""
        theme_key = theme_manager.get_current_theme_name() if hasattr(
            theme_manager, 'get_current_theme_name') else 'default'
        cached_style = _cache_manager.get_cached_style(
            theme_key, 'action_toolbar')

        if not cached_style:
            cached_style = f"""
                FluentActionToolbar {{
                    background: {theme_manager.get_color("surface")};
                    border-bottom: 1px solid {theme_manager.get_color("border")};
                    border-radius: 0px;
                }}
            """
            _cache_manager._cache[f"{theme_key}_action_toolbar"] = cached_style

        self.setStyleSheet(cached_style)

    @contextmanager
    def batch_updates(self):
        """Context manager for batching multiple toolbar updates"""
        self.setUpdatesEnabled(False)
        try:
            yield
        finally:
            self.setUpdatesEnabled(True)
            self.update()

    def add_action_group(self, group_id: str, actions: Sequence[ActionConfig],
                         separator: bool = True) -> list[QPushButton]:
        """Add a group of related actions with enhanced configuration

        Args:
            group_id: Unique identifier for the group
            actions: Sequence of ActionConfig objects
            separator: Whether to add separator before this group
        """
        if not group_id or not actions:
            raise ValueError("Group ID and actions are required")

        if separator and self._action_groups:
            self.addSeparator()

        buttons = []
        group_widget = QWidget()
        group_layout = FluentLayoutBuilder.create_horizontal_layout(spacing=4)
        group_widget.setLayout(group_layout)

        with self.batch_updates():
            for action_config in actions:
                btn = self._create_action_button(action_config)
                group_layout.addWidget(btn)
                buttons.append(btn)

        if self._layout:
            self._layout.addWidget(group_widget)

        # Store weak references to buttons for memory efficiency
        self._weak_buttons[group_id] = [weakref.ref(btn) for btn in buttons]

        self._action_groups[group_id] = {
            'widget': group_widget,
            'buttons': buttons,
            'actions': list(actions)  # Convert to list for indexing
        }

        return buttons

    def _create_action_button(self, action_config: ActionConfig) -> FluentStandardButton:
        """Create a button from action configuration"""
        btn = FluentStandardButton(
            text=action_config.text,
            icon=action_config.icon,
            size=(None, 28)
        )

        if action_config.tooltip:
            btn.setToolTip(action_config.tooltip)

        btn.setEnabled(action_config.enabled)

        # Connect callback with proper error handling
        if action_config.callback:
            btn.clicked.connect(self._safe_callback(action_config.callback))

        # Emit action triggered signal
        btn.clicked.connect(
            partial(self._emit_action_triggered, action_config.id)
        )

        # Add micro-interaction
        FluentMicroInteraction.button_press(btn)

        return btn

    def _safe_callback(self, callback: ActionCallback) -> ActionCallback:
        """Wrap callback with error handling"""
        def wrapper():
            try:
                callback()
            except Exception as e:
                print(f"Error in action callback: {e}")
                # Could emit error signal here for better error handling
        return wrapper

    def _emit_action_triggered(self, action_id: str, checked: bool = False) -> None:
        """Emit action triggered signal safely"""
        self.action_triggered.emit(action_id)

    def add_toggle_group(self, group_id: str, actions: Sequence[ActionConfig],
                         exclusive: bool = True) -> QButtonGroup:
        """Add a group of toggle buttons with enhanced configuration"""
        button_group = QButtonGroup(self)
        button_group.setExclusive(exclusive)

        buttons = self.add_action_group(group_id, actions, separator=True)

        for i, btn in enumerate(buttons):
            btn.setCheckable(True)
            button_group.addButton(btn, i)

        return button_group

    def set_action_enabled(self, group_id: str, action_index: int, enabled: bool) -> None:
        """Enable/disable specific action with validation"""
        if group_id not in self._action_groups:
            raise ValueError(f"Group '{group_id}' not found")

        buttons = self._action_groups[group_id]['buttons']
        if not 0 <= action_index < len(buttons):
            raise IndexError(f"Action index {action_index} out of range")

        buttons[action_index].setEnabled(enabled)

    def get_action_button(self, group_id: str, action_index: int) -> QPushButton | None:
        """Get specific action button with validation"""
        if group_id not in self._action_groups:
            return None

        buttons = self._action_groups[group_id]['buttons']
        if not 0 <= action_index < len(buttons):
            return None

        return buttons[action_index]

    def set_toolbar_state(self, state: ToolbarState) -> None:
        """Set toolbar state with visual feedback"""
        self._state = state

        # Update all buttons based on state
        for group_data in self._action_groups.values():
            for button in group_data['buttons']:
                if state == ToolbarState.DISABLED:
                    button.setEnabled(False)
                elif state == ToolbarState.LOADING:
                    button.setEnabled(False)
                    # Could add loading animation here
                else:
                    button.setEnabled(True)

    def _apply_pending_styles(self) -> None:
        """Apply any pending style updates"""
        self._setup_enhanced_styling()

    def _on_theme_changed(self, theme_name: str = "") -> None:
        """Handle theme changes with optimized updates"""
        _cache_manager.clear_cache()
        self._style_update_timer.start(100)  # Debounce style updates


class FluentSearchToolbar(FluentToolbar):
    """Enhanced search toolbar with filters and view controls

    Optimized with modern Python features and better resource management.
    """

    search_changed = Signal(str)
    filter_changed = Signal(str, str)  # filter_type, value
    view_changed = Signal(str)  # view_mode

    def __init__(self, placeholder: str = "搜索...", parent: QWidget | None = None, height: int = 44):
        super().__init__(height, parent)
        self._placeholder = placeholder
        self._filters: dict[str, QComboBox] = {}
        self._view_buttons: list[tuple[str, QToolButton]] = []
        self._search_input: QLineEdit | None = None
        self._search_animation: QPropertyAnimation | None = None
        self._search_debounce_timer = QTimer(self)

        # Setup debounced search
        self._search_debounce_timer.setSingleShot(True)
        self._search_debounce_timer.timeout.connect(self._emit_search_changed)

        self.setFixedHeight(height)
        self._setup_search_ui()
        self._setup_enhanced_styling()

    def _setup_search_ui(self) -> None:
        """Setup search interface with optimizations"""
        # Search input with debouncing
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(self._placeholder)
        self._search_input.setFixedHeight(32)
        self._search_input.textChanged.connect(self._on_search_text_changed)

        # Add search animation
        self._search_animation = FluentTransition.create_transition(
            self._search_input, FluentTransition.SCALE, duration=200
        )

        # Enhanced search input styling with caching
        self._apply_search_styling()

        if self._layout and self._search_input:
            self._layout.addWidget(self._search_input)

        # Add spacer to push filters and views to the right
        spacer = QSpacerItem(
            10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        if self._layout:
            self._layout.addItem(spacer)

    def _apply_search_styling(self) -> None:
        """Apply optimized search input styling"""
        if not self._search_input:
            return

        theme_key = theme_manager.get_current_theme_name() if hasattr(
            theme_manager, 'get_current_theme_name') else 'default'
        cached_style = _cache_manager.get_cached_style(
            theme_key, 'search_input')

        if not cached_style:
            cached_style = f"""
                QLineEdit {{
                    background: {theme_manager.get_color("input_background")};
                    border: 1px solid {theme_manager.get_color("border")};
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 13px;
                    min-width: 200px;
                }}
                QLineEdit:focus {{
                    border-color: {theme_manager.get_color("accent")};
                    background: {theme_manager.get_color("surface")};
                }}
            """
            _cache_manager._cache[f"{theme_key}_search_input"] = cached_style

        self._search_input.setStyleSheet(cached_style)

    def _on_search_text_changed(self, text: str) -> None:
        """Handle search text changes with debouncing"""
        self._search_debounce_timer.stop()
        self._current_search_text = text
        self._search_debounce_timer.start(300)  # 300ms debounce

    def _emit_search_changed(self) -> None:
        """Emit search changed signal after debounce"""
        if hasattr(self, '_current_search_text'):
            self.search_changed.emit(self._current_search_text)

    def _setup_enhanced_styling(self) -> None:
        """Apply enhanced styling with caching"""
        theme_key = theme_manager.get_current_theme_name() if hasattr(
            theme_manager, 'get_current_theme_name') else 'default'
        cached_style = _cache_manager.get_cached_style(
            theme_key, 'search_toolbar')

        if not cached_style:
            cached_style = f"""
                FluentSearchToolbar {{
                    background: {theme_manager.get_color("surface")};
                    border-bottom: 1px solid {theme_manager.get_color("border")};
                }}
            """
            _cache_manager._cache[f"{theme_key}_search_toolbar"] = cached_style

        self.setStyleSheet(cached_style)

    def add_filter_combo(self, filter_config: FilterConfig) -> QComboBox:
        """Add filter combobox with enhanced configuration

        Args:
            filter_config: FilterConfig object with filter settings
        """
        # Label
        filter_label = QLabel(filter_config.label)
        filter_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color("text")};
                font-size: 12px;
                margin-right: 4px;
            }}
        """)

        # Combobox
        combo = QComboBox()
        combo.setFixedHeight(32)

        for display_text, value in filter_config.options:
            combo.addItem(display_text, value)

        if 0 <= filter_config.default_index < len(filter_config.options):
            combo.setCurrentIndex(filter_config.default_index)

        # Connect signal with safe emission
        combo.currentTextChanged.connect(
            partial(self._emit_filter_changed, filter_config.id, combo)
        )

        # Apply optimized styling
        self._apply_combo_styling(combo)

        # Add to toolbar
        container = QWidget()
        layout = FluentLayoutBuilder.create_horizontal_layout(spacing=4)
        layout.addWidget(filter_label)
        layout.addWidget(combo)
        container.setLayout(layout)

        if self._layout:
            self._layout.addWidget(container)

        self._filters[filter_config.id] = combo
        return combo

    def _emit_filter_changed(self, filter_id: str, combo: QComboBox, text: str) -> None:
        """Safely emit filter changed signal"""
        try:
            value = combo.currentData()
            self.filter_changed.emit(filter_id, str(
                value) if value is not None else "")
        except Exception as e:
            print(f"Error in filter change: {e}")

    def _apply_combo_styling(self, combo: QComboBox) -> None:
        """Apply consistent combobox styling"""
        combo.setStyleSheet(f"""
            QComboBox {{
                background: {theme_manager.get_color("input_background")};
                border: 1px solid {theme_manager.get_color("border")};
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 12px;
                min-width: 100px;
            }}
            QComboBox:hover {{
                border-color: {theme_manager.get_color("accent")};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
        """)

    def add_view_controls(self, views: Sequence[ViewConfig], default: str | None = None) -> QButtonGroup:
        """Add view mode controls with enhanced configuration

        Args:
            views: Sequence of ViewConfig objects
            default: Default view id
        """
        view_group = QButtonGroup(self)
        view_group.setExclusive(True)

        container = QWidget()
        layout = FluentLayoutBuilder.create_horizontal_layout(spacing=2)
        container.setLayout(layout)

        for view_config in views:
            btn = QToolButton()
            btn.setFixedSize(32, 32)
            btn.setCheckable(True)

            if view_config.icon:
                btn.setIcon(view_config.icon)
            if view_config.tooltip:
                btn.setToolTip(view_config.tooltip)

            # Apply optimized styling
            self._apply_view_button_styling(btn)

            # Connect signal safely
            btn.clicked.connect(
                partial(self._emit_view_changed, view_config.id)
            )

            # Add micro-interaction
            FluentMicroInteraction.button_press(btn)

            layout.addWidget(btn)
            view_group.addButton(btn)
            self._view_buttons.append((view_config.id, btn))

            # Set default
            if default and view_config.id == default:
                btn.setChecked(True)

        if self._layout:
            self._layout.addWidget(container)

        return view_group

    def _emit_view_changed(self, view_id: str, checked: bool = False) -> None:
        """Safely emit view changed signal"""
        self.view_changed.emit(view_id)

    def _apply_view_button_styling(self, btn: QToolButton) -> None:
        """Apply consistent view button styling"""
        btn.setStyleSheet(f"""
            QToolButton {{
                background: transparent;
                border: 1px solid {theme_manager.get_color("border")};
                border-radius: 6px;
            }}
            QToolButton:hover {{
                background: {theme_manager.get_color("hover")};
            }}
            QToolButton:checked {{
                background: {theme_manager.get_color("accent")};
                border-color: {theme_manager.get_color("accent")};
            }}
        """)

    # Enhanced getter/setter methods with validation
    def set_search_text(self, text: str) -> None:
        """Set search input text with validation"""
        if self._search_input and isinstance(text, str):
            self._search_input.setText(text)

    def get_search_text(self) -> str:
        """Get current search text"""
        return self._search_input.text() if self._search_input else ""

    def set_filter_value(self, filter_id: str, value: Any) -> bool:
        """Set filter combobox value with validation"""
        if filter_id not in self._filters:
            return False

        combo = self._filters[filter_id]
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return True
        return False

    def focus_search(self) -> None:
        """Focus the search input with enhanced animation"""
        if not self._search_input:
            return

        self._search_input.setFocus()

        # Enhanced animation with bounds checking
        if self._search_animation and isinstance(self._search_animation, QPropertyAnimation):
            current_width = self._search_input.width()
            target_width = min(300, current_width + 100)

            self._search_animation.setTargetObject(self._search_input)
            self._search_animation.setPropertyName(b"minimumWidth")
            self._search_animation.setStartValue(current_width)
            self._search_animation.setEndValue(target_width)
            self._search_animation.start()

    def _on_theme_changed(self, theme_name: str = "") -> None:
        """Handle theme changes with optimized updates"""
        _cache_manager.clear_cache()
        self._setup_enhanced_styling()
        self._apply_search_styling()

        # Update all combo boxes
        for combo in self._filters.values():
            self._apply_combo_styling(combo)

        # Update view buttons
        for _, btn in self._view_buttons:
            self._apply_view_button_styling(btn)


class FluentViewToolbar(FluentToolbar):
    """Enhanced view toolbar with sorting, grouping, and display options

    Modern implementation with dataclasses, type safety, and performance optimizations.
    """

    sort_changed = Signal(str, bool)  # field, ascending
    group_changed = Signal(str)  # field
    display_changed = Signal(str, object)  # option, value

    def __init__(self, title: str = "视图选项", parent: QWidget | None = None, height: int = 40):
        super().__init__(height, parent)
        self._sort_combo: QComboBox | None = None
        self._sort_order_btn: QToolButton | None = None
        self._group_combo: QComboBox | None = None
        self._display_options: dict[str, QWidget] = {}
        self._current_sort_field: str = ""
        self._current_sort_ascending: bool = True

        self.setFixedHeight(height)
        self._setup_view_controls()
        self._setup_enhanced_styling()

    def _setup_view_controls(self) -> None:
        """Setup view control interface with enhanced organization"""
        # Sort controls
        self._add_sort_controls()

        # Add separator
        self.addSeparator()

        # Group controls
        self._add_group_controls()

    @contextmanager
    def _null_context(self):
        """Null context manager fallback"""
        yield

    def _add_sort_controls(self) -> None:
        """Add sorting controls with enhanced styling"""
        # Sort label
        sort_label = QLabel("排序:")
        sort_label.setStyleSheet(
            f"color: {theme_manager.get_color('text')}; font-size: 12px;")

        # Sort field combo
        self._sort_combo = QComboBox()
        self._sort_combo.setFixedHeight(28)
        self._sort_combo.setMinimumWidth(120)
        self._sort_combo.currentTextChanged.connect(self._on_sort_changed)

        # Sort order button with enhanced functionality
        self._sort_order_btn = QToolButton()
        self._sort_order_btn.setFixedSize(28, 28)
        self._sort_order_btn.setCheckable(True)
        self._sort_order_btn.setToolTip("切换排序顺序")
        self._sort_order_btn.clicked.connect(self._on_sort_order_changed)

        # Apply styling
        self._style_sort_controls()

        # Add to toolbar
        container = QWidget()
        layout = FluentLayoutBuilder.create_horizontal_layout(spacing=6)
        layout.addWidget(sort_label)

        if self._sort_combo:
            layout.addWidget(self._sort_combo)
        if self._sort_order_btn:
            layout.addWidget(self._sort_order_btn)

        container.setLayout(layout)

        if self._layout:
            self._layout.addWidget(container)

    def _add_group_controls(self) -> None:
        """Add grouping controls with validation"""
        # Group label
        group_label = QLabel("分组:")
        group_label.setStyleSheet(
            f"color: {theme_manager.get_color('text')}; font-size: 12px;")

        # Group combo
        self._group_combo = QComboBox()
        self._group_combo.setFixedHeight(28)
        self._group_combo.setMinimumWidth(100)
        self._group_combo.addItem("无分组", None)
        self._group_combo.currentTextChanged.connect(self._on_group_changed)

        # Apply consistent styling
        self._apply_combo_styling(self._group_combo)

        # Add to toolbar
        container = QWidget()
        layout = FluentLayoutBuilder.create_horizontal_layout(spacing=6)
        layout.addWidget(group_label)

        if self._group_combo:
            layout.addWidget(self._group_combo)

        container.setLayout(layout)

        if self._layout:
            self._layout.addWidget(container)

    def _style_sort_controls(self) -> None:
        """Apply optimized styling to sort controls"""
        combo_style = f"""
            QComboBox {{
                background: {theme_manager.get_color("input_background")};
                border: 1px solid {theme_manager.get_color("border")};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }}
            QComboBox:hover {{
                border-color: {theme_manager.get_color("accent")};
            }}
        """

        if self._sort_combo:
            self._sort_combo.setStyleSheet(combo_style)

        btn_style = f"""
            QToolButton {{
                background: {theme_manager.get_color("input_background")};
                border: 1px solid {theme_manager.get_color("border")};
                border-radius: 4px;
            }}
            QToolButton:hover {{
                background: {theme_manager.get_color("hover")};
            }}
            QToolButton:checked {{
                background: {theme_manager.get_color("accent")};
                color: white;
            }}
        """

        if self._sort_order_btn:
            self._sort_order_btn.setStyleSheet(btn_style)

        # Set initial display
        self._update_sort_order_display()

    def _apply_combo_styling(self, combo: QComboBox) -> None:
        """Apply consistent combobox styling"""
        combo.setStyleSheet(f"""
            QComboBox {{
                background: {theme_manager.get_color("input_background")};
                border: 1px solid {theme_manager.get_color("border")};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }}
            QComboBox:hover {{
                border-color: {theme_manager.get_color("accent")};
            }}
        """)

    def _setup_enhanced_styling(self) -> None:
        """Apply enhanced styling with caching"""
        theme_key = theme_manager.get_current_theme_name() if hasattr(
            theme_manager, 'get_current_theme_name') else 'default'
        cached_style = _cache_manager.get_cached_style(
            theme_key, 'view_toolbar')

        if not cached_style:
            cached_style = f"""
                FluentViewToolbar {{
                    background: {theme_manager.get_color("surface")};
                    border-bottom: 1px solid {theme_manager.get_color("border")};
                }}
            """
            _cache_manager._cache[f"{theme_key}_view_toolbar"] = cached_style

        self.setStyleSheet(cached_style)

    def add_sort_options(self, options: Sequence[OptionTuple]) -> None:
        """Add sort field options with validation

        Args:
            options: Sequence of (display_text, field_name) tuples
        """
        if not self._sort_combo or not options:
            return

        self._sort_combo.clear()
        for display_text, field_name in options:
            if not isinstance(display_text, str) or not field_name:
                continue
            self._sort_combo.addItem(display_text, field_name)

    def add_group_options(self, options: Sequence[OptionTuple]) -> None:
        """Add group field options with validation

        Args:
            options: Sequence of (display_text, field_name) tuples
        """
        if not self._group_combo or not options:
            return

        # Keep the "无分组" option and add new ones
        current_count = self._group_combo.count()
        for display_text, field_name in options:
            if not isinstance(display_text, str) or not field_name:
                continue
            self._group_combo.addItem(display_text, field_name)

    def add_display_option(self, option_id: str, widget: QWidget) -> None:
        """Add custom display option widget with validation"""
        if not option_id or not widget:
            raise ValueError("Option ID and widget are required")

        self.addSeparator()
        if self._layout:
            self._layout.addWidget(widget)
        self._display_options[option_id] = widget

    def _on_sort_changed(self) -> None:
        """Handle sort field change with error handling"""
        if not self._sort_combo or not self._sort_order_btn:
            return

        try:
            field = self._sort_combo.currentData()
            if field is not None:
                self._current_sort_field = str(field)
                ascending = not self._sort_order_btn.isChecked()
                self._current_sort_ascending = ascending
                self.sort_changed.emit(self._current_sort_field, ascending)
        except Exception as e:
            print(f"Error in sort change: {e}")

    def _on_sort_order_changed(self) -> None:
        """Handle sort order change with state tracking"""
        if not self._sort_combo or not self._sort_order_btn:
            return

        try:
            field = self._sort_combo.currentData()
            if field is not None:
                ascending = not self._sort_order_btn.isChecked()
                self._current_sort_ascending = ascending
                self.sort_changed.emit(str(field), ascending)
        except Exception as e:
            print(f"Error in sort order change: {e}")

        self._update_sort_order_display()

    def _on_group_changed(self) -> None:
        """Handle group field change with validation"""
        if not self._group_combo:
            return

        try:
            field = self._group_combo.currentData()
            if field is not None:
                self.group_changed.emit(str(field))
            elif self._group_combo.currentText() == "无分组":
                self.group_changed.emit("")
        except Exception as e:
            print(f"Error in group change: {e}")

    def _update_sort_order_display(self) -> None:
        """Update sort order button display with icons"""
        if not self._sort_order_btn:
            return

        if self._sort_order_btn.isChecked():
            self._sort_order_btn.setText("↓")
            self._sort_order_btn.setToolTip("降序排列")
        else:
            self._sort_order_btn.setText("↑")
            self._sort_order_btn.setToolTip("升序排列")

    # Enhanced public API with validation
    def set_sort_field(self, field: str) -> bool:
        """Set current sort field with validation

        Returns:
            True if field was set successfully, False otherwise
        """
        if not self._sort_combo or not field:
            return False

        for i in range(self._sort_combo.count()):
            if self._sort_combo.itemData(i) == field:
                self._sort_combo.setCurrentIndex(i)
                self._current_sort_field = field
                return True
        return False

    def set_sort_ascending(self, ascending: bool) -> None:
        """Set sort order with state tracking"""
        if self._sort_order_btn:
            self._sort_order_btn.setChecked(not ascending)
            self._current_sort_ascending = ascending
            self._update_sort_order_display()

    def set_group_field(self, field: str | None) -> bool:
        """Set current group field with validation

        Returns:
            True if field was set successfully, False otherwise
        """
        if not self._group_combo:
            return False

        if field is None or field == "":
            # Find "无分组" option
            idx = self._group_combo.findData(None)
            if idx != -1:
                self._group_combo.setCurrentIndex(idx)
                return True

            # Fallback to text search
            for i in range(self._group_combo.count()):
                if self._group_combo.itemText(i) == "无分组":
                    self._group_combo.setCurrentIndex(i)
                    return True
        else:
            for i in range(self._group_combo.count()):
                if self._group_combo.itemData(i) == field:
                    self._group_combo.setCurrentIndex(i)
                    return True

        return False

    def get_current_sort(self) -> tuple[str, bool]:
        """Get current sort field and order"""
        return self._current_sort_field, self._current_sort_ascending

    def get_current_group(self) -> str | None:
        """Get current group field"""
        if not self._group_combo:
            return None

        data = self._group_combo.currentData()
        return str(data) if data is not None else None

    def _on_theme_changed(self, theme_name: str = "") -> None:
        """Handle theme changes with comprehensive updates"""
        _cache_manager.clear_cache()
        self._setup_enhanced_styling()
        self._style_sort_controls()

        if self._group_combo:
            self._apply_combo_styling(self._group_combo)


class FluentStatusToolbar(FluentToolbar):
    """Enhanced status toolbar with progress, stats, and notifications

    Modern implementation with async-friendly design and resource management.
    """

    # Enhanced signals for better monitoring
    status_updated = Signal(str)
    progress_started = Signal(str)
    progress_finished = Signal()

    def __init__(self, parent: QWidget | None = None, height: int = 32):
        super().__init__(height, parent)
        self._status_label: QLabel | None = None
        self._progress_widget: QWidget | None = None
        self._progress_container: QWidget | None = None
        self._stats_widgets: dict[str, QLabel] = {}
        self._notification_timer = QTimer(self)
        self._current_status = "就绪"
        self._is_progress_active = False

        # Setup timer
        self._notification_timer.timeout.connect(self._clear_temporary_status)
        self._notification_timer.setSingleShot(True)

        self.setFixedHeight(height)
        self._setup_status_ui()
        self._setup_enhanced_styling()

    def _setup_status_ui(self) -> None:
        """Setup status interface with optimized layout"""
        # Main status label
        self._status_label = QLabel(self._current_status)
        self._apply_status_label_styling()

        if self._layout and self._status_label:
            self._layout.addWidget(self._status_label)

        # Add spacer to push stats to the right
        spacer = QSpacerItem(
            10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        if self._layout:
            self._layout.addItem(spacer)

    def _apply_status_label_styling(self) -> None:
        """Apply optimized status label styling"""
        if not self._status_label:
            return

        self._status_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color("text")};
                font-size: 12px;
                padding: 4px 8px;
            }}
        """)

    def _setup_enhanced_styling(self) -> None:
        """Apply enhanced styling with caching"""
        theme_key = theme_manager.get_current_theme_name() if hasattr(
            theme_manager, 'get_current_theme_name') else 'default'
        cached_style = _cache_manager.get_cached_style(
            theme_key, 'status_toolbar')

        if not cached_style:
            cached_style = f"""
                FluentStatusToolbar {{
                    background: {theme_manager.get_color("surface")};
                    border-top: 1px solid {theme_manager.get_color("border")};
                    border-radius: 0px;
                }}
            """
            _cache_manager._cache[f"{theme_key}_status_toolbar"] = cached_style

        self.setStyleSheet(cached_style)

    def set_status(self, text: str, temporary: bool = False, duration: int = 3000) -> None:
        """Set status text with enhanced validation and feedback

        Args:
            text: Status text to display
            temporary: Whether status should auto-clear
            duration: Duration in ms for temporary status
        """
        if not isinstance(text, str):
            text = str(text)

        if not text.strip():
            text = "就绪"

        self._current_status = text

        if self._status_label:
            self._status_label.setText(text)

        # Emit status update signal
        self.status_updated.emit(text)

        if temporary and duration > 0:
            self._notification_timer.stop()
            self._notification_timer.start(duration)

    def add_stat(self, stat_id: str, label: str, value: str = "0") -> QLabel | None:
        """Add a statistics display with validation

        Args:
            stat_id: Unique identifier for the stat
            label: Display label
            value: Initial value
        """
        if not stat_id or not label:
            raise ValueError("Stat ID and label are required")

        if stat_id in self._stats_widgets:
            # Update existing stat
            self.update_stat(stat_id, value)
            return self._stats_widgets[stat_id]

        container = QWidget()
        layout = FluentLayoutBuilder.create_horizontal_layout(spacing=4)

        # Label
        stat_label = QLabel(f"{label}:")
        stat_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color("text")};
                font-size: 11px;
                font-weight: 500;
            }}
        """)

        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color("accent")};
                font-size: 11px;
                font-weight: bold;
            }}
        """)

        layout.addWidget(stat_label)
        layout.addWidget(value_label)
        container.setLayout(layout)

        if self._layout:
            self._layout.addWidget(container)

        self._stats_widgets[stat_id] = value_label
        return value_label

    def update_stat(self, stat_id: str, value: str | int | float) -> bool:
        """Update statistics value with validation

        Returns:
            True if stat was updated successfully, False otherwise
        """
        if stat_id not in self._stats_widgets:
            return False

        try:
            self._stats_widgets[stat_id].setText(str(value))
            return True
        except Exception as e:
            print(f"Error updating stat {stat_id}: {e}")
            return False

    def remove_stat(self, stat_id: str) -> bool:
        """Remove a statistics display

        Returns:
            True if stat was removed successfully, False otherwise        """
        if stat_id not in self._stats_widgets:
            return False

        try:
            label = self._stats_widgets[stat_id]
            parent_widget = label.parent()

            if parent_widget and self._layout and isinstance(parent_widget, QWidget):
                self._layout.removeWidget(parent_widget)
                parent_widget.deleteLater()

            del self._stats_widgets[stat_id]
            return True
        except Exception as e:
            print(f"Error removing stat {stat_id}: {e}")
            return False

    def show_progress(self, text: str = "处理中...") -> None:
        """Show progress indicator with enhanced management"""
        if self._is_progress_active:
            # Update existing progress text
            if hasattr(self, '_progress_label'):
                self._progress_label.setText(text)
            return

        self._is_progress_active = True

        # Create progress indicator (placeholder)
        if self._progress_widget is None:
            # Placeholder for loading indicator
            self._progress_widget = QLabel("⏳")

        # Create progress container
        self._progress_container = QWidget()
        layout = FluentLayoutBuilder.create_horizontal_layout(spacing=6)

        if self._progress_widget:
            layout.addWidget(self._progress_widget)

        self._progress_label = QLabel(text)
        self._progress_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color("text")};
                font-size: 12px;
            }}
        """)
        layout.addWidget(self._progress_label)
        self._progress_container.setLayout(layout)

        # Hide status label temporarily
        if self._status_label:
            self._status_label.hide()

        # Add progress container
        if self._layout and self._progress_container:
            self._layout.insertWidget(0, self._progress_container)

        # Emit progress signal
        self.progress_started.emit(text)

    def hide_progress(self) -> None:
        """Hide progress indicator with cleanup"""
        if not self._is_progress_active:
            return

        self._is_progress_active = False

        try:
            if self._progress_container and self._layout:
                self._layout.removeWidget(self._progress_container)
                self._progress_container.deleteLater()
                self._progress_container = None

            if self._status_label:
                self._status_label.show()

            # Emit progress finished signal
            self.progress_finished.emit()
        except Exception as e:
            print(f"Error hiding progress: {e}")

    def update_progress_text(self, text: str) -> None:
        """Update progress text if progress is active"""
        if self._is_progress_active and hasattr(self, '_progress_label'):
            self._progress_label.setText(text)

    def _clear_temporary_status(self) -> None:
        """Clear temporary status message"""
        self.set_status("就绪")
        self._notification_timer.stop()

    @contextmanager
    def progress_context(self, text: str = "处理中..."):
        """Context manager for automatic progress management"""
        self.show_progress(text)
        try:
            yield
        finally:
            self.hide_progress()

    def get_current_status(self) -> str:
        """Get current status text"""
        return self._current_status

    def is_progress_active(self) -> bool:
        """Check if progress is currently active"""
        return self._is_progress_active

    def get_stats(self) -> dict[str, str]:
        """Get all current stats as a dictionary"""
        return {
            stat_id: label.text()
            for stat_id, label in self._stats_widgets.items()
        }

    def clear_stats(self) -> None:
        """Clear all statistics"""
        stat_ids = list(self._stats_widgets.keys())
        for stat_id in stat_ids:
            self.remove_stat(stat_id)

    def _on_theme_changed(self, theme_name: str = "") -> None:
        """Handle theme changes with comprehensive updates"""
        _cache_manager.clear_cache()
        self._setup_enhanced_styling()
        self._apply_status_label_styling()

        # Update all stat widgets
        for label in self._stats_widgets.values():
            label.setStyleSheet(f"""
                QLabel {{
                    color: {theme_manager.get_color("accent")};
                    font-size: 11px;
                    font-weight: bold;
                }}
            """)

    def __del__(self):
        """Cleanup resources on deletion"""
        try:
            if hasattr(self, '_notification_timer'):
                self._notification_timer.stop()
        except:
            pass  # Ignore cleanup errors


# Example usage and best practices for optimized toolbars
"""
Usage Examples for Optimized Fluent Toolbars

This section demonstrates how to use the optimized toolbar components
with modern Python features and best practices.

Example 1: Action Toolbar with Dataclasses
```python
from dataclasses import dataclass
from PySide6.QtGui import QIcon

# Define actions using dataclasses for type safety
file_actions = [
    ActionConfig(
        id="new_file",
        text="新建",
        icon=QIcon(":/icons/new.png"),
        tooltip="创建新文件",
        callback=lambda: print("新建文件")
    ),
    ActionConfig(
        id="open_file", 
        text="打开",
        icon=QIcon(":/icons/open.png"),
        tooltip="打开文件",
        callback=lambda: print("打开文件")
    ),
]

# Create toolbar with batch operations
toolbar = FluentActionToolbar(height=48)
with toolbar.batch_updates():
    buttons = toolbar.add_action_group("file_ops", file_actions)
    toolbar.set_toolbar_state(ToolbarState.NORMAL)
```

Example 2: Search Toolbar with Advanced Features  
```python
# Create search toolbar with filters
search_toolbar = FluentSearchToolbar(placeholder="搜索文档...")

# Add filters using configuration objects
filter_configs = [
    FilterConfig(
        id="file_type",
        label="类型",
        options=[("所有", "all"), ("文档", "doc"), ("图片", "img")],
        default_index=0
    ),
    FilterConfig(
        id="date_range",
        label="日期",
        options=[("所有", "all"), ("今天", "today"), ("本周", "week")],
        default_index=0
    ),
]

for config in filter_configs:
    search_toolbar.add_filter_combo(config)

# Add view controls
view_configs = [
    ViewConfig(id="list", icon=QIcon(":/icons/list.png"), tooltip="列表视图"),
    ViewConfig(id="grid", icon=QIcon(":/icons/grid.png"), tooltip="网格视图"),
]

search_toolbar.add_view_controls(view_configs, default="list")
```

Example 3: Status Toolbar with Progress Management
```python
status_toolbar = FluentStatusToolbar()

# Add statistics
status_toolbar.add_stat("files", "文件", "0")
status_toolbar.add_stat("size", "大小", "0 MB")

# Use context manager for automatic progress handling
async def process_files():
    with status_toolbar.progress_context("处理文件中..."):
        # Simulate file processing
        for i in range(100):
            await asyncio.sleep(0.01)
            status_toolbar.update_progress_text(f"处理文件 {i+1}/100")
            status_toolbar.update_stat("files", str(i+1))

# Or manual progress control
status_toolbar.show_progress("上传文件...")
# ... do work ...
status_toolbar.hide_progress()
```

Performance Tips:
1. Use batch_updates() context manager for multiple operations
2. Leverage dataclasses for type-safe configuration
3. Use weak references for memory efficiency in large applications
4. Enable caching for frequently accessed styles
5. Use debounced search for better UX and performance
6. Implement proper error handling for robust applications

Memory Management:
- Toolbars use weak references internally to prevent memory leaks
- Cache manager automatically clears outdated style cache
- Progress contexts ensure proper cleanup
- Statistics can be dynamically added/removed

Type Safety:
- Modern union types (str | None) for better IDE support
- Protocols for duck typing and interface compliance
- Generic types for flexible but safe APIs
- Dataclasses for structured configuration
"""
