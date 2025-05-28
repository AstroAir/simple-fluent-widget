"""
Fluent Design Divider Component
Visual separators and dividers with various styles
"""

from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient
from core.theme import theme_manager
from typing import Optional
from enum import Enum


class FluentDivider(QFrame):
    """Fluent Design divider component"""

    class Orientation(Enum):
        HORIZONTAL = Qt.Orientation.Horizontal
        VERTICAL = Qt.Orientation.Vertical

    class Style(Enum):
        SOLID = "solid"
        DASHED = "dashed"
        DOTTED = "dotted"
        GRADIENT = "gradient"
        DOUBLE = "double"

    def __init__(self, orientation: Orientation = Orientation.HORIZONTAL,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._orientation = orientation
        self._style = self.Style.SOLID
        self._thickness = 1
        self._color = None  # Will use theme default
        self._margin = 16
        self._text = ""
        self._text_position = 0.5  # 0.0 to 1.0

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setFrameStyle(QFrame.Shape.NoFrame)

        if self._orientation == self.Orientation.HORIZONTAL:
            self.setFixedHeight(self._thickness + self._margin * 2)
            self.setSizePolicy(QSizePolicy.Policy.Expanding,
                               QSizePolicy.Policy.Fixed)
        else:
            self.setFixedWidth(self._thickness + self._margin * 2)
            self.setSizePolicy(QSizePolicy.Policy.Fixed,
                               QSizePolicy.Policy.Expanding)

    def _setup_style(self):
        """Setup style"""
        if self._color is None:
            self._line_color = theme_manager.get_color('border')
        else:
            self._line_color = self._color

        self.update()

    def paintEvent(self, event):
        """Custom paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()

        if self._orientation == self.Orientation.HORIZONTAL:
            self._draw_horizontal_divider(painter, rect)
        else:
            self._draw_vertical_divider(painter, rect)

    def _draw_horizontal_divider(self, painter: QPainter, rect):
        """Draw horizontal divider"""
        y = rect.center().y()
        x1 = rect.left() + self._margin
        x2 = rect.right() - self._margin

        # Draw text if present
        if self._text:
            font = QFont()
            font.setPointSize(12)
            painter.setFont(font)

            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(self._text)
            text_height = fm.height()

            # Calculate text position
            text_x = x1 + (x2 - x1 - text_width) * self._text_position
            text_y = y + text_height // 4

            # Draw line segments around text
            text_margin = 8
            if text_x > x1:
                self._draw_line_segment(
                    painter, x1, y, text_x - text_margin, y)
            if text_x + text_width < x2:
                self._draw_line_segment(
                    painter, text_x + text_width + text_margin, y, x2, y)

            # Draw text
            painter.setPen(QPen(theme_manager.get_color('text_secondary')))
            painter.drawText(int(text_x), int(text_y), self._text)
        else:
            # Draw full line
            self._draw_line_segment(painter, x1, y, x2, y)

    def _draw_vertical_divider(self, painter: QPainter, rect):
        """Draw vertical divider"""
        x = rect.center().x()
        y1 = rect.top() + self._margin
        y2 = rect.bottom() - self._margin

        # For vertical dividers, text is not commonly used
        self._draw_line_segment(painter, x, y1, x, y2)

    def _draw_line_segment(self, painter: QPainter, x1: float, y1: float, x2: float, y2: float):
        """Draw line segment with specified style"""
        pen = QPen()
        pen.setWidth(self._thickness)
        pen.setColor(self._line_color)

        if self._style == self.Style.SOLID:
            pen.setStyle(Qt.PenStyle.SolidLine)
        elif self._style == self.Style.DASHED:
            pen.setStyle(Qt.PenStyle.DashLine)
        elif self._style == self.Style.DOTTED:
            pen.setStyle(Qt.PenStyle.DotLine)
        elif self._style == self.Style.DOUBLE:
            # Draw two parallel lines
            pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(pen)

            if self._orientation == self.Orientation.HORIZONTAL:
                offset = self._thickness + 2
                painter.drawLine(int(x1), int(y1 - offset//2),
                                 int(x2), int(y2 - offset//2))
                painter.drawLine(int(x1), int(y1 + offset//2),
                                 int(x2), int(y2 + offset//2))
            else:
                offset = self._thickness + 2
                painter.drawLine(int(x1 - offset//2), int(y1),
                                 int(x2 - offset//2), int(y2))
                painter.drawLine(int(x1 + offset//2), int(y1),
                                 int(x2 + offset//2), int(y2))
            return
        elif self._style == self.Style.GRADIENT:
            # Create gradient brush
            gradient = QLinearGradient(x1, y1, x2, y2)

            transparent = QColor(self._line_color)
            transparent.setAlpha(0)

            gradient.setColorAt(0.0, transparent)
            gradient.setColorAt(0.5, self._line_color)
            gradient.setColorAt(1.0, transparent)

            pen.setBrush(gradient)

        painter.setPen(pen)
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def setOrientation(self, orientation: Orientation):
        """Set divider orientation"""
        if self._orientation != orientation:
            self._orientation = orientation
            self._setup_ui()
            self.update()

    def orientation(self) -> Orientation:
        """Get divider orientation"""
        return self._orientation

    def setDividerStyle(self, style: Style):
        """Set divider style"""
        self._style = style
        self.update()

    def dividerStyle(self) -> Style:
        """Get divider style"""
        return self._style

    def setThickness(self, thickness: int):
        """Set divider thickness"""
        self._thickness = max(1, thickness)
        self._setup_ui()
        self.update()

    def thickness(self) -> int:
        """Get divider thickness"""
        return self._thickness

    def setColor(self, color: QColor):
        """Set divider color"""
        self._color = color
        self._setup_style()

    def color(self) -> QColor:
        """Get divider color"""
        return self._color if self._color else self._line_color

    def setMargin(self, margin: int):
        """Set divider margin"""
        self._margin = max(0, margin)
        self._setup_ui()
        self.update()

    def margin(self) -> int:
        """Get divider margin"""
        return self._margin

    def setText(self, text: str):
        """Set divider text (horizontal only)"""
        self._text = text
        self.update()

    def text(self) -> str:
        """Get divider text"""
        return self._text

    def setTextPosition(self, position: float):
        """Set text position (0.0 = left/top, 1.0 = right/bottom)"""
        self._text_position = max(0.0, min(1.0, position))
        self.update()

    def textPosition(self) -> float:
        """Get text position"""
        return self._text_position

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentSeparator(FluentDivider):
    """Alias for FluentDivider for convenience"""
    pass


class FluentSection(QWidget):
    """Section divider with title and optional description"""

    def __init__(self, title: str = "", description: str = "",
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._description = description

        self._setup_ui()
        self._setup_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(8)

        # Title
        if self._title:
            self._title_label = QLabel(self._title)
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setWeight(QFont.Weight.Bold)
            self._title_label.setFont(title_font)
            layout.addWidget(self._title_label)

        # Description
        if self._description:
            self._desc_label = QLabel(self._description)
            desc_font = QFont()
            desc_font.setPointSize(14)
            self._desc_label.setFont(desc_font)
            layout.addWidget(self._desc_label)

        # Divider
        self._divider = FluentDivider()
        self._divider.setMargin(0)
        layout.addWidget(self._divider)

    def _setup_style(self):
        """Setup style"""
        style_sheet = f"""
            FluentSection {{
                background-color: transparent;
            }}
        """

        self.setStyleSheet(style_sheet)

        if hasattr(self, '_title_label'):
            title_style = f"color: {theme_manager.get_color('text_primary').name()};"
            self._title_label.setStyleSheet(title_style)

        if hasattr(self, '_desc_label'):
            desc_style = f"color: {theme_manager.get_color('text_secondary').name()};"
            self._desc_label.setStyleSheet(desc_style)

    def setTitle(self, title: str):
        """Set section title"""
        self._title = title
        if hasattr(self, '_title_label'):
            self._title_label.setText(title)

    def title(self) -> str:
        """Get section title"""
        return self._title

    def setDescription(self, description: str):
        """Set section description"""
        self._description = description
        if hasattr(self, '_desc_label'):
            self._desc_label.setText(description)

    def description(self) -> str:
        """Get section description"""
        return self._description

    def divider(self) -> FluentDivider:
        """Get the divider component"""
        return self._divider

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
