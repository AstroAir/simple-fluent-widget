"""
Fluent Design Style Card Component - Optimized Version
Enhanced performance, consistent theming, and smooth animations
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, Property, QByteArray, QTimer, QParallelAnimationGroup
from PySide6.QtGui import QPainter, QPainterPath, QColor, QBrush, QPixmap, QFont
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                      FluentRevealEffect, FluentSequence)
from typing import Optional, Dict, Any
import weakref


class FluentCard(QFrame):
    """Fluent Design style card component with optimized animations and consistent theming"""

    # Signals
    clicked = Signal()
    hoverProgressChanged = Signal(float)
    pressProgressChanged = Signal(float)
    currentElevationChanged = Signal(float)

    # Class-level animation cache for performance
    _animation_cache: Dict[str, Any] = {}

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Core properties
        self._clickable = False
        self._elevation = 2
        self._hover_elevation = 4
        self._corner_radius = 8
        self._current_elevation = 2.0
        self._hover_progress = 0.0
        self._press_progress = 0.0
        
        # Performance optimizations
        self._style_cache = {}
        self._shadow_cache = {}
        self._theme_version = 0
        
        # Animation groups for better performance
        self._hover_group = None
        self._press_group = None
        
        # Weak reference to prevent memory leaks
        self._active_animations = weakref.WeakSet()

        self._setup_ui()
        self._setup_optimized_style()
        self._setup_optimized_animations()
        self._setup_optimized_shadow()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI components"""
        self.setFrameStyle(QFrame.Shape.NoFrame)

        # Main layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)
        
    def _setup_optimized_style(self):
        """Setup component style with caching and theme consistency"""
        theme = theme_manager
        current_theme_version = getattr(theme, '_version', 0)
        
        # Check cache validity
        cache_key = f"{self._corner_radius}_{current_theme_version}"
        if cache_key in self._style_cache and self._theme_version == current_theme_version:
            self.setStyleSheet(self._style_cache[cache_key])
            return
        
        # Generate optimized stylesheet with consistent theming
        style_sheet = f"""
            FluentCard {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: {self._corner_radius}px;
                /* Remove transition from CSS for better performance */
            }}
            FluentCard:hover {{
                border-color: {theme.get_color('primary').name()};
            }}
            FluentCard[clickable="true"] {{
                cursor: pointer;
            }}
            FluentCard[clickable="true"]:hover {{
                background-color: {theme.get_color('surface_variant').name()};
            }}
        """
        
        # Cache the stylesheet
        self._style_cache[cache_key] = style_sheet
        self._theme_version = current_theme_version
        self.setStyleSheet(style_sheet)
        
        # Set property for CSS selector
        self.setProperty("clickable", self._clickable)
        
    def _setup_optimized_animations(self):
        """Setup optimized animation system with better performance"""
        # Create animation groups for better coordination
        self._hover_group = QParallelAnimationGroup(self)
        self._press_group = QParallelAnimationGroup(self)
        
        # Optimized hover animation with smooth easing
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_progress"), self)
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
        self._hover_group.addAnimation(self._hover_animation)

        # Optimized press animation with crisp response
        self._press_animation = QPropertyAnimation(
            self, QByteArray(b"press_progress"), self)
        self._press_animation.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
        self._press_animation.setEasingCurve(FluentTransition.EASE_CRISP)
        self._press_group.addAnimation(self._press_animation)

        # Optimized elevation animation with spring effect
        self._elevation_animation = QPropertyAnimation(
            self, QByteArray(b"current_elevation"), self)
        self._elevation_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._elevation_animation.setEasingCurve(FluentTransition.EASE_SPRING)
        self._hover_group.addAnimation(self._elevation_animation)

        # Add to active animations for cleanup
        self._active_animations.add(self._hover_group)
        self._active_animations.add(self._press_group)

        # Delayed entrance animation for performance
        QTimer.singleShot(100, self._show_optimized_entrance_animation)
        
    def _show_optimized_entrance_animation(self):
        """Show optimized entrance animation with performance considerations"""
        # Only animate if widget is visible to improve performance
        if not self.isVisible():
            return
            
        entrance_sequence = FluentSequence(self)

        # Optimized fade in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self, 250))
        entrance_sequence.addPause(50)  # Reduced pause for snappier feel

        # Optimized scale in effect with subtle bounce
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.scale_in(self, 200))

        entrance_sequence.start()
        self._active_animations.add(entrance_sequence)
        
    def _setup_optimized_shadow(self):
        """Setup optimized drop shadow effect with caching"""
        self._shadow = QGraphicsDropShadowEffect(self)
        self._update_optimized_shadow()
        self.setGraphicsEffect(self._shadow)
        
    def _update_optimized_shadow(self):
        """Update shadow with caching and optimized parameters"""
        theme = theme_manager
        elevation_key = f"{self._current_elevation}_{self._theme_version}"
        
        # Check shadow cache
        if elevation_key in self._shadow_cache:
            cached_shadow = self._shadow_cache[elevation_key]
            self._shadow.setBlurRadius(cached_shadow['blur'])
            self._shadow.setOffset(cached_shadow['offset_x'], cached_shadow['offset_y'])
            self._shadow.setColor(cached_shadow['color'])
            return

        # Calculate optimized shadow parameters
        blur_radius = max(2, self._current_elevation * 2.5)  # More subtle blur
        offset_y = max(1, int(self._current_elevation * 0.8))  # More natural offset
        offset_x = 0  # Keep horizontal offset at 0 for cleaner look

        # Optimized shadow color with better alpha calculation
        shadow_color = QColor(theme.get_color('shadow'))
        alpha = min(100, int(40 + self._current_elevation * 8))  # More subtle shadow
        shadow_color.setAlpha(alpha)

        # Cache the shadow parameters
        self._shadow_cache[elevation_key] = {
            'blur': blur_radius,
            'offset_x': offset_x,
            'offset_y': offset_y,
            'color': shadow_color
        }

        # Apply shadow settings
        self._shadow.setBlurRadius(blur_radius)
        self._shadow.setOffset(offset_x, offset_y)
        self._shadow.setColor(shadow_color)

    # Enhanced property getters and setters
    def _get_hover_progress(self):
        return self._hover_progress

    def _set_hover_progress(self, value):
        if self._hover_progress != value:
            self._hover_progress = value
            self.hoverProgressChanged.emit(value)
            self.update()

    def _get_press_progress(self):
        return self._press_progress

    def _set_press_progress(self, value):
        if self._press_progress != value:
            self._press_progress = value
            self.pressProgressChanged.emit(value)
            self.update()

    def _get_current_elevation(self):
        return self._current_elevation
        
    def _set_current_elevation(self, value):
        if self._current_elevation != value:
            self._current_elevation = value
            self.currentElevationChanged.emit(value)
            self._update_optimized_shadow()

    hover_progress = Property(float, _get_hover_progress, _set_hover_progress, None, "",
                              notify=hoverProgressChanged)
    press_progress = Property(float, _get_press_progress, _set_press_progress, None, "",
                              notify=pressProgressChanged)
    current_elevation = Property(float, _get_current_elevation, _set_current_elevation, None, "",
                                 notify=currentElevationChanged)

    def isClickable(self) -> bool:
        """Check if the card is clickable"""
        return self._clickable

    def getElevation(self) -> int:
        """Get the card elevation"""
        return int(self._elevation)


    def setHoverElevation(self, elevation: int):
        """Set the elevation when hovered with validation"""
        self._hover_elevation = max(self._elevation, float(elevation))

    def getHoverElevation(self) -> int:
        """Get the hover elevation"""
        return int(self._hover_elevation)
        
    def setCornerRadius(self, radius: int):
        """Set the corner radius with optimized transition"""
        new_radius = max(0, radius)
        if self._corner_radius != new_radius:
            self._corner_radius = new_radius
            # Clear style cache to force refresh
            self._style_cache.clear()
            self._setup_optimized_style()
            FluentMicroInteraction.pulse_animation(self, 1.005)  # Subtle animation

    def getCornerRadius(self) -> int:
        """Get the corner radius"""
        return self._corner_radius

    # Enhanced layout management methods    def addWidget(self, widget: QWidget):
        """Add a widget to the card's main layout with optimized animation"""
        widget.setParent(self)
        self._layout.addWidget(widget)

        # Only animate if widget is visible for better performance
        if self.isVisible():
            FluentRevealEffect.slide_in(widget, 200, "up")

    def insertWidget(self, index: int, widget: QWidget):
        """Insert a widget at the specified index with optimized animation"""
        widget.setParent(self)
        self._layout.insertWidget(index, widget)

        # Optimized entrance animation
        if self.isVisible():
            FluentRevealEffect.scale_in(widget, 150)

    def removeWidget(self, widget: QWidget):
        """Remove a widget from the card with optimized animation"""
        if widget in [self._layout.itemAt(i).widget() for i in range(self._layout.count()) if self._layout.itemAt(i).widget()]:
            # Optimized removal animation
            removal_sequence = FluentSequence(self)
            removal_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(widget, 0.0))
            removal_sequence.addPause(150)  # Reduced pause
            removal_sequence.addCallback(
                lambda: self._complete_widget_removal(widget))
            removal_sequence.start()
            self._active_animations.add(removal_sequence)

    def _complete_widget_removal(self, widget: QWidget):
        """Complete widget removal"""
        self._layout.removeWidget(widget)
        widget.setParent(None)

    def addLayout(self, layout):
        """Add a layout to the card's main layout"""
        self._layout.addLayout(layout)

    def addStretch(self, stretch: int = 0):
        """Add stretch to the card's main layout"""
        self._layout.addStretch(stretch)
        
    def setMargins(self, left: int, top: int, right: int, bottom: int):
        """Set content margins with optimized transition"""
        self._layout.setContentsMargins(left, top, right, bottom)
        # Reduced animation intensity for better performance
        FluentMicroInteraction.pulse_animation(self, 1.005)

    def setSpacing(self, spacing: int):
        """Set layout spacing with optimized transition"""
        self._layout.setSpacing(max(0, spacing))
        # Reduced animation intensity for better performance
        FluentMicroInteraction.pulse_animation(self, 1.005)

    def setClickable(self, clickable: bool):
        """Set whether the card is clickable with optimized feedback"""
        if self._clickable != clickable:
            self._clickable = clickable
            
            # Update CSS property for styling
            self.setProperty("clickable", clickable)
            self._setup_optimized_style()

            if clickable:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                # Subtle hover indication
                FluentMicroInteraction.pulse_animation(self, 1.01)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def setElevation(self, elevation: int):
        """Set the card elevation with optimized animation"""
        new_elevation = max(0, float(elevation))
        if self._elevation != new_elevation:
            old_elevation = self._current_elevation
            self._elevation = new_elevation

            # Optimized elevation animation
            self._elevation_animation.setStartValue(old_elevation)
            self._elevation_animation.setEndValue(new_elevation)
            self._elevation_animation.start()

    def cleanup(self):
        """Cleanup method to prevent memory leaks"""
        # Stop all active animations
        for animation in list(self._active_animations):
            if animation and hasattr(animation, 'stop'):
                animation.stop()
        
        # Clear caches
        self._style_cache.clear()
        self._shadow_cache.clear()
        
        # Clear animation groups
        if self._hover_group:
            self._hover_group.stop()
            self._hover_group = None
        if self._press_group:
            self._press_group.stop()
            self._press_group = None

    # Enhanced event handlers
    
    def enterEvent(self, event):
        """Handle mouse enter with optimized animation coordination"""
        if self._clickable:
            # Stop any running animations first
            if self._hover_group and self._hover_group.state() == QParallelAnimationGroup.State.Running:
                self._hover_group.stop()

            # Coordinated hover animation
            self._hover_animation.setStartValue(self._hover_progress)
            self._hover_animation.setEndValue(1.0)
            self._elevation_animation.setStartValue(self._current_elevation)
            self._elevation_animation.setEndValue(self._hover_elevation)
            
            # Start coordinated animation group if exists
            if self._hover_group:
                self._hover_group.start()

            # Optimized hover glow effect (reduced intensity)
            FluentMicroInteraction.hover_glow(self, 0.05)

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave with optimized animation coordination"""
        if self._clickable:
            # Stop any running animations first
            if self._hover_group and self._hover_group.state() == QParallelAnimationGroup.State.Running:
                self._hover_group.stop()

            # Coordinated return animation
            self._hover_animation.setStartValue(self._hover_progress)
            self._hover_animation.setEndValue(0.0)
            self._elevation_animation.setStartValue(self._current_elevation)
            self._elevation_animation.setEndValue(self._elevation)
            
            # Start coordinated animation group if exists
            if self._hover_group:
                self._hover_group.start()

            # Remove glow effect
            FluentMicroInteraction.hover_glow(self, -0.05)

        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        """Handle mouse press with optimized animation response"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            # Stop any running press animations
            if self._press_group and self._press_group.state() == QParallelAnimationGroup.State.Running:
                self._press_group.stop()

            # Optimized press animation (more responsive)
            self._press_animation.setStartValue(self._press_progress)
            self._press_animation.setEndValue(1.0)
            if self._press_group:
                if self._press_group:
                    self._press_group.start()

            # Subtle scale down effect (reduced scale change)
            FluentMicroInteraction.button_press(self, 0.995)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release with optimized feedback"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            # Stop any running press animations
            if self._press_group and self._press_group.state() == QParallelAnimationGroup.State.Running:
                self._press_group.stop()

            # Quick release animation
            self._press_animation.setStartValue(self._press_progress)
            self._press_animation.setEndValue(0.0)
            if self._press_group:
                self._press_group.start()

            # Emit clicked signal if mouse is still over widget
            if self.rect().contains(event.position().toPoint()):
                # Optimized ripple effect with shorter delay
                FluentMicroInteraction.ripple_effect(self)
                QTimer.singleShot(50, self.clicked.emit)  # Faster response

        super().mouseReleaseEvent(event)
        
    def paintEvent(self, event):
        """Paint the card with optimized custom effects and better performance"""
        super().paintEvent(event)

        # Only paint custom effects if there's actual progress to show
        if self._hover_progress <= 0 and self._press_progress <= 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Create optimized card path (cached if possible)
        rect_adjusted = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect_adjusted, self._corner_radius - 1, self._corner_radius - 1)

        theme = theme_manager

        # Draw optimized hover effect with better blending
        if self._hover_progress > 0:
            hover_color = QColor(theme.get_color('accent_light'))
            # Smoother opacity curve
            opacity = 0.08 * self._hover_progress * self._hover_progress  # Quadratic easing
            hover_color.setAlphaF(opacity)
            painter.fillPath(path, QBrush(hover_color))

        # Draw optimized press effect with subtle feedback
        if self._press_progress > 0:
            press_color = QColor(theme.get_color('primary'))
            # More subtle press effect with better curve
            opacity = 0.05 * self._press_progress
            press_color.setAlphaF(opacity)
            painter.fillPath(path, QBrush(press_color))

        painter.end()  # Explicit cleanup for better performance
        
    def _on_theme_changed(self, _=None):
        """Handle theme change with optimized transition"""
        # Clear caches to force refresh
        self._style_cache.clear()
        self._shadow_cache.clear()
        
        # Update styling
        self._setup_optimized_style()
        self._update_optimized_shadow()
        
        # Subtle theme transition animation
        FluentMicroInteraction.pulse_animation(self, 1.01)
        self.update()


class FluentImageCard(FluentCard):
    """Card with image header and enhanced image handling"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._image_label: QLabel  # Remove Optional, guaranteed to be created
        self._image_height = 200
        self._original_pixmap: Optional[QPixmap] = None

        self._setup_image_ui()

    def _setup_image_ui(self):
        """Setup image UI with enhanced styling"""
        # Create image label with enhanced properties
        self._image_label = QLabel()  # Now guaranteed to not be None
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setMinimumHeight(self._image_height)
        self._image_label.setMaximumHeight(self._image_height)
        self._image_label.setScaledContents(True)  # Enable scaling

        # Enhanced styling for image area
        theme = theme_manager
        self._image_label.setStyleSheet(f"""
            QLabel {{
                background-color: {theme.get_color('surface_variant').name()};
                border-top-left-radius: {self.getCornerRadius()}px;
                border-top-right-radius: {self.getCornerRadius()}px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                border: none;
            }}
        """)

        # Insert at the beginning of the main layout
        self._layout.insertWidget(0, self._image_label)

        # Adjust layout margins for image card
        self._layout.setContentsMargins(16, 0, 16, 16)

        # Add entrance animation for image area - now safe without None check
        QTimer.singleShot(100, lambda: FluentRevealEffect.slide_in(
            self._image_label, 300, "up"))

    def setImage(self, pixmap: QPixmap):
        """Set the card image with transition and proper scaling"""
        if not pixmap.isNull():
            self._original_pixmap = pixmap

            # Enhanced scaling with proper aspect ratio handling
            scaled_pixmap = pixmap.scaled(
                self._image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )

            # Create transition effect - now safe without None check
            transition_sequence = FluentSequence(self)
            transition_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self._image_label, 0.95))
            transition_sequence.addPause(150)
            transition_sequence.addCallback(
                lambda: self._image_label.setPixmap(scaled_pixmap))
            transition_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self._image_label, 1.0))
            transition_sequence.start()

    def setImageHeight(self, height: int):
        """Set the image height with animation"""
        new_height = max(100, height)  # Minimum height validation
        if self._image_height != new_height:
            self._image_height = new_height

            # Animate height change - now safe without None check
            old_height = self._image_label.height()

            height_animation = QPropertyAnimation(
                self._image_label, QByteArray(b"minimumHeight"))
            height_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
            height_animation.setEasingCurve(FluentTransition.EASE_SPRING)
            height_animation.setStartValue(old_height)
            height_animation.setEndValue(new_height)
            height_animation.finished.connect(
                lambda: self._image_label.setMaximumHeight(new_height))
            height_animation.start()

            # Re-scale image if it exists
            if self._original_pixmap and not self._original_pixmap.isNull():
                QTimer.singleShot(200, lambda: self.setImage(
                    self._original_pixmap) if self._original_pixmap else None)

    def getImageHeight(self) -> int:
        """Get the current image height"""
        return self._image_height

    def clearImage(self):
        """Clear the image with animation"""
        # Animate image removal - now safe without None check
        clear_sequence = FluentSequence(self)
        clear_sequence.addCallback(lambda: FluentRevealEffect.fade_in(
            self._image_label, 200))  # Fade out
        clear_sequence.addPause(200)
        clear_sequence.addCallback(lambda: self._image_label.clear())
        clear_sequence.addCallback(lambda: FluentRevealEffect.fade_in(
            self._image_label, 200))  # Fade back in
        clear_sequence.start()

        self._original_pixmap = None


class FluentActionCard(FluentCard):
    """Card with action buttons and enhanced action management"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._action_layout: QHBoxLayout  # Remove Optional, guaranteed to be created
        self._action_widgets: list = []

        self._setup_action_ui()

    def _setup_action_ui(self):
        """Setup action UI with enhanced styling"""
        # Create action area at the bottom
        self._action_layout = QHBoxLayout()  # Now guaranteed to not be None
        self._action_layout.setContentsMargins(0, 12, 0, 0)
        self._action_layout.setSpacing(8)  # Enhanced spacing
        self._action_layout.addStretch()  # Right-align actions by default

        # Add separator line above actions
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        theme = theme_manager
        separator.setStyleSheet(f"""
            QFrame {{
                color: {theme.get_color('border').name()};
                background-color: {theme.get_color('border').name()};
                height: 1px;
                border: none;
            }}
        """)

        self._layout.addWidget(separator)
        self._layout.addLayout(self._action_layout)

    def addActionWidget(self, widget: QWidget):
        """Add an action widget with animation"""
        if widget not in self._action_widgets:
            widget.setParent(self)
            self._action_widgets.append(widget)

            # Insert before the stretch - now safe without None check
            self._action_layout.insertWidget(
                self._action_layout.count() - 1, widget)

            # Add entrance animation
            FluentRevealEffect.slide_in(widget, 200, "up")

    def removeActionWidget(self, widget: QWidget):
        """Remove an action widget with animation"""
        if widget in self._action_widgets:
            # Animate removal
            removal_sequence = FluentSequence(self)
            removal_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(widget, 0.0))
            removal_sequence.addPause(200)
            removal_sequence.addCallback(
                lambda: self._complete_action_removal(widget))
            removal_sequence.start()

    def _complete_action_removal(self, widget: QWidget):
        """Complete action widget removal"""
        if widget in self._action_widgets:
            self._action_widgets.remove(widget)
            self._action_layout.removeWidget(
                widget)  # Now safe without None check
            widget.setParent(None)

    def clearActions(self):
        """Clear all action widgets with staggered animation"""
        if self._action_widgets:
            # Staggered removal animation
            for i, widget in enumerate(self._action_widgets.copy()):
                QTimer.singleShot(
                    i * 100, lambda w=widget: self.removeActionWidget(w))

    def getActionCount(self) -> int:
        """Get the number of action widgets"""
        return len(self._action_widgets)

    def setActionAlignment(self, alignment: Qt.AlignmentFlag):
        """Set the alignment of action widgets"""
        # Remove existing stretch - now safe without None check
        for i in range(self._action_layout.count()):
            item = self._action_layout.itemAt(i)
            if item and item.spacerItem():
                self._action_layout.removeItem(item)
                break

        # Add stretch based on alignment
        if alignment == Qt.AlignmentFlag.AlignLeft:
            self._action_layout.addStretch()
        elif alignment == Qt.AlignmentFlag.AlignCenter:
            self._action_layout.insertStretch(0)
            self._action_layout.addStretch()
        elif alignment == Qt.AlignmentFlag.AlignRight:
            self._action_layout.insertStretch(0)

        # Add transition effect
        FluentMicroInteraction.pulse_animation(self, 1.01)


class FluentInfoCard(FluentCard):
    """Specialized card for displaying information with icon and text"""

    def __init__(self, title: str = "", subtitle: str = "", icon: str = "",
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title_label: QLabel    # Remove Optional, guaranteed to be created
        self._subtitle_label: QLabel  # Remove Optional, guaranteed to be created
        self._icon_label: QLabel     # Remove Optional, guaranteed to be created

        self._setup_info_ui()
        self.setTitle(title)
        self.setSubtitle(subtitle)
        self.setIcon(icon)

    def _setup_info_ui(self):
        """Setup information card UI"""
        # Create header layout for icon and text
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Icon label
        self._icon_label = QLabel()  # Now guaranteed to not be None
        self._icon_label.setFixedSize(48, 48)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setStyleSheet("""
            QLabel {
                border-radius: 24px;
                background-color: rgba(0, 120, 215, 0.1);
                color: #0078d4;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        # Text layout
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        # Title label
        self._title_label = QLabel()  # Now guaranteed to not be None
        title_font = self._title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self._title_label.setFont(title_font)

        # Subtitle label
        self._subtitle_label = QLabel()  # Now guaranteed to not be None
        subtitle_font = self._subtitle_label.font()
        subtitle_font.setPointSize(10)
        self._subtitle_label.setFont(subtitle_font)

        theme = theme_manager
        self._subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: {theme.get_color('text_secondary').name()};
            }}
        """)

        text_layout.addWidget(self._title_label)
        text_layout.addWidget(self._subtitle_label)
        text_layout.addStretch()

        header_layout.addWidget(self._icon_label)
        header_layout.addLayout(text_layout)

        # Insert header at the top
        self._layout.insertLayout(0, header_layout)

        # Add entrance animations - now safe without None checks
        QTimer.singleShot(100, lambda: FluentRevealEffect.slide_in(
            self._icon_label, 200, "left"))
        QTimer.singleShot(150, lambda: FluentRevealEffect.slide_in(
            self._title_label, 200, "right"))
        QTimer.singleShot(200, lambda: FluentRevealEffect.slide_in(
            self._subtitle_label, 200, "right"))

    def setTitle(self, title: str):
        """Set the card title with animation"""
        if self._title_label.text() != title:
            self._title_label.setText(title)
            FluentMicroInteraction.pulse_animation(self._title_label, 1.02)

    def setSubtitle(self, subtitle: str):
        """Set the card subtitle with animation"""
        if self._subtitle_label.text() != subtitle:
            self._subtitle_label.setText(subtitle)
            FluentMicroInteraction.pulse_animation(self._subtitle_label, 1.02)

    def setIcon(self, icon: str):
        """Set the card icon with animation"""
        if self._icon_label.text() != icon:
            # Animate icon change - now safe without None checks
            icon_sequence = FluentSequence(self)
            icon_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self._icon_label, 0.8))
            icon_sequence.addPause(100)
            icon_sequence.addCallback(lambda: self._icon_label.setText(icon))
            icon_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self._icon_label, 1.0))
            icon_sequence.start()

    def getTitle(self) -> str:
        """Get the card title"""
        return self._title_label.text()

    def getSubtitle(self) -> str:
        """Get the card subtitle"""
        return self._subtitle_label.text()

    def getIcon(self) -> str:
        """Get the card icon"""
        return self._icon_label.text()
