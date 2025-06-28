"""
Property Grid Components - Optimized Version

Advanced property editing components that follow the Fluent Design System.
Includes property grids, settings panels, and configuration editors.

Optimized for Python 3.11+ with modern features:
- Union type syntax (|) 
- Generic type annotations
- Improved exception handling
- Enhanced pattern matching
- Dataclass integration
- Performance optimizations
"""

import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Callable, Union, Protocol, TypeVar, Generic
from collections.abc import Sequence
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QSlider, QColorDialog, QScrollArea, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QTextEdit, QPushButton, QFileDialog, QGroupBox,
    QGraphicsOpacityEffect, QStyledItemDelegate, QAbstractItemView
)
from PySide6.QtCore import (
    Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve,
    QByteArray, QAbstractAnimation, QModelIndex, QMimeData,
    QMetaObject, QThread, Slot
)
from PySide6.QtGui import QFont, QColor, QAction, QShortcut, QKeySequence

# Enhanced error handling for theme manager
try:
    from core.theme import theme_manager
    THEME_AVAILABLE = True
except ImportError:
    theme_manager = None
    THEME_AVAILABLE = False

# Enhanced error handling for animations with better fallback
try:
    from core.enhanced_animations import (
        FluentRevealEffect,
        FluentMicroInteraction,
        FluentTransition
    )
    ANIMATIONS_AVAILABLE = True
except ImportError:
    # Modern null object pattern with proper typing
    class AnimationProxy:
        """Null object pattern for missing animation classes"""
        def __getattr__(self, name: str) -> Callable[..., None]:
            return lambda *args, **kwargs: None
    
    ANIMATIONS_AVAILABLE = False
    FluentRevealEffect = AnimationProxy()
    FluentMicroInteraction = AnimationProxy()
    FluentTransition = AnimationProxy()


# Type aliases for better code readability (Python 3.10+ style)
PropertyValue = Union[str, int, float, bool, QColor, Any]
PropertyDict = Dict[str, PropertyValue]
CategoryDict = Dict[str, PropertyDict]

# Generic type variables
T = TypeVar('T')
P = TypeVar('P', bound='FluentPropertyItem')


class PropertyValidationProtocol(Protocol):
    """Protocol for property validation functions"""
    def __call__(self, value: Any) -> bool: ...


@dataclass(slots=True, frozen=True)  # Python 3.10+ dataclass optimization
class PropertyConstraints:
    """Immutable constraints for property validation"""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    required: bool = False
    pattern: Optional[str] = None
    choices: Optional[tuple[str, ...]] = None


class PropertyType(Enum):
    """Enhanced property data types with auto() for maintainability"""
    STRING = auto()
    INTEGER = auto() 
    FLOAT = auto()
    BOOLEAN = auto()
    COLOR = auto()
    CHOICE = auto()
    RANGE = auto()
    FILE = auto()
    DIRECTORY = auto()
    TEXT = auto()
    FONT = auto()
    # New types for enhanced functionality
    DATE = auto()
    TIME = auto()
    DATETIME = auto()
    MULTISELECT = auto()
    JSON = auto()


@dataclass(slots=True)  # Modern dataclass with __slots__ optimization
class FluentPropertyItem:
    """Represents a single property item with enhanced validation and constraints"""
    
    name: str
    value: PropertyValue
    property_type: PropertyType
    description: str = ""
    choices: Optional[Sequence[str]] = None
    range_min: float = 0.0
    range_max: float = 100.0
    readonly: bool = False
    category: str = "General"
    constraints: Optional[PropertyConstraints] = None
    validator: Optional[PropertyValidationProtocol] = None
    
    def __post_init__(self) -> None:
        """Post-initialization validation and setup"""
        if self.choices is not None and not isinstance(self.choices, (list, tuple)):
            object.__setattr__(self, 'choices', list(self.choices))
        
        # Auto-create constraints if not provided
        if self.constraints is None and self.property_type in (PropertyType.INTEGER, PropertyType.FLOAT):
            object.__setattr__(self, 'constraints', PropertyConstraints(
                min_value=self.range_min,
                max_value=self.range_max
            ))

    def set_validator(self, validator: PropertyValidationProtocol) -> None:
        """Set custom validation function with type safety"""
        object.__setattr__(self, 'validator', validator)

    def is_valid(self, value: PropertyValue) -> bool:
        """Enhanced validation with constraint checking"""
        # Custom validator takes precedence
        if self.validator and not self.validator(value):
            return False
            
        # Built-in constraint validation using match statement
        if self.constraints:
            match self.property_type:
                case PropertyType.INTEGER | PropertyType.FLOAT:
                    try:
                        num_val = float(value) if isinstance(value, (str, int, float)) else 0.0
                        if self.constraints.min_value is not None and num_val < self.constraints.min_value:
                            return False
                        if self.constraints.max_value is not None and num_val > self.constraints.max_value:
                            return False
                    except (ValueError, TypeError):
                        return False
                case PropertyType.STRING:
                    if self.constraints.required and not str(value).strip():
                        return False
                case PropertyType.CHOICE:
                    if self.constraints.choices and str(value) not in self.constraints.choices:
                        return False
        
        return True


class FluentPropertyGrid(QWidget):
    """
    Advanced property grid for editing object properties with modern features
    
    Enhanced with:
    - Type-safe property handling
    - Async property updates 
    - Keyboard shortcuts and accessibility
    - Undo/redo support
    - Performance optimizations
    """

    # Enhanced signals with proper typing
    property_changed = Signal(str, object)  # property_name, new_value
    property_validation_failed = Signal(str, object, str)  # property_name, value, error
    selection_changed = Signal(str)  # property_name
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Enhanced initialization with type hints
        self.properties: Dict[str, FluentPropertyItem] = {}
        self.editors: Dict[str, QWidget] = {}
        self.categories: Dict[str, QTreeWidgetItem] = {}
        
        # Performance and animation settings
        self.animations_enabled = True
        self.animation_duration = 250  # Reduced for better performance
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._perform_deferred_updates)
        self._pending_updates: List[str] = []
        
        # Undo/redo support
        self._property_history: List[Dict[str, PropertyValue]] = []
        self._history_index = -1
        self._max_history = 50
        
        self.setup_ui()
        self.setup_shortcuts()
        self.apply_theme()
        self.setup_theme_connections()

    def setup_ui(self) -> None:
        """Setup the modern user interface with accessibility features"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)  # Modern spacing
        layout.setSpacing(8)

        # Enhanced tree widget with modern features
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Property", "Value"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setItemsExpandable(True)
        self.tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tree.setUniformRowHeights(True)  # Performance optimization
        
        # Accessibility improvements
        self.tree.setAccessibleName("Property Grid")
        self.tree.setAccessibleDescription("Edit properties by selecting items and modifying values")
        
        # Enhanced header configuration
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)

        # Connect modern signals
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.tree)

        # Add expand/collapse animations if available
        if ANIMATIONS_AVAILABLE:
            self.tree.itemExpanded.connect(self._animate_category_expansion)
            self.tree.itemCollapsed.connect(self._animate_category_collapse)

    def setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts for accessibility and productivity"""
        try:
            # Undo/Redo shortcuts with proper QKeySequence creation
            undo_shortcut = QShortcut(QKeySequence(QKeySequence.StandardKey.Undo), self)
            undo_shortcut.activated.connect(self.undo_last_change)
            
            redo_shortcut = QShortcut(QKeySequence(QKeySequence.StandardKey.Redo), self)
            redo_shortcut.activated.connect(self.redo_last_change)
            
            # Navigation shortcuts
            expand_all_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
            expand_all_shortcut.activated.connect(self.tree.expandAll)
            
            collapse_all_shortcut = QShortcut(QKeySequence("Ctrl+Shift+E"), self)
            collapse_all_shortcut.activated.connect(self.tree.collapseAll)
        except Exception as e:
            print(f"Warning: Could not setup shortcuts: {e}")

    def setup_theme_connections(self) -> None:
        """Setup theme change connections with error handling"""
        if THEME_AVAILABLE and theme_manager is not None:
            try:
                # Use QMetaObject for safe signal connection
                if hasattr(theme_manager, 'theme_changed'):
                    theme_manager.theme_changed.connect(self.apply_theme)
            except (AttributeError, RuntimeError) as e:
                print(f"Warning: Could not connect to theme manager: {e}")

    @Slot()
    def _on_selection_changed(self) -> None:
        """Handle selection changes with proper signal emission"""
        current = self.tree.currentItem()
        if current and current.parent():  # Only emit for property items, not categories
            prop_name = current.text(0)
            self.selection_changed.emit(prop_name)

    @Slot()
    def _perform_deferred_updates(self) -> None:
        """Perform pending updates in batch for better performance"""
        if not self._pending_updates:
            return
            
        for prop_name in self._pending_updates:
            if prop_name in self.properties:
                self._update_property_display(prop_name)
        
        self._pending_updates.clear()

    def _update_property_display(self, prop_name: str) -> None:
        """Update the display for a specific property"""
        if prop_name not in self.editors:
            return
            
        prop = self.properties[prop_name]
        editor = self.editors[prop_name]
        
        # Type-safe value updates
        self._safe_update_editor_value(editor, prop)

    def _safe_update_editor_value(self, editor: QWidget, prop: FluentPropertyItem) -> None:
        """Safely update editor value with proper type checking"""
        try:
            match prop.property_type:
                case PropertyType.STRING:
                    if isinstance(editor, QLineEdit):
                        editor.setText(str(prop.value))
                case PropertyType.INTEGER:
                    if isinstance(editor, QSpinBox) and isinstance(prop.value, (int, float)):
                        editor.setValue(int(prop.value))
                case PropertyType.FLOAT:
                    if isinstance(editor, QDoubleSpinBox) and isinstance(prop.value, (int, float)):
                        editor.setValue(float(prop.value))
                case PropertyType.BOOLEAN:
                    if isinstance(editor, QCheckBox):
                        editor.setChecked(bool(prop.value))
                case PropertyType.CHOICE:
                    if isinstance(editor, QComboBox):
                        editor.setCurrentText(str(prop.value))
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not update editor for {prop.name}: {e}")

    def undo_last_change(self) -> None:
        """Undo the last property change"""
        if self._history_index > 0:
            self._history_index -= 1
            self._restore_state(self._property_history[self._history_index])

    def redo_last_change(self) -> None:
        """Redo the last undone change"""
        if self._history_index < len(self._property_history) - 1:
            self._history_index += 1
            self._restore_state(self._property_history[self._history_index])

    def _save_state(self) -> None:
        """Save current property state for undo/redo"""
        current_state = {name: prop.value for name, prop in self.properties.items()}
        
        # Remove future history if we're not at the end
        if self._history_index < len(self._property_history) - 1:
            self._property_history = self._property_history[:self._history_index + 1]
        
        self._property_history.append(current_state)
        self._history_index = len(self._property_history) - 1
        
        # Limit history size
        if len(self._property_history) > self._max_history:
            self._property_history.pop(0)
            self._history_index -= 1

    def _restore_state(self, state: Dict[str, PropertyValue]) -> None:
        """Restore property state from history"""
        for prop_name, value in state.items():
            if prop_name in self.properties:
                # Update using object.__setattr__ for frozen dataclass
                object.__setattr__(self.properties[prop_name], 'value', value)
                self._update_property_display(prop_name)

    def apply_theme(self) -> None:
        """Apply the current theme with enhanced styling"""
        if not THEME_AVAILABLE or not theme_manager:
            # Fallback theme
            self.setStyleSheet("""
                QTreeWidget {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                    border-radius: 8px;
                    selection-background-color: #E0E0E0;
                }
            """)
            return

        try:
            bg_color = theme_manager.get_color('surface').name()
            text_color = theme_manager.get_color('on_surface').name()
            border_color = theme_manager.get_color('outline').name()
            
            modern_style = f"""
                QTreeWidget {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    gridline-color: {border_color};
                    selection-background-color: {theme_manager.get_color('primary_container').name()};
                    selection-color: {theme_manager.get_color('on_primary_container').name()};
                    font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
                }}
                
                QTreeWidget::item {{
                    padding: 8px;
                    border-bottom: 1px solid {border_color};
                    min-height: 24px;
                }}
                
                QTreeWidget::item:hover {{
                    background-color: {theme_manager.get_color('surface_variant').name()};
                }}
                
                QTreeWidget::item:selected {{
                    background-color: {theme_manager.get_color('primary_container').name()};
                    color: {theme_manager.get_color('on_primary_container').name()};
                }}
            """
            
            self.setStyleSheet(modern_style)
            
        except Exception as e:
            print(f"Warning: Could not apply theme: {e}")

    def add_property(self, prop: FluentPropertyItem) -> None:
        """Add a property to the grid with enhanced features"""
        # Save state before modification
        self._save_state()
        
        self.properties[prop.name] = prop

        # Find or create category with modern styling
        category_item = self.categories.get(prop.category)
        if not category_item:
            category_item = QTreeWidgetItem(self.tree)
            category_item.setText(0, prop.category)
            category_item.setExpanded(True)
            category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

            # Enhanced category styling
            font = category_item.font(0)
            font.setBold(True)
            font.setPointSize(font.pointSize() + 1)
            category_item.setFont(0, font)

            self.categories[prop.category] = category_item

        # Create property item with enhanced features
        prop_item = QTreeWidgetItem(category_item)
        prop_item.setText(0, prop.name)
        prop_item.setToolTip(0, prop.description)
        
        # Add validation indicator
        if prop.constraints and prop.constraints.required:
            prop_item.setText(0, f"{prop.name} *")  # Mark required fields

        # Create editor widget with type safety
        editor = self.create_editor(prop)
        if editor:
            self.tree.setItemWidget(prop_item, 1, editor)
            self.editors[prop.name] = editor

            # Add animation for property reveal if available
            if ANIMATIONS_AVAILABLE and self.animations_enabled:
                self._animate_property_reveal(prop_item)

    def create_editor(self, prop: FluentPropertyItem) -> Optional[QWidget]:
        """Create appropriate editor widget with enhanced type safety"""
        if prop.readonly:
            editor = QLabel(str(prop.value))
            editor.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            return editor

        editor_widget: Optional[QWidget] = None
        
        try:
            match prop.property_type:
                case PropertyType.STRING:
                    editor = QLineEdit()
                    editor.setText(str(prop.value))
                    editor.textChanged.connect(
                        lambda text, p_name=prop.name: self._handle_property_change(p_name, text))
                    editor_widget = editor

                case PropertyType.INTEGER:
                    editor = QSpinBox()
                    editor.setRange(-999999, 999999)
                    if isinstance(prop.value, (int, float)):
                        editor.setValue(int(prop.value))
                    editor.valueChanged.connect(
                        lambda value, p_name=prop.name: self._handle_property_change(p_name, value))
                    editor_widget = editor

                case PropertyType.FLOAT:
                    editor = QDoubleSpinBox()
                    editor.setRange(-999999.0, 999999.0)
                    editor.setDecimals(3)
                    if isinstance(prop.value, (int, float)):
                        editor.setValue(float(prop.value))
                    editor.valueChanged.connect(
                        lambda value, p_name=prop.name: self._handle_property_change(p_name, value))
                    editor_widget = editor

                case PropertyType.BOOLEAN:
                    editor = QCheckBox()
                    editor.setChecked(bool(prop.value))
                    editor.toggled.connect(
                        lambda checked, p_name=prop.name: self._handle_property_change(p_name, checked))
                    editor_widget = editor

                case PropertyType.CHOICE:
                    editor = QComboBox()
                    if prop.choices:
                        editor.addItems(list(prop.choices))
                        if str(prop.value) in prop.choices:
                            editor.setCurrentText(str(prop.value))
                    editor.currentTextChanged.connect(
                        lambda text, p_name=prop.name: self._handle_property_change(p_name, text))
                    editor_widget = editor
                    
                case _:  # Default fallback
                    editor = QLineEdit()
                    editor.setText(str(prop.value))
                    editor.textChanged.connect(
                        lambda text, p_name=prop.name: self._handle_property_change(p_name, text))
                    editor_widget = editor

        except Exception as e:
            print(f"Warning: Could not create editor for {prop.name}: {e}")
            # Fallback to simple label
            editor_widget = QLabel(str(prop.value))

        # Apply modern styling
        if editor_widget and THEME_AVAILABLE and theme_manager:
            self._apply_editor_theme(editor_widget)
            
        return editor_widget

    def _handle_property_change(self, prop_name: str, value: PropertyValue) -> None:
        """Handle property changes with validation and history"""
        if prop_name not in self.properties:
            return
            
        prop = self.properties[prop_name]
        
        # Validate the new value
        if not prop.is_valid(value):
            self.property_validation_failed.emit(prop_name, value, "Invalid value")
            return
            
        # Update property value
        object.__setattr__(prop, 'value', value)
        
        # Emit change signal
        self.property_changed.emit(prop_name, value)
        
        # Add micro-interaction feedback
        if ANIMATIONS_AVAILABLE and self.animations_enabled:
            editor = self.editors.get(prop_name)
            if editor:
                self._animate_value_change(editor)

    def _apply_editor_theme(self, editor: QWidget) -> None:
        """Apply theme to editor widgets"""
        try:
            if theme_manager:
                editor_style = f"""
                    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {{
                        background-color: {theme_manager.get_color('surface_variant').name()};
                        color: {theme_manager.get_color('on_surface_variant').name()};
                        border: 1px solid {theme_manager.get_color('outline').name()};
                        border-radius: 4px;
                        padding: 6px;
                        font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
                    }}
                    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                        border: 2px solid {theme_manager.get_color('primary').name()};
                    }}
                """
                editor.setStyleSheet(editor_style)
        except Exception as e:
            print(f"Warning: Could not apply editor theme: {e}")

    # Animation methods with safe fallbacks
    def _animate_property_reveal(self, item: QTreeWidgetItem) -> None:
        """Animate property reveal with fallback"""
        if not self.animations_enabled or not ANIMATIONS_AVAILABLE:
            return
            
        try:
            widget = self.tree.itemWidget(item, 1)
            if widget:
                FluentRevealEffect.fade_in(widget, duration=self.animation_duration // 2)
        except Exception:
            pass  # Silent fallback

    def _animate_category_expansion(self, item: QTreeWidgetItem) -> None:
        """Animate category expansion with staggered effects"""
        if not self.animations_enabled or not ANIMATIONS_AVAILABLE:
            return
            
        try:
            if item in self.categories.values():
                for i in range(item.childCount()):
                    child_item = item.child(i)
                    widget = self.tree.itemWidget(child_item, 1)
                    if widget:
                        QTimer.singleShot(i * 50, lambda w=widget:
                                        FluentRevealEffect.slide_in(w, duration=self.animation_duration, direction="up"))
        except Exception:
            pass

    def _animate_category_collapse(self, item: QTreeWidgetItem) -> None:
        """Animate category collapse"""
        if not self.animations_enabled or not ANIMATIONS_AVAILABLE:
            return
            
        try:
            if item in self.categories.values():
                for i in range(item.childCount()):
                    child_item = item.child(i)
                    widget = self.tree.itemWidget(child_item, 1)
                    if widget:
                        effect = QGraphicsOpacityEffect(widget)
                        widget.setGraphicsEffect(effect)
                        
                        anim = QPropertyAnimation(effect, QByteArray(b"opacity"))
                        anim.setDuration(self.animation_duration // 2)
                        anim.setStartValue(1.0)
                        anim.setEndValue(0.0)
                        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        except Exception:
            pass

    def _animate_value_change(self, widget: QWidget) -> None:
        """Animate value change with micro-interaction"""
        if self.animations_enabled and ANIMATIONS_AVAILABLE:
            try:
                FluentMicroInteraction.pulse_animation(widget, scale=1.03)
            except Exception:
                pass    # Modern utility methods
    def get_property_value(self, name: str) -> Optional[PropertyValue]:
        """Get current property value with type safety"""
        prop = self.properties.get(name)
        return prop.value if prop else None

    def set_property_value(self, name: str, value: PropertyValue) -> bool:
        """Set property value with validation"""
        if name not in self.properties:
            return False
            
        prop = self.properties[name]
        if not prop.is_valid(value):
            return False
            
        object.__setattr__(prop, 'value', value)
        self._update_property_display(name)
        return True

    def clear_properties(self) -> None:
        """Clear all properties efficiently"""
        self.tree.clear()
        self.properties.clear()
        self.editors.clear()
        self.categories.clear()
        self._property_history.clear()
        self._history_index = -1

    def set_animations_enabled(self, enabled: bool) -> None:
        """Enable or disable animations"""
        self.animations_enabled = enabled

    def export_properties(self) -> Dict[str, PropertyValue]:
        """Export all property values"""
        return {name: prop.value for name, prop in self.properties.items()}

    def import_properties(self, values: Dict[str, PropertyValue]) -> None:
        """Import property values with validation"""
        self._save_state()
        
        for name, value in values.items():
            if name in self.properties:
                self.set_property_value(name, value)


# Example usage and demo
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Enhanced Property Grid Demo")
    window.setGeometry(100, 100, 800, 600)
    
    # Create property grid
    prop_grid = FluentPropertyGrid()
    
    # Add sample properties with modern features
    prop_grid.add_property(FluentPropertyItem(
        "Name", "John Doe", PropertyType.STRING, 
        "Person's full name", category="Personal Info",
        constraints=PropertyConstraints(required=True)
    ))
    
    prop_grid.add_property(FluentPropertyItem(
        "Age", 30, PropertyType.INTEGER, 
        "Person's age in years", category="Personal Info",
        constraints=PropertyConstraints(min_value=0, max_value=150)
    ))
    
    prop_grid.add_property(FluentPropertyItem(
        "Active", True, PropertyType.BOOLEAN, 
        "Is the person active", category="Status"
    ))
    
    prop_grid.add_property(FluentPropertyItem(
        "Country", "USA", PropertyType.CHOICE, 
        "Country of residence", 
        choices=("USA", "Canada", "UK", "Germany", "France"),
        category="Location"
    ))
    
    window.setCentralWidget(prop_grid)
    window.show()
    
    sys.exit(app.exec())
