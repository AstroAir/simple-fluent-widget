"""
Enhanced Base Components with Better Abstractions
Provides higher-level base classes that eliminate code duplication and improve reusability.
"""

from typing import Optional, Dict, Any, List, Callable
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QFrame, QLabel, QPushButton, QScrollArea)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QByteArray
from PySide6.QtGui import QFont, QIcon

from .base import FluentBaseWidget, FluentBaseContainer
from .theme import theme_manager
from .animation import FluentAnimation


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


class FluentStandardButton(QPushButton):
    """Standardized button with consistent sizing and styling"""

    def __init__(self, text: str = "", icon: Optional[QIcon] = None,
                 size: tuple = (None, None), parent: Optional[QWidget] = None):
        super().__init__(text, parent)

        if icon:
            self.setIcon(icon)

        # Apply standard sizing
        if size[0] is not None:
            self.setFixedWidth(size[0])
        if size[1] is not None:
            self.setFixedHeight(size[1])

        # Standard styling
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_animations()
        self._apply_theme()

        theme_manager.theme_changed.connect(self._apply_theme)

    def _setup_animations(self):
        """Setup hover animations"""
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"geometry"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def _apply_theme(self):
        """Apply theme-based styling"""
        theme = theme_manager
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('primary').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QPushButton:disabled {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_disabled').name()};
                border-color: {theme.get_color('border').name()};
            }}
        """)


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
            self.collapse_btn = QPushButton("▼")
            self.collapse_btn.setFixedSize(24, 24)
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


class FluentToolbar(QFrame):
    """Enhanced toolbar with standardized styling and common actions"""

    def __init__(self, height: int = 40, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedHeight(height)
        self._actions: Dict[str, QPushButton] = {}

        self._setup_ui()
        self._apply_styling()

    def _setup_ui(self):
        """Setup toolbar UI"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 4, 8, 4)
        self._layout.setSpacing(4)

    def addToolbarAction(self, name: str, text: str, callback: Optional[Callable] = None,
                         icon: Optional[QIcon] = None, tooltip: str = "") -> QPushButton:
        """Add an action button to toolbar"""
        button = FluentStandardButton(text, icon, (None, 32))

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

    def getAction(self, name: str) -> Optional[QPushButton]:
        """Get action button by name"""
        return self._actions.get(name)

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

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(title, False, 16, parent)
        self._fields: Dict[str, QWidget] = {}
        self._validators: Dict[str, List[Callable]] = {}
        self._error_labels: Dict[str, QLabel] = {}

    def addField(self, name: str, widget: QWidget, label_text: str = "",
                 required: bool = False, validators: Optional[List[Callable]] = None):
        """Add a form field with optional validation"""
        field_layout = QVBoxLayout()

        # Label
        if label_text:
            label = QLabel(label_text)
            if required:
                label.setText(f"{label_text} *")
                # Consider a less intrusive way to indicate required, or make color themeable
                # label.setStyleSheet("color: red;")
            field_layout.addWidget(label)

        # Widget
        field_layout.addWidget(widget)

        # Error label (hidden by default)
        error_label = QLabel()
        # Consider making color themeable
        error_label.setStyleSheet("color: red; font-size: 12px;")
        error_label.hide()
        field_layout.addWidget(error_label)

        self.content_layout.addLayout(field_layout)

        # Store references
        self._fields[name] = widget
        self._error_labels[name] = error_label
        if validators:
            self._validators[name] = validators

    def validateField(self, name: str) -> bool:
        """Validate a specific field"""
        if name not in self._fields or name not in self._validators:
            return True

        widget = self._fields[name]
        error_label = self._error_labels[name]

        # Get field value
        value = None
        if hasattr(widget, 'text') and callable(getattr(widget, 'text')):
            value = widget.text()  # type: ignore
        elif hasattr(widget, 'value') and callable(getattr(widget, 'value')):
            value = widget.value()  # type: ignore
        # Add more specific checks if needed, e.g., for QCheckBox
        elif hasattr(widget, 'isChecked') and callable(getattr(widget, 'isChecked')):
            value = widget.isChecked()  # type: ignore
        else:
            # If the widget type is unknown or doesn't have a standard value property
            error_label.hide()
            return True  # Or False, depending on desired behavior for unvalidatable fields

        # Run validators
        for validator in self._validators[name]:
            try:
                is_valid, message = validator(value) if isinstance(
                    validator(value), tuple) else (validator(value), "Invalid value")
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
        return all_valid

    def getFieldValue(self, name: str) -> Any:
        """Get field value by name"""
        if name not in self._fields:
            return None

        widget = self._fields[name]
        if hasattr(widget, 'text') and callable(getattr(widget, 'text')):
            return widget.text()  # type: ignore
        elif hasattr(widget, 'value') and callable(getattr(widget, 'value')):
            return widget.value()  # type: ignore
        elif hasattr(widget, 'isChecked') and callable(getattr(widget, 'isChecked')):
            return widget.isChecked()  # type: ignore
        return None

    def getAllValues(self) -> Dict[str, Any]:
        """Get all field values as dictionary"""
        return {name: self.getFieldValue(name) for name in self._fields}


class FluentCompositeWidget(FluentBaseWidget):
    """Base class for composite widgets that combine multiple components"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._components: Dict[str, QWidget] = {}
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

    def getComponent(self, name: str) -> Optional[QWidget]:
        """Get component by name"""
        return self._components.get(name)

    def showWithAnimation(self):
        """Show the composite widget with animation"""
        self.show()
        self._fade_in.start()

    def animateComponentChange(self, old_component: QWidget, new_component: QWidget):
        """Animate transition between components"""
        # Ensure new_component is properly parented and visible if replacing
        # This might require layout management depending on how components are displayed

        fade_out = FluentAnimation.fade_out(
            old_component, FluentAnimation.DURATION_FAST)
        fade_in = FluentAnimation.fade_in(
            new_component, FluentAnimation.DURATION_FAST)

        # Ensure new_component is shown when fade_in starts, and old_component is hidden after fade_out
        # old_component.hide() # Hide immediately or after animation
        # new_component.show() # Show before animation or as part of it

        def on_fade_out_finished():
            old_component.hide()  # Or remove from layout
            new_component.show()  # Ensure it's visible before fading in
            fade_in.start()

        fade_out.finished.connect(on_fade_out_finished)
        fade_out.start()


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
        self._hover_timer.timeout.connect(self._apply_stylesheet_hover_effect)

    def enterEvent(self, event):
        """Enhanced mouse enter with delayed hover effect"""
        super().enterEvent(event)
        if self.isEnabled():  # Only apply hover if widget is enabled
            self._hover_timer.start(100)  # Slight delay for smooth feel

    def leaveEvent(self, event):
        """Enhanced mouse leave"""
        super().leaveEvent(event)
        if self.isEnabled():
            self._hover_timer.stop()
            self._remove_stylesheet_hover_effect()

    def _apply_stylesheet_hover_effect(self):
        """Apply subtle hover effect via stylesheet"""
        theme = theme_manager
        # Append to existing stylesheet to avoid overriding other styles
        # A more robust way would be to manage style properties or use dynamic properties
        current_style = self.styleSheet()
        hover_style = f"""
            FluentAnimatedPanel:hover {{
                border-color: {theme.get_color('primary').name()};
                /* box-shadow is not a standard Qt stylesheet property. 
                   Custom painting would be needed for this.
                   For simplicity, we'll stick to border-color. */
            }}
        """
        # It's tricky to just "add" hover pseudo-state styles.
        # Usually, the :hover state is part of the base stylesheet.
        # For dynamic changes, consider setting a property and re-polishing.
        self.setProperty("hovering", True)
        self.style().unpolish(self)
        self.style().polish(self)
        # The below is a simplified approach that might have issues with specificity
        # self.setStyleSheet(current_style + hover_style)
        # A better way for hover is to define it in the main _apply_styling
        # and use properties to trigger re-evaluation if needed, or rely on Qt's hover handling.
        # For this example, we'll assume the base _apply_styling needs to include the hover state.
        # Let's adjust _apply_styling in FluentPanel to include a generic hover for panels.

    def _remove_stylesheet_hover_effect(self):
        """Remove hover effect by reapplying base styling or unsetting property"""
        self.setProperty("hovering", False)
        self.style().unpolish(self)
        self.style().polish(self)
        # self._apply_styling() # Reapplies the entire base style

    def _apply_styling(self):
        """Apply panel styling, including hover states if applicable."""
        super()._apply_styling()  # Call base class styling first
        theme = theme_manager
        # Add or modify stylesheet for FluentAnimatedPanel specifically
        # This demonstrates how to extend styling for derived classes.
        # Note: The :hover state should ideally be part of the initial stylesheet.
        self.setStyleSheet(f"""
            FluentAnimatedPanel {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 8px;
            }}
            FluentAnimatedPanel:hover {{
                border-color: {theme.get_color('primary').name()};
            }}
            QFrame#header {{ /* Targeting header within FluentAnimatedPanel */
                background-color: {theme.get_color('background').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
                border-radius: 8px 8px 0 0; /* top-left and top-right */
            }}
             QLabel {{ /* General QLabel styling within this panel context */
                color: {theme.get_color('text_primary').name()};
                background-color: transparent;
                border: none;
            }}
        """)
        if hasattr(self, 'header') and self.header:
            self.header.setObjectName("header")
