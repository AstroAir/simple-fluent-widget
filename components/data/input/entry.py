"""
Fluent Design Data Entry Components - Python 3.11+ Optimized

Advanced input fields, editors, and form controls with modern animation effects.
Optimized for Python 3.11+ with:
- Union type syntax (|) and PEP 604 union types  
- Dataclasses with slots and frozen optimizations
- Enhanced pattern matching and type safety
- Better error handling and validation
- Performance optimizations with caching
- Modern animation system integration
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol, TypeVar, Generic, TypeAlias, Final, Any, Callable, Optional, List
from collections.abc import Sequence, Mapping
from functools import lru_cache, cached_property
from contextlib import contextmanager, suppress

from PySide6.QtWidgets import (
    QWidget, QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QTimeEdit, QDateTimeEdit, QSpinBox, QDoubleSpinBox,
    QSlider, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QCompleter, QListWidget, QListWidgetItem, QScrollArea,
    QCheckBox, QRadioButton, QButtonGroup, QGroupBox,
    QGridLayout, QPushButton, QFileDialog, QProgressBar
)
from PySide6.QtCore import (
    Qt, Signal, QDate, QTime, QDateTime, QTimer, QRegularExpression,
    QStringListModel, QPropertyAnimation, QEasingCurve, QRect, Slot
)
from PySide6.QtGui import (
    QValidator, QRegularExpressionValidator, QFont, QPixmap,
    QIcon, QPainter, QColor, QBrush, QPen, QLinearGradient
)

# Enhanced error handling for imports
try:
    from core.theme import theme_manager
    THEME_AVAILABLE = True
except ImportError:
    theme_manager = None
    THEME_AVAILABLE = False

try:
    from core.animation import FluentAnimation
    BASIC_ANIMATION_AVAILABLE = True
except ImportError:
    FluentAnimation = None
    BASIC_ANIMATION_AVAILABLE = False

try:
    from core.enhanced_animations import (
        FluentTransition, FluentMicroInteraction,  # type: ignore
        FluentRevealEffect, FluentSequence, FluentStateTransition  # type: ignore
    )
    ENHANCED_ANIMATION_AVAILABLE = True
except ImportError:
    ENHANCED_ANIMATION_AVAILABLE = False
    
    # Fallback classes with proper typing
    class AnimationProxy:
        @staticmethod
        def fade_in(widget, duration=200): pass
        @staticmethod 
        def hover_glow(widget, intensity=0.1): pass
        @staticmethod
        def pulse_animation(widget, scale=1.02): pass
        @staticmethod
        def shake_animation(widget, intensity=3): pass
        @staticmethod
        def slide_in(widget, duration=200, direction="up"): pass
        @staticmethod
        def button_press(widget, scale=0.9): pass
        @staticmethod
        def scale_animation(widget, scale=1.05): pass
        
    # Create instances for consistent interface
    FluentRevealEffect = AnimationProxy()
    FluentMicroInteraction = AnimationProxy()
    
    # Proxy classes for enhanced animations
    class FluentTransition:
        EASE_SMOOTH = "smooth"
        EASE_CRISP = "crisp"
        EASE_SPRING = "spring"
    
    class FluentStateTransition:
        def __init__(self, widget): 
            self.widget = widget
        def addState(self, name, props, duration=200, easing="smooth"): pass
        def transitionTo(self, state): pass
        
    class FluentSequence:
        def __init__(self, widget): 
            self.widget = widget
        def addCallback(self, callback): pass
        def addPause(self, duration): pass
        def start(self): pass

# Type definitions
WidgetValue: TypeAlias = str | int | float | bool | QDate | QTime | QDateTime
ValidatorResult: TypeAlias = tuple[QValidator.State, str, int]


# Enums for component states
class InputState(Enum):
    """Enhanced input field states"""
    NORMAL = auto()
    FOCUSED = auto()
    ERROR = auto()
    DISABLED = auto()
    SUCCESS = auto()

class MaskCharacter(Enum):
    """Mask character definitions"""
    DIGIT = ('#', r'\d')
    LETTER = ('A', r'[A-Za-z]')
    ANY = ('*', r'.')

@dataclass(slots=True, frozen=True)
class ValidationResult:
    """Immutable validation result"""
    is_valid: bool
    error_message: str = ""
    suggestions: tuple[str, ...] = field(default_factory=tuple)

@dataclass(slots=True)
class AnimationSettings:
    """Animation configuration with defaults"""
    duration: int = 200
    entrance_delay: int = 50
    hover_intensity: float = 0.1
    pulse_scale: float = 1.02

# Utility functions with caching
@lru_cache(maxsize=128)
def get_safe_color(color_name: str, fallback: str = "#000000") -> str:
    """Get theme color safely with fallback"""
    if not THEME_AVAILABLE or theme_manager is None:
        return fallback
    try:
        return theme_manager.get_color(color_name).name()
    except (AttributeError, KeyError):
        return fallback

@contextmanager
def animation_context(widget: QWidget, enabled: bool = True):
    """Context manager for animations"""
    if not enabled or not ENHANCED_ANIMATION_AVAILABLE:
        yield
        return
    
    try:
        yield
    except Exception:
        # Graceful fallback if animation fails
        pass


class FluentMaskedLineEdit(QLineEdit):
    """Fluent Design style masked input field with enhanced animations"""
    
    # Modern signals with proper typing
    validation_failed = Signal(str)  # error_message
    input_completed = Signal(str)    # final_value

    def __init__(self, mask: str = "", placeholder: str = "", parent: QWidget | None = None):
        super().__init__(parent)

        self._mask_pattern = mask
        self._original_placeholder = placeholder
        self._mask_chars = {char.value[0]: char.value[1] for char in MaskCharacter}
        self._animation_settings = AnimationSettings()
        self._current_state = InputState.NORMAL

        self._setup_animations()
        self.setPlaceholderText(placeholder)
        self._setup_style()
        self._setup_validator()

        # Safe theme connection
        if THEME_AVAILABLE and theme_manager is not None:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animations(self):
        """Setup enhanced animation system with fallbacks"""
        if not ENHANCED_ANIMATION_AVAILABLE:
            return
            
        try:
            # Setup state transitions for input field
            self._state_transition = FluentStateTransition(self)

            self._state_transition.addState("normal", {
                "border": f"2px solid {get_safe_color('border', '#cccccc')}",
            })

            self._state_transition.addState("focused", {
                "border": f"2px solid {get_safe_color('primary', '#0078d4')}",
            }, duration=200, easing=FluentTransition.EASE_SMOOTH)

            self._state_transition.addState("error", {
                "border": f"2px solid {get_safe_color('error', '#d13438')}",
            }, duration=150, easing=FluentTransition.EASE_CRISP)

            # Entrance animation
            QTimer.singleShot(self._animation_settings.entrance_delay, self._show_entrance_animation)
        except Exception:
            # Graceful fallback if animation setup fails
            pass

    def _show_entrance_animation(self):
        """Show entrance animation with fallback"""
        with animation_context(self, ENHANCED_ANIMATION_AVAILABLE):
            FluentRevealEffect.fade_in(self, self._animation_settings.duration)

    def focusInEvent(self, event):
        """Enhanced focus in event with animation"""
        super().focusInEvent(event)
        self._state_transition.transitionTo("focused")
        FluentMicroInteraction.hover_glow(self, intensity=0.1)

    def focusOutEvent(self, event):
        """Enhanced focus out event with animation"""
        super().focusOutEvent(event)
        self._state_transition.transitionTo("normal")

    def setInputMask(self, mask: str):
        """Set input mask pattern with animation feedback"""
        self._mask_pattern = mask
        self._setup_validator()
        self._update_placeholder()
        # Add subtle pulse feedback
        FluentMicroInteraction.pulse_animation(self, scale=1.02)

    def _setup_validator(self):
        """Setup input validator based on mask"""
        if not self._mask_pattern:
            return

        # Convert mask to regex
        regex_pattern = ""
        for char in self._mask_pattern:
            if char in self._mask_chars:
                regex_pattern += self._mask_chars[char]
            else:
                regex_pattern += re.escape(char)

        validator = QRegularExpressionValidator(
            QRegularExpression(regex_pattern))
        self.setValidator(validator)

    def _update_placeholder(self):
        """Update placeholder to show mask"""
        if self._mask_pattern:
            placeholder = self._mask_pattern.replace(
                '#', '0').replace('A', 'A').replace('*', 'X')
            self.setPlaceholderText(
                f"{self._original_placeholder} ({placeholder})")
        else:
            self.setPlaceholderText(self._original_placeholder)

    def show_error(self):
        """Show error state with animation"""
        self._state_transition.transitionTo("error")
        FluentMicroInteraction.shake_animation(self, intensity=3)

    def clear_error(self):
        """Clear error state with animation"""
        self._state_transition.transitionTo("normal")

    def _setup_style(self):
        """Setup style"""
        style_sheet = f"""
            FluentMaskedLineEdit {{
                background-color: {get_safe_color('surface', '#ffffff')};
                border: 2px solid {get_safe_color('border', '#cccccc')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: {get_safe_color('text_primary', '#000000')};
                selection-background-color: {get_safe_color('primary', '#0078d4')};
                selection-color: white;
            }}
            FluentMaskedLineEdit:focus {{
                border-color: {get_safe_color('primary', '#0078d4')};
                background-color: {get_safe_color('surface', '#ffffff')};
            }}
            FluentMaskedLineEdit:hover {{
                border-color: {get_safe_color('primary', '#0078d4')};
            }}
            FluentMaskedLineEdit:disabled {{
                background-color: {get_safe_color('background', '#f5f5f5')};
                color: {get_safe_color('text_disabled', '#666666')};
                border-color: {get_safe_color('border', '#cccccc')};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentAutoCompleteEdit(QLineEdit):
    """Fluent Design style auto-complete input field with enhanced animations"""

    item_selected = Signal(str)

    def __init__(self, suggestions: Optional[List[str]] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._suggestions = suggestions or []
        self._filtered_suggestions = []
        self._setup_animations()
        self._setup_completer()
        self._setup_style()

        # Safe theme connection
        if THEME_AVAILABLE and theme_manager is not None:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animations(self):
        """Setup enhanced animation system"""
        # Setup state transitions
        self._state_transition = FluentStateTransition(self)

        self._state_transition.addState("normal", {
            "minimumWidth": 200,
        })

        self._state_transition.addState("active", {
            "minimumWidth": 220,
        }, duration=200, easing=FluentTransition.EASE_SMOOTH)

        # Entrance animation
        QTimer.singleShot(75, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation with staggered effects"""
        entrance_sequence = FluentSequence(self)

        # Slide in from right
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.slide_in(self, 250, "right"))
        entrance_sequence.addPause(100)

        # Subtle scale effect
        entrance_sequence.addCallback(
            lambda: FluentMicroInteraction.pulse_animation(self, scale=1.02))

        entrance_sequence.start()

    def focusInEvent(self, event):
        """Enhanced focus in event"""
        super().focusInEvent(event)
        self._state_transition.transitionTo("active")

        # Animate completer popup if available
        if self.completer() and self.completer().popup():
            FluentRevealEffect.fade_in(self.completer().popup(), 150)

    def focusOutEvent(self, event):
        """Enhanced focus out event"""
        super().focusOutEvent(event)
        self._state_transition.transitionTo("normal")

    def setSuggestions(self, suggestions: List[str]):
        """Set suggestion list with animation feedback"""
        self._suggestions = suggestions
        self._setup_completer()
        # Add subtle feedback for suggestion update
        FluentMicroInteraction.pulse_animation(self, scale=1.01)

    def addSuggestion(self, suggestion: str):
        """Add a suggestion with animation"""
        if suggestion not in self._suggestions:
            self._suggestions.append(suggestion)
            self._setup_completer()
            # Subtle pulse to indicate addition
            FluentMicroInteraction.pulse_animation(self, scale=1.01)

    def _setup_completer(self):
        """Setup auto-completer with enhanced popup styling"""
        if self._suggestions:
            model = QStringListModel(self._suggestions)
            completer = QCompleter(model)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)

            # Style the completer popup with animations
            popup = completer.popup()
            popup.setStyleSheet(f"""
                QListView {{
                    background-color: {get_safe_color('surface', '#ffffff')};
                    border: 1px solid {get_safe_color('border', '#cccccc')};
                    border-radius: 6px;
                    selection-background-color: {get_safe_color('primary', '#0078d4')};
                    selection-color: white;
                    font-size: 14px;
                    padding: 4px;
                }}
                QListView::item {{
                    padding: 6px 12px;
                    border-radius: 4px;
                }}
                QListView::item:hover {{
                    background-color: {get_safe_color('accent_light', '#f0f0f0')};
                }}
            """)

            # Add selection animation
            completer.activated.connect(self._on_item_selected)
            self.setCompleter(completer)

    def _on_item_selected(self, text: str):
        """Handle item selection with animation"""
        # Pulse animation for selection feedback
        FluentMicroInteraction.pulse_animation(self, scale=1.03)
        self.item_selected.emit(text)

    def _setup_style(self):
        """Setup style"""
        style_sheet = f"""
            FluentAutoCompleteEdit {{
                background-color: {get_safe_color('surface', '#ffffff')};
                border: 2px solid {get_safe_color('border', '#cccccc')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: {get_safe_color('text_primary', '#000000')};
                selection-background-color: {get_safe_color('primary', '#0078d4')};
                selection-color: white;
            }}
            FluentAutoCompleteEdit:focus {{
                border-color: {get_safe_color('primary', '#0078d4')};
            }}
            FluentAutoCompleteEdit:hover {{
                border-color: {get_safe_color('primary', '#0078d4')};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
        self._setup_completer()


class FluentRichTextEditor(QWidget):
    """Fluent Design style rich text editor with enhanced animations"""

    text_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._setup_animations()
        self._setup_ui()
        self._setup_style()

        # Safe theme connection
        if THEME_AVAILABLE and theme_manager is not None:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animations(self):
        """Setup enhanced animation system"""
        # Setup state transitions
        self._state_transition = FluentStateTransition(self)

        self._state_transition.addState("normal", {
            "minimumHeight": 200,
        })

        self._state_transition.addState("expanded", {
            "minimumHeight": 220,
        }, duration=300, easing=FluentTransition.EASE_SPRING)

        # Toolbar button animations
        self._button_animations = {}

        # Entrance animation
        QTimer.singleShot(100, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation with staggered toolbar buttons"""
        entrance_sequence = FluentSequence(self)

        # Fade in the editor first
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self, 300))
        entrance_sequence.addPause(100)

        # Animate toolbar buttons with stagger
        entrance_sequence.addCallback(
            lambda: self._animate_toolbar_buttons())

        entrance_sequence.start()

    def _animate_toolbar_buttons(self):
        """Animate toolbar buttons with staggered reveals"""
        buttons = [self.bold_btn, self.italic_btn,
                   self.underline_btn, self.font_size_combo]

        for i, button in enumerate(buttons):
            delay = i * 50
            QTimer.singleShot(
                delay, lambda b=button: FluentRevealEffect.slide_in(b, 150, "up"))

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(40)
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(8, 4, 8, 4)
        toolbar_layout.setSpacing(4)

        # Bold button with enhanced interaction
        self.bold_btn = QPushButton("B")
        self.bold_btn.setFixedSize(28, 28)
        self.bold_btn.setCheckable(True)
        self.bold_btn.setFont(QFont("", 10, QFont.Weight.Bold))
        self.bold_btn.clicked.connect(self._toggle_bold)
        # Add micro-interaction
        self.bold_btn.mousePressEvent = lambda e: self._handle_button_press(
            self.bold_btn, e, self._toggle_bold_original)

        # Italic button with enhanced interaction
        self.italic_btn = QPushButton("I")
        self.italic_btn.setFixedSize(28, 28)
        self.italic_btn.setCheckable(True)
        self.italic_btn.setFont(QFont("", 10, QFont.Weight.Normal))
        self.italic_btn.clicked.connect(self._toggle_italic)
        self.italic_btn.mousePressEvent = lambda e: self._handle_button_press(
            self.italic_btn, e, self._toggle_italic_original)

        # Underline button with enhanced interaction
        self.underline_btn = QPushButton("U")
        self.underline_btn.setFixedSize(28, 28)
        self.underline_btn.setCheckable(True)
        self.underline_btn.setFont(QFont("", 10, QFont.Weight.Normal))
        self.underline_btn.clicked.connect(self._toggle_underline)
        self.underline_btn.mousePressEvent = lambda e: self._handle_button_press(
            self.underline_btn, e, self._toggle_underline_original)

        # Store original methods for proper chaining
        self._toggle_bold_original = self.bold_btn.mousePressEvent
        self._toggle_italic_original = self.italic_btn.mousePressEvent
        self._toggle_underline_original = self.underline_btn.mousePressEvent

        # Font size combo with enhanced styling
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(
            ["8", "10", "12", "14", "16", "18", "20", "24"])
        self.font_size_combo.setCurrentText("14")
        self.font_size_combo.currentTextChanged.connect(self._change_font_size)

        toolbar_layout.addWidget(self.bold_btn)
        toolbar_layout.addWidget(self.italic_btn)
        toolbar_layout.addWidget(self.underline_btn)
        toolbar_layout.addWidget(QFrame())  # Separator
        toolbar_layout.addWidget(QLabel("Size:"))
        toolbar_layout.addWidget(self.font_size_combo)
        toolbar_layout.addStretch()

        # Text editor with enhanced focus handling
        self.text_edit = QTextEdit()
        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.focusInEvent = self._text_focus_in
        self.text_edit.focusOutEvent = self._text_focus_out

        layout.addWidget(self.toolbar)
        layout.addWidget(self.text_edit)

    def _handle_button_press(self, button, event, original_handler):
        """Handle button press with micro-interaction"""
        # Call original handler
        original_handler(event)
        # Add micro-interaction
        FluentMicroInteraction.button_press(button, scale=0.90)

    def _text_focus_in(self, event):
        """Enhanced text editor focus in"""
        QTextEdit.focusInEvent(self.text_edit, event)
        self._state_transition.transitionTo("expanded")

    def _text_focus_out(self, event):
        """Enhanced text editor focus out"""
        QTextEdit.focusOutEvent(self.text_edit, event)
        self._state_transition.transitionTo("normal")

    def _toggle_bold(self):
        """Toggle bold formatting with animation"""
        if self.bold_btn.isChecked():
            self.text_edit.setFontWeight(QFont.Weight.Bold)
        else:
            self.text_edit.setFontWeight(QFont.Weight.Normal)

        # Add visual feedback
        FluentMicroInteraction.pulse_animation(self.bold_btn, scale=1.1)

    def _toggle_italic(self):
        """Toggle italic formatting with animation"""
        self.text_edit.setFontItalic(self.italic_btn.isChecked())
        FluentMicroInteraction.pulse_animation(self.italic_btn, scale=1.1)

    def _toggle_underline(self):
        """Toggle underline formatting with animation"""
        self.text_edit.setFontUnderline(self.underline_btn.isChecked())
        FluentMicroInteraction.pulse_animation(self.underline_btn, scale=1.1)

    def _change_font_size(self, size_text: str):
        """Change font size with animation"""
        try:
            size = int(size_text)
            self.text_edit.setFontPointSize(size)
            # Add subtle scale feedback
            FluentMicroInteraction.scale_animation(
                self.font_size_combo, scale=1.05)
        except ValueError:
            pass

    def _on_text_changed(self):
        """Handle text change"""
        self.text_changed.emit(self.text_edit.toHtml())

    def getText(self) -> str:
        """Get plain text"""
        return self.text_edit.toPlainText()

    def getHtml(self) -> str:
        """Get HTML text"""
        return self.text_edit.toHtml()

    def setText(self, text: str):
        """Set plain text with animation"""
        self.text_edit.setPlainText(text)
        FluentMicroInteraction.pulse_animation(self.text_edit, scale=1.01)

    def setHtml(self, html: str):
        """Set HTML text with animation"""
        self.text_edit.setHtml(html)
        FluentMicroInteraction.pulse_animation(self.text_edit, scale=1.01)

    def _setup_style(self):
        """Setup style"""
        # Toolbar style
        toolbar_style = f"""
            QFrame {{
                background-color: {get_safe_color('surface', '#ffffff')};
                border-bottom: 1px solid {get_safe_color('border', '#cccccc')};
            }}
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                color: {get_safe_color('text_primary', '#000000')};
            }}
            QPushButton:hover {{
                background-color: {get_safe_color('accent_light', '#f0f0f0')};
                border-color: {get_safe_color('border', '#cccccc')};
            }}
            QPushButton:checked {{
                background-color: {get_safe_color('primary', '#0078d4')};
                color: white;
            }}
            QComboBox {{
                background-color: {get_safe_color('surface', '#ffffff')};
                border: 1px solid {get_safe_color('border', '#cccccc')};
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 60px;
            }}
            QLabel {{
                color: {get_safe_color('text_secondary', '#666666')};
                font-size: 12px;
            }}
        """

        # Text editor style
        editor_style = f"""
            QTextEdit {{
                background-color: {get_safe_color('surface', '#ffffff')};
                border: 1px solid {get_safe_color('border', '#cccccc')};
                border-top: none;
                color: {get_safe_color('text_primary', '#000000')};
                font-size: 14px;
                font-family: "Segoe UI", sans-serif;
                selection-background-color: {get_safe_color('primary', '#0078d4')};
                selection-color: white;
            }}
            QTextEdit:focus {{
                border-color: {get_safe_color('primary', '#0078d4')};
            }}
        """

        self.toolbar.setStyleSheet(toolbar_style)
        self.text_edit.setStyleSheet(editor_style)

        # Widget container style
        self.setStyleSheet(f"""
            FluentRichTextEditor {{
                background-color: {get_safe_color('surface', '#ffffff')};
                border: 1px solid {get_safe_color('border', '#cccccc')};
                border-radius: 6px;
            }}
        """)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentDateTimePicker(QWidget):
    """Fluent Design style date/time picker with enhanced animations"""

    date_changed = Signal(QDate)
    time_changed = Signal(QTime)
    datetime_changed = Signal(QDateTime)

    class PickerMode:
        DATE_ONLY = "date"
        TIME_ONLY = "time"
        DATETIME = "datetime"

    def __init__(self, mode: str = PickerMode.DATETIME, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._mode = mode
        self._setup_animations()
        self._setup_ui()
        self._setup_style()

        # Safe theme connection
        if THEME_AVAILABLE and theme_manager is not None:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animations(self):
        """Setup enhanced animation system"""
        # Setup state transitions
        self._state_transition = FluentStateTransition(self)

        self._state_transition.addState("normal", {
            "minimumHeight": 35,
        })

        self._state_transition.addState("expanded", {
            "minimumHeight": 40,
        }, duration=200, easing=FluentTransition.EASE_SMOOTH)

        # Entrance animation
        QTimer.singleShot(125, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation with staggered components"""
        entrance_sequence = FluentSequence(self)

        # Fade in the container
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self, 250))
        entrance_sequence.addPause(50)

        # Animate individual components based on mode
        if hasattr(self, 'date_edit'):
            entrance_sequence.addCallback(
                lambda: FluentRevealEffect.slide_in(self.date_edit, 150, "left"))

        if hasattr(self, 'time_edit'):
            entrance_sequence.addCallback(
                lambda: FluentRevealEffect.slide_in(self.time_edit, 150, "right"))

        entrance_sequence.start()

    def _setup_ui(self):
        """Setup UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        if self._mode in [self.PickerMode.DATE_ONLY, self.PickerMode.DATETIME]:
            self.date_edit = QDateEdit()
            self.date_edit.setDate(QDate.currentDate())
            self.date_edit.setCalendarPopup(True)
            self.date_edit.dateChanged.connect(self._on_date_changed)

            # Add enhanced interaction for date edit
            self.date_edit.focusInEvent = lambda e: self._date_focus_in(e)
            self.date_edit.focusOutEvent = lambda e: self._date_focus_out(e)

            layout.addWidget(self.date_edit)

        if self._mode in [self.PickerMode.TIME_ONLY, self.PickerMode.DATETIME]:
            self.time_edit = QTimeEdit()
            self.time_edit.setTime(QTime.currentTime())
            self.time_edit.timeChanged.connect(self._on_time_changed)

            # Add enhanced interaction for time edit
            self.time_edit.focusInEvent = lambda e: self._time_focus_in(e)
            self.time_edit.focusOutEvent = lambda e: self._time_focus_out(e)

            layout.addWidget(self.time_edit)

    def _date_focus_in(self, event):
        """Enhanced date edit focus in"""
        QDateEdit.focusInEvent(self.date_edit, event)
        self._state_transition.transitionTo("expanded")
        FluentMicroInteraction.hover_glow(self.date_edit, intensity=0.1)

    def _date_focus_out(self, event):
        """Enhanced date edit focus out"""
        QDateEdit.focusOutEvent(self.date_edit, event)
        self._state_transition.transitionTo("normal")

    def _time_focus_in(self, event):
        """Enhanced time edit focus in"""
        QTimeEdit.focusInEvent(self.time_edit, event)
        self._state_transition.transitionTo("expanded")
        FluentMicroInteraction.hover_glow(self.time_edit, intensity=0.1)

    def _time_focus_out(self, event):
        """Enhanced time edit focus out"""
        QTimeEdit.focusOutEvent(self.time_edit, event)
        self._state_transition.transitionTo("normal")

    def _on_date_changed(self, date: QDate):
        """Handle date change with animation"""
        # Add pulse feedback for date change
        if hasattr(self, 'date_edit'):
            FluentMicroInteraction.pulse_animation(self.date_edit, scale=1.02)

        self.date_changed.emit(date)
        if hasattr(self, 'time_edit'):
            datetime = QDateTime(date, self.time_edit.time())
            self.datetime_changed.emit(datetime)

    def _on_time_changed(self, time: QTime):
        """Handle time change with animation"""
        # Add pulse feedback for time change
        if hasattr(self, 'time_edit'):
            FluentMicroInteraction.pulse_animation(self.time_edit, scale=1.02)

        self.time_changed.emit(time)
        if hasattr(self, 'date_edit'):
            datetime = QDateTime(self.date_edit.date(), time)
            self.datetime_changed.emit(datetime)

    def getDate(self) -> QDate:
        """Get selected date"""
        if hasattr(self, 'date_edit'):
            return self.date_edit.date()
        return QDate()

    def getTime(self) -> QTime:
        """Get selected time"""
        if hasattr(self, 'time_edit'):
            return self.time_edit.time()
        return QTime()

    def getDateTime(self) -> QDateTime:
        """Get selected datetime"""
        if hasattr(self, 'date_edit') and hasattr(self, 'time_edit'):
            return QDateTime(self.date_edit.date(), self.time_edit.time())
        elif hasattr(self, 'date_edit'):
            return QDateTime(self.date_edit.date(), QTime())
        elif hasattr(self, 'time_edit'):
            return QDateTime(QDate(), self.time_edit.time())
        return QDateTime()

    def setDate(self, date: QDate):
        """Set date with animation"""
        if hasattr(self, 'date_edit'):
            self.date_edit.setDate(date)
            FluentMicroInteraction.pulse_animation(self.date_edit, scale=1.02)

    def setTime(self, time: QTime):
        """Set time with animation"""
        if hasattr(self, 'time_edit'):
            self.time_edit.setTime(time)
            FluentMicroInteraction.pulse_animation(self.time_edit, scale=1.02)

    def setDateTime(self, datetime: QDateTime):
        """Set datetime with coordinated animation"""
        entrance_sequence = FluentSequence(self)

        if hasattr(self, 'date_edit'):
            entrance_sequence.addCallback(
                lambda: (self.date_edit.setDate(datetime.date()),
                         FluentMicroInteraction.pulse_animation(self.date_edit, scale=1.02)))

        if hasattr(self, 'time_edit'):
            entrance_sequence.addPause(50)
            entrance_sequence.addCallback(
                lambda: (self.time_edit.setTime(datetime.time()),
                         FluentMicroInteraction.pulse_animation(self.time_edit, scale=1.02)))

        entrance_sequence.start()

    def _setup_style(self):
        """Setup style"""
        style_sheet = f"""
            QDateEdit, QTimeEdit {{
                background-color: {get_safe_color('surface', '#ffffff')};
                border: 2px solid {get_safe_color('border', '#cccccc')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: {get_safe_color('text_primary', '#000000')};
                min-width: 120px;
            }}
            QDateEdit:focus, QTimeEdit:focus {{
                border-color: {get_safe_color('primary', '#0078d4')};
            }}
            QDateEdit:hover, QTimeEdit:hover {{
                border-color: {get_safe_color('primary', '#0078d4')};
            }}
            QDateEdit::drop-down, QTimeEdit::drop-down {{
                border: none;
                background-color: transparent;
                width: 20px;
            }}
            QDateEdit::down-arrow, QTimeEdit::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {get_safe_color('text_secondary', '#666666')};
                margin-right: 8px;
            }}
            QCalendarWidget {{
                background-color: {get_safe_color('surface', '#ffffff')};
                border: 1px solid {get_safe_color('border', '#cccccc')};
                border-radius: 8px;
            }}
            QCalendarWidget QTableView {{
                background-color: {get_safe_color('surface', '#ffffff')};
                selection-background-color: {get_safe_color('primary', '#0078d4')};
                selection-color: white;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentSlider(QWidget):
    """Fluent Design style slider with value display and enhanced animations"""

    value_changed = Signal(int)

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._orientation = orientation
        self._show_value = True
        self._show_ticks = True

        self._setup_animations()
        self._setup_ui()
        self._setup_style()

        # Safe theme connection
        if THEME_AVAILABLE and theme_manager is not None:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animations(self):
        """Setup enhanced animation system"""
        # Setup state transitions
        self._state_transition = FluentStateTransition(self)

        if self._orientation == Qt.Orientation.Horizontal:
            self._state_transition.addState("normal", {
                "minimumHeight": 60,
            })
            self._state_transition.addState("active", {
                "minimumHeight": 70,
            }, duration=200, easing=FluentTransition.EASE_SMOOTH)
        else:
            self._state_transition.addState("normal", {
                "minimumWidth": 60,
            })
            self._state_transition.addState("active", {
                "minimumWidth": 70,
            }, duration=200, easing=FluentTransition.EASE_SMOOTH)

        # Entrance animation
        QTimer.singleShot(150, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation"""
        entrance_sequence = FluentSequence(self)

        # Slide in the slider
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.slide_in(self.slider, 200, "up"))
        entrance_sequence.addPause(100)

        # Fade in the value label
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self.value_label, 150))

        entrance_sequence.start()

    def _setup_ui(self):
        """Setup UI"""
        if self._orientation == Qt.Orientation.Horizontal:
            layout = QVBoxLayout(self)
        else:
            layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.slider = QSlider(self._orientation)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self._on_value_changed)

        # Add enhanced interaction for slider
        self.slider.mousePressEvent = lambda e: self._slider_press(e)
        self.slider.mouseReleaseEvent = lambda e: self._slider_release(e)

        self.value_label = QLabel("50")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setMinimumWidth(40)

        if self._orientation == Qt.Orientation.Horizontal:
            layout.addWidget(self.slider)
            layout.addWidget(self.value_label)
        else:
            layout.addWidget(self.value_label)
            layout.addWidget(self.slider)

    def _slider_press(self, event):
        """Enhanced slider press event"""
        QSlider.mousePressEvent(self.slider, event)
        self._state_transition.transitionTo("active")
        FluentMicroInteraction.button_press(self.slider, scale=0.98)

    def _slider_release(self, event):
        """Enhanced slider release event"""
        QSlider.mouseReleaseEvent(self.slider, event)
        self._state_transition.transitionTo("normal")

    def _on_value_changed(self, value: int):
        """Handle value change with animation"""
        if self._show_value:
            # Animate value label update
            FluentMicroInteraction.pulse_animation(self.value_label, scale=1.1)
            self.value_label.setText(str(value))

        self.value_changed.emit(value)

    def setValue(self, value: int):
        """Set slider value with animation"""
        self.slider.setValue(value)
        FluentMicroInteraction.pulse_animation(self.slider, scale=1.02)

    def setRange(self, minimum: int, maximum: int):
        """Set value range with animation feedback"""
        self.slider.setRange(minimum, maximum)
        FluentMicroInteraction.scale_animation(self.slider, scale=1.01)

    def setShowValue(self, show: bool):
        """Set value display visibility with animation"""
        self._show_value = show
        if show:
            FluentRevealEffect.fade_in(self.value_label, 200)
        else:
            # Could use fade_out if available
            FluentRevealEffect.fade_in(self.value_label, 200)
        self.value_label.setVisible(show)

    def value(self) -> int:
        """Get current value"""
        return self.slider.value()

    def _setup_style(self):
        """Setup style"""
        style_sheet = f"""
            QSlider::groove:horizontal {{
                background-color: {get_safe_color('border', '#cccccc')};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background-color: {get_safe_color('primary', '#0078d4')};
                border: 2px solid white;
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: -7px 0;
            }}
            QSlider::handle:horizontal:hover {{
                background-color: {get_safe_color('primary', '#0078d4')};
            }}
            QSlider::handle:horizontal:pressed {{
                background-color: {get_safe_color('primary', '#0078d4')};
            }}
            QSlider::sub-page:horizontal {{
                background-color: {get_safe_color('primary', '#0078d4')};
                border-radius: 3px;
            }}
            QSlider::groove:vertical {{
                background-color: {get_safe_color('border', '#cccccc')};
                width: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:vertical {{
                background-color: {get_safe_color('primary', '#0078d4')};
                border: 2px solid white;
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: 0 -7px;
            }}
            QSlider::sub-page:vertical {{
                background-color: {get_safe_color('primary', '#0078d4')};
                border-radius: 3px;
            }}
            QLabel {{
                color: {get_safe_color('text_primary', '#000000')};
                font-size: 12px;
                font-weight: 600;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentFileSelector(QWidget):
    """Fluent Design style file selector with enhanced animations"""

    file_selected = Signal(str)  # file_path
    files_selected = Signal(list)  # file_paths

    def __init__(self, multi_select: bool = False, file_filter: str = "All Files (*)",
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._multi_select = multi_select
        self._file_filter = file_filter
        self._selected_files = []

        self._setup_animations()
        self._setup_ui()
        self._setup_style()

        # Safe theme connection
        if THEME_AVAILABLE and theme_manager is not None:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_animations(self):
        """Setup enhanced animation system"""
        # Setup state transitions
        self._state_transition = FluentStateTransition(self)

        self._state_transition.addState("normal", {
            "minimumHeight": 40,
        })

        self._state_transition.addState("active", {
            "minimumHeight": 45,
        }, duration=200, easing=FluentTransition.EASE_SMOOTH)

        # Entrance animation
        QTimer.singleShot(175, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation with staggered components"""
        entrance_sequence = FluentSequence(self)

        # Slide in file display
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.slide_in(self.file_display, 200, "left"))
        entrance_sequence.addPause(50)

        # Slide in browse button
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.slide_in(self.browse_btn, 150, "up"))
        entrance_sequence.addPause(50)

        # Slide in clear button
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.slide_in(self.clear_btn, 150, "down"))

        entrance_sequence.start()

    def _setup_ui(self):
        """Setup UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.file_display = QLineEdit()
        self.file_display.setReadOnly(True)
        self.file_display.setPlaceholderText("No file selected")

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.clicked.connect(self._browse_files)
        # Add micro-interaction
        self.browse_btn.mousePressEvent = lambda e: self._handle_button_press(
            self.browse_btn, e)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedWidth(60)
        self.clear_btn.clicked.connect(self._clear_selection)
        self.clear_btn.setEnabled(False)
        # Add micro-interaction
        self.clear_btn.mousePressEvent = lambda e: self._handle_button_press(
            self.clear_btn, e)

        layout.addWidget(self.file_display)
        layout.addWidget(self.browse_btn)
        layout.addWidget(self.clear_btn)

    def _handle_button_press(self, button, event):
        """Handle button press with micro-interaction"""
        QPushButton.mousePressEvent(button, event)
        FluentMicroInteraction.button_press(button, scale=0.92)

    def _browse_files(self):
        """Browse for files with animation feedback"""
        self._state_transition.transitionTo("active")

        if self._multi_select:
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Files", "", self._file_filter)
            if files:
                self._selected_files = files
                self.file_display.setText(f"{len(files)} files selected")
                self.clear_btn.setEnabled(True)

                # Animation feedback
                FluentMicroInteraction.pulse_animation(
                    self.file_display, scale=1.02)
                FluentRevealEffect.fade_in(self.clear_btn, 150)

                self.files_selected.emit(files)
        else:
            file, _ = QFileDialog.getOpenFileName(
                self, "Select File", "", self._file_filter)
            if file:
                self._selected_files = [file]
                self.file_display.setText(
                    file.split('/')[-1])  # Show filename only
                self.clear_btn.setEnabled(True)

                # Animation feedback
                FluentMicroInteraction.pulse_animation(
                    self.file_display, scale=1.02)
                FluentRevealEffect.fade_in(self.clear_btn, 150)

                self.file_selected.emit(file)

        QTimer.singleShot(
            300, lambda: self._state_transition.transitionTo("normal"))

    def _clear_selection(self):
        """Clear file selection with animation"""
        # Animate clearing
        clear_sequence = FluentSequence(self)

        # Pulse the display field
        clear_sequence.addCallback(
            lambda: FluentMicroInteraction.pulse_animation(self.file_display, scale=0.95))
        clear_sequence.addPause(100)

        # Clear and reset
        clear_sequence.addCallback(self._perform_clear)

        clear_sequence.start()

    def _perform_clear(self):
        """Perform the actual clearing"""
        self._selected_files = []
        self.file_display.clear()
        self.file_display.setPlaceholderText("No file selected")
        self.clear_btn.setEnabled(False)

    def getSelectedFiles(self) -> List[str]:
        """Get selected file paths"""
        return self._selected_files.copy()

    def getSelectedFile(self) -> str:
        """Get first selected file path"""
        return self._selected_files[0] if self._selected_files else ""

    def _setup_style(self):
        """Setup style"""
        style_sheet = f"""
            QLineEdit {{
                background-color: {get_safe_color('surface', '#ffffff')};
                border: 2px solid {get_safe_color('border', '#cccccc')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: {get_safe_color('text_primary', '#000000')};
            }}
            QPushButton {{
                background-color: {get_safe_color('primary', '#0078d4')};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {get_safe_color('primary', '#005a9e')};
            }}
            QPushButton:pressed {{
                background-color: {get_safe_color('primary', '#004578')};
            }}
            QPushButton:disabled {{
                background-color: {get_safe_color('border', '#cccccc')};
                color: {get_safe_color('text_disabled', '#666666')};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
