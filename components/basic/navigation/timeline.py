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
from typing import Optional, List, Union, cast, Dict
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

    # Class-level cache for status colors
    _status_color_cache: Dict[tuple, QColor] = {}

    def __init__(self, title: str = "", description: str = "",
                 timestamp: Optional[Union[datetime, QDateTime]] = None,
                 status: Status = Status.PENDING,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Core properties
        self._title = title
        self._description = description
        self._timestamp = timestamp
        self._status = status
        self._clickable = False

        # Visual properties
        self._dot_size = 12
        self._line_width = 2
        self._pulse_progress = 0.0
        self._needs_dot_redraw = True

        # Widget references
        self._content_widget_internal: Optional[QWidget] = None
        self._title_label: Optional[QLabel] = None
        self._desc_label: Optional[QLabel] = None
        self._timestamp_label: Optional[QLabel] = None
        self._dot_container: Optional[QFrame] = None
        self._pulse_animation: Optional[QPropertyAnimation] = None

        # Setup
        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_MEDIUM)

    def _setup_ui(self):
        """Setup UI with optimized layout"""
        self.setFrameStyle(QFrame.Shape.NoFrame)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # Dot container with fixed size for better performance
        self._dot_container = QFrame()
        self._dot_container.setFixedWidth(self._dot_size + 8)
        self._dot_container.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # Content frame
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 16)
        content_layout.setSpacing(4)

        # Create header only if needed (title or timestamp exists)
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

        # Add description if provided
        if self._description:
            self._desc_label = QLabel(self._description)
            self._desc_label.setWordWrap(True)
            desc_font = QFont()
            desc_font.setPointSize(13)
            self._desc_label.setFont(desc_font)
            content_layout.addWidget(self._desc_label)

        # Add components to main layout
        main_layout.addWidget(self._dot_container)
        main_layout.addWidget(content_frame, 1)

    def _setup_style(self):
        """Setup style with efficient stylesheet application"""
        if not theme_manager:
            return
        theme = theme_manager

        # Use direct styling for performance
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

        self._needs_dot_redraw = True
        self.update()

    def _setup_animations(self):
        """Setup optimized pulse animation"""
        self._pulse_animation = QPropertyAnimation(
            self, QByteArray(b"pulse_progress"))
        self._pulse_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._pulse_animation.setEasingCurve(FluentAnimation.EASE_OUT)
        # Use keyframes for smoother animation with less CPU usage
        self._pulse_animation.setKeyValueAt(0.0, 0.0)
        self._pulse_animation.setKeyValueAt(0.5, 1.0)
        self._pulse_animation.setKeyValueAt(1.0, 0.0)

    def resizeEvent(self, event):
        """Mark for redraw on resize"""
        super().resizeEvent(event)
        self._needs_dot_redraw = True

    def paintEvent(self, event):
        """Optimized paint event with conditional rendering"""
        super().paintEvent(event)

        # Only redraw when necessary (status change, size change, or pulse animation)
        if self._needs_dot_redraw or self._status == self.Status.CURRENT:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self._draw_timeline_elements(painter)

            # Reset redraw flag except for current status (needs continuous updates for pulse)
            if self._status != self.Status.CURRENT:
                self._needs_dot_redraw = False

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

        # Draw lines
        painter.setPen(QPen(line_color, self._line_width))
        if dot_center_y > self._dot_size:
            painter.drawLine(dot_center_x, 0, dot_center_x,
                             dot_center_y - self._dot_size // 2)
        painter.drawLine(dot_center_x, dot_center_y + self._dot_size // 2,
                         dot_center_x, self.height())

        # Draw status dot
        self._draw_status_dot(painter, dot_center_x, dot_center_y, dot_color)

    def _draw_status_dot(self, painter: QPainter, x: int, y: int, color: QColor):
        """Draw status dot with optimized rendering"""
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

        # Draw pulse effect only when needed
        if (self._status == self.Status.CURRENT and
            self._pulse_animation and
            self._pulse_animation.state() == QPropertyAnimation.State.Running and
                self._pulse_progress > 0.01):  # Skip insignificant pulses

            pulse_factor = self._pulse_progress
            pulse_size = self._dot_size + int(4 * pulse_factor)
            pulse_color = QColor(color)
            pulse_color.setAlpha(int(50 * (1 - pulse_factor)))
            painter.setBrush(QBrush(pulse_color))
            painter.drawEllipse(x - pulse_size // 2, y - pulse_size // 2,
                                pulse_size, pulse_size)

    def _get_status_color(self) -> QColor:
        """Get color based on status with caching for performance"""
        if not theme_manager:
            return QColor(Qt.GlobalColor.gray)

        theme = theme_manager

        # Use class-level cache for status colors
        cache_key = (self._status, theme.current_theme)
        if cache_key in self._status_color_cache:
            return self._status_color_cache[cache_key]

        # Calculate if not in cache
        status_colors = {
            self.Status.PENDING: theme.get_color('text_tertiary'),
            self.Status.CURRENT: theme.get_color('primary'),
            self.Status.COMPLETED: theme.get_color('success'),
            self.Status.ERROR: theme.get_color('error'),
            self.Status.WARNING: theme.get_color('warning')
        }
        color = status_colors.get(
            self._status, theme.get_color('text_tertiary'))

        # Store in cache
        self._status_color_cache[cache_key] = color
        return color

    def _format_timestamp(self, timestamp_input: Union[datetime, QDateTime]) -> str:
        """Format timestamp for display"""
        # Convert QDateTime to Python datetime if needed
        py_timestamp: datetime
        if isinstance(timestamp_input, QDateTime):
            py_timestamp = cast(datetime, timestamp_input.toPython())
        elif isinstance(timestamp_input, datetime):
            py_timestamp = timestamp_input
        else:
            return "Invalid date"

        # Format relative time
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

    # Pulse animation property with optimization
    def _get_pulse_progress(self) -> float:
        return self._pulse_progress

    def _set_pulse_progress(self, value: float):
        if self._pulse_progress != value:
            self._pulse_progress = value
            self.pulse_progress_changed.emit()
            # Only update for current status (reduces repaints)
            if self._status == self.Status.CURRENT:
                self.update()

    pulse_progress = Property(float, _get_pulse_progress, _set_pulse_progress, None, "",
                              notify=pulse_progress_changed)

    def setTitle(self, title: str):
        """Set item title with change check"""
        if self._title == title:
            return

        self._title = title
        if self._title_label:
            self._title_label.setText(title)

    def title(self) -> str:
        """Get item title"""
        return self._title

    def setDescription(self, description: str):
        """Set item description with change check"""
        if self._description == description:
            return

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
        """Set item status with optimized updates"""
        # Skip if no change and not pulsing
        if self._status == status:
            if (status == self.Status.CURRENT and
                self._pulse_animation and
                    self._pulse_animation.state() == QPropertyAnimation.State.Running):
                return
            elif status != self.Status.CURRENT:
                return

        # Update status and redraw
        self._status = status
        self._needs_dot_redraw = True
        self.update()

        # Handle pulse animation
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
        """Set custom content widget with efficient transitions"""
        if self._content_widget_internal:
            # Fade out current content
            FluentAnimation.fade_out(
                self._content_widget_internal,
                duration=FluentAnimation.DURATION_FAST,
            )
            self._content_widget_internal.setParent(None)

        # Set new content
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
                            # Add to existing layout
                            content_frame_layout.addWidget(widget)
                            FluentRevealEffect.fade_in(
                                widget, duration=FluentAnimation.DURATION_MEDIUM)
                        else:
                            # Create new layout
                            new_content_layout = QVBoxLayout(content_frame)
                            new_content_layout.addWidget(widget)
                            FluentRevealEffect.fade_in(
                                widget, duration=FluentAnimation.DURATION_MEDIUM)

    def contentWidget(self) -> Optional[QWidget]:
        """Get content widget"""
        return self._content_widget_internal

    def setClickable(self, clickable: bool):
        """Set whether item is clickable"""
        if self._clickable == clickable:
            return

        self._clickable = clickable
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if clickable else Qt.CursorShape.ArrowCursor)

    def isClickable(self) -> bool:
        """Check if item is clickable"""
        return self._clickable

    def _start_pulse_animation(self):
        """Start optimized pulse animation"""
        if not self._pulse_animation:
            return

        # Reset running animation
        if self._pulse_animation.state() == QPropertyAnimation.State.Running:
            self._pulse_animation.stop()

        # Configure and start animation
        self._pulse_animation.setDuration(1000)
        self._pulse_animation.setLoopCount(-1)  # Infinite loop
        self._pulse_animation.start()

    def mousePressEvent(self, event):
        """Optimized mouse press handling"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            FluentMicroInteraction.button_press(self, scale=0.98)
            self.clicked.emit()
        super().mousePressEvent(event)

    def _on_theme_changed(self, _=None):
        """Efficient theme change handling"""
        # Clear color cache on theme change
        self._status_color_cache.clear()

        # Update styles
        self._setup_style()
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_FAST)


class FluentTimeline(QScrollArea):
    """Fluent Design timeline widget with optimized rendering"""

    item_clicked = Signal(int)

    # Class constants for layout
    LAYOUT_MARGINS = 16
    ITEM_SPACING = 0

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Properties
        self._items: List[FluentTimelineItem] = []
        self._reverse_order = False
        self._content_widget_internal: Optional[QWidget] = None
        self._layout_internal: Optional[QVBoxLayout] = None
        self._style_initialized = False

        # Setup
        self._setup_ui()
        self._setup_style()

        # Connect theme changes
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

        # Initial animation
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_MEDIUM)

    def _setup_ui(self):
        """Setup optimized UI structure"""
        # Configure scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create content widget
        self._content_widget_internal = QWidget()

        # Create layout
        self._layout_internal = QVBoxLayout(self._content_widget_internal)
        self._layout_internal.setContentsMargins(
            self.LAYOUT_MARGINS, self.LAYOUT_MARGINS,
            self.LAYOUT_MARGINS, self.LAYOUT_MARGINS
        )
        self._layout_internal.setSpacing(self.ITEM_SPACING)
        self._layout_internal.addStretch()

        # Set content widget
        self.setWidget(self._content_widget_internal)

    def _setup_style(self):
        """Setup efficient styling"""
        if not theme_manager:
            return

        # Skip if already styled for this theme
        if self._style_initialized:
            return

        theme = theme_manager

        # Build optimized stylesheet
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

        # Apply stylesheet
        self.setObjectName("FluentTimeline")
        self.setStyleSheet(style_sheet)

        # Style content widget
        if self._content_widget_internal:
            self._content_widget_internal.setStyleSheet(
                "background-color: transparent;")

        self._style_initialized = True

    def addItem(self, title: str = "", description: str = "",
                timestamp: Optional[Union[datetime, QDateTime]] = None,
                status: FluentTimelineItem.Status = FluentTimelineItem.Status.PENDING) -> int:
        """Add timeline item with optimized insertion"""
        if not self._layout_internal or not self._content_widget_internal:
            return -1

        # Create item
        item = FluentTimelineItem(
            title, description, timestamp, status, self._content_widget_internal)
        item.clicked.connect(
            lambda item_ref=item: self._on_item_clicked_ref(item_ref))

        # Add to appropriate position
        if self._reverse_order:
            self._layout_internal.insertWidget(0, item)
            self._items.insert(0, item)
        else:
            # Position before stretch spacer
            insert_pos = self._layout_internal.count() - 1
            if insert_pos < 0:
                insert_pos = 0
            self._layout_internal.insertWidget(insert_pos, item)
            self._items.append(item)

        # Animate
        FluentRevealEffect.slide_in(
            item, duration=FluentAnimation.DURATION_MEDIUM, direction="down")

        return self._items.index(item)

    def insertItem(self, index: int, title: str = "", description: str = "",
                   timestamp: Optional[Union[datetime, QDateTime]] = None,
                   status: FluentTimelineItem.Status = FluentTimelineItem.Status.PENDING):
        """Insert item at specific index with validation"""
        # Validate parameters
        if not (0 <= index <= len(self._items) and
                self._layout_internal and
                self._content_widget_internal):
            return

        # Create item
        item = FluentTimelineItem(
            title, description, timestamp, status, self._content_widget_internal)
        item.clicked.connect(
            lambda item_ref=item: self._on_item_clicked_ref(item_ref))

        # Calculate layout index based on reverse order setting
        layout_index = index
        if self._reverse_order:
            layout_index = len(self._items) - index

        # Insert into layout and list
        self._layout_internal.insertWidget(layout_index, item)
        self._items.insert(index, item)

        # Animate
        FluentRevealEffect.slide_in(
            item, duration=FluentAnimation.DURATION_MEDIUM, direction="down")

    def removeItem(self, index: int):
        """Remove item with optimized animation"""
        # Validate index
        if not (0 <= index < len(self._items) and
                self._layout_internal and
                self._content_widget_internal):
            return

        # Get item to remove
        item_widget_to_remove = self._items[index]

        # Create animation group
        group_anim = FluentParallel(item_widget_to_remove)

        # Add fade animation
        fade_anim = FluentTransition._create_fade_transition(
            item_widget_to_remove,
            FluentAnimation.DURATION_FAST,
            FluentTransition.EASE_SMOOTH
        )

        # Get current opacity
        current_opacity = 1.0
        effect = item_widget_to_remove.graphicsEffect()
        if isinstance(effect, QGraphicsOpacityEffect):
            current_opacity = effect.opacity()

        # Configure fade
        fade_anim.setStartValue(current_opacity)
        fade_anim.setEndValue(0.0)
        group_anim.addAnimation(fade_anim)

        # Add height animation
        geom_anim = QPropertyAnimation(
            item_widget_to_remove, QByteArray(b"maximumHeight"))
        geom_anim.setDuration(FluentAnimation.DURATION_FAST)
        geom_anim.setStartValue(item_widget_to_remove.height())
        geom_anim.setEndValue(0)
        geom_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        group_anim.addAnimation(geom_anim)

        # Clean up after animation
        def on_finished_removal():
            if item_widget_to_remove in self._items:
                self._items.remove(item_widget_to_remove)

            if (self._layout_internal and
                    item_widget_to_remove.parent() == self._content_widget_internal):
                self._layout_internal.removeWidget(item_widget_to_remove)

            item_widget_to_remove.setParent(None)
            item_widget_to_remove.deleteLater()

        group_anim.finished.connect(on_finished_removal)
        group_anim.start()

    def item(self, index: int) -> Optional[FluentTimelineItem]:
        """Get item at index with bounds checking"""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def itemCount(self) -> int:
        """Get item count"""
        return len(self._items)

    def clear(self):
        """Clear all items with batch animation"""
        # Quick path if no items
        if not self._items or not self._layout_internal:
            self._items.clear()
            if self._layout_internal:
                while self._layout_internal.count() > 1:
                    child = self._layout_internal.takeAt(0)
                    if child and child.widget():
                        child.widget().setParent(None)
                        child.widget().deleteLater()
            return

        # Create master animation for all removals
        master_removal_animation = FluentParallel(self)
        for item_widget in list(self._items):
            # Create animation group for item
            group_anim = FluentParallel(item_widget)

            # Add fade animation
            fade_anim = FluentTransition._create_fade_transition(
                item_widget,
                FluentAnimation.DURATION_FAST,
                FluentTransition.EASE_SMOOTH
            )

            # Get current opacity
            current_opacity = 1.0
            effect = item_widget.graphicsEffect()
            if isinstance(effect, QGraphicsOpacityEffect):
                current_opacity = effect.opacity()

            # Configure fade
            fade_anim.setStartValue(current_opacity)
            fade_anim.setEndValue(0.0)
            group_anim.addAnimation(fade_anim)

            # Add height animation
            geom_anim = QPropertyAnimation(
                item_widget, QByteArray(b"maximumHeight"))
            geom_anim.setDuration(FluentAnimation.DURATION_FAST)
            geom_anim.setStartValue(item_widget.height())
            geom_anim.setEndValue(0)
            geom_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
            group_anim.addAnimation(geom_anim)

            # Add to master animation
            if hasattr(master_removal_animation, '_parallel') and hasattr(group_anim, '_parallel'):
                master_removal_animation._parallel.addAnimation(
                    group_anim._parallel)

        # Clean up after all animations complete
        def after_all_cleared():
            for item_widget_to_clear in list(self._items):
                if (self._layout_internal and
                        item_widget_to_clear.parent() == self._content_widget_internal):
                    self._layout_internal.removeWidget(item_widget_to_clear)

                item_widget_to_clear.setParent(None)
                item_widget_to_clear.deleteLater()

            self._items.clear()

        master_removal_animation.finished.connect(after_all_cleared)
        master_removal_animation.start()

    def setReverseOrder(self, reverse: bool):
        """Set display order with optimized reordering"""
        # Skip if no change or invalid state
        if (self._reverse_order == reverse or
            not self._layout_internal or
                not self._content_widget_internal):
            return

        # Update order flag
        self._reverse_order = reverse
        items_copy = list(self._items)

        # Skip if no items
        if not items_copy:
            return

        # Create fade-out animation
        group_fade_out = FluentParallel(self)
        for itm in items_copy:
            anim = FluentTransition._create_fade_transition(
                itm, FluentAnimation.DURATION_FAST, FluentTransition.EASE_SMOOTH)
            anim.setEndValue(0.0)
            group_fade_out.addAnimation(anim)

        # Reorder function
        def reorder_and_fade_in():
            if not self._layout_internal or not self._content_widget_internal:
                return

            # Remove all widgets from layout
            for i in range(self._layout_internal.count() - 1, -1, -1):
                layout_item = self._layout_internal.itemAt(i)
                if layout_item and layout_item.widget() and layout_item.widget() in items_copy:
                    widget = layout_item.widget()
                    self._layout_internal.removeWidget(widget)
                    widget.setParent(None)

            # Clear list
            self._items.clear()

            # Reverse if needed
            if reverse:
                items_copy.reverse()

            # Fade in animation group
            group_fade_in = FluentParallel(self)

            # Re-add items in new order
            for itm_to_add in items_copy:
                # Add to layout
                if self._reverse_order:
                    self._layout_internal.insertWidget(0, itm_to_add)
                    self._items.insert(0, itm_to_add)
                else:
                    insert_pos = self._layout_internal.count() - 1
                    if insert_pos < 0:
                        insert_pos = 0
                    self._layout_internal.insertWidget(insert_pos, itm_to_add)
                    self._items.append(itm_to_add)

                # Re-parent and show
                itm_to_add.setParent(self._content_widget_internal)
                itm_to_add.show()

                # Setup opacity effect
                current_effect = itm_to_add.graphicsEffect()
                if not isinstance(current_effect, QGraphicsOpacityEffect):
                    opacity_effect = QGraphicsOpacityEffect(itm_to_add)
                    itm_to_add.setGraphicsEffect(opacity_effect)
                    opacity_effect.setOpacity(0.0)
                elif current_effect:
                    current_effect.setOpacity(0.0)

                # Create fade-in animation
                anim_in = FluentTransition._create_fade_transition(
                    itm_to_add,
                    FluentAnimation.DURATION_MEDIUM,
                    FluentTransition.EASE_SMOOTH
                )
                anim_in.setStartValue(0.0)
                anim_in.setEndValue(1.0)
                group_fade_in.addAnimation(anim_in)

            # Start animations
            group_fade_in.start()

        # Connect and start fade-out
        group_fade_out.finished.connect(reorder_and_fade_in)
        group_fade_out.start()

    def reverseOrder(self) -> bool:
        """Check if items are in reverse order"""
        return self._reverse_order

    def scrollToItem(self, index: int):
        """Scroll to specific item"""
        if 0 <= index < len(self._items):
            item = self._items[index]
            self.ensureWidgetVisible(item)

    def scrollToTop(self):
        """Scroll to top with direct scrollbar control"""
        scroll_bar = self.verticalScrollBar()
        if scroll_bar:
            scroll_bar.setValue(0)

    def scrollToBottom(self):
        """Scroll to bottom with direct scrollbar control"""
        scroll_bar = self.verticalScrollBar()
        if scroll_bar:
            scroll_bar.setValue(scroll_bar.maximum())

    def _on_item_clicked_ref(self, item_ref: FluentTimelineItem):
        """Handle item click with index retrieval"""
        try:
            index = self._items.index(item_ref)
            self.item_clicked.emit(index)
        except ValueError:
            # Item not found (might have been removed)
            pass

    def _on_theme_changed(self, _=None):
        """Efficiently handle theme changes"""
        # Reset style flag
        self._style_initialized = False

        # Update styles
        self._setup_style()

        # Smooth transition
        FluentRevealEffect.fade_in(
            self, duration=FluentAnimation.DURATION_FAST)

        # Update all items
        for item_widget in self._items:
            item_widget._on_theme_changed()
