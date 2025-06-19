"""
Enhanced Fluent Design Style Card Component
Advanced animations, performance optimization, responsive layout, and theme integration
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                              QGraphicsDropShadowEffect, QSizePolicy, QStackedWidget,
                              QGraphicsOpacityEffect, QApplication, QScrollArea, QPushButton)
from PySide6.QtCore import (Qt, Signal, QPropertyAnimation, Property, QByteArray, 
                           QTimer, QParallelAnimationGroup, QSequentialAnimationGroup,
                           QEasingCurve, QRect, QSize, QPoint, QVariantAnimation,
                           QAbstractAnimation, QEventLoop, QEvent)
from PySide6.QtGui import (QPainter, QPainterPath, QColor, QBrush, QPixmap, QFont,
                          QLinearGradient, QPen, QTransform, QRegion, QPaintEvent, 
                          QResizeEvent, QMouseEvent, QFontMetrics)
from core.theme import theme_manager, ThemeMode
from core.animation import FluentAnimation
from core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                      FluentRevealEffect, FluentSequence)
from typing import Optional, Dict, Any, List, Callable, Union, Tuple, Set
import weakref
import gc
import time


class FluentCardMetrics:
    """Card UI metrics for consistent layout and responsive design"""
    
    # Standard spacing metrics
    MARGIN_SMALL = 8
    MARGIN_MEDIUM = 16
    MARGIN_LARGE = 24
    
    # Standard corner radius settings
    RADIUS_SMALL = 4
    RADIUS_MEDIUM = 8
    RADIUS_LARGE = 12
    RADIUS_PILL = 24
    
    # Standard elevation levels
    ELEVATION_NONE = 0
    ELEVATION_LOW = 1
    ELEVATION_MEDIUM = 2
    ELEVATION_HIGH = 4
    ELEVATION_OVERLAY = 8
    
    # Responsive breakpoints
    BREAKPOINT_SMALL = 320  # Compact layout
    BREAKPOINT_MEDIUM = 640  # Standard layout
    BREAKPOINT_LARGE = 1024  # Expanded layout


class FluentCard(QFrame):
    """Fluent Design style card component with optimized animations and consistent theming"""

    # Enhanced signals
    clicked = Signal()
    doubleClicked = Signal()
    hoverProgressChanged = Signal(float)
    pressProgressChanged = Signal(float)
    currentElevationChanged = Signal(float)
    themeChanged = Signal(str)  # Theme name
    expanded = Signal()
    collapsed = Signal()
    resized = Signal(QSize)
    sizeChanged = Signal(QSize)
    contentLoaded = Signal()
    renderingPerformanceMeasured = Signal(float)  # Render time in ms

    # Class-level animation cache for performance
    _animation_cache = {}
    
    # Track instances for memory management using weak references
    _instances = weakref.WeakSet()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize a new FluentCard"""
        super().__init__(parent)
        FluentCard._instances.add(self)

        # Core properties
        self._clickable = False
        self._elevation = FluentCardMetrics.ELEVATION_MEDIUM
        self._hover_elevation = FluentCardMetrics.ELEVATION_HIGH
        self._corner_radius = FluentCardMetrics.RADIUS_MEDIUM
        self._current_elevation = FluentCardMetrics.ELEVATION_MEDIUM
        self._hover_progress = 0.0
        self._press_progress = 0.0
        self._is_expanded = False
        self._is_loading = False
        self._loading_progress = 0.0
        self._use_hover_animation = True
        self._use_press_animation = True
        self._use_elevation_animation = True
        self._last_redraw_time = 0
        self._render_times = []  # Track rendering performance
        
        # Responsive design properties
        self._current_breakpoint = FluentCardMetrics.BREAKPOINT_MEDIUM
        self._responsive_mode = True
        self._size_policies = {
            "small": (QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred),
            "medium": (QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred),
            "large": (QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred),
        }
        self._margin_by_size = {
            "small": (FluentCardMetrics.MARGIN_SMALL, FluentCardMetrics.MARGIN_SMALL, 
                     FluentCardMetrics.MARGIN_SMALL, FluentCardMetrics.MARGIN_SMALL),
            "medium": (FluentCardMetrics.MARGIN_MEDIUM, FluentCardMetrics.MARGIN_MEDIUM, 
                      FluentCardMetrics.MARGIN_MEDIUM, FluentCardMetrics.MARGIN_MEDIUM),
            "large": (FluentCardMetrics.MARGIN_LARGE, FluentCardMetrics.MARGIN_LARGE, 
                     FluentCardMetrics.MARGIN_LARGE, FluentCardMetrics.MARGIN_LARGE),
        }
        
        # Performance optimizations
        self._style_cache = {}
        self._shadow_cache = {}
        self._theme_version = 0
        self._paint_optimizer_enabled = True
        self._clip_to_rounded_corners = True
        self._hardware_acceleration = True
        self._paint_offset = QPoint(0, 0)
        self._last_dirty_rect = QRect()
        self._delayed_update_timer = QTimer()
        self._delayed_update_timer.setSingleShot(True)
        self._delayed_update_timer.setInterval(16)  # ~60fps
        self._delayed_update_timer.timeout.connect(self.update)
        
        # Create animation groups
        self._hover_group = QParallelAnimationGroup(self)
        self._press_group = QParallelAnimationGroup(self)
        self._elevation_group = QParallelAnimationGroup(self)
        self._expand_group = QParallelAnimationGroup(self)
        
        # Weak references to prevent memory leaks
        self._active_animations = set()  # Using standard set as WeakSet can cause issues
        self._cached_pixmaps = {}  # Use standard dict as WeakValueDictionary isn't available in PySide6

        # Setup UI components and behavior
        self._setup_ui()
        self._setup_optimized_style()
        self._setup_optimized_animations()
        self._setup_optimized_shadow()
        self._setup_event_connections()

        # Ensure theme changes are properly handled
        if hasattr(theme_manager, 'theme_changed') and theme_manager is not None:
            theme_manager.theme_changed.connect(self._on_theme_changed)
            
        # Initialize metrics collection
        self._collect_rendering_metrics()
            
        # Apply hardware acceleration if enabled
        if self._hardware_acceleration:
            self._setup_hardware_acceleration()

    def _setup_ui(self):
        """Setup UI components with responsive considerations"""
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        
        # Set minimum size based on metrics
        self.setMinimumSize(100, 60)
        
        # Main layout with optimized parameters
        self._layout = QVBoxLayout(self)
        
        # Initialize with medium size margins
        left, top, right, bottom = self._margin_by_size["medium"]
        self._layout.setContentsMargins(left, top, right, bottom)
        self._layout.setSpacing(12)
        
        # Set default size policy
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        # Track performance on creation
        self._last_redraw_time = time.time()
    
    def _setup_optimized_style(self):
        """Setup component style with enhanced caching and theme consistency"""
        if not theme_manager:
            return
            
        theme = theme_manager
        current_theme_version = getattr(theme, '_version', 0)
        
        # Enhanced cache key with more parameters for precise matching
        cache_key = f"{self._corner_radius}_{current_theme_version}_{theme.get_theme_mode().value}"
        
        # Check cache validity with fast lookup
        if cache_key in self._style_cache and self._theme_version == current_theme_version:
            self.setStyleSheet(self._style_cache[cache_key])
            return
        
        # Generate optimized stylesheet with consistent theming
        # and reduced CSS transitions for better performance
        border_color = theme.get_color('border').name()
        surface_color = theme.get_color('surface').name()
        primary_color = theme.get_color('primary').name()
        surface_variant_color = theme.get_color('surface_variant').name()
        
        # Enhanced stylesheet with better selectors and performance
        style_sheet = f"""
            FluentCard {{
                background-color: {surface_color};
                border: 1px solid {border_color};
                border-radius: {self._corner_radius}px;
            }}
            FluentCard[clickable="true"] {{
                cursor: pointer;
            }}
            FluentCard[clickable="true"]:hover {{
                background-color: {surface_variant_color};
            }}
        """
        
        # Cache the stylesheet for future use
        self._style_cache[cache_key] = style_sheet
        self._theme_version = current_theme_version
        self.setStyleSheet(style_sheet)
        
        # Set property for CSS selector
        self.setProperty("clickable", self._clickable)
        
    def _setup_optimized_animations(self):
        """Setup enhanced animation system with better coordination and performance"""
        # Hover animation group
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_progress"), self)
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
        self._hover_group.addAnimation(self._hover_animation)

        # Press animation group
        self._press_animation = QPropertyAnimation(
            self, QByteArray(b"press_progress"), self)
        self._press_animation.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
        self._press_animation.setEasingCurve(FluentTransition.EASE_CRISP)
        self._press_group.addAnimation(self._press_animation)

        # Elevation animation group with spring physics
        self._elevation_animation = QPropertyAnimation(
            self, QByteArray(b"current_elevation"), self)
        self._elevation_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._elevation_animation.setEasingCurve(FluentTransition.EASE_SPRING)
        self._elevation_group.addAnimation(self._elevation_animation)

        # Setup expand/collapse animation parameters
        self._expand_height_animation = QPropertyAnimation(
            self, QByteArray(b"maximumHeight"), self)
        self._expand_height_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self._expand_height_animation.setEasingCurve(FluentTransition.EASE_SPRING)
        self._expand_group.addAnimation(self._expand_height_animation)
        
        # Add to active animations for cleanup and tracking
        self._active_animations.add(self._hover_group)
        self._active_animations.add(self._press_group)
        self._active_animations.add(self._elevation_group)
        self._active_animations.add(self._expand_group)

        # Set up entrance animation with slight delay for better sequencing
        QTimer.singleShot(50, self._show_optimized_entrance_animation)
        
    def _show_optimized_entrance_animation(self):
        """Show enhanced entrance animation with better performance and smoother motion"""
        # Skip animation if widget isn't visible to save resources
        if not self.isVisible() or not self.isEnabled():
            return
            
        # Create a smoother and more coordinated entrance sequence
        entrance_sequence = FluentSequence(self)

        # Start with optimized fade in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self, 250))
        entrance_sequence.addPause(30)  # Shorter pause for smoother flow

        # Add scale in effect with improved spring motion
        scale_anim = FluentMicroInteraction.scale_animation(self, 1.0)
        entrance_sequence.addCallback(
            lambda: scale_anim.start() if scale_anim else None)
        
        # Add slight elevation increase for depth
        if self._use_elevation_animation and hasattr(self, "_elevation_animation"):
            self._elevation_animation.setStartValue(0.0)
            self._elevation_animation.setEndValue(self._elevation)
            entrance_sequence.addCallback(
                lambda: self._elevation_animation.start() if self._elevation_animation else None)
            
        entrance_sequence.start()
        self._active_animations.add(entrance_sequence)
        
    def _setup_optimized_shadow(self):
        """Setup optimized drop shadow effect with enhanced caching and performance"""
        self._shadow = QGraphicsDropShadowEffect(self)
        self._update_optimized_shadow()
        self.setGraphicsEffect(self._shadow)
        
    def _update_optimized_shadow(self):
        """Update shadow with enhanced parameters and more efficient caching"""
        if not theme_manager:
            return
            
        theme = theme_manager
        elevation_key = f"{self._current_elevation}_{theme.get_theme_mode().value}_{self._theme_version}"
        
        # Check shadow cache for performance
        if elevation_key in self._shadow_cache:
            cached = self._shadow_cache[elevation_key]
            self._shadow.setBlurRadius(cached['blur'])
            self._shadow.setXOffset(cached['offset_x'])
            self._shadow.setYOffset(cached['offset_y'])
            self._shadow.setColor(cached['color'])
            return

        # Calculate improved shadow parameters for better visuals
        blur_radius = max(1, self._current_elevation * 2.0)  # More subtle blur
        offset_y = max(0, int(self._current_elevation * 0.7))  # More natural offset
        offset_x = 0  # Keep horizontal offset at 0 for cleaner look

        # Generate shadow color based on theme mode
        if theme.get_theme_mode() == ThemeMode.LIGHT:
            shadow_color = QColor(0, 0, 0)
            alpha = min(80, int(30 + self._current_elevation * 6))
        else:
            shadow_color = QColor(0, 0, 0)
            alpha = min(120, int(50 + self._current_elevation * 8))
            
        shadow_color.setAlpha(alpha)

        # Cache shadow parameters
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
        
    def _setup_event_connections(self):
        """Setup event connections for better responsiveness"""
        # Connect signals to manage state and updates
        if hasattr(self, "hoverProgressChanged"):
            self.hoverProgressChanged.connect(self._on_hover_progress_changed)
        
        if hasattr(self, "pressProgressChanged"):
            self.pressProgressChanged.connect(self._on_press_progress_changed)
        
        if hasattr(self, "currentElevationChanged"):
            self.currentElevationChanged.connect(self._on_elevation_changed)
            
        # Connect resize signal for responsive layout
        self.resized.connect(self._on_size_changed)
        
    def _on_hover_progress_changed(self, progress):
        """Handle hover progress changes efficiently"""
        # Only update if significant change occurred (reduces repaints)
        if abs(progress - self._hover_progress) > 0.01:
            self._schedule_optimized_update()
            
    def _on_press_progress_changed(self, progress):
        """Handle press progress changes efficiently"""
        # Only update if significant change occurred (reduces repaints)
        if abs(progress - self._press_progress) > 0.01:
            self._schedule_optimized_update()
            
    def _on_elevation_changed(self, elevation):
        """Handle elevation changes efficiently"""
        # Only update if significant change occurred (reduces shadow updates)
        if abs(elevation - self._current_elevation) > 0.1:
            self._update_optimized_shadow()
            
    def _on_size_changed(self, size):
        """Handle size changes for responsive layout adjustments"""
        # Determine the current breakpoint based on width
        width = size.width()
        
        # Determine new breakpoint
        new_breakpoint = FluentCardMetrics.BREAKPOINT_MEDIUM  # Default
        if width < FluentCardMetrics.BREAKPOINT_SMALL:
            new_breakpoint = FluentCardMetrics.BREAKPOINT_SMALL
        elif width >= FluentCardMetrics.BREAKPOINT_LARGE:
            new_breakpoint = FluentCardMetrics.BREAKPOINT_LARGE
            
        # Update layout if breakpoint changed
        if self._responsive_mode and new_breakpoint != self._current_breakpoint:
            self._current_breakpoint = new_breakpoint
            self._apply_responsive_layout()
            
    def _apply_responsive_layout(self):
        """Apply responsive layout changes based on current breakpoint"""
        if not self._responsive_mode:
            return
            
        # Determine size category
        size_category = "medium"  # Default
        if self._current_breakpoint <= FluentCardMetrics.BREAKPOINT_SMALL:
            size_category = "small"
        elif self._current_breakpoint >= FluentCardMetrics.BREAKPOINT_LARGE:
            size_category = "large"
            
        # Apply appropriate margins
        if size_category in self._margin_by_size:
            left, top, right, bottom = self._margin_by_size[size_category]
            self._layout.setContentsMargins(left, top, right, bottom)
            
        # Apply appropriate size policy
        if size_category in self._size_policies:
            h_policy, v_policy = self._size_policies[size_category]
            self.setSizePolicy(h_policy, v_policy)
            
    def _schedule_optimized_update(self):
        """Schedule an optimized update to reduce multiple repaints"""
        if self._paint_optimizer_enabled and not self._delayed_update_timer.isActive():
            self._delayed_update_timer.start()
        else:
            self.update()
            
    def _setup_hardware_acceleration(self):
        """Setup hardware acceleration for smoother animations"""
        # This enables OpenGL rendering if available
        if self._hardware_acceleration:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
            
            # Enable layer-based rendering for hardware acceleration
            self.setWindowFlag(Qt.WindowType.MSWindowsOwnDC, True)
            
    def _collect_rendering_metrics(self):
        """Collect and analyze rendering performance metrics"""
        # Track frame times for performance analysis
        if self._render_times and len(self._render_times) > 10:
            # Calculate average render time
            avg_time = sum(self._render_times) / len(self._render_times)
            self._render_times.clear()
            
            # Emit metric for external monitoring
            self.renderingPerformanceMeasured.emit(avg_time)
            
            # Auto-optimize based on performance
            if avg_time > 16.0:  # Aiming for 60fps (16.6ms/frame)
                # Reduce animation complexity if performance is poor
                self._paint_optimizer_enabled = True
                
    # Enhanced property getters and setters with better change detection
    def _get_hover_progress(self):
        return self._hover_progress

    def _set_hover_progress(self, value):
        value = max(0.0, min(1.0, value))  # Clamp value between 0 and 1
        if abs(self._hover_progress - value) > 0.001:  # Only update on significant change
            self._hover_progress = value
            self.hoverProgressChanged.emit(value)
            self._schedule_optimized_update()

    def _get_press_progress(self):
        return self._press_progress

    def _set_press_progress(self, value):
        value = max(0.0, min(1.0, value))  # Clamp value between 0 and 1
        if abs(self._press_progress - value) > 0.001:  # Only update on significant change
            self._press_progress = value
            self.pressProgressChanged.emit(value)
            self._schedule_optimized_update()

    def _get_current_elevation(self):
        return self._current_elevation
        
    def _set_current_elevation(self, value):
        value = max(0.0, min(10.0, value))  # Clamp to reasonable elevation range
        if abs(self._current_elevation - value) > 0.05:  # Only update on significant change
            self._current_elevation = value
            self.currentElevationChanged.emit(value)
            self._update_optimized_shadow()

    # Define properties with QtCore.Property - fixed for PySide6
    hover_progress = Property(float, _get_hover_progress, _set_hover_progress, None, "Hover animation progress", hoverProgressChanged)
    press_progress = Property(float, _get_press_progress, _set_press_progress, None, "Press animation progress", pressProgressChanged)
    current_elevation = Property(float, _get_current_elevation, _set_current_elevation, None, "Current elevation level", currentElevationChanged)

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
            # Store old value for animation
            old_radius = self._corner_radius
            self._corner_radius = new_radius
            
            # Clear style cache to force refresh
            self._style_cache.clear()
            self._setup_optimized_style()
            
            # Animate radius change with subtle effect
            if self.isVisible():
                # Create a cleaner micro-interaction
                sequence = FluentSequence(self)
                sequence.addCallback(
                    lambda: FluentMicroInteraction.pulse_animation(self, 1.003))
                sequence.start()
                self._active_animations.add(sequence)

    def getCornerRadius(self) -> int:
        """Get the corner radius"""
        return self._corner_radius
        
    def setResponsiveMode(self, enabled: bool):
        """Enable or disable responsive layout mode"""
        if self._responsive_mode != enabled:
            self._responsive_mode = enabled
            if enabled:
                # Apply responsive layout immediately if enabled
                self._on_size_changed(self.size())
                
    def isResponsiveMode(self) -> bool:
        """Check if responsive mode is enabled"""
        return self._responsive_mode
        
    def setHardwareAcceleration(self, enabled: bool):
        """Enable or disable hardware acceleration"""
        if self._hardware_acceleration != enabled:
            self._hardware_acceleration = enabled
            if enabled:
                self._setup_hardware_acceleration()
            else:
                # Disable hardware acceleration attributes
                self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
                self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
                self.setWindowFlag(Qt.WindowType.MSWindowsOwnDC, False)
                
    def isHardwareAcceleration(self) -> bool:
        """Check if hardware acceleration is enabled"""
        return self._hardware_acceleration
        
    def setClipToRoundedCorners(self, enabled: bool):
        """Enable or disable clipping content to rounded corners"""
        if self._clip_to_rounded_corners != enabled:
            self._clip_to_rounded_corners = enabled
            self.update()
                
    def isClipToRoundedCorners(self) -> bool:
        """Check if clipping to rounded corners is enabled"""
        return self._clip_to_rounded_corners

    # Enhanced layout management methods
    def addWidget(self, widget: QWidget):
        """Add a widget to the card's layout with enhanced animation"""
        widget.setParent(self)
        self._layout.addWidget(widget)

        # Only animate if widget and card are visible
        if self.isVisible() and widget.isVisible():
            # Use smoother slide-in animation
            entrance = FluentRevealEffect.slide_in(widget, 250, "up")
            if entrance:
                entrance.start()
                self._active_animations.add(entrance)

    def insertWidget(self, index: int, widget: QWidget):
        """Insert a widget at the specified index with enhanced animation"""
        widget.setParent(self)
        self._layout.insertWidget(index, widget)

        # Optimized entrance animation
        if self.isVisible() and widget.isVisible():
            # Use opacity effect for fade in
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            effect.setOpacity(0.0)
            
            # Create animation group
            entrance_group = QParallelAnimationGroup(self)
            
            # Fade in animation
            fade = QPropertyAnimation(effect, QByteArray(b"opacity"))
            fade.setDuration(200)
            fade.setStartValue(0.0)
            fade.setEndValue(1.0)
            fade.setEasingCurve(FluentTransition.EASE_SMOOTH)
            
            # Scale animation
            scale = FluentMicroInteraction.scale_animation(widget, 1.0)
            
            # Add animations to group
            entrance_group.addAnimation(fade)
            if scale is not None:
                entrance_group.addAnimation(scale)
            entrance_group.start()
            
            self._active_animations.add(entrance_group)

    def removeWidget(self, widget: QWidget):
        """Remove a widget with enhanced transition animation"""
        if not widget or not self._layout:
            return
            
        # Check if widget is in layout
        widget_in_layout = False
        for i in range(self._layout.count()):
            if self._layout.itemAt(i) and self._layout.itemAt(i).widget() == widget:
                widget_in_layout = True
                break
                
        if not widget_in_layout:
            return
            
        # Only animate if widget is visible
        if self.isVisible() and widget.isVisible():
            # Create a smooth removal sequence
            removal_sequence = FluentSequence(self)
            
            # Start with opacity effect
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            effect.setOpacity(1.0)
            
            # Fade out animation
            fade_out = QPropertyAnimation(effect, QByteArray(b"opacity"))
            fade_out.setDuration(180)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.setEasingCurve(FluentTransition.EASE_SMOOTH)
            
            # Add animations to sequence
            removal_sequence.addCallback(
                lambda: fade_out.start() if fade_out else None)
                
            # Add subtle scale down
            scale_down = FluentMicroInteraction.scale_animation(widget, 0.95)
            
            removal_sequence.addCallback(
                lambda: scale_down.start() if scale_down else None)
                
            # Complete removal after animations
            removal_sequence.addPause(180)
            removal_sequence.addCallback(
                lambda: self._complete_widget_removal(widget))
                
            removal_sequence.start()
            self._active_animations.add(removal_sequence)
        else:
            # No animation needed, remove immediately
            self._complete_widget_removal(widget)

    def _complete_widget_removal(self, widget: QWidget):
        """Safely complete widget removal"""
        if widget and self._layout:
            self._layout.removeWidget(widget)
            widget.setParent(None)
            
            # Schedule layout update
            QTimer.singleShot(0, self._layout.update)

    def addLayout(self, layout):
        """Add a layout to the card's main layout"""
        if self._layout:
            self._layout.addLayout(layout)

    def addStretch(self, stretch: int = 0):
        """Add stretch to the card's main layout"""
        if self._layout:
            self._layout.addStretch(stretch)
        
    def setMargins(self, left: int, top: int, right: int, bottom: int):
        """Set content margins with optimized animation"""
        if not self._layout:
            return
            
        # Store current margins for animation
        old_margins = self._layout.contentsMargins()
        
        # Set new margins
        self._layout.setContentsMargins(left, top, right, bottom)
        
        # Animate transition if visible
        if self.isVisible():
            # Subtle pulse animation
            pulse = FluentMicroInteraction.pulse_animation(self, 1.003)
            
            # Update margin maps for responsive mode
            current_size_key = "medium"
            if self._current_breakpoint <= FluentCardMetrics.BREAKPOINT_SMALL:
                current_size_key = "small"
            elif self._current_breakpoint >= FluentCardMetrics.BREAKPOINT_LARGE:
                current_size_key = "large"
                
            self._margin_by_size[current_size_key] = (left, top, right, bottom)

    def setSpacing(self, spacing: int):
        """Set layout spacing with optimized transition"""
        if not self._layout:
            return
            
        # Store current spacing for animation
        old_spacing = self._layout.spacing()
        
        # Set new spacing with validation
        self._layout.setSpacing(max(0, spacing))
        
        # Animate transition if visible and spacing changed
        if self.isVisible() and old_spacing != spacing:
            # Very subtle pulse animation
            pulse = FluentMicroInteraction.pulse_animation(self, 1.002)

    def setClickable(self, clickable: bool):
        """Set whether the card is clickable with enhanced feedback"""
        if self._clickable != clickable:
            self._clickable = clickable
            
            # Update CSS property for styling
            self.setProperty("clickable", clickable)
            self.style().unpolish(self)
            self.style().polish(self)
            self._setup_optimized_style()

            if clickable:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                # Add subtle feedback animation
                FluentMicroInteraction.pulse_animation(self, 1.01)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
                # Reset hover and press states
                self._set_hover_progress(0.0)
                self._set_press_progress(0.0)
                
                # Reset cursor and animations
                if self._hover_group and self._hover_group.state() == QParallelAnimationGroup.State.Running:
                    self._hover_group.stop()
                if self._press_group and self._press_group.state() == QParallelAnimationGroup.State.Running:
                    self._press_group.stop()

    def setElevation(self, elevation: int):
        """Set the card elevation with optimized animation"""
        new_elevation = max(0, float(elevation))
        if self._elevation != new_elevation:
            old_elevation = self._current_elevation
            self._elevation = new_elevation

            # Only animate if visible
            if self.isVisible() and self._use_elevation_animation:
                # Stop any running elevation animations
                if self._elevation_group and self._elevation_group.state() == QParallelAnimationGroup.State.Running:
                    self._elevation_group.stop()
                    
                # Configure new elevation animation
                if self._elevation_animation:
                    self._elevation_animation.setStartValue(old_elevation)
                    self._elevation_animation.setEndValue(new_elevation)
                    self._elevation_group.start()
            else:
                # Apply immediately without animation
                self._set_current_elevation(new_elevation)
                
    def cleanup(self):
        """Enhanced cleanup method to prevent memory leaks"""
        # Stop all active animations safely
        animations_to_stop = list(self._active_animations)
        for animation in animations_to_stop:
            if animation is not None and isinstance(animation, QAbstractAnimation):
                try:
                    animation.stop()
                except (RuntimeError, TypeError):
                    pass  # Animation may already be deleted
        
        # Clear all caches
        if hasattr(self, '_style_cache'):
            self._style_cache.clear()
        if hasattr(self, '_shadow_cache'):
            self._shadow_cache.clear()
        if hasattr(self, '_cached_pixmaps'):
            self._cached_pixmaps.clear()
        
        # Stop and clear animation groups safely
        for group_name in ['_hover_group', '_press_group', '_elevation_group', '_expand_group']:
            if hasattr(self, group_name):
                group = getattr(self, group_name)
                if group is not None:
                    try:
                        group.stop()
                    except (RuntimeError, TypeError):
                        pass  # Group may already be deleted
                setattr(self, group_name, None)
        
        # Disconnect signals safely
        if hasattr(theme_manager, 'theme_changed') and theme_manager is not None:
            try:
                theme_manager.theme_changed.disconnect(self._on_theme_changed)
            except (RuntimeError, TypeError):
                pass  # Already disconnected
                
        # Stop timers safely
        if hasattr(self, '_delayed_update_timer') and self._delayed_update_timer is not None:
            if self._delayed_update_timer.isActive():
                self._delayed_update_timer.stop()
            
        # Clear active animations set
        if hasattr(self, '_active_animations'):
            self._active_animations.clear()
            
        # Remove from instances tracking
        if hasattr(FluentCard, '_instances') and self in FluentCard._instances:
            try:
                FluentCard._instances.discard(self)
            except (RuntimeError, TypeError):
                pass
    
    def _on_theme_changed(self, _=None):
        """Handle theme change with enhanced transition"""
        # Clear caches to force refresh
        if not hasattr(self, '_style_cache') or not hasattr(self, '_shadow_cache'):
            return
            
        self._style_cache.clear()
        self._shadow_cache.clear()
        
        # Update styling and shadow
        self._setup_optimized_style()
        self._update_optimized_shadow()
        
        # Add subtle theme transition animation if visible
        if self.isVisible():
            try:
                sequence = FluentSequence(self)
                sequence.addCallback(
                    lambda: FluentMicroInteraction.pulse_animation(self, 1.008))
                sequence.start()
            except (RuntimeError, AttributeError):
                # Fallback if animation fails
                self.update()
            
        # Signal theme change safely
        theme_name = ''
        if theme_manager is not None and hasattr(theme_manager, '_current_theme'):
            theme_name = theme_manager._current_theme
        self.themeChanged.emit(theme_name)
        
        # Schedule repaint
        self._schedule_optimized_update()
    
    @staticmethod
    def cleanup_all_instances():
        """Clean up all card instances to prevent memory leaks"""
        instances = list(FluentCard._instances)
        for card in instances:
            if card and hasattr(card, 'cleanup'):
                card.cleanup()
                
        # Clear animation cache
        FluentCard._animation_cache.clear()
        
    # Optimized lifecycle handling
    def showEvent(self, event):
        """Enhanced show event with optimized animations"""
        super().showEvent(event)
        
        # Reset metrics collection
        self._render_times.clear()
        
        # Show entrance animation if not visible before
        if not hasattr(self, '_has_shown_entrance'):
            self._show_optimized_entrance_animation()
            self._has_shown_entrance = True
            
    def hideEvent(self, event):
        """Enhanced hide event with cleanup"""
        super().hideEvent(event)
        
        # Pause any running animations when hidden
        for group in [self._hover_group, self._press_group, 
                     self._elevation_group, self._expand_group]:
            if group and group.state() == QParallelAnimationGroup.State.Running:
                group.pause()
                
    def closeEvent(self, event):
        """Enhanced close event with proper cleanup"""
        # Clean up resources
        self.cleanup()
        super().closeEvent(event)
        
    def __del__(self):
        """Ensure cleanup on deletion"""
        try:
            self.cleanup()
        except:
            pass


class ExpandableFluentCard(FluentCard):
    """
    Enhanced Fluent Design card component with smooth expand/collapse animations.
    
    Features:
    - Fluid height/width transitions
    - Collapsible content area
    - Customizable expand/collapse animations
    - Memory-efficient content loading
    - Theme-consistent styling
    """

    # Additional signals
    expandedChanged = Signal(bool)  # Emitted when expanded state changes
    expandProgress = Signal(float)  # Progress of expansion (0.0-1.0)
    expandIconRotationChanged = Signal(float)  # Icon rotation signal

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize an expandable card"""
        super().__init__(parent)
        
        # Expandable card properties
        self._is_expanded = False
        self._expand_progress = 0.0
        self._header_widget = None
        self._content_widget = None
        self._content_container = None
        self._expand_direction = "vertical"  # or "horizontal"
        self._expand_duration = 300
        self._collapsed_height = 0
        self._expanded_height = 0
        self._collapsed_width = 0
        self._expanded_width = 0
        self._auto_collapse_others = False
        self._expand_icon = None
        self._expand_icon_rotation = 0.0
        
        # Setup additional UI for expandable cards
        self._setup_expandable_ui()
        
    def _setup_expandable_ui(self):
        """Setup the UI components specific to expandable cards"""
        # Main layout is already set up in parent class
        
        # Create header container that's always visible
        self._header_widget = QWidget(self)
        self._header_layout = QHBoxLayout(self._header_widget)
        self._header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create content container that shows/hides with animation
        self._content_container = QWidget(self)
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Initially collapsed
        if self._content_container is not None:
            self._content_container.setMaximumHeight(0)
            self._content_container.setVisible(False)
        
        # Add to main layout
        self._layout.addWidget(self._header_widget)
        self._layout.addWidget(self._content_container)
        
        # Setup expand animation
        self._expand_height_animation = QPropertyAnimation(self._content_container, QByteArray(b"maximumHeight"))
        self._expand_height_animation.setDuration(self._expand_duration)
        self._expand_height_animation.setEasingCurve(FluentTransition.EASE_SPRING)
        
        # Set up rotation animation for expand icon
        self._expand_icon_animation = QPropertyAnimation(self, QByteArray(b"expandIconRotation"))
        self._expand_icon_animation.setDuration(self._expand_duration)
        self._expand_icon_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)
        
        # Add animations to group
        self._expand_group = QParallelAnimationGroup(self)
        self._expand_group.addAnimation(self._expand_height_animation)
        self._expand_group.addAnimation(self._expand_icon_animation)
        
        # Connect animation finished to handle states
        self._expand_group.finished.connect(self._on_expand_animation_finished)
        
    def setHeader(self, widget: QWidget):
        """Set the header widget that's always visible"""
        if self._header_layout.count() > 0:
            # Clear existing header
            while self._header_layout.count():
                item = self._header_layout.takeAt(0)
                if item and item.widget():
                    item.widget().setParent(None)
        
        if widget:
            widget.setParent(self._header_widget)
            self._header_layout.addWidget(widget)
            
            # Make header clickable if it's a compatible widget
            # (button or other clickable widget)
            try:
                if hasattr(widget, 'clicked') and callable(getattr(widget, 'clicked', None)):
                    # Only connect if it's a button or has a clicked signal
                    getattr(widget, 'clicked').connect(self.toggleExpand)
            except (AttributeError, TypeError):
                pass
            
            # Make header clickable for expand/collapse
            if self._header_widget is not None:
                self._header_widget.setCursor(Qt.CursorShape.PointingHandCursor)
                self._header_widget.mousePressEvent = self._header_mouse_press_event
            
    def _header_mouse_press_event(self, event):
        """Handle mouse press on header to toggle expand state"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggleExpand()
            
    def setContent(self, widget: QWidget):
        """Set the content widget that shows/hides with animation"""
        if self._content_layout and self._content_layout.count() > 0:
            # Clear existing content
            while self._content_layout.count():
                item = self._content_layout.takeAt(0)
                if item and item.widget():
                    item.widget().setParent(None)
        
        if widget and self._content_container is not None:
            self._content_widget = widget
            widget.setParent(self._content_container)
            self._content_layout.addWidget(widget)
            
            # Calculate expanded height but maintain collapsed state
            self._calculate_content_sizes()
            
    def _calculate_content_sizes(self):
        """Calculate the proper expanded and collapsed sizes"""
        if not self._content_widget or not self._content_container:
            return
            
        # Store current state
        was_visible = self._content_container.isVisible()
        current_max_height = self._content_container.maximumHeight()
        
        # Temporarily show to get proper size
        self._content_container.setVisible(True)
        self._content_container.setMaximumHeight(10000)  # Large enough to fit content
        
        # Let the layout adjust
        self._content_container.adjustSize()
        self.adjustSize()
        QApplication.processEvents()
        
        # Calculate sizes
        if self._expand_direction == "vertical":
            self._collapsed_height = 0
            self._expanded_height = self._content_widget.sizeHint().height() + \
                                   self._content_layout.contentsMargins().top() + \
                                   self._content_layout.contentsMargins().bottom()
        else:
            self._collapsed_width = 0
            self._expanded_width = self._content_widget.sizeHint().width() + \
                                  self._content_layout.contentsMargins().left() + \
                                  self._content_layout.contentsMargins().right()
        
        # Restore previous state
        self._content_container.setVisible(was_visible)
        self._content_container.setMaximumHeight(current_max_height)
                
    def setExpandDirection(self, direction: str):
        """Set expansion direction ('vertical' or 'horizontal')"""
        if direction in ["vertical", "horizontal"] and self._expand_direction != direction:
            self._expand_direction = direction
            
            # Reconfigure animations based on direction
            if direction == "vertical" and self._content_container is not None:
                self._expand_height_animation.setTargetObject(self._content_container)
                self._expand_height_animation.setPropertyName(QByteArray(b"maximumHeight"))
            elif self._content_container is not None:
                self._expand_height_animation.setTargetObject(self._content_container)
                self._expand_height_animation.setPropertyName(QByteArray(b"maximumWidth"))
                
            # Recalculate sizes
            self._calculate_content_sizes()
            
    def setExpandDuration(self, duration: int):
        """Set the duration of expand/collapse animation in milliseconds"""
        self._expand_duration = max(100, min(1000, duration))
        if hasattr(self, '_expand_height_animation'):
            self._expand_height_animation.setDuration(self._expand_duration)
        if hasattr(self, '_expand_icon_animation'):
            self._expand_icon_animation.setDuration(self._expand_duration)
        
    def setExpandIcon(self, icon_widget: QWidget):
        """Set an icon widget that rotates when expanded/collapsed"""
        self._expand_icon = icon_widget
        if icon_widget and self._header_layout:
            # Add to right side of header
            self._header_layout.addStretch()
            self._header_layout.addWidget(icon_widget)
            
    def _get_expand_icon_rotation(self) -> float:
        """Get current rotation of expand icon"""
        return self._expand_icon_rotation
        
    def _set_expand_icon_rotation(self, value: float):
        """Set rotation of expand icon with update"""
        if self._expand_icon_rotation != value:
            self._expand_icon_rotation = value
            self.expandIconRotationChanged.emit(value)
            # Instead of trying to rotate the widget directly, 
            # just update the stored value and let custom implementations handle it
                  # Property for animation - simplified for PySide6 compatibility
    expandIconRotation = Property(float, _get_expand_icon_rotation, _set_expand_icon_rotation, None, "Expand icon rotation angle", expandIconRotationChanged)
                
    def isExpanded(self) -> bool:
        """Check if the card is currently expanded"""
        return self._is_expanded
        
    def expand(self):
        """Expand the card with animation"""
        if self._is_expanded or not self._content_container:
            return
            
        # Stop any running animations
        if self._expand_group and self._expand_group.state() == QParallelAnimationGroup.State.Running:
            self._expand_group.stop()
            
        # Make container visible before animation
        self._content_container.setVisible(True)
        
        # Set up animation
        if self._expand_direction == "vertical":
            self._expand_height_animation.setStartValue(self._collapsed_height)
            self._expand_height_animation.setEndValue(self._expanded_height)
        else:
            self._expand_height_animation.setStartValue(self._collapsed_width)
            self._expand_height_animation.setEndValue(self._expanded_width)
            
        # Setup icon rotation if available
        if self._expand_icon and hasattr(self, '_expand_icon_animation'):
            self._expand_icon_animation.setStartValue(0.0)
            self._expand_icon_animation.setEndValue(180.0)
            
        # Start animation
        if self._expand_group:
            self._expand_group.start()
        self._is_expanded = True
        self.expandedChanged.emit(True)
        self.expanded.emit()
        
    def collapse(self):
        """Collapse the card with animation"""
        if not self._is_expanded or not self._content_container:
            return
            
        # Stop any running animations
        if self._expand_group and self._expand_group.state() == QParallelAnimationGroup.State.Running:
            self._expand_group.stop()
            
        # Set up animation
        if self._expand_direction == "vertical":
            self._expand_height_animation.setStartValue(self._content_container.height())
            self._expand_height_animation.setEndValue(self._collapsed_height)
        else:
            self._expand_height_animation.setStartValue(self._content_container.width())
            self._expand_height_animation.setEndValue(self._collapsed_width)
            
        # Setup icon rotation if available
        if self._expand_icon and hasattr(self, '_expand_icon_animation'):
            self._expand_icon_animation.setStartValue(180.0)
            self._expand_icon_animation.setEndValue(0.0)
            
        # Start animation
        if self._expand_group:
            self._expand_group.start()
        self._is_expanded = False
        self.expandedChanged.emit(False)
        self.collapsed.emit()
        
    def toggleExpand(self):
        """Toggle between expanded and collapsed states"""
        if self._is_expanded:
            self.collapse()
        else:
            # Auto-collapse other cards if enabled
            if self._auto_collapse_others and self.parent():
                for sibling in self.parent().findChildren(ExpandableFluentCard):
                    if sibling != self and sibling.isExpanded():
                        sibling.collapse()
            self.expand()
            
    def _on_expand_animation_finished(self):
        """Handle animation completion for proper cleanup"""
        # Hide container when fully collapsed
        if not self._is_expanded and self._content_container:
            if self._expand_direction == "vertical":
                if self._content_container.maximumHeight() <= 0:
                    self._content_container.setVisible(False)
            elif self._expand_direction == "horizontal":
                if self._content_container.maximumWidth() <= 0:
                    self._content_container.setVisible(False)
        
        # Show container when expanding starts
        elif self._is_expanded and self._content_container:
            self._content_container.setVisible(True)
        
        # Emit signals to notify completion
        self.expandedChanged.emit(self._is_expanded)
        if self._is_expanded:
            self.expanded.emit()
        else:
            self.collapsed.emit()
                
    def setAutoCollapseOthers(self, enable: bool):
        """When enabled, expanding this card will collapse other expandable siblings"""
        self._auto_collapse_others = enable
        
    def resizeEvent(self, event: QResizeEvent):
        """Handle resize with proper content adjustment"""
        super().resizeEvent(event)
        
        # Recalculate content sizes on width change if vertical expansion
        if (self._expand_direction == "vertical" and 
            event.oldSize().width() != event.size().width() and 
            self._content_widget and self._content_container):
            QTimer.singleShot(0, self._calculate_content_sizes)
            
            # Update animation if expanded
            if self._is_expanded:
                QTimer.singleShot(10, self._update_expanded_size)
                
    def _update_expanded_size(self):
        """Update content size after resize to maintain proper expansion"""
        if self._is_expanded and self._expand_direction == "vertical" and self._content_container:
            self._content_container.setMaximumHeight(self._expanded_height)
