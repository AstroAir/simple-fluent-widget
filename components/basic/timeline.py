"""
Fluent Design Timeline Component
Visual timeline for displaying chronological events and processes
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QFrame, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QDateTime, QPropertyAnimation, Property, QByteArray
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional, List, Union, cast
from enum import Enum
from datetime import datetime


class FluentTimelineItem(QFrame):
    """Individual timeline item"""

    class Status(Enum):
        PENDING = "pending"
        CURRENT = "current"
        COMPLETED = "completed"
        ERROR = "error"
        WARNING = "warning"

    # Signals
    clicked = Signal()
    hover_progress_changed = Signal()

    def __init__(self, title: str = "", description: str = "",
                 timestamp: Optional[Union[datetime, QDateTime]] = None,
                 status: Status = Status.PENDING,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._description = description
        self._timestamp = timestamp
        self._status = status
        self._clickable = False
        self._dot_size = 12
        self._line_width = 2
        self._content_widget: Optional[QWidget] = None
        self._hover_progress = 0.0

        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setFrameStyle(QFrame.Shape.NoFrame)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # Timeline dot container
        self._dot_container = QFrame()
        self._dot_container.setFixedWidth(self._dot_size + 8)
        self._dot_container.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # Content container
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 16)
        content_layout.setSpacing(4)

        # Header (title and timestamp)
        if self._title or self._timestamp:
            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(12)

            if self._title:
                self._title_label = QLabel(self._title)
                title_font = QFont()
                title_font.setPointSize(14)
                title_font.setWeight(QFont.Weight.Medium)
                self._title_label.setFont(title_font)
                header_layout.addWidget(self._title_label)

            header_layout.addStretch()

            if self._timestamp:
                timestamp_text = self._format_timestamp(self._timestamp)
                self._timestamp_label = QLabel(timestamp_text)
                timestamp_font = QFont()
                timestamp_font.setPointSize(12)
                self._timestamp_label.setFont(timestamp_font)
                header_layout.addWidget(self._timestamp_label)

            content_layout.addLayout(header_layout)

        # Description
        if self._description:
            self._desc_label = QLabel(self._description)
            self._desc_label.setWordWrap(True)
            desc_font = QFont()
            desc_font.setPointSize(13)
            self._desc_label.setFont(desc_font)
            content_layout.addWidget(self._desc_label)

        main_layout.addWidget(self._dot_container)
        main_layout.addWidget(content_frame, 1)

    def _setup_style(self):
        """Setup style"""
        if not theme_manager:
            return
        theme = theme_manager

        # Dot container style
        self._dot_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)

        # Title style
        if hasattr(self, '_title_label'):
            title_color = theme.get_color('text_primary')
            self._title_label.setStyleSheet(f"color: {title_color.name()};")

        # Description style
        if hasattr(self, '_desc_label'):
            desc_color = theme.get_color('text_secondary')
            self._desc_label.setStyleSheet(f"color: {desc_color.name()};")

        # Timestamp style
        if hasattr(self, '_timestamp_label'):
            timestamp_color = theme.get_color('text_tertiary')
            self._timestamp_label.setStyleSheet(
                f"color: {timestamp_color.name()};")

        self.update()

    def _setup_animations(self):
        """Setup animations"""
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_progress"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def paintEvent(self, event):
        """Custom paint event for timeline dot and line"""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._draw_timeline_elements(painter)

    def _draw_timeline_elements(self, painter: QPainter):
        """Draw timeline dot and connecting line"""
        if not theme_manager:
            return
        theme = theme_manager

        # Get dot container geometry
        dot_rect = self._dot_container.geometry()
        dot_center_x = dot_rect.center().x()
        dot_center_y = dot_rect.top() + self._dot_size // 2 + 8

        # Get status color
        dot_color = self._get_status_color()

        # Draw connecting line (if not first item)
        line_color = theme.get_color('border')
        painter.setPen(QPen(line_color, self._line_width))

        # Line from top to dot
        if dot_center_y > self._dot_size:
            painter.drawLine(dot_center_x, 0, dot_center_x,
                             dot_center_y - self._dot_size // 2)

        # Line from dot to bottom
        painter.drawLine(dot_center_x, dot_center_y + self._dot_size // 2,
                         dot_center_x, self.height())

        # Draw status dot
        self._draw_status_dot(painter, dot_center_x, dot_center_y, dot_color)

    def _draw_status_dot(self, painter: QPainter, x: int, y: int, color: QColor):
        """Draw status dot"""
        # Outer ring
        ring_color = color.lighter(120)
        painter.setPen(QPen(ring_color, 2))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawEllipse(x - self._dot_size // 2, y - self._dot_size // 2,
                            self._dot_size, self._dot_size)

        # Inner dot
        inner_size = self._dot_size - 4
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(x - inner_size // 2, y - inner_size // 2,
                            inner_size, inner_size)

        # Add pulsing effect for current status
        if self._status == self.Status.CURRENT:
            pulse_size = self._dot_size + int(4 * self._hover_progress)
            pulse_color = QColor(color)
            pulse_color.setAlpha(int(50 * (1 - self._hover_progress)))
            painter.setBrush(QBrush(pulse_color))
            painter.drawEllipse(x - pulse_size // 2, y - pulse_size // 2,
                                pulse_size, pulse_size)

    def _get_status_color(self) -> QColor:
        """Get color based on status"""
        if not theme_manager:
            return QColor(Qt.GlobalColor.gray)  # Fallback color
        theme = theme_manager

        status_colors = {
            self.Status.PENDING: theme.get_color('text_tertiary'),
            self.Status.CURRENT: theme.get_color('primary'),
            self.Status.COMPLETED: theme.get_color('success'),
            self.Status.ERROR: theme.get_color('error'),
            self.Status.WARNING: theme.get_color('warning')
        }

        return status_colors.get(self._status, theme.get_color('text_tertiary'))

    def _format_timestamp(self, timestamp_input: Union[datetime, QDateTime]) -> str:
        """Format timestamp for display"""
        py_timestamp: datetime
        if isinstance(timestamp_input, QDateTime):
            py_timestamp = cast(datetime, timestamp_input.toPython())
        elif isinstance(timestamp_input, datetime):
            py_timestamp = timestamp_input
        else:
            return "Invalid date"  # Should not happen with type hints

        now = datetime.now()
        diff = now - py_timestamp

        if diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}小时前"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"

    def _get_hover_progress(self) -> float:
        return self._hover_progress

    def _set_hover_progress(self, value: float):
        if self._hover_progress != value:
            self._hover_progress = value
            self.hover_progress_changed.emit()
            self.update()

    hover_progress = Property(float, _get_hover_progress,
                              _set_hover_progress, None, "", notify=hover_progress_changed)

    def setTitle(self, title: str):
        """Set item title"""
        self._title = title
        if hasattr(self, '_title_label'):
            self._title_label.setText(title)

    def title(self) -> str:
        """Get item title"""
        return self._title

    def setDescription(self, description: str):
        """Set item description"""
        self._description = description
        if hasattr(self, '_desc_label'):
            self._desc_label.setText(description)

    def description(self) -> str:
        """Get item description"""
        return self._description

    def setTimestamp(self, timestamp: Union[datetime, QDateTime]):
        """Set item timestamp"""
        self._timestamp = timestamp
        if hasattr(self, '_timestamp_label'):
            self._timestamp_label.setText(self._format_timestamp(timestamp))

    def timestamp(self) -> Optional[Union[datetime, QDateTime]]:
        """Get item timestamp"""
        return self._timestamp

    def setStatus(self, status: Status):
        """Set item status"""
        self._status = status
        self.update()

        # Start pulsing animation for current status
        if status == self.Status.CURRENT:
            self._start_pulse_animation()

    def status(self) -> Status:
        """Get item status"""
        return self._status

    def setContentWidget(self, widget: QWidget):
        """Set custom content widget"""
        if self._content_widget:
            self._content_widget.setParent(None)
            self._content_widget.deleteLater()  # Ensure proper cleanup

        self._content_widget = widget
        if widget:
            # Find content layout and add widget
            current_layout = self.layout()
            if current_layout and current_layout.count() > 1:
                content_item = current_layout.itemAt(1)
                if content_item:
                    content_frame = content_item.widget()
                    if content_frame:
                        content_frame_layout = content_frame.layout()
                        if content_frame_layout:
                            content_frame_layout.addWidget(widget)
                        else:
                            # If content_frame has no layout, create one
                            new_content_layout = QVBoxLayout(content_frame)
                            new_content_layout.addWidget(widget)

    def contentWidget(self) -> Optional[QWidget]:
        """Get content widget"""
        return self._content_widget

    def setClickable(self, clickable: bool):
        """Set whether item is clickable"""
        self._clickable = clickable
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if clickable else Qt.CursorShape.ArrowCursor)

    def isClickable(self) -> bool:
        """Check if item is clickable"""
        return self._clickable

    def _start_pulse_animation(self):
        """Start pulsing animation for current items"""
        self._hover_animation.setStartValue(0.0)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.setDuration(1000)
        self._hover_animation.setLoopCount(-1)  # Infinite loop
        self._hover_animation.start()

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def _on_theme_changed(self, _=None):  # Add default for signal argument
        """Handle theme change"""
        self._setup_style()


class FluentTimeline(QScrollArea):
    """Fluent Design timeline widget"""

    # Signals
    item_clicked = Signal(int)  # item index

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items: List[FluentTimelineItem] = []
        self._reverse_order = False

        self._setup_ui()
        self._setup_style()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Content widget
        self._content_widget = QWidget()
        self._layout = QVBoxLayout(self._content_widget)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(0)

        # Add stretch at the end
        self._layout.addStretch()

        self.setWidget(self._content_widget)

    def _setup_style(self):
        """Setup style"""
        if not theme_manager:
            return
        theme = theme_manager

        style_sheet = f"""
            QScrollArea {{
                background-color: {theme.get_color('background').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
            QScrollArea > QWidget {{ /* Target the viewport's child */
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background: {theme.get_color('surface').name()};
                border: none;
                border-radius: 6px;
                width: 12px;
                margin: 0px 0px 0px 0px; /* Adjusted margins */
            }}
            QScrollBar::handle:vertical {{
                background: {theme.get_color('border').name()};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme.get_color('text_secondary').name()};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px; /* Remove arrows */
                border: none;
                background: none;
            }}
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """

        self.setStyleSheet(style_sheet)
        if self._content_widget:  # Ensure content widget also gets transparent background
            self._content_widget.setStyleSheet(
                "background-color: transparent;")

    def addItem(self, title: str = "", description: str = "",
                timestamp: Optional[Union[datetime, QDateTime]] = None,
                status: FluentTimelineItem.Status = FluentTimelineItem.Status.PENDING) -> int:
        """Add timeline item

        Returns:
            Index of added item
        """
        item = FluentTimelineItem(
            title, description, timestamp, status, self)  # Parent to self for QScrollArea

        # Connect signals
        # Ensure lambda captures current length for correct index
        # current_item_count = len(self._items) # Unused variable
        item.clicked.connect(
            lambda item_ref=item: self._on_item_clicked_ref(item_ref))

        # Insert item based on order
        if self._reverse_order:
            self._layout.insertWidget(0, item)
            self._items.insert(0, item)
        else:
            # Insert before stretch
            self._layout.insertWidget(len(self._items), item)
            self._items.append(item)

        return self._items.index(item)

    def insertItem(self, index: int, title: str = "", description: str = "",
                   timestamp: Optional[Union[datetime, QDateTime]] = None,
                   status: FluentTimelineItem.Status = FluentTimelineItem.Status.PENDING):
        """Insert item at index"""
        if not 0 <= index <= len(self._items):
            return  # Or raise IndexError

        item = FluentTimelineItem(title, description, timestamp, status, self)
        item.clicked.connect(
            lambda item_ref=item: self._on_item_clicked_ref(item_ref))

        self._layout.insertWidget(index, item)
        self._items.insert(index, item)

    def removeItem(self, index: int):
        """Remove item at index"""
        if not 0 <= index < len(self._items):
            return

        item = self._items.pop(index)
        self._layout.removeWidget(item)
        item.setParent(None)
        item.deleteLater()

    def item(self, index: int) -> Optional[FluentTimelineItem]:
        """Get item at index"""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def itemCount(self) -> int:
        """Get item count"""
        return len(self._items)

    def clear(self):
        """Clear all items"""
        while self._items:
            item = self._items.pop(0)
            self._layout.removeWidget(item)
            item.setParent(None)
            item.deleteLater()

    def setReverseOrder(self, reverse: bool):
        """Set whether to display items in reverse order (newest first)"""
        if self._reverse_order != reverse:
            self._reverse_order = reverse

            # Reorder items in the layout
            items_copy = list(self._items)  # Shallow copy of item references

            # Clear layout but keep item objects
            for _ in range(self._layout.count() - 1):  # -1 for the stretch
                layout_item = self._layout.takeAt(0)
                if layout_item and layout_item.widget():
                    layout_item.widget().setParent(None)  # Detach from layout

            self._items.clear()  # Clear internal list

            if reverse:
                items_copy.reverse()

            for itm in items_copy:
                # Re-add to internal list and layout
                # The addItem logic will handle reverse order correctly if called now
                # but to avoid re-creating signals, we add directly
                if self._reverse_order:  # If now reverse, add to top of layout
                    self._layout.insertWidget(0, itm)
                    self._items.insert(0, itm)
                else:  # Add to bottom (before stretch)
                    self._layout.insertWidget(len(self._items), itm)
                    self._items.append(itm)
                # Ensure parent is correct for layout
                itm.setParent(self._content_widget)

    def reverseOrder(self) -> bool:
        """Check if items are in reverse order"""
        return self._reverse_order

    def scrollToItem(self, index: int):
        """Scroll to item at index"""
        if 0 <= index < len(self._items):
            item = self._items[index]
            self.ensureWidgetVisible(item)

    def scrollToTop(self):
        """Scroll to top"""
        if self.verticalScrollBar():
            self.verticalScrollBar().setValue(0)

    def scrollToBottom(self):
        """Scroll to bottom"""
        if self.verticalScrollBar():
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def _on_item_clicked_ref(self, item_ref: FluentTimelineItem):
        """Handle item clicked using item reference"""
        try:
            index = self._items.index(item_ref)
            self.item_clicked.emit(index)
        except ValueError:
            # Item not found, should not happen if managed correctly
            pass

    def _on_theme_changed(self, _=None):  # Add default for signal argument
        """Handle theme change"""
        self._setup_style()
        for item_widget in self._items:
            item_widget._on_theme_changed()  # Propagate theme change to items
