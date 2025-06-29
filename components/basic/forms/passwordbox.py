"""
Fluent Design Password Box Component
Enhanced password input with reveal functionality
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, 
                               QLabel, QFrame, QSizePolicy)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor
from core.theme import theme_manager
from core.enhanced_base import FluentBaseWidget
from core.enhanced_animations import FluentMicroInteraction
from typing import Optional
import base64


class FluentPasswordBox(FluentBaseWidget):
    """
    Fluent Design Password Box Component
    
    Enhanced password input field with:
    - Password reveal/hide toggle
    - Strength indicator
    - Clear button
    - Fluent styling
    - Accessibility features
    """
    
    # Signals
    text_changed = Signal(str)  # Emitted when password changes
    return_pressed = Signal()  # Emitted when Enter is pressed
    reveal_toggled = Signal(bool)  # Emitted when reveal state changes
    
    def __init__(self, parent: Optional[QWidget] = None,
                 placeholder_text: str = "Enter password"):
        super().__init__(parent)
        
        # Properties
        self._placeholder_text = placeholder_text
        self._password_text = ""
        self._header_text = ""
        self._description_text = ""
        self._is_password_revealed = False
        
        # Configuration
        self._show_reveal_button = True
        self._show_clear_button = True
        self._show_strength_indicator = False
        self._auto_clear_on_focus_lost = False
        
        # UI Elements (will be initialized in setup)
        self._main_layout: Optional[QVBoxLayout] = None  # type: ignore
        self._header_label: Optional[QLabel] = None  # type: ignore
        self._input_container: Optional[QFrame] = None  # type: ignore
        self._input_field: Optional[QLineEdit] = None  # type: ignore
        self._reveal_button: Optional[QPushButton] = None  # type: ignore
        self._clear_button: Optional[QPushButton] = None  # type: ignore
        self._description_label: Optional[QLabel] = None  # type: ignore
        self._strength_indicator: Optional[QWidget] = None  # type: ignore
        
        # Animations
        self._reveal_animation: Optional[FluentMicroInteraction] = None
        
        # Setup
        self._setup_ui()
        self._connect_signals()
        
        # Setup style after everything else is initialized
        QTimer.singleShot(0, self._setup_style)
        
    def _setup_ui(self):
        """Setup the UI layout"""
        # Main vertical layout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(4)
        
        # Header label (optional)
        if self._header_text:
            self._header_label = QLabel(self._header_text)
            self._header_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
            self._main_layout.addWidget(self._header_label)
        
        # Input container frame
        self._input_container = QFrame()
        self._input_container.setFrameStyle(QFrame.Shape.NoFrame)
        self._input_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        input_layout = QHBoxLayout(self._input_container)
        input_layout.setContentsMargins(12, 8, 8, 8)
        input_layout.setSpacing(4)
        
        # Password input field
        self._input_field = QLineEdit()
        self._input_field.setPlaceholderText(self._placeholder_text)
        self._input_field.setEchoMode(QLineEdit.EchoMode.Password)
        self._input_field.setFrame(False)
        self._input_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._input_field.setMinimumHeight(24)
        
        input_layout.addWidget(self._input_field)
        
        # Clear button (optional)
        if self._show_clear_button:
            self._clear_button = self._create_action_button("✕", "Clear password")
            self._clear_button.hide()  # Initially hidden
            input_layout.addWidget(self._clear_button)
        
        # Reveal/Hide button (optional)
        if self._show_reveal_button:
            self._reveal_button = self._create_action_button("👁", "Show password")
            input_layout.addWidget(self._reveal_button)
            
        self._main_layout.addWidget(self._input_container)
        
        # Password strength indicator (optional)
        if self._show_strength_indicator:
            self._setup_strength_indicator()
        
        # Description label (optional)
        if self._description_text:
            self._description_label = QLabel(self._description_text)
            self._description_label.setFont(QFont("Segoe UI", 10))
            self._description_label.setWordWrap(True)
            self._main_layout.addWidget(self._description_label)
            
    def _create_action_button(self, text: str, tooltip: str) -> QPushButton:
        """Create a styled action button"""
        button = QPushButton(text)
        button.setFixedSize(24, 24)
        button.setFlat(True)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setToolTip(tooltip)
        button.setFont(QFont("Segoe UI", 10))
        return button
        
    def _setup_strength_indicator(self):
        """Setup password strength indicator"""
        if not self._main_layout:
            return
            
        self._strength_indicator = QWidget()
        self._strength_indicator.setFixedHeight(4)
        self._strength_indicator.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._main_layout.addWidget(self._strength_indicator)
        
    def _setup_style(self):
        """Apply Fluent Design styling"""
        if not self._input_container or not self._input_field:
            return
            
        theme = theme_manager
        
        # Input container style
        container_style = f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
            }}
            QFrame:hover {{
                border-color: {theme.get_color('primary').lighter(150).name()};
                background-color: {theme.get_color('accent_light').name()};
            }}
            QFrame:focus-within {{
                border-color: {theme.get_color('primary').name()};
                border-width: 2px;
            }}
        """
        
        # Input field style
        field_style = f"""
            QLineEdit {{
                background: transparent;
                border: none;
                font-size: 14px;
                color: {theme.get_color('text_primary').name()};
                selection-background-color: {theme.get_color('primary').name()}40;
                font-family: "Segoe UI", monospace;
            }}
            QLineEdit::placeholder {{
                color: {theme.get_color('text_secondary').name()};
                font-family: "Segoe UI";
            }}
        """
        
        # Action button style
        button_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 4px;
                color: {theme.get_color('text_secondary').name()};
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                color: {theme.get_color('text_primary').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
        """
        
        self._input_container.setStyleSheet(container_style)
        self._input_field.setStyleSheet(field_style)
        
        if self._reveal_button:
            self._reveal_button.setStyleSheet(button_style)
        if self._clear_button:
            self._clear_button.setStyleSheet(button_style)
            
        # Header and description styles
        if self._header_label:
            self._header_label.setStyleSheet(f"""
                QLabel {{ color: {theme.get_color('text_primary').name()}; }}
            """)
            
        if self._description_label:
            self._description_label.setStyleSheet(f"""
                QLabel {{ color: {theme.get_color('text_secondary').name()}; }}
            """)
            
        # Strength indicator style
        if self._strength_indicator:
            self._update_strength_indicator()
            
    def _connect_signals(self):
        """Connect signals and slots"""
        if not self._input_field:
            return
            
        # Input field signals
        self._input_field.textChanged.connect(self._on_text_changed)
        self._input_field.returnPressed.connect(self._on_return_pressed)
        self._input_field.focusOutEvent = self._on_focus_out
        
        # Action button signals
        if self._reveal_button:
            self._reveal_button.clicked.connect(self._toggle_password_reveal)
        if self._clear_button:
            self._clear_button.clicked.connect(self._clear_password)
            
        # Theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)
        
    def _on_theme_changed(self):
        """Handle theme changes"""
        self._setup_style()
        
    def _on_text_changed(self, text: str):
        """Handle text changes"""
        self._password_text = text
        
        # Show/hide clear button based on content
        if self._clear_button:
            self._clear_button.setVisible(bool(text))
            
        # Update strength indicator
        if self._strength_indicator:
            self._update_strength_indicator()
            
        self.text_changed.emit(text)
        
    def _on_return_pressed(self):
        """Handle return key pressed"""
        self.return_pressed.emit()
        
    def _on_focus_out(self, event):
        """Handle focus out event"""
        if self._auto_clear_on_focus_lost:
            self._clear_password()
        # Call original focus out event
        if self._input_field:
            QLineEdit.focusOutEvent(self._input_field, event)
        
    def _toggle_password_reveal(self):
        """Toggle password visibility"""
        if not self._input_field or not self._reveal_button:
            return
            
        self._is_password_revealed = not self._is_password_revealed
        
        if self._is_password_revealed:
            self._input_field.setEchoMode(QLineEdit.EchoMode.Normal)
            self._reveal_button.setText("🙈")
            self._reveal_button.setToolTip("Hide password")
        else:
            self._input_field.setEchoMode(QLineEdit.EchoMode.Password)
            self._reveal_button.setText("👁")
            self._reveal_button.setToolTip("Show password")
            
        # Simple animation effect (can be enhanced later)
        self._reveal_button.setStyleSheet(self._reveal_button.styleSheet() + """
            QPushButton { transform: scale(1.1); }
        """)
        QTimer.singleShot(100, lambda: self._reset_button_style())
        
        self.reveal_toggled.emit(self._is_password_revealed)
        
    def _reset_button_style(self):
        """Reset button style after animation"""
        if self._reveal_button:
            # Re-apply the original style
            self._setup_style()
        
    def _clear_password(self):
        """Clear the password field"""
        if self._input_field:
            self._input_field.clear()
        self._password_text = ""
        
    def _calculate_password_strength(self, password: str) -> float:
        """Calculate password strength (0.0 to 1.0)"""
        if not password:
            return 0.0
            
        score = 0.0
        
        # Length score (up to 0.3)
        length_score = min(len(password) / 12.0, 1.0) * 0.3
        score += length_score
        
        # Character diversity score (up to 0.4)
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        diversity_score = sum([has_lower, has_upper, has_digit, has_special]) / 4.0 * 0.4
        score += diversity_score
        
        # Pattern avoidance score (up to 0.3)
        pattern_score = 0.3
        
        # Penalty for common patterns
        if password.lower() in ['password', '123456', 'qwerty', 'abc123']:
            pattern_score = 0.0
        elif len(set(password)) < len(password) * 0.5:  # Too many repeated characters
            pattern_score *= 0.5
        elif password.isdigit() or password.isalpha():  # Only numbers or letters
            pattern_score *= 0.7
            
        score += pattern_score
        
        return min(score, 1.0)
        
    def _update_strength_indicator(self):
        """Update the password strength indicator"""
        if not self._strength_indicator:
            return
            
        strength = self._calculate_password_strength(self._password_text)
        theme = theme_manager
        
        # Determine strength color
        if strength < 0.3:
            color = theme.get_color('error').name()
        elif strength < 0.6:
            color = theme.get_color('warning').name()
        else:
            color = theme.get_color('success').name()
            
        # Apply gradient style based on strength
        width_percentage = int(strength * 100)
        
        style = f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:{strength:.2f} {color},
                    stop:{strength:.2f} {theme.get_color('border').name()},
                    stop:1 {theme.get_color('border').name()});
                border-radius: 2px;
            }}
        """
        
        self._strength_indicator.setStyleSheet(style)
        
    # Public API
    
    def get_password(self) -> str:
        """Get the current password"""
        return self._password_text
        
    def set_password(self, password: str):
        """Set the password"""
        if self._input_field:
            self._input_field.setText(password)
        self._password_text = password
        
    def clear(self):
        """Clear the password"""
        self._clear_password()
        
    def set_placeholder_text(self, text: str):
        """Set the placeholder text"""
        self._placeholder_text = text
        if self._input_field:
            self._input_field.setPlaceholderText(text)
            
    def set_header_text(self, text: str):
        """Set the header text"""
        self._header_text = text
        if self._header_label:
            self._header_label.setText(text)
            self._header_label.setVisible(bool(text))
            
    def set_description_text(self, text: str):
        """Set the description text"""
        self._description_text = text
        if self._description_label:
            self._description_label.setText(text)
            self._description_label.setVisible(bool(text))
            
    def set_reveal_button_visible(self, visible: bool):
        """Show or hide the reveal button"""
        self._show_reveal_button = visible
        if self._reveal_button:
            self._reveal_button.setVisible(visible)
            
    def set_clear_button_visible(self, visible: bool):
        """Show or hide the clear button"""
        self._show_clear_button = visible
        if self._clear_button:
            self._clear_button.setVisible(visible and bool(self._password_text))
            
    def set_strength_indicator_visible(self, visible: bool):
        """Show or hide the strength indicator"""
        self._show_strength_indicator = visible
        if self._strength_indicator:
            self._strength_indicator.setVisible(visible)
            
    def is_password_revealed(self) -> bool:
        """Check if password is currently revealed"""
        return self._is_password_revealed
        
    def set_auto_clear_on_focus_lost(self, auto_clear: bool):
        """Enable or disable auto-clear when focus is lost"""
        self._auto_clear_on_focus_lost = auto_clear


# Export classes
__all__ = [
    'FluentPasswordBox'
]
