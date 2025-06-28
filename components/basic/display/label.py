"""
Fluent Design Style Label Components - 优化版本
提供各种样式的文本标签组件，包含流畅动画效果和一致的主题支持
"""

from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer, QParallelAnimationGroup, QByteArray
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor
from core.theme import theme_manager
from core.animation import AnimationHelper, FluentAnimation
from typing import Optional, Union, Dict


class FluentLabel(QLabel):
    """Fluent Design Style base label - 优化版本

    Features:
    - 支持多种文本样式 (title, body, caption, etc.)
    - 主题自适应颜色，完全统一的主题支持
    - 流畅的动画效果支持
    - 性能优化的渲染
    - 可与其他组件组合使用
    - 智能文本缓存和重用
    """

    class LabelStyle:
        """Label style enum - 扩展样式定义"""
        BODY = "body"
        CAPTION = "caption"
        SUBTITLE = "subtitle"
        TITLE = "title"
        TITLE_LARGE = "title_large"
        DISPLAY = "display"
        # 新增样式
        HERO = "hero"           # 超大标题
        OVERLINE = "overline"   # 上标文字

    class LabelType:
        """Label type enum - 扩展类型定义"""
        PRIMARY = "primary"
        SECONDARY = "secondary"
        DISABLED = "disabled"
        ACCENT = "accent"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"
        # 新增类型
        INFO = "info"
        MUTED = "muted"

    # 性能优化：缓存字体和样式
    _font_cache: Dict[str, QFont] = {}

    clicked = Signal()
    hover_changed = Signal(bool)  # 新增悬停状态信号

    def __init__(self, text: str = "", parent: Optional[QWidget] = None,
                 style: Optional[str] = None, label_type: Optional[str] = None,
                 enable_animations: bool = True):
        super().__init__(text, parent)

        self._label_style = style or self.LabelStyle.BODY
        self._label_type = label_type or self.LabelType.PRIMARY
        self._is_clickable = False
        self._enable_animations = enable_animations
        self._animation_helper = None
        self._opacity_effect = None
        self._hover_animation = None
        self._click_animation = None
        self._is_hovering = False

        # 性能优化：减少不必要的重新计算
        self._last_theme_hash = None
        self._style_applied = False

        self.setWordWrap(True)
        self._setup_animations()
        self._apply_style()

        # Initialize opacity effect
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        # 连接主题变化信号
        theme_manager.theme_changed.connect(self._on_theme_changed)

    def set_style(self, style: str):
        """Set label style - 优化版本"""
        if self._label_style != style:
            self._label_style = style
            self._style_applied = False  # 标记需要重新应用样式
            self._apply_style()

    def set_type(self, label_type: str):
        """Set label type - 优化版本"""
        if self._label_type != label_type:
            self._label_type = label_type
            self._style_applied = False
            self._apply_style()

    def set_clickable(self, clickable: bool):
        """Set whether the label is clickable - 增强版本"""
        if self._is_clickable != clickable:
            self._is_clickable = clickable
            if clickable:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                if self._enable_animations and not self._animation_helper:
                    self._animation_helper = AnimationHelper(self)
                    self._setup_click_animations()
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
                if self._animation_helper:
                    self._animation_helper.cleanup()
                    self._animation_helper = None

    def set_animations_enabled(self, enabled: bool):
        """启用或禁用动画效果"""
        self._enable_animations = enabled
        if not enabled and self._animation_helper:
            self._animation_helper.cleanup()
            self._animation_helper = None
        elif enabled and self._is_clickable and not self._animation_helper:
            self._animation_helper = AnimationHelper(self)
            self._setup_click_animations()

    def _setup_animations(self):
        """设置动画效果"""
        if not self._enable_animations:
            return

        # 创建透明度效果用于动画
        self._opacity_effect = QGraphicsOpacityEffect()
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        # 悬停动画
        self._hover_animation = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def _setup_click_animations(self):
        """设置点击动画"""
        if not self._enable_animations or not self._opacity_effect:
            return

        # 点击动画组
        self._click_animation = QParallelAnimationGroup()

        # 透明度动画
        opacity_anim = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        opacity_anim.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
        opacity_anim.setStartValue(1.0)
        opacity_anim.setKeyValueAt(0.5, 0.7)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(FluentAnimation.EASE_IN_OUT)

        self._click_animation.addAnimation(opacity_anim)

    def fade_in(self, duration: Optional[int] = None):
        """淡入动画"""
        if not self._enable_animations or not self._opacity_effect or not self._hover_animation:
            return

        duration = duration or FluentAnimation.DURATION_MEDIUM

        if self._hover_animation.state() == QPropertyAnimation.State.Running:
            self._hover_animation.stop()

        self._hover_animation.setDuration(duration)
        self._hover_animation.setStartValue(0.0)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()

    def fade_out(self, duration: Optional[int] = None):
        """淡出动画"""
        if not self._enable_animations or not self._opacity_effect or not self._hover_animation:
            return

        duration = duration or FluentAnimation.DURATION_MEDIUM

        if self._hover_animation.state() == QPropertyAnimation.State.Running:
            self._hover_animation.stop()

        self._hover_animation.setDuration(duration)
        self._hover_animation.setStartValue(1.0)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()

    def pulse_animation(self):
        """脉冲动画效果"""
        if not self._enable_animations or not self._opacity_effect:
            return

        pulse_anim = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        pulse_anim.setDuration(FluentAnimation.DURATION_MEDIUM)
        pulse_anim.setStartValue(1.0)
        pulse_anim.setKeyValueAt(0.5, 0.6)
        pulse_anim.setEndValue(1.0)
        pulse_anim.setEasingCurve(FluentAnimation.EASE_IN_OUT)
        pulse_anim.start()

    def _get_cached_font(self) -> QFont:
        """获取缓存的字体 - 性能优化"""
        cache_key = f"{self._label_style}"

        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        font = QFont("Segoe UI")  # 使用Fluent Design推荐字体

        # 设置字体大小和权重
        if self._label_style == self.LabelStyle.BODY:
            font.setPointSize(14)
            font.setWeight(QFont.Weight.Normal)
        elif self._label_style == self.LabelStyle.CAPTION:
            font.setPointSize(12)
            font.setWeight(QFont.Weight.Normal)
        elif self._label_style == self.LabelStyle.OVERLINE:
            font.setPointSize(11)
            font.setWeight(QFont.Weight.Medium)
            font.setCapitalization(QFont.Capitalization.AllUppercase)
        elif self._label_style == self.LabelStyle.SUBTITLE:
            font.setPointSize(16)
            font.setWeight(QFont.Weight.Medium)
        elif self._label_style == self.LabelStyle.TITLE:
            font.setPointSize(20)
            font.setWeight(QFont.Weight.Bold)
        elif self._label_style == self.LabelStyle.TITLE_LARGE:
            font.setPointSize(28)
            font.setWeight(QFont.Weight.Bold)
        elif self._label_style == self.LabelStyle.DISPLAY:
            font.setPointSize(36)
            font.setWeight(QFont.Weight.Bold)
        elif self._label_style == self.LabelStyle.HERO:
            font.setPointSize(48)
            font.setWeight(QFont.Weight.Bold)

        # 缓存字体
        self._font_cache[cache_key] = font
        return font

    def _get_theme_color(self) -> QColor:
        """获取主题颜色 - 完全统一的主题支持"""
        theme = theme_manager

        if self._label_type == self.LabelType.PRIMARY:
            return theme.get_color('text_primary')
        elif self._label_type == self.LabelType.SECONDARY:
            return theme.get_color('text_secondary')
        elif self._label_type == self.LabelType.DISABLED:
            return theme.get_color('text_disabled')
        elif self._label_type == self.LabelType.ACCENT:
            return theme.get_color('primary')
        elif self._label_type == self.LabelType.SUCCESS:
            # 使用主题感知的成功色
            base_color = QColor("#107c10")
            if theme._current_mode.value == "dark":
                return base_color.lighter(120)
            return base_color
        elif self._label_type == self.LabelType.WARNING:
            base_color = QColor("#ff8c00")
            if theme._current_mode.value == "dark":
                return base_color.lighter(110)
            return base_color
        elif self._label_type == self.LabelType.ERROR:
            base_color = QColor("#d13438")
            if theme._current_mode.value == "dark":
                return base_color.lighter(115)
            return base_color
        elif self._label_type == self.LabelType.INFO:
            return theme.get_color('primary')
        elif self._label_type == self.LabelType.MUTED:
            return theme.get_color('text_secondary').darker(150)

        return theme.get_color('text_primary')

    def _apply_style(self):
        """Apply label style - 完全重写的优化版本"""
        # 性能优化：检查是否需要重新应用样式
        current_theme_hash = hash((
            theme_manager._current_mode.value,
            self._label_style,
            self._label_type,
            str(theme_manager.get_color('text_primary').name())
        ))

        if self._style_applied and self._last_theme_hash == current_theme_hash:
            return  # 避免不必要的重新计算

        self._last_theme_hash = current_theme_hash

        # 设置字体
        font = self._get_cached_font()
        self.setFont(font)

        # 获取颜色
        color = self._get_theme_color()

        # 生成样式表
        style_sheet = self._generate_style_sheet(color)
        self.setStyleSheet(style_sheet)

        self._style_applied = True

    def _generate_style_sheet(self, color: QColor) -> str:
        """生成样式表 - 增强版本"""
        base_style = f"""
            FluentLabel {{
                color: {color.name()};
                background: transparent;
                border: none;
                padding: 2px 0px;
            }}
        """

        if self._is_clickable:
            hover_color = color.lighter(120)
            active_color = color.darker(110)

            base_style += f"""
                FluentLabel:hover {{
                    color: {hover_color.name()};
                }}
                FluentLabel:pressed {{
                    color: {active_color.name()};
                }}
            """

        return base_style

    def mousePressEvent(self, event):
        """Mouse press event - 增强版本"""
        if self._is_clickable:
            # 播放点击动画
            if self._enable_animations and self._click_animation:
                self._click_animation.start()
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Hover enter event - 增强版本"""
        if not self._is_hovering:
            self._is_hovering = True
            self.hover_changed.emit(True)

            # 播放悬停进入动画
            if self._enable_animations and self._hover_animation:
                # Ensure opacity effect is initialized before use
                # Opacity effect is always initialized in __init__
                if self._opacity_effect:
                    self._hover_animation.setDuration(
                        FluentAnimation.DURATION_FAST)
                    if self._opacity_effect:
                        self._hover_animation.setStartValue(
                            self._opacity_effect.opacity())
                    self._hover_animation.setEndValue(0.8)
                    self._hover_animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave event - 增强版本"""
        if self._is_hovering:
            self._is_hovering = False
            self.hover_changed.emit(False)

            # 播放悬停离开动画
            if self._enable_animations and self._hover_animation:
                self._hover_animation.setDuration(
                    FluentAnimation.DURATION_FAST)
                # Check opacity effect exists before accessing its properties
                if self._opacity_effect:
                    self._hover_animation.setStartValue(
                        self._opacity_effect.opacity())
                self._hover_animation.setEndValue(1.0)
                self._hover_animation.start()

        super().leaveEvent(event)

    def _on_theme_changed(self, _):
        """Theme change handler - 优化版本"""
        self._style_applied = False  # 强制重新应用样式
        self._apply_style()


class FluentIconLabel(QWidget):
    """Label component with an icon - 优化版本"""

    clicked = Signal()
    hover_changed = Signal(bool)

    def __init__(self, text: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
                 parent: Optional[QWidget] = None, icon_size: int = 16,
                 layout_direction: str = "horizontal", enable_animations: bool = True):
        super().__init__(parent)

        self._is_clickable = False
        self._layout_direction = layout_direction
        self._enable_animations = enable_animations
        self._opacity_effect = None
        self._hover_animation = None

        self._setup_ui(text, icon, icon_size)
        self._setup_animations()
        self._apply_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self, text: str, icon: Optional[Union[QIcon, QPixmap, str]], icon_size: int):
        """Set up UI layout - 优化版本"""
        if self._layout_direction == "horizontal":
            layout = QHBoxLayout(self)
        else:
            layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Create icon label
        if icon:
            self.icon_label = QLabel()
            self.icon_label.setFixedSize(icon_size, icon_size)
            self.icon_label.setScaledContents(True)

            if isinstance(icon, str):
                pixmap = QPixmap(icon)
                self.icon_label.setPixmap(pixmap)
            elif isinstance(icon, QPixmap):
                self.icon_label.setPixmap(icon)
            elif isinstance(icon, QIcon):
                pixmap = icon.pixmap(icon_size, icon_size)
                self.icon_label.setPixmap(pixmap)

            layout.addWidget(self.icon_label)
        else:
            self.icon_label = None

        # Create text label with animations enabled
        self.text_label = FluentLabel(
            text, enable_animations=self._enable_animations)
        layout.addWidget(self.text_label)

        if self._layout_direction == "horizontal":
            layout.addStretch()

    def _setup_animations(self):
        """设置动画效果"""
        if not self._enable_animations:
            return

        # 为整个组件创建透明度效果
        self._opacity_effect = QGraphicsOpacityEffect()
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        # 悬停动画
        self._hover_animation = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def set_text(self, text: str):
        """Set text"""
        self.text_label.setText(text)

    def text(self) -> str:
        """Get text"""
        return self.text_label.text()

    def set_clickable(self, clickable: bool):
        """Set whether the label is clickable - 增强版本"""
        self._is_clickable = clickable
        self.text_label.set_clickable(clickable)
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def set_text_style(self, style: str):
        """Set text style"""
        self.text_label.set_style(style)

    def set_text_type(self, label_type: str):
        """Set text type"""
        self.text_label.set_type(label_type)

    def set_animations_enabled(self, enabled: bool):
        """启用或禁用动画效果"""
        self._enable_animations = enabled
        self.text_label.set_animations_enabled(enabled)

    def _apply_style(self):
        """Apply style - 优化版本"""
        theme = theme_manager
        bg_color = theme.get_color('surface')

        style_sheet = f"""
            FluentIconLabel {{
                background: transparent;
                border: none;
                border-radius: 4px;
            }}
        """

        if self._is_clickable:
            hover_bg = bg_color.lighter(110)
            style_sheet += f"""
                FluentIconLabel:hover {{
                    background-color: {hover_bg.name()}30;
                }}
            """

        self.setStyleSheet(style_sheet)

    def mousePressEvent(self, event):
        """Mouse press event"""
        if self._is_clickable:
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Hover enter event"""
        self.hover_changed.emit(True)
        if self._enable_animations and self._hover_animation and self._is_clickable:
            self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
            self._hover_animation.setStartValue(1.0)
            self._hover_animation.setEndValue(0.9)
            self._hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave event"""
        self.hover_changed.emit(False)
        if self._enable_animations and self._hover_animation and self._is_clickable:
            self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
            self._hover_animation.setStartValue(0.9)
            self._hover_animation.setEndValue(1.0)
            self._hover_animation.start()
        super().leaveEvent(event)

    def _on_theme_changed(self, _):
        """Theme change handler"""
        self._apply_style()


class FluentStatusLabel(QWidget):
    """Status label component - 优化版本"""

    class StatusType:
        """Status type"""
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"
        INFO = "info"
        PROCESSING = "processing"

    def __init__(self, text: str = "", status: Optional[str] = None,
                 parent: Optional[QWidget] = None, show_indicator: bool = True,
                 enable_animations: bool = True):
        super().__init__(parent)

        self._status = status or self.StatusType.INFO
        self._show_indicator = show_indicator
        self._enable_animations = enable_animations
        self._opacity_effect = None
        self._pulse_animation = None

        self._setup_ui(text)
        self._setup_animations()
        self._apply_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self, text: str):
        """Set up UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # Status indicator
        if self._show_indicator:
            self.indicator = QLabel()
            self.indicator.setFixedSize(8, 8)
            layout.addWidget(self.indicator)
        else:
            self.indicator = None

        # Text label
        self.text_label = FluentLabel(text, style=FluentLabel.LabelStyle.BODY,
                                      enable_animations=self._enable_animations)
        layout.addWidget(self.text_label)

        layout.addStretch()

    def _setup_animations(self):
        """设置动画效果"""
        if not self._enable_animations:
            return

        # 为指示器创建脉冲动画（仅在PROCESSING状态时使用）
        if self.indicator:
            self._opacity_effect = QGraphicsOpacityEffect()
            self._opacity_effect.setOpacity(1.0)
            self.indicator.setGraphicsEffect(self._opacity_effect)

            self._pulse_animation = QPropertyAnimation(
                self._opacity_effect, QByteArray(b"opacity"))
            self._pulse_animation.setDuration(1000)
            self._pulse_animation.setStartValue(0.3)
            self._pulse_animation.setEndValue(1.0)
            self._pulse_animation.setEasingCurve(FluentAnimation.EASE_IN_OUT)
            self._pulse_animation.setLoopCount(-1)  # 无限循环

    def set_status(self, status: str):
        """Set status"""
        old_status = self._status
        self._status = status
        self._apply_style()

        # 状态变化时的动画效果
        if self._enable_animations and old_status != status:
            self._animate_status_change()

    def _animate_status_change(self):
        """状态变化动画"""
        if not self._enable_animations:
            return

        # 简单的脉冲效果表示状态变化
        if self.text_label:
            self.text_label.pulse_animation()

    def set_text(self, text: str):
        """Set text"""
        self.text_label.setText(text)

    def text(self) -> str:
        """获取文字"""
        return self.text_label.text()

    def start_processing_animation(self):
        """开始处理动画"""
        if self._enable_animations and self._pulse_animation and self._status == self.StatusType.PROCESSING:
            self._pulse_animation.start()

    def stop_processing_animation(self):
        """停止处理动画"""
        if self._pulse_animation and self._pulse_animation.state() == QPropertyAnimation.State.Running:
            self._pulse_animation.stop()

    def _apply_style(self):
        """Apply style - 优化版本"""
        theme = theme_manager

        # Set status color
        if self._status == self.StatusType.SUCCESS:
            status_color = QColor("#107c10")
            text_type = FluentLabel.LabelType.SUCCESS
        elif self._status == self.StatusType.WARNING:
            status_color = QColor("#ff8c00")
            text_type = FluentLabel.LabelType.WARNING
        elif self._status == self.StatusType.ERROR:
            status_color = QColor("#d13438")
            text_type = FluentLabel.LabelType.ERROR
        elif self._status == self.StatusType.PROCESSING:
            status_color = theme.get_color('primary')
            text_type = FluentLabel.LabelType.ACCENT
            # 开始脉冲动画
            if self._enable_animations:
                self.start_processing_animation()
        else:  # INFO
            status_color = theme.get_color('text_secondary')
            text_type = FluentLabel.LabelType.SECONDARY

        # 主题感知的颜色调整
        if theme._current_mode.value == "dark":
            status_color = status_color.lighter(120)

        # Set indicator style
        if self.indicator:
            self.indicator.setStyleSheet(f"""
                QLabel {{
                    background-color: {status_color.name()};
                    border-radius: 4px;
                }}
            """)

        # Set text type
        self.text_label.set_type(text_type)

        # Set overall style with improved visual hierarchy
        bg_alpha = "15" if theme._current_mode.value == "light" else "25"
        border_alpha = "30" if theme._current_mode.value == "light" else "40"

        self.setStyleSheet(f"""
            FluentStatusLabel {{
                background-color: {status_color.name()}{bg_alpha};
                border: 1px solid {status_color.name()}{border_alpha};
                border-radius: 6px;
            }}
        """)

    def _on_theme_changed(self, _):
        """Theme change handler"""
        self._apply_style()


class FluentLinkLabel(FluentLabel):
    """Link label component - 优化版本"""

    def __init__(self, text: str = "", url: str = "", parent: Optional[QWidget] = None,
                 enable_animations: bool = True):
        super().__init__(text, parent, style=FluentLabel.LabelStyle.BODY,
                         label_type=FluentLabel.LabelType.ACCENT,
                         enable_animations=enable_animations)

        self._url = url
        self.set_clickable(True)
        self._setup_link_style()

        self.clicked.connect(self._on_link_clicked)

    def _setup_link_style(self):
        """Set link style - 优化版本"""
        theme = theme_manager
        primary_color = theme.get_color('primary')
        hover_color = primary_color.lighter(120)
        active_color = primary_color.darker(110)

        style_sheet = f"""
            FluentLinkLabel {{
                color: {primary_color.name()};
                text-decoration: underline;
                padding: 2px 4px;
                border-radius: 3px;
            }}
            FluentLinkLabel:hover {{
                color: {hover_color.name()};
                background-color: {primary_color.name()}10;
            }}
            FluentLinkLabel:pressed {{
                color: {active_color.name()};
                background-color: {primary_color.name()}20;
            }}
        """
        self.setStyleSheet(style_sheet)

    def set_url(self, url: str):
        """Set link URL"""
        self._url = url

    def get_url(self) -> str:
        """Get link URL"""
        return self._url

    def _on_link_clicked(self):
        """Link click handler"""
        if self._url:
            import webbrowser
            webbrowser.open(self._url)

    def _on_theme_changed(self, _):
        """Theme change handler"""
        super()._on_theme_changed(_)
        self._setup_link_style()


class FluentLabelGroup(QWidget):
    """Label group component - 优化版本"""

    def __init__(self, parent: Optional[QWidget] = None,
                 layout_direction: str = "horizontal", spacing: int = 12,
                 enable_animations: bool = True):
        super().__init__(parent)

        self._labels = []
        self._layout_direction = layout_direction
        self._enable_animations = enable_animations

        self._setup_ui(spacing)

    def _setup_ui(self, spacing: int):
        """Set up UI"""
        if self._layout_direction == "horizontal":
            self._layout = QHBoxLayout(self)
        else:
            self._layout = QVBoxLayout(self)

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(spacing)
        self._layout.addStretch()

    def add_label(self, label: Union[FluentLabel, FluentIconLabel, FluentStatusLabel, str],
                  animate: bool = True) -> QWidget:
        """Add label with optional animation"""
        if isinstance(label, str):
            label_widget = FluentLabel(
                label, enable_animations=self._enable_animations)
        else:
            label_widget = label

        self._labels.append(label_widget)
        self._layout.insertWidget(self._layout.count() - 1, label_widget)

        # 添加时的淡入动画
        if animate and self._enable_animations:
            # 延迟一帧以确保组件已经布局完成
            QTimer.singleShot(
                10, lambda: self._start_fade_animation(label_widget, 0, 1))

        return label_widget

    def remove_label(self, label: Union[QWidget, int], animate: bool = True):
        """Remove label with optional animation"""
        def do_remove():
            if isinstance(label, int):
                if 0 <= label < len(self._labels):
                    label_widget = self._labels.pop(label)
                    self._layout.removeWidget(label_widget)
                    label_widget.setParent(None)
            else:
                if label in self._labels:
                    self._labels.remove(label)
                    self._layout.removeWidget(label)
                    label.setParent(None)

        if animate and self._enable_animations:
            # 淡出后删除
            target_widget = self._labels[label] if isinstance(
                label, int) else label
            # 使用容器自身的淡出动画
            self._start_fade_animation(target_widget, 1, 0)
            # 动画完成后删除
            QTimer.singleShot(FluentAnimation.DURATION_MEDIUM, do_remove)
        else:
            do_remove()

    def clear_labels(self, animate: bool = True):
        """Clear all labels with optional animation"""
        if animate and self._enable_animations:
            # 交错淡出动画
            for i, label in enumerate(self._labels[:]):
                if hasattr(label, 'fade_out'):
                    QTimer.singleShot(i * 50, label.fade_out)

            # 所有动画完成后清理
            total_delay = len(self._labels) * 50 + \
                FluentAnimation.DURATION_MEDIUM
            QTimer.singleShot(total_delay, lambda: self._clear_immediately())
        else:
            self._clear_immediately()

    def _start_fade_animation(self, widget, start_value, end_value):
        """启动淡入淡出动画"""
        if not self._enable_animations:
            return

        if hasattr(widget, '_opacity_effect') and widget._opacity_effect:
            animation = QPropertyAnimation(
                widget._opacity_effect, QByteArray(b"opacity"))
            animation.setDuration(FluentAnimation.DURATION_MEDIUM)
            animation.setStartValue(start_value)
            animation.setEndValue(end_value)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)

            if end_value == 0:
                animation.finished.connect(lambda: widget.setVisible(False))

            animation.start()

    def _clear_immediately(self):
        """立即清理所有标签"""
        for label in self._labels[:]:
            self._layout.removeWidget(label)
            label.setParent(None)
        self._labels.clear()

    def get_labels(self):
        """Get all labels"""
        return self._labels.copy()

    def set_spacing(self, spacing: int):
        """Set spacing"""
        self._layout.setSpacing(spacing)

    def set_animations_enabled(self, enabled: bool):
        """启用或禁用所有标签的动画效果"""
        self._enable_animations = enabled
        for label in self._labels:
            if hasattr(label, 'set_animations_enabled'):
                label.set_animations_enabled(enabled)
