"""
Fluent Design Style Text Input Components
Enhanced with improved animations and consistent styling patterns
"""

from PySide6.QtWidgets import QLineEdit, QTextEdit, QWidget
from PySide6.QtCore import Signal, QTimer, Qt, QEvent, QPropertyAnimation
from PySide6.QtGui import QFocusEvent, QPainter
from core.theme import theme_manager
from core.enhanced_animations import (FluentMicroInteraction, FluentTransition,
                                      FluentStateTransition, FluentRevealEffect)
from typing import Optional
import weakref


class FluentInputBase:
    """Base class for all Fluent Design text inputs with shared behavior"""

    _animation_pool = weakref.WeakValueDictionary()
    _style_cache = {}

    def __init__(self, widget):
        self._widget = widget
        self._state_transition = FluentStateTransition(widget)
        self._is_focused = False
        self._is_hovered = False
        self._animation_active = False

        self._animation_timer = QTimer()
        self._animation_timer.setSingleShot(True)
        self._animation_timer.setInterval(50)

        self._style_update_timer = QTimer()
        self._style_update_timer.setSingleShot(True)
        self._style_update_timer.setInterval(100)
        self._style_update_timer.timeout.connect(self._apply_style)
        theme_manager.theme_changed.connect(self._queue_style_update)

    def _queue_style_update(self, _theme_name):
        FluentInputBase._style_cache.clear()
        self._style_update_timer.start()

    def _get_cached_style(self, widget_class: str, **kwargs) -> str:
        cache_key = (widget_class, theme_manager.current_theme,
                     frozenset(kwargs.items()))
        if cache_key not in FluentInputBase._style_cache:
            current_theme = theme_manager
            style = f"""
                {widget_class} {{
                    background-color: {current_theme.get_color('surface').name()};
                    border: 1px solid {current_theme.get_color('border').name()};
                    border-radius: 6px;
                    padding: {kwargs.get('padding_x', 8)}px {kwargs.get('padding_y', 12)}px;
                    font-size: 14px;
                    color: {current_theme.get_color('text_primary').name()};
                    selection-background-color: {current_theme.get_color('primary').name()}40;
                }}
                {widget_class}:hover {{
                    border-color: {current_theme.get_color('primary').lighter(150).name()};
                    background-color: {current_theme.get_color('accent_light').name()};
                }}
                {widget_class}:focus {{
                    border-color: {current_theme.get_color('primary').name()};
                    border-width: 2px;
                    padding: {kwargs.get('padding_x', 8)-1}px {kwargs.get('padding_y', 12)-1}px;
                    background-color: {current_theme.get_color('surface').name()};
                }}
                {widget_class}:disabled {{
                    background-color: {current_theme.get_color('surface').name()};
                    color: {current_theme.get_color('text_disabled').name()};
                    border-color: {current_theme.get_color('border').name()};
                }}
            """
            FluentInputBase._style_cache[cache_key] = style
        return FluentInputBase._style_cache[cache_key]

    def _get_animation(self, target, property_name, duration, start_value, end_value, easing_curve=None):
        key = (id(target), property_name, duration)
        if key in FluentInputBase._animation_pool:
            animation = FluentInputBase._animation_pool[key]
            animation.setStartValue(start_value)
            animation.setEndValue(end_value)
            if easing_curve:
                animation.setEasingCurve(easing_curve)
            return animation
        animation = QPropertyAnimation(target, property_name.encode())
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        if easing_curve:
            animation.setEasingCurve(easing_curve)
        FluentInputBase._animation_pool[key] = animation
        return animation

    def throttled_animation(self, fn, *args, **kwargs):
        if not self._animation_active:
            self._animation_active = True
            fn(*args, **kwargs)

            def reset_animation_state():
                self._animation_active = False
            self._animation_timer.timeout.connect(reset_animation_state)
            self._animation_timer.start()

    def handle_focus_in(self, _event):
        self._is_focused = True
        self.throttled_animation(
            FluentMicroInteraction.hover_glow,
            self._widget,
            0.2
        )
        self._state_transition.transitionTo("focused")

    def handle_focus_out(self, _event):
        self._is_focused = False
        if self._is_hovered:
            self._state_transition.transitionTo("hovered")
        else:
            self._state_transition.transitionTo("normal")

    def handle_enter_event(self, _event):
        self._is_hovered = True
        if not self._is_focused:
            self.throttled_animation(
                FluentMicroInteraction.hover_glow,
                self._widget,
                0.1
            )
            self._state_transition.transitionTo("hovered")

    def handle_leave_event(self, _event):
        self._is_hovered = False
        if not self._is_focused:
            self._state_transition.transitionTo("normal")

    def _apply_style(self):
        # This method is called by the style update timer
        if hasattr(self._widget, "_apply_style"):
            self._widget._apply_style()


class FluentLineEdit(QLineEdit):
    """Fluent Design Style Single Line Text Input with enhanced animations"""

    def __init__(self, parent: Optional[QWidget] = None,
                 placeholder: str = ""):
        super().__init__(parent)
        self._fluent_base = FluentInputBase(self)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setMinimumHeight(32)
        self._setup_enhanced_animations()
        self._apply_style()
        self.installEventFilter(self)

    def _setup_enhanced_animations(self):
        self._fluent_base._state_transition.addState("normal", {
            "minimumHeight": 32,
        })
        self._fluent_base._state_transition.addState("hovered", {
            "minimumHeight": 34,
        }, duration=150, easing=FluentTransition.EASE_SMOOTH)
        self._fluent_base._state_transition.addState("focused", {
            "minimumHeight": 36,
        }, duration=200, easing=FluentTransition.EASE_SPRING)

    def _apply_style(self):
        style_sheet = self._fluent_base._get_cached_style(
            "FluentLineEdit",
            padding_x=8,
            padding_y=12,
            min_height=32
        )
        self.setStyleSheet(style_sheet)

    def focusInEvent(self, event: QFocusEvent):
        self._fluent_base.handle_focus_in(event)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        self._fluent_base.handle_focus_out(event)
        super().focusOutEvent(event)

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.Type.Enter:
                self._fluent_base.handle_enter_event(event)
            elif event.type() == QEvent.Type.Leave:
                self._fluent_base.handle_leave_event(event)
        return super().eventFilter(obj, event)


class FluentTextEdit(QTextEdit):
    """Fluent Design Style Multi-line Text Input with enhanced animations"""

    def __init__(self, parent: Optional[QWidget] = None,
                 placeholder: str = ""):
        super().__init__(parent)
        self._fluent_base = FluentInputBase(self)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setMinimumHeight(80)
        self._setup_enhanced_animations()
        self._apply_style()
        self.installEventFilter(self)

    def _setup_enhanced_animations(self):
        self._fluent_base._state_transition.addState("normal", {
            "minimumHeight": 80,
        })
        self._fluent_base._state_transition.addState("hovered", {
            "minimumHeight": 82,
        }, duration=150, easing=FluentTransition.EASE_SMOOTH)
        self._fluent_base._state_transition.addState("focused", {
            "minimumHeight": 84,
        }, duration=200, easing=FluentTransition.EASE_SPRING)

    def _apply_style(self):
        style_sheet = self._fluent_base._get_cached_style(
            "FluentTextEdit",
            padding_x=12,
            padding_y=12,
            min_height=80
        )
        self.setStyleSheet(style_sheet)

    def focusInEvent(self, event: QFocusEvent):
        self._fluent_base.handle_focus_in(event)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        self._fluent_base.handle_focus_out(event)
        super().focusOutEvent(event)

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.Type.Enter:
                self._fluent_base.handle_enter_event(event)
            elif event.type() == QEvent.Type.Leave:
                self._fluent_base.handle_leave_event(event)
        return super().eventFilter(obj, event)


class FluentPasswordEdit(FluentLineEdit):
    """Fluent Design Style Password Input with enhanced animations"""

    def __init__(self, parent: Optional[QWidget] = None,
                 placeholder: str = "Enter password"):
        super().__init__(parent, placeholder)
        self.setEchoMode(QLineEdit.EchoMode.Password)
        QTimer.singleShot(0, lambda: FluentRevealEffect.fade_in(self, 300))

    def _apply_style(self):
        super()._apply_style()
        current_theme = theme_manager
        additional_style = f"""
            FluentPasswordEdit {{
                font-family: 'Consolas', 'Courier New', monospace;
                letter-spacing: 2px;
            }}
            FluentPasswordEdit:focus {{
                border-color: {current_theme.get_color('primary').name()};
                box-shadow: 0 0 0 3px {current_theme.get_color('primary').name()}30;
            }}
        """
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + additional_style)


class FluentSearchBox(FluentLineEdit):
    """Fluent Design Style Search Box with enhanced animations"""

    search_triggered = Signal(str)
    _SEARCH_ICON_NORMAL = """
        <svg width="16" height="16" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
            <path d="M11.742 10.344L14.5 13.1L14 13.6L11.244 10.844C10.5 11.5 9.25 12 8 12C4.686 12 2 9.314 2 6S4.686 0 8 0S14 2.686 14 6C14 7.25 13.5 10.5 11.742 10.344Z" fill="#666" />
        </svg>
    """
    _SEARCH_ICON_FOCUS = """
        <svg width="16" height="16" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
            <path d="M11.742 10.344L14.5 13.1L14 13.6L11.244 10.844C10.5 11.5 9.25 12 8 12C4.686 12 2 9.314 2 6S4.686 0 8 0S14 2.686 14 6C14 7.25 13.5 10.5 11.742 10.344Z" fill="#fff" />
        </svg>
    """

    def __init__(self, parent: Optional[QWidget] = None,
                 placeholder: str = "Search..."):
        super().__init__(parent, placeholder)
        self.returnPressed.connect(self._on_search)
        self._apply_search_style()
        QTimer.singleShot(
            0, lambda: FluentRevealEffect.slide_in(self, 300, "right"))

    def _apply_search_style(self):
        super()._apply_style()
        additional_style = f"""
            FluentSearchBox {{
                background-repeat: no-repeat;
                background-position: 12px center;
                padding-left: 40px;
            }}
            FluentSearchBox:focus {{
                padding-left: 39px;
            }}
        """
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + additional_style)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        svg_icon = self._SEARCH_ICON_FOCUS if self.hasFocus() else self._SEARCH_ICON_NORMAL
        # Placeholder for SVG rendering

    def _on_search(self):
        text = self.text().strip()
        if text:
            self._fluent_base.throttled_animation(
                FluentMicroInteraction.pulse_animation,
                self,
                1.05
            )
            self.search_triggered.emit(text)

    def set_search_text(self, text: str):
        if text == self.text():
            return
        animation = self._fluent_base._get_animation(
            self, "opacity", 300, 1.0, 1.0,
            FluentTransition.EASE_SMOOTH
        )
        animation.setKeyValueAt(0.5, 0.7)

        def update_at_midpoint(value):
            if value <= 0.75 and not hasattr(animation, "_text_updated"):
                self.setText(text)
                setattr(animation, "_text_updated", True)
        animation.valueChanged.connect(update_at_midpoint)
        animation.finished.connect(lambda: delattr(
            animation, "_text_updated") if hasattr(animation, "_text_updated") else None)
        animation.start()


class FluentNumericEdit(FluentLineEdit):
    """Fluent Design Style Numeric Input with enhanced animations"""

    value_changed = Signal(float)

    def __init__(self, parent: Optional[QWidget] = None,
                 minimum: float = 0, maximum: float = 100,
                 decimals: int = 2, placeholder: str = "Enter number"):
        super().__init__(parent, placeholder)
        self._minimum = minimum
        self._maximum = maximum
        self._decimals = decimals
        self._current_value = minimum
        self._format_string = f"{{:.{decimals}f}}" if decimals > 0 else "{:.0f}"
        from PySide6.QtGui import QDoubleValidator
        validator = QDoubleValidator(minimum, maximum, decimals, self)
        self.setValidator(validator)
        self._text_change_timer = QTimer()
        self._text_change_timer.setSingleShot(True)
        self._text_change_timer.setInterval(100)
        self._text_change_timer.timeout.connect(self._process_text_change)
        self.textChanged.connect(self._queue_text_change)
        QTimer.singleShot(0, lambda: FluentRevealEffect.scale_in(self, 200))
        self.set_value(minimum)

    def _queue_text_change(self, text: str):
        self._pending_text = text
        self._text_change_timer.start()

    def _process_text_change(self):
        text = self._pending_text.strip()
        try:
            if text:
                value = float(text)
                value = max(self._minimum, min(self._maximum, value))
                if abs(value - self._current_value) > 1e-10:
                    self._current_value = value
                    self._fluent_base.throttled_animation(
                        FluentMicroInteraction.pulse_animation,
                        self,
                        1.02
                    )
                    self.value_changed.emit(value)
            else:
                self._current_value = self._minimum
        except ValueError:
            self._fluent_base.throttled_animation(
                FluentMicroInteraction.shake_animation,
                self,
                5
            )

    def set_value(self, value: float):
        value = max(self._minimum, min(self._maximum, value))
        if abs(value - self._current_value) < 1e-10:
            return
        self._current_value = value
        text = self._format_string.format(value)
        self.setText(text)
        from PySide6.QtGui import QColor
        original_bg = self.palette().color(self.backgroundRole())
        highlight_color = theme_manager.get_color('primary').lighter(180)

        def update_highlight(progress):
            if progress < 0.5:
                blend_factor = progress * 2
                color = QColor(
                    int(original_bg.red() * (1-blend_factor) +
                        highlight_color.red() * blend_factor),
                    int(original_bg.green() * (1-blend_factor) +
                        highlight_color.green() * blend_factor),
                    int(original_bg.blue() * (1-blend_factor) +
                        highlight_color.blue() * blend_factor)
                )
            else:
                blend_factor = (progress - 0.5) * 2
                color = QColor(
                    int(highlight_color.red() * (1-blend_factor) +
                        original_bg.red() * blend_factor),
                    int(highlight_color.green() * (1-blend_factor) +
                        original_bg.green() * blend_factor),
                    int(highlight_color.blue() * (1-blend_factor) +
                        original_bg.blue() * blend_factor)
                )
            self.setStyleSheet(
                f"{self.styleSheet()}\nFluentNumericEdit {{ background-color: {color.name()}; }}")
        animation = self._fluent_base._get_animation(
            self, "progress", 400, 0.0, 1.0,
            FluentTransition.EASE_SMOOTH
        )
        animation.valueChanged.connect(update_highlight)
        animation.finished.connect(lambda: self._apply_style())
        animation.start()

    def get_value(self) -> float:
        return self._current_value

    def set_range(self, minimum: float, maximum: float):
        if self._minimum == minimum and self._maximum == maximum:
            return
        self._minimum = minimum
        self._maximum = maximum
        validator = self.validator()
        if validator:
            from PySide6.QtGui import QDoubleValidator
            if isinstance(validator, QDoubleValidator):
                validator.setRange(minimum, maximum, self._decimals)
        self.set_value(self._current_value)
