"""
Property Grid Components

Advanced property editing components that follow the Fluent Design System.
Includes property grids, settings panels, and configuration editors.
"""

import sys
from enum import Enum
from typing import Any, Dict, List, Optional, Callable # Removed Union
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, # Removed QGridLayout
                               QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, 
                               QCheckBox, QComboBox, QSlider, QColorDialog,
                               QScrollArea, QTreeWidget, # Removed QFrame, QSizePolicy
                               QTreeWidgetItem, QHeaderView, # Removed QSplitter
                               QTextEdit, QPushButton, QFileDialog, QGroupBox)
from PySide6.QtCore import Qt, Signal # Removed QPropertyAnimation, QEasingCurve, pyqtSignal
from PySide6.QtGui import QFont, QColor # Removed QPainter, QPalette, QIcon

# Import theme manager
try:
    from core.theme import theme_manager
except ImportError:
    theme_manager = None


class PropertyType(Enum):
    """Property data types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    COLOR = "color"
    CHOICE = "choice"
    RANGE = "range"
    FILE = "file"
    DIRECTORY = "directory"
    TEXT = "text"
    FONT = "font"


class FluentPropertyItem:
    """Represents a single property item"""
    
    def __init__(self, name: str, value: Any, property_type: PropertyType,
                 description: str = "", choices: Optional[List[str]] = None,
                 range_min: float = 0, range_max: float = 100,
                 readonly: bool = False, category: str = "General"):
        self.name = name
        self.value = value
        self.property_type = property_type
        self.description = description
        self.choices = choices or []
        self.range_min = range_min
        self.range_max = range_max
        self.readonly = readonly
        self.category = category
        self.validator = None
        
    def set_validator(self, validator: Callable[[Any], bool]):
        """Set custom validation function"""
        self.validator = validator
        
    def is_valid(self, value: Any) -> bool:
        """Check if value is valid"""
        if self.validator:
            return self.validator(value)
        return True


class FluentPropertyGrid(QWidget):
    """
    Advanced property grid for editing object properties
    """
    
    property_changed = Signal(str, object)  # property_name, new_value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.properties = {}
        self.editors = {}
        self.categories = {}
        
        self.setup_ui()
        self.apply_theme()
        
        # Connect to theme changes
        if theme_manager:
            theme_manager.theme_changed.connect(self.apply_theme)
            
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create tree widget for properties
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Property", "Value"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setItemsExpandable(True)
        
        # Configure header
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.tree)
        
    def apply_theme(self):
        """Apply the current theme"""
        if not theme_manager:
            return
            
        bg_color = theme_manager.get_color('surface').name()
        text_color = theme_manager.get_color('on_surface').name()
        border_color = theme_manager.get_color('outline').name()
        
        self.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                gridline-color: {border_color};
                selection-background-color: {theme_manager.get_color('primary_container').name()};
                selection-color: {theme_manager.get_color('on_primary_container').name()};
            }}
            
            QTreeWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {border_color};
            }}
            
            QTreeWidget::item:hover {{
                background-color: {theme_manager.get_color('surface_variant').name()};
            }}
            
            QTreeWidget::item:selected {{
                background-color: {theme_manager.get_color('primary_container').name()};
                color: {theme_manager.get_color('on_primary_container').name()};
            }}
            
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                border-image: none;
                image: url(:/icons/chevron_right.png); /* Assuming icons are in Qt resource file */
            }}
            
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                border-image: none;
                image: url(:/icons/chevron_down.png); /* Assuming icons are in Qt resource file */
            }}
        """)
        
    def add_property(self, prop: FluentPropertyItem):
        """Add a property to the grid"""
        self.properties[prop.name] = prop
        
        # Find or create category
        category_item = self.categories.get(prop.category)
        if not category_item:
            category_item = QTreeWidgetItem(self.tree)
            category_item.setText(0, prop.category)
            category_item.setExpanded(True)
            category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            
            # Style category item
            font = category_item.font(0)
            font.setBold(True)
            category_item.setFont(0, font)
            
            self.categories[prop.category] = category_item
            
        # Create property item
        prop_item = QTreeWidgetItem(category_item)
        prop_item.setText(0, prop.name)
        prop_item.setToolTip(0, prop.description)
        
        # Create editor widget
        editor = self.create_editor(prop)
        if editor:
            self.tree.setItemWidget(prop_item, 1, editor)
            self.editors[prop.name] = editor
            
    def create_editor(self, prop: FluentPropertyItem) -> Optional[QWidget]:
        """Create appropriate editor widget for property type"""
        editor_widget: Optional[QWidget] = None
        if prop.readonly:
            editor_widget = QLabel(str(prop.value))
            editor_widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            return editor_widget
            
        if prop.property_type == PropertyType.STRING:
            editor = QLineEdit()
            editor.setText(str(prop.value))
            editor.textChanged.connect(lambda text, p_name=prop.name: self.property_changed.emit(p_name, text))
            editor_widget = editor
            
        elif prop.property_type == PropertyType.INTEGER:
            editor = QSpinBox()
            editor.setRange(-999999, 999999)
            editor.setValue(int(prop.value))
            editor.valueChanged.connect(lambda value, p_name=prop.name: self.property_changed.emit(p_name, value))
            editor_widget = editor
            
        elif prop.property_type == PropertyType.FLOAT:
            editor = QDoubleSpinBox()
            editor.setRange(-999999.0, 999999.0)
            editor.setDecimals(3)
            editor.setValue(float(prop.value))
            editor.valueChanged.connect(lambda value, p_name=prop.name: self.property_changed.emit(p_name, value))
            editor_widget = editor
            
        elif prop.property_type == PropertyType.BOOLEAN:
            editor = QCheckBox()
            editor.setChecked(bool(prop.value))
            editor.toggled.connect(lambda checked, p_name=prop.name: self.property_changed.emit(p_name, checked))
            editor_widget = editor
            
        elif prop.property_type == PropertyType.CHOICE:
            editor = QComboBox()
            editor.addItems(prop.choices)
            if str(prop.value) in prop.choices:
                editor.setCurrentText(str(prop.value))
            editor.currentTextChanged.connect(lambda text, p_name=prop.name: self.property_changed.emit(p_name, text))
            editor_widget = editor
            
        elif prop.property_type == PropertyType.RANGE:
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(int(prop.range_min), int(prop.range_max))
            slider.setValue(int(prop.value))
            
            value_label = QLabel(str(prop.value))
            value_label.setMinimumWidth(40)
            
            def update_value(value, p_name=prop.name):
                value_label.setText(str(value))
                self.property_changed.emit(p_name, value)
                
            slider.valueChanged.connect(update_value)
            
            layout.addWidget(slider)
            layout.addWidget(value_label)
            
            editor_widget = container
            
        elif prop.property_type == PropertyType.COLOR:
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            
            color_button = QPushButton()
            color_button.setFixedSize(40, 25)
            
            current_color_val = prop.value
            color = QColor(current_color_val) if isinstance(current_color_val, str) else QColor() # Handle invalid string
            if not color.isValid() and isinstance(current_color_val, QColor): # if prop.value was already QColor
                color = current_color_val

            color_button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            
            color_label = QLabel(color.name())

            def choose_color(p_name=prop.name):
                # Ensure the initial color for the dialog is the current valid color
                initial_color_str = color_label.text()
                initial_q_color = QColor(initial_color_str)
                if not initial_q_color.isValid(): # Fallback if label somehow has invalid color
                    initial_q_color = QColor(Qt.GlobalColor.white)

                new_color = QColorDialog.getColor(initial_q_color, self, "Choose Color")
                if new_color.isValid():
                    color_button.setStyleSheet(f"background-color: {new_color.name()}; border: 1px solid #ccc;")
                    color_label.setText(new_color.name())
                    self.property_changed.emit(p_name, new_color.name())
                    
            color_button.clicked.connect(choose_color)
            
            layout.addWidget(color_button)
            layout.addWidget(color_label)
            layout.addStretch()
            
            editor_widget = container
            
        elif prop.property_type == PropertyType.FILE:
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            
            file_edit = QLineEdit()
            file_edit.setText(str(prop.value))
            file_edit.setReadOnly(True)
            
            browse_button = QPushButton("Browse...")
            browse_button.setMaximumWidth(80)
            
            def browse_file(p_name=prop.name):
                filename, _ = QFileDialog.getOpenFileName(self, "Select File", str(prop.value))
                if filename:
                    file_edit.setText(filename)
                    self.property_changed.emit(p_name, filename)
                    
            browse_button.clicked.connect(browse_file)
            
            layout.addWidget(file_edit)
            layout.addWidget(browse_button)
            
            editor_widget = container
            
        elif prop.property_type == PropertyType.TEXT:
            editor = QTextEdit()
            editor.setPlainText(str(prop.value))
            editor.setMaximumHeight(100)
            editor.textChanged.connect(lambda p_name=prop.name: self.property_changed.emit(p_name, editor.toPlainText()))
            editor_widget = editor
            
        else: # Default to string editor
            editor = QLineEdit()
            editor.setText(str(prop.value))
            editor.textChanged.connect(lambda text, p_name=prop.name: self.property_changed.emit(p_name, text))
            editor_widget = editor

        if editor_widget and theme_manager: # Apply theme to common editor properties
            editor_widget.setStyleSheet(f"""
                QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {{
                    background-color: {theme_manager.get_color('surface_variant').name()};
                    color: {theme_manager.get_color('on_surface_variant').name()};
                    border: 1px solid {theme_manager.get_color('outline').name()};
                    border-radius: 4px;
                    padding: 4px;
                }}
                QPushButton {{
                     background-color: {theme_manager.get_color('secondary_container').name()};
                     color: {theme_manager.get_color('on_secondary_container').name()};
                     border: none;
                     border-radius: 4px;
                     padding: 4px 8px;
                }}
                 QPushButton:hover {{
                     background-color: {theme_manager.get_color('secondary_container').lighter(110).name()};
                }}
            """)
        return editor_widget
        
    def get_property_value(self, name: str) -> Any:
        """Get current property value"""
        if name in self.properties:
            editor = self.editors.get(name)
            prop = self.properties[name] # Get prop to check its type

            if editor: # If an editor widget exists
                if prop.property_type == PropertyType.STRING:
                    return editor.text() if isinstance(editor, QLineEdit) else prop.value
                elif prop.property_type == PropertyType.INTEGER:
                    return editor.value() if isinstance(editor, QSpinBox) else prop.value
                elif prop.property_type == PropertyType.FLOAT:
                    return editor.value() if isinstance(editor, QDoubleSpinBox) else prop.value
                elif prop.property_type == PropertyType.BOOLEAN:
                    return editor.isChecked() if isinstance(editor, QCheckBox) else prop.value
                elif prop.property_type == PropertyType.CHOICE:
                    return editor.currentText() if isinstance(editor, QComboBox) else prop.value
                elif prop.property_type == PropertyType.TEXT:
                    return editor.toPlainText() if isinstance(editor, QTextEdit) else prop.value
                elif prop.property_type == PropertyType.RANGE: # Range has a container
                    # Assuming the slider's value is the source of truth if editor is the container
                    slider = editor.findChild(QSlider)
                    return slider.value() if slider else prop.value
                elif prop.property_type == PropertyType.COLOR: # Color has a container
                    color_label = editor.findChild(QLabel)
                    return color_label.text() if color_label else prop.value
                elif prop.property_type == PropertyType.FILE: # File has a container
                    file_edit = editor.findChild(QLineEdit)
                    return file_edit.text() if file_edit else prop.value
                # For readonly, editor is QLabel
                elif prop.readonly and isinstance(editor, QLabel):
                    return editor.text()

            # Fallback to stored value if no editor or specific logic
            return prop.value
        return None
        
    def set_property_value(self, name: str, value: Any):
        """Set property value"""
        if name in self.properties:
            self.properties[name].value = value # Update internal storage first
            editor = self.editors.get(name)
            prop = self.properties[name]

            if editor:
                if prop.readonly and isinstance(editor, QLabel):
                    editor.setText(str(value))
                    return

                if prop.property_type == PropertyType.STRING and isinstance(editor, QLineEdit):
                    editor.setText(str(value))
                elif prop.property_type == PropertyType.INTEGER and isinstance(editor, QSpinBox):
                    editor.setValue(int(value))
                elif prop.property_type == PropertyType.FLOAT and isinstance(editor, QDoubleSpinBox):
                    editor.setValue(float(value))
                elif prop.property_type == PropertyType.BOOLEAN and isinstance(editor, QCheckBox):
                    editor.setChecked(bool(value))
                elif prop.property_type == PropertyType.CHOICE and isinstance(editor, QComboBox):
                    editor.setCurrentText(str(value))
                elif prop.property_type == PropertyType.TEXT and isinstance(editor, QTextEdit):
                    editor.setPlainText(str(value))
                elif prop.property_type == PropertyType.RANGE and isinstance(editor, QWidget): # Container
                    slider = editor.findChild(QSlider)
                    value_label = editor.findChild(QLabel)
                    if slider: slider.setValue(int(value))
                    if value_label: value_label.setText(str(int(value)))
                elif prop.property_type == PropertyType.COLOR and isinstance(editor, QWidget): # Container
                    color_button = editor.findChild(QPushButton)
                    color_label = editor.findChild(QLabel)
                    new_q_color = QColor(value)
                    if new_q_color.isValid():
                        if color_button: color_button.setStyleSheet(f"background-color: {new_q_color.name()}; border: 1px solid #ccc;")
                        if color_label: color_label.setText(new_q_color.name())
                elif prop.property_type == PropertyType.FILE and isinstance(editor, QWidget): # Container
                    file_edit = editor.findChild(QLineEdit)
                    if file_edit: file_edit.setText(str(value))
                    
    def clear_properties(self):
        """Clear all properties"""
        self.tree.clear()
        self.properties.clear()
        self.editors.clear()
        self.categories.clear()


class FluentSettingsPanel(QWidget):
    """
    Settings panel with categorized sections
    """
    
    setting_changed = Signal(str, str, object)  # category, setting_name, value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_groups: Dict[str, Dict[str, Any]] = {} # Ensure type hint consistency
        
        self.setup_ui()
        self.apply_theme()
        
        # Connect to theme changes
        if theme_manager:
            theme_manager.theme_changed.connect(self.apply_theme)
            
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(20)
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
        
    def apply_theme(self):
        """Apply the current theme"""
        if not theme_manager:
            return
            
        bg_color = theme_manager.get_color('surface').name()
        text_color = theme_manager.get_color('on_surface').name()
        border_color = theme_manager.get_color('outline').name()
        
        self.setStyleSheet(f"""
            QWidget {{ /* General background for the panel itself */
                background-color: {bg_color};
            }}
            QScrollArea {{
                background-color: {bg_color};
                border: none;
            }}
            
            QGroupBox {{
                font-weight: bold;
                color: {text_color};
                border: 1px solid {border_color}; /* Common border style */
                border-radius: 8px;
                margin-top: 1ex; /* Space for title */
                padding: 15px; /* Inner padding */
                padding-top: 20px; /* More padding at top for title */
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {text_color};
                background-color: {bg_color}; /* Match groupbox background */
            }}
        """)
        # Apply theme to existing group boxes
        for group_data in self.settings_groups.values():
            if 'group_box' in group_data and group_data['group_box']:
                group_data['group_box'].setStyleSheet(self.styleSheet()) # Re-apply to ensure QGroupBox style takes
            if 'property_grid' in group_data and group_data['property_grid']:
                 group_data['property_grid'].apply_theme()

        
    def add_settings_group(self, name: str, title: Optional[str] = None) -> FluentPropertyGrid:
        """Add a new settings group"""
        if name in self.settings_groups:
            return self.settings_groups[name]['property_grid']
            
        group_box = QGroupBox(title or name)
        # group_box.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold)) # Example font
        group_layout = QVBoxLayout(group_box)
        group_layout.setSpacing(15)
        
        # Create property grid for this group
        property_grid = FluentPropertyGrid()
        property_grid.property_changed.connect(
            # Use a lambda that captures the current group name
            lambda prop_name, value, group_name_capture=name: self.setting_changed.emit(group_name_capture, prop_name, value)
        )
        
        group_layout.addWidget(property_grid)
        
        self.content_layout.addWidget(group_box)
        self.settings_groups[name] = {
            'group_box': group_box,
            'property_grid': property_grid
        }
        self.apply_theme() # Re-apply theme to style the new group box
        return property_grid
        
    def add_setting(self, group_name: str, prop: FluentPropertyItem):
        """Add a setting to a group"""
        if group_name not in self.settings_groups:
            self.add_settings_group(group_name, group_name) # Use group_name as title if not existing
            
        property_grid = self.settings_groups[group_name]['property_grid']
        property_grid.add_property(prop)
        
    def get_setting_value(self, group_name: str, setting_name: str) -> Any:
        """Get setting value"""
        if group_name in self.settings_groups:
            property_grid = self.settings_groups[group_name]['property_grid']
            return property_grid.get_property_value(setting_name)
        return None
        
    def set_setting_value(self, group_name: str, setting_name: str, value: Any):
        """Set setting value"""
        if group_name in self.settings_groups:
            property_grid = self.settings_groups[group_name]['property_grid']
            property_grid.set_property_value(setting_name, value)
            
    def export_settings(self) -> Dict[str, Dict[str, Any]]:
        """Export all settings as dictionary"""
        settings = {}
        for group_name, group_data in self.settings_groups.items():
            property_grid = group_data['property_grid']
            group_settings = {}
            
            for prop_name in property_grid.properties.keys():
                group_settings[prop_name] = property_grid.get_property_value(prop_name)
                
            settings[group_name] = group_settings
            
        return settings
        
    def import_settings(self, settings: Dict[str, Dict[str, Any]]):
        """Import settings from dictionary"""
        for group_name, group_settings in settings.items():
            # Ensure group exists, creating it if necessary
            if group_name not in self.settings_groups:
                self.add_settings_group(group_name, group_name) # Or a more descriptive title if available

            for setting_name, value in group_settings.items():
                # Ensure the setting exists in the property grid before setting its value
                # This might involve adding the FluentPropertyItem if it wasn't predefined
                # For simplicity, this example assumes settings are predefined.
                # A more robust implementation might create FluentPropertyItem on the fly
                # based on the type of 'value' if setting_name is not in property_grid.properties.
                if setting_name in self.settings_groups[group_name]['property_grid'].properties:
                    self.set_setting_value(group_name, setting_name, value)
                # else:
                #     print(f"Warning: Setting '{setting_name}' in group '{group_name}' not found. Cannot import.")


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    # Example theme setup (replace with your actual theme manager init)
    if theme_manager is None:
        class DummyThemeManager:
            def __init__(self):
                self.colors = {
                    'surface': QColor("#FFFFFF"), 'on_surface': QColor("#000000"),
                    'outline': QColor("#CCCCCC"), 'primary_container': QColor("#E0E0E0"),
                    'on_primary_container': QColor("#000000"), 'surface_variant': QColor("#F0F0F0"),
                    'secondary_container': QColor("#D0D0D0"), 'on_secondary_container': QColor("#000000"),
                }
                self.theme_changed = Signal() # Dummy signal

            def get_color(self, name: str) -> QColor:
                return self.colors.get(name, QColor("#FF00FF")) # Magenta for missing
        
        theme_manager = DummyThemeManager()


    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Property Grid Demo")
    window.setGeometry(100, 100, 800, 600)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    main_layout = QHBoxLayout(central_widget) # Renamed from layout to avoid conflict
    
    # Create property grid
    prop_grid = FluentPropertyGrid()
    
    # Add sample properties
    prop_grid.add_property(FluentPropertyItem("Name", "John Doe", PropertyType.STRING, "Person's name", category="User Info"))
    prop_grid.add_property(FluentPropertyItem("Age", 30, PropertyType.INTEGER, "Person's age", category="User Info"))
    prop_grid.add_property(FluentPropertyItem("Height", 175.5, PropertyType.FLOAT, "Height in cm", category="Details"))
    prop_grid.add_property(FluentPropertyItem("Active", True, PropertyType.BOOLEAN, "Is active", category="Status"))
    prop_grid.add_property(FluentPropertyItem("Country", "USA", PropertyType.CHOICE, "Country", 
                                               choices=["USA", "Canada", "UK", "Germany"], category="Location"))
    prop_grid.add_property(FluentPropertyItem("Score", 75, PropertyType.RANGE, "Score percentage", 
                                               range_min=0, range_max=100, category="Details"))
    prop_grid.add_property(FluentPropertyItem("Primary Color", "#ff0000", PropertyType.COLOR, "Favorite color", category="Appearance"))
    prop_grid.add_property(FluentPropertyItem("Notes", "Some notes here.", PropertyType.TEXT, "Additional notes", category="Details"))
    prop_grid.add_property(FluentPropertyItem("Config File", "/path/to/config.ini", PropertyType.FILE, "Path to config file", category="Advanced"))
    
    main_layout.addWidget(prop_grid)
    
    # Create settings panel
    settings_panel = FluentSettingsPanel()
    
    # Add appearance settings
    settings_panel.add_setting("Appearance", 
                               FluentPropertyItem("Theme", "Dark", PropertyType.CHOICE, 
                                                  "Application theme", choices=["Light", "Dark", "Auto"]))
    settings_panel.add_setting("Appearance", 
                               FluentPropertyItem("Font Size", 12, PropertyType.INTEGER, "UI font size"))
    settings_panel.add_setting("Appearance", 
                               FluentPropertyItem("Accent Color", "#0078d4", PropertyType.COLOR, "Accent color"))
    
    # Add behavior settings
    settings_panel.add_setting("Behavior", 
                               FluentPropertyItem("Auto Save", True, PropertyType.BOOLEAN, "Auto save documents"))
    settings_panel.add_setting("Behavior", 
                               FluentPropertyItem("Save Interval", 300, PropertyType.INTEGER, "Auto save interval (seconds)"))
    
    main_layout.addWidget(settings_panel)
    
    window.show()
    sys.exit(app.exec())
