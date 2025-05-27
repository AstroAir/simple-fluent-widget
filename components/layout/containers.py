"""
Fluent Design Layout and Container Components
Advanced layout containers and panel components for enterprise applications
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                               QTabWidget, QFrame, QLabel, QPushButton,
                               QStackedWidget, QGraphicsDropShadowEffect)
from PySide6.QtCore import (Qt, Signal, QPropertyAnimation, QEasingCurve,
                            QRect, QByteArray)
from PySide6.QtGui import QFont, QColor
from core.theme import theme_manager
from typing import Optional


class FluentCard(QFrame):
    """Fluent Design style card container"""

    clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._elevated = True
        self._clickable = False
        self._corner_radius = 8
        self._padding = 16
        self._header_text = ""
        self._is_hovered = False

        self.setFrameStyle(QFrame.Shape.NoFrame)
        self._setup_layout()
        self._setup_style()
        self._setup_effects()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_layout(self):
        """Setup layout"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(self._padding, self._padding,
                                            self._padding, self._padding)
        self.main_layout.setSpacing(12)

        # Header area
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)

        self.header_label = QLabel()
        self.header_label.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        self.header_layout.addWidget(self.header_label)
        self.header_layout.addStretch()

        # Content area
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addLayout(self.content_layout)

    def _setup_effects(self):
        """Setup shadow effects"""
        if self._elevated:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 50))
            shadow.setOffset(0, 4)
            self.setGraphicsEffect(shadow)

    def setElevated(self, elevated: bool):
        """Set elevation effect"""
        self._elevated = elevated
        if elevated:
            self._setup_effects()
        else:
            # Clear graphics effect by setting a new empty one
            self.setGraphicsEffect(QGraphicsDropShadowEffect())

    def setClickable(self, clickable: bool):
        """Set clickable state"""
        self._clickable = clickable
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def setHeaderText(self, text: str):
        """Set header text"""
        self._header_text = text
        self.header_label.setText(text)
        self.header_label.setVisible(bool(text))

    def addWidget(self, widget: QWidget):
        """Add widget to content area"""
        self.content_layout.addWidget(widget)

    def addLayout(self, layout):
        """Add layout to content area"""
        self.content_layout.addLayout(layout)

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter"""
        self._is_hovered = True
        self._animate_hover(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave"""
        self._is_hovered = False
        self._animate_hover(False)
        super().leaveEvent(event)

    def _animate_hover(self, hovered: bool):
        """Animate hover effect"""
        if not self._clickable:
            return

        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self._hover_animation.setDuration(200)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        current_rect = self.geometry()
        if hovered:
            # Slight scale up effect
            target_rect = QRect(current_rect.x() - 2, current_rect.y() - 2,
                                current_rect.width() + 4, current_rect.height() + 4)
        else:
            # Return to original size
            target_rect = current_rect

        self._hover_animation.setStartValue(current_rect)
        self._hover_animation.setEndValue(target_rect)
        self._hover_animation.start()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        bg_color = theme.get_color('surface')
        if self._is_hovered and self._clickable:
            bg_color = theme.get_color('accent_light')

        style_sheet = f"""
            FluentCard {{
                background-color: {bg_color.name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: {self._corner_radius}px;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentExpander(QWidget):
    """Fluent Design style expandable container"""

    expanded = Signal(bool)

    def __init__(self, title: str = "Expander", parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._is_expanded = False
        self._animation_duration = 300

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header
        self.header = QPushButton()
        self.header.setCheckable(True)
        self.header.clicked.connect(self._toggle_expansion)
        self.header.setFixedHeight(48)

        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(16, 0, 16, 0)

        # Expand/collapse icon
        self.expand_icon = QLabel("▶")
        self.expand_icon.setFont(QFont("Segoe UI", 10))
        self.expand_icon.setFixedWidth(20)

        # Title
        self.title_label = QLabel(self._title)
        self.title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))

        header_layout.addWidget(self.expand_icon)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # Content container
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(16, 8, 16, 16)

        # Initially hide content
        self.content_container.setMaximumHeight(0)
        self.content_container.setVisible(False)

        self.main_layout.addWidget(self.header)
        self.main_layout.addWidget(self.content_container)

    def addWidget(self, widget: QWidget):
        """Add widget to content area"""
        self.content_layout.addWidget(widget)

    def addLayout(self, layout):
        """Add layout to content area"""
        self.content_layout.addLayout(layout)

    def setExpanded(self, expanded: bool):
        """Set expanded state"""
        if self._is_expanded != expanded:
            self._is_expanded = expanded
            self._animate_expansion()
            self.expanded.emit(expanded)

    def isExpanded(self) -> bool:
        """Check if expanded"""
        return self._is_expanded

    def _toggle_expansion(self):
        """Toggle expansion state"""
        self.setExpanded(not self._is_expanded)

    def _animate_expansion(self):
        """Animate expansion/collapse"""
        # Icon rotation animation (simplified - just change text)
        if self._is_expanded:
            self.expand_icon.setText("▼")
        else:
            self.expand_icon.setText("▶")

        # Content height animation
        self._height_animation = QPropertyAnimation(
            self.content_container, QByteArray(b"maximumHeight"))
        self._height_animation.setDuration(self._animation_duration)
        self._height_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        if self._is_expanded:
            self.content_container.setVisible(True)
            target_height = self.content_container.sizeHint().height()
            self._height_animation.setStartValue(0)
            self._height_animation.setEndValue(target_height)
        else:
            self._height_animation.setStartValue(
                self.content_container.height())
            self._height_animation.setEndValue(0)
            self._height_animation.finished.connect(
                lambda: self.content_container.setVisible(False))

        self._height_animation.start()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentExpander {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                text-align: left;
                color: {theme.get_color('text_primary').name()};
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                background-color: transparent;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentSplitter(QSplitter):
    """Fluent Design style splitter"""

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal,
                 parent: Optional[QWidget] = None):
        super().__init__(orientation, parent)

        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QSplitter::handle {{
                background-color: {theme.get_color('border').name()};
                border: 1px solid {theme.get_color('border').name()};
            }}
            QSplitter::handle:horizontal {{
                width: 6px;
                border-radius: 3px;
                margin: 2px 0;
            }}
            QSplitter::handle:vertical {{
                height: 6px;
                border-radius: 3px;
                margin: 0 2px;
            }}
            QSplitter::handle:hover {{
                background-color: {theme.get_color('primary').name()};
            }}
            QSplitter::handle:pressed {{
                background-color: {theme.get_color('primary').darker(110).name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentTabWidget(QTabWidget):
    """Fluent Design style tab widget"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._tab_position = QTabWidget.TabPosition.North
        self._closable_tabs = False

        self._setup_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def setTabsClosable(self, closable: bool):
        """Set tabs closable"""
        self._closable_tabs = closable
        super().setTabsClosable(closable)

    def setTabPosition(self, position: QTabWidget.TabPosition):
        """Set tab position"""
        self._tab_position = position
        super().setTabPosition(position)
        self._setup_style()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QTabWidget::pane {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
                margin-top: -1px;
            }}
            QTabWidget::tab-bar {{
                alignment: left;
            }}
            QTabBar::tab {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_secondary').name()};
                border: 1px solid {theme.get_color('border').name()};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
                border-bottom-color: {theme.get_color('surface').name()};
                font-weight: 600;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {theme.get_color('accent_light').name()};
                color: {theme.get_color('text_primary').name()};
            }}
            QTabBar::close-button {{
                image: none;
                border: none;
                padding: 2px;
            }}
            QTabBar::close-button:hover {{
                background-color: {theme.get_color('accent_medium').name()};
                border-radius: 4px;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentInfoBar(QFrame):
    """Fluent Design style information bar"""

    class Severity:
        INFO = "info"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"

    closed = Signal()
    action_clicked = Signal(str)

    def __init__(self, title: str, message: str = "",
                 severity: str = Severity.INFO,
                 closable: bool = True,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._message = message
        self._severity = severity
        self._closable = closable
        self._actions = []

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_severity_icon()

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)

        self.title_label = QLabel(self._title)
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))

        if self._message:
            self.message_label = QLabel(self._message)
            self.message_label.setFont(QFont("Segoe UI", 11))
            self.message_label.setWordWrap(True)
            content_layout.addWidget(self.message_label)

        content_layout.addWidget(self.title_label)

        # Actions
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(8)

        layout.addWidget(self.icon_label)
        layout.addLayout(content_layout, 1)
        layout.addLayout(self.actions_layout)

        # Close button
        if self._closable:
            self.close_btn = QPushButton("×")
            self.close_btn.setFixedSize(24, 24)
            self.close_btn.clicked.connect(self._close_info_bar)
            layout.addWidget(self.close_btn)

    def _set_severity_icon(self):
        """Set icon based on severity"""
        icons = {
            self.Severity.INFO: "ℹ",
            self.Severity.SUCCESS: "✓",
            self.Severity.WARNING: "⚠",
            self.Severity.ERROR: "✕"
        }

        icon_text = icons.get(self._severity, "ℹ")
        self.icon_label.setText(icon_text)
        self.icon_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))

    def addActionButton(self, action_name: str, action_text: str):
        """Add action button (renamed to avoid conflict with QWidget.addAction)"""
        action_btn = QPushButton(action_text)
        action_btn.clicked.connect(
            lambda: self.action_clicked.emit(action_name))

        self._actions.append((action_name, action_btn))
        self.actions_layout.addWidget(action_btn)

    def _close_info_bar(self):
        """Close info bar"""
        self.closed.emit()
        self.deleteLater()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        # Severity colors
        severity_colors = {
            self.Severity.INFO: theme.get_color('primary'),
            self.Severity.SUCCESS: QColor("#28a745"),
            self.Severity.WARNING: QColor("#ffc107"),
            self.Severity.ERROR: QColor("#dc3545")
        }

        accent_color = severity_colors.get(
            self._severity, theme.get_color('primary'))

        style_sheet = f"""
            FluentInfoBar {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {accent_color.name()};
                border-left: 4px solid {accent_color.name()};
                border-radius: 8px;
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                background-color: transparent;
                border: none;
            }}
            QPushButton {{
                background-color: {accent_color.name()};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {accent_color.darker(110).name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentPivot(QWidget):
    """Fluent Design style pivot (horizontal tab navigation)"""

    selection_changed = Signal(int)  # Selected index

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._items = []
        self._selected_index = 0
        self._content_widget = None

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header with pivot items
        self.header = QFrame()
        self.header.setFixedHeight(48)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(16, 0, 16, 0)
        self.header_layout.setSpacing(0)

        self.header_layout.addStretch()

        # Content area
        self.content_stack = QStackedWidget()

        self.main_layout.addWidget(self.header)
        self.main_layout.addWidget(self.content_stack, 1)

    def addItem(self, text: str, widget: Optional[QWidget] = None) -> int:
        """Add pivot item"""
        index = len(self._items)

        # Create pivot button
        pivot_btn = QPushButton(text)
        pivot_btn.setCheckable(True)
        pivot_btn.clicked.connect(lambda: self._select_item(index))

        # Add to layout (before stretch)
        self.header_layout.insertWidget(
            self.header_layout.count() - 1, pivot_btn)

        # Store item info
        self._items.append({
            'text': text,
            'button': pivot_btn,
            'widget': widget
        })

        # Add widget to stack if provided
        if widget:
            self.content_stack.addWidget(widget)

        # Select first item
        if index == 0:
            self._select_item(0)

        return index

    def setCurrentIndex(self, index: int):
        """Set current selected index"""
        if 0 <= index < len(self._items):
            self._select_item(index)

    def getCurrentIndex(self) -> int:
        """Get current selected index"""
        return self._selected_index

    def _select_item(self, index: int):
        """Select pivot item"""
        if index == self._selected_index:
            return

        # Update button states
        for i, item in enumerate(self._items):
            item['button'].setChecked(i == index)

        # Switch content
        if self._items[index]['widget']:
            self.content_stack.setCurrentWidget(self._items[index]['widget'])

        self._selected_index = index
        self.selection_changed.emit(index)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
            QPushButton {{
                background-color: transparent;
                color: {theme.get_color('text_secondary').name()};
                border: none;
                border-bottom: 3px solid transparent;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:checked {{
                color: {theme.get_color('primary').name()};
                border-bottom: 3px solid {theme.get_color('primary').name()};
                font-weight: 600;
            }}
            QPushButton:hover:!checked {{
                color: {theme.get_color('text_primary').name()};
                background-color: {theme.get_color('accent_light').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
