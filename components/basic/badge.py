"""
Fluent Design Style Badge and Tag Components
Badges, tags and status indicators for informational displays
"""

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, Signal, QSize, Property
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPaintEvent, QPainterPath
from core.theme import theme_manager
from typing import Optional


class FluentBadge(QWidget):
    """Fluent Design Style Badge
    
    Features:
    - Multiple badge types (default, info, success, warning, error)
    - Customizable content (text or count)
    - Dot mode for simple status indication
    """
    
    class BadgeType:
        DEFAULT = "default"
        INFO = "info"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"
    
    def __init__(self, parent: Optional[QWidget] = None, 
                 badge_type: str = BadgeType.DEFAULT,
                 text: str = "", dot: bool = False):
        super().__init__(parent)
        
        self._badge_type = badge_type
        self._text = text
        self._dot_mode = dot
        
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 2, 4, 2)
        
        self._label = QLabel(text)
        self._label.setAlignment(Qt.AlignCenter)
        
        # Set font for label
        font = self._label.font()
        font.setPointSize(9)
        self._label.setFont(font)
        
        self._layout.addWidget(self._label)
        
        # Set size policy
        if dot:
            self.setFixedSize(8, 8)
            self._label.setVisible(False)
            self._layout.setContentsMargins(0, 0, 0, 0)
        else:
            self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            self.setMinimumHeight(20)
            
        self._apply_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _apply_style(self):
        """Apply badge style based on type"""
        theme = theme_manager
        style_sheet = ""
        
        # Define colors based on badge type
        if self._badge_type == self.BadgeType.DEFAULT:
            bg_color = theme.get_color('border').name()
            text_color = theme.get_color('text_primary').name()
        elif self._badge_type == self.BadgeType.INFO:
            bg_color = theme.get_color('primary').name()
            text_color = "white" if theme.current_mode.name == "LIGHT" else theme.get_color('background').name()
        elif self._badge_type == self.BadgeType.SUCCESS:
            bg_color = "#0f7b0f"  # Green
            text_color = "white"
        elif self._badge_type == self.BadgeType.WARNING:
            bg_color = "#ffc83d"  # Amber
            text_color = theme.get_color('text_primary').name()
        elif self._badge_type == self.BadgeType.ERROR:
            bg_color = "#e81123"  # Red
            text_color = "white"
        
        if self._dot_mode:
            style_sheet = f"""
                FluentBadge {{
                    background-color: {bg_color};
                    border-radius: 4px;
                }}
            """
        else:
            style_sheet = f"""
                FluentBadge {{
                    background-color: {bg_color};
                    border-radius: 10px;
                    padding: 2px 8px;
                }}
                QLabel {{
                    color: {text_color};
                    background-color: transparent;
                    border: none;
                }}
            """
        
        self.setStyleSheet(style_sheet)
    
    def _on_theme_changed(self):
        """Handle theme changes"""
        self._apply_style()
    
    def setText(self, text: str):
        """Set badge text"""
        self._text = text
        self._label.setText(text)
        
        # Adjust size for number-only content
        try:
            value = int(text)
            if value < 10:
                self.setFixedWidth(20)
            elif value < 100:
                self.setFixedWidth(28)
            else:
                self.setMinimumWidth(32)
        except ValueError:
            self.setMinimumWidth(10)
            self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
    
    def setBadgeType(self, badge_type: str):
        """Set badge type"""
        self._badge_type = badge_type
        self._apply_style()
    
    def setDotMode(self, dot: bool):
        """Set dot mode"""
        self._dot_mode = dot
        if dot:
            self.setFixedSize(8, 8)
            self._label.setVisible(False)
            self._layout.setContentsMargins(0, 0, 0, 0)
        else:
            self._label.setVisible(True)
            self._layout.setContentsMargins(4, 2, 4, 2)
            self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            self.setMinimumHeight(20)
        
        self._apply_style()


class FluentTag(QWidget):
    """Fluent Design Style Tag
    
    Features:
    - Multiple tag variants (default, outline, filled)
    - Customizable colors
    - Optional close button
    - Click event support
    """
    
    clicked = Signal()
    closed = Signal()
    
    class TagVariant:
        DEFAULT = "default"
        OUTLINE = "outline"
        FILLED = "filled"
    
    def __init__(self, text: str = "", parent: Optional[QWidget] = None, 
                 variant: str = TagVariant.DEFAULT, closable: bool = False):
        super().__init__(parent)
        
        self._text = text
        self._variant = variant
        self._closable = closable
        self._color = None  # Custom color if set
        
        # Setup UI
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 4, 8, 4)
        self._layout.setSpacing(4)
        
        self._label = QLabel(text)
        
        # Set font for label
        font = self._label.font()
        font.setPointSize(10)
        self._label.setFont(font)
        
        self._layout.addWidget(self._label)
        
        if closable:
            self._close_btn = QPushButton()
            self._close_btn.setFixedSize(16, 16)
            self._close_btn.clicked.connect(self._on_close_clicked)
            self._close_btn.setCursor(Qt.PointingHandCursor)
            self._layout.addWidget(self._close_btn)
        
        # Set cursor
        self.setCursor(Qt.PointingHandCursor)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setMinimumHeight(26)
        
        self._apply_style()
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _apply_style(self):
        """Apply tag style based on variant"""
        theme = theme_manager
        style_sheet = ""
        
        # Get colors
        if self._color:
            primary_color = self._color
        else:
            primary_color = theme.get_color('primary').name()
        
        text_color = theme.get_color('text_primary').name()
        bg_color = theme.get_color('surface').name()
        
        # Define style based on variant
        if self._variant == self.TagVariant.DEFAULT:
            style_sheet = f"""
                FluentTag {{
                    background-color: {bg_color};
                    border: 1px solid {theme.get_color('border').name()};
                    border-radius: 13px;
                }}
                QLabel {{
                    color: {text_color};
                    background-color: transparent;
                    border: none;
                }}
            """
        elif self._variant == self.TagVariant.OUTLINE:
            style_sheet = f"""
                FluentTag {{
                    background-color: transparent;
                    border: 1px solid {primary_color};
                    border-radius: 13px;
                }}
                QLabel {{
                    color: {primary_color};
                    background-color: transparent;
                    border: none;
                }}
            """
        elif self._variant == self.TagVariant.FILLED:
            text_color = "white" if theme.current_mode.name == "LIGHT" else theme.get_color('background').name()
            style_sheet = f"""
                FluentTag {{
                    background-color: {primary_color};
                    border: none;
                    border-radius: 13px;
                }}
                QLabel {{
                    color: {text_color};
                    background-color: transparent;
                    border: none;
                }}
            """
        
        # Add close button style
        if self._closable:
            close_icon_color = text_color
            if self._variant == self.TagVariant.FILLED:
                close_icon_color = text_color
            elif self._variant == self.TagVariant.OUTLINE:
                close_icon_color = primary_color
            
            style_sheet += f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 8px;
                    color: {close_icon_color};
                    font-family: "Segoe UI Symbol";
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 0, 0, 0.1);
                }}
            """
        
        self.setStyleSheet(style_sheet)
        
        # Set close button text if exists
        if self._closable:
            self._close_btn.setText("✕")
    
    def _on_theme_changed(self):
        """Handle theme changes"""
        self._apply_style()
    
    def _on_close_clicked(self):
        """Handle close button click"""
        self.closed.emit()
        self.hide()
    
    def setText(self, text: str):
        """Set tag text"""
        self._text = text
        self._label.setText(text)
    
    def setColor(self, color: str):
        """Set custom tag color"""
        self._color = color
        self._apply_style()
    
    def setVariant(self, variant: str):
        """Set tag variant"""
        self._variant = variant
        self._apply_style()
    
    def mousePressEvent(self, event):
        """Handle mouse press event"""
        super().mousePressEvent(event)
        self.clicked.emit()


from PySide6.QtWidgets import QPushButton
