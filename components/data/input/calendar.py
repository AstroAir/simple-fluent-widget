#!/usr/bin/env python3
"""
Calendar and Date/Time Picker Components for Fluent UI - Ultra-Optimized

Modern calendar and date/time picker components following Fluent Design principles.
Ultra-optimized for Python 3.11+ with:
- Union type syntax (|) and PEP 604 union types
- Dataclasses with slots and frozen optimizations
- Enhanced pattern matching with structural patterns
- Type safety improvements with strict typing
- Performance optimizations with memory pooling
- Better error handling with exception groups
- Cached properties and methods with LRU caching
- Modern animation system with easing functions
- Memory-efficient state management
- Batch operations and lazy evaluation
"""

from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QFrame, QLineEdit, QGraphicsOpacityEffect,
    QSizePolicy, QApplication
)
from PySide6.QtGui import QFont, QColor, QPainter, QMouseEvent, QPalette
from PySide6.QtCore import (
    Qt, Signal, QDate, QTime, QDateTime, QTimer, QPropertyAnimation,
    QEasingCurve, QRect, QSize, Property, QByteArray, Slot
)

import calendar
import weakref
from dataclasses import dataclass, field
from enum import Enum, StrEnum, auto
from typing import (
    Protocol, TypeVar, Generic, Union, Optional, Sequence, Callable, List,
    Dict, Any, Final, TypeAlias, ClassVar
)
from collections.abc import Iterable, Mapping
from functools import lru_cache, cached_property, singledispatch
from contextlib import contextmanager, suppress
import operator
from itertools import cycle

# Type variables
Self = TypeVar('Self')
def override(func): return func


# Enhanced imports with better error handling
try:
    from core.theme import theme_manager
    THEME_AVAILABLE = True
except ImportError:
    theme_manager = None
    THEME_AVAILABLE = False

try:
    from core.enhanced_animations import (
        FluentRevealEffect, FluentMicroInteraction, FluentTransition,
        FluentSequence, FluentStateTransition
    )
    ANIMATIONS_AVAILABLE = True
except ImportError:
    # Create null objects for missing animation classes
    class AnimationProxy:
        def __getattr__(self, name): return lambda *args, **kwargs: None

    ANIMATIONS_AVAILABLE = False
    FluentRevealEffect = AnimationProxy()
    FluentMicroInteraction = AnimationProxy()
    FluentTransition = AnimationProxy()
    FluentSequence = AnimationProxy()
    FluentStateTransition = AnimationProxy()


# Type aliases using modern union syntax (Python 3.10+)
DateLike: TypeAlias = QDate | str
TimeLike: TypeAlias = QTime | str
DateTimeLike: TypeAlias = QDateTime | str
ColorLike: TypeAlias = QColor | str

# Widget pools for memory optimization
WidgetPool: TypeAlias = Dict[str, List[QWidget]]
StateDict: TypeAlias = Dict[str, Any]


@dataclass(slots=True, frozen=True)
class CalendarTheme:
    """Theme configuration for calendar components with slots optimization"""
    surface_color: str = "#FFFFFF"
    primary_color: str = "#0078D4"
    text_color: str = "#000000"
    border_color: str = "#D1D1D1"
    today_color: str = "#FFF4CE"
    weekend_color: str = "#FF6B6B"
    hover_color: str = "#F5F5F5"
    selected_color: str = "#0078D4"
    animation_duration: int = 200

    @lru_cache(maxsize=32)
    def get_state_color(self, state: str) -> str:
        """Get color for specific state with caching"""
        match state:
            case "selected":
                return self.selected_color
            case "today":
                return self.today_color
            case "hovered":
                return self.hover_color
            case "weekend":
                return self.weekend_color
            case "disabled":
                return "#CCCCCC"
            case _:
                return self.surface_color


# Additional type aliases after class definitions
ThemeCache: TypeAlias = Dict[str, CalendarTheme]


@dataclass(slots=True)
class CalendarConfig:
    """Configuration for calendar behavior with slots optimization"""
    show_week_numbers: bool = False
    first_day_of_week: int = 0  # 0 = Sunday
    date_format: str = "yyyy-MM-dd"
    enable_animations: bool = True
    weekend_highlighting: bool = True
    today_highlighting: bool = True
    locale: str = "zh_CN"

    # Performance optimizations
    cache_size: int = 128
    batch_update_threshold: int = 10
    lazy_loading: bool = True


class CalendarStateType(StrEnum):
    """Calendar state enumeration using StrEnum for better performance"""
    NORMAL = "normal"
    HOVERED = "hovered"
    SELECTED = "selected"
    TODAY = "today"
    WEEKEND = "weekend"
    DISABLED = "disabled"


class DateValidationProtocol(Protocol):
    """Protocol for date validation"""

    def is_valid_date(self, date: QDate) -> bool: ...
    def get_validation_message(self, date: QDate) -> str: ...


class CalendarAnimationProtocol(Protocol):
    """Protocol for calendar animations"""

    def animate_selection(self, widget: QWidget) -> None: ...
    def animate_hover(self, widget: QWidget, enter: bool) -> None: ...
    def animate_month_change(self, widget: QWidget,
                             direction: str) -> None: ...


# Performance optimization: Widget pool for memory efficiency
class WidgetPoolManager:
    """Singleton widget pool manager for memory optimization"""
    _instance: Optional['WidgetPoolManager'] = None
    _pools: ClassVar[Dict[str, List[QWidget]]] = {}

    def __new__(cls) -> 'WidgetPoolManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_widget(cls, widget_type: str, factory: Callable[[], QWidget]) -> QWidget:
        """Get widget from pool or create new one"""
        pool = cls._pools.setdefault(widget_type, [])
        if pool:
            return pool.pop()
        return factory()

    @classmethod
    def return_widget(cls, widget_type: str, widget: QWidget) -> None:
        """Return widget to pool for reuse"""
        pool = cls._pools.setdefault(widget_type, [])
        if len(pool) < 50:  # Limit pool size
            if hasattr(widget, 'reset') and callable(getattr(widget, 'reset')):
                getattr(widget, 'reset')()
            pool.append(widget)


# Performance helper functions
def batch_widget_updates(widgets: Sequence[QWidget]):
    """Context manager for batch widget updates"""
    for widget in widgets:
        widget.setUpdatesEnabled(False)
    try:
        yield
    finally:
        for widget in widgets:
            widget.setUpdatesEnabled(True)
            widget.update()


class OptimizedFluentCalendar(QWidget):
    """
    Modern calendar widget with Fluent Design styling - Optimized

    Features:
    - Month/year navigation with smooth animations
    - Today highlighting with dynamic theming
    - Selected date highlighting with state management
    - Weekend highlighting with configurable colors
    - Hover effects with micro-interactions
    - Smooth animations with easing curves
    - Performance optimizations with caching
    - Enhanced accessibility support
    """

    # Signals with type hints
    dateClicked = Signal(QDate)
    dateSelected = Signal(QDate)
    monthChanged = Signal(int, int)  # month, year

    # Class constants
    ANIMATION_DURATION: Final[int] = 200
    GRID_SIZE: Final[tuple[int, int]] = (6, 7)

    # Cache for month names to avoid repeated lookups
    _month_names_cache: ClassVar[Dict[str, List[str]]] = {}
    _day_names_cache: ClassVar[Dict[str, List[str]]] = {}

    def __init__(self, parent: Optional[QWidget] = None, config: Optional[CalendarConfig] = None):
        super().__init__(parent)

        # Configuration
        self._config = config or CalendarConfig()

        # State management with dataclass-like approach
        self._state = self._create_initial_state()

        # Performance optimization: weak references for cleanup
        self._day_buttons: List[List[CalendarDayButton]] = []
        self._animation_group: Optional[QPropertyAnimation] = None

        # Cache for frequently accessed values
        self._cached_theme: Optional[CalendarTheme] = None
        self._layout_cache: Dict[str, Any] = {}

        # Setup UI and animations
        self._setup_ui()
        self._setup_animations()
        self._apply_theme()

        # Connect to theme manager if available
        if THEME_AVAILABLE and theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _create_initial_state(self) -> Dict[str, Any]:
        """Create initial state dictionary"""
        today = QDate.currentDate()
        return {
            'selected_date': today,
            'today': today,
            'current_month': today.month(),
            'current_year': today.year(),
            'hovered_date': None,
            'is_animating': False,
        }

    @cached_property
    def month_names(self) -> List[str]:
        """Get cached month names based on locale"""
        locale_key = self._config.locale
        if locale_key not in self._month_names_cache:
            if self._config.locale == "zh_CN":
                self._month_names_cache[locale_key] = [
                    "一月", "二月", "三月", "四月", "五月", "六月",
                    "七月", "八月", "九月", "十月", "十一月", "十二月"
                ]
            else:
                # Default to English
                self._month_names_cache[locale_key] = [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ]
        return self._month_names_cache[locale_key]

    @cached_property
    def day_names(self) -> List[str]:
        """Get cached day names based on locale"""
        locale_key = self._config.locale
        if locale_key not in self._day_names_cache:
            if self._config.locale == "zh_CN":
                self._day_names_cache[locale_key] = [
                    "周日", "周一", "周二", "周三", "周四", "周五", "周六"]
            else:
                self._day_names_cache[locale_key] = [
                    "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        return self._day_names_cache[locale_key]

    def _setup_ui(self) -> None:
        """Setup the calendar UI with optimized layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header with navigation
        self._setup_header(layout)

        # Day of week labels
        self._setup_day_labels(layout)

        # Calendar grid
        self._setup_calendar_grid(layout)        # Initial calendar update
        self._update_calendar()

    def _setup_animations(self) -> None:
        """Setup enhanced animation system"""
        if not ANIMATIONS_AVAILABLE or not self._config.enable_animations:
            return

        # Setup state transitions with modern easing
        self._state_transition = FluentStateTransition
    def _setup_header(self, layout: QVBoxLayout) -> None:
        """Setup header with month/year navigation"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # Previous month button with enhanced styling
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(32, 32)
        self.prev_btn.setToolTip("Previous month")
        self.prev_btn.clicked.connect(self._previous_month)
        header_layout.addWidget(self.prev_btn)

        # Month/Year display with better typography
        self.month_year_label = QLabel()
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        self.month_year_label.setFont(font)
        self.month_year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.month_year_label, 1)

        # Next month button
        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(32, 32)
        self.next_btn.setToolTip("Next month")
        self.next_btn.clicked.connect(self._next_month)
        header_layout.addWidget(self.next_btn)

        layout.addLayout(header_layout)

    def _setup_day_labels(self, layout: QVBoxLayout) -> None:
        """Setup day of week labels with proper internationalization"""
        days_layout = QHBoxLayout()
        days_layout.setSpacing(0)

        for day_name in self.day_names:
            label = QLabel(day_name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedHeight(32)
            font = QFont()
            font.setWeight(QFont.Weight.Bold)
            label.setFont(font)
            days_layout.addWidget(label)

        layout.addLayout(days_layout)

    def _setup_calendar_grid(self, layout: QVBoxLayout) -> None:
        """Setup calendar grid with optimized button creation"""
        self.calendar_widget = QWidget()
        self.calendar_layout = QGridLayout(self.calendar_widget)
        self.calendar_layout.setSpacing(2)
        self.calendar_layout.setContentsMargins(0, 0, 0, 0)

        # Create 6x7 grid for calendar days with object pooling
        self._day_buttons = []
        for row in range(self.GRID_SIZE[0]):
            button_row = []
            for col in range(self.GRID_SIZE[1]):
                btn = CalendarDayButton(config=self._config)
                btn.setFixedSize(40, 40)
                btn.clicked.connect(self._on_day_clicked)
                self.calendar_layout.addWidget(btn, row, col)
                button_row.append(btn)
            self._day_buttons.append(button_row)

        layout.addWidget(self.calendar_widget)

    @Slot()
    def _update_calendar(self) -> None:
        """Update calendar display with optimized rendering"""
        # Update month/year label with cached values
        month_name = self.month_names[self._state['current_month'] - 1]
        self.month_year_label.setText(
            f"{self._state['current_year']}年 {month_name}")

        # Get first day of month with proper calendar calculation
        first_day = QDate(self._state['current_year'],
                          self._state['current_month'], 1)
        days_in_month = first_day.daysInMonth()
        start_day = (first_day.dayOfWeek() +
                     (7 - self._config.first_day_of_week)) % 7

        # Batch update for better performance
        self._batch_update_day_buttons(days_in_month, start_day)

        # Apply theme after update
        self._apply_theme()

        # Emit month changed signal
        self.monthChanged.emit(
            self._state['current_month'], self._state['current_year'])

    def _batch_update_day_buttons(self, days_in_month: int, start_day: int) -> None:
        """Batch update day buttons for better performance"""
        day = 1
        today = self._state['today']
        selected_date = self._state['selected_date']

        for row in range(self.GRID_SIZE[0]):
            for col in range(self.GRID_SIZE[1]):
                btn = self._day_buttons[row][col]
                cell_index = row * 7 + col

                if cell_index < start_day or day > days_in_month:
                    btn.setVisible(False)
                    btn.reset()
                else:
                    btn.setVisible(True)

                    # Create current date for comparison
                    current_date = QDate(
                        self._state['current_year'],
                        self._state['current_month'],
                        day
                    )

                    # Update button state efficiently
                    btn.update_state(
                        day=day,
                        is_today=(current_date == today),
                        is_selected=(current_date == selected_date),
                        is_weekend=(col == 0 or col ==
                                    6) and self._config.weekend_highlighting
                    )

                    day += 1

    @Slot()
    def _on_day_clicked(self) -> None:
        """Handle day button click with enhanced feedback"""
        sender = self.sender()
        if not isinstance(sender, CalendarDayButton) or sender.day() <= 0:
            return

        selected_date = QDate(
            self._state['current_year'],
            self._state['current_month'],
            sender.day()
        )

        # Update state
        self._state['selected_date'] = selected_date

        # Add micro-interaction
        if ANIMATIONS_AVAILABLE and self._config.enable_animations:
            FluentMicroInteraction.pulse_animation(sender, scale=1.1)

        # Update calendar and emit signals
        self._update_calendar()
        self.dateClicked.emit(selected_date)
        self.dateSelected.emit(selected_date)

    @Slot()
    def _previous_month(self) -> None:
        """Go to previous month with animation"""
        if self._state['current_month'] == 1:
            self._state['current_month'] = 12
            self._state['current_year'] -= 1
        else:
            self._state['current_month'] -= 1

        self._animate_month_change("left")
        self._update_calendar()

    @Slot()
    def _next_month(self) -> None:
        """Go to next month with animation"""
        if self._state['current_month'] == 12:
            self._state['current_month'] = 1
            self._state['current_year'] += 1
        else:
            self._state['current_month'] += 1

        self._animate_month_change("right")
        self._update_calendar()

    def _animate_month_change(self, direction: str) -> None:
        """Animate month change transition"""
        if not ANIMATIONS_AVAILABLE or not self._config.enable_animations:
            return

        # Prevent multiple simultaneous animations
        if self._state['is_animating']:
            return

        self._state['is_animating'] = True
        # Create slide animation with error handling
        with suppress(Exception):
            # Check if the animation class has the required method
            if (hasattr(FluentMicroInteraction, 'slide_animation') and
                    callable(getattr(FluentMicroInteraction, 'slide_animation', None))):
                slide_anim = getattr(FluentMicroInteraction, 'slide_animation', None)
                if callable(slide_anim):
                    slide_anim(
                        self.calendar_widget,
                        direction=direction,
                        duration=self.ANIMATION_DURATION
                    )

        # Reset animation state after completion
        QTimer.singleShot(self.ANIMATION_DURATION, self._reset_animation_state)

    @Slot()
    def _reset_animation_state(self) -> None:
        """Reset animation state"""
        self._state['is_animating'] = False

    # Public API methods with type safety
    def selectedDate(self) -> QDate:
        """Get selected date"""
        return self._state['selected_date']

    def setSelectedDate(self, date: QDate) -> None:
        """Set selected date with validation"""
        if not date.isValid():
            return

        self._state['selected_date'] = date
        self._state['current_month'] = date.month()
        self._state['current_year'] = date.year()
        self._update_calendar()

    def currentMonth(self) -> int:
        """Get current month (1-12)"""
        return self._state['current_month']

    def currentYear(self) -> int:
        """Get current year"""
        return self._state['current_year']

    def setCurrentMonthYear(self, month: int, year: int) -> None:
        """Set current month and year with validation"""
        if not (1 <= month <= 12) or year < 1900 or year > 2100:
            return

        self._state['current_month'] = month
        self._state['current_year'] = year
        self._update_calendar()

    @Slot()
    def _on_theme_changed(self) -> None:
        """Handle theme change with cached theme invalidation"""
        self._cached_theme = None
        self._apply_theme()

    def _get_theme_colors(self) -> CalendarTheme:
        """Get theme colors with caching"""
        if self._cached_theme is not None:
            return self._cached_theme

        if THEME_AVAILABLE and theme_manager:
            try:
                self._cached_theme = CalendarTheme(
                    surface_color=theme_manager.get_color('surface').name(),
                    primary_color=theme_manager.get_color('primary').name(),
                    text_color=theme_manager.get_color('on_surface').name(),
                    border_color=theme_manager.get_color('outline').name(),
                    today_color=theme_manager.get_color(
                        'secondary_container').name(),
                    weekend_color=theme_manager.get_color('error').name(),
                    hover_color=theme_manager.get_color(
                        'surface_variant').name(),
                    selected_color=theme_manager.get_color('primary').name(),
                )
            except (AttributeError, KeyError):
                # Fallback to default theme
                self._cached_theme = CalendarTheme()
        else:
            self._cached_theme = CalendarTheme()

        return self._cached_theme

    def _apply_theme(self) -> None:
        """Apply current theme with performance optimization"""
        theme = self._get_theme_colors()

        # Apply theme to main widget
        self.setStyleSheet(f"""
            OptimizedFluentCalendar {{
                background-color: {theme.surface_color};
                border: 1px solid {theme.border_color};
                border-radius: 12px;
            }}
            QPushButton {{
                background-color: {theme.hover_color};
                color: {theme.text_color};
                border: none;
                border-radius: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme.primary_color};
                color: white;
            }}
            QLabel {{
                color: {theme.text_color};
            }}
        """)

        # Update day buttons theme in batch
        for row in self._day_buttons:
            for btn in row:
                btn.apply_theme(theme)

    # Context manager for batch operations
    @contextmanager
    def batch_update(self):
        """Context manager for batch updates"""
        old_updates = self.updatesEnabled()
        self.setUpdatesEnabled(False)
        try:
            yield
        finally:
            self.setUpdatesEnabled(old_updates)
            if old_updates:
                self.update()

    def __del__(self):
        """Cleanup method"""
        # Clean up weak references and animations
        if hasattr(self, '_animation_group') and self._animation_group:
            self._animation_group.stop()

        # Clear caches
        self._layout_cache.clear()


class CalendarDayButton(QPushButton):
    """Individual day button for calendar - Optimized

    Features:
    - Enhanced state management with dataclass-like approach
    - Performance optimizations with cached properties
    - Modern animation support
    - Improved theming system
    - Better accessibility support
    """

    # State management using slots for memory efficiency
    __slots__ = ['_day', '_state', '_config',
                 '_cached_style', '_animation_timer']

    def __init__(self, config: Optional[CalendarConfig] = None):
        super().__init__()

        # Configuration
        self._config = config or CalendarConfig()

        # State management - using dict for flexibility
        self._state = {
            'day': 0,
            'is_today': False,
            'is_selected': False,
            'is_weekend': False,
            'is_hovered': False,
            'is_animating': False
        }

        # Performance optimizations
        self._cached_style: Optional[str] = None
        self._animation_timer: Optional[QTimer] = None

        # Setup
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def update_state(self, *, day: int, is_today: bool = False,
                     is_selected: bool = False, is_weekend: bool = False) -> None:
        """Update button state efficiently with keyword-only arguments"""
        # Batch state updates for better performance
        old_state = self._state.copy()

        self._state.update({
            'day': day,
            'is_today': is_today,
            'is_selected': is_selected,
            'is_weekend': is_weekend
        })

        # Only update UI if state actually changed
        if old_state != self._state:
            self.setText(str(day))
            self._invalidate_style_cache()
            self._apply_cached_theme()

    def day(self) -> int:
        """Get day number"""
        return self._state['day']

    def setDay(self, day: int) -> None:
        """Set day number (backward compatibility)"""
        self.update_state(day=day)

    def setIsToday(self, is_today: bool) -> None:
        """Set if this is today (backward compatibility)"""
        self.update_state(
            day=self._state['day'],
            is_today=is_today,
            is_selected=self._state['is_selected'],
            is_weekend=self._state['is_weekend']
        )

    def setIsSelected(self, is_selected: bool) -> None:
        """Set if this is selected (backward compatibility)"""
        self.update_state(
            day=self._state['day'],
            is_today=self._state['is_today'],
            is_selected=is_selected,
            is_weekend=self._state['is_weekend']
        )

    def setIsWeekend(self, is_weekend: bool) -> None:
        """Set if this is weekend (backward compatibility)"""
        self.update_state(
            day=self._state['day'],
            is_today=self._state['is_today'],
            is_selected=self._state['is_selected'],
            is_weekend=is_weekend
        )

    def reset(self) -> None:
        """Reset button state efficiently"""
        self._state = {
            'day': 0,
            'is_today': False,
            'is_selected': False,
            'is_weekend': False,
            'is_hovered': False,
            'is_animating': False
        }
        self.setText("")
        self._invalidate_style_cache()

    def enterEvent(self, event) -> None:
        """Handle mouse enter with enhanced animations"""
        self._state['is_hovered'] = True

        # Add hover animation if available
        if (ANIMATIONS_AVAILABLE and self._config.enable_animations
                and not self._state['is_animating']):
            self._animate_hover(True)

        self._apply_cached_theme()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Handle mouse leave"""
        self._state['is_hovered'] = False

        # Add leave animation if available
        if (ANIMATIONS_AVAILABLE and self._config.enable_animations
                and not self._state['is_animating']):
            self._animate_hover(False)

        self._apply_cached_theme()
        super().leaveEvent(event)

    def _animate_hover(self, enter: bool) -> None:
        """Animate hover state with micro-interactions"""
        if not ANIMATIONS_AVAILABLE:
            return

        self._state['is_animating'] = True
        # Use scale animation for hover feedback
        scale = 1.05 if enter else 1.0
        with suppress(Exception):
            # Check if the animation class has the required method
            if (hasattr(FluentMicroInteraction, 'scale_animation') and
                    callable(getattr(FluentMicroInteraction, 'scale_animation', None))):
                FluentMicroInteraction.scale_animation(self, scale=scale)

        # Reset animation state after completion
        if self._animation_timer:
            self._animation_timer.stop()

        self._animation_timer = QTimer()
        self._animation_timer.setSingleShot(True)
        self._animation_timer.timeout.connect(
            lambda: setattr(self._state, 'is_animating', False))
        self._animation_timer.start(150)

    def _invalidate_style_cache(self) -> None:
        """Invalidate cached style"""
        self._cached_style = None

    def _generate_style(self, theme: CalendarTheme) -> str:
        """Generate style string based on current state and theme"""
        if not self.isVisible() or self._state['day'] == 0:
            return ""

        # Determine colors based on state priority
        bg_color = theme.surface_color
        text_color = theme.text_color
        font_weight = "normal"

        # Apply state-based styling with proper priority
        if self._state['is_selected']:
            bg_color = theme.selected_color
            text_color = "white"
            font_weight = "bold"
        elif self._state['is_today']:
            bg_color = theme.today_color
            text_color = theme.text_color
            font_weight = "bold"
        elif self._state['is_hovered']:
            bg_color = theme.hover_color
            text_color = theme.text_color

        # Weekend styling (if not overridden by selection/today)
        if (self._state['is_weekend'] and not self._state['is_selected']
                and not self._state['is_today']):
            text_color = theme.weekend_color

        return f"""
            CalendarDayButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 20px;
                font-weight: {font_weight};
                padding: 2px;
            }}
            CalendarDayButton:hover {{
                background-color: {theme.hover_color};
            }}
        """

    def apply_theme(self, theme: Optional[CalendarTheme] = None) -> None:
        """Apply theme with caching optimization"""
        if theme is None:
            # Use default theme if none provided
            theme = CalendarTheme()

        # Use cached style if available and state hasn't changed
        if self._cached_style is None:
            self._cached_style = self._generate_style(theme)

        self.setStyleSheet(self._cached_style)

    def _apply_cached_theme(self) -> None:
        """Apply theme using cached values"""
        self._invalidate_style_cache()
        self.apply_theme()

    def sizeHint(self) -> QSize:
        """Provide optimized size hint"""
        return QSize(40, 40)

    def minimumSizeHint(self) -> QSize:
        """Provide minimum size hint"""
        return QSize(32, 32)

    def __del__(self):
        """Cleanup method"""
        if self._animation_timer:
            self._animation_timer.stop()


class OptimizedFluentDatePicker(QWidget):
    """
    Modern date picker widget with calendar popup - Optimized

    Features:
    - Input field with date formatting and validation
    - Calendar popup with enhanced positioning
    - Keyboard navigation support
    - Date validation with user feedback
    - Performance optimizations
    - Enhanced accessibility
    """

    # Signals with type hints
    dateChanged = Signal(QDate)
    validationError = Signal(str)  # New signal for validation errors

    def __init__(self, parent: Optional[QWidget] = None, config: Optional[CalendarConfig] = None):
        super().__init__(parent)

        # Configuration
        self._config = config or CalendarConfig()

        # State management
        self._date = QDate.currentDate()
        self._format = self._config.date_format
        self._is_popup_visible = False

        # Performance optimization
        self._cached_popup: Optional[CalendarPopup] = None

        self._setup_ui()
        self._apply_theme()

        # Connect to theme manager if available
        if THEME_AVAILABLE and theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self) -> None:
        """Setup the date picker UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Date input field with enhanced validation
        self.date_edit = QLineEdit()
        self.date_edit.setText(self._date.toString(self._format))
        self.date_edit.textChanged.connect(self._on_text_changed)
        self.date_edit.returnPressed.connect(self._on_return_pressed)
        self.date_edit.setPlaceholderText(self._format.replace(
            'y', 'Y').replace('d', 'D').replace('M', 'M'))
        layout.addWidget(self.date_edit)

        # Calendar button with better icon
        self.calendar_btn = QPushButton("📅")
        self.calendar_btn.setFixedSize(32, 32)
        self.calendar_btn.setToolTip("Open calendar")
        self.calendar_btn.clicked.connect(self._show_calendar)
        layout.addWidget(self.calendar_btn)

    @Slot()
    def _show_calendar(self) -> None:
        """Show calendar popup with lazy initialization"""
        if self._is_popup_visible:
            return

        # Lazy initialization of popup
        if self._cached_popup is None:
            self._cached_popup = CalendarPopup(self, config=self._config)
            self._cached_popup.calendar.dateSelected.connect(
                self._on_date_selected)

        self._cached_popup.setDate(self._date)
        self._cached_popup.show_at_widget(self)
        self._is_popup_visible = True

    @Slot(QDate)
    def _on_date_selected(self, date: QDate) -> None:
        """Handle date selection from calendar"""
        self.setDate(date)
        if self._cached_popup:
            self._cached_popup.hide()
        self._is_popup_visible = False

    @Slot()
    def _on_text_changed(self, text: str) -> None:
        """Handle text change in input field with validation"""
        if not text.strip():
            return

        try:
            date = QDate.fromString(text, self._format)
            if date.isValid():
                self._date = date
                self.dateChanged.emit(date)
                # Clear any previous validation styling
                self._apply_theme()
            else:
                # Apply error styling
                self._apply_error_styling()
                self.validationError.emit(
                    f"Invalid date format. Expected: {self._format}")
        except Exception as e:
            self._apply_error_styling()
            self.validationError.emit(f"Date parsing error: {str(e)}")

    @Slot()
    def _on_return_pressed(self) -> None:
        """Handle return key press"""
        # Validate and format the current text
        current_text = self.date_edit.text()
        try:
            date = QDate.fromString(current_text, self._format)
            if date.isValid():
                self.setDate(date)  # This will format the text properly
        except:
            # Revert to last valid date
            self.date_edit.setText(self._date.toString(self._format))

    def _apply_error_styling(self) -> None:
        """Apply error styling to input field"""
        error_color = "#FF6B6B"  # Red color for errors
        self.date_edit.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {error_color};
                background-color: #FFF5F5;
            }}
        """)

    # Public API with enhanced type safety
    def date(self) -> QDate:
        """Get current date"""
        return self._date

    def setDate(self, date: QDate) -> None:
        """Set current date with validation"""
        if not date.isValid():
            return

        self._date = date
        self.date_edit.setText(date.toString(self._format))
        self.dateChanged.emit(date)
        self._apply_theme()  # Reset styling

    def format(self) -> str:
        """Get date format"""
        return self._format

    def setFormat(self, format_str: str) -> None:
        """Set date format with validation"""
        if not format_str.strip():
            return

        self._format = format_str
        self.date_edit.setText(self._date.toString(self._format))
        self.date_edit.setPlaceholderText(format_str.replace(
            'y', 'Y').replace('d', 'D').replace('M', 'M'))

    @Slot()
    def _on_theme_changed(self) -> None:
        """Handle theme change"""
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Apply current theme with fallback colors"""
        # Default colors as fallback
        bg_color = "#FFFFFF"
        text_color = "#000000"
        primary_color = "#0078D4"
        border_color = "#D1D1D1"

        # Use theme colors if available
        if THEME_AVAILABLE and theme_manager:
            try:
                bg_color = theme_manager.get_color('surface').name()
                text_color = theme_manager.get_color('on_surface').name()
                primary_color = theme_manager.get_color('primary').name()
                border_color = theme_manager.get_color('outline').name()
            except (AttributeError, KeyError):
                pass  # Use default colors

        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {primary_color};
            }}
            QPushButton {{
                background-color: {primary_color};
                color: white;
                border: none;
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background-color: {primary_color};
                opacity: 0.8;
            }}
        """)

    def closeEvent(self, event) -> None:
        """Handle close event"""
        if self._cached_popup and self._cached_popup.isVisible():
            self._cached_popup.hide()
        super().closeEvent(event)


class CalendarPopup(QWidget):
    """Calendar popup window - Optimized"""

    def __init__(self, parent: Optional[QWidget] = None, config: Optional[CalendarConfig] = None):
        super().__init__(parent)

        # Configuration
        self._config = config or CalendarConfig()

        # Setup window properties
        self.setWindowFlags(Qt.WindowType.Popup |
                            Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._setup_ui()
        self._apply_theme()

        # Connect to theme manager if available
        if THEME_AVAILABLE and theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self) -> None:
        """Setup popup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Shadow frame
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.Shape.Box)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        # Calendar with optimized configuration
        self.calendar = OptimizedFluentCalendar(config=self._config)
        frame_layout.addWidget(self.calendar)

        layout.addWidget(self.frame)

    def setDate(self, date: QDate) -> None:
        """Set calendar date"""
        self.calendar.setSelectedDate(date)

    def show_at_widget(self, widget: QWidget) -> None:
        """Show popup below the given widget with smart positioning"""
        # Calculate optimal position
        global_pos = widget.mapToGlobal(widget.rect().bottomLeft())

        # Ensure popup stays within screen bounds
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            popup_size = self.sizeHint()

            # Adjust horizontal position if needed
            if global_pos.x() + popup_size.width() > screen_geometry.right():
                global_pos.setX(screen_geometry.right() - popup_size.width())

            # Adjust vertical position if needed (show above widget if no space below)
            if global_pos.y() + popup_size.height() > screen_geometry.bottom():
                global_pos = widget.mapToGlobal(widget.rect().topLeft())
                global_pos.setY(global_pos.y() - popup_size.height())

        self.move(global_pos.x(), global_pos.y() + 4)
        self.show()

        # Add entrance animation if available
        if ANIMATIONS_AVAILABLE and self._config.enable_animations:
            FluentRevealEffect.fade_in(self, duration=200)

    @Slot()
    def _on_theme_changed(self) -> None:
        """Handle theme change"""
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Apply current theme"""
        # Default colors as fallback
        surface_color = "#FFFFFF"
        border_color = "#D1D1D1"

        # Use theme colors if available
        if THEME_AVAILABLE and theme_manager:
            try:
                surface_color = theme_manager.get_color('surface').name()
                border_color = theme_manager.get_color('outline').name()
            except (AttributeError, KeyError):
                pass

        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: {surface_color};
                border: 1px solid {border_color};
                border-radius: 12px;
            }}
        """)


class OptimizedFluentTimePicker(QWidget):
    """
    Modern time picker widget - Optimized

    Features:
    - Hour/minute/second selection with validation
    - 12/24 hour format support
    - Enhanced spin box controls
    - Time validation with user feedback
    - Performance optimizations
    - Accessibility improvements
    """

    # Signals
    timeChanged = Signal(QTime)
    validationError = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None, config: Optional[CalendarConfig] = None):
        super().__init__(parent)

        # Configuration
        self._config = config or CalendarConfig()

        # State management
        self._time = QTime.currentTime()
        self._use_24_hour = True
        self._show_seconds = False

        # Performance optimization - cache control references
        self._controls_cache: Dict[str, QWidget] = {}

        self._setup_ui()
        self._apply_theme()

        # Connect to theme manager if available
        if THEME_AVAILABLE and theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self) -> None:
        """Setup time picker UI with optimized controls"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Hour spinbox
        self.hour_spin = QSpinBox()
        self.hour_spin.setMinimum(0 if self._use_24_hour else 1)
        self.hour_spin.setMaximum(23 if self._use_24_hour else 12)
        self.hour_spin.setValue(self._time.hour())
        self.hour_spin.valueChanged.connect(self._on_time_changed)
        self.hour_spin.setToolTip("Hour")
        layout.addWidget(self.hour_spin)
        self._controls_cache['hour_spin'] = self.hour_spin

        layout.addWidget(QLabel(":"))

        # Minute spinbox
        self.minute_spin = QSpinBox()
        self.minute_spin.setMinimum(0)
        self.minute_spin.setMaximum(59)
        self.minute_spin.setValue(self._time.minute())
        self.minute_spin.valueChanged.connect(self._on_time_changed)
        self.minute_spin.setToolTip("Minute")
        layout.addWidget(self.minute_spin)
        self._controls_cache['minute_spin'] = self.minute_spin

        # Second spinbox (optional)
        self.second_label = QLabel(":")
        self.second_spin = QSpinBox()
        self.second_spin.setMinimum(0)
        self.second_spin.setMaximum(59)
        self.second_spin.setValue(self._time.second())
        self.second_spin.valueChanged.connect(self._on_time_changed)
        self.second_spin.setToolTip("Second")

        layout.addWidget(self.second_label)
        layout.addWidget(self.second_spin)
        self._controls_cache['second_spin'] = self.second_spin
        self._controls_cache['second_label'] = self.second_label

        # AM/PM combo (for 12-hour format)
        self.ampm_combo = QComboBox()
        self.ampm_combo.addItems(["AM", "PM"])
        self.ampm_combo.currentTextChanged.connect(self._on_time_changed)
        self.ampm_combo.setToolTip("AM/PM")
        layout.addWidget(self.ampm_combo)
        self._controls_cache['ampm_combo'] = self.ampm_combo

        # Update visibility based on configuration
        self._update_format()

    @Slot()
    def _on_time_changed(self) -> None:
        """Handle time change with validation"""
        try:
            hour = self.hour_spin.value()
            minute = self.minute_spin.value()
            second = self.second_spin.value() if self._show_seconds else 0

            # Handle AM/PM conversion for 12-hour format
            if not self._use_24_hour:
                is_pm = self.ampm_combo.currentText() == "PM"
                if hour == 12:
                    hour = 0 if not is_pm else 12
                elif is_pm and hour < 12:
                    hour += 12

            new_time = QTime(hour, minute, second)
            if new_time.isValid():
                self._time = new_time
                self.timeChanged.emit(new_time)
            else:
                self.validationError.emit(
                    f"Invalid time: {hour:02d}:{minute:02d}:{second:02d}")

        except Exception as e:
            self.validationError.emit(f"Time parsing error: {str(e)}")

    # Public API with enhanced type safety
    def time(self) -> QTime:
        """Get current time"""
        return self._time

    def setTime(self, time: QTime) -> None:
        """Set current time with validation"""
        if not time.isValid():
            return

        self._time = time
        self._update_controls()

    def use24HourFormat(self) -> bool:
        """Check if using 24-hour format"""
        return self._use_24_hour

    def setUse24HourFormat(self, use_24_hour: bool) -> None:
        """Set 24-hour format usage"""
        self._use_24_hour = use_24_hour
        self._update_format()
        self._update_controls()

    def showSeconds(self) -> bool:
        """Check if showing seconds"""
        return self._show_seconds

    def setShowSeconds(self, show_seconds: bool) -> None:
        """Set seconds visibility"""
        self._show_seconds = show_seconds
        self._update_format()
        self._update_controls()

    def _update_format(self) -> None:
        """Update format-related UI with cached controls"""        # Update hour range
        hour_spin = self._controls_cache.get('hour_spin')
        if hour_spin and isinstance(hour_spin, QSpinBox):
            hour_spin.setMinimum(0 if self._use_24_hour else 1)
            hour_spin.setMaximum(23 if self._use_24_hour else 12)

        # Show/hide seconds with cached references
        second_label = self._controls_cache.get('second_label')
        second_spin = self._controls_cache.get('second_spin')
        if second_label and second_spin:
            second_label.setVisible(self._show_seconds)
            second_spin.setVisible(self._show_seconds)

        # Show/hide AM/PM
        ampm_combo = self._controls_cache.get('ampm_combo')
        if ampm_combo:
            ampm_combo.setVisible(not self._use_24_hour)

    def _update_controls(self) -> None:
        """Update control values efficiently"""
        hour = self._time.hour()

        # Block signals during batch update
        with self._signal_blocker():
            if self._use_24_hour:
                self.hour_spin.setValue(hour)
            else:
                # Convert to 12-hour format
                display_hour = hour % 12
                if display_hour == 0:  # Midnight or Noon
                    display_hour = 12
                self.hour_spin.setValue(display_hour)

                if hour < 12:
                    self.ampm_combo.setCurrentText("AM")
                else:
                    self.ampm_combo.setCurrentText("PM")

            self.minute_spin.setValue(self._time.minute())
            self.second_spin.setValue(self._time.second())

    @contextmanager
    def _signal_blocker(self):
        """Context manager to block signals during batch updates"""
        controls = [self.hour_spin, self.minute_spin,
                    self.second_spin, self.ampm_combo]

        # Block signals
        for control in controls:
            control.blockSignals(True)

        try:
            yield
        finally:
            # Restore signals
            for control in controls:
                control.blockSignals(False)

    @Slot()
    def _on_theme_changed(self) -> None:
        """Handle theme change"""
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Apply current theme with fallback colors"""
        # Default colors as fallback
        bg_color = "#FFFFFF"
        text_color = "#000000"
        primary_color = "#0078D4"
        border_color = "#D1D1D1"

        # Use theme colors if available
        if THEME_AVAILABLE and theme_manager:
            try:
                bg_color = theme_manager.get_color('surface').name()
                text_color = theme_manager.get_color('on_surface').name()
                primary_color = theme_manager.get_color('primary').name()
                border_color = theme_manager.get_color('outline').name()
            except (AttributeError, KeyError):
                pass

        self.setStyleSheet(f"""
            QSpinBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 4px;
                min-width: 40px;
            }}
            QSpinBox:focus {{
                border-color: {primary_color};
            }}
            QComboBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 4px;
                min-width: 50px;
            }}
            QComboBox:focus {{
                border-color: {primary_color};
            }}
            QLabel {{
                color: {text_color};
                font-weight: bold;
            }}
        """)


class OptimizedFluentDateTimePicker(QWidget):
    """
    Combined date and time picker widget - Optimized

    Features:
    - Date picker with calendar integration
    - Time picker with enhanced controls
    - Combined datetime output with validation
    - Flexible formatting options
    - Performance optimizations
    - Enhanced accessibility
    """

    # Signals with type hints
    dateTimeChanged = Signal(QDateTime)
    dateChanged = Signal(QDate)
    timeChanged = Signal(QTime)
    validationError = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None, config: Optional[CalendarConfig] = None):
        super().__init__(parent)

        # Configuration
        self._config = config or CalendarConfig()

        # State management
        self._datetime = QDateTime.currentDateTime()

        # Performance optimization - cache child widgets
        self._widget_cache: Dict[str, QWidget] = {}

        self._setup_ui()
        # Theme is applied by child components

    def _setup_ui(self) -> None:
        """Setup datetime picker UI with optimized layout"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Date picker
        self.date_picker = OptimizedFluentDatePicker(config=self._config)
        self.date_picker.setDate(self._datetime.date())
        self.date_picker.dateChanged.connect(self._on_date_changed)
        self.date_picker.validationError.connect(self.validationError.emit)
        layout.addWidget(self.date_picker)
        self._widget_cache['date_picker'] = self.date_picker

        # Time picker
        self.time_picker = OptimizedFluentTimePicker(config=self._config)
        self.time_picker.setTime(self._datetime.time())
        self.time_picker.timeChanged.connect(self._on_time_changed)
        self.time_picker.validationError.connect(self.validationError.emit)
        layout.addWidget(self.time_picker)
        self._widget_cache['time_picker'] = self.time_picker

    @Slot(QDate)
    def _on_date_changed(self, date: QDate) -> None:
        """Handle date change efficiently"""
        current_time = self._datetime.time()
        self._datetime = QDateTime(date, current_time)
        self.dateChanged.emit(date)
        self.dateTimeChanged.emit(self._datetime)

    @Slot(QTime)
    def _on_time_changed(self, time: QTime) -> None:
        """Handle time change efficiently"""
        current_date = self._datetime.date()
        self._datetime = QDateTime(current_date, time)
        self.timeChanged.emit(time)
        self.dateTimeChanged.emit(self._datetime)

    # Public API with enhanced type safety and validation
    def dateTime(self) -> QDateTime:
        """Get current datetime"""
        return self._datetime

    def setDateTime(self, datetime: QDateTime) -> None:
        """Set current datetime with validation"""
        if not datetime.isValid():
            return

        self._datetime = datetime

        # Update child components efficiently
        with self._batch_update():
            self.date_picker.setDate(datetime.date())
            self.time_picker.setTime(datetime.time())

    def date(self) -> QDate:
        """Get current date"""
        return self._datetime.date()

    def setDate(self, date: QDate) -> None:
        """Set current date"""
        if not date.isValid():
            return

        current_time = self._datetime.time()
        self.setDateTime(QDateTime(date, current_time))

    def time(self) -> QTime:
        """Get current time"""
        return self._datetime.time()

    def setTime(self, time: QTime) -> None:
        """Set current time"""
        if not time.isValid():
            return

        current_date = self._datetime.date()
        self.setDateTime(QDateTime(current_date, time))

    # Time picker delegation methods
    def use24HourFormat(self) -> bool:
        """Check if using 24-hour format"""
        return self.time_picker.use24HourFormat()

    def setUse24HourFormat(self, use_24_hour: bool) -> None:
        """Set 24-hour format usage"""
        self.time_picker.setUse24HourFormat(use_24_hour)

    def showSeconds(self) -> bool:
        """Check if showing seconds"""
        return self.time_picker.showSeconds()

    def setShowSeconds(self, show_seconds: bool) -> None:
        """Set seconds visibility"""
        self.time_picker.setShowSeconds(show_seconds)

    # Date picker delegation methods
    def dateFormat(self) -> str:
        """Get date format"""
        return self.date_picker.format()

    def setDateFormat(self, format_str: str) -> None:
        """Set date format"""
        self.date_picker.setFormat(format_str)

    @contextmanager
    def _batch_update(self):
        """Context manager for batch updates to prevent multiple signal emissions"""
        # Block child widget signals temporarily
        self.date_picker.dateChanged.disconnect()
        self.time_picker.timeChanged.disconnect()

        try:
            yield
        finally:
            # Reconnect signals
            self.date_picker.dateChanged.connect(self._on_date_changed)
            self.time_picker.timeChanged.connect(self._on_time_changed)

    def sizeHint(self) -> QSize:
        """Provide optimized size hint"""
        date_hint = self.date_picker.sizeHint()
        time_hint = self.time_picker.sizeHint()
        return QSize(date_hint.width() + time_hint.width() + 12,
                     max(date_hint.height(), time_hint.height()))


# Backward compatibility aliases
FluentCalendar = OptimizedFluentCalendar
FluentDatePicker = OptimizedFluentDatePicker
FluentTimePicker = OptimizedFluentTimePicker
FluentDateTimePicker = OptimizedFluentDateTimePicker


# Export all classes with backward compatibility
__all__ = [
    # Optimized classes
    'OptimizedFluentCalendar',
    'OptimizedFluentDatePicker',
    'OptimizedFluentTimePicker',
    'OptimizedFluentDateTimePicker',

    # Backward compatibility aliases
    'FluentCalendar',
    'FluentDatePicker',
    'FluentTimePicker',
    'FluentDateTimePicker',

    # Supporting classes
    'CalendarDayButton',
    'CalendarPopup',

    # Configuration and theme classes
    'CalendarConfig',
    'CalendarTheme',
    'CalendarStateType',

    # Type aliases
    'DateLike',
    'TimeLike',
    'DateTimeLike',
    'ColorLike',
]
