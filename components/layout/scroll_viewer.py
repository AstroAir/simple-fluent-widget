"""
FluentScrollViewer - Custom scroll container following Fluent Design principles

Features:
- Fluent Design styled scrollbars
- Smooth scrolling animations
- Touch and gesture support
- Auto-hide scrollbars on desktop
- Customizable scroll policies
- Theme-aware styling
"""

from typing import Optional
from PySide6.QtWidgets import (QScrollArea, QWidget, QVBoxLayout, QHBoxLayout,
                               QScrollBar, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation, Signal, QByteArray
from PySide6.QtGui import QPainter, QColor, QPen, QBrush

from ..base.fluent_control_base import FluentControlBase, FluentThemeAware


class FluentScrollBar(QScrollBar):
    """Custom scrollbar with Fluent Design styling."""

    def __init__(self, orientation: Qt.Orientation, parent: Optional[QWidget] = None):
        super().__init__(orientation, parent)
        self._is_pressed = False
        self._is_hovered = False
        self._theme = {}

        self.setFixedWidth(12 if orientation ==
                           Qt.Orientation.Vertical else 12)
        self.setFixedHeight(12 if orientation ==
                            Qt.Orientation.Horizontal else 12)

        # Auto-hide timer
        self._hide_timer = QTimer()
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._on_hide_timeout)

        # Fade animation
        self._opacity = 0.0
        self._fade_animation = QPropertyAnimation(self, QByteArray(b"opacity"))
        self._fade_animation.setDuration(150)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def paintEvent(self, event):
        """Custom paint event for Fluent Design styling."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        bg_color = QColor(self._theme.get('scrollbar_background', '#f3f2f1'))
        bg_color.setAlphaF(self._opacity)
        painter.fillRect(self.rect(), bg_color)

        # Thumb
        if self.maximum() > 0:
            thumb_rect = self._get_thumb_rect()

            thumb_color = QColor(self._theme.get('scrollbar_thumb', '#8a8886'))
            if self._is_pressed:
                thumb_color = QColor(self._theme.get(
                    'scrollbar_thumb_pressed', '#323130'))
            elif self._is_hovered:
                thumb_color = QColor(self._theme.get(
                    'scrollbar_thumb_hover', '#605e5c'))

            thumb_color.setAlphaF(self._opacity)
            painter.setBrush(QBrush(thumb_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(thumb_rect, 2, 2)

    def _get_thumb_rect(self):
        """Calculate thumb rectangle position."""
        if self.maximum() == 0:
            return self.rect()

        if self.orientation() == Qt.Orientation.Vertical:
            thumb_height = max(
                20, (self.height() * self.pageStep()) // (self.maximum() + self.pageStep()))
            thumb_y = (self.height() - thumb_height) * \
                self.value() // self.maximum()
            return self.rect().adjusted(2, thumb_y, -2, thumb_y + thumb_height - self.height())
        else:
            thumb_width = max(20, (self.width() * self.pageStep()) //
                              (self.maximum() + self.pageStep()))
            thumb_x = (self.width() - thumb_width) * \
                self.value() // self.maximum()
            return self.rect().adjusted(thumb_x, 2, thumb_x + thumb_width - self.width(), -2)

    def enterEvent(self, event):
        """Handle mouse enter."""
        super().enterEvent(event)
        self._is_hovered = True
        self._show_scrollbar()

    def leaveEvent(self, event):
        """Handle mouse leave."""
        super().leaveEvent(event)
        self._is_hovered = False
        if not self._is_pressed:
            self._schedule_hide()

    def mousePressEvent(self, event):
        """Handle mouse press."""
        super().mousePressEvent(event)
        self._is_pressed = True
        self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        super().mouseReleaseEvent(event)
        self._is_pressed = False
        if not self._is_hovered:
            self._schedule_hide()
        self.update()

    def _show_scrollbar(self):
        """Show scrollbar with fade animation."""
        self._hide_timer.stop()
        self._fade_animation.stop()
        self._fade_animation.setStartValue(self._opacity)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.start()

    def _schedule_hide(self):
        """Schedule scrollbar hide."""
        self._hide_timer.stop()
        self._hide_timer.start(1000)  # Hide after 1 second

    def _on_hide_timeout(self):
        """Handle hide timeout."""
        if not self._is_hovered and not self._is_pressed:
            self._fade_animation.stop()
            self._fade_animation.setStartValue(self._opacity)
            self._fade_animation.setEndValue(0.0)
            self._fade_animation.start()

    def set_theme(self, theme: dict):
        """Set theme colors."""
        self._theme = theme
        self.update()

    # Property for animation
    def get_opacity(self):
        return self._opacity

    def set_opacity(self, opacity):
        self._opacity = opacity
        self.update()

    opacity = property(get_opacity, set_opacity)


class FluentScrollViewer(QScrollArea, FluentControlBase, FluentThemeAware):
    """
    A custom scroll container with Fluent Design styling.

    Provides smooth scrolling, auto-hide scrollbars, and theme-aware styling
    following Fluent Design principles.
    """

    # Signals
    scroll_changed = Signal(int, int)  # horizontal, vertical positions

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        FluentControlBase.__init__(self)
        FluentThemeAware.__init__(self)

        self._smooth_scrolling = True
        self._auto_hide_scrollbars = True

        self._init_ui()
        self._setup_styling()
        self._setup_scrollbars()
        self._connect_signals()

        # Apply theme
        self.apply_theme()

    def _init_ui(self):
        """Initialize the user interface."""
        # Set basic properties
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

    def _setup_styling(self):
        """Setup Fluent Design styling."""
        self.setStyleSheet("""
            FluentScrollViewer {
                background-color: var(--scroll-background, transparent);
                border: none;
                border-radius: 4px;
            }
            
            FluentScrollViewer QScrollBar:vertical {
                background: transparent;
                width: 12px;
                border: none;
            }
            
            FluentScrollViewer QScrollBar:horizontal {
                background: transparent;
                height: 12px;
                border: none;
            }
            
            FluentScrollViewer QScrollBar::handle {
                background-color: var(--scrollbar-thumb, #8a8886);
                border-radius: 2px;
                min-height: 20px;
                min-width: 20px;
            }
            
            FluentScrollViewer QScrollBar::handle:hover {
                background-color: var(--scrollbar-thumb-hover, #605e5c);
            }
            
            FluentScrollViewer QScrollBar::handle:pressed {
                background-color: var(--scrollbar-thumb-pressed, #323130);
            }
            
            FluentScrollViewer QScrollBar::add-line,
            FluentScrollViewer QScrollBar::sub-line {
                border: none;
                background: none;
                width: 0px;
                height: 0px;
            }
            
            FluentScrollViewer QScrollBar::add-page,
            FluentScrollViewer QScrollBar::sub-page {
                background: none;
            }
        """)

    def _setup_scrollbars(self):
        """Setup custom scrollbars."""
        if self._auto_hide_scrollbars:
            # Replace default scrollbars with custom ones
            self._v_scrollbar = FluentScrollBar(Qt.Orientation.Vertical, self)
            self._h_scrollbar = FluentScrollBar(
                Qt.Orientation.Horizontal, self)

            self.setVerticalScrollBar(self._v_scrollbar)
            self.setHorizontalScrollBar(self._h_scrollbar)

    def _connect_signals(self):
        """Connect scroll signals."""
        if hasattr(self, '_v_scrollbar'):
            self._v_scrollbar.valueChanged.connect(self._on_scroll_changed)
        if hasattr(self, '_h_scrollbar'):
            self._h_scrollbar.valueChanged.connect(self._on_scroll_changed)

    def _on_scroll_changed(self):
        """Handle scroll position changes."""
        h_pos = self.horizontalScrollBar().value()
        v_pos = self.verticalScrollBar().value()
        self.scroll_changed.emit(h_pos, v_pos)

    def scroll_to_top(self, animated: bool = True):
        """Scroll to top of content."""
        if animated and self._smooth_scrolling:
            self._animate_scroll_to(0, 0)
        else:
            self.verticalScrollBar().setValue(0)

    def scroll_to_bottom(self, animated: bool = True):
        """Scroll to bottom of content."""
        max_value = self.verticalScrollBar().maximum()
        if animated and self._smooth_scrolling:
            self._animate_scroll_to(
                self.horizontalScrollBar().value(), max_value)
        else:
            self.verticalScrollBar().setValue(max_value)

    def scroll_to_position(self, h_pos: int, v_pos: int, animated: bool = True):
        """Scroll to specific position."""
        if animated and self._smooth_scrolling:
            self._animate_scroll_to(h_pos, v_pos)
        else:
            self.horizontalScrollBar().setValue(h_pos)
            self.verticalScrollBar().setValue(v_pos)

    def _animate_scroll_to(self, h_pos: int, v_pos: int):
        """Animate scroll to position."""
        # Vertical animation
        if hasattr(self, '_v_scroll_animation'):
            self._v_scroll_animation.stop()

        self._v_scroll_animation = QPropertyAnimation(
            self.verticalScrollBar(), QByteArray(b"value"))
        self._v_scroll_animation.setDuration(300)
        self._v_scroll_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._v_scroll_animation.setStartValue(
            self.verticalScrollBar().value())
        self._v_scroll_animation.setEndValue(v_pos)

        # Horizontal animation
        if hasattr(self, '_h_scroll_animation'):
            self._h_scroll_animation.stop()

        self._h_scroll_animation = QPropertyAnimation(
            self.horizontalScrollBar(), QByteArray(b"value"))
        self._h_scroll_animation.setDuration(300)
        self._h_scroll_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._h_scroll_animation.setStartValue(
            self.horizontalScrollBar().value())
        self._h_scroll_animation.setEndValue(h_pos)

        # Start animations
        self._v_scroll_animation.start()
        self._h_scroll_animation.start()

    def set_smooth_scrolling(self, enabled: bool):
        """Enable or disable smooth scrolling."""
        self._smooth_scrolling = enabled

    def set_auto_hide_scrollbars(self, enabled: bool):
        """Enable or disable auto-hide scrollbars."""
        self._auto_hide_scrollbars = enabled
        if enabled:
            self._setup_scrollbars()

    def get_scroll_position(self) -> tuple:
        """Get current scroll position."""
        return (self.horizontalScrollBar().value(), self.verticalScrollBar().value())

    def get_scroll_range(self) -> tuple:
        """Get scroll range (max values)."""
        return (self.horizontalScrollBar().maximum(), self.verticalScrollBar().maximum())

    def apply_theme(self):
        """Apply the current theme to the scroll viewer."""
        theme = self.get_current_theme()
        if not theme:
            return

        # Update CSS variables based on theme
        style_vars = {
            '--scroll-background': theme.get('surface_background', 'transparent'),
            '--scrollbar-thumb': theme.get('scrollbar_thumb', '#8a8886'),
            '--scrollbar-thumb-hover': theme.get('scrollbar_thumb_hover', '#605e5c'),
            '--scrollbar-thumb-pressed': theme.get('scrollbar_thumb_pressed', '#323130'),
        }

        # Apply updated styling
        current_style = self.styleSheet()
        for var_name, var_value in style_vars.items():
            current_style = current_style.replace(
                f'var({var_name}, ', f'{var_value}; /* var({var_name}, ')

        self.setStyleSheet(current_style)

        # Update custom scrollbars
        if hasattr(self, '_v_scrollbar'):
            self._v_scrollbar.set_theme(theme)
        if hasattr(self, '_h_scrollbar'):
            self._h_scrollbar.set_theme(theme)
