"""
Fluent Design Style Dialog and Notification Components
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QWidget, QGraphicsOpacityEffect, QApplication,
                               QLineEdit)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QByteArray, QPoint
from PySide6.QtGui import QColor
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import FluentTransition, FluentMicroInteraction
from components.basic.forms.button import FluentButton
from typing import Optional, Callable, List, Tuple


class FluentDialog(QDialog):
    """**Fluent Design Base Dialog**"""

    def __init__(self, parent: Optional[QWidget] = None,
                 title: str = "Dialog", width: int = 400, height: int = 300):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.WindowType.Dialog |
                            Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._setup_ui()
        self._setup_style()

        # Add animation effects
        self._setup_animations()

        theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Title bar
        title_layout = QHBoxLayout()

        self.title_label = QLabel(self.windowTitle())
        self.title_label.setFont(self.font())
        title_font = self.title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)

        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.clicked.connect(self.close)

        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_btn)

        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        # Button area
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.addStretch()

        layout.addLayout(title_layout)
        layout.addWidget(self.content_widget, 1)
        layout.addLayout(self.button_layout)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentDialog {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 12px;
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                font-size: 14px;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 16px;
                font-size: 18px;
                font-weight: bold;
                color: {theme.get_color('text_secondary').name()};
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                color: {theme.get_color('text_primary').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup animations"""
        # Fade in animation with enhanced easing
        self.fade_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.fade_effect)

        self.fade_animation = FluentTransition.create_transition(
            self, FluentTransition.FADE,
            duration=FluentAnimation.DURATION_MEDIUM,
            easing=FluentTransition.EASE_SPRING
        )
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)

        # Scale animation with enhanced easing
        self.scale_animation = FluentTransition.create_transition(
            self, FluentTransition.SCALE,
            duration=FluentAnimation.DURATION_MEDIUM,
            easing=FluentTransition.EASE_SPRING
        )

    def add_content_widget(self, widget: QWidget):
        """**Add content widget**"""
        self.content_layout.addWidget(widget)

    def add_button(self, text: str, style: Optional[str] = None,
                   callback: Optional[Callable] = None) -> FluentButton:
        """**Add button**"""
        button = FluentButton(
            text, style=style or FluentButton.ButtonStyle.PRIMARY)

        if callback:
            button.clicked.connect(callback)

        # Add micro-interaction to button
        button.pressed.connect(
            lambda: FluentMicroInteraction.button_press(button, scale=0.95)
        )

        self.button_layout.addWidget(button)
        return button

    def show_animated(self):
        """**Show with animation**"""
        # Calculate center position
        parent_widget = self.parent()
        if parent_widget and isinstance(parent_widget, QWidget):
            parent_rect = parent_widget.geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
        else:
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2

        # Set initial position and size
        start_rect = QRect(x + self.width() // 4, y + self.height() // 4,
                           self.width() // 2, self.height() // 2)
        end_rect = QRect(x, y, self.width(), self.height())

        self.setGeometry(start_rect)
        self.show()

        # Start animation
        self.scale_animation.setStartValue(start_rect)
        self.scale_animation.setEndValue(end_rect)

        self.fade_animation.start()
        self.scale_animation.start()

    def close_animated(self):
        """**Close with animation**"""
        # Fade out animation with enhanced easing
        fade_out = FluentTransition.create_transition(
            self, FluentTransition.FADE,
            duration=FluentAnimation.DURATION_FAST,
            easing=FluentTransition.EASE_SMOOTH
        )
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.finished.connect(self.close)
        fade_out.start()

    def _on_theme_changed(self, theme_name: str):
        """Theme change handler"""
        # Suppress unused parameter warning
        _ = theme_name
        self._setup_style()


class FluentMessageBox(FluentDialog):
    """**Fluent Design Message Box**"""

    class Icon:
        INFORMATION = "ℹ️"
        WARNING = "⚠️"
        ERROR = "❌"
        QUESTION = "❓"
        SUCCESS = "✅"

    def __init__(self, parent: Optional[QWidget] = None,
                 title: str = "Message", message: str = "",
                 icon: Optional[str] = None, buttons: Optional[List[str]] = None):
        super().__init__(parent, title, 450, 250)

        self._setup_message_ui(message, icon, buttons or ["OK"])

        self._dialog_result: Optional[str] = None

    def _setup_message_ui(self, message: str, icon: Optional[str], buttons: List[str]):
        """Setup message box UI"""
        # Icon and message
        content_layout = QHBoxLayout()

        if icon:
            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            icon_label.setFont(self.font())
            icon_font = icon_label.font()
            icon_font.setPointSize(24)
            icon_label.setFont(icon_font)
            content_layout.addWidget(icon_label)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.addWidget(message_label, 1)

        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        self.add_content_widget(content_widget)

        # Add buttons
        for i, button_text in enumerate(buttons):
            style = (FluentButton.ButtonStyle.PRIMARY if i == 0
                     else FluentButton.ButtonStyle.SECONDARY)

            self.add_button(button_text, style,
                            lambda _, text=button_text: self._on_button_clicked(text))

    def _on_button_clicked(self, button_text: str):
        """Button click handler"""
        self._dialog_result = button_text
        self.close_animated()

    def get_result(self) -> Optional[str]:
        """Get dialog result"""
        return self._dialog_result

    @staticmethod
    def information(parent: QWidget, title: str, message: str) -> Optional[str]:
        """**Show information dialog**"""
        dialog = FluentMessageBox(parent, title, message,
                                  FluentMessageBox.Icon.INFORMATION)
        dialog.exec()
        return dialog.get_result()

    @staticmethod
    def warning(parent: QWidget, title: str, message: str) -> Optional[str]:
        """**Show warning dialog**"""
        dialog = FluentMessageBox(parent, title, message,
                                  FluentMessageBox.Icon.WARNING)
        dialog.exec()
        return dialog.get_result()

    @staticmethod
    def error(parent: QWidget, title: str, message: str) -> Optional[str]:
        """**Show error dialog**"""
        dialog = FluentMessageBox(parent, title, message,
                                  FluentMessageBox.Icon.ERROR)
        dialog.exec()
        return dialog.get_result()

    @staticmethod
    def question(parent: QWidget, title: str, message: str) -> Optional[str]:
        """**Show question dialog**"""
        dialog = FluentMessageBox(parent, title, message,
                                  FluentMessageBox.Icon.QUESTION,
                                  ["Yes", "No"])
        dialog.exec()
        return dialog.get_result()


class FluentInputDialog(FluentDialog):
    """**Input Dialog**"""

    def __init__(self, parent: Optional[QWidget] = None,
                 title: str = "Input", label: str = "Please enter:",
                 default_text: str = ""):
        super().__init__(parent, title, 400, 200)

        self.input_text = ""
        self._setup_input_ui(label, default_text)

    def _setup_input_ui(self, label: str, default_text: str):
        """Setup input UI"""
        # Label and input box
        label_widget = QLabel(label)

        self.line_edit = QLineEdit(default_text)
        self.line_edit.returnPressed.connect(self._on_ok_clicked)

        self.add_content_widget(label_widget)
        self.add_content_widget(self.line_edit)

        # Buttons
        self.add_button("OK", FluentButton.ButtonStyle.PRIMARY,
                        self._on_ok_clicked)
        self.add_button(
            "Cancel", FluentButton.ButtonStyle.SECONDARY, self.close)

        # Set focus
        QTimer.singleShot(100, self.line_edit.setFocus)

    def _on_ok_clicked(self):
        """OK button click"""
        self.input_text = self.line_edit.text()
        self.accept()

    @staticmethod
    def get_text(parent: QWidget, title: str, label: str, default_text: str = "") -> Tuple[str, bool]:
        """**Get user input text**

        Returns:
            (text, ok) - Input text and whether confirmed
        """
        dialog = FluentInputDialog(parent, title, label, default_text)
        result = dialog.exec()
        return dialog.input_text, result == QDialog.DialogCode.Accepted


class FluentProgressDialog(FluentDialog):
    """**Progress Dialog**"""

    def __init__(self, parent: Optional[QWidget] = None,
                 title: str = "Please wait", message: str = "Processing...",
                 cancelable: bool = True):
        super().__init__(parent, title, 400, 200)

        self.canceled = False
        self._setup_progress_ui(message, cancelable)

    def _setup_progress_ui(self, message: str, cancelable: bool):
        """Setup progress UI"""
        # Message
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Progress bar
        from components.basic.display.progress import FluentProgressBar
        self.progress_bar = FluentProgressBar()
        self.progress_bar.setRange(0, 100)

        # Detail information
        self.detail_label = QLabel("")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color('text_secondary').name()};
                font-size: 12px;
            }}
        """)

        self.add_content_widget(message_label)
        self.add_content_widget(self.progress_bar)
        self.add_content_widget(self.detail_label)

        # Cancel button
        if cancelable:
            self.add_button(
                "Cancel", FluentButton.ButtonStyle.SECONDARY, self._on_cancel_clicked)

    def set_progress(self, value: int, detail: str = ""):
        """**Set progress**"""
        self.progress_bar.setValue(value)
        if detail:
            self.detail_label.setText(detail)

    def set_indeterminate(self, enabled: bool):
        """**Set indeterminate progress**"""
        self.progress_bar.set_indeterminate(enabled)

    def _on_cancel_clicked(self):
        """Cancel button click"""
        self.canceled = True
        self.close()


class FluentToast(QWidget):
    """**Toast Notification**"""

    class Type:
        INFO = "info"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"

    def __init__(self, message: str, toast_type: str = Type.INFO,
                 duration: int = 3000, parent: Optional[QWidget] = None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.toast_type = toast_type
        self.duration = duration

        self._setup_ui(message)
        self._setup_style()
        self._setup_animations()

    def _setup_ui(self, message: str):
        """Setup UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Icon
        icon_map = {
            self.Type.INFO: "ℹ️",
            self.Type.SUCCESS: "✅",
            self.Type.WARNING: "⚠️",
            self.Type.ERROR: "❌"
        }

        self.icon_label = QLabel(icon_map.get(self.toast_type, "ℹ️"))
        self.icon_label.setFont(self.font())
        icon_font = self.icon_label.font()
        icon_font.setPointSize(16)
        self.icon_label.setFont(icon_font)

        # Message text
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.message_label, 1)

        self.adjustSize()

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        # Set different background colors based on type
        color_map = {
            self.Type.INFO: theme.get_color('primary'),
            self.Type.SUCCESS: QColor("#10b981"),
            self.Type.WARNING: QColor("#f59e0b"),
            self.Type.ERROR: QColor("#ef4444")
        }

        bg_color = color_map.get(self.toast_type, theme.get_color('primary'))

        style_sheet = f"""
            FluentToast {{
                background-color: {bg_color.name()};
                border-radius: 8px;
                border: 1px solid {bg_color.darker(110).name()};
            }}
            QLabel {{
                color: white;
                font-size: 14px;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup animations"""
        # Fade in/out effect
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        # Slide in animation
        self.slide_animation = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self.slide_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self.slide_animation.setEasingCurve(FluentAnimation.EASE_OUT)

        # Fade in animation
        self.fade_in_animation = QPropertyAnimation(
            self.opacity_effect, QByteArray(b"opacity"))
        self.fade_in_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)

        # Fade out animation
        self.fade_out_animation = QPropertyAnimation(
            self.opacity_effect, QByteArray(b"opacity"))
        self.fade_out_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.finished.connect(self.close)

    def show_toast(self, parent_widget: Optional[QWidget] = None):
        """**Show Toast**"""
        if parent_widget:
            # Calculate display position (top right corner)
            parent_rect = parent_widget.geometry()
            x = parent_rect.right() - self.width() - 20
            y = parent_rect.top() + 20
        else:
            # Use screen top right corner
            screen = QApplication.primaryScreen().geometry()
            x = screen.right() - self.width() - 20
            y = screen.top() + 20

        # Set initial position (off screen)
        start_rect = QRect(x + self.width(), y, self.width(), self.height())
        end_rect = QRect(x, y, self.width(), self.height())

        self.setGeometry(start_rect)
        self.show()

        # Start slide in animation
        self.slide_animation.setStartValue(start_rect)
        self.slide_animation.setEndValue(end_rect)
        self.slide_animation.start()
        self.fade_in_animation.start()

        # Set auto close timer
        if self.duration > 0:
            QTimer.singleShot(self.duration, self.fade_out_animation.start)

    @staticmethod
    def show_info(message: str, parent: Optional[QWidget] = None, duration: int = 3000):
        """**Show info Toast**"""
        toast = FluentToast(message, FluentToast.Type.INFO, duration, parent)
        toast.show_toast(parent)
        return toast

    @staticmethod
    def show_success(message: str, parent: Optional[QWidget] = None, duration: int = 3000):
        """**Show success Toast**"""
        toast = FluentToast(
            message, FluentToast.Type.SUCCESS, duration, parent)
        toast.show_toast(parent)
        return toast

    @staticmethod
    def show_warning(message: str, parent: Optional[QWidget] = None, duration: int = 3000):
        """**Show warning Toast**"""
        toast = FluentToast(
            message, FluentToast.Type.WARNING, duration, parent)
        toast.show_toast(parent)
        return toast

    @staticmethod
    def show_error(message: str, parent: Optional[QWidget] = None, duration: int = 3000):
        """**Show error Toast**"""
        toast = FluentToast(message, FluentToast.Type.ERROR, duration, parent)
        toast.show_toast(parent)
        return toast
