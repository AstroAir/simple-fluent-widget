# filepath: d:\Project\simple-fluent-widget\components\basic\combobox.py
"""
Enhanced Fluent Design style dropdown components with improved animations and performance
"""

from PySide6.QtWidgets import (QComboBox, QWidget, QVBoxLayout, QHBoxLayout,
                               QListWidget, QListWidgetItem, QPushButton,
                               QScrollArea, QLineEdit, QGraphicsDropShadowEffect,
                               QCheckBox)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QRect, QByteArray, QTimer, QEasingCurve, QPoint
from PySide6.QtGui import QIcon, QColor, QPainter, QPainterPath
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                      FluentRevealEffect, FluentSequence)
from typing import Optional, List, Any, Dict


class FluentComboBoxStyle:
    """Centralized style management for all ComboBox components"""

    @staticmethod
    def get_base_styles() -> Dict[str, str]:
        """Get base styles for consistency across all components"""
        theme = theme_manager

        return {
            "primary": theme.get_color('primary').name(),
            "secondary": theme.get_color('secondary').name(),
            "surface": theme.get_color('surface').name(),
            "background": theme.get_color('background').name(),
            "card": theme.get_color('card').name(),
            "border": theme.get_color('border').name(),
            "text_primary": theme.get_color('text_primary').name(),
            "text_secondary": theme.get_color('text_secondary').name(),
            "text_disabled": theme.get_color('text_disabled').name(),
            "accent_light": theme.get_color('accent_light').name(),
            "accent_medium": theme.get_color('accent_medium').name(),
            "accent_dark": theme.get_color('accent_dark').name(),
        }

    @staticmethod
    def get_combobox_style() -> str:
        """Get unified ComboBox style"""
        colors = FluentComboBoxStyle.get_base_styles()

        return f"""
            QComboBox {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                font-weight: 400;
                color: {colors['text_primary']};
                selection-background-color: {colors['primary']};
                min-height: 20px;
            }}
            QComboBox:hover {{
                border-color: {colors['primary']};
                background-color: {colors['accent_light']};
                box-shadow: 0 2px 12px rgba(0, 120, 212, 0.15);
            }}
            QComboBox:focus {{
                border-color: {colors['primary']};
                border-width: 2px;
                padding: 9px 13px;
                background-color: {colors['surface']};
                box-shadow: 0 0 0 3px rgba(0, 120, 212, 0.1);
            }}
            QComboBox:disabled {{
                background-color: {colors['background']};
                border-color: {colors['border']};
                color: {colors['text_disabled']};
                opacity: 0.6;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 32px;
                background: transparent;
                border-radius: 6px;
                margin-right: 4px;
            }}
            QComboBox::drop-down:hover {{
                background-color: {colors['accent_light']};
            }}
            QComboBox::down-arrow {{
                image: none;
                border-style: solid;
                border-width: 4px 4px 0 4px;
                border-color: {colors['text_primary']} transparent transparent transparent;
                width: 0;
                height: 0;
                margin: 8px;
            }}
            QComboBox::down-arrow:hover {{
                border-top-color: {colors['primary']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
                selection-background-color: {colors['primary']};
                selection-color: white;
                padding: 8px;
                outline: none;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
                margin-top: 4px;
                show-decoration-selected: 1;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 12px 16px;
                border-radius: 8px;
                margin: 2px;
                border: none;
                min-height: 20px;
                color: {colors['text_primary']};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {colors['accent_light']};
                color: {colors['text_primary']};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {colors['primary']};
                color: white;
                font-weight: 500;
            }}
            QComboBox QAbstractItemView::item:selected:hover {{
                background-color: {colors['accent_dark']};
                color: white;
            }}
        """

    @staticmethod
    def get_button_style() -> str:
        """Get unified button style"""
        colors = FluentComboBoxStyle.get_base_styles()

        return f"""
            QPushButton {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: 400;
                color: {colors['text_primary']};
                text-align: left;
                min-height: 20px;
            }}
            QPushButton:hover {{
                border-color: {colors['primary']};
                background-color: {colors['accent_light']};
                box-shadow: 0 2px 12px rgba(0, 120, 212, 0.15);
            }}
            QPushButton:pressed {{
                background-color: {colors['accent_medium']};
                transform: scale(0.98);
            }}
            QPushButton:disabled {{
                background-color: {colors['background']};
                border-color: {colors['border']};
                color: {colors['text_disabled']};
                opacity: 0.6;
            }}
        """

    @staticmethod
    def get_list_style() -> str:
        """Get unified list widget style"""
        colors = FluentComboBoxStyle.get_base_styles()

        return f"""
            QListWidget {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
                outline: none;
                padding: 8px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            }}
            QListWidget::item {{
                padding: 12px 16px;
                border-radius: 8px;
                margin: 2px;
                color: {colors['text_primary']};
                border: none;
                min-height: 20px;
            }}
            QListWidget::item:hover {{
                background-color: {colors['accent_light']};
            }}
            QListWidget::item:selected {{
                background-color: {colors['primary']};
                color: white;
            }}
            QScrollBar:vertical {{
                background: {colors['background']};
                width: 8px;
                border-radius: 4px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors['border']};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors['text_secondary']};
            }}
        """


class FluentAnimationManager:
    """Centralized animation management for better performance"""

    _animation_cache: Dict[str, QPropertyAnimation] = {}
    _effect_cache: Dict[QWidget, Any] = {}

    @classmethod
    def get_or_create_animation(cls, widget: QWidget, property_name: str,
                                duration: int = FluentAnimation.DURATION_MEDIUM) -> QPropertyAnimation:
        """Get or create animation with caching for performance"""
        cache_key = f"{id(widget)}_{property_name}"

        if cache_key not in cls._animation_cache:
            animation = QPropertyAnimation(
                widget, QByteArray(property_name.encode()))
            animation.setDuration(duration)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            cls._animation_cache[cache_key] = animation            # Clean up when widget is destroyed
            widget.destroyed.connect(lambda: cls._cleanup_animation(cache_key))

        return cls._animation_cache[cache_key]

    @classmethod
    def _cleanup_animation(cls, cache_key: str):
        """Clean up animation cache"""
        if cache_key in cls._animation_cache:
            try:
                animation = cls._animation_cache[cache_key]
                # Check if the animation object is still valid
                if animation and hasattr(animation, 'stop'):
                    animation.stop()
            except RuntimeError:
                # Animation object already deleted by Qt
                pass
            finally:
                # Always remove from cache
                del cls._animation_cache[cache_key]

    @classmethod
    def create_smooth_dropdown_animation(cls, view_widget: QWidget) -> QPropertyAnimation:
        """Create optimized dropdown animation"""
        animation = cls.get_or_create_animation(
            view_widget, "geometry", FluentAnimation.DURATION_FAST)
        animation.setEasingCurve(QEasingCurve.Type.OutBack)
        return animation

    @classmethod
    def create_fade_animation(cls, widget: QWidget, duration: int = 200) -> QPropertyAnimation:
        """Create optimized fade animation"""
        from PySide6.QtWidgets import QGraphicsOpacityEffect

        # Reuse or create effect
        if widget not in cls._effect_cache:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            cls._effect_cache[widget] = effect
            widget.destroyed.connect(
                lambda: cls._effect_cache.pop(widget, None))

        effect = cls._effect_cache[widget]
        animation = cls.get_or_create_animation(effect, "opacity", duration)
        return animation


class FluentSearchBox(QLineEdit):
    """Enhanced search box component with improved performance"""

    text_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.textChanged.connect(self.text_changed.emit)
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_debounced_change)
        self._setup_style()

    def _setup_style(self):
        """Setup enhanced search box style"""
        colors = FluentComboBoxStyle.get_base_styles()

        style = f"""
            QLineEdit {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: {colors['text_primary']};
                selection-background-color: {colors['primary']};
            }}
            QLineEdit:hover {{
                border-color: {colors['primary']};
                background-color: {colors['accent_light']};
            }}
            QLineEdit:focus {{
                border-color: {colors['primary']};
                border-width: 2px;
                padding: 9px 13px;
                box-shadow: 0 0 0 3px rgba(0, 120, 212, 0.1);
            }}
        """
        self.setStyleSheet(style)

    def set_text(self, text: str):
        """Set text content with debounced change detection"""
        self.setText(text)

    def _emit_debounced_change(self):
        """Emit change after debounce period"""
        self.text_changed.emit(self.text())

    def keyPressEvent(self, event):
        """Override to add debounced text change"""
        super().keyPressEvent(event)
        self._debounce_timer.start(150)  # 150ms debounce


class FluentComboBox(QComboBox):
    """Enhanced Fluent Design style combo box with improved animations and performance"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._drop_animation = None
        self._is_expanded = False
        self._last_theme_mode = theme_manager.get_theme_mode()

        self.setMinimumHeight(42)
        self._setup_enhanced_style()
        self._setup_optimized_animations()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_enhanced_style(self):
        """Setup enhanced style with better visual hierarchy"""
        self.setStyleSheet(FluentComboBoxStyle.get_combobox_style())

        # Add drop shadow effect for better depth perception
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def _setup_optimized_animations(self):
        """Setup optimized animations with caching"""
        # Use cached animation manager
        self._drop_animation = FluentAnimationManager.create_smooth_dropdown_animation(
            self)

    def showPopup(self):
        """Show dropdown with enhanced smooth animation"""
        self._is_expanded = True

        # First show the popup to get correct geometry
        super().showPopup()

        # Add slight delay to ensure view is properly initialized
        QTimer.singleShot(10, self._animate_popup_show)

    def _animate_popup_show(self):
        """Animate popup show with proper geometry handling"""
        if not self.view() or not self._is_expanded:
            return

        view = self.view()

        # Get final position
        final_rect = view.geometry()

        # Create smooth reveal animation from top
        start_rect = QRect(
            final_rect.x(),
            final_rect.y() - 5,  # Reduced start offset to prevent jumping
            final_rect.width(),
            max(1, final_rect.height() // 4)  # Start with 1/4 height
        )

        # Use smoother easing curve
        if self._drop_animation:
            self._drop_animation.setStartValue(start_rect)
            self._drop_animation.setEndValue(final_rect)
            self._drop_animation.setEasingCurve(QEasingCurve.Type.OutQuart)
            # Slightly longer for smoothness
            self._drop_animation.setDuration(200)
            self._drop_animation.start()

        # Add fade effect with proper timing
        fade_anim = FluentAnimationManager.create_fade_animation(view, 150)
        fade_anim.setStartValue(0.3)
        fade_anim.setEndValue(1.0)
        fade_anim.start()

    def hidePopup(self):
        """Hide dropdown with smooth fade out"""
        self._is_expanded = False

        if self.view():
            # Stop any running animations first
            if self._drop_animation:
                self._drop_animation.stop()

            # Create quick fade out
            fade_anim = FluentAnimationManager.create_fade_animation(
                self.view(), 120)
            fade_anim.setStartValue(1.0)
            fade_anim.setEndValue(0.0)
            fade_anim.finished.connect(self._complete_hide_popup)
            fade_anim.start()
        else:
            super().hidePopup()

    def _complete_hide_popup(self):
        """Complete the hide popup operation"""
        super().hidePopup()

    def enterEvent(self, event):
        """Handle mouse enter with subtle micro-interaction"""
        # Only apply hover effect if not expanded to prevent interference
        if not self._is_expanded:
            # Use style-based hover effect instead of geometry changes
            self.setProperty("hovered", True)
            self.style().unpolish(self)
            self.style().polish(self)

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave"""
        # Remove hover state
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)

        super().leaveEvent(event)

    def _on_theme_changed(self):
        """Handle theme change with smooth transition"""
        current_mode = theme_manager.get_theme_mode()
        if current_mode != self._last_theme_mode:
            self._setup_enhanced_style()
            self._last_theme_mode = current_mode

    def paintEvent(self, event):
        """Custom paint event for better visual feedback"""
        super().paintEvent(event)

        # Add visual indicator for selected state
        if self.currentText() and not self._is_expanded:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Draw subtle selection indicator
            rect = self.rect()
            painter.setPen(QColor(theme_manager.get_color('primary')))
            painter.drawLine(rect.left() + 2, rect.bottom() - 2,
                             rect.left() + 20, rect.bottom() - 2)


class FluentMultiSelectComboBox(QWidget):
    """Enhanced multi-select combo box with optimized animations and performance"""

    selection_changed = Signal(list)  # List of selected items

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items = []
        self._selected_items = []
        self._is_expanded = False
        self._dropdown_widget = None
        self._last_theme_mode = theme_manager.get_theme_mode()

        self._setup_ui()
        self._setup_enhanced_style()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI with enhanced components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Enhanced main button with better typography
        self.main_button = QPushButton("Select items...")
        self.main_button.setMinimumHeight(42)
        self.main_button.clicked.connect(self._toggle_dropdown)

        layout.addWidget(self.main_button)

    def _setup_enhanced_style(self):
        """Setup enhanced style with better visual consistency"""
        self.main_button.setStyleSheet(FluentComboBoxStyle.get_button_style())

        # Add subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(6)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 1)
        self.main_button.setGraphicsEffect(shadow)

    def add_item(self, text: str, data: Any = None):
        """Add item with optimized feedback"""
        item = {
            'text': text,
            'data': data,
            'selected': False
        }
        self._items.append(item)
        self._update_display()

    def add_items(self, items: List[str]):
        """Add multiple items with batch optimization"""
        for item_text in items:
            item = {
                'text': item_text,
                'data': None,
                'selected': False
            }
            self._items.append(item)

        self._update_display()

    def get_selected_items(self) -> List[str]:
        """Get selected items"""
        return [item['text'] for item in self._items if item['selected']]

    def get_selected_data(self) -> List[Any]:
        """Get selected item data"""
        return [item['data'] for item in self._items if item['selected']]

    def set_selected_items(self, selected_texts: List[str]):
        """Set selected items with smooth animation"""
        changed = False
        for item in self._items:
            new_selected = item['text'] in selected_texts
            if item['selected'] != new_selected:
                item['selected'] = new_selected
                changed = True

        if changed:
            self._selected_items = self.get_selected_items()
            self._update_display()
            self.selection_changed.emit(self._selected_items)

    def clear_selection(self):
        """Clear selection with feedback animation"""
        changed = any(item['selected'] for item in self._items)

        for item in self._items:
            item['selected'] = False

        if changed:
            self._selected_items = []
            self._update_display()
            self.selection_changed.emit(self._selected_items)

    def _toggle_dropdown(self):
        """Toggle dropdown state with enhanced animation"""
        if self._is_expanded:
            self._hide_dropdown()
        else:
            self._show_dropdown()

    def _show_dropdown(self):
        """Show dropdown with enhanced smooth animation"""
        if self._dropdown_widget:
            self._dropdown_widget.close()

        self._dropdown_widget = self._create_enhanced_dropdown_widget()
        self._dropdown_widget.show()
        self._is_expanded = True

        # Optimized show animation sequence
        scale_anim = FluentAnimationManager.get_or_create_animation(
            self._dropdown_widget, "geometry", 200)

        # Calculate smooth entry animation
        final_rect = self._dropdown_widget.geometry()
        start_rect = QRect(final_rect.x(), final_rect.y() - 10,
                           final_rect.width(), max(1, final_rect.height() // 4))

        scale_anim.setStartValue(start_rect)
        scale_anim.setEndValue(final_rect)
        scale_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        scale_anim.start()

        # Add fade effect
        fade_anim = FluentAnimationManager.create_fade_animation(
            self._dropdown_widget, 150)
        fade_anim.setStartValue(0.5)
        fade_anim.setEndValue(1.0)
        fade_anim.start()

    def _hide_dropdown(self):
        """Hide dropdown with smooth animation"""
        if self._dropdown_widget:
            # Optimized hide animation
            fade_anim = FluentAnimationManager.create_fade_animation(
                self._dropdown_widget, 120)
            fade_anim.setStartValue(1.0)
            fade_anim.setEndValue(0.0)
            fade_anim.finished.connect(
                lambda: self._dropdown_widget.close() if self._dropdown_widget else None)
            fade_anim.start()

        self._is_expanded = False

    def _create_enhanced_dropdown_widget(self) -> QWidget:
        """Create enhanced dropdown widget with better performance"""
        dropdown = QWidget(self, Qt.WindowType.Popup)
        dropdown.setFixedWidth(self.width())
        dropdown.setMaximumHeight(280)

        # Calculate optimal position
        global_pos = self.mapToGlobal(self.rect().bottomLeft())
        dropdown.move(global_pos)

        layout = QVBoxLayout(dropdown)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Enhanced styling with better shadows and borders
        colors = FluentComboBoxStyle.get_base_styles()
        dropdown.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
                box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
            }}
        """)

        # Create optimized scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(4, 4, 4, 4)
        content_layout.setSpacing(3)

        # Add enhanced checkbox options
        self._create_checkbox_items(content_layout)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        # Enhanced action buttons with better spacing
        self._create_action_buttons(layout)

        return dropdown

    def _create_checkbox_items(self, layout: QVBoxLayout):
        """Create checkbox items with optimized performance"""
        colors = FluentComboBoxStyle.get_base_styles()

        for i, item in enumerate(self._items):
            checkbox = QCheckBox(item['text'])
            checkbox.setChecked(item['selected'])
            checkbox.stateChanged.connect(
                lambda state, idx=i: self._on_item_toggled(idx, state))

            # Style the checkbox
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {colors['text_primary']};
                    font-size: 14px;
                    padding: 8px;
                    border-radius: 6px;
                }}
                QCheckBox:hover {{
                    background-color: {colors['accent_light']};
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border-radius: 3px;
                    border: 2px solid {colors['border']};
                    background-color: {colors['surface']};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {colors['primary']};
                    border-color: {colors['primary']};
                }}
            """)

            layout.addWidget(checkbox)

    def _create_action_buttons(self, layout: QVBoxLayout):
        """Create action buttons with enhanced styling"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        colors = FluentComboBoxStyle.get_base_styles()
        button_style = f"""
            QPushButton {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 13px;
                font-weight: 500;
                color: {colors['text_primary']};
                min-height: 16px;
            }}
            QPushButton:hover {{
                background-color: {colors['primary']};
                color: white;
                border-color: {colors['primary']};
            }}
            QPushButton:pressed {{
                background-color: {colors['accent_dark']};
            }}
        """

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        select_all_btn.setStyleSheet(button_style)

        clear_all_btn = QPushButton("Clear")
        clear_all_btn.clicked.connect(self.clear_selection)
        clear_all_btn.setStyleSheet(button_style)

        done_btn = QPushButton("Done")
        done_btn.clicked.connect(self._hide_dropdown)
        done_btn.setStyleSheet(button_style + f"""
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {colors['accent_dark']};
            }}
        """)

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(clear_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(done_btn)

        layout.addLayout(button_layout)

    def _on_item_toggled(self, index: int, state: int):
        """Handle item toggle with optimized feedback"""
        if 0 <= index < len(self._items):
            self._items[index]['selected'] = (
                state == Qt.CheckState.Checked.value)
            self._selected_items = self.get_selected_items()
            self._update_display()
            self.selection_changed.emit(self._selected_items)

    def _select_all(self):
        """Select all items with enhanced feedback"""
        for item in self._items:
            item['selected'] = True

        self._selected_items = self.get_selected_items()
        self._update_display()
        self.selection_changed.emit(self._selected_items)

        # Recreate dropdown to update checkboxes
        if self._dropdown_widget:
            self._dropdown_widget.close()
            QTimer.singleShot(50, self._show_dropdown)

    def _update_display(self):
        """Update display text with optimized transitions"""
        selected_count = len(self._selected_items)

        if selected_count == 0:
            new_text = "Select items..."
        elif selected_count == 1:
            new_text = self._selected_items[0]
            if len(new_text) > 25:  # Truncate long text
                new_text = new_text[:22] + "..."
        else:
            new_text = f"{selected_count} items selected"

        self.main_button.setText(new_text)

    def _on_theme_changed(self):
        """Handle theme change with optimized transition"""
        current_mode = theme_manager.get_theme_mode()
        if current_mode != self._last_theme_mode:
            self._setup_enhanced_style()
            self._last_theme_mode = current_mode


class FluentSearchableComboBox(QWidget):
    """Enhanced searchable combo box with optimized search and animations"""

    item_selected = Signal(str, object)  # text, data

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items = []
        self._filtered_items = []
        self._selected_item = None
        self._is_expanded = False
        self._last_theme_mode = theme_manager.get_theme_mode()
        self._search_debounce_timer = QTimer()
        self._search_debounce_timer.setSingleShot(True)
        self._search_debounce_timer.timeout.connect(self._perform_search)

        self._setup_ui()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup enhanced UI with better performance"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Enhanced search input with better UX
        self.search_box = FluentSearchBox()
        self.search_box.setPlaceholderText("Type to search...")
        self.search_box.setMinimumHeight(42)
        self.search_box.text_changed.connect(self._on_search_text_changed)
        self.search_box.returnPressed.connect(self._select_first_item)

        # Enhanced dropdown list with better styling
        self.list_widget = QListWidget()
        self.list_widget.setMaximumHeight(240)
        self.list_widget.setVisible(False)
        self.list_widget.itemClicked.connect(self._on_item_clicked)

        layout.addWidget(self.search_box)
        layout.addWidget(self.list_widget)

        self._setup_enhanced_list_style()

    def _setup_enhanced_list_style(self):
        """Setup enhanced list style with better consistency"""
        self.list_widget.setStyleSheet(FluentComboBoxStyle.get_list_style())

        # Add drop shadow for better depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.list_widget.setGraphicsEffect(shadow)

    def add_item(self, text: str, data: Any = None):
        """Add item with optimized feedback"""
        item = {
            'text': text,
            'data': data
        }
        self._items.append(item)
        self._update_filtered_items()

    def add_items(self, items: List[str]):
        """Add multiple items with batch optimization"""
        for item_text in items:
            item = {
                'text': item_text,
                'data': None
            }
            self._items.append(item)

        self._update_filtered_items()

    def clear_items(self):
        """Clear items with animation"""
        self._items.clear()
        self._filtered_items.clear()
        self.list_widget.clear()

        if self.list_widget.isVisible():
            self._hide_list_with_animation()

    def set_selected_text(self, text: str):
        """Set selected text"""
        self.search_box.set_text(text)
        self._selected_item = next(
            (item for item in self._items if item['text'] == text), None)

    def get_selected_item(self) -> Optional[dict]:
        """Get selected item"""
        return self._selected_item

    def _on_search_text_changed(self, text: str):
        """Handle search text change with debouncing for better performance"""
        self._search_debounce_timer.stop()
        self._search_debounce_timer.start(200)  # 200ms debounce

    def _perform_search(self):
        """Perform the actual search with optimized filtering"""
        text = self.search_box.text()
        self._update_filtered_items(text)

        if text and self._filtered_items:
            if not self.list_widget.isVisible():
                self._show_list_with_animation()
            self._is_expanded = True
        else:
            if self.list_widget.isVisible():
                self._hide_list_with_animation()
            self._is_expanded = False

    def _show_list_with_animation(self):
        """Show list with optimized animation"""
        self.list_widget.setVisible(True)

        # Smooth reveal animation
        reveal_anim = FluentAnimationManager.get_or_create_animation(
            self.list_widget, "geometry", 180)

        final_rect = self.list_widget.geometry()
        start_rect = QRect(final_rect.x(), final_rect.y() - 10,
                           final_rect.width(), max(1, final_rect.height() // 3))

        reveal_anim.setStartValue(start_rect)
        reveal_anim.setEndValue(final_rect)
        reveal_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        reveal_anim.start()

        # Add fade effect
        fade_anim = FluentAnimationManager.create_fade_animation(
            self.list_widget, 150)
        fade_anim.setStartValue(0.7)
        fade_anim.setEndValue(1.0)
        fade_anim.start()

    def _hide_list_with_animation(self):
        """Hide list with smooth animation"""
        fade_anim = FluentAnimationManager.create_fade_animation(
            self.list_widget, 120)
        fade_anim.setStartValue(1.0)
        fade_anim.setEndValue(0.0)
        fade_anim.finished.connect(lambda: self.list_widget.setVisible(False))
        fade_anim.start()

    def _update_filtered_items(self, filter_text: str = ""):
        """Update filtered items with optimized search algorithm"""
        self.list_widget.clear()
        self._filtered_items.clear()

        if not filter_text:
            self._filtered_items = self._items.copy()
        else:
            filter_lower = filter_text.lower()
            self._filtered_items = [
                item for item in self._items
                if filter_lower in item['text'].lower()
            ]

        # Batch add items for better performance (limit to 50)
        for item in self._filtered_items[:50]:
            list_item = QListWidgetItem(item['text'])
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.list_widget.addItem(list_item)

        # Add ellipsis if more items available
        if len(self._filtered_items) > 50:
            ellipsis_item = QListWidgetItem(
                f"... and {len(self._filtered_items) - 50} more")
            ellipsis_item.setData(Qt.ItemDataRole.UserRole, None)
            self.list_widget.addItem(ellipsis_item)

    def _on_item_clicked(self, list_item: QListWidgetItem):
        """Handle item click with enhanced feedback"""
        item = list_item.data(Qt.ItemDataRole.UserRole)

        # Ignore ellipsis item
        if item is None:
            return

        self._selected_item = item
        self.search_box.set_text(item['text'])

        self._hide_list_with_animation()
        self._is_expanded = False

        self.item_selected.emit(item['text'], item['data'])

    def _select_first_item(self):
        """Select first item with enhanced feedback"""
        if self._filtered_items:
            first_item = self._filtered_items[0]
            self._selected_item = first_item
            self.search_box.set_text(first_item['text'])

            self._hide_list_with_animation()
            self._is_expanded = False

            self.item_selected.emit(first_item['text'], first_item['data'])

    def _on_theme_changed(self):
        """Handle theme change with optimized transition"""
        current_mode = theme_manager.get_theme_mode()
        if current_mode != self._last_theme_mode:
            self._setup_enhanced_list_style()
            self._last_theme_mode = current_mode


class FluentDropDownButton(QPushButton):
    """Enhanced dropdown button with optimized animations and performance"""

    item_clicked = Signal(str, object)  # text, data

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        self._menu_items = []
        self._dropdown_widget = None
        self._is_expanded = False
        self._original_text = text
        self._last_theme_mode = theme_manager.get_theme_mode()

        self.clicked.connect(self._toggle_dropdown)
        self.setMinimumHeight(42)

        self._setup_enhanced_style()
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_enhanced_style(self):
        """Setup enhanced style with better visual hierarchy"""
        self.setStyleSheet(FluentComboBoxStyle.get_button_style())

        # Add drop shadow for better depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        # Update text with dropdown indicator
        self._update_button_text()

    def _update_button_text(self):
        """Update button text with enhanced dropdown indicator"""
        if self._original_text:
            self.setText(f"{self._original_text} ▼")
        else:
            self.setText("Select ▼")

    def add_menu_item(self, text: str, data: Any = None, icon: Optional[QIcon] = None):
        """Add menu item"""
        item = {
            'text': text,
            'data': data,
            'icon': icon
        }
        self._menu_items.append(item)

    def add_menu_items(self, items: List[str]):
        """Add multiple menu items with batch optimization"""
        for item_text in items:
            item = {
                'text': item_text,
                'data': None,
                'icon': None
            }
            self._menu_items.append(item)

    def clear_menu_items(self):
        """Clear menu items"""
        self._menu_items.clear()

    def _toggle_dropdown(self):
        """Toggle dropdown menu with enhanced animations"""
        if self._is_expanded:
            self._hide_dropdown()
        else:
            self._show_dropdown()

    def _show_dropdown(self):
        """Show dropdown menu with enhanced smooth animation"""
        if not self._menu_items:
            return

        if self._dropdown_widget:
            self._dropdown_widget.close()

        self._dropdown_widget = self._create_enhanced_dropdown_menu()
        self._dropdown_widget.show()
        self._is_expanded = True

        # Enhanced show animation
        scale_anim = FluentAnimationManager.get_or_create_animation(
            self._dropdown_widget, "geometry", 180)

        final_rect = self._dropdown_widget.geometry()
        start_rect = QRect(final_rect.x(), final_rect.y() - 12,
                           final_rect.width(), max(1, final_rect.height() // 3))

        scale_anim.setStartValue(start_rect)
        scale_anim.setEndValue(final_rect)
        scale_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        scale_anim.start()

        # Add fade effect
        fade_anim = FluentAnimationManager.create_fade_animation(
            self._dropdown_widget, 150)
        fade_anim.setStartValue(0.5)
        fade_anim.setEndValue(1.0)
        fade_anim.start()

    def _hide_dropdown(self):
        """Hide dropdown menu with smooth animation"""
        if self._dropdown_widget:
            fade_anim = FluentAnimationManager.create_fade_animation(
                self._dropdown_widget, 120)
            fade_anim.setStartValue(1.0)
            fade_anim.setEndValue(0.0)
            fade_anim.finished.connect(
                lambda: self._dropdown_widget.close() if self._dropdown_widget else None)
            fade_anim.start()

        self._is_expanded = False

    def _create_enhanced_dropdown_menu(self) -> QWidget:
        """Create enhanced dropdown menu with better performance and styling"""
        menu = QWidget(None, Qt.WindowType.Popup)
        menu.setMinimumWidth(self.width())

        # Calculate optimal position
        global_pos = self.mapToGlobal(self.rect().bottomLeft())
        menu.move(global_pos)

        layout = QVBoxLayout(menu)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Enhanced styling with modern design
        colors = FluentComboBoxStyle.get_base_styles()
        menu.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
                box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
            }}
        """)

        # Add drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 6)
        menu.setGraphicsEffect(shadow)

        # Create enhanced menu items
        self._create_menu_items(layout, colors)

        return menu

    def _create_menu_items(self, layout: QVBoxLayout, colors: Dict[str, str]):
        """Create menu items with optimized styling and animations"""
        for item in self._menu_items:
            menu_item_btn = QPushButton(item['text'])
            if item['icon']:
                menu_item_btn.setIcon(item['icon'])

            menu_item_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 16px;
                    text-align: left;
                    color: {colors['text_primary']};
                    font-size: 14px;
                    font-weight: 400;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background-color: {colors['accent_light']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['accent_medium']};
                    transform: scale(0.98);
                }}
            """)

            menu_item_btn.clicked.connect(
                lambda checked, item=item: self._on_menu_item_clicked(item)
            )

            layout.addWidget(menu_item_btn)

    def _on_menu_item_clicked(self, item: dict):
        """Handle menu item click"""
        # Hide dropdown after small delay
        QTimer.singleShot(100, self._hide_dropdown)
        self.item_clicked.emit(item['text'], item['data'])

    def _on_theme_changed(self):
        """Handle theme change"""
        current_mode = theme_manager.get_theme_mode()
        if current_mode != self._last_theme_mode:
            self._setup_enhanced_style()
            self._last_theme_mode = current_mode
