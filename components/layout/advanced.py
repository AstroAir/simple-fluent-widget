#!/usr/bin/env python3
"""
Layout Components for Fluent UI

This module provides modern layout components following Fluent Design principles.
Includes FluentGrid, FluentStack, FluentWrap, and FluentSpacer components for flexible layouts.
"""

from typing import Optional, List, Union, Any
from enum import Enum
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QSizePolicy,
    QSpacerItem, QScrollArea, QLabel
)
from PySide6.QtCore import Qt, Signal, QSize, QRect, QPropertyAnimation, QEasingCurve, QMargins
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from core.theme import theme_manager


class FluentDirection(Enum):
    """Layout direction enumeration"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class FluentAlignment(Enum):
    """Alignment enumeration"""
    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"
    SPACE_BETWEEN = "space_between"
    SPACE_AROUND = "space_around"
    SPACE_EVENLY = "space_evenly"


class FluentWrap(Enum):
    """Wrap enumeration"""
    NO_WRAP = "no_wrap"
    WRAP = "wrap"
    WRAP_REVERSE = "wrap_reverse"


class FluentStack(QWidget):
    """
    Stack layout widget for organizing child widgets

    Features:
    - Horizontal or vertical direction
    - Flexible alignment options
    - Configurable spacing
    - Support for stretch factors
    - Responsive behavior
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._direction = FluentDirection.VERTICAL
        self._alignment = FluentAlignment.START
        self._cross_alignment = FluentAlignment.START
        self._spacing = 8
        self._padding = QMargins(0, 0, 0, 0)

        self.setup_ui()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup the stack UI"""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(self._spacing)
        self.update_layout()

    def update_layout(self):
        """Update layout based on current settings"""
        # Clear existing layout
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
            elif child.spacerItem():
                del child

        # Create new layout based on direction
        if self._direction == FluentDirection.HORIZONTAL:
            new_layout = QHBoxLayout()
        else:
            new_layout = QVBoxLayout()

        new_layout.setContentsMargins(
            self._padding.left(), self._padding.top(),
            self._padding.right(), self._padding.bottom()
        )
        new_layout.setSpacing(self._spacing)

        # Copy widgets from old layout
        widgets = []
        current_layout = self.layout()
        if current_layout:
            for i in range(current_layout.count()):
                item = current_layout.itemAt(i)
                if item and item.widget():
                    widgets.append(item.widget())

        # Remove old layout
        self._layout.deleteLater()

        # Set new layout
        self._layout = new_layout
        self.setLayout(self._layout)

        # Add widgets back
        for widget in widgets:
            self.addWidget(widget)

        self.update_alignment()

    def update_alignment(self):
        """Update alignment settings"""
        # Main axis alignment
        if self._alignment == FluentAlignment.CENTER:
            self._layout.addStretch()
            # Widgets are added in the middle
            self._layout.addStretch()
        elif self._alignment == FluentAlignment.END:
            self._layout.insertStretch(0)
        elif self._alignment == FluentAlignment.SPACE_BETWEEN:
            # Add stretch between each widget
            for i in range(1, self._layout.count(), 2):
                self._layout.insertStretch(i)
        elif self._alignment == FluentAlignment.SPACE_AROUND:
            # Add stretch around each widget
            self._layout.insertStretch(0)
            for i in range(2, self._layout.count(), 2):
                self._layout.insertStretch(i)
            self._layout.addStretch()
        elif self._alignment == FluentAlignment.SPACE_EVENLY:
            # Add equal stretch everywhere
            self._layout.insertStretch(0)
            for i in range(2, self._layout.count(), 2):
                self._layout.insertStretch(i)
            self._layout.addStretch()

        # Cross axis alignment
        cross_align = Qt.AlignmentFlag.AlignLeft
        if self._cross_alignment == FluentAlignment.CENTER:
            cross_align = Qt.AlignmentFlag.AlignCenter
        elif self._cross_alignment == FluentAlignment.END:
            cross_align = Qt.AlignmentFlag.AlignRight

        if self._direction == FluentDirection.VERTICAL:
            if self._cross_alignment == FluentAlignment.CENTER:
                cross_align = Qt.AlignmentFlag.AlignHCenter
            elif self._cross_alignment == FluentAlignment.END:
                cross_align = Qt.AlignmentFlag.AlignRight
        else:
            if self._cross_alignment == FluentAlignment.CENTER:
                cross_align = Qt.AlignmentFlag.AlignVCenter
            elif self._cross_alignment == FluentAlignment.END:
                cross_align = Qt.AlignmentFlag.AlignBottom

        self._layout.setAlignment(cross_align)

    def addWidget(self, widget: QWidget, stretch: int = 0):
        """Add widget to stack"""
        if self._alignment == FluentAlignment.CENTER and self._layout.count() == 0:
            self._layout.addStretch()

        self._layout.addWidget(widget, stretch)

        if self._alignment == FluentAlignment.CENTER and self._layout.count() == 2:
            self._layout.addStretch()

    def removeWidget(self, widget: QWidget):
        """Remove widget from stack"""
        self._layout.removeWidget(widget)
        widget.setParent(None)

    def direction(self) -> FluentDirection:
        """Get layout direction"""
        return self._direction

    def setDirection(self, direction: FluentDirection):
        """Set layout direction"""
        if direction != self._direction:
            self._direction = direction
            self.update_layout()

    def alignment(self) -> FluentAlignment:
        """Get main axis alignment"""
        return self._alignment

    def setAlignment(self, alignment: FluentAlignment):
        """Set main axis alignment"""
        if alignment != self._alignment:
            self._alignment = alignment
            self.update_layout()

    def crossAlignment(self) -> FluentAlignment:
        """Get cross axis alignment"""
        return self._cross_alignment

    def setCrossAlignment(self, alignment: FluentAlignment):
        """Set cross axis alignment"""
        if alignment != self._cross_alignment:
            self._cross_alignment = alignment
            self.update_alignment()

    def spacing(self) -> int:
        """Get spacing between widgets"""
        return self._spacing

    def setSpacing(self, spacing: int):
        """Set spacing between widgets"""
        self._spacing = spacing
        self._layout.setSpacing(spacing)

    def padding(self) -> QMargins:
        """Get padding"""
        return self._padding

    def setPadding(self, padding: Union[int, QMargins]):
        """Set padding"""
        if isinstance(padding, int):
            self._padding = QMargins(padding, padding, padding, padding)
        else:
            self._padding = padding

        self._layout.setContentsMargins(
            self._padding.left(), self._padding.top(),
            self._padding.right(), self._padding.bottom()
        )

    def apply_theme(self):
        """Apply current theme"""
        bg_color = theme_manager.get_color('background')
        self.setStyleSheet(f"""
            FluentStack {{
                background-color: {bg_color};
            }}
        """)


class FluentGrid(QWidget):
    """
    Grid layout widget for organizing widgets in rows and columns

    Features:
    - Flexible grid sizing
    - Responsive column/row spans
    - Automatic sizing
    - Gap control
    - Alignment options
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._columns = 1
        self._gap = 8
        self._auto_size = True

        self.setup_ui()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup the grid UI"""
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(self._gap)

    def addWidget(self, widget: QWidget, row: int = -1, column: int = -1,
                  row_span: int = 1, column_span: int = 1):
        """Add widget to grid"""
        if row == -1 or column == -1:
            # Auto placement
            if self._auto_size:
                next_row = self._layout.rowCount()
                next_col = 0
                self._layout.addWidget(
                    widget, next_row, next_col, row_span, column_span)
            else:
                # Find next available position
                for r in range(self._layout.rowCount() + 1):
                    for c in range(self._columns):
                        if self._layout.itemAtPosition(r, c) is None:
                            self._layout.addWidget(
                                widget, r, c, row_span, column_span)
                            return
        else:
            self._layout.addWidget(widget, row, column, row_span, column_span)

    def removeWidget(self, widget: QWidget):
        """Remove widget from grid"""
        self._layout.removeWidget(widget)
        widget.setParent(None)

    def widgetAt(self, row: int, column: int) -> Optional[QWidget]:
        """Get widget at specific position"""
        item = self._layout.itemAtPosition(row, column)
        return item.widget() if item else None

    def columns(self) -> int:
        """Get number of columns"""
        return self._columns

    def setColumns(self, columns: int):
        """Set number of columns"""
        self._columns = max(1, columns)
        if not self._auto_size:
            self.reorganize_widgets()

    def gap(self) -> int:
        """Get gap between cells"""
        return self._gap

    def setGap(self, gap: int):
        """Set gap between cells"""
        self._gap = gap
        self._layout.setSpacing(gap)

    def autoSize(self) -> bool:
        """Check if auto sizing is enabled"""
        return self._auto_size

    def setAutoSize(self, auto_size: bool):
        """Set auto sizing"""
        self._auto_size = auto_size
        if not auto_size:
            self.reorganize_widgets()

    def reorganize_widgets(self):
        """Reorganize widgets based on current settings"""
        if self._auto_size:
            return

        # Get all widgets
        widgets = []
        for i in range(self._layout.count()):
            item = self._layout.itemAt(i)
            if item and item.widget():
                widgets.append(item.widget())

        # Clear layout
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        # Re-add widgets in grid pattern
        for i, widget in enumerate(widgets):
            row = i // self._columns
            col = i % self._columns
            self._layout.addWidget(widget, row, col)

    def apply_theme(self):
        """Apply current theme"""
        bg_color = theme_manager.get_color('background')
        self.setStyleSheet(f"""
            FluentGrid {{
                background-color: {bg_color};
            }}
        """)


class FluentWrapLayout(QWidget):
    """
    Wrap layout that automatically wraps widgets to next line when needed

    Features:
    - Automatic wrapping
    - Configurable wrap direction
    - Flexible spacing
    - Responsive behavior
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._direction = FluentDirection.HORIZONTAL
        self._wrap = FluentWrap.WRAP
        self._spacing = 8
        self._line_spacing = 8
        self._widgets = []

        self.setup_ui()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup the wrap layout UI"""
        # We'll implement custom layout logic in resizeEvent
        pass

    def addWidget(self, widget: QWidget):
        """Add widget to wrap layout"""
        widget.setParent(self)
        self._widgets.append(widget)
        self.update_layout()

    def removeWidget(self, widget: QWidget):
        """Remove widget from wrap layout"""
        if widget in self._widgets:
            self._widgets.remove(widget)
            widget.setParent(None)
            self.update_layout()

    def clear(self):
        """Remove all widgets"""
        for widget in self._widgets.copy():
            self.removeWidget(widget)

    def update_layout(self):
        """Update widget positions"""
        if not self._widgets:
            return

        available_width = self.width() - 20  # Account for margins
        if available_width <= 0:
            return

        x, y = 10, 10  # Starting position with margin
        max_height_in_line = 0

        for widget in self._widgets:
            widget_size = widget.sizeHint()

            # Check if we need to wrap
            if x + widget_size.width() > available_width and x > 10:
                # Wrap to next line
                x = 10
                y += max_height_in_line + self._line_spacing
                max_height_in_line = 0

            # Position widget
            widget.move(x, y)
            widget.resize(widget_size)
            widget.show()

            # Update position for next widget
            x += widget_size.width() + self._spacing
            max_height_in_line = max(max_height_in_line, widget_size.height())

        # Update our minimum height
        self.setMinimumHeight(y + max_height_in_line + 10)

    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)
        self.update_layout()

    def direction(self) -> FluentDirection:
        """Get layout direction"""
        return self._direction

    def setDirection(self, direction: FluentDirection):
        """Set layout direction"""
        self._direction = direction
        self.update_layout()

    def wrap(self) -> FluentWrap:
        """Get wrap mode"""
        return self._wrap

    def setWrap(self, wrap: FluentWrap):
        """Set wrap mode"""
        self._wrap = wrap
        self.update_layout()

    def spacing(self) -> int:
        """Get spacing between widgets"""
        return self._spacing

    def setSpacing(self, spacing: int):
        """Set spacing between widgets"""
        self._spacing = spacing
        self.update_layout()

    def lineSpacing(self) -> int:
        """Get spacing between lines"""
        return self._line_spacing

    def setLineSpacing(self, spacing: int):
        """Set spacing between lines"""
        self._line_spacing = spacing
        self.update_layout()

    def apply_theme(self):
        """Apply current theme"""
        bg_color = theme_manager.get_color('background')
        self.setStyleSheet(f"""
            FluentWrapLayout {{
                background-color: {bg_color};
            }}
        """)


class FluentSpacer(QWidget):
    """
    Spacer widget for adding flexible or fixed space in layouts

    Features:
    - Fixed or flexible sizing
    - Horizontal or vertical orientation
    - Minimum and maximum size constraints
    """

    def __init__(self, width: int = 0, height: int = 0,
                 horizontal_policy: QSizePolicy.Policy = QSizePolicy.Policy.Expanding,
                 vertical_policy: QSizePolicy.Policy = QSizePolicy.Policy.Expanding,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Set size policy
        size_policy = QSizePolicy(horizontal_policy, vertical_policy)
        self.setSizePolicy(size_policy)

        # Set fixed size if specified
        if width > 0 or height > 0:
            if width > 0 and height > 0:
                self.setFixedSize(width, height)
            elif width > 0:
                self.setFixedWidth(width)
            elif height > 0:
                self.setFixedHeight(height)

        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)

    def apply_theme(self):
        """Apply current theme"""
        self.setStyleSheet("""
            FluentSpacer {
                background-color: transparent;
            }
        """)


class FluentDivider(QFrame):
    """
    Divider widget for visually separating content

    Features:
    - Horizontal or vertical orientation
    - Customizable thickness and color
    - Text labels
    - Margins and padding
    """

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal,
                 text: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._orientation = orientation
        self._text = text
        self._thickness = 1
        self._margins = QMargins(0, 8, 0, 8)

        self.setup_ui()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup divider UI"""
        if self._orientation == Qt.Orientation.Horizontal:
            self.setFrameShape(QFrame.Shape.HLine)
            self.setFixedHeight(
                self._thickness + self._margins.top() + self._margins.bottom())
        else:
            self.setFrameShape(QFrame.Shape.VLine)
            self.setFixedWidth(self._thickness +
                               self._margins.left() + self._margins.right())

        self.setFrameShadow(QFrame.Shadow.Plain)

        # Add text label if provided
        if self._text:
            self.setup_text_label()

    def setup_text_label(self):
        """Setup text label for divider"""
        # For horizontal divider with text, we need a layout
        if self._orientation == Qt.Orientation.Horizontal:
            layout = QHBoxLayout(self)
            layout.setContentsMargins(self._margins.left(), self._margins.top(),
                                      self._margins.right(), self._margins.bottom())

            # Left line
            left_line = QFrame()
            left_line.setFrameShape(QFrame.Shape.HLine)
            left_line.setFrameShadow(QFrame.Shadow.Plain)
            layout.addWidget(left_line)

            # Text label
            label = QLabel(self._text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(10)
            label.setFont(font)
            layout.addWidget(label)

            # Right line
            right_line = QFrame()
            right_line.setFrameShape(QFrame.Shape.HLine)
            right_line.setFrameShadow(QFrame.Shadow.Plain)
            layout.addWidget(right_line)

    def text(self) -> str:
        """Get divider text"""
        return self._text

    def setText(self, text: str):
        """Set divider text"""
        self._text = text
        self.setup_ui()

    def orientation(self) -> Qt.Orientation:
        """Get divider orientation"""
        return self._orientation

    def setOrientation(self, orientation: Qt.Orientation):
        """Set divider orientation"""
        self._orientation = orientation
        self.setup_ui()

    def thickness(self) -> int:
        """Get divider thickness"""
        return self._thickness

    def setThickness(self, thickness: int):
        """Set divider thickness"""
        self._thickness = thickness
        self.setup_ui()

    def margins(self) -> QMargins:
        """Get divider margins"""
        return self._margins

    def setMargins(self, margins: Union[int, QMargins]):
        """Set divider margins"""
        if isinstance(margins, int):
            self._margins = QMargins(margins, margins, margins, margins)
        else:
            self._margins = margins
        self.setup_ui()

    def apply_theme(self):
        """Apply current theme"""
        divider_color = theme_manager.get_color('outline')
        text_color = theme_manager.get_color('on_surface')

        self.setStyleSheet(f"""
            FluentDivider {{
                color: {divider_color};
                background-color: {divider_color};
            }}
            QLabel {{
                color: {text_color};
                background-color: {theme_manager.get_color('background')};
                padding: 0 8px;
            }}
            QFrame {{
                color: {divider_color};
                background-color: {divider_color};
            }}
        """)


class FluentContainer(QWidget):
    """
    Container widget with padding, margins, and background styling

    Features:
    - Configurable padding and margins
    - Background color and border styling
    - Shadow effects
    - Rounded corners
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._padding = QMargins(16, 16, 16, 16)
        self._border_radius = 8
        self._border_width = 1
        self._show_shadow = False

        self.setup_ui()
        self.apply_theme()
        theme_manager.theme_changed.connect(self.apply_theme)

    def setup_ui(self):
        """Setup container UI"""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(
            self._padding.left(), self._padding.top(),
            self._padding.right(), self._padding.bottom()
        )

    def addWidget(self, widget: QWidget):
        """Add widget to container"""
        self._layout.addWidget(widget)

    def removeWidget(self, widget: QWidget):
        """Remove widget from container"""
        self._layout.removeWidget(widget)
        widget.setParent(None)

    def setLayout(self, layout):
        """Set custom layout"""
        # Clear existing layout
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        self._layout.deleteLater()
        self._layout = layout
        super().setLayout(layout)

        # Apply padding
        self._layout.setContentsMargins(
            self._padding.left(), self._padding.top(),
            self._padding.right(), self._padding.bottom()
        )

    def padding(self) -> QMargins:
        """Get container padding"""
        return self._padding

    def setPadding(self, padding: Union[int, QMargins]):
        """Set container padding"""
        if isinstance(padding, int):
            self._padding = QMargins(padding, padding, padding, padding)
        else:
            self._padding = padding

        self._layout.setContentsMargins(
            self._padding.left(), self._padding.top(),
            self._padding.right(), self._padding.bottom()
        )

    def borderRadius(self) -> int:
        """Get border radius"""
        return self._border_radius

    def setBorderRadius(self, radius: int):
        """Set border radius"""
        self._border_radius = radius
        self.apply_theme()

    def borderWidth(self) -> int:
        """Get border width"""
        return self._border_width

    def setBorderWidth(self, width: int):
        """Set border width"""
        self._border_width = width
        self.apply_theme()

    def showShadow(self) -> bool:
        """Check if shadow is shown"""
        return self._show_shadow

    def setShowShadow(self, show_shadow: bool):
        """Set shadow visibility"""
        self._show_shadow = show_shadow
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme"""
        bg_color = theme_manager.get_color('surface')
        border_color = theme_manager.get_color('outline')

        shadow_style = ""
        if self._show_shadow:
            shadow_style = """
                FluentContainer {
                    border: 1px solid rgba(0, 0, 0, 0.1);
                    background-color: rgba(255, 255, 255, 0.8);
                }
            """

        self.setStyleSheet(f"""
            FluentContainer {{
                background-color: {bg_color};
                border: {self._border_width}px solid {border_color};
                border-radius: {self._border_radius}px;
            }}
            {shadow_style}
        """)


# Export all classes
__all__ = [
    'FluentDirection',
    'FluentAlignment',
    'FluentWrap',
    'FluentStack',
    'FluentGrid',
    'FluentWrapLayout',
    'FluentSpacer',
    'FluentDivider',
    'FluentContainer'
]
