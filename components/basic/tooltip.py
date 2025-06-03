"""
Fluent Design Style Tooltip Component
Provides animated, responsive tooltips with consistent theme integration.
"""

from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect,
                               QGraphicsOpacityEffect, QSizePolicy, QHBoxLayout)
from PySide6.QtCore import (Qt, QTimer, QPoint, QPropertyAnimation, QParallelAnimationGroup,
                            QEasingCurve, QSequentialAnimationGroup, QByteArray, Signal,
                            Property, QRect, QSize)
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPaintEvent, QResizeEvent
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional, Union, Callable, Dict, Any
import weakref


class FluentTooltip(QWidget):
    """
    Enhanced Fluent Design style tooltip with smooth animations and theme integration

    Features:
    - Smooth entrance/exit animations 
    - Theme-aware styling with consistent shadows
    - Fluid expand/collapse effect for content
    - Optimized rendering and memory management
    - Support for dynamic rich content
    - Responsive positioning with screen awareness
    """

    # Signals
    opacityChanged = Signal()
    sizeChanged = Signal()
    contentChanged = Signal(str)

    # Constants for styling and animation
    BORDER_RADIUS = 6
    ARROW_SIZE = 8
    MIN_WIDTH = 50
    MAX_WIDTH = 350
    PADDING = 12

    # Animation durations
    FADE_IN_DURATION = FluentAnimation.DURATION_FAST
    FADE_OUT_DURATION = FluentAnimation.DURATION_FAST
    EXPAND_DURATION = FluentAnimation.DURATION_FAST

    # Easing curves
    EASE_SPRING = QEasingCurve.Type.OutBack
    EASE_SMOOTH = QEasingCurve.Type.OutCubic

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Internal state
        self._text = text
        self._show_delay = 400  # ms - slightly faster than default for better UX
        self._hide_delay = 200  # ms - brief delay before hide animation starts
        self._auto_hide_delay = 3000  # ms - time before tooltip auto-hides
        self._show_timer = QTimer(self)
        self._hide_timer = QTimer(self)
        self._auto_hide_timer = QTimer(self)
        self._opacity = 0.0
        self._target_size = QSize()
        self._current_size = QSize()
        self._position_mode = "auto"  # "auto", "above", "below", "left", "right"
        self._rich_text_mode = False
        self._animation_group = None
        self._visible_widgets = weakref.WeakSet()  # Track actively shown tooltips
        self._is_showing = False
        self._is_hiding = False
        self._pointer_position = None  # Position to show arrow pointer
        self._show_arrow = True
        self._custom_theme = {}
        self._cached_style = ""

        # Setup core components
        self._setup_ui()
        self._setup_style()
        self._setup_timers()
        self._setup_animations()

        # Set window flags for a tooltip
        self._setup_window_flags()

        # Connect to theme system
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup the UI layout and components"""
        # Set sizing constraints
        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMaximumWidth(self.MAX_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Minimum)

        # Main layout with proper padding for the borders and arrow
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(
            self.PADDING, self.PADDING, self.PADDING, self.PADDING)
        self._main_layout.setSpacing(8)

        # Content container for dynamic content
        self._content_container = QWidget(self)
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(4)

        # Main label for text content
        self._label = QLabel(self._text)
        self._label.setWordWrap(True)
        self._label.setTextFormat(
            Qt.TextFormat.RichText if self._rich_text_mode else Qt.TextFormat.PlainText)
        self._label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Add components to layouts
        self._content_layout.addWidget(self._label)
        self._main_layout.addWidget(self._content_container)

        # Set up effects
        self._setup_effects()

    def _setup_effects(self):
        """Setup visual effects for the tooltip"""
        # Shadow effect for depth
        self._shadow_effect = QGraphicsDropShadowEffect()
        self._shadow_effect.setBlurRadius(15)
        self._shadow_effect.setOffset(0, 2)
        if theme_manager:
            self._shadow_effect.setColor(theme_manager.get_color('shadow'))
        self.setGraphicsEffect(self._shadow_effect)

        # Prepare opacity effect for animations
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self._content_container.setGraphicsEffect(self._opacity_effect)

    def _setup_window_flags(self):
        """Set up window flags for tooltip behavior"""
        self.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def _setup_style(self):
        """Setup style based on current theme"""
        if not theme_manager:
            return

        theme = theme_manager
        border_color = theme.get_color('border')

        # Use custom theme colors if set, otherwise use theme defaults
        surface_color = self._custom_theme.get(
            'surface', theme.get_color('surface'))
        text_color = self._custom_theme.get(
            'text', theme.get_color('text_primary'))

        # Build style sheet with current theme colors
        style_sheet = f"""
            FluentTooltip {{
                background-color: {surface_color.name()};
                border: 1px solid {border_color.name()};
                border-radius: {self.BORDER_RADIUS}px;
            }}
            
            QLabel {{
                color: {text_color.name()};
                font-size: 12px;
                font-family: "Segoe UI", sans-serif;
                background: transparent;
                border: none;
                padding: 0px;
            }}
        """

        self._cached_style = style_sheet
        self.setStyleSheet(style_sheet)

    def _setup_timers(self):
        """Setup timers for show/hide behavior"""
        self._show_timer.setSingleShot(True)
        self._show_timer.timeout.connect(self._show_tooltip_animated)

        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._hide_tooltip_animated)

        self._auto_hide_timer.setSingleShot(True)
        self._auto_hide_timer.timeout.connect(self.hideTooltip)

    def _setup_animations(self):
        """Setup animations for all transitions"""
        # Fade animation
        self._fade_animation = QPropertyAnimation(self, QByteArray(b"opacity"))
        self._fade_animation.setDuration(self.FADE_IN_DURATION)
        self._fade_animation.setEasingCurve(FluentAnimation.EASE_OUT)

        # Size animation for expand/collapse effect
        self._size_animation = QPropertyAnimation(
            self, QByteArray(b"currentSize"))
        self._size_animation.setDuration(self.EXPAND_DURATION)
        self._size_animation.setEasingCurve(self.EASE_SPRING)

    def _get_opacity(self) -> float:
        """Getter for opacity property"""
        return self._opacity

    def _set_opacity(self, value: float):
        """Setter for opacity property with signal emission"""
        if self._opacity != value:
            self._opacity = value
            self.setWindowOpacity(value)
            self.opacityChanged.emit()

    def _get_current_size(self) -> QSize:
        """Getter for currentSize property"""
        return self._current_size

    def _set_current_size(self, size: QSize):
        """Setter for currentSize property with signal emission"""
        if self._current_size != size:
            self._current_size = size
            self.updateGeometry()
            self.sizeChanged.emit()
            self.update()  # Force a repaint to update the size

    # Define Qt properties for animation
    opacity = Property(float, _get_opacity, _set_opacity,
                       None, "", notify=opacityChanged)
    currentSize = Property(QSize, _get_current_size,
                           _set_current_size, None, "", notify=sizeChanged)

    def sizeHint(self) -> QSize:
        """Return current size hint based on animation state"""
        if self._current_size.isValid():
            return self._current_size
        return super().sizeHint()

    def setText(self, text: str, rich_text: bool = False):
        """
        Set tooltip text content

        Args:
            text: Text content to display
            rich_text: Whether to interpret as rich text (HTML)
        """
        self._text = text
        self._rich_text_mode = rich_text

        # Update label
        self._label.setText(text)
        self._label.setTextFormat(
            Qt.TextFormat.RichText if rich_text else Qt.TextFormat.PlainText)

        # Adjust size after content change
        self.adjustSize()
        self._target_size = self.size()

        # Emit signal for content change
        self.contentChanged.emit(text)

    def getText(self) -> str:
        """Get current tooltip text"""
        return self._text

    def setRichTextMode(self, enabled: bool):
        """Enable or disable rich text rendering"""
        if self._rich_text_mode != enabled:
            self._rich_text_mode = enabled
            self._label.setTextFormat(
                Qt.TextFormat.RichText if enabled else Qt.TextFormat.PlainText)
            self.adjustSize()

    def setShowDelay(self, delay: int):
        """Set show delay in milliseconds"""
        self._show_delay = max(0, delay)  # Ensure non-negative

    def setHideDelay(self, delay: int):
        """Set hide delay in milliseconds"""
        self._hide_delay = max(0, delay)  # Ensure non-negative

    def setAutoHideDelay(self, delay: int):
        """Set auto-hide delay in milliseconds (0 to disable)"""
        self._auto_hide_delay = delay

    def setPositionMode(self, mode: str):
        """
        Set position mode for tooltip placement

        Args:
            mode: One of "auto", "above", "below", "left", "right"
        """
        if mode in ("auto", "above", "below", "left", "right"):
            self._position_mode = mode

    def setShowArrow(self, show: bool):
        """Enable or disable the direction arrow"""
        self._show_arrow = show
        self.update()  # Force repaint to show/hide arrow

    def setCustomTheme(self, theme_dict: Dict[str, QColor]):
        """
        Set custom theme colors

        Args:
            theme_dict: Dictionary with theme color overrides
                        (keys: 'surface', 'text', 'border')
        """
        self._custom_theme = theme_dict
        self._setup_style()

    def showTooltip(self, position: QPoint, target_widget: Optional[QWidget] = None):
        """
        Show tooltip at position after a delay

        Args:
            position: Global position where to show the tooltip
            target_widget: Optional widget target (for tracking)
        """
        # Stop any pending timers
        self._hide_timer.stop()
        self._auto_hide_timer.stop()

        # Save pointer position for arrow
        self._pointer_position = position

        # Adjust size to content first
        self.adjustSize()
        self._target_size = self.size()

        # Calculate optimal position based on mode and screen
        final_pos = self._calculate_position(position)
        self.move(final_pos)

        # If provided, track the target widget
        if target_widget is not None:
            self._visible_widgets.add(target_widget)

        # Show after delay or immediately
        if self._show_delay > 0 and not self._is_showing:
            self._show_timer.start(self._show_delay)
        else:
            self._show_tooltip_animated()

    def hideTooltip(self, immediate: bool = False):
        """
        Hide tooltip, possibly after a delay

        Args:
            immediate: If True, hide immediately without animation
        """
        self._show_timer.stop()  # Stop any pending show
        self._auto_hide_timer.stop()  # Stop auto-hide timer

        if not self.isVisible() or (self._is_hiding and not immediate):
            return  # Already hiding

        if immediate:
            # Immediate hide without animation
            self._is_showing = False
            self._is_hiding = False
            self.hide()
            self._set_opacity(0.0)
            return

        # Hide after a brief delay
        if self._hide_delay > 0 and not self._is_hiding:
            self._hide_timer.start(self._hide_delay)
        else:
            self._hide_tooltip_animated()

    def _calculate_position(self, position: QPoint) -> QPoint:
        """
        Calculate optimal position for tooltip based on screen constraints

        Args:
            position: Requested position

        Returns:
            Adjusted position within screen bounds
        """
        screen_geom = self.screen().availableGeometry() if self.screen() else None
        if not screen_geom:
            return position

        size = self._target_size
        x, y = position.x(), position.y()

        # Default positioning logic based on mode
        if self._position_mode == "auto":
            # Try above first (preferred)
            y = position.y() - size.height() - 12

            # If too high, try below
            if y < screen_geom.top():
                y = position.y() + 12

            # Center horizontally on pointer
            x = position.x() - size.width() // 2
        elif self._position_mode == "above":
            y = position.y() - size.height() - 12
            x = position.x() - size.width() // 2
        elif self._position_mode == "below":
            y = position.y() + 12
            x = position.x() - size.width() // 2
        elif self._position_mode == "left":
            x = position.x() - size.width() - 12
            y = position.y() - size.height() // 2
        elif self._position_mode == "right":
            x = position.x() + 12
            y = position.y() - size.height() // 2

        # Ensure within screen bounds
        if x < screen_geom.left():
            x = screen_geom.left() + 5
        elif x + size.width() > screen_geom.right():
            x = screen_geom.right() - size.width() - 5

        if y < screen_geom.top():
            y = screen_geom.top() + 5
        elif y + size.height() > screen_geom.bottom():
            y = screen_geom.bottom() - size.height() - 5

        return QPoint(x, y)

    def _show_tooltip_animated(self):
        """Show tooltip with smooth animation sequence"""
        self._is_showing = True
        self._is_hiding = False

        # Create parallel animation group for simultaneous effects
        self._animation_group = QParallelAnimationGroup(self)

        # Fade animation
        self._fade_animation.setStartValue(self._opacity)
        self._fade_animation.setEndValue(1.0)
        self._animation_group.addAnimation(self._fade_animation)

        # Size animation for expand effect
        self._current_size = QSize(
            self._target_size.width(), 0)  # Start collapsed
        self._size_animation.setStartValue(self._current_size)
        self._size_animation.setEndValue(self._target_size)
        self._animation_group.addAnimation(self._size_animation)

        # Connect finished signal and start
        self._animation_group.finished.connect(
            self._on_show_animation_finished)

        # Show widget and start animation
        self.show()
        self._animation_group.start()

        # Setup auto-hide if enabled
        if self._auto_hide_delay > 0:
            self._auto_hide_timer.start(self._auto_hide_delay)

    def _hide_tooltip_animated(self):
        """Hide tooltip with smooth animation sequence"""
        self._is_showing = False
        self._is_hiding = True

        # Cancel any running animations
        if self._animation_group and self._animation_group.state() == QPropertyAnimation.State.Running:
            self._animation_group.stop()

        # Create new animation group for hide sequence
        self._animation_group = QParallelAnimationGroup(self)

        # Fade out animation
        self._fade_animation.setStartValue(self._opacity)
        self._fade_animation.setEndValue(0.0)
        self._animation_group.addAnimation(self._fade_animation)

        # Size collapse animation (if needed)
        current_height = self._current_size.height()
        if current_height > 0:
            collapse_size = QSize(self._current_size.width(), 0)
            self._size_animation.setStartValue(self._current_size)
            self._size_animation.setEndValue(collapse_size)
            self._animation_group.addAnimation(self._size_animation)

        # Connect finished signal and start
        self._animation_group.finished.connect(
            self._on_hide_animation_finished)
        self._animation_group.start()

    def _on_show_animation_finished(self):
        """Handle show animation completion"""
        self._is_showing = False
        self._is_hiding = False
        self._animation_group = None

    def _on_hide_animation_finished(self):
        """Handle hide animation completion"""
        self._is_showing = False
        self._is_hiding = False
        self._animation_group = None
        self.hide()

    def _on_theme_changed(self, _=None):
        """Handle theme change event"""
        self._setup_style()
        # Update shadow color if theme changes
        if theme_manager and self._shadow_effect:
            self._shadow_effect.setColor(theme_manager.get_color('shadow'))

    def paintEvent(self, event: QPaintEvent):
        """Custom paint for tooltip with optional arrow"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get colors from theme
        if theme_manager:
            border_color = self._custom_theme.get(
                'border', theme_manager.get_color('border'))
            bg_color = self._custom_theme.get(
                'surface', theme_manager.get_color('surface'))
        else:
            border_color = QColor(200, 200, 200)
            bg_color = QColor(255, 255, 255)

        # Create path for rounded rectangle
        path = QPainterPath()
        rect = self.rect().adjusted(1, 1, -1, -1)  # Adjust for border
        path.addRoundedRect(rect, self.BORDER_RADIUS, self.BORDER_RADIUS)

        # Add arrow if enabled and position is valid
        if self._show_arrow and self._pointer_position:
            global_pos = self.mapFromGlobal(self._pointer_position)
            arrow_size = self.ARROW_SIZE

            # Determine where to draw the arrow based on position mode
            if self._position_mode == "below" or (self._position_mode == "auto" and
                                                  global_pos.y() < 0):
                # Arrow points up (tooltip below pointer)
                arrow_x = max(self.BORDER_RADIUS * 2,
                              min(rect.width() - self.BORDER_RADIUS * 2,
                                  rect.center().x()))
                path.moveTo(arrow_x - arrow_size, arrow_size)
                path.lineTo(arrow_x, 0)
                path.lineTo(arrow_x + arrow_size, arrow_size)
            elif self._position_mode == "above" or (self._position_mode == "auto" and
                                                    global_pos.y() > rect.height()):
                # Arrow points down (tooltip above pointer)
                arrow_x = max(self.BORDER_RADIUS * 2,
                              min(rect.width() - self.BORDER_RADIUS * 2,
                                  rect.center().x()))
                path.moveTo(arrow_x - arrow_size, rect.height() - arrow_size)
                path.lineTo(arrow_x, rect.height())
                path.lineTo(arrow_x + arrow_size, rect.height() - arrow_size)

        # Draw the background and border
        painter.setPen(border_color)
        painter.setBrush(bg_color)
        painter.drawPath(path)

    def resizeEvent(self, event: QResizeEvent):
        """Handle resize to ensure correct animation state"""
        super().resizeEvent(event)

        # Update target size only if not in animation
        if not self._is_showing and not self._is_hiding:
            self._target_size = event.size()
            self._current_size = event.size()

    def setWidget(self, widget: QWidget):
        """Set a custom widget as tooltip content"""
        # Clean up previous content
        for i in reversed(range(self._content_layout.count())):
            item = self._content_layout.itemAt(i)
            if item and item.widget() != self._label:
                item.widget().setParent(None)

        # Add new widget
        self._content_layout.addWidget(widget)

        # Adjust size
        self.adjustSize()
        self._target_size = self.size()

    def clearWidgets(self):
        """Clear any custom widgets from content"""
        self.setText(self._text)  # Restore just the text

    def widgetDestroyed(self, widget):
        """Handle cleanup when a tracked widget is destroyed"""
        if widget in self._visible_widgets:
            self._visible_widgets.remove(widget)
            # If this was the last widget, hide tooltip
            if not self._visible_widgets:
                self.hideTooltip(immediate=True)


class FluentTooltipManager:
    """
    Global manager for tooltips to prevent multiple tooltips showing simultaneously
    and provide consistent tooltip behavior across the application.
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(FluentTooltipManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the tooltip manager once"""
        self._active_tooltips = {}  # widget -> tooltip mapping
        self._global_tooltip = FluentTooltip()  # Shared tooltip for simple text

    def showTooltip(self, text: str, position: QPoint,
                    source_widget: Optional[QWidget] = None,
                    rich_text: bool = False):
        """
        Show tooltip at position

        Args:
            text: Text content to display
            position: Global screen position
            source_widget: Optional source widget
            rich_text: Whether text is rich text (HTML)
        """
        # Hide any existing tooltips for the same widget
        if source_widget in self._active_tooltips:
            self._active_tooltips[source_widget].hideTooltip()

        # Use the global tooltip for simple text
        self._global_tooltip.setText(text, rich_text=rich_text)
        self._global_tooltip.showTooltip(position, source_widget)

        if source_widget:
            self._active_tooltips[source_widget] = self._global_tooltip

    def hideTooltip(self, source_widget: Optional[QWidget] = None):
        """
        Hide tooltip(s)

        Args:
            source_widget: Widget whose tooltip should be hidden,
                           or None to hide all tooltips
        """
        if source_widget is None:
            # Hide all tooltips
            self._global_tooltip.hideTooltip()
            for tooltip in set(self._active_tooltips.values()):
                tooltip.hideTooltip()
        elif source_widget in self._active_tooltips:
            # Hide specific tooltip
            self._active_tooltips[source_widget].hideTooltip()
            del self._active_tooltips[source_widget]

    def createTooltip(self, text: str = "", parent: Optional[QWidget] = None) -> FluentTooltip:
        """
        Create a new tooltip instance

        Args:
            text: Initial tooltip text
            parent: Parent widget

        Returns:
            New FluentTooltip instance
        """
        tooltip = FluentTooltip(text, parent)
        return tooltip


# Global tooltip manager instance
tooltip_manager = FluentTooltipManager()


class TooltipMixin:
    """
    Mixin class to add tooltip functionality to any QWidget

    Features:
    - Easy tooltip activation on hover
    - Support for rich text and custom tooltips
    - Automatic positioning and theme integration
    - Memory-efficient shared tooltip management
    """

    def __init__(self, *args, **kwargs):
        # Store tooltip settings
        self._tooltip_text_content = ""
        self._tooltip_rich_text = False
        self._tooltip_show_delay = 400
        self._tooltip_position_mode = "auto"
        self._tooltip_custom_widget = None

    def setTooltipText(self, text: str, rich_text: bool = False):
        """
        Set tooltip text

        Args:
            text: Tooltip text content
            rich_text: Whether to render as rich text (HTML)
        """
        self._tooltip_text_content = text
        self._tooltip_rich_text = rich_text

    def setTooltipRichText(self, html: str):
        """Convenience method to set rich text tooltip"""
        self.setTooltipText(html, rich_text=True)

    def setTooltipWidget(self, widget: QWidget):
        """Set custom widget as tooltip content"""
        self._tooltip_custom_widget = widget

    def setTooltipShowDelay(self, delay_ms: int):
        """Set tooltip show delay in milliseconds"""
        self._tooltip_show_delay = delay_ms

    def setTooltipPosition(self, mode: str):
        """Set tooltip position mode"""
        if mode in ("auto", "above", "below", "left", "right"):
            self._tooltip_position_mode = mode

    def toolTipText(self) -> str:
        """Get the current tooltip text"""
        return self._tooltip_text_content

    def enterEvent(self, event, /):
        """Handle mouse enter event to show tooltip"""

        if isinstance(self, QWidget):  # Ensure self is a QWidget
            if self._tooltip_text_content:
                # Show tooltip near cursor position
                cursor_pos = self.cursor().pos()

                # If a custom widget is set, use a dedicated tooltip
                if self._tooltip_custom_widget:
                    tooltip = tooltip_manager.createTooltip()
                    tooltip.setWidget(self._tooltip_custom_widget)
                    tooltip.setShowDelay(self._tooltip_show_delay)
                    tooltip.setPositionMode(self._tooltip_position_mode)
                    tooltip.showTooltip(cursor_pos, self)
                else:
                    # Use shared tooltip manager for text tooltips
                    tooltip_manager.showTooltip(
                        self._tooltip_text_content,
                        cursor_pos,
                        self,
                        self._tooltip_rich_text
                    )

        # Call parent class enterEvent if it exists
        # Check MRO for classes that have enterEvent method
        for cls in self.__class__.__mro__[1:]:  # Skip current class
            if hasattr(cls, 'enterEvent') and cls.enterEvent is not TooltipMixin.enterEvent:
                cls.enterEvent(self, event)
                break

    def leaveEvent(self, event, /):
        """Handle mouse leave event to hide tooltip"""

        if isinstance(self, QWidget):  # Ensure self is a QWidget
            # Hide any tooltip associated with this widget
            tooltip_manager.hideTooltip(self)

        # Call parent class leaveEvent if it exists
        # Check MRO for classes that have leaveEvent method
        for cls in self.__class__.__mro__[1:]:  # Skip current class
            if hasattr(cls, 'leaveEvent') and cls.leaveEvent is not TooltipMixin.leaveEvent:
                cls.leaveEvent(self, event)
                break
