"""
Enhanced Animation System
Provides fluid animations and transitions with modern easing curves and effects.
Includes theme-aware animations and coordinated transitions.
"""

from typing import Optional, Callable, List, Dict, Any, Union, Tuple
from PySide6.QtCore import (QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
                            QSequentialAnimationGroup, QByteArray, QTimer, QRect, QPoint,
                            QObject, Signal, QAbstractAnimation, Property, Qt, QSize)
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect, QGraphicsBlurEffect
from PySide6.QtGui import QColor

# Import theme manager for theme-aware animations
from .theme import get_theme_manager, ThemeTransitionType


class ThemeAwareFluentAnimation:
    """Enhanced animation system with theme integration"""
    
    def __init__(self):
        self._theme_manager = get_theme_manager()
        self._active_animations: Dict[str, QPropertyAnimation] = {}
        self._animation_theme_colors: Dict[str, str] = {}
        self._theme_transition_callbacks: List[Callable] = []
        
        # Connect to theme signals
        self._theme_manager.theme_changed.connect(self._on_theme_changed)
        self._theme_manager.transition_started.connect(self._on_theme_transition_started)
        self._theme_manager.transition_finished.connect(self._on_theme_transition_finished)
    
    def _on_theme_changed(self):
        """Handle theme change by updating animation colors"""
        self._update_animation_colors()
    
    def _on_theme_transition_started(self, transition_type: str):
        """Handle theme transition start"""
        for callback in self._theme_transition_callbacks:
            callback(transition_type, True)
    
    def _on_theme_transition_finished(self):
        """Handle theme transition end"""
        for callback in self._theme_transition_callbacks:
            callback("", False)
    
    def _update_animation_colors(self):
        """Update colors in active animations based on current theme"""
        for animation_id, animation in self._active_animations.items():
            if animation_id in self._animation_theme_colors:
                color_name = self._animation_theme_colors[animation_id]
                new_color = self._theme_manager.get_color(color_name)
                animation.setEndValue(new_color)
    
    def register_theme_transition_callback(self, callback: Callable):
        """Register callback for theme transition events"""
        if callback not in self._theme_transition_callbacks:
            self._theme_transition_callbacks.append(callback)
    
    def unregister_theme_transition_callback(self, callback: Callable):
        """Unregister theme transition callback"""
        if callback in self._theme_transition_callbacks:
            self._theme_transition_callbacks.remove(callback)
    
    def create_theme_aware_color_animation(self, widget: QWidget, color_property: str,
                                         theme_color_name: str, duration: int = 250) -> QPropertyAnimation:
        """Create animation that uses theme colors"""
        animation = QPropertyAnimation(widget, QByteArray(color_property.encode()))
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Generate unique animation ID
        animation_id = f"{id(widget)}_{color_property}_{id(animation)}"
        
        # Store theme color reference for updates
        self._animation_theme_colors[animation_id] = theme_color_name
        
        # Set values based on current theme
        current_color = self._theme_manager.get_color(theme_color_name)
        animation.setStartValue(current_color.darker(120))
        animation.setEndValue(current_color)
        
        # Store animation for color updates
        self._active_animations[animation_id] = animation
        
        # Clean up when animation finishes
        def cleanup():
            self._active_animations.pop(animation_id, None)
            self._animation_theme_colors.pop(animation_id, None)
        
        animation.finished.connect(cleanup)
        
        return animation


# Global theme-aware animation instance
_theme_aware_animation = None

def get_theme_aware_animation() -> ThemeAwareFluentAnimation:
    """Get global theme-aware animation instance"""
    global _theme_aware_animation
    if _theme_aware_animation is None:
        _theme_aware_animation = ThemeAwareFluentAnimation()
    return _theme_aware_animation


class FluentAnimation:
    """Base animation constants and utility functions"""

    # Duration constants (in milliseconds)
    DURATION_INSTANT = 0
    DURATION_ULTRA_FAST = 50
    DURATION_VERY_FAST = 100
    DURATION_FAST = 150
    DURATION_MEDIUM = 200
    DURATION_SLOW = 300
    DURATION_VERY_SLOW = 400

    # Default properties
    DEFAULT_EASING = QEasingCurve.Type.OutCubic

    @staticmethod
    def create_animation(target: QObject, property_name: str, duration: int = DURATION_MEDIUM,
                         easing: QEasingCurve.Type = DEFAULT_EASING) -> QPropertyAnimation:
        """Creates a basic property animation with standard settings"""
        animation = QPropertyAnimation(
            target, QByteArray(property_name.encode()))
        animation.setDuration(duration)
        animation.setEasingCurve(easing)
        return animation

    @staticmethod
    def animate_property(target: QObject, property_name: str,
                         start_value: Any, end_value: Any,
                         duration: int = DURATION_MEDIUM,
                         easing: QEasingCurve.Type = DEFAULT_EASING,
                         auto_start: bool = True) -> QPropertyAnimation:
        """Creates and configures a complete animation ready to use"""
        anim = FluentAnimation.create_animation(
            target, property_name, duration, easing)
        anim.setStartValue(start_value)
        anim.setEndValue(end_value)

        if auto_start:
            anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

        return anim


class FluentTransition:
    """Enhanced transition effects for modern UI"""

    # Transition types
    FADE = "fade"
    SLIDE = "slide"
    SCALE = "scale"
    BLUR = "blur"
    MORPH = "morph"

    # Enhanced easing curves
    EASE_SPRING = QEasingCurve.Type.OutBack
    EASE_ELASTIC = QEasingCurve.Type.OutElastic
    EASE_BOUNCE = QEasingCurve.Type.OutBounce
    EASE_SMOOTH = QEasingCurve.Type.OutCubic
    EASE_CRISP = QEasingCurve.Type.OutQuart

    @staticmethod
    def create_transition(widget: QWidget, transition_type: str,
                          duration: int = FluentAnimation.DURATION_MEDIUM,
                          easing: QEasingCurve.Type = EASE_SMOOTH) -> QPropertyAnimation:
        """Create a transition animation"""
        if not widget or widget is None:
            print("Warning: Cannot create transition for None widget")
            return None

        if transition_type == FluentTransition.FADE:
            return FluentTransition._create_fade_transition(widget, duration, easing)
        elif transition_type == FluentTransition.SCALE:
            return FluentTransition._create_scale_transition(widget, duration, easing)
        elif transition_type == FluentTransition.SLIDE:
            return FluentTransition._create_slide_transition(widget, duration, easing)
        elif transition_type == FluentTransition.BLUR:
            return FluentTransition._create_blur_transition(widget, duration, easing)
        else:
            print(
                f"Warning: Unknown transition type '{transition_type}', using fade as fallback")
            return FluentTransition._create_fade_transition(widget, duration, easing)

    @staticmethod
    def _create_fade_transition(widget: QWidget, duration: int,
                                easing: QEasingCurve.Type) -> QPropertyAnimation:
        """Create fade transition"""
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
        animation.setDuration(duration)
        animation.setEasingCurve(easing)
        return animation

    @staticmethod
    def _create_scale_transition(widget: QWidget, duration: int,
                                 easing: QEasingCurve.Type) -> QPropertyAnimation:
        """Create scale transition"""
        animation = QPropertyAnimation(widget, QByteArray(b"geometry"))
        animation.setDuration(duration)
        animation.setEasingCurve(easing)

        # We don't set start/end values here as they'll be set when actually using the animation
        # This allows the caller to define the scale direction and magnitude
        return animation

    @staticmethod
    def _create_slide_transition(widget: QWidget, duration: int,
                                 easing: QEasingCurve.Type) -> QPropertyAnimation:
        """Create slide transition"""
        animation = QPropertyAnimation(widget, QByteArray(b"pos"))
        animation.setDuration(duration)
        animation.setEasingCurve(easing)
        return animation

    @staticmethod
    def _create_blur_transition(widget: QWidget, duration: int,
                                easing: QEasingCurve.Type) -> QPropertyAnimation:
        """Create blur transition"""
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsBlurEffect):
            effect = QGraphicsBlurEffect(widget)
            widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, QByteArray(b"blurRadius"))
        animation.setDuration(duration)
        animation.setEasingCurve(easing)
        return animation


class FluentSequence(QObject):
    """Manages complex animation sequences"""

    finished = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._sequence = QSequentialAnimationGroup()
        self._sequence.finished.connect(self.finished)

    def addAnimation(self, animation: QPropertyAnimation):
        """Add animation to sequence"""
        if animation:
            self._sequence.addAnimation(animation)
        return self  # Allow method chaining

    def addPause(self, duration: int):
        """Add pause to sequence"""
        self._sequence.addPause(duration)
        return self  # Allow method chaining

    def addCallback(self, callback: Callable):
        """Add callback function to sequence"""
        # Use QTimer instead of dummy animation to avoid target issues
        def timer_callback():
            try:
                callback()
            except Exception as e:
                print(f"FluentSequence callback error: {e}")
          # Create a minimal pause followed by timer callback
        self._sequence.addPause(1)  # 1ms pause
        # Schedule callback to run after the pause
        QTimer.singleShot(1, timer_callback)
        return self  # Allow method chaining

    def start(self):
        """Start the sequence"""
        self._sequence.start()
        return self  # Allow method chaining

    def stop(self):
        """Stop the sequence"""
        self._sequence.stop()
        return self  # Allow method chaining

    def isRunning(self) -> bool:
        """Check if sequence is currently running"""
        return self._sequence.state() == QAbstractAnimation.State.Running


class FluentParallel(QObject):
    """Manages parallel animation groups"""

    finished = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._parallel = QParallelAnimationGroup()
        self._parallel.finished.connect(self.finished)

    def addAnimation(self, animation: QPropertyAnimation):
        """Add animation to parallel group"""
        if animation:
            self._parallel.addAnimation(animation)
        return self  # Allow method chaining

    def start(self):
        """Start all animations in parallel"""
        self._parallel.start()
        return self  # Allow method chaining

    def stop(self):
        """Stop all animations"""
        self._parallel.stop()
        return self  # Allow method chaining

    def isRunning(self) -> bool:
        """Check if any animations are currently running"""
        return self._parallel.state() == QAbstractAnimation.State.Running


class FluentMicroInteraction:
    """Micro-interactions for enhanced user feedback"""

    @staticmethod
    def button_press(button: QWidget, scale: float = 0.95) -> Optional[QSequentialAnimationGroup]:
        """Micro-interaction for button press"""
        # Validate target widget
        if not button or button is None:
            return None

        try:
            original_size = button.size()
            pressed_size = QSize(int(original_size.width() * scale),
                                 int(original_size.height() * scale))

            # Press animation
            press_anim = QPropertyAnimation(button, QByteArray(b"geometry"))
            press_anim.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
            press_anim.setEasingCurve(FluentTransition.EASE_CRISP)

            # Calculate new geometry
            original_rect = button.geometry()
            size_diff_w = original_size.width() - pressed_size.width()
            size_diff_h = original_size.height() - pressed_size.height()

            new_rect = QRect(
                original_rect.x() + size_diff_w // 2,
                original_rect.y() + size_diff_h // 2,
                pressed_size.width(),
                pressed_size.height()
            )

            press_anim.setStartValue(original_rect)
            press_anim.setEndValue(new_rect)

            # Release animation
            release_anim = QPropertyAnimation(button, QByteArray(b"geometry"))
            release_anim.setDuration(FluentAnimation.DURATION_FAST)
            release_anim.setEasingCurve(FluentTransition.EASE_SPRING)
            release_anim.setStartValue(new_rect)
            release_anim.setEndValue(original_rect)

            # Sequence
            sequence = QSequentialAnimationGroup(
                button)  # Set parent for auto-deletion
            sequence.addAnimation(press_anim)
            sequence.addAnimation(release_anim)
            # Ensure it's deleted after running
            sequence.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            return sequence
        except Exception as e:
            print(f"FluentMicroInteraction.button_press error: {e}")
            return None

    @staticmethod
    def hover_glow(widget: QWidget, intensity: float = 0.2) -> Optional[QPropertyAnimation]:
        """Add subtle glow effect on hover"""
        # Validate target widget
        if not widget or widget is None:
            return None

        try:
            effect = widget.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(effect)

            glow_in = QPropertyAnimation(effect, QByteArray(b"opacity"))
            glow_in.setDuration(FluentAnimation.DURATION_FAST)
            glow_in.setEasingCurve(FluentTransition.EASE_SMOOTH)
            glow_in.setStartValue(1.0)  # Assuming current opacity is 1.0
            glow_in.setEndValue(min(1.0, 1.0 + intensity if intensity >= 0
                                    else 1.0 - abs(intensity)))  # Clamp opacity
            return glow_in
        except Exception as e:
            print(f"FluentMicroInteraction.hover_glow error: {e}")
            return None

    @staticmethod
    def scale_animation(widget: QWidget, scale: float = 0.95) -> Optional[QPropertyAnimation]:
        """Create a simple scale animation"""
        # Validate target widget
        if not widget or widget is None:
            return None

        try:
            original_rect = widget.geometry()
            width = int(original_rect.width() * scale)
            height = int(original_rect.height() * scale)

            x = original_rect.x() + (original_rect.width() - width) // 2
            y = original_rect.y() + (original_rect.height() - height) // 2

            new_rect = QRect(x, y, width, height)

            anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
            anim.setDuration(FluentAnimation.DURATION_FAST)
            anim.setEasingCurve(FluentTransition.EASE_SPRING)
            anim.setStartValue(original_rect)
            anim.setEndValue(new_rect)
            anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            return anim
        except Exception as e:
            print(f"FluentMicroInteraction.scale_animation error: {e}")
            return None

    @staticmethod
    def pulse_animation(widget: QWidget, scale: float = 1.05) -> Optional[QSequentialAnimationGroup]:
        """Create a pulse animation effect"""
        # Validate target widget
        if not widget or widget is None:
            return None

        try:
            original_rect = widget.geometry()
            width = int(original_rect.width() * scale)
            height = int(original_rect.height() * scale)

            x = original_rect.x() - (width - original_rect.width()) // 2
            y = original_rect.y() - (height - original_rect.height()) // 2

            expanded_rect = QRect(x, y, width, height)

            sequence = QSequentialAnimationGroup(widget)

            # Expand animation
            expand_anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
            expand_anim.setDuration(FluentAnimation.DURATION_FAST)
            expand_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
            expand_anim.setStartValue(original_rect)
            expand_anim.setEndValue(expanded_rect)
            sequence.addAnimation(expand_anim)

            # Contract animation
            contract_anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
            contract_anim.setDuration(FluentAnimation.DURATION_FAST)
            contract_anim.setEasingCurve(FluentTransition.EASE_SPRING)
            contract_anim.setStartValue(expanded_rect)
            contract_anim.setEndValue(original_rect)
            sequence.addAnimation(contract_anim)

            sequence.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            return sequence
        except Exception as e:
            print(f"FluentMicroInteraction.pulse_animation error: {e}")
            return None

    @staticmethod
    def shake_animation(widget: QWidget, intensity: float = 5) -> QSequentialAnimationGroup:
        """Create a shake animation for error feedback"""
        # Validate target widget
        if not widget:
            print("Warning: Cannot create shake animation for None widget")
            return QSequentialAnimationGroup()  # Return empty group

        try:
            original_pos = widget.pos()
            sequence = QSequentialAnimationGroup(widget)

            # Create shake movement
            for i in range(3):
                # Move right
                right_anim = QPropertyAnimation(widget, QByteArray(b"pos"))
                right_anim.setDuration(50)
                right_anim.setStartValue(original_pos)
                right_anim.setEndValue(
                    QPoint(original_pos.x() + int(intensity), original_pos.y()))
                right_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
                sequence.addAnimation(right_anim)

                # Move left
                left_anim = QPropertyAnimation(widget, QByteArray(b"pos"))
                left_anim.setDuration(50)
                left_anim.setStartValue(
                    QPoint(original_pos.x() + int(intensity), original_pos.y()))
                left_anim.setEndValue(
                    QPoint(original_pos.x() - int(intensity), original_pos.y()))
                left_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
                sequence.addAnimation(left_anim)

                # Return to center
                center_anim = QPropertyAnimation(widget, QByteArray(b"pos"))
                center_anim.setDuration(50)
                center_anim.setStartValue(
                    QPoint(original_pos.x() - int(intensity), original_pos.y()))
                center_anim.setEndValue(original_pos)
                center_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
                sequence.addAnimation(center_anim)

            sequence.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            return sequence
        except Exception as e:
            print(f"FluentMicroInteraction.shake_animation error: {e}")
            return QSequentialAnimationGroup()  # Return empty group

    @staticmethod
    def ripple_effect(widget: QWidget) -> Optional[QSequentialAnimationGroup]:
        """Create ripple effect at specified position"""
        # Validate target widget
        if not widget or widget is None:
            return None

        try:
            # This would typically involve creating a temporary widget overlay
            # For now, we'll simulate with a scale animation
            ripple_anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
            ripple_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
            ripple_anim.setEasingCurve(FluentTransition.EASE_ELASTIC)

            original_rect = widget.geometry()
            expanded_rect = original_rect.adjusted(-5, -5, 5, 5)

            ripple_anim.setStartValue(original_rect)
            ripple_anim.setEndValue(expanded_rect)

            # Return to normal
            return_anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
            return_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
            return_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
            return_anim.setStartValue(expanded_rect)
            return_anim.setEndValue(original_rect)

            sequence = QSequentialAnimationGroup(widget)  # Set parent
            sequence.addAnimation(ripple_anim)
            sequence.addAnimation(return_anim)
            sequence.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

            return sequence
        except Exception as e:
            print(f"FluentMicroInteraction.ripple_effect error: {e}")
            return None


class FluentStateTransition:
    """Manages smooth transitions between widget states"""

    def __init__(self, widget: QWidget):
        self.widget = widget
        # Changed type to QParallelAnimationGroup
        self._state_animations: Dict[str, QParallelAnimationGroup] = {}
        self._current_state = "default"
        self._property_setters: Dict[str, Callable[[QObject, Any], None]] = {}

    def registerPropertySetter(self, prop_name: str, setter: Callable[[QObject, Any], None]):
        """Register a custom property setter for properties that need special handling"""
        self._property_setters[prop_name] = setter
        return self  # Allow method chaining

    def addState(self, state_name: str, properties: Dict[str, Any],
                 duration: int = FluentAnimation.DURATION_MEDIUM,
                 easing: QEasingCurve.Type = FluentTransition.EASE_SMOOTH):
        """Add a state with its properties"""
        animations = QParallelAnimationGroup()

        for prop_name, value in properties.items():
            # Check if we have a custom setter for this property
            if prop_name in self._property_setters:
                # Create a special animation using the custom setter
                animation = QPropertyAnimation(
                    self.widget, QByteArray(prop_name.encode()))
                animation.setDuration(duration)
                animation.setEasingCurve(easing)
                animation.setEndValue(value)
                animations.addAnimation(animation)
            else:
                # Ensure property name is bytes for QByteArray
                # Create QByteArray for property animation
                byte_prop_name = QByteArray(prop_name.encode('utf-8'))
                # Use original string for property lookup since indexOfProperty expects a string
                if hasattr(self.widget, prop_name) or self.widget.metaObject().indexOfProperty(prop_name) != -1:
                    animation = QPropertyAnimation(self.widget, byte_prop_name)
                    animation.setDuration(duration)
                    animation.setEasingCurve(easing)
                    animation.setEndValue(value)
                    animations.addAnimation(animation)
                # else:
                    # print(f"Warning: Property '{prop_name}' not found on widget {self.widget}")

        self._state_animations[state_name] = animations
        return self  # Allow method chaining

    def transitionTo(self, state_name: str):
        """Transition to specified state"""
        if state_name in self._state_animations and state_name != self._current_state:
            # Stop any currently running animations
            for anim_state, anim_group in self._state_animations.items():
                if anim_group.state() == QAbstractAnimation.State.Running:
                    anim_group.stop()

            # Start new animation
            self._state_animations[state_name].start(
                QAbstractAnimation.DeletionPolicy.KeepWhenStopped)
            self._current_state = state_name
        return self  # Allow method chaining

    def getCurrentState(self) -> str:
        """Get current state name"""
        return self._current_state

    def getState(self, state_name: str) -> Optional[QParallelAnimationGroup]:
        """Get animation group for a state"""
        return self._state_animations.get(state_name)


class FluentRevealEffect:
    """Modern reveal animations for content"""

    @staticmethod
    def fade_in(widget: QWidget, duration: int = 300) -> Optional[QPropertyAnimation]:
        """Fade in animation"""
        if not widget:
            print("Warning: Cannot create fade-in effect for None widget")
            return None

        try:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            effect.setOpacity(0)

            fade_anim = QPropertyAnimation(effect, QByteArray(b"opacity"))
            fade_anim.setDuration(duration)
            fade_anim.setStartValue(0.0)
            fade_anim.setEndValue(1.0)
            fade_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
            fade_anim.start(
                QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            return fade_anim
        except Exception as e:
            print(f"FluentRevealEffect.fade_in error: {e}")
            return None

    @staticmethod
    def fade_out(widget: QWidget, duration: int = 300) -> Optional[QPropertyAnimation]:
        """Fade out animation"""
        if not widget:
            print("Warning: Cannot create fade-out effect for None widget")
            return None

        try:
            effect = widget.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(effect)

            fade_anim = QPropertyAnimation(effect, QByteArray(b"opacity"))
            fade_anim.setDuration(duration)
            fade_anim.setStartValue(1.0)
            fade_anim.setEndValue(0.0)
            fade_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
            fade_anim.start(
                QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            return fade_anim
        except Exception as e:
            print(f"FluentRevealEffect.fade_out error: {e}")
            return None

    @staticmethod
    def slide_in(widget: QWidget, duration: int = 300,
                 direction: str = "up") -> Optional[QPropertyAnimation]:
        """Slide in animation from specified direction"""
        if not widget:
            print("Warning: Cannot create slide-in effect for None widget")
            return None

        try:
            original_pos = widget.pos()
            start_pos = QPoint(original_pos)

            if direction == "up":
                start_pos.setY(original_pos.y() + 30)
            elif direction == "down":
                start_pos.setY(original_pos.y() - 30)
            elif direction == "left":
                start_pos.setX(original_pos.x() + 30)
            elif direction == "right":
                start_pos.setX(original_pos.x() - 30)

            widget.move(start_pos)  # Move to start position before animation

            slide_anim = QPropertyAnimation(widget, QByteArray(b"pos"))
            slide_anim.setDuration(duration)
            slide_anim.setStartValue(start_pos)
            slide_anim.setEndValue(original_pos)
            slide_anim.setEasingCurve(FluentTransition.EASE_SPRING)
            slide_anim.start(
                QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            return slide_anim
        except Exception as e:
            print(f"FluentRevealEffect.slide_in error: {e}")
            return None

    @staticmethod
    def scale_in(widget: QWidget, duration: int = 200) -> Optional[QPropertyAnimation]:
        """Scale in animation"""
        if not widget:
            print("Warning: Cannot create scale-in effect for None widget")
            return None

        try:
            original_rect = widget.geometry()
            start_rect = QRect(
                original_rect.center().x() - 1,
                original_rect.center().y() - 1,
                2, 2
            )

            widget.setGeometry(start_rect)  # Set initial size

            scale_anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
            scale_anim.setDuration(duration)
            scale_anim.setStartValue(start_rect)
            scale_anim.setEndValue(original_rect)
            scale_anim.setEasingCurve(FluentTransition.EASE_SPRING)
            scale_anim.start(
                QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            return scale_anim
        except Exception as e:
            print(f"FluentRevealEffect.scale_in error: {e}")
            return None

    @staticmethod
    def reveal_up(widget: QWidget, delay: int = 0) -> Optional[QPropertyAnimation]:
        """Reveal widget from bottom"""
        if not widget:
            print("Warning: Cannot create reveal-up effect for None widget")
            return None

        try:
            original_pos = widget.pos()
            start_pos = QPoint(original_pos.x(), original_pos.y() + 30)
            widget.move(start_pos)  # Set initial position

            reveal_anim = QPropertyAnimation(widget, QByteArray(b"pos"))
            reveal_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
            reveal_anim.setEasingCurve(FluentTransition.EASE_SPRING)
            reveal_anim.setStartValue(start_pos)
            reveal_anim.setEndValue(original_pos)

            if delay > 0:
                # Use a QTimer associated with the widget to ensure it's managed
                timer = QTimer(widget)
                timer.setSingleShot(True)
                timer.timeout.connect(lambda: reveal_anim.start(
                    QAbstractAnimation.DeletionPolicy.DeleteWhenStopped))
                timer.start(delay)
            else:
                reveal_anim.start(
                    QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

            return reveal_anim
        except Exception as e:
            print(f"FluentRevealEffect.reveal_up error: {e}")
            return None

    @staticmethod
    def reveal_fade(widget: QWidget, duration: int = FluentAnimation.DURATION_MEDIUM,
                    start_value: float = 0.0, end_value: float = 1.0,
                    easing_curve_type: QEasingCurve.Type = FluentTransition.EASE_SMOOTH):
        """
        Applies a fade-in reveal effect to the widget.
        The animation is started immediately and will be deleted when stopped.
        """
        if not widget:
            print("Warning: Cannot create reveal-fade effect for None widget")
            return None

        try:
            opacity_effect = widget.graphicsEffect()
            if not isinstance(opacity_effect, QGraphicsOpacityEffect):
                opacity_effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(opacity_effect)

            opacity_effect.setOpacity(start_value)  # Set initial opacity

            animation = QPropertyAnimation(
                opacity_effect, QByteArray(b"opacity"), widget)
            animation.setDuration(duration)
            animation.setStartValue(start_value)
            animation.setEndValue(end_value)
            animation.setEasingCurve(easing_curve_type)

            animation.start(
                QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            return animation
        except Exception as e:
            print(f"FluentRevealEffect.reveal_fade error: {e}")
            return None

    @staticmethod
    def reveal_scale(widget: QWidget, delay: int = 0) -> Optional[QPropertyAnimation]:
        """Reveal widget with scale effect"""
        if not widget:
            print("Warning: Cannot create reveal-scale effect for None widget")
            return None

        try:
            original_rect = widget.geometry()
            center_x = original_rect.center().x()
            center_y = original_rect.center().y()

            start_rect = QRect(
                center_x - 1,
                center_y - 1,
                2, 2
            )

            widget.setGeometry(start_rect)  # Set initial size

            scale_anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
            scale_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
            scale_anim.setEasingCurve(FluentTransition.EASE_SPRING)
            scale_anim.setStartValue(start_rect)
            scale_anim.setEndValue(original_rect)

            if delay > 0:
                timer = QTimer(widget)
                timer.setSingleShot(True)
                timer.timeout.connect(lambda: scale_anim.start(
                    QAbstractAnimation.DeletionPolicy.DeleteWhenStopped))
                timer.start(delay)
            else:
                scale_anim.start(
                    QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

            return scale_anim
        except Exception as e:
            print(f"FluentRevealEffect.reveal_scale error: {e}")
            return None

    @staticmethod
    def staggered_reveal(widgets: List[QWidget], transition_type: str = "fade",
                         stagger_delay: int = 100,
                         duration: int = FluentAnimation.DURATION_MEDIUM) -> QSequentialAnimationGroup:
        """
        Reveal multiple widgets with staggered timing

        transition_type: "fade", "up", "scale" or others
        """
        if not widgets:
            print("Warning: Cannot create staggered reveal with empty widgets list")
            return QSequentialAnimationGroup()

        try:
            # Use sequential group to ensure proper timing control
            animations_group = QSequentialAnimationGroup()

            for i, widget in enumerate(widgets):
                if not widget:
                    continue

                # Create a parallel group for this widget's animations
                widget_animations = QParallelAnimationGroup()

                # Choose animation type
                if transition_type == "fade":
                    effect = QGraphicsOpacityEffect(widget)
                    widget.setGraphicsEffect(effect)
                    effect.setOpacity(0)

                    fade_anim = QPropertyAnimation(
                        effect, QByteArray(b"opacity"))
                    fade_anim.setDuration(duration)
                    fade_anim.setStartValue(0.0)
                    fade_anim.setEndValue(1.0)
                    fade_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
                    widget_animations.addAnimation(fade_anim)

                elif transition_type == "up":
                    original_pos = widget.pos()
                    start_pos = QPoint(original_pos.x(), original_pos.y() + 30)
                    widget.move(start_pos)

                    move_anim = QPropertyAnimation(widget, QByteArray(b"pos"))
                    move_anim.setDuration(duration)
                    move_anim.setStartValue(start_pos)
                    move_anim.setEndValue(original_pos)
                    move_anim.setEasingCurve(FluentTransition.EASE_SPRING)
                    widget_animations.addAnimation(move_anim)

                elif transition_type == "scale":
                    original_rect = widget.geometry()
                    center_x = original_rect.center().x()
                    center_y = original_rect.center().y()

                    start_rect = QRect(
                        center_x - 1,
                        center_y - 1,
                        2, 2
                    )
                    widget.setGeometry(start_rect)

                    scale_anim = QPropertyAnimation(
                        widget, QByteArray(b"geometry"))
                    scale_anim.setDuration(duration)
                    scale_anim.setStartValue(start_rect)
                    scale_anim.setEndValue(original_rect)
                    scale_anim.setEasingCurve(FluentTransition.EASE_SPRING)
                    widget_animations.addAnimation(scale_anim)

                # Only add a pause for widgets after the first one
                if i > 0:
                    animations_group.addPause(stagger_delay)

                # Add this widget's animations
                animations_group.addAnimation(widget_animations)

            # Start the animations
            if animations_group.animationCount() > 0:
                animations_group.start(
                    QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

            return animations_group
        except Exception as e:
            print(f"FluentRevealEffect.staggered_reveal error: {e}")
            return QSequentialAnimationGroup()


class FluentLayoutTransition:
    """Smooth transitions for layout changes"""

    @staticmethod
    def prepare_layout_change(container: QWidget) -> Dict[QWidget, QRect]:
        """
        Capture current widget positions before a layout change

        Call this before modifying the layout to store original positions
        """
        if not container:
            print("Warning: Cannot prepare layout change for None container")
            return {}

        try:
            original_geometries = {}
            layout = container.layout()

            if not layout:
                return original_geometries

            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and item.widget():
                    child_widget = item.widget()
                    original_geometries[child_widget] = child_widget.geometry()

            return original_geometries
        except Exception as e:
            print(f"FluentLayoutTransition.prepare_layout_change error: {e}")
            return {}

    @staticmethod
    def animate_layout_change(container: QWidget,
                              original_geometries: Dict[QWidget, QRect],
                              duration: int = FluentAnimation.DURATION_MEDIUM,
                              easing_curve: QEasingCurve.Type = FluentTransition.EASE_SMOOTH) -> QParallelAnimationGroup:
        """
        Animate layout changes using original positions

        Usage:
        1. original_geometries = FluentLayoutTransition.prepare_layout_change(container)
        2. [Make your layout changes]
        3. FluentLayoutTransition.animate_layout_change(container, original_geometries)
        """
        if not container:
            print("Warning: Cannot animate layout change for None container")
            return QParallelAnimationGroup()

        try:
            animations = QParallelAnimationGroup(container)
            layout = container.layout()

            if not layout or not original_geometries:
                return animations

            # Process all widgets in the layout
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and item.widget():
                    child = item.widget()
                    if child in original_geometries:
                        original_rect = original_geometries[child]
                        target_rect = child.geometry()

                        # Only animate if position actually changed
                        if original_rect != target_rect:
                            # Set to original position
                            child.setGeometry(original_rect)

                            # Create animation to new position
                            anim = QPropertyAnimation(
                                child, QByteArray(b"geometry"))
                            anim.setDuration(duration)
                            anim.setEasingCurve(easing_curve)
                            anim.setStartValue(original_rect)
                            anim.setEndValue(target_rect)
                            animations.addAnimation(anim)

            if animations.animationCount() > 0:
                animations.start(
                    QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

            return animations
        except Exception as e:
            print(f"FluentLayoutTransition.animate_layout_change error: {e}")
            return QParallelAnimationGroup()

    @staticmethod
    def animated_visibility_change(widgets: List[Tuple[QWidget, bool]],
                                   duration: int = FluentAnimation.DURATION_MEDIUM) -> QParallelAnimationGroup:
        """
        Animate visibility changes for multiple widgets

        Args:
            widgets: List of (widget, should_show) tuples
            duration: Animation duration

        Returns:
            QParallelAnimationGroup: Animation group containing all animations
        """
        animations = QParallelAnimationGroup()

        try:
            for widget, should_show in widgets:
                if not widget:
                    continue

                # Create opacity effect if needed
                effect = widget.graphicsEffect()
                if not isinstance(effect, QGraphicsOpacityEffect):
                    effect = QGraphicsOpacityEffect(widget)
                    widget.setGraphicsEffect(effect)

                # Make widget visible but transparent if showing
                if should_show:
                    widget.setVisible(True)

                # Create animation
                anim = QPropertyAnimation(effect, QByteArray(b"opacity"))
                anim.setDuration(duration)
                anim.setStartValue(0.0 if should_show else 1.0)
                anim.setEndValue(1.0 if should_show else 0.0)
                anim.setEasingCurve(FluentTransition.EASE_SMOOTH)

                # Hide widget when fade out completes
                if not should_show:
                    anim.finished.connect(lambda w=widget: w.setVisible(False))

                animations.addAnimation(anim)
        except Exception as e:
            print(
                f"FluentLayoutTransition.animated_visibility_change error: {e}")

        if animations.animationCount() > 0:
            animations.start(
                QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

        return animations
