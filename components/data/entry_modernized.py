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
from typing import Protocol, TypeVar, Generic, TypeAlias, Final, Any, Callable
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
        FluentTransition, FluentMicroInteraction,
        FluentRevealEffect, FluentSequence, FluentStateTransition
    )
    ENHANCED_ANIMATION_AVAILABLE = True
except ImportError:
    ENHANCED_ANIMATION_AVAILABLE = False
    # Fallback classes
    class AnimationProxy:
        @staticmethod
        def fade_in(widget, duration=200): pass
        @staticmethod 
        def hover_glow(widget, intensity=0.1): pass
        @staticmethod
        def pulse_animation(widget, scale=1.02): pass
        @staticmethod
        def slide_in(widget, duration=250, direction="right"): pass
        
    FluentRevealEffect = AnimationProxy()
    FluentMicroInteraction = AnimationProxy()
    
    class StateTransitionProxy:
        def __init__(self, widget): pass
        def addState(self, name, style, duration=200, easing=None): pass
        def transitionTo(self, state): pass
        
    FluentStateTransition = StateTransitionProxy
    
    class TransitionProxy:
        EASE_SMOOTH = "ease_smooth"
        EASE_CRISP = "ease_crisp"
        
    FluentTransition = TransitionProxy()
    FluentSequence = lambda widget: None

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
            with suppress(AttributeError):
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
            })

            self._state_transition.addState("error", {
                "border": f"2px solid {get_safe_color('error', '#d13438')}",
            })

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
        self._current_state = InputState.FOCUSED
        
        with animation_context(self, ENHANCED_ANIMATION_AVAILABLE):
            if hasattr(self, '_state_transition'):
                self._state_transition.transitionTo("focused")
            FluentMicroInteraction.hover_glow(self, intensity=self._animation_settings.hover_intensity)

    def focusOutEvent(self, event):
        """Enhanced focus out event with animation"""
        super().focusOutEvent(event)
        self._current_state = InputState.NORMAL
        
        with animation_context(self, ENHANCED_ANIMATION_AVAILABLE):
            if hasattr(self, '_state_transition'):
                self._state_transition.transitionTo("normal")

    def setInputMask(self, mask: str):
        """Set input mask pattern with animation feedback"""
        self._mask_pattern = mask
        self._setup_validator()
        self._update_placeholder()
        
        # Add subtle pulse feedback
        with animation_context(self, ENHANCED_ANIMATION_AVAILABLE):
            FluentMicroInteraction.pulse_animation(self, scale=self._animation_settings.pulse_scale)

    def _setup_validator(self):
        """Setup input validator based on mask"""
        if not self._mask_pattern:
            return

        # Convert mask to regex using modern pattern matching
        regex_pattern = ""
        for char in self._mask_pattern:
            match char:
                case c if c in self._mask_chars:
                    regex_pattern += self._mask_chars[c]
                case _:
                    regex_pattern += re.escape(char)

        validator = QRegularExpressionValidator(QRegularExpression(regex_pattern))
        self.setValidator(validator)

    def _update_placeholder(self):
        """Update placeholder text based on mask"""
        if self._mask_pattern:
            placeholder = self._mask_pattern.replace('#', '_').replace('A', '_').replace('*', '_')
            self.setPlaceholderText(f"{self._original_placeholder} ({placeholder})")
        else:
            self.setPlaceholderText(self._original_placeholder)

    def _show_validation_error(self, message: str):
        """Show validation error with animation"""
        self._current_state = InputState.ERROR
        self.validation_failed.emit(message)
        
        with animation_context(self, ENHANCED_ANIMATION_AVAILABLE):
            if hasattr(self, '_state_transition'):
                self._state_transition.transitionTo("error")

    def _setup_style(self):
        """Setup component styling with theme integration"""
        # Get theme colors safely with fallbacks
        background_color = get_safe_color('surface', '#ffffff')
        border_color = get_safe_color('border', '#cccccc')
        text_color = get_safe_color('text_primary', '#000000')
        primary_color = get_safe_color('primary', '#0078d4')
        disabled_bg = get_safe_color('background', '#f3f2f1')
        disabled_text = get_safe_color('text_disabled', '#8a8886')
        
        style = f"""
            QLineEdit {{
                background-color: {background_color};
                border: 2px solid {border_color};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                color: {text_color};
                selection-background-color: {primary_color};
            }}
            
            QLineEdit:focus {{
                border-color: {primary_color};
                background-color: {background_color};
            }}
            
            QLineEdit:hover:!focus {{
                border-color: {primary_color};
            }}
            
            QLineEdit:disabled {{
                background-color: {disabled_bg};
                color: {disabled_text};
                border-color: {border_color};
            }}
        """
        self.setStyleSheet(style)

    @Slot()
    def _on_theme_changed(self):
        """Handle theme changes"""
        self._setup_style()


class FluentAutoCompleteLineEdit(QLineEdit):
    """Enhanced auto-complete line edit with modern features"""
    
    # Type-safe signals
    suggestion_selected = Signal(str)
    suggestions_updated = Signal(tuple)  # tuple of suggestions

    def __init__(self, suggestions: Sequence[str] | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        
        self._suggestions = tuple(suggestions) if suggestions else ()
        self._completer = QCompleter(list(self._suggestions), self)
        self._animation_settings = AnimationSettings()
        
        self._setup_completer()
        self._setup_style()
        self._setup_animations()
        
        # Safe theme connection
        if THEME_AVAILABLE and theme_manager is not None:
            with suppress(AttributeError):
                theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_completer(self):
        """Setup the auto-completer with modern settings"""
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setMaxVisibleItems(10)
        
        self.setCompleter(self._completer)
        
        # Connect signals
        if self._completer.activated:
            self._completer.activated.connect(self._on_suggestion_selected)

    def _setup_animations(self):
        """Setup animation effects"""
        with animation_context(self, ENHANCED_ANIMATION_AVAILABLE):
            QTimer.singleShot(self._animation_settings.entrance_delay, 
                             lambda: FluentRevealEffect.fade_in(self, self._animation_settings.duration))

    def setSuggestions(self, suggestions: Sequence[str]):
        """Update suggestions with type safety"""
        self._suggestions = tuple(suggestions)
        model = QStringListModel(list(self._suggestions))
        self._completer.setModel(model)
        self.suggestions_updated.emit(self._suggestions)

    @Slot(str)
    def _on_suggestion_selected(self, text: str):
        """Handle suggestion selection"""
        self.suggestion_selected.emit(text)
        with animation_context(self, ENHANCED_ANIMATION_AVAILABLE):
            FluentMicroInteraction.pulse_animation(self, scale=self._animation_settings.pulse_scale)

    def _setup_style(self):
        """Setup styling with theme integration"""
        # Get colors safely
        surface_color = get_safe_color('surface', '#ffffff')
        border_color = get_safe_color('border', '#cccccc')
        
        popup_style = f"""
            QListView {{
                background-color: {surface_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                outline: none;
                selection-background-color: {get_safe_color('primary', '#0078d4')};
            }}
        """
        
        if self._completer.popup():
            self._completer.popup().setStyleSheet(popup_style)

    @Slot()
    def _on_theme_changed(self):
        """Handle theme changes"""
        self._setup_style()


class FluentRichTextEditor(QTextEdit):
    """Rich text editor with Fluent Design styling and modern features"""
    
    # Type-safe signals
    text_formatted = Signal(str)  # formatted_text
    selection_changed = Signal(str, str)  # selected_text, format_info

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        
        self._animation_settings = AnimationSettings()
        self._current_state = InputState.NORMAL
        
        self._setup_editor()
        self._setup_style()
        self._setup_animations()
        
        # Safe theme connection
        if THEME_AVAILABLE and theme_manager is not None:
            with suppress(AttributeError):
                theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_editor(self):
        """Setup the text editor with modern settings"""
        self.setAcceptRichText(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.setTabChangesFocus(False)
        
        # Connect signals
        self.selectionChanged.connect(self._on_selection_changed)
        self.textChanged.connect(self._on_text_changed)

    def _setup_animations(self):
        """Setup animation effects"""
        with animation_context(self, ENHANCED_ANIMATION_AVAILABLE):
            QTimer.singleShot(self._animation_settings.entrance_delay,
                             lambda: FluentRevealEffect.fade_in(self, self._animation_settings.duration))

    def _setup_style(self):
        """Setup styling with theme integration"""
        background_color = get_safe_color('surface', '#ffffff')
        border_color = get_safe_color('border', '#cccccc')
        text_color = get_safe_color('text_primary', '#000000')
        primary_color = get_safe_color('primary', '#0078d4')
        
        style = f"""
            QTextEdit {{
                background-color: {background_color};
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                color: {text_color};
                selection-background-color: {primary_color};
            }}
            
            QTextEdit:focus {{
                border-color: {primary_color};
            }}
        """
        self.setStyleSheet(style)

    @Slot()
    def _on_selection_changed(self):
        """Handle selection changes"""
        cursor = self.textCursor()
        selected_text = cursor.selectedText()
        
        # Get format information (simplified)
        format_info = "plain"
        if cursor.charFormat().fontWeight() > QFont.Weight.Normal:
            format_info = "bold"
        
        self.selection_changed.emit(selected_text, format_info)

    @Slot()
    def _on_text_changed(self):
        """Handle text changes"""
        self.text_formatted.emit(self.toHtml())

    @Slot()
    def _on_theme_changed(self):
        """Handle theme changes"""
        self._setup_style()


# Simplified factory function for creating entry components
def create_entry_component(component_type: str, **kwargs) -> QWidget:
    """Factory function for creating entry components"""
    match component_type.lower():
        case "masked":
            return FluentMaskedLineEdit(**kwargs)
        case "autocomplete":
            return FluentAutoCompleteLineEdit(**kwargs)
        case "richtext":
            return FluentRichTextEditor(**kwargs)
        case _:
            # Default to regular line edit
            return QLineEdit(**kwargs)


# Example usage
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QMainWindow

    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Modern Entry Components Demo")
    window.setGeometry(100, 100, 600, 400)
    
    # Create container widget
    container = QWidget()
    layout = QVBoxLayout(container)
    
    # Add sample components
    masked_input = FluentMaskedLineEdit("###-##-####", "SSN", window)
    layout.addWidget(QLabel("Masked Input (SSN):"))
    layout.addWidget(masked_input)
    
    autocomplete = FluentAutoCompleteLineEdit(
        ["Apple", "Banana", "Cherry", "Date", "Elderberry"], window
    )
    layout.addWidget(QLabel("Auto-complete:"))
    layout.addWidget(autocomplete)
    
    rich_editor = FluentRichTextEditor(window)
    layout.addWidget(QLabel("Rich Text Editor:"))
    layout.addWidget(rich_editor)
    
    window.setCentralWidget(container)
    window.show()
    
    sys.exit(app.exec())
