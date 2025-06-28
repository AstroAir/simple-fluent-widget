"""
Optimized Fluent Design Style Badge and Tag Components
Enhanced badges, tags and status indicators with improved animations and unified theme support
"""

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy, QPushButton
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QPainter, QPainterPath, QColor, QBrush, QPen
from core.theme import theme_manager, ThemeMode
from core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                      FluentRevealEffect, FluentSequence)
from typing import Optional, Dict
import weakref


class FluentBadge(QWidget):
    """Enhanced Fluent Design Style Badge with optimized animations and unified theming

    Features:
    - Multiple badge types with consistent theme colors
    - Optimized animations with hardware acceleration
    - Smart size management and performance optimization
    - Enhanced visual feedback and accessibility
    - Memory-efficient caching system
    """

    class BadgeType:
        DEFAULT = "default"
        INFO = "info"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"

    # Class-level cache for style sheets to improve performance
    _style_cache: Dict[str, str] = {}

    def __init__(self, parent: Optional[QWidget] = None,
                 badge_type: str = BadgeType.DEFAULT,
                 text: str = "", dot: bool = False):
        super().__init__(parent)

        self._badge_type = badge_type
        self._text = text
        self._dot_mode = dot
        self._is_animating = False
        self._current_theme_hash = None

        # Performance optimization: pre-calculate geometry
        self._cached_size = None
        self._theme_colors = {}

        self._setup_ui()
        self._setup_enhanced_animations()
        self._apply_style()

        # Connect to theme manager
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI components with optimized layout"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 2, 4, 2)
        self._layout.setSpacing(0)

        self._label = QLabel(self._text)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Optimized font setting
        font = QFont("Segoe UI", 9, QFont.Weight.Medium)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self._label.setFont(font)

        self._layout.addWidget(self._label)

        # Optimized size policy setup
        if self._dot_mode:
            self.setFixedSize(8, 8)
            self._label.setVisible(False)
            self._layout.setContentsMargins(0, 0, 0, 0)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Minimum,
                               QSizePolicy.Policy.Fixed)
            self.setMinimumHeight(20)
            self._optimize_size_for_content()

    def _optimize_size_for_content(self):
        """Optimize size based on content for better performance"""
        if not self._text:
            return

        try:
            # Smart sizing for numeric content
            value = int(self._text)
            if value < 10:
                self.setFixedWidth(20)
            elif value < 100:
                self.setFixedWidth(28)
            elif value < 1000:
                self.setFixedWidth(36)
            else:
                # For very large numbers, use dynamic sizing
                self.setMinimumWidth(40)
        except ValueError:
            # For text content, use minimum width with dynamic expansion
            self.setMinimumWidth(max(20, len(self._text) * 6 + 16))

    def _get_theme_colors(self) -> Dict[str, str]:
        """Get theme colors with caching for performance"""
        current_theme_hash = hash(
            (theme_manager.get_theme_mode(), self._badge_type))

        if self._current_theme_hash == current_theme_hash and self._theme_colors:
            return self._theme_colors

        self._current_theme_hash = current_theme_hash
        theme = theme_manager

        # Get semantic colors from theme
        if self._badge_type == self.BadgeType.DEFAULT:
            bg_color = theme.get_color('surface').name()
            text_color = theme.get_color('text_primary').name()
            border_color = theme.get_color('border').name()
        elif self._badge_type == self.BadgeType.INFO:
            bg_color = theme.get_color('primary').name()
            text_color = theme.get_color('surface').name()
            border_color = bg_color
        elif self._badge_type == self.BadgeType.SUCCESS:
            # Use theme-aware success color
            if theme.get_theme_mode() == ThemeMode.DARK:
                bg_color = "#0d7377"  # Darker green for dark theme
            else:
                bg_color = "#107c10"  # Standard green for light theme
            text_color = theme.get_color('surface').name()
            border_color = bg_color
        elif self._badge_type == self.BadgeType.WARNING:
            # Use theme-aware warning color
            if theme.get_theme_mode() == ThemeMode.DARK:
                bg_color = "#ca5010"  # Orange for dark theme
            else:
                bg_color = "#fde047"  # Yellow for light theme
            text_color = theme.get_color('text_primary').name()
            border_color = bg_color
        elif self._badge_type == self.BadgeType.ERROR:
            # Use theme-aware error color
            if theme.get_theme_mode() == ThemeMode.DARK:
                bg_color = "#d13438"  # Lighter red for dark theme
            else:
                bg_color = "#dc2626"  # Standard red for light theme
            text_color = theme.get_color('surface').name()
            border_color = bg_color
        else:
            bg_color = theme.get_color('surface').name()
            text_color = theme.get_color('text_primary').name()
            border_color = theme.get_color('border').name()

        # Create hover and active states
        hover_bg = self._adjust_color_brightness(bg_color, 0.1)
        active_bg = self._adjust_color_brightness(bg_color, -0.1)

        self._theme_colors = {
            'bg': bg_color,
            'text': text_color,
            'border': border_color,
            'hover_bg': hover_bg,
            'active_bg': active_bg
        }

        return self._theme_colors

    def _adjust_color_brightness(self, hex_color: str, factor: float) -> str:
        """Adjust color brightness for hover/active states"""
        try:
            color = QColor(hex_color)
            if factor > 0:
                # Lighten
                color = color.lighter(int(100 + factor * 100))
            else:
                # Darken
                color = color.darker(int(100 - factor * 100))
            return color.name()
        except Exception:
            return hex_color

    def _apply_style(self):
        """Apply optimized badge style with theme colors and caching"""
        colors = self._get_theme_colors()

        # Create cache key for style
        cache_key = f"{self._badge_type}_{self._dot_mode}_{hash(str(colors))}"

        if cache_key in self._style_cache:
            self.setStyleSheet(self._style_cache[cache_key])
            return

        if self._dot_mode:
            style_sheet = f"""
                FluentBadge {{
                    background-color: {colors['bg']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    transition: all 0.25s cubic-bezier(0.4, 0.0, 0.2, 1);
                }}
                FluentBadge:hover {{
                    background-color: {colors['hover_bg']};
                    transform: scale(1.15);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                }}
                FluentBadge:pressed {{
                    background-color: {colors['active_bg']};
                    transform: scale(1.05);
                }}
            """
        else:
            style_sheet = f"""
                FluentBadge {{
                    background-color: {colors['bg']};
                    border: 1px solid {colors['border']};
                    border-radius: 10px;
                    padding: 2px 8px;
                    transition: all 0.25s cubic-bezier(0.4, 0.0, 0.2, 1);
                }}
                FluentBadge:hover {{
                    background-color: {colors['hover_bg']};
                    transform: translateY(-1px);
                    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
                }}
                FluentBadge:pressed {{
                    background-color: {colors['active_bg']};
                    transform: translateY(0px);
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                }}
                QLabel {{
                    color: {colors['text']};
                    background-color: transparent;
                    border: none;
                    font-weight: 500;
                }}
            """

        # Cache the style sheet
        self._style_cache[cache_key] = style_sheet
        self.setStyleSheet(style_sheet)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system with performance optimization"""
        # Delay entrance animation to avoid blocking UI
        QTimer.singleShot(50, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show optimized entrance animation"""
        if self._is_animating:
            return

        self._is_animating = True

        # Use more efficient animation sequence
        entrance_sequence = FluentSequence(self)

        # Optimized fade in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self, 200))
        entrance_sequence.addPause(25)

        # Optimized scale in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.scale_in(self, 150))

        # Reset animation flag
        entrance_sequence.addCallback(
            lambda: setattr(self, '_is_animating', False))

        entrance_sequence.start()

    def _on_theme_changed(self, _):
        """Handle theme changes with optimized transition"""
        # Clear cached colors to force refresh
        self._theme_colors.clear()
        self._current_theme_hash = None

        # Apply new style
        self._apply_style()

        # Add subtle transition effect
        if not self._is_animating:
            FluentMicroInteraction.pulse_animation(self, 1.02)

    def setText(self, text: str):
        """Set badge text with optimized transition"""
        if self._text == text:
            return

        old_text = self._text
        self._text = text
        self._label.setText(text)

        # Optimize size for new content
        self._optimize_size_for_content()

        # Add transition effect only if content changed significantly
        if len(old_text) != len(text) or old_text != text:
            FluentMicroInteraction.pulse_animation(self._label, 1.03)

    def setBadgeType(self, badge_type: str):
        """Set badge type with optimized transition"""
        if self._badge_type == badge_type:
            return

        self._badge_type = badge_type

        # Clear cached colors to force refresh
        self._theme_colors.clear()
        self._current_theme_hash = None

        self._apply_style()
        FluentMicroInteraction.pulse_animation(self, 1.03)

    def setDotMode(self, dot: bool):
        """Set dot mode with optimized transition"""
        if self._dot_mode == dot:
            return

        self._dot_mode = dot

        # Optimized transition sequence
        transition_sequence = FluentSequence(self)
        transition_sequence.addCallback(
            lambda: FluentMicroInteraction.scale_animation(self, 0.8))
        transition_sequence.addPause(100)
        transition_sequence.addCallback(self._apply_dot_mode_changes)
        transition_sequence.addCallback(
            lambda: FluentMicroInteraction.scale_animation(self, 1.0))
        transition_sequence.start()

    def _apply_dot_mode_changes(self):
        """Apply dot mode changes with optimized layout"""
        if self._dot_mode:
            self.setFixedSize(8, 8)
            self._label.setVisible(False)
            self._layout.setContentsMargins(0, 0, 0, 0)
        else:
            self._label.setVisible(True)
            self._layout.setContentsMargins(4, 2, 4, 2)
            self.setSizePolicy(QSizePolicy.Policy.Minimum,
                               QSizePolicy.Policy.Fixed)
            self.setMinimumHeight(20)
            self._optimize_size_for_content()

        # Clear style cache and reapply
        cache_key = f"{self._badge_type}_{not self._dot_mode}_{hash(str(self._theme_colors))}"
        if cache_key in self._style_cache:
            del self._style_cache[cache_key]

        self._apply_style()

    def enterEvent(self, event):
        """Handle mouse enter with optimized animation"""
        if not self._is_animating:
            FluentMicroInteraction.hover_glow(self, 0.08)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave with optimized animation"""
        if not self._is_animating:
            FluentMicroInteraction.hover_glow(self, -0.08)
        super().leaveEvent(event)

    def cleanup(self):
        """Cleanup resources and connections"""
        # Disconnect from theme manager
        try:
            theme_manager.theme_changed.disconnect(self._on_theme_changed)
        except RuntimeError:
            pass  # Already disconnected

        # Clear caches
        self._theme_colors.clear()
        self._cached_size = None


class FluentTag(QWidget):
    """Enhanced Fluent Design Style Tag with optimized performance

    Features:
    - Multiple tag variants with consistent theme colors
    - Optimized animations and interactions
    - Optional close button with smooth animations
    - Click event support with enhanced feedback
    - Memory-efficient style caching
    """

    clicked = Signal()
    closed = Signal()

    class TagVariant:
        DEFAULT = "default"
        OUTLINE = "outline"
        FILLED = "filled"

    # Class-level cache for style sheets
    _style_cache: Dict[str, str] = {}

    def __init__(self, text: str = "", parent: Optional[QWidget] = None,
                 variant: str = TagVariant.DEFAULT, closable: bool = False):
        super().__init__(parent)

        self._text = text
        self._variant = variant
        self._closable = closable
        self._color = None  # Custom color if set
        self._is_animating = False
        self._current_theme_hash = None
        self._theme_colors = {}

        self._setup_ui()
        self._setup_enhanced_animations()
        self._apply_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI components with optimized layout"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 4, 8, 4)
        self._layout.setSpacing(4)

        self._label = QLabel(self._text)

        # Optimized font setting
        font = QFont("Segoe UI", 10, QFont.Weight.Medium)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self._label.setFont(font)

        self._layout.addWidget(self._label)

        if self._closable:
            self._close_btn = QPushButton("✕")
            self._close_btn.setFixedSize(16, 16)
            self._close_btn.clicked.connect(self._on_close_clicked)
            self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._layout.addWidget(self._close_btn)

        # Set cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Optimized size policy
        self.setSizePolicy(QSizePolicy.Policy.Minimum,
                           QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(26)

    def _get_theme_colors(self) -> Dict[str, str]:
        """Get theme colors with caching for performance"""
        current_theme_hash = hash(
            (theme_manager.get_theme_mode(), self._variant, self._color))

        if self._current_theme_hash == current_theme_hash and self._theme_colors:
            return self._theme_colors

        self._current_theme_hash = current_theme_hash
        theme = theme_manager

        # Get colors
        if self._color:
            primary_color = self._color
        else:
            primary_color = theme.get_color('primary').name()

        text_color = theme.get_color('text_primary').name()
        bg_color = theme.get_color('surface').name()
        border_color = theme.get_color('border').name()

        # Create hover and active states
        if self._variant == self.TagVariant.FILLED:
            hover_bg = self._adjust_color_brightness(primary_color, 0.1)
            active_bg = self._adjust_color_brightness(primary_color, -0.1)
            text_color = theme.get_color('surface').name()
        else:
            hover_bg = self._hex_to_rgba(primary_color, 0.1)
            active_bg = self._hex_to_rgba(primary_color, 0.2)

        self._theme_colors = {
            'primary': primary_color,
            'text': text_color,
            'bg': bg_color,
            'border': border_color,
            'hover_bg': hover_bg,
            'active_bg': active_bg
        }

        return self._theme_colors

    def _hex_to_rgba(self, hex_color: str, alpha: float) -> str:
        """Convert hex color to RGBA with alpha"""
        try:
            color = QColor(hex_color)
            return f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha})"
        except Exception:
            return f"rgba(0, 0, 0, {alpha})"

    def _adjust_color_brightness(self, hex_color: str, factor: float) -> str:
        """Adjust color brightness for hover/active states"""
        try:
            color = QColor(hex_color)
            if factor > 0:
                color = color.lighter(int(100 + factor * 100))
            else:
                color = color.darker(int(100 - factor * 100))
            return color.name()
        except Exception:
            return hex_color

    def _apply_style(self):
        """Apply optimized tag style with theme colors and caching"""
        colors = self._get_theme_colors()

        # Create cache key for style
        cache_key = f"{self._variant}_{self._closable}_{hash(str(colors))}"

        if cache_key in self._style_cache:
            self.setStyleSheet(self._style_cache[cache_key])
            return

        # Define style based on variant
        style_sheet = ""  # Initialize style_sheet
        if self._variant == self.TagVariant.DEFAULT:
            style_sheet = f"""
                FluentTag {{
                    background-color: {colors['bg']};
                    border: 1px solid {colors['border']};
                    border-radius: 13px;
                    transition: all 0.25s cubic-bezier(0.4, 0.0, 0.2, 1);
                }}
                FluentTag:hover {{
                    border-color: {colors['primary']};
                    background-color: {colors['hover_bg']};
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                FluentTag:pressed {{
                    background-color: {colors['active_bg']};
                    transform: translateY(0px);
                }}
                QLabel {{
                    color: {colors['text']};
                    background-color: transparent;
                    border: none;
                    font-weight: 500;
                }}
            """
        elif self._variant == self.TagVariant.OUTLINE:
            style_sheet = f"""
                FluentTag {{
                    background-color: transparent;
                    border: 1px solid {colors['primary']};
                    border-radius: 13px;
                    transition: all 0.25s cubic-bezier(0.4, 0.0, 0.2, 1);
                }}
                FluentTag:hover {{
                    background-color: {colors['hover_bg']};
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                FluentTag:pressed {{
                    background-color: {colors['active_bg']};
                    transform: translateY(0px);
                }}
                QLabel {{
                    color: {colors['primary']};
                    background-color: transparent;
                    border: none;
                    font-weight: 500;
                }}
            """
        elif self._variant == self.TagVariant.FILLED:
            style_sheet = f"""
                FluentTag {{
                    background-color: {colors['primary']};
                    border: none;
                    border-radius: 13px;
                    transition: all 0.25s cubic-bezier(0.4, 0.0, 0.2, 1);
                }}
                FluentTag:hover {{
                    background-color: {colors['hover_bg']};
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }}
                FluentTag:pressed {{
                    background-color: {colors['active_bg']};
                    transform: translateY(0px);
                }}
                QLabel {{
                    color: {colors['text']};
                    background-color: transparent;
                    border: none;
                    font-weight: 500;
                }}
            """

        # Add close button style if applicable
        if self._closable:
            close_icon_color = colors['text']
            if self._variant == self.TagVariant.OUTLINE:
                close_icon_color = colors['primary']

            style_sheet += f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 8px;
                    color: {close_icon_color};
                    font-family: "Segoe UI Symbol";
                    font-size: 12px;
                    font-weight: bold;
                    transition: all 0.2s ease;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 0, 0, 0.1);
                    transform: scale(1.1);
                }}
                QPushButton:pressed {{
                    transform: scale(0.9);
                }}
            """

        # Cache and apply the style sheet
        self._style_cache[cache_key] = style_sheet
        self.setStyleSheet(style_sheet)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system"""
        # Delay entrance animation
        QTimer.singleShot(75, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show optimized entrance animation"""
        if self._is_animating:
            return

        self._is_animating = True

        entrance_sequence = FluentSequence(self)

        # Optimized slide in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.slide_in(self, 250, "up"))
        entrance_sequence.addPause(50)

        # Subtle pulse effect
        entrance_sequence.addCallback(
            lambda: FluentMicroInteraction.pulse_animation(self, 1.02))

        # Reset animation flag
        entrance_sequence.addCallback(
            lambda: setattr(self, '_is_animating', False))

        entrance_sequence.start()

    def _on_theme_changed(self, _):
        """Handle theme changes with optimized transition"""
        # Clear cached colors
        self._theme_colors.clear()
        self._current_theme_hash = None

        self._apply_style()

        if not self._is_animating:
            FluentMicroInteraction.pulse_animation(self, 1.02)

    def _on_close_clicked(self):
        """Handle close button click with enhanced animation"""
        if self._is_animating:
            return

        self._is_animating = True

        # Optimized close animation sequence
        close_sequence = FluentSequence(self)

        # Scale down animation
        close_sequence.addCallback(
            lambda: FluentMicroInteraction.scale_animation(self, 0.8))
        close_sequence.addPause(100)

        # Fade out animation
        close_sequence.addCallback(
            lambda: FluentRevealEffect.fade_out(self, 150))
        close_sequence.addPause(150)

        # Complete removal
        close_sequence.addCallback(self._complete_close)

        close_sequence.start()

    def _complete_close(self):
        """Complete the close operation"""
        self.closed.emit()
        self.hide()

    def setText(self, text: str):
        """Set tag text with optimized transition"""
        if self._text == text:
            return

        self._text = text
        self._label.setText(text)

        if not self._is_animating:
            FluentMicroInteraction.pulse_animation(self._label, 1.03)

    def setColor(self, color: str):
        """Set custom tag color with optimized transition"""
        if self._color == color:
            return

        self._color = color

        # Clear cached colors
        self._theme_colors.clear()
        self._current_theme_hash = None

        self._apply_style()

        if not self._is_animating:
            FluentMicroInteraction.pulse_animation(self, 1.02)

    def setVariant(self, variant: str):
        """Set tag variant with optimized transition"""
        if self._variant == variant:
            return

        self._variant = variant

        # Clear cached colors
        self._theme_colors.clear()
        self._current_theme_hash = None

        self._apply_style()

        if not self._is_animating:
            FluentMicroInteraction.pulse_animation(self, 1.03)

    def mousePressEvent(self, event):
        """Handle mouse press event with enhanced animation"""
        if not self._is_animating:
            FluentMicroInteraction.button_press(self, 0.95)
        super().mousePressEvent(event)
        self.clicked.emit()

    def enterEvent(self, event):
        """Handle mouse enter with optimized animation"""
        if not self._is_animating:
            FluentMicroInteraction.hover_glow(self, 0.08)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave with optimized animation"""
        if not self._is_animating:
            FluentMicroInteraction.hover_glow(self, -0.08)
        super().leaveEvent(event)

    def cleanup(self):
        """Cleanup resources and connections"""
        try:
            theme_manager.theme_changed.disconnect(self._on_theme_changed)
        except RuntimeError:
            pass

        self._theme_colors.clear()


class FluentStatusIndicator(QWidget):
    """Enhanced status indicator with optimized animations and consistent theming"""

    class Status:
        ONLINE = "online"
        OFFLINE = "offline"
        BUSY = "busy"
        AWAY = "away"
        UNKNOWN = "unknown"

    def __init__(self, status: str = Status.UNKNOWN, size: int = 12,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._status = status
        self._size = size
        self._is_animating = False
        self._breathing_timer = None

        self.setFixedSize(size, size)
        self._setup_enhanced_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system"""
        # Breathing animation for active statuses
        if self._status in [self.Status.ONLINE, self.Status.BUSY]:
            QTimer.singleShot(100, self._start_breathing_animation)

        # Entrance animation
        QTimer.singleShot(50, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show optimized entrance animation"""
        if not self._is_animating:
            FluentRevealEffect.scale_in(self, 200)

    def _start_breathing_animation(self):
        """Start optimized breathing animation"""
        if self._breathing_timer:
            self._breathing_timer.stop()

        def breathe():
            if not self._is_animating and self.isVisible():
                FluentMicroInteraction.pulse_animation(self, 1.05)

        self._breathing_timer = QTimer(self)
        self._breathing_timer.timeout.connect(breathe)
        self._breathing_timer.start(3000)  # Every 3 seconds

    def _get_status_color(self) -> str:
        """Get theme-aware color based on status"""
        theme = theme_manager

        if self._status == self.Status.ONLINE:
            return "#107c10" if theme.get_theme_mode() == ThemeMode.LIGHT else "#0d7377"
        elif self._status == self.Status.OFFLINE:
            return theme.get_color('text_disabled').name()
        elif self._status == self.Status.BUSY:
            return "#dc2626" if theme.get_theme_mode() == ThemeMode.LIGHT else "#d13438"
        elif self._status == self.Status.AWAY:
            return "#ca5010" if theme.get_theme_mode() == ThemeMode.LIGHT else "#fde047"
        else:  # UNKNOWN
            return theme.get_color('border').name()

    def paintEvent(self, event):
        """Custom paint with enhanced styling and anti-aliasing"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        # Draw status indicator with subtle shadow
        color = QColor(self._get_status_color())

        # Draw shadow
        shadow_color = QColor(0, 0, 0, 30)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(1, 1, self._size - 1, self._size - 1)

        # Draw main indicator
        painter.setBrush(QBrush(color))
        painter.drawEllipse(0, 0, self._size, self._size)

    def setStatus(self, status: str):
        """Set status with optimized transition"""
        if self._status == status:
            return

        old_status = self._status
        self._status = status

        # Optimized transition effect
        transition_sequence = FluentSequence(self)
        transition_sequence.addCallback(
            lambda: FluentMicroInteraction.scale_animation(self, 0.8))
        transition_sequence.addPause(75)
        transition_sequence.addCallback(self.update)
        transition_sequence.addCallback(
            lambda: FluentMicroInteraction.scale_animation(self, 1.0))
        transition_sequence.start()

        # Update breathing animation
        if status in [self.Status.ONLINE, self.Status.BUSY] and old_status not in [self.Status.ONLINE, self.Status.BUSY]:
            QTimer.singleShot(150, self._start_breathing_animation)
        elif status not in [self.Status.ONLINE, self.Status.BUSY] and self._breathing_timer:
            self._breathing_timer.stop()

    def setSize(self, size: int):
        """Set indicator size with optimized animation"""
        if self._size == size:
            return

        old_size = self._size
        self._size = size

        # Animate size change
        scale_factor = size / old_size
        FluentMicroInteraction.scale_animation(self, scale_factor)
        QTimer.singleShot(200, lambda: self.setFixedSize(size, size))

    def _on_theme_changed(self, _):
        """Handle theme changes with optimized updates"""
        self.update()
        if not self._is_animating:
            FluentMicroInteraction.pulse_animation(self, 1.02)

    def cleanup(self):
        """Cleanup resources and timers"""
        if self._breathing_timer:
            self._breathing_timer.stop()
            self._breathing_timer = None

        try:
            theme_manager.theme_changed.disconnect(self._on_theme_changed)
        except RuntimeError:
            pass
