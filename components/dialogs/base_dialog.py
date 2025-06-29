"""
Base Dialog Component for Fluent Design System

Provides a unified foundation for all dialog types with consistent:
- Styling and theming
- Animation patterns  
- Layout management
- Accessibility support
- Event handling
"""

from typing import Optional, Callable, Dict, Any, List, Union
from enum import Enum
from abc import abstractmethod

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QWidget, QGraphicsOpacityEffect,
                               QGraphicsDropShadowEffect, QSizePolicy)
from PySide6.QtCore import (Qt, QEasingCurve, QPropertyAnimation, Signal,
                            QByteArray, QTimer, QSize, QRect, QPoint)
from PySide6.QtGui import QPainter, QColor, QPaintEvent, QKeyEvent

from ..base.fluent_control_base import FluentControlBase, FluentThemeAware
from core.theme import theme_manager


class DialogSize(Enum):
    """Standard dialog size presets"""
    SMALL = (320, 200)
    MEDIUM = (480, 320)
    LARGE = (640, 480)
    EXTRA_LARGE = (800, 600)
    CUSTOM = None


class DialogType(Enum):
    """Dialog type for styling and behavior"""
    MODAL = "modal"
    MODELESS = "modeless"
    POPUP = "popup"
    OVERLAY = "overlay"


class ButtonRole(Enum):
    """Standard button roles for dialogs"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    DESTRUCTIVE = "destructive"
    CANCEL = "cancel"
    CLOSE = "close"


class FluentBaseDialog(QDialog, FluentControlBase, FluentThemeAware):
    """
    Base class for all Fluent Design dialogs.

    Provides consistent foundation for:
    - Modal and modeless dialogs
    - Standard button layouts
    - Theme-aware styling
    - Smooth animations
    - Accessibility support
    - Keyboard navigation
    """

    # Enhanced signals
    dialog_opened = Signal()
    dialog_closed = Signal(int)  # Result code
    button_clicked = Signal(str, object)  # Button role, button object
    content_changed = Signal()
    size_changed = Signal(QSize)

    def __init__(self,
                 parent: Optional[QWidget] = None,
                 title: str = "",
                 dialog_type: DialogType = DialogType.MODAL,
                 size_preset: DialogSize = DialogSize.MEDIUM):
        super().__init__(parent)
        FluentControlBase.__init__(self)
        FluentThemeAware.__init__(self)

        # Core properties
        self._title = title
        self._dialog_type = dialog_type
        self._size_preset = size_preset
        self._custom_size: Optional[QSize] = None

        # Content management
        self._content_widgets: List[QWidget] = []
        self._buttons: Dict[str, QPushButton] = {}
        self._button_layout: Optional[QHBoxLayout] = None

        # Animation system
        self._entrance_animation: Optional[QPropertyAnimation] = None
        self._exit_animation: Optional[QPropertyAnimation] = None
        self._is_animating = False

        # Accessibility
        self._escape_closes = True
        self._enter_accepts = True
        self._focus_chain: List[QWidget] = []

        # Initialize UI
        self._setup_dialog_properties()
        self._create_layout()
        self._setup_styling()
        self._setup_animations()
        self._setup_keyboard_handling()

        # Apply initial theme
        self.apply_theme()

        # Connect to theme changes
        try:
            if hasattr(theme_manager, 'theme_changed'):
                theme_manager.theme_changed.connect(self.apply_theme)
        except Exception:
            # Handle cases where theme manager might not be fully initialized
            pass

    def _setup_dialog_properties(self):
        """Configure basic dialog properties"""
        # Window flags based on dialog type
        flags = Qt.WindowType.Dialog

        if self._dialog_type == DialogType.MODAL:
            flags |= Qt.WindowType.FramelessWindowHint
            self.setModal(True)
        elif self._dialog_type == DialogType.POPUP:
            flags |= Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
            self.setModal(False)
        elif self._dialog_type == DialogType.OVERLAY:
            flags |= Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip
            self.setModal(True)

        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set size
        if self._size_preset != DialogSize.CUSTOM:
            size = self._size_preset.value
            self.setMinimumSize(size[0], size[1])
            self.resize(size[0], size[1])

    def _create_layout(self):
        """Create the main dialog layout structure"""
        # Main layout with padding for shadow
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Content container with rounded corners and shadow
        self.content_container = QFrame()
        self.content_container.setObjectName("dialogContainer")
        self.content_container.setFrameStyle(QFrame.Shape.NoFrame)

        # Add shadow effect
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setColor(QColor(0, 0, 0, 60))
        self.shadow_effect.setOffset(0, 8)
        self.content_container.setGraphicsEffect(self.shadow_effect)

        main_layout.addWidget(self.content_container)

        # Container layout
        self.container_layout = QVBoxLayout(self.content_container)
        self.container_layout.setContentsMargins(24, 24, 24, 24)
        self.container_layout.setSpacing(16)

        # Title section
        self._create_title_section()

        # Content area (to be populated by subclasses)
        self.content_area = QFrame()
        self.content_area.setObjectName("contentArea")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)
        self.container_layout.addWidget(self.content_area, 1)

        # Button area
        self._create_button_section()

    def _create_title_section(self):
        """Create the title section"""
        if self._title:
            self.title_label = QLabel(self._title)
            self.title_label.setObjectName("dialogTitle")
            self.container_layout.addWidget(self.title_label)

    def _create_button_section(self):
        """Create the button section"""
        self.button_container = QFrame()
        self.button_container.setObjectName("buttonContainer")
        self._button_layout = QHBoxLayout(self.button_container)
        self._button_layout.setContentsMargins(0, 16, 0, 0)
        self._button_layout.setSpacing(12)
        self._button_layout.addStretch()

        self.container_layout.addWidget(self.button_container)

    def _setup_styling(self):
        """Setup Fluent Design styling"""
        self.setStyleSheet("""
            FluentBaseDialog {
                background: transparent;
            }
            
            #dialogContainer {
                background-color: var(--dialog-background, #f9f9f9);
                border: 1px solid var(--dialog-border, #e1e1e1);
                border-radius: 8px;
            }
            
            #dialogTitle {
                font-size: 20px;
                font-weight: 600;
                color: var(--text-primary, #323130);
                margin-bottom: 8px;
            }
            
            #contentArea {
                background: transparent;
            }
            
            #buttonContainer {
                background: transparent;
                border-top: 1px solid var(--dialog-separator, #e1e1e1);
                margin-top: 8px;
                padding-top: 16px;
            }
            
            QPushButton[role="primary"] {
                background-color: var(--accent-default, #0078d4);
                color: var(--text-on-accent, white);
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 600;
                min-width: 80px;
                min-height: 32px;
            }
            
            QPushButton[role="primary"]:hover {
                background-color: var(--accent-hover, #106ebe);
            }
            
            QPushButton[role="primary"]:pressed {
                background-color: var(--accent-pressed, #005a9e);
            }
            
            QPushButton[role="secondary"] {
                background-color: var(--button-background, transparent);
                color: var(--text-primary, #323130);
                border: 1px solid var(--button-border, #8a8886);
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 14px;
                min-width: 80px;
                min-height: 32px;
            }
            
            QPushButton[role="secondary"]:hover {
                background-color: var(--button-hover, #f3f2f1);
                border-color: var(--button-border-hover, #323130);
            }
            
            QPushButton[role="secondary"]:pressed {
                background-color: var(--button-pressed, #edebe9);
                border-color: var(--button-border-pressed, #201f1e);
            }
            
            QPushButton[role="destructive"] {
                background-color: var(--error-default, #d13438);
                color: var(--text-on-accent, white);
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 600;
                min-width: 80px;
                min-height: 32px;
            }
            
            QPushButton[role="destructive"]:hover {
                background-color: var(--error-hover, #a4262c);
            }
            
            QPushButton[role="destructive"]:pressed {
                background-color: var(--error-pressed, #751d21);
            }
            
            QPushButton[role="cancel"], QPushButton[role="close"] {
                background-color: var(--button-background, transparent);
                color: var(--text-secondary, #605e5c);
                border: 1px solid var(--button-border, #8a8886);
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 14px;
                min-width: 80px;
                min-height: 32px;
            }
            
            QPushButton[role="cancel"]:hover, QPushButton[role="close"]:hover {
                background-color: var(--button-hover, #f3f2f1);
                border-color: var(--button-border-hover, #323130);
            }
        """)

    def _setup_animations(self):
        """Setup entrance and exit animations"""
        # Opacity effect for animations
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        # Entrance animation (fade in + scale)
        self._entrance_animation = QPropertyAnimation(
            self.opacity_effect, QByteArray(b"opacity"))
        self._entrance_animation.setDuration(250)
        self._entrance_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._entrance_animation.finished.connect(self._on_entrance_finished)

        # Exit animation (fade out)
        self._exit_animation = QPropertyAnimation(
            self.opacity_effect, QByteArray(b"opacity"))
        self._exit_animation.setDuration(200)
        self._exit_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._exit_animation.finished.connect(self._on_exit_finished)

    def _setup_keyboard_handling(self):
        """Setup keyboard navigation and shortcuts"""
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def add_content_widget(self, widget: QWidget, stretch: int = 0):
        """Add a widget to the content area"""
        self.content_layout.addWidget(widget, stretch)
        self._content_widgets.append(widget)
        self.content_changed.emit()

    def insert_content_widget(self, index: int, widget: QWidget):
        """Insert a widget at specific position in content area"""
        self.content_layout.insertWidget(index, widget)
        self._content_widgets.insert(index, widget)
        self.content_changed.emit()

    def remove_content_widget(self, widget: QWidget):
        """Remove a widget from the content area"""
        if widget in self._content_widgets:
            self.content_layout.removeWidget(widget)
            self._content_widgets.remove(widget)
            widget.setParent(None)
            self.content_changed.emit()

    def add_button(self,
                   text: str,
                   role: ButtonRole = ButtonRole.SECONDARY,
                   callback: Optional[Callable] = None,
                   enabled: bool = True) -> QPushButton:
        """Add a button to the dialog"""
        button = QPushButton(text)
        button.setProperty("role", role.value)
        button.setEnabled(enabled)

        if callback:
            button.clicked.connect(callback)

        # Connect to button clicked signal
        button.clicked.connect(
            lambda: self.button_clicked.emit(role.value, button))

        # Add to layout
        if self._button_layout:
            if role == ButtonRole.CANCEL or role == ButtonRole.CLOSE:
                self._button_layout.insertWidget(0, button)
            else:
                self._button_layout.addWidget(button)

        # Store reference
        self._buttons[role.value] = button

        return button

    def get_button(self, role: ButtonRole) -> Optional[QPushButton]:
        """Get button by role"""
        return self._buttons.get(role.value)

    def set_button_enabled(self, role: ButtonRole, enabled: bool):
        """Enable/disable button by role"""
        button = self.get_button(role)
        if button:
            button.setEnabled(enabled)

    def set_title(self, title: str):
        """Set dialog title"""
        self._title = title
        if hasattr(self, 'title_label'):
            self.title_label.setText(title)

    def set_custom_size(self, width: int, height: int):
        """Set custom dialog size"""
        self._size_preset = DialogSize.CUSTOM
        self._custom_size = QSize(width, height)
        self.resize(width, height)
        self.size_changed.emit(self._custom_size)

    def show_animated(self):
        """Show dialog with entrance animation"""
        if self._is_animating:
            return

        self._is_animating = True
        self.show()

        # Center on parent
        self._center_on_parent()

        # Start entrance animation
        if hasattr(self, 'opacity_effect') and self._entrance_animation:
            self.opacity_effect.setOpacity(0.0)
            self._entrance_animation.setStartValue(0.0)
            self._entrance_animation.setEndValue(1.0)
            self._entrance_animation.start()

        self.dialog_opened.emit()

    def close_animated(self, result: int = QDialog.DialogCode.Rejected):
        """Close dialog with exit animation"""
        if self._is_animating:
            return

        self._is_animating = True
        self._exit_result = result

        # Start exit animation
        if self._exit_animation:
            self._exit_animation.setStartValue(1.0)
            self._exit_animation.setEndValue(0.0)
            self._exit_animation.start()
        else:
            # Fallback if animation not available
            self._on_exit_finished()

    def _center_on_parent(self):
        """Center dialog on parent widget"""
        parent = self.parent()
        if parent and isinstance(parent, QWidget):
            parent_widget = parent
            parent_rect = parent_widget.geometry()
            self.move(
                parent_rect.center().x() - self.width() // 2,
                parent_rect.center().y() - self.height() // 2
            )

    def _on_entrance_finished(self):
        """Handle entrance animation completion"""
        self._is_animating = False

    def _on_exit_finished(self):
        """Handle exit animation completion"""
        self._is_animating = False
        self.dialog_closed.emit(
            getattr(self, '_exit_result', QDialog.DialogCode.Rejected))
        self.done(getattr(self, '_exit_result', QDialog.DialogCode.Rejected))

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape and self._escape_closes:
            self.close_animated(QDialog.DialogCode.Rejected)
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and self._enter_accepts:
            # Try to trigger primary button
            primary_button = self.get_button(ButtonRole.PRIMARY)
            if primary_button and primary_button.isEnabled():
                primary_button.click()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event: QPaintEvent):
        """Custom paint event for backdrop"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw backdrop for modal dialogs
        if self._dialog_type in (DialogType.MODAL, DialogType.OVERLAY):
            backdrop_color = self.get_theme_color(
                'dialog-backdrop', '#80000000')
            painter.fillRect(self.rect(), QColor(backdrop_color))

        super().paintEvent(event)

    def apply_theme(self):
        """Apply current theme to dialog"""
        theme = self.get_current_theme()
        if not theme:
            return

        # Update CSS variables
        style_vars = {
            '--dialog-background': theme.get('surface_primary', '#f9f9f9'),
            '--dialog-border': theme.get('stroke_default', '#e1e1e1'),
            '--dialog-separator': theme.get('stroke_subtle', '#e1e1e1'),
            '--dialog-backdrop': theme.get('backdrop', '#80000000'),
            '--text-primary': theme.get('text_primary', '#323130'),
            '--text-secondary': theme.get('text_secondary', '#605e5c'),
            '--text-on-accent': theme.get('text_on_accent', '#ffffff'),
            '--accent-default': theme.get('accent_default', '#0078d4'),
            '--accent-hover': theme.get('accent_hover', '#106ebe'),
            '--accent-pressed': theme.get('accent_pressed', '#005a9e'),
            '--error-default': theme.get('error_default', '#d13438'),
            '--error-hover': theme.get('error_hover', '#a4262c'),
            '--error-pressed': theme.get('error_pressed', '#751d21'),
            '--button-background': theme.get('button_background', 'transparent'),
            '--button-border': theme.get('button_border', '#8a8886'),
            '--button-border-hover': theme.get('button_border_hover', '#323130'),
            '--button-border-pressed': theme.get('button_border_pressed', '#201f1e'),
            '--button-hover': theme.get('button_hover', '#f3f2f1'),
            '--button-pressed': theme.get('button_pressed', '#edebe9'),
        }

        # Apply updated styling
        current_style = self.styleSheet()
        for var_name, var_value in style_vars.items():
            current_style = current_style.replace(
                f'var({var_name}, ', f'{var_value}; /* var({var_name}, ')

        self.setStyleSheet(current_style)
        self.theme_applied.emit()

    @abstractmethod
    def accept(self):
        """Accept the dialog - to be implemented by subclasses"""
        pass

    @abstractmethod
    def reject(self):
        """Reject the dialog - to be implemented by subclasses"""
        pass


class FluentDialogBuilder:
    """Builder pattern for creating dialogs with fluent API"""

    def __init__(self, dialog_class=FluentBaseDialog):
        self._dialog_class = dialog_class
        self._title = ""
        self._dialog_type = DialogType.MODAL
        self._size_preset = DialogSize.MEDIUM
        self._buttons = []
        self._content_widgets = []

    def title(self, title: str):
        """Set dialog title"""
        self._title = title
        return self

    def modal(self):
        """Make dialog modal"""
        self._dialog_type = DialogType.MODAL
        return self

    def modeless(self):
        """Make dialog modeless"""
        self._dialog_type = DialogType.MODELESS
        return self

    def size(self, preset: DialogSize):
        """Set dialog size preset"""
        self._size_preset = preset
        return self

    def add_button(self, text: str, role: ButtonRole, callback: Optional[Callable] = None):
        """Add button to dialog"""
        self._buttons.append((text, role, callback))
        return self

    def add_content(self, widget: QWidget):
        """Add content widget"""
        self._content_widgets.append(widget)
        return self

    def build(self, parent: Optional[QWidget] = None):
        """Build the dialog"""
        dialog = self._dialog_class(
            parent, self._title, self._dialog_type, self._size_preset)

        # Add content widgets
        for widget in self._content_widgets:
            dialog.add_content_widget(widget)

        # Add buttons
        for text, role, callback in self._buttons:
            dialog.add_button(text, role, callback)

        return dialog
