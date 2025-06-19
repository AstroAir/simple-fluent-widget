from typing import Optional, Dict, Any, List, Callable, Tuple, Union
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QFrame, QLabel, QPushButton, QScrollArea,
                               QLineEdit, QCheckBox, QComboBox, QSpinBox)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QByteArray, Signal, Property
from PySide6.QtGui import QFont, QIcon, QColor

from .base import FluentBaseWidget, FluentBaseContainer
from .theme import theme_manager, get_theme_manager
from .animation import FluentAnimation
from .theme_integration import get_transition_manager
from .enhanced_animations import get_theme_aware_animation
from .enhanced_animations import get_theme_aware_animation


class FluentLayoutBuilder:
    """Helper class for building common layout patterns with consistent styling"""

    @staticmethod
    def create_horizontal_layout(spacing: int = 8, margins: tuple = (0, 0, 0, 0)) -> QHBoxLayout:
        """Create a standardized horizontal layout"""
        layout = QHBoxLayout()
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        return layout

    @staticmethod
    def create_vertical_layout(spacing: int = 8, margins: tuple = (0, 0, 0, 0)) -> QVBoxLayout:
        """Create a standardized vertical layout"""
        layout = QVBoxLayout()
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        return layout

    @staticmethod
    def create_grid_layout(spacing: int = 8, margins: tuple = (0, 0, 0, 0)) -> QGridLayout:
        """Create a standardized grid layout"""
        layout = QGridLayout()
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        return layout

    @staticmethod
    def create_toolbar_layout(height: int = 40) -> tuple[QFrame, QHBoxLayout]:
        """Create a standardized toolbar with layout"""
        toolbar = QFrame()
        toolbar.setFixedHeight(height)
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        return toolbar, layout

    @staticmethod
    def create_content_area(scrollable: bool = True) -> tuple[QWidget, QVBoxLayout]:
        """Create a standardized content area"""
        if scrollable:
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            content_widget = QWidget()
            layout = QVBoxLayout(content_widget)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(20)

            scroll_area.setWidget(content_widget)
            return scroll_area, layout
        else:
            content_widget = QWidget()
            layout = QVBoxLayout(content_widget)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(20)
            return content_widget, layout

    @staticmethod
    def create_form_layout(label_width: Optional[int] = None) -> tuple[QWidget, QGridLayout]:
        """Create a standardized form layout with aligned labels"""
        container = QWidget()
        layout = QGridLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        # Make the second column (fields) stretch
        layout.setColumnStretch(1, 1)

        if label_width is not None:
            layout.setColumnMinimumWidth(0, label_width)

        return container, layout

    @staticmethod
    def create_card_layout(padding: int = 16) -> tuple[QFrame, QVBoxLayout]:
        """Create a card-like container with drop shadow"""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setFrameShadow(QFrame.Shadow.Raised)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme_manager.get_color('surface').name()};
                border-radius: 8px;
                border: 1px solid {theme_manager.get_color('border').name()};
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(padding, padding, padding, padding)
        layout.setSpacing(12)

        return card, layout


class FluentStandardButton(QPushButton):
    """Standardized button with consistent sizing and styling"""

    # Button variants
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACCENT = "accent"
    OUTLINE = "outline"
    DANGER = "danger"
    SUCCESS = "success"

    def __init__(self, text: str = "", icon: Optional[QIcon] = None,
                 size: tuple = (None, None), parent: Optional[QWidget] = None,
                 variant: str = SECONDARY):
        super().__init__(text, parent)
        self._variant = variant

        if icon:
            self.setIcon(icon)

        # Apply standard sizing
        if size[0] is not None:
            self.setFixedWidth(size[0])
        if size[1] is not None:
            self.setFixedHeight(size[1])
        else:
            self.setMinimumHeight(32)  # Standard minimum height

        # Standard styling
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_animations()
        self._apply_theme()

        # Connect theme changes
        theme_manager.theme_changed.connect(self._apply_theme)

    @property
    def variant(self) -> str:
        """Get button variant"""
        return self._variant

    @variant.setter
    def variant(self, value: str):
        """Set button variant and update styling"""
        if value in (self.PRIMARY, self.SECONDARY, self.ACCENT,
                     self.OUTLINE, self.DANGER, self.SUCCESS):
            self._variant = value
            self._apply_theme()

    def _setup_animations(self):
        """Setup hover animations"""
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentAnimation.EASE_OUT)

        # Add animated hover effect for smooth transitions
        self._opacity = 0.0
        self._opacity_effect = QPropertyAnimation(self, QByteArray(b"opacity"))
        self._opacity_effect.setDuration(FluentAnimation.DURATION_FAST)
        self._opacity_effect.setEasingCurve(FluentAnimation.EASE_OUT)

    def _apply_theme(self):
        """Apply theme-based styling"""
        theme = theme_manager

        # Base styles
        base_style = f"""
            QPushButton {{
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:disabled {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_disabled').name()};
                border-color: {theme.get_color('border').name()};
            }}
        """

        # Variant-specific styles
        if self._variant == self.PRIMARY:
            style = f"""
                QPushButton {{
                    background-color: {theme.get_color('primary').name()};
                    color: white;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {theme.get_color('primary_dark').name()};
                }}
                QPushButton:pressed {{
                    background-color: {theme.get_color('primary_dark').name()};
                }}
            """
        elif self._variant == self.ACCENT:
            style = f"""
                QPushButton {{
                    background-color: {theme.get_color('accent').name()};
                    color: white;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {theme.get_color('primary_dark').name()};
                }}
                QPushButton:pressed {{
                    background-color: {theme.get_color('primary_dark').name()};
                }}
            """
        elif self._variant == self.OUTLINE:
            style = f"""
                QPushButton {{
                    background-color: transparent;
                    color: {theme.get_color('primary').name()};
                    border: 1px solid {theme.get_color('primary').name()};
                }}
                QPushButton:hover {{
                    background-color: {theme.get_color('accent_light').name()};
                }}
                QPushButton:pressed {{
                    background-color: {theme.get_color('accent_medium').name()};
                }}
            """
        elif self._variant == self.DANGER:
            style = f"""
                QPushButton {{
                    background-color: {theme.get_color('error').name()};
                    color: white;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: #C23601;
                }}
                QPushButton:pressed {{
                    background-color: #B23000;
                }}
            """
        elif self._variant == self.SUCCESS:
            style = f"""
                QPushButton {{
                    background-color: {theme.get_color('success').name()};
                    color: white;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: #096C09;
                }}
                QPushButton:pressed {{
                    background-color: #075C07;
                }}
            """
        else:  # Default SECONDARY
            style = f"""
                QPushButton {{
                    background-color: {theme.get_color('surface').name()};
                    color: {theme.get_color('text_primary').name()};
                    border: 1px solid {theme.get_color('border').name()};
                }}
                QPushButton:hover {{
                    background-color: {theme.get_color('accent_light').name()};
                    border-color: {theme.get_color('primary').name()};
                }}
                QPushButton:pressed {{
                    background-color: {theme.get_color('accent_medium').name()};
                }}
            """

        self.setStyleSheet(base_style + style)

    def enterEvent(self, event):
        """Handle mouse enter events for custom animations"""
        super().enterEvent(event)
        if self.isEnabled():
            self._opacity_effect.setStartValue(0.0)
            self._opacity_effect.setEndValue(1.0)
            self._opacity_effect.start()

    def leaveEvent(self, event):
        """Handle mouse leave events for custom animations"""
        super().leaveEvent(event)
        if self.isEnabled():
            self._opacity_effect.setStartValue(1.0)
            self._opacity_effect.setEndValue(0.0)
            self._opacity_effect.start()

    # Property to animate opacity
    def get_opacity(self):
        return self._opacity

    def set_opacity(self, opacity):
        if self._opacity != opacity:
            self._opacity = opacity
            self.update()

    opacity = Property(float, get_opacity, set_opacity, None, "")


class FluentPanel(FluentBaseContainer):
    """Enhanced panel with standard styling and layout options"""

    def __init__(self, title: str = "", collapsible: bool = False,
                 padding: int = 16, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._title = title
        self._collapsible = collapsible
        self._collapsed = False
        self._padding = padding

        self._setup_ui()
        self._setup_animations()
        self._apply_styling()

        # Connect theme changes
        theme_manager.theme_changed.connect(self._apply_styling)

    def _setup_ui(self):
        """Setup panel UI structure"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header (if title provided)
        if self._title:
            self._setup_header()

        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(self._padding, self._padding,
                                               self._padding, self._padding)
        self.content_layout.setSpacing(8)

        self.main_layout.addWidget(self.content_widget)

    def _setup_header(self):
        """Setup panel header"""
        self.header = QFrame()
        self.header.setFixedHeight(40)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(16, 8, 16, 8)

        # Collapse button (if collapsible)
        if self._collapsible:
            self.collapse_btn = FluentStandardButton("▼", size=(24, 24))
            self.collapse_btn.clicked.connect(self._toggle_collapse)
            header_layout.addWidget(self.collapse_btn)

        # Title
        self.title_label = QLabel(self._title)
        self.title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()
        self.main_layout.addWidget(self.header)

    def _setup_animations(self):
        """Setup collapse/expand animations"""
        if self._collapsible:
            self._collapse_animation = QPropertyAnimation(
                self.content_widget, QByteArray(b"maximumHeight"))
            self._collapse_animation.setDuration(
                FluentAnimation.DURATION_MEDIUM)
            self._collapse_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def _toggle_collapse(self):
        """Toggle panel collapse state"""
        if not self._collapsible:
            return

        self._collapsed = not self._collapsed

        if self._collapsed:
            self.collapse_btn.setText("▶")
            self._collapse_animation.setStartValue(
                self.content_widget.height())
            self._collapse_animation.setEndValue(0)
        else:
            self.collapse_btn.setText("▼")
            self._collapse_animation.setStartValue(0)
            self._collapse_animation.setEndValue(
                self.content_widget.sizeHint().height())

        self._collapse_animation.start()

    def _apply_styling(self):
        """Apply panel styling"""
        theme = theme_manager
        self.setStyleSheet(f"""
            FluentPanel {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
            QFrame#header {{ /* Add ID selector for specificity */
                background-color: {theme.get_color('background').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
                border-radius: 8px 8px 0 0;
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                background-color: transparent;
                border: none;
            }}
        """)
        if hasattr(self, 'header') and self.header:
            # Ensure QFrame can be targeted by ID
            self.header.setObjectName("header")

    def addWidget(self, widget: QWidget):
        """Add widget to panel content"""
        self.content_layout.addWidget(widget)

    def addLayout(self, layout):
        """Add layout to panel content"""
        self.content_layout.addLayout(layout)

    def setTitle(self, title: str):
        """Set panel title"""
        self._title = title
        if hasattr(self, 'title_label'):
            self.title_label.setText(title)

    def title(self) -> str:
        """Get panel title"""
        return self._title

    def isCollapsible(self) -> bool:
        """Check if panel is collapsible"""
        return self._collapsible

    def isCollapsed(self) -> bool:
        """Check if panel is currently collapsed"""
        return self._collapsed

    def setCollapsed(self, collapsed: bool):
        """Set panel collapse state"""
        if self._collapsed != collapsed and self._collapsible:
            self._toggle_collapse()


class FluentToolbar(QFrame):
    """Enhanced toolbar with standardized styling and common actions"""

    def __init__(self, height: int = 40, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedHeight(height)
        self._actions: Dict[str, QPushButton] = {}

        self._setup_ui()
        self._apply_styling()

        # Connect theme changes
        theme_manager.theme_changed.connect(self._apply_styling)

    def _setup_ui(self):
        """Setup toolbar UI"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 4, 8, 4)
        self._layout.setSpacing(4)

    def addToolbarAction(self, name: str, text: str, callback: Optional[Callable] = None,
                         icon: Optional[QIcon] = None, tooltip: str = "",
                         variant: str = FluentStandardButton.SECONDARY) -> FluentStandardButton:
        """Add an action button to toolbar"""
        button = FluentStandardButton(text, icon, (None, 32), variant=variant)

        if callback:
            button.clicked.connect(callback)

        if tooltip:
            button.setToolTip(tooltip)

        self._actions[name] = button
        self._layout.addWidget(button)
        return button

    def addSeparator(self):
        """Add a visual separator"""
        separator = QFrame()
        separator.setFixedWidth(1)
        separator.setFixedHeight(24)
        separator.setFrameStyle(QFrame.Shape.VLine | QFrame.Shadow.Sunken)
        self._layout.addWidget(separator)

    def addStretch(self):
        """Add a stretch to push subsequent items to the right"""
        self._layout.addStretch()

    def addWidget(self, widget: QWidget):
        """Add any widget to toolbar"""
        self._layout.addWidget(widget)

    def getAction(self, name: str) -> Optional[QPushButton]:
        """Get action button by name"""
        return self._actions.get(name)

    def removeToolbarAction(self, name: str) -> bool:
        """Remove an action button by name"""
        if name in self._actions:
            action = self._actions.pop(name)
            action.setParent(None)  # Remove from layout
            action.deleteLater()    # Schedule for deletion
            return True
        return False

    def _apply_styling(self):
        """Apply toolbar styling"""
        theme = theme_manager
        self.setStyleSheet(f"""
            FluentToolbar {{
                background-color: {theme.get_color('background').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
            QFrame[frameShape="5"] {{ /* Targets separators */
                color: {theme.get_color('border').name()};
                background-color: {theme.get_color('border').name()};
            }}
        """)


class FluentFormGroup(FluentPanel):
    """Specialized panel for form fields with validation"""

    # Signal emitted when form validation state changes
    validation_changed = Signal(bool)

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(title, False, 16, parent)
        self._fields: Dict[str, QWidget] = {}
        self._validators: Dict[str, List[Callable]] = {}
        self._error_labels: Dict[str, QLabel] = {}
        self._required_fields: List[str] = []
        self._is_valid = False

        # Set suitable form layout
        self.content_layout.setSpacing(16)

    def addField(self, name: str, widget: QWidget, label_text: str = "",
                 required: bool = False, validators: Optional[List[Callable]] = None):
        """Add a form field with optional validation"""
        field_layout = QVBoxLayout()

        # Label
        if label_text:
            label = QLabel(label_text)
            if required:
                label.setText(f"{label_text} *")
                self._required_fields.append(name)
            field_layout.addWidget(label)

        # Widget
        field_layout.addWidget(widget)

        # Error label (hidden by default)
        error_label = QLabel()
        error_label.setStyleSheet(
            f"color: {theme_manager.get_color('error').name()}; font-size: 12px;")
        error_label.hide()
        field_layout.addWidget(error_label)

        self.content_layout.addLayout(field_layout)

        # Store references
        self._fields[name] = widget
        self._error_labels[name] = error_label
        if validators:
            self._validators[name] = validators

        # Connect change signals for auto-validation
        self._connect_field_signals(widget)

    def _connect_field_signals(self, widget: QWidget):
        """Connect appropriate signals based on widget type for auto-validation"""
        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(self._on_field_change)
        elif isinstance(widget, QCheckBox):
            widget.toggled.connect(self._on_field_change)
        elif isinstance(widget, QComboBox):
            widget.currentIndexChanged.connect(self._on_field_change)
        elif isinstance(widget, QSpinBox):
            widget.valueChanged.connect(self._on_field_change)
        # Add more widget types as needed

    def _on_field_change(self):
        """Handle field value changes"""
        # Optional: Implement delayed validation for better performance
        # For now, just validate immediately
        self.validateAll()

    def validateField(self, name: str) -> bool:
        """Validate a specific field"""
        if name not in self._fields:
            return True

        widget = self._fields[name]
        error_label = self._error_labels[name]

        # Get field value
        value = self._get_field_value(widget)

        # Check required fields
        if name in self._required_fields:
            if value is None or (isinstance(value, str) and not value.strip()):
                error_label.setText("This field is required")
                error_label.show()
                return False

        # Run validators if set for this field
        if name in self._validators:
            for validator in self._validators[name]:
                try:
                    result = validator(value)

                    # Handle both return types: boolean or (boolean, message)
                    if isinstance(result, tuple) and len(result) == 2:
                        is_valid, message = result
                    else:
                        is_valid, message = result, "Invalid value"

                    if not is_valid:
                        error_label.setText(message)
                        error_label.show()
                        return False
                except Exception as e:
                    error_label.setText(str(e))
                    error_label.show()
                    return False

        error_label.hide()
        return True

    def validateAll(self) -> bool:
        """Validate all fields"""
        all_valid = True
        for name in self._fields:
            if not self.validateField(name):
                all_valid = False

        # Emit signal if validation state changed
        if all_valid != self._is_valid:
            self._is_valid = all_valid
            self.validation_changed.emit(all_valid)

        return all_valid

    def _get_field_value(self, widget: QWidget) -> Any:
        """Get field value based on widget type"""
        if isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        # Add more widget types as needed
        return None

    def getFieldValue(self, name: str) -> Any:
        """Get field value by name"""
        if name not in self._fields:
            return None
        return self._get_field_value(self._fields[name])

    def getAllValues(self) -> Dict[str, Any]:
        """Get all field values as dictionary"""
        return {name: self.getFieldValue(name) for name in self._fields}

    def setFieldValue(self, name: str, value: Any) -> bool:
        """Set field value by name"""
        if name not in self._fields:
            return False

        widget = self._fields[name]

        try:
            if isinstance(widget, QLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
            elif isinstance(widget, QComboBox):
                index = widget.findText(str(value))
                if index >= 0:
                    widget.setCurrentIndex(index)
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(value))
            else:
                return False
            return True
        except (ValueError, TypeError):
            return False

    def resetForm(self):
        """Reset all form fields to default values"""
        for name, widget in self._fields.items():
            # Clear errors
            if name in self._error_labels:
                self._error_labels[name].hide()

            # Reset widget based on type
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QSpinBox):
                widget.setValue(widget.minimum())
            # Add more widget types as needed

        # Update validation state
        self._is_valid = False
        self.validation_changed.emit(False)

    def isValid(self) -> bool:
        """Check if form is currently valid"""
        return self._is_valid


class FluentCompositeWidget(FluentBaseWidget):
    """Base class for composite widgets that combine multiple components"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._components: Dict[str, QWidget] = {}

        # Create main layout for composite
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self._setup_composite()
        self._setup_composite_animations()

    def _setup_composite(self):
        """Override in subclasses to setup composite structure"""
        pass

    def _setup_composite_animations(self):
        """Setup animations for composite widget"""
        # Fade in animation for the entire composite
        self._fade_in = FluentAnimation.fade_in(
            self, FluentAnimation.DURATION_MEDIUM)

    def addComponent(self, name: str, component: QWidget):
        """Add a named component"""
        self._components[name] = component
        # Ensure parent is set for proper Qt object tree
        component.setParent(self)

        # Add to layout if exists
        if hasattr(self, '_main_layout') and self._main_layout:
            self._main_layout.addWidget(component)

    def getComponent(self, name: str) -> Optional[QWidget]:
        """Get component by name"""
        return self._components.get(name)

    def showWithAnimation(self):
        """Show the composite widget with animation"""
        self.show()
        self._fade_in.start()

    def animateComponentChange(self, old_name: str, new_name: str):
        """Animate transition between named components"""
        if old_name not in self._components or new_name not in self._components:
            return False

        old_component = self._components[old_name]
        new_component = self._components[new_name]

        fade_out = FluentAnimation.fade_out(
            old_component, FluentAnimation.DURATION_FAST)
        fade_in = FluentAnimation.fade_in(
            new_component, FluentAnimation.DURATION_FAST)

        def on_fade_out_finished():
            old_component.hide()
            new_component.show()
            fade_in.start()

        fade_out.finished.connect(on_fade_out_finished)
        fade_out.start()
        return True

    def removeComponent(self, name: str):
        """Remove a component by name"""
        if name in self._components:
            component = self._components.pop(name)
            if hasattr(self, '_main_layout') and self._main_layout:
                self._main_layout.removeWidget(component)
            component.setParent(None)
            component.deleteLater()
            return True
        return False

    def getComponentNames(self) -> List[str]:
        """Get list of all component names"""
        return list(self._components.keys())


class FluentAnimatedPanel(FluentPanel):
    """Panel with enhanced animations for state changes"""

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        # Collapsible is True by default for animated panel
        super().__init__(title, True, 16, parent)
        self._setup_enhanced_animations()

    def _setup_enhanced_animations(self):
        """Setup enhanced animations"""
        # Smooth expand/collapse with bounce effect
        if self._collapsible:  # This check is somewhat redundant due to __init__
            self._collapse_animation.setEasingCurve(
                FluentAnimation.EASE_OUT_BACK)

        # Hover effect
        self._hover_timer = QTimer(self)  # Set parent for QTimer
        self._hover_timer.setSingleShot(True)
        self._hover_timer.timeout.connect(self._apply_hover_effect)

        # Track hover state
        self._is_hovered = False

    def enterEvent(self, event):
        """Enhanced mouse enter with delayed hover effect"""
        super().enterEvent(event)
        if self.isEnabled():
            self._is_hovered = True
            self._hover_timer.start(100)

    def leaveEvent(self, event):
        """Enhanced mouse leave"""
        super().leaveEvent(event)
        if self.isEnabled():
            self._is_hovered = False
            self._hover_timer.stop()
            self._remove_hover_effect()

    def _apply_hover_effect(self, painter=None, rect=None, base_color=None, hover_intensity=0.1):
        """Apply hover effect via property"""
        if self._is_hovered:
            self.setProperty("hovering", True)
            self.style().unpolish(self)
            self.style().polish(self)
            self.update()

    def _remove_hover_effect(self):
        """Remove hover effect"""
        self.setProperty("hovering", False)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _apply_styling(self):
        """Apply panel styling, including hover states"""
        theme = theme_manager

        self.setStyleSheet(f"""
            FluentAnimatedPanel {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
            FluentAnimatedPanel[hovering="true"] {{
                border-color: {theme.get_color('primary').name()};
            }}
            QFrame#header {{
                background-color: {theme.get_color('background').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
                border-radius: 8px 8px 0 0;
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                background-color: transparent;
                border: none;
            }}
        """)

        if hasattr(self, 'header') and self.header:
            self.header.setObjectName("header")


from core.theme_integration import ThemeAwareWidget

class ThemeIntegratedFluentButton(FluentStandardButton, ThemeAwareWidget):
    """Enhanced button with full theme integration and smooth transitions"""
    
    def __init__(self, text: str = "", icon: Optional[QIcon] = None,
                 size: tuple = (None, None), parent: Optional[QWidget] = None,
                 variant: str = FluentStandardButton.SECONDARY):
        
        FluentStandardButton.__init__(self, text, icon, size, parent, variant)
        ThemeAwareWidget.__init__(self, parent)
        
        # Initialize theme integration
        self._theme_manager = get_theme_manager()
        self._cached_styles: Dict[str, str] = {}
        
        # Register with theme manager
        self._theme_manager.register_component(self)
        
        # Connect to theme signals
        self._theme_manager.transition_started.connect(self._on_theme_transition_started)
        self._theme_manager.transition_finished.connect(self._on_theme_transition_finished)
        
        self._setup_theme_integration()

    def focusInEvent(self, event):
        FluentStandardButton.focusInEvent(self, event)
        ThemeAwareWidget.focusInEvent(self, event)

    def focusOutEvent(self, event):
        FluentStandardButton.focusOutEvent(self, event)
        ThemeAwareWidget.focusOutEvent(self, event)

    # 移除与父类同名的 _setup_theme_integration 和 _on_theme_transition，避免遮盖父类方法
    
    def _setup_theme_integration(self):
        """Setup theme integration features"""
        # Register with transition coordinator
        coordinator = get_transition_manager()
        coordinator.add_component(self)
        
        # Register for theme transition callbacks
        # 已移除主题动画回调注册，避免类型错误
    
    def _on_theme_transition_started(self, transition_type: str):
        """Handle theme transition start"""
        # Add smooth transition effects
        pass
    
    def _on_theme_transition_finished(self):
        """Handle theme transition completion"""
        self.update()
    
    def _on_theme_transition(self, transition_type: str, is_starting: bool):
        """Handle theme transition callbacks"""
        if is_starting:
            pass
    
    def _apply_theme(self):
        """Enhanced theme application with smooth transitions"""
        super()._apply_theme()
        # Additional theme-specific customizations
        self._update_variant_colors()
    
    def _update_variant_colors(self):
        """Update colors based on current variant and theme"""
        theme_colors = {
            self.PRIMARY: "primary",
            self.SECONDARY: "surface", 
            self.ACCENT: "accent_medium",
            self.OUTLINE: "border",
            self.DANGER: "error",
            self.SUCCESS: "success"
        }
        
        color_name = theme_colors.get(self._variant, "surface")
        # Apply variant-specific styling here


class ThemeIntegratedContainer(FluentBaseContainer, ThemeAwareWidget):
    """Enhanced container with theme integration and elevation effects"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        FluentBaseContainer.__init__(self, parent)
        ThemeAwareWidget.__init__(self, parent)
        
        # Initialize theme integration
        self._theme_manager = get_theme_manager()
        self._cached_styles: Dict[str, str] = {}
        
        # Register with theme manager
        self._theme_manager.register_component(self)
        
        # Connect to theme signals
        self._theme_manager.transition_started.connect(self._on_theme_transition_started)
        self._theme_manager.transition_finished.connect(self._on_theme_transition_finished)
        
        self._elevation_level = 1
        self._setup_theme_container()
    
    def _on_theme_transition_started(self, transition_type: str):
        """Handle theme transition start"""
        pass
    
    def _on_theme_transition_finished(self):
        """Handle theme transition completion"""
        self.update()
    
    def _setup_theme_container(self):
        """Setup theme-specific container features"""
        # Apply theme-based elevation
        self._apply_theme_elevation()
        
        # Register with coordinator
        coordinator = get_transition_manager()
        coordinator.add_component(self)
    
    def _apply_theme_elevation(self):
        """Apply elevation effect based on current theme"""
        elevation_color = self._theme_manager.get_elevation_color(self._elevation_level)
        
        # Create subtle shadow effect
        shadow_style = f"""
            QWidget {{
                background-color: {elevation_color.name()};
                border-radius: {self._border_radius}px;
                border: 1px solid {self._get_theme_color('border').name()};
            }}
        """
        self.setStyleSheet(shadow_style)
    
    def set_elevation(self, level: int):
        """Set elevation level with smooth transition"""
        if level != self._elevation_level:
            self._elevation_level = max(0, min(level, 12))
            
            # Animate elevation change
            theme_anim = get_theme_aware_animation()
            elevation_anim = theme_anim.create_theme_aware_color_animation(
                self, "background-color", f"elevation_{self._elevation_level}", 150
            )
            elevation_anim.start()
            
            self._apply_theme_elevation()
            self.update()


class FluentComponentFactory:
    """Factory for creating theme-integrated components"""
    
    @staticmethod
    def create_button(text: str = "", variant: str = FluentStandardButton.SECONDARY,
                     **kwargs) -> ThemeIntegratedFluentButton:
        """Create a theme-integrated button"""
        return ThemeIntegratedFluentButton(text=text, variant=variant, **kwargs)
    
    @staticmethod
    def create_container(elevation: int = 1, **kwargs) -> ThemeIntegratedContainer:
        """Create a theme-integrated container"""
        container = ThemeIntegratedContainer(**kwargs)
        container.set_elevation(elevation)
        return container
    
    @staticmethod
    def create_card(title: str = "", padding: int = 16, 
                   elevation: int = 2, **kwargs) -> tuple[ThemeIntegratedContainer, QVBoxLayout]:
        """Create a theme-integrated card with title"""
        card = FluentComponentFactory.create_container(elevation=elevation, **kwargs)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(padding, padding, padding, padding)
        layout.setSpacing(12)
        
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 16px;
                    font-weight: 600;
                    color: {card._get_theme_color('text_primary').name()};
                    margin-bottom: 8px;
                }}
            """)
            layout.addWidget(title_label)
        
        return card, layout
