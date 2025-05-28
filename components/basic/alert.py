"""
Fluent Design Alert and Notification Components

Implements alerts, notifications, and message bars with various styles.
Based on Windows 11 Fluent Design principles.
"""

from typing import Optional  # Tuple removed as it's not used
from enum import Enum
from PySide6.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
                               QPushButton, QFrame, QGraphicsOpacityEffect, QApplication)
from PySide6.QtCore import (Qt, QPropertyAnimation, QTimer, Signal,
                            QEasingCurve, QPoint, QByteArray)
from PySide6.QtGui import QColor  # QFont removed as it's not used

# 修复导入问题
from core.theme import theme_manager, ThemeMode


class AlertType(Enum):
    """警告类型枚举"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class FluentAlert(QFrame):
    """
    现代化的警告组件
    """

    # 信号
    closed = Signal()
    action_clicked = Signal()

    def __init__(self,
                 title: str = "",
                 message: str = "",
                 alert_type: AlertType = AlertType.INFO,
                 closable: bool = True,
                 action_text: str = "",
                 timeout: int = 0,  # 0表示不自动关闭
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._message = message
        self._alert_type = alert_type
        self._closable = closable
        self._action_text = action_text
        self._timeout = timeout

        self._setup_ui()
        self._setup_animation()
        self._connect_theme()

        if timeout > 0:
            QTimer.singleShot(timeout, self.close_with_animation)

    def _setup_ui(self):
        """设置UI"""
        self.setFrameStyle(QFrame.Shape.NoFrame)

        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(12)

        # 图标
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(24, 24)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self._icon_label)

        # 内容布局
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        # 标题
        if self._title:
            self._title_label = QLabel(self._title)
            self._title_label.setWordWrap(True)
            content_layout.addWidget(self._title_label)

        # 消息
        if self._message:
            self._message_label = QLabel(self._message)
            self._message_label.setWordWrap(True)
            content_layout.addWidget(self._message_label)

        main_layout.addLayout(content_layout, 1)

        # 操作按钮
        if self._action_text:
            self._action_button = QPushButton(self._action_text)
            self._action_button.clicked.connect(self.action_clicked.emit)
            main_layout.addWidget(self._action_button)

        # 关闭按钮
        if self._closable:
            self._close_button = QPushButton("×")
            self._close_button.setFixedSize(24, 24)
            self._close_button.clicked.connect(self.close_with_animation)
            main_layout.addWidget(self._close_button)

        self._update_style()

    def _setup_animation(self):
        """设置动画"""
        self._opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self._opacity_effect)

        # 修复 QByteArray 参数问题
        self._fade_animation = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        self._fade_animation.setDuration(300)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 进入动画
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.finished.connect(self._on_fade_finished)
        self._fade_animation.start()

    def _connect_theme(self):
        """连接主题"""
        theme_manager.theme_changed.connect(self._update_style)

    def _get_colors(self) -> tuple[QColor, QColor, QColor]:
        """根据类型获取颜色"""
        theme = theme_manager

        if self._alert_type == AlertType.INFO:
            return (QColor(0, 120, 215), QColor(240, 248, 255), QColor(0, 90, 158))
        elif self._alert_type == AlertType.SUCCESS:
            return (QColor(16, 124, 16), QColor(240, 248, 240), QColor(12, 100, 12))
        elif self._alert_type == AlertType.WARNING:
            return (QColor(255, 185, 0), QColor(255, 252, 240), QColor(200, 145, 0))
        elif self._alert_type == AlertType.ERROR:
            return (QColor(196, 43, 28), QColor(255, 245, 245), QColor(160, 30, 20))
        else:
            return (QColor(theme.get_color('accent')), QColor(theme.get_color('background')), QColor(theme.get_color('text_primary')))

    def _update_style(self):
        """更新样式"""
        accent_color, bg_color, text_color = self._get_colors()
        theme = theme_manager

        # 调整背景色透明度
        if theme._current_mode == ThemeMode.DARK:  # 使用 _current_mode
            bg_color = bg_color.darker(200)
        bg_color.setAlpha(230)

        # 主容器样式
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, {bg_color.alpha()});
                border: 1px solid rgba({accent_color.red()}, {accent_color.green()}, {accent_color.blue()}, 150);
                border-radius: 8px;
            }}
        """)

        # 标题样式
        if hasattr(self, '_title_label'):
            self._title_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color.name()};
                    font-weight: 600;
                    font-size: 14px;
                    background: transparent;
                }}
            """)

        # 消息样式
        if hasattr(self, '_message_label'):
            self._message_label.setStyleSheet(f"""
                QLabel {{
                    color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 180);
                    font-size: 13px;
                    background: transparent;
                }}
            """)

        # 操作按钮样式
        if hasattr(self, '_action_button'):
            self._action_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {accent_color.name()};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {accent_color.lighter(110).name()};
                }}
                QPushButton:pressed {{
                    background-color: {accent_color.darker(110).name()};
                }}
            """)

        # 关闭按钮样式
        if hasattr(self, '_close_button'):
            self._close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color.name()};
                    border: none;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 30);
                }}
                QPushButton:pressed {{
                    background-color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 50);
                }}
            """)

        # 更新图标
        self._update_icon()

    def _update_icon(self):
        """更新图标"""
        # 这里可以设置图标，目前使用简单的文本图标
        icon_map = {
            AlertType.INFO: "ℹ",
            AlertType.SUCCESS: "✓",
            AlertType.WARNING: "⚠",
            AlertType.ERROR: "✗"
        }

        icon_text = icon_map.get(self._alert_type, "ℹ")
        accent_color, _, _ = self._get_colors()

        self._icon_label.setText(icon_text)
        self._icon_label.setStyleSheet(f"""
            QLabel {{
                color: {accent_color.name()};
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }}
        """)

    def _on_fade_finished(self):
        """淡出动画完成"""
        if self._fade_animation.endValue() == 0.0:
            self.hide()
            self.closed.emit()

    def close_with_animation(self):
        """带动画的关闭"""
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.start()

    def setTitle(self, title: str):
        """设置标题"""
        self._title = title
        if hasattr(self, '_title_label'):
            self._title_label.setText(title)

    def setMessage(self, message: str):
        """设置消息"""
        self._message = message
        if hasattr(self, '_message_label'):
            self._message_label.setText(message)

    def setAlertType(self, alert_type: AlertType):
        """设置警告类型"""
        self._alert_type = alert_type
        self._update_style()


class FluentNotification(QWidget):
    """
    浮动通知组件
    """

    closed = Signal()
    clicked = Signal()

    def __init__(self,
                 title: str = "",
                 message: str = "",
                 notification_type: AlertType = AlertType.INFO,
                 timeout: int = 5000,
                 closable: bool = True,
                 clickable: bool = False,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title = title
        self._message = message
        self._notification_type = notification_type
        self._timeout = timeout
        self._closable = closable
        self._clickable = clickable

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._setup_ui()
        self._setup_animation()
        self._connect_theme()

        if timeout > 0:
            QTimer.singleShot(timeout, self.close_with_animation)

    def _setup_ui(self):
        """设置UI"""
        # 主容器
        self._container = QFrame()
        self._container.setFrameStyle(QFrame.Shape.NoFrame)

        # 布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._container)

        container_layout = QHBoxLayout(self._container)
        container_layout.setContentsMargins(16, 12, 16, 12)
        container_layout.setSpacing(12)

        # 图标
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(32, 32)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self._icon_label)

        # 内容
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)

        # 标题
        self._title_label = QLabel(self._title)
        self._title_label.setWordWrap(True)
        content_layout.addWidget(self._title_label)

        # 消息
        if self._message:
            self._message_label = QLabel(self._message)
            self._message_label.setWordWrap(True)
            content_layout.addWidget(self._message_label)

        container_layout.addLayout(content_layout, 1)

        # 关闭按钮
        if self._closable:
            self._close_button = QPushButton("×")
            self._close_button.setFixedSize(24, 24)
            self._close_button.clicked.connect(self.close_with_animation)
            container_layout.addWidget(self._close_button)

        # 点击事件
        if self._clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setFixedWidth(350)
        self.adjustSize()

    def _setup_animation(self):
        """设置动画"""
        self._opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self._opacity_effect)

        # 修复 QByteArray 参数问题
        self._fade_animation = QPropertyAnimation(
            self._opacity_effect, QByteArray(b"opacity"))
        self._fade_animation.setDuration(300)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_animation.finished.connect(self._on_animation_finished)

        # 滑入动画
        self._slide_animation = QPropertyAnimation(self, QByteArray(b"pos"))
        self._slide_animation.setDuration(300)
        self._slide_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 显示动画
        self.show_notification()

    def _connect_theme(self):
        """连接主题"""
        theme_manager.theme_changed.connect(self._update_style)
        self._update_style()

    def _update_style(self):
        """更新样式"""
        theme = theme_manager
        # text_color is not directly used here for container
        accent_color, _, _ = self._get_colors()

        # 主容器样式
        if theme._current_mode == ThemeMode.DARK:  # 使用 _current_mode
            bg_color_container = QColor(45, 45, 45)
            border_color_container = QColor(70, 70, 70)
        else:
            bg_color_container = QColor(255, 255, 255)
            border_color_container = QColor(220, 220, 220)

        self._container.setStyleSheet(f"""
            QFrame {{
                background-color: rgba({bg_color_container.red()}, {bg_color_container.green()}, {bg_color_container.blue()}, 245);
                border: 1px solid rgba({border_color_container.red()}, {border_color_container.green()}, {border_color_container.blue()}, 180);
                border-radius: 8px;
            }}
        """)

        # 标题样式
        self._title_label.setStyleSheet(f"""
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                font-weight: 600;
                font-size: 14px;
                background: transparent;
            }}
        """)

        # 消息样式
        if hasattr(self, '_message_label'):
            msg_text_color = QColor(theme.get_color('text_primary'))
            self._message_label.setStyleSheet(f"""
                QLabel {{
                    color: rgba({msg_text_color.red()}, {msg_textColor.green()}, {msg_textColor.blue()}, 180);
                    font-size: 12px;
                    background: transparent;
                }}
            """)

        # 关闭按钮样式
        if hasattr(self, '_close_button'):
            close_btn_text_color = QColor(theme.get_color('text_primary'))
            self._close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {close_btn_text_color.name()};
                    border: none;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba({close_btn_text_color.red()}, {close_btn_textColor.green()}, {close_btn_textColor.blue()}, 30);
                }}
            """)

        # 更新图标, 传递 accent_color
        self._update_icon(accent_color)

    def _get_colors(self) -> tuple[QColor, QColor, QColor]:
        """根据类型获取颜色"""
        if self._notification_type == AlertType.INFO:
            return (QColor(0, 120, 215), QColor(240, 248, 255), QColor(0, 90, 158))
        elif self._notification_type == AlertType.SUCCESS:
            return (QColor(16, 124, 16), QColor(240, 248, 240), QColor(12, 100, 12))
        elif self._notification_type == AlertType.WARNING:
            return (QColor(255, 185, 0), QColor(255, 252, 240), QColor(200, 145, 0))
        elif self._notification_type == AlertType.ERROR:
            return (QColor(196, 43, 28), QColor(255, 245, 245), QColor(160, 30, 20))
        else:
            theme = theme_manager
            return (QColor(theme.get_color('accent')), QColor(theme.get_color('background')), QColor(theme.get_color('text_primary')))

    def _update_icon(self, accent_color: QColor):  # 接受 accent_color 作为参数
        """更新图标"""
        icon_map = {
            AlertType.INFO: "ℹ",
            AlertType.SUCCESS: "✓",
            AlertType.WARNING: "⚠",
            AlertType.ERROR: "✗"
        }

        icon_text = icon_map.get(self._notification_type, "ℹ")
        # accent_color, _, _ = self._get_colors() # 不再需要重新获取

        self._icon_label.setText(icon_text)
        self._icon_label.setStyleSheet(f"""
            QLabel {{
                color: {accent_color.name()};
                font-size: 20px;
                font-weight: bold;
                background: transparent;
            }}
        """)

    def show_notification(self):
        """显示通知"""
        # 定位到屏幕右下角
        screen_geometry = QApplication.primaryScreen().geometry()
        start_pos = QPoint(screen_geometry.width() - self.width() - 20,
                           screen_geometry.height() + 100)  # 从下方滑入

        end_pos = QPoint(screen_geometry.width() - self.width() - 20,
                         screen_geometry.height() - self.height() - 20)

        self.move(start_pos)
        self.show()

        # 滑入动画
        self._slide_animation.setStartValue(start_pos)
        self._slide_animation.setEndValue(end_pos)
        self._slide_animation.start()

        # 淡入动画
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.start()

    def close_with_animation(self):
        """带动画的关闭"""
        # 滑出动画
        current_pos = self.pos()
        end_pos = QPoint(current_pos.x() + 400, current_pos.y())  # 向右滑出

        self._slide_animation.setStartValue(current_pos)
        self._slide_animation.setEndValue(end_pos)
        self._slide_animation.start()

        # 淡出动画
        self._fade_animation.setStartValue(1.0)
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.start()

    def _on_animation_finished(self):
        """动画完成"""
        if self._fade_animation.endValue() == 0.0:
            self.close()
            self.closed.emit()

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class FluentMessageBar(QFrame):
    """
    消息栏组件
    """

    closed = Signal()

    def __init__(self,
                 message: str = "",
                 message_type: AlertType = AlertType.INFO,
                 closable: bool = True,
                 action_text: str = "",
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._message = message
        self._message_type = message_type
        self._closable = closable
        self._action_text = action_text

        self.setFrameStyle(QFrame.Shape.NoFrame)
        self._setup_ui()
        self._connect_theme()

    def _setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # 图标
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(20, 20)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._icon_label)

        # 消息
        self._message_label = QLabel(self._message)
        self._message_label.setWordWrap(True)
        layout.addWidget(self._message_label, 1)

        # 操作按钮
        if self._action_text:
            self._action_button = QPushButton(self._action_text)
            layout.addWidget(self._action_button)

        # 关闭按钮
        if self._closable:
            self._close_button = QPushButton("×")
            self._close_button.setFixedSize(20, 20)
            self._close_button.clicked.connect(self._close_clicked)
            layout.addWidget(self._close_button)

    def _connect_theme(self):
        """连接主题"""
        theme_manager.theme_changed.connect(self._update_style)
        self._update_style()

    def _update_style(self):
        """更新样式"""
        accent_color, bg_color, text_color = self._get_colors()

        # 调整背景色透明度
        bg_color.setAlpha(200)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, {bg_color.alpha()});
                border-left: 4px solid {accent_color.name()};
            }}
        """)

        # 更新子组件样式
        self._update_icon()

        # 消息样式
        self._message_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color.name()};
                font-size: 13px;
                background: transparent;
            }}
        """)

        # 按钮样式
        if hasattr(self, '_action_button'):
            self._action_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {accent_color.name()};
                    border: 1px solid {accent_color.name()};
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: rgba({accent_color.red()}, {accent_color.green()}, {accent_color.blue()}, 30);
                }}
            """)

        if hasattr(self, '_close_button'):
            self._close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color.name()};
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba({text_color.red()}, {text_color.green()}, {text_color.blue()}, 30);
                }}
            """)

    def _get_colors(self) -> tuple[QColor, QColor, QColor]:
        """根据类型获取颜色"""
        if self._message_type == AlertType.INFO:
            return (QColor(0, 120, 215), QColor(240, 248, 255), QColor(0, 90, 158))
        elif self._message_type == AlertType.SUCCESS:
            return (QColor(16, 124, 16), QColor(240, 248, 240), QColor(12, 100, 12))
        elif self._message_type == AlertType.WARNING:
            return (QColor(255, 185, 0), QColor(255, 252, 240), QColor(200, 145, 0))
        elif self._message_type == AlertType.ERROR:
            return (QColor(196, 43, 28), QColor(255, 245, 245), QColor(160, 30, 20))
        else:
            theme = theme_manager
            return (QColor(theme.get_color('accent')), QColor(theme.get_color('background')), QColor(theme.get_color('text_primary')))

    def _update_icon(self):
        """更新图标"""
        icon_map = {
            AlertType.INFO: "ℹ",
            AlertType.SUCCESS: "✓",
            AlertType.WARNING: "⚠",
            AlertType.ERROR: "✗"
        }

        icon_text = icon_map.get(self._message_type, "ℹ")
        accent_color, _, _ = self._get_colors()

        self._icon_label.setText(icon_text)
        self._icon_label.setStyleSheet(f"""
            QLabel {{
                color: {accent_color.name()};
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }}
        """)

    def _close_clicked(self):
        """关闭按钮点击"""
        self.hide()
        self.closed.emit()

    def setMessage(self, message: str):
        """设置消息"""
        self._message = message
        self._message_label.setText(message)

    def setMessageType(self, message_type: AlertType):
        """设置消息类型"""
        self._message_type = message_type
        self._update_style()
