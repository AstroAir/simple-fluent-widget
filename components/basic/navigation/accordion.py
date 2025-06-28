"""
Enhanced Fluent Design Accordion Component
High-performance expandable and collapsible content panels with advanced animations,
theme integration, and responsive design following QFluentWidget patterns.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QLabel, QGraphicsOpacityEffect,
                               QSizePolicy, QScrollArea, QApplication)
from PySide6.QtCore import (Qt, Signal, QPropertyAnimation, QEasingCurve,
                            Property, QByteArray, QParallelAnimationGroup, QTimer,
                            QSize, QAbstractAnimation, QObject, QEvent)
from PySide6.QtGui import (QFont, QPainter, QPen, QColor,
                           QFontMetrics, QTransform)
from core.theme import theme_manager
from typing import Optional, List, Dict, Any, Union, Callable
import math


class AccordionAnimationManager(QObject):
    """Advanced animation manager for accordion operations"""

    def __init__(self, accordion_item: 'FluentAccordionItem'):
        super().__init__(accordion_item)
        self.item = accordion_item
        self._animation_group = QParallelAnimationGroup(self)
        self._is_animating = False
        self._setup_animations()

    def _setup_animations(self):
        """Setup coordinated animations for smooth transitions"""
        # Height animation with spring easing
        self._height_animation = QPropertyAnimation(
            self.item, QByteArray(b"expand_progress"))
        self._height_animation.setDuration(300)
        self._height_animation.setEasingCurve(QEasingCurve.Type.OutBack)

        # Icon rotation with elastic easing
        self._icon_animation = QPropertyAnimation(
            self.item, QByteArray(b"icon_rotation"))
        self._icon_animation.setDuration(250)
        self._icon_animation.setEasingCurve(QEasingCurve.Type.OutElastic)

        # Content opacity animation
        if hasattr(self.item, '_content_opacity_effect'):
            self._opacity_animation = QPropertyAnimation(
                self.item._content_opacity_effect, QByteArray(b"opacity"))
            self._opacity_animation.setDuration(200)
            self._opacity_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
            self._animation_group.addAnimation(self._opacity_animation)

        # Hover animation
        self._hover_animation = QPropertyAnimation(
            self.item, QByteArray(b"hover_progress"))
        self._hover_animation.setDuration(150)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Press animation
        self._press_animation = QPropertyAnimation(
            self.item, QByteArray(b"press_scale"))
        self._press_animation.setDuration(100)
        self._press_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Add animations to group
        self._animation_group.addAnimation(self._height_animation)
        self._animation_group.addAnimation(self._icon_animation)
        self._animation_group.finished.connect(self._on_animation_finished)

    def animate_expand(self, expand: bool) -> None:
        """Animate expand/collapse transition"""
        if self._is_animating:
            return

        self._is_animating = True

        # Setup height animation
        self._height_animation.setStartValue(self.item._expand_progress)
        self._height_animation.setEndValue(1.0 if expand else 0.0)

        # Setup icon rotation
        self._icon_animation.setStartValue(self.item._icon_rotation)
        self._icon_animation.setEndValue(90.0 if expand else 0.0)

        # Setup opacity animation
        if expand:
            self.item._content_container.setVisible(True)
            if hasattr(self, '_opacity_animation'):
                self._opacity_animation.setStartValue(0.0)
                self._opacity_animation.setEndValue(1.0)
        else:
            if hasattr(self, '_opacity_animation'):
                self._opacity_animation.setStartValue(1.0)
                self._opacity_animation.setEndValue(0.0)

        # Start coordinated animation
        self._animation_group.start()

    def animate_hover(self, hovered: bool) -> None:
        """Animate hover state transition"""
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self.item._hover_progress)
        self._hover_animation.setEndValue(1.0 if hovered else 0.0)
        self._hover_animation.start()

    def animate_press(self, pressed: bool) -> None:
        """Animate press feedback"""
        self._press_animation.stop()
        self._press_animation.setStartValue(self.item._press_scale)
        self._press_animation.setEndValue(0.96 if pressed else 1.0)
        self._press_animation.start()

    def _on_animation_finished(self):
        """Handle animation completion"""
        self._is_animating = False
        if not self.item._is_expanded:
            self.item._content_container.setVisible(False)

    def pause_animations(self):
        """Pause all running animations"""
        if self._animation_group.state() == QAbstractAnimation.State.Running:
            self._animation_group.pause()

    def resume_animations(self):
        """Resume paused animations"""
        if self._animation_group.state() == QAbstractAnimation.State.Paused:
            self._animation_group.resume()

    def cleanup(self):
        """Clean up animations and resources"""
        if self._animation_group.state() == QAbstractAnimation.State.Running:
            self._animation_group.stop()
        self._animation_group.deleteLater()


class ContentLoader(QObject):
    """Dynamic content loader for lazy loading and content management"""

    content_loaded = Signal(QWidget)
    loading_finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._loaded_content: Dict[str, QWidget] = {}
        self._loading_callbacks: Dict[str, Callable] = {}

    def register_content(self, key: str, loader_func: Callable[[], QWidget]):
        """Register a content loader function"""
        self._loading_callbacks[key] = loader_func

    def load_content(self, key: str) -> Optional[QWidget]:
        """Load content dynamically"""
        if key in self._loaded_content:
            return self._loaded_content[key]

        if key in self._loading_callbacks:
            try:
                content = self._loading_callbacks[key]()
                self._loaded_content[key] = content
                self.content_loaded.emit(content)
                return content
            except Exception as e:
                print(f"Error loading content for key '{key}': {e}")

        return None

    def unload_content(self, key: str):
        """Unload content to free memory"""
        if key in self._loaded_content:
            widget = self._loaded_content.pop(key)
            if widget:
                widget.deleteLater()


class ThemeManager(QObject):
    """Enhanced theme manager for consistent styling"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cached_styles: Dict[str, str] = {}
        self._cached_colors: Dict[str, QColor] = {}
        theme_manager.theme_changed.connect(self._clear_cache)

    def get_cached_color(self, color_key: str) -> QColor:
        """Get cached color with fallback"""
        if color_key not in self._cached_colors:
            try:
                self._cached_colors[color_key] = theme_manager.get_color(
                    color_key)
            except:
                # Fallback to default colors if theme manager fails
                defaults = {
                    "primaryColor": QColor(0, 120, 215),
                    "backgroundColor": QColor(255, 255, 255),
                    "textColor": QColor(0, 0, 0),
                    "borderColor": QColor(200, 200, 200)
                }
                self._cached_colors[color_key] = defaults.get(
                    color_key, QColor(128, 128, 128))
        return self._cached_colors[color_key]

    def get_interpolated_color(self, start_color: str, end_color: str, progress: float) -> QColor:
        """Get interpolated color between two theme colors"""
        start = self.get_cached_color(start_color)
        end = self.get_cached_color(end_color)

        r = int(start.red() + (end.red() - start.red()) * progress)
        g = int(start.green() + (end.green() - start.green()) * progress)
        b = int(start.blue() + (end.blue() - start.blue()) * progress)
        a = int(start.alpha() + (end.alpha() - start.alpha()) * progress)

        return QColor(r, g, b, a)

    def get_style_for_state(self, base_style: str, state: str) -> str:
        """Get cached style for specific state"""
        cache_key = f"{base_style}_{state}"
        if cache_key not in self._cached_styles:
            # Generate style based on state
            self._cached_styles[cache_key] = self._generate_state_style(
                base_style, state)
        return self._cached_styles[cache_key]

    def _generate_state_style(self, base_style: str, state: str) -> str:
        """Generate CSS style for specific state"""
        primary = self.get_cached_color("primaryColor")
        background = self.get_cached_color("backgroundColor")
        text = self.get_cached_color("textColor")
        border = self.get_cached_color("borderColor")

        if base_style == "accordion_header":
            if state == "hover":
                hover_color = self.get_interpolated_color(
                    "backgroundColor", "primaryColor", 0.1)
                return f"""
                QFrame {{
                    background-color: {hover_color.name()};
                    border: 1px solid {primary.name()};
                    border-radius: 8px;
                }}
                """
            else:  # normal state
                return f"""
                QFrame {{
                    background-color: {background.name()};
                    border: 1px solid {border.name()};
                    border-radius: 8px;
                }}
                QFrame:hover {{
                    border-color: {primary.name()};
                }}
                """
        elif base_style == "accordion_content":
            return f"""
            QFrame {{
                background-color: {background.name()};
                border: none;
                padding: 16px;
            }}
            """

        return ""

    def _clear_cache(self):
        """Clear cached styles and colors when theme changes"""
        self._cached_styles.clear()
        self._cached_colors.clear()


class FluentAccordionItem(QFrame):
    """Enhanced accordion item with advanced animations and theme integration"""

    # Signals
    expanded = Signal(bool)
    clicked = Signal()
    content_changed = Signal()

    # Property change signals for animations
    expand_progress_changed = Signal()
    hover_progress_changed = Signal()
    icon_rotation_changed = Signal()
    press_scale_changed = Signal()

    def __init__(self, title: str = "", content_widget: Optional[QWidget] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._is_expanded = False
        self._content_height = 0
        self._header_height = 56  # Increased for better touch targets
        self._expand_progress = 0.0
        self._hover_progress = 0.0
        self._icon_rotation = 0.0
        self._press_scale = 1.0

        # Performance and memory management
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._perform_deferred_update)
        self._pending_updates = set()

        # Content management
        self._content_loader = ContentLoader(self)
        self._theme_manager = ThemeManager(self)

        # Animation management
        self._animation_manager = None

        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        if content_widget:
            self.setContentWidget(content_widget)

        # Connect theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup enhanced UI with better layout and accessibility"""
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Maximum)

        # Main layout with better spacing
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Enhanced header with better visual hierarchy
        self._header = QFrame()
        self._header.setFixedHeight(self._header_height)
        self._header.setCursor(Qt.CursorShape.PointingHandCursor)
        self._header.setFocusPolicy(Qt.FocusPolicy.TabFocus)  # Accessibility
        self._header.mousePressEvent = self._on_header_pressed
        self._header.mouseReleaseEvent = self._on_header_released
        self._header.enterEvent = self._on_header_enter
        self._header.leaveEvent = self._on_header_leave
        self._header.keyPressEvent = self._on_key_pressed

        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(20, 12, 20, 12)  # Better padding
        header_layout.setSpacing(16)

        # Enhanced expand/collapse icon with better visual feedback
        self._icon_label = QLabel()
        # Slightly larger for better visibility
        self._icon_label.setFixedSize(20, 20)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_icon()

        # Enhanced title label with better typography
        self._title_label = QLabel(self._title)
        title_font = QFont()
        title_font.setPointSize(15)  # Slightly larger
        title_font.setWeight(QFont.Weight.Medium)
        self._title_label.setFont(title_font)
        self._title_label.setWordWrap(True)  # Support for longer titles

        header_layout.addWidget(self._icon_label)
        header_layout.addWidget(self._title_label, 1)  # Expand to fill

        # Enhanced content container with optimized rendering
        self._content_container = QFrame()
        self._content_container.setFixedHeight(0)
        self._content_container.setVisible(False)
        self._content_container.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        # Enhanced opacity effect with better performance
        self._content_opacity_effect = QGraphicsOpacityEffect()
        self._content_opacity_effect.setOpacity(0.0)
        self._content_container.setGraphicsEffect(self._content_opacity_effect)

        # Content layout
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(20, 16, 20, 16)
        self._content_layout.setSpacing(12)

        # Add widgets to main layout
        self._layout.addWidget(self._header)
        self._layout.addWidget(self._content_container)

    def _setup_style(self):
        """Setup enhanced styling with theme integration"""
        self._update_styles()

    def _setup_animations(self):
        """Setup animation manager"""
        self._animation_manager = AccordionAnimationManager(self)

    def _update_styles(self):
        """Update styles based on current theme and state"""
        header_style = self._theme_manager.get_style_for_state(
            "accordion_header", "normal")
        content_style = self._theme_manager.get_style_for_state(
            "accordion_content", "normal")

        self._header.setStyleSheet(header_style)
        self._content_container.setStyleSheet(content_style)

        text_color = self._theme_manager.get_cached_color("textColor")
        self._title_label.setStyleSheet(f"color: {text_color.name()};")

    def _update_icon(self):
        """Update icon based on rotation state"""
        # Create a simple arrow icon using Unicode
        icon_char = "▶"  # Right-pointing triangle

        # Apply rotation transform
        transform = QTransform()
        transform.rotate(self._icon_rotation)

        # Create rotated text
        self._icon_label.setText(icon_char)

        # Update icon color based on theme
        icon_color = self._theme_manager.get_cached_color("textColor")
        self._icon_label.setStyleSheet(f"""
        QLabel {{
            color: {icon_color.name()};
            font-size: 12px;
            font-weight: bold;
        }}
        """)

    # Property getters and setters
    def _get_expand_progress(self) -> float:
        return self._expand_progress

    def _set_expand_progress(self, value: float):
        if self._expand_progress != value:
            self._expand_progress = value
            self._schedule_update("expand_progress")
            self.expand_progress_changed.emit()

    def _get_hover_progress(self) -> float:
        return self._hover_progress

    def _set_hover_progress(self, value: float):
        if self._hover_progress != value:
            self._hover_progress = value
            self._schedule_update("hover_progress")
            self.hover_progress_changed.emit()

    def _get_icon_rotation(self) -> float:
        return self._icon_rotation

    def _set_icon_rotation(self, value: float):
        if self._icon_rotation != value:
            self._icon_rotation = value
            self._schedule_update("icon_rotation")
            self.icon_rotation_changed.emit()

    def _get_press_scale(self) -> float:
        return self._press_scale

    def _set_press_scale(self, value: float):
        if self._press_scale != value:
            self._press_scale = value
            self._schedule_update("press_scale")
            self.press_scale_changed.emit()    # Qt Properties for animations
    expand_progress = Property(
        float, _get_expand_progress, _set_expand_progress, "", "")
    hover_progress = Property(
        float, _get_hover_progress, _set_hover_progress, "", "")
    icon_rotation = Property(float, _get_icon_rotation,
                             _set_icon_rotation, "", "")
    press_scale = Property(float, _get_press_scale, _set_press_scale, "", "")

    def _schedule_update(self, update_type: str):
        """Schedule deferred updates for better performance"""
        self._pending_updates.add(update_type)
        if not self._update_timer.isActive():
            self._update_timer.start(16)  # ~60 FPS

    def _perform_deferred_update(self):
        """Perform scheduled updates in batch"""
        updates = self._pending_updates.copy()
        self._pending_updates.clear()

        for update_type in updates:
            if update_type == "expand_progress":
                self._update_content_height()
            elif update_type == "hover_progress":
                self._update_hover_effects()
            elif update_type == "icon_rotation":
                self._update_icon()
            elif update_type == "press_scale":
                self._update_press_effects()

    def _update_content_height(self):
        """Update content container height based on progress"""
        target_height = max(
            0, int(self._content_height * self._expand_progress))
        self._content_container.setFixedHeight(target_height)

    def _update_hover_effects(self):
        """Update visual hover effects"""
        if self._hover_progress > 0:
            hover_style = self._theme_manager.get_style_for_state(
                "accordion_header", "hover")
            self._header.setStyleSheet(hover_style)
        else:
            normal_style = self._theme_manager.get_style_for_state(
                "accordion_header", "normal")
            self._header.setStyleSheet(normal_style)

    def _update_press_effects(self):
        """Update press visual feedback"""
        # Since QWidget stylesheets don't support transform, we'll use subtle color changes instead
        scale_factor = self._press_scale
        base_style = self._theme_manager.get_style_for_state(
            "accordion_header", "normal")

        if scale_factor < 1.0:
            # Apply pressed state with darker background
            primary = self._theme_manager.get_cached_color("primaryColor")
            pressed_color = primary.darker(120)
            press_style = f"""
            QFrame {{
                background-color: {pressed_color.name()};
                border: 1px solid {primary.name()};
                border-radius: 8px;
            }}
            """
            self._header.setStyleSheet(press_style)
        else:
            self._header.setStyleSheet(base_style)

    # Event handlers
    def _on_header_pressed(self, event):
        """Handle mouse press with animation feedback"""
        if self._animation_manager:
            self._animation_manager.animate_press(True)

    def _on_header_released(self, event):
        """Handle mouse release and toggle state"""
        if self._animation_manager:
            self._animation_manager.animate_press(False)
            QTimer.singleShot(100, self.toggle)

    def _on_header_enter(self, event):
        """Handle mouse enter with smooth transition"""
        if self._animation_manager:
            self._animation_manager.animate_hover(True)

    def _on_header_leave(self, event):
        """Handle mouse leave with smooth transition"""
        if self._animation_manager:
            self._animation_manager.animate_hover(False)

    def _on_key_pressed(self, event):
        """Handle keyboard interaction for accessibility"""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Space):
            self.toggle()
            event.accept()
        else:
            event.ignore()

    def _on_theme_changed(self, theme):
        """Handle theme change with smooth transition"""
        self._update_styles()

    def _set_compact_mode(self, compact: bool):
        """Set compact mode for responsive design"""
        if compact:
            self._header_height = 48
            self._header.setFixedHeight(self._header_height)
            # Reduce padding and font size for compact mode
            header_layout = self._header.layout()
            if header_layout:
                header_layout.setContentsMargins(16, 8, 16, 8)

            font = self._title_label.font()
            font.setPointSize(13)
            self._title_label.setFont(font)
        else:
            self._header_height = 56
            self._header.setFixedHeight(self._header_height)
            # Restore normal padding and font size
            header_layout = self._header.layout()
            if header_layout:
                header_layout.setContentsMargins(20, 12, 20, 12)

            font = self._title_label.font()
            font.setPointSize(15)
            self._title_label.setFont(font)

    # Public API
    def setTitle(self, title: str):
        """Set the accordion item title"""
        self._title = title
        self._title_label.setText(title)

    def getTitle(self) -> str:
        """Get the accordion item title"""
        return self._title

    def setContentWidget(self, widget: QWidget):
        """Set the content widget"""
        # Clear existing content
        while self._content_layout.count():
            child = self._content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add new content
        if widget:
            self._content_layout.addWidget(widget)

            # Calculate content height with safety check
            widget.adjustSize()
            self._content_height = max(
                0, widget.sizeHint().height() + 32)  # padding

            # Emit content changed signal
            self.content_changed.emit()

    def getContentWidget(self) -> Optional[QWidget]:
        """Get the content widget"""
        if self._content_layout.count() > 0:
            return self._content_layout.itemAt(0).widget()
        return None

    def toggle(self):
        """Toggle the expanded state"""
        self.setExpanded(not self._is_expanded)

    def setExpanded(self, expanded: bool):
        """Set the expanded state with animation"""
        if self._is_expanded == expanded:
            return

        self._is_expanded = expanded

        if self._animation_manager:
            self._animation_manager.animate_expand(expanded)

        self.expanded.emit(expanded)
        self.clicked.emit()

    def isExpanded(self) -> bool:
        """Check if the accordion is expanded"""
        return self._is_expanded

    def sizeHint(self):
        """Provide optimized size hint"""
        base_height = self._header_height
        if self._is_expanded and self._content_height > 0:
            base_height += self._content_height
        return QSize(400, base_height)  # Default width suggestion

    def minimumSizeHint(self):
        """Provide minimum size hint"""
        return QSize(200, self._header_height)

    def cleanup(self):
        """Clean up resources when widget is destroyed"""
        if self._animation_manager:
            self._animation_manager.cleanup()

        if self._update_timer.isActive():
            self._update_timer.stop()

        # Clean up content loader
        self._content_loader.deleteLater()


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

    def _setup_ui(self):
        """Setup UI layout"""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)  # Small gap between items

    def _setup_style(self):
        """Setup styling"""
        self.setStyleSheet("""
        FluentAccordion {
            background-color: transparent;
        }
        """)

    def addItem(self, title: str, content_widget: Optional[QWidget] = None) -> FluentAccordionItem:
        """Add a new accordion item"""
        item = FluentAccordionItem(title, content_widget, self)

        # Connect signals
        item.expanded.connect(lambda expanded, idx=len(
            self._items): self._on_item_expanded(idx, expanded))
        item.clicked.connect(lambda idx=len(self._items)
                             : self._on_item_clicked(idx))

        self._items.append(item)
        self._layout.addWidget(item)

        return item

    def insertItem(self, index: int, title: str, content_widget: Optional[QWidget] = None) -> FluentAccordionItem:
        """Insert an accordion item at the specified index"""
        if index < 0 or index > len(self._items):
            return self.addItem(title, content_widget)

        item = FluentAccordionItem(title, content_widget, self)

        # Connect signals
        item.expanded.connect(
            lambda expanded, idx=index: self._on_item_expanded(idx, expanded))
        item.clicked.connect(lambda idx=index: self._on_item_clicked(idx))

        self._items.insert(index, item)
        self._layout.insertWidget(index, item)

        # Update signal connections for items after the inserted one
        self._update_signal_connections()

        return item

    def removeItem(self, index: int) -> bool:
        """Remove an accordion item by index"""
        if 0 <= index < len(self._items):
            item = self._items.pop(index)
            self._layout.removeWidget(item)
            item.cleanup()
            item.deleteLater()

            # Update signal connections
            self._update_signal_connections()
            return True
        return False

    def _update_signal_connections(self):
        """Update signal connections after item insertion/removal"""
        for i, item in enumerate(self._items):
            # Disconnect old connections
            item.expanded.disconnect()
            item.clicked.disconnect()

            # Reconnect with correct index
            item.expanded.connect(
                lambda expanded, idx=i: self._on_item_expanded(idx, expanded))
            item.clicked.connect(lambda idx=i: self._on_item_clicked(idx))

    def getItem(self, index: int) -> Optional[FluentAccordionItem]:
        """Get accordion item by index"""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def setAllowMultiple(self, allow: bool):
        """Set whether multiple items can be expanded simultaneously"""
        self._allow_multiple = allow

    def getAllowMultiple(self) -> bool:
        """Check if multiple items can be expanded simultaneously"""
        return self._allow_multiple

    def setStaggerDelay(self, delay: int):
        """Set the stagger delay for expand/collapse all animations"""
        self._stagger_delay = delay

    def getItemCount(self) -> int:
        """Get the number of accordion items"""
        return len(self._items)

    def expandAll(self):
        """Expand all accordion items"""
        if self._animate_transitions:
            self._staggered_expand_all(True)
        else:
            for item in self._items:
                item.setExpanded(True)

    def collapseAll(self):
        """Collapse all accordion items"""
        if self._animate_transitions:
            self._staggered_expand_all(False)
        else:
            for item in self._items:
                item.setExpanded(False)

    def _staggered_expand_all(self, expand: bool):
        """Perform staggered animation for expand/collapse all"""
        for i, item in enumerate(self._items):
            # Use QTimer to create staggered effect
            QTimer.singleShot(i * self._stagger_delay,
                              lambda item=item, exp=expand: item.setExpanded(exp))

    def _on_item_expanded(self, index: int, expanded: bool):
        """Handle item expansion"""
        if expanded and not self._allow_multiple:
            # Collapse other items if multiple expansion is not allowed
            for i, item in enumerate(self._items):
                if i != index and item.isExpanded():
                    item.setExpanded(False)

        self.item_expanded.emit(index, expanded)

    def _on_item_clicked(self, index: int):
        """Handle item click"""
        self.item_clicked.emit(index)

    def resizeEvent(self, event):
        """Handle resize with responsive adjustments"""
        super().resizeEvent(event)
        self._update_responsive_layout()

    def _update_responsive_layout(self):
        """Update layout based on current size with optimized performance"""
        try:
            current_width = self.width()

            # Responsive breakpoints for better UX
            for item in self._items:
                if hasattr(item, '_set_compact_mode'):
                    if current_width < 300:
                        item._set_compact_mode(True)
                    elif current_width < 600:
                        item._set_compact_mode(False)
                    else:
                        item._set_compact_mode(False)

        except Exception as e:
            print(f"Error in responsive layout update: {e}")

    def getAnimateTransitions(self) -> bool:
        """Check if animated transitions are enabled"""
        return self._animate_transitions

    def setAnimateTransitions(self, animate: bool):
        """Enable or disable animated transitions"""
        self._animate_transitions = animate

    def pauseAnimations(self):
        """Pause all item animations (useful for performance)"""
        for item in self._items:
            if hasattr(item, '_animation_manager') and item._animation_manager:
                item._animation_manager.pause_animations()

    def resumeAnimations(self):
        """Resume all item animations"""
        for item in self._items:
            if hasattr(item, '_animation_manager') and item._animation_manager:
                item._animation_manager.resume_animations()

    def cleanup(self):
        """Clean up all resources"""
        for item in self._items:
            item.cleanup()
        self._items.clear()
