"""
Fluent Design动画效果系统
实现平滑的过渡动画和交互反馈
"""

from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QByteArray
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect
from typing import Optional, Callable


class FluentAnimation:
    """**Fluent Design动画管理器**"""

    # **定义标准动画时长**
    DURATION_FAST = 150      # 快速动画
    DURATION_MEDIUM = 250    # 中等动画
    DURATION_SLOW = 350      # 慢速动画

    # **定义标准缓动曲线**
    EASE_IN_OUT = QEasingCurve.Type.InOutCubic
    EASE_OUT = QEasingCurve.Type.OutCubic
    EASE_IN = QEasingCurve.Type.InCubic

    @staticmethod
    def fade_in(widget: QWidget, duration: int = DURATION_MEDIUM,
                callback: Optional[Callable] = None) -> QPropertyAnimation:
        """**淡入动画**"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(FluentAnimation.EASE_OUT)

        if callback:
            animation.finished.connect(callback)

        return animation

    @staticmethod
    def fade_out(widget: QWidget, duration: int = DURATION_MEDIUM,
                 callback: Optional[Callable] = None) -> QPropertyAnimation:
        """**淡出动画**"""
        if not widget.graphicsEffect():
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)

        effect = widget.graphicsEffect()
        if effect is None:
            raise RuntimeError("Failed to get graphics effect")

        animation = QPropertyAnimation(effect, QByteArray(b"opacity"))
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(FluentAnimation.EASE_IN)

        if callback:
            animation.finished.connect(callback)

        return animation

    @staticmethod
    def slide_in(widget: QWidget, direction: str = "left",
                 duration: int = DURATION_MEDIUM) -> QPropertyAnimation:
        """**滑入动画**

        Args:
            direction: 滑动方向 ('left', 'right', 'up', 'down')
        """
        start_pos = widget.pos()

        if direction == "left":
            widget.move(start_pos.x() - widget.width(), start_pos.y())
        elif direction == "right":
            widget.move(start_pos.x() + widget.width(), start_pos.y())
        elif direction == "up":
            widget.move(start_pos.x(), start_pos.y() - widget.height())
        elif direction == "down":
            widget.move(start_pos.x(), start_pos.y() + widget.height())

        animation = QPropertyAnimation(widget, QByteArray(b"pos"))
        animation.setDuration(duration)
        animation.setEndValue(start_pos)
        animation.setEasingCurve(FluentAnimation.EASE_OUT)

        return animation

    @staticmethod
    def scale_animation(widget: QWidget, _start_scale: float = 0.8,
                        _end_scale: float = 1.0,
                        duration: int = DURATION_FAST) -> QParallelAnimationGroup:
        """**缩放动画**"""
        # 这里需要自定义缩放效果，因为Qt没有直接的缩放属性动画
        # 可以通过QGraphicsEffect或几何变换实现
        group = QParallelAnimationGroup()

        # 透明度动画配合缩放效果
        opacity_anim = FluentAnimation.fade_in(widget, duration)
        group.addAnimation(opacity_anim)

        return group

    @staticmethod
    def hover_effect(widget: QWidget, _hover_scale: float = 1.05) -> tuple:
        """**悬停效果动画**

        Returns:
            (enter_animation, leave_animation)
        """
        # 悬停进入动画
        enter_anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
        enter_anim.setDuration(FluentAnimation.DURATION_FAST)
        enter_anim.setEasingCurve(FluentAnimation.EASE_OUT)

        # 悬停离开动画
        leave_anim = QPropertyAnimation(widget, QByteArray(b"geometry"))
        leave_anim.setDuration(FluentAnimation.DURATION_FAST)
        leave_anim.setEasingCurve(FluentAnimation.EASE_IN)

        return enter_anim, leave_anim


class AnimationHelper:
    """**动画辅助类**"""

    def __init__(self, widget: QWidget):
        self.widget = widget
        self._animations = []

    def add_hover_effect(self):
        """**添加悬停效果**"""
        def on_enter():
            enter_anim, _ = FluentAnimation.hover_effect(self.widget)
            current_rect = self.widget.geometry()
            scaled_rect = current_rect.adjusted(-2, -2, 2, 2)
            enter_anim.setStartValue(current_rect)
            enter_anim.setEndValue(scaled_rect)
            enter_anim.start()
            self._animations.append(enter_anim)

        def on_leave():
            _, leave_anim = FluentAnimation.hover_effect(self.widget)
            current_rect = self.widget.geometry()
            normal_rect = current_rect.adjusted(2, 2, -2, -2)
            leave_anim.setStartValue(current_rect)
            leave_anim.setEndValue(normal_rect)
            leave_anim.start()
            self._animations.append(leave_anim)

        self.widget.enterEvent = lambda _event: on_enter()
        self.widget.leaveEvent = lambda _event: on_leave()

    def cleanup(self):
        """**清理动画资源**"""
        for anim in self._animations:
            if anim.state() == QPropertyAnimation.State.Running:
                anim.stop()
        self._animations.clear()
