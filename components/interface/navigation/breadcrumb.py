"""
Fluent Design Breadcrumb Component
Navigation breadcrumb with separators and interactive items
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton,
                               QSizePolicy, QMenu)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QTimer
from PySide6.QtGui import QFont, QAction
from core.theme import theme_manager
from core.enhanced_animations import (FluentMicroInteraction, FluentTransition, 
                                    FluentSequence, FluentParallel)
from core.animation import FluentAnimation  # Keep backward compatibility
from typing import Optional, List, Dict, Any
from enum import Enum


class FluentBreadcrumbItem(QPushButton):
    """Individual breadcrumb item with enhanced animations"""
    def __init__(self, text: str = "", data: Any = None, parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self._data = data
        self._is_current = False
        self._hover_animation = None
        self._press_animation = None
        self._fade_animation = None

        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        # Setup hover and press animations
        self.enterEvent = self._on_enter
        self.leaveEvent = self._on_leave
        self.pressed.connect(self._on_pressed)

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set font
        font = QFont()
        font.setPointSize(13)
        self.setFont(font)

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Minimum,
                           QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(32)

    def _setup_animations(self):
        """Setup enhanced animations"""
        # Create fade transition for smooth appearance
        self._fade_animation = FluentTransition.create_transition(
            self, FluentTransition.FADE, 
            FluentAnimation.DURATION_FAST,
            FluentTransition.EASE_SMOOTH
        )
        
        # Initialize with full opacity
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        if self._is_current:
            text_color = theme.get_color('text_primary')
            bg_color = "transparent"
        else:
            text_color = theme.get_color('text_secondary')
            bg_color = "transparent"

        style_sheet = f"""
            QPushButton {{
                background-color: {bg_color};
                border: none;
                color: {text_color.name()};
                padding: 6px 8px;
                border-radius: 4px;
                text-align: left;
                transition: all 0.2s ease;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
        """

        if self._is_current:
            style_sheet += """
                QPushButton:hover {
                    background-color: transparent;
                }
                QPushButton:pressed {
                    background-color: transparent;
                }
            """
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet(style_sheet)

    def _on_enter(self, event):
        """Handle hover enter event with enhanced animations"""
        if not self._is_current:
            # Stop any existing hover animation
            if self._hover_animation:
                self._hover_animation.stop()
            
            # Create enhanced hover effect with multiple animations
            hover_sequence = FluentSequence(self)
            
            # Scale animation
            scale_anim = FluentTransition.create_transition(
                self, FluentTransition.SCALE,
                FluentAnimation.DURATION_ULTRA_FAST,
                FluentTransition.EASE_SPRING
            )
            scale_anim.setStartValue(self.geometry())
            
            # Calculate scaled geometry
            original_rect = self.geometry()
            scale_factor = 1.03
            new_width = int(original_rect.width() * scale_factor)
            new_height = int(original_rect.height() * scale_factor)
            new_x = original_rect.x() - (new_width - original_rect.width()) // 2
            new_y = original_rect.y() - (new_height - original_rect.height()) // 2
            
            from PySide6.QtCore import QRect
            scaled_rect = QRect(new_x, new_y, new_width, new_height)
            scale_anim.setEndValue(scaled_rect)
            
            hover_sequence.addAnimation(scale_anim)
            
            # Add subtle glow effect
            glow_anim = FluentMicroInteraction.hover_glow(self, intensity=0.1)
            hover_sequence.addAnimation(glow_anim)
            
            self._hover_animation = hover_sequence
            hover_sequence.start()

    def _on_leave(self, event):
        """Handle hover leave event with enhanced animations"""
        if not self._is_current:
            # Stop any existing hover animation
            if self._hover_animation:
                self._hover_animation.stop()
            
            # Create smooth return animation
            return_anim = FluentTransition.create_transition(
                self, FluentTransition.SCALE,
                FluentAnimation.DURATION_FAST,
                FluentTransition.EASE_SMOOTH
            )
            
            # Get current and original geometry
            current_rect = self.geometry()
            # Calculate original size (assuming 1.03 scale factor)
            original_width = int(current_rect.width() / 1.03)
            original_height = int(current_rect.height() / 1.03)
            original_x = current_rect.x() + (current_rect.width() - original_width) // 2
            original_y = current_rect.y() + (current_rect.height() - original_height) // 2
            
            from PySide6.QtCore import QRect
            original_rect = QRect(original_x, original_y, original_width, original_height)
            
            return_anim.setStartValue(current_rect)
            return_anim.setEndValue(original_rect)
            
            self._hover_animation = return_anim
            return_anim.start()

    def _on_pressed(self):
        """Handle button press with enhanced micro-interaction"""
        if not self._is_current:
            # Stop any existing animations
            if self._press_animation:
                self._press_animation.stop()
            
            # Create enhanced press sequence
            press_sequence = FluentSequence(self)
            
            # Quick press animation with elastic easing
            # Create press animation and add its child animations individually
            press_anim_group = FluentMicroInteraction.button_press(self, scale=0.96)
            for i in range(press_anim_group.animationCount()):
                anim = press_anim_group.animationAt(i)
                # Only add property animations to the sequence
                if isinstance(anim, QPropertyAnimation):
                    press_sequence.addAnimation(anim)
            
            # Add subtle pulse effect for feedback
            pulse_anim = FluentMicroInteraction.pulse_animation(self, scale=1.02)
            press_sequence.addCallback(lambda: pulse_anim.start())
            
            self._press_animation = press_sequence
            press_sequence.start()

    def setData(self, data: Any):
        """Set item data"""
        self._data = data

    def data(self) -> Any:
        """Get item data"""
        return self._data

    def setCurrent(self, current: bool):
        """Set whether this is the current item with smooth transition"""
        if self._is_current != current:
            self._is_current = current
            
            # Animate the state change
            transition_sequence = FluentSequence(self)
            
            # Fade out current style
            fade_out = FluentTransition.create_transition(
                self, FluentTransition.FADE,
                FluentAnimation.DURATION_FAST // 2,
                FluentTransition.EASE_SMOOTH
            )
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.7)
            transition_sequence.addAnimation(fade_out)
            
            # Update style and fade back in
            transition_sequence.addCallback(self._setup_style)
            
            fade_in = FluentTransition.create_transition(
                self, FluentTransition.FADE,
                FluentAnimation.DURATION_FAST // 2,
                FluentTransition.EASE_SMOOTH
            )
            fade_in.setStartValue(0.7)
            fade_in.setEndValue(1.0)
            transition_sequence.addAnimation(fade_in)
            
            transition_sequence.start()
        else:
            self._setup_style()

    def isCurrent(self) -> bool:
        """Check if this is the current item"""
        return self._is_current

    def showWithAnimation(self):
        """Show item with entrance animation"""
        if self._fade_animation:
            self._fade_animation.start()

    def _on_theme_changed(self, _):
        """Handle theme change with smooth transition"""
        # Create smooth theme transition
        theme_transition = FluentTransition.create_transition(
            self, FluentTransition.FADE,
            FluentAnimation.DURATION_MEDIUM,
            FluentTransition.EASE_SMOOTH
        )
        
        theme_transition.setStartValue(1.0)
        theme_transition.setEndValue(0.8)
        
        # Update style after fade
        theme_transition.finished.connect(
            lambda: [
                self._setup_style(),
                FluentTransition.create_transition(
                    self, FluentTransition.FADE,
                    FluentAnimation.DURATION_MEDIUM,
                    FluentTransition.EASE_SMOOTH
                ).start() if (
                    lambda fade_in: [
                        fade_in.setStartValue(0.8),
                        fade_in.setEndValue(1.0)
                    ]
                )(FluentTransition.create_transition(
                    self, FluentTransition.FADE,
                    FluentAnimation.DURATION_MEDIUM,
                    FluentTransition.EASE_SMOOTH
                )) else None
            ]
        )
        
        theme_transition.start()


class FluentBreadcrumbSeparator(QLabel):
    """Breadcrumb separator with smooth animations"""

    def __init__(self, separator: str = ">", parent: Optional[QWidget] = None):
        super().__init__(separator, parent)

        self._fade_animation = None
        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedWidth(20)

        font = QFont()
        font.setPointSize(12)
        self.setFont(font)

    def _setup_animations(self):
        """Setup smooth entrance animation"""
        self._fade_animation = FluentTransition.create_transition(
            self, FluentTransition.FADE,
            FluentAnimation.DURATION_MEDIUM,
            FluentTransition.EASE_SMOOTH
        )
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QLabel {{
                color: {theme.get_color('text_tertiary').name()};
                background-color: transparent;
                border: none;
                transition: color 0.3s ease;
            }}
        """

        self.setStyleSheet(style_sheet)

    def showWithAnimation(self):
        """Show separator with smooth animation"""
        if self._fade_animation:
            self._fade_animation.start()

    def _on_theme_changed(self, _):
        """Handle theme change with smooth transition"""
        # Smooth color transition
        color_transition = FluentTransition.create_transition(
            self, FluentTransition.FADE,
            FluentAnimation.DURATION_MEDIUM,
            FluentTransition.EASE_SMOOTH
        )
        
        color_transition.finished.connect(self._setup_style)
        color_transition.start()


class FluentBreadcrumb(QWidget):
    """Fluent Design breadcrumb navigation with enhanced animations"""

    class OverflowMode(Enum):
        ELLIPSIS = "ellipsis"
        DROPDOWN = "dropdown"
        SCROLL = "scroll"

    # Signals
    item_clicked = Signal(int, object)  # index, data

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items: List[Dict[str, Any]] = []
        self._max_items = 5
        self._overflow_mode = self.OverflowMode.ELLIPSIS
        self._separator = ">"
        self._show_home = True
        self._home_text = "主页"
        self._home_data = None
        self._update_animation = None
        self._entrance_animations = []

        self._setup_ui()
        self._setup_style()
        self._setup_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 4, 8, 4)
        self._layout.setSpacing(0)

        # Add stretch at the end
        self._layout.addStretch()

        self._update_breadcrumb()

    def _setup_animations(self):
        """Setup container animations"""
        # Container fade animation for smooth updates
        self._container_fade = FluentTransition.create_transition(
            self, FluentTransition.FADE,
            FluentAnimation.DURATION_MEDIUM,
            FluentTransition.EASE_SMOOTH
        )

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentBreadcrumb {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
                transition: all 0.3s ease;
            }}
        """

        self.setStyleSheet(style_sheet)

    def addItem(self, text: str, data: Any = None):
        """Add breadcrumb item with smooth animation"""
        self._items.append({"text": text, "data": data})
        self._update_breadcrumb_animated()

    def insertItem(self, index: int, text: str, data: Any = None):
        """Insert item at index with animation"""
        if 0 <= index <= len(self._items):
            self._items.insert(index, {"text": text, "data": data})
            self._update_breadcrumb_animated()

    def removeItem(self, index: int):
        """Remove item at index with fade-out animation"""
        if 0 <= index < len(self._items):
            self._items.pop(index)
            self._update_breadcrumb_animated()

    def setItems(self, items: List[Dict[str, Any]]):
        """Set all items with smooth transition

        Args:
            items: List of dicts with 'text' and optionally 'data' keys
        """
        self._items = items.copy()
        self._update_breadcrumb_animated()

    def items(self) -> List[Dict[str, Any]]:
        """Get all items"""
        return self._items.copy()

    def clear(self):
        """Clear all items with fade-out animation"""
        if self._items:
            # Animate clearing
            clear_sequence = FluentSequence(self)
            
            # Fade out current items
            fade_out = FluentTransition.create_transition(
                self, FluentTransition.FADE,
                FluentAnimation.DURATION_FAST,
                FluentTransition.EASE_SMOOTH
            )
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.3)
            clear_sequence.addAnimation(fade_out)
            
            # Clear and update
            clear_sequence.addCallback(lambda: [
                self._items.clear(),
                self._update_breadcrumb()
            ])
            
            # Fade back in
            fade_in = FluentTransition.create_transition(
                self, FluentTransition.FADE,
                FluentAnimation.DURATION_FAST,
                FluentTransition.EASE_SMOOTH
            )
            fade_in.setStartValue(0.3)
            fade_in.setEndValue(1.0)
            clear_sequence.addAnimation(fade_in)
            
            clear_sequence.start()
        else:
            self._update_breadcrumb()

    def setMaxItems(self, max_items: int):
        """Set maximum visible items"""
        self._max_items = max(1, max_items)
        self._update_breadcrumb_animated()

    def maxItems(self) -> int:
        """Get maximum visible items"""
        return self._max_items

    def setOverflowMode(self, mode: OverflowMode):
        """Set overflow handling mode with smooth transition"""
        if self._overflow_mode != mode:
            self._overflow_mode = mode
            self._update_breadcrumb_animated()

    def overflowMode(self) -> OverflowMode:
        """Get overflow handling mode"""
        return self._overflow_mode

    def setSeparator(self, separator: str):
        """Set separator text"""
        self._separator = separator
        self._update_breadcrumb_animated()

    def separator(self) -> str:
        """Get separator text"""
        return self._separator

    def setShowHome(self, show: bool):
        """Set whether to show home item"""
        self._show_home = show
        self._update_breadcrumb_animated()

    def showHome(self) -> bool:
        """Check if home item is shown"""
        return self._show_home

    def setHomeText(self, text: str):
        """Set home item text"""
        self._home_text = text
        self._update_breadcrumb_animated()

    def homeText(self) -> str:
        """Get home item text"""
        return self._home_text

    def setHomeData(self, data: Any):
        """Set home item data"""
        self._home_data = data

    def homeData(self) -> Any:
        """Get home item data"""
        return self._home_data

    def _update_breadcrumb_animated(self):
        """Update breadcrumb with smooth animation"""
        if self._update_animation:
            self._update_animation.stop()
        
        # Create update sequence
        update_sequence = FluentSequence(self)
        
        # Fade out current content
        fade_out = FluentTransition.create_transition(
            self, FluentTransition.FADE,
            FluentAnimation.DURATION_FAST,
            FluentTransition.EASE_SMOOTH
        )
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.7)
        update_sequence.addAnimation(fade_out)
        
        # Update content
        update_sequence.addCallback(self._update_breadcrumb)
        
        # Fade in new content
        fade_in = FluentTransition.create_transition(
            self, FluentTransition.FADE,
            FluentAnimation.DURATION_FAST,
            FluentTransition.EASE_SMOOTH
        )
        fade_in.setStartValue(0.7)
        fade_in.setEndValue(1.0)
        update_sequence.addAnimation(fade_in)
        
        self._update_animation = update_sequence
        update_sequence.start()

    def _update_breadcrumb(self):
        """Update breadcrumb display"""
        # Clear existing widgets
        for i in reversed(range(self._layout.count())):
            item = self._layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget and not widget.objectName() == "stretch":
                    widget.setParent(None)

        # Remove stretch
        if self._layout.count() > 0:
            self._layout.removeItem(
                self._layout.itemAt(self._layout.count() - 1))

        all_items = []

        # Add home item if enabled
        if self._show_home:
            all_items.append(
                {"text": self._home_text, "data": self._home_data, "is_home": True})

        # Add regular items
        all_items.extend([{**item, "is_home": False} for item in self._items])

        if not all_items:
            self._layout.addStretch()
            return

        # Handle overflow
        visible_items = self._get_visible_items(all_items)

        # Clear previous entrance animations
        self._entrance_animations.clear()

        # Create widgets with staggered entrance animations
        entrance_sequence = FluentSequence(self)
        
        for i, item_data in enumerate(visible_items):
            # Add separator (except for first item)
            if i > 0:
                separator = FluentBreadcrumbSeparator(self._separator, self)
                self._layout.addWidget(separator)
                
                # Add delayed entrance animation for separator
                QTimer.singleShot(
                    i * 50,  # Stagger delay
                    separator.showWithAnimation
                )

            # Create item
            if item_data.get("is_ellipsis", False):
                # Ellipsis item with dropdown
                ellipsis_item = self._create_ellipsis_item(
                    item_data["hidden_items"])
                self._layout.addWidget(ellipsis_item)
                
                # Add entrance animation
                QTimer.singleShot(
                    i * 50 + 25,  # Slight offset from separator
                    ellipsis_item.showWithAnimation
                )
            else:
                # Regular item
                item = FluentBreadcrumbItem(
                    item_data["text"], item_data["data"], self)

                # Set current state (last item is current)
                is_current = (i == len(visible_items) - 1)
                item.setCurrent(is_current)

                # Connect click signal
                if not is_current:
                    original_index = item_data.get("original_index", -1)
                    item.clicked.connect(
                        lambda _checked=False, idx=original_index, current_item_data=item_data["data"]:
                        self._on_item_clicked(idx, current_item_data)
                    )

                self._layout.addWidget(item)
                
                # Add staggered entrance animation
                QTimer.singleShot(
                    i * 50 + 25,  # Slight offset from separator
                    item.showWithAnimation
                )

        # Add stretch at the end
        self._layout.addStretch()

    def _get_visible_items(self, all_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get visible items based on overflow mode"""
        # Ensure all items have an original_index before slicing or processing
        for idx, item_content in enumerate(all_items):
            if "original_index" not in item_content:
                if item_content.get("is_home"):
                    item_content["original_index"] = -1
                else:
                    try:
                        item_content["original_index"] = self._items.index(next(
                            i for i in self._items if i["text"] == item_content["text"] and i["data"] == item_content["data"]
                        ))
                    except (ValueError, StopIteration):
                        item_content["original_index"] = idx

        if len(all_items) <= self._max_items:
            return all_items

        if self._overflow_mode == self.OverflowMode.ELLIPSIS:
            visible = []

            first_item = all_items[0].copy()
            visible.append(first_item)

            hidden_start = 1
            hidden_end = len(all_items) - (self._max_items - 2)

            if hidden_start < hidden_end:
                hidden_items_list = all_items[hidden_start:hidden_end]
                if hidden_items_list:
                    ellipsis_data = {
                        "text": "...", "data": None, "is_ellipsis": True,
                        "hidden_items": hidden_items_list
                    }
                    visible.append(ellipsis_data)
            else:
                hidden_end = hidden_start

            for i in range(hidden_end, len(all_items)):
                item = all_items[i].copy()
                visible.append(item)

            return visible

        elif self._overflow_mode == self.OverflowMode.DROPDOWN:
            if len(all_items) > 2:
                visible = []

                first_item = all_items[0].copy()
                visible.append(first_item)

                hidden_items_list = all_items[1:-1]
                if hidden_items_list:
                    dropdown_data = {
                        "text": "...", "data": None, "is_ellipsis": True,
                        "hidden_items": hidden_items_list
                    }
                    visible.append(dropdown_data)

                last_item = all_items[-1].copy()
                visible.append(last_item)

                return visible
            return all_items[-self._max_items:].copy()

        # SCROLL mode or fallback
        return all_items[-self._max_items:].copy()

    def _create_ellipsis_item(self, hidden_items: List[Dict[str, Any]]) -> FluentBreadcrumbItem:
        """Create ellipsis item with dropdown menu and animations"""
        ellipsis_item = FluentBreadcrumbItem("...", None, self)
        ellipsis_item.setCurrent(False)

        menu = QMenu(self)

        for item_data_loop_var in hidden_items:
            action_text = item_data_loop_var.get("text", "N/A")
            action = QAction(action_text, menu)

            action.triggered.connect(
                lambda _checked=False, current_item_data=item_data_loop_var:
                self._on_item_clicked(current_item_data.get(
                    "original_index", -1), current_item_data.get("data"))
            )
            menu.addAction(action)

        ellipsis_item.clicked.connect(
            lambda _checked=False: self._show_dropdown_menu_animated(ellipsis_item, menu)
        )

        return ellipsis_item

    def _show_dropdown_menu_animated(self, button: FluentBreadcrumbItem, menu: QMenu):
        """Show dropdown menu with smooth animation"""
        # Add subtle scale animation to button before showing menu
        scale_anim = FluentMicroInteraction.scale_animation(button, scale=0.95)
        
        # Show menu after animation
        QTimer.singleShot(
            FluentAnimation.DURATION_ULTRA_FAST,
            lambda: self._show_dropdown_menu(button, menu)
        )

    def _show_dropdown_menu(self, button: FluentBreadcrumbItem, menu: QMenu):
        """Show dropdown menu"""
        global_pos = button.mapToGlobal(button.rect().bottomLeft())
        menu.exec(global_pos)

    def _on_item_clicked(self, index: int, data: Any):
        """Handle item clicked with feedback animation"""
        # Add click feedback
        clicked_items = [
            widget for widget in self.findChildren(FluentBreadcrumbItem)
            if hasattr(widget, 'data') and widget.data() == data
        ]
        
        for item in clicked_items:
            FluentMicroInteraction.pulse_animation(item, scale=1.05)
        
        self.item_clicked.emit(index, data)

    def _on_theme_changed(self, _):
        """Handle theme change with smooth transitions"""
        # Create smooth theme transition sequence
        theme_sequence = FluentSequence(self)
        
        # Fade container
        container_fade = FluentTransition.create_transition(
            self, FluentTransition.FADE,
            FluentAnimation.DURATION_MEDIUM,
            FluentTransition.EASE_SMOOTH
        )
        container_fade.setStartValue(1.0)
        container_fade.setEndValue(0.8)
        theme_sequence.addAnimation(container_fade)
        
        # Update styles
        theme_sequence.addCallback(lambda: [
            self._setup_style(),
            self._update_breadcrumb()
        ])
        
        # Fade back in
        fade_in = FluentTransition.create_transition(
            self, FluentTransition.FADE,
            FluentAnimation.DURATION_MEDIUM,
            FluentTransition.EASE_SMOOTH
        )
        fade_in.setStartValue(0.8)
        fade_in.setEndValue(1.0)
        theme_sequence.addAnimation(fade_in)
        
        theme_sequence.start()
