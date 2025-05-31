"""
Fluent Design Timeline Component
Visual timeline for displaying chronological events and processes
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QFrame, QScrollArea, QSizePolicy, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, Signal, QDateTime, QPropertyAnimation, Property, QByteArray, QAbstractAnimation
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import FluentRevealEffect, FluentMicroInteraction, FluentTransition, FluentParallel
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
    pulse_progress_changed = Signal()

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
        self._content_widget_internal: Optional[QWidget] = None
        self._pulse_progress = 0.0

        self._title_label: Optional[QLabel] = None
        self._desc_label: Optional[QLabel] = None
        self._timestamp_label: Optional[QLabel] = None
        self._dot_container: Optional[QFrame] = None
        self._pulse_animation: Optional[QPropertyAnimation] = None

        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_MEDIUM)

    def _setup_ui(self):
        """Setup UI"""
        self.setFrameStyle(QFrame.Shape.NoFrame)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        self._dot_container = QFrame()
        self._dot_container.setFixedWidth(self._dot_size + 8)
        self._dot_container.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 16)
        content_layout.setSpacing(4)

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

        if self._dot_container:
            self._dot_container.setStyleSheet("""
                QFrame {
                    background-color: transparent;
                    border: none;
                }
            """)

        if self._title_label:
            title_color = theme.get_color('text_primary')
            self._title_label.setStyleSheet(f"color: {title_color.name()};")

        if self._desc_label:
            desc_color = theme.get_color('text_secondary')
            self._desc_label.setStyleSheet(f"color: {desc_color.name()};")

        if self._timestamp_label:
            timestamp_color = theme.get_color('text_tertiary')
            self._timestamp_label.setStyleSheet(
                f"color: {timestamp_color.name()};")

        self.update()

    def _setup_animations(self):
        """Setup animations"""
        self._pulse_animation = QPropertyAnimation(
            self, QByteArray(b"pulse_progress"))
        self._pulse_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._pulse_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def paintEvent(self, event):
        """Custom paint event for timeline dot and line"""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_timeline_elements(painter)

    def _draw_timeline_elements(self, painter: QPainter):
        """Draw timeline dot and connecting line"""
        if not theme_manager or not self._dot_container:
            return
        theme = theme_manager
        dot_rect = self._dot_container.geometry()
        dot_center_x = dot_rect.center().x()
        dot_center_y = dot_rect.top() + self._dot_size // 2 + 8
        dot_color = self._get_status_color()
        line_color = theme.get_color('border')
        painter.setPen(QPen(line_color, self._line_width))
        if dot_center_y > self._dot_size:
            painter.drawLine(dot_center_x, 0, dot_center_x,
                             dot_center_y - self._dot_size // 2)
        painter.drawLine(dot_center_x, dot_center_y + self._dot_size // 2,
                         dot_center_x, self.height())
        self._draw_status_dot(painter, dot_center_x, dot_center_y, dot_color)

    def _draw_status_dot(self, painter: QPainter, x: int, y: int, color: QColor):
        """Draw status dot"""
        ring_color = color.lighter(120)
        painter.setPen(QPen(ring_color, 2))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawEllipse(x - self._dot_size // 2, y - self._dot_size // 2,
                            self._dot_size, self._dot_size)
        inner_size = self._dot_size - 4
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(x - inner_size // 2, y - inner_size // 2,
                            inner_size, inner_size)
        if self._status == self.Status.CURRENT and self._pulse_animation and \
           self._pulse_animation.state() == QPropertyAnimation.State.Running:
            pulse_factor = self._pulse_progress
            pulse_size = self._dot_size + int(4 * pulse_factor)
            pulse_color = QColor(color)
            pulse_color.setAlpha(int(50 * (1 - pulse_factor)))
            painter.setBrush(QBrush(pulse_color))
            painter.drawEllipse(x - pulse_size // 2, y - pulse_size // 2,
                                pulse_size, pulse_size)

    def _get_status_color(self) -> QColor:
        """Get color based on status"""
        if not theme_manager:
            return QColor(Qt.GlobalColor.gray)
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
            return "Invalid date"
        now = datetime.now()
        diff = now - py_timestamp
        if diff.days > 0:
            return f"{diff.days} days ago" if diff.days > 1 else "1 day ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago" if hours > 1 else "1 hour ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago" if minutes > 1 else "1 minute ago"
        else:
            return "just now"

    def _get_pulse_progress(self) -> float:
        return self._pulse_progress

    def _set_pulse_progress(self, value: float):
        if self._pulse_progress != value:
            self._pulse_progress = value
            self.pulse_progress_changed.emit()
            self.update()

    pulse_progress = Property(float, _get_pulse_progress,
                              _set_pulse_progress, None, "", notify=pulse_progress_changed)

    def setTitle(self, title: str):
        """Set item title"""
        self._title = title
        if self._title_label:
            self._title_label.setText(title)

    def title(self) -> str:
        """Get item title"""
        return self._title

    def setDescription(self, description: str):
        """Set item description"""
        self._description = description
        if self._desc_label:
            self._desc_label.setText(description)

    def description(self) -> str:
        """Get item description"""
        return self._description

    def setTimestamp(self, timestamp: Union[datetime, QDateTime]):
        """Set item timestamp"""
        self._timestamp = timestamp
        if self._timestamp_label and self._timestamp:
            self._timestamp_label.setText(
                self._format_timestamp(self._timestamp))

    def timestamp(self) -> Optional[Union[datetime, QDateTime]]:
        """Get item timestamp"""
        return self._timestamp

    def setStatus(self, status: Status):
        """Set item status"""
        if self._status == status and self._status == self.Status.CURRENT and \
           self._pulse_animation and self._pulse_animation.state() == QPropertyAnimation.State.Running:
            return
        self._status = status
        self.update()
        if self._pulse_animation:
            if status == self.Status.CURRENT:
                self._start_pulse_animation()
            else:
                self._pulse_animation.stop()
                self._set_pulse_progress(0.0)

    def status(self) -> Status:
        """Get item status"""
        return self._status

    def setContentWidget(self, widget: QWidget):
        """Set custom content widget"""
        if self._content_widget_internal:
            FluentAnimation.fade_out(
                self._content_widget_internal, duration=FluentAnimation.DURATION_FAST)
            self._content_widget_internal.setParent(None)
            self._content_widget_internal.deleteLater()
        self._content_widget_internal = widget
        if widget:
            current_layout = self.layout()
            if current_layout and current_layout.count() > 1:
                content_item = current_layout.itemAt(1)
                if content_item and content_item.widget():
                    content_frame = content_item.widget()
                    if content_frame:
                        content_frame_layout = content_frame.layout()
                        if content_frame_layout:
                            content_frame_layout.addWidget(widget)
                            FluentRevealEffect.fade_in(
                                widget, duration=FluentAnimation.DURATION_MEDIUM)
                        else:
                            new_content_layout = QVBoxLayout(content_frame)
                            new_content_layout.addWidget(widget)
                            FluentRevealEffect.fade_in(
                                widget, duration=FluentAnimation.DURATION_MEDIUM)

    def contentWidget(self) -> Optional[QWidget]:
        """Get content widget"""
        return self._content_widget_internal

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
        if self._pulse_animation:
            if self._pulse_animation.state() == QPropertyAnimation.State.Running:
                self._pulse_animation.stop()
            self._pulse_animation.setStartValue(0.0)
            self._pulse_animation.setEndValue(1.0)
            self._pulse_animation.setDuration(1000)
            self._pulse_animation.setLoopCount(-1)
            self._pulse_animation.start()

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            FluentMicroInteraction.button_press(self, scale=0.98)
            self.clicked.emit()
        super().mousePressEvent(event)

    def _on_theme_changed(self, _=None):
        """Handle theme change"""
        self._setup_style()
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_FAST)


class FluentTimeline(QScrollArea):
    """Fluent Design timeline widget"""

    item_clicked = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._items: List[FluentTimelineItem] = []
        self._reverse_order = False
        self._content_widget_internal: Optional[QWidget] = None
        self._layout_internal: Optional[QVBoxLayout] = None
        self._setup_ui()
        self._setup_style()
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_MEDIUM)

    def _setup_ui(self):
        """Setup UI"""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._content_widget_internal = QWidget()
        self._layout_internal = QVBoxLayout(self._content_widget_internal)
        self._layout_internal.setContentsMargins(16, 16, 16, 16)
        self._layout_internal.setSpacing(0)
        self._layout_internal.addStretch()
        self.setWidget(self._content_widget_internal)

    def _setup_style(self):
        """Setup style"""
        if not theme_manager:
            return
        theme = theme_manager
        style_sheet = f"""
            FluentTimeline {{
                background-color: {theme.get_color('background').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
            FluentTimeline > QWidget > QWidget {{
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background: {theme.get_color('surface').name()};
                border: none;
                border-radius: 6px;
                width: 12px;
                margin: 1px 1px 1px 1px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme.get_color('border').name()};
                border-radius: 5px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme.get_color('text_secondary').name()};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px; 
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
        self.setObjectName("FluentTimeline")
        self.setStyleSheet(style_sheet)
        if self._content_widget_internal:
            self._content_widget_internal.setStyleSheet(
                "background-color: transparent;")

    def addItem(self, title: str = "", description: str = "",
                timestamp: Optional[Union[datetime, QDateTime]] = None,
                status: FluentTimelineItem.Status = FluentTimelineItem.Status.PENDING) -> int:
        """Add timeline item"""
        if not self._layout_internal or not self._content_widget_internal:
            return -1
        item = FluentTimelineItem(
            title, description, timestamp, status, self._content_widget_internal)
        item.clicked.connect(
            lambda item_ref=item: self._on_item_clicked_ref(item_ref))
        if self._reverse_order:
            self._layout_internal.insertWidget(0, item)
            self._items.insert(0, item)
        else:
            self._layout_internal.insertWidget(len(self._items), item)
            self._items.append(item)
        FluentRevealEffect.slide_in(
            item, duration=FluentAnimation.DURATION_MEDIUM, direction="down")
        return self._items.index(item)

    def insertItem(self, index: int, title: str = "", description: str = "",
                   timestamp: Optional[Union[datetime, QDateTime]] = None,
                   status: FluentTimelineItem.Status = FluentTimelineItem.Status.PENDING):
        """Insert item at index"""
        if not (0 <= index <= len(self._items) and self._layout_internal and self._content_widget_internal):
            return
        item = FluentTimelineItem(
            title, description, timestamp, status, self._content_widget_internal)
        item.clicked.connect(
            lambda item_ref=item: self._on_item_clicked_ref(item_ref))
        self._layout_internal.insertWidget(index, item)
        self._items.insert(index, item)
        FluentRevealEffect.slide_in(
            item, duration=FluentAnimation.DURATION_MEDIUM, direction="down")

    def removeItem(self, index: int):
        """Remove item at index"""
        if not (0 <= index < len(self._items) and self._layout_internal and self._content_widget_internal):
            return
        item_widget_to_remove = self._items[index]
        group_anim = FluentParallel(item_widget_to_remove)
        fade_anim = FluentTransition._create_fade_transition(
            item_widget_to_remove, FluentAnimation.DURATION_FAST, FluentTransition.EASE_SMOOTH)
        current_opacity = 1.0
        effect = item_widget_to_remove.graphicsEffect()
        if isinstance(effect, QGraphicsOpacityEffect):
            current_opacity = effect.opacity()
        fade_anim.setStartValue(current_opacity)
        fade_anim.setEndValue(0.0)
        group_anim.addAnimation(fade_anim)
        geom_anim = QPropertyAnimation(
            item_widget_to_remove, QByteArray(b"maximumHeight"))
        geom_anim.setDuration(FluentAnimation.DURATION_FAST)
        geom_anim.setStartValue(item_widget_to_remove.height())
        geom_anim.setEndValue(0)
        geom_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        group_anim.addAnimation(geom_anim)

        def on_finished_removal():
            if item_widget_to_remove in self._items:
                self._items.remove(item_widget_to_remove)
            if self._layout_internal and item_widget_to_remove.parent() == self._content_widget_internal:
                self._layout_internal.removeWidget(item_widget_to_remove)
            item_widget_to_remove.setParent(None)
            item_widget_to_remove.deleteLater()
        group_anim.finished.connect(on_finished_removal)
        group_anim.start()

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
        if not self._items or not self._layout_internal:
            self._items.clear()
            if self._layout_internal:
                while self._layout_internal.count() > 1:
                    child = self._layout_internal.takeAt(0)
                    if child and child.widget():
                        child.widget().setParent(None)
                        child.widget().deleteLater()
            return

        master_removal_animation = FluentParallel(self)
        for item_widget in list(self._items):
            group_anim = FluentParallel(item_widget)  # This is FluentParallel
            fade_anim = FluentTransition._create_fade_transition(
                item_widget, FluentAnimation.DURATION_FAST, FluentTransition.EASE_SMOOTH)
            current_opacity = 1.0
            effect = item_widget.graphicsEffect()
            if isinstance(effect, QGraphicsOpacityEffect):
                current_opacity = effect.opacity()
            fade_anim.setStartValue(current_opacity)
            fade_anim.setEndValue(0.0)
            # This expects QPropertyAnimation
            group_anim.addAnimation(fade_anim)

            geom_anim = QPropertyAnimation(
                item_widget, QByteArray(b"maximumHeight"))
            geom_anim.setDuration(FluentAnimation.DURATION_FAST)
            geom_anim.setStartValue(item_widget.height())
            geom_anim.setEndValue(0)
            geom_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
            # This expects QPropertyAnimation
            group_anim.addAnimation(geom_anim)

            # To add a FluentParallel's underlying QParallelAnimationGroup to another:
            if hasattr(master_removal_animation, '_parallel') and hasattr(group_anim, '_parallel'):
                master_removal_animation._parallel.addAnimation(
                    group_anim._parallel)

        def after_all_cleared():
            for item_widget_to_clear in list(self._items):
                if self._layout_internal and item_widget_to_clear.parent() == self._content_widget_internal:
                    self._layout_internal.removeWidget(item_widget_to_clear)
                item_widget_to_clear.setParent(None)
                item_widget_to_clear.deleteLater()
            self._items.clear()
        master_removal_animation.finished.connect(after_all_cleared)
        master_removal_animation.start()

    def setReverseOrder(self, reverse: bool):
        """Set whether to display items in reverse order (newest first)"""
        if self._reverse_order == reverse or not self._layout_internal or not self._content_widget_internal:
            return
        self._reverse_order = reverse
        items_copy = list(self._items)
        group_fade_out = FluentParallel(self)
        for itm in items_copy:
            anim = FluentTransition._create_fade_transition(
                itm, FluentAnimation.DURATION_FAST, FluentTransition.EASE_SMOOTH)
            anim.setEndValue(0.0)
            group_fade_out.addAnimation(anim)

        def reorder_and_fade_in():
            if self._layout_internal and self._content_widget_internal:  # Ensure layout is valid
                for i in range(self._layout_internal.count() - 1, -1, -1):
                    layout_item = self._layout_internal.itemAt(i)
                    if layout_item and layout_item.widget() and layout_item.widget() in items_copy:
                        widget = layout_item.widget()
                        self._layout_internal.removeWidget(widget)
                        widget.setParent(None)
                self._items.clear()
                if reverse:
                    items_copy.reverse()
                group_fade_in = FluentParallel(self)
                for itm_to_add in items_copy:
                    if self._reverse_order:
                        self._layout_internal.insertWidget(0, itm_to_add)
                        self._items.insert(0, itm_to_add)
                    else:
                        self._layout_internal.insertWidget(
                            len(self._items), itm_to_add)
                        self._items.append(itm_to_add)
                    itm_to_add.setParent(self._content_widget_internal)
                    itm_to_add.show()

                    current_effect = itm_to_add.graphicsEffect()
                    if not isinstance(current_effect, QGraphicsOpacityEffect):
                        opacity_effect = QGraphicsOpacityEffect(itm_to_add)
                        itm_to_add.setGraphicsEffect(opacity_effect)
                        opacity_effect.setOpacity(0.0)
                    elif current_effect:  # It is QGraphicsEffect but maybe not QGraphicsOpacityEffect
                        current_effect.setOpacity(0.0)  # type: ignore

                    anim_in = FluentTransition._create_fade_transition(
                        itm_to_add, FluentAnimation.DURATION_MEDIUM, FluentTransition.EASE_SMOOTH)
                    anim_in.setStartValue(0.0)  # Ensure start from transparent
                    anim_in.setEndValue(1.0)
                    group_fade_in.addAnimation(anim_in)
                group_fade_in.start()
            else:  # Fallback if layout became invalid somehow
                self._items.clear()

        if items_copy:
            group_fade_out.finished.connect(reorder_and_fade_in)
            group_fade_out.start()
        else:
            reorder_and_fade_in()

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
        scroll_bar = self.verticalScrollBar()
        if scroll_bar:
            scroll_bar.setValue(0)

    def scrollToBottom(self):
        """Scroll to bottom"""
        scroll_bar = self.verticalScrollBar()
        if scroll_bar:
            scroll_bar.setValue(scroll_bar.maximum())

    def _on_item_clicked_ref(self, item_ref: FluentTimelineItem):
        """Handle item clicked using item reference"""
        try:
            index = self._items.index(item_ref)
            self.item_clicked.emit(index)
        except ValueError:
            pass

    def _on_theme_changed(self, _=None):
        """Handle theme change"""
        self._setup_style()
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_FAST)
        for item_widget in self._items:
            item_widget._on_theme_changed()
