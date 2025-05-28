"""
Fluent Design Style Label Components
提供各种样式的文本标签组件
"""

from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor
from core.theme import theme_manager
from core.animation import AnimationHelper
from typing import Optional, Union


class FluentLabel(QLabel):
    """Fluent Design Style基础标签

    Features:
    - 支持多种文本样式（标题、正文、说明文字等）
    - 主题自适应颜色
    - 动画效果支持
    - 可与其他组件组合使用
    """

    class LabelStyle:
        """标签样式枚举"""
        BODY = "body"
        CAPTION = "caption"
        SUBTITLE = "subtitle"
        TITLE = "title"
        TITLE_LARGE = "title_large"
        DISPLAY = "display"

    class LabelType:
        """标签类型枚举"""
        PRIMARY = "primary"
        SECONDARY = "secondary"
        DISABLED = "disabled"
        ACCENT = "accent"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"

    clicked = Signal()

    def __init__(self, text: str = "", parent: Optional[QWidget] = None,
                 style: Optional[str] = None, label_type: Optional[str] = None):
        super().__init__(text, parent)

        self._label_style = style or self.LabelStyle.BODY
        self._label_type = label_type or self.LabelType.PRIMARY
        self._is_clickable = False
        self._animation_helper = None

        self.setWordWrap(True)
        self._apply_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def set_style(self, style: str):
        """设置标签样式"""
        self._label_style = style
        self._apply_style()

    def set_type(self, label_type: str):
        """设置标签类型"""
        self._label_type = label_type
        self._apply_style()

    def set_clickable(self, clickable: bool):
        """设置是否可点击"""
        self._is_clickable = clickable
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            if not self._animation_helper:
                self._animation_helper = AnimationHelper(self)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def _apply_style(self):
        """应用标签样式"""
        theme = theme_manager

        # 设置字体
        font = QFont()
        if self._label_style == self.LabelStyle.BODY:
            font.setPointSize(14)
            font.setWeight(QFont.Weight.Normal)
        elif self._label_style == self.LabelStyle.CAPTION:
            font.setPointSize(12)
            font.setWeight(QFont.Weight.Normal)
        elif self._label_style == self.LabelStyle.SUBTITLE:
            font.setPointSize(16)
            font.setWeight(QFont.Weight.Medium)
        elif self._label_style == self.LabelStyle.TITLE:
            font.setPointSize(20)
            font.setWeight(QFont.Weight.Medium)
        elif self._label_style == self.LabelStyle.TITLE_LARGE:
            font.setPointSize(28)
            font.setWeight(QFont.Weight.Medium)
        elif self._label_style == self.LabelStyle.DISPLAY:
            font.setPointSize(36)
            font.setWeight(QFont.Weight.Bold)

        self.setFont(font)

        # 设置颜色
        color = theme.get_color('text_primary')
        if self._label_type == self.LabelType.SECONDARY:
            color = theme.get_color('text_secondary')
        elif self._label_type == self.LabelType.DISABLED:
            color = theme.get_color('text_disabled')
        elif self._label_type == self.LabelType.ACCENT:
            color = theme.get_color('primary')
        elif self._label_type == self.LabelType.SUCCESS:
            color = QColor("#107c10")
        elif self._label_type == self.LabelType.WARNING:
            color = QColor("#ff8c00")
        elif self._label_type == self.LabelType.ERROR:
            color = QColor("#d13438")

        style_sheet = f"""
            FluentLabel {{
                color: {color.name()};
                background: transparent;
                border: none;
            }}
        """

        if self._is_clickable:
            hover_color = color.lighter(120)
            style_sheet += f"""
                FluentLabel:hover {{
                    color: {hover_color.name()};
                }}
            """

        self.setStyleSheet(style_sheet)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if self._is_clickable:
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """悬停进入事件"""
        if self._is_clickable and self._animation_helper:
            self._animation_helper.add_hover_effect()
        super().enterEvent(event)

    def _on_theme_changed(self, theme_name: str):  # noqa: ARG002
        """主题变化处理"""
        self._apply_style()


class FluentIconLabel(QWidget):
    """带图标的标签组件"""

    clicked = Signal()

    def __init__(self, text: str = "", icon: Optional[Union[QIcon, QPixmap, str]] = None,
                 parent: Optional[QWidget] = None, icon_size: int = 16,
                 layout_direction: str = "horizontal"):
        super().__init__(parent)

        self._is_clickable = False
        self._layout_direction = layout_direction

        self._setup_ui(text, icon, icon_size)
        self._apply_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self, text: str, icon: Optional[Union[QIcon, QPixmap, str]], icon_size: int):
        """设置UI布局"""
        if self._layout_direction == "horizontal":
            layout = QHBoxLayout(self)
        else:
            layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 创建图标标签
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

        # 创建文字标签
        self.text_label = FluentLabel(text)
        layout.addWidget(self.text_label)

        if self._layout_direction == "horizontal":
            layout.addStretch()

    def set_text(self, text: str):
        """设置文字"""
        self.text_label.setText(text)

    def text(self) -> str:
        """获取文字"""
        return self.text_label.text()

    def set_clickable(self, clickable: bool):
        """设置是否可点击"""
        self._is_clickable = clickable
        self.text_label.set_clickable(clickable)
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def set_text_style(self, style: str):
        """设置文字样式"""
        self.text_label.set_style(style)

    def set_text_type(self, label_type: str):
        """设置文字类型"""
        self.text_label.set_type(label_type)

    def _apply_style(self):
        """应用样式"""
        self.setStyleSheet("""
            FluentIconLabel {
                background: transparent;
                border: none;
            }
        """)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if self._is_clickable:
            self.clicked.emit()
        super().mousePressEvent(event)

    def _on_theme_changed(self, theme_name: str):  # noqa: ARG002
        """主题变化处理"""
        self._apply_style()


class FluentStatusLabel(QWidget):
    """状态标签组件"""

    class StatusType:
        """状态类型"""
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"
        INFO = "info"
        PROCESSING = "processing"

    def __init__(self, text: str = "", status: Optional[str] = None,
                 parent: Optional[QWidget] = None, show_indicator: bool = True):
        super().__init__(parent)

        self._status = status or self.StatusType.INFO
        self._show_indicator = show_indicator

        self._setup_ui(text)
        self._apply_style()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self, text: str):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # 状态指示器
        if self._show_indicator:
            self.indicator = QLabel()
            self.indicator.setFixedSize(8, 8)
            layout.addWidget(self.indicator)
        else:
            self.indicator = None

        # 文字标签
        self.text_label = FluentLabel(text, style=FluentLabel.LabelStyle.BODY)
        layout.addWidget(self.text_label)

        layout.addStretch()

    def set_status(self, status: str):
        """设置状态"""
        self._status = status
        self._apply_style()

    def set_text(self, text: str):
        """设置文字"""
        self.text_label.setText(text)

    def text(self) -> str:
        """获取文字"""
        return self.text_label.text()

    def _apply_style(self):
        """应用样式"""
        theme = theme_manager

        # 设置状态颜色
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
        else:  # INFO
            status_color = theme.get_color('text_secondary')
            text_type = FluentLabel.LabelType.SECONDARY

        # 设置指示器样式
        if self.indicator:
            self.indicator.setStyleSheet(f"""
                QLabel {{
                    background-color: {status_color.name()};
                    border-radius: 4px;
                }}
            """)

        # 设置文字类型
        self.text_label.set_type(text_type)

        # 设置整体样式
        self.setStyleSheet(f"""
            FluentStatusLabel {{
                background-color: {status_color.name()}15;
                border: 1px solid {status_color.name()}30;
                border-radius: 4px;
            }}
        """)

    def _on_theme_changed(self, theme_name: str):  # noqa: ARG002
        """主题变化处理"""
        self._apply_style()


class FluentLinkLabel(FluentLabel):
    """链接标签组件"""

    def __init__(self, text: str = "", url: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent, style=FluentLabel.LabelStyle.BODY,
                         label_type=FluentLabel.LabelType.ACCENT)

        self._url = url
        self.set_clickable(True)
        self._setup_link_style()

        self.clicked.connect(self._on_link_clicked)

    def _setup_link_style(self):
        """设置链接样式"""
        theme = theme_manager
        primary_color = theme.get_color('primary')
        hover_color = primary_color.lighter(120)

        style_sheet = f"""
            FluentLinkLabel {{
                color: {primary_color.name()};
                text-decoration: underline;
            }}
            FluentLinkLabel:hover {{
                color: {hover_color.name()};
            }}
        """
        self.setStyleSheet(style_sheet)

    def set_url(self, url: str):
        """设置链接URL"""
        self._url = url

    def get_url(self) -> str:
        """获取链接URL"""
        return self._url

    def _on_link_clicked(self):
        """链接点击处理"""
        if self._url:
            import webbrowser
            webbrowser.open(self._url)

    def _on_theme_changed(self, theme_name: str):  # noqa: ARG002
        """主题变化处理"""
        super()._on_theme_changed(theme_name)
        self._setup_link_style()


class FluentLabelGroup(QWidget):
    """标签组组件"""

    def __init__(self, parent: Optional[QWidget] = None,
                 layout_direction: str = "horizontal", spacing: int = 12):
        super().__init__(parent)

        self._labels = []
        self._layout_direction = layout_direction

        self._setup_ui(spacing)

    def _setup_ui(self, spacing: int):
        """设置UI"""
        if self._layout_direction == "horizontal":
            self._layout = QHBoxLayout(self)
        else:
            self._layout = QVBoxLayout(self)

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(spacing)
        self._layout.addStretch()

    def add_label(self, label: Union[FluentLabel, FluentIconLabel, FluentStatusLabel, str]) -> QWidget:
        """添加标签"""
        if isinstance(label, str):
            label_widget = FluentLabel(label)
        else:
            label_widget = label

        self._labels.append(label_widget)
        self._layout.insertWidget(self._layout.count() - 1, label_widget)

        return label_widget

    def remove_label(self, label: Union[QWidget, int]):
        """移除标签"""
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

    def clear_labels(self):
        """清空所有标签"""
        for label in self._labels[:]:
            self.remove_label(label)

    def get_labels(self):
        """获取所有标签"""
        return self._labels.copy()

    def set_spacing(self, spacing: int):
        """设置间距"""
        self._layout.setSpacing(spacing)
