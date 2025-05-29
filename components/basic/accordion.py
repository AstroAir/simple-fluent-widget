"""
Fluent Design Accordion Component
Expandable and collapsible content panels with smooth animations
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QGraphicsOpacityEffect)
from PySide6.QtCore import (Qt, Signal, QPropertyAnimation, QEasingCurve,
                            Property, QByteArray, QParallelAnimationGroup, QTimer)
from PySide6.QtGui import QFont, QTransform, QPainter, QPen
from core.theme import theme_manager
from core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                      FluentRevealEffect, FluentSequence, FluentParallel)
from core.animation import FluentAnimation
from typing import Optional, List


class FluentAccordionItem(QFrame):
    """Individual accordion item with header and content"""

    # Signals
    expanded = Signal(bool)
    clicked = Signal()

    def __init__(self, title: str = "", content_widget: Optional[QWidget] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._is_expanded = False
        self._content_height = 0
        self._header_height = 48
        self._animation_duration = FluentAnimation.DURATION_MEDIUM
        self._expand_progress = 0.0
        self._hover_progress = 0.0
        self._icon_rotation = 0.0
        self._press_scale = 1.0

        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        if content_widget:
            self.setContentWidget(content_widget)

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setFrameStyle(QFrame.Shape.NoFrame)

        # Main layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Header
        self._header = QFrame()
        self._header.setFixedHeight(self._header_height)
        self._header.setCursor(Qt.CursorShape.PointingHandCursor)

        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(16, 0, 16, 0)
        header_layout.setSpacing(12)

        # Expand/collapse icon
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(16, 16)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_icon()

        # Title label
        self._title_label = QLabel(self._title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.Medium)
        self._title_label.setFont(title_font)

        header_layout.addWidget(self._icon_label)
        header_layout.addWidget(self._title_label)
        header_layout.addStretch()

        # Content container with opacity effect for smooth transitions
        self._content_container = QFrame()
        self._content_container.setFixedHeight(0)
        self._content_container.setVisible(False)

        # Add opacity effect for content fade in/out
        self._content_opacity_effect = QGraphicsOpacityEffect()
        self._content_container.setGraphicsEffect(self._content_opacity_effect)

        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(16, 0, 16, 16)
        self._content_layout.setSpacing(8)

        self._layout.addWidget(self._header)
        self._layout.addWidget(self._content_container)

        # Connect header events
        self._header.mousePressEvent = self._on_header_pressed
        self._header.mouseReleaseEvent = self._on_header_released
        self._header.enterEvent = self._on_header_enter
        self._header.leaveEvent = self._on_header_leave

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        # Header style with smooth transition support
        header_style = f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-bottom: none;
                border-radius: 8px 8px 0px 0px;
            }}
            QFrame:hover {{
                background-color: {theme.get_color('surface_hover').name()};
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                background: transparent;
                border: none;
            }}
        """

        # Content style
        content_style = f"""
            QFrame {{
                background-color: {theme.get_color('background').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-top: none;
                border-radius: 0px 0px 8px 8px;
            }}
        """

        self._header.setStyleSheet(header_style)
        self._content_container.setStyleSheet(content_style)

    def _setup_animations(self):
        """Setup enhanced animations"""
        # Enhanced expand animation with spring easing
        self._expand_animation = QPropertyAnimation(
            self, QByteArray(b"expand_progress"))
        self._expand_animation.setDuration(self._animation_duration)
        self._expand_animation.setEasingCurve(FluentTransition.EASE_SPRING)
        self._expand_animation.finished.connect(self._on_expand_finished)

        # Smooth hover animation with subtle easing
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_progress"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)

        # Enhanced icon rotation with elastic easing
        self._icon_animation = QPropertyAnimation(
            self, QByteArray(b"icon_rotation"))
        self._icon_animation.setDuration(self._animation_duration)
        self._icon_animation.setEasingCurve(FluentTransition.EASE_ELASTIC)

        # Content fade animation
        self._content_fade_animation = QPropertyAnimation(
            self._content_opacity_effect, QByteArray(b"opacity"))
        self._content_fade_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._content_fade_animation.setEasingCurve(
            FluentTransition.EASE_SMOOTH)

        # Press scale animation for micro-interaction
        self._press_animation = QPropertyAnimation(
            self, QByteArray(b"press_scale"))
        self._press_animation.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
        self._press_animation.setEasingCurve(FluentTransition.EASE_CRISP)

    def _update_icon(self):
        """Update expand/collapse icon with rotation"""
        theme = theme_manager
        icon_color = theme.get_color('text_secondary')

        # Use Unicode arrow that rotates smoothly
        self._icon_label.setText("▶")
        self._icon_label.setStyleSheet(f"color: {icon_color.name()};")

    def paintEvent(self, event):
        """Custom paint with rotation and scaling"""
        super().paintEvent(event)

        # Apply icon rotation
        if hasattr(self, '_icon_label') and self._icon_rotation != 0:
            painter = QPainter(self._icon_label)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Create rotation transform
            transform = QTransform()
            transform.translate(8, 8)  # Center of 16x16 icon
            transform.rotate(self._icon_rotation)
            transform.translate(-8, -8)

            painter.setTransform(transform)
            painter.end()

    def _get_expand_progress(self):
        return self._expand_progress

    def _set_expand_progress(self, value):
        self._expand_progress = value

        # Smooth height transition with easing
        if self._content_height > 0:
            # Apply easing curve manually for smoother visual effect
            eased_value = self._apply_easing_curve(value)
            height = int(self._content_height * eased_value)
            self._content_container.setFixedHeight(height)

        self.update()

    def _get_hover_progress(self):
        return self._hover_progress

    def _set_hover_progress(self, value):
        self._hover_progress = value
        # Apply subtle hover effect to header
        self._apply_hover_effect(value)
        self.update()

    def _get_icon_rotation(self):
        return self._icon_rotation

    def _set_icon_rotation(self, value):
        self._icon_rotation = value
        self.update()

    def _get_press_scale(self):
        return self._press_scale

    def _set_press_scale(self, value):
        self._press_scale = value
        # Apply scaling transform to header
        if hasattr(self, '_header'):
            self._header.setStyleSheet(
                self._header.styleSheet() +
                f"transform: scale({value});"
            )

    expand_progress = Property(
        float, _get_expand_progress, _set_expand_progress, None, "", user=True)
    hover_progress = Property(
        float, _get_hover_progress, _set_hover_progress, None, "", user=True)
    icon_rotation = Property(float, _get_icon_rotation,
                             _set_icon_rotation, None, "", user=True)
    press_scale = Property(float, _get_press_scale,
                           _set_press_scale, None, "", user=True)

    def _apply_easing_curve(self, value: float) -> float:
        """Apply custom easing curve for smoother animation"""
        # Smooth step function for better visual effect
        if value <= 0:
            return 0
        elif value >= 1:
            return 1
        else:
            # Smooth hermite interpolation
            return value * value * (3 - 2 * value)

    def _apply_hover_effect(self, progress: float):
        """Apply subtle hover effect"""
        if hasattr(self, '_header'):
            # Subtle background color change during hover
            theme = theme_manager
            base_color = theme.get_color('surface')
            hover_color = theme.get_color('surface_hover')

            # Interpolate between base and hover colors
            r = int(base_color.red() +
                    (hover_color.red() - base_color.red()) * progress)
            g = int(base_color.green() +
                    (hover_color.green() - base_color.green()) * progress)
            b = int(base_color.blue() +
                    (hover_color.blue() - base_color.blue()) * progress)

            interpolated_color = f"rgb({r}, {g}, {b})"

            style = self._header.styleSheet()
            # Update background color while preserving other styles
            if "background-color:" in style:
                import re
                style = re.sub(r'background-color:[^;]+;',
                               f'background-color: {interpolated_color};', style)

            self._header.setStyleSheet(style)

    def setTitle(self, title: str):
        """Set accordion item title"""
        self._title = title
        self._title_label.setText(title)

    def title(self) -> str:
        """Get accordion item title"""
        return self._title

    def setContentWidget(self, widget: QWidget):
        """Set content widget with reveal animation"""
        # Clear existing content
        for i in reversed(range(self._content_layout.count())):
            child = self._content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Add new content
        self._content_layout.addWidget(widget)

        # Calculate content height
        widget.adjustSize()
        self._content_height = widget.sizeHint().height() + 32  # Add margins

        # Apply reveal animation to new content if expanded
        if self._is_expanded:
            FluentRevealEffect.fade_in(widget, FluentAnimation.DURATION_FAST)

    def contentWidget(self) -> Optional[QWidget]:
        """Get content widget"""
        if self._content_layout.count() > 0:
            return self._content_layout.itemAt(0).widget()
        return None

    def setExpanded(self, expanded: bool, animate: bool = True):
        """Set expanded state with enhanced animations"""
        if self._is_expanded == expanded:
            return

        self._is_expanded = expanded
        self._update_icon()

        if animate:
            # Create parallel animation group for coordinated effects
            parallel_group = FluentParallel(self)

            # Height animation
            start_value = self._expand_progress
            end_value = 1.0 if expanded else 0.0

            self._expand_animation.setStartValue(start_value)
            self._expand_animation.setEndValue(end_value)
            parallel_group.addAnimation(self._expand_animation)

            # Icon rotation animation
            start_rotation = self._icon_rotation
            end_rotation = 90.0 if expanded else 0.0

            self._icon_animation.setStartValue(start_rotation)
            self._icon_animation.setEndValue(end_rotation)
            parallel_group.addAnimation(self._icon_animation)

            # Content fade animation
            if expanded:
                self._content_container.setVisible(True)
                self._content_opacity_effect.setOpacity(0.0)
                self._content_fade_animation.setStartValue(0.0)
                self._content_fade_animation.setEndValue(1.0)

                # Delay content fade for smoother effect
                QTimer.singleShot(
                    100, lambda: self._content_fade_animation.start())
            else:
                self._content_fade_animation.setStartValue(1.0)
                self._content_fade_animation.setEndValue(0.0)
                parallel_group.addAnimation(self._content_fade_animation)

            parallel_group.start()

            # Add content reveal animation for child widgets
            content_widget = self.contentWidget()
            if expanded and content_widget:
                QTimer.singleShot(150, lambda: FluentRevealEffect.reveal_up(
                    content_widget, 0))

        else:
            # Immediate state change
            self._expand_progress = 1.0 if expanded else 0.0
            self._icon_rotation = 90.0 if expanded else 0.0
            self._content_container.setVisible(expanded)
            self._content_opacity_effect.setOpacity(1.0 if expanded else 0.0)

            if expanded and self._content_height > 0:
                self._content_container.setFixedHeight(self._content_height)
            else:
                self._content_container.setFixedHeight(0)

        self.expanded.emit(expanded)

    def isExpanded(self) -> bool:
        """Check if item is expanded"""
        return self._is_expanded

    def toggle(self, animate: bool = True):
        """Toggle expanded state with micro-interaction"""
        # Add subtle pulse effect for feedback
        if hasattr(self, '_header'):
            FluentMicroInteraction.pulse_animation(self._header, 1.02)

        self.setExpanded(not self._is_expanded, animate)

    def _on_header_pressed(self, event):
        """Handle header press with micro-interaction"""
        # Add press animation for immediate feedback
        self._press_animation.setStartValue(1.0)
        self._press_animation.setEndValue(0.98)
        self._press_animation.start()

        # Add subtle ripple effect
        FluentMicroInteraction.ripple_effect(self._header)

    def _on_header_released(self, event):
        """Handle header release"""
        # Return to normal scale
        self._press_animation.setStartValue(0.98)
        self._press_animation.setEndValue(1.0)
        self._press_animation.start()

        # Toggle on release
        self.toggle()
        self.clicked.emit()

    def _on_header_enter(self, event):
        """Handle mouse enter header with smooth transition"""
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()

    def _on_header_leave(self, event):
        """Handle mouse leave header with smooth transition"""
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()

    def _on_expand_finished(self):
        """Handle expand animation finished"""
        if not self._is_expanded:
            self._content_container.setVisible(False)

    def _on_theme_changed(self, theme):
        """Handle theme change"""
        self._setup_style()
        self._update_icon()


class FluentAccordion(QWidget):
    """Fluent Design accordion widget with multiple expandable items"""

    # Signals
    item_expanded = Signal(int, bool)  # index, expanded
    item_clicked = Signal(int)  # index

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items: List[FluentAccordionItem] = []
        self._allow_multiple = True
        self._animate_transitions = True
        self._stagger_delay = 50  # Delay between item animations

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        # Slightly larger gap for better visual separation
        self._layout.setSpacing(2)

        # Add stretch at the end
        self._layout.addStretch()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentAccordion {{
                background-color: {theme.get_color('background').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def addItem(self, title: str, content_widget: Optional[QWidget] = None) -> int:
        """Add accordion item with staggered reveal animation"""
        item = FluentAccordionItem(title, content_widget, self)

        # Connect signals
        item.expanded.connect(lambda expanded, idx=len(
            self._items): self._on_item_expanded(idx, expanded))
        item.clicked.connect(lambda idx=len(self._items): self._on_item_clicked(idx))

        # Insert before stretch
        self._layout.insertWidget(len(self._items), item)
        self._items.append(item)

        # Add staggered reveal animation for new items
        if self._animate_transitions:
            delay = len(self._items) * self._stagger_delay
            FluentRevealEffect.reveal_up(item, delay)

        return len(self._items) - 1

    def insertItem(self, index: int, title: str, content_widget: Optional[QWidget] = None):
        """Insert accordion item at index with smooth animation"""
        if not 0 <= index <= len(self._items):
            return

        item = FluentAccordionItem(title, content_widget, self)

        # Connect signals
        item.expanded.connect(
            lambda expanded, idx=index: self._on_item_expanded(idx, expanded))
        item.clicked.connect(lambda idx=index: self._on_item_clicked(idx))

        self._layout.insertWidget(index, item)
        self._items.insert(index, item)

        # Update signal connections for items after the inserted one
        for i in range(index + 1, len(self._items)):
            self._items[i].expanded.disconnect()
            self._items[i].clicked.disconnect()
            self._items[i].expanded.connect(
                lambda expanded, idx=i: self._on_item_expanded(idx, expanded))
            self._items[i].clicked.connect(
                lambda idx=i: self._on_item_clicked(idx))

        # Add reveal animation for inserted item
        if self._animate_transitions:
            FluentRevealEffect.scale_in(item, FluentAnimation.DURATION_MEDIUM)

    def removeItem(self, index: int):
        """Remove item at index with smooth fade out"""
        if not 0 <= index < len(self._items):
            return

        item = self._items[index]

        if self._animate_transitions:
            # Fade out animation before removal
            fade_out = FluentTransition.create_transition(
                item, FluentTransition.FADE, FluentAnimation.DURATION_FAST)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.finished.connect(
                lambda: self._complete_item_removal(index))
            fade_out.start()
        else:
            self._complete_item_removal(index)

    def _complete_item_removal(self, index: int):
        """Complete item removal after animation"""
        if 0 <= index < len(self._items):
            item = self._items.pop(index)
            item.setParent(None)

            # Update signal connections
            for i in range(index, len(self._items)):
                self._items[i].expanded.disconnect()
                self._items[i].clicked.disconnect()
                self._items[i].expanded.connect(
                    lambda expanded, idx=i: self._on_item_expanded(idx, expanded))
                self._items[i].clicked.connect(
                    lambda idx=i: self._on_item_clicked(idx))

    def item(self, index: int) -> Optional[FluentAccordionItem]:
        """Get item at index"""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def itemCount(self) -> int:
        """Get item count"""
        return len(self._items)

    def setItemExpanded(self, index: int, expanded: bool):
        """Set item expanded state"""
        if 0 <= index < len(self._items):
            self._items[index].setExpanded(expanded, self._animate_transitions)

    def isItemExpanded(self, index: int) -> bool:
        """Check if item is expanded"""
        if 0 <= index < len(self._items):
            return self._items[index].isExpanded()
        return False

    def setAllowMultipleExpanded(self, allow: bool):
        """Set whether multiple items can be expanded simultaneously"""
        self._allow_multiple = allow

    def allowMultipleExpanded(self) -> bool:
        """Check if multiple items can be expanded"""
        return self._allow_multiple

    def setAnimateTransitions(self, animate: bool):
        """Set whether to animate transitions"""
        self._animate_transitions = animate

    def animateTransitions(self) -> bool:
        """Check if transitions are animated"""
        return self._animate_transitions

    def setStaggerDelay(self, delay: int):
        """Set stagger delay for batch animations"""
        self._stagger_delay = max(0, delay)

    def staggerDelay(self) -> int:
        """Get stagger delay"""
        return self._stagger_delay

    def expandAll(self):
        """Expand all items with staggered animation"""
        if self._animate_transitions:
            # Use staggered animation for visual appeal
            for i, item in enumerate(self._items):
                delay = i * self._stagger_delay
                QTimer.singleShot(
                    delay, lambda itm=item: itm.setExpanded(True, True))
        else:
            for item in self._items:
                item.setExpanded(True, False)

    def collapseAll(self):
        """Collapse all items with staggered animation"""
        if self._animate_transitions:
            # Reverse order for collapse animation
            for i, item in enumerate(reversed(self._items)):
                delay = i * self._stagger_delay
                QTimer.singleShot(
                    delay, lambda itm=item: itm.setExpanded(False, True))
        else:
            for item in self._items:
                item.setExpanded(False, False)

    def _on_item_expanded(self, index: int, expanded: bool):
        """Handle item expanded with enhanced animations"""
        if expanded and not self._allow_multiple:
            # Collapse other items with staggered animation
            for i, item in enumerate(self._items):
                if i != index and item.isExpanded():
                    if self._animate_transitions:
                        # Add small delay for smooth visual effect
                        delay = abs(i - index) * 30  # 30ms per item distance
                        QTimer.singleShot(
                            delay, lambda itm=item: itm.setExpanded(False, True))
                    else:
                        item.setExpanded(False, False)

        self.item_expanded.emit(index, expanded)

    def _on_item_clicked(self, index: int):
        """Handle item clicked"""
        self.item_clicked.emit(index)

    def _on_theme_changed(self, theme):
        """Handle theme change"""
        self._setup_style()
