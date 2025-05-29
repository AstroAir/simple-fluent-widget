"""
Composite Toolbar Components
High-level toolbar components that combine multiple widgets for common use cases.
"""

from typing import Optional, Dict, Any, List, Callable, Union
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame, 
                               QLabel, QPushButton, QLineEdit, QComboBox,
                               QToolButton, QButtonGroup, QSizePolicy,
                               QSpacerItem, QMenu, QAction)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QIcon, QPixmap, QFont

from ...core.enhanced_base import FluentLayoutBuilder, FluentStandardButton, FluentToolbar
from ...core.enhanced_animations import FluentTransitionManager, FluentMicroInteractions
from ...core.base import FluentBaseWidget
from ...core.theme import theme_manager


class FluentActionToolbar(FluentToolbar):
    """Enhanced action toolbar with grouped actions and animations"""
    
    action_triggered = Signal(str)  # action_id
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(title, parent)
        self._action_groups = {}
        self._separators = []
        
        self.setFixedHeight(48)
        self._setup_enhanced_styling()
    
    def _setup_enhanced_styling(self):
        """Apply enhanced styling with animations"""
        self.setStyleSheet(f"""
            FluentActionToolbar {{
                background: {theme_manager.surface_color()};
                border-bottom: 1px solid {theme_manager.border_color()};
                border-radius: 0px;
            }}
        """)
    
    def add_action_group(self, group_id: str, actions: List[Dict[str, Any]], 
                        separator: bool = True) -> List[QPushButton]:
        """Add a group of related actions
        
        Args:
            group_id: Unique identifier for the group
            actions: List of action dicts with keys: id, text, icon, tooltip, callback
            separator: Whether to add separator before this group
        """
        if separator and self._action_groups:
            self.add_separator()
        
        buttons = []
        group_widget = QWidget()
        group_layout = FluentLayoutBuilder.create_horizontal_layout(spacing=4)
        group_widget.setLayout(group_layout)
        
        for action_data in actions:
            btn = FluentStandardButton(
                text=action_data.get('text', ''),
                icon=action_data.get('icon'),
                size='small'
            )
            
            if 'tooltip' in action_data:
                btn.setToolTip(action_data['tooltip'])
            
            # Connect callback
            action_id = action_data['id']
            if 'callback' in action_data:
                btn.clicked.connect(action_data['callback'])
            btn.clicked.connect(lambda checked, aid=action_id: self.action_triggered.emit(aid))
            
            # Add micro-interaction
            FluentMicroInteractions.add_button_feedback(btn)
            
            group_layout.addWidget(btn)
            buttons.append(btn)
        
        self.add_widget(group_widget)
        self._action_groups[group_id] = {
            'widget': group_widget,
            'buttons': buttons,
            'actions': actions
        }
        
        return buttons
    
    def add_toggle_group(self, group_id: str, actions: List[Dict[str, Any]], 
                        exclusive: bool = True) -> QButtonGroup:
        """Add a group of toggle buttons"""
        button_group = QButtonGroup(self)
        button_group.setExclusive(exclusive)
        
        buttons = self.add_action_group(group_id, actions, separator=True)
        
        for i, btn in enumerate(buttons):
            btn.setCheckable(True)
            button_group.addButton(btn, i)
        
        return button_group
    
    def set_action_enabled(self, group_id: str, action_index: int, enabled: bool):
        """Enable/disable specific action"""
        if group_id in self._action_groups:
            buttons = self._action_groups[group_id]['buttons']
            if 0 <= action_index < len(buttons):
                buttons[action_index].setEnabled(enabled)
    
    def get_action_button(self, group_id: str, action_index: int) -> Optional[QPushButton]:
        """Get specific action button"""
        if group_id in self._action_groups:
            buttons = self._action_groups[group_id]['buttons']
            if 0 <= action_index < len(buttons):
                return buttons[action_index]
        return None


class FluentSearchToolbar(FluentToolbar):
    """Enhanced search toolbar with filters and view controls"""
    
    search_changed = Signal(str)
    filter_changed = Signal(str, str)  # filter_type, value
    view_changed = Signal(str)  # view_mode
    
    def __init__(self, placeholder: str = "搜索...", parent=None):
        super().__init__("", parent)
        self._placeholder = placeholder
        self._filters = {}
        self._view_buttons = []
        
        self.setFixedHeight(44)
        self._setup_search_ui()
        self._setup_enhanced_styling()
    
    def _setup_search_ui(self):
        """Setup search interface"""
        # Search input
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(self._placeholder)
        self._search_input.setFixedHeight(32)
        self._search_input.textChanged.connect(self.search_changed.emit)
        
        # Add search animation
        self._search_animation = FluentTransitionManager.create_smooth_resize(
            self._search_input, duration=200
        )
        
        # Search input styling
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {theme_manager.input_background()};
                border: 1px solid {theme_manager.border_color()};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                min-width: 200px;
            }}
            QLineEdit:focus {{
                border-color: {theme_manager.accent_color()};
                background: {theme_manager.surface_color()};
            }}
        """)
        
        self.add_widget(self._search_input)
        
        # Add spacer
        spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Expanding)
        self.layout().addItem(spacer)
    
    def _setup_enhanced_styling(self):
        """Apply enhanced styling"""
        self.setStyleSheet(f"""
            FluentSearchToolbar {{
                background: {theme_manager.surface_color()};
                border-bottom: 1px solid {theme_manager.border_color()};
            }}
        """)
    
    def add_filter_combo(self, filter_id: str, label: str, options: List[tuple], 
                        default_index: int = 0) -> QComboBox:
        """Add filter combobox
        
        Args:
            filter_id: Unique identifier for filter
            label: Display label
            options: List of (display_text, value) tuples
            default_index: Default selection index
        """
        # Label
        filter_label = QLabel(label)
        filter_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.text_color()};
                font-size: 12px;
                margin-right: 4px;
            }}
        """)
        
        # Combobox
        combo = QComboBox()
        combo.setFixedHeight(32)
        for display_text, value in options:
            combo.addItem(display_text, value)
        
        if 0 <= default_index < len(options):
            combo.setCurrentIndex(default_index)
        
        # Connect signal
        combo.currentTextChanged.connect(
            lambda text: self.filter_changed.emit(filter_id, combo.currentData())
        )
        
        # Styling
        combo.setStyleSheet(f"""
            QComboBox {{
                background: {theme_manager.input_background()};
                border: 1px solid {theme_manager.border_color()};
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 12px;
                min-width: 100px;
            }}
            QComboBox:hover {{
                border-color: {theme_manager.accent_color()};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
        """)
        
        # Add to toolbar
        container = QWidget()
        layout = FluentLayoutBuilder.create_horizontal_layout(spacing=4)
        layout.addWidget(filter_label)
        layout.addWidget(combo)
        container.setLayout(layout)
        
        self.add_widget(container)
        self._filters[filter_id] = combo
        
        return combo
    
    def add_view_controls(self, views: List[Dict[str, Any]], default: str = None) -> QButtonGroup:
        """Add view mode controls
        
        Args:
            views: List of view dicts with keys: id, icon, tooltip
            default: Default view id
        """
        view_group = QButtonGroup(self)
        view_group.setExclusive(True)
        
        container = QWidget()
        layout = FluentLayoutBuilder.create_horizontal_layout(spacing=2)
        container.setLayout(layout)
        
        for view_data in views:
            btn = QToolButton()
            btn.setFixedSize(32, 32)
            btn.setCheckable(True)
            
            if 'icon' in view_data:
                btn.setIcon(view_data['icon'])
            if 'tooltip' in view_data:
                btn.setToolTip(view_data['tooltip'])
            
            # Styling
            btn.setStyleSheet(f"""
                QToolButton {{
                    background: transparent;
                    border: 1px solid {theme_manager.border_color()};
                    border-radius: 6px;
                }}
                QToolButton:hover {{
                    background: {theme_manager.hover_color()};
                }}
                QToolButton:checked {{
                    background: {theme_manager.accent_color()};
                    border-color: {theme_manager.accent_color()};
                }}
            """)
            
            # Connect signal
            view_id = view_data['id']
            btn.clicked.connect(lambda checked, vid=view_id: self.view_changed.emit(vid))
            
            # Add micro-interaction
            FluentMicroInteractions.add_button_feedback(btn)
            
            layout.addWidget(btn)
            view_group.addButton(btn)
            self._view_buttons.append((view_id, btn))
            
            # Set default
            if default and view_id == default:
                btn.setChecked(True)
        
        self.add_widget(container)
        return view_group
    
    def set_search_text(self, text: str):
        """Set search input text"""
        self._search_input.setText(text)
    
    def get_search_text(self) -> str:
        """Get current search text"""
        return self._search_input.text()
    
    def set_filter_value(self, filter_id: str, value: Any):
        """Set filter combobox value"""
        if filter_id in self._filters:
            combo = self._filters[filter_id]
            for i in range(combo.count()):
                if combo.itemData(i) == value:
                    combo.setCurrentIndex(i)
                    break
    
    def focus_search(self):
        """Focus the search input with animation"""
        self._search_input.setFocus()
        # Animate width expansion
        if self._search_animation:
            self._search_animation.setStartValue(self._search_input.width())
            self._search_animation.setEndValue(min(300, self._search_input.width() + 50))
            self._search_animation.start()


class FluentViewToolbar(FluentToolbar):
    """Enhanced view toolbar with sorting, grouping, and display options"""
    
    sort_changed = Signal(str, bool)  # field, ascending
    group_changed = Signal(str)  # field
    display_changed = Signal(str, Any)  # option, value
    
    def __init__(self, title: str = "视图选项", parent=None):
        super().__init__(title, parent)
        self._sort_combo = None
        self._sort_order_btn = None
        self._group_combo = None
        self._display_options = {}
        
        self.setFixedHeight(40)
        self._setup_view_controls()
        self._setup_enhanced_styling()
    
    def _setup_view_controls(self):
        """Setup view control interface"""
        # Sort controls
        self._add_sort_controls()
        
        # Add separator
        self.add_separator()
        
        # Group controls
        self._add_group_controls()
    
    def _add_sort_controls(self):
        """Add sorting controls"""
        # Sort label
        sort_label = QLabel("排序:")
        sort_label.setStyleSheet(f"color: {theme_manager.text_color()}; font-size: 12px;")
        
        # Sort field combo
        self._sort_combo = QComboBox()
        self._sort_combo.setFixedHeight(28)
        self._sort_combo.setMinimumWidth(120)
        self._sort_combo.currentTextChanged.connect(self._on_sort_changed)
        
        # Sort order button
        self._sort_order_btn = QToolButton()
        self._sort_order_btn.setFixedSize(28, 28)
        self._sort_order_btn.setCheckable(True)
        self._sort_order_btn.setToolTip("切换排序顺序")
        self._sort_order_btn.clicked.connect(self._on_sort_order_changed)
        
        # Style sort controls
        self._style_sort_controls()
        
        # Add to toolbar
        container = QWidget()
        layout = FluentLayoutBuilder.create_horizontal_layout(spacing=6)
        layout.addWidget(sort_label)
        layout.addWidget(self._sort_combo)
        layout.addWidget(self._sort_order_btn)
        container.setLayout(layout)
        
        self.add_widget(container)
    
    def _add_group_controls(self):
        """Add grouping controls"""
        # Group label
        group_label = QLabel("分组:")
        group_label.setStyleSheet(f"color: {theme_manager.text_color()}; font-size: 12px;")
        
        # Group combo
        self._group_combo = QComboBox()
        self._group_combo.setFixedHeight(28)
        self._group_combo.setMinimumWidth(100)
        self._group_combo.addItem("无分组", None)
        self._group_combo.currentTextChanged.connect(self._on_group_changed)
        
        # Style group controls
        combo_style = f"""
            QComboBox {{
                background: {theme_manager.input_background()};
                border: 1px solid {theme_manager.border_color()};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }}
            QComboBox:hover {{
                border-color: {theme_manager.accent_color()};
            }}
        """
        self._group_combo.setStyleSheet(combo_style)
        
        # Add to toolbar
        container = QWidget()
        layout = FluentLayoutBuilder.create_horizontal_layout(spacing=6)
        layout.addWidget(group_label)
        layout.addWidget(self._group_combo)
        container.setLayout(layout)
        
        self.add_widget(container)
    
    def _style_sort_controls(self):
        """Apply styling to sort controls"""
        combo_style = f"""
            QComboBox {{
                background: {theme_manager.input_background()};
                border: 1px solid {theme_manager.border_color()};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }}
            QComboBox:hover {{
                border-color: {theme_manager.accent_color()};
            }}
        """
        self._sort_combo.setStyleSheet(combo_style)
        
        btn_style = f"""
            QToolButton {{
                background: {theme_manager.input_background()};
                border: 1px solid {theme_manager.border_color()};
                border-radius: 4px;
            }}
            QToolButton:hover {{
                background: {theme_manager.hover_color()};
            }}
            QToolButton:checked {{
                background: {theme_manager.accent_color()};
                color: white;
            }}
        """
        self._sort_order_btn.setStyleSheet(btn_style)
        
        # Set icons/text for sort order
        self._update_sort_order_display()
    
    def _setup_enhanced_styling(self):
        """Apply enhanced styling"""
        self.setStyleSheet(f"""
            FluentViewToolbar {{
                background: {theme_manager.surface_color()};
                border-bottom: 1px solid {theme_manager.border_color()};
            }}
        """)
    
    def add_sort_options(self, options: List[tuple]):
        """Add sort field options
        
        Args:
            options: List of (display_text, field_name) tuples
        """
        if self._sort_combo:
            self._sort_combo.clear()
            for display_text, field_name in options:
                self._sort_combo.addItem(display_text, field_name)
    
    def add_group_options(self, options: List[tuple]):
        """Add group field options
        
        Args:
            options: List of (display_text, field_name) tuples
        """
        if self._group_combo:
            # Keep "无分组" option
            current_count = self._group_combo.count()
            for display_text, field_name in options:
                self._group_combo.addItem(display_text, field_name)
    
    def add_display_option(self, option_id: str, widget: QWidget):
        """Add custom display option widget"""
        self.add_separator()
        self.add_widget(widget)
        self._display_options[option_id] = widget
    
    def _on_sort_changed(self):
        """Handle sort field change"""
        if self._sort_combo:
            field = self._sort_combo.currentData()
            ascending = not self._sort_order_btn.isChecked()
            self.sort_changed.emit(field, ascending)
    
    def _on_sort_order_changed(self):
        """Handle sort order change"""
        if self._sort_combo:
            field = self._sort_combo.currentData()
            ascending = not self._sort_order_btn.isChecked()
            self.sort_changed.emit(field, ascending)
        self._update_sort_order_display()
    
    def _on_group_changed(self):
        """Handle group field change"""
        if self._group_combo:
            field = self._group_combo.currentData()
            self.group_changed.emit(field)
    
    def _update_sort_order_display(self):
        """Update sort order button display"""
        if self._sort_order_btn:
            if self._sort_order_btn.isChecked():
                self._sort_order_btn.setText("↓")
                self._sort_order_btn.setToolTip("降序排列")
            else:
                self._sort_order_btn.setText("↑")
                self._sort_order_btn.setToolTip("升序排列")
    
    def set_sort_field(self, field: str):
        """Set current sort field"""
        if self._sort_combo:
            for i in range(self._sort_combo.count()):
                if self._sort_combo.itemData(i) == field:
                    self._sort_combo.setCurrentIndex(i)
                    break
    
    def set_sort_ascending(self, ascending: bool):
        """Set sort order"""
        if self._sort_order_btn:
            self._sort_order_btn.setChecked(not ascending)
            self._update_sort_order_display()
    
    def set_group_field(self, field: str):
        """Set current group field"""
        if self._group_combo:
            for i in range(self._group_combo.count()):
                if self._group_combo.itemData(i) == field:
                    self._group_combo.setCurrentIndex(i)
                    break


class FluentStatusToolbar(FluentToolbar):
    """Enhanced status toolbar with progress, stats, and notifications"""
    
    def __init__(self, parent=None):
        super().__init__("", parent)
        self._status_label = None
        self._progress_widget = None
        self._stats_widgets = {}
        self._notification_timer = QTimer()
        self._notification_timer.timeout.connect(self._clear_temporary_status)
        
        self.setFixedHeight(32)
        self._setup_status_ui()
        self._setup_enhanced_styling()
    
    def _setup_status_ui(self):
        """Setup status interface"""
        # Main status label
        self._status_label = QLabel("就绪")
        self._status_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.text_color()};
                font-size: 12px;
                padding: 4px 8px;
            }}
        """)
        
        self.add_widget(self._status_label)
        
        # Add spacer to push stats to the right
        spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Expanding)
        self.layout().addItem(spacer)
    
    def _setup_enhanced_styling(self):
        """Apply enhanced styling"""
        self.setStyleSheet(f"""
            FluentStatusToolbar {{
                background: {theme_manager.surface_color()};
                border-top: 1px solid {theme_manager.border_color()};
                border-radius: 0px;
            }}
        """)
    
    def set_status(self, text: str, temporary: bool = False, duration: int = 3000):
        """Set status text
        
        Args:
            text: Status text to display
            temporary: Whether status should auto-clear
            duration: Duration in ms for temporary status
        """
        self._status_label.setText(text)
        
        if temporary:
            self._notification_timer.stop()
            self._notification_timer.start(duration)
    
    def add_stat(self, stat_id: str, label: str, value: str = "0") -> QLabel:
        """Add a statistics display
        
        Args:
            stat_id: Unique identifier for the stat
            label: Display label
            value: Initial value
        """
        container = QWidget()
        layout = FluentLayoutBuilder.create_horizontal_layout(spacing=4)
        
        # Label
        stat_label = QLabel(f"{label}:")
        stat_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.text_color()};
                font-size: 11px;
                font-weight: 500;
            }}
        """)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.accent_color()};
                font-size: 11px;
                font-weight: bold;
            }}
        """)
        
        layout.addWidget(stat_label)
        layout.addWidget(value_label)
        container.setLayout(layout)
        
        self.add_widget(container)
        self._stats_widgets[stat_id] = value_label
        
        return value_label
    
    def update_stat(self, stat_id: str, value: str):
        """Update statistics value"""
        if stat_id in self._stats_widgets:
            self._stats_widgets[stat_id].setText(value)
    
    def show_progress(self, text: str = "处理中..."):
        """Show progress indicator"""
        if self._progress_widget is None:
            from ...components.basic.loading import FluentLoadingIndicator
            self._progress_widget = FluentLoadingIndicator(size=16)
        
        # Create progress container
        container = QWidget()
        layout = FluentLayoutBuilder.create_horizontal_layout(spacing=6)
        layout.addWidget(self._progress_widget)
        
        progress_label = QLabel(text)
        progress_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.text_color()};
                font-size: 12px;
            }}
        """)
        layout.addWidget(progress_label)
        container.setLayout(layout)
        
        # Replace status label temporarily
        self._status_label.hide()
        self.add_widget(container)
        self._progress_container = container
        
        self._progress_widget.start()
    
    def hide_progress(self):
        """Hide progress indicator"""
        if hasattr(self, '_progress_container'):
            self._progress_widget.stop()
            self._progress_container.hide()
            self.layout().removeWidget(self._progress_container)
            self._progress_container.deleteLater()
            del self._progress_container
            
        self._status_label.show()
    
    def _clear_temporary_status(self):
        """Clear temporary status message"""
        self.set_status("就绪")
        self._notification_timer.stop()
