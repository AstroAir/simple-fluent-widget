"""
Fluent Design Navigation View Component
A side navigation panel with hierarchical menu structure
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QScrollArea, QFrame, QPushButton, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QByteArray
from PySide6.QtGui import QIcon, QFont
from core.theme import theme_manager
from core.enhanced_base import FluentBaseWidget
from core.enhanced_animations import FluentMicroInteraction
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum


class NavigationViewDisplayMode(Enum):
    """Navigation view display modes"""
    MINIMAL = "minimal"      # Only icons visible
    COMPACT = "compact"      # Icons and minimal text
    EXPANDED = "expanded"    # Full navigation with text and icons


@dataclass
class NavigationItem:
    """Represents a navigation item"""
    text: str
    icon: Optional[QIcon] = None
    key: str = ""
    tooltip: str = ""
    enabled: bool = True
    visible: bool = True
    children: Optional[List['NavigationItem']] = None
    badge_text: str = ""
    badge_count: int = 0
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if not self.key:
            self.key = self.text.lower().replace(" ", "_")


class FluentNavigationItemWidget(QWidget):
    """Widget representing a single navigation item"""
    
    clicked = Signal(str)  # Emits the item key
    
    def __init__(self, item: NavigationItem, display_mode: NavigationViewDisplayMode, 
                 level: int = 0, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._item = item
        self._display_mode = display_mode
        self._level = level
        self._is_selected = False
        self._is_hovered = False
        
        self._setup_ui()
        self._setup_style()
        
    def _setup_ui(self):
        """Setup the UI for the navigation item"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8 + (self._level * 16), 8, 8, 8)
        layout.setSpacing(12)
        
        # Icon
        if self._item.icon:
            self._icon_label = QLabel()
            self._icon_label.setPixmap(self._item.icon.pixmap(16, 16))
            self._icon_label.setFixedSize(16, 16)
            layout.addWidget(self._icon_label)
        
        # Text (hidden in minimal mode)
        if self._display_mode != NavigationViewDisplayMode.MINIMAL:
            self._text_label = QLabel(self._item.text)
            self._text_label.setFont(QFont("Segoe UI", 11))
            layout.addWidget(self._text_label)
            
            layout.addStretch()
            
            # Badge (if present)
            if self._item.badge_count > 0 or self._item.badge_text:
                self._setup_badge(layout)
        
        self.setFixedHeight(36)
        
    def _setup_badge(self, layout: QHBoxLayout):
        """Setup badge display"""
        badge_text = self._item.badge_text or str(self._item.badge_count)
        badge_label = QLabel(badge_text)
        badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_label.setFixedSize(20, 16)
        badge_label.setStyleSheet(f"""
            QLabel {{
                background-color: {theme_manager.get_color('primary').name()};
                color: white;
                border-radius: 8px;
                font-size: 10px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(badge_label)
        
    def _setup_style(self):
        """Apply styling to the navigation item"""
        theme = theme_manager
        
        style = f"""
            FluentNavigationItemWidget {{
                border: none;
                border-radius: 4px;
                background-color: transparent;
            }}
            FluentNavigationItemWidget:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
        """
        
        if self._is_selected:
            style += f"""
                FluentNavigationItemWidget {{
                    background-color: {theme.get_color('accent_medium').name()};
                    border-left: 3px solid {theme.get_color('primary').name()};
                }}
            """
        
        self.setStyleSheet(style)
        
    def set_selected(self, selected: bool):
        """Set the selection state"""
        self._is_selected = selected
        self._setup_style()
        
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._item.key)
        super().mousePressEvent(event)
        
    def enterEvent(self, event):
        """Handle mouse enter"""
        self._is_hovered = True
        # Use simple hover effect instead of animation to avoid dependency issues
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave"""
        self._is_hovered = False
        super().leaveEvent(event)


class FluentNavigationView(FluentBaseWidget):
    """
    Fluent Design Navigation View Component
    
    Provides hierarchical side navigation with support for:
    - Collapsible/expandable modes
    - Icons and text
    - Badges and counts
    - Nested navigation items
    - Smooth animations
    - Theme consistency
    """
    
    # Signals
    selection_changed = Signal(str)  # Selected item key
    display_mode_changed = Signal(NavigationViewDisplayMode)
    
    # Constants
    WIDTH_MINIMAL = 48
    WIDTH_COMPACT = 120
    WIDTH_EXPANDED = 280
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Properties
        self._display_mode = NavigationViewDisplayMode.EXPANDED
        self._is_pane_open = True
        self._selected_item_key = ""
        self._auto_suggest_box_visible = False
        self._settings_visible = True
        
        # Data
        self._navigation_items: List[NavigationItem] = []
        self._item_widgets: Dict[str, FluentNavigationItemWidget] = {}
        
        # UI Elements - initialize as non-Optional since they're always created
        self._main_layout: QVBoxLayout
        self._header_area: QWidget
        self._content_area: QScrollArea
        self._content_widget: QWidget
        self._content_layout: QVBoxLayout
        self._footer_area: Optional[QWidget] = None
        self._pane_toggle_button: QPushButton
        
        # Setup
        self._setup_ui()
        self._setup_style()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup the UI layout"""
        # Set initial size
        self.setFixedWidth(self._get_current_width())
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        
        # Main layout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # Header area (hamburger button, auto-suggest box)
        self._setup_header()
        
        # Content area (navigation items)
        self._setup_content()
        
        # Footer area (settings, etc.)
        self._setup_footer()
        
    def _setup_header(self):
        """Setup the header area with toggle button"""
        self._header_area = QWidget()
        self._header_area.setFixedHeight(48)
        
        header_layout = QHBoxLayout(self._header_area)
        header_layout.setContentsMargins(8, 8, 8, 8)
        
        # Pane toggle button (hamburger menu)
        self._pane_toggle_button = QPushButton()
        self._pane_toggle_button.setText("☰")  # Use Unicode hamburger menu
        self._pane_toggle_button.setFixedSize(32, 32)
        self._pane_toggle_button.setToolTip("Toggle navigation pane")
        self._pane_toggle_button.clicked.connect(self._toggle_pane)
        header_layout.addWidget(self._pane_toggle_button)
        
        header_layout.addStretch()
        
        self._main_layout.addWidget(self._header_area)
        
    def _setup_content(self):
        """Setup the scrollable content area for navigation items"""
        self._content_area = QScrollArea()
        self._content_area.setWidgetResizable(True)
        self._content_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._content_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._content_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(4, 4, 4, 4)
        self._content_layout.setSpacing(2)
        self._content_layout.addStretch()
        
        self._content_area.setWidget(self._content_widget)
        self._main_layout.addWidget(self._content_area, 1)
        
    def _setup_footer(self):
        """Setup the footer area with settings"""
        if self._settings_visible:
            self._footer_area = QWidget()
            self._footer_area.setFixedHeight(48)
            
            footer_layout = QHBoxLayout(self._footer_area)
            footer_layout.setContentsMargins(8, 8, 8, 8)
            
            # Settings button
            settings_button = QPushButton()
            settings_button.setText("⚙")  # Use Unicode gear symbol
            settings_button.setFixedSize(32, 32)
            settings_button.setToolTip("Settings")
            footer_layout.addWidget(settings_button)
            
            footer_layout.addStretch()
            
            self._main_layout.addWidget(self._footer_area)
            
    def _setup_style(self):
        """Apply Fluent Design styling"""
        theme = theme_manager
        
        style = f"""
            FluentNavigationView {{
                background-color: {theme.get_color('surface').name()};
                border-right: 1px solid {theme.get_color('border').name()};
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
                font-size: 16px;
                color: {theme.get_color('text_primary').name()};
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
        """
        
        self.setStyleSheet(style)
        
    def _connect_signals(self):
        """Connect signals"""
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
    def _on_theme_changed(self):
        """Handle theme changes"""
        self._setup_style()
        for widget in self._item_widgets.values():
            widget._setup_style()
            
    def _get_current_width(self) -> int:
        """Get current width based on display mode"""
        width_map = {
            NavigationViewDisplayMode.MINIMAL: self.WIDTH_MINIMAL,
            NavigationViewDisplayMode.COMPACT: self.WIDTH_COMPACT,
            NavigationViewDisplayMode.EXPANDED: self.WIDTH_EXPANDED
        }
        return width_map[self._display_mode]
        
    def _toggle_pane(self):
        """Toggle between expanded and minimal modes"""
        if self._display_mode == NavigationViewDisplayMode.EXPANDED:
            self.set_display_mode(NavigationViewDisplayMode.MINIMAL)
        else:
            self.set_display_mode(NavigationViewDisplayMode.EXPANDED)
            
    def _rebuild_navigation(self):
        """Rebuild the navigation items with current display mode"""
        # Clear existing widgets
        for widget in self._item_widgets.values():
            widget.setParent(None)
        self._item_widgets.clear()
        
        # Rebuild items
        for item in self._navigation_items:
            self._add_navigation_item_widget(item)
            
    def _add_navigation_item_widget(self, item: NavigationItem, level: int = 0):
        """Add a navigation item widget to the layout"""
        widget = FluentNavigationItemWidget(item, self._display_mode, level)
        widget.clicked.connect(self._on_item_clicked)
        
        # Insert before the stretch
        insert_index = self._content_layout.count() - 1
        self._content_layout.insertWidget(insert_index, widget)
        
        self._item_widgets[item.key] = widget
        
        # Add children if present
        if item.children:
            for child_item in item.children:
                self._add_navigation_item_widget(child_item, level + 1)
            
    def _on_item_clicked(self, item_key: str):
        """Handle navigation item clicks"""
        # Update selection
        for key, widget in self._item_widgets.items():
            widget.set_selected(key == item_key)
            
        self._selected_item_key = item_key
        self.selection_changed.emit(item_key)
        
    # Public API
    
    def set_display_mode(self, mode: NavigationViewDisplayMode):
        """Set the display mode with smooth animation"""
        if mode == self._display_mode:
            return
            
        old_width = self._get_current_width()
        self._display_mode = mode
        new_width = self._get_current_width()
        
        # Animate width change
        self._width_animation = QPropertyAnimation(self, QByteArray(b"maximumWidth"))
        self._width_animation.setDuration(250)
        self._width_animation.setStartValue(old_width)
        self._width_animation.setEndValue(new_width)
        self._width_animation.finished.connect(lambda: self.setFixedWidth(new_width))
        self._width_animation.start()
        
        # Rebuild navigation items
        self._rebuild_navigation()
        
        self.display_mode_changed.emit(mode)
        
    def add_navigation_item(self, item: NavigationItem):
        """Add a navigation item to the view"""
        self._navigation_items.append(item)
        self._add_navigation_item_widget(item)
        
    def remove_navigation_item(self, item_key: str):
        """Remove a navigation item by key"""
        # Remove from data
        self._navigation_items = [item for item in self._navigation_items if item.key != item_key]
        
        # Remove widget
        if item_key in self._item_widgets:
            widget = self._item_widgets[item_key]
            widget.setParent(None)
            del self._item_widgets[item_key]
            
    def set_selected_item(self, item_key: str):
        """Set the selected navigation item"""
        self._on_item_clicked(item_key)
        
    def get_selected_item(self) -> str:
        """Get the currently selected item key"""
        return self._selected_item_key
        
    def clear_navigation_items(self):
        """Clear all navigation items"""
        self._navigation_items.clear()
        for widget in self._item_widgets.values():
            widget.setParent(None)
        self._item_widgets.clear()


# Export classes
__all__ = [
    'FluentNavigationView',
    'NavigationItem',
    'NavigationViewDisplayMode',
    'FluentNavigationItemWidget'
]
