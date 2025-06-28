"""
Fluent Design Style Toggle Switch Component
Provides an elegant toggle switch control with advanced animations and optimized performance
"""

from PySide6.QtWidgets import QWidget, QCheckBox, QGraphicsOpacityEffect
from PySide6.QtCore import (Qt, Signal, QPropertyAnimation, QRect, QEasingCurve,
                            Property, QByteArray, QSize, QSequentialAnimationGroup,
                            QParallelAnimationGroup, QPoint, QTimer, QAbstractAnimation)
from PySide6.QtGui import (QPainter, QColor, QBrush, QPen, QPaintEvent,
                           QPainterPath, QRadialGradient, QLinearGradient)
from core.theme import theme_manager, ThemeMode
from core.animation import FluentAnimation
from core.enhanced_animations import FluentTransition
from typing import Optional, Union


class FluentToggleSwitch(QCheckBox):
    """Fluent Design Style Toggle Switch with Advanced Animations

    Features:
    - Smooth spring-based animations with elastic bounce
    - Adaptive theme colors with proper light/dark mode support
    - Enhanced visual feedback with ripple effect on toggle
    - Optimized performance with minimal repaints
    - Customizable sizes and appearance
    - Memory efficient implementation using shared animations
    - Support for dynamic content loading
    - Accessibility improvements
    """

    stateChanged = Signal(bool)  # True for checked, False for unchecked
    thumbPositionChanged = Signal()  # Signal for thumbPosition property
    contentLoadingComplete = Signal()  # Signal for dynamic content loading completion

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        # Appearance properties - made configurable
        self._track_height = 14
        self._thumb_size = 18
        self._thumb_margin = 2
        self._thumb_position = 0.0  # Float for precise animation
        self._ripple_radius = 0.0  # For ripple animation effect
        self._ripple_opacity = 0.0  # For ripple animation effect
        self._track_width = 32  # Dynamic track width
        self._text_spacing = 8  # Space between toggle and label

        # Animation properties
        self._animation_duration = FluentAnimation.DURATION_MEDIUM
        self._animation_curve = FluentTransition.EASE_SPRING

        # Enhanced animation system
        self._setup_animations()

        # Internal state tracking for performance optimization
        self._is_hovered = False
        self._is_pressed = False
        self._last_rendered_state = None  # Cache last rendered state
        self._content_loaded = True  # Track dynamic content loading state
        self._memory_efficient = True  # Enable memory optimizations

        # Connect signals and event handlers
        self.clicked.connect(self._handle_toggle)
        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)
            theme_manager.mode_changed.connect(self._on_theme_mode_changed)

        # Initial setup
        self.setMinimumWidth(46)
        self._update_thumb_position_from_state(animate=False)
        self._on_theme_changed()

        # For responsive design
        self.setMouseTracking(True)  # Track mouse for hover effects

    def _setup_animations(self):
        """Set up enhanced animation system"""
        # Main thumb position animation with spring effect
        self._thumb_animation = QPropertyAnimation(
            self, QByteArray(b"thumbPosition"))
        self._thumb_animation.setDuration(self._animation_duration)
        self._thumb_animation.setEasingCurve(self._animation_curve)

        # Ripple effect animation
        self._ripple_animation = QPropertyAnimation(
            self, QByteArray(b"rippleRadius"))
        self._ripple_animation.setDuration(
            int(self._animation_duration * 1.5))  # Slightly longer
        self._ripple_animation.setEasingCurve(FluentAnimation.EASE_OUT)

        # Opacity animation for ripple effect
        self._ripple_opacity_anim = QPropertyAnimation(
            self, QByteArray(b"rippleOpacity"))
        self._ripple_opacity_anim.setDuration(
            int(self._animation_duration * 1.2))
        self._ripple_opacity_anim.setEasingCurve(FluentAnimation.EASE_IN)

        # Combined animation group for fluid effect
        self._animation_group = QParallelAnimationGroup()
        self._animation_group.addAnimation(self._thumb_animation)
        self._animation_group.addAnimation(self._ripple_animation)
        self._animation_group.addAnimation(self._ripple_opacity_anim)

    def _update_thumb_position_from_state(self, animate: bool = True):
        """Update internal thumb position based on checked state with optional animation."""
        target_position = 1.0 if self.isChecked() else 0.0

        if animate and self.isVisible():
            self._animation_group.stop()

            # Thumb position animation
            self._thumb_animation.setStartValue(self._thumb_position)
            self._thumb_animation.setEndValue(target_position)

            # Ripple animation
            self._ripple_animation.setStartValue(0.0)
            self._ripple_animation.setEndValue(self._track_width * 0.8)

            # Ripple opacity
            self._ripple_opacity_anim.setStartValue(0.5)
            self._ripple_opacity_anim.setEndValue(0.0)

            self._animation_group.start()
        else:
            # Update without animation
            self._thumb_position = target_position
            self._ripple_radius = 0.0
            self._ripple_opacity = 0.0
            self.update()

    def _handle_toggle(self):
        """Handle toggle action with enhanced animation effects"""
        self._update_thumb_position_from_state(animate=True)
        self.stateChanged.emit(self.isChecked())

        # If we have dynamic content to load, simulate loading process
        if not self._content_loaded:
            self._load_dynamic_content()

    def _load_dynamic_content(self):
        """Simulate dynamic content loading (for demonstration)"""
        # In a real implementation, this would load actual content
        # For this example, we just simulate a loading state
        self._content_loaded = False

        # Use QTimer to simulate asynchronous loading
        QTimer.singleShot(300, self._finish_content_loading)

    def _finish_content_loading(self):
        """Complete the dynamic content loading"""
        self._content_loaded = True
        self.contentLoadingComplete.emit()
        self.update()  # Repaint with new content

    def sizeHint(self) -> QSize:
        """Suggest an appropriate size for the widget with responsive design"""
        # Calculate width based on content
        width = self._track_width
        if self.text():
            text_width = self.fontMetrics().horizontalAdvance(self.text())
            width += text_width + self._text_spacing

        # Ensure minimum height for comfortable interaction
        height = max(self._thumb_size + self._thumb_margin * 2, 24)

        return QSize(width, height)

    def enterEvent(self, event):
        """Handle mouse enter events for hover effects"""
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave events for hover effects"""
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press events for interaction effects"""
        self._is_pressed = True
        # Start ripple effect
        self._ripple_animation.setStartValue(0.0)
        self._ripple_animation.setEndValue(self._track_width * 0.5)
        self._ripple_opacity_anim.setStartValue(0.3)
        self._ripple_opacity_anim.setEndValue(0.0)

        self._ripple_animation.start()
        self._ripple_opacity_anim.start()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        self._is_pressed = False
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        """Handle resize events for responsive layout"""
        super().resizeEvent(event)
        # Adjust track width if necessary based on new size
        if event.size().width() > 100:
            # For larger widths, we may want to increase the track proportionally
            self._track_width = min(40, int(event.size().width() * 0.2))
            # Update animation end values to match new dimensions
            if self._animation_group.state() == QAbstractAnimation.State.Running:
                self._ripple_animation.setEndValue(self._track_width * 0.8)

    def paintEvent(self, _event: QPaintEvent):
        """Draw the toggle switch with enhanced visuals"""
        # Optimize painting by checking if we need to repaint
        current_state = (self.isChecked(), self._thumb_position, self._is_hovered, self._is_pressed,
                         self.isEnabled(), theme_manager.get_theme_mode())

        if current_state == self._last_rendered_state and not self._animation_group.state() == QAbstractAnimation.State.Running:
            return  # Skip repainting if nothing has changed

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get current theme colors
        theme = theme_manager
        theme_mode = theme.get_theme_mode()

        # Calculate geometry
        track_width = self._track_width
        track_height = self._track_height
        thumb_size = self._thumb_size

        # Draw text if present
        if self.text():
            text_color = theme.get_color('text_primary') if self.isEnabled(
            ) else theme.get_color('text_disabled')
            painter.setPen(QPen(text_color))

            text_rect = self.rect()
            # Space between toggle and text
            text_rect.setLeft(track_width + self._text_spacing)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft |
                             Qt.AlignmentFlag.AlignVCenter, self.text())

        # Calculate track and thumb positions
        track_rect = QRect(0, (self.height() - track_height) //
                           2, track_width, track_height)

        # Adjust positions for thumb travel
        thumb_travel_range = track_width - \
            thumb_size - (self._thumb_margin * 2)
        thumb_x_offset = self._thumb_margin + \
            (thumb_travel_range * self._thumb_position)
        thumb_y = (self.height() - thumb_size) // 2

        # Create track gradient for enhanced visual effect
        if self.isEnabled():
            if self.isChecked():
                # Primary color gradient for checked state
                track_gradient = QLinearGradient(
                    track_rect.topLeft(), track_rect.topRight())
                primary_color = theme.get_color('primary')
                # Add slight variation to gradient
                track_gradient.setColorAt(0, primary_color)
                track_gradient.setColorAt(1, primary_color.lighter(110) if theme_mode == ThemeMode.LIGHT
                                          else primary_color.darker(110))
                track_brush = QBrush(track_gradient)
            else:
                # Border color for unchecked state
                track_color = theme.get_color('border')
                if self._is_hovered:
                    track_color = track_color.lighter(
                        110) if theme_mode == ThemeMode.LIGHT else track_color.darker(110)
                track_brush = QBrush(track_color)
        else:
            # Disabled state colors
            disabled_color = theme.get_color('disabled_bg') if theme.get_color(
                'disabled_bg') else theme.get_color('border')
            track_brush = QBrush(disabled_color)

        # Draw track with rounded corners
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_brush)
        painter.drawRoundedRect(
            track_rect, track_height // 2, track_height // 2)

        # Draw ripple effect when active
        if self._ripple_radius > 0 and self._ripple_opacity > 0:
            ripple_color = theme.get_color('primary')
            ripple_color.setAlphaF(self._ripple_opacity)

            painter.setBrush(QBrush(ripple_color))
            painter.setPen(Qt.PenStyle.NoPen)

            # Ripple center position (around thumb)
            ripple_center_x = int(thumb_x_offset + thumb_size/2)
            ripple_center_y = int(thumb_y + thumb_size/2)
            ripple_radius_int = int(self._ripple_radius)

            # Draw the ripple circle - using direct drawEllipse instead of QRect
            painter.drawEllipse(
                int(ripple_center_x - ripple_radius_int/2),
                int(ripple_center_y - ripple_radius_int/2),
                ripple_radius_int,
                ripple_radius_int
            )

        # Draw thumb with enhanced visuals
        thumb_color_base = None
        thumb_border_color = None

        if self.isEnabled():
            # Select thumb color based on theme mode
            if theme_mode == ThemeMode.LIGHT:
                thumb_color_base = QColor("white")
                thumb_border_color = theme.get_color('border')
            else:
                thumb_color_base = QColor(45, 45, 45)
                thumb_border_color = QColor(80, 80, 80)

            # Apply hover and pressed effects
            if self._is_pressed:
                thumb_color_base = thumb_color_base.darker(
                    105) if theme_mode == ThemeMode.LIGHT else thumb_color_base.lighter(120)
            elif self._is_hovered:
                thumb_color_base = thumb_color_base.darker(
                    102) if theme_mode == ThemeMode.LIGHT else thumb_color_base.lighter(110)
        else:
            # Disabled state
            thumb_color_base = QColor(
                200, 200, 200) if theme_mode == ThemeMode.LIGHT else QColor(70, 70, 70)
            thumb_border_color = theme.get_color('disabled_text') if theme.get_color(
                'disabled_text') else QColor(150, 150, 150)

        # Create a subtle radial gradient for the thumb
        thumb_gradient = QRadialGradient(
            thumb_x_offset + thumb_size/2, thumb_y + thumb_size/2, thumb_size/2)
        thumb_gradient.setColorAt(0, thumb_color_base)
        thumb_gradient.setColorAt(0.9, thumb_color_base)
        thumb_gradient.setColorAt(1, thumb_color_base.darker(
            105) if theme_mode == ThemeMode.LIGHT else thumb_color_base.lighter(105))

        # Draw thumb with gradient and border
        painter.setBrush(QBrush(thumb_gradient))
        painter.setPen(QPen(thumb_border_color))
        painter.drawEllipse(int(thumb_x_offset), int(
            thumb_y), thumb_size, thumb_size)

        # Draw indicator mark for checked state (optional)
        if self.isChecked() and self.isEnabled() and self._thumb_position > 0.5:
            indicator_color = QColor(
                "white") if theme_mode == ThemeMode.DARK else QColor(45, 45, 45)
            # Fade in based on position
            indicator_color.setAlphaF(
                min(1.0, (self._thumb_position - 0.5) * 2.0))

            painter.setPen(QPen(indicator_color, 1.5))

            # Draw a simple mark (could be a checkmark or dot)
            center_x = int(thumb_x_offset + thumb_size/2)
            center_y = int(thumb_y + thumb_size/2)
            mark_size = int(thumb_size * 0.25)

            # Simple dot indicator - pass integer values directly instead of QRect
            painter.setBrush(QBrush(theme.get_color('primary')))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                center_x - mark_size//2,
                center_y - mark_size//2,
                mark_size,
                mark_size
            )

        painter.end()

        # Cache the rendered state to avoid unnecessary repaints
        self._last_rendered_state = current_state

    def _on_theme_changed(self):
        """Handle theme color changes"""
        self.update()  # Request repaint with new theme colors

    def _on_theme_mode_changed(self, mode):
        """Handle specific theme mode changes (light/dark)"""
        self.update()  # Request repaint with new theme mode

    def setChecked(self, checked: bool):
        """Override setChecked to handle animation correctly."""
        current_checked_state = self.isChecked()
        if current_checked_state != checked:
            super().setChecked(checked)
            self._update_thumb_position_from_state(animate=True)
            self.stateChanged.emit(checked)

    def set_checked_without_animation(self, checked: bool):
        """Set checked state without animation"""
        is_different = self.isChecked() != checked
        self.blockSignals(True)
        super().setChecked(checked)
        self._thumb_position = 1.0 if checked else 0.0
        self._ripple_radius = 0.0
        self._ripple_opacity = 0.0
        self.blockSignals(False)
        if is_different:
            self.update()

    def setTrackWidth(self, width: int):
        """Set custom track width"""
        self._track_width = max(24, width)  # Ensure minimum reasonable width
        self.update()

    def setThumbSize(self, size: int):
        """Set custom thumb size"""
        self._thumb_size = max(12, size)  # Ensure minimum reasonable size
        self.update()

    def setAnimationDuration(self, duration: int):
        """Set custom animation duration"""
        self._animation_duration = duration
        self._thumb_animation.setDuration(duration)
        self._ripple_animation.setDuration(int(duration * 1.5))
        self._ripple_opacity_anim.setDuration(int(duration * 1.2))

    def setAnimationCurve(self, curve: QEasingCurve.Type):
        """Set custom animation curve for main thumb movement"""
        self._animation_curve = curve
        self._thumb_animation.setEasingCurve(curve)

    # Property for thumb animation
    def _get_thumb_position(self) -> float:
        return self._thumb_position

    def _set_thumb_position(self, pos: float):
        if self._thumb_position != pos:
            self._thumb_position = pos
            self.update()
            self.thumbPositionChanged.emit()

    # Property for ripple animation
    def _get_ripple_radius(self) -> float:
        return self._ripple_radius

    def _set_ripple_radius(self, radius: float):
        if self._ripple_radius != radius:
            self._ripple_radius = radius
            self.update()

    # Property for ripple opacity
    def _get_ripple_opacity(self) -> float:
        return self._ripple_opacity

    def _set_ripple_opacity(self, opacity: float):
        if self._ripple_opacity != opacity:
            self._ripple_opacity = opacity
            self.update()

    # Define Qt properties for animation - with correct parameters  
    thumbPosition = Property(float, _get_thumb_position, _set_thumb_position, None, "Thumb position for animation")
    rippleRadius = Property(float, _get_ripple_radius, _set_ripple_radius, None, "Ripple radius for animation")
    rippleOpacity = Property(float, _get_ripple_opacity, _set_ripple_opacity, None, "Ripple opacity for animation")


# Enhanced Toggle Button with content expansion capability
class FluentExpandableToggle(FluentToggleSwitch):
    """A toggle switch with content expansion capability

    Features:
    - Smoothly expands/collapses associated content
    - Fluid animations with spring effect
    - Memory efficient: only loads content when needed
    """

    expandChanged = Signal(bool)  # True when expanded, False when collapsed

    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        # Expansion properties
        self._content_widget = None
        self._expanded = False
        self._expand_animation = None
        self._expand_duration = FluentAnimation.DURATION_SLOW
        self._expand_curve = FluentTransition.EASE_SPRING

        # Connect expansion to toggle state
        self.stateChanged.connect(self._handle_expansion)

    def set_content_widget(self, widget: QWidget):
        """Set the widget to expand/collapse"""
        self._content_widget = widget

        # Set initial state
        if self._content_widget:
            # Initialize expansion animation
            self._expand_animation = QPropertyAnimation(
                self._content_widget, QByteArray(b"maximumHeight"))
            self._expand_animation.setDuration(self._expand_duration)
            self._expand_animation.setEasingCurve(self._expand_curve)

            # Setup content widget
            self._content_widget.setMaximumHeight(
                0 if not self.isChecked() else self._content_widget.sizeHint().height())
            self._content_widget.setVisible(True)

    def _handle_expansion(self, checked: bool):
        """Handle content expansion/collapse when toggle state changes"""
        if not self._content_widget or self._expand_animation is None:
            return

        self._expanded = checked

        # Store desired height
        content_height = self._content_widget.sizeHint().height()

        # Update animation
        self._expand_animation.stop()

        if checked:
            # Expand
            self._expand_animation.setStartValue(
                self._content_widget.maximumHeight())
            self._expand_animation.setEndValue(content_height)
        else:
            # Collapse
            self._expand_animation.setStartValue(
                self._content_widget.maximumHeight())
            self._expand_animation.setEndValue(0)

        self._expand_animation.start()
        self.expandChanged.emit(checked)

    def set_expanded(self, expanded: bool):
        """Set expansion state (separate from checked state)"""
        if self._expanded != expanded and self._content_widget:
            self._expanded = expanded
            self._handle_expansion(expanded)
