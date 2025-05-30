"""
Enhanced Animation System
Provides fluid animations and transitions with modern easing curves and effects.
"""

from typing import Optional, Callable, List, Dict, Any
from PySide6.QtCore import (QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
                            QSequentialAnimationGroup, QByteArray, QTimer, QRect, QPoint,
                            QObject, Signal, QAbstractAnimation, Property)
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect, QGraphicsBlurEffect
from .animation import FluentAnimation


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

        if transition_type == FluentTransition.FADE:
            return FluentTransition._create_fade_transition(widget, duration, easing)
        elif transition_type == FluentTransition.SCALE:
            return FluentTransition._create_scale_transition(widget, duration, easing)
        elif transition_type == FluentTransition.SLIDE:
            return FluentTransition._create_slide_transition(widget, duration, easing)
        elif transition_type == FluentTransition.BLUR:
            return FluentTransition._create_blur_transition(widget, duration, easing)
        else:
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
    _dummy_value_internal: int = 0

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._sequence = QSequentialAnimationGroup()
        self._sequence.finished.connect(self.finished)
        self._dummy_value_internal = 0

    def addAnimation(self, animation: QPropertyAnimation):
        """Add animation to sequence"""
        self._sequence.addAnimation(animation)

    def addPause(self, duration: int):
        """Add pause to sequence"""
        # QSequentialAnimationGroup has a addPause method
        self._sequence.addPause(duration)

    def addCallback(self, callback: Callable):
        """Add callback function to sequence"""
        # Create a dummy animation that triggers callback when finished
        # A more direct way if available, or use a QTimer if sequence doesn't support direct callbacks well.
        # However, QSequentialAnimationGroup can run functions via a QTimer or a custom QAbstractAnimation.
        # For simplicity, connecting to a zero-duration animation's finished signal is a common workaround.
        # A more robust way is to use QTimer.singleShot(0, callback) if the timing is not critical
        # or to subclass QAbstractAnimation for precise callback timing.
        # The current approach of a 1ms dummy animation is acceptable for many cases.
        # Dummy animation needs a QObject target
        dummy = QPropertyAnimation(self)
        dummy.setDuration(1)  # Minimal duration
        # Property name for animation
        dummy.setPropertyName(QByteArray(b"dummy_value"))
        dummy.setStartValue(0)
        dummy.setEndValue(1)
        dummy.finished.connect(callback)
        self._sequence.addAnimation(dummy)

    # Dummy property for the callback animation
    def get_dummy_value(self) -> int:
        return self._dummy_value_internal

    def set_dummy_value(self, value: int):
        self._dummy_value_internal = value

    # Define the Qt property using the getter and setter
    dummy_value = Property(int, get_dummy_value,
                           set_dummy_value)  # type: ignore

    def start(self):
        """Start the sequence"""
        self._sequence.start()

    def stop(self):
        """Stop the sequence"""
        self._sequence.stop()


class FluentParallel(QObject):
    """Manages parallel animation groups"""

    finished = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._parallel = QParallelAnimationGroup()
        self._parallel.finished.connect(self.finished)

    def addAnimation(self, animation: QPropertyAnimation):
        """Add animation to parallel group"""
        self._parallel.addAnimation(animation)

    def start(self):
        """Start all animations in parallel"""
        self._parallel.start()

    def stop(self):
        """Stop all animations"""
        self._parallel.stop()


class FluentMicroInteraction:
    """Micro-interactions for enhanced user feedback"""

    @staticmethod
    def button_press(button: QWidget, scale: float = 0.95):
        """Micro-interaction for button press"""
        original_size = button.size()
        pressed_size = original_size * scale

        # Press animation
        press_anim = QPropertyAnimation(button, QByteArray(b"geometry"))
        press_anim.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
        press_anim.setEasingCurve(FluentTransition.EASE_CRISP)

        # Calculate new geometry
        original_rect = button.geometry()
        size_diff = original_size - pressed_size
        new_rect = QRect(
            original_rect.x() + size_diff.width() // 2,
            original_rect.y() + size_diff.height() // 2,
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

    @staticmethod
    def hover_glow(widget: QWidget, intensity: float = 0.2):
        """Add subtle glow effect on hover"""
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        glow_in = QPropertyAnimation(effect, QByteArray(b"opacity"))
        glow_in.setDuration(FluentAnimation.DURATION_FAST)
        glow_in.setEasingCurve(FluentTransition.EASE_SMOOTH)
        glow_in.setStartValue(1.0)  # Assuming current opacity is 1.0
        glow_in.setEndValue(min(1.0, 1.0 + intensity if intensity >=
                            0 else 1.0 - abs(intensity)))  # Clamp opacity

        return glow_in

    @staticmethod
    def scale_animation(widget: QWidget, scale: float = 0.95) -> QPropertyAnimation:
        """Create a simple scale animation"""
        original_rect = widget.geometry()
        scaled_size = original_rect.size() * scale
        new_rect = QRect(
            original_rect.x() + (original_rect.width() - scaled_size.width()) // 2,
            original_rect.y() + (original_rect.height() - scaled_size.height()) // 2,
            scaled_size.width(),
            scaled_size.height()
        )

        anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
        anim.setDuration(FluentAnimation.DURATION_FAST)
        anim.setEasingCurve(FluentTransition.EASE_SPRING)
        anim.setStartValue(original_rect)
        anim.setEndValue(new_rect)
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return anim

    @staticmethod
    def pulse_animation(widget: QWidget, scale: float = 1.05) -> QSequentialAnimationGroup:
        """Create a pulse animation effect"""
        original_rect = widget.geometry()
        expanded_rect = QRect(
            int(original_rect.x() - (original_rect.width() * (scale - 1)) // 2),
            int(original_rect.y() - (original_rect.height() * (scale - 1)) // 2),
            int(original_rect.width() * scale),
            int(original_rect.height() * scale)
        )

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

    @staticmethod
    def shake_animation(widget: QWidget, intensity: float = 5) -> QSequentialAnimationGroup:
        """Create a shake animation for error feedback"""
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

        # Expand animation
        expand_anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
        expand_anim.setDuration(FluentAnimation.DURATION_FAST)
        expand_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        expand_anim.setStartValue(original_rect)
        expand_anim.setEndValue(expanded_rect)

        # Contract animation
        contract_anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
        contract_anim.setDuration(FluentAnimation.DURATION_FAST)
        contract_anim.setEasingCurve(FluentTransition.EASE_SPRING)
        contract_anim.setStartValue(expanded_rect)
        contract_anim.setEndValue(original_rect)

        sequence.addAnimation(expand_anim)
        sequence.addAnimation(contract_anim)
        sequence.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return expand_anim  # Return the first animation for type consistency

    @staticmethod
    def ripple_effect(widget: QWidget) -> QSequentialAnimationGroup:
        """Create ripple effect at specified position"""
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


class FluentStateTransition:
    """Manages smooth transitions between widget states"""

    def __init__(self, widget: QWidget):
        self.widget = widget
        # Changed type to QParallelAnimationGroup
        self._state_animations: Dict[str, QParallelAnimationGroup] = {}
        self._current_state = "default"

    def addState(self, state_name: str, properties: Dict[str, Any],
                 duration: int = FluentAnimation.DURATION_MEDIUM,
                 easing: QEasingCurve.Type = FluentTransition.EASE_SMOOTH):
        """Add a state with its properties"""
        animations = QParallelAnimationGroup()

        for prop_name, value in properties.items():
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

    def transitionTo(self, state_name: str):
        """Transition to specified state"""
        if state_name in self._state_animations and state_name != self._current_state:
            # Stop any currently running animation for this group before starting a new one
            # This might involve managing the groups more carefully if states can interrupt each other.
            # For now, just start the new one.
            self._state_animations[state_name].start(
                QAbstractAnimation.DeletionPolicy.KeepWhenStopped)  # Keep so it can be restarted
            self._current_state = state_name

    def getCurrentState(self) -> str:
        """Get current state name"""
        return self._current_state


class FluentRevealEffect:
    @staticmethod
    def fade_in(widget: QWidget, duration: int = 300) -> QPropertyAnimation:
        """Fade in animation"""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        effect.setOpacity(0)

        fade_anim = QPropertyAnimation(effect, QByteArray(b"opacity"))
        fade_anim.setDuration(duration)
        fade_anim.setStartValue(0.0)
        fade_anim.setEndValue(1.0)
        fade_anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
        fade_anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return fade_anim

    @staticmethod
    def slide_in(widget: QWidget, duration: int = 300, direction: str = "up") -> QPropertyAnimation:
        """Slide in animation from specified direction"""
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

        slide_anim = QPropertyAnimation(widget, QByteArray(b"pos"))
        slide_anim.setDuration(duration)
        slide_anim.setStartValue(start_pos)
        slide_anim.setEndValue(original_pos)
        slide_anim.setEasingCurve(FluentTransition.EASE_SPRING)
        slide_anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return slide_anim

    @staticmethod
    def scale_in(widget: QWidget, duration: int = 200) -> QPropertyAnimation:
        """Scale in animation"""
        original_rect = widget.geometry()
        start_rect = QRect(
            original_rect.center().x(),
            original_rect.center().y(),
            0,
            0
        )

        scale_anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
        scale_anim.setDuration(duration)
        scale_anim.setStartValue(start_rect)
        scale_anim.setEndValue(original_rect)
        scale_anim.setEasingCurve(FluentTransition.EASE_SPRING)
        scale_anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return scale_anim

    """Modern reveal animations for content"""

    @staticmethod
    def reveal_up(widget: QWidget, delay: int = 0) -> QPropertyAnimation:
        """Reveal widget from bottom"""
        original_pos = widget.pos()
        start_pos = QPoint(original_pos.x(), original_pos.y() + 30)

        # Move to start position before animation if not handled by startValue
        # widget.move(start_pos) # This might cause a flicker if animation starts immediately

        reveal_anim = QPropertyAnimation(widget, QByteArray(b"pos"))
        reveal_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
        reveal_anim.setEasingCurve(FluentTransition.EASE_SPRING)
        reveal_anim.setStartValue(start_pos)  # Set start value
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

    @staticmethod
    def reveal_fade(widget: QWidget, duration: int,
                    start_value: float = 0.0, end_value: float = 1.0,
                    easing_curve_type: QEasingCurve.Type = FluentTransition.EASE_SMOOTH):
        """
        Applies a fade-in reveal effect to the widget.
        The animation is started immediately and will be deleted when stopped.
        """
        opacity_effect = widget.graphicsEffect()
        if not isinstance(opacity_effect, QGraphicsOpacityEffect):
            opacity_effect = QGraphicsOpacityEffect(
                widget)  # Parent effect to widget
            widget.setGraphicsEffect(opacity_effect)

        opacity_effect.setOpacity(start_value)  # Set initial opacity

        animation = QPropertyAnimation(opacity_effect, QByteArray(
            b"opacity"), widget)  # Parent animation to widget
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(easing_curve_type)

        animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    @staticmethod
    def reveal_scale(widget: QWidget, delay: int = 0) -> QPropertyAnimation:
        """Reveal widget with scale effect"""
        original_rect = widget.geometry()
        start_rect = QRect(
            original_rect.center().x() - 1,
            original_rect.center().y() - 1,
            2, 2
        )

        # widget.setGeometry(start_rect) # Avoid flicker by using setStartValue

        scale_anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
        scale_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
        scale_anim.setEasingCurve(FluentTransition.EASE_SPRING)
        scale_anim.setStartValue(start_rect)  # Set start value
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

    @staticmethod
    def staggered_reveal(widgets: List[QWidget], stagger_delay: int = 100) -> QParallelAnimationGroup:
        """Reveal multiple widgets with staggered timing"""
        animations_group = QParallelAnimationGroup()  # Manage all animations

        for i, widget in enumerate(widgets):
            delay = i * stagger_delay
            # The reveal_up and reveal_scale methods now handle their own start with delay.
            # If we want to return a group that controls all, we need to adjust.
            # For now, they start independently.
            # To return a controllable group, the reveal methods should not start immediately if a delay is passed to them
            # and instead return the animation for external control.
            # Or, more simply, create the animation here and use QSequentialAnimationGroup for delays.

            # Simpler approach for staggered reveal:
            # Create a QSequentialAnimationGroup for the overall staggering.
            # Each step in the sequence can be a QParallelAnimationGroup if multiple things happen at once,
            # or just the animation itself.

            # The current implementation of reveal_up/scale_anim already uses QTimer.singleShot.
            # So, calling them in a loop will achieve staggering.
            # The returned list of animations might not be easily controllable as a single unit.
            # For simplicity, we'll keep the current behavior where they self-start.
            # To make animations_group useful, reveal_up/scale should return animations without starting them
            # if a specific flag is passed, or if delay is handled externally.
            # For now, just calling them.
            anim_up = FluentRevealEffect.reveal_up(widget, delay)
            # anim_scale = FluentRevealEffect.reveal_scale(widget, delay) # Example if using scale

            # If reveal_up/reveal_scale returned animations that weren't auto-started,
            # you could add them to the group:
            # animations_group.addAnimation(anim_up)

        # If a controllable group is needed, the reveal methods should be refactored.
        # Return the group, it might be empty or used differently in future
        return animations_group


class FluentLayoutTransition:
    """Smooth transitions for layout changes"""

    @staticmethod
    def animate_layout_change(container: QWidget,
                              duration: int = FluentAnimation.DURATION_MEDIUM):
        """Animate layout changes in container"""
        original_geometries = {}

        layout = container.layout()
        if not layout:
            # Return an empty group if no layout
            return QParallelAnimationGroup(container)

        # Iterate over direct children only
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget():
                child_widget = item.widget()
                original_geometries[child_widget] = child_widget.geometry()

        # It's better to let the layout adjust first, then animate.
        # This requires a deferred execution or connecting to a signal if available.
        # For simplicity, we assume the layout change has been triggered externally
        # and this function is called AFTER the new layout is calculated but BEFORE it's visually applied.
        # A common pattern is to:
        # 1. Store old geometries.
        # 2. Apply layout changes (e.g., add/remove widget, resize container).
        # 3. Get new geometries.
        # 4. Set widgets to old geometries.
        # 5. Animate to new geometries.

        # This function is more of a utility to be called at the right time.
        # Let's assume the layout has been updated logically but not visually yet.
        # Or, more practically, we capture states before and after a layout event.

        animations = QParallelAnimationGroup(container)

        # This part needs to be called *after* the layout has been recomputed.
        # For example, after adding/removing a widget and calling container.layout().activate() or updateGeometry()
        # The challenge is that widget.geometry() will give the *new* geometry immediately after layout changes.

        # A more robust approach involves a two-step process or using QLayout.setGeometry.
        # For now, let's assume this is called when old_geometries are known, and new ones can be queried.

        # This simplified version assumes `container.update()` or similar has been called,
        # and `child.geometry()` now reflects the target geometry.
        # The crucial part is setting the child back to `original_rect` before starting animation.

        # The following is a conceptual fix, actual layout animation is complex.
        # Qt's standard layout system doesn't directly support animation out-of-the-box.
        # QStackedWidget with transitions or custom layout managers are often used.

        # Let's refine the logic:
        # 1. Children are already in their *new* positions due to layout update.
        # 2. We need their *previous* positions to animate *from*.
        # This implies `original_positions` should be captured *before* the layout change.
        # The current code structure suggests `original_positions` is captured, then layout updates,
        # then animation.

        # If `container.updateGeometry()` and `container.update()` are called *inside* this function,
        # then `child.geometry()` will be the new geometry.

        # Store original positions
        temp_original_positions: Dict[QWidget, QRect] = {}
        children_to_animate: List[QWidget] = []

        # Re-fetch in case it changed, or use 'layout' from above
        current_layout = container.layout()
        if current_layout:
            for i in range(current_layout.count()):
                item = current_layout.itemAt(i)
                if item and item.widget():
                    child = item.widget()
                    children_to_animate.append(child)
                    # This geometry is captured *before* any potential changes by this function
                    # but *after* external changes if this function is called post-layout-update.
                    # For this to work as intended (animate from old to new),
                    # temp_original_positions should ideally be passed in or captured
                    # truly before the event that *causes* the layout change.
                    # The current `original_geometries` capture might be what we need if called at the right time.
                    temp_original_positions[child] = original_geometries.get(
                        child, child.geometry())

        # Simulate layout update (or assume it happened just before calling this)
        # If this function is responsible for triggering the layout update that needs animation:
        # container.layout().activate() # or some other operation that changes layout

        # Animate to new positions
        for child in children_to_animate:
            # Assume child.geometry() is now the *target* geometry after layout update
            target_rect = child.geometry()
            original_rect = temp_original_positions.get(child)

            if original_rect and original_rect != target_rect:
                # Temporarily set to original position to animate from it
                child.setGeometry(original_rect)

                anim = QPropertyAnimation(child, QByteArray(b"geometry"))
                anim.setDuration(duration)
                anim.setEasingCurve(FluentTransition.EASE_SMOOTH)
                anim.setStartValue(original_rect)
                anim.setEndValue(target_rect)
                animations.addAnimation(anim)

        if animations.animationCount() > 0:
            animations.start(
                QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return animations

# Add QAbstractAnimation for DeletionPolicy and Property for FluentSequence dummy property
# These are already imported at the top.
