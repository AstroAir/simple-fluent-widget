"""
Fluent Design Divider Component
Visual separators and dividers with various styles
"""

from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QLabel, QSizePolicy, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QByteArray
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient, QPaintEvent
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import FluentTransition
from typing import Optional
from enum import Enum


class FluentDivider(QFrame):
    """
    Fluent Design styled divider.
    Can be horizontal or vertical, with various line styles and optional text.
    """

    class Orientation(Enum):
        """Orientation of the divider."""
        HORIZONTAL = Qt.Orientation.Horizontal
        VERTICAL = Qt.Orientation.Vertical

    class Style(Enum):
        """Drawing style of the divider line."""
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
        self._color: Optional[QColor] = None  # Will use theme default if None
        # Margin on each side (top/bottom for horizontal, left/right for vertical)
        self._margin = 16
        self._text = ""
        # Position of text along the divider (0.0 to 1.0)
        self._text_position = 0.5

        self._line_color: QColor = theme_manager.get_color(
            'border') if theme_manager else QColor(Qt.GlobalColor.gray)

        self._setup_ui()

        # Animation setup
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_animation = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        self._opacity_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._opacity_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)

        self._setup_style()  # Initial style setup

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Set up fixed size policies based on orientation and thickness/margin."""
        self.setFrameStyle(QFrame.Shape.NoFrame)

        if self._orientation == self.Orientation.HORIZONTAL:
            # Height is determined by thickness and vertical margins
            self.setFixedHeight(self._thickness + self._margin * 2)
            self.setSizePolicy(QSizePolicy.Policy.Expanding,
                               QSizePolicy.Policy.Fixed)
        else:  # VERTICAL
            # Width is determined by thickness and horizontal margins
            self.setFixedWidth(self._thickness + self._margin * 2)
            self.setSizePolicy(QSizePolicy.Policy.Fixed,
                               QSizePolicy.Policy.Expanding)
        self.updateGeometry()  # Ensure layout is re-evaluated

    def _setup_style(self):
        """Set up the visual style, primarily the line color."""
        if self._color is None:
            self._line_color = theme_manager.get_color(
                'border') if theme_manager else QColor(Qt.GlobalColor.gray)
        else:
            self._line_color = self._color
        self.update()  # Trigger a repaint

    def paintEvent(self, _event: QPaintEvent):
        """
        Custom paint event to draw the divider line and optional text.
        The '_event' parameter is not used directly as the entire component is redrawn.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()

        if self._orientation == self.Orientation.HORIZONTAL:
            self._draw_horizontal_divider(painter, rect)
        else:  # VERTICAL
            self._draw_vertical_divider(painter, rect)

    def _draw_horizontal_divider(self, painter: QPainter, rect):
        """Draw a horizontal divider line, potentially with text."""
        y = rect.height() / 2.0

        x1 = float(rect.left() + self._margin)
        x2 = float(rect.right() - self._margin)

        if self._text:
            font = QFont()
            font.setPointSize(12)
            painter.setFont(font)

            fm = painter.fontMetrics()
            text_width = float(fm.horizontalAdvance(str(self._text)))
            text_height = float(fm.height())

            text_x = x1 + (x2 - x1 - text_width) * self._text_position
            text_y = y + text_height / 2.0 - fm.descent()

            text_segment_margin = 8.0

            if text_x > x1 + text_segment_margin:
                self._draw_line_segment(
                    painter, x1, y, text_x - text_segment_margin, y)

            if text_x + text_width + text_segment_margin < x2:
                self._draw_line_segment(
                    painter, text_x + text_width + text_segment_margin, y, x2, y)

            painter.setPen(QPen(theme_manager.get_color(
                'text_secondary') if theme_manager else QColor(Qt.GlobalColor.darkGray)))
            painter.drawText(int(text_x), int(text_y), str(self._text))
        else:
            self._draw_line_segment(painter, x1, y, x2, y)

    def _draw_vertical_divider(self, painter: QPainter, rect):
        """Draw a vertical divider line."""
        x = rect.width() / 2.0
        y1 = float(rect.top() + self._margin)
        y2 = float(rect.bottom() - self._margin)
        self._draw_line_segment(painter, x, y1, x, y2)

    def _draw_line_segment(self, painter: QPainter, x1: float, y1: float, x2: float, y2: float):
        """Draw a line segment with the configured style and thickness."""
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
            pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(pen)

            gap = 2
            line_thickness = self._thickness

            if self._orientation == self.Orientation.HORIZONTAL:
                offset = (line_thickness + gap) / 2.0
                painter.drawLine(int(x1), int(y1 - offset),
                                 int(x2), int(y2 - offset))
                painter.drawLine(int(x1), int(y1 + offset),
                                 int(x2), int(y2 + offset))
            else:  # VERTICAL
                offset = (line_thickness + gap) / 2.0
                painter.drawLine(int(x1 - offset), int(y1),
                                 int(x2 - offset), int(y2))
                painter.drawLine(int(x1 + offset), int(y1),
                                 int(x2 + offset), int(y2))
            return
        elif self._style == self.Style.GRADIENT:
            gradient = QLinearGradient(x1, y1, x2, y2)

            transparent_color = QColor(self._line_color)
            transparent_color.setAlpha(0)

            gradient.setColorAt(0.0, transparent_color)
            gradient.setColorAt(0.5, self._line_color)
            gradient.setColorAt(1.0, transparent_color)

            pen.setBrush(gradient)
            pen.setStyle(Qt.PenStyle.SolidLine)

        painter.setPen(pen)
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def setOrientation(self, orientation: Orientation):
        """Set the orientation of the divider (HORIZONTAL or VERTICAL)."""
        if self._orientation != orientation:
            self._orientation = orientation
            self._setup_ui()
            self.update()

    def orientation(self) -> Orientation:
        """Get the current orientation of the divider."""
        return self._orientation

    def setDividerStyle(self, style: Style):
        """Set the drawing style of the divider line."""
        if self._style != style:
            self._style = style
            self.update()

    def dividerStyle(self) -> Style:
        """Get the current drawing style of the divider line."""
        return self._style

    def setThickness(self, thickness: int):
        """Set the thickness of the divider line."""
        new_thickness = max(1, thickness)
        if self._thickness != new_thickness:
            self._thickness = new_thickness
            self._setup_ui()
            self.update()

    def thickness(self) -> int:
        """Get the current thickness of the divider line."""
        return self._thickness

    def setColor(self, color: QColor):
        """Set a custom color for the divider line. If None, theme color is used."""
        if self._color != color:
            self._color = color
            self._setup_style()

    def color(self) -> QColor:
        """Get the current custom color of the divider. Returns theme color if custom not set."""
        return self._color if self._color else self._line_color

    def setMargin(self, margin: int):
        """Set the margin around the divider line (space on sides)."""
        new_margin = max(0, margin)
        if self._margin != new_margin:
            self._margin = new_margin
            self._setup_ui()
            self.update()

    def margin(self) -> int:
        """Get the current margin around the divider line."""
        return self._margin

    def setText(self, text: str):
        """Set the text to display on a horizontal divider."""
        if self._text != text:
            self._text = text
            self.update()

    def text(self) -> str:
        """Get the text displayed on the divider."""
        return self._text

    def setTextPosition(self, position: float):
        """
        Set the position of the text along the horizontal divider.
        0.0 for left, 0.5 for center, 1.0 for right.
        """
        new_position = max(0.0, min(1.0, position))
        if self._text_position != new_position:
            self._text_position = new_position
            self.update()

    def textPosition(self) -> float:
        """Get the current position of the text."""
        return self._text_position

    def _on_theme_changed(self, _=None):
        """Handle theme changes by updating style and animating the transition."""
        self._setup_style()

        if self._opacity_animation.state() == QPropertyAnimation.State.Running:
            self._opacity_animation.stop()

        self._opacity_effect.setOpacity(0.0)

        self._opacity_animation.setStartValue(0.0)
        self._opacity_animation.setEndValue(1.0)
        self._opacity_animation.start()


class FluentSeparator(FluentDivider):
    """
    An alias for FluentDivider, can be used for semantic distinction
    if "Separator" is preferred over "Divider" in certain contexts.
    Functionally identical to FluentDivider.
    """
    pass


class FluentSection(QWidget):
    """
    A section component that includes a title, an optional description,
    and a FluentDivider. Useful for grouping content.
    """

    def __init__(self, title: str = "", description: str = "",
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._description = description

        self._title_label: Optional[QLabel] = None
        self._desc_label: Optional[QLabel] = None
        self._divider: FluentDivider = FluentDivider()

        self._setup_ui()

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_animation = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        self._opacity_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._opacity_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)

        self._setup_style()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Initialize and arrange UI elements: title, description, and divider."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 8)
        layout.setSpacing(8)

        if self._title:
            self._title_label = QLabel(self._title)
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setWeight(QFont.Weight.Bold)
            self._title_label.setFont(title_font)
            layout.addWidget(self._title_label)

        if self._description:
            self._desc_label = QLabel(self._description)
            desc_font = QFont()
            desc_font.setPointSize(14)
            self._desc_label.setFont(desc_font)
            layout.addWidget(self._desc_label)

        self._divider.setMargin(0)
        layout.addWidget(self._divider)

        if not self._title and not self._description:
            layout.setContentsMargins(0, 0, 0, 0)

    def _setup_style(self):
        """Apply styles from the theme to the section's elements."""
        if self._title_label:
            title_color = theme_manager.get_color('text_primary').name(
            ) if theme_manager else QColor(Qt.GlobalColor.black).name()
            title_style = f"color: {title_color};"
            self._title_label.setStyleSheet(title_style)

        if self._desc_label:
            desc_color = theme_manager.get_color('text_secondary').name(
            ) if theme_manager else QColor(Qt.GlobalColor.darkGray).name()
            desc_style = f"color: {desc_color};"
            self._desc_label.setStyleSheet(desc_style)

        self.update()

    def setTitle(self, title: str):
        """Set the title text of the section."""
        self._title = title
        if self._title_label:
            self._title_label.setText(title)
            self._title_label.setVisible(bool(title))
        # Consider creating the label if it doesn't exist and title is set
        self.updateGeometry()

    def title(self) -> str:
        """Get the current title text of the section."""
        return self._title

    def setDescription(self, description: str):
        """Set the description text of the section."""
        self._description = description
        if self._desc_label:
            self._desc_label.setText(description)
            self._desc_label.setVisible(bool(description))
        # Consider creating the label if it doesn't exist and description is set
        self.updateGeometry()

    def description(self) -> str:
        """Get the current description text of the section."""
        return self._description

    def divider(self) -> FluentDivider:
        """Get the FluentDivider instance used by this section."""
        return self._divider

    def _on_theme_changed(self, _=None):
        """Handle theme changes by updating styles and animating the section's appearance."""
        self._setup_style()

        if self._opacity_animation.state() == QPropertyAnimation.State.Running:
            self._opacity_animation.stop()

        self._opacity_effect.setOpacity(0.0)

        self._opacity_animation.setStartValue(0.0)
        self._opacity_animation.setEndValue(1.0)
        self._opacity_animation.start()
