"""
FluentStackPanel - Vertical/horizontal stack layout following Fluent Design principles

Features:
- Vertical or horizontal stacking
- Fluent Design spacing and alignment
- Responsive behavior options
- Theme-aware styling
- Smooth animations for adding/removing items
- Auto-wrapping option for responsive layouts
"""

from typing import Optional, List, Dict
from enum import Enum
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QFrame
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Signal, QByteArray
from PySide6.QtGui import QResizeEvent

from ..base.fluent_control_base import FluentControlBase, FluentThemeAware


class StackOrientation(Enum):
    """Stack orientation enumeration."""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class FluentStackPanel(FluentControlBase):
    """
    A stack layout container with Fluent Design styling.

    Provides vertical or horizontal stacking with proper spacing,
    alignment, and theme integration following Fluent Design principles.
    """

    # Signals
    item_added = Signal(QWidget)
    item_removed = Signal(QWidget)
    orientation_changed = Signal(str)

    def __init__(self, orientation: StackOrientation = StackOrientation.VERTICAL,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._orientation = orientation
        self._spacing = 8
        self._auto_wrap = False
        self._wrap_threshold = 600
        self._items: List[QWidget] = []
        # Store animations separately
        self._animations: Dict[QWidget, QPropertyAnimation] = {}

        self._init_ui()
        self._setup_styling()

        # Apply theme
        self.apply_theme()

    def _init_ui(self):
        """Initialize the user interface."""
        # Create layout based on orientation
        self._update_layout()

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Preferred)

    def _update_layout(self):
        """Update layout based on current orientation."""
        # Remove existing layout
        current_layout = self.layout()
        if current_layout:
            while current_layout.count():
                child = current_layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
            current_layout.deleteLater()

        # Create new layout
        if self._orientation == StackOrientation.VERTICAL:
            self._stack_layout = QVBoxLayout(self)
        else:
            self._stack_layout = QHBoxLayout(self)

        self._stack_layout.setSpacing(self._spacing)
        self._stack_layout.setContentsMargins(8, 8, 8, 8)

        # Re-add items
        for item in self._items:
            self._stack_layout.addWidget(item)

    def _setup_styling(self):
        """Setup Fluent Design styling."""
        self.setStyleSheet("""
            FluentStackPanel {
                background-color: var(--stack-background, transparent);
                border: none;
                border-radius: 4px;
            }
        """)

    def add_widget(self, widget: QWidget, stretch: int = 0):
        """
        Add a widget to the stack.

        Args:
            widget: Widget to add
            stretch: Stretch factor for the widget
        """
        self._items.append(widget)
        self._stack_layout.addWidget(widget, stretch)

        # Apply entrance animation
        self._animate_widget_entrance(widget)

        self.item_added.emit(widget)

    def insert_widget(self, index: int, widget: QWidget, stretch: int = 0):
        """
        Insert a widget at specific index.

        Args:
            index: Index to insert at
            widget: Widget to insert
            stretch: Stretch factor for the widget
        """
        index = max(0, min(index, len(self._items)))
        self._items.insert(index, widget)
        self._stack_layout.insertWidget(index, widget, stretch)

        # Apply entrance animation
        self._animate_widget_entrance(widget)

        self.item_added.emit(widget)

    def remove_widget(self, widget: QWidget):
        """Remove a widget from the stack."""
        if widget in self._items:
            self._items.remove(widget)

        # Apply exit animation before removal
        self._animate_widget_exit(
            widget, lambda: self._complete_widget_removal(widget))

    def _complete_widget_removal(self, widget: QWidget):
        """Complete widget removal after animation."""
        self._stack_layout.removeWidget(widget)
        widget.setParent(None)
        # Clean up animations
        if widget in self._animations:
            del self._animations[widget]
        self.item_removed.emit(widget)

    def clear(self):
        """Remove all widgets from the stack."""
        widgets_to_remove = self._items.copy()
        for widget in widgets_to_remove:
            self.remove_widget(widget)

    def _animate_widget_entrance(self, widget: QWidget):
        """Animate widget entrance."""
        # Set initial state
        widget.setMaximumHeight(
            0 if self._orientation == StackOrientation.VERTICAL else widget.maximumHeight())
        widget.setMaximumWidth(
            0 if self._orientation == StackOrientation.HORIZONTAL else widget.maximumWidth())

        # Create animation
        property_name = QByteArray(
            b"maximumHeight") if self._orientation == StackOrientation.VERTICAL else QByteArray(b"maximumWidth")
        animation = QPropertyAnimation(widget, property_name)
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(0)

        # Get target size
        widget.adjustSize()
        target_size = widget.sizeHint().height(
        ) if self._orientation == StackOrientation.VERTICAL else widget.sizeHint().width()
        animation.setEndValue(target_size)

        # Reset max size when animation finishes
        def reset_max_size():
            if self._orientation == StackOrientation.VERTICAL:
                widget.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX
            else:
                widget.setMaximumWidth(16777215)

        animation.finished.connect(reset_max_size)
        animation.start()

        # Store animation to prevent garbage collection
        self._animations[widget] = animation

    def _animate_widget_exit(self, widget: QWidget, callback):
        """Animate widget exit."""
        property_name = QByteArray(
            b"maximumHeight") if self._orientation == StackOrientation.VERTICAL else QByteArray(b"maximumWidth")
        current_size = widget.height(
        ) if self._orientation == StackOrientation.VERTICAL else widget.width()

        animation = QPropertyAnimation(widget, property_name)
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.Type.InCubic)
        animation.setStartValue(current_size)
        animation.setEndValue(0)

        animation.finished.connect(callback)
        animation.start()

        # Store animation to prevent garbage collection
        self._animations[widget] = animation

    def set_orientation(self, orientation: StackOrientation):
        """Set stack orientation."""
        if self._orientation != orientation:
            self._orientation = orientation
            self._update_layout()
            self.orientation_changed.emit(orientation.value)

    def get_orientation(self) -> StackOrientation:
        """Get current orientation."""
        return self._orientation

    def set_spacing(self, spacing: int):
        """Set spacing between items."""
        self._spacing = spacing
        if self._stack_layout:
            self._stack_layout.setSpacing(spacing)

    def get_spacing(self) -> int:
        """Get current spacing."""
        return self._spacing

    def set_auto_wrap(self, enabled: bool, threshold: int = 600):
        """
        Enable auto-wrap to change orientation based on size.

        Args:
            enabled: Whether to enable auto-wrap
            threshold: Width threshold for wrapping (horizontal to vertical)
        """
        self._auto_wrap = enabled
        self._wrap_threshold = threshold

    def add_stretch(self, stretch: int = 1):
        """Add stretch space to the layout."""
        self._stack_layout.addStretch(stretch)

    def insert_stretch(self, index: int, stretch: int = 1):
        """Insert stretch space at specific index."""
        self._stack_layout.insertStretch(index, stretch)

    def get_widget_count(self) -> int:
        """Get number of widgets in the stack."""
        return len(self._items)

    def get_widget_at(self, index: int) -> Optional[QWidget]:
        """Get widget at specific index."""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def get_widget_index(self, widget: QWidget) -> int:
        """Get index of widget, returns -1 if not found."""
        try:
            return self._items.index(widget)
        except ValueError:
            return -1

    def resizeEvent(self, event: QResizeEvent):
        """Handle resize events for auto-wrap functionality."""
        super().resizeEvent(event)

        if self._auto_wrap:
            new_width = event.size().width()

            # Switch to vertical if width is below threshold
            if new_width < self._wrap_threshold and self._orientation == StackOrientation.HORIZONTAL:
                self.set_orientation(StackOrientation.VERTICAL)
            # Switch to horizontal if width is above threshold
            elif new_width >= self._wrap_threshold and self._orientation == StackOrientation.VERTICAL:
                self.set_orientation(StackOrientation.HORIZONTAL)

    def apply_theme(self):
        """Apply the current theme to the stack panel."""
        # Use theme manager directly instead of missing method
        from core.theme import theme_manager
        
        if not theme_manager:
            return

        # Update CSS variables based on theme
        style_vars = {
            '--stack-background': 'transparent',  # Fallback value
        }

        # Apply updated styling
        current_style = self.styleSheet()
        for var_name, var_value in style_vars.items():
            current_style = current_style.replace(
                f'var({var_name}, ', f'{var_value}; /* var({var_name}, ')

        self.setStyleSheet(current_style)


class FluentWrapPanel(QFrame, FluentControlBase, FluentThemeAware):
    """
    A wrapping layout container with Fluent Design styling.

    Automatically wraps widgets to new lines/columns when space is limited,
    following Fluent Design principles.
    """

    # Signals
    item_added = Signal(QWidget)
    item_removed = Signal(QWidget)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        FluentControlBase.__init__(self)
        FluentThemeAware.__init__(self)

        self._items: List[QWidget] = []
        self._spacing = 8
        self._item_width = 100
        self._item_height = 32

        self._init_ui()
        self._setup_styling()

        # Apply theme
        self.apply_theme()

    def _init_ui(self):
        """Initialize the user interface."""
        # Don't use a layout manager, we'll position manually
        self.setMinimumSize(200, 100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

    def _setup_styling(self):
        """Setup Fluent Design styling."""
        self.setStyleSheet("""
            FluentWrapPanel {
                background-color: var(--wrap-background, transparent);
                border: none;
                border-radius: 4px;
            }
        """)

    def add_widget(self, widget: QWidget):
        """Add a widget to the wrap panel."""
        widget.setParent(self)
        self._items.append(widget)
        self._relayout_widgets()
        widget.show()
        self.item_added.emit(widget)

    def remove_widget(self, widget: QWidget):
        """Remove a widget from the wrap panel."""
        if widget in self._items:
            self._items.remove(widget)
            widget.setParent(None)
            self._relayout_widgets()
            self.item_removed.emit(widget)

    def clear(self):
        """Remove all widgets."""
        widgets_to_remove = self._items.copy()
        for widget in widgets_to_remove:
            self.remove_widget(widget)

    def _relayout_widgets(self):
        """Re-layout all widgets with wrapping."""
        if not self._items:
            return

        x = self._spacing
        y = self._spacing
        row_height = 0

        for widget in self._items:
            widget_size = widget.sizeHint()
            widget_width = max(widget_size.width(), self._item_width)
            widget_height = max(widget_size.height(), self._item_height)

            # Check if we need to wrap to next line
            if x + widget_width > self.width() - self._spacing and x > self._spacing:
                x = self._spacing
                y += row_height + self._spacing
                row_height = 0

            # Position widget
            widget.setGeometry(x, y, widget_width, widget_height)

            # Update position for next widget
            x += widget_width + self._spacing
            row_height = max(row_height, widget_height)

        # Update minimum height
        min_height = y + row_height + self._spacing
        self.setMinimumHeight(min_height)

    def resizeEvent(self, event: QResizeEvent):
        """Handle resize events."""
        super().resizeEvent(event)
        self._relayout_widgets()

    def set_spacing(self, spacing: int):
        """Set spacing between items."""
        self._spacing = spacing
        self._relayout_widgets()

    def set_item_size(self, width: int, height: int):
        """Set default item size."""
        self._item_width = width
        self._item_height = height
        self._relayout_widgets()

    def apply_theme(self):
        """Apply the current theme to the wrap panel."""
        theme = self.get_current_theme()
        if not theme:
            return

        # Update CSS variables based on theme
        style_vars = {
            '--wrap-background': theme.get('surface_background', 'transparent'),
        }

        # Apply updated styling
        current_style = self.styleSheet()
        for var_name, var_value in style_vars.items():
            current_style = current_style.replace(
                f'var({var_name}, ', f'{var_value}; /* var({var_name}, ')

        self.setStyleSheet(current_style)
