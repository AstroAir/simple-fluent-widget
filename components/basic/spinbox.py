"""
Enhanced Fluent Design Style Numeric Adjuster with Modern PySide6 Features
"""

from PySide6.QtWidgets import (QSpinBox, QDoubleSpinBox, QWidget, QHBoxLayout,
                              QPushButton, QGraphicsOpacityEffect, QSizePolicy)
from PySide6.QtCore import (Signal, QPropertyAnimation, QByteArray, QTimer, 
                           QParallelAnimationGroup, QSequentialAnimationGroup,
                           QEasingCurve, Property, QObject, Qt, QRect)
from PySide6.QtGui import (QWheelEvent, QPainter, QPainterPath, QColor, QBrush)
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import FluentTransition
from typing import Optional


class AnimatedProperty(QObject):
    """Helper class for custom animated properties with optimized signal emission"""
    
    shadowBlurChanged = Signal(float)
    glowIntensityChanged = Signal(float)
    scaleFactorChanged = Signal(float)
    
    def __init__(self, parent):
        super().__init__(parent)
        self._shadow_blur = 0.0
        self._glow_intensity = 0.0
        self._scale_factor = 1.0
        
    def get_shadow_blur(self):
        return self._shadow_blur
    
    def set_shadow_blur(self, value):
        if self._shadow_blur != value:
            self._shadow_blur = value
            self.shadowBlurChanged.emit(value)
            parent = self.parent()
            if parent and isinstance(parent, QWidget):
                parent.update()
    
    def get_glow_intensity(self):
        return self._glow_intensity
    
    def set_glow_intensity(self, value):
        if self._glow_intensity != value:
            self._glow_intensity = value
            self.glowIntensityChanged.emit(value)
            parent = self.parent()
            if parent and isinstance(parent, QWidget):
                parent.update()
            
    def get_scale_factor(self):
        return self._scale_factor
    
    def set_scale_factor(self, value):
        if self._scale_factor != value:
            self._scale_factor = value
            self.scaleFactorChanged.emit(value)
            parent = self.parent()
            if parent and isinstance(parent, QWidget):
                parent.update()


class FluentSpinBox(QSpinBox):
    """**Enhanced Fluent Design SpinBox with Modern Features**"""

    value_changed_animated = Signal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # State tracking
        self._is_hovered = False
        self._is_focused = False
        self._is_animating = False
        
        # Animation properties
        self._animated_props = AnimatedProperty(self)
        
        # Animation groups for complex transitions
        self._hover_group = QParallelAnimationGroup(self)
        self._focus_group = QParallelAnimationGroup(self)
        self._value_group = QSequentialAnimationGroup(self)
        
        # Performance optimization: cache frequently used objects
        self._cached_theme_colors = {}
        self._last_theme_hash = None
        self._cached_glow_path = None
        self._last_size_for_path = None
        
        # Debounce timer for theme updates
        self._theme_update_timer = QTimer(self)
        self._theme_update_timer.setSingleShot(True)
        self._theme_update_timer.timeout.connect(self._apply_theme_update)
        
        self._setup_widget()
        self._setup_animations()
        self._connect_signals()
        
        # Initial setup
        self._cache_theme_colors()
        self._setup_style()
        
        # Entrance animation
        self._play_entrance_animation()

    def _setup_widget(self):
        """Setup widget properties with modern configurations"""
        self.setMinimumHeight(36)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        
        # Enable hardware acceleration if available
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        
        # Optimize rendering
        self.setAutoFillBackground(False)

    def _setup_animations(self):
        """**Setup comprehensive animation system with optimized groups**"""
        duration_fast = FluentAnimation.DURATION_FAST
        duration_medium = FluentAnimation.DURATION_MEDIUM
        
        # Hover animations group
        self._hover_shadow_anim = QPropertyAnimation(self._animated_props, QByteArray(b"shadow_blur"))
        self._hover_shadow_anim.setDuration(duration_fast)
        self._hover_shadow_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        
        self._hover_glow_anim = QPropertyAnimation(self._animated_props, QByteArray(b"glow_intensity"))
        self._hover_glow_anim.setDuration(duration_fast)
        self._hover_glow_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        
        self._hover_group.addAnimation(self._hover_shadow_anim)
        self._hover_group.addAnimation(self._hover_glow_anim)
        
        # Focus animations group
        self._focus_scale_anim = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
        self._focus_scale_anim.setDuration(duration_medium)
        self._focus_scale_anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        
        self._focus_glow_anim = QPropertyAnimation(self._animated_props, QByteArray(b"glow_intensity"))
        self._focus_glow_anim.setDuration(duration_medium)
        self._focus_glow_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        
        self._focus_group.addAnimation(self._focus_scale_anim)
        self._focus_group.addAnimation(self._focus_glow_anim)
        
        # Value change animation with bounce effect
        self._value_scale_out = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
        self._value_scale_out.setDuration(duration_fast // 2)
        self._value_scale_out.setEasingCurve(QEasingCurve.Type.InQuad)
        
        self._value_change_anim = QPropertyAnimation(self, QByteArray(b"value"))
        self._value_change_anim.setDuration(duration_medium)
        self._value_change_anim.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        self._value_scale_in = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
        self._value_scale_in.setDuration(duration_fast // 2)
        self._value_scale_in.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self._value_group.addAnimation(self._value_scale_out)
        self._value_group.addAnimation(self._value_change_anim)
        self._value_group.addAnimation(self._value_scale_in)

    def _connect_signals(self):
        """Connect signals with proper cleanup"""
        self.valueChanged.connect(self._on_value_changed)
        theme_manager.theme_changed.connect(self._on_theme_changed_debounced)
        
        # Animation completion signals
        self._value_group.finished.connect(lambda: self._set_animating(False))
        self._hover_group.finished.connect(self._on_hover_animation_finished)

    def _cache_theme_colors(self):
        """**Cache theme colors for performance optimization**"""
        theme = theme_manager
        theme_hash = hash(str(getattr(theme, 'current_theme', 'default')))
        
        if theme_hash != self._last_theme_hash:
            self._cached_theme_colors = {
                'surface': theme.get_color('surface'),
                'border': theme.get_color('border'),
                'primary': theme.get_color('primary'),
                'text_primary': theme.get_color('text_primary'),
                'accent_light': theme.get_color('accent_light'),
                'text_disabled': theme.get_color('text_disabled'),
                'background': theme.get_color('background'),
                'on_primary': theme.get_color('on_primary')
            }
            self._last_theme_hash = theme_hash

    def _setup_style(self):
        """Setup optimized styling with cached colors"""
        colors = self._cached_theme_colors
        
        style_sheet = f"""
            QSpinBox {{
                background-color: {colors['surface'].name()};
                border: 2px solid {colors['border'].name()};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                color: {colors['text_primary'].name()};
                selection-background-color: {colors['primary'].name()}40;
            }}
            QSpinBox:hover {{
                border-color: {colors['primary'].name()};
                background-color: {colors['accent_light'].name()};
            }}
            QSpinBox:focus {{
                border-color: {colors['primary'].name()};
                border-width: 2px;
                background-color: {colors['surface'].lighter(105).name()};
                outline: none;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: transparent;
                border: none;
                width: 24px;
                height: 18px;
                border-radius: 4px;
                margin: 2px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {colors['primary'].lighter(130).name()};
                border-radius: 4px;
            }}
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {{
                background-color: {colors['primary'].name()};
            }}
            QSpinBox::up-arrow, QSpinBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QSpinBox:disabled {{
                background-color: {colors['background'].name()};
                color: {colors['text_disabled'].name()};
                border-color: {colors['text_disabled'].name()};
                opacity: 0.6;
            }}
        """
        
        self.setStyleSheet(style_sheet)

    def set_value_animated(self, value: int, duration: Optional[int] = None):
        """**Set value with smooth animation and performance optimization**"""
        if self._is_animating:
            self._value_group.stop()
        
        current_value = self.value()
        if current_value == value:
            return
            
        self._set_animating(True)
        
        # Dynamic duration based on value difference
        if duration is None:
            diff = abs(value - current_value)
            duration = min(FluentAnimation.DURATION_MEDIUM, max(200, diff * 50))
        
        # Setup scale out animation
        self._value_scale_out.setStartValue(1.0)
        self._value_scale_out.setEndValue(0.95)
        
        # Setup value change animation
        self._value_change_anim.setDuration(duration)
        self._value_change_anim.setStartValue(current_value)
        self._value_change_anim.setEndValue(value)
        
        # Setup scale in animation
        self._value_scale_in.setStartValue(0.95)
        self._value_scale_in.setEndValue(1.0)
        
        self._value_group.start()
        
        # Emit custom signal
        self.value_changed_animated.emit(value)

    def _play_entrance_animation(self):
        """Play entrance animation with modern effects"""
        # Start with invisible and scaled down
        self._animated_props.set_scale_factor(0.8)
        opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0.0)
        
        # Animate opacity
        opacity_anim = QPropertyAnimation(opacity_effect, QByteArray(b"opacity"))
        opacity_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Animate scale
        scale_anim = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
        scale_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
        scale_anim.setStartValue(0.8)
        scale_anim.setEndValue(1.0)
        scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        
        # Play both animations together
        entrance_group = QParallelAnimationGroup(self)
        entrance_group.addAnimation(opacity_anim)
        entrance_group.addAnimation(scale_anim)
        def clear_graphics_effect():
            if self.graphicsEffect() is not None:
                self.setGraphicsEffect(None)  # type: ignore
        entrance_group.finished.connect(clear_graphics_effect)
        entrance_group.start()

    def _set_animating(self, animating: bool):
        """Set animation state with optimization"""
        self._is_animating = animating
        if not animating:
            self.update()  # Force repaint when animation completes

    def enterEvent(self, event):
        """Enhanced hover enter with performance optimization"""
        if self._is_hovered:
            return
            
        self._is_hovered = True
        
        # Stop any running hover animations
        if self._hover_group.state() == QParallelAnimationGroup.State.Running:
            self._hover_group.stop()
        
        # Setup hover in animations
        self._hover_shadow_anim.setStartValue(self._animated_props.get_shadow_blur())
        self._hover_shadow_anim.setEndValue(8.0)
        
        self._hover_glow_anim.setStartValue(self._animated_props.get_glow_intensity())
        self._hover_glow_anim.setEndValue(0.3)
        
        self._hover_group.start()
        
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Enhanced hover leave with smooth transition"""
        if not self._is_hovered:
            return
            
        self._is_hovered = False
        
        # Stop any running hover animations
        if self._hover_group.state() == QParallelAnimationGroup.State.Running:
            self._hover_group.stop()
        
        # Setup hover out animations
        self._hover_shadow_anim.setStartValue(self._animated_props.get_shadow_blur())
        self._hover_shadow_anim.setEndValue(0.0)
        
        self._hover_glow_anim.setStartValue(self._animated_props.get_glow_intensity())
        self._hover_glow_anim.setEndValue(0.0)
        
        self._hover_group.start()
        
        super().leaveEvent(event)

    def focusInEvent(self, event):
        """Enhanced focus in with modern animations"""
        if self._is_focused:
            return
            
        self._is_focused = True
        
        # Setup focus animations
        self._focus_scale_anim.setStartValue(self._animated_props.get_scale_factor())
        self._focus_scale_anim.setEndValue(1.02)
        
        self._focus_glow_anim.setStartValue(self._animated_props.get_glow_intensity())
        self._focus_glow_anim.setEndValue(0.5)
        
        self._focus_group.start()
        
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Enhanced focus out with smooth transition"""
        if not self._is_focused:
            return
            
        self._is_focused = False
        
        # Setup focus out animations
        self._focus_scale_anim.setStartValue(self._animated_props.get_scale_factor())
        self._focus_scale_anim.setEndValue(1.0)
        
        self._focus_glow_anim.setStartValue(self._animated_props.get_glow_intensity())
        self._focus_glow_anim.setEndValue(0.0)
        
        self._focus_group.start()
        
        super().focusOutEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Enhanced wheel event with visual feedback"""
        if not self.hasFocus():
            return
            
        old_value = self.value()
        super().wheelEvent(event)
        new_value = self.value()
        
        if old_value != new_value:
            # Quick scale pulse for wheel changes
            pulse_anim = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
            pulse_anim.setDuration(150)
            pulse_anim.setStartValue(1.0)
            pulse_anim.setKeyValueAt(0.5, 1.05)
            pulse_anim.setEndValue(1.0)
            pulse_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            pulse_anim.start()

    def stepBy(self, steps: int):
        """Enhanced step by with directional feedback"""
        old_value = self.value()
        super().stepBy(steps)
        new_value = self.value()
        
        if old_value != new_value:
            # Directional animation feedback
            direction_scale = 1.03 if steps > 0 else 0.97
            
            direction_anim = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
            direction_anim.setDuration(200)
            direction_anim.setStartValue(1.0)
            direction_anim.setKeyValueAt(0.5, direction_scale)
            direction_anim.setEndValue(1.0)
            direction_anim.setEasingCurve(QEasingCurve.Type.OutElastic)
            direction_anim.start()

    def paintEvent(self, event):
        """**Enhanced paint event with optimized custom effects**"""
        super().paintEvent(event)
        
        # Only add custom effects if there are active animations
        if (self._animated_props.get_glow_intensity() > 0 or 
            self._animated_props.get_shadow_blur() > 0 or 
            abs(self._animated_props.get_scale_factor() - 1.0) > 0.01):
            
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Apply scale transform
            if abs(self._animated_props.get_scale_factor() - 1.0) > 0.01:
                center = self.rect().center()
                painter.translate(center)
                painter.scale(self._animated_props.get_scale_factor(), 
                            self._animated_props.get_scale_factor())
                painter.translate(-center)
            
            # Draw glow effect
            if self._animated_props.get_glow_intensity() > 0:
                self._draw_glow_effect(painter)

    def _draw_glow_effect(self, painter: QPainter):
        """Draw custom glow effect with path caching for enhanced visual feedback"""
        # Check if glow path needs to be recreated (size changed)
        current_size = (self.width(), self.height())
        if self._cached_glow_path is None or self._last_size_for_path != current_size:
            # Create glow path
            glow_rect = self.rect().adjusted(-2, -2, 2, 2)
            self._cached_glow_path = QPainterPath()
            self._cached_glow_path.addRoundedRect(glow_rect, 10, 10)
            self._last_size_for_path = current_size
        
        colors = self._cached_theme_colors
        glow_color = colors['primary']
        glow_color.setAlphaF(self._animated_props.get_glow_intensity() * 0.3)
        
        # Draw glow
        painter.setBrush(QBrush(glow_color))
        painter.setPen(glow_color)
        painter.drawPath(self._cached_glow_path)

    def _on_value_changed(self, value: int):
        """Handle value changes with optimized feedback"""
        if not self._is_animating:
            # Quick feedback for direct value changes
            feedback_anim = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
            feedback_anim.setDuration(100)
            feedback_anim.setStartValue(self._animated_props.get_scale_factor())
            feedback_anim.setKeyValueAt(0.5, 1.02)
            feedback_anim.setEndValue(1.0)
            feedback_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            feedback_anim.start()

    def _on_hover_animation_finished(self):
        """Handle hover animation completion"""
        # Optimize by reducing update frequency when not animating
        if not self._is_hovered and self._animated_props.get_glow_intensity() <= 0:
            self.update()

    def _on_theme_changed_debounced(self, theme_name: str):
        """Debounced theme change handler for performance"""
        self._theme_update_timer.start(50)  # 50ms debounce

    def _apply_theme_update(self):
        """Apply theme update with smooth transition"""
        # Cache new colors
        self._cache_theme_colors()
        
        # Smooth transition effect
        transition_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(transition_effect)
        
        opacity_anim = QPropertyAnimation(transition_effect, QByteArray(b"opacity"))
        opacity_anim.setDuration(FluentAnimation.DURATION_FAST)
        opacity_anim.setStartValue(1.0)
        opacity_anim.setKeyValueAt(0.5, 0.8)
        opacity_anim.setEndValue(1.0)
        def clear_transition_effect():
            if self.graphicsEffect() is not None:
                self.setGraphicsEffect(None)  # type: ignore[call-arg]
        opacity_anim.finished.connect(clear_transition_effect)
        
        # Update style
        self._setup_style()
        opacity_anim.start()

    def cleanup(self):
        """**Cleanup method for proper memory management**"""
        # Stop all animations
        self._hover_group.stop()
        self._focus_group.stop()
        self._value_group.stop()
        
        # Clear cached data
        self._cached_theme_colors.clear()
        self._cached_glow_path = None
        
        # Disconnect signals
        try:
            theme_manager.theme_changed.disconnect(self._on_theme_changed_debounced)
        except:
            pass

    def __del__(self):
        """Destructor with cleanup"""
        self.cleanup()


class FluentDoubleSpinBox(QDoubleSpinBox):
    """Enhanced Fluent Design DoubleSpinBox with Modern Features"""

    value_changed_animated = Signal(float)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # State tracking
        self._is_hovered = False
        self._is_focused = False
        self._is_animating = False
        
        # Animation properties
        self._animated_props = AnimatedProperty(self)
        
        # Animation groups for complex transitions
        self._hover_group = QParallelAnimationGroup(self)
        self._focus_group = QParallelAnimationGroup(self)
        self._value_group = QSequentialAnimationGroup(self)
        
        # Performance optimization: cache frequently used objects
        self._cached_theme_colors = {}
        self._last_theme_hash = None
        self._cached_glow_path = None
        self._last_size_for_path = None
        
        # Debounce timer for theme updates
        self._theme_update_timer = QTimer(self)
        self._theme_update_timer.setSingleShot(True)
        self._theme_update_timer.timeout.connect(self._apply_theme_update)
        
        self._setup_widget()
        self._setup_animations()
        self._connect_signals()
        
        # Initial setup
        self._cache_theme_colors()
        self._setup_style()
        
        # Entrance animation
        self._play_entrance_animation()

    def _setup_widget(self):
        """Setup widget properties with modern configurations"""
        self.setMinimumHeight(36)
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.UpDownArrows)
        
        # Enable hardware acceleration if available
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        
        # Optimize rendering
        self.setAutoFillBackground(False)

    def _setup_animations(self):
        """Setup comprehensive animation system"""
        duration_fast = FluentAnimation.DURATION_FAST
        duration_medium = FluentAnimation.DURATION_MEDIUM
        
        # Hover animations group
        self._hover_shadow_anim = QPropertyAnimation(self._animated_props, QByteArray(b"shadow_blur"))
        self._hover_shadow_anim.setDuration(duration_fast)
        self._hover_shadow_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        
        self._hover_glow_anim = QPropertyAnimation(self._animated_props, QByteArray(b"glow_intensity"))
        self._hover_glow_anim.setDuration(duration_fast)
        self._hover_glow_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        
        self._hover_group.addAnimation(self._hover_shadow_anim)
        self._hover_group.addAnimation(self._hover_glow_anim)
        
        # Focus animations group
        self._focus_scale_anim = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
        self._focus_scale_anim.setDuration(duration_medium)
        self._focus_scale_anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        
        self._focus_glow_anim = QPropertyAnimation(self._animated_props, QByteArray(b"glow_intensity"))
        self._focus_glow_anim.setDuration(duration_medium)
        self._focus_glow_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        
        self._focus_group.addAnimation(self._focus_scale_anim)
        self._focus_group.addAnimation(self._focus_glow_anim)
        
        # Value change animation with bounce effect
        self._value_scale_out = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
        self._value_scale_out.setDuration(duration_fast // 2)
        self._value_scale_out.setEasingCurve(QEasingCurve.Type.InQuad)
        
        self._value_change_anim = QPropertyAnimation(self, QByteArray(b"value"))
        self._value_change_anim.setDuration(duration_medium)
        self._value_change_anim.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        self._value_scale_in = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
        self._value_scale_in.setDuration(duration_fast // 2)
        self._value_scale_in.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self._value_group.addAnimation(self._value_scale_out)
        self._value_group.addAnimation(self._value_change_anim)
        self._value_group.addAnimation(self._value_scale_in)

    def _connect_signals(self):
        """Connect signals with proper cleanup"""
        self.valueChanged.connect(self._on_value_changed)
        theme_manager.theme_changed.connect(self._on_theme_changed_debounced)
        
        # Animation completion signals
        self._value_group.finished.connect(lambda: self._set_animating(False))
        self._hover_group.finished.connect(self._on_hover_animation_finished)

    def _cache_theme_colors(self):
        """Cache theme colors for performance"""
        theme = theme_manager
        theme_hash = hash(str(getattr(theme, 'current_theme', 'default')))
        
        if theme_hash != self._last_theme_hash:
            self._cached_theme_colors = {
                'surface': theme.get_color('surface'),
                'border': theme.get_color('border'),
                'primary': theme.get_color('primary'),
                'text_primary': theme.get_color('text_primary'),
                'accent_light': theme.get_color('accent_light'),
                'text_disabled': theme.get_color('text_disabled'),
                'background': theme.get_color('background'),
                'on_primary': theme.get_color('on_primary')
            }
            self._last_theme_hash = theme_hash

    def _setup_style(self):
        """Setup optimized styling with cached colors"""
        colors = self._cached_theme_colors
        
        style_sheet = f"""
            QDoubleSpinBox {{
                background-color: {colors['surface'].name()};
                border: 2px solid {colors['border'].name()};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                color: {colors['text_primary'].name()};
                selection-background-color: {colors['primary'].name()}40;
            }}
            QDoubleSpinBox:hover {{
                border-color: {colors['primary'].name()};
                background-color: {colors['accent_light'].name()};
            }}
            QDoubleSpinBox:focus {{
                border-color: {colors['primary'].name()};
                border-width: 2px;
                background-color: {colors['surface'].lighter(105).name()};
                outline: none;
            }}
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                background-color: transparent;
                border: none;
                width: 24px;
                height: 18px;
                border-radius: 4px;
                margin: 2px;
            }}
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {colors['primary'].lighter(130).name()};
                border-radius: 4px;
            }}
            QDoubleSpinBox::up-button:pressed, QDoubleSpinBox::down-button:pressed {{
                background-color: {colors['primary'].name()};
            }}
            QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QDoubleSpinBox:disabled {{
                background-color: {colors['background'].name()};
                color: {colors['text_disabled'].name()};
                border-color: {colors['text_disabled'].name()};
                opacity: 0.6;
            }}
        """
        
        self.setStyleSheet(style_sheet)

    def set_value_animated(self, value: float, duration: Optional[int] = None):
        """**Set value with smooth animation and performance optimization**"""
        if self._is_animating:
            self._value_group.stop()
        
        current_value = self.value()
        if abs(current_value - value) < 1e-10:  # Floating point comparison
            return
            
        self._set_animating(True)
        
        # Dynamic duration based on value difference
        if duration is None:
            diff = abs(value - current_value)
            duration = min(FluentAnimation.DURATION_MEDIUM, max(200, int(diff * 50)))
        
        # Setup scale out animation
        self._value_scale_out.setStartValue(1.0)
        self._value_scale_out.setEndValue(0.95)
        
        # Setup value change animation
        self._value_change_anim.setDuration(duration)
        self._value_change_anim.setStartValue(current_value)
        self._value_change_anim.setEndValue(value)
        
        # Setup scale in animation
        self._value_scale_in.setStartValue(0.95)
        self._value_scale_in.setEndValue(1.0)
        
        self._value_group.start()
        
        # Emit custom signal
        self.value_changed_animated.emit(value)

    def _play_entrance_animation(self):
        """Play entrance animation with modern effects"""
        # Start with invisible and scaled down
        self._animated_props.set_scale_factor(0.8)
        opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0.0)
        
        # Animate opacity
        opacity_anim = QPropertyAnimation(opacity_effect, QByteArray(b"opacity"))
        opacity_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Animate scale
        scale_anim = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
        scale_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
        scale_anim.setStartValue(0.8)
        scale_anim.setEndValue(1.0)
        scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        
        # Play both animations together
        entrance_group = QParallelAnimationGroup(self)
        entrance_group.addAnimation(opacity_anim)
        entrance_group.addAnimation(scale_anim)
        def clear_graphics_effect():
            if self.graphicsEffect() is not None:
                self.setGraphicsEffect(None)  # type: ignore[call-arg]
        entrance_group.finished.connect(clear_graphics_effect)
        entrance_group.start()

    def _set_animating(self, animating: bool):
        """Set animation state with optimization"""
        self._is_animating = animating
        if not animating:
            self.update()  # Force repaint when animation completes

    def enterEvent(self, event):
        """Enhanced hover enter with performance optimization"""
        if self._is_hovered:
            return
            
        self._is_hovered = True
        
        # Stop any running hover animations
        if self._hover_group.state() == QParallelAnimationGroup.State.Running:
            self._hover_group.stop()
        
        # Setup hover in animations
        self._hover_shadow_anim.setStartValue(self._animated_props.get_shadow_blur())
        self._hover_shadow_anim.setEndValue(8.0)
        
        self._hover_glow_anim.setStartValue(self._animated_props.get_glow_intensity())
        self._hover_glow_anim.setEndValue(0.3)
        
        self._hover_group.start()
        
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Enhanced hover leave with smooth transition"""
        if not self._is_hovered:
            return
            
        self._is_hovered = False
        
        # Stop any running hover animations
        if self._hover_group.state() == QParallelAnimationGroup.State.Running:
            self._hover_group.stop()
        
        # Setup hover out animations
        self._hover_shadow_anim.setStartValue(self._animated_props.get_shadow_blur())
        self._hover_shadow_anim.setEndValue(0.0)
        
        self._hover_glow_anim.setStartValue(self._animated_props.get_glow_intensity())
        self._hover_glow_anim.setEndValue(0.0)
        
        self._hover_group.start()
        
        super().leaveEvent(event)

    def focusInEvent(self, event):
        """Enhanced focus in with modern animations"""
        if self._is_focused:
            return
            
        self._is_focused = True
        
        # Setup focus animations
        self._focus_scale_anim.setStartValue(self._animated_props.get_scale_factor())
        self._focus_scale_anim.setEndValue(1.02)
        
        self._focus_glow_anim.setStartValue(self._animated_props.get_glow_intensity())
        self._focus_glow_anim.setEndValue(0.5)
        
        self._focus_group.start()
        
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Enhanced focus out with smooth transition"""
        if not self._is_focused:
            return
            
        self._is_focused = False
        
        # Setup focus out animations
        self._focus_scale_anim.setStartValue(self._animated_props.get_scale_factor())
        self._focus_scale_anim.setEndValue(1.0)
        
        self._focus_glow_anim.setStartValue(self._animated_props.get_glow_intensity())
        self._focus_glow_anim.setEndValue(0.0)
        
        self._focus_group.start()
        
        super().focusOutEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Enhanced wheel event with visual feedback"""
        if not self.hasFocus():
            return
            
        old_value = self.value()
        super().wheelEvent(event)
        new_value = self.value()
        
        if abs(old_value - new_value) > 1e-10:  # Floating point comparison
            # Quick scale pulse for wheel changes
            pulse_anim = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
            pulse_anim.setDuration(150)
            pulse_anim.setStartValue(1.0)
            pulse_anim.setKeyValueAt(0.5, 1.05)
            pulse_anim.setEndValue(1.0)
            pulse_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            pulse_anim.start()

    def stepBy(self, steps: int):
        """Enhanced step by with directional feedback"""
        old_value = self.value()
        super().stepBy(steps)
        new_value = self.value()
        
        if abs(old_value - new_value) > 1e-10:  # Floating point comparison
            # Directional animation feedback
            direction_scale = 1.03 if steps > 0 else 0.97
            
            direction_anim = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
            direction_anim.setDuration(200)
            direction_anim.setStartValue(1.0)
            direction_anim.setKeyValueAt(0.5, direction_scale)
            direction_anim.setEndValue(1.0)
            direction_anim.setEasingCurve(QEasingCurve.Type.OutElastic)
            direction_anim.start()

    def paintEvent(self, event):
        """**Enhanced paint event with optimized custom effects**"""
        super().paintEvent(event)
        
        # Only add custom effects if there are active animations
        if (self._animated_props.get_glow_intensity() > 0 or 
            self._animated_props.get_shadow_blur() > 0 or 
            abs(self._animated_props.get_scale_factor() - 1.0) > 0.01):
            
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Apply scale transform
            if abs(self._animated_props.get_scale_factor() - 1.0) > 0.01:
                center = self.rect().center()
                painter.translate(center)
                painter.scale(self._animated_props.get_scale_factor(), 
                            self._animated_props.get_scale_factor())
                painter.translate(-center)
            
            # Draw glow effect
            if self._animated_props.get_glow_intensity() > 0:
                self._draw_glow_effect(painter)

    def _draw_glow_effect(self, painter: QPainter):
        """Draw custom glow effect with path caching for enhanced visual feedback"""
        # Check if glow path needs to be recreated (size changed)
        current_size = (self.width(), self.height())
        if self._cached_glow_path is None or self._last_size_for_path != current_size:
            # Create glow path
            glow_rect = self.rect().adjusted(-2, -2, 2, 2)
            self._cached_glow_path = QPainterPath()
            self._cached_glow_path.addRoundedRect(glow_rect, 10, 10)
            self._last_size_for_path = current_size
        
        colors = self._cached_theme_colors
        glow_color = colors['primary']
        glow_color.setAlphaF(self._animated_props.get_glow_intensity() * 0.3)
        
        # Draw glow
        painter.setBrush(QBrush(glow_color))
        painter.setPen(glow_color)
        painter.drawPath(self._cached_glow_path)

    def _on_value_changed(self, value: float):
        """Handle value changes with optimized feedback"""
        if not self._is_animating:
            # Quick feedback for direct value changes
            feedback_anim = QPropertyAnimation(self._animated_props, QByteArray(b"scale_factor"))
            feedback_anim.setDuration(100)
            feedback_anim.setStartValue(self._animated_props.get_scale_factor())
            feedback_anim.setKeyValueAt(0.5, 1.02)
            feedback_anim.setEndValue(1.0)
            feedback_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            feedback_anim.start()

    def _on_hover_animation_finished(self):
        """Handle hover animation completion"""
        # Optimize by reducing update frequency when not animating
        if not self._is_hovered and self._animated_props.get_glow_intensity() <= 0:
            self.update()

    def _on_theme_changed_debounced(self, theme_name: str):
        """Debounced theme change handler for performance"""
        self._theme_update_timer.start(50)  # 50ms debounce

    def _apply_theme_update(self):
        """Apply theme update with smooth transition"""
        # Cache new colors
        self._cache_theme_colors()
        
        # Smooth transition effect
        transition_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(transition_effect)
        
        opacity_anim = QPropertyAnimation(transition_effect, QByteArray(b"opacity"))
        opacity_anim.setDuration(FluentAnimation.DURATION_FAST)
        opacity_anim.setStartValue(1.0)
        opacity_anim.setKeyValueAt(0.5, 0.8)
        opacity_anim.setEndValue(1.0)
        def clear_transition_effect():
            if self.graphicsEffect() is not None:
                self.setGraphicsEffect(None)  # type: ignore[call-arg]
        opacity_anim.finished.connect(clear_transition_effect)
        
        # Update style
        self._setup_style()
        opacity_anim.start()

    def cleanup(self):
        """Cleanup method for proper memory management"""
        # Stop all animations
        self._hover_group.stop()
        self._focus_group.stop()
        self._value_group.stop()
        
        # Clear cached data
        self._cached_theme_colors.clear()
        self._cached_glow_path = None
        
        # Disconnect signals
        try:
            theme_manager.theme_changed.disconnect(self._on_theme_changed_debounced)
        except:
            pass

    def __del__(self):
        """Destructor with cleanup"""
        self.cleanup()


class FluentNumberInput(QWidget):
    """**Enhanced Numeric Input with Modern Animations and Performance Optimizations**"""

    value_changed = Signal(float)
    
    def __init__(self, parent: Optional[QWidget] = None,
                 minimum: float = 0.0, maximum: float = 100.0,
                 decimals: int = 2, step: float = 1.0):
        super().__init__(parent)
        
        self._minimum = minimum
        self._maximum = maximum
        self._decimals = decimals
        self._step = step
        self._value = minimum
        
        # Performance optimization
        self._layout_cache = None
        self._button_animations = {}
        self._cached_button_rects = {}
        self._last_button_sizes = {}
        self._cached_colors = None
        
        self._setup_ui()
        self._setup_responsive_layout()
        
        # Entrance animation
        self._play_entrance_animation()

    def _setup_ui(self):
        """Setup UI with modern responsive design"""
        self._layout_cache = QHBoxLayout(self)
        self._layout_cache.setContentsMargins(4, 4, 4, 4)
        self._layout_cache.setSpacing(8)
        
        # Create enhanced buttons with modern styling
        self._create_control_buttons()
        self._create_spinbox()
        
        # Add widgets to layout
        self._layout_cache.addWidget(self.decrease_btn)
        self._layout_cache.addWidget(self.spin_box, 1)
        self._layout_cache.addWidget(self.increase_btn)
        
        self._setup_button_style()
        self._setup_button_interactions()
        self._connect_signals()

    def _create_control_buttons(self):
        """Create enhanced control buttons with modern animations"""
        button_size = 40  # Responsive size
        
        self.decrease_btn = QPushButton("−")
        self.decrease_btn.setFixedSize(button_size, button_size)
        self.decrease_btn.setObjectName("decrease_button")
        
        self.increase_btn = QPushButton("+")
        self.increase_btn.setFixedSize(button_size, button_size)
        self.increase_btn.setObjectName("increase_button")

    def _create_spinbox(self):
        """**Create appropriate spinbox based on decimal requirement**"""
        if self._decimals > 0:
            self.spin_box = FluentDoubleSpinBox()
            self.spin_box.setDecimals(self._decimals)
            self.spin_box.setRange(self._minimum, self._maximum)
            self.spin_box.setSingleStep(self._step)
            self.spin_box.setValue(self._value)
        else:
            self.spin_box = FluentSpinBox()
            self.spin_box.setRange(int(self._minimum), int(self._maximum))
            self.spin_box.setSingleStep(int(self._step))
            self.spin_box.setValue(int(self._value))

    def _setup_responsive_layout(self):
        """Setup responsive layout that adapts to container size"""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(48)  # Minimum touch-friendly height

    def _setup_button_style(self):
        """Setup modern button styling with cached colors"""
        # Cache theme colors for performance
        self._cached_colors = theme_manager.current_colors()
        colors = self._cached_colors
        
        style = f"""
            QPushButton {{
                background-color: {colors.get('surface', '#FFFFFF')};
                color: {colors.get('text_primary', '#000000')};
                border: 2px solid {colors.get('border', '#CCCCCC')};
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {colors.get('accent_light', '#E6F7FF')};
                border-color: {colors.get('primary', '#0078D4')};
            }}
            
            QPushButton:pressed {{
                background-color: {colors.get('primary', '#0078D4')};
                color: {colors.get('on_primary', '#FFFFFF')};
            }}
            
            QPushButton:disabled {{
                background-color: {colors.get('background', '#F0F0F0')};
                border-color: {colors.get('text_disabled', '#CCCCCC')};
                color: {colors.get('text_disabled', '#CCCCCC')};
            }}
        """
        
        self.decrease_btn.setStyleSheet(style)
        self.increase_btn.setStyleSheet(style)

    def _setup_button_interactions(self):
        """**Setup button interactions with optimized animations**"""
        # Increase button click handler
        def on_increase():
            if isinstance(self.spin_box, FluentDoubleSpinBox):
                step = self.spin_box.singleStep()
                new_value = min(self.spin_box.value() + step, self.spin_box.maximum())
                self.spin_box.set_value_animated(new_value)
            else:
                step = self.spin_box.singleStep()
                new_value = min(self.spin_box.value() + step, self.spin_box.maximum())
                self.spin_box.set_value_animated(new_value)
                
            self._animate_button(self.increase_btn, 1.1, 0.95)
        
        # Decrease button click handler
        def on_decrease():
            if isinstance(self.spin_box, FluentDoubleSpinBox):
                step = self.spin_box.singleStep()
                new_value = max(self.spin_box.value() - step, self.spin_box.minimum())
                self.spin_box.set_value_animated(new_value)
            else:
                step = self.spin_box.singleStep()
                new_value = max(self.spin_box.value() - step, self.spin_box.minimum())
                self.spin_box.set_value_animated(new_value)
                
            self._animate_button(self.decrease_btn, 1.1, 0.95)
        
        self.increase_btn.clicked.connect(on_increase)
        self.decrease_btn.clicked.connect(on_decrease)

    def _animate_button(self, button, scale_out=1.1, scale_in=0.95):
        """Apply optimized button animation with caching"""
        # Get or create cached rectangle for this button
        button_id = id(button)
        current_size = (button.width(), button.height())
        
        if button_id not in self._cached_button_rects or self._last_button_sizes.get(button_id) != current_size:
            # Button geometry
            rect = button.geometry()
            center_x = rect.center().x()
            center_y = rect.center().y()
            width = rect.width()
            height = rect.height()
            
            # Cache original and scaled rectangles
            self._cached_button_rects[button_id] = {
                'original': rect,
                'out': QRect(
                    center_x - int(width * scale_out) // 2,
                    center_y - int(height * scale_out) // 2,
                    int(width * scale_out),
                    int(height * scale_out)
                ),
                'in': QRect(
                    center_x - int(width * scale_in) // 2,
                    center_y - int(height * scale_in) // 2,
                    int(width * scale_in),
                    int(height * scale_in)
                )
            }
            self._last_button_sizes[button_id] = current_size
        
        # Reuse existing animation if possible
        if button_id in self._button_animations:
            anim = self._button_animations[button_id]
            if anim.state() == QPropertyAnimation.State.Running:
                anim.stop()
        else:
            anim = QPropertyAnimation(button, QByteArray(b"geometry"))
            self._button_animations[button_id] = anim
            
        # Get cached rectangles
        rects = self._cached_button_rects[button_id]
        
        # Animation setup
        anim.setDuration(200)
        anim.setStartValue(rects['original'])
        anim.setKeyValueAt(0.3, rects['out'])
        anim.setKeyValueAt(0.6, rects['in'])
        anim.setEndValue(rects['original'])
        
        # Use modern easing curve
        anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        anim.start()

    def _connect_signals(self):
        """Connect signals for synchronized value updates"""
        # Update value when spinbox changes
        def on_spinbox_value_changed(value):
            if isinstance(self.spin_box, FluentDoubleSpinBox):
                self._value = float(value)
                self.value_changed.emit(float(value))
            else:
                self._value = float(value)
                self.value_changed.emit(float(value))
        
        # Connect the appropriate signal
        if isinstance(self.spin_box, FluentDoubleSpinBox):
            self.spin_box.valueChanged.connect(on_spinbox_value_changed)
        else:
            self.spin_box.valueChanged.connect(on_spinbox_value_changed)
        
        # Connect theme changes for button styling updates
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
    def _on_theme_changed(self):
        """Handle theme changes with optimized updates"""
        # Only update if colors have actually changed
        current_colors = theme_manager.current_colors()
        if self._cached_colors != current_colors:
            self._cached_colors = current_colors
            self._setup_button_style()

    def _play_entrance_animation(self):
        """Play modern entrance animation with staggered effects"""
        widgets = [self.decrease_btn, self.spin_box, self.increase_btn]
        
        for i, widget in enumerate(widgets):
            # Staggered entrance animation
            QTimer.singleShot(i * 50, lambda w=widget: self._animate_widget_entrance(w))

    def _animate_widget_entrance(self, widget):
        """Animate individual widget entrance"""
        # Start scaled down and transparent
        opacity_effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0.0)
        
        # Animate opacity
        opacity_anim = QPropertyAnimation(opacity_effect, QByteArray(b"opacity"))
        opacity_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Cleanup effect after animation
        opacity_anim.finished.connect(lambda: widget.setGraphicsEffect(None))
        opacity_anim.start()

    def set_value(self, value: float):
        """Set value with animated feedback"""
        # Update internal value
        self._value = max(min(value, self._maximum), self._minimum)
        
        # Update spinbox with animation
        if isinstance(self.spin_box, FluentDoubleSpinBox):
            self.spin_box.set_value_animated(float(value))
        else:
            self.spin_box.set_value_animated(int(value))

    def value(self) -> float:
        """Get current value"""
        return self._value

    def cleanup(self):
        """**Enhanced cleanup for proper memory management**"""
        # Stop all button animations
        for anim in self._button_animations.values():
            if anim and anim.state() == QPropertyAnimation.State.Running:
                anim.stop()
        
        # Clear caches
        self._button_animations.clear()
        self._cached_button_rects.clear()
        self._last_button_sizes.clear()
        self._cached_colors = None
        
        # Cleanup child widgets
        if hasattr(self.spin_box, 'cleanup'):
            self.spin_box.cleanup()
        
        # Disconnect signals
        try:
            theme_manager.theme_changed.disconnect(self._on_theme_changed)
        except:
            pass

    def __del__(self):
        """Destructor with cleanup"""
        self.cleanup()
