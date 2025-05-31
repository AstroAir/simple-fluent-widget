"""
Fluent Design Divider Component
Visual separators and dividers with various styles
Optimized for performance and smooth animations
"""

from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QLabel, QSizePolicy, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QByteArray, QTimer, QEasingCurve, QParallelAnimationGroup
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient, QPaintEvent, QFontMetrics
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import FluentTransition
from typing import Optional, Callable
from enum import Enum


class FluentDivider(QFrame):
    """
    Fluent Design styled divider with optimized performance and smooth animations.
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
        
        # Performance optimization: cache theme colors
        self._cached_line_color: QColor = QColor()
        self._cached_text_color: QColor = QColor()
        self._theme_cache_valid = False
        
        # Animation state management
        self._is_animating = False
        self._animation_queue: list = []

        self._setup_ui()
        self._setup_animations()
        self._update_theme_cache()

        # Connect theme changes with debouncing for performance
        if theme_manager:
            self._theme_timer = QTimer()
            self._theme_timer.setSingleShot(True)
            self._theme_timer.timeout.connect(self._on_theme_changed_debounced)
            theme_manager.theme_changed.connect(self._on_theme_changed_request)

    def _setup_ui(self):
        """Set up fixed size policies based on orientation and thickness/margin."""
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)  # Performance optimization

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

    def _setup_animations(self):
        """Set up optimized animation system with parallel animations."""
        # Opacity animation for theme changes
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        
        self._opacity_animation = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        self._opacity_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._opacity_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
        
        # Color transition animation (using custom property)
        self._color_transition = QPropertyAnimation(self, QByteArray(b"_transition_progress"))
        self._color_transition.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._color_transition.setEasingCurve(FluentTransition.EASE_SPRING)
        
        # Animation group for parallel animations
        self._animation_group = QParallelAnimationGroup()
        self._animation_group.addAnimation(self._opacity_animation)
        self._animation_group.addAnimation(self._color_transition)
        self._animation_group.finished.connect(self._on_animation_finished)
        
        # Initialize transition properties
        self._transition_progress_value = 1.0
        self._start_color = QColor()
        self._end_color = QColor()

    def _update_theme_cache(self):
        """Update cached theme colors for better performance."""
        if not theme_manager:
            self._cached_line_color = QColor(Qt.GlobalColor.gray)
            self._cached_text_color = QColor(Qt.GlobalColor.darkGray)
        else:
            if self._color is None:
                self._cached_line_color = theme_manager.get_color('border')
            else:
                self._cached_line_color = self._color
            self._cached_text_color = theme_manager.get_color('text_secondary')
        
        self._theme_cache_valid = True

    def _invalidate_theme_cache(self):
        """Mark theme cache as invalid."""
        self._theme_cache_valid = False

    def _get_transition_progress(self) -> float:
        """Get transition progress for color animation."""
        return getattr(self, '_transition_progress_value', 1.0)
    
    def _set_transition_progress(self, value: float):
        """Set transition progress and trigger repaint."""
        self._transition_progress_value = value
        if hasattr(self, '_start_color') and hasattr(self, '_end_color'):
            # Interpolate colors based on progress
            factor = value
            r = int(self._start_color.red() + (self._end_color.red() - self._start_color.red()) * factor)
            g = int(self._start_color.green() + (self._end_color.green() - self._start_color.green()) * factor)
            b = int(self._start_color.blue() + (self._end_color.blue() - self._start_color.blue()) * factor)
            a = int(self._start_color.alpha() + (self._end_color.alpha() - self._start_color.alpha()) * factor)
            self._cached_line_color = QColor(r, g, b, a)
            self.update()

    # Property for animation
    _transition_progress = property(_get_transition_progress, _set_transition_progress)

    def paintEvent(self, _event: QPaintEvent):
        """
        Optimized paint event to draw the divider line and optional text.
        """
        if not self._theme_cache_valid:
            self._update_theme_cache()
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

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
            # Use cached font metrics for better performance
            if not hasattr(self, '_cached_font_metrics'):
                font = QFont()
                font.setPointSize(12)
                font.setWeight(QFont.Weight.Medium)  # Better theme consistency
                painter.setFont(font)
                self._cached_font_metrics = QFontMetrics(font)
                self._cached_font = font
            else:
                painter.setFont(self._cached_font)

            fm = self._cached_font_metrics
            text_width = float(fm.horizontalAdvance(str(self._text)))
            text_height = float(fm.height())

            text_x = x1 + (x2 - x1 - text_width) * self._text_position
            text_y = y + text_height / 2.0 - fm.descent()

            text_segment_margin = 8.0

            # Draw line segments on both sides of text
            if text_x > x1 + text_segment_margin:
                self._draw_line_segment(
                    painter, x1, y, text_x - text_segment_margin, y)

            if text_x + text_width + text_segment_margin < x2:
                self._draw_line_segment(
                    painter, text_x + text_width + text_segment_margin, y, x2, y)

            # Draw text with cached color
            painter.setPen(QPen(self._cached_text_color))
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
        """Draw a line segment with the configured style and thickness - optimized version."""
        pen = QPen()
        pen.setWidth(self._thickness)
        pen.setColor(self._cached_line_color)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)  # Better visual appearance

        if self._style == self.Style.SOLID:
            pen.setStyle(Qt.PenStyle.SolidLine)
        elif self._style == self.Style.DASHED:
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setDashPattern([4, 2])  # Custom dash pattern for better appearance
        elif self._style == self.Style.DOTTED:
            pen.setStyle(Qt.PenStyle.DotLine)
        elif self._style == self.Style.DOUBLE:
            pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(pen)

            gap = max(2, self._thickness // 2)  # Adaptive gap based on thickness
            line_thickness = max(1, self._thickness // 2)  # Adaptive line thickness

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

            # Improved gradient with theme-aware transparency
            start_color = QColor(self._cached_line_color)
            start_color.setAlpha(0)
            mid_color = QColor(self._cached_line_color)
            mid_color.setAlpha(180)  # Better visibility
            end_color = QColor(self._cached_line_color)
            end_color.setAlpha(0)

            gradient.setColorAt(0.0, start_color)
            gradient.setColorAt(0.5, mid_color)
            gradient.setColorAt(1.0, end_color)

            pen.setBrush(gradient)
            pen.setStyle(Qt.PenStyle.SolidLine)

        painter.setPen(pen)
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def setOrientation(self, orientation: Orientation):
        """Set the orientation of the divider (HORIZONTAL or VERTICAL) with smooth animation."""
        if self._orientation != orientation:
            old_orientation = self._orientation
            self._orientation = orientation
            
            # Animate the orientation change
            self._animate_orientation_change(old_orientation, orientation)
            
            self._setup_ui()

    def _animate_orientation_change(self, old_orientation: Orientation, new_orientation: Orientation):
        """Animate the orientation change with a smooth transition."""
        if self._is_animating:
            return
            
        self._is_animating = True
        
        # Create fade out, change, fade in sequence
        self._opacity_effect.setOpacity(1.0)
        
        fade_out = QPropertyAnimation(self._opacity_effect, QByteArray(b"opacity"))
        fade_out.setDuration(FluentAnimation.DURATION_FAST)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.3)
        fade_out.setEasingCurve(FluentTransition.EASE_SMOOTH)
        
        fade_in = QPropertyAnimation(self._opacity_effect, QByteArray(b"opacity"))
        fade_in.setDuration(FluentAnimation.DURATION_FAST)
        fade_in.setStartValue(0.3)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(FluentTransition.EASE_SMOOTH)
        
        # Connect animations
        fade_out.finished.connect(lambda: self._delayed_fade_in(fade_in))
        fade_out.start()

    def _delayed_fade_in(self, fade_in_animation: QPropertyAnimation):
        """Execute the fade in part of orientation change."""
        self.update()  # Trigger repaint with new orientation
        fade_in_animation.finished.connect(self._on_animation_finished)
        fade_in_animation.start()

    def orientation(self) -> Orientation:
        """Get the current orientation of the divider."""
        return self._orientation

    def setDividerStyle(self, style: Style):
        """Set the drawing style of the divider line with smooth transition."""
        if self._style != style:
            old_style = self._style
            self._style = style
            self._animate_style_change(old_style, style)

    def _animate_style_change(self, old_style: Style, new_style: Style):
        """Animate style changes with a subtle effect."""
        # Animate opacity for style change
        if not self._is_animating:
            self._is_animating = True
            self._opacity_effect.setOpacity(0.7)
            
            style_animation = QPropertyAnimation(self._opacity_effect, QByteArray(b"opacity"))
            style_animation.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
            style_animation.setStartValue(0.7)
            style_animation.setEndValue(1.0)
            style_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
            style_animation.finished.connect(self._on_animation_finished)
            style_animation.start()
        
        self.update()

    def dividerStyle(self) -> Style:
        """Get the current drawing style of the divider line."""
        return self._style

    def setThickness(self, thickness: int):
        """Set the thickness of the divider line with smooth animation."""
        new_thickness = max(1, thickness)
        if self._thickness != new_thickness:
            old_thickness = self._thickness
            self._thickness = new_thickness
            self._animate_thickness_change(old_thickness, new_thickness)
            self._setup_ui()

    def _animate_thickness_change(self, old_thickness: int, new_thickness: int):
        """Animate thickness changes."""
        # Create a scaling effect for thickness change
        if not self._is_animating:
            self._is_animating = True
            
            # Subtle pulse effect
            pulse_animation = QPropertyAnimation(self._opacity_effect, QByteArray(b"opacity"))
            pulse_animation.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
            pulse_animation.setStartValue(1.0)
            pulse_animation.setKeyValueAt(0.5, 0.8)
            pulse_animation.setEndValue(1.0)
            pulse_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
            pulse_animation.finished.connect(self._on_animation_finished)
            pulse_animation.start()

    def thickness(self) -> int:
        """Get the current thickness of the divider line."""
        return self._thickness

    def setColor(self, color: QColor):
        """Set a custom color for the divider line with smooth color transition."""
        if self._color != color:
            old_color = self._cached_line_color
            self._color = color
            self._animate_color_change(old_color, color if color else theme_manager.get_color('border'))

    def _animate_color_change(self, old_color: QColor, new_color: QColor):
        """Animate color changes with smooth transition."""
        if self._is_animating:
            return
            
        self._is_animating = True
        self._start_color = old_color
        self._end_color = new_color
        
        self._color_transition.setStartValue(0.0)
        self._color_transition.setEndValue(1.0)
        self._color_transition.finished.connect(self._on_animation_finished)
        self._color_transition.start()

    def color(self) -> QColor:
        """Get the current custom color of the divider. Returns theme color if custom not set."""
        return self._color if self._color else self._cached_line_color

    def setMargin(self, margin: int):
        """Set the margin around the divider line (space on sides) with animation."""
        new_margin = max(0, margin)
        if self._margin != new_margin:
            self._margin = new_margin
            self._setup_ui()
            # Subtle resize animation
            self._animate_margin_change()

    def _animate_margin_change(self):
        """Animate margin changes."""
        if not self._is_animating:
            self._is_animating = True
            
            # Quick fade effect for margin change
            margin_animation = QPropertyAnimation(self._opacity_effect, QByteArray(b"opacity"))
            margin_animation.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
            margin_animation.setStartValue(0.9)
            margin_animation.setEndValue(1.0)
            margin_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
            margin_animation.finished.connect(self._on_animation_finished)
            margin_animation.start()

    def margin(self) -> int:
        """Get the current margin around the divider line."""
        return self._margin

    def setText(self, text: str):
        """Set the text to display on a horizontal divider with fade transition."""
        if self._text != text:
            old_text = self._text
            self._text = text
            self._animate_text_change(old_text, text)

    def _animate_text_change(self, old_text: str, new_text: str):
        """Animate text changes."""
        if not self._is_animating:
            self._is_animating = True
            
            # Invalidate font cache when text changes
            if hasattr(self, '_cached_font_metrics'):
                delattr(self, '_cached_font_metrics')
            
            # Text change animation
            text_animation = QPropertyAnimation(self._opacity_effect, QByteArray(b"opacity"))
            text_animation.setDuration(FluentAnimation.DURATION_FAST)
            text_animation.setStartValue(0.7)
            text_animation.setEndValue(1.0)
            text_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
            text_animation.finished.connect(self._on_animation_finished)
            text_animation.start()

    def text(self) -> str:
        """Get the text displayed on the divider."""
        return self._text

    def setTextPosition(self, position: float):
        """
        Set the position of the text along the horizontal divider with smooth transition.
        0.0 for left, 0.5 for center, 1.0 for right.
        """
        new_position = max(0.0, min(1.0, position))
        if self._text_position != new_position:
            self._text_position = new_position
            self._animate_text_position_change()

    def _animate_text_position_change(self):
        """Animate text position changes."""
        if not self._is_animating:
            self._is_animating = True
            
            # Smooth slide effect for text position
            position_animation = QPropertyAnimation(self._opacity_effect, QByteArray(b"opacity"))
            position_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
            position_animation.setStartValue(0.8)
            position_animation.setEndValue(1.0)
            position_animation.setEasingCurve(FluentTransition.EASE_SPRING)
            position_animation.finished.connect(self._on_animation_finished)
            position_animation.start()

    def textPosition(self) -> float:
        """Get the current position of the text."""
        return self._text_position

    def _on_theme_changed_request(self):
        """Handle theme change request with debouncing."""
        if hasattr(self, '_theme_timer'):
            self._theme_timer.start(50)  # 50ms debounce

    def _on_theme_changed_debounced(self):
        """Handle debounced theme changes by updating style and animating the transition."""
        self._invalidate_theme_cache()
        
        if not self._is_animating:
            self._is_animating = True
            
            # Store old color for transition
            old_color = self._cached_line_color
            self._update_theme_cache()
            new_color = self._cached_line_color
            
            # Animate theme transition
            if old_color != new_color:
                self._animate_color_change(old_color, new_color)
            else:
                # Just a subtle pulse for theme change
                theme_animation = QPropertyAnimation(self._opacity_effect, QByteArray(b"opacity"))
                theme_animation.setDuration(FluentAnimation.DURATION_FAST)
                theme_animation.setStartValue(0.7)
                theme_animation.setEndValue(1.0)
                theme_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
                theme_animation.finished.connect(self._on_animation_finished)
                theme_animation.start()

    def _on_animation_finished(self):
        """Handle animation completion."""
        self._is_animating = False
        
        # Process any queued animations
        if self._animation_queue:
            next_animation = self._animation_queue.pop(0)
            next_animation()

    def animateIn(self, direction: str = "fade", callback: Optional[Callable] = None):
        """Animate the divider appearing with specified direction."""
        if direction == "fade":
            self._opacity_effect.setOpacity(0.0)
            animation = QPropertyAnimation(self._opacity_effect, QByteArray(b"opacity"))
            animation.setDuration(FluentAnimation.DURATION_MEDIUM)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
            
            if callback:
                animation.finished.connect(callback)
            
            animation.start()
            return animation
        
        return None

    def animateOut(self, direction: str = "fade", callback: Optional[Callable] = None):
        """Animate the divider disappearing with specified direction."""
        if direction == "fade":
            animation = QPropertyAnimation(self._opacity_effect, QByteArray(b"opacity"))
            animation.setDuration(FluentAnimation.DURATION_MEDIUM)
            animation.setStartValue(1.0)
            animation.setEndValue(0.0)
            animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
            
            if callback:
                animation.finished.connect(callback)
            
            animation.start()
            return animation
        
        return None


class FluentSeparator(FluentDivider):
    """
    An alias for FluentDivider, can be used for semantic distinction
    if "Separator" is preferred over "Divider" in certain contexts.
    Functionally identical to FluentDivider but with optimizations.
    """
    pass


class FluentSection(QWidget):
    """
    A section component that includes a title, an optional description,
    and a FluentDivider. Useful for grouping content with enhanced animations.
    """

    def __init__(self, title: str = "", description: str = "",
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._description = description
        self._is_animating = False

        self._title_label: Optional[QLabel] = None
        self._desc_label: Optional[QLabel] = None
        self._divider: FluentDivider = FluentDivider()

        self._setup_ui()
        self._setup_animations()
        self._setup_style()

        if theme_manager:
            self._theme_timer = QTimer()
            self._theme_timer.setSingleShot(True)
            self._theme_timer.timeout.connect(self._on_theme_changed_debounced)
            theme_manager.theme_changed.connect(self._on_theme_changed_request)

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

    def _setup_animations(self):
        """Set up enhanced animation system for section."""
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        
        self._opacity_animation = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        self._opacity_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._opacity_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)

    def _setup_style(self):
        """Apply styles from the theme to the section's elements with optimized caching."""
        if self._title_label and theme_manager:
            title_color = theme_manager.get_color('text_primary').name()
            title_style = f"color: {title_color};"
            self._title_label.setStyleSheet(title_style)

        if self._desc_label and theme_manager:
            desc_color = theme_manager.get_color('text_secondary').name()
            desc_style = f"color: {desc_color};"
            self._desc_label.setStyleSheet(desc_style)

    def setTitle(self, title: str):
        """Set the title text of the section with smooth transition."""
        if self._title != title:
            self._title = title
            if self._title_label:
                self._animate_text_change(self._title_label, title)
            self.updateGeometry()

    def _animate_text_change(self, label: QLabel, new_text: str):
        """Animate text changes in labels."""
        if not self._is_animating:
            self._is_animating = True
            
            fade_out = QPropertyAnimation(label, QByteArray(b"windowOpacity"))
            fade_out.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.3)
            fade_out.setEasingCurve(FluentTransition.EASE_SMOOTH)
            
            fade_out.finished.connect(lambda: self._complete_text_change(label, new_text))
            fade_out.start()

    def _complete_text_change(self, label: QLabel, new_text: str):
        """Complete the text change animation."""
        label.setText(new_text)
        
        fade_in = QPropertyAnimation(label, QByteArray(b"windowOpacity"))
        fade_in.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
        fade_in.setStartValue(0.3)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(FluentTransition.EASE_SMOOTH)
        fade_in.finished.connect(self._on_animation_finished)
        fade_in.start()

    def title(self) -> str:
        """Get the current title text of the section."""
        return self._title

    def setDescription(self, description: str):
        """Set the description text of the section with smooth transition."""
        if self._description != description:
            self._description = description
            if self._desc_label:
                self._animate_text_change(self._desc_label, description)
            self.updateGeometry()

    def description(self) -> str:
        """Get the current description text of the section."""
        return self._description

    def divider(self) -> FluentDivider:
        """Get the FluentDivider instance used by this section."""
        return self._divider

    def _on_theme_changed_request(self):
        """Handle theme change request with debouncing."""
        if hasattr(self, '_theme_timer'):
            self._theme_timer.start(50)  # 50ms debounce

    def _on_theme_changed_debounced(self):
        """Handle debounced theme changes by updating styles and animating the section's appearance."""
        self._setup_style()

        if not self._is_animating:
            self._is_animating = True
            
            self._opacity_effect.setOpacity(0.7)
            self._opacity_animation.setStartValue(0.7)
            self._opacity_animation.setEndValue(1.0)
            self._opacity_animation.finished.connect(self._on_animation_finished)
            self._opacity_animation.start()

    def _on_animation_finished(self):
        """Handle animation completion."""
        self._is_animating = False

    def animateIn(self, callback: Optional[Callable] = None):
        """Animate the entire section appearing."""
        self._opacity_effect.setOpacity(0.0)
        
        animation = QPropertyAnimation(self._opacity_effect, QByteArray(b"opacity"))
        animation.setDuration(FluentAnimation.DURATION_SLOW)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(FluentTransition.EASE_SPRING)
        
        if callback:
            animation.finished.connect(callback)
        
        animation.start()
        return animation

    def animateOut(self, callback: Optional[Callable] = None):
        """Animate the entire section disappearing."""
        animation = QPropertyAnimation(self._opacity_effect, QByteArray(b"opacity"))
        animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
        
        if callback:
            animation.finished.connect(callback)
        
        animation.start()
        return animation
