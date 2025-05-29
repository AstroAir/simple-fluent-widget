"""
增强的Fluent Design动画效果系统
实现平滑的过渡动画和交互反馈，包含更多动画效果和缓动函数
"""

from PySide6.QtCore import (QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
                            QSequentialAnimationGroup, QByteArray, QTimer, QRect, QPoint)
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect, QGraphicsColorizeEffect, QPushButton
from PySide6.QtGui import QColor
from typing import Optional, Callable, List


class FluentAnimation:
    """**增强的Fluent Design动画管理器**"""

    # **定义标准动画时长**
    DURATION_ULTRA_FAST = 100   # 超快速动画
    DURATION_FAST = 150         # 快速动画
    DURATION_MEDIUM = 250       # 中等动画
    DURATION_SLOW = 350         # 慢速动画
    DURATION_ULTRA_SLOW = 500   # 超慢速动画

    # **定义标准缓动曲线**
    EASE_IN_OUT = QEasingCurve.Type.InOutCubic
    EASE_OUT = QEasingCurve.Type.OutCubic
    EASE_IN = QEasingCurve.Type.InCubic
    EASE_OUT_BACK = QEasingCurve.Type.OutBack
    EASE_IN_OUT_BACK = QEasingCurve.Type.InOutBack
    EASE_OUT_ELASTIC = QEasingCurve.Type.OutElastic
    EASE_OUT_BOUNCE = QEasingCurve.Type.OutBounce

    # **Spring动画参数**
    SPRING_SMOOTH = QEasingCurve.Type.OutCubic
    SPRING_BOUNCY = QEasingCurve.Type.OutBack
    SPRING_WOBBLY = QEasingCurve.Type.OutElastic

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
    def scale_animation(widget: QWidget, start_scale: float = 0.8,
                        end_scale: float = 1.0,
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
    def hover_effect(widget: QWidget, hover_scale: float = 1.05) -> tuple:
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

    @staticmethod
    def spring_animation(widget: QWidget, property_name: str,
                         start_value, end_value,
                         spring_type: QEasingCurve.Type = SPRING_SMOOTH,
                         duration: int = DURATION_MEDIUM) -> QPropertyAnimation:
        """**Spring弹性动画**"""
        animation = QPropertyAnimation(
            widget, QByteArray(property_name.encode()))
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(spring_type)
        return animation

    @staticmethod
    def morph_animation(widget: QWidget, start_rect: QRect, end_rect: QRect,
                        duration: int = DURATION_MEDIUM) -> QPropertyAnimation:
        """**形状变换动画**"""
        animation = QPropertyAnimation(widget, QByteArray(b"geometry"))
        animation.setDuration(duration)
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        animation.setEasingCurve(FluentAnimation.EASE_OUT_BACK)
        return animation

    @staticmethod
    def color_transition(widget: QWidget, start_color: QColor, end_color: QColor,
                         duration: int = DURATION_MEDIUM) -> QPropertyAnimation:
        """**颜色过渡动画**"""
        effect = QGraphicsColorizeEffect()
        widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, QByteArray(b"color"))
        animation.setDuration(duration)
        animation.setStartValue(start_color)
        animation.setEndValue(end_color)
        animation.setEasingCurve(FluentAnimation.EASE_OUT)
        return animation

    @staticmethod
    def bounce_animation(widget: QWidget, bounce_height: int = 10,
                         duration: int = DURATION_FAST) -> QSequentialAnimationGroup:
        """**弹跳动画**"""
        original_pos = widget.pos()
        up_pos = QPoint(original_pos.x(), original_pos.y() - bounce_height)

        sequence = QSequentialAnimationGroup()

        # 上升
        up_anim = QPropertyAnimation(widget, QByteArray(b"pos"))
        up_anim.setDuration(duration // 2)
        up_anim.setStartValue(original_pos)
        up_anim.setEndValue(up_pos)
        up_anim.setEasingCurve(FluentAnimation.EASE_OUT)

        # 下降
        down_anim = QPropertyAnimation(widget, QByteArray(b"pos"))
        down_anim.setDuration(duration // 2)
        down_anim.setStartValue(up_pos)
        down_anim.setEndValue(original_pos)
        down_anim.setEasingCurve(FluentAnimation.EASE_IN)

        sequence.addAnimation(up_anim)
        sequence.addAnimation(down_anim)
        return sequence

    @staticmethod
    def ripple_effect(widget: QWidget, center_point: QPoint,
                      duration: int = DURATION_MEDIUM) -> QParallelAnimationGroup:
        """**涟漪效果动画**"""
        group = QParallelAnimationGroup()

        # 创建涟漪效果（简化版，实际可能需要自定义绘制）
        opacity_anim = FluentAnimation.fade_in(widget, duration)
        scale_anim = FluentAnimation.scale_animation(
            widget, 0.8, 1.2, duration)

        group.addAnimation(opacity_anim)
        group.addAnimation(scale_anim)
        return group

    @staticmethod
    def slide_transition(widget: QWidget, direction: str = "left",
                         distance: Optional[int] = None, duration: int = DURATION_MEDIUM,
                         easing: QEasingCurve.Type = EASE_OUT) -> QPropertyAnimation:
        """**滑动过渡动画（增强版）**"""
        if distance is None:
            distance = widget.width() if direction in [
                "left", "right"] else widget.height()

        start_pos = widget.pos()

        if direction == "left":
            end_pos = QPoint(start_pos.x() - distance, start_pos.y())
        elif direction == "right":
            end_pos = QPoint(start_pos.x() + distance, start_pos.y())
        elif direction == "up":
            end_pos = QPoint(start_pos.x(), start_pos.y() - distance)
        elif direction == "down":
            end_pos = QPoint(start_pos.x(), start_pos.y() + distance)
        else:
            end_pos = start_pos

        animation = QPropertyAnimation(widget, QByteArray(b"pos"))
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(easing)
        return animation

    @staticmethod
    def shake_animation(widget: QWidget, intensity: int = 5,
                        duration: int = DURATION_FAST) -> QSequentialAnimationGroup:
        """**摇摆动画**"""
        original_pos = widget.pos()
        sequence = QSequentialAnimationGroup()

        for i in range(4):
            direction = 1 if i % 2 == 0 else -1
            shake_pos = QPoint(original_pos.x() + direction *
                               intensity, original_pos.y())

            shake_anim = QPropertyAnimation(widget, QByteArray(b"pos"))
            shake_anim.setDuration(duration // 4)
            shake_anim.setStartValue(widget.pos())
            shake_anim.setEndValue(shake_pos)
            shake_anim.setEasingCurve(FluentAnimation.EASE_IN_OUT)

            sequence.addAnimation(shake_anim)

        # 回到原位
        reset_anim = QPropertyAnimation(widget, QByteArray(b"pos"))
        reset_anim.setDuration(duration // 4)
        reset_anim.setEndValue(original_pos)
        sequence.addAnimation(reset_anim)

        return sequence

    @staticmethod
    def pulse_animation(widget: QWidget, scale_factor: float = 1.1,
                        duration: int = DURATION_MEDIUM) -> QSequentialAnimationGroup:
        """**脉冲动画**"""
        sequence = QSequentialAnimationGroup()

        # 放大
        grow_anim = FluentAnimation.scale_animation(
            widget, 1.0, scale_factor, duration // 2)
        # 缩小
        shrink_anim = FluentAnimation.scale_animation(
            widget, scale_factor, 1.0, duration // 2)

        sequence.addAnimation(grow_anim)
        sequence.addAnimation(shrink_anim)
        return sequence

    @staticmethod
    def breathing_animation(widget: QWidget, min_opacity: float = 0.5,
                            duration: int = DURATION_SLOW) -> QSequentialAnimationGroup:
        """**呼吸动画（无限循环）**"""
        sequence = QSequentialAnimationGroup()

        # 淡出
        fade_out = FluentAnimation.fade_out(widget, duration // 2)
        fade_out.setEndValue(min_opacity)

        # 淡入
        fade_in = FluentAnimation.fade_in(widget, duration // 2)
        fade_in.setStartValue(min_opacity)

        sequence.addAnimation(fade_out)
        sequence.addAnimation(fade_in)
        sequence.setLoopCount(-1)  # 无限循环
        return sequence

    @staticmethod
    def stagger_animation(widgets: List[QWidget], animation_func: Callable,
                          stagger_delay: int = 50) -> QSequentialAnimationGroup:
        """**交错动画**"""
        sequence = QSequentialAnimationGroup()

        for i, widget in enumerate(widgets):
            if i > 0:
                # 添加延迟
                delay_timer = QTimer()
                delay_timer.setSingleShot(True)
                delay_timer.timeout.connect(lambda: None)

            # 应用动画
            anim = animation_func(widget)
            sequence.addAnimation(anim)

        return sequence


class AnimationHelper:
    """**动画辅助类**"""

    def __init__(self, widget: QWidget):
        self.widget = widget
        self._animations = []
        self._original_show_event = None

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

        # 重写事件处理方法
        original_enter_event = self.widget.enterEvent
        original_leave_event = self.widget.leaveEvent

        def new_enter_event(event):
            if original_enter_event:
                original_enter_event(event)
            on_enter()

        def new_leave_event(event):
            if original_leave_event:
                original_leave_event(event)
            on_leave()

        self.widget.enterEvent = new_enter_event
        self.widget.leaveEvent = new_leave_event

    def add_click_ripple(self):
        """**添加点击涟漪效果**"""
        def on_click():
            center = self.widget.rect().center()
            ripple = FluentAnimation.ripple_effect(self.widget, center)
            ripple.start()
            self._animations.append(ripple)

        # 只有按钮类控件才有clicked信号
        if isinstance(self.widget, QPushButton):
            self.widget.clicked.connect(on_click)

    def add_bounce_on_show(self):
        """**显示时添加弹跳效果**"""
        def on_show():
            bounce = FluentAnimation.bounce_animation(self.widget)
            bounce.start()
            self._animations.append(bounce)

        # 保存原始的showEvent方法
        self._original_show_event = self.widget.showEvent

        def new_show_event(event):
            # 调用原始的showEvent
            if self._original_show_event:
                self._original_show_event(event)
            # 执行动画
            on_show()

        self.widget.showEvent = new_show_event

    def add_breathing_effect(self):
        """**添加呼吸效果**"""
        breathing = FluentAnimation.breathing_animation(self.widget)
        breathing.start()
        self._animations.append(breathing)

    def cleanup(self):
        """**清理动画资源**"""
        for anim in self._animations:
            if anim.state() == QPropertyAnimation.State.Running:
                anim.stop()
        self._animations.clear()


class FluentTransition:
    """**页面过渡动画管理器**"""

    @staticmethod
    def fade_transition(old_widget: QWidget, new_widget: QWidget,
                        duration: int = FluentAnimation.DURATION_MEDIUM):
        """**淡入淡出过渡**"""
        fade_out = FluentAnimation.fade_out(old_widget, duration // 2)
        fade_in = FluentAnimation.fade_in(new_widget, duration // 2)

        fade_out.finished.connect(lambda: fade_in.start())
        fade_out.start()

    @staticmethod
    def slide_transition(old_widget: QWidget, new_widget: QWidget,
                         direction: str = "left",
                         duration: int = FluentAnimation.DURATION_MEDIUM):
        """**滑动过渡**"""
        # 旧组件滑出
        slide_out = FluentAnimation.slide_transition(
            old_widget, direction, None, duration)

        # 新组件滑入
        opposite_direction = {
            "left": "right", "right": "left",
            "up": "down", "down": "up"
        }.get(direction, "right")

        slide_in = FluentAnimation.slide_in(
            new_widget, opposite_direction, duration)

        slide_out.finished.connect(lambda: slide_in.start())
        slide_out.start()

    @staticmethod
    def morph_transition(old_widget: QWidget, new_widget: QWidget,
                         duration: int = FluentAnimation.DURATION_MEDIUM):
        """**形变过渡**"""
        old_rect = old_widget.geometry()
        new_rect = new_widget.geometry()

        morph = FluentAnimation.morph_animation(
            old_widget, old_rect, new_rect, duration)
        fade = FluentAnimation.fade_out(old_widget, duration)

        group = QParallelAnimationGroup()
        group.addAnimation(morph)
        group.addAnimation(fade)

        group.finished.connect(lambda: new_widget.show())
        group.start()
