"""
Composite Panel Components

This module provides higher-level panel components that combine multiple basic
widgets into common patterns like settings panels, property editors, and dialogs.

Optimized for Python 3.10+ with modern typing, dataclasses, context managers,
and enhanced performance features.
"""

from __future__ import annotations
from typing import Any, Callable, TypeVar, TypeAlias, Protocol, Optional, Dict, List, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import lru_cache, partial
from contextlib import contextmanager
import weakref
from collections.abc import Sequence

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QLineEdit, QComboBox, QSpinBox,
                               QScrollArea, QFrame, QDoubleSpinBox,
                               QButtonGroup, QSizePolicy, QApplication)
from PySide6.QtCore import Signal, QTimer, QPropertyAnimation, Qt, QModelIndex
from PySide6.QtGui import QFont, QIcon, QValidator

from core.enhanced_base import (FluentPanel, FluentStandardButton,
                                FluentLayoutBuilder, FluentCompositeWidget,
                                FluentFormGroup)
from core.enhanced_animations import FluentTransition, FluentMicroInteraction
from core.theme import theme_manager
from ..basic.textbox import FluentLineEdit
from ..basic.checkbox import FluentCheckBox

# Type aliases for better readability
SettingValue: TypeAlias = str | int | float | bool | Any
ValidationCallback: TypeAlias = Callable[[Any], bool]
ChangeCallback: TypeAlias = Callable[[str, Any], None]
FormData: TypeAlias = Dict[str, Any]

T = TypeVar('T', bound=QWidget)
P = TypeVar('P', bound=QWidget)


# Configuration dataclasses for better structure and type safety
@dataclass(frozen=True)
class SettingConfig:
    """Configuration for panel settings with enhanced validation"""
    key: str
    label: str
    default_value: SettingValue
    setting_type: type = str
    validator: Optional[ValidationCallback] = None
    help_text: str = ""
    required: bool = False
    
    def __post_init__(self):
        if not self.key or not self.label:
            raise ValueError("Setting key and label are required")
        if self.setting_type not in (str, int, float, bool):
            raise ValueError(f"Unsupported setting type: {self.setting_type}")


@dataclass(frozen=True)
class ChoiceConfig:
    """Configuration for choice settings"""
    key: str
    label: str
    choices: Sequence[tuple[str, Any]]
    default_index: int = 0
    help_text: str = ""
    required: bool = False
    
    def __post_init__(self):
        if not self.choices:
            raise ValueError("Choices cannot be empty")
        if not 0 <= self.default_index < len(self.choices):
            raise ValueError("Default index out of range")


@dataclass(frozen=True)
class PropertyDescriptor:
    """Enhanced property descriptor with metadata"""
    name: str
    value: Any
    prop_type: type
    editable: bool = True
    validator: Optional[ValidationCallback] = None
    display_name: Optional[str] = None
    category: str = "General"
    
    @property
    def effective_display_name(self) -> str:
        return self.display_name or self.name.replace('_', ' ').title()


class PanelState(Enum):
    """Panel state enumeration"""
    NORMAL = auto()
    LOADING = auto()
    ERROR = auto()
    MODIFIED = auto()


class ValidatorProtocol(Protocol):
    """Protocol for setting validators"""
    def validate(self, value: Any) -> bool: ...
    def error_message(self) -> str: ...


class CacheManager:
    """Optimized cache manager for panel resources"""
    
    def __init__(self, max_size: int = 256):
        self._cache: Dict[str, Any] = {}
        self._max_size = max_size
    
    @lru_cache(maxsize=256)
    def get_cached_style(self, theme_name: str, component_type: str) -> str:
        """Get cached style for component"""
        key = f"{theme_name}_{component_type}"
        return self._cache.get(key, "")
    
    def set_cached_style(self, theme_name: str, component_type: str, style: str) -> None:
        """Set cached style with size management"""
        if len(self._cache) >= self._max_size:
            # Remove oldest entries
            oldest_keys = list(self._cache.keys())[:self._max_size // 4]
            for key in oldest_keys:
                self._cache.pop(key, None)
        
        key = f"{theme_name}_{component_type}"
        self._cache[key] = style
    
    def clear_cache(self) -> None:
        """Clear the cache"""
        self._cache.clear()
        self.get_cached_style.cache_clear()


# Global cache instance
_cache_manager = CacheManager()


class FluentSettingsPanel(FluentPanel):
    """
    High-level settings panel that automatically organizes settings into
    collapsible groups with consistent styling and validation.
    
    Enhanced with modern Python features, better type safety, and optimized performance.
    """

    setting_changed = Signal(str, object)  # setting_key, new_value
    settings_applied = Signal(dict)  # all_settings
    settings_reset = Signal()

    def __init__(self, title: str = "Settings", parent: Optional[QWidget] = None):
        super().__init__(title, collapsible=False, parent=parent)
        self._settings_groups: Dict[str, FluentFormGroup] = {}
        self._current_values: Dict[str, Any] = {}
        self._default_values: Dict[str, Any] = {}
        self._validators: Dict[str, ValidationCallback] = {}
        self._setting_widgets: Dict[str, QWidget] = {}
        self._state = PanelState.NORMAL
        self._debounce_timer = QTimer(self)
        self._weak_refs: List[weakref.ref] = []

        # Setup debouncing for change notifications
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_deferred_changes)
        self._pending_changes: Dict[str, Any] = {}

        # Setup main layout for settings groups
        self._setup_settings_layout()
        self._apply_enhanced_styling()

    def _setup_settings_layout(self):
        """Setup the main settings layout with optimizations"""
        # Add action buttons at the bottom
        self._setup_action_buttons()

    @contextmanager
    def batch_updates(self):
        """Context manager for batching multiple setting updates"""
        self.setUpdatesEnabled(False)
        try:
            yield
        finally:
            self.setUpdatesEnabled(True)
            self.update()

    def _setup_action_buttons(self):
        """Setup action buttons with enhanced styling"""
        button_frame = QFrame()
        button_layout = FluentLayoutBuilder.create_horizontal_layout(spacing=8)
        button_frame.setLayout(button_layout)

        # Add stretch to push buttons to the right
        button_layout.addStretch()

        # Reset button with modern styling
        self.reset_button = FluentStandardButton(
            "Reset", 
            size=(80, 32),
            variant=FluentStandardButton.OUTLINE
        )
        self.reset_button.clicked.connect(self._reset_settings)
        FluentMicroInteraction.button_press(self.reset_button)
        button_layout.addWidget(self.reset_button)

        # Apply button with accent styling
        self.apply_button = FluentStandardButton(
            "Apply", 
            size=(80, 32),
            variant=FluentStandardButton.PRIMARY
        )
        self.apply_button.clicked.connect(self._apply_settings)
        FluentMicroInteraction.button_press(self.apply_button)
        button_layout.addWidget(self.apply_button)

        self.addWidget(button_frame)

    def _apply_enhanced_styling(self) -> None:
        """Apply enhanced styling with caching"""
        theme_key = getattr(theme_manager, 'get_current_theme_name', lambda: 'default')()
        cached_style = _cache_manager.get_cached_style(theme_key, 'settings_panel')
        
        if not cached_style:
            cached_style = f"""
                FluentSettingsPanel {{
                    background-color: {theme_manager.get_color("surface")};
                    border: 1px solid {theme_manager.get_color("border")};
                    border-radius: 8px;
                }}
                QFrame {{
                    background-color: transparent;
                }}
            """
            _cache_manager.set_cached_style(theme_key, 'settings_panel', cached_style)
        
        self.setStyleSheet(cached_style)

    def add_settings_group(self, group_name: str, title: Optional[str] = None) -> FluentFormGroup:
        """Add a new settings group with enhanced management"""
        if title is None:
            title = group_name

        group = FluentFormGroup(title)
        self._settings_groups[group_name] = group

        # Insert before action buttons with improved layout management
        layout = self.content_layout
        if layout:
            layout.insertWidget(layout.count() - 1, group)

        return group

    def add_setting_from_config(self, group_name: str, config: SettingConfig) -> QWidget:
        """Add setting from configuration object"""
        if config.setting_type == str:
            return self.add_text_setting(
                group_name, config.key, config.label,
                str(config.default_value), validator=config.validator
            )
        elif config.setting_type == bool:
            return self.add_boolean_setting(
                group_name, config.key, config.label, bool(config.default_value)
            )
        elif config.setting_type == int:
            return self.add_number_setting(
                group_name, config.key, config.label, int(config.default_value)
            )
        elif config.setting_type == float:
            return self.add_number_setting(
                group_name, config.key, config.label, float(config.default_value), 
                decimals=2
            )
        else:
            raise ValueError(f"Unsupported setting type: {config.setting_type}")

    def add_choice_from_config(self, group_name: str, config: ChoiceConfig) -> QComboBox:
        """Add choice setting from configuration object"""
        choices = [choice[0] for choice in config.choices]
        return self.add_choice_setting(
            group_name, config.key, config.label, 
            choices, config.default_index
        )

    def add_text_setting(self, group_name: str, setting_key: str,
                         label: str, default_value: str = "",
                         placeholder: str = "", validator: Optional[ValidationCallback] = None) -> FluentLineEdit:
        """Add a text input setting with enhanced validation"""
        group = self._get_or_create_group(group_name)

        field_edit = FluentLineEdit()
        field_edit.setText(default_value)
        if placeholder:
            field_edit.setPlaceholderText(placeholder)

        # Enhanced change handling with debouncing
        field_edit.textChanged.connect(
            partial(self._on_setting_changed_debounced, setting_key)
        )

        # Store validator if provided
        if validator:
            self._validators[setting_key] = validator
            field_edit.textChanged.connect(
                partial(self._validate_setting, setting_key, field_edit)
            )

        # Use addField from FluentFormGroup
        group.addField(setting_key, field_edit, label_text=label)
        self._current_values[setting_key] = default_value
        self._default_values[setting_key] = default_value
        self._setting_widgets[setting_key] = field_edit

        return field_edit

    def add_choice_setting(self, group_name: str, setting_key: str,
                           label: str, choices: List[str],
                           default_index: int = 0) -> QComboBox:
        """Add a choice dropdown setting with enhanced management"""
        group = self._get_or_create_group(group_name)

        combo = QComboBox()
        combo.addItems(choices)
        if choices and 0 <= default_index < len(choices):
            combo.setCurrentIndex(default_index)

        combo.currentTextChanged.connect(
            partial(self._on_setting_changed_debounced, setting_key)
        )

        # Apply enhanced styling
        self._apply_combo_styling(combo)

        group.addField(setting_key, combo, label_text=label)
        
        default_value = choices[default_index] if choices and 0 <= default_index < len(choices) else ""
        self._current_values[setting_key] = default_value
        self._default_values[setting_key] = default_value
        self._setting_widgets[setting_key] = combo

        return combo

    def add_boolean_setting(self, group_name: str, setting_key: str,
                            label: str, default_value: bool = False) -> FluentCheckBox:
        """Add a boolean checkbox setting with enhanced styling"""
        group = self._get_or_create_group(group_name)

        checkbox = FluentCheckBox(label)
        checkbox.setChecked(default_value)

        checkbox.toggled.connect(
            partial(self._on_setting_changed_debounced, setting_key)
        )

        group.addField(setting_key, checkbox, label_text="")
        self._current_values[setting_key] = default_value
        self._default_values[setting_key] = default_value
        self._setting_widgets[setting_key] = checkbox

        return checkbox

    def add_number_setting(self, group_name: str, setting_key: str,
                           label: str, default_value: Union[int, float] = 0,
                           min_value: Union[int, float] = 0, 
                           max_value: Union[int, float] = 100,
                           decimals: int = 0) -> Union[QSpinBox, QDoubleSpinBox]:
        """Add a number input setting with enhanced type handling"""
        group = self._get_or_create_group(group_name)

        if decimals > 0 or isinstance(default_value, float):
            spinbox = QDoubleSpinBox()
            spinbox.setDecimals(decimals)
            spinbox.setRange(float(min_value), float(max_value))
            spinbox.setValue(float(default_value))
            
            spinbox.valueChanged.connect(
                partial(self._on_setting_changed_debounced, setting_key)
            )
        else:
            spinbox = QSpinBox()
            spinbox.setRange(int(min_value), int(max_value))
            spinbox.setValue(int(default_value))
            
            spinbox.valueChanged.connect(
                partial(self._on_setting_changed_debounced, setting_key)
            )

        self._apply_spinbox_styling(spinbox)
        group.addField(setting_key, spinbox, label_text=label)
        self._current_values[setting_key] = default_value
        self._default_values[setting_key] = default_value
        self._setting_widgets[setting_key] = spinbox

        return spinbox

    def _apply_combo_styling(self, combo: QComboBox) -> None:
        """Apply enhanced combo box styling"""
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {theme_manager.get_color("input_background")};
                border: 1px solid {theme_manager.get_color("border")};
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 13px;
                min-width: 120px;
            }}
            QComboBox:hover {{
                border-color: {theme_manager.get_color("accent")};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
        """)

    def _apply_spinbox_styling(self, spinbox: Union[QSpinBox, QDoubleSpinBox]) -> None:
        """Apply enhanced spinbox styling"""
        spinbox.setStyleSheet(f"""
            QSpinBox, QDoubleSpinBox {{
                background-color: {theme_manager.get_color("input_background")};
                border: 1px solid {theme_manager.get_color("border")};
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 13px;
                min-width: 80px;
            }}
            QSpinBox:hover, QDoubleSpinBox:hover {{
                border-color: {theme_manager.get_color("accent")};
            }}
        """)

    def _get_or_create_group(self, group_name: str) -> FluentFormGroup:
        """Get existing group or create new one"""
        if group_name not in self._settings_groups:
            return self.add_settings_group(group_name, group_name)
        return self._settings_groups[group_name]

    def _on_setting_changed_debounced(self, setting_key: str, value: Any = None):
        """Handle setting value change with debouncing"""
        if value is None:
            # Get value from widget
            widget = self._setting_widgets.get(setting_key)
            if isinstance(widget, FluentLineEdit):
                value = widget.text()
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
            elif isinstance(widget, FluentCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = widget.value()
        
        self._pending_changes[setting_key] = value
        self._debounce_timer.start(300)  # 300ms debounce

    def _emit_deferred_changes(self):
        """Emit all pending changes after debounce period"""
        for setting_key, value in self._pending_changes.items():
            self._current_values[setting_key] = value
            self.setting_changed.emit(setting_key, value)
        
        self._pending_changes.clear()
        self._update_apply_button_state()

    def _validate_setting(self, setting_key: str, widget: QWidget, value: Any = None):
        """Validate setting value and provide visual feedback"""
        if setting_key not in self._validators:
            return True
        
        validator = self._validators[setting_key]
        if value is None:
            if isinstance(widget, FluentLineEdit):
                value = widget.text()
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
            elif isinstance(widget, FluentCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = widget.value()
        
        is_valid = validator(value)
        
        # Apply visual feedback
        if hasattr(widget, 'setStyleSheet'):
            if is_valid:
                widget.setStyleSheet("")  # Reset to default
            else:
                widget.setStyleSheet(f"""
                    border-color: {theme_manager.get_color("error")};
                    background-color: {theme_manager.get_color("error_background")};
                """)
        
        return is_valid

    def _update_apply_button_state(self):
        """Update apply button state based on changes"""
        has_changes = any(
            self._current_values.get(key) != self._default_values.get(key)
            for key in self._current_values.keys()
        )
        
        if hasattr(self, 'apply_button'):
            self.apply_button.setEnabled(has_changes)
            if has_changes:
                self.apply_button.setProperty("modified", True)
            else:
                self.apply_button.setProperty("modified", False)
            self.apply_button.style().unpolish(self.apply_button)
            self.apply_button.style().polish(self.apply_button)

    def _apply_settings(self):
        """Apply current settings with enhanced validation"""
        # Validate all settings
        all_valid = True
        for setting_key, widget in self._setting_widgets.items():
            if not self._validate_setting(setting_key, widget):
                all_valid = False

        if all_valid:
            # Emit settings applied signal
            self.settings_applied.emit(self._current_values.copy())
            # Reset the "modified" state
            self._default_values.update(self._current_values)
            self._update_apply_button_state()
        else:
            # Show validation error with sound feedback  
            # Could add proper error dialog here
            pass

    def _reset_settings(self):
        """Reset all settings to defaults with confirmation"""
        with self.batch_updates():
            for setting_key, default_value in self._default_values.items():
                widget = self._setting_widgets.get(setting_key)
                if isinstance(widget, FluentLineEdit):
                    widget.setText(str(default_value))
                elif isinstance(widget, QComboBox):
                    index = widget.findText(str(default_value))
                    if index >= 0:
                        widget.setCurrentIndex(index)
                elif isinstance(widget, FluentCheckBox):
                    widget.setChecked(bool(default_value))
                elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    widget.setValue(default_value)
        
        self._current_values.update(self._default_values)
        self.settings_reset.emit()
        self._update_apply_button_state()    # Enhanced public API with type safety
    def get_setting_value(self, setting_key: str) -> Optional[Any]:
        """Get current value of a setting"""
        return self._current_values.get(setting_key)

    def set_setting_value(self, setting_key: str, value: Any) -> bool:
        """Set value of a setting with validation"""
        if setting_key not in self._setting_widgets:
            return False
        
        try:
            widget = self._setting_widgets[setting_key]
            if isinstance(widget, FluentLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, QComboBox):
                index = widget.findText(str(value))
                if index >= 0:
                    widget.setCurrentIndex(index)
                else:
                    return False
            elif isinstance(widget, FluentCheckBox):
                widget.setChecked(bool(value))
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(value)
            
            self._current_values[setting_key] = value
            self._update_apply_button_state()
            return True
        except Exception:
            return False

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings as a dictionary"""
        return self._current_values.copy()

    def set_settings(self, settings: Dict[str, Any]) -> Dict[str, bool]:
        """Set multiple settings at once, returns success status for each"""
        results = {}
        with self.batch_updates():
            for key, value in settings.items():
                results[key] = self.set_setting_value(key, value)
        return results

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes"""
        return any(
            self._current_values.get(key) != self._default_values.get(key)
            for key in self._current_values.keys()
        )

    def validate_all_settings(self) -> Dict[str, bool]:
        """Validate all settings and return results"""
        results = {}
        for setting_key, widget in self._setting_widgets.items():
            results[setting_key] = self._validate_setting(setting_key, widget)
        return results

    def clear_settings(self) -> None:
        """Clear all settings and groups"""
        with self.batch_updates():
            for group in self._settings_groups.values():
                if hasattr(group, 'deleteLater'):
                    group.deleteLater()
            
            self._settings_groups.clear()
            self._current_values.clear()
            self._default_values.clear()
            self._validators.clear()
            self._setting_widgets.clear()

    def get_setting_groups(self) -> List[str]:
        """Get list of all setting group names"""
        return list(self._settings_groups.keys())

    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, '_debounce_timer'):
                self._debounce_timer.stop()
            self.clear_settings()
        except:
            pass  # Ignore cleanup errors


class FluentPropertiesEditor(FluentCompositeWidget):
    """
    Properties editor panel for editing object properties with
    automatic type detection and validation.
    
    Enhanced with modern Python features, better performance, and type safety.
    """

    property_changed = Signal(str, object)  # property_name, new_value
    properties_applied = Signal(dict)  # all_properties

    def __init__(self, title: str = "Properties", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._properties: Dict[str, Any] = {}
        self._property_descriptors: Dict[str, PropertyDescriptor] = {}
        self._controls: Dict[str, QWidget] = {}
        self._categories: Dict[str, List[str]] = {}
        self._category_widgets: Dict[str, QWidget] = {}
        self._debounce_timer = QTimer(self)
        self._pending_changes: Dict[str, Any] = {}

        # Setup debouncing
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_deferred_changes)

        self._setup_ui(title)
        self._apply_enhanced_styling()

    def _setup_ui(self, title: str):
        """Setup the properties editor UI with enhanced layout"""
        layout = FluentLayoutBuilder.create_vertical_layout()
        self.setLayout(layout)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color("text")};
                padding: 8px 0px;
            }}
        """)
        layout.addWidget(title_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.properties_widget = QWidget()
        self.properties_layout = FluentLayoutBuilder.create_vertical_layout(spacing=4)
        self.properties_widget.setLayout(self.properties_layout)

        self.scroll_area.setWidget(self.properties_widget)
        layout.addWidget(self.scroll_area)

        self.properties_layout.addStretch()

    def _apply_enhanced_styling(self) -> None:
        """Apply enhanced styling with caching"""
        theme_key = getattr(theme_manager, 'get_current_theme_name', lambda: 'default')()
        cached_style = _cache_manager.get_cached_style(theme_key, 'properties_editor')
        
        if not cached_style:
            cached_style = f"""
                FluentPropertiesEditor {{
                    background-color: {theme_manager.get_color("surface")};
                    border: 1px solid {theme_manager.get_color("border")};
                    border-radius: 8px;
                }}
                QScrollArea {{
                    background-color: transparent;
                    border: none;
                }}
            """
            _cache_manager.set_cached_style(theme_key, 'properties_editor', cached_style)
        
        self.setStyleSheet(cached_style)

    @contextmanager
    def batch_updates(self):
        """Context manager for batching multiple property updates"""
        self.setUpdatesEnabled(False)
        try:
            yield
        finally:
            self.setUpdatesEnabled(True)
            self.update()

    def set_object_properties(self, obj: object, property_names: Optional[List[str]] = None, 
                             categories: Optional[Dict[str, List[str]]] = None):
        """Set object to edit properties for with enhanced categorization"""
        self.clear_properties()

        if property_names is None:
            property_names = [attr for attr in dir(obj)
                              if not attr.startswith('_') and
                              not callable(getattr(obj, attr))]

        # Setup categories
        if categories:
            self._categories = categories.copy()
        else:
            self._categories = {"General": property_names}

        with self.batch_updates():
            for category, props in self._categories.items():
                self._add_category_section(category)
                
                for prop_name in props:
                    if prop_name in property_names and hasattr(obj, prop_name):
                        value = getattr(obj, prop_name)
                        descriptor = PropertyDescriptor(
                            name=prop_name,
                            value=value,
                            prop_type=type(value),
                            category=category
                        )
                        self.add_property_from_descriptor(descriptor)

    def _add_category_section(self, category: str):
        """Add a category section header"""
        if category in self._category_widgets:
            return
        
        category_frame = QFrame()
        category_frame.setFrameShape(QFrame.Shape.StyledPanel)
        category_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme_manager.get_color("hover")};
                border-radius: 4px;
                margin: 4px 0px;
            }}
        """)
        
        category_layout = FluentLayoutBuilder.create_vertical_layout(spacing=2)
        category_frame.setLayout(category_layout)
        
        category_label = QLabel(category)
        category_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        category_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color("text")};
                padding: 6px 8px;
            }}
        """)
        category_layout.addWidget(category_label)
        
        self.properties_layout.insertWidget(self.properties_layout.count() - 1, category_frame)
        self._category_widgets[category] = category_frame

    def add_property_from_descriptor(self, descriptor: PropertyDescriptor):
        """Add property from descriptor object"""
        self.add_property(
            descriptor.name, 
            descriptor.value, 
            descriptor.prop_type,
            descriptor.editable,
            descriptor.validator,
            descriptor.effective_display_name,
            descriptor.category        )

    def add_property(self, name: str, value: Any, prop_type: Optional[type] = None,
                     editable: bool = True, validator: Optional[ValidationCallback] = None,
                     display_name: Optional[str] = None, category: str = "General"):
        """Add a property to edit with enhanced configuration"""
        if prop_type is None:
            prop_type = type(value)

        control = self._create_control_for_type(name, prop_type, value, editable, validator)
        if control is None:
            return

        # Create property row
        prop_frame = self._create_property_row(
            display_name or name.replace('_', ' ').title(), 
            control
        )

        # Store property data
        descriptor = PropertyDescriptor(
            name=name,
            value=value,
            prop_type=prop_type,
            editable=editable,
            validator=validator,
            display_name=display_name,
            category=category
        )
        
        self._properties[name] = value
        self._property_descriptors[name] = descriptor
        self._controls[name] = control

        # Add to appropriate category
        if category not in self._category_widgets:
            self._add_category_section(category)
        
        category_widget = self._category_widgets[category]
        if category_widget and hasattr(category_widget, 'layout'):
            layout = category_widget.layout()
            if layout and hasattr(layout, 'addWidget'):
                layout.addWidget(prop_frame)

    def _create_property_row(self, label_text: str, control: QWidget) -> QFrame:
        """Create a property row with consistent styling"""
        prop_frame = QFrame()
        prop_layout = FluentLayoutBuilder.create_horizontal_layout()
        prop_frame.setLayout(prop_layout)

        name_label = QLabel(label_text + ":")
        name_label.setMinimumWidth(120)
        name_label.setFont(QFont("Segoe UI", 9))
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color("text")};
                padding: 4px 0px;
            }}
        """)
        prop_layout.addWidget(name_label)

        prop_layout.addWidget(control, 1)  # Give control more space

        return prop_frame

    def _emit_deferred_changes(self):
        """Emit all pending property changes after debounce period"""
        for prop_name, value in self._pending_changes.items():
            self._properties[prop_name] = value
            self.property_changed.emit(prop_name, value)
            self._pending_changes.clear()

    def _create_control_for_type(self, prop_name: str, prop_type: type, value: Any,
                                editable: bool = True, validator: Optional[ValidationCallback] = None) -> Optional[QWidget]:
        """Create appropriate control for property type with enhanced options"""
        control: Optional[QWidget] = None
        
        if not editable:
            # Read-only display
            read_only_control = QLineEdit()
            read_only_control.setText(str(value))
            read_only_control.setReadOnly(True)
            read_only_control.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {theme_manager.get_color("disabled_background")};
                    color: {theme_manager.get_color("text_disabled")};
                    border: 1px solid {theme_manager.get_color("border")};
                    border-radius: 4px;
                    padding: 4px 8px;
                }}
            """)
            return read_only_control
        
        if prop_type == str:
            edit_control = FluentLineEdit()
            edit_control.setText(str(value))
            edit_control.textChanged.connect(
                partial(self._on_property_changed_debounced, prop_name)
            )
            
            if validator:
                edit_control.textChanged.connect(
                    partial(self._validate_property, prop_name, edit_control, validator)
                )
            
            control = edit_control

        elif prop_type == bool:
            check_control = FluentCheckBox()
            check_control.setChecked(bool(value))
            check_control.toggled.connect(
                partial(self._on_property_changed_debounced, prop_name)
            )
            control = check_control

        elif prop_type == int:
            spin_control = QSpinBox()
            spin_control.setRange(-2147483648, 2147483647)  # Max int range
            spin_control.setValue(int(value))
            spin_control.valueChanged.connect(
                partial(self._on_property_changed_debounced, prop_name)
            )
            self._apply_spinbox_styling(spin_control)
            control = spin_control

        elif prop_type == float:
            float_spin_control = QDoubleSpinBox()
            float_spin_control.setDecimals(4)
            float_spin_control.setRange(-1e10, 1e10)
            float_spin_control.setValue(float(value))
            float_spin_control.valueChanged.connect(
                partial(self._on_property_changed_debounced, prop_name)
            )
            self._apply_spinbox_styling(float_spin_control)
            control = float_spin_control

        else:  # Default for unknown types
            default_edit_control = QLineEdit()
            default_edit_control.setText(str(value))
            default_edit_control.setReadOnly(True)
            default_edit_control.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {theme_manager.get_color("disabled_background")};
                    color: {theme_manager.get_color("text_disabled")};
                    border: 1px solid {theme_manager.get_color("border")};
                    border-radius: 4px;
                    padding: 4px 8px;
                }}
            """)
            control = default_edit_control
            
        return control

    def _apply_spinbox_styling(self, spinbox: Union[QSpinBox, QDoubleSpinBox]) -> None:
        """Apply enhanced spinbox styling"""
        spinbox.setStyleSheet(f"""
            QSpinBox, QDoubleSpinBox {{
                background-color: {theme_manager.get_color("input_background")};
                border: 1px solid {theme_manager.get_color("border")};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                min-width: 80px;
            }}
            QSpinBox:hover, QDoubleSpinBox:hover {{
                border-color: {theme_manager.get_color("accent")};
            }}
        """)

    def _on_property_changed_debounced(self, prop_name: str, value: Any = None):
        """Handle property value change with debouncing"""
        if value is None:
            # Get value from widget
            widget = self._controls.get(prop_name)
            if isinstance(widget, FluentLineEdit):
                value = widget.text()
            elif isinstance(widget, FluentCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = widget.value()
            elif isinstance(widget, QLineEdit):
                value = widget.text()
        
        self._pending_changes[prop_name] = value
        self._debounce_timer.start(300)  # 300ms debounce

    def _validate_property(self, prop_name: str, widget: QWidget, 
                          validator: ValidationCallback, value: Any = None):
        """Validate property value and provide visual feedback"""
        if value is None:
            if isinstance(widget, (FluentLineEdit, QLineEdit)):
                value = widget.text()
            elif isinstance(widget, FluentCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = widget.value()
        
        is_valid = validator(value)
        
        # Apply visual feedback
        if hasattr(widget, 'setStyleSheet'):
            if is_valid:
                # Reset to default styling based on widget type
                if isinstance(widget, FluentLineEdit):
                    widget.setStyleSheet("")
                elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    self._apply_spinbox_styling(widget)
            else:
                widget.setStyleSheet(f"""
                    border-color: {theme_manager.get_color("error")};
                    background-color: {theme_manager.get_color("error_background")};
                """)
        
        return is_valid

    def _on_property_changed(self, name: str, value: Any):
        """Handle property value change (legacy method for compatibility)"""
        self._properties[name] = value
        self.property_changed.emit(name, value)

    def clear_properties(self):
        """Clear all properties with enhanced cleanup"""
        with self.batch_updates():
            # Clear categories first
            for category_widget in self._category_widgets.values():
                if hasattr(category_widget, 'deleteLater'):
                    category_widget.deleteLater()
            
            # Clear main properties layout
            while self.properties_layout.count() > 1:  # Keep the stretch
                item = self.properties_layout.takeAt(0)
                if item and item.widget():
                    item.widget().deleteLater()

        self._properties.clear()
        self._property_descriptors.clear()
        self._controls.clear()
        self._categories.clear()
        self._category_widgets.clear()
        self._pending_changes.clear()

    def get_property_value(self, name: str) -> Any:
        """Get current value of a property"""
        return self._properties.get(name)

    def set_property_value(self, name: str, value: Any) -> bool:
        """Set property value programmatically"""
        if name not in self._controls:
            return False
        
        try:
            widget = self._controls[name]
            if isinstance(widget, FluentLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, FluentCheckBox):
                widget.setChecked(bool(value))
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(value)
            elif isinstance(widget, QLineEdit):
                widget.setText(str(value))
            
            self._properties[name] = value
            return True
        except Exception:
            return False

    def get_all_properties(self) -> Dict[str, Any]:
        """Get all current properties as a dictionary"""
        return self._properties.copy()

    def set_properties(self, properties: Dict[str, Any]) -> Dict[str, bool]:
        """Set multiple properties at once"""
        results = {}
        with self.batch_updates():
            for name, value in properties.items():
                results[name] = self.set_property_value(name, value)
        return results

    def get_property_categories(self) -> List[str]:
        """Get list of all property categories"""
        return list(self._categories.keys())

    def get_properties_by_category(self, category: str) -> Dict[str, Any]:
        """Get all properties in a specific category"""
        if category not in self._categories:
            return {}
        
        return {
            prop_name: self._properties.get(prop_name)
            for prop_name in self._categories[category]
            if prop_name in self._properties
        }

    def validate_all_properties(self) -> Dict[str, bool]:
        """Validate all properties and return results"""
        results = {}
        for prop_name, descriptor in self._property_descriptors.items():
            if descriptor.validator:
                widget = self._controls.get(prop_name)
                if widget:
                    results[prop_name] = self._validate_property(
                        prop_name, widget, descriptor.validator
                    )
            else:
                results[prop_name] = True
        return results

    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, '_debounce_timer'):
                self._debounce_timer.stop()
            self.clear_properties()
        except:
            pass  # Ignore cleanup errors


class FluentFormDialog(FluentCompositeWidget):
    """
    High-level form dialog that automatically creates form fields
    and handles validation and submission.
    
    Enhanced with modern Python features, better validation, and type safety.
    """

    submitted = Signal(dict)  # form_data
    cancelled = Signal()
    validation_changed = Signal(bool)  # is_valid

    def __init__(self, title: str = "Form", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._form_fields: Dict[str, QWidget] = {}
        self._validators: Dict[str, ValidationCallback] = {}
        self._required_fields: set[str] = set()
        self._field_configs: Dict[str, Any] = {}
        self._validation_state: Dict[str, bool] = {}
        self._debounce_timer = QTimer(self)

        # Setup debouncing for validation
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._perform_validation)

        self._setup_ui(title)
        self._apply_enhanced_styling()

    def _setup_ui(self, title: str):
        """Setup form dialog UI with enhanced layout"""
        main_layout = FluentLayoutBuilder.create_vertical_layout()
        self.setLayout(main_layout)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color("text")};
                padding: 12px 0px;
            }}
        """)
        main_layout.addWidget(title_label)

        # Create scrollable form area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.form_widget = QWidget()
        self.form_layout = FluentLayoutBuilder.create_vertical_layout()
        self.form_widget.setLayout(self.form_layout)
        
        scroll_area.setWidget(self.form_widget)
        main_layout.addWidget(scroll_area)

        # Setup buttons
        self._setup_buttons(main_layout)

    def _apply_enhanced_styling(self) -> None:
        """Apply enhanced styling with caching"""
        theme_key = getattr(theme_manager, 'get_current_theme_name', lambda: 'default')()
        cached_style = _cache_manager.get_cached_style(theme_key, 'form_dialog')
        
        if not cached_style:
            cached_style = f"""
                FluentFormDialog {{
                    background-color: {theme_manager.get_color("surface")};
                    border: 1px solid {theme_manager.get_color("border")};
                    border-radius: 12px;
                }}
                QScrollArea {{
                    background-color: transparent;
                    border: none;
                }}
            """
            _cache_manager.set_cached_style(theme_key, 'form_dialog', cached_style)
        
        self.setStyleSheet(cached_style)

    @contextmanager
    def batch_updates(self):
        """Context manager for batching multiple form updates"""
        self.setUpdatesEnabled(False)
        try:
            yield
        finally:
            self.setUpdatesEnabled(True)
            self.update()

    def _setup_buttons(self, main_layout: QVBoxLayout):
        """Setup form buttons with enhanced styling"""
        button_frame = QFrame()
        button_layout = FluentLayoutBuilder.create_horizontal_layout()
        button_frame.setLayout(button_layout)

        button_layout.addStretch()

        self.cancel_button = FluentStandardButton(
            "Cancel", 
            size=(80, 32),
            variant=FluentStandardButton.OUTLINE
        )
        self.cancel_button.clicked.connect(self._on_cancel)
        FluentMicroInteraction.button_press(self.cancel_button)
        button_layout.addWidget(self.cancel_button)

        self.submit_button = FluentStandardButton(
            "Submit", 
            size=(80, 32),
            variant=FluentStandardButton.PRIMARY
        )
        self.submit_button.clicked.connect(self._on_submit)
        self.submit_button.setEnabled(False)  # Disabled until form is valid
        FluentMicroInteraction.button_press(self.submit_button)
        button_layout.addWidget(self.submit_button)

        main_layout.addWidget(button_frame)

    @dataclass(frozen=True)
    class FieldConfig:
        """Configuration for form fields"""
        name: str
        label: str
        field_type: type = str
        required: bool = False
        validator: Optional[ValidationCallback] = None
        choices: Optional[List[str]] = None
        placeholder: str = ""
        help_text: str = ""
        min_value: Optional[Union[int, float]] = None
        max_value: Optional[Union[int, float]] = None

    def add_field_from_config(self, config: FieldConfig) -> QWidget:
        """Add field from configuration object"""
        if config.field_type == str:
            return self.add_text_field(
                config.name, config.label, config.required, 
                config.validator, config.placeholder
            )
        elif config.field_type == bool:
            return self.add_boolean_field(config.name, config.label, config.required)
        elif config.choices:
            return self.add_choice_field(
                config.name, config.label, config.choices, config.required
            )
        elif config.field_type in (int, float):
            return self.add_number_field(
                config.name, config.label, config.required, 
                config.min_value, config.max_value, config.field_type
            )
        else:
            raise ValueError(f"Unsupported field type: {config.field_type}")

    def add_text_field(self, field_name: str, label: str,
                       required: bool = False, validator: Optional[ValidationCallback] = None,
                       placeholder: str = "") -> FluentLineEdit:
        """Add text input field with enhanced validation"""
        field_edit = FluentLineEdit()
        field_edit.setPlaceholderText(placeholder or f"Enter {label.lower()}")

        # Connect validation with debouncing
        field_edit.textChanged.connect(self._trigger_validation)

        self._add_form_row(label, field_edit, required)
        self._form_fields[field_name] = field_edit
        self._field_configs[field_name] = {
            'type': str, 'required': required, 'validator': validator
        }

        if validator:
            self._validators[field_name] = validator
        if required:
            self._required_fields.add(field_name)

        return field_edit

    def add_choice_field(self, field_name: str, label: str,
                         choices: List[str], required: bool = False) -> QComboBox:
        """Add choice field with enhanced styling"""
        combo = QComboBox()
        if not required:
            combo.addItem("-- Select --", None)
        combo.addItems(choices)

        combo.currentTextChanged.connect(self._trigger_validation)
        self._apply_combo_styling(combo)

        self._add_form_row(label, combo, required)
        self._form_fields[field_name] = combo
        self._field_configs[field_name] = {
            'type': str, 'required': required, 'choices': choices
        }

        if required:
            self._required_fields.add(field_name)

        return combo

    def add_boolean_field(self, field_name: str, label: str, 
                          required: bool = False) -> FluentCheckBox:
        """Add boolean checkbox field"""
        checkbox = FluentCheckBox(label)
        checkbox.toggled.connect(self._trigger_validation)

        # For checkbox, we don't need separate label
        self._add_form_row("", checkbox, required)
        self._form_fields[field_name] = checkbox
        self._field_configs[field_name] = {
            'type': bool, 'required': required
        }

        if required:
            self._required_fields.add(field_name)

        return checkbox

    def add_number_field(self, field_name: str, label: str,
                         required: bool = False, min_value: Optional[Union[int, float]] = None,
                         max_value: Optional[Union[int, float]] = None,
                         number_type: type = int) -> Union[QSpinBox, QDoubleSpinBox]:
        """Add number input field with type-specific handling"""
        if number_type == float:
            spinbox = QDoubleSpinBox()
            spinbox.setDecimals(2)
            spinbox.setRange(
                float(min_value) if min_value is not None else -1e10,
                float(max_value) if max_value is not None else 1e10
            )
        else:
            spinbox = QSpinBox()
            spinbox.setRange(
                int(min_value) if min_value is not None else -2147483648,
                int(max_value) if max_value is not None else 2147483647
            )

        spinbox.valueChanged.connect(self._trigger_validation)
        self._apply_spinbox_styling(spinbox)

        self._add_form_row(label, spinbox, required)
        self._form_fields[field_name] = spinbox
        self._field_configs[field_name] = {
            'type': number_type, 'required': required, 
            'min_value': min_value, 'max_value': max_value
        }

        if required:
            self._required_fields.add(field_name)

        return spinbox

    def _apply_combo_styling(self, combo: QComboBox) -> None:
        """Apply enhanced combo box styling"""
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {theme_manager.get_color("input_background")};
                border: 1px solid {theme_manager.get_color("border")};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 150px;
            }}
            QComboBox:hover {{
                border-color: {theme_manager.get_color("accent")};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
        """)

    def _apply_spinbox_styling(self, spinbox: Union[QSpinBox, QDoubleSpinBox]) -> None:
        """Apply enhanced spinbox styling"""
        spinbox.setStyleSheet(f"""
            QSpinBox, QDoubleSpinBox {{
                background-color: {theme_manager.get_color("input_background")};
                border: 1px solid {theme_manager.get_color("border")};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 100px;
            }}
            QSpinBox:hover, QDoubleSpinBox:hover {{
                border-color: {theme_manager.get_color("accent")};
            }}
        """)

    def _add_form_row(self, label: str, widget: QWidget, required: bool = False):
        """Add a form row with label and widget"""
        row_frame = QFrame()
        row_layout = FluentLayoutBuilder.create_horizontal_layout()
        row_frame.setLayout(row_layout)

        if label:  # Only add label if provided
            label_text = label + ("*" if required else "") + ":"
            label_widget = QLabel(label_text)
            label_widget.setMinimumWidth(120)
            label_widget.setStyleSheet(f"""
                QLabel {{
                    color: {theme_manager.get_color("text")};
                    font-size: 13px;
                    padding: 4px 0px;
                }}
            """)
            if required:
                label_widget.setStyleSheet(label_widget.styleSheet() + f"""
                    QLabel {{
                        font-weight: bold;
                    }}
                """)

            row_layout.addWidget(label_widget)

        row_layout.addWidget(widget, 1)  # Give widget more space

        self.form_layout.addWidget(row_frame)

    def _trigger_validation(self):
        """Trigger validation with debouncing"""
        self._debounce_timer.start(200)  # 200ms debounce

    def _perform_validation(self) -> bool:
        """Perform comprehensive form validation"""
        is_valid = True
        validation_results = {}

        for field_name, widget in self._form_fields.items():
            field_valid = self._validate_field(field_name, widget)
            validation_results[field_name] = field_valid
            if not field_valid:
                is_valid = False

        self._validation_state = validation_results
        self.submit_button.setEnabled(is_valid)
        self.validation_changed.emit(is_valid)

        return is_valid

    def _validate_field(self, field_name: str, widget: QWidget) -> bool:
        """Validate individual field"""
        config = self._field_configs.get(field_name, {})
        is_required = config.get('required', False)
        validator = self._validators.get(field_name)

        # Get field value
        value = self._get_field_value(field_name, widget)

        # Check required fields
        if is_required and (value is None or str(value).strip() == ""):
            self._apply_validation_style(widget, False)
            return False

        # Apply custom validator
        if validator and not validator(value):
            self._apply_validation_style(widget, False)
            return False

        # Field is valid
        self._apply_validation_style(widget, True)
        return True

    def _get_field_value(self, field_name: str, widget: QWidget) -> Any:
        """Get value from form field"""
        if isinstance(widget, FluentLineEdit):
            return widget.text()
        elif isinstance(widget, QComboBox):
            return widget.currentText() if widget.currentData() is not None else None
        elif isinstance(widget, FluentCheckBox):
            return widget.isChecked()
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.value()
        else:
            return None

    def _apply_validation_style(self, widget: QWidget, is_valid: bool):
        """Apply validation styling to widget"""
        if not hasattr(widget, 'setStyleSheet'):
            return

        if is_valid:
            # Reset to default styling
            if isinstance(widget, FluentLineEdit):
                widget.setStyleSheet("")
            elif isinstance(widget, QComboBox):
                self._apply_combo_styling(widget)
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                self._apply_spinbox_styling(widget)
        else:
            # Apply error styling
            error_style = f"""
                border-color: {theme_manager.get_color("error")};
                background-color: {theme_manager.get_color("error_background")};
            """
            current_style = widget.styleSheet()
            widget.setStyleSheet(current_style + error_style)

    def _on_submit(self):
        """Handle form submission with validation"""
        if not self._perform_validation():
            return

        form_data = {}
        for field_name, widget in self._form_fields.items():
            form_data[field_name] = self._get_field_value(field_name, widget)

        self.submitted.emit(form_data)

    def _on_cancel(self):
        """Handle form cancellation"""
        self.cancelled.emit()

    def get_form_data(self) -> Dict[str, Any]:
        """Get current form data"""
        return {
            field_name: self._get_field_value(field_name, widget)
            for field_name, widget in self._form_fields.items()
        }

    def set_form_data(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """Set form data programmatically"""
        results = {}
        with self.batch_updates():
            for field_name, value in data.items():
                if field_name in self._form_fields:
                    results[field_name] = self._set_field_value(field_name, value)
                else:
                    results[field_name] = False
        
        self._trigger_validation()
        return results

    def _set_field_value(self, field_name: str, value: Any) -> bool:
        """Set value for specific field"""
        widget = self._form_fields.get(field_name)
        if not widget:
            return False

        try:
            if isinstance(widget, FluentLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, QComboBox):
                index = widget.findText(str(value))
                if index >= 0:
                    widget.setCurrentIndex(index)
                else:
                    return False
            elif isinstance(widget, FluentCheckBox):
                widget.setChecked(bool(value))
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(value)
            return True
        except Exception:
            return False

    def clear_form(self):
        """Clear all form fields"""
        with self.batch_updates():
            for field_name, widget in self._form_fields.items():
                if isinstance(widget, FluentLineEdit):
                    widget.clear()
                elif isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)
                elif isinstance(widget, FluentCheckBox):
                    widget.setChecked(False)
                elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    widget.setValue(0)
        
        self._trigger_validation()

    def get_validation_state(self) -> Dict[str, bool]:
        """Get current validation state for all fields"""
        return self._validation_state.copy()

    def is_form_valid(self) -> bool:
        """Check if entire form is currently valid"""
        return all(self._validation_state.values()) if self._validation_state else False

    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, '_debounce_timer'):
                self._debounce_timer.stop()
        except:
            pass  # Ignore cleanup errors


class FluentConfirmationDialog(FluentCompositeWidget):
    """
    Standardized confirmation dialog with customizable actions and animations.
    
    Enhanced with modern Python features, better accessibility, and flexible configuration.
    """

    confirmed = Signal()
    rejected = Signal()
    button_clicked = Signal(str)  # button_id

    @dataclass(frozen=True)
    class DialogConfig:
        """Configuration for confirmation dialog"""
        title: str = "Confirm"
        message: str = "Are you sure?"
        confirm_text: str = "Yes"
        cancel_text: str = "No"
        confirm_variant: str = FluentStandardButton.PRIMARY
        cancel_variant: str = FluentStandardButton.OUTLINE
        icon: Optional[QIcon] = None
        danger_mode: bool = False
        auto_close: bool = True
        timeout: int = 0  # Auto-close timeout in seconds (0 = no timeout)

    def __init__(self, config: Optional[DialogConfig] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._config = config or self.DialogConfig()
        self._auto_close_timer: Optional[QTimer] = None
        self._entrance_animation: Optional[QPropertyAnimation] = None
        self._exit_animation: Optional[QPropertyAnimation] = None

        self._setup_ui()
        self._setup_animations()
        self._apply_enhanced_styling()

        # Setup auto-close timer if specified
        if self._config.timeout > 0:
            self._setup_auto_close_timer()

    @classmethod
    def create_simple(cls, message: str, title: str = "Confirm", 
                      parent: Optional[QWidget] = None) -> FluentConfirmationDialog:
        """Factory method for simple confirmation dialog"""
        config = cls.DialogConfig(title=title, message=message)
        return cls(config, parent)

    @classmethod
    def create_danger(cls, message: str, title: str = "Warning", 
                      confirm_text: str = "Delete", parent: Optional[QWidget] = None) -> FluentConfirmationDialog:
        """Factory method for dangerous action confirmation"""
        config = cls.DialogConfig(
            title=title, 
            message=message, 
            confirm_text=confirm_text,
            confirm_variant=FluentStandardButton.DANGER,
            danger_mode=True
        )
        return cls(config, parent)

    @classmethod  
    def create_info(cls, message: str, title: str = "Information",
                    confirm_text: str = "OK", parent: Optional[QWidget] = None) -> FluentConfirmationDialog:
        """Factory method for information dialog (single button)"""
        config = cls.DialogConfig(
            title=title,
            message=message, 
            confirm_text=confirm_text,
            cancel_text=""  # No cancel button
        )
        return cls(config, parent)

    def _setup_ui(self):
        """Setup confirmation dialog UI with enhanced layout"""
        layout = FluentLayoutBuilder.create_vertical_layout(spacing=16)
        self.setLayout(layout)

        # Icon and title row
        if self._config.icon or self._config.title:
            header_frame = QFrame()
            header_layout = FluentLayoutBuilder.create_horizontal_layout(spacing=12)
            header_frame.setLayout(header_layout)

            if self._config.icon:
                icon_label = QLabel()
                icon_label.setPixmap(self._config.icon.pixmap(32, 32))
                header_layout.addWidget(icon_label)

            if self._config.title:
                title_label = QLabel(self._config.title)
                title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
                title_label.setStyleSheet(f"""
                    QLabel {{
                        color: {theme_manager.get_color("text")};
                    }}
                """)
                if self._config.danger_mode:
                    title_label.setStyleSheet(title_label.styleSheet() + f"""
                        QLabel {{
                            color: {theme_manager.get_color("error")};
                        }}
                    """)
                header_layout.addWidget(title_label)

            header_layout.addStretch()
            layout.addWidget(header_frame)

        # Message
        message_label = QLabel(self._config.message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Segoe UI", 10))
        message_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_manager.get_color("text")};
                line-height: 1.4;
                padding: 8px 0px;
            }}
        """)
        layout.addWidget(message_label)

        # Buttons
        self._setup_buttons(layout)

    def _setup_buttons(self, layout: QVBoxLayout):
        """Setup dialog buttons with enhanced styling"""
        button_frame = QFrame()
        button_layout = FluentLayoutBuilder.create_horizontal_layout()
        button_frame.setLayout(button_layout)

        button_layout.addStretch()

        # Cancel button (if specified)
        if self._config.cancel_text:
            self.cancel_button = FluentStandardButton(
                self._config.cancel_text, 
                size=(80, 32),
                variant=self._config.cancel_variant
            )
            self.cancel_button.clicked.connect(self._on_cancel)
            FluentMicroInteraction.button_press(self.cancel_button)
            button_layout.addWidget(self.cancel_button)

        # Confirm button
        self.confirm_button = FluentStandardButton(
            self._config.confirm_text, 
            size=(80, 32),
            variant=self._config.confirm_variant
        )
        self.confirm_button.clicked.connect(self._on_confirm)
        FluentMicroInteraction.button_press(self.confirm_button)
        
        # Set as default button for Enter key
        self.confirm_button.setDefault(True)
        
        button_layout.addWidget(self.confirm_button)

        layout.addWidget(button_frame)

    def _apply_enhanced_styling(self) -> None:
        """Apply enhanced styling with theme awareness"""
        theme_key = getattr(theme_manager, 'get_current_theme_name', lambda: 'default')()
        cached_style = _cache_manager.get_cached_style(theme_key, 'confirmation_dialog')
        
        if not cached_style:
            border_color = theme_manager.get_color("error") if self._config.danger_mode else theme_manager.get_color("border")
            
            cached_style = f"""
                FluentConfirmationDialog {{
                    background-color: {theme_manager.get_color("surface")};
                    border: 2px solid {border_color};
                    border-radius: 12px;
                    padding: 16px;
                }}
            """
            _cache_manager.set_cached_style(theme_key, 'confirmation_dialog', cached_style)
        
        self.setStyleSheet(cached_style)

    def _setup_animations(self):
        """Setup entrance and exit animations"""
        if not isinstance(self, QWidget):
            return
            
        # Entrance animation (fade in + scale)
        self._entrance_animation = FluentTransition.create_transition(
            self, FluentTransition.FADE, duration=250
        )
        
        # Exit animation (fade out)
        self._exit_animation = FluentTransition.create_transition(
            self, FluentTransition.FADE, duration=200
        )
        
        if self._exit_animation:
            self._exit_animation.finished.connect(self._on_exit_animation_finished)

    def _setup_auto_close_timer(self):
        """Setup auto-close timer for timed dialogs"""
        self._auto_close_timer = QTimer(self)
        self._auto_close_timer.setSingleShot(True)
        self._auto_close_timer.timeout.connect(self._on_timeout)
        
        # Update button text with countdown
        self._update_countdown_text()

    def _update_countdown_text(self):
        """Update button text with countdown"""
        if not self._auto_close_timer or not hasattr(self, 'confirm_button'):
            return
            
        remaining = self._config.timeout - (self._config.timeout - self._auto_close_timer.remainingTime() // 1000)
        if remaining > 0:
            original_text = self._config.confirm_text
            self.confirm_button.setText(f"{original_text} ({remaining})")
            QTimer.singleShot(1000, self._update_countdown_text)
        else:
            self.confirm_button.setText(self._config.confirm_text)

    def _on_confirm(self):
        """Handle confirmation with proper cleanup"""
        self.button_clicked.emit("confirm")
        self.confirmed.emit()
        if self._config.auto_close:
            self._close_with_animation()

    def _on_cancel(self):
        """Handle cancellation with proper cleanup"""
        self.button_clicked.emit("cancel")
        self.rejected.emit()
        if self._config.auto_close:
            self._close_with_animation()

    def _on_timeout(self):
        """Handle timeout auto-close"""
        self.button_clicked.emit("timeout")
        self.confirmed.emit()  # Default to confirm on timeout
        if self._config.auto_close:
            self._close_with_animation()

    def show_animated(self):
        """Show dialog with entrance animation"""
        self.show()
        
        if self._entrance_animation and hasattr(self._entrance_animation, 'start'):
            # Setup entrance animation properties
            if hasattr(self, 'setGraphicsEffect'):
                from PySide6.QtWidgets import QGraphicsOpacityEffect
                effect = QGraphicsOpacityEffect(self)
                effect.setOpacity(0.0)
                self.setGraphicsEffect(effect)
                
                # Animate opacity
                if hasattr(self._entrance_animation, 'setTargetObject'):
                    self._entrance_animation.setTargetObject(effect)
                    self._entrance_animation.setPropertyName(b"opacity")
                    self._entrance_animation.setStartValue(0.0)
                    self._entrance_animation.setEndValue(1.0)
                    self._entrance_animation.start()
        
        # Start auto-close timer if configured
        if self._auto_close_timer:
            self._auto_close_timer.start(self._config.timeout * 1000)

    def _close_with_animation(self):
        """Close dialog with exit animation"""
        if self._exit_animation and hasattr(self._exit_animation, 'start'):
            # Setup exit animation
            effect = self.graphicsEffect()
            if effect and hasattr(self._exit_animation, 'setTargetObject'):
                self._exit_animation.setTargetObject(effect)
                self._exit_animation.setPropertyName(b"opacity")
                self._exit_animation.setStartValue(1.0)
                self._exit_animation.setEndValue(0.0)
                self._exit_animation.start()
        else:
            self._on_exit_animation_finished()

    def _on_exit_animation_finished(self):
        """Handle completion of exit animation"""
        if hasattr(self, 'close'):
            self.close()
        if hasattr(self, 'deleteLater'):
            self.deleteLater()

    def update_message(self, message: str):
        """Update dialog message dynamically"""
        # Find message label and update
        for child in self.findChildren(QLabel):
            if child.wordWrap():  # Likely the message label
                child.setText(message)
                break

    def set_button_enabled(self, button_type: str, enabled: bool):
        """Enable/disable specific button"""
        if button_type == "confirm" and hasattr(self, 'confirm_button'):
            self.confirm_button.setEnabled(enabled)
        elif button_type == "cancel" and hasattr(self, 'cancel_button'):
            self.cancel_button.setEnabled(enabled)

    def get_button(self, button_type: str) -> Optional[FluentStandardButton]:
        """Get reference to specific button"""
        if button_type == "confirm" and hasattr(self, 'confirm_button'):
            return self.confirm_button
        elif button_type == "cancel" and hasattr(self, 'cancel_button'):
            return self.cancel_button
        return None

    def __del__(self):
        """Cleanup resources"""
        try:
            if self._auto_close_timer:
                self._auto_close_timer.stop()
            if self._entrance_animation:
                self._entrance_animation.stop()
            if self._exit_animation:
                self._exit_animation.stop()
        except:
            pass  # Ignore cleanup errors


# Example usage and best practices documentation
"""
Enhanced Panel Components Usage Examples

This section demonstrates how to use the optimized panel components with
modern Python features and best practices.

Example 1: Settings Panel with Configuration Objects
```python
from dataclasses import dataclass

# Create settings panel
settings_panel = FluentSettingsPanel("Application Settings")

# Define settings using dataclasses
app_settings = [
    SettingConfig(
        key="app_name",
        label="Application Name", 
        default_value="My App",
        setting_type=str,
        validator=lambda x: len(x) > 0,
        help_text="The display name for your application"
    ),
    SettingConfig(
        key="auto_save",
        label="Auto Save",
        default_value=True,
        setting_type=bool,
        help_text="Automatically save changes"
    ),
    SettingConfig(
        key="save_interval",
        label="Save Interval (minutes)",
        default_value=5,
        setting_type=int,
        validator=lambda x: 1 <= x <= 60,
        help_text="How often to auto-save"
    )
]

# Add settings using batch operations
with settings_panel.batch_updates():
    for setting in app_settings:
        settings_panel.add_setting_from_config("general", setting)

# Connect to changes
settings_panel.setting_changed.connect(
    lambda key, value: print(f"Setting {key} changed to {value}")
)
```

Example 2: Properties Editor with Categories
```python
# Create properties editor with categories
props_editor = FluentPropertiesEditor("Object Properties")

# Define property categories
categories = {
    "Appearance": ["name", "color", "visible"],
    "Behavior": ["enabled", "auto_update", "timeout"], 
    "Advanced": ["debug_mode", "custom_data"]
}

# Set object properties with categories
obj = MyCustomObject()
props_editor.set_object_properties(obj, categories=categories)

# Or add individual properties with descriptors
descriptor = PropertyDescriptor(
    name="priority",
    value=1,
    prop_type=int,
    editable=True,
    validator=lambda x: 0 <= x <= 10,
    display_name="Task Priority",
    category="Behavior"
)
props_editor.add_property_from_descriptor(descriptor)
```

Example 3: Form Dialog with Validation
```python
# Create form dialog with enhanced validation
form_dialog = FluentFormDialog("User Registration")

# Define form fields using configuration
fields = [
    FluentFormDialog.FieldConfig(
        name="username",
        label="Username",
        field_type=str,
        required=True,
        validator=lambda x: len(x) >= 3 and x.isalnum(),
        placeholder="Enter username",
        help_text="Username must be at least 3 characters"
    ),
    FluentFormDialog.FieldConfig(
        name="email", 
        label="Email",
        field_type=str,
        required=True,
        validator=lambda x: "@" in x and "." in x,
        placeholder="Enter email address"
    ),
    FluentFormDialog.FieldConfig(
        name="age",
        label="Age", 
        field_type=int,
        required=True,
        min_value=13,
        max_value=120
    )
]

# Add fields with batch operations
with form_dialog.batch_updates():
    for field in fields:
        form_dialog.add_field_from_config(field)

# Connect to submission
form_dialog.submitted.connect(
    lambda data: print(f"Form submitted: {data}")
)

# Monitor validation state
form_dialog.validation_changed.connect(
    lambda valid: print(f"Form valid: {valid}")
)
```

Example 4: Confirmation Dialogs with Factory Methods
```python
# Simple confirmation
simple_dialog = FluentConfirmationDialog.create_simple(
    "Are you sure you want to save these changes?",
    "Save Changes"
)

# Dangerous action confirmation
danger_dialog = FluentConfirmationDialog.create_danger(
    "This action cannot be undone. All data will be permanently deleted.",
    "Delete All Data",
    "Delete Forever"
)

# Information dialog
info_dialog = FluentConfirmationDialog.create_info(
    "Operation completed successfully!",
    "Success",
    "OK"
)

# Custom configuration
config = FluentConfirmationDialog.DialogConfig(
    title="Custom Dialog",
    message="This is a custom confirmation dialog with auto-close.",
    confirm_text="Proceed",
    cancel_text="Cancel", 
    timeout=10,  # Auto-close after 10 seconds
    danger_mode=False
)
custom_dialog = FluentConfirmationDialog(config)

# Show with animation
custom_dialog.show_animated()
```

Performance Tips:
1. Use batch_updates() context manager for multiple operations
2. Leverage dataclasses for type-safe configuration
3. Use weak references in custom components for memory efficiency
4. Enable caching for frequently used styles
5. Implement debouncing for real-time validation
6. Use factory methods for common dialog patterns

Memory Management:
- All panels implement proper cleanup in __del__ methods
- Weak references prevent circular dependencies
- Timers are properly stopped during cleanup
- Animations are stopped and cleaned up
- Cache manager automatically manages memory usage

Type Safety:
- Modern union types (str | None) for better IDE support
- Protocols for duck typing and interface compliance
- Generic types for flexible but safe APIs
- Dataclasses for structured configuration
- Comprehensive type hints throughout
"""
